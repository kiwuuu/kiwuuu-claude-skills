#!/bin/bash
# Daily competitor scrape + digest. Install via:
#   crontab -e
#   0 6 * * * <path-to-this-skill-on-T1>/cron.sh   (T1 = 169.58.50.23)
#
# Logs to data/cron.log

set -u
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SKILL_DIR/data/cron.log"
mkdir -p "$SKILL_DIR/data"

echo "=== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily run start ===" >> "$LOG"

# halt flag honored
if [ -f /var/run/kiwuuu/scraper_halt.flag ]; then
  echo "halt flag present — skipping" >> "$LOG"
  exit 0
fi

cd "$SKILL_DIR"
python3 bin/scrape.py >> "$LOG" 2>&1
SCRAPE_RC=$?

# Fail loud: don't run the digest (which would write a misleading "nothing changed"
# brief) when the scrape produced nothing. Record failures in their own log.
if [ "$SCRAPE_RC" -ne 0 ]; then
  echo "!!! SCRAPE FAILED rc=$SCRAPE_RC — skipping digest, no brief written !!!" >> "$LOG"
  echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') SCRAPE FAILED rc=$SCRAPE_RC" >> "$SKILL_DIR/data/FAILURES.log"
  echo "=== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily run end (FAILED) ===" >> "$LOG"
  exit "$SCRAPE_RC"
fi

python3 bin/digest.py >> "$LOG" 2>&1
DIGEST_RC=$?

echo "scrape rc=$SCRAPE_RC digest rc=$DIGEST_RC" >> "$LOG"
echo "=== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily run end ===" >> "$LOG"
