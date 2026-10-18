"""Regression tests for the self-authored safe_json demonstration."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from safe_json import save_json


class SaveJsonTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "settings.json"
        self.original = b'{"keep": "original"}\n'
        self.path.write_bytes(self.original)

    def test_naive_save_reproduces_truncation_bug(self):
        # The common before implementation destroys the existing content.
        with self.assertRaises(TypeError):
            with self.path.open("w", encoding="utf-8") as stream:
                json.dump({"unsupported": object()}, stream)
        self.assertNotEqual(self.path.read_bytes(), self.original)

    def test_unserializable_value_keeps_original(self):
        with self.assertRaises(TypeError):
            save_json(self.path, {"unsupported": object()})
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_nonstandard_nan_keeps_original(self):
        with self.assertRaises(ValueError):
            save_json(self.path, {"amount": float("nan")})
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_replace_failure_keeps_original_and_cleans_temp(self):
        with patch("safe_json.os.replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                save_json(self.path, {"new": True})
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_unicode_round_trip_and_existing_permissions(self):
        self.path.chmod(0o640)
        expected = {"label": "你好", "enabled": True, "items": [1, 2]}
        save_json(self.path, expected)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), expected)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o640)

    def test_new_file_has_private_permissions(self):
        new_path = self.path.parent / "new.json"
        save_json(new_path, {"new": True})
        self.assertEqual(json.loads(new_path.read_text()), {"new": True})
        self.assertEqual(new_path.stat().st_mode & 0o777, 0o600)

    def test_symlink_is_rejected_without_changing_target(self):
        link = self.path.parent / "link.json"
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            save_json(link, {"overwrite": True})
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertTrue(link.is_symlink())


if __name__ == "__main__":
    unittest.main()
