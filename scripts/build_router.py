#!/usr/bin/env python3
"""Generate the skill router index from a directory of Claude Code skills.

Scans <skills_dir>/*/SKILL.md, extracts the routing-relevant metadata, and
rewrites the generated block of ROUTER.md in place. Hand-written sections
(Disambiguation, Chains, and anything else outside the markers) are preserved.

Usage:
    python3 scripts/build_router.py skills/ --out ROUTER.md
    python3 scripts/build_router.py ~/.claude/skills --out ROUTER.md
    python3 scripts/build_router.py skills/ --stdout      # preview, write nothing

No third-party dependencies — the frontmatter parser handles the small YAML
subset skills actually use, so this runs on a bare VPS python3.
"""

import argparse
import os
import re
import sys

# Rewriting is confined to the span between these markers so the judgment-driven
# sections of ROUTER.md survive regeneration.
BEGIN_MARKER = "<!-- BEGIN GENERATED -->"
END_MARKER = "<!-- END GENERATED -->"

# Skill bodies routinely exceed this; the canonical guide caps SKILL.md at 500
# lines, so anything longer is flagged as an authoring problem, not truncated.
BODY_LINE_LIMIT = 500

# A description under this length almost never carries enough trigger vocabulary
# to win selection against 100+ competing skills. Chosen to be roughly the point
# where "what it does" plus a USE WHEN clause both fit.
MIN_DESCRIPTION_CHARS = 120

# Anthropic's hard limit on the description field.
MAX_DESCRIPTION_CHARS = 1024


def parse_frontmatter(text):
    """Return (frontmatter_dict, body) from a SKILL.md.

    Handles `key: value`, folded (`>`) and literal (`|`) block scalars, and
    bare continuation lines. Values are flattened to single-line strings, which
    is all the router needs. Returns ({}, text) when there is no frontmatter.
    """
    if not text.startswith("---"):
        return {}, text

    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text

    data = {}
    key = None
    buffer = []

    def flush():
        if key is not None:
            data[key] = " ".join(part.strip() for part in buffer if part.strip()).strip()

    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match and not line.startswith((" ", "\t")):
            flush()
            key = match.group(1)
            value = match.group(2).strip()
            buffer = [] if value in (">", "|", ">-", "|-", "") else [value]
        elif key is not None:
            buffer.append(line)
    flush()

    return data, "\n".join(lines[end + 1:])


def split_description(description):
    """Split a description into (what_it_does, [trigger_keywords]).

    Recognises the `USE WHEN:` / `Use when` convention. Skills that omit it
    return an empty keyword list, which the report flags.
    """
    match = re.search(r"\bUSE WHEN\b\s*:?\s*(.*)$", description, re.IGNORECASE | re.DOTALL)
    if not match:
        return description.strip(), []

    what = description[:match.start()].strip()
    raw = match.group(1)
    keywords = [k.strip(" .;") for k in re.split(r"[,;]", raw)]
    return what, [k for k in keywords if k]


def parse_routing_table(body):
    """Extract (trigger, target) pairs from a `## Workflow Routing` table."""
    match = re.search(
        r"^##+\s*Workflow Routing\s*$(.*?)(?=^##\s|\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []

    rows = []
    for line in match.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s|:-]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() in ("trigger", "if the user says…"):
            continue
        target = cells[1].strip("`")
        # Trigger cells hold comma-separated phrases; one row per phrase keeps
        # the rendered route table scannable.
        for trigger in (t.strip() for t in cells[0].split(",")):
            if trigger:
                rows.append((trigger, target))
    return rows


def summarize_workflow(path):
    """One-line summary of a workflow file: its first real prose paragraph."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        return f"(unreadable: {exc})"

    for block in text.split("\n\n"):
        block = block.strip()
        if not block or block.startswith(("#", "```", "|", ">", "-", "*")):
            continue
        return " ".join(block.split())
    return "(no prose summary found)"


def scan_skill(skill_dir):
    """Collect router metadata for one skill directory, or None if it has no SKILL.md."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return None

    try:
        with open(skill_md, encoding="utf-8") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"  ! skipping {skill_dir}: {exc}", file=sys.stderr)
        return None

    front, body = parse_frontmatter(text)
    description = front.get("description", "")
    what, keywords = split_description(description)

    workflows = []
    workflow_dir = next(
        (os.path.join(skill_dir, name)
         for name in ("Workflows", "workflows")
         if os.path.isdir(os.path.join(skill_dir, name))),
        None,
    )
    if workflow_dir:
        for filename in sorted(os.listdir(workflow_dir)):
            if filename.endswith(".md"):
                workflows.append((
                    f"{os.path.basename(workflow_dir)}/{filename}",
                    summarize_workflow(os.path.join(workflow_dir, filename)),
                ))

    return {
        "name": front.get("name") or os.path.basename(skill_dir),
        "dir": os.path.basename(skill_dir),
        "version": front.get("version", ""),
        "status": front.get("status", ""),
        "description": description,
        "what": what,
        "keywords": keywords,
        "routing": parse_routing_table(body),
        "workflows": workflows,
        "body_lines": len(body.split("\n")),
    }


