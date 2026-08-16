---
name: kiwuuu-youtube-director
description: Director layer for faceless YouTube videos on the Higgsfield MCP — preset gallery pick, one-pass questionnaire, story beats, a DETAILED script pass (hook workshop, 10s-block word budgets, retention edit, fix loop with Kiwu), then a hard credit gate before any generation. USE WHEN the user says "make a youtube video", "video questionnaire", wants to plan/script an explainer, history, kids or story video, or asks to restart the youtube engine. Wraps faceless-channel-video — never generates until the script is LOCKED and credits approved.
---

# kiwuuu-youtube-director

Pre-production director for Higgsfield's `faceless-channel-video` workflow. Its whole job:
make the look, story and script excellent — with Kiwu in the loop — BEFORE a single credit
is spent. Output maps 1:1 onto the Higgsfield workflow intake so nothing gets re-asked.

> 📐 **Script doctrine:** the Step 4 script pass runs on `kallaway-method` — packaging-before-
> script order, the 5-part intro, 2-1-3-4 body ordering, re-hook cadence, fortune-cookie outro.
> Gate the locked script against its `assets/preflight.md`.

## Hard rules
1. **No `generate_*` calls, no workflow launch, until Step 6's explicit GO.** Steps 1–5 are
   free (chat + read-only MCP calls only).
2. **The script belongs to Kiwu.** It ships only after he says "lock" in Step 5. Never
   silently rewrite a locked script.
3. If the Higgsfield MCP is down, run Steps 2–5 anyway (script work needs no tools) and
   park the handoff.

## Step 1 — The look
- `get_explainer_presets` → present as a compact table: preset name + preview `video_url`
  link. All are 9:16; note that.
- For 16:9 or long-form looks, pull the wider catalog:
  `get_workflow_bundle_file({workflow:'faceless-channel-video', path:'references/preset-catalog.md'})`
  and `references/channel-styles.md`.
- One pick. If he can't decide, recommend ONE with a reason (match to topic tone), not a
  survey.

## Step 2 — Questionnaire (one pass, fixed order, ≤2 rounds)
Mirror the workflow's intake exactly so it never re-asks:
1. **Type** — Explainer / History (incl. documentary) / Kids / Fairy Tale & Myth
2. **Motion mode** — Animated (10s hard-cut blocks, recommended) / Picture-story (stills)
3. **Duration** — 1 / 2 / 3 min. Long-form 10/15/20 min exists only under
   History-documentary and is vendor-flagged "being verified" — surface the cost warning
   from `references/history-longform.md` before accepting it.
4. **Aspect** — 9:16 or 16:9 (where will it live: Shorts/TikTok vs YouTube long-form)
5. **Subtitles** — on/off; font patrick / caveat / marker / anton
6. **Topic + source** — his idea, a competitor video to beat (run `kiwuuu-analyze` on it
   first), or niche research
7. **Voice** — narrator character (pick once, reuse forever: same `voice_id` + type)
8. **CTA** — what we ask for and the mid-video placement line

Use AskUserQuestion when available; otherwise numbered questions in chat. Batch 1–4
together, then 5–8.

## Step 3 — Story pass
- Propose **2–3 angles** on the topic, each with a one-line hook. He picks or blends.
- Build the skeleton: **hook → build → turn → payoff**, plus:
  - **Through-line**: ONE physical object that appears in every block and escalates;
    payoff resolves it.
  - **Locations plan**: ~4–6 for a 2-min video, ≤2 consecutive blocks per location.
- Show the skeleton in chat. Brainstorm until the shape is right. Do NOT script yet.

## Step 4 — SCRIPT PASS (the core — be thorough here)

### 4a — Block math first
- `N = duration_seconds / 10` blocks. Every block = one 10s clip + one VO line.
- Word budget per full block line: **27–32 dense words** (Kids: **24–28**). Short final
  block gets a proportional budget. This is the Higgsfield narrator contract — a script
  written to it drops straight into the workflow with zero rework.
- Sanity: ~3 words/sec; each line must land in **8.6–10.0s of speech**.

### 4b — Hook workshop (block 1 gets special treatment)
Write **3 alternative openings** and let Kiwu pick/blend:
1. **Flat cold-open** — the claim stated short and blunt, no greeting, no throat-clearing
2. **Contrarian** — attack the assumption the viewer walked in with
3. **Open loop** — the question the payoff will answer
Test each: would YOU stop scrolling? Cut every word that isn't load-bearing.

### 4c — Draft format
Write all N blocks, numbered, each as:
```
[n] (arc: hook|build|turn|payoff) — VO line (word count)
    through-line state: <where the object is / what changed>
    shots: 5 hard cuts, sizes+angles varied (Kids: 4)
    location: <name> (consecutive-count check)
```
One idea per block. The block boundary is a cut point: **end a block on the question,
open the next with the answer** — that curiosity gap is the retention engine.

