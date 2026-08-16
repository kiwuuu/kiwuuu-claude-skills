---
name: kiwuuu-experiment-loop
description: Runs an autonomous propose-measure-keep/discard experiment loop over any Kiwuuu asset with a single numeric benchmark, using git commits as memory (Karpathy AutoResearch pattern). Use when the user wants to optimize something measurable overnight or unattended — scanner signals, script pacing, landing conversion copy, SFX timing — or says "experiment loop", "autoresearch", "optimize while I sleep".
---

# kiwuuu-experiment-loop — AutoResearch for Kiwuuu

Pattern stolen from Karpathy's AutoResearch (MIT, 2026-03: 630-line loop ran 700
experiments in 48h, kept 20, zero humans). The whole trick: **an agent may only keep a
change if a single number says it's better. Git is the memory** — wins persist as
commits, losses get reset. No judgment calls mid-loop, no scope creep.

## Preconditions (refuse to start without all three)

1. **One metric, one command.** A `benchmark` command that prints exactly one number to
   stdout in < ~5 min. If the metric needs human eyes or days of view-data, this skill
   does not apply — say so and stop.
2. **Git repo** around the asset (init one if absent; separate branch `exp/<topic>`).
3. **A frozen eval set.** The benchmark's inputs must not change mid-run (lock a copy in
   `eval/` first) — otherwise the loop optimizes noise.

## The loop

```
baseline = run benchmark on clean branch, commit "exp: baseline <score>"
repeat until budget/time/dry-out:
  1. PROPOSE  — one small, single-idea change (never batch ideas)
  2. RUN      — benchmark; parse the number
  3. JUDGE    — better than current best (beyond noise margin)? 
               YES → git commit "exp: <idea> <score>"  (new best)
               NO  → git reset --hard                  (discard, log the idea)
  4. LOG      — append idea/score/verdict to experiments.jsonl (kept AND killed)
dry-out rule: 2 consecutive rounds of no-improvement across ≥5 ideas → stop, report.
```

Noise margin: run the baseline 3x first; margin = observed spread. A "win" must clear
best + margin, else discard. (This is what separates the pattern from wishful tuning.)

## Kiwuuu benchmark recipes (ready to wire)

| Asset | Metric command sketch |
|---|---|
| Script pacing ([[stick-figure-genre-study]]) | words-per-beat distance from 10-16 band across a script file |
| Scanner signals | backtest hit-rate of signal rules over frozen klines in `eval/` |
| Landing/one-pager copy | LLM-judge panel score (fixed rubric, temp 0, same model) — weakest metric, flag as proxy |
| SFX/caption sync | mean |caption_ts − keyword_ts| from assemble_kw.py timeline |
| n8n workflow latency | wall-clock of test execution on fixed payload |

## Rules

- Small diffs only — one idea per experiment; if a change can't be described in one
  line, split it.
- NEVER run against live/production data or a live customer app (Limonella = hard no);
  copy to a sandbox first.
- experiments.jsonl is append-only and is the deliverable alongside the wins — killed
  ideas are knowledge (n≥5 statistical patience, per Warren Stick doctrine).
- Report at the end: baseline → final score, kept commits with one-liners, ideas
  killed, and the dry-out reason. Founder decides merge; the loop never merges to main.
- Budget: default 25 experiments or 2h, whichever first, unless the user sets more.
