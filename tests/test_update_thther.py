import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from scripts import update_thther as updater


class UpdateThtherTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.formula = Path(directory.name) / "thther.rb"
        # Exercise the real formula layout without tying tests to its current version.
        source = updater.DEFAULT_FORMULA.read_text(encoding="utf-8")
        self.source = re.sub(r"[0-9]+\.[0-9]+\.[0-9]+", "1.2.3", source)
        self.formula.write_text(self.source, encoding="utf-8")
        self.formula.chmod(0o644)
        self.make_release("v1.3.0")
        self.requests = []
        self.network = patch.object(updater, "urlopen", side_effect=self.respond).start()
        self.addCleanup(patch.stopall)
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def make_release(self, tag):
        self.tag = tag
        self.release = {
            "tag_name": tag,
            "draft": False,
            "prerelease": False,
            "published_at": "2026-09-23T00:00:00Z",
            "assets": [],
        }
        self.downloads = {}
        self.digests = {}
        for target in updater.TARGETS:
            name = f"thther-{tag}-{target}.tar.gz"
            url = f"{updater.RELEASE_URL}/{tag}/{name}"
            content = f"release content for {tag} {target}".encode()
            digest = hashlib.sha256(content).hexdigest()
            self.digests[target] = digest
            self.downloads[url] = content
            self.downloads[url + ".sha256"] = f"{digest}  {name}\n".encode()
            for suffix in ("", ".sha256"):
                self.release["assets"].append({
                    "name": name + suffix,
                    "state": "uploaded",
                    "browser_download_url": url + suffix,
                })

    def respond(self, request, **kwargs):
        self.requests.append(request)
        url = request.full_url
        if url == f"https://api.github.com/repos/{updater.REPOSITORY}/releases/tags/{self.tag}":
            return io.BytesIO(json.dumps(self.release).encode())
        if url not in self.downloads:
            raise AssertionError(f"Unexpected request: {url}")
        return io.BytesIO(self.downloads[url])

    def update(self, **kwargs):
        return updater.update_formula(self.formula, self.tag, **kwargs)

    def assert_failure_unchanged(self, pattern):
        before = self.formula.read_bytes()
        with self.assertRaisesRegex(updater.UpdateError, pattern):
            self.update()
        self.assertEqual(self.formula.read_bytes(), before)
        self.assertEqual(list(self.formula.parent.iterdir()), [self.formula])

    def test_upgrades_all_platforms_and_preserves_other_content_and_permissions(self):
        self.assertTrue(self.update())
        actual = self.formula.read_text()
        self.assertIn('version "1.3.0"', actual)
        for target, digest in self.digests.items():
            self.assertIn(f"thther-v1.3.0-{target}.tar.gz", actual)
            self.assertIn(f'sha256 "{digest}"', actual)
        remove_release_lines = lambda text: re.sub(
            r"^\s*(version|url|sha256) .*\n", "", text, flags=re.MULTILINE
        )
        self.assertEqual(remove_release_lines(actual), remove_release_lines(self.source))
        self.assertEqual(self.formula.stat().st_mode & 0o777, 0o644)

    def test_repeated_run_does_not_rewrite_file(self):
        self.update()
        before = self.formula.read_bytes()
        modified = self.formula.stat().st_mtime_ns
        self.assertFalse(self.update())
        self.assertEqual(self.formula.read_bytes(), before)
        self.assertEqual(self.formula.stat().st_mtime_ns, modified)

    def test_older_release_is_skipped_without_network_access(self):
        self.make_release("v1.2.2")
        self.assertFalse(self.update())
        self.network.assert_not_called()
        self.assertEqual(self.formula.read_text(), self.source)

    def test_versions_are_compared_numerically(self):
        self.formula.write_text(self.source.replace("1.2.3", "1.9.0"))
        self.make_release("v1.10.0")
        self.assertTrue(self.update())
        self.assertIn('version "1.10.0"', self.formula.read_text())

    def test_same_version_can_repair_checksums(self):
        self.make_release("v1.2.3")
        self.assertTrue(self.update())
        actual = self.formula.read_text()
        self.assertIn('version "1.2.3"', actual)
        for digest in self.digests.values():
            self.assertIn(f'sha256 "{digest}"', actual)

    def test_prerelease_and_draft_are_skipped(self):
        for flag in ("prerelease", "draft"):
            with self.subTest(flag=flag):
                self.make_release("v1.3.0")
                self.release[flag] = True
                self.assertFalse(self.update())
                self.assertEqual(self.formula.read_text(), self.source)

    def test_unpublished_release_fails(self):
        self.release["published_at"] = None
        self.assert_failure_unchanged("not been published")

    def test_release_tag_must_match(self):
        self.release["tag_name"] = "v9.0.0"
        self.assert_failure_unchanged("tag does not match")

    def test_each_of_the_six_assets_is_required(self):
        for index in range(6):
            with self.subTest(asset=index):
                self.make_release("v1.3.0")
                self.release["assets"].pop(index)
                self.assert_failure_unchanged("fully uploaded asset")

    def test_duplicate_asset_fails(self):
        self.release["assets"].append(self.release["assets"][0].copy())
        self.assert_failure_unchanged("fully uploaded asset")

    def test_incomplete_upload_fails(self):
        self.release["assets"][-1]["state"] = "starter"
        self.assert_failure_unchanged("fully uploaded asset")

    def test_unexpected_download_url_fails(self):
        self.release["assets"][0]["browser_download_url"] = "https://example.com/binary"
        self.assert_failure_unchanged("Unexpected asset URL")

    def test_invalid_checksum_files_fail(self):
        for content in (b"invalid", b"0" * 64, b"0" * 64 + b"  wrong-file.tar.gz\n"):
            with self.subTest(content=content):
                url = self.release["assets"][-1]["browser_download_url"]
                self.downloads[url] = content
                self.assert_failure_unchanged("Invalid checksum file")

    def test_binary_checksum_mismatch_on_last_platform_changes_nothing(self):
        url = self.release["assets"][-2]["browser_download_url"]
        self.downloads[url] = b"corrupted archive"
        self.assert_failure_unchanged("SHA-256 mismatch")

    def test_download_failure_changes_nothing(self):
        final_url = self.release["assets"][-2]["browser_download_url"]

        def failed_download(request, **kwargs):
            if request.full_url == final_url:
                raise URLError("download failed")
            return self.respond(request, **kwargs)

        self.network.side_effect = failed_download
        with self.assertRaises(URLError):
            self.update()
        self.assertEqual(self.formula.read_text(), self.source)

    def test_formula_layout_change_is_not_overwritten(self):
        self.formula.write_text(self.source.replace("on_macos do", "# keep this comment\n  on_macos do"))
        self.assertTrue(self.update())
        self.assertIn("# keep this comment", self.formula.read_text())

    def test_missing_formula_target_fails_without_partial_edit(self):
        self.formula.write_text(self.source.replace("aarch64-apple-darwin", "unsupported-target"))
        self.assert_failure_unchanged("URL/checksum pair")

    def test_duplicate_formula_target_fails_without_partial_edit(self):
        source = self.source.replace("aarch64-unknown-linux-gnu", "aarch64-apple-darwin")
        self.formula.write_text(source)
        self.assert_failure_unchanged("URL/checksum pair")

    def test_dry_run_verifies_and_prints_diff_without_writing(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertTrue(self.update(dry_run=True))
        self.assertIn('+  version "1.3.0"', output.getvalue())
        self.assertEqual(self.formula.read_text(), self.source)
        self.assertEqual(len(self.requests), 7)

    def test_invalid_tag_is_rejected_before_network_access(self):
        for tag in ("v1.3.0-rc.1", "1.3.0", "v01.3.0", "v1.3.0\n", "$(false)", ""):
            with self.subTest(tag=tag):
                self.tag = tag
                self.assert_failure_unchanged("stable release tag")
        self.network.assert_not_called()

    def test_api_token_is_not_sent_to_assets(self):
        with patch.dict(os.environ, {"GH_TOKEN": "test-token"}):
            self.update()
        self.assertEqual(self.requests[0].get_header("Authorization"), "Bearer test-token")
        for request in self.requests[1:]:
            self.assertIsNone(request.get_header("Authorization"))

    def test_concurrent_local_edit_is_preserved(self):
        changed = self.source + "# concurrent edit\n"

        def concurrent_edit(request, **kwargs):
            self.formula.write_text(changed)
            return self.respond(request, **kwargs)

        self.network.side_effect = concurrent_edit
        with self.assertRaisesRegex(updater.UpdateError, "changed during download"):
            self.update()
        self.assertEqual(self.formula.read_text(), changed)
        self.assertEqual(list(self.formula.parent.iterdir()), [self.formula])


if __name__ == "__main__":
    unittest.main()
