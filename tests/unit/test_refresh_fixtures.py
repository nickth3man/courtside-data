import importlib.util
import tempfile
from pathlib import Path
from unittest import TestCase


def load_refresh_fixtures_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "refresh_fixtures.py"
    spec = importlib.util.spec_from_file_location("refresh_fixtures", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestRefreshFixtures(TestCase):
    def setUp(self):
        self.refresh_fixtures = load_refresh_fixtures_module()

    def test_writes_response_content_to_staging_path(self):
        html_bytes = b'<html><body><table id="box-SAS-game-basic"><tfoot><tr><td>totals</td></tr></tfoot></table><table id="box-ATL-game-basic"><tfoot><tr><td>totals</td></tr></tfoot></table></body></html>'
        response = _Response(content=html_bytes)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self.refresh_fixtures.Fixture(
                key="boxscore_201701010ATL",
                url="https://www.basketball-reference.com/boxscores/201701010ATL.html",
                path=Path("tests/integration/files/boxscores/2017/1/201701010ATL.html"),
                checks=(self.refresh_fixtures.verify_box_score_fixture,),
            )

            result = self.refresh_fixtures.refresh_fixture(
                fixture=fixture,
                output_root=root / "staged",
                get=lambda url, timeout, headers: response,
                sleep=lambda _: None,
            )

            self.assertEqual(html_bytes, result.output_path.read_bytes())
            self.assertEqual(root / "staged" / fixture.path, result.output_path)
            self.assertEqual(1, result.request_count)

    def test_rejects_rate_limited_response_without_writing_file(self):
        response = _Response(status_code=429, content=b"Rate Limited Request")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self.refresh_fixtures.Fixture(
                key="boxscore_201701010ATL",
                url="https://www.basketball-reference.com/boxscores/201701010ATL.html",
                path=Path("tests/integration/files/boxscores/2017/1/201701010ATL.html"),
                checks=(self.refresh_fixtures.verify_html_fixture,),
            )

            with self.assertRaises(self.refresh_fixtures.FixtureRefreshError):
                self.refresh_fixtures.refresh_fixture(
                    fixture=fixture,
                    output_root=root / "staged",
                    get=lambda url, timeout, headers: response,
                    sleep=lambda _: None,
                )

            self.assertFalse((root / "staged" / fixture.path).exists())

    def test_rejects_box_score_without_game_basic_totals(self):
        html_bytes = b"<html><body><table id='other'></table></body></html>"

        with self.assertRaises(self.refresh_fixtures.FixtureRefreshError):
            self.refresh_fixtures.verify_box_score_fixture(html_bytes)

    def test_manifest_contains_expected_pilot_fixture(self):
        fixture = self.refresh_fixtures.FIXTURES["boxscore_201701010ATL"]

        self.assertEqual(
            "https://www.basketball-reference.com/boxscores/201701010ATL.html",
            fixture.url,
        )
        self.assertEqual(
            Path("tests/integration/files/boxscores/2017/1/201701010ATL.html"),
            fixture.path,
        )

    def test_main_requires_explicit_fixture_key_unless_listing(self):
        with self.assertRaises(self.refresh_fixtures.FixtureRefreshError):
            self.refresh_fixtures.main([])

    # ------------------------------------------------------------------
    # promote_to_final_destination
    # ------------------------------------------------------------------

    def test_promote_to_final_destination_copies_staged_to_fixture_path(self):
        rf = self.refresh_fixtures
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged_root = root / "staged"

            fixture = rf.Fixture(
                key="test_fixture",
                url="http://example.com/test.html",
                path=Path("subdir/test.html"),
                checks=(),
            )

            staged_src = staged_root / fixture.path
            staged_src.parent.mkdir(parents=True)
            staged_src.write_bytes(b"<html>staged</html>")

            copyfile_calls = []

            def tracking_copyfile(src, dst):
                copyfile_calls.append((src, dst))

            result = rf.promote_to_final_destination(
                output_root=staged_root,
                fixture=fixture,
                copyfile=tracking_copyfile,
            )

            self.assertTrue(result)
            self.assertEqual(len(copyfile_calls), 1)
            self.assertEqual(copyfile_calls[0][0], str(staged_src))
            self.assertEqual(copyfile_calls[0][1], str(fixture.path))

    def test_promote_to_final_destination_skips_if_staged_missing(self):
        rf = self.refresh_fixtures
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = rf.Fixture(
                key="test_fixture",
                url="http://example.com/test.html",
                path=Path("nonexistent.html"),
                checks=(),
            )
            result = rf.promote_to_final_destination(
                output_root=root / "staged",
                fixture=fixture,
                copyfile=lambda src, dst: None,
            )
            self.assertFalse(result)

    # ------------------------------------------------------------------
    # check_expected_drift
    # ------------------------------------------------------------------

    def test_check_expected_drift_unmapped_key_returns_none(self):
        """Keys not in FIXTURE_KEY_TO_TEST return None without invoking pytest."""
        rf = self.refresh_fixtures
        spy = []

        def fake_pytest(*args, **kwargs):
            spy.append(True)
            return _PytestResult(returncode=0)

        result = rf.check_expected_drift(
            fixture=rf.Fixture(
                key="unmapped_key",
                url="http://example.com",
                path=Path("x.html"),
                checks=(),
            ),
            output_root=Path("/tmp"),
            run_pytest=fake_pytest,
        )
        self.assertIsNone(result)
        self.assertEqual(len(spy), 0)

    def test_check_expected_drift_pytest_passes_returns_none(self):
        """When pytest exits 0, drift is None."""
        rf = self.refresh_fixtures
        # players_season_totals_2018 is mapped AND its expected file exists
        fixture = rf.Fixture(
            key="players_season_totals_2018",
            url="http://example.com",
            path=Path("x.html"),
            checks=(),
        )
        result = rf.check_expected_drift(
            fixture=fixture,
            output_root=Path("/tmp"),
            run_pytest=lambda args, **kwargs: _PytestResult(returncode=0),
        )
        self.assertIsNone(result)

    def test_check_expected_drift_pytest_fails_returns_warning(self):
        """When pytest exits non-zero, a drift warning is returned."""
        rf = self.refresh_fixtures
        fixture = rf.Fixture(
            key="players_season_totals_2018",
            url="http://example.com",
            path=Path("x.html"),
            checks=(),
        )
        result = rf.check_expected_drift(
            fixture=fixture,
            output_root=Path("/tmp"),
            run_pytest=lambda args, **kwargs: _PytestResult(returncode=1),
        )
        self.assertIsNotNone(result)
        self.assertIn("drift", result.lower())
        self.assertIn("players_season_totals_2018", result)


class _PytestResult:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class _Response:
    def __init__(self, status_code=200, content=b"<html></html>", url="https://www.basketball-reference.com/test.html", headers=None):
        self.status_code = status_code
        self.content = content
        self.url = url
        self.headers = headers or {"content-type": "text/html; charset=utf-8"}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)
