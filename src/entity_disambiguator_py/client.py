import json
from urllib.parse import urljoin

import boto3
import requests
from requests.models import Response
from requests_aws4auth import AWS4Auth


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
            session_token=creds.token
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

    def say_hello(self) -> Response:
        url = self.url + "/"
        print(f"RPC URL {url}")
        return self._get_request(url)

    def rpc_call(self, payload: dict) -> Response:
        return self._post_request(self.rpc_url, payload)

    def get_aliases(self, name: str) -> Response:
        payload = {
            "id": 1,
            "method": "get_aliases",
            "params": {
                "id": name
            }
        }
        return self.rpc_call(payload)
