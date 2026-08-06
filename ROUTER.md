# Skill Router

The routing map for every skill in this repo. Claude reads this to pick the right skill *and* the right workflow inside it, without loading each `SKILL.md` first.

The index, route table, and health report below are generated from the skills themselves. Regenerate after adding or editing a skill:

```bash
python3 scripts/build_router.py skills/ --out ROUTER.md
```

It works on any skills directory, so the same command maps a full install:

```bash
python3 scripts/build_router.py ~/.claude/skills --out ROUTER.md
```

Everything outside the `BEGIN/END GENERATED` markers is hand-written and survives regeneration.

---

## How routing actually works

Claude only sees **`name` + `description`** from each skill's YAML frontmatter at startup — roughly 100 tokens per skill. The body loads only after the skill is picked; bundled files load only when read.

Two consequences that shape everything here:

1. **Trigger keywords must live inside `description`.** A separate `keywords:` YAML field is never read at selection time — it would be pure decoration. Every keyword below is also present in the skill's real `description` and in its Workflow Routing table, which is what makes it fire.
2. **This file is the second layer.** Descriptions have no room to disambiguate skills that overlap, or to route to a specific workflow. That's what the hand-written sections at the bottom do.

---

<!-- BEGIN GENERATED -->

## Skill index (2 skills)

### `content-factory` — 1.0.0 · production

Social content production pipeline: pillar-weighted LLM generation, FLUX images and LTX cinematic video via fal.ai, ffmpeg text-overlay and ElevenLabs voiceover video, a 1-10 quality gate, and rate-limited posting to X, LinkedIn, Instagram and TikTok. Writes to a SQLite queue, spends API credits, and publishes publicly — confirm before running generate, run_due, or run_slot.

- `Workflows/Generate.md` — Step-by-step execution of the full content creation cycle: brief → generation → quality gate → queue.
- `Workflows/Report.md` — Check pipeline status, diagnose failures, and pull engagement data.

### `ultimate-loop` — 2.2.0 · production

Read-only verification for VPS-hosted stacks. Checks HTTP endpoints, PM2 process counts, SSH keys, disk/RAM/swap thresholds, and media asset inventory in parallel, then prints a scored PASS/FAIL report with failures itemized. Never fixes, deploys, restarts, or generates anything — every operation is a check, so a wrong invocation costs only seconds.

- `Workflows/CatchUp.md` — Get fully up to speed from zero context in under 60 seconds. Read project state, check what changed, verify everything works.
- `Workflows/Content.md` — Verify all content assets exist, are correctly sized, and are publicly accessible.
- `Workflows/Full.md` — Complete system, content, and infrastructure verification.
- `Workflows/Quick.md` — Fast endpoints + PM2 check only. Use for quick session-start verification.

## Route table — keyword → skill → workflow

| Trigger keywords | Skill | Workflow |
|---|---|---|
| `generate content`, `generate posts`, `create posts`, `write a post`, `fill the queue`, `new content`, `caption`, `carousel`, `reel`, `generate an image`, `FLUX`, `generate a video`, `LTX`, `cinematic`, `voiceover` | `content-factory` | `Workflows/Generate.md` |
| `content stats`, `what posted today`, `pipeline status`, `engagement`, `content queue`, `approve post`, `why didn't it post`, `posting failed`, `debug content`, `check the logs`, `rate limit`, `quality gate failed`, `empty queue` | `content-factory` | `Workflows/Report.md` |
| `verify assets are live`, `is the media accessible` | `content-factory` | `/ultimate-loop content` |
| `ultimate loop`, `run checks`, `verify everything`, `full check`, `health check`, `system check`, `smoke test`, `sanity check`, `after deploy`, `did anything break`, `regression check` | `ultimate-loop` | `Workflows/Full.md` |
| `quick check`, `fast check`, `is the site up`, `is everything running`, `are services online`, `uptime`, `ping endpoints`, `pm2 status` | `ultimate-loop` | `Workflows/Quick.md` |
| `catch up`, `catch me up`, `where were we`, `what changed`, `session start`, `zero context`, `brief me`, `get up to speed` | `ultimate-loop` | `Workflows/CatchUp.md` |
| `check assets`, `asset inventory`, `are the videos there`, `is the media live`, `content check`, `queue depth` | `ultimate-loop` | `Workflows/Content.md` |

## Routing health

All skills carry a description, trigger keywords, and a routing table.

<!-- END GENERATED -->

---

## Disambiguation — the overlaps that actually bite

Both skills claim the word **"content"**. This is by far the most likely mis-route, so decide on the **verb**, not the noun:

| Skill | Verbs | Never |
|---|---|---|
| `ultimate-loop` | verify, check, test, inspect, confirm, audit | fix, deploy, restart, generate |
| `content-factory` | generate, create, write, post, schedule, approve, debug | verify infrastructure health |

Applied:

| User intent | Skill | Why |
|---|---|---|
| "check the content" / "is it there" / "did it publish" | `ultimate-loop` → `Workflows/Content.md` | Verification. Counts files, HEADs URLs, reads queue depth. |
| "make the content" / "post it" / "why is the queue empty" | `content-factory` | Production. Writes, renders, scores, posts. |

Two more:

- **"queue"** — `ultimate-loop/Content.md` reports queue *depth* as a health number. `content-factory/Report.md` inspects queue *contents* and acts on them. Depth only → `ultimate-loop`. Anything actionable → `content-factory`.
- **"check the logs"** — cron/PM2/system logs → `ultimate-loop`. `social/cron.log` and posting failures → `content-factory/Report.md`.

---

## Cost of a wrong route

Which mistakes are cheap, and which are not:

| Skill | Side effects | Recovery |
|---|---|---|
| `ultimate-loop` | None — read-only. `sudo pm2 jlist`, HTTP GET/HEAD, `df`/`free`, file `stat`. | Free. A wrong route costs seconds. |
| `content-factory` | **Writes.** Spends fal.ai and Anthropic credits, mutates `social.db`, and `run_due`/`run_slot` **publish publicly**. | Not free. Confirm before `run_due`, `run_slot`, or any `generate` when the queue is already full. |

When intent is ambiguous between the two, run `ultimate-loop` first. It is the safe default.

---

## Chains

Common multi-skill sequences, so Claude proposes the next step instead of waiting to be asked:

```
session start          →  ultimate-loop CatchUp  →  (if failures) ultimate-loop Full
after a deploy         →  ultimate-loop Full
generate content       →  content-factory Generate  →  ultimate-loop Content
content asset missing  →  ultimate-loop Content  →  content-factory Report
posting broken         →  content-factory Report  →  ultimate-loop Full  (rules out infra)
```

`content-factory` also defers grading to the external `council` skill (4-agent scoring, post if avg ≥7/10) before high-stakes posts. That skill lives in the VPS install, not this repo.

---

## Adding a skill

1. Write `skills/<name>/SKILL.md`. The `description` states **what it does** in third person, then `USE WHEN:` followed by dense, comma-separated trigger phrases — the literal words a user would type, not a category label.
2. Put multi-mode logic in `skills/<name>/Workflows/*.md` and add a `## Workflow Routing` table to `SKILL.md`. Comma-separate the triggers; the generator splits on commas and one row per phrase lands in the route table.
3. Run `python3 scripts/build_router.py skills/ --out ROUTER.md` and fix anything the **Routing health** table flags.
4. Hand-write the Disambiguation and Chains entries. Those are judgment and cannot be extracted.
