---
# Kiwuuu DESIGN.md — machine-readable design system for AI agents
# Drop into any project and tell the agent: "design strictly against assets/kiwuuu-DESIGN.md"
name: Kiwuuu
vibe: Pragmatic-futurist. Dark, high-contrast, neon-accented. Confident, no fluff.
mode: dark-first (light mode is a tint inversion, not a separate system)

color:
  bg:        "#0a0a0b"   # near-black canvas
  bg_elev:   "#121214"   # raised surfaces / cards
  bg_inset:  "#1b1b1f"   # inputs, wells
  border:    "#26262b"   # hairline dividers
  fg:        "#f5f5f4"   # primary text
  fg_muted:  "#a1a1aa"   # secondary text
  fg_faint:  "#6b6b73"   # tertiary / captions
  primary:   "#a3e635"   # electric lime — the Kiwuuu brand mark color
  primary_fg:"#0a0a0b"   # text on primary
  accent:    "#22d3ee"   # cyan secondary accent (use sparingly)
  success:   "#34d399"
  warning:   "#fbbf24"
  danger:    "#f87171"
  ring:      "#a3e635"   # focus ring = primary

typography:
  font_sans: "Geist, Inter, ui-sans-serif, system-ui"
  font_mono: "Geist Mono, ui-monospace, SFMono-Regular"
  scale: "1.250 (major third)"
  display: "clamp(2.5rem, 6vw, 4.5rem) / 700 / -0.03em"
  h1: "2.5rem / 700 / -0.02em"
  h2: "2rem / 600 / -0.02em"
  h3: "1.5rem / 600 / -0.01em"
  body: "1rem / 400 / 0 / line-height 1.6"
  small: "0.875rem / 400"
  caption: "0.75rem / 500 / 0.02em / uppercase"

radius:
  sm: "0.375rem"
  md: "0.625rem"   # default for buttons/inputs
  lg: "1rem"       # cards
  xl: "1.5rem"     # hero panels
  full: "9999px"

spacing:
  base: "4px grid (0.25rem steps)"
  section_y: "clamp(4rem, 10vw, 8rem)"
  container: "max-w-5xl, px-4 md:px-6"
  gap_default: "1rem"

elevation:
  card: "border border-[--border] bg-[--bg_elev]"
  glow: "shadow-[0_0_40px_-12px_var(--primary)]  # neon glow ONLY on primary CTAs / hero accents"
  hairline: "single 1px [--border] line; prefer borders over heavy shadows"

motion:
  ease: "cubic-bezier(0.22, 1, 0.36, 1)"
  duration: "150ms micro / 300ms entrance / 600ms hero"
  principle: "purposeful, subtle. Draw-on/fade-up entrances. No bounce, no confetti."

components:
  button:
    primary: "bg [--primary], text [--primary_fg], radius md, font-medium, hover brightness-110, focus ring [--ring]"
    secondary: "bg [--bg_inset], text [--fg], border [--border], hover bg [--bg_elev]"
    ghost: "transparent, text [--fg_muted], hover text [--fg]"
  card: "radius lg, [--bg_elev], border [--border], p-6; hover: border brightens to [--fg_faint]"
  input: "[--bg_inset], border [--border], radius md, focus ring [--ring]"
  badge: "radius full, caption type, [--bg_inset] / [--fg_muted]; primary variant = [--primary] tint"
---

# Kiwuuu design intent (human-readable)

**Feel:** a control room for AI agents. Dark, precise, fast. Electric lime is the
single hero color — it marks the one action that matters on a screen. Never wash a
page in lime; one CTA, one glow, maximum impact.

**Hierarchy:** lead with a bold display headline, one line of muted subcopy, one
primary CTA. Everything else is hairline-bordered structure on near-black.

**Do:** generous vertical rhythm, monospace for numbers/metrics/code, crisp 1px
borders, subtle neon glow only on the primary CTA or a hero stat.

**Don't:** gradients-as-decoration, drop shadows everywhere, more than one accent
color per viewport, rounded-everything, emoji in product UI, generic SaaS-purple.

**Voice in UI copy:** direct, confident, lowercase wordmark `kiwuuu.`, no exclamation
spam. "Start free" beats "Get Started Today!". Specific beats vague.
