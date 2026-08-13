# Daily Workflow

End-to-end: scrape 10 competitors → diff vs yesterday → produce a content brief.
Target wall-clock: ~3 minutes.

## Steps

### 1. Scrape

```bash
python3 <skill-dir>/bin/scrape.py   # run from the skill directory
```

Outputs `data/<today>/<slug>.json` for each competitor. Honors robots.txt, 1s polite throttle, fails-open on per-target errors.

### 2. Digest

```bash
python3 <skill-dir>/bin/digest.py
```

Outputs:
- `briefs/<today>.md` — human-readable summary
- `briefs/<today>.json` — structured for downstream consumption

### 3. Wire into content engine (manual or cron)

The brief's `suggested_kiwuuu_angles` field is the high-leverage signal. Pipe into:
- `kiwuuu-video-factory` if a pricing move triggers a fast-response video
- `/studio/library/posts/` rewrite agent if positioning language needs counter-attack
- The 90-day calendar at `/studio/calendar/` — bump a relevant week's theme

## When NOT to run

- Within 24h of last successful run (cache).
- If `/var/run/kiwuuu/scraper_halt.flag` exists.
- If you suspect Kiwuuu is being blocked (consecutive failures across 3+ targets).

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| All targets HTTP 403 | UA banned | Rotate UA or back off 24h |
| Single target hangs | Slow site | Per-request 12s timeout already kills it |
| Empty pricing extract | Site moved to JS-rendered pricing | Add Playwright fallback (future) |
| robots.txt blocks /pricing | Some BSPs block | Skip that page, scrape homepage only |
