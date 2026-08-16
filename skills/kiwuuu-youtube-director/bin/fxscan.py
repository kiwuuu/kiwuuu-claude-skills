#!/usr/bin/env python3
"""fxscan — scan a rough-draft beat sheet and flag where effects belong.

MANDATORY STEP: run this on every video once the beat sheet exists and BEFORE
the final render. It reads each beat's VO and proposes effects from fxlib.

  python fxscan.py <beats.json>

Detection is deliberately conservative — it flags candidates, the director
picks. Silence is a failure mode: a 2-minute video with zero flagged effects
means the script has no concrete numbers or comparisons, which is a script
problem, not a scan problem.
"""
import json, re, sys

# each rule: (effect, regex, why, priority 1-3)
RULES = [
    ("bar_compare",
     r"\b(more than|less than|versus|vs\.?|compared|than the|times (?:more|less|that|bigger|smaller)|"
     r"only (?:a|one)|could (?:only )?(?:reach|cross|go)|died after|stretch(?:ed)? )",
     "an explicit A-vs-B comparison — show it, don't say it", 1),

    ("counter",
     r"""(\$\s?[\d,.]+|\b[\d,.]+\s?(?:million|billion|thousand)\b|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)\b(?:[\s\-]+\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)\b)*[\s\-]*(?:dollars?|cents?|million|billion|horsepower|pounds?)\b)""",
     "a money/scale figure — spin it up or crash it to zero", 1),

    ("typewriter",
     r"\b(1[6-9]\d{2}|20[0-2]\d)\b|"
     r"\b(New York|London|Paris|Miami|Chicago|Belgrade|Hong Kong|Wall Street|Sotheby|Christie)",
     "a date or place — type it out as a location/date card with keystrokes", 1),

    ("stat_pop",
     r"\b(\d+\s?(?:percent|%)|one in \w+|every \w+|per (?:second|minute|hour|day|horsepower))\b",
     "a hard rate/ratio — slam it on screen", 2),

    ("strike",
     r"\b(never|not true|myth|everyone (?:gets|thinks)|wrong|didn'?t|did not|actually)\b",
     "a correction or myth-bust — appear then cross out", 2),

    ("accent:impact-bass-1",
     r"\b(gone|broke|dead|died|collapsed|destroyed|vanished|zero|nothing|over)\b",
     "a hard landing — bass impact on the cut", 2),

    ("accent:whoosh",
     r"^(so|then|now|but|and here|fast forward|meanwhile|nine years later|five years)",
     "a time or logic pivot — whoosh the transition", 3),

    ("flash",
     r"\b(suddenly|instantly|in (?:one|a) (?:second|moment|instant)|snapped|slammed)\b",
     "an abrupt shock — one-frame flash", 3),
]


def scan(beats):
    hits = []
    for b in beats:
        vo = b.get("vo", "")
        low = vo.lower()
        for eff, rx, why, pri in RULES:
            m = re.search(rx, low if not rx.startswith("^") else low, re.I)
            if m:
                hits.append({"beat": b["n"], "effect": eff, "priority": pri,
                             "trigger": m.group(0).strip(), "why": why,
                             "vo": vo[:78]})
    return hits


def main(path):
    D = json.load(open(path, encoding="utf-8"))
    beats = D["beats"]
    hits = scan(beats)
    by_pri = {}
    for h in hits:
        by_pri.setdefault(h["priority"], []).append(h)

    print(f"FX SCAN — {len(beats)} beats, {len(hits)} candidates\n")
    for p in sorted(by_pri):
        tag = {1: "STRONG — add these", 2: "GOOD — add if it earns screen time",
               3: "OPTIONAL — audio-only accents"}[p]
        print(f"[P{p}] {tag}")
        for h in by_pri[p]:
            print(f"   beat {h['beat']:>2}  {h['effect']:<24} <- \"{h['trigger']}\"")
            print(f"            {h['why']}")
        print()

    strong = len(by_pri.get(1, []))
    dens = len(hits) / max(1, len(beats))
    print(f"density {dens:.2f} effects/beat  |  {strong} strong candidates")
    if strong == 0:
        print("\n!! NO STRONG CANDIDATES. The script has no concrete numbers or\n"
              "   comparisons to visualise. Fix the SCRIPT before rendering.")
    elif dens < 0.25:
        print("\n!  Thin. Consider adding a concrete figure or comparison per act.")
    return hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
