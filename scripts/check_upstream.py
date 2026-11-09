#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "packaging>=24.0",
# ]
# ///
"""check_upstream.py - Monitor upstream releases and manage automated PR updates."""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from packaging.version import parse as parse_version

REPO_ROOT = Path(__file__).resolve().parent.parent


class PackageUpdate(TypedDict):
    package: str
    spec_path: Path
    current_version: str
    latest_version: str
    build_id: str | None
    url: str


@dataclass(frozen=True)
class PackageDefinition:
    name: str
    source_type: str  # "updater_api" | "github_api"
    api_url: str
    build_urls: Callable[[str, str | None], tuple[str, str]]


PACKAGES: dict[str, PackageDefinition] = {
    "antigravity": PackageDefinition(
        name="antigravity",
        source_type="updater_api",
        api_url="https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/releases",
        build_urls=lambda v, b: (
            f"https://storage.googleapis.com/antigravity-public/antigravity-hub/{v}-{b}/linux-x64/Antigravity.tar.gz",
            f"https://storage.googleapis.com/antigravity-public/antigravity-hub/{v}-{b}/linux-arm/Antigravity.tar.gz",
        ),
    ),
    "antigravity-ide": PackageDefinition(
        name="antigravity-ide",
        source_type="updater_api",
        api_url="https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases",
        build_urls=lambda v, b: (
            f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{v}-{b}/linux-x64/Antigravity%20IDE.tar.gz",
            f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{v}-{b}/linux-arm/Antigravity%20IDE.tar.gz",
        ),
    ),
    "antigravity-cli": PackageDefinition(
        name="antigravity-cli",
        source_type="github_api",
        api_url="https://api.github.com/repos/google-antigravity/antigravity-cli/releases/latest",
        build_urls=lambda v, _: (
            f"https://github.com/google-antigravity/antigravity-cli/releases/download/{v}/agy_cli_linux_x64.tar.gz",
            f"https://github.com/google-antigravity/antigravity-cli/releases/download/{v}/agy_cli_linux_arm64.tar.gz",
        ),
    ),
    "slack": PackageDefinition(
        name="slack",
        source_type="slack_web",
        api_url="https://slack.com/release-notes/linux",
        build_urls=lambda v, _: (
            f"https://downloads.slack-edge.com/desktop-releases/linux/x64/{v}/slack-{v}-0.1.el8.x86_64.rpm",
            "N/A",
        ),
    ),
    "zoom": PackageDefinition(
        name="zoom",
        source_type="zoom_redirect",
        api_url="https://zoom.us/client/latest/zoom_x86_64.rpm",
        build_urls=lambda v, _: (
            f"https://cdn.zoom.us/prod/{v}/zoom_x86_64.rpm",
            "N/A",
        ),
    ),
}


# --- Helpers ---


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if check and proc.returncode != 0:
        error_msg = proc.stderr.strip() or proc.stdout.strip()
        print(
            f"Command {' '.join(cmd)} failed (code {proc.returncode}): {error_msg}",
            file=sys.stderr,
        )
        raise subprocess.CalledProcessError(
            proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr
        )
    return proc


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], check=check)


def gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["gh", *args], check=check)


