#!/usr/bin/env python3
"""SessionEnd hook: leave mechanical facts even when no handoff happened.

Appends one entry to <vault>/_breadcrumbs/<hostname>.log recording what this
session's workspace looks like at the moment the session ended: per-repo
branch, the commits made since _now.md was last updated, and dirty-file
counts. No judgment, no LLM — facts a script can gather, so the safety net
needs zero discipline to function.

Per-hostname files on purpose: two machines ending sessions offline can never
write the same file, so Syncthing has nothing to conflict on. The log is
trimmed to the newest entries and never committed by this script — the next
session's handoff commit carries it, or Syncthing does.

Failure policy: exit 0 on every error. A breadcrumb is a bonus, never a cost.
"""

import json
import os
import re
import socket
import subprocess
import sys
import time

# Enough history to reconstruct "what happened on this machine lately"
# without the log becoming an archive; git and _now.md hold real history.
KEEP_ENTRIES = 10

ENTRY_MARK = "=== session "


def git(args, cwd):
    try:
        out = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def find_vault(start):
    env = os.environ.get("MEMPALACE_ROOT")
    if env and os.path.isfile(os.path.join(env, "_now.md")):
        return env
    here = os.path.abspath(start)
    for base in (here, os.path.dirname(here), os.path.expanduser("~")):
        for name in ("kiwuuu-mempalace", "mempalace"):
            cand = os.path.join(base, name)
            if os.path.isfile(os.path.join(cand, "_now.md")):
                return cand
    return None


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    cwd = payload.get("cwd") or os.getcwd()

    vault = find_vault(cwd)
    if not vault:
        return 0

    now_epoch = 0
    out = git(["log", "-1", "--format=%ct", "--", "_now.md"], vault)
    if out.isdigit():
        now_epoch = int(out)

    root = git(["rev-parse", "--show-toplevel"], cwd) or cwd
    parent = os.path.dirname(root)
    repos = []
    try:
        for entry in sorted(os.listdir(parent))[:20]:
            cand = os.path.join(parent, entry)
            if os.path.isdir(os.path.join(cand, ".git")):
                repos.append(cand)
    except OSError:
        repos = [root]

    lines = [
        f"{ENTRY_MARK}{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} "
        f"(id {payload.get('session_id', 'unknown')[:12]}) ==="
    ]
    for repo in repos:
        branch = git(["rev-parse", "--abbrev-ref", "HEAD"], repo) or "?"
        since = (
            ["--since", time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now_epoch))]
            if now_epoch
            else ["-5"]
        )
        commits = git(["log", "--format=%h %s"] + since, repo).split("\n")
        commits = [c for c in commits if c][:5]
        dirty = git(["status", "--porcelain"], repo).split("\n")
        dirty = [d for d in dirty if d]
        if not commits and not dirty:
            continue  # untouched repos are noise
        lines.append(f"  {os.path.basename(repo)} @ {branch}"
                     f" — {len(commits)} commit(s) since handoff, {len(dirty)} dirty")
        for c in commits:
            lines.append(f"    {c}")

    if len(lines) == 1:
        return 0  # nothing happened; leave no crumb

    crumb_dir = os.path.join(vault, "_breadcrumbs")
    os.makedirs(crumb_dir, exist_ok=True)
    path = os.path.join(crumb_dir, f"{socket.gethostname()}.log")

    existing = ""
    if os.path.isfile(path):
        existing = open(path, encoding="utf-8").read()
    entries = [e for e in re.split(rf"(?=^{re.escape(ENTRY_MARK)})", existing, flags=re.MULTILINE) if e.strip()]
    entries.append("\n".join(lines) + "\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(e.rstrip("\n") for e in entries[-KEEP_ENTRIES:]) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
