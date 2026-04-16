# Report Workflow — Stats, Logs & Debugging

Check pipeline status, diagnose failures, and pull engagement data.

Trigger: "content stats", "what posted today", "pipeline status", "debug content", "content report"

## Step 1: Quick pipeline stats

```bash
python3 /root/kiwubot/social/social_main.py stats
```

Key fields to look for in the JSON output:
- `posts_today` — how many posted today
- `monthly_used` — Late API usage vs 120/month limit
- `queue_depth` — pending items
- `platforms_enabled` — which platforms are active

## Step 2: What's in the queue right now

```bash
python3 /root/kiwubot/social/social_main.py queue
```

Shows all `pending_review` items with IDs, platforms, and preview text.

## Step 3: Check cron log for errors

```bash
tail -50 /root/kiwubot/social/cron.log
```

Common patterns to look for:
```
[quality-gate] score=X   → quality scores per item
[poster] RATE_LIMIT       → posting rate limit hit
[poster] 403              → Late API key expired / quota
[generator] JSONDecodeError → rewriter failed (non-blocking, uses original)
[image] GCS ACL error     → cosmetic, image still saved locally
```

## Step 4: Inspect the database directly

```bash
# Last 10 posts
sqlite3 /root/kiwubot/social/social.db \
  "SELECT id, platform, status, substr(content,1,60), created_at FROM posts ORDER BY created_at DESC LIMIT 10;"

# Pending review items
sqlite3 /root/kiwubot/social/social.db \
  "SELECT id, platform, substr(content,1,80) FROM content_queue WHERE status='pending_review';"

# Today's posting activity
sqlite3 /root/kiwubot/social/social.db \
  "SELECT platform, COUNT(*) as count FROM posts WHERE date(created_at)=date('now') GROUP BY platform;"
```

## Step 5: Check platform enable/disable state

```bash
python3 /root/kiwubot/social/social_main.py status
```

Enable/disable:
```bash
python3 /root/kiwubot/social/social_main.py enable instagram
python3 /root/kiwubot/social/social_main.py disable tiktok
```

## Step 6: Check cron schedule is active

```bash
crontab -l | grep social
```

Expected entries:
```
0 4 * * *  cron_generate.sh    # Daily content generation at 04:00 UTC
*/120 * * * * cron_run_due.sh  # Post due items every 2 hours
```

If missing: check `/root/kiwubot/social/cron_generate.sh` exists and re-add to crontab.

## Common Failures & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| 0 posts today | Approval mode = supervised | `approve` items or switch to `auto` |
| 403 on posting | Late API quota hit | Check `monthly_used`, wait for reset or upgrade plan |
| Generation fails | Ollama offline + no Claude key | Add `ANTHROPIC_API_KEY` to `.env` |
| Images not in queue | fal.ai key expired | Update `FAL_KEY` in `.env` |
| `JSONDecodeError` in logs | Rewriter parse failure | Non-blocking — original content used |
| `GCS ACL error` | Uniform bucket blocks legacy ACL | Images still saved locally, cosmetic |
| Empty queue after generate | All items scored <7 | Lower quality gate or improve prompts in `content_engine.py` |

## Step 7: Force-post a specific slot now

```bash
python3 /root/kiwubot/social/social_main.py run_slot morning
# slots: morning | midday | afternoon | evening
```

## Step 8: Run the ultimate-loop content check

After diagnosing, verify assets are publicly accessible:

```
/ultimate-loop content
```

## Adapting to Your Stack

- Replace `social_main.py` with your orchestrator
- Replace the `sqlite3` DB path with your queue database
- Replace `cron_generate.sh` / `cron_run_due.sh` with your cron scripts
- Replace `Late API` / Zernio with your posting API
- Adjust the `monthly_used` limit to match your plan

## Done

Pipeline health verified. Any failures diagnosed and actioned.
