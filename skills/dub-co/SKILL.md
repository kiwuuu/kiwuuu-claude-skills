---
name: dub-co
description: Link management and attribution for Kiwuuu. USE WHEN creating short links, tracking UTM campaigns, managing branded links, pulling click analytics, or building attribution reports. Requires DUB_API_KEY in environment.
---

# Dub.co Link Management

Expert at using the Dub.co API for link management, UTM attribution, and campaign analytics.

## Setup

```bash
# Sign up: app.dub.co (Pro plan $7/mo for custom domains + advanced analytics)
# Get API key: app.dub.co/account/tokens
# Add to .env: DUB_API_KEY=your_key_here
```

## Core Operations

### Create Short Link with UTM
```python
import urllib.request, json, os

def create_dub_link(url, utm_source, utm_medium, utm_campaign, tag=None):
    payload = {
        "url": url,
        "utm_source": utm_source,
        "utm_medium": utm_medium,
        "utm_campaign": utm_campaign,
    }
    if tag:
        payload["tagNames"] = [tag]

    req = urllib.request.Request(
        "https://api.dub.co/links",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['DUB_API_KEY']}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

### Get Analytics for a Link
```python
def get_link_analytics(link_id, interval="30d"):
    req = urllib.request.Request(
        f"https://api.dub.co/analytics?linkId={link_id}&interval={interval}&groupBy=timeseries",
        headers={"Authorization": f"Bearer {os.environ['DUB_API_KEY']}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

### List All Links
```python
def list_links(tag=None, page=1):
    url = f"https://api.dub.co/links?page={page}&pageSize=50"
    if tag:
        url += f"&tagNames={tag}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {os.environ['DUB_API_KEY']}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

## UTM Strategy for Kiwuuu

| Campaign | utm_source | utm_medium | utm_campaign |
|----------|-----------|------------|--------------|
| WhatsApp agent post | instagram/tiktok/x | social | whatsapp-agents |
| Beehiiv newsletter | beehiiv | email | weekly-digest |
| Cold outreach | gmail/linkedin | outreach | enterprise-demo |
| Partner referral | partner-name | referral | affiliate |

## Kiwuuu Link Conventions

- All social posts: tag `social-content`
- All outbound marketing: tag `marketing`
- Acquisition funnel: tag `acquisition`
- Custom domain: use `kwuu.link` or similar (set up in Dub.co dashboard)

## Acquisition Due Diligence Value

When tracking links from day 1:
- Click-to-signup conversion rate per channel
- CAC by source (direct data, not GA estimates)
- Content ROI: which posts drive signups
- Partner/affiliate performance

This data makes every metric in the acquisition pitch **verified**, not estimated.

## MCP Server (Optional)

For direct tool integration:
```bash
# After getting API key, configure in ~/.claude/settings.json:
{
  "mcpServers": {
    "dub": {
      "command": "npx",
      "args": ["-y", "dubco-mcp-server"],
      "env": {
        "DUBCO_API_KEY": "your_key_here"
      }
    }
  }
}
```
Provides tools: create_link, update_link, delete_link, get_analytics
