---
name: kiwuuu-design-kit
description: Premium UI building blocks for React/Next.js + shadcn projects. USE WHEN building or restyling a landing page, marketing section, dashboard, or app screen (hero, pricing, CTA, footer, features, testimonials) and you want production-grade components instead of generic AI markup. Pulls real source from the Efferd shadcn registry and applies the Kiwuuu DESIGN.md system. Web/app UI only — NOT video/motion.
---

# Kiwuuu Design Kit

Two assets that turn "AI design slop" into shippable UI:
1. **Efferd shadcn registry** — 166 production blocks across 17 categories, pulled straight into a repo via the shadcn CLI (verified working 2026-06-24).
2. **`assets/kiwuuu-DESIGN.md`** — the Kiwuuu design system (tokens + intent) to enforce brand consistency when generating or restyling.

Scope: web React/Next.js + Tailwind + shadcn/ui projects (kiwusaas, TraficShop, Limonella web). For static `kiwuuu.com` HTML landings, use these as reference/spec, not CLI installs. **Efferd blocks are web DOM + shadcn — they CANNOT drop into Expo / React Native apps (kiwuuu-finance, GymOS); for those, use the DESIGN.md half only, or build a separate web landing.** This kit does NOT touch the faceless-YouTube/HyperFrames video pipeline.

## A. Pull blocks from the Efferd registry

One-time per project — register the namespace in `components.json`:
```json
"registries": { "@efferd": "https://efferd.com/r/{name}.json" }
```
(Project must already be shadcn-init'd: `npx shadcn@latest init -d -f -y` — the `-d` defaults preset is required; `--base-color` no longer exists.)

Then add any block; deps (core shadcn + sibling Efferd blocks) auto-resolve:
```bash
npx shadcn@latest add @efferd/cta-1 @efferd/pricing-1 @efferd/hero-1 -y
```

**Freemium gotcha:** many blocks are free (HTTP 200), some are paid (HTTP 401 →
`[Unauthorized] ... need your EFFERD_REGISTRY_TOKEN`). `shadcn add` fails atomically
on a paid item. Check first, then only add free ones (or set `EFFERD_REGISTRY_TOKEN`
if a paid plan is ever purchased):
```bash
curl -s -o /dev/null -w '%{http_code}\n' https://efferd.com/r/<block>.json   # 200=free 401=paid
```
List the whole catalog: `curl -s https://efferd.com/r/registry.json` → `.items[]`.
Categories: app-shell, auth, blogs, contact, cta, dashboard, faqs, features, footer,
header, hero, image-gallery, integrations, logo-cloud, not-found, pricing, testimonials.
License: blocks are MIT (source copied into your repo, no node_modules lock-in).

## B. Enforce the Kiwuuu look

After (or instead of) pulling a block, restyle to brand by instructing the agent:
> "Restyle this section strictly against `assets/kiwuuu-DESIGN.md` — dark canvas,
> electric-lime primary on the single CTA only, hairline borders, no decorative gradients."

The DESIGN.md is machine-readable (YAML tokens) + human intent. Map its tokens onto
the project's Tailwind theme / CSS variables before generating.

## C. Harvest more design systems (optional)

- **designmd.app** — 454 free DESIGN.md files (Claude Code / Cursor / Kiro compatible). JS-gated, so grab via the browser (Claude-in-Chrome): open a design → copy its DESIGN.md → save into `assets/`.
- **neuform.ai** — AI HTML landing builder; "save skill" or "download DESIGN.md".
- **superdesign.dev** — open-source design *agent* with a real Claude Code skill (`npm i -g @superdesign/cli` → `superdesign login` → `npx skills add superdesigndev/superdesign-skill` → `/superdesign ...`) + community MCP. Overlaps existing claude-design-autopilot / frontend-design / ui-ux-pro-max; adopt only for its canvas-variations loop.

## Companion skills
`ui-ux-pro-max` (shadcn/ui MCP), `frontend-design`, `shadcn-ui`, `claude-design-autopilot`.
