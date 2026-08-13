---
name: send-to-my-whatsapp
description: Send a file (video, image, PDF, any document) or a text message to Kiwu's own WhatsApp via the Kiwuuu Cloud API number. USE WHEN Kiwu says "send it to my whatsapp", "send me that on whatsapp", "whatsapp me the video/file", or asks for any deliverable on his phone. Handles credential lookup, auto-compression to WhatsApp's real media caps, the correct recipient, and the 24-hour-window failure mode.
---

# send-to-my-whatsapp

One command to put a local file on Kiwu's phone. Wraps the Kiwuuu WhatsApp Cloud API number.

```bash
python C:/Users/Korisnik/.claude/skills/send-to-my-whatsapp/bin/wa_send.py <file> [--caption "..."] [--as document]
python C:/Users/Korisnik/.claude/skills/send-to-my-whatsapp/bin/wa_send.py --text "message body"
```

The script handles everything below automatically. Read on only when it errors.

## The numbers (do not mix these up — this cost a failed send once)

| Role | Number | Where it lives |
|---|---|---|
| **Kiwu's personal phone (RECIPIENT)** | `+381693311331` | `SOCIAL_APPROVAL_PHONE`, `FOUNDER_WA_E164` |
| Kiwuuu AI business sender | `+381628258341` | `WHATSAPP_DEMO_NUMBER`, phone id `1094433003749898` |

**`WHATSAPP_DEMO_NUMBER` is the SENDER, not Kiwu.** Sending there returns a bogus
`(#100) Invalid parameter` because a number cannot message itself.

Credentials live in `C:\Users\Korisnik\kiwuuu-backup\memory\SECRETS_LOCAL.md`
(`WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`). Local-only, never synced — never
copy them into the vault, a skills repo, or Claude memory.

## Real media caps (the documented ones are wrong in practice)

| Type | Hard cap on `/media` upload |
|---|---|
| **Video** | **16 MB** — the "100 MB document" figure does NOT apply; the upload endpoint rejects it |
| Image | 5 MB |
| Audio | 16 MB |
| Document | 100 MB (genuinely) |

Over the cap returns `(#100) Invalid parameter` with
`details: "File Too Large"`. For video the script two-pass re-encodes to ~15 MB:

```
-c:v libx264 -b:v <computed> -tune animation -vf scale=720:1280,fps=24 -preset slower
-c:a aac -b:a 64k -ac 1 -movflags +faststart
```

`-tune animation` matters for the stickman/doodle content — line art on white holds up
at ~350 kbps where live action would fall apart. A 4:52 video went 121.6 MB → 14.8 MB
with no visible loss.

## The 24-hour window — the silent failure

**A `wamid` in the response does NOT mean delivered.** It means accepted. If Kiwu's phone
has not messaged the business number in the last 24 h, Meta accepts the message and then
drops it asynchronously; the failure only appears in a webhook this PC cannot see.
Symptom: API says success, nothing arrives.

**Fix:** Kiwu texts anything to **+381 62 8258341** from his phone, then resend
immediately. That reopens the free service window for 24 h.

**CONFIRMED 2026-08-03.** Three sends (video + two text probes) all returned a `wamid`
and all silently vanished. Every config check passed — token valid, `account_mode: LIVE`,
GREEN quality, media stored, recipient resolved. Kiwu sent "hey" to the business number;
the very next send arrived first try. When everything looks healthy and nothing lands,
**it is the window — do not go hunting elsewhere.** Ask him to text the business number
before spending time on diagnostics.

## Templates — the always-open channel

An approved **template** is the only way to reach Kiwu outside the window. Manage them with:

```bash
python .../send-to-my-whatsapp/bin/wa_templates.py --list      # status of each
python .../send-to-my-whatsapp/bin/wa_templates.py --create    # create the set
```

Three templates cover everything:

