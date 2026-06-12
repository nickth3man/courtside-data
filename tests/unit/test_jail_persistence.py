"""On-disk persistence of the rate-limit jail circuit breaker."""

import json
import time
from unittest import mock

import httpx
import pytest

from courtside_data.errors import RateLimitJailed
from courtside_data.http_service import HTTPService, _persist_jail, _read_persisted_jail


@pytest.fixture
def jail_file(tmp_path, monkeypatch):
    path = tmp_path / "jail.json"
    monkeypatch.setenv("BASKETBALL_REF_JAIL_STATE_PATH", str(path))
    HTTPService._last_request_time = float("-inf")
    HTTPService._jailed_until = 0.0
    HTTPService._jail_state_loaded = False
    yield path
    HTTPService._last_request_time = float("-inf")
    HTTPService._jailed_until = 0.0
    HTTPService._jail_state_loaded = True


def _service(**kwargs):
    return HTTPService(parser=mock.MagicMock(), rate_limit_interval=0, impersonate=None, **kwargs)


class TestReadPersistedJail:
    def test_missing_file_returns_none(self, jail_file):
        assert _read_persisted_jail() is None

    def test_active_jail_is_returned(self, jail_file):
        until = time.time() + 600
        jail_file.write_text(json.dumps({"jailed_until_epoch": until}), encoding="utf-8")
        assert _read_persisted_jail() == until

    def test_expired_jail_is_ignored_and_removed(self, jail_file):
        jail_file.write_text(json.dumps({"jailed_until_epoch": time.time() - 10}), encoding="utf-8")
        assert _read_persisted_jail() is None
        assert not jail_file.exists()

    def test_corrupt_file_is_ignored(self, jail_file):
        jail_file.write_text("not json", encoding="utf-8")
        assert _read_persisted_jail() is None

    def test_disabled_by_empty_env(self, jail_file, monkeypatch):
        monkeypatch.setenv("BASKETBALL_REF_JAIL_STATE_PATH", "")
        assert _read_persisted_jail() is None


class TestPersistJail:
    def test_round_trip(self, jail_file):
        until = time.time() + 900
        _persist_jail(until)
        assert json.loads(jail_file.read_text(encoding="utf-8"))["jailed_until_epoch"] == until

    def test_creates_parent_directories(self, tmp_path, monkeypatch):
        path = tmp_path / "nested" / "dir" / "jail.json"
        monkeypatch.setenv("BASKETBALL_REF_JAIL_STATE_PATH", str(path))
        _persist_jail(time.time() + 900)
        assert path.exists()

    def test_disabled_by_empty_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("BASKETBALL_REF_JAIL_STATE_PATH", "")
        _persist_jail(time.time() + 900)
        assert list(tmp_path.iterdir()) == []


class TestJailPersistenceIntegration:
    def test_jail_detection_writes_state_file(self, jail_file):
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(429, headers={"Retry-After": "3600"}, request=request)
        session = mock.MagicMock()
        session.get.return_value = response

        service = _service(session=session)
        with pytest.raises(RateLimitJailed):
            service._get(url="https://example.com")

        payload = json.loads(jail_file.read_text(encoding="utf-8"))
        assert payload["jailed_until_epoch"] > time.time()

    def test_persisted_jail_blocks_a_fresh_process(self, jail_file):
        jail_file.write_text(json.dumps({"jailed_until_epoch": time.time() + 600}), encoding="utf-8")

        service = _service()
        with pytest.raises(RateLimitJailed) as exc_info:
            service._apply_rate_limiting()
        assert exc_info.value.retry_after == pytest.approx(600, abs=30)

    def test_state_is_loaded_only_once_per_process(self, jail_file):
        service = _service()
        service._apply_rate_limiting()  # loads (missing file), sets the flag

        # A jail file appearing later must not affect an already-running process
        jail_file.write_text(json.dumps({"jailed_until_epoch": time.time() + 600}), encoding="utf-8")
        service._apply_rate_limiting()  # does not raise
