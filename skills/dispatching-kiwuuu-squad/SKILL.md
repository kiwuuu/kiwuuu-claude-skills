---
name: dispatching-kiwuuu-squad
description: Use when a Kiwuuu task spans 3+ files or 2+ subsystems (souls audit, landing batch, multi-tenant migration, content factory). Splits work into independent units, fans out parallel Task sub-agents with explicit deliverable contracts, then runs one synthesizer to merge results and log to the ops log (PHONE_LOG.md, currently at C:/Users/Korisnik/kiwuuu-backup/memory/ pending vault consolidation). Compresses 30-min serial passes into ~5-min parallel ones.
license: MIT
---

# dispatching-kiwuuu-squad

Pattern for parallel Task-agent dispatch tuned to the Kiwuuu codebase. Adapted
from @sarutalksai's "second engineering team" framing into a reusable workflow
with five pre-baked Kiwuuu squad templates.

## When to fire

Trigger when the request meets ANY:
- Touches **3+ files** that don't share state (souls, landings, agent souls).
- Spans **2+ subsystems** on T1 (e.g. `/var/www/kiwuuu/` + kiwubot + saas-app — verify paths on T1 before dispatch).
- Is a **batch operation** ("audit all 25 souls", "port all decks", "regrade every video").
- Is an **audit pipeline** (research / code-review / brand / business in parallel).
- Has **independent work-units with one merge step** at the end.

**Do NOT fire when:**
- The work has sequential dependencies (output of step 1 feeds step 2).
- Only 1-2 files change (just do it inline; spawn-tax > savings).
- Touches the crypto-auto-trader on SG VPS (immutable rule, no parallel changes).
- Touches kiwubot/.env or soul files without explicit founder approval.

## The shape — 4 phases

```
1. DECOMPOSE  → split request into N ≤ 5 independent units, each with:
                  • scope (file paths or query)
                  • deliverable contract (what the sub-agent must return)
                  • acceptance criterion (how to know it's done)

2. DISPATCH   → fire all N Task agents in ONE message, parallel.
                Each gets: kiwuuu context-pack + scoped prompt + deliverable schema.

3. COLLECT    → wait for all N to return. Triage:
                  • PASS reports → feed to synthesizer
                  • PARTIAL    → re-fire with narrowed scope
                  • BLOCKED    → surface to user before continuing

4. SYNTHESIZE → one final Task agent (or inline if cheap) merges patches,
                resolves overlaps, runs verification, writes PHONE_LOG entry.
```

## Pre-baked squad templates

For full templates with sub-agent briefs ready to copy-paste, read
`templates.md` in this skill folder. The five templates:

1. **souls-audit** — 4 sub-agents grade 25 souls vs canonical `security_guard.md` patterns
2. **landing-batch** — N sub-agents port/optimize N HTML pages in `/var/www/kiwuuu/`
3. **tokens-migration** — 2-3 sub-agents catalog inline `:root` blocks across surfaces, 1 synthesizer plans the migration
4. **audit-pipeline** — 4 sub-agents (research, code-review, brand, business) + 1 kiwuuu-debate synthesizer
5. **content-factory-parallel** — image-gen + video-gen + copy-gen + scheduler in parallel

Pick the template, customize the inputs, dispatch.

## Context-pack every sub-agent gets

Prepend this block to every sub-agent prompt:

```
# Kiwuuu context (updated 2026-07-21 post-migration)
- Production VPS (T1): 169.58.50.23 · Ubuntu 24.04 · systemd services (NOT PM2): kiwubot, wa-cloud-webhook, kiwubot-panel, memory-bridge, kiwubot-demo, saas-app, limonella-finance, traficshop, kiwuuu-landing, n8n
- OLD VPS 89.167.55.166 is HOSTILE (root-compromised) — NEVER connect, NEVER reference as production
- Skills (audited): C:/Users/Korisnik/kiwuuu-skills-review/claude-skills/.claude/skills/ (this PC = cockpit; T1 = machine)
- Vault/brain: C:/Users/Korisnik/Obsidian/Kiwuuu/ (entry: _start-here.md)
- After service edits on T1: systemctl restart <service> (verify unit names on T1 first)
- Pricing truth: Agency Tier $499/mo base + $19/workspace (see vault kiwuuu-pricing)
- 25 WhatsApp souls in the kiwubot mesh
- DO NOT touch crypto-auto-trader on SG box 45.76.153.234 (immutable rule)
- Brand canon: electric-lime on dark (#a3e635 on #0a0a0a)
```

