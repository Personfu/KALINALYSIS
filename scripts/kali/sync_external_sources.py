#!/usr/bin/env python3
"""Mirror external source repositories into a local workspace via source archives."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

DEFAULT_MANIFEST = "data/kali/source-mirrors.json"
DEFAULT_STATE = "data/kali/source-sync-state.json"
DEFAULT_TIMEOUT = 120


class SyncError(RuntimeError):
    """Raised for expected sync failures."""


def http_json(url: str, timeout: int) -> dict:
    req = Request(url, headers={"User-Agent": "kali-source-sync/1.0", "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def download_to_file(url: str, destination: Path, timeout: int) -> None:
    req = Request(url, headers={"User-Agent": "kali-source-sync/1.0"})
    with urlopen(req, timeout=timeout) as response, destination.open("wb") as f:
        shutil.copyfileobj(response, f)


def github_source_details(source: dict, timeout: int) -> dict:
    owner = source["owner"]
    repo = source["repo"]
    api = http_json(f"https://api.github.com/repos/{owner}/{repo}", timeout)
    branch = source.get("ref") or api.get("default_branch")
    if not branch:
        raise SyncError(f"No branch found for github repo {owner}/{repo}")

    branch_api = http_json(f"https://api.github.com/repos/{owner}/{repo}/branches/{quote(branch)}", timeout)
    commit_sha = branch_api.get("commit", {}).get("sha")

    archive_url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{quote(branch)}"
    return {
        "provider": "github",
        "repository": f"{owner}/{repo}",
        "branch": branch,
        "commit": commit_sha,
        "archive_url": archive_url,
    }


def gitlab_source_details(source: dict, timeout: int) -> dict:
    project = source["project"]
    encoded_project = quote(project, safe="")
    api = http_json(f"https://gitlab.com/api/v4/projects/{encoded_project}", timeout)
    branch = source.get("ref") or api.get("default_branch")
    if not branch:
        raise SyncError(f"No branch found for gitlab project {project}")

    branch_api = http_json(
        f"https://gitlab.com/api/v4/projects/{encoded_project}/repository/branches/{quote(branch, safe='')}",
        timeout,
    )
    commit_sha = branch_api.get("commit", {}).get("id")

    archive_url = (
        f"https://gitlab.com/api/v4/projects/{encoded_project}/repository/archive.tar.gz?sha={quote(branch, safe='')}"
    )
    return {
        "provider": "gitlab",
        "repository": project,
        "branch": branch,
        "commit": commit_sha,
        "archive_url": archive_url,
    }


def resolve_source_details(source: dict, timeout: int) -> dict:
    host = source.get("host")
    if host == "github":
        return github_source_details(source, timeout)
    if host == "gitlab":
        return gitlab_source_details(source, timeout)
    raise SyncError(f"Unsupported host '{host}' for source {source.get('id')}")


def extract_archive(archive_path: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="kali-src-extract-") as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(archive_path, mode="r:gz") as tar:
            for member in tar.getmembers():
                member_target = (tmp_path / member.name).resolve()
                if not str(member_target).startswith(str(tmp_path.resolve())):
                    raise SyncError(f"Unsafe archive path detected: {member.name}")
            tar.extractall(path=tmp_path)

        extracted_entries = [p for p in tmp_path.iterdir() if p.is_dir()]
        if len(extracted_entries) == 1:
            root = extracted_entries[0]
            for item in root.iterdir():
                target = destination / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)
        else:
            for item in tmp_path.iterdir():
                target = destination / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)


def sync_source(source: dict, timeout: int, plan_only: bool) -> dict:
    if plan_only:
        details = {
            "repository": source.get("project") or f"{source.get('owner')}/{source.get('repo')}",
            "branch": source.get("ref") or "<default>",
            "commit": None,
            "archive_url": None,
        }
    else:
        details = resolve_source_details(source, timeout)
    record = {
        "id": source.get("id"),
        "host": source.get("host"),
        "target_dir": source.get("target_dir"),
        "repository": details.get("repository"),
        "branch": details.get("branch"),
        "commit": details.get("commit"),
        "archive_url": details.get("archive_url"),
        "status": "planned" if plan_only else "synced",
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    if plan_only:
        return record

    archive_target = Path(tempfile.mkdtemp(prefix="kali-source-archive-")) / "archive.tar.gz"
    try:
        download_to_file(details["archive_url"], archive_target, timeout)
        extract_archive(archive_target, Path(source["target_dir"]))
    finally:
        if archive_target.exists():
            archive_target.unlink(missing_ok=True)
        archive_dir = archive_target.parent
        if archive_dir.exists():
            shutil.rmtree(archive_dir, ignore_errors=True)

    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--state", default=DEFAULT_STATE)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--plan-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = manifest.get("sources", [])
    if args.source:
        wanted = set(args.source)
        sources = [s for s in sources if s.get("id") in wanted]

    results = []
    errors = []

    for source in sources:
        source_id = source.get("id", "<unknown>")
        try:
            result = sync_source(source, timeout=args.timeout, plan_only=args.plan_only)
            results.append(result)
            print(f"[{source_id}] {result['status']} ({result.get('branch')} @ {result.get('commit')})")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            errors.append({"id": source_id, "error": str(exc)})
            print(f"[{source_id}] error: {exc}", file=sys.stderr)

    state = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "manifest": str(manifest_path),
        "plan_only": args.plan_only,
        "results": results,
        "errors": errors,
    }

    state_path = Path(args.state)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
