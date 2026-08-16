#!/usr/bin/env python3
"""Send a file or text to Kiwu's WhatsApp via the Kiwuuu Cloud API number.

  wa_send.py <file> [--caption "..."] [--as document] [--to +3816...]
  wa_send.py --text "message body"
  wa_send.py <file> --template          force the template path (outside 24h window)
  wa_send.py <file> --no-template       fail instead of falling back

Auto-compresses video over WhatsApp's real 16 MB cap, and auto-falls back to an approved
template when the 24 h service window is closed. See ../SKILL.md for the failure modes.
"""
import argparse, json, os, re, subprocess, sys, tempfile, urllib.request, urllib.error, uuid

SECRETS = r"C:\Users\Korisnik\kiwuuu-backup\memory\SECRETS_LOCAL.md"
BASE = "https://graph.facebook.com/v21.0"
KIWU = "+381693311331"                                   # personal phone — the recipient
CAPS = {"video": 16, "image": 5, "audio": 16, "document": 100}      # MB, real upload caps
TPL = {"video": "kiwuuu_delivery_video", "document": "kiwuuu_delivery_document",
       "ping": "kiwuuu_delivery_ping"}
MIME = {".mp4": ("video", "video/mp4"), ".mov": ("video", "video/mp4"),
        ".jpg": ("image", "image/jpeg"), ".jpeg": ("image", "image/jpeg"),
        ".png": ("image", "image/png"), ".mp3": ("audio", "audio/mpeg"),
        ".ogg": ("audio", "audio/ogg"), ".wav": ("audio", "audio/mpeg"),
        ".pdf": ("document", "application/pdf")}


def secret(name):
    m = re.search(rf"{name}\s*=\s*([^\s]+)", open(SECRETS, encoding="utf-8").read())
    if not m:
        sys.exit(f"missing {name} in {SECRETS}")
    return m.group(1).strip()


TOKEN = secret("WHATSAPP_ACCESS_TOKEN")
PNID = secret("WHATSAPP_PHONE_NUMBER_ID")


