#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["tiktoken==0.12.0"]
# ///
"""Measure the token cost of commands' stdout, as an agent receives it.

Each argument after `--` is one shell command. It runs with stdout piped (not
a terminal), which is what an agent's tool call sees. Prints one JSON object.
The tokenizer (o200k_base) is a proxy: compare before/after, don't treat the
absolute numbers as any specific model's billing.
"""

import json
import subprocess
import sys

import tiktoken


def measure(commands, timeout=120):
    enc = tiktoken.get_encoding("o200k_base")
    rows = []
    for cmd in commands:
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                  timeout=timeout)
            out, code = proc.stdout, proc.returncode
        except subprocess.TimeoutExpired:
            out, code = "", None
        rows.append({"command": cmd, "tokens": len(enc.encode(out)),
                     "bytes": len(out.encode()), "exit": code})
    return {"ok": all(r["exit"] == 0 for r in rows), "tokenizer": "o200k_base (proxy)",
            "total_tokens": sum(r["tokens"] for r in rows), "commands": rows}


def main(argv):
    if "--" not in argv or argv.index("--") == len(argv) - 1:
        print(json.dumps({"ok": False, "error": {"code": "USAGE", "message":
              "usage: token_cost.py -- 'cmd one' ['cmd two' ...]"}}))
        return 2
    result = measure(argv[argv.index("--") + 1:])
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
