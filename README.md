# entity-disambiguator-py

A simple client for interacting with the entity-disambiguator lambda service

## Development

Install uv
...

Sync dependencies

```shell
uv synv
```

## Testing

Login to AWS
`aws sso login`

Create `test.env` file

```
URL=<lambda url for entity disambiguator>
REGION=<region for above>
```

```shell
uv run pytest
```

## Usage example

The entity disambiguator client uses an RPC pattern

Initialize the client

```python
import json

from entity_disambiguator_py.client import EntityDisambiguatorLambdaClient

lambda_url = "<url_of_entity_disambiguator_lambda>"
region = "<aws_region_of_lambda>"
client = EntityDisambiguatorLambdaClient(
    lambda_url=lambda_url, region=region
)

rpc_request = {
    "id": 1,
    "method": "rpc_method"
    "params": {
        "p": "param for method"
    }
}

resp = client.rpc_call(json.dumps(rpc_request))
```

### RPC Functions

see README.md in the `entity-disambiguator` repo
