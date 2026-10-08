#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema==4.25.1"]
# ///
"""Validate declared report structure/completeness, never execute evidence."""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / "report.schema.json"


def validate_report(report):
    """Return a JSON envelope and exit code; evidence truth is always unknown."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    error = next(Draft202012Validator(schema).iter_errors(report), None)
    if error is not None:
        # Do not echo arbitrary private values from a submitted report.
        return {"ok": False, "evidence_verified": False, "error": {
            "code": "INVALID_REPORT", "message": "Report does not match report.schema.json",
            "path": list(error.absolute_path), "rule": error.validator,
        }}, 2
    incomplete = [name for name, gate in report["gates"].items()
                  if gate["status"] in ("fail", "unverified")]
    return {"ok": True, "evidence_verified": False, "result": {
        "format_valid": True, "claims_complete": not incomplete,
        "incomplete_gates": incomplete,
    }}, 3 if incomplete else 0


def run(args, stdin, stdout):
    if len(args) != 1:
        result, code = {"ok": False, "evidence_verified": False, "error": {
            "code": "USAGE", "message": "Usage: validate_report.py <report.json|->",
        }}, 2
    else:
        try:
            raw = stdin.read() if args[0] == "-" else Path(args[0]).read_text(encoding="utf-8")
            result, code = validate_report(json.loads(raw))
        except (OSError, UnicodeError, ValueError, RecursionError):
            result, code = {"ok": False, "evidence_verified": False, "error": {
                "code": "INVALID_INPUT", "message": "Cannot read valid UTF-8 JSON report",
            }}, 2
    stdout.write(json.dumps(result, ensure_ascii=True) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:], sys.stdin, sys.stdout))
