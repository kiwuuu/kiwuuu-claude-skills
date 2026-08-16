# Kiwuuu Claude Code Skills

A collection of production-grade skills for the [Claude Code](https://claude.ai/code) agent system, built and battle-tested by [Kiwuuu](https://kiwuuu.com).

Claude Code skills are modular instruction sets that extend the agent's capabilities. Drop a skill folder into `.claude/skills/` in any project and Claude Code will automatically detect and use it.

---

## Installation

```bash
# Copy a skill into your project
cp -r skills/ultimate-loop /your-project/.claude/skills/
cp -r skills/content-factory /your-project/.claude/skills/
```

That's it. Claude Code picks up skills automatically — no config required.

---

## Skills

### `ultimate-loop` — Comprehensive System Verification

**Trigger:** `ultimate loop`, `run checks`, `verify everything`, `health check`

Runs parallel verification across your entire stack and produces a scored report. Built for teams that deploy fast and need to catch regressions before users do.

**What it checks:**
- All public endpoints and internal service health
- PM2 process status (root + non-root users)
- Firewall, open ports, SSH keys
- Disk, RAM, and swap with threshold alerts
- Content asset inventory (videos, images, carousels)
- Pipeline health (cron status, queue depth, posting rate)

**Three workflows:**

| Command | What it runs | Time |
|---------|-------------|------|
| `ultimate loop` | All 7 check categories | ~30s |
| `ultimate loop quick` | Endpoints + PM2 only | ~5s |
| `ultimate loop catch-up` | Zero to speed — loads context, checks changes, verifies health | ~15s |

**Example:**
```
> ultimate loop
============================================================
ULTIMATE LOOP — System Verification
============================================================

--- ENDPOINTS ---
  [PASS] Main site — 200
  [PASS] App — 200
  [PASS] CLI (auth) — 401
  [PASS] API — 200

--- PM2 SERVICES ---
  [PASS] Root PM2 (5 online) — n8n, kiwubot, saas-app, server, figma-mcp
  [PASS] User PM2 (3 online) — mesh-coordinator, memory-bridge, control-panel

ULTIMATE LOOP: 12/12 PASS
============================================================
```

---

### `content-factory` — Content Production Pipeline

**Trigger:** `generate posts`, `content pipeline`, `run content factory`, `post to social`, `check queue`

Complete content production system in one skill. Text generation, image creation, video assembly, scheduling, posting, and reporting — all wired together.

**Pipeline:**
```
Brief / Pillar
    ↓
content_engine.py  →  Queue (SQLite)
    ↓                      ↓
image_generator.py    social_poster.py  →  Platform
    ↓
video_factory.py / LTX cinematic pipeline
```

**Covers:**
- Queue management (`generate`, `approve`, `run_due`, `run_slot`)
- FLUX image generation via fal.ai (1080×1080, 1200×627, 1080×1920)
- LTX-2.3 cinematic video generation
- ffmpeg text overlay videos for stats and product demos
- ElevenLabs voiceover videos
- Quality gate scoring (7+ pass, 8+ no-rewrite required)
- Platform rate limits and monthly guard rails
- WhatsApp bot commands for on-the-go control
- Cron schedule management

**Example:**
```
> generate posts for today

Generating content for 4 slots (morning, midday, afternoon, evening)...
  [✓] morning — LinkedIn: "The agency that replaced 3 tools with 1 WhatsApp bot" (score: 8.2)
  [✓] midday  — X/Twitter: "We handle 847 messages/day for €0.03 each" (score: 7.9)
  [✓] afternoon — Instagram: product showcase reel (score: 8.5)
  [✓] evening — TikTok: behind-the-scenes (score: 7.1)

Queue: 4 items pending review. Run `approve all` to schedule.
```

---

### `session-state` — Never Play Catchup Again

**Trigger:** `handoff`, `save state`, `wrap up`, `end session`

Writes the session's real state — active threads, next actions, blockers — into `_now.md` at the vault root, then commits. The `next` column must pass one test: a fresh session with zero history can execute it without asking. Paired with `ultimate-loop catch-up`, which reads `_now.md` first at session start.

```
session end   →  session-state writes _now.md
session start →  ultimate-loop CatchUp reads it
```

State lives in the file, never only in a dying context window. Either half alone decays: writing without reading is a diary, reading without writing is fiction.

Three scripts make the loop self-enforcing rather than remembered: `now_doctor.py --report` (expiry + drift checks, run at session start), `now_doctor.py --guard` (Stop hook — blocks ending a session whose commits are newer than `_now.md`, once), and `session_breadcrumb.py` (SessionEnd hook — records branch/commits/dirty facts per machine even when no handoff happened). Install the hooks once per machine: `python3 skills/session-state/scripts/install_hooks.py` (all platforms — from PowerShell on Windows: `python skills\session-state\scripts\install_hooks.py`; do not use `bash` on Windows, it routes into WSL).

---

## Routing

[`ROUTER.md`](ROUTER.md) is the map: what every skill and workflow does, the trigger keywords that select each one, the overlaps that cause mis-routes, and which skills are safe to invoke by mistake.

The index and route table are generated from the skills themselves:

```bash
python3 scripts/build_router.py skills/ --out ROUTER.md
```

Point it at any skills directory to map a full install — `python3 scripts/build_router.py ~/.claude/skills --out ROUTER.md`. It also lints for the things that silently break skill selection: missing descriptions, absent `USE WHEN` clauses, bodies over 500 lines, and workflow files with no routing table.

---

## How Claude Code Skills Work

Skills are plain Markdown files that load into Claude's context when triggered. They contain:
- A YAML frontmatter block with the skill name, description, and trigger phrases
- Structured instructions Claude follows to complete the task
- Workflow routing (optional) for multi-mode skills
- Command references, file paths, and domain knowledge

The agent reads the relevant skill, follows its workflow, and executes the task using your actual project files and services. No plugins, no API calls to skill registries — just Markdown the agent reads.

Full docs: [Claude Code Skills documentation](https://docs.anthropic.com/en/docs/claude-code/skills)

---

## Adapting These Skills

These skills were built for the Kiwuuu production stack. To use them in your own project:

1. Copy the skill folder into `.claude/skills/`
2. Edit the file paths, service names, and endpoints in `SKILL.md` to match your stack
3. For `ultimate-loop`: update the endpoints list in `Workflows/Full.md`
4. For `content-factory`: update the pipeline paths and platform config

The skill structure (trigger phrases, workflow routing, output format) works as-is. Only the project-specific references need updating.

---

## About Kiwuuu

[Kiwuuu](https://kiwuuu.com) builds WhatsApp AI agent infrastructure for agencies and SMBs. These skills power our internal Claude Code workflows — we ship them publicly because good tools should be shared.

More skills coming. Star the repo to get notified.

---

**[Star this repo](https://github.com/kiwuuu/claude-skills)** if it saves you time. Takes 2 seconds, helps us know it's useful.
