#!/usr/bin/env python3
"""
check_upstream.py - Monitor upstream Google Antigravity releases.

Checks:
  - antigravity (Desktop): storage.googleapis.com
  - antigravity-ide:       edgedl.me.gvt1.com
  - antigravity-cli:       GitHub releases API

Updates corresponding .spec files and opens GitHub Pull Requests if updates exist.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any, TypedDict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PackageUpdate(TypedDict):
    package: str
    spec_path: str
    current_version: str
    latest_version: str
    build_id: str | None
    url: str


def fetch_url(url: str, headers: dict[str, str] | None = None) -> str:
    req_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="replace")


def get_current_spec_version(spec_path: str) -> tuple[str, str | None]:
    """Extract (version, build_id) from an RPM spec file."""
    version = ""
    build_id: str | None = None
    with open(spec_path, encoding="utf-8") as f:
        for line in f:
            v_match = re.match(r"^Version:\s*([^\s]+)", line)
            if v_match:
                version = v_match.group(1).strip()
            b_match = re.match(r"^%global\s+build_id\s+([^\s]+)", line)
            if b_match:
                build_id = b_match.group(1).strip()
    return version, build_id


def version_tuple(ver_str: str) -> tuple[int, ...]:
    """Convert version string like 2.29.0 into tuple of ints for comparison."""
    clean = re.sub(r"[^\d.]", "", ver_str)
    return tuple(int(x) for x in clean.split(".") if x.isdigit())


def parse_dataset(attr_name: str, html_text: str) -> list[dict[str, Any]] | None:
    """Extract and decode a JSON data attribute from HTML."""
    m = re.search(rf"{attr_name}=[\x27\"]([^\x27\"]+)[\x27\"]", html_text)
    if not m:
        return None
    try:
        data: Any = json.loads(html.unescape(m.group(1)))
        if isinstance(data, list):
            return data
        return None
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Warning: Failed to parse JSON for {attr_name}: {e}", file=sys.stderr)
        return None


def check_all_from_releases(
    releases_html: str, verbose: bool = False
) -> dict[str, PackageUpdate | None]:
    results: dict[str, PackageUpdate | None] = {
        "antigravity": None,
        "antigravity-ide": None,
        "antigravity-cli": None,
    }

    # 1. Desktop App
    ag_items = parse_dataset("data-fallback-antigravity", releases_html)
    spec_path_hub = os.path.join(
        REPO_ROOT, "packages", "antigravity", "antigravity.spec"
    )
    cur_ver_hub, cur_build_hub = get_current_spec_version(spec_path_hub)

    if ag_items and len(ag_items) > 0:
        latest = ag_items[0]
        latest_hub_ver = str(latest["version"])
        latest_hub_build = str(latest["execution_id"])
        hub_url_x64 = f"https://storage.googleapis.com/antigravity-public/antigravity-hub/{latest_hub_ver}-{latest_hub_build}/linux-x64/Antigravity.tar.gz"
        hub_url_arm = f"https://storage.googleapis.com/antigravity-public/antigravity-hub/{latest_hub_ver}-{latest_hub_build}/linux-arm/Antigravity.tar.gz"

        print(
            f"[antigravity] Upstream: {latest_hub_ver}-{latest_hub_build} | Spec: {cur_ver_hub}-{cur_build_hub}"
        )
        if verbose:
            print(
                "  └─ Source: https://antigravity.google/releases (data-fallback-antigravity)"
            )
            print(f"  └─ Download x64: {hub_url_x64}")
            print(f"  └─ Download arm64: {hub_url_arm}")

        if (version_tuple(latest_hub_ver) > version_tuple(cur_ver_hub)) or (
            latest_hub_ver == cur_ver_hub
            and cur_build_hub
            and int(latest_hub_build) > int(cur_build_hub)
        ):
            results["antigravity"] = {
                "package": "antigravity",
                "spec_path": spec_path_hub,
                "current_version": cur_ver_hub,
                "latest_version": latest_hub_ver,
                "build_id": latest_hub_build,
                "url": f"x86_64: {hub_url_x64}\n- aarch64: {hub_url_arm}",
            }
    else:
        print(
            "[antigravity] Warning: data-fallback-antigravity not found in releases HTML!",
            file=sys.stderr,
        )

    # 2. Standalone IDE
    ide_items = parse_dataset("data-fallback-ide", releases_html)
    spec_path_ide = os.path.join(
        REPO_ROOT, "packages", "antigravity-ide", "antigravity-ide.spec"
    )
    cur_ver_ide, cur_build_ide = get_current_spec_version(spec_path_ide)

    if ide_items and len(ide_items) > 0:
        latest = ide_items[0]
        latest_ide_ver = str(latest["version"])
        latest_ide_build = str(latest["execution_id"])
        ide_url_x64 = f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{latest_ide_ver}-{latest_ide_build}/linux-x64/Antigravity%20IDE.tar.gz"
        ide_url_arm = f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{latest_ide_ver}-{latest_ide_build}/linux-arm/Antigravity%20IDE.tar.gz"

        print(
            f"[antigravity-ide] Upstream: {latest_ide_ver}-{latest_ide_build} | Spec: {cur_ver_ide}-{cur_build_ide}"
        )
        if verbose:
            print(
                "  └─ Source: https://antigravity.google/releases (data-fallback-ide)"
            )
            print(f"  └─ Download x64: {ide_url_x64}")
            print(f"  └─ Download arm64: {ide_url_arm}")

        if (version_tuple(latest_ide_ver) > version_tuple(cur_ver_ide)) or (
            latest_ide_ver == cur_ver_ide
            and cur_build_ide
            and int(latest_ide_build) > int(cur_build_ide)
        ):
            results["antigravity-ide"] = {
                "package": "antigravity-ide",
                "spec_path": spec_path_ide,
                "current_version": cur_ver_ide,
                "latest_version": latest_ide_ver,
                "build_id": latest_ide_build,
                "url": f"x86_64: {ide_url_x64}\n- aarch64: {ide_url_arm}",
            }
    else:
        print(
            "[antigravity-ide] Warning: data-fallback-ide not found in releases HTML!",
            file=sys.stderr,
        )

    # 3. CLI
    cli_items = parse_dataset("data-fallback-cli", releases_html)
    spec_path_cli = os.path.join(
        REPO_ROOT, "packages", "antigravity-cli", "antigravity-cli.spec"
    )
    cur_ver_cli, _ = get_current_spec_version(spec_path_cli)

    candidate_cli_ver: str | None = None
    cli_source = "webpage"
    if cli_items and len(cli_items) > 0:
        candidate_cli_ver = str(cli_items[0]["version"])

    # Also check GitHub API for the latest published tag
    try:
        gh_raw = fetch_url(
            "https://api.github.com/repos/google-antigravity/antigravity-cli/releases/latest"
        )
        gh_data: Any = json.loads(gh_raw)
        if isinstance(gh_data, dict):
            gh_tag = str(gh_data.get("tag_name", "")).lstrip("v")
            if gh_tag and (
                not candidate_cli_ver
                or version_tuple(gh_tag) > version_tuple(candidate_cli_ver)
            ):
                candidate_cli_ver = gh_tag
                cli_source = "GitHub Releases API"
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        pass

    if candidate_cli_ver:
        cli_url_x64 = f"https://github.com/google-antigravity/antigravity-cli/releases/download/{candidate_cli_ver}/agy_cli_linux_x64.tar.gz"
        cli_url_arm = f"https://github.com/google-antigravity/antigravity-cli/releases/download/{candidate_cli_ver}/agy_cli_linux_arm64.tar.gz"
        print(f"[antigravity-cli] Upstream: {candidate_cli_ver} | Spec: {cur_ver_cli}")
        if verbose:
            print(f"  └─ Source: {cli_source}")
            print(f"  └─ Download x64: {cli_url_x64}")
            print(f"  └─ Download arm64: {cli_url_arm}")

        if version_tuple(candidate_cli_ver) > version_tuple(cur_ver_cli):
            results["antigravity-cli"] = {
                "package": "antigravity-cli",
                "spec_path": spec_path_cli,
                "current_version": cur_ver_cli,
                "latest_version": candidate_cli_ver,
                "build_id": None,
                "url": f"x86_64: {cli_url_x64}\n- aarch64: {cli_url_arm}",
            }
    else:
        print(
            "[antigravity-cli] Warning: CLI version not found in HTML or GitHub!",
            file=sys.stderr,
        )

    return results


def update_spec_file(
    spec_path: str, new_version: str, new_build_id: str | None
) -> None:
    with open(spec_path, encoding="utf-8") as f:
        content = f.read()

    # Update Version:
    content = re.sub(r"(Version:\s*)[^\n]+", rf"\g<1>{new_version}", content, count=1)

    # Update build_id if present
    if new_build_id:
        content = re.sub(
            r"(%global\s+build_id\s+)[^\n]+", rf"\g<1>{new_build_id}", content, count=1
        )

    # Reset Release to 1%{?dist}
    content = re.sub(r"(Release:\s*)[^\n]+", r"\g<1>1%{?dist}", content, count=1)

    # Add changelog entry
    now = datetime.datetime.now(datetime.UTC).strftime("%a %b %d %Y")
    log_entry = f"* {now} Azhar Momin <azhar-momin@outlook.com> - {new_version}-1\n- Upstream release update to {new_version}\n\n"
    content = re.sub(r"(%changelog\n)", rf"\g<1>{log_entry}", content, count=1)

    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(content)


def create_pr_for_update(update_info: PackageUpdate) -> None:
    pkg = update_info["package"]
    new_ver = update_info["latest_version"]
    branch_name = f"update/{pkg}-{new_ver}"

    print(f"Creating branch and Pull Request for {pkg} -> {new_ver}...")
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "add", update_info["spec_path"]], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore({pkg}): bump to {new_ver}"], check=True
    )
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

    title = f"chore({pkg}): update to {new_ver}"
    body = (
        f"Automated update for **{pkg}**.\n\n"
        f"- Previous Version: `{update_info['current_version']}`\n"
        f"- Upstream Version: `{new_ver}`\n\n"
        f"Review spec changes and merge to trigger Fedora COPR build."
    )
    subprocess.run(
        ["gh", "pr", "create", "--title", title, "--body", body, "--head", branch_name],
        check=True,
    )
    subprocess.run(["git", "checkout", "master"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check for upstream Antigravity updates."
    )
    parser.add_argument(
        "--create-pr", action="store_true", help="Create Git branch and PR via gh CLI."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show full debug info, URLs, and origins.",
    )
    parser.add_argument(
        "--file", help="Path to local releases.html file (bypasses network fetch)."
    )
    args = parser.parse_args()

    updates: list[PackageUpdate] = []

    try:
        if args.file and os.path.isfile(args.file):
            if args.verbose:
                print(f"Reading releases from local file: {args.file}")
            with open(args.file, encoding="utf-8") as f:
                releases_html = f.read()
        else:
            if args.verbose:
                print("Fetching https://antigravity.google/releases (timeout: 45s)...")
            releases_html = fetch_url("https://antigravity.google/releases")
        all_res = check_all_from_releases(releases_html, verbose=args.verbose)

        for pkg in ["antigravity", "antigravity-ide", "antigravity-cli"]:
            up = all_res.get(pkg)
            if up:
                print(
                    f"[{pkg}] Update available: {up['current_version']} -> {up['latest_version']}"
                )
                updates.append(up)
            else:
                print(f"[{pkg}] Up to date.")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"Warning: Failed to fetch releases page: {e}", file=sys.stderr)

    if not updates:
        print("All packages are currently up-to-date with upstream.")
        return

    for up in updates:
        update_spec_file(up["spec_path"], up["latest_version"], up["build_id"])
        print(f"Updated spec file: {up['spec_path']}")
        if args.create_pr:
            create_pr_for_update(up)


if __name__ == "__main__":
    main()
