# Generate Workflow — Content Creation Cycle

Step-by-step execution of the full content creation cycle: brief → generation → quality gate → queue.

Trigger: "generate content", "create posts", "fill the queue", "content factory generate"

## Prerequisites

- Python 3.x + `fal-client` (`pip install fal-client`)
- `ffmpeg` installed (for video overlays)
- `sqlite3` CLI available
- API keys in `.env`: `ANTHROPIC_API_KEY`, `FAL_KEY`, `LATE_API_KEY`
- Ollama running locally (optional — Claude fallback activates automatically if offline)

## Step 1: Check queue before generating

```bash
python3 /root/kiwubot/social/social_main.py queue
python3 /root/kiwubot/social/social_main.py stats
```

**Skip generation if** queue already has 6+ pending items. Only generate if queue is low.

## Step 2: Generate today's content

```bash
python3 /root/kiwubot/social/social_main.py generate
```

This command:
1. Selects content pillars by weight (product_showcase 30%, customer_wins 25%, etc.)
2. Calls Ollama (if online) or Claude API (fallback)
3. Runs quality gate — scores 1–10
4. Items scoring ≥7 enter the queue
5. Items scoring ≥8 skip the auto-rewriter
6. Items scoring <7 are rewritten once, then re-scored
7. Generates a FLUX image via fal.ai for each item

**Expected output:** 3–6 new queue items (text + image URL per item)

## Step 3: Review quality gate results

Check the cron log for scores:
```bash
tail -30 /root/kiwubot/social/cron.log
```

Look for lines like:
```
[quality-gate] item 42: score=8.2 → PASS (no rewrite)
[quality-gate] item 43: score=6.1 → REWRITE → score=7.4 → PASS
[quality-gate] item 44: score=5.0 → FAIL (dropped)
```

## Step 4: Approve or reject items (supervised mode)

If `SOCIAL_APPROVAL_MODE=supervised` in `.env`:

```bash
# View pending items
python3 /root/kiwubot/social/social_main.py queue

# Approve specific item
python3 /root/kiwubot/social/social_main.py approve <id>
```

If `SOCIAL_APPROVAL_MODE=auto`: items post automatically when scheduled — skip this step.

## Step 5: Optional — Generate images manually

For a specific visual brief (when auto-generation isn't right):
```bash
# Edit PROMPT in image_generator.py, then:
python3 /root/kiwubot/social/image_generator.py
# Output: /root/kiwubot/social/images/YYYYMMDD_HHMMSS.png
```

**Brand-compliant prompt formula:**
```
{subject}, dark background #0D0D0D, electric cyan accent #00FFD1,
minimalist flat design, Space Grotesk typography,
high contrast, no gradients, no glass morphism
```

> ⚠️ Never use AI image generation for readable text or UI screenshots — renders as gibberish.
> Use ffmpeg text overlay instead (see Step 6).

## Step 6: Optional — Create a video with text overlay

For stat callouts, data drops, or product demos:
```bash
python3 /root/kiwubot/social/video_factory.py
```

Font path: `/home/claude/.fonts/Inter-Bold.ttf`
Brand colors: BG `#0D0D0D` | Text `#FFFFFF` | Accent `#00FFD1`

## Step 7: Optional — Generate a cinematic LTX video

For mood/atmosphere content (founder story, product feel):
```bash
python3 /root/kiwubot/social/ltx_pipeline/generate_ltx_batch.py
# Output: /var/www/kiwuuu/media/ltx_test/
```

**LTX prompt rules:**
- ✅ `entrepreneur sleeping while phone glows with notifications, moody blue light`
- ✅ `dark office, single screen illuminating a hand typing, city visible through window`
- ❌ No app UI, no WhatsApp screens, no readable text (renders gibberish)

## Step 8: Verify assets accessible

After generation, run a quick content check:
```bash
python3 /root/kiwubot/social/social_main.py stats
```

Then optionally run `/ultimate-loop content` to verify all assets are publicly accessible.

## Quality Gate Reference

| Score | Action |
|-------|--------|
| ≥8 | PASS — post as-is |
| 7–7.9 | PASS — auto-rewrite first |
| <7 | FAIL — dropped from queue |

Criteria checked: ICP fit, hook strength, value delivery, CTA presence, brand tone.

## Adapting to Your Stack

- Replace `social_main.py` with your orchestrator script
- Replace `image_generator.py` with your image generation wrapper
- Replace `video_factory.py` / `ltx_pipeline/` with your video tools
- Adjust quality gate threshold in your quality_gate script
- Replace `SOCIAL_APPROVAL_MODE` env var with your approval flow

## Done

Queue is filled. Items are scored, approved (if supervised), and ready for the Post workflow.
