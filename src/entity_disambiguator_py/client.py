import json
from urllib.parse import urljoin

import boto3
import requests
from requests.models import Response
from requests.exceptions import HTTPError
from requests_aws4auth import AWS4Auth

from entity_disambiguator_py.model import (
    GetAliasesResponse,
    GetConceptInfoResponse,
    GetConceptResponse,
    GraphTraversalResponse,
    ListConceptResponse,
    MessageResponse,
    RelationshipType,
)


def get_current_credentials():
    sess = boto3.Session()
    creds = sess.get_credentials()

    if creds is None:
        raise PermissionError(
            "No credentials found, make sure you're logged in with AWS SSO"
        )
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

    def get_concept_info(
        self, concept_id: str, call_id: int = 1
    ) -> GetConceptInfoResponse:
        payload = {
            "id": call_id,
            "method": "get_concept_info",
            "params": {"id": concept_id},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_concept")

        return GetConceptInfoResponse.model_validate_json(r.content)

    def get_parents(
        self, umls_id: str, sort_prefix: str, call_id: int
    ) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": call_id,
            "method": "get_parents",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_concept")

        return GraphTraversalResponse.model_validate_json(r.content)

    def get_children(
        self, umls_id: str, sort_prefix: str, call_id: int
    ) -> GraphTraversalResponse:
        try:
            _ = RelationshipType[sort_prefix]
        except KeyError:
            raise HTTPError(f"Invalid sort prefix {sort_prefix}")

        payload = {
            "id": call_id,
            "method": "get_children",
            "params": {"query": {"start_node": umls_id, "sort_prefix": sort_prefix}},
        }
        r = self.rpc_call(payload)
        if r.status_code != 200:
            raise HTTPError(f"status: {r.status_code} error in get_concept")

        return GraphTraversalResponse.model_validate_json(r.content)

    def get_subgraph(
        self, umls_id: str, sort_prefix: str, call_id: int
    ) -> GraphTraversalResponse:
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
            raise HTTPError(f"status: {r.status_code} error in get_concept")

        return GraphTraversalResponse.model_validate_json(r.content)
