#!/usr/bin/env python3
"""Update thther from a complete, checksum-verified GitHub release."""

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from urllib.error import URLError
from urllib.request import Request, urlopen


REPOSITORY = "lakakala/thther-tty"
RELEASE_URL = f"https://github.com/{REPOSITORY}/releases/download"
TARGETS = (
    "aarch64-apple-darwin",
    "aarch64-unknown-linux-gnu",
    "x86_64-unknown-linux-gnu",
)
VERSION = r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
VERSION_LINE = re.compile(r'^([ \t]+version )"(' + VERSION + r')"$', re.MULTILINE)
DEFAULT_FORMULA = Path(__file__).resolve().parents[1] / "Formula/thther.rb"


class UpdateError(Exception):
    """The release or formula cannot safely be updated."""


def tag_version(tag):
    match = re.fullmatch("v" + VERSION, tag)
    if not match:
        raise UpdateError("Expected a stable release tag such as v0.1.3")
    return tuple(int(part) for part in match.groups())


def open_url(url, *, api=False):
    headers = {"User-Agent": "homebrew-tap-thther-updater"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        # Never send the API token to asset download/redirect hosts.
        if token := os.environ.get("GH_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"
    return urlopen(Request(url, headers=headers), timeout=60)


def release_checksums(tag):
    with open_url(
        f"https://api.github.com/repos/{REPOSITORY}/releases/tags/{tag}", api=True
    ) as response:
        release = json.load(response)
    if release.get("tag_name") != tag:
        raise UpdateError("Release tag does not match the requested tag")
    if release.get("draft") or release.get("prerelease"):
        print(f"Skipping unpublished or prerelease {tag}")
        return None
    if not release.get("published_at"):
        raise UpdateError("Release has not been published")

    assets = release.get("assets", [])
    for target in TARGETS:
        name = f"thther-{tag}-{target}.tar.gz"
        for asset_name in (name, name + ".sha256"):
            matches = [asset for asset in assets if asset.get("name") == asset_name]
            if len(matches) != 1 or matches[0].get("state") != "uploaded":
                raise UpdateError(f"Expected one fully uploaded asset: {asset_name}")
            if matches[0].get("browser_download_url") != f"{RELEASE_URL}/{tag}/{asset_name}":
                raise UpdateError(f"Unexpected asset URL: {asset_name}")

    checksums = {}
    for target in TARGETS:
        name = f"thther-{tag}-{target}.tar.gz"
        url = f"{RELEASE_URL}/{tag}/{name}"
        with open_url(url + ".sha256") as response:
            checksum_file = response.read(4097).decode("utf-8")
        match = re.fullmatch(
            r"([a-fA-F0-9]{64})[ \t]+\*?" + re.escape(name) + r"\s*", checksum_file
        )
        if not match or len(checksum_file) > 4096:
            raise UpdateError(f"Invalid checksum file for {name}")
        expected = match.group(1).lower()
        digest = hashlib.sha256()
        with open_url(url) as response:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            raise UpdateError(f"SHA-256 mismatch for {name}")
        checksums[target] = expected
        print(f"Verified {name}")
    return checksums


def formula_version(source):
    matches = list(VERSION_LINE.finditer(source))
    if len(matches) != 1:
        raise UpdateError("Expected exactly one stable formula version")
    return matches[0].group(2)


def render_formula(source, tag, checksums):
    old_tag = "v" + formula_version(source)
    updated = source
    for target in TARGETS:
        old_url = f"{RELEASE_URL}/{old_tag}/thther-{old_tag}-{target}.tar.gz"
        new_url = f"{RELEASE_URL}/{tag}/thther-{tag}-{target}.tar.gz"
        pattern = re.compile(
            r'^([ \t]+)url "' + re.escape(old_url) + r'"\n\1sha256 "[a-fA-F0-9]{64}"$',
            re.MULTILINE,
        )
        updated, count = pattern.subn(
            lambda match: (
                f'{match[1]}url "{new_url}"\n{match[1]}sha256 "{checksums[target]}"'
            ),
            updated,
        )
        if count != 1:
            raise UpdateError(f"Expected exactly one URL/checksum pair for {target}")
    return VERSION_LINE.sub(lambda match: f'{match[1]}"{tag[1:]}"', updated)


def update_formula(formula, tag, *, dry_run=False):
    requested = tag_version(tag)
    source = formula.read_text(encoding="utf-8")
    current = formula_version(source)
    if requested < tag_version("v" + current):
        print(f"Skipping {tag}: formula is already at {current}")
        return False
    checksums = release_checksums(tag)
    if checksums is None:
        return False
    updated = render_formula(source, tag, checksums)
    if updated == source:
        print(f"Formula already matches {tag}; no changes")
        return False
    if dry_run:
        print("".join(difflib.unified_diff(
            source.splitlines(keepends=True), updated.splitlines(keepends=True),
            fromfile=str(formula), tofile=str(formula),
        )), end="")
        return True

    # Write only after every asset and replacement has been validated.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=formula.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            output.write(updated)
        temporary.chmod(stat.S_IMODE(formula.stat().st_mode))
        if formula.read_text(encoding="utf-8") != source:
            raise UpdateError("Formula changed during download; refusing to overwrite it")
        temporary.replace(formula)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Updated {formula} to {tag}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Stable release tag, e.g. v0.1.3")
    parser.add_argument("--formula", type=Path, default=DEFAULT_FORMULA)
    parser.add_argument("--dry-run", action="store_true", help="Verify and show the diff only")
    args = parser.parse_args()
    try:
        update_formula(args.formula, args.tag, dry_run=args.dry_run)
    except (UpdateError, OSError, URLError, ValueError) as error:
        print(f"Update failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
