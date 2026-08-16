---
name: kiwuuu-video-factory
description: Generate, voice, caption, and deploy short vertical demo videos for Kiwuuu social (TikTok / IG Reels / Threads / X). USE WHEN the user asks to "make a video for kiwuuu", "create a TikTok demo", "generate social videos", or wants to produce vertical 9:16 cinematic clips with voiceover and burned captions. Outputs land at /var/www/kiwuuu/media/content/ and serve at https://kiwuuu.com/media/content/.
---

> ⚠️ **Runs on T1 (169.58.50.23).** All `/var/www/` and `/root/` paths refer to T1's layout — verify they exist post-cutover before running. Never run against the old VPS (89.167.55.166 — hostile).

# Kiwuuu Video Factory

> 📐 **Script/hook first:** run `kallaway-method` before writing the caption track — hook stack,
> re-hook cadence, and CTA placement. Ship nothing that fails `assets/preflight.md`.

End-to-end pipeline: prompt + caption track → fal.ai wan/turbo clip → ElevenLabs voiceover → ffmpeg compose → Cloudflare-served URL.

## Why this skill

Confirmed-working stack from 2026-05-01 batch (9 videos shipped in ~10 min total):

```
text prompt + caption track (you provide)
     │
     ▼
fal.ai/wan/v2.2-a14b/text-to-video/turbo  ← 60s/clip, 720x1280 9:16
     │
     ▼
ElevenLabs eleven_turbo_v2_5  ← 5s/clip, ~12s of speech
     │
     ▼
ffmpeg compose:
  setpts slow-mo to match VO duration
  drawtext captions at scripted timecodes
  scale to 1080x1920 + AAC audio + H.264
     │
     ▼
/var/www/kiwuuu/media/content/<slug>_final.mp4
     │
     ▼
https://kiwuuu.com/media/content/<slug>_final.mp4   (Cloudflare-fronted)
```

## Hard constraints

| Constraint | Implication |
|---|---|
| Use `fal-ai/wan/v2.2-a14b/text-to-video/turbo` — **not** `ltx-video` | LTX queues are slow/unreliable; wan/turbo is reliable 60s |
| Generate at 9:16 / 720p — let ffmpeg upscale | Saves cost, native to TikTok/IG/Reels |
| Always slow-mo via `setpts=N*PTS` to match voiceover duration | Default wan clip is 5s, voiceover is ~12s — silence kills retention |
| Burn captions with `drawtext` filter at scripted timecodes | Captioned video gets ~3× more retention on muted feeds |
| Generate poster thumbs at the 6-second mark | After captions appear |
| Deploy to `/var/www/kiwuuu/media/content/` (Cloudflare-fronted; **NOT** `/root/kiwuuu-landing/`) | Memory `reference_kiwuuu_com_origin` |

## Inputs (per concept)

```yaml
slug: k_demo_<thing>            # url-safe, becomes filename
prompt: <100-300 word visual prompt for wan>   # cinematic, brand colors, no text overlays
voiceover: <text — keep <14 seconds at normal pace>
captions:                        # 4-6 timed cards
  - [start_sec, end_sec, "ALL CAPS BOLD TEXT"]
```

## Workflow routing

| Trigger | Workflow |
|---|---|
| Single concept | `Workflows/Single.md` |
| 3+ concepts at once | `Workflows/Batch.md` (parallel gen) |
| Existing clip needs different captions | `Workflows/Recompose.md` |

Default for "make 3 videos" or larger asks: `Batch.md`.

## Cost gate & output guard

`factory.py` prices the batch and confirms before spending:

```bash
python3 bin/factory.py --dry-run config.yaml   # print est. cost, generate nothing
python3 bin/factory.py config.yaml             # interactive [y/N] confirm before any fal call
python3 bin/factory.py --yes config.yaml       # skip prompt (or FACTORY_YES=1 — for cron/background)
```

Non-interactive stdin with no `--yes`/`FACTORY_YES=1` aborts before spending (won't silently burn API credits). `FACTORY_YES` is read from the real invocation environment *before* dotenv loads — putting it in `/root/kiwubot/.env` will **not** disable the gate (by design). Unknown flags are rejected.

Each final clip is size-checked: if it exceeds `FACTORY_MAX_MB` (default 25 — fits every social platform cap), it's auto re-encoded at a rising CRF (24→28→32) until it fits, then temp files are cleaned. Set `FACTORY_MAX_MB=0` to disable.

## Quick reference

| File | What |
|---|---|
| `SKILL.md` | this file |
| `Workflows/Batch.md` | parallel pipeline for N concepts |
| `Workflows/Single.md` | single concept |
| `bin/factory.py` | reusable Python implementation |
| `examples/9_video_drop_2026-05-01.yaml` | the proven 9-clip batch (capability + use cases + product proof) |

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `fal-ai/ltx-video` hangs >5 min | LTX endpoint queue depth | Always use wan/v2.2/turbo |
| Voice longer than video, awkward silence at end | Forgot setpts slow-mo | `pts = vo_dur / raw_dur` |
| Captions don't show | drawtext escape error | Escape `:` and `'` in caption text |
| Cloudflare returns 404 after deploy | Wrong target dir | Must be `/var/www/kiwuuu/media/content/`, not `/root/kiwuuu-landing/` |
| ElevenLabs auth error | Missing key | `ELEVENLABS_API_KEY` in `/root/kiwubot/.env` |
| Video appears upside down | wan returned wrong rotation flag | Re-encode with `-vf transpose=2` |

## Cost (confirmed 2026-05-01)

- wan/v2.2 turbo: ~$0.10-0.20 per 5s clip
- ElevenLabs turbo_v2_5: <$0.01 per voiceover (negligible)
- 9-video drop: ~$1-2 in API costs, ~$0 in compute

## Output URLs (existing assets)

All in `https://kiwuuu.com/media/content/`:

| Slug | Hook |
|---|---|
| `k_demo_22agents_final.mp4` | 22 agents, 1 number, zero sleep |
| `k_demo_2am_lead_final.mp4` | Cold lead at 2:47 AM |
| `k_demo_autopilot_final.mp4` | 5 minutes, no browser |
| `k_demo_dental_final.mp4` | Tooth pain → booked in 61s |
| `k_demo_pricing_final.mp4` | $15 vs €97 reveal |
| `k_demo_handoff_final.mp4` | Booker → Qualifier → Recovery |
| `k_demo_dashboard_final.mp4` | Live counter dashboard |
| `k_demo_4channels_final.mp4` | IG/FB/WA/email → one inbox |
| `k_demo_brand_morph_final.mp4` | White-label, every vertical |

Public gallery: `https://kiwuuu.com/videos/`
