---
name: content-factory
version: 1.0.0
status: production
last-updated: 2026-04-16
description: >
  Automated social media content pipeline: LLM generation → image/video production →
  quality gate → multi-platform posting. Covers X, LinkedIn, Instagram, TikTok.
  USE WHEN: generate content, post to social, content queue, content pipeline, social media, schedule posts.
---

# ContentFactory Skill — Kiwuuu Content Pipeline

The entire content production system in one skill. Text, images, videos, scheduling, posting, reporting. Everything runs on the VPS at `/root/kiwubot/social/`.

## Contents

- [Workflow Routing](#workflow-routing)
- [Pipeline Architecture](#pipeline-architecture)
- [Key Files](#key-files)
- [Quick Commands](#quick-command-reference)
- [Content Pillars](#content-pillars-weights)
- [Cron Schedule](#cron-schedule-active)
- [Image Generation](#image-generation)
- [Video Generation](#video-generation)
- [Quality Gate](#quality-gate)
- [Brand Rules](#brand-rules-locked)
- [Post Approval](#post-approval-flow)
- [Rate Limits](#platform-rate-limits-enforced-in-poster)
- [Ready Assets](#content-assets-ready-to-deploy)
- [Common Workflows](#common-workflows)
- [WhatsApp Commands](#whatsapp-commands-via-bot)
- [Logs & Debugging](#logs--debugging)
- [Known Issues](#known-issues--workarounds)
- [Adapting This Skill](#adapting-this-skill)

## Workflow Routing

| Trigger | Workflow |
|---------|----------|
| Generate content / fill queue | `Workflows/Generate.md` |
| Check stats / debug / view logs | `Workflows/Report.md` |
| Verify assets are live | `/ultimate-loop content` |

---

## Pipeline Architecture

```
Brief / Pillar
    ↓
content_engine.py  →  social.db (queue)
    ↓                      ↓
image_generator.py    social_poster.py  →  Late API  →  Platform
    ↓
video_factory.py / ltx_pipeline/
    ↓
/var/www/kiwuuu/media/
```

**Key files:**
| File | Role |
|------|------|
| `/root/kiwubot/social/social_main.py` | Master orchestrator — all pipeline commands |
| `/root/kiwubot/social/content_engine.py` | LLM content generation (Ollama / Claude) |
| `/root/kiwubot/social/social_poster.py` | Posts to X, LinkedIn, Instagram, TikTok via Late API |
| `/root/kiwubot/social/image_generator.py` | FLUX image generation via fal.ai |
| `/root/kiwubot/social/video_factory.py` | ffmpeg video assembly (text overlay, voiceover) |
| `/root/kiwubot/social/ltx_pipeline/` | LTX-2.3 cinematic video via fal.ai |
| `/root/kiwubot/social/social.db` | Content queue (SQLite) |
| `/root/kiwubot/social/quality_gate.py` | Quality scoring — 7+ pass, 8+ no-rewrite |
| `/root/kiwubot/social/VISUAL_SYSTEM.md` | Locked brand rules — READ BEFORE GENERATING |
| `/var/www/kiwuuu/media/POST_COPY.md` | 11 ready-to-paste post copies |
| `/var/www/kiwuuu/media/` | All media assets (images, videos, carousels) |

---

## Quick Command Reference

### Generate content
```bash
python3 /root/kiwubot/social/social_main.py generate
```
Fills the queue with today's content. Runs via Ollama (PC must be on) or Claude fallback. Quality gate: 7+ pass, 8+ skip rewrite.

### Post due items
```bash
python3 /root/kiwubot/social/social_main.py run_due
```
Posts any queue items scheduled for now. Rate limited: 6 posts/day, 2h cooldown per platform.

### Force post a slot
```bash
python3 /root/kiwubot/social/social_main.py run_slot morning
# slots: morning | midday | afternoon | evening
```

### View queue
```bash
python3 /root/kiwubot/social/social_main.py queue
```
Shows `pending_review` items waiting for approval.

### Approve a post
```bash
python3 /root/kiwubot/social/social_main.py approve <id>
```

### Pipeline stats (JSON)
```bash
python3 /root/kiwubot/social/social_main.py stats
```

### Platform status
```bash
python3 /root/kiwubot/social/social_main.py status
python3 /root/kiwubot/social/social_main.py enable instagram
python3 /root/kiwubot/social/social_main.py disable tiktok
```

---

## Content Pillars (Weights)

| Pillar | Weight | Content Types |
|--------|--------|---------------|
| `product_showcase` | 30% | case_study, comparison, data_drop |
| `customer_wins` | 25% | case_study, hot_take, data_drop, meme_humor, objection_killer |
| `building_in_public` | 15% | behind_scenes, vulnerability, day_in_life (max 1/week) |
| `ai_business_tips` | 10% | tip_tutorial, question, meme_humor, prediction |
| `industry_specific` | 10% | comparison, case_study, hot_take, tip_tutorial |
| `social_proof` | 10% | data_drop, case_study, prediction |

**TikTok/Instagram restriction:** Only `product_showcase`, `customer_wins`, `ai_business_tips`, `industry_specific`, `social_proof` allowed.

---

## Cron Schedule (Active)

```
04:00 UTC  → generate (fill daily queue)
Every 2h   → run_due (post scheduled items)
Daily      → analytics sync
Every 30m  → comment monitor
Sunday 19:00 UTC → weekly feedback harvester
Monday 10:00 UTC → prompt evolver
```

Check crons: `crontab -l | grep social`
Logs: `/root/kiwubot/social/cron.log`

---

## Image Generation

### FLUX via fal.ai (production)
```python
# In image_generator.py
python3 /root/kiwubot/social/image_generator.py
```

**Brand-compliant prompt formula:**
```
{subject}, dark background #0D0D0D, electric cyan accent #00FFD1,
minimalist flat design, Space Grotesk typography,
high contrast, professional, no gradients, no glass morphism
```

**Platform sizes:**
| Platform | Size |
|----------|------|
| Instagram feed | 1080×1080 |
| Instagram/TikTok Reels | 1080×1920 |
| LinkedIn | 1200×627 |
| X/Twitter | 1200×675 |

**⚠️ NEVER** use AI image gen for readable text/UI screenshots — it renders gibberish. Use ffmpeg text overlay instead.

Pre-made images available at: `/var/www/kiwuuu/media/content/` (use for queue posts).

---

## Video Generation

### LTX-2.3 Cinematic (fal.ai) — for social proof / mood content
```python
# Batch pipeline
python3 /root/kiwubot/social/ltx_pipeline/generate_ltx_batch.py

# Single video via fal.ai (in script)
import fal_client
result = fal_client.submit("fal-ai/ltx-video", arguments={
    "prompt": "your_prompt",
    "width": 1280, "height": 720,
    "num_frames": 49
})
```

**LTX prompt rules:**
- ✅ Cinematic/ambient: `entrepreneur sleeping while phone glows with notifications, moody blue light`
- ✅ Abstract atmosphere: `dark office, single screen illuminating a hand typing, city visible through window`
- ❌ Never: app UI, readable text, specific product screens, WhatsApp mockups (renders gibberish)

**Storage:** `/var/www/kiwuuu/media/ltx_test/` (cinematic) | `/var/www/kiwuuu/media/tiktok/` (posted)

### ffmpeg Text Overlay Videos — for stats/data/product
```python
python3 /root/kiwubot/social/video_factory.py
```
Use for: stat callouts, product demos, comparison videos.
Font: Inter Bold at `/home/claude/.fonts/Inter-Bold.ttf`
Brand colors: BG `#0D0D0D`, text `#FFFFFF`, accent `#00FFD1`

### ElevenLabs Voiceover Videos
```python
python3 /root/kiwubot/social/video_factory.py  # includes ElevenLabs mode
```
Voice: Liam (ID from ElevenLabs). Use for product explanation reels.

---

## Quality Gate

Threshold: **7+** = pass. **8+** = pass without rewrite. **6 or below** = fail, rewrite.
```python
python3 /root/kiwubot/social/quality_gate.py
```

Criteria:
1. ICP fit — does it speak to SMB/agency owner?
2. Hook strength — stops the scroll in 3 seconds?
3. Value delivery — teaches or shows something real?
4. CTA presence — drives to signup/demo?
5. Brand tone — bold, founder-to-founder, no fluff?

---

## Brand Rules (LOCKED — Council Decision 2026-04-15)

| Rule | Value |
|------|-------|
| Background | `#0D0D0D` (near-black, NOT `#000000`) |
| Primary accent | `#00FFD1` (electric cyan) |
| Secondary | `#BF5FFF` (neon violet — abstract only) |
| Text | `#FFFFFF` / `#A0A0A0` muted |
| Font | PP Neue Montreal Bold (or Space Grotesk Bold fallback) |
| Layout | Asymmetric, heavy negative space, one giant stat per slide |
| No | Gradients, glass morphism, stock photos, Monument Extended, IBM Plex Mono |
| Photos | Real UI screenshots, real WhatsApp chats, real numbers only |

Full system: `/root/kiwubot/social/VISUAL_SYSTEM.md`

---

## Post Approval Flow

### Auto mode (default)
```bash
SOCIAL_APPROVAL_MODE=auto  # in /root/kiwubot/.env
```
Items post automatically when due.

### Supervised mode
```bash
SOCIAL_APPROVAL_MODE=supervised
```
Items queue as `pending_review`. WhatsApp preview sent to `SOCIAL_APPROVAL_PHONE`.
Approve: `python3 social_main.py approve <id>`

---

## Platform Rate Limits (Enforced in poster)

| Platform | Max/day | Cooldown |
|----------|---------|---------|
| X/Twitter | 2 | 2h |
| LinkedIn | 1 | 2h |
| Instagram | 2 | 2h |
| TikTok | 1 | 2h |
| YouTube | 1 | 2h |
| **Total** | **6** | — |

Monthly guard: 120 posts/month (Zernio plan limit).

---

## Content Assets Ready to Deploy

**POST_COPY.md** — 11 posts ready to paste: `/var/www/kiwuuu/media/POST_COPY.md`

**Canva carousels:** Store your Canva design edit links in `/root/kiwubot/social/CANVA_LINKS.md` (private — do not commit to public repos).

**Videos (ready to post):**
- `/var/www/kiwuuu/media/ltx_test/v2_sleeping_entrepreneur.mp4` — cinematic ✅
- `/var/www/kiwuuu/media/ltx_test/v2_phone_notification.mp4` — cinematic ✅
- `/var/www/kiwuuu/media/ltx_test/v2_city_night_reply.mp4` — cinematic ✅
- `/var/www/kiwuuu/media/tiktok/` — 12 videos total

**Gallery:** kiwuuu.com/media/gallery.html

---

## Common Workflows

### Workflow 1: Generate + review + post one item manually
```bash
# 1. Generate
python3 /root/kiwubot/social/social_main.py generate

# 2. See queue
python3 /root/kiwubot/social/social_main.py queue

# 3. Approve item ID 42
python3 /root/kiwubot/social/social_main.py approve 42

# 4. Post due items now
python3 /root/kiwubot/social/social_main.py run_due
```

### Workflow 2: Generate a FLUX image for a specific brief
```bash
# Edit image_generator.py PROMPT variable, then:
python3 /root/kiwubot/social/image_generator.py

# Output at: /root/kiwubot/social/images/YYYYMMDD_HHMMSS.png
```

### Workflow 3: Create an LTX cinematic video
```bash
# Edit generate_ltx_batch.py PROMPTS list, then:
python3 /root/kiwubot/social/ltx_pipeline/generate_ltx_batch.py

# Output at: /var/www/kiwuuu/media/ltx_test/
```

### Workflow 4: Emergency — post a specific piece RIGHT NOW
```bash
# Force a slot
python3 /root/kiwubot/social/social_main.py run_slot morning
```

### Workflow 5: Check what posted today + engagement
```bash
python3 /root/kiwubot/social/social_main.py stats
# Shows: posts today, platform breakdown, queue length
```

### Workflow 6: Council-grade a piece before posting
Use `/council` skill. Give it: platform, content text, target ICP.
Ask for: hook strength, CTA quality, brand voice score (1-10).
Threshold: post if avg ≥ 7/10 across all 4 agents.

---

## WhatsApp Commands (via bot)

From WhatsApp, send to the bot number:
```
/social stats     → JSON stats of pipeline
/social generate  → Trigger manual generate
/social queue     → Show pending review items
/social approve 42 → Approve item 42
/social enable instagram
/social disable tiktok
```

---

## Logs & Debugging

```bash
# Main cron log
tail -50 /root/kiwubot/social/cron.log

# Posting log
tail -50 /root/kiwubot/social/logs/

# DB inspection
sqlite3 /root/kiwubot/social/social.db "SELECT id, platform, status, created_at FROM posts ORDER BY created_at DESC LIMIT 20;"

# Queue inspection
sqlite3 /root/kiwubot/social/social.db "SELECT * FROM content_queue WHERE status='pending_review';"
```

---

## Known Issues & Workarounds

| Issue | Workaround |
|-------|-----------|
| GCS ACL error on image upload | Cosmetic — images still generated locally at `/root/kiwubot/social/images/` |
| Rewriter JSON parse errors | Non-blocking — original content used if rewrite fails |
| Apollo API 403 (since Apr 12) | Manual LinkedIn prospecting only — `cold_email_sequencer.py import-csv` |
| LTX renders gibberish UI | Use cinematic/ambient prompts only, overlay captions via ffmpeg |
| PC Ollama offline | Claude fallback activates automatically (uses `ANTHROPIC_API_KEY`) |
| Late API monthly limit 120 | Check: `python3 social_main.py stats` → `monthly_used` field |

---

## NotebookLM Podcast Content

```bash
# Store your notebook ID in .env as NOTEBOOKLM_NOTEBOOK_ID
NB_ID="$(grep NOTEBOOKLM_NOTEBOOK_ID /root/kiwubot/.env | cut -d= -f2)"

# Check artifact status
notebooklm artifact list -n "$NB_ID"

# Generate audio
notebooklm generate audio "prompt" -n "$NB_ID"

# Download + move to media
notebooklm download audio <ID> -n "$NB_ID" --output /var/www/kiwuuu/media/

# Batch generate (quota resets daily)
bash /var/www/kiwuuu/media/podcasts/generate_episodes.sh
```
Auth: `/home/claude/.notebooklm/storage_state.json`
⚠️ URL sources fail (NotebookLM can't crawl most sites). Use text/file sources only.

---

## Performance Benchmarks

Targets only — get current actuals with: `python3 social_main.py stats`

| Metric | Target |
|--------|--------|
| Posts/day | 4 |
| Quality gate pass rate | >70% |
| Platforms active | 4 (X, LinkedIn, Instagram, TikTok) |
| Image generation time | <60s |
| LTX video generation | <3min |
| Monthly post limit | check your posting API plan |

---

## Adapting This Skill

This skill ships with Kiwuuu-specific defaults. Every constant to replace:

| What | Kiwuuu default | Replace with |
|------|---------------|--------------|
| App code root | `/root/kiwubot/social/` | your social pipeline directory |
| Media directory | `/var/www/kiwuuu/media/` | your static files / CDN path |
| Orchestrator | `social_main.py` | your main orchestrator script |
| Content engine | `content_engine.py` | your LLM generation script |
| Poster | `social_poster.py` | your platform API wrapper |
| Queue DB | `social.db` | your queue database |
| Posting API | Late API (Zernio) | Buffer, Hootsuite, direct platform API |
| Monthly limit | 120 posts | your plan's limit |
| Image gen | fal.ai FLUX | Replicate, DALL-E, Stable Diffusion |
| Video gen | fal.ai LTX-2.3 | RunPod, Replicate, local ComfyUI |
| Approval env var | `SOCIAL_APPROVAL_MODE` | your approval mechanism |
| WhatsApp bot API | `http://localhost:3001/send` | your notification endpoint |

**Minimum viable adaptation:** Update the `social_main.py` path and your queue DB path in `Workflows/Report.md`. Everything else adapts from there.
