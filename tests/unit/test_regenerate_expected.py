"""Unit tests for scripts/regenerate_expected.py.

Tests the tripwire comparison and diff printing logic in isolation,
mocking subprocess calls.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Ensure the script module can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

import regenerate_expected  # noqa: E402  # ty: ignore[unresolved-import] — resolved via the sys.path insert above


class TestTripwireComparison(unittest.TestCase):
    """Tripwire runs a subprocess -- we mock that and verify the result logic."""

    @mock.patch("regenerate_expected.subprocess.run")
    def test_tripwire_passes(self, mock_run):
        """When pytest exits 0, tripwire returns (True, '')."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""

        passed, detail = regenerate_expected.run_tripwire("some::node::id", expected_length=605)
        self.assertTrue(passed)
        self.assertEqual(detail, "")
        mock_run.assert_called_once()

    @mock.patch("regenerate_expected.subprocess.run")
    def test_tripwire_fails(self, mock_run):
        """When pytest exits non-zero, tripwire returns (False, detail)."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "AssertionError: 605 != 600"
        mock_run.return_value.stderr = ""

        passed, detail = regenerate_expected.run_tripwire("some::node::id", expected_length=605)
        self.assertFalse(passed)
        self.assertIn("AssertionError", detail)

    @mock.patch("regenerate_expected.subprocess.run")
    def test_tripwire_timeout(self, mock_run):
        """A timeout is caught and reported."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pytest", timeout=30)

        passed, detail = regenerate_expected.run_tripwire("some::node::id", expected_length=605)
        self.assertFalse(passed)
        self.assertIn("timed out", detail)


class TestDiffPrinter(unittest.TestCase):
    """print_diff writes unified diff lines to stdout."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.gen = self.tmpdir / "generated.json"
        self.exp = self.tmpdir / "expected.json"

    def tearDown(self):
        for p in [self.gen, self.exp]:
            if p.exists():
                p.unlink()
        self.tmpdir.rmdir()

    def test_diff_with_both_files(self):
        self.exp.write_text('{"a": 1}\n', encoding="utf-8")
        self.gen.write_text('{"a": 2}\n', encoding="utf-8")

        with mock.patch("regenerate_expected.sys.stdout") as mock_stdout:
            regenerate_expected.print_diff(self.gen, self.exp)

        # At least one diff line was written
        self.assertTrue(mock_stdout.write.called)

    def test_diff_missing_generated(self):
        """If generated file is missing, print a message."""
        self.exp.write_text("data\n", encoding="utf-8")

        with mock.patch("builtins.print") as mock_print:
            regenerate_expected.print_diff(self.gen, self.exp)

        mock_print.assert_any_call(f"  (generated file not found: {self.gen})")

    def test_diff_no_expected(self):
        """If expected file doesn't exist yet, treat as empty."""
        self.gen.write_text("brand new\n", encoding="utf-8")

        with mock.patch("regenerate_expected.sys.stdout") as mock_stdout:
            regenerate_expected.print_diff(self.gen, self.exp)

        self.assertTrue(mock_stdout.write.called)


class TestModuleInfo(unittest.TestCase):
    """Sanity-check the SNAPSHOT_MODULES registry."""

    def test_all_modules_have_years(self):
        for key, info in regenerate_expected.SNAPSHOT_MODULES.items():
            self.assertTrue(info.years, f"{key} has no years defined")
            self.assertTrue(info.formats, f"{key} has no formats defined")

    def test_node_id_generators(self):
        for key, info in regenerate_expected.SNAPSHOT_MODULES.items():
            for year in info.years:
                node = info.snapshot_node(year, info.formats[0])
                self.assertIsNotNone(
                    node,
                    f"{key} snapshot_node({year}, {info.formats[0]}) returned None",
                )
                # The node-id must reference the module's test file (pytest uses / always)
                test_file_posix = info.test_file.replace("\\", "/")
                node_posix = node.replace("\\", "/")
                self.assertIn(test_file_posix, node_posix)

    def test_tripwire_lengths_are_positive(self):
        for (module_key, year), length in regenerate_expected.TRIPWIRE_LENGTHS.items():
            self.assertGreater(
                length,
                0,
                f"Tripwire for {module_key}/{year} is {length}, expected > 0",
            )


if __name__ == "__main__":
    unittest.main()
