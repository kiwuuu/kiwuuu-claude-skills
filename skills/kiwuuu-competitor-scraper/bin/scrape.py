#!/usr/bin/python3
"""Daily competitor scrape. Fetches homepage + /pricing + /blog feed for each target.
Saves raw extracts to data/<date>/<slug>.json. Polite UA, robots.txt-respecting, 1s host throttle.

Usage:
  python3 scrape.py              # full daily run
  python3 scrape.py --dry-run    # no writes
  python3 scrape.py --only manychat  # one target
"""
import argparse, json, sys, time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "targets.yaml"
DATA   = ROOT / "data"

UA = "Kiwuuu Content Research Bot - research@kiwuuu.com"
HOST_DELAY = 1.0  # seconds between requests to same host
TIMEOUT = 12

def allowed(url):
    """robots.txt check — respect a real (HTTP 200) robots.txt, but fail OPEN on any
    non-200 or fetch failure. RobotFileParser.read() treats a CDN 401/403 on the robots
    fetch as disallow-all; fetching it ourselves and only parsing 200s avoids that trap
    (which previously marked every Cloudflare-fronted target 'blocked-by-robots')."""
    try:
        p = urlparse(url)
        robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
        rr = requests.get(robots_url, headers={"User-Agent": UA, "Accept": "text/plain,*/*"}, timeout=TIMEOUT)
        if rr.status_code != 200 or not rr.text.strip():
            return True  # no parseable robots → allow (polite default)
        rp = RobotFileParser()
        rp.parse(rr.text.splitlines())
        return rp.can_fetch(UA, url)
    except Exception:
        return True  # don't block on robots-fetch failures

def fetch(url):
    if not allowed(url):
        return None, "blocked-by-robots"
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"}, timeout=TIMEOUT)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        return r.text, None
    except Exception as e:
        return None, f"exc:{type(e).__name__}"
    finally:
        time.sleep(HOST_DELAY)

def parse(html):
    """Extract a small structured dossier from HTML."""
    if not html: return {}
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.find("title").get_text(strip=True) if soup.find("title") else "")[:200]
    h1s = [h.get_text(strip=True)[:200] for h in soup.find_all("h1")[:3]]
    h2s = [h.get_text(strip=True)[:160] for h in soup.find_all("h2")[:8]]
    # Look for explicit price tokens
    body = soup.get_text(" ", strip=True)
    import re
    prices = sorted(set(re.findall(r"[€$£]\s?\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?(?:/(?:mo|month|year|user|contact))?", body)))[:12]
    # First 5 article-list links (blog feed proxy)
    article_titles = [a.get_text(strip=True)[:120] for a in soup.select("article h2, article h3, article a") if a.get_text(strip=True)][:8]
    meta_desc = ""
    md = soup.find("meta", attrs={"name":"description"}) or soup.find("meta", attrs={"property":"og:description"})
    if md and md.get("content"):
        meta_desc = md["content"][:300]
    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1s,
        "h2": h2s,
        "prices_found": prices,
        "article_titles": article_titles,
    }

def scrape_target(t, dry_run=False):
    out = {"slug": t["slug"], "name": t["name"], "category": t.get("category",""), "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pages": {}}
    for key in ["homepage", "pricing", "blog"]:
        url = t.get(key)
        if not url: continue
        html, err = fetch(url)
        if err:
            out["pages"][key] = {"url": url, "error": err}
        else:
            out["pages"][key] = {"url": url, **parse(html)}
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="single target slug")
    args = ap.parse_args()

    cfg = yaml.safe_load(TARGETS.read_text())
    targets = cfg["competitors"]
    if args.only:
        targets = [t for t in targets if t["slug"] == args.only]
        if not targets:
            print(f"no target with slug={args.only}"); sys.exit(2)

    today = date.today().isoformat()
    out_dir = DATA / today
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scraping {len(targets)} target(s) → {out_dir}")
    total_ok = 0
    total_pages = 0
    for t in targets:
        print(f"  · {t['slug']:12s}", end=" ", flush=True)
        try:
            data = scrape_target(t, dry_run=args.dry_run)
            ok = sum(1 for p in data["pages"].values() if "error" not in p)
            total_ok += ok
            total_pages += len(data["pages"])
            print(f"{ok}/{len(data['pages'])} pages")
            if not args.dry_run:
                (out_dir / f"{t['slug']}.json").write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"FAIL: {e}")

    print(f"\ndone. {total_ok}/{total_pages} pages fetched across {len(targets)} target(s).")
    # Fail loudly on a total wipe so cron stops writing misleading "nothing changed" briefs.
    if total_pages and total_ok == 0:
        print(f"ERROR: 0/{total_pages} pages fetched — total failure (check UA/robots/network).", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
