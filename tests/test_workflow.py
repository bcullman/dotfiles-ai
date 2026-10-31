import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import capture
import policy

spec = importlib.util.spec_from_file_location("snapshot_export", SCRIPTS / "export.py")
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class WorkflowTests(unittest.TestCase):
    def test_family_and_local_rules(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "policies").mkdir()
            (root / "base.json").write_text(json.dumps({"patterns": [".zshrc", ".vimrc", ".config/nvim"], "excludes": ["*.bak"], "max_file_bytes": 100}))
            (root / "policies/linux.json").write_text(json.dumps({"patterns": [".profile"]}))
            (root / "policies/wsl.json").write_text(json.dumps({"patterns": [".wslrc"]}))
            (root / "local.json").write_text(json.dumps({"remove_patterns": [".vimrc", ".config/nvim"], "excludes": [".config/nvim/work"]}))
            with patch.object(policy, "REPO", root):
                result = policy.load_policy(root / "base.json", "wsl", root / "local.json")
            self.assertEqual(result["patterns"], [".profile", ".wslrc", ".zshrc"])
            self.assertTrue(policy.excluded(Path(".config/nvim/work/settings.lua"), result))
            self.assertTrue(policy.excluded(Path(".zshrc.bak"), result))
            (root / "local.json").write_text(json.dumps({"remove_excludes": ["*.bak"]}))
            with patch.object(policy, "REPO", root):
                changed = policy.load_policy(root / "base.json", "wsl", root / "local.json")
            self.assertFalse(policy.excluded(Path(".zshrc.bak"), changed))

    def fixture(self, root, text="export ROOT=/home/example\n"):
        home = root / "home"
        home.mkdir()
        (home / ".zshrc").write_text(text)
        snapshot = root / "raw"
        capture.capture(home, snapshot, "test", {"patterns": [".zshrc"],
            "max_file_bytes": 10000, "family": "linux"}, "machine")
        rules = {"files": [{"source": ".zshrc", "target": ".zshrc"}],
                 "replacements": [{"value": "/home/example", "placeholder": "__HOME__", "files": ["*"]}]}
        return snapshot, rules

    def test_scrub_preserves_structure_and_omits_raw_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, rules = self.fixture(root)
            candidate = root / "candidate"
            export.build(raw, rules, candidate)
            self.assertEqual((candidate / "files/.zshrc").read_text(), "export ROOT=__HOME__\n")
            manifest = json.loads((candidate / "manifest.json").read_text())
            self.assertEqual(manifest["representation"], "sanitized-not-installable")
            self.assertNotIn("inventory_names_only", manifest)
            self.assertNotIn("policy", manifest)
            digest = export.digest_tree(candidate)
            (candidate / "files/.zshrc").write_text("changed")
            self.assertNotEqual(digest, export.digest_tree(candidate))
            self.assertEqual(export.scrub("abcd abc", ".zshrc", [
                {"value": "abc", "placeholder": "__A__", "files": ["*"]},
                {"value": "abcd", "placeholder": "__B__", "files": ["*"]}]), "__B__ __A__")

    def test_residual_values_paths_and_changed_raw_block_export(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, rules = self.fixture(root)
            rules["replacements"][0]["files"] = [".vimrc"]
            with self.assertRaises(export.ExportError):
                export.build(raw, rules, root / "out1")
            rules["replacements"][0]["files"] = ["*"]
            rules["files"][0]["target"] = "../escape"
            with self.assertRaises(ValueError):
                export.build(raw, rules, root / "out2")
            rules["files"][0]["target"] = ".zshrc"
            (raw / "files/.zshrc").write_text("changed")
            with self.assertRaises(export.ExportError):
                export.build(raw, rules, root / "out3")

    def test_missing_or_failed_scanner_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(export.shutil, "which", return_value=None):
                with self.assertRaises(export.ExportError):
                    export.scan(root, root)
            with patch.object(export.shutil, "which", return_value="gitleaks"), patch.object(export.subprocess, "run", return_value=subprocess.CompletedProcess([], 2)):
                with self.assertRaises(export.ExportError):
                    export.scan(root, root)

    def test_publish_requires_exact_review_and_rescan(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            private = repo / ".private"
            private.mkdir()
            raw, rules = self.fixture(private)
            rules_path = private / "rules.json"
            rules_path.write_text(json.dumps(rules))
            args = ["export.py", "export", "--capture", str(raw), "--rules", str(rules_path)]
            with patch.object(export, "REPO", repo), patch.object(export, "scan") as scan:
                with patch.object(sys, "argv", args), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(export.main(), 0)
                self.assertFalse((repo / "evidence").exists())
                candidate = next(private.glob("export-*/candidate"))
                digest = export.digest_tree(candidate)
                with patch.object(sys, "argv", args + ["--reviewed", "wrong"]), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(export.main(), 1)
                self.assertFalse((repo / "evidence").exists())
                with patch.object(sys, "argv", args + ["--reviewed", digest]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(export.main(), 0)
                self.assertTrue((repo / "evidence/snapshots/test" / digest[:16] / "files/.zshrc").is_file())
                self.assertEqual(scan.call_count, 3)

    @unittest.skipUnless(shutil.which("zsh"), "zsh unavailable")
    def test_zsh_preflight_without_python(self):
        result = subprocess.run([shutil.which("zsh"), str(SCRIPTS.parent / "dotfiles.zsh"), "doctor"],
            env={"PATH": "/nonexistent"}, capture_output=True, text=True, cwd="/tmp")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python 3.8+ is required", result.stderr)

    @unittest.skipUnless(shutil.which("gitleaks"), "install Gitleaks for real scanner integration")
    def test_real_scanner_clean_and_unknown_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, rules = self.fixture(root)
            candidate = root / "candidate"
            export.build(raw, rules, candidate)
            export.scan(candidate, root)
            # Synthetic provider-format token, constructed to avoid a credential literal in source.
            token = "ghp_" + "Ab3dEf7hIj9kLm2nOp5qRs8tUv1wXy4zABCD"
            (candidate / "files/.zshrc").write_text("export GITHUB_TOKEN=" + token + "\n")
            with self.assertRaises(export.ExportError):
                export.scan(candidate, root)


if __name__ == "__main__":
    unittest.main()
