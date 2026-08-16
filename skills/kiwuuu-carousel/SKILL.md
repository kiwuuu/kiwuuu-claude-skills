---
name: kiwuuu-carousel
description: Produces TikTok/IG photo-mode carousel posts (10-12 slides) in the proven save-bait listicle format — hook slide, numbered item slides with "START WITH" action pills, save-CTA closer — styled per Kiwuuu channel brand. Use when the user asks for a carousel, slide post, photo-mode post, listicle post, or a zero-video content drop for Absurdity/REKT/BLACK BOX/THE MACHINE or Kiwuuu main.
---

# kiwuuu-carousel — save-bait carousel factory

> 📐 **Hook slide + closer:** run `kallaway-method` for the slide-1 hook and the save-CTA —
> the hook bank and CTA formula there are drawn from 53 measured shorts.

Stolen from @catalin.ai's "10 skills / $10M business" post (2026-07-07: 842 saves vs 512
likes — saves 1.6:1). Carousels are our cheapest content lane: no render pipeline, no
voiceover, no AI-voice monetization exposure, and they hit the algorithm's heaviest
weights (saves ≈ 5x likes, shares ≈ 10x — see vault [[niche-intel]] Cycle 6).

## The architecture (10-12 slides, 1080x1350 portrait)

1. **Slide 1 — HOOK.** Kicker line (category label, accent color, all-caps) → big claim
   headline with ONE number in accent ("10 skills to build a **$10M** business in 2026")
   → one-line FOMO subhead ("Most people are sleeping on every single one") → "SWIPE →".
   Never brand-first; curiosity-first.
2. **Slides 2-11 — ITEMS (one idea per slide).** Fixed anatomy, never deviate:
   - corner counter "n/12"
   - icon chip + kicker: "TOOL 0X / NAME" (or STORY 0X, MOVE 0X)
   - big display name with trailing period ("Ultron.") — matches our wordmark system
   - **one-line promise in accent color** — the slide's thesis, quotable on its own
   - 4-6 line body, ≤55 words, containing **exactly one concrete number**
     (stars, $, hours, %) — credibility-by-numbers, Coffeezilla doctrine
   - **"START WITH →" + 2-3 action pills** — every slide ends in an action, not a claim
3. **Final slide — THE CLOSER.** "THE BOTTOM LINE" kicker → consequence framing ("The
   people who master this win. The people who don't will be replaced by the people who
   do.") → explicit save instruction ("Save this, come back to it, start with one.") →
   comment prompt question ("Which one are you starting with? Comment below."). Dual CTA:
   saves feed the algorithm, comments feed engagement.

## Writing rules

- Every accent-line must land as a standalone quotable (Sam O'Nella density law).
- One number per slide, zero unverified numbers — verify each stat before it ships
  (policy doctrine: keep creativity receipts).
- Body lines are spoken-rhythm short. No sentence over ~14 words.
- Item count in the headline must be honest (10 items = 12 slides).
- Editorial fence applies (no deaths/abuse/victim-mocking — [[niche-intel]] Cycle 3).

## Channel skins

| Channel | Accent | Background motif | Item kicker |
|---|---|---|---|
| Kiwuuu main | lime #b8e352 | dark panel #141720, hairline borders | TOOL 0X |
| ABSURDITY. | red | cream + sketch doodles | STORY 0X |
| REKT. | green | cream + crashing-chart doodles | BLOWUP 0X |
| BLACK BOX. | blue | cream + circuit doodles | INCIDENT 0X |
| THE MACHINE. | orange | cream + robot doodles | MACHINE 0X |

## Production

1. Draft all slide copy first as a table (slide, kicker, headline, accent line, body,
   pills). Get founder eyes on copy BEFORE rendering.
2. Render via `assets/template.html` — one self-contained HTML file, 1080x1350 per
   slide; set the skin variables at the top, duplicate the `.slide` node per item,
   screenshot each slide (browser at 1080x1350, or headless chrome if available).
   Alternative when Higgsfield MCP is live: generate background plates with the
   channel's saved character, overlay text via the same template with transparent bg.
3. Export slide_01.jpg ... slide_N.jpg, post via Late as photo-mode carousel with
   trending-audio bed. Caption: one lowercase confident line + 5 niche hashtags
   (pattern: "pretty much all you need to X in 2026").
4. Log performance (saves:likes ratio is THE metric; target >1:1) in the channel's
   PATTERNS log.

## Story-bank starters (pre-verified wells in the vault)

- REKT.: "10 trades that vaporized billions" — pull from [[absurdity-network]] slate.
- BLACK BOX.: "10 times AI ended up in court" — AI-vs-the-Law arc.
- THE MACHINE.: "10 machines quietly running your life" — automation slate.
- Kiwuuu main: "10 AI skills agencies bill for in 2026" — Agency Tier top-of-funnel.