| Template | Header | Use |
|---|---|---|
| `kiwuuu_delivery_ping` | text only | Cheapest. Tells him a file is waiting; his reply reopens the free window, then send anything. |
| `kiwuuu_delivery_document` | DOCUMENT | Any file type, delivered in one shot |
| `kiwuuu_delivery_video` | VIDEO | Inline playable video in one shot |

**Preferred flow: send `kiwuuu_delivery_ping`, he replies, then push the media free.**
One cheap utility message instead of a paid template per file, and no media-header limits.

**All three created 2026-08-03** (ids: ping `1818443899144057`, document `27656943097288883`,
video `1542714247492377`). `wa_send.py` uses them automatically — a normal send that hits
`131047` retries as the matching template with the media already uploaded. `--template`
forces that path; `--no-template` disables it.

### WABA id — the thing that unblocked this

`WHATSAPP_WABA_ID=1470206464768255` in SECRETS_LOCAL.md. **Required** — do not delete it.

**`WHATSAPP_BUSINESS_ACCOUNT_ID=2258537087886158` is the Business Portfolio id, NOT the
WABA.** It answers to `?fields=id,name` ("Kiwuuu AI") so it looks correct, but rejects
`message_templates` and `phone_numbers`. That mislabel burned a debugging round.

Auto-discovery does not work and never will with this token: reading
`assigned_whatsapp_business_accounts` needs `business_management` scope, which the token
lacks (403 Missing Permissions). Also note the system user has two ids — `61569227937728`
in Business Manager, `122095945526640931` from `/me` (app-scoped alias). The explicit
`WHATSAPP_WABA_ID` sidesteps all of it.

### Gotchas hit while creating these

- **Body text may not start or end with a variable** — `"... : {{1}}"` is rejected with
  subcode 2388299 "Leading or Trailing Params Not Allowed". Always put words after the
  last `{{n}}`.
- **Media-header templates need a sample file handle** via the resumable upload API
  (`POST /{app-id}/uploads` → `POST /{session-id}` with raw bytes → `h`). `wa_templates.py`
  does this automatically using `bin/sample.mp4` and `bin/sample.pdf` — keep those files.
- Approval is usually minutes, occasionally 24 h. Check with `--list`.
- UTILITY is the correct category and is cheap (fractions of a cent in Serbia). Never
  label delivery templates MARKETING — they get throttled by opt-outs.

## Token

Current token is a **System User token, non-expiring** (`type: SYSTEM_USER`, `expires_at: 0`,
app `1689690292022154`) with `whatsapp_business_messaging` + `whatsapp_business_management`.
If it ever 401s with code 190, mint a new one:
Business Settings → Users → System Users → Generate New Token → expiration **Never**.
A token from the WhatsApp → API Setup page instead expires in 24 h — avoid it.

Verify a token without sending anything:
```bash
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://graph.facebook.com/v21.0/1094433003749898?fields=display_phone_number,quality_rating,account_mode"
```
Healthy looks like: `Kiwuuu AI`, `GREEN`, `account_mode: LIVE`, tier `TIER_250`.

## Errors worth knowing

| Symptom | Cause | Fix |
|---|---|---|
| Accepted, never arrives | 24 h window closed | Kiwu texts the business number, resend |
| `401` code 190 | Token dead/expired | New System User token |
| `(#100) Invalid parameter`, no detail | Sending to the sender's own number | Recipient must be `+381693311331` |
| `(#100)` + `File Too Large` | Over the type cap | Let the script compress, or send `--as document` |
| `131030` | Recipient not on WhatsApp | Wrong number |
| `131047` | Re-engagement required | Same as window fix; needs a template outside it |

## Notes
- Sending inside the window is **free** (service conversation), no template needed.
- Uploaded media ids stay valid ~30 days — reuse the id to resend rather than re-uploading.
- ffmpeg comes from `imageio-ffmpeg` (`pip install imageio-ffmpeg`); there is no system
  ffmpeg on T3 readable by this account.
- Companion: `whatsapp-cloud-api` skill for building bot/webhook features — this skill is
  only the "put a file on Kiwu's phone" path.
