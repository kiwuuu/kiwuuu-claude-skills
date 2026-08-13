#!/usr/bin/env python3
"""Create / list the Kiwuuu delivery templates — the always-open channel.

  wa_templates.py --list      show templates + approval status
  wa_templates.py --create    create the three delivery templates
  wa_templates.py --waba      resolve the WABA id (needs asset assignment)

Templates let us reach Kiwu OUTSIDE the 24h service window. Without them the only
way in is him messaging the business number first.
"""
import argparse, json, re, sys, urllib.request, urllib.error

SECRETS = r"C:\Users\Korisnik\kiwuuu-backup\memory\SECRETS_LOCAL.md"
B = "https://graph.facebook.com/v21.0"
# kiwu-bot system user. The Business Manager id is 61569227937728 (shown in the UI);
# /me returns 122095945526640931, the app-scoped alias. Asset edges want the BM id, but
# reading them needs business_management — which this token does not have. So the
# reliable path is WHATSAPP_WABA_ID in SECRETS_LOCAL.md.
SU = "61569227937728"


def secret(n, required=True):
    m = re.search(rf"{n}\s*=\s*([^\s]+)", open(SECRETS, encoding="utf-8").read())
    if not m and required:
        sys.exit(f"missing {n}")
    return m.group(1).strip() if m else None


TOKEN = secret("WHATSAPP_ACCESS_TOKEN")


def api(path, data=None, method=None):
    h = {"Authorization": f"Bearer {TOKEN}"}
    if data:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{B}/{path}", data=json.dumps(data).encode() if data else None,
                                 headers=h, method=method)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        return {"ERR": e.code, "body": e.read().decode()[:400]}


def resolve_waba():
    """WABA id: explicit override in secrets, else the system user's assigned asset."""
    override = secret("WHATSAPP_WABA_ID", required=False)
    if override:
        return override
    r = api(f"{SU}/assigned_whatsapp_business_accounts?fields=id,name")
    data = r.get("data") or []
    if not data:
        sys.exit(
            "No WABA assigned to the kiwu-bot system user.\n\n"
            "FIX (one time, ~1 min):\n"
            "  business.facebook.com > Settings > Users > System Users > kiwu-bot\n"
            "  > Add Assets > WhatsApp Accounts > select 'Kiwuuu AI'\n"
            "  > enable Full control > Save\n\n"
            "Or paste the id straight into SECRETS_LOCAL.md as:\n"
            "  WHATSAPP_WABA_ID=<id from WhatsApp Manager>\n"
            "(NOTE: WHATSAPP_BUSINESS_ACCOUNT_ID=2258537087886158 is the Business\n"
            " Portfolio id, NOT the WABA — that mislabel cost a debugging round.)")
    print(f"WABA: {data[0]['id']}  ({data[0].get('name')})")
    return data[0]["id"]


# Three templates = full coverage.
#  ping     -> cheapest way to reopen the free window for anything
#  document -> any file type in one shot
#  video    -> inline playable video in one shot
TEMPLATES = [
    {
        "name": "kiwuuu_delivery_ping",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "BODY",
             "text": "Your requested file is ready: {{1}}\n\nReply to this message and it will be sent through.",
             "example": {"body_text": [["banana_final.mp4"]]}},
        ],
    },
    {
        "name": "kiwuuu_delivery_document",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "HEADER", "format": "DOCUMENT",
             "example": {"header_handle": ["REPLACE_WITH_HANDLE"]}},
            {"type": "BODY", "text": "Here is the file you asked for: {{1}} — sent from Kiwuuu.",
             "example": {"body_text": [["report.pdf"]]}},
        ],
    },
    {
        "name": "kiwuuu_delivery_video",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "HEADER", "format": "VIDEO",
             "example": {"header_handle": ["REPLACE_WITH_HANDLE"]}},
            {"type": "BODY", "text": "Here is the video you asked for: {{1}} — sent from Kiwuuu.",
             "example": {"body_text": [["banana_final.mp4"]]}},
        ],
    },
]


def cmd_list(waba):
    r = api(f"{waba}/message_templates?limit=50&fields=name,status,category,language,components")
    if "ERR" in r:
        print(json.dumps(r, indent=1)); return
    ts = r.get("data", [])
    print(f"{len(ts)} template(s)\n")
    for t in ts:
        hdr = next((c.get("format") for c in t.get("components", []) if c.get("type") == "HEADER"), "-")
        print(f"  {t['status']:9} {t['category']:9} {t['language']:5} header={hdr:9} {t['name']}")


APP_ID = "1689690292022154"


def upload_handle(path, mime):
    """Resumable upload -> sample media handle for a template media HEADER."""
    import os
    n = os.path.getsize(path)
    q = (f"{APP_ID}/uploads?file_name={os.path.basename(path)}"
         f"&file_length={n}&file_type={mime}")
    sess = api(q, data={}, method="POST")
    if "ERR" in sess:
        return None, sess
    sid = sess["id"]
    req = urllib.request.Request(f"{B}/{sid}", data=open(path, "rb").read(),
                                 headers={"Authorization": f"OAuth {TOKEN}", "file_offset": "0"},
                                 method="POST")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=300).read())["h"], None
    except urllib.error.HTTPError as e:
        return None, {"ERR": e.code, "body": e.read().decode()[:300]}


SAMPLES = {"kiwuuu_delivery_video": ("sample.mp4", "video/mp4"),
           "kiwuuu_delivery_document": ("sample.pdf", "application/pdf")}


def cmd_create(waba, sample_dir=None):
    import os
    for t in TEMPLATES:
        t = json.loads(json.dumps(t))          # deep copy
        hdr = next((c for c in t["components"] if c.get("type") == "HEADER"), None)
        if hdr:
            fname, mime = SAMPLES[t["name"]]
            path = os.path.join(sample_dir or ".", fname)
            if not os.path.exists(path):
                print(f"  ! {t['name']}: sample {path} missing — skipped")
                continue
            h, err = upload_handle(path, mime)
            if not h:
                print(f"  ! {t['name']}: sample upload failed {json.dumps(err)[:200]}")
                continue
            hdr["example"]["header_handle"] = [h]
        r = api(f"{waba}/message_templates", data=t)
        ok = "id" in r
        print(f"  {'OK ' if ok else 'ERR'} {t['name']}: {json.dumps(r)[:220]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--create", action="store_true")
    ap.add_argument("--waba", action="store_true")
    a = ap.parse_args()
    w = resolve_waba()
    if a.waba: sys.exit()
    if a.create: cmd_create(w)
    else: cmd_list(w)
