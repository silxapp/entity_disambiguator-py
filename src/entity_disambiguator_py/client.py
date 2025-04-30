from typing import Any
import requests
import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth


class EntityDisambiguatorClient:

    def __init__(self, lambda_url: str) -> None:
        self.url = lambda_url

        session = boto3.Session()
        credentials = session.get_credentials()

        self.auth = AWSRequestsAuth(
            aws_host=lambda_url,
            aws_access_key=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_region=session.region_name,
            aws_service="lambda",
            aws_token=credentials.token,
        )
        self.headers = {"Content-Type": "application/json"}

    def say_hello(self) -> dict[str, Any]:
        response = requests.get(self.url, auth=self.auth, headers=self.headers)
        return {"status_code": response.status_code, "body": response.text}
