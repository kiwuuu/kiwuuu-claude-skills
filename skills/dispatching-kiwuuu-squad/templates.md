> ⚠️ All server paths below refer to T1 (169.58.50.23). Verify they exist on T1 before dispatching — layout was rebuilt 2026-07-21. Old VPS 89.167.55.166 is HOSTILE, never target it.

# Squad templates — copy-paste-ready

Each template = one DECOMPOSE block + N sub-agent briefs + one synthesizer brief.
Customize the **bold** placeholders. Fire all sub-agents in a single Agent tool
call message (parallel) — never sequentially.

---

## 1. souls-audit

Audit all 22 WhatsApp souls against the canonical security_guard patterns.

**4 sub-agents (read-only) + 1 synthesizer**

```
unit_1  → souls 1-6  (sales, support, scheduler, lead_gen, customer_success, hr)
unit_2  → souls 7-12 (legal, finance, marketing, content, design_coordinator, brand_analyst)
unit_3  → souls 13-18 (devops, fullstack, data_scientist, data_miner, database_analyst, content_strategist)
unit_4  → souls 19-22 (academic_researcher, executive_assistant, financial_analyst, + canonical diff)
unit_5  → synthesizer: emit deploy-plan with deploy lines + systemctl restart kiwubot (T1 is systemd, not PM2)
```

Sub-agent brief template:
```
Read souls **X..Y** at /root/kiwubot/agents/souls/<name>_soul.md
(souls are kiwubot:kiwubot 600 — use sudo /bin/cp to /tmp/ + sudo chown claude:claude).
Compare each against /root/kiwubot/agents/security_guard.md canonical patterns
(post-Apr-28: shell_exfil, env_dump, secret_exfil, zero_width_obfuscation).
For each soul, return: missing patterns, severity, exact 5-line patch to apply.
Cap output at 500 words.
```

---

## 2. landing-batch

Port or optimize N HTML pages in `/var/www/kiwuuu/`.

**N sub-agents (1 per page, max 5) + 1 synthesizer**

```
unit_N  → port one of: index.html · agencies.html · kiwuuu_pitch_v2.html · book-demo · pitch-data.html
unit_synth → cross-page consistency check + curl live verify + FIX_LOG entry
```

Sub-agent brief template:
```
File: /var/www/kiwuuu/**<page>**
Goal: **<port to tokens.css | swap CTA hierarchy | add DACH trust strip | etc>**
Constraints:
  - Don't change copy unless explicitly told
  - Don't change page IDs / anchor links (breaks deep links)
  - Preserve all existing <a href> targets
  - If file is root-owned, use sudo /bin/cp workflow
Deliverable: the unified diff + curl check that it still renders.
```

---

## 3. tokens-migration

Drive lime-canon adoption across all surfaces.

**2-3 sub-agents (cataloging) + 1 synthesizer (planning)**

```
unit_1 → catalog inline :root blocks across /var/www/kiwuuu/*.html
unit_2 → catalog inline :root blocks across /root/kiwusaas/templates/*.html
unit_3 → (optional) catalog inline :root blocks across /var/www/kiwuuu/studio/**
unit_synth → produce migration plan: per-page diff, sort by traffic, flag risky surfaces
```

Output is a plan, NOT edits. Founder approves before any actual migration squad fires.

---

## 4. audit-pipeline

The Round-1 audit pattern. 4 deep-dives + 2 councils.

**4 research sub-agents (parallel) + 2 council sub-agents (sequential)**

```
unit_1 → research: state, market position, current grade
unit_2 → code-review: 6 CRITICAL exploit scan + verification
unit_3 → brand + CRO: walk buyer journey, grade each funnel stop
unit_4 → business state: blockers, runway, time-to-revenue

unit_5 → kiwuuu-debate council mode (5 voices): synthesize 1-4 → grade
unit_6 → kiwuuu-debate business panel (CFO/CPO/CMO/CTO): synthesize 1-4 → revised target
```

All four deep-dives run in one Agent call message. The two debate units run
sequentially because the business panel depends on the engineering grade.

---

## 5. content-factory-parallel

Image + video + copy + scheduling in one shot.

**4 sub-agents (parallel) + 1 synthesizer**

```
unit_1 → image-gen: 3 IG carousels via fal.ai FLUX Schnell ($0.003/img)
unit_2 → video-gen: 2 vertical demos via wan/v2.2-a14b/text-to-video/turbo
unit_3 → copy-gen: caption set per platform (LinkedIn / X / IG / Threads)
unit_4 → asset-fetch: load /var/www/kiwuuu/media/content/ existing assets, choose rotation
unit_synth → schedule via Late API (POST /v1/posts), update content library tile cards
```

---

## Quick reference — when to use which template

| Situation | Template |
|---|---|
| "Audit all 25 souls for X" | souls-audit |
| "Port these N pages to Y" | landing-batch |
| "Plan the migration of inline styles to tokens" | tokens-migration |
| "Grade the Kiwuuu project / pre-launch audit" | audit-pipeline |
| "Ship a content drop across all 4 platforms" | content-factory-parallel |
| One-off "do X in N files" — no template fits | DECOMPOSE inline per the SKILL.md shape, then dispatch |

---

## Synthesizer brief template (universal)

```
You are the synthesizer for a dispatching-kiwuuu-squad run.

INPUT: structured reports from N sub-agents (deliverable schema in SKILL.md).
JOB:
  1. Detect conflicts/overlaps between unit reports.
  2. Apply patches in dependency order (if any).
  3. Run verification commands listed by each unit.
  4. Write a SINGLE PHONE_LOG.md entry summarizing all units (≤ 8 lines).
  5. Write a fix-log markdown file with all changes for git commit.

Cap output at 800 words.
Return: PASS | NEEDS_FOUNDER_APPROVAL | FAILED, plus the phone_log entry.
```
