# Council Members

Reference for council member roles, perspectives, and voice assignments.

**Upgraded 2026-04-17:** The council now loads 5 REAL AI voice essences (Cursor, Manus, Lovable, Perplexity, Devin) instead of 4 generic Claude personas. Each member's cognition is shaped by a compressed distillation of a distinct top-tier AI system prompt — producing genuine cognitive diversity rather than 4 flavors of the same model. Voice files live in `Voices/`.

## Default Council (5 Members)

| Agent | Role | Source AI | Voice File | Strengths | When to Skip |
|-------|------|-----------|------------|-----------|--------------|
| **Serena Blackwood** | Architect | Cursor | `Voices/cursor_voice.md` | System design, symbol-tracing, comprehensive exploration before commit, verified answers | Trivial UX questions where architecture is not the bottleneck |
| **Aditi Sharma** | Designer | Lovable | `Voices/lovable_voice.md` | UX, design systems, semantic tokens, user-first framing, "beautiful or reject" bar | Pure backend/infra debates with no user-facing surface |
| **Marcus Webb** | Engineer | Manus | `Voices/manus_voice.md` | Step-by-step execution plans, dependency mapping, adaptive re-planning when approaches fail | One-line changes that don't need a plan |
| **Ava Chen** | Researcher | Perplexity | `Voices/perplexity_voice.md` | Sourced citations, precedent, source-tier discipline, table-based comparisons | Internal-only decisions where external precedent doesn't apply |
| **Rook Blackburn** | Verifier | Devin | `Voices/devin_voice.md` | Root-cause analysis, completion-checklist rigor, environment-aware caution, test-fix discipline | Early-stage ideation where premature verification kills momentum |

## Optional Members (Legacy)

Add these as needed based on topic. Legacy members (not yet voice-upgraded):

| Agent | Perspective | When to Add |
|-------|-------------|-------------|
| **Security** (Rook Blackburn — legacy pentester persona) | Risk, attack surface, compliance | Auth, data, APIs — **Note:** name collides with new Verifier; prefer Verifier unless explicit pentest is needed |
| **Intern** (Dev Patel) | Fresh eyes, naive questions | Complex UX, onboarding |
| **Writer** (Emma Hartley) | Communication, documentation | Public-facing, docs |

## Agent Type Mapping

All 5 default voices use the `general-purpose` subagent_type. The voice essence file contents are prepended to the debate prompt — shaping HOW the agent thinks, not the infrastructure.

| Council Role | Task subagent_type | Voice |
|--------------|-------------------|-------|
| Architect | general-purpose | Serena Blackwood (Cursor) |
| Designer | general-purpose | Aditi Sharma (Lovable) |
| Engineer | general-purpose | Marcus Webb (Manus) |
| Researcher | general-purpose | Ava Chen (Perplexity) |
| Verifier | general-purpose | Rook Blackburn (Devin) |

## Custom Council Composition

Defaults to all 5 voices. Allow overrides:

- "Council without Devin" → Skip Verifier (Rook)
- "Council without researcher" → Skip Perplexity voice (Ava)
- "Just Cursor and Lovable" → Only Architect + Designer
- "Council with security" → Add legacy pentester (note: different Rook from Verifier)
- "Council with intern" → Add intern for fresh perspective
- "Just architect and engineer" → Only those two

## Why 5 AI Voices Beat 4 Claude Personas

Old setup: 4 persona prompts all pulling from the same underlying model, producing convergent reasoning dressed in different costumes.

New setup: each voice carries the distilled behavioral signature of a real top-tier AI:
- **Cursor** brings "trace everything, verify comprehensively"
- **Manus** brings "break down, loop, adapt"
- **Lovable** brings "design system first, beautiful or reject"
- **Perplexity** brings "cite or demote, source-tier discipline"
- **Devin** brings "verify at every gate, root-cause before fix"

Debates now surface genuine cognitive friction — Perplexity asks "where's the source?" while Lovable asks "does it feel good?" while Devin asks "has this been verified end-to-end?" — producing insights the old council missed.
