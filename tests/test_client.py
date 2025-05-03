import os
from pathlib import Path
from dotenv import dotenv_values

from entity_disambiguator_py.awscurl import get_credentials_botocore
from entity_disambiguator_py.client import EntityDisambiguatorLambdaClient


config = dotenv_values("test.env")
client = EntityDisambiguatorLambdaClient(
    lambda_url=config["URL"], region=config["REGION"]
)


def __read(p):
    with open(p, "r") as f:
        s = f.read()
    return s


def __run_rpc(p):
    data = __read(p)
    resp = client.rpc_call(data)
    assert resp["status_code"] == 200, f"{resp}"


def test_get_credentials():
    ak, sk, st = get_credentials_botocore()

    assert isinstance(ak, str)
    assert isinstance(sk, str)
    assert isinstance(st, str)


def test_say_hello():
    r = client.say_hello()
    assert r["status_code"] == 200


def test_concept_rpc():
    test_directory = Path(os.path.abspath(os.path.dirname(__file__))).joinpath(
        "test_payloads"
    )

    __run_rpc(test_directory.joinpath("concept_post.json"))
    # __run_rpc(test_directory.joinpath("alias_name_post.json"))
    # __run_rpc(test_directory.joinpath("alias_id_post.json"))
