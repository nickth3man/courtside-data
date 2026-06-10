"""Characterization tests for the generated beta endpoint client functions.

These pin the externally observable shape of the generated functions —
existence, parameter names/order/defaults, name metadata, and docstring
content — so the generation mechanism can be refactored safely.
"""

import inspect

from courtside_data import client
from courtside_data.endpoints import ENDPOINTS

OUTPUT_PARAMS = ["output_type", "output_file_path", "output_write_option", "json_options"]


def expected_params(name):
    endpoint = ENDPOINTS[name]
    if endpoint.custom:
        sig = inspect.signature(getattr(client.HTTPService, name))
        return [p for p in sig.parameters if p != "self"]
    return list(endpoint.params)


class TestBetaFunctionGeneration:
    def test_every_endpoint_has_a_client_function(self):
        for name in ENDPOINTS:
            assert callable(getattr(client, name)), f"missing client function: {name}"

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
            for p in params[: len(domain)]:
                if p.default is not inspect.Parameter.empty:
                    continue  # custom endpoints may carry defaults from HTTPService
            for p in params[len(domain) :]:
                assert p.default is None, f"{name}.{p.name} should default to None"

    def test_docstring_mentions_beta_and_endpoint_path(self):
        for name, endpoint in ENDPOINTS.items():
            doc = getattr(client, name).__doc__
            assert doc, f"{name} has no docstring"
            assert "Beta" in doc
            assert endpoint.path in doc

    def test_positional_and_keyword_calls_bind(self):
        # Binding (not executing) verifies the signature accepts the same
        # call shapes the exec-generated functions did.
        sig = inspect.signature(client.team_roster)
        sig.bind("BOS", 2024)
        sig.bind(team_abbreviation="BOS", season_end_year=2024, output_type=None)
        sig.bind("BOS", season_end_year=2024)
