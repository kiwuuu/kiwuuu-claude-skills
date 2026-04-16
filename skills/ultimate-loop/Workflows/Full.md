# Full Ultimate Loop Workflow

Complete system, content, and infrastructure verification.

## Prerequisites

This workflow uses `sudo` to check PM2 process managers. Ensure the following NOPASSWD sudo rules exist:
```
your-user ALL=(ALL) NOPASSWD: /usr/local/bin/pm2
your-user ALL=(your-app-user) NOPASSWD: /usr/local/bin/pm2
```

> ⚠️ **Security note:** Never execute scripts from `/tmp` — it is world-writable and
> vulnerable to race conditions. This template uses `~/.claude/skills/ultimate-loop/runner.py`.

## Execution

### Step 1: Run the verification script

```bash
python3 ~/.claude/skills/ultimate-loop/runner.py
```

If the script doesn't exist, create it from the template below.

### Step 2: Template (create at ~/.claude/skills/ultimate-loop/runner.py)

Adapt the `# CONFIGURATION` section at the top before running.

```python
#!/usr/bin/env python3
"""Ultimate Loop — comprehensive system verification. Adapt config section below."""
import urllib.request, json, os, subprocess
from datetime import datetime

# ── CONFIGURATION — adapt these to your stack ─────────────────────────────────
PROJECT_NAME             = "My Project"
EXPECTED_ROOT_PROCESSES  = 3         # How many PM2 processes you expect
EXPECTED_APP_PROCESSES   = 0         # Secondary PM2 user process count (0 = skip)
APP_PM2_USER             = "appuser" # Secondary PM2 user name
SSH_KEY_PATH             = os.path.expanduser("~/.ssh/authorized_keys")
DISK_WARN_PCT            = 85
RAM_WARN_PCT             = 90
SWAP_WARN_PCT            = 90
MEDIA_ROOT               = ""        # Set to your static media dir, or "" to skip

# Endpoints: (url, expected_http_code, label)
ENDPOINTS = [
    ("https://your-domain.com",      200, "Main site"),
    ("https://app.your-domain.com",  200, "App"),
    ("http://localhost:4000/health", 200, "App service"),
]

KEY_FILES  = []  # (path, label) tuples for important files to check
PUBLIC_URLS = [] # (label, /path) tuples for public URL HEAD checks
# ── END CONFIGURATION ──────────────────────────────────────────────────────────

PASS_COUNT = FAIL_COUNT = 0
results = []
UA = {"User-Agent": "Mozilla/5.0 (UltimateLoop/v2)"}

def test(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    icon = "PASS" if passed else "FAIL"
    if passed: PASS_COUNT += 1
    else: FAIL_COUNT += 1
    results.append((icon, name, detail))
    print(f"  [{icon}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 60)
print(f"ULTIMATE LOOP — {PROJECT_NAME} Verification")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# === ENDPOINTS ===
if ENDPOINTS:
    print("\n--- ENDPOINTS ---")
    for url, expected, label in ENDPOINTS:
        try:
            req = urllib.request.Request(url, headers=UA)
            resp = urllib.request.urlopen(req, timeout=10)
            test(label, resp.getcode() == expected, str(resp.getcode()))
        except urllib.error.HTTPError as e:
            test(label, e.code == expected, str(e.code))
        except Exception as e:
            test(label, False, str(e)[:60])

# === PM2 ===
print("\n--- PM2 SERVICES ---")
pm2_checks = [("Root PM2", ["sudo", "/usr/local/bin/pm2", "jlist"], EXPECTED_ROOT_PROCESSES)]
if EXPECTED_APP_PROCESSES > 0:
    pm2_checks.append((f"{APP_PM2_USER} PM2",
                       ["sudo", "-u", APP_PM2_USER, "pm2", "jlist"],
                       EXPECTED_APP_PROCESSES))
for cmd_label, cmd, expected in pm2_checks:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        procs = json.loads(r.stdout)
        online = [p for p in procs if p.get("pm2_env", {}).get("status") == "online"]
        names = ", ".join(p["name"] for p in online)
        test(f"{cmd_label} ({len(online)}/{expected} online)",
             len(online) >= expected, names[:80])
    except Exception as e:
        test(cmd_label, False, str(e)[:60])

# === SECURITY ===
print("\n--- SECURITY ---")
# Read-only existence check — never modifies authorized_keys
try:
    exists = os.path.exists(SSH_KEY_PATH)
    size   = os.path.getsize(SSH_KEY_PATH) if exists else 0
    test("SSH keys exist", exists and size > 0, f"{size} bytes")
except Exception as e:
    test("SSH keys exist", False, str(e)[:60])

# === RESOURCES ===
print("\n--- RESOURCES ---")
try:
    r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    line = r.stdout.strip().split("\n")[-1].split()
    pct = int(line[4].replace("%", ""))
    test(f"Disk ({pct}%)", pct < DISK_WARN_PCT, f"{line[2]} / {line[1]}")
except Exception:
    test("Disk", False)
try:
    r = subprocess.run(["free", "-m"], capture_output=True, text=True)
    lines = r.stdout.strip().split("\n")
    mem = lines[1].split()
    ram_pct = (int(mem[2]) * 100) // int(mem[1])
    test(f"RAM ({ram_pct}%)", ram_pct < RAM_WARN_PCT, f"{mem[2]}MB / {mem[1]}MB")
    if len(lines) > 2:
        swap = lines[2].split()
        swap_pct = (int(swap[2]) * 100) // int(swap[1]) if int(swap[1]) > 0 else 0
        test(f"Swap ({swap_pct}%)", swap_pct < SWAP_WARN_PCT, f"{swap[2]}MB / {swap[1]}MB")
except Exception:
    test("Memory", False)

# === CONTENT ASSETS ===
if MEDIA_ROOT and os.path.isdir(MEDIA_ROOT):
    print("\n--- CONTENT ASSETS ---")
    for subdir, exts, label in [
        ("videos",    (".mp4", ".mov"),          "Videos"),
        ("images",    (".jpg", ".jpeg", ".png"), "Images"),
        ("documents", (".pdf",),                 "Documents"),
    ]:
        path = os.path.join(MEDIA_ROOT, subdir)
        if os.path.isdir(path):
            files = [f for f in os.listdir(path) if f.endswith(exts)]
            valid = [f for f in files if os.path.getsize(os.path.join(path, f)) > 1000]
            test(f"{label} ({len(valid)})", len(valid) > 0, f"{len(valid)} files")

if KEY_FILES:
    for name, path in KEY_FILES:
        exists = os.path.exists(path)
        test(name, exists, f"{os.path.getsize(path)//1024}KB" if exists else "missing")

# === PUBLIC URLS ===
if PUBLIC_URLS and ENDPOINTS:
    print("\n--- PUBLIC URLS ---")
    base = ENDPOINTS[0][0].rstrip("/")
    for label, path in PUBLIC_URLS:
        try:
            req = urllib.request.Request(f"{base}{path}", method="HEAD", headers=UA)
            resp = urllib.request.urlopen(req, timeout=10)
            test(f"URL: {label}", resp.getcode() == 200)
        except Exception as e:
            test(f"URL: {label}", False, str(e)[:50])

# === SUMMARY ===
print(f"\n{'='*60}")
print(f"ULTIMATE LOOP: {PASS_COUNT}/{PASS_COUNT+FAIL_COUNT} PASS")
if FAIL_COUNT > 0:
    print(f"\nFAILED ({FAIL_COUNT}):")
    for i, n, d in results:
        if i == "FAIL":
            print(f"  ✗ {n}: {d}")
print(f"{'='*60}")
```

### Step 3: Report results

- **All PASS** → "System healthy. X/X PASS."
- **Any FAIL** → List failures with recommended fixes.
- **Multiple runs** → Run N times, report consistency.

## Done

Loop complete. Report the score and any failures that need attention.
