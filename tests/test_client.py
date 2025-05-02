from dotenv import dotenv_values

from entity_disambiguator_py.awscurl import get_credentials_botocore
from entity_disambiguator_py.client import EntityDisambiguatorLambdaClient


config = dotenv_values("test.env")
client = EntityDisambiguatorLambdaClient(
    lambda_url=config["URL"], region=config["REGION"]
)


def test_get_credentials():
    ak, sk, st = get_credentials_botocore()

    assert isinstance(ak, str)
    assert isinstance(sk, str)
    assert isinstance(st, str)


def test_say_hello():
    r = client.say_hello()
    assert r["status_code"] == 200
