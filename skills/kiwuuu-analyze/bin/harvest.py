#!/usr/bin/env python3
"""Harvest transcripts + engagement stats WITHOUT a Supadata key and WITHOUT keeping media.

Proven on T3 2026-08-08: pulled 53 TikTok + 35 YouTube transcripts for the Kallaway study.
Use this when gather.py returns "no SUPADATA_API_KEY" (the key never made it off the old VPS).

    # whole TikTok profile -> ranked video list
    python harvest.py profile https://www.tiktok.com/@handle --out DIR

    # YouTube channel -> ranked video list
    python harvest.py profile https://www.youtube.com/@handle/videos --out DIR

    # transcripts for specific videos (YouTube ids or full URLs)
    python harvest.py fetch DIR VIDEO_ID_OR_URL [...]

    # transcripts for every video found by `profile` (YouTube only; see TikTok note)
    python harvest.py fetch-all DIR [--limit N]

Requires: pip install --user yt-dlp truststore requests   (no ffmpeg needed)

TIKTOK CAVEAT — read before you fight it:
  yt-dlp hits TikTok's bot wall on individual video pages roughly half the time, but the
  PROFILE listing works fine. For per-video TikTok transcripts the reliable path is the
  in-app browser: navigate to any tiktok.com page once, then fetch the video URLs from
  inside that origin with credentials:'include', parse
  __UNIVERSAL_DATA_FOR_REHYDRATION__ -> __DEFAULT_SCOPE__["webapp.video-detail"]
      .itemInfo.itemStruct -> {desc, stats, video.subtitleInfos[].Url}
  and hand the signed subtitle URLs to `python harvest.py vtt DIR < urls.json`.
  Signed subtitle URLs expire — fetch them in the same session you extracted them.
  Fetch the VTT with plain requests + a normal UA + Referer https://www.tiktok.com/ ;
  fetching it from inside the page origin returns the TikTok HTML shell instead.
  Full writeup: vault lessons/2026-08-03_tiktok-transcripts-without-supadata.md
"""
import json
import os
import re
import sys
from pathlib import Path

# A BitLocker-locked D: drive makes yt-dlp's PATH scan for helper binaries throw. Drop it.
os.environ["PATH"] = os.pathsep.join(
    p for p in os.environ.get("PATH", "").split(os.pathsep) if not p.upper().startswith("D:")
)

import truststore  # noqa: E402  — use the Windows cert store instead of disabling TLS verify
truststore.inject_into_ssl()
import requests  # noqa: E402
import yt_dlp  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def vtt_to_text(vtt: str) -> str:
    """WebVTT -> plain prose, dropping cue numbers, timings and duplicate rolling lines."""
    out, prev = [], None
    for ln in vtt.splitlines():
        ln = ln.strip()
        if not ln or ln == "WEBVTT" or "-->" in ln or re.fullmatch(r"\d+", ln):
            continue
        if ln.startswith(("Kind:", "Language:", "NOTE", "Style:")):
            continue
        ln = re.sub(r"<[^>]+>", "", ln).strip()
        if ln and ln != prev:
            out.append(ln)
            prev = ln
    return " ".join(out)


def profile(url: str, out: Path):
    """List every video on a channel/profile, ranked by views. No media downloaded."""
    out.mkdir(parents=True, exist_ok=True)
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    rows = [{
        "id": e.get("id"),
        "title": (e.get("title") or "")[:200],
        "views": e.get("view_count"),
        "dur": e.get("duration"),
        "ts": e.get("timestamp"),
        "url": e.get("url") or e.get("webpage_url"),
    } for e in (info.get("entries") or [])]
    rows.sort(key=lambda r: r["views"] or 0, reverse=True)
    (out / "videos.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{info.get('channel') or info.get('title')}: {len(rows)} videos -> {out/'videos.json'}")
    for r in rows[:25]:
        print(f"  {r['views'] or 0:>9}  {int(r['dur'] or 0):>5}s  {r['id']}  {r['title'][:80]}")
    return rows


