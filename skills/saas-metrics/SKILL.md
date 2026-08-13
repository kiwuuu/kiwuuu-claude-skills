---
name: saas-metrics
description: SaaS metrics framework for founders. USE WHEN calculating MRR, ARR, churn rate, LTV, CAC, NPS, activation rate, or building investor-ready dashboards. Covers cohort analysis, revenue forecasting, unit economics, and growth accounting. Includes Kiwuuu-specific metric targets and SQL queries.
---

# SaaS Metrics Skill

The definitive metric framework for early-stage SaaS. Know what to measure, what's a vanity metric, and what actually drives decisions.

---

## The 6 Metrics That Matter (Pre-$1M ARR)

### 1. MRR (Monthly Recurring Revenue)
```
MRR = Σ (active subscriptions × monthly price)

MRR Breakdown:
  New MRR       = new subscriptions this month
  Expansion MRR = upgrades (trial→pro, pro→business)
  Contraction MRR = downgrades
  Churn MRR     = cancellations
  
Net New MRR = New + Expansion - Contraction - Churn

Kiwuuu targets:
  Month 1: $0-500 (friends/network)
  Month 3: $1,000-3,000 (content + referral kicking in)
  Month 6: $5,000-10,000 (product-market fit signal)
  Month 12: $25,000+ (scale phase begins)
```

### 2. Churn Rate
```
Monthly Churn Rate = Churned customers / Customers at start of month

Benchmark by stage:
  Early SaaS (<$1M ARR): <8%/mo acceptable, target <5%
  Growth ($1-10M ARR): <3%/mo
  Scale ($10M+): <2%/mo

Revenue Churn vs Customer Churn:
  Customer churn: % of customers lost
  Revenue churn: % of MRR lost (more important)
  
Net Revenue Retention (NRR):
  NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
  NRR > 100% = expansion revenue exceeds churn (best case)
  NRR > 110% = world class
```

### 3. LTV (Lifetime Value)
```
LTV = ARPU / Monthly Churn Rate

ARPU (Avg Revenue Per Account) — Agency Tier pricing ($499/mo base + $19/workspace):
  Kiwuuu ARPU = (accounts × $499 + total workspaces × $19) / accounts

Example:
  3 agencies averaging 4 workspaces each = (3×$499 + 12×$19) / 3 = $575 ARPU
  Monthly churn = 5%
  LTV = $575 / 0.05 = $11,500

LTV:CAC ratio:
  >3:1 = healthy
  >5:1 = great
  <2:1 = problem
```

### 4. CAC (Customer Acquisition Cost)
```
CAC = Total S&M spend / New customers acquired

Early stage (no paid ads):
  CAC = founder time cost (hours × hourly rate) + tool costs
  
Payback period = CAC / (ARPU × Gross Margin)
Target: <12 months payback for SMB SaaS
```

### 5. Activation Rate
```
Activation Rate = Users who hit "first value moment" / Total signups

Kiwuuu definition of activated:
  - Connected WhatsApp (or ran first agent in sandbox)
  - Received first agent response
  - Used agent ≥3 times in first 7 days

Target: >40% D7 activation (top quartile SaaS)
Current benchmark: unknown — instrument this first
```

### 6. NPS (Net Promoter Score)
```
NPS = % Promoters (9-10) - % Detractors (0-6)

When to ask:
  - After 3rd agent run (value delivered)
  - At Day 30 (habit formed or not)
  - After upgrade (peak satisfaction)

NPS Benchmarks (SaaS):
  >50 = excellent
  30-50 = good
  0-30 = work needed
  <0 = urgent problem
```

---

## Growth Accounting Framework

### Monthly Cohort Tracking
```sql
-- Users acquired each month and their retention
SELECT 
  DATE_TRUNC('month', created_at) as cohort_month,
  COUNT(*) as acquired,
  COUNT(CASE WHEN plan IN ('pro','business') THEN 1 END) as converted,
  ROUND(COUNT(CASE WHEN plan IN ('pro','business') THEN 1 END)::numeric / COUNT(*) * 100, 1) as conversion_pct
FROM profiles
GROUP BY 1
ORDER BY 1;
```

### Revenue Waterfall (Monthly)
```
Starting MRR:          $X,XXX
+ New MRR:             +$XXX   (new paying customers)
+ Expansion MRR:       +$XXX   (pro→business upgrades)
- Contraction MRR:     -$XXX   (business→pro downgrades)
- Churned MRR:         -$XXX   (cancellations)
= Ending MRR:          $X,XXX
```

---

## Kiwuuu-Specific Dashboard Queries

### Admin stats needed (add to /api/admin/stats)
```python
# Current /api/admin/stats returns:
# total_users, paying, mrr, trials, churned, near_limit

# Add these:
# trial_conversion_rate = paying / (paying + churned + trial_converted)
# avg_trial_msgs_used = avg of trial_msgs_used for trial users
# activation_rate = users with >=3 runs / total signups (need run tracking)
# mrr_growth = (current_mrr - last_month_mrr) / last_month_mrr
```

### Churn Early Warning (run weekly)
```python
# Users at churn risk: paying + no activity in 14 days
# Proxy: plan = 'pro'/'business' AND trial_msgs_used not increasing
# (can't track this without a last_active field — add it)
```

---

## Metric Red Flags → Actions

| Red Flag | Threshold | Action |
|----------|-----------|--------|
| Trial→Paid conversion | <2% | Fix activation / pricing |
| Day 7 retention | <20% | Fix onboarding |
| MoM churn | >10% | Emergency: talk to churned users |
| LTV:CAC | <2:1 | Pause paid acquisition |
| NPS | <20 | Product quality issue |
| Activation rate | <20% | Rework first-run experience |

---

## Investor-Ready Metrics (When You Need Them)

At Series A, investors want:
1. MRR + MoM growth rate (need >15% MoM for 12+ months)
2. NRR >110%
3. LTV:CAC >3:1 with <12 month payback
4. Gross margin >70% (SaaS standard)
5. Rule of 40: Revenue growth % + Profit margin % > 40

For Kiwuuu at current stage: focus on MRR and activation rate only.
Don't track 20 metrics. Track 3 obsessively.

---

## Quick Reference: Benchmark Table

| Metric | Bad | OK | Good | Great |
|--------|-----|-----|------|-------|
| Monthly Churn | >10% | 5-10% | 3-5% | <2% |
| NRR | <90% | 90-100% | 100-110% | >110% |
| LTV:CAC | <2x | 2-3x | 3-5x | >5x |
| Payback period | >24mo | 12-24mo | 6-12mo | <6mo |
| D30 Retention | <20% | 20-35% | 35-50% | >50% |
| NPS | <20 | 20-40 | 40-60 | >60 |
| Trial conversion | <1% | 1-3% | 3-7% | >7% |
