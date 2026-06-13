"""Registry-drift tests for the endpoint client functions.

Every name in ENDPOINTS must be exposed by the client as an explicit function
whose signature matches its registry entry (call params + the standard output
params). For custom endpoints the registry params must also agree with the
bespoke HTTPService method, so the three layers cannot drift apart.
"""

import inspect

from courtside_data import client
from courtside_data.endpoints import ENDPOINTS
from courtside_data.schemas import ROW_ADAPTERS

OUTPUT_PARAMS = ["output_type", "output_file_path", "output_write_option", "json_options", "raw"]


def expected_params(name):
    endpoint = ENDPOINTS[name]
    params = list(endpoint.params)
    if endpoint.custom:
        sig = inspect.signature(getattr(client.HTTPService, name))
        http_params = [p for p in sig.parameters if p != "self"]
        assert params == http_params, f"{name}: registry params {params} != HTTPService params {http_params}"
    return params


class TestClientRegistrySync:
    def test_every_endpoint_has_a_client_function(self):
        for name in ENDPOINTS:
            assert callable(getattr(client, name)), f"missing client function: {name}"

    def test_every_endpoint_has_matching_row_adapter(self):
        assert ENDPOINTS.keys() == ROW_ADAPTERS.keys()

    def test_function_metadata(self):
        for name in ENDPOINTS:
            func = getattr(client, name)
            assert func.__name__ == name

    def test_signature_params_order_and_defaults(self):
        for name in ENDPOINTS:
            func = getattr(client, name)
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            domain = expected_params(name)
            assert [p.name for p in params] == domain + OUTPUT_PARAMS, name
            for p in params[len(domain) : -1]:
                assert p.default is None, f"{name}.{p.name} should default to None"
            assert params[-1].default is False, f"{name}.raw should default to False"

    def test_docstring_mentions_endpoint_path(self):
        for name, endpoint in ENDPOINTS.items():
            doc = getattr(client, name).__doc__
            assert doc, f"{name} has no docstring"
            assert endpoint.path in doc, f"{name} docstring should mention {endpoint.path}"

    def test_positional_and_keyword_calls_bind(self):
        # Binding (not executing) verifies the signatures accept the same
        # call shapes as before the explicit-def refactor.
        sig = inspect.signature(client.team_roster)
        sig.bind("BOS", 2024)
        sig.bind(team_abbreviation="BOS", season_end_year=2024, output_type=None)
        sig.bind(team_abbreviation="BOS", season_end_year=2024, raw=True)
        sig.bind("BOS", season_end_year=2024)
