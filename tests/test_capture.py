import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "scripts" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


capture = module("capture")
compare = module("compare")


class CaptureTests(unittest.TestCase):
    def test_file_wildcards_deduplicate_and_respect_exclusions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "home"
            config = root / ".config"
            config.mkdir(parents=True)
            for name in [".shell_alias", ".shell_exports", ".shell_private", "other"]:
                (config / name).write_text("fixture\n")
            result = capture.capture(root, Path(temp) / "out", "test", {
                "files": [".config/.shell_*", ".config/.shell_alias", ".config/.shell_[ae]*",
                          ".config/.shell_export?", ".config/absent*", ".missing"],
                "directories": [], "exclude_components": ["*private*"], "max_file_bytes": 100
            }, "machine")
            rows = {r["path"]: r["status"] for r in result["files"]}
            self.assertEqual(rows, {".config/.shell_alias": "captured",
                                   ".config/.shell_exports": "captured",
                                   ".config/.shell_private": "excluded-name", ".missing": "missing"})
            self.assertEqual(len(rows), len(result["files"]))
            self.assertEqual(result["patterns"][-1]["status"], "no-matches")
            self.assertEqual(result["patterns"][2]["matches"], [".config/.shell_exports"])

    def test_wildcards_do_not_traverse_links_or_excluded_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "home"
            config = root / ".config"
            for name in ["safe", "private"]:
                (config / name).mkdir(parents=True)
                (config / name / "settings.conf").write_text("fixture")
            (config / "link").symlink_to(config / "safe", target_is_directory=True)
            result = capture.capture(root, Path(temp) / "out", "test", {
                "files": [".config/*/*.conf"], "directories": [],
                "exclude_components": ["private"], "max_file_bytes": 100
            }, "machine")
            self.assertEqual({r["path"]: r["status"] for r in result["files"]}, {
                ".config/safe/settings.conf": "captured", ".config/private": "excluded-name",
                ".config/link": "symlink-not-followed"})
            self.assertEqual(result["patterns"][0]["status"], "incomplete")
            with self.assertRaises(ValueError):
                capture.expand_files(root, [".config/**/*.conf"], {})
            with self.assertRaises(ValueError):
                capture.expand_files(root, ["../*.conf"], {})

    def test_capture_boundaries_and_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            home = base / "home"
            home.mkdir()
            (home / ".zshrc").write_text("export EDITOR=vim\n")
            (home / ".env").write_text("SECRET=do-not-copy")
            (home / ".zprofile").symlink_to(home / ".env")
            (home / ".config").mkdir()
            directory = home / ".config/nvim"
            directory.mkdir()
            (directory / "init.lua").write_text("-- config")
            (directory / "secrets.lua").write_text("secret")
            (directory / "binary").write_bytes(b"\0foo")
            (directory / "large").write_text("x" * 101)
            (directory / "linkdir").symlink_to(home, target_is_directory=True)
            os.mkfifo(str(directory / "pipe"))
            policy = {"files": [".zshrc", ".env", ".zprofile", ".bashrc"],
                      "directories": [".config/nvim"], "max_file_bytes": 100,
                      "exclude_components": [".env", "secrets.*"]}
            output = base / "capture"
            result = capture.capture(home, output, "test", policy, "machine")
            rows = {r["path"]: r["status"] for r in result["files"]}
            self.assertEqual(rows[".env"], "excluded-name")
            self.assertEqual(rows[".zprofile"], "symlink-not-followed")
            self.assertEqual(rows[".bashrc"], "missing")
            self.assertEqual(rows[".config/nvim/secrets.lua"], "excluded-name")
            self.assertEqual(rows[".config/nvim/binary"], "non-text")
            self.assertEqual(rows[".config/nvim/large"], "too-large")
            self.assertEqual(rows[".config/nvim/pipe"], "not-regular-file")
            self.assertEqual(rows[".config/nvim/linkdir"], "excluded-directory")
            self.assertEqual((output / "files/.zshrc").read_bytes(), (home / ".zshrc").read_bytes())
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((output / "files/.zshrc").stat().st_mode), 0o600)
            self.assertEqual(json.loads((output / "manifest.json").read_text()), result)
            with self.assertRaises(FileExistsError):
                capture.capture(home, output, "test", policy, "machine")

    def test_parent_symlink_and_policy_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "home"
            root.mkdir()
            outside = Path(temp) / "outside"
            outside.mkdir()
            (outside / "config").write_text("private")
            (root / ".config").symlink_to(outside, target_is_directory=True)
            result = capture.capture(root, Path(temp) / "out", "test",
                                     {"files": [".config/config"], "directories": [], "max_file_bytes": 100}, "machine")
            self.assertEqual(result["files"][0]["status"], "symlink-not-followed")
            for value in ["../secret", "/etc/passwd", ".", ""]:
                with self.assertRaises(ValueError):
                    capture.relative_path(value)

    def test_comparison_does_not_confuse_unknown_with_missing(self):
        left = {"files": [{"path": ".zshrc", "status": "captured", "sha256": "a", "mode": "0o600"}]}
        for status, expected in [("missing", "left-only"), ("unreadable", "unresolved"),
                                 ("symlink-not-followed", "unresolved")]:
            right = {"files": [{"path": ".zshrc", "status": status}]}
            self.assertEqual(compare.compare(left, right)[0]["comparison"], expected)
        self.assertEqual(compare.compare(left, left)[0]["comparison"], "identical")
        right = {"files": [{"path": ".zshrc", "status": "captured", "sha256": "b", "mode": "0o644"}]}
        self.assertEqual(compare.compare(left, right)[0]["comparison"], "content-differs+mode-differs")


if __name__ == "__main__":
    unittest.main()
