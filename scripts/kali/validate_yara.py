#!/usr/bin/env python3
"""
validate_yara.py
================
Validate all YARA rule files under a directory tree, reporting parse
errors and basic style warnings.

Usage
-----
  python scripts/kali/validate_yara.py --rules-dir yara/rules/

Options
-------
  --rules-dir  PATH   Directory containing .yar / .yara rule files (default: yara/rules)
  --recursive         Recurse into subdirectories (default: True)
  --verbose           Print rule names as they are validated
  --strict            Treat warnings as errors (non-zero exit on warnings)
"""

import argparse
import logging
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger("validate_yara")

try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Validate YARA rules in KALINALYSIS.")
    parser.add_argument("--rules-dir",  default="yara/rules")
    parser.add_argument("--recursive",  action="store_true", default=True)
    parser.add_argument("--verbose",    action="store_true")
    parser.add_argument("--strict",     action="store_true")
    return parser.parse_args(argv)


def collect_rule_files(rules_dir: Path, recursive: bool) -> list[Path]:
    patterns = ["*.yar", "*.yara"]
    files: list[Path] = []
    for pattern in patterns:
        if recursive:
            files.extend(rules_dir.rglob(pattern))
        else:
            files.extend(rules_dir.glob(pattern))
    return sorted(set(files))


def validate_with_yara_lib(rule_files: list[Path], verbose: bool) -> tuple[int, int, int]:
    """Return (ok_count, warning_count, error_count)."""
    ok = warn = err = 0
    for path in rule_files:
        try:
            compiled = yara.compile(filepath=str(path))
            if verbose:
                log.info("OK       %s", path)
            ok += 1
            # Basic style checks
            text = path.read_text(encoding="utf-8", errors="replace")
            if "TODO" in text or "FIXME" in text:
                log.warning("WARN     %s — contains TODO/FIXME markers", path)
                warn += 1
        except yara.SyntaxError as exc:
            log.error("ERROR    %s — %s", path, exc)
            err += 1
        except Exception as exc:
            log.error("ERROR    %s — unexpected: %s", path, exc)
            err += 1
    return ok, warn, err


def validate_without_yara_lib(rule_files: list[Path], verbose: bool) -> tuple[int, int, int]:
    """
    Lightweight textual heuristic validation when the `yara-python` library
    is not installed. Checks for obvious structural issues only.
    """
    log.warning(
        "yara-python not installed — falling back to text-based heuristic validation. "
        "Install with: pip install yara-python"
    )
    ok = warn = err = 0
    for path in rule_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        issues: list[str] = []
        # Must contain at least one rule block
        if "rule " not in text:
            issues.append("no 'rule' keyword found")
        # Must have condition section
        if "condition:" not in text:
            issues.append("missing 'condition:' section")
        # Check for unclosed braces (rough)
        if text.count("{") != text.count("}"):
            issues.append("unbalanced braces")
        # Style warnings
        if "TODO" in text or "FIXME" in text:
            log.warning("WARN     %s — contains TODO/FIXME markers", path)
            warn += 1
        if issues:
            for issue in issues:
                log.error("ERROR    %s — %s", path, issue)
            err += 1
        else:
            if verbose:
                log.info("OK       %s", path)
            ok += 1
    return ok, warn, err


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.verbose:
        log.setLevel(logging.DEBUG)

    rules_dir = Path(args.rules_dir)
    if not rules_dir.exists():
        log.error("Rules directory not found: %s", rules_dir)
        return 2

    rule_files = collect_rule_files(rules_dir, args.recursive)
    if not rule_files:
        log.warning("No .yar/.yara files found under %s", rules_dir)
        return 0

    log.info("Validating %d rule file(s) under %s …", len(rule_files), rules_dir)

    if YARA_AVAILABLE:
        ok, warn, err = validate_with_yara_lib(rule_files, args.verbose)
    else:
        ok, warn, err = validate_without_yara_lib(rule_files, args.verbose)

    log.info("Results: %d OK, %d warning(s), %d error(s)", ok, warn, err)

    if err:
        return 1
    if warn and args.strict:
        log.error("Strict mode: treating %d warning(s) as errors.", warn)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
