# Quick Health Check Workflow

Fast endpoints + PM2 check only. Use for quick session-start verification.

## Execution

Run these checks only:

1. **Endpoints** (6 URLs)
2. **PM2 status** (root + kiwubot user)
3. **Disk + RAM** (quick resource check)

Skip: content assets, public URLs, security, pipeline health.

## Commands

```bash
# Quick endpoint check
for url in "https://kiwuuu.com" "https://app.kiwuuu.com" "http://localhost:4000/health" "http://localhost:3003/health"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "User-Agent: Mozilla/5.0" "$url" 2>/dev/null)
  echo "$code $url"
done

# PM2
sudo /usr/local/bin/pm2 list
sudo -u kiwubot pm2 list

# Resources
df -h / | tail -1
free -h | head -3
```

## Output Format

```
Quick Health: [X/X] endpoints up | PM2: [X/X] online | Disk: X% | RAM: X%
```

## Done

Quick check complete. If any failures, recommend running the Full workflow.
