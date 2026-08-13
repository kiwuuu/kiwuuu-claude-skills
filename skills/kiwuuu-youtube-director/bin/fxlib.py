#!/usr/bin/env python3
"""fxlib — the Kiwuuu video effects library.

Reusable motion/graphic/sound effects for the stick-figure explainer format.
Everything is local ffmpeg + ASS + the bundled SFX pack. No credits, no API.

Each builder returns a dict:
    {"ass": [dialogue lines], "filters": [ffmpeg filter strings], "sfx": [(path, t, gain)]}
so a caller can merge many effects into one render pass.

SFX pack: OpenMontage/.agents/skills/hyperframes-media/assets/sfx/
"""
import os, math

SFX_DIR = r"C:\Users\Korisnik\OpenMontage\.agents\skills\hyperframes-media\assets\sfx"
SFX = {k: os.path.join(SFX_DIR, f"{k}.mp3") for k in [
    "key-press", "typing", "click", "click-soft", "pop", "ping", "chime",
    "notification", "sparkle", "whoosh", "whoosh-short", "whoosh-cinematic",
    "impact-bass-1", "impact-bass-2", "riser", "error", "glitch-1", "glitch-2", "glitch-3"]}

# house style — matches the burned karaoke captions
LIME = "&H002EE9A6"
WHITE = "&H00FFFFFF"
BLACK = "&H00000000"
RED = "&H002222DD"
FONT = "Segoe UI Black"


def ts(t):
    cs = max(0, int(round(t * 100)))
    return f"{cs//360000}:{cs%360000//6000:02d}:{cs%6000//100:02d}.{cs%100:02d}"


def style_line(name, size, primary=WHITE, outline=6, align=8, ml=80, mr=80, mv=90, spacing=0):
    return (f"Style: {name},{FONT},{size},{primary},{WHITE},{BLACK},{BLACK},"
            f"-1,0,0,0,100,100,{spacing},0,1,{outline},0,{align},{ml},{mr},{mv},1")


# ─────────────────────────── 1. TYPEWRITER ───────────────────────────
def typewriter(text, t0, type_dur=None, hold=1.2, style="FX_TYPE",
               cps=11.5, cursor="▌", sfx_gain=0.7, blink=True):
    """Character-by-character reveal with one keystroke sound per character.

    Used for: location cards, dates, names, "signed / dated" beats.
    cps = characters per second (11-13 reads as brisk-but-legible).
    """
    n = len(text)
    step = (type_dur / n) if type_dur else (1.0 / cps)
    ass, sfx = [], []
    for i in range(1, n + 1):
        a, b = t0 + (i - 1) * step, t0 + i * step
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},{style},,0,0,0,,{text[:i]}{cursor}")
        if text[i - 1] != " ":
            sfx.append((SFX["key-press"], round(a, 3), sfx_gain))
    end_type = t0 + n * step
    if blink:
        t = end_type
        while t < end_type + hold:
            on = min(t + 0.4, end_type + hold)
            ass.append(f"Dialogue: 0,{ts(t)},{ts(on)},{style},,0,0,0,,{text}{cursor}")
            off = min(on + 0.4, end_type + hold)
            if off > on:
                ass.append(f"Dialogue: 0,{ts(on)},{ts(off)},{style},,0,0,0,,{text}")
            t = off
    else:
        ass.append(f"Dialogue: 0,{ts(end_type)},{ts(end_type+hold)},{style},,0,0,0,,{text}")
    return {"ass": ass, "filters": [], "sfx": sfx,
            "styles": [style_line(style, 62, WHITE, 7, 7, 100, 60, 110, 4)],
            "end": end_type + hold}


# ─────────────────────────── 2. BAR COMPARE ───────────────────────────
def bar_compare(items, t0, dur, W=1920, H=1080, base_y=820, bar_w=210, gap=150,
                grow=0.9, colors=None):
    """Animated bar chart that grows from zero — for any A-vs-B comparison.

    items: [(label, value), ...]  values are relative; tallest fills the plot.
    Bars grow over `grow` seconds then hold. Returns ffmpeg drawbox filters
    (cheap, no PIL) plus label ASS and a ping per bar as it lands.
    """
    colors = colors or ["0x2EE9A6", "0xDD2222", "0x888888"]
    top_pad, plot_h = 250, base_y - 250
    mx = max(v for _, v in items) or 1
    total_w = len(items) * bar_w + (len(items) - 1) * gap
    x0 = (W - total_w) // 2
    filters, ass, sfx = [], [], []
    # baseline
    filters.append(f"drawbox=x={x0-70}:y={base_y}:w={total_w+140}:h=5:"
                   f"color=0x333333@0.9:t=fill:enable='between(t,{t0},{t0+dur})'")
    for i, (label, val) in enumerate(items):
        x = x0 + i * (bar_w + gap)
        h_full = int(plot_h * val / mx)
        c = colors[i % len(colors)]
        # height ramps 0 -> h_full over `grow`, eased
        hexpr = f"min(1\\,max(0\\,(t-{t0+i*0.18})/{grow}))"
        h = f"({h_full}*{hexpr})"
        filters.append(
            f"drawbox=x={x}:y='{base_y}-{h}':w={bar_w}:h='{h}':color={c}@0.92:t=fill:"
            f"enable='between(t,{t0+i*0.18},{t0+dur})'")
        land = t0 + i * 0.18 + grow
        ass.append(f"Dialogue: 0,{ts(land-0.05)},{ts(t0+dur)},FX_BARLBL,,0,0,0,,"
                   f"{{\\pos({x+bar_w//2},{base_y+40})}}{label}")
        sfx.append((SFX["ping"], round(land, 3), 0.45))
    return {"ass": ass, "filters": filters, "sfx": sfx,
            "styles": [style_line("FX_BARLBL", 46, WHITE, 6, 8, 0, 0, 0)],
            "end": t0 + dur}


