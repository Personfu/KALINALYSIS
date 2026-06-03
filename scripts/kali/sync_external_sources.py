#!/usr/bin/env python3
"""
sync_external_sources.py
========================
Clone or update all mirror targets defined in source-mirrors.json, then
write a fresh source-sync-state.json with per-repo timestamps and statuses.

Usage
-----
  python scripts/kali/sync_external_sources.py \\
    --mirrors data/kali/source-mirrors.json \\
    --state   data/kali/source-sync-state.json \\
    --dest    external_sources/

Options
-------
  --mirrors  PATH  Path to source-mirrors.json
  --state    PATH  Path to write source-sync-state.json
  --dest     PATH  Base directory for cloned repositories
  --dry-run        Print what would be done without executing
  --verbose        Emit verbose logging
  --only     ID    Sync only the mirror with this source_id (repeatable)
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger("sync_external_sources")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    log.info("Wrote %s", path)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    log.debug("RUN %s  (cwd=%s)", " ".join(cmd), cwd)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=True,
        text=True,
    )


def get_head_sha(repo_dir: Path) -> str:
    """Return the current HEAD commit SHA of a git repo."""
    result = run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
    return result.stdout.strip()


def source_url_for_id(sources: list[dict], source_id: str) -> str | None:
    for s in sources:
        if s.get("id") == source_id:
            return s.get("url")
    return None


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------


def sync_mirror(
    mirror: dict,
    dest_base: Path,
    source_url: str,
    dry_run: bool = False,
) -> dict:
    """Clone or update a single mirror. Returns a state record."""

    local_path = dest_base / mirror["local_path"]
    branch = mirror.get("branch", "main")
    strategy = mirror.get("strategy", "shallow")
    depth = mirror.get("depth", 1)
    hook = mirror.get("post_sync_hook")
    source_id = mirror["source_id"]

    started_at = datetime.now(timezone.utc).isoformat()

    if dry_run:
        log.info("[DRY RUN] Would sync %s → %s", source_url, local_path)
        return {
            "source_id": source_id,
            "local_path": str(local_path),
            "last_synced": started_at,
            "commit_sha": "dry-run",
            "status": "dry-run",
            "error": None,
        }

    try:
        if (local_path / ".git").exists():
            log.info("Updating %s …", local_path)
            run(["git", "fetch", "--prune", "origin"], cwd=local_path)
            run(["git", "checkout", branch], cwd=local_path)
            run(["git", "reset", "--hard", f"origin/{branch}"], cwd=local_path)
        else:
            log.info("Cloning %s → %s …", source_url, local_path)
            local_path.mkdir(parents=True, exist_ok=True)
            clone_cmd = ["git", "clone", "--branch", branch]
            if strategy == "shallow":
                clone_cmd += ["--depth", str(depth)]
            clone_cmd += [source_url, str(local_path)]
            run(clone_cmd)

        sha = get_head_sha(local_path)

        if hook:
            hook_path = Path(hook)
            if hook_path.exists() and os.access(hook_path, os.X_OK):
                log.info("Running post-sync hook: %s", hook_path)
                subprocess.run([str(hook_path)], check=True, cwd=str(local_path))
            else:
                log.warning("Post-sync hook not found or not executable: %s", hook_path)

        return {
            "source_id": source_id,
            "local_path": str(local_path),
            "last_synced": datetime.now(timezone.utc).isoformat(),
            "commit_sha": sha,
            "status": "success",
            "error": None,
        }

    except subprocess.CalledProcessError as exc:
        err_msg = exc.stderr.strip() if exc.stderr else str(exc)
        log.error("Failed to sync %s: %s", source_id, err_msg)
        return {
            "source_id": source_id,
            "local_path": str(local_path),
            "last_synced": started_at,
            "commit_sha": None,
            "status": "error",
            "error": err_msg[:500],
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync external source mirrors for KALINALYSIS."
    )
    parser.add_argument("--mirrors", default="data/kali/source-mirrors.json")
    parser.add_argument("--state",   default="data/kali/source-sync-state.json")
    parser.add_argument("--dest",    default="external_sources")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--only",    action="append", dest="only_ids", default=[])
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.verbose:
        log.setLevel(logging.DEBUG)

    mirrors_path = Path(args.mirrors)
    state_path   = Path(args.state)
    dest_base    = Path(args.dest)

    mirrors_data  = load_json(mirrors_path)
    mirrors       = mirrors_data.get("mirrors", [])

    # Load sources for URL lookup
    sources_path = mirrors_path.parent / "sources.json"
    sources = load_json(sources_path).get("sources", []) if sources_path.exists() else []

    if args.only_ids:
        mirrors = [m for m in mirrors if m["source_id"] in args.only_ids]
        log.info("Filtering to %d mirror(s): %s", len(mirrors), args.only_ids)

    run_start = datetime.now(timezone.utc)
    repo_states: list[dict] = []

    for mirror in mirrors:
        if not mirror.get("enabled", True):
            log.info("Skipping disabled mirror: %s", mirror["source_id"])
            continue

        url = source_url_for_id(sources, mirror["source_id"])
        if not url:
            log.warning("No URL found for source_id=%s; skipping.", mirror["source_id"])
            continue

        state = sync_mirror(mirror, dest_base, url, dry_run=args.dry_run)
        repo_states.append(state)

    run_end = datetime.now(timezone.utc)
    duration = (run_end - run_start).total_seconds()
    errors = [r for r in repo_states if r["status"] == "error"]
    overall = "error" if errors else ("dry-run" if args.dry_run else "success")

    state_data = {
        "_meta": {
            "schema_version": "1.0",
            "description": "Runtime sync state written by sync_external_sources.py. Do not edit manually.",
            "last_run": run_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "run_duration_seconds": round(duration, 1),
            "overall_status": overall,
        },
        "repos": repo_states,
    }

    if not args.dry_run:
        write_json(state_path, state_data)
    else:
        log.info("[DRY RUN] Would write state to %s", state_path)

    if errors:
        log.error("%d mirror(s) failed: %s", len(errors), [e["source_id"] for e in errors])
        return 1

    log.info("All mirrors synced successfully in %.1fs.", duration)
    return 0


if __name__ == "__main__":
    sys.exit(main())
