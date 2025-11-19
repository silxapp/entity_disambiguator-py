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
    DocDBRelationship,
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
    def __init__(self, lambda_url: str, region: str, call_id: int = 1) -> None:
        self.headers = {"Accept": "application/xml", "Content-Type": "application/json"}
        self.url = lambda_url
        self.rpc_url = urljoin(self.url, "/api/rpc")
        self.region = region
        self.call_id = call_id

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
            raise HTTPError(f"status: {r.status_code} error in say_hello {r.content}")

        return MessageResponse(message=r.content.decode())

    def rpc_call(self, payload: dict) -> Response:
        return self._post_request(self.rpc_url, payload)

    def get_alias_id(self, alias_id: str) -> GetAliasResponse:
        payload = {"id": self.call_id, "method": "get_alias_id", "params": {"id": alias_id}}
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_alias_id {r.content}")

        return GetAliasResponse.model_validate_json(r.content)

    def get_aliases(self, name: str) -> GetAliasesResponse:
        payload = {"id": self.call_id, "method": "get_aliases", "params": {"id": name}}

        r = self.rpc_call(payload)
        if r.status_code == 404:
            return GetAliasesResponse(id=self.call_id, result=[])

        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_aliases {r.content}")
        print(r.content)

        return GetAliasesResponse.model_validate_json(r.content)

    def list_concepts(self) -> ListConceptResponse:
        payload = {"id": self.call_id, "method": "list_concepts"}
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in list_concept {r.content}")
        return ListConceptResponse.model_validate_json(r.content)

    def get_concept(self, concept_id: str) -> GetConceptResponse:
        payload = {"id": self.call_id, "method": "get_concept", "params": {"id": concept_id}}
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_concept {r.content}")

        return GetConceptResponse.model_validate_json(r.content)

    def get_concept_info(self, concept_id: str) -> GetConceptInfoResponse:
        payload = {
            "id": self.call_id,
            "method": "get_concept_info",
            "params": {"id": concept_id},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_concept {r.content}")

        return GetConceptInfoResponse.model_validate_json(r.content)

    def get_ancestors(self, umls_id: str, sort_prefix: str) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": self.call_id,
            "method": "get_ancestors",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]["edges"]}

        return GraphTraversalResponse.model_validate(content)

    def get_descendants(self, umls_id: str, sort_prefix: str) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": self.call_id,
            "method": "get_descendants",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]["edges"]}

        return GraphTraversalResponse.model_validate(content)

    def get_parents(self, umls_id: str, sort_prefix: str) -> GetFamilyResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": self.call_id,
            "method": "get_parents",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_parent {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]}

        return GetFamilyResponse.model_validate(content)

    def get_children(self, umls_id: str, sort_prefix: str) -> GetFamilyResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": self.call_id,
            "method": "get_children",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]}

        return GetFamilyResponse.model_validate(content)

    def get_neighbors(self, umls_id: str, sort_prefix: str) -> GetNeighborsResponse:
        payload = {
            "id": self.call_id,
            "method": "get_neighbors",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_children {r.content}")

        content = json.loads(r.content)
        return GetNeighborsResponse.model_validate(content)

    def get_subgraph(self, umls_id: str, sort_prefix: str) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": self.call_id,
            "method": "get_subgraph",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_subgraph {r.content}")

        content = json.loads(r.content)
        content = {"id": content["id"], "edges": content["result"]["edges"]}

        return GraphTraversalResponse.model_validate(content)

    def get_canonical_synonym(self, cid: str) -> CanonicalSynonymsResponse:
        payload = {
            "id": self.call_id,
            "method": "get_canonical_synonym",
            "params": {"id": cid},
        }
        r = self.rpc_call(payload)
        if r.status_code == 404:
            logger.debug(f"no synonyms found for {cid}")
            return CanonicalSynonymsResponse(
                id=self.call_id,
                result=CanonicalSynonym(cui_id=cid, canonical_cui=cid, synset_id="-1"),
            )

        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_synonyms {r.content}")

        content = json.loads(r.content)
        return CanonicalSynonymsResponse.model_validate(content)

    def get_synonym_set(self, ssid: str) -> SynonymSetResponse:
        payload = {
            "id": self.call_id,
            "method": "get_synonym_subgraph",
            "params": {"id": ssid},
        }
        r = self.rpc_call(payload)
        if r.status_code == 404:
            logger.debug(f"no synonyms found for {ssid}")
            raise NoSynonymsFound(ssid)

        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_synonyms {r.content}")

        content = json.loads(r.content)
        return SynonymSetResponse.model_validate(content)

    def create_relationship(self, relationship: DocDBRelationship) -> None:
        relationship_dict = relationship.model_dump()
        payload = {
            "id": self.call_id,
            "method": "create_relationship",
            "params": {"data": relationship_dict},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in create relationship {r.content}")

        content = json.loads(r.content)
        logger.info(f"response {content}")

    def reset_cache(self) -> MessageResponse:
        payload = {
            "id": self.call_id,
            "method": "reset_cache",
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in reset cache {r.content}")

        return MessageResponse(message=r.content.decode())