# ─────────────────────────── 3. COUNTER ───────────────────────────
def counter(t0, dur, lo, hi, prefix="$", suffix="", style="FX_COUNT",
            steps=26, tick_every=3, crash=False):
    """A number that spins up (or crashes to zero). Ticks as it climbs."""
    ass, sfx = [], []
    step = dur / steps
    for i in range(steps + 1):
        p = i / steps
        p = 1 - (1 - p) ** 3                      # ease-out
        v = lo + (hi - lo) * p
        a, b = t0 + i * step, t0 + (i + 1) * step
        txt = f"{prefix}{v:,.0f}{suffix}"
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},{style},,0,0,0,,{txt}")
        if i % tick_every == 0 and i < steps:
            sfx.append((SFX["click-soft"], round(a, 3), 0.30))
    sfx.append((SFX["impact-bass-1"] if crash else SFX["ping"], round(t0 + dur, 3), 0.55))
    return {"ass": ass, "filters": [], "sfx": sfx,
            "styles": [style_line(style, 96, LIME if not crash else RED, 8, 5, 0, 0, 0)],
            "end": t0 + dur}


# ─────────────────────────── 4. STAT POP ───────────────────────────
def stat_pop(text, t0, dur=2.2, style="FX_STAT", sound="pop"):
    """A single hard fact slamming onto screen. Scale-punch via ASS \\fscx."""
    ass = [
        f"Dialogue: 0,{ts(t0)},{ts(t0+0.10)},{style},,0,0,0,,{{\\fscx130\\fscy130\\alpha&H40&}}{text}",
        f"Dialogue: 0,{ts(t0+0.10)},{ts(t0+0.20)},{style},,0,0,0,,{{\\fscx94\\fscy94}}{text}",
        f"Dialogue: 0,{ts(t0+0.20)},{ts(t0+dur)},{style},,0,0,0,,{text}",
    ]
    return {"ass": ass, "filters": [], "sfx": [(SFX[sound], t0, 0.6)],
            "styles": [style_line(style, 84, LIME, 8, 5, 0, 0, 0)], "end": t0 + dur}


# ─────────────────────────── 5. STRIKE-THROUGH ───────────────────────────
def strike(text, t0, dur=2.4, style="FX_STRIKE"):
    """Word appears, then gets crossed out — for myths/corrections."""
    ass = [f"Dialogue: 0,{ts(t0)},{ts(t0+0.55)},{style},,0,0,0,,{text}",
           f"Dialogue: 0,{ts(t0+0.55)},{ts(t0+dur)},{style},,0,0,0,,{{\\s1}}{text}"]
    return {"ass": ass, "filters": [], "sfx": [(SFX["error"], t0 + 0.55, 0.45)],
            "styles": [style_line(style, 76, RED, 8, 5, 0, 0, 0)], "end": t0 + dur}


# ─────────────────────────── 6. ACCENTS ───────────────────────────
def accent(t0, kind="whoosh", gain=0.5):
    """Bare sound accent on a cut — whoosh / impact-bass-1 / glitch-1 / sparkle."""
    return {"ass": [], "filters": [], "sfx": [(SFX[kind], t0, gain)], "styles": [], "end": t0}


def flash(t0, dur=0.14, W=1920, H=1080, color="white@0.55"):
    """One-frame-ish white flash for a hard beat change."""
    return {"ass": [], "sfx": [],
            "filters": [f"drawbox=x=0:y=0:w={W}:h={H}:color={color}:t=fill:"
                        f"enable='between(t,{t0},{t0+dur})'"],
            "styles": [], "end": t0 + dur}


# ─────────────────────────── merge helper ───────────────────────────
def merge(*fx):
    out = {"ass": [], "filters": [], "sfx": [], "styles": []}
    for f in fx:
        for k in out:
            out[k] += f.get(k, [])
    seen, styles = set(), []
    for s in out["styles"]:
        nm = s.split(",")[0]
        if nm not in seen:
            seen.add(nm); styles.append(s)
    out["styles"] = styles
    return out


def build_sfx_track(sfx, total, out_path, ff):
    """Mix all (path, t, gain) cues into one bed the length of the video."""
    import subprocess
    if not sfx:
        subprocess.run([ff, "-y", "-f", "lavfi", "-i",
                        f"anullsrc=r=48000:cl=stereo:d={total}", out_path],
                       capture_output=True)
        return out_path
    args, parts, mixes = [ff, "-y"], [], []
    for i, (p, t, g) in enumerate(sfx):
        args += ["-i", p]
        ms = int(max(0, t) * 1000)
        parts.append(f"[{i}:a]aresample=48000,volume={g},adelay={ms}|{ms}[s{i}]")
        mixes.append(f"[s{i}]")
    graph = (";".join(parts) + ";" + "".join(mixes) +
             f"amix=inputs={len(sfx)}:duration=longest:normalize=0,"
             f"apad,atrim=0:{total}[out]")
    args += ["-filter_complex", graph, "-map", "[out]", "-ac", "2", "-ar", "48000", out_path]
    subprocess.run(args, capture_output=True)
    return out_path


EFFECT_INDEX = """
typewriter   text types out with keystroke clicks   dates, place cards, names, contract clauses
bar_compare  bars grow from zero, ping on landing   any A-vs-B: distance, cost, speed, volume
counter      number spins up or crashes             money totals, view counts, casualty counts
stat_pop     single fact slams in with a punch      the one number the beat exists for
strike       word appears then is crossed out       myths, corrections, "everyone gets this wrong"
accent       bare sound on a cut                    whoosh / impact / glitch / sparkle
flash        white frame flash                      hard pivot, reveal, shock cut
"""
