#!/usr/bin/python3
"""
Kiwuuu Video Factory — one command, end-to-end.
Reads a YAML config, generates clips + voiceovers, composes finals, deploys to Cloudflare-fronted origin.

Usage:
  python3 factory.py path/to/config.yaml

YAML schema:
  concepts:
    - slug: k_demo_<name>
      prompt: <visual prompt>
      voiceover: <voiceover text>
      captions:
        - [start_sec, end_sec, "TEXT"]
        - ...
"""
import os, sys, time, json, subprocess, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
# Capture the spend-gate override from the REAL environment BEFORE dotenv can inject it.
# A stray FACTORY_YES=1 in /root/kiwubot/.env must never silently disable the cost gate.
_FACTORY_YES_ENV = os.environ.get("FACTORY_YES") == "1"
load_dotenv('/root/kiwubot/.env')
if not os.environ.get("FAL_KEY") and os.environ.get("FAL_API_KEY"):
    os.environ["FAL_KEY"] = os.environ["FAL_API_KEY"]
import fal_client
import requests
import yaml

OUT  = Path("/var/www/kiwuuu/media/content")
OUT.mkdir(parents=True, exist_ok=True)
THUMBS = OUT / "thumbs"
THUMBS.mkdir(parents=True, exist_ok=True)

VIDEO_EP   = "fal-ai/wan/v2.2-a14b/text-to-video/turbo"
VOICE_ID   = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
TTS_MODEL  = "eleven_turbo_v2_5"
TTS_KEY    = os.environ["ELEVENLABS_API_KEY"]
FONT       = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# wan/v2.2 turbo confirmed range 2026-05-01: ~$0.10-0.20 per 5s clip; TTS negligible
EST_CLIP_LOW  = 0.10
EST_CLIP_HIGH = 0.20
# Final-clip upload guard. 0 disables. Default 25MB fits every social platform's cap.
MAX_FINAL_MB  = float(os.environ.get("FACTORY_MAX_MB", "25"))

def gen_video(slug, prompt):
    """Submit to wan/turbo and download mp4. Returns (path, elapsed_s)."""
    t0 = time.time()
    h = fal_client.submit(VIDEO_EP, arguments={
        "prompt": prompt, "duration": 5, "resolution": "720p", "aspect_ratio": "9:16",
    })
    deadline = t0 + 240
    while time.time() < deadline:
        st = str(h.status()).upper()
        if "COMPLET" in st:
            r = h.get()
            url = (r.get("video") or {}).get("url") or r.get("url")
            out = OUT / f"{slug}.mp4"
            urllib.request.urlretrieve(url, out)
            return out, time.time() - t0
        if "FAIL" in st:
            raise RuntimeError(f"video gen failed: {st}")
        time.sleep(5)
    raise TimeoutError(f"video gen timeout for {slug}")

def gen_voice(slug, text):
    """ElevenLabs TTS → mp3."""
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={"xi-api-key": TTS_KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        json={"text": text, "model_id": TTS_MODEL,
              "voice_settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.30, "use_speaker_boost": True}},
        timeout=60,
    )
    r.raise_for_status()
    out = OUT / f"{slug}_vo.mp3"
    out.write_bytes(r.content)
    return out

def probe_dur(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())

def build_drawtext(captions):
    parts = []
    for s, e, t in captions:
        safe = str(t).replace(":", r"\:").replace("'", r"\'")
        parts.append(
            f"drawtext=fontfile={FONT}:text='{safe}':fontcolor=white:fontsize=72"
            f":box=1:boxcolor=black@0.78:boxborderw=22:x=(w-text_w)/2:y=h-(h*0.18)"
            f":enable='between(t,{s},{e})'"
        )
    return ",".join(parts)

def ensure_under_size(final, slug, max_mb=MAX_FINAL_MB):
    """If final mp4 exceeds the upload cap, re-encode tighter (rising CRF) from the
    original until it fits or the floor is hit. Mirrors the auto-compress-on-limit retry."""
    if max_mb <= 0:
        return final
    size_mb = final.stat().st_size / (1024 * 1024)
    if size_mb <= max_mb:
        return final
    best = None
    for crf in (24, 28, 32):
        tmp = final.with_name(f"{final.stem}.c{crf}.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", str(final),
            "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(tmp),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[{slug}] compress crf={crf} failed: {r.stderr[-200:]}"); sys.stdout.flush()
            continue
        new_mb = tmp.stat().st_size / (1024 * 1024)
        print(f"[{slug}] {size_mb:.1f}MB > {max_mb:.0f}MB cap → crf={crf} → {new_mb:.1f}MB"); sys.stdout.flush()
        best = tmp
        if new_mb <= max_mb:
            break
    if best is not None:
        best.replace(final)
    for crf in (24, 28, 32):
        leftover = final.with_name(f"{final.stem}.c{crf}.mp4")
        if leftover.exists():
            leftover.unlink()
    final_mb = final.stat().st_size / (1024 * 1024)
    if final_mb > max_mb:
        print(f"[{slug}] WARNING: still {final_mb:.1f}MB after max compression (cap {max_mb:.0f}MB)"); sys.stdout.flush()
    return final

def compose(slug, captions):
    """Slow-mo + voiceover + captions → final mp4."""
    raw   = OUT / f"{slug}.mp4"
    vo    = OUT / f"{slug}_vo.mp3"
    final = OUT / f"{slug}_final.mp4"
    pts   = max(1.0, probe_dur(vo) / probe_dur(raw))
    vf    = f"[0:v]setpts={pts:.4f}*PTS,scale=1080:1920:flags=lanczos,{build_drawtext(captions)}[v]"
    cmd = [
        "ffmpeg", "-y", "-i", str(raw), "-i", str(vo),
        "-filter_complex", vf, "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-r", "30", "-pix_fmt", "yuv420p",
        str(final),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])
    # poster
    subprocess.run([
        "ffmpeg", "-y", "-ss", "6", "-i", str(final),
        "-vframes", "1", "-q:v", "3",
        str(THUMBS / f"{slug}_thumb.jpg"),
    ], capture_output=True)
    return ensure_under_size(final, slug)