## Deliverable contract — every sub-agent returns

```yaml
unit_id: <slug>
status: PASS | PARTIAL | BLOCKED
files_touched:
  - path: /abs/path
    change_type: read | edit | create
    bytes_delta: ±N
findings:
  - severity: HIGH|MED|LOW
    desc: ...
    fix: ...
verification:
  - command: curl ...
    expect: HTTP 200
    actual: <result>
phone_log_line: "one-line summary for PHONE_LOG.md"
```

If a sub-agent returns prose without this schema, the synthesizer re-fires it
with the schema appended and a 300-word ceiling.

## Cost discipline

- **Max 5 parallel sub-agents per dispatch.** Above 5, overhead > savings.
- **Each sub-agent capped at 500 words output** unless explicitly extended.
- **Synthesizer reads sub-agent summaries, NOT raw transcripts** — keep context window tight.
- **No nested squads** — a sub-agent must not dispatch its own squad. One layer deep.
- **Pre-flight check:** if you'd be embarrassed for the founder to see all 5 sub-agent
  transcripts billed at Opus rates, don't dispatch — do the work inline with Haiku.

## Failure modes — checked at COLLECT phase

| Symptom | Cause | Recovery |
|---|---|---|
| Sub-agent overlaps another's scope | Decomposition was lossy | Re-fire with disjoint file lists |
| Sub-agent times out / huge transcript | Scope too broad | Re-fire with narrower brief, 500-word ceiling |
| Synthesizer says "conflict between unit 2 and 4" | Hidden dependency | Re-do as sequential, abandon parallel for this task |
| All sub-agents return PARTIAL | Task is research-shaped, not patch-shaped | Switch to single deep-research agent instead |
| One sub-agent writes to a path another reads | Race condition | Worktree isolation (per superpowers:using-git-worktrees) |

## Worked example — Round 2 audit pipeline

```
Request: "Audit the Kiwuuu project and grade above 9.3/10."

DECOMPOSE
├── unit_1: research/state          → STATE.md
├── unit_2: code/security-review    → REVIEW.md
├── unit_3: brand-cohesion + CRO    → BRAND_CRO.md
└── unit_4: business-state          → BUSINESS_STATE.md

DISPATCH  (all 4 fired in one message → 4 parallel general-purpose agents)

COLLECT   (~3-4 minutes wall-clock for all 4)

SYNTHESIZE
├── unit_5: 5-voice council debate (Cursor/Lovable/Manus/Perplexity/Devin)
└── unit_6: 4-perspective business council (CFO/CPO/CMO/CTO)
   → FINAL_REPORT.md
```

This skill made the Round 2 audit cycle take 12 minutes instead of an estimated
45 minutes serial. The pattern survived the audit and is the basis for this skill.

## Anti-patterns

- **Don't dispatch for tasks under 10 minutes serial.** Spawn overhead is ~30s each.
- **Don't dispatch when the work needs your judgment in the loop.** Sub-agents can't ask you.
- **Don't dispatch for unbounded research** ("find all bugs in Kiwuuu"). Sub-agents will write 3,000 lines and you'll re-read everything.
- **Don't dispatch for trivial parallel reads.** Use multi-Bash or multi-Read in one tool call instead.

## How this skill plays with others

- **Pairs with:** `superpowers:dispatching-parallel-agents` (generic version), `superpowers:subagent-driven-development`
- **Pairs with:** `kiwuuu-debate` (use the audit-pipeline template with a debate council as synthesizer)
- **Replaces:** none. This is additive, not a swap.
