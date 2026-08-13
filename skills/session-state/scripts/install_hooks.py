#!/usr/bin/env python3
"""Cross-platform installer for the anti-catchup hooks (Windows/macOS/Linux).

    python skills/session-state/scripts/install_hooks.py

Merges into <home>/.claude/settings.json — backs up first, idempotent, never
clobbers other hooks. Installs:

    Stop       -> now_doctor.py --guard      (block stop once if state unsaved)
    SessionEnd -> session_breadcrumb.py      (mechanical facts, always)

Hook commands are built from sys.executable and this file's absolute location,
so they survive any install path and need no bash, no WSL, no PATH luck. If a
previous install points at an old checkout location, the entry is updated in
place rather than duplicated.
"""

import json
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SETTINGS = Path.home() / ".claude" / "settings.json"

HOOK_SPECS = [
    ("Stop", "now_doctor.py", "--guard"),
    ("SessionEnd", "session_breadcrumb.py", ""),
]


def build_command(script_name, extra):
    script = SCRIPT_DIR / script_name
    if not script.is_file():
        sys.exit(f"error: {script} not found — run this from a full checkout")
    # Quote both paths: Windows interpreters commonly live under "Program Files".
    cmd = f'"{sys.executable}" "{script}"'
    return f"{cmd} {extra}".strip()


def main():
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    if SETTINGS.is_file():
        raw = SETTINGS.read_text(encoding="utf-8")
        try:
            settings = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            sys.exit(f"error: {SETTINGS} is not valid JSON ({exc}) — fix it first, nothing was changed")
        backup = SETTINGS.with_suffix(f".json.bak.{int(time.time())}")
        backup.write_text(raw, encoding="utf-8")
    else:
        settings = {}
        backup = None

    hooks = settings.setdefault("hooks", {})
    report = []

    for event, script_name, extra in HOOK_SPECS:
        command = build_command(script_name, extra)
        groups = hooks.setdefault(event, [])
        found = False
        for group in groups:
            for hook in group.get("hooks", []):
                if script_name in hook.get("command", ""):
                    found = True
                    if hook["command"] != command:
                        hook["command"] = command  # checkout moved; repoint
                        report.append(f"{event}: updated path -> {script_name}")
                    else:
                        report.append(f"{event}: already installed")
        if not found:
            groups.append({"hooks": [{"type": "command", "command": command}]})
            report.append(f"{event}: installed -> {script_name}")

    SETTINGS.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    for line in report:
        print(line)
    if backup:
        print(f"backup: {backup}")
    print(f"settings: {SETTINGS}")
    print("Restart Claude Code to pick the hooks up.")


if __name__ == "__main__":
    main()
