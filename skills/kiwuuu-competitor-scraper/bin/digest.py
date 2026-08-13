#!/usr/bin/python3
"""Diff today's scrape vs yesterday's. Output a content brief at briefs/<date>.md.

Usage:
  python3 digest.py              # diff today vs yesterday
  python3 digest.py --date 2026-05-02 --vs 2026-05-01
"""
import argparse, json, sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA   = ROOT / "data"
BRIEFS = ROOT / "briefs"

def load(day):
    d = DATA / day
    if not d.exists(): return {}
    out = {}
    for f in d.glob("*.json"):
        try:
            out[f.stem] = json.loads(f.read_text())
        except Exception:
            pass
    return out

def diff_one(today, yesterday):
    """Return list of changes between two competitor dossiers."""
    if not yesterday: return ["NEW: first time tracked"]
    changes = []
    for page in ["homepage", "pricing", "blog"]:
        t = today.get("pages", {}).get(page, {}) or {}
        y = yesterday.get("pages", {}).get(page, {}) or {}
        if t.get("title") != y.get("title") and (t.get("title") or y.get("title")):
            changes.append(f"[{page}] title changed: '{y.get('title','')[:100]}' → '{t.get('title','')[:100]}'")
        new_prices = sorted(set(t.get("prices_found",[])) - set(y.get("prices_found",[])))
        gone_prices = sorted(set(y.get("prices_found",[])) - set(t.get("prices_found",[])))
        if new_prices:
            changes.append(f"[{page}] new price token(s): {', '.join(new_prices[:6])}")
        if gone_prices:
            changes.append(f"[{page}] removed price token(s): {', '.join(gone_prices[:6])}")
        new_h1 = set(t.get("h1",[])) - set(y.get("h1",[]))
        if new_h1:
            for h in list(new_h1)[:2]:
                changes.append(f"[{page}] new h1: '{h[:120]}'")
        new_articles = set(t.get("article_titles",[])) - set(y.get("article_titles",[]))
        if new_articles:
            for a in list(new_articles)[:3]:
                changes.append(f"[{page}] new article/headline: '{a[:120]}'")
    return changes

def suggested_angle(slug, changes):
    """Map raw changes to a Kiwuuu content angle suggestion."""
    if any("price" in c.lower() for c in changes):
        return f"PRICING ANGLE: {slug} moved pricing — opportunity for €97-flat counter-positioning. See council A02 BSP Markup Tax."
    if any("ai" in c.lower() or "agent" in c.lower() for c in changes):
        return f"POSITIONING ANGLE: {slug} is leaning into AI/agent language — sharpen 'workforce not chatbot' (council A09)."
    if any("blog" in c.lower() or "article" in c.lower() for c in changes):
        return f"REACTIVE CONTENT: {slug} published new content — consider response/contrarian post within 24h."
    if changes:
        return f"NOISE WATCH: {slug} changed something. Review manually."
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--vs", default=(date.today() - timedelta(days=1)).isoformat())
    args = ap.parse_args()

    today = load(args.date)
    yesterday = load(args.vs)

    if not today:
        print(f"No data for {args.date}. Run scrape.py first."); sys.exit(2)

    BRIEFS.mkdir(parents=True, exist_ok=True)
    out_md = BRIEFS / f"{args.date}.md"
    out_json = BRIEFS / f"{args.date}.json"

    brief_data = {"date": args.date, "vs": args.vs, "competitors": {}}
    md_lines = [
        f"# Competitor brief — {args.date} (vs {args.vs})",
        "",
        f"Tracked: {len(today)} competitors. New since yesterday: {len(set(today)-set(yesterday))}.",
        "",
    ]

    pricing_moves = []
    positioning_moves = []
    new_content = []
    suggested_kiwuuu_angles = []

    for slug, data in sorted(today.items()):
        y = yesterday.get(slug, {})
        changes = diff_one(data, y)
        brief_data["competitors"][slug] = {"changes": changes}

        if not changes: continue
        md_lines.append(f"## {data.get('name', slug)}")
        for c in changes:
            md_lines.append(f"- {c}")
            if "price" in c.lower(): pricing_moves.append(f"{slug}: {c}")
            elif "h1" in c.lower() or "title" in c.lower(): positioning_moves.append(f"{slug}: {c}")
            else: new_content.append(f"{slug}: {c}")
        ang = suggested_angle(slug, changes)
        if ang:
            md_lines.append(f"- **→ {ang}**")
            suggested_kiwuuu_angles.append(ang)
        md_lines.append("")

    # Summary section at top
    summary = [
        "## Summary",
        "",
        "### What changed at competitors",
        ("- " + "\n- ".join(pricing_moves + positioning_moves + new_content)) if (pricing_moves or positioning_moves or new_content) else "- (nothing changed)",
        "",
        "### Pricing moves",
        ("- " + "\n- ".join(pricing_moves)) if pricing_moves else "- (none)",
        "",
        "### New positioning language",
        ("- " + "\n- ".join(positioning_moves)) if positioning_moves else "- (none)",
        "",
        "### Suggested Kiwuuu content angle for the week",
        ("- " + "\n- ".join(suggested_kiwuuu_angles[:5])) if suggested_kiwuuu_angles else "- (no urgent angle — keep current calendar)",
        "",
        "---",
        "",
    ]
    md_lines = md_lines[:3] + summary + md_lines[3:]
    out_md.write_text("\n".join(md_lines))

    brief_data["pricing_moves"] = pricing_moves
    brief_data["positioning_moves"] = positioning_moves
    brief_data["new_content"] = new_content
    brief_data["suggested_kiwuuu_angles"] = suggested_kiwuuu_angles
    out_json.write_text(json.dumps(brief_data, indent=2))

    print(f"Brief written: {out_md}")
    print(f"  pricing moves: {len(pricing_moves)}")
    print(f"  positioning:   {len(positioning_moves)}")
    print(f"  new content:   {len(new_content)}")

if __name__ == "__main__":
    main()
