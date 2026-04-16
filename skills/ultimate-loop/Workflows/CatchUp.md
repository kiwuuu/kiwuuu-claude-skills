# CatchUp Workflow — Zero to Speed

Get fully up to speed from zero context in under 60 seconds. Read everything that matters, check what changed, verify everything works.

Trigger: `/ultimate-loop catch-up` or at session start when context is fresh.

## Execution

### Step 1: Read Core Context Files (Parallel)

Read these files in parallel to load full project state:

```
/root/claude-skills/memory/HANDOFF.md          — Session state, what was done, what's pending
/root/claude-skills/memory/PHONE_LOG.md        — Activity from phone CLI sessions
/root/claude-skills/memory/MASTER_PROMPT.md    — The operating manual (skim sections 1-4)
/root/claude-skills/SOUL.md                    — Identity and behavioral context
```

### Step 2: Check What Changed Since Last Session

```bash
# Recent file changes (last 24 hours)
find /root/kiwubot \( -name "*.js" -o -name "*.py" \) -mtime -1 2>/dev/null | head -20
find /var/www/kiwuuu -mtime -1 2>/dev/null | head -20

# Git log (last 5 commits)
cd /root/kiwubot && git log --oneline -5 2>/dev/null
cd /root/claude-skills && git log --oneline -5 2>/dev/null

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
for url in "https://kiwuuu.com" "https://app.kiwuuu.com" "http://localhost:4000/health" "http://localhost:3003/health"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "User-Agent: Mozilla/5.0" "$url" 2>/dev/null)
  echo "$code $url"
done

# Resources
df -h / | tail -1
free -h | head -3
```

### Step 4: Check Pending Actions

```bash
# Cold email status
python3 /root/kiwubot/social/cold_email_sequencer.py status 2>/dev/null | head -10

# Content queue
ls /root/kiwubot/social/content_bank/brainstorm_$(date +%Y-%m-%d).md 2>/dev/null && echo "Today's brainstorm exists" || echo "No brainstorm for today"

# Recent cron activity
tail -20 /root/kiwubot/social/cron.log 2>/dev/null

# Check for any replies/notifications
tail -5 /var/log/kiwuuu-outreach.log 2>/dev/null
```

### Step 5: Generate Session Brief

Output a concise brief:

```
## Session Brief — [populate with: python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d %H:%M'))"]

**Last Session:** [session number, key actions from HANDOFF]
**Services:** [X/X] online
**Resources:** Disk X% | RAM X% | Swap X%
**Recent Changes:** [files modified in last 24h]
**Pending Actions:** [from HANDOFF priorities]
**Cold Email:** [X sent, X replies, X follow-ups due]
**Content:** [queue depth, last post time]

**Recommended First Action:** [highest-priority task from MASTER_PROMPT]
```

## Integration with Full Loop

After CatchUp, if any health issues are detected, automatically trigger the Full workflow for deeper verification.

## Done

You're caught up. Context loaded, health verified, priorities identified. Execute the recommended first action.
