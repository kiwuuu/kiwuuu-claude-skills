---
name: ultimate-loop
version: 2.2.0
status: production
last-updated: 2026-04-16
description: >
  Read-only verification for VPS-hosted stacks. Checks HTTP endpoints, PM2 process counts, SSH keys,
  disk/RAM/swap thresholds, and media asset inventory in parallel, then prints a scored PASS/FAIL
  report with failures itemized. Never fixes, deploys, restarts, or generates anything — every
  operation is a check, so a wrong invocation costs only seconds.
  USE WHEN: ultimate loop, run checks, verify everything, health check, system check, smoke test,
  sanity check, is the site up, is everything running, are services online, uptime, ping endpoints,
  test all endpoints, pm2 status, disk full, after deploy, did anything break, regression check,
  catch up, catch me up, where were we, what changed, session start, brief me, get up to speed,
  check assets, asset inventory, is the media live.
---

## Customization

**Before executing, check for user customizations at:**
`~/.claude/skills/CORE/USER/SKILLCUSTOMIZATIONS/UltimateLoop/`

If this directory exists, load and apply any PREFERENCES.md, configurations, or resources found there. These override default behavior. If the directory does not exist, proceed with skill defaults.

# UltimateLoop Skill

Comprehensive system, content, and infrastructure verification for VPS-hosted stacks. Runs all checks in parallel and produces a scored report.

## Sample Output

```
============================================================
ULTIMATE LOOP — System Verification
============================================================

--- ENDPOINTS ---
  [PASS] Main site — 200
  [PASS] SaaS app — 200
  [PASS] CLI (auth) — 401
  [PASS] saas-app — 200
  [PASS] mesh-coordinator — 200

--- PM2 SERVICES ---
  [PASS] Root PM2 (7 online) — your-services...
  [PASS] App PM2 (3 online) — your-app-services

--- SECURITY ---
  [PASS] SSH keys exist — 412 bytes
  [PASS] Open ports — 22, 80, 443 only

--- RESOURCES ---
  [PASS] Disk (49%) — 74G / 150G
  [PASS] RAM (39%) — 3.0GB / 7.6GB
  [PASS] Swap (51%) — 1.0GB / 2.0GB

--- CONTENT ASSETS ---
  [PASS] Videos (12) — 12 files
  [PASS] Images (6) — 6 files

============================================================
ULTIMATE LOOP: 14/14 PASS
============================================================
```

## Workflow Routing

| Trigger | Workflow |
|---------|----------|
| ultimate loop, run checks, verify everything, full check, health check, system check, smoke test, sanity check, after deploy, did anything break, regression check | `Workflows/Full.md` |
| quick check, fast check, is the site up, is everything running, are services online, uptime, ping endpoints, pm2 status | `Workflows/Quick.md` |
| catch up, catch me up, where were we, what changed, session start, zero context, brief me, get up to speed | `Workflows/CatchUp.md` |
| check assets, asset inventory, are the videos there, is the media live, content check, queue depth | `Workflows/Content.md` |

## Quick Reference

| Workflow | Purpose | Duration | Output |
|----------|---------|----------|--------|
| **FULL** | All 7 check categories | ~30s | Scored report X/Y PASS |
| **QUICK** | Endpoints + PM2 only | ~5s | Quick status |
| **CATCHUP** | Zero to speed — read all context, check changes, verify health | ~15s | Session brief |
| **CONTENT** | Content assets only | ~10s | Asset inventory |

## When to Use

- After deploying code changes
- After content generation sessions
- At session start for health verification
- Before and after major infrastructure changes
- When the user says "ultimate loop", "run checks", "test everything"

## Check Categories

1. **Endpoints** — All public URLs + internal service health endpoints
2. **PM2 Services** — Root (7) + Kiwubot user (3) process status
3. **Security** — UFW firewall, open ports, SSH keys
4. **Resources** — Disk, RAM, swap with threshold alerts
5. **Content Assets** — Videos, images, carousels, podcasts, post copy
6. **Public URLs** — Verify all content is accessible via HTTPS
7. **Pipeline Health** — Cron status, queue depth, posting rate

## Core Philosophy

**Origin:** "Trust but verify." Every session, every deployment, every change — run the loop. Catches regressions before users do.

**Speed:** Parallel HTTP checks, sequential only where dependencies exist. Full loop completes in under 30 seconds.

## Integration

**Works well with:**
- **Council** — Grade content before verifying it exists
- **RedTeam** — Security audit after loop identifies issues
- **content-factory** — Use `/content-factory` for deep pipeline inspection after this loop identifies asset issues
- Run after any agent makes changes

## Default: Full Workflow

When invoked without specifying a workflow, run the **FULL** workflow.

---

## Adapting This Skill to Your Stack

This skill ships with Kiwuuu-specific defaults. Here's every constant to replace:

| What | Kiwuuu default | Replace with |
|------|---------------|--------------|
| Public domain | `kiwuuu.com` | your domain |
| App subdomain | `app.kiwuuu.com` | your app URL |
| CLI subdomain | `cli.kiwuuu.com` | your CLI URL (or remove) |
| SaaS app port | `:4000` | your app's local port |
| Mesh service port | `:3003` | your service's local port |
| Server port | `:8096` | your server's local port |
| Root PM2 count | `EXPECTED_ROOT_PROCESSES = 7` | your process count |
| App PM2 count | `EXPECTED_APP_PROCESSES = 3` | your process count |
| App PM2 user | `kiwubot` user | your deploy user |
| Media directory | `/var/www/kiwuuu/media/` | your static files path |
| App code directory | `/root/kiwubot/` | your app root |
| Content queue log | `/root/kiwubot/social/cron.log` | your cron log path |

**Minimum viable adaptation:** Update the `endpoints` list in `Full.md` and adjust `EXPECTED_ROOT_PROCESSES`. Everything else can be removed if not applicable.
