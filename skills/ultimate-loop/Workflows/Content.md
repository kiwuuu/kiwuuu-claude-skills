# Content Workflow — Asset Inventory

Verify all content assets exist, are correctly sized, and are publicly accessible.

Trigger: `/ultimate-loop content` or after any content generation session.

## Execution

### Step 1: Count assets by type

```python
import os

MEDIA_ROOT = "/var/www/kiwuuu/media"  # Adapt to your media directory

asset_dirs = {
    "Videos (TikTok/Reels)": (f"{MEDIA_ROOT}/tiktok", (".mp4", ".mov")),
    "Cinematic videos":       (f"{MEDIA_ROOT}/ltx_test", (".mp4",)),
    "Images (FLUX/IG)":       (f"{MEDIA_ROOT}/content", (".jpg", ".jpeg", ".png")),
    "Carousels":              (f"{MEDIA_ROOT}/carousels", (".png", ".jpg", ".pdf")),
    "Podcasts":               (f"{MEDIA_ROOT}/podcasts", (".mp3", ".wav", ".ogg")),
}

for label, (path, exts) in asset_dirs.items():
    if not os.path.isdir(path):
        print(f"  MISSING DIR  {label}: {path}")
        continue
    files = [f for f in os.listdir(path) if f.endswith(exts)]
    valid = [f for f in files if os.path.getsize(os.path.join(path, f)) > 10_000]
    print(f"  {'OK' if valid else 'EMPTY  '} {label}: {len(valid)} files")
```

### Step 2: Verify key content files exist

```python
KEY_FILES = [
    ("/var/www/kiwuuu/media/POST_COPY.md",          "Post copy (ready to paste)"),
    ("/root/kiwubot/social/VISUAL_SYSTEM.md",        "Visual brand system"),
    ("/var/www/kiwuuu/media/gallery.html",           "Gallery page"),
    ("/root/kiwubot/social/SKILLS_PLAYBOOK.md",      "Skills playbook"),
]
# Adapt paths to your project

for path, label in KEY_FILES:
    exists = os.path.exists(path)
    size   = os.path.getsize(path) if exists else 0
    status = f"{size // 1024}KB" if exists else "MISSING"
    print(f"  {'OK' if exists else 'MISSING'} {label}: {status}")
```

### Step 3: Verify public URL accessibility

```python
import urllib.request

DOMAIN = "https://kiwuuu.com"  # Adapt to your domain
PUBLIC_PATHS = [
    "/media/gallery.html",
    # Add your key public asset paths here
]

UA = {"User-Agent": "Mozilla/5.0 (UltimateLoop/Content)"}
for path in PUBLIC_PATHS:
    try:
        req = urllib.request.Request(f"{DOMAIN}{path}", method="HEAD", headers=UA)
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"  OK  {path} — {resp.getcode()}")
    except Exception as e:
        print(f"  FAIL {path} — {str(e)[:60]}")
```

### Step 4: Check content queue depth

```python
import sqlite3

# Adapt DB path to your project
DB_PATH = "/root/kiwubot/social/social.db"

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    pending = conn.execute(
        "SELECT COUNT(*) FROM content_queue WHERE status='pending_review'"
    ).fetchone()[0]
    posted_today = conn.execute(
        "SELECT COUNT(*) FROM posts WHERE date(created_at) = date('now')"
    ).fetchone()[0]
    conn.close()
    print(f"  Queue: {pending} pending review")
    print(f"  Posted today: {posted_today}")
else:
    print("  No content DB found (adapt DB_PATH)")
```

### Step 5: Check recent cron activity

```bash
# Check last 10 lines of content cron log
tail -10 /root/kiwubot/social/cron.log 2>/dev/null || echo "No cron log found"
```

## Output Format

```
Content Asset Inventory — [DATE]

Videos (TikTok/Reels):  12 files  ✓
Cinematic videos:        3 files  ✓
Images (FLUX/IG):        6 files  ✓
Carousels:               4 files  ✓
Podcasts:                1 file   ✓

Key files:
  ✓ Post copy: 14KB
  ✓ Visual system: 4KB
  ✓ Gallery page: 8KB

Public URLs: 1/1 accessible

Queue: 3 pending review | Posted today: 4
```

## Adapting to Your Stack

- Replace `MEDIA_ROOT` with your media directory path
- Replace `DOMAIN` with your public domain
- Replace `DB_PATH` with your content queue database path
- Replace `KEY_FILES` with your project's key content files
- Add/remove `PUBLIC_PATHS` entries to match your media structure

## Integration

After this workflow, if public URLs are failing:
1. Check nginx config: `nginx -t`
2. Check file permissions: `ls -la /var/www/your-media/`
3. Run the Full workflow for deeper system diagnosis

## Done

Asset inventory complete. Report counts and any missing/inaccessible files.
