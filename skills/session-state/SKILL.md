---
name: session-state
version: 1.0.0
status: production
last-updated: 2026-08-13
description: >
  Writes the current session's state into the vault's _now.md so the next session — any machine,
  any tool — starts with zero catchup. Updates the Active/Waiting/Parked thread tables, stamps
  dates, deletes finished rows, and commits. Ships now_doctor.py (mechanical rot checks plus a
  Stop-hook guard that blocks ending a session with unsaved state) and a SessionEnd breadcrumb
  hook that records facts even when no handoff happens. The write-side counterpart to
  ultimate-loop CatchUp, which reads _now.md at session start.
  USE WHEN: handoff, save state, update now, wrap up, end session, ending for today, closing up,
  before you go, park this, record where we are, save progress, update the now file, sync state,
  now doctor, state doctor, check state health, stale threads, install handoff hooks.
---

# session-state — the write side of never playing catchup

`_now.md` in the mempalace vault is the single live answer to "what is in flight."
`ultimate-loop CatchUp` reads it at session start. This skill writes it at session end.
Both halves together are the protocol; either half alone decays into fiction.

## Locate the vault

In priority order:

1. `$MEMPALACE_ROOT` if set
2. A sibling or child checkout named `kiwuuu-mempalace` (search two levels from cwd)
3. `~/mempalace` or `~/vaults/mempalace`

If none exists, say so and offer to write the state block into the conversation instead —
never invent a vault path.

## Update `_now.md`

Work from what actually happened this session — commits made, PRs opened or updated,
decisions taken, blockers hit. Do not copy aspirations into the file; only state.

1. **Active table** — one row per in-flight thread:
   - `thread` — short stable name (survives across sessions; don't rename casually)
   - `status` — where it truly stands, one clause
   - `next` — an action a fresh session can execute **without asking anything**
   - `where` — repo · branch · PR/link/path, so nobody hunts
   - `updated` — today's date
2. **Waiting on** — threads blocked on a person or event; name the blocker and since-when.
3. **Parked** — deliberately shelved; name the wake condition.
4. **Delete finished rows.** Git history is the archive; the file stays one screen long.
5. Stamp `updated:` in the frontmatter.

## Quality gate for `next`

The whole system stands or falls on the `next` column. Test each entry: could a session
with zero conversation history execute it from the file alone? 

- ✅ `run scripts/build_router.py ~/.claude/skills --out ROUTER.md, then hand-write disambiguation for the n8n-* cluster`
- ❌ `continue the router work` (continue *what*, from *where*?)

If a `next` fails the test, it isn't saved state — it's a reminder that something was lost.

## Commit

```bash
cd "$VAULT" && git add _now.md && git commit -m "now: <one-line summary of state change>" && git push
```

If the vault has an active feature branch for current work, commit there; otherwise the
default branch. Never force-push. If push fails on network, retry with backoff (2s/4s/8s/16s).

## Output

End with the updated Active table pasted into the reply, so the human sees exactly what
the next session will see. No prose summary on top of it — the table is the summary.

## Enforcement — the parts that don't rely on discipline

Three scripts in `scripts/`, layered so state survives even a session that ignores every rule:

| Layer | When it runs | What it does |
|---|---|---|
| `now_doctor.py --report` | Session start (CatchUp Step 1 runs it) | Flags Active rows stale >7d, Waiting rows dead >30d, Parked rows without a wake condition, `_now.md` older than the vault's newest commit, `_index.md` count drift. Exit 1 on findings. |
| `now_doctor.py --guard` | Stop hook | If the workspace has commits newer than `_now.md`'s last update, blocks the stop once and instructs the handoff. One nag per session, silent when the invariant holds, exits 0 on any internal error. |
| `session_breadcrumb.py` | SessionEnd hook | Appends per-repo branch/commits/dirty facts to `_breadcrumbs/<hostname>.log` in the vault. Per-hostname files so machines never Syncthing-conflict; trimmed to the newest 10 entries; never commits. |

Run `analyze` intent through the doctor, not by eyeballing: **execute** `python3 scripts/now_doctor.py --report`.

Install the two hooks once per machine (merges into `~/.claude/settings.json`, backs up, idempotent):

```bash
bash scripts/install_hooks.sh
```

The invariant all three defend: **`_now.md` is the last thing a working session commits.**
When that holds, the guard is silent, the doctor is clean, and breadcrumbs are redundant.

## Boundaries

- **Never** delete or rewrite rows describing threads this session didn't touch — other
  sessions own those. Only stamp rows you have first-hand state for.
- This skill writes `_now.md` and nothing else. Vault notes, decisions, lessons are other
  skills' territory.
- Read-side is `ultimate-loop CatchUp` (`catch up`, `where were we`). If the user asks
  *what* the state is rather than to *save* it, route there.