### 4d — Retention edit (run this checklist on the full draft)
- [ ] Block 1 hits the hook inside the first line — no wind-up
- [ ] Every line 27–32 words (count them; a 37-word line rushes the VO — measured failure)
- [ ] One idea per block; anything doing two jobs gets split or cut
- [ ] Escalation: each build block raises stakes over the last; no plateau
- [ ] Turn actually pivots — if you can delete it and the story still flows, it's not a turn
- [ ] Through-line present in every block, resolved in the payoff
- [ ] CTA placed **mid-video** as a comment-bait line (outperforms end-CTA); end carries
      only a short subscribe/next-video line
- [ ] Read the whole thing ALOUD mentally at 3 wps — flag any tongue-twister
- [ ] Banned words absent: leverage, synergy, ecosystem, journey, robust, seamless
- [ ] Voice is Pragmatic Futurist (`kiwuuu-brand-voice`): direct, confident, zero fluff

### 4e — Fix loop with Kiwu
Present the full script in chat — every block, word counts visible. Then brainstorm:
- What's the weakest block? (there always is one — name it yourself first)
- Offer concrete alternatives for anything he flags: 2 rewrites per flagged line, not
  essays about rewriting.
- Iterate until he says **"lock"**. A locked script is frozen — changes after lock go
  back through this step.

## Step 4f — FX SCAN (mandatory, never skip)

Once the beat sheet exists and **before** the final render, run the scanner over it:

```bash
python C:/Users/Korisnik/.claude/skills/kiwuuu-youtube-director/bin/fxscan.py <beats.json>
```

It reads every VO line and flags where an effect belongs, at three priorities:
**P1 add these · P2 add if it earns screen time · P3 audio-only accents.**

Rules of thumb it enforces:
- **Zero P1 candidates = a SCRIPT problem, not a scan problem.** It means the script
  contains no concrete number and no comparison. Rewrite before rendering.
- Healthy density is **0.4–0.7 effects per beat**. Below 0.25 the video will feel flat.
- Numbers are spelled out in VO for TTS ("two dollars fifty"), so the counter rule
  matches word-numbers as well as digits — don't "fix" it back to digits-only.

Effects come from `bin/fxlib.py` — all local ffmpeg + ASS + the bundled SFX pack,
**zero credits**:

| effect | what it does | use it for |
|---|---|---|
| `typewriter` | types text out, one keystroke click per character | dates, place cards, names, contract clauses |
| `bar_compare` | bars grow from zero, ping as each lands | any A-vs-B: distance, cost, speed, volume |
| `counter` | number spins up, or crashes to zero | money totals, casualty counts, view counts |
| `stat_pop` | one fact slams in with a scale-punch | the single number the beat exists for |
| `strike` | word appears, then is crossed out | myths, corrections, "everyone gets this wrong" |
| `accent` | bare sound on a cut | whoosh / impact-bass / glitch / sparkle |
| `flash` | white frame flash | hard pivot, shock cut |

`fxlib.merge(...)` combines effects; `fxlib.build_sfx_track(...)` mixes every cue into one
bed. SFX live at `OpenMontage/.agents/skills/hyperframes-media/assets/sfx/` (19 files).

## Step 5 — Credit gate (hard stop)
Before anything generates, show the bill:
- `balance` → current credits + plan
- Estimate: **N clip generations + N voice takes + ~25–40 style/asset images + ~40% retry
  overhead** (the workflow's own measured figure), blocks render at 720p, Topaz upscale at
  the end. State it as a range, not one number.
- If the estimate approaches the balance, say so and stop. Top-ups expire in 90 days —
  his call, never auto-suggest buying.
- **Explicit GO required.** "Looks good" is not GO. Ask plainly: "Spend the credits?"

## Step 6 — Handoff
- Load `get_workflow_instructions({workflow:'faceless-channel-video'})` and follow it
  EXACTLY — it owns generation, QC gates, assembly and delivery.
- Hand over the locked parameters: type, motion mode, style/preset, duration, aspect,
  subtitles+font, voice pair, topic, and the locked script (its Phase 3 accepts an
  authored script; word budgets already conform, so it passes validation untouched).
- Never let the workflow re-ask what Steps 1–2 already settled; answer its intake from
  the questionnaire record.

## NOT for
- Product/brand ads or UGC → the `ugc-*` workflows in the Higgsfield catalog
- Short vertical Kiwuuu promos → `kiwuuu-video-factory`
- Thumbnails → `youtube-thumbnail-generator` workflow
- Restyling existing footage → OpenMontage

## Companions
`kiwuuu-analyze` (beat a competitor video: transcript → breakdown → better script here),
`kiwuuu-brand-voice` (voice rules), `kiwuuu-debate` (angle stress-test for big topics).