def api(path, data=None, headers=None, timeout=600, fatal=True):
    h = {"Authorization": f"Bearer {TOKEN}"}
    h.update(headers or {})
    try:
        return json.loads(urllib.request.urlopen(
            urllib.request.Request(f"{BASE}/{path}", data=data, headers=h), timeout=timeout).read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if not fatal:
            return {"ERR": e.code, "body": body}
        print(f"HTTP {e.code}: {body[:400]}")
        if "File Too Large" in body:
            print("\n-> over the type cap; retry with --as document")
        if '"code":190' in body:
            print("\n-> token dead. Business Settings > Users > System Users > "
                  "Generate New Token (expiration: Never)")
        sys.exit(1)


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(path):
    r = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else None


def shrink_video(path, target_mb=15.0):
    """Two-pass x264 to land just under the cap. Tuned for flat/animated art."""
    dur = duration(path) or sys.exit("could not probe duration")
    vb = max(120, int((target_mb * 8192) / dur - 64))
    out = os.path.join(tempfile.gettempdir(), f"wa_{uuid.uuid4().hex[:8]}.mp4")
    log = os.path.join(tempfile.gettempdir(), f"walog_{uuid.uuid4().hex[:8]}")
    print(f"compressing: {dur:.0f}s -> target {target_mb} MB (video {vb} kbps)")
    common = [ffmpeg(), "-y", "-i", path, "-c:v", "libx264", "-b:v", f"{vb}k",
              "-tune", "animation", "-preset", "slower", "-passlogfile", log,
              "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,fps=24"]
    subprocess.run(common + ["-pass", "1", "-an", "-f", "null", os.devnull], capture_output=True)
    subprocess.run(common + ["-pass", "2", "-c:a", "aac", "-b:a", "64k", "-ac", "1",
                             "-movflags", "+faststart", out], capture_output=True)
    if not os.path.exists(out):
        sys.exit("compression failed")
    print(f"compressed -> {os.path.getsize(out)/1048576:.2f} MB")
    return out


def upload(path, mime):
    b = uuid.uuid4().hex
    body = b""
    for n, v in [("messaging_product", "whatsapp"), ("type", mime)]:
        body += f"--{b}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n".encode()
    body += (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; "
             f"filename=\"{os.path.basename(path)}\"\r\nContent-Type: {mime}\r\n\r\n").encode()
    body += open(path, "rb").read() + f"\r\n--{b}--\r\n".encode()
    r = api(f"{PNID}/media", data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    print("uploaded:", r["id"])
    return r["id"]


def post(payload, fatal=True):
    return api(f"{PNID}/messages", data=json.dumps(payload).encode(),
               headers={"Content-Type": "application/json"}, timeout=180, fatal=fatal)


def template_payload(to, name, label, kind=None, media_id=None):
    comps = [{"type": "body", "parameters": [{"type": "text", "text": label}]}]
    if kind and media_id:
        comps.insert(0, {"type": "header",
                         "parameters": [{"type": kind, kind: {"id": media_id}}]})
    return {"messaging_product": "whatsapp", "to": to, "type": "template",
            "template": {"name": name, "language": {"code": "en"}, "components": comps}}


def deliver(payload, to, label, kind=None, media_id=None, allow_tpl=True):
    """Free send inside the window; approved template outside it."""
    r = post(payload, fatal=False)
    if "ERR" not in r:
        print("ACCEPTED ->", r["messages"][0]["id"])
        return
    body = r["body"]
    if "131047" not in body or not allow_tpl:
        print(f"HTTP {r['ERR']}: {body[:400]}")
        sys.exit(1)
    name = TPL.get(kind) if kind in ("video", "document") else TPL["ping"]
    print(f"24h window closed -> template '{name}'")
    r2 = post(template_payload(to, name, label, kind if kind in ("video", "document") else None,
                              media_id), fatal=False)
    if "ERR" in r2:
        print(f"template send failed: {r2['body'][:400]}")
        if "132001" in r2["body"]:
            print("-> template not approved yet; check wa_templates.py --list")
        sys.exit(1)
    print("TEMPLATE SENT ->", r2["messages"][0]["id"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--text")
    ap.add_argument("--caption", default="")
    ap.add_argument("--to", default=KIWU)
    ap.add_argument("--as", dest="force", choices=list(CAPS))
    ap.add_argument("--template", action="store_true", help="force template path")
    ap.add_argument("--no-template", action="store_true", help="never fall back")
    a = ap.parse_args()

    if a.text:
        if a.template:
            r = post(template_payload(a.to, TPL["ping"], a.text))
            print("TEMPLATE SENT ->", r["messages"][0]["id"])
        else:
            deliver({"messaging_product": "whatsapp", "to": a.to, "type": "text",
                     "text": {"body": a.text}}, a.to, a.text,
                    allow_tpl=not a.no_template)
        sys.exit()
    if not a.file:
        ap.error("give a file or --text")

    path = os.path.abspath(a.file)
    ext = os.path.splitext(path)[1].lower()
    kind, mime = MIME.get(ext, ("document", "application/octet-stream"))
    if a.force:
        kind = a.force
        mime = MIME[ext][1] if ext in MIME else "application/octet-stream"
    mb = os.path.getsize(path) / 1048576
    print(f"{os.path.basename(path)} ({mb:.2f} MB) as {kind} -> {a.to}")

    if mb > CAPS[kind]:
        if kind != "video":
            sys.exit(f"{mb:.1f} MB exceeds the {CAPS[kind]} MB cap for {kind}")
        path = shrink_video(path, CAPS["video"] - 1)

    mid = upload(path, mime)
    label = a.caption or os.path.basename(a.file)
    body = {"id": mid}
    if a.caption and kind in ("video", "image", "document"):
        body["caption"] = a.caption
    if kind == "document":
        body["filename"] = os.path.basename(a.file)

    if a.template:
        name = TPL.get(kind, TPL["ping"])
        r = post(template_payload(a.to, name, label,
                                  kind if kind in ("video", "document") else None, mid))
        print("TEMPLATE SENT ->", r["messages"][0]["id"])
    else:
        deliver({"messaging_product": "whatsapp", "to": a.to, "type": kind, kind: body},
                a.to, label, kind, mid, allow_tpl=not a.no_template)
