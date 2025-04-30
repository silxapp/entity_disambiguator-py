from dotenv import dotenv_values

from entity_disambiguator_py.client import EntityDisambiguatorClient

config = dotenv_values("test.env")
client = EntityDisambiguatorClient(lambda_url=config["URL"])


def test_say_hello():
    r = client.say_hello()
    print(r)
    print(client.auth.aws_access_key)
    print()
    print(client.auth.aws_secret_access_key)
    print()
    print(client.auth.aws_token)
    assert 1 == 2