def fetch(out: Path, ids):
    """Pull auto-caption transcripts for specific videos. Writes out/transcripts/<id>.json."""
    dst_dir = out / "transcripts"
    dst_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
        for vid in ids:
            url = vid if "://" in vid else f"https://www.youtube.com/watch?v={vid}"
            key = re.sub(r"[^A-Za-z0-9_-]", "_", vid.rsplit("/", 1)[-1])[:60]
            dst = dst_dir / f"{key}.json"
            if dst.exists() and json.loads(dst.read_text(encoding="utf-8")).get("transcript"):
                print(f"{key}  cached")
                ok += 1
                continue
            rec = {"id": key, "url": url, "transcript": None, "error": None}
            try:
                info = ydl.extract_info(url, download=False)
                rec.update({
                    "title": info.get("title") or info.get("description", "")[:200],
                    "views": info.get("view_count"),
                    "likes": info.get("like_count"),
                    "comments": info.get("comment_count"),
                    "duration": info.get("duration"),
                    "chapters": [{"t": c.get("start_time"), "title": c.get("title")}
                                 for c in (info.get("chapters") or [])],
                })
                pool = {**(info.get("automatic_captions") or {}), **(info.get("subtitles") or {})}
                tracks = (pool.get("en") or pool.get("en-orig") or pool.get("en-US")
                          or next(iter(pool.values()), []))
                turl = next((t["url"] for t in tracks if t.get("ext") == "vtt"),
                            tracks[0]["url"] if tracks else None)
                if turl:
                    r = requests.get(turl, timeout=90, headers={"User-Agent": UA,
                                                               "Referer": "https://www.tiktok.com/"})
                    if r.status_code == 200 and r.text.lstrip().startswith("WEBVTT"):
                        rec["transcript"] = vtt_to_text(r.text)
                    else:
                        rec["error"] = f"caption HTTP {r.status_code}"
                else:
                    rec["error"] = "no caption track"
            except Exception as e:
                rec["error"] = f"{type(e).__name__}: {str(e)[:150]}"
            dst.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
            ok += bool(rec["transcript"])
            n = len(rec["transcript"]) if rec["transcript"] else 0
            print(f"{key}  {'OK ' + str(n) + 'ch' if n else 'FAIL: ' + str(rec['error'])}")
    print(f"\n{ok}/{len(ids)} transcripts -> {dst_dir}")


def vtt(out: Path, records):
    """Given [{id, desc, stats, subUrl}] scraped in-browser, fetch each VTT and store it."""
    dst_dir = out / "transcripts"
    dst_dir.mkdir(parents=True, exist_ok=True)
    sess = requests.Session()
    sess.headers.update({"User-Agent": UA, "Referer": "https://www.tiktok.com/"})
    ok = 0
    for rec in records:
        vid = str(rec.get("id", ""))
        if not vid:
            continue
        t, err = None, None
        if rec.get("subUrl"):
            try:
                r = sess.get(rec["subUrl"], timeout=60)
                if r.status_code == 200 and r.text.lstrip().startswith("WEBVTT"):
                    t = vtt_to_text(r.text)
                else:
                    err = f"vtt HTTP {r.status_code} (signed URL may have expired)"
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:100]}"
        else:
            err = "no subUrl (video has no ASR track — pull frames instead)"
        rec["transcript"], rec["transcript_error"] = t, err
        rec.pop("subUrl", None)
        (dst_dir / f"{vid}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
        ok += bool(t)
        print(f"{vid}  {'OK ' + str(len(t)) + 'ch' if t else 'FAIL: ' + str(err)}")
    print(f"\n{ok}/{len(records)} transcripts -> {dst_dir}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    cmd = args[0]
    if cmd == "profile":
        url = args[1]
        out = Path(args[args.index("--out") + 1]) if "--out" in args else Path("harvest")
        profile(url, out)
    elif cmd == "fetch":
        fetch(Path(args[1]), args[2:])
    elif cmd == "fetch-all":
        out = Path(args[1])
        rows = json.loads((out / "videos.json").read_text(encoding="utf-8"))
        if "--limit" in args:
            rows = rows[: int(args[args.index("--limit") + 1])]
        fetch(out, [r["id"] for r in rows])
    elif cmd == "vtt":
        vtt(Path(args[1]), json.load(sys.stdin))
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
