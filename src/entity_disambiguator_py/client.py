import json
import logging
from urllib.parse import urljoin

import boto3
import requests
from requests.exceptions import HTTPError
from requests.models import Response
from requests_aws4auth import AWS4Auth

from entity_disambiguator_py.model import (
    CanonicalSynonym,
    CanonicalSynonymsResponse,
    GetAliasesResponse,
    GetAliasResponse,
    GetConceptInfoResponse,
    GetConceptResponse,
    GetFamilyResponse,
    GetNeighborsResponse,
    GraphTraversalResponse,
    ListConceptResponse,
    MessageResponse,
    RelationshipType,
    SynonymSetResponse,
)

logger = logging.getLogger(__name__)


class NoSynonymsFound(Exception):
    def __init__(self, cid: str):
        self.message = f"No synonyms for {cid}"
        super().__init__(self.message)


def get_current_credentials():
    sess = boto3.Session()
    creds = sess.get_credentials()

    if creds is None:
        raise PermissionError("No credentials found, make sure you're logged in with AWS SSO")
    return creds


class EntityDisambiguatorLambdaClient:
    def __init__(self, lambda_url: str, region: str) -> None:
        self.headers = {"Accept": "application/xml", "Content-Type": "application/json"}
        self.url = lambda_url
        self.rpc_url = urljoin(self.url, "/api/rpc")
        self.region = region

        creds = get_current_credentials()
        self.auth = AWS4Auth(
            creds.access_key,
            creds.secret_key,
            region,
            "lambda",
            session_token=creds.token,
        )

    def _get_request(self, url: str) -> Response:
        return requests.get(
            url,
            auth=self.auth,
            headers=self.headers,
        )

    def _post_request(self, url: str, payload: dict) -> Response:
        return requests.post(
            url,
            auth=self.auth,
            headers=self.headers,
            data=json.dumps(payload),
        )

    def say_hello(self) -> MessageResponse:
        url = self.url + "/"
        r = self._get_request(url)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in say_hello")

        return MessageResponse(message=r.content.decode())

    def rpc_call(self, payload: dict) -> Response:
        return self._post_request(self.rpc_url, payload)

    def get_alias_id(self, alias_id: str, call_id: int = 1) -> GetAliasResponse:
        payload = {"id": call_id, "method": "get_alias_id", "params": {"id": alias_id}}
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_alias_id")

        return GetAliasResponse.model_validate_json(r.content)

    def get_aliases(self, name: str, call_id: int = 1) -> GetAliasesResponse:
        payload = {"id": call_id, "method": "get_aliases", "params": {"id": name}}

        r = self.rpc_call(payload)
        if r.status_code == 404:
            return GetAliasesResponse(id=call_id, result=[])

        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_aliases")

        return GetAliasesResponse.model_validate_json(r.content)

    def list_concepts(self, call_id: int = 1) -> ListConceptResponse:
        payload = {"id": call_id, "method": "list_concepts"}
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in list_concept")
        return ListConceptResponse.model_validate_json(r.content)

    def get_concept(self, concept_id: str, call_id: int = 1) -> GetConceptResponse:
        payload = {"id": call_id, "method": "get_concept", "params": {"id": concept_id}}
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_concept")

        return GetConceptResponse.model_validate_json(r.content)

    def get_concept_info(self, concept_id: str, call_id: int = 1) -> GetConceptInfoResponse:
        payload = {
            "id": call_id,
            "method": "get_concept_info",
            "params": {"id": concept_id},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_concept")

        return GetConceptInfoResponse.model_validate_json(r.content)

    def get_ancestors(self, umls_id: str, sort_prefix: str, call_id: int) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": call_id,
            "method": "get_ancestors",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]["edges"]}

        return GraphTraversalResponse.model_validate(content)

    def get_descendants(
        self, umls_id: str, sort_prefix: str, call_id: int
    ) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": call_id,
            "method": "get_descendants",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]["edges"]}

        return GraphTraversalResponse.model_validate(content)

    def get_parents(self, umls_id: str, sort_prefix: str, call_id: int) -> GetFamilyResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": call_id,
            "method": "get_parents",
            "params": {"query": {"partition_key": umls_id, "sort_key": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_parent {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]}

        return GetFamilyResponse.model_validate(content)

    def get_children(self, umls_id: str, sort_prefix: str, call_id: int) -> GetFamilyResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": call_id,
            "method": "get_children",
            "params": {"query": {"partition_key": umls_id, "sort_key": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]}

        return GetFamilyResponse.model_validate(content)

    def get_neighbors(
        self, umls_id: str, sort_prefix: str, call_id: int = 1
    ) -> GetNeighborsResponse:
        payload = {
            "id": call_id,
            "method": "get_neighbors",
            "params": {"query": {"partition_key": umls_id, "sort_key": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        return GetNeighborsResponse.model_validate(content)

    def get_subgraph(self, umls_id: str, sort_prefix: str, call_id: int) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": call_id,
            "method": "get_subgraph",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_subgraph")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]["edges"]}

        return GraphTraversalResponse.model_validate(content)

    def get_canonical_synonym(self, cid: str, call_id: int = 1) -> CanonicalSynonymsResponse:
        payload = {
            "id": call_id,
            "method": "get_canonical_synonym",
            "params": {"id": cid},
        }
        r = self.rpc_call(payload)
        if r.status_code == 404:
            logger.debug(f"no synonyms found for {cid}")
            return CanonicalSynonymsResponse(
                id=call_id, result=CanonicalSynonym(cui_id=cid, canonical_cui=cid, synset_id="-1")
            )

        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_synonyms")

        content = json.loads(r.content)
        return CanonicalSynonymsResponse.model_validate(content)

    def get_synonym_set(self, ssid: str, call_id: int = 1) -> SynonymSetResponse:
        payload = {
            "id": call_id,
            "method": "get_synonym_subgraph",
            "params": {"id": ssid},
        }
        r = self.rpc_call(payload)
        if r.status_code == 404:
            logger.debug(f"no synonyms found for {ssid}")
            raise NoSynonymsFound(ssid)

        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_synonyms")

        content = json.loads(r.content)
        return SynonymSetResponse.model_validate(content)
