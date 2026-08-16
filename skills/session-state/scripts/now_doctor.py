#!/usr/bin/env python3
"""Health checks for the anti-catchup loop. Two modes, one file.

--report (default): human-readable rot report for _now.md and the vault.
    Run by ultimate-loop CatchUp at session start. Flags:
      - Active rows untouched past their shelf life
      - Waiting-on rows old enough to be presumed dead
      - Parked rows with no wake condition
      - _now.md older than the vault's newest commit (stale state)
      - _index.md total_files drifted from the actual file count
      - latest breadcrumb per machine, so silent sessions still leave a trace

--guard: Claude Code Stop-hook mode. Reads the hook JSON on stdin. If this
    session committed work more recent than _now.md's last update, prints a
    block decision so the harness makes Claude run the handoff before
    stopping. Nags at most once per session; any internal error exits 0 —
    a guard must never break the session it guards.

Zero dependencies. Self-contained on purpose: hooks execute this file
directly with no package context, so nothing here may import siblings.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time

# An "active" thread nobody stamped for a week isn't active — it's either done
# (delete the row) or blocked (move to Waiting on).
ACTIVE_STALE_DAYS = 7

# A blocker nobody has chased for a month is presumed dead: confirm or delete.
WAITING_DEAD_DAYS = 30

# Commits made within this window of _now.md's own commit are the same
# wrap-up burst (handoff commits land seconds around the work they describe).
GUARD_SLACK_SECONDS = 120

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def find_vault(start=None):
    """Locate the mempalace vault: $MEMPALACE_ROOT, then nearby checkouts."""
    env = os.environ.get("MEMPALACE_ROOT")
    if env and os.path.isfile(os.path.join(env, "_now.md")):
        return env
    here = os.path.abspath(start or os.getcwd())
    candidates = []
    for base in (here, os.path.dirname(here), os.path.expanduser("~")):
        candidates.append(os.path.join(base, "kiwuuu-mempalace"))
        candidates.append(os.path.join(base, "mempalace"))
    candidates.append(os.path.expanduser("~/vaults/mempalace"))
    for cand in candidates:
        if os.path.isfile(os.path.join(cand, "_now.md")):
            return cand
    return None


def git(args, cwd):
    try:
        out = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def last_commit_epoch(repo, path=None):
    args = ["log", "-1", "--format=%ct"]
    if path:
        args += ["--", path]
    out = git(args, repo)
    return int(out) if out.isdigit() else 0


def parse_now_tables(text):
    """Return {section: [row_line, ...]} for the three state tables."""
    sections = {"Active": [], "Waiting on": [], "Parked": []}
    current = None
    for line in text.split("\n"):
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            name = heading.group(1)
            current = name if name in sections else None
            continue
        if current and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells or re.match(r"^[-: ]+$", cells[0]):
                continue
            if cells[0].lower() in ("thread",):
                continue
            sections[current].append(cells)
    return sections


def newest_date_epoch(cells):
    """Newest YYYY-MM-DD found anywhere in the row, as epoch. 0 if none."""
    dates = DATE_RE.findall(" | ".join(cells))
    if not dates:
        return 0
    newest = max(dates)
    try:
        return int(time.mktime(time.strptime(newest, "%Y-%m-%d")))
    except ValueError:
        return 0


def days_old(epoch, now=None):
    if epoch <= 0:
        return None
    return int(((now or time.time()) - epoch) / 86400)


# ── report mode ────────────────────────────────────────────────────────────────


def report(vault):
    now_path = os.path.join(vault, "_now.md")
    text = open(now_path, encoding="utf-8").read()
    tables = parse_now_tables(text)
    findings = []

    for cells in tables["Active"]:
        age = days_old(newest_date_epoch(cells))
        if age is None:
            findings.append(f"ACTIVE  '{cells[0]}' has no date — undateable rows can't expire")
        elif age > ACTIVE_STALE_DAYS:
            findings.append(
                f"ACTIVE  '{cells[0]}' untouched {age}d (> {ACTIVE_STALE_DAYS}d) — "
                "finish it, delete it, or move it to Waiting on"
            )

    for cells in tables["Waiting on"]:
        age = days_old(newest_date_epoch(cells))
        if age is not None and age > WAITING_DEAD_DAYS:
            findings.append(
                f"WAITING '{cells[0]}' blocked {age}d (> {WAITING_DEAD_DAYS}d) — "
                "presumed dead: chase the blocker or delete the row"
            )

    for cells in tables["Parked"]:
        wake = cells[2] if len(cells) > 2 else ""
        if not wake:
            findings.append(f"PARKED  '{cells[0]}' has no wake condition — parked forever is deleted slowly")

    now_epoch = last_commit_epoch(vault, "_now.md") or int(os.path.getmtime(now_path))
    head_epoch = last_commit_epoch(vault)
    if head_epoch - now_epoch > GUARD_SLACK_SECONDS:
        gap_days = max(0, int((head_epoch - now_epoch) / 86400))
        findings.append(
            f"STALE   _now.md last updated {gap_days}d before the vault's newest commit — "
            "work was committed after the last handoff; trust git, then re-run handoff"
        )

    index_path = os.path.join(vault, "_index.md")
    if os.path.isfile(index_path):
        idx = open(index_path, encoding="utf-8").read()
        match = re.search(r"^total_files:\s*(\d+)", idx, re.MULTILINE)
        actual = 0
        for root, dirs, files in os.walk(vault):
            dirs[:] = [d for d in dirs if d != ".git"]
            actual += sum(1 for f in files if f.endswith(".md"))
        if match and int(match.group(1)) != actual:
            findings.append(
                f"INDEX   _index.md claims {match.group(1)} files, actual {actual} — regenerate the index"
            )

    crumb_dir = os.path.join(vault, "_breadcrumbs")
    if os.path.isdir(crumb_dir):
        for fname in sorted(os.listdir(crumb_dir)):
            path = os.path.join(crumb_dir, fname)
            age = days_old(os.path.getmtime(path))
            print(f"  breadcrumb {fname}: last session {age}d ago")

    if findings:
        print(f"NOW DOCTOR — {len(findings)} finding(s):")
        for f in findings:
            print(f"  [{f.split()[0]}] {f[len(f.split()[0]):].strip()}")
        return 1
    print("NOW DOCTOR — clean. State is current, nothing expired, index matches.")
    return 0


# ── guard mode (Stop hook) ─────────────────────────────────────────────────────


def guard():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    if payload.get("stop_hook_active"):
        return 0  # we already blocked once this turn-chain; never loop

    session_id = payload.get("session_id", "unknown")
    marker = os.path.join(
        tempfile.gettempdir(), f"session-state-guard-{session_id}"
    )
    if os.path.exists(marker):
        return 0  # one nag per session, maximum

    cwd = payload.get("cwd") or os.getcwd()
    vault = find_vault(cwd)
    if not vault:
        return 0  # no vault, nothing to guard

    now_epoch = last_commit_epoch(vault, "_now.md")
    if now_epoch == 0:
        now_path = os.path.join(vault, "_now.md")
        now_epoch = int(os.path.getmtime(now_path)) if os.path.isfile(now_path) else 0

    # Workspace = the cwd's repo plus sibling checkouts one level up.
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

    newest_work = max((last_commit_epoch(r) for r in repos), default=0)

    if newest_work > now_epoch + GUARD_SLACK_SECONDS:
        with open(marker, "w") as fh:
            fh.write(str(int(time.time())))
        print(json.dumps({
            "decision": "block",
            "reason": (
                "Handoff guard: this workspace has commits newer than _now.md's last "
                "update. Before finishing, run the session-state handoff — update the "
                "vault's _now.md (Active/Waiting/Parked, every `next` executable "
                "cold), commit, push. If you are genuinely mid-task, update just your "
                "thread's row now; the guard will not fire again this session."
            ),
        }))
    return 0


def main():
    if "--guard" in sys.argv:
        return guard()
    vault = find_vault()
    if not vault:
        print("NOW DOCTOR — no vault found ($MEMPALACE_ROOT unset, no checkout nearby)")
        return 0
    return report(vault)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # a guard/doctor must never take the session down
        print(f"now_doctor: swallowed error: {exc}", file=sys.stderr)
        sys.exit(0)
