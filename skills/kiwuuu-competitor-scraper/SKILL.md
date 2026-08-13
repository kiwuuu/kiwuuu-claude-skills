---
name: kiwuuu-competitor-scraper
description: Scrape WhatsApp BSP and AI agent competitor websites every 24h, diff against yesterday, and emit a content brief JSON/MD that the kiwuuu-video-factory and content-factory skills can consume. USE WHEN the user asks to "check what competitors are doing", "run the competitor scrape", "produce a competitive content brief", or wants a daily digest of pricing/positioning moves at ManyChat, Wati, Respond.io, Tidio, Trengo, Sintra, Lindy, Sierra, AiSensy, Chatarmin. Output lands in {data,briefs}/ next to the skill (deploy target: T1 cron — historical data archived in _quarantine/competitor-scraper-data/).
---

# Kiwuuu Competitor Scraper

Daily ethical scrape of competitor homepages + public social metadata, diffed against yesterday, output as a content brief the video-factory + content-factory consume.

## Workflow Routing

| Trigger | Workflow |
|---------|----------|
| run the competitor scrape, check what competitors are doing, competitive content brief, daily digest, what changed at competitors | `Workflows/Daily.md` |

## Why this skill

Sister to `kiwuuu-video-factory`. That skill makes content. This skill **decides what content to make** by surfacing what competitors changed in the last 24h:

- New headline / hero copy → potential Kiwuuu counter-positioning
- Price changes → opportunity for "$15 vs €97" angle (proven hook in `k_demo_pricing_final.mp4`)
- New feature launches → reactive content within 24h
- Blog post titles → topic gaps Kiwuuu can claim

## Pipeline

```
targets.yaml (10 competitors, seeded)
     │
     ▼
bin/scrape.py  ← polite GET, bs4 parse, 1s delay between hosts
     │           respects robots.txt, public pages only
     ▼
data/<YYYY-MM-DD>/<competitor>.json   (raw)
     │
     ▼
bin/digest.py  ← diffs today vs yesterday
     │
     ▼
briefs/<YYYY-MM-DD>.md                (content brief)
briefs/<YYYY-MM-DD>.json              (machine-readable for video-factory)
```

## Hard constraints

| Constraint | Implication |
|---|---|
| Respect robots.txt | Skip any path the target disallows for our UA |
| User-Agent: `Kiwuuu Content Research Bot — research@kiwuuu.com` | Identifies us; lets sites block if they want |
| 1s minimum delay between requests to the same host | Polite, no rate-limit triggers |
| **Never scrape behind logins** | No auth, no cookies, no protected content |
| Only homepage, `/pricing`, openly-listed `/blog` feeds | Public surface only |
| 24h cache: skip refetch if `data/<today>/<competitor>.json` exists | Avoids redundant load |
| Tolerate per-target failure | One competitor 5xx must not break the run |
| Filesystem output only | No auto-posting, no DMs, no email |

## Workflow routing

| Trigger | Workflow |
|---|---|
| Daily scheduled run | `Workflows/Daily.md` |
| Manual invocation, today only | `python3 bin/scrape.py && python3 bin/digest.py` |
| Dry-run (no network, no writes) | `python3 bin/scrape.py --dry-run` |
| Ad-hoc single target | `python3 bin/scrape.py --only <slug>` |

## Inputs

`targets.yaml` — list of competitors. Each entry:

```yaml
- slug: manychat
  name: ManyChat
  homepage: https://manychat.com/
  pricing: https://manychat.com/pricing
  blog: https://manychat.com/blog
  socials:
    linkedin: https://www.linkedin.com/company/manychat/
    twitter: https://twitter.com/manychat
```

## Output schema (data/<date>/<slug>.json)

```json
{
  "slug": "manychat",
  "fetched_at": "2026-05-01T06:00:14Z",
  "homepage": {"title": "...", "h1": "...", "meta_description": "...", "ok": true},
  "pricing": {"tiers": ["Free", "Pro $15/mo"], "ok": true},
  "blog": {"latest_post_title": "...", "latest_post_url": "...", "ok": true},
  "socials": {"linkedin": {"title": "...", "ok": true}, "twitter": {"title": "...", "ok": true}},
  "errors": []
}
```

## Brief schema (briefs/<date>.md)

Sections, in order:
1. **What changed at competitors** — bullet list, one line per change
2. **Pricing moves** — table: competitor / before / after / signal
3. **New positioning language** — phrases harvested from changed h1/title
4. **Suggested Kiwuuu content angle for the week** — 3 ranked angles, each with: hook, format suggestion, urgency

## File map

| File | What |
|---|---|
| `SKILL.md` | this file |
| `targets.yaml` | competitor list (10 seeded) |
| `bin/scrape.py` | scraper (bs4 + requests) |
| `bin/digest.py` | diff + brief generator |
| `cron.sh` | wrapper for cron, logs to `data/cron.log` |
| `Workflows/Daily.md` | daily run playbook |
| `data/<date>/` | per-day raw JSON |
| `briefs/<date>.{md,json}` | generated briefs |

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `requests.exceptions.SSLError` on a target | Cert mismatch or expired | Log error in target's `errors[]`, continue |
| 403 with our UA | Site explicitly blocks bots | Skip target, note in brief "blocked" |
| Diff produces empty brief | Nothing changed since yesterday | Brief says "no significant moves"; still write it |
| Yesterday's data missing (first run) | Cold start | Brief is "baseline established" — no diff |
| robots.txt forbids `/pricing` | Site doesn't want us there | Skip that path only, mark `pricing.ok = false` |

## Install (cron, daily 06:00 UTC)

```bash
crontab -l 2>/dev/null | grep -v 'kiwuuu-competitor-scraper' > /tmp/crontab.tmp
echo "0 6 * * * <path-to-skill-on-T1>/cron.sh"  # T1 = 169.58.50.23; set the real path when deploying >> /tmp/crontab.tmp
crontab /tmp/crontab.tmp
rm /tmp/crontab.tmp
crontab -l | grep kiwuuu-competitor-scraper
```

## Manual smoke test

```bash
cd <path-to-skill>  # PC: C:/Users/Korisnik/kiwuuu-skills-review/claude-skills/.claude/skills/kiwuuu-competitor-scraper · T1: set on deploy
python3 bin/scrape.py --dry-run     # parse targets.yaml, no network, no writes
python3 bin/scrape.py --only manychat
python3 bin/digest.py
```
