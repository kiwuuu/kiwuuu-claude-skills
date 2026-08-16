# CatchUp Workflow — Zero to Speed

Get fully up to speed from zero context in under 60 seconds. Read project state, check what changed, verify everything works.

Trigger: `/ultimate-loop catch-up` or at session start when context is fresh.

## Configuration

Before using this workflow, set these variables to match your project:

```bash
APP_ROOT="/your/app/root"        # e.g. /root/myapp
WEB_ROOT="/var/www/yourapp"      # e.g. /var/www/myapp
CONTEXT_DIR="/your/context/dir"  # Directory with your session notes / handoff files
LOG_DIR="/your/app/logs"         # Your application log directory
```

## Execution

### Step 1: Read Core Context Files (Parallel)

**Read `_now.md` first.** It is the live session-state file the `session-state` skill
maintains at the vault root (`$CONTEXT_DIR/_now.md`) — Active/Waiting/Parked thread
tables where every `next` is executable without asking. If it exists, it is the
authority on what's in flight; everything below only fills in detail.

Then the supporting context files — adapt paths to wherever you store project memory:

```
$CONTEXT_DIR/_now.md        — Live state: active threads, next actions, blockers  ← READ FIRST
$CONTEXT_DIR/HANDOFF.md     — Session state, what was done, what's pending
$CONTEXT_DIR/CHANGELOG.md   — Recent changes log
$CONTEXT_DIR/PRIORITIES.md  — Current task priorities
```

> Tip: if you don't have structured handoff files, read your git log and README instead.

Then run the state doctor — it mechanizes the staleness and expiry checks (stale Active
rows, dead Waiting rows, index drift, `_now.md` behind the vault's git HEAD) so none of
them depend on you noticing:

```bash
python3 <skills>/session-state/scripts/now_doctor.py --report
```

Carry its findings into the session brief verbatim. If it reports STALE, trust git over
`_now.md` — stale state presented as current is worse than none. Also glance at
`$CONTEXT_DIR/_breadcrumbs/*.log`: if the last entry there is newer than `_now.md`'s
update, a session ended without a handoff and the breadcrumb says what it touched.

### Step 2: Check What Changed Since Last Session

```bash
# Recent file changes (last 24 hours) — adapt paths to your project
find $APP_ROOT \( -name "*.js" -o -name "*.py" \) -mtime -1 2>/dev/null | head -20
find $WEB_ROOT -mtime -1 2>/dev/null | head -20

# Git log (last 5 commits)
cd $APP_ROOT && git log --oneline -5 2>/dev/null

# PM2 restart counts (indicates crashes or deployments)
sudo /usr/local/bin/pm2 jlist 2>/dev/null | python3 -c "
import json, sys
procs = json.load(sys.stdin)
for p in procs:
    restarts = p.get('pm2_env', {}).get('restart_time', 0)
    name = p.get('name', '?')
    if restarts > 0:
        print(f'  {name}: {restarts} restarts')
"
```

### Step 3: Quick Health Check

Run the Quick workflow endpoints + PM2 check:

```bash
# Adapt URLs to your project
for url in "https://your-domain.com" "https://app.your-domain.com" "http://localhost:YOUR_PORT/health"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "User-Agent: Mozilla/5.0" "$url" 2>/dev/null)
  echo "$code $url"
done

# Resources
df -h / | tail -1
free -h | head -3
```

### Step 4: Check Pending Actions

```bash
# Recent log activity
tail -20 $LOG_DIR/cron.log 2>/dev/null || tail -20 $LOG_DIR/app.log 2>/dev/null

# Your pending queue checks here
# e.g. python3 $APP_ROOT/scripts/status.py 2>/dev/null | head -10
```

### Step 5: Generate Session Brief

Output a concise brief:

```
## Session Brief — [populate with: python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d %H:%M'))"]

**Last Session:** [key actions from _now.md or git log]
**Services:** [X/X] online
**Resources:** Disk X% | RAM X% | Swap X%
**Recent Changes:** [files modified in last 24h]
**Pending Actions:** [from HANDOFF / issue tracker]
**Recommended First Action:** [highest-priority task]
```

## Integration with Full Loop

After CatchUp, if any health issues are detected, automatically trigger the Full workflow for deeper verification.

## Done

You're caught up. Context loaded, health verified, priorities identified. Execute the recommended first action.
