#!/usr/bin/python3
"""Gather raw material for a viral-video breakdown WITHOUT downloading by default.

Transcript comes from Supadata (URL in, text out — no media). Frames are pulled
only with --frames N (download -> extract N stills -> delete the video), for clips
whose payload is on-screen (tool lists, UI, diagrams) rather than spoken.

Usage:
  gather.py <url> [<url> ...] [--frames N] [--out DIR]
Output: <out>/<slug>.json per video (+ <out>/frames/<slug>/*.jpg) and a summary table.
"""
import sys, os, re, json, time, subprocess, tempfile, shutil
from pathlib import Path
import requests

# Env resolution: $YT_ENGINE_ENV override > .env next to this skill > legacy old-VPS path (historical)
ENV = Path(os.environ.get("YT_ENGINE_ENV") or (Path(__file__).resolve().parent.parent / ".env"))
def supadata_key():
    if ENV.exists():
        for ln in ENV.read_text().splitlines():
            if ln.startswith("SUPADATA_API_KEY="):
                return ln.split("=", 1)[1].strip()
    return os.environ.get("SUPADATA_API_KEY", "")

KEY = supadata_key()

def slugify(url):
    m = re.search(r"(\d{6,})", url) or re.search(r"([A-Za-z0-9_-]{6,})/?$", url)
    base = m.group(1) if m else "video"
    host = re.sub(r"^www\.", "", re.sub(r"https?://", "", url).split("/")[0]).split(".")[0]
    return f"{host}_{base}"[:60]

def transcript(url):
    if not KEY:
        return None, "no SUPADATA_API_KEY"
    try:
        r = requests.get("https://api.supadata.ai/v1/transcript",
                         params={"url": url, "text": "true"},
                         headers={"x-api-key": KEY}, timeout=120)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}: {r.text[:120]}"
        j = r.json()
        if isinstance(j, dict) and j.get("jobId"):
            jid = j["jobId"]
            for _ in range(40):
                time.sleep(3)
                jj = requests.get(f"https://api.supadata.ai/v1/transcript/{jid}",
                                  headers={"x-api-key": KEY}, timeout=60).json()
                st = jj.get("status")
                if st == "completed":
                    j = jj.get("result", jj); break
                if st == "failed":
                    return None, f"failed: {jj.get('error')}"
            else:
                return None, "timeout polling"
        c = j.get("content") if isinstance(j, dict) else None
        if isinstance(c, list):
            c = " ".join(s.get("text", "") for s in c)
        return (c or None), (None if c else "empty")
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:100]}"

YT_ID = re.compile(r"(?:youtu\.be/|[?&]v=|/shorts/|/embed/)([A-Za-z0-9_-]{11})")

def metadata(url):
    m = YT_ID.search(url)
    if m and KEY:
        try:
            r = requests.get("https://api.supadata.ai/v1/youtube/video",
                             params={"id": m.group(1)}, headers={"x-api-key": KEY}, timeout=40)
            if r.status_code == 200:
                j = r.json(); ch = j.get("channel") or {}
                return {"title": j.get("title"), "description": j.get("description"),
                        "uploader": ch.get("name"), "duration": j.get("duration"),
                        "view_count": j.get("viewCount"), "like_count": j.get("likeCount"),
                        "comment_count": None, "upload_date": j.get("uploadDate")}
        except Exception:
            pass
    try:
        out = subprocess.run(["yt-dlp", "-J", "--skip-download", "--no-warnings", url],
                             capture_output=True, text=True, timeout=90)
        d = json.loads(out.stdout)
        return {k: d.get(k) for k in ("title", "description", "uploader", "duration",
                "view_count", "like_count", "comment_count", "repost_count")}
    except Exception:
        return {}

def frames(url, n, dst):
    dst.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    try:
        mp4 = tmp / "v.mp4"
        subprocess.run(["yt-dlp", "-f", "mp4/best", "--no-warnings", "-o", str(mp4), url],
                       capture_output=True, text=True, timeout=180)
        if not mp4.exists():
            cand = list(tmp.glob("v.*"))
            if not cand: return []
            mp4 = cand[0]
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
              "format=duration", "-of", "csv=p=0", str(mp4)],
              capture_output=True, text=True, timeout=30).stdout.strip() or 30)
        fps = max(n / dur, 0.05)
        subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-vf",
                        f"fps={fps:.4f},scale=540:-1", "-frames:v", str(n),
                        str(dst / "f_%02d.jpg")], capture_output=True, timeout=120)
        return sorted(str(p) for p in dst.glob("f_*.jpg"))
    except Exception:
        return []
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    args = sys.argv[1:]
    nframes = 0; out = Path("/tmp/kiwuuu-analyze")
    urls = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--frames": nframes = int(args[i+1]); i += 2
        elif a == "--out": out = Path(args[i+1]); i += 2
        else: urls.append(a); i += 1
    if not urls:
        print("usage: gather.py <url> [<url> ...] [--frames N] [--out DIR]"); sys.exit(1)
    out.mkdir(parents=True, exist_ok=True)
    print(f"{'video':28} {'transcript':>11}  {'frames':>6}  note")
    manifest = []
    for url in urls:
        slug = slugify(url)
        txt, err = transcript(url)
        meta = metadata(url)
        fr = frames(url, nframes, out / "frames" / slug) if nframes > 0 else []
        rec = {"url": url, "slug": slug, "meta": meta,
               "transcript": txt, "transcript_error": err, "frames": fr}
        (out / f"{slug}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        manifest.append(rec)
        tlen = f"{len(txt)} ch" if txt else "—"
        print(f"{slug:28} {tlen:>11}  {len(fr):>6}  {err or 'ok'}")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\nwrote {len(manifest)} record(s) -> {out}/  (read the .json transcripts; view frames/*.jpg if present)")

if __name__ == "__main__":
    main()
