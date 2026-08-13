---
name: kiwuuu-debate
description: Runs multi-perspective deliberation for Kiwuuu decisions in one of three modes - council (collaborative 5-voice debate), adversarial (steelman + counter-argument stress test), or peer (agents challenge each other directly). Use when the user says council, debate, red team, stress test, poke holes, perspectives, or when a strategic/architectural decision needs structured challenge before commitment.
license: MIT
---

# kiwuuu-debate

One deliberation skill, three modes. Consolidated 2026-07-21 from `council`, `redteam`, and `kiwuuu-debate-team` (those are retired — this replaces all three).

## Mode selection

| User intent | Mode | Cost |
|---|---|---|
| "council", "debate", "perspectives on X" | **council** — collaborative debate, 5 voices, 3 rounds | ~15 agent calls |
| "red team", "stress test", "poke holes", "counterargument" | **adversarial** — steelman + counter | ~6-8 agent calls |
| "have them challenge each other", build-or-defer / pricing decisions where positions must clash | **peer** — direct agent-to-agent challenge | 3-4× tokens — confirm with founder before running |
| Quick sanity check ("quick council") | **council-quick** — 1 round | ~5 agent calls |

If the mode is ambiguous, default to **council-quick** and say so. Never escalate to peer mode without the founder asking for it.

## Council mode (collaborative)

Five distilled voice essences from real AIs, each shaping how a member thinks. The debate workflow prepends the voice file contents to each agent's round prompt — cognitive diversity is real, not cosmetic.

| Member | Role | Source AI |
|--------|------|-----------|
| Serena Blackwood | Architect | Cursor |
| Aditi Sharma | Designer | Lovable |
| Marcus Webb | Engineer | Manus |
| Ava Chen | Researcher | Perplexity |
| Rook Blackburn | Verifier | Devin |

- Full 3-round debate: `Workflows/Debate.md` · Quick 1-round: `Workflows/Quick.md`
- Round structure: `RoundStructure.md` · Transcript format: `OutputFormat.md` · Voices: `Voices/*.md`
- For business decisions, swap in the business panel from `Voices/BusinessRoles.md` (CFO/CPO/CMO/CTO) instead of the AI voices.
- Skip voices that don't fit ("council without Devin", "just CFO and CMO") — honor it.

## Adversarial mode (steelman + counter)

Five-phase protocol, hard-capped at **8 parallel agents** (the old 32-agent version burned tokens for no accuracy gain):

1. **Decompose** the target into at most 10 atomic claims.
2. **Attack** — up to 8 agents with distinct lenses (correctness, economics, security, execution risk, customer reality, timing, competition, founder capacity) examine strengths AND weaknesses in parallel.
3. **Synthesize** convergent findings.
4. **Steelman** — strongest honest version of the idea (max 8 points).
5. **Counter** — strongest rebuttal (max 8 points), ending with the ONE issue most likely to collapse the plan.

## Peer mode (agents challenge each other)

Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Teammates exchange positions and must respond to each other's actual arguments, not restate their own. Use ONLY when the value comes from positions clashing (build-vs-defer, pricing, competing architectures) — for independent parallel work use `dispatching-kiwuuu-squad` instead. Cap at 3-4 teammates. Announce estimated cost before dispatch.

## Output

Every non-quick run ends with a verdict block: **decision → top 3 arguments for → top 3 against → the one collapse risk → recommendation**. For decisions the founder will act on, save the verdict to `C:/Users/Korisnik/Obsidian/Kiwuuu/decisions/debates/<topic>-<YYYY-MM-DD>.md` (vault) so it enters the permanent decision log.

## Rules

- Insights live in the friction between voices — surface disagreements, never average them away.
- Trust convergence only across genuinely different cognitive styles.
- Founder context for every debate: solo founder, $0 MRR, Limonella is the sole paying client (sacred), Agency Tier $499/mo + $19/workspace is the pricing truth, bad news first.
