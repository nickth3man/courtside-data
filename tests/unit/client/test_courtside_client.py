"""CourtsideClient exposes every endpoint function bound to its own service."""

from unittest import TestCase, mock

from courtside_data import client
from courtside_data.client import CourtsideClient, _runner
from courtside_data.endpoints import ENDPOINTS


def _client_with_mock_service():
    instance = CourtsideClient.__new__(CourtsideClient)
    instance._service = mock.MagicMock()
    return instance


class TestCourtsideClientSurface(TestCase):
    def test_every_endpoint_is_exposed_as_a_method(self):
        instance = _client_with_mock_service()
        for name in ENDPOINTS:
            self.assertTrue(callable(getattr(instance, name)), f"missing CourtsideClient method: {name}")

    def test_methods_keep_function_metadata(self):
        instance = _client_with_mock_service()
        method = instance.team_roster
        self.assertEqual(method.__name__, "team_roster")
        self.assertIn(ENDPOINTS["team_roster"].path, method.__doc__)

    def test_unknown_attribute_raises(self):
        instance = _client_with_mock_service()
        self.assertRaises(AttributeError, getattr, instance, "not_an_endpoint")

    def test_private_attribute_raises(self):
        instance = _client_with_mock_service()
        self.assertRaises(AttributeError, getattr, instance, "_run_endpoint")

    def test_dir_includes_endpoints(self):
        instance = _client_with_mock_service()
        listing = dir(instance)
        self.assertIn("team_roster", listing)
        self.assertIn("search", listing)


class TestCourtsideClientServiceBinding(TestCase):
    def test_method_call_uses_the_clients_service(self):
        instance = _client_with_mock_service()
        instance._service.fetch_table.return_value = [{"player": "Jayson Tatum"}]

        result = instance.team_roster(team_abbreviation="BOS", season_end_year=2024)

        instance._service.fetch_table.assert_called_once()
        self.assertEqual(result, [{"player": "Jayson Tatum"}])

    def test_custom_endpoint_dispatches_to_the_clients_service(self):
        instance = _client_with_mock_service()
        instance._service.standings.return_value = [{"team": "BOSTON CELTICS"}]

        result = instance.standings(season_end_year=2024)

        instance._service.standings.assert_called_once_with(season_end_year=2024)
        self.assertEqual(result, [{"team": "BOSTON CELTICS"}])

    def test_override_is_cleared_after_the_call(self):
        instance = _client_with_mock_service()
        instance._service.fetch_table.return_value = [{"player": "X"}]
        instance.team_roster(team_abbreviation="BOS", season_end_year=2024)
        self.assertIsNone(_runner._service_override.get())


class TestSharedDefaultService(TestCase):
    def test_default_service_is_created_once(self):
        with mock.patch.object(_runner, "_shared_service", None):
            with mock.patch.object(_runner, "HTTPService") as service_cls:
                first = _runner._default_service()
                second = _runner._default_service()
        self.assertIs(first, second)
        service_cls.assert_called_once()

    def test_module_functions_resolve_to_shared_service(self):
        shared = mock.MagicMock()
        shared.fetch_table.return_value = [{"player": "X"}]
        with mock.patch.object(_runner, "_shared_service", shared):
            client.team_roster(team_abbreviation="BOS", season_end_year=2024)
        shared.fetch_table.assert_called_once()
