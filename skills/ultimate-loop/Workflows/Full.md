# Full Ultimate Loop Workflow

Complete system, content, and infrastructure verification.

## Execution

### Step 1: Run the verification script

Execute the Python verification script. If it doesn't exist or is outdated, generate it dynamically.

```bash
python3 /tmp/ultimate_loop.py
```

If the script doesn't exist, create it from the template below and run it.

### Step 2: Template (create at /tmp/ultimate_loop.py if missing)

```python
#!/usr/bin/env python3
"""Ultimate Loop — Kiwuuu comprehensive system verification."""
import urllib.request, json, os, subprocess, sys

PASS = FAIL = 0
results = []
UA = {"User-Agent": "Mozilla/5.0 (UltimateLoop/v2)"}

def test(name, passed, detail=""):
    global PASS, FAIL
    icon = "PASS" if passed else "FAIL"
    if passed: PASS += 1
    else: FAIL += 1
    results.append((icon, name, detail))
    print(f"  [{icon}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 60)
print("ULTIMATE LOOP — Kiwuuu System Verification")
print("=" * 60)

# === ENDPOINTS ===
print("\n--- ENDPOINTS ---")
endpoints = [
    ("https://kiwuuu.com", 200, "Main site"),
    ("https://app.kiwuuu.com", 200, "SaaS app"),
    ("https://cli.kiwuuu.com", 401, "CLI (auth)"),
    ("http://localhost:4000/health", 200, "saas-app"),
    ("http://localhost:3003/health", 200, "mesh-coordinator"),
    ("http://localhost:8096/", 200, "kiwuuu-server"),
]
for url, expected, label in endpoints:
    try:
        req = urllib.request.Request(url, headers=UA)
        resp = urllib.request.urlopen(req, timeout=10)
        test(label, resp.getcode() == expected, str(resp.getcode()))
    except urllib.error.HTTPError as e:
        test(label, e.code == expected, str(e.code))
    except Exception as e:
        test(label, False, str(e)[:60])

# === PM2 ===
# Adapt these constants to your expected process counts
EXPECTED_ROOT_PROCESSES = 7
EXPECTED_APP_PROCESSES = 3
APP_PM2_USER = "kiwubot"  # The user running the app's PM2 instance

print("\n--- PM2 SERVICES ---")
for cmd_label, cmd, expected in [
    ("Root PM2", ["sudo", "/usr/local/bin/pm2", "jlist"], EXPECTED_ROOT_PROCESSES),
    (f"{APP_PM2_USER} PM2", ["sudo", "-u", APP_PM2_USER, "pm2", "jlist"], EXPECTED_APP_PROCESSES)
]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        procs = json.loads(r.stdout)
        online = [p for p in procs if p.get("pm2_env", {}).get("status") == "online"]
        names = ", ".join(p["name"] for p in online)
        test(f"{cmd_label} ({len(online)}/{expected} online)", len(online) >= expected, names[:80])
    except Exception as e:
        test(cmd_label, False, str(e)[:60])

# === SECURITY ===
print("\n--- SECURITY ---")
# Check SSH authorized_keys exists and is non-empty (safe read-only check)
ssh_key_path = "/root/.ssh/authorized_keys"
try:
    exists = os.path.exists(ssh_key_path)
    size = os.path.getsize(ssh_key_path) if exists else 0
    test("SSH keys exist", exists and size > 0, f"{size} bytes")
except Exception as e:
    test("SSH keys exist", False, str(e)[:60])

# === RESOURCES ===
print("\n--- RESOURCES ---")
try:
    r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    line = r.stdout.strip().split("\n")[-1].split()
    pct = int(line[4].replace("%", ""))
    test(f"Disk ({pct}%)", pct < 85, f"{line[2]} / {line[1]}")
except:
    test("Disk", False)

try:
    r = subprocess.run(["free", "-m"], capture_output=True, text=True)
    lines = r.stdout.strip().split("\n")
    mem = lines[1].split()
    ram_pct = (int(mem[2]) * 100) // int(mem[1])
    test(f"RAM ({ram_pct}%)", ram_pct < 90, f"{mem[2]}MB / {mem[1]}MB")
    if len(lines) > 2:
        swap = lines[2].split()
        swap_pct = (int(swap[2]) * 100) // int(swap[1]) if int(swap[1]) > 0 else 0
        test(f"Swap ({swap_pct}%)", swap_pct < 90, f"{swap[2]}MB / {swap[1]}MB")
except:
    test("Memory", False)

# === CONTENT ASSETS ===
print("\n--- CONTENT ASSETS ---")
asset_checks = {
    "TikTok videos": [f"/var/www/kiwuuu/media/tiktok/{f}" for f in
        os.listdir("/var/www/kiwuuu/media/tiktok/") if f.endswith(".mp4")]
        if os.path.isdir("/var/www/kiwuuu/media/tiktok/") else [],
    "FLUX images": [f"/var/www/kiwuuu/media/content/{f}" for f in
        os.listdir("/var/www/kiwuuu/media/content/") if f.endswith((".jpg", ".png"))]
        if os.path.isdir("/var/www/kiwuuu/media/content/") else [],
    "Canva designs": [f"/var/www/kiwuuu/media/carousels/{f}" for f in
        os.listdir("/var/www/kiwuuu/media/carousels/") if f.endswith(".png")]
        if os.path.isdir("/var/www/kiwuuu/media/carousels/") else [],
    "Podcasts": [f"/var/www/kiwuuu/media/podcasts/{f}" for f in
        os.listdir("/var/www/kiwuuu/media/podcasts/") if f.endswith((".mp3", ".wav"))]
        if os.path.isdir("/var/www/kiwuuu/media/podcasts/") else [],
}
for cat, files in asset_checks.items():
    valid = [f for f in files if os.path.getsize(f) > 1000]
    test(f"{cat} ({len(valid)})", len(valid) > 0, f"{len(valid)} files")

# Key files
for name, path in [("POST_COPY.md", "/var/www/kiwuuu/media/POST_COPY.md"),
                    ("Visual System", "/root/kiwubot/social/VISUAL_SYSTEM.md"),
                    ("Gallery page", "/var/www/kiwuuu/media/gallery.html"),
                    ("Master Prompt", "/root/claude-skills/memory/MASTER_PROMPT.md")]:
    exists = os.path.exists(path)
    test(name, exists, f"{os.path.getsize(path)//1024}KB" if exists else "missing")

# === PUBLIC URLS ===
print("\n--- PUBLIC URLS ---")
pub_urls = [
    ("Gallery", "/media/gallery.html"),
    ("TikTok video", "/media/tiktok/post_sleeping_profit.mp4"),
    ("IG image", "/media/content/ig_agency_desk.jpg"),
    ("Carousel", "/media/carousels/carousel_agency_math.png"),
]
for label, path in pub_urls:
    try:
        req = urllib.request.Request(f"https://kiwuuu.com{path}", method="HEAD", headers=UA)
        resp = urllib.request.urlopen(req, timeout=10)
        test(f"URL: {label}", resp.getcode() == 200)
    except Exception as e:
        test(f"URL: {label}", False, str(e)[:50])

# === SUMMARY ===
print(f"\n{'='*60}")
print(f"ULTIMATE LOOP: {PASS}/{PASS+FAIL} PASS")
if FAIL > 0:
    print(f"\nFAILED ({FAIL}):")
    for i, n, d in results:
        if i == "FAIL":
            print(f"  ✗ {n}: {d}")
print(f"{'='*60}")
```

### Step 3: Report results

After running, report the score:
- **All PASS** → "System healthy. X/X PASS."
- **Any FAIL** → List failures with recommended fixes.
- **Multiple runs** → If user asks for N loops, run the script N times and report consistency.

## Done

Loop complete. Report the score and any failures that need attention.
