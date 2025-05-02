from typing import Any
import boto3
from botocore.exceptions import TokenRetrievalError
from requests.structures import CaseInsensitiveDict

from entity_disambiguator_py.awscurl import get_credentials_botocore, make_request


def get_current_credentials():
    sess = boto3.Session()
    creds = sess.get_credentials()

    if creds is None:
        raise PermissionError(
            "No credentials found, make sure you're logged in with AWS SSO"
        )


class EntityDisambiguatorLambdaClient:

    def __init__(self, lambda_url: str, region: str) -> None:
        self.headers = CaseInsensitiveDict(
            {"Accept": "application/xml", "Content-Type": "application/json"}
        )
        self.url = lambda_url
        try:
            self.key, self.secret, self.token = get_credentials_botocore()
        except TokenRetrievalError as e:
            raise PermissionError(
                f"Failed to retrieve token due to {e}. Are you logged in?"
            )

        self.region = region

    def say_hello(self) -> dict[str, Any]:
        response = make_request(
            method="GET",
            service="lambda",
            region=self.region,
            uri=self.url,
            headers=self.headers,
            data="",
            access_key=self.key,
            secret_key=self.secret,
            security_token=self.token,
            data_binary=False,
            verify=True,
            allow_redirects=False,
        )
        return {"status_code": response.status_code, "body": response.text}
