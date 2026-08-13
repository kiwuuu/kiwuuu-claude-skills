---
name: kiwuuu-analyze
description: Reverse-engineer any social video (TikTok/Reel/Short/YouTube) into a replicable viral breakdown — hook, story structure, CTA, on-screen text — and batch-synthesize trends across many. USE WHEN the user pastes a video URL and asks to analyze/break down/"what makes it work"/study a competitor, do content research, or find what's trending. Supadata-first (transcript from URL, no download); pulls frames only when the payload is on-screen.
---

# kiwuuu-analyze

Turns video URLs into structured content intelligence that feeds the content pipeline (`content-factory`, repo skill — not wired locally),
`viral-content`, and the faceless-YouTube pipeline. Built Supadata-first so we do NOT
download every clip (that wastes time + OOMs this box).

## Step 1 — gather raw material
```bash
python3 .claude/skills/kiwuuu-analyze/bin/gather.py <url> [<url> ...] [--frames N] [--out DIR]
```
- **Default (no `--frames`)**: transcript only, via Supadata. No download, ~1–2 s/video.
- **Add `--frames 6` to 10** when the video's value is ON-SCREEN, not spoken: tool/skill
  lists, app/UI screencasts, dashboards, diagrams, before/afters — or when the transcript
  came back empty/short. Frames mode downloads once, extracts N stills, then deletes the video.
- Writes `<out>/<slug>.json` (transcript + metadata + frame paths) and `manifest.json`.

Decide frames up front from the URL/topic: "3 tools to…", "I built…", any screen-record →
use `--frames`. Pure talking-head opinion/story → transcript only.

## Step 2 — read it
Read each `<slug>.json` for the transcript + metadata (caption/hashtags/views/likes).
If frames were pulled, view `frames/<slug>/*.jpg` to capture on-screen text the transcript misses.

## Step 3 — per-video breakdown
Produce this for each video (concise, specific, no fluff). Decompose against the **seven Lego
bricks** from `kallaway-method` — topic · angle · hook structure · story structure · visual
format · key visuals · audio — so the output is directly remixable:
- **Hook (0–3s)** — exact opening line/visual + why it stops the scroll
- **Format & topic** — talking-head / screencast / listicle / story; the one idea
- **Story structure** — numbered beats with timestamps (hook → setup → payoff → CTA)
- **Script logic** — the persuasion/retention move (open loop, contrarian claim, proof)
- **Re-hooks** — where and how attention is re-bought mid-video; quote the actual lines
- **Visual layout** — captions style, on-screen text, b-roll, pacing/cut rhythm
- **CTA & lead magnet** — what's asked, and WHERE
  ⚠️ *Corrected 2026-08-08:* this previously said mid-video "comment X" often beats end
  placement. Measured against Kallaway's 53-short corpus that's wrong — **51 of 53 place it
  last, median 96% through**. Record what the video actually does; don't assume mid-roll wins.
- **Metrics** — views/likes/comments/**saves and shares** + engagement read
  (share rate = shares ÷ views; >3% sustained is the virality threshold)
- **Steal-for-Kiwuuu** — 1–3 replicable moves for our channels

Sort candidates by **outlier score** (views ÷ that creator's own average), not raw views — it
removes channel size from the comparison.

## Step 4 — batch trend synthesis (2+ videos)
Across the set, surface what no single video shows: recurring hooks, shared structure,
common CTA placement, format patterns, topic angles. Output a ranked "what's working now"
list + 3 concrete content ideas for Kiwuuu.

## Step 5 — hand off (optional)
Feed the breakdown/ideas into the content pipeline (content-factory in the skills repo) or the faceless-YouTube brief.

## Step 1b — no Supadata key? use `harvest.py` (proven 2026-08-08)

⚠️ **The Supadata key is not on this PC** — it lived on the old VPS, so `gather.py` returns
"no SUPADATA_API_KEY" and produces nothing. Until the key is restored, use:

```bash
pip install --user yt-dlp truststore requests    # one-time, no ffmpeg needed
python .claude/skills/kiwuuu-analyze/bin/harvest.py profile https://www.tiktok.com/@handle --out DIR
python .claude/skills/kiwuuu-analyze/bin/harvest.py fetch-all DIR --limit 20
```

- `profile` lists a whole channel ranked by views (works on TikTok *and* YouTube).
- `fetch` / `fetch-all` pull auto-caption transcripts. No media kept.
- **TikTok per-video pages hit a bot wall ~half the time.** The reliable route is the in-app
  browser: navigate to tiktok.com once, `fetch()` the video URLs from inside that origin with
  `credentials:'include'`, parse `__UNIVERSAL_DATA_FOR_REHYDRATION__`, then pipe the records to
  `harvest.py vtt DIR`. Signed subtitle URLs expire — use them the same session.
  Details in the script docstring + [[2026-08-03_tiktok-transcripts-without-supadata]].
- ASR mangles proper nouns ("Claude" → "cloud"/"CLAW"). Never quote a product name verbatim.

## Notes / reliability
- Supadata key: youtube-engine `.env` (old-VPS path was /home/claude/youtube-engine/.env — verify location on T1 post-cutover). See [[reference_supadata_transcripts]].
- Caveats: transcript-only (use `--frames` for on-screen text); needs speech/captions
  (silent clips return empty → use `--frames`); free-tier quota.
- Fallback if Supadata fails AND frames aren't enough: `yt-dlp` + local whisper
  (`whisper base`, run `--workers 1`; OOM-prone at ~1 GB free — prefer `tiny`).
- Doctrine layer: **`kallaway-method`** — what the breakdown *means* and how to act on it.
- Companion: `competitor-intel`, `kiwuuu-competitor-scraper` (monitoring/briefs — different job).
