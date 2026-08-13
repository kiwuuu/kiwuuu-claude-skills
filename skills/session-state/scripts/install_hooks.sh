#!/usr/bin/env bash
# Install the anti-catchup hooks into ~/.claude/settings.json (user level, all
# projects). Merges — never clobbers existing hooks; backs up first; idempotent.
#
#   bash skills/session-state/scripts/install_hooks.sh
#
# Installs:
#   Stop       → now_doctor.py --guard      (block stop once if state unsaved)
#   SessionEnd → session_breadcrumb.py      (mechanical facts, always)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS="${HOME}/.claude/settings.json"

GUARD_CMD="python3 ${SCRIPT_DIR}/now_doctor.py --guard"
CRUMB_CMD="python3 ${SCRIPT_DIR}/session_breadcrumb.py"

mkdir -p "${HOME}/.claude"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
cp "$SETTINGS" "${SETTINGS}.bak.$(date +%s)"

python3 - "$SETTINGS" "$GUARD_CMD" "$CRUMB_CMD" <<'PY'
import json, sys

path, guard_cmd, crumb_cmd = sys.argv[1], sys.argv[2], sys.argv[3]
settings = json.load(open(path))
hooks = settings.setdefault("hooks", {})

def ensure(event, command):
    groups = hooks.setdefault(event, [])
    for group in groups:
        for hook in group.get("hooks", []):
            if hook.get("command") == command:
                return False  # already installed
    groups.append({"hooks": [{"type": "command", "command": command}]})
    return True

added = []
if ensure("Stop", guard_cmd):
    added.append("Stop → handoff guard")
if ensure("SessionEnd", crumb_cmd):
    added.append("SessionEnd → breadcrumb")

json.dump(settings, open(path, "w"), indent=2)
print("installed: " + (", ".join(added) if added else "nothing (already present)"))
PY

echo "Hooks live in ${SETTINGS}; backup saved alongside. Restart Claude Code to pick them up."