def lint(skill):
    """Authoring problems that degrade routing, per the canonical skills guide."""
    problems = []
    length = len(skill["description"])
    if not skill["description"]:
        problems.append("no description — this skill can never be selected")
    elif length < MIN_DESCRIPTION_CHARS:
        problems.append(f"description only {length} chars — too thin to win selection")
    if length > MAX_DESCRIPTION_CHARS:
        problems.append(f"description {length} chars — over the {MAX_DESCRIPTION_CHARS} limit")
    if not skill["keywords"]:
        problems.append("no USE WHEN clause — no trigger keywords")
    if skill["body_lines"] > BODY_LINE_LIMIT:
        problems.append(f"body {skill['body_lines']} lines — over the {BODY_LINE_LIMIT} guideline")
    if skill["workflows"] and not skill["routing"]:
        problems.append("has workflow files but no Workflow Routing table")
    return problems


def render(skills):
    """Render the generated block: skill index, route table, and lint report."""
    out = [BEGIN_MARKER, ""]
    out.append(f"## Skill index ({len(skills)} skills)")
    out.append("")

    for skill in skills:
        heading = f"### `{skill['name']}`"
        meta = " · ".join(p for p in (skill["version"], skill["status"]) if p)
        out.append(f"{heading}{f' — {meta}' if meta else ''}")
        out.append("")
        out.append(skill["what"] or "_No description._")
        out.append("")
        for path, summary in skill["workflows"]:
            out.append(f"- `{path}` — {summary}")
        if skill["workflows"]:
            out.append("")

    out.append("## Route table — keyword → skill → workflow")
    out.append("")
    out.append("| Trigger keywords | Skill | Workflow |")
    out.append("|---|---|---|")

    for skill in skills:
        targets = {}
        for trigger, target in skill["routing"]:
            targets.setdefault(target, []).append(trigger)

        for target, triggers in targets.items():
            out.append(
                f"| {', '.join(f'`{t}`' for t in triggers)} "
                f"| `{skill['name']}` | `{target}` |"
            )
        # Single-mode skills have no routing table; fall back to the description's
        # USE WHEN keywords so they still appear in the route table.
        if not targets and skill["keywords"]:
            out.append(
                f"| {', '.join(f'`{k}`' for k in skill['keywords'])} "
                f"| `{skill['name']}` | _(single mode)_ |"
            )

    out.append("")

    flagged = [(s, lint(s)) for s in skills]
    flagged = [(s, p) for s, p in flagged if p]
    out.append("## Routing health")
    out.append("")
    if not flagged:
        out.append("All skills carry a description, trigger keywords, and a routing table.")
    else:
        out.append("| Skill | Problem |")
        out.append("|---|---|")
        for skill, problems in flagged:
            for problem in problems:
                out.append(f"| `{skill['name']}` | {problem} |")
    out.append("")
    out.append(END_MARKER)
    return "\n".join(out)


def splice(existing, generated):
    """Replace the marked block in `existing`, or append it if not present."""
    start = existing.find(BEGIN_MARKER)
    end = existing.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        return existing.rstrip() + "\n\n" + generated + "\n"
    return existing[:start] + generated + existing[end + len(END_MARKER):]


def main():
    parser = argparse.ArgumentParser(description="Build the skill router index.")
    parser.add_argument("skills_dir", help="Directory containing skill subfolders.")
    parser.add_argument("--out", default="ROUTER.md", help="Router file to update.")
    parser.add_argument("--stdout", action="store_true", help="Print instead of writing.")
    args = parser.parse_args()

    if not os.path.isdir(args.skills_dir):
        print(f"error: {args.skills_dir} is not a directory", file=sys.stderr)
        return 1

    try:
        entries = sorted(os.listdir(args.skills_dir))
    except PermissionError as exc:
        print(f"error: cannot read {args.skills_dir}: {exc}", file=sys.stderr)
        return 1

    skills = []
    for entry in entries:
        path = os.path.join(args.skills_dir, entry)
        if os.path.isdir(path):
            skill = scan_skill(path)
            if skill:
                skills.append(skill)

    if not skills:
        print(f"error: no SKILL.md found under {args.skills_dir}", file=sys.stderr)
        return 1

    generated = render(skills)

    if args.stdout:
        print(generated)
        return 0

    existing = ""
    if os.path.isfile(args.out):
        try:
            with open(args.out, encoding="utf-8") as handle:
                existing = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: cannot read {args.out}: {exc}", file=sys.stderr)
            return 1

    try:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(splice(existing, generated))
    except OSError as exc:
        print(f"error: cannot write {args.out}: {exc}", file=sys.stderr)
        return 1

    problems = sum(len(lint(s)) for s in skills)
    print(f"Wrote {args.out} — {len(skills)} skills, {problems} routing problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