def process_concept(c):
    slug = c["slug"]
    print(f"[{slug}] gen video"); sys.stdout.flush()
    raw, vid_elapsed = gen_video(slug, c["prompt"])
    print(f"[{slug}] video done in {vid_elapsed:.0f}s ({raw.stat().st_size//1024}KB)"); sys.stdout.flush()
    print(f"[{slug}] gen voice"); sys.stdout.flush()
    gen_voice(slug, c["voiceover"])
    print(f"[{slug}] compose"); sys.stdout.flush()
    final = compose(slug, c["captions"])
    print(f"[{slug}] DONE → {final}"); sys.stdout.flush()
    return slug, str(final)

def confirm_spend(concepts, dry_run, auto_yes):
    """Show the estimated batch cost and gate generation behind a confirmation.
    Returns True to proceed, False to abort before any fal call."""
    n = len(concepts)
    lo, hi = n * EST_CLIP_LOW, n * EST_CLIP_HIGH
    print(f"Cost estimate: {n} clip(s) × ~$0.10–$0.20 (wan/turbo) + TTS (negligible)")
    print(f"  → est. total ~${lo:.2f}–${hi:.2f}"); sys.stdout.flush()
    if dry_run:
        print("--dry-run: priced only, nothing generated.")
        return False
    if auto_yes:
        print("--yes / FACTORY_YES=1 → proceeding without prompt.")
        return True
    if not sys.stdin.isatty():
        print("Non-interactive stdin and no --yes/FACTORY_YES=1 → aborting before spend.")
        return False
    resp = input(f"Proceed and spend up to ~${hi:.2f}? [y/N] ").strip().lower()
    if resp not in ("y", "yes"):
        print("Aborted by user — nothing generated.")
        return False
    return True

def main():
    args = sys.argv[1:]
    unknown = [a for a in args if a.startswith("--") and a not in ("--yes", "--dry-run")]
    if unknown:
        print(f"unknown flag(s): {' '.join(unknown)}")
        print("usage: factory.py [--dry-run] [--yes] <config.yaml>")
        sys.exit(2)
    dry_run  = "--dry-run" in args
    auto_yes = "--yes" in args or _FACTORY_YES_ENV
    positional = [a for a in args if not a.startswith("--")]
    if not positional:
        print("usage: factory.py [--dry-run] [--yes] <config.yaml>")
        sys.exit(2)
    cfg = yaml.safe_load(Path(positional[0]).read_text())
    concepts = cfg["concepts"]
    if not confirm_spend(concepts, dry_run, auto_yes):
        sys.exit(0)
    print(f"Processing {len(concepts)} concepts in parallel")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=min(len(concepts), 5)) as ex:
        futures = [ex.submit(process_concept, c) for c in concepts]
        results = []
        for f in as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                print(f"✗ failed: {e}")
    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s. Outputs:")
    for slug, path in results:
        print(f"  https://kiwuuu.com/media/content/{slug}_final.mp4")

if __name__ == "__main__":
    main()