def fetch_json(
    url: str, headers: dict[str, str] | None = None, timeout: int = 15
) -> Any:
    """Fetch and decode JSON from URL via urllib."""
    req_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Accept": "application/json,*/*;q=0.8",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_text(
    url: str, headers: dict[str, str] | None = None, timeout: int = 15
) -> str:
    """Fetch text/HTML content from URL via urllib."""
    req_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def get_current_spec_version(spec_path: Path) -> tuple[str, str | None]:
    """Extract (version, build_id) from an RPM spec file."""
    version = ""
    build_id: str | None = None
    with spec_path.open(encoding="utf-8") as f:
        for line in f:
            v_match = re.match(r"^Version:\s*([^\s]+)", line)
            if v_match:
                version = v_match.group(1).strip()
            b_match = re.match(r"^%global\s+build_id\s+([^\s]+)", line)
            if b_match:
                build_id = b_match.group(1).strip()
    return version, build_id


def is_newer(
    latest_ver: str,
    latest_build: str | None,
    cur_ver: str,
    cur_build: str | None,
) -> bool:
    """Compare upstream version/build against current spec version/build."""
    v_latest = parse_version(latest_ver)
    v_cur = parse_version(cur_ver)
    if v_latest > v_cur:
        return True
    if v_latest == v_cur and latest_build and cur_build:
        try:
            return int(latest_build) > int(cur_build)
        except ValueError:
            return latest_build != cur_build
    return False


def check_package(
    pkg: PackageDefinition, verbose: bool = False
) -> tuple[PackageUpdate | None, PackageUpdate | None]:
    """Check a single package against upstream and return (update_if_newer, latest_info)."""
    spec_path = REPO_ROOT / "packages" / pkg.name / f"{pkg.name}.spec"
    cur_ver, cur_build = get_current_spec_version(spec_path)

    latest_ver: str | None = None
    latest_build: str | None = None
    source_label = ""

    try:
        if pkg.source_type == "slack_web":
            html = fetch_text(pkg.api_url)
            versions = re.findall(r"Slack\s+([0-9]+\.[0-9]+\.[0-9]+)", html)
            # Slack often pre-publishes release notes hours before the CDN upload completes.
            # Check the top 5 newest releases with HTTP HEAD; pick the first one that is live on CDN.
            for v in versions[:5]:
                rpm_url, _ = pkg.build_urls(v, None)
                head_req = urllib.request.Request(
                    rpm_url,
                    method="HEAD",
                    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
                )
                try:
                    with urllib.request.urlopen(head_req, timeout=5) as resp:
                        if resp.status == 200:
                            latest_ver = v
                            source_label = "Slack Release Notes (Live CDN Verified)"
                            break
                except (urllib.error.URLError, TimeoutError, OSError):
                    continue
        elif pkg.source_type == "zoom_redirect":

            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, *args: Any, **kwargs: Any) -> None:
                    return None

            opener = urllib.request.build_opener(NoRedirect)
            head_req = urllib.request.Request(
                pkg.api_url,
                method="HEAD",
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
            )
            try:
                resp = opener.open(head_req, timeout=10)
                final_url = resp.geturl()
            except urllib.error.HTTPError as e:
                final_url = e.headers.get("Location") or ""

            m = re.search(r"/prod/([^/]+)/zoom_x86_64\.rpm", final_url)
            if m:
                latest_ver = m.group(1)
                source_label = "Zoom CDN Redirect"
        else:
            data = fetch_json(pkg.api_url)
            if pkg.source_type == "updater_api":
                if isinstance(data, list) and len(data) > 0:
                    first = data[0]
                    latest_ver = str(first["version"])
                    latest_build = str(first.get("execution_id", ""))
                    source_label = "Live Cloud Run Auto-Updater API"
            elif pkg.source_type == "github_api":
                if isinstance(data, dict):
                    tag = str(data.get("tag_name", "")).lstrip("v")
                    if tag:
                        latest_ver = tag
                        source_label = "GitHub Releases API"
    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        KeyError,
    ) as e:
        print(f"[{pkg.name}] Error checking upstream API: {e}", file=sys.stderr)
        return None, None

    if not latest_ver:
        print(
            f"[{pkg.name}] Warning: No version info returned by upstream API!",
            file=sys.stderr,
        )
        return None, None

    x64_url, arm_url = pkg.build_urls(latest_ver, latest_build)
    display_ver = f"{latest_ver}-{latest_build}" if latest_build else latest_ver
    display_spec = f"{cur_ver}-{cur_build}" if cur_build else cur_ver
    print(f"[{pkg.name}] Upstream: {display_ver} | Spec: {display_spec}")

    if verbose:
        print(f"  └─ Source: {source_label}")
        print(f"  └─ Download x64: {x64_url}")
        if arm_url != "N/A":
            print(f"  └─ Download arm64: {arm_url}")

    url_str = (
        f"  - x86_64: {x64_url}\n  - aarch64: {arm_url}"
        if arm_url != "N/A"
        else f"  - x86_64: {x64_url}"
    )

    info: PackageUpdate = {
        "package": pkg.name,
        "spec_path": spec_path,
        "current_version": cur_ver,
        "latest_version": latest_ver,
        "build_id": latest_build,
        "url": url_str,
    }

    update = info if is_newer(latest_ver, latest_build, cur_ver, cur_build) else None
    return update, info


def check_all(
    verbose: bool = False,
) -> tuple[dict[str, PackageUpdate | None], dict[str, PackageUpdate]]:
    updates: dict[str, PackageUpdate | None] = {}
    latest_info: dict[str, PackageUpdate] = {}
    for name, pkg in PACKAGES.items():
        up, info = check_package(pkg, verbose=verbose)
        updates[name] = up
        if info:
            latest_info[name] = info
    return updates, latest_info


# --- Spec & README Modifiers ---


def update_spec_file(
    spec_path: Path, new_version: str, new_build_id: str | None
) -> None:
    content = spec_path.read_text(encoding="utf-8")

    # Update Version:
    content = re.sub(r"(Version:\s*)[^\n]+", rf"\g<1>{new_version}", content, count=1)

    # Update build_id if present
    if new_build_id:
        content = re.sub(
            r"(%global\s+build_id\s+)[^\n]+", rf"\g<1>{new_build_id}", content, count=1
        )

    # Reset Release to 1%{?dist}
    content = re.sub(r"(Release:\s*)[^\n]+", r"\g<1>1%{?dist}", content, count=1)

    # Add changelog entry if not already present
    if f"- {new_version}-1" not in content:
        now = datetime.datetime.now(datetime.UTC).strftime("%a %b %d %Y")
        log_entry = (
            f"* {now} Azhar Momin <azhar-momin@outlook.com> - {new_version}-1\n"
            f"- Upstream release update to {new_version}\n\n"
        )
        content = re.sub(r"(%changelog\n)", rf"\g<1>{log_entry}", content, count=1)

    spec_path.write_text(content, encoding="utf-8")


def update_readme_version(pkg: str, new_version_release: str) -> None:
    readme_path = REPO_ROOT / "README.md"
    if not readme_path.is_file():
        return
    content = readme_path.read_text(encoding="utf-8")

    pattern = rf"(\|\s*\*\*`{re.escape(pkg)}`\*\*\s*\|\s*`[^`]+`\s*\|\s*)`[^`]+`(\s*\|)"
    replacement = rf"\g<1>`{new_version_release}`\g<2>"
    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        readme_path.write_text(new_content, encoding="utf-8")
        print(f"Updated README.md version for {pkg} -> {new_version_release}")


# --- GitHub PR Integration ---


def find_open_pr_for_package(pkg: str) -> dict[str, Any] | None:
    try:
        res = gh(
            "pr", "list", "--state", "open", "--json", "number,title,headRefName,body"
        )
        prs = json.loads(res.stdout)
        for pr in prs:
            head = pr.get("headRefName", "")
            title = pr.get("title", "")
            if (
                re.search(rf"^update/{re.escape(pkg)}-v?\d", head)
                or f"({pkg})" in title
            ):
                return pr
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as e:
        print(f"Note: Could not query GitHub PRs: {e}", file=sys.stderr)
    return None


def get_open_pr_by_number(pr_number: int) -> dict[str, Any] | None:
    try:
        res = gh(
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,title,headRefName,body,state",
        )
        pr = json.loads(res.stdout)
        if pr.get("state") == "OPEN":
            return pr
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as e:
        print(f"Note: Could not query PR #{pr_number}: {e}", file=sys.stderr)
    return None


def sync_pr_for_update(
    update_info: PackageUpdate,
    existing_pr: dict[str, Any] | None = None,
) -> None:
    pkg = update_info["package"]
    new_ver = update_info["latest_version"]
    new_build = update_info["build_id"]

    if existing_pr is None:
        existing_pr = find_open_pr_for_package(pkg)

    branch_name = (
        existing_pr["headRefName"] if existing_pr else f"update/{pkg}-{new_ver}"
    )

    git("fetch", "--prune", "origin", check=False)

    # If an open PR already exists, check if it's already up-to-date with upstream and origin/master
    if existing_pr:
        pr_number = existing_pr["number"]
        remote_ref = f"origin/{branch_name}"
        remote_exists = (
            git("rev-parse", "--verify", remote_ref, check=False).returncode == 0
        )
        is_rebased = (
            remote_exists
            and git(
                "merge-base", "--is-ancestor", "origin/master", remote_ref, check=False
            ).returncode
            == 0
        )

        rel_spec_path = update_info["spec_path"].relative_to(REPO_ROOT)
        remote_spec = git("show", f"{remote_ref}:{rel_spec_path}", check=False)
        remote_ver: str | None = None
        remote_build: str | None = None
        if remote_spec.returncode == 0:
            for line in remote_spec.stdout.splitlines():
                v_match = re.match(r"^Version:\s*([^\s]+)", line)
                if v_match:
                    remote_ver = v_match.group(1).strip()
                b_match = re.match(r"^%global\s+build_id\s+([^\s]+)", line)
                if b_match:
                    remote_build = b_match.group(1).strip()

        if is_rebased and remote_ver == new_ver and remote_build == new_build:
            print(
                f"[{pkg}] Open PR #{pr_number} on '{branch_name}' is already up-to-date with upstream {new_ver} and origin/master."
            )
            return

        print(
            f"[{pkg}] Found open PR #{pr_number} on '{branch_name}'. Resetting cleanly from origin/master..."
        )
    else:
        print(f"[{pkg}] Creating branch '{branch_name}' from origin/master...")

    try:
        # Always reset the branch cleanly from origin/master to ensure exactly 1 commit
        git("checkout", "-B", branch_name, "origin/master")

        # Apply spec and README changes
        update_spec_file(update_info["spec_path"], new_ver, update_info["build_id"])
        update_readme_version(pkg, f"{new_ver}-1")

        # Commit and push changes
        status = git("status", "--porcelain", check=False).stdout.strip()
        if status:
            git("add", str(update_info["spec_path"]), "README.md")
            git("commit", "-m", f"chore({pkg}): bump to {new_ver}")
            git("push", "--force-with-lease", "-u", "origin", branch_name)
            print(f"[{pkg}] Pushed updated commit to '{branch_name}'.")
        else:
            print(
                f"[{pkg}] No changes detected after applying updates from origin/master."
            )

        # Update or create PR metadata
        title = f"chore({pkg}): update to {new_ver}"
        body = (
            f"Automated update for **{pkg}** to `{new_ver}`.\n\n"
            f"- Upstream Version: `{new_ver}`\n"
            f"- Download URLs:\n"
            f"{update_info['url']}\n\n"
            f"Review spec changes and merge to trigger Fedora COPR build."
        )

        if existing_pr:
            pr_number = existing_pr["number"]
            try:
                gh("pr", "edit", str(pr_number), "--title", title, "--body", body)
                print(f"[{pkg}] Updated PR #{pr_number} metadata.")
            except (subprocess.SubprocessError, OSError) as e:
                print(
                    f"[{pkg}] Note: Could not update PR metadata: {e}",
                    file=sys.stderr,
                )
        elif status:
            try:
                gh(
                    "pr",
                    "create",
                    "--title",
                    title,
                    "--body",
                    body,
                    "--head",
                    branch_name,
                    "--base",
                    "master",
                )
                print(f"[{pkg}] Created Pull Request for '{branch_name}'.")
            except subprocess.CalledProcessError as e:
                if "already exists" in (e.stderr or "").lower():
                    print(
                        f"[{pkg}] Pull Request already exists for '{branch_name}'.",
                        file=sys.stderr,
                    )
                else:
                    raise
    finally:
        git("checkout", "-f", "master", check=False)


# --- Main Entrypoint ---


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check for upstream updates and synchronize Fedora COPR packaging."
    )
    _ = parser.add_argument(
        "--create-pr", action="store_true", help="Create Git branch and PR via gh CLI."
    )
    _ = parser.add_argument(
        "--refresh",
        nargs="?",
        const="all",
        help="Rebase and sync open PR(s) against upstream and origin/master (e.g. '--refresh', '--refresh antigravity').",
    )
    _ = parser.add_argument(
        "--refresh-pr",
        type=int,
        help="Target a specific open PR number to rebase and refresh against upstream.",
    )
    _ = parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show full debug info, URLs, and origins.",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check versions without modifying spec files or creating/refreshing PRs.",
    )
    args = parser.parse_args()

    try:
        all_updates, latest_info = check_all(verbose=args.verbose)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"Warning: Failed to fetch upstream info: {e}", file=sys.stderr)
        return

    # Handle --refresh-pr <NUMBER>
    if args.refresh_pr:
        pr = get_open_pr_by_number(args.refresh_pr)
        if not pr:
            print(
                f"Error: Open PR #{args.refresh_pr} not found or is closed.",
                file=sys.stderr,
            )
            sys.exit(1)
        target_pkg = None
        for p in PACKAGES:
            head = pr.get("headRefName", "")
            title = pr.get("title", "")
            if re.search(rf"^update/{re.escape(p)}-v?\d", head) or f"({p})" in title:
                target_pkg = p
                break
        if not target_pkg or target_pkg not in latest_info:
            print(
                f"Error: Could not determine package for PR #{args.refresh_pr}",
                file=sys.stderr,
            )
            sys.exit(1)
        info = latest_info[target_pkg]
        print(
            f"Refreshing PR #{args.refresh_pr} for '{target_pkg}' (latest upstream: {info['latest_version']})..."
        )
        sync_pr_for_update(info, existing_pr=pr)
        return

    # Handle --refresh [all|pkg]
    if args.refresh:
        target_pkgs = list(PACKAGES.keys()) if args.refresh == "all" else [args.refresh]
        refreshed_any = False
        for p in target_pkgs:
            pr = find_open_pr_for_package(p)
            if pr:
                info = latest_info.get(p)
                if info:
                    print(f"Found open PR #{pr['number']} for '{p}'. Refreshing...")
                    sync_pr_for_update(info, existing_pr=pr)
                    refreshed_any = True
            else:
                up = all_updates.get(p)
                if up:
                    print(
                        f"No open PR for '{p}', but update {up['latest_version']} is available. Creating PR..."
                    )
                    sync_pr_for_update(up)
                    refreshed_any = True
        if not refreshed_any:
            print(
                "No open PRs found to refresh and all target packages are up to date."
            )
        return

    # Standard check / update flow
    updates = [up for up in all_updates.values() if up is not None]
    for pkg in PACKAGES:
        up = all_updates.get(pkg)
        if up:
            print(
                f"[{pkg}] Update available: {up['current_version']} -> {up['latest_version']}"
            )
        else:
            print(f"[{pkg}] Up to date.")

    if not updates:
        print("All packages are currently up-to-date with upstream.")
        return

    if args.dry_run:
        print("[dry-run] Check completed. No files modified.")
        return

    for up in updates:
        if args.create_pr:
            sync_pr_for_update(up)
        else:
            update_spec_file(up["spec_path"], up["latest_version"], up["build_id"])
            update_readme_version(up["package"], f"{up['latest_version']}-1")
            print(f"Updated spec file: {up['spec_path']}")


if __name__ == "__main__":
    main()
