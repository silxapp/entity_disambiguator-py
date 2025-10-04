import json
import os
from pathlib import Path
<<<<<<< HEAD

import pytest
from dotenv import dotenv_values

from entity_disambiguator_py.client import EntityDisambiguatorLambdaClient, NoSynonymsFound
=======

from dotenv import dotenv_values

from entity_disambiguator_py.client import EntityDisambiguatorLambdaClient
>>>>>>> e865f7d9ce30c5b8f24a9728143192fc47faf938

config = dotenv_values("test.env")
lambda_url = config["URL"]
if lambda_url is None:
    raise SystemExit("No lambda url set")

region = config["REGION"]
if region is None:
    raise SystemExit("No AWS region set")

client = EntityDisambiguatorLambdaClient(lambda_url=lambda_url, region=region)


def __read(p):
    with open(p, "r") as f:
        s = json.load(f)
    return s


def __run_rpc(p):
    data = __read(p)
    resp = client.rpc_call(data)
    assert resp.status_code == 200, f"{resp}"


def test_say_hello():
    resp = client.say_hello()
    assert resp.message == "Silχ Digital Health entity disambiguator service"


def test_concept_rpc():
    test_directory = Path(os.path.abspath(os.path.dirname(__file__))).joinpath("test_payloads")

    __run_rpc(test_directory.joinpath("concept_post.json"))
    __run_rpc(test_directory.joinpath("alias_name_post.json"))
    __run_rpc(test_directory.joinpath("alias_id_post.json"))


def test_get_aliases():
    r = client.get_aliases("magnovatin b")
    assert len(r.result) == 1
    assert r.result[0].atom_id == "A17398278"

    r = client.get_aliases("adslkfjalj31-3i")
    assert len(r.result) == 0


def test_get_ancestors():
    # tylenol
    r = client.get_parents("C0699142", sort_prefix="PRED", call_id=1)
    print(r)
    assert len(r.edges) == 2

    r = client.get_ancestors("C0699142", sort_prefix="SYN", call_id=1)
    print(r)


def test_get_descendants():
    # tylenol
    r = client.get_children("C0699142", sort_prefix="SYN", call_id=1)
    assert len(r.edges) == 1


def test_get_synonyms():
    r = client.get_canonical_synonym("C3556763")
    assert r.result.canonical_cui == "C3556763"

    with pytest.raises(NoSynonymsFound):
        _ = client.get_canonical_synonym("not in graph")

    r = client.get_synonym_set(r.result.synset_id)
    assert "C3556763" in r.result.subgraph
    assert len(r.result.subgraph) == 2
