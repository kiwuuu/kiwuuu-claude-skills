# Debate Workflow

Full structured multi-agent debate with 3 rounds and visible transcript.

## Upgrade Note (2026-04-17)

Council now runs **5 real AI voice essences** instead of 4 Claude personas. Each subagent Task prompt is **prefixed with the contents of its voice essence file** from `../Voices/`. The voice shapes HOW the agent thinks about the topic; the topic itself is unchanged. Five voices:

- **Serena Blackwood** (Architect) — `../Voices/cursor_voice.md`
- **Aditi Sharma** (Designer) — `../Voices/lovable_voice.md`
- **Marcus Webb** (Engineer) — `../Voices/manus_voice.md`
- **Ava Chen** (Researcher) — `../Voices/perplexity_voice.md`
- **Rook Blackburn** (Verifier) — `../Voices/devin_voice.md`

Read the voice file contents at the start of the workflow, then embed them into each agent's Round-1/2/3 prompts as a preamble.

## Prerequisites

- Topic or question to debate
- Optional: Custom council members (default: all 5 voices above)

## Execution

### Step 0: Load Voice Essences

Before spawning any subagents, READ the 5 voice essence files from `../Voices/`. Hold each voice's full text in memory — you will prepend it to that agent's prompt in every round.

If the user has overridden membership (e.g. "council without Devin" or "just Cursor and Lovable"), only load the voices for the selected members.

### Step 1: Announce the Council

Output the debate header:

```markdown
## Council Debate: [Topic]

**Council Members:** [List members participating + their source AI]
**Rounds:** 3 (Positions → Responses → Synthesis)
**Voice source:** Real AI essences from knowledge/ai-intelligence/
```

### Step 2: Round 1 — Initial Positions

Launch 5 parallel Task calls (one per council member, or fewer if membership overridden).

**Each agent prompt structure:**
```
[FULL VOICE ESSENCE FILE CONTENTS — verbatim, including frontmatter]

---

COUNCIL DEBATE — ROUND 1: INITIAL POSITIONS

Topic: [The topic being debated]

Give your initial position on this topic IN YOUR VOICE as defined above.
- Speak in first person as the persona described in the voice essence
- Preserve the cognitive style, voice markers, and anti-patterns from your voice file
- Be specific and substantive (50-150 words)
- State your key concern, recommendation, or insight
- You'll respond to other council members in Round 2

Your role's focus: [Architect/Designer/Engineer/Researcher/Verifier domain]
```

**Output each response as it completes:**
```markdown
### Round 1: Initial Positions

**Architect (Serena — Cursor voice):**
[Response]

**Designer (Aditi — Lovable voice):**
[Response]

**Engineer (Marcus — Manus voice):**
[Response]

**Researcher (Ava — Perplexity voice):**
[Response]

**Verifier (Rook — Devin voice):**
[Response]
```

### Step 3: Round 2 — Responses & Challenges

Launch parallel Task calls with Round 1 transcript included.

**Each agent prompt structure:**
```
[FULL VOICE ESSENCE FILE CONTENTS]

---

COUNCIL DEBATE — ROUND 2: RESPONSES & CHALLENGES

Topic: [The topic being debated]

Here's what the council said in Round 1:
[Full Round 1 transcript — all 5 positions]

Now respond to the other council members IN YOUR VOICE:
- Reference specific points they made ("I disagree with [Name]'s point about X...")
- Challenge assumptions or add nuance
- Build on points you agree with
- Maintain your specialized perspective AND the cognitive style from your voice file
- 50-150 words

The value is in genuine intellectual friction — engage with their actual arguments using the lens your voice gives you. A Cursor-voice Architect traces their claim to definitions; a Perplexity-voice Researcher asks for sources; a Devin-voice Verifier asks what's been verified.
```

**Output:**
```markdown
### Round 2: Responses & Challenges

**Architect (Serena):** [Response referencing others' points]
**Designer (Aditi):** [Response referencing others' points]
**Engineer (Marcus):** [Response referencing others' points]
**Researcher (Ava):** [Response referencing others' points]
**Verifier (Rook):** [Response referencing others' points]
```

### Step 4: Round 3 — Synthesis

Launch parallel Task calls with Round 1 + Round 2 transcripts.

**Each agent prompt structure:**
```
[FULL VOICE ESSENCE FILE CONTENTS]

---

COUNCIL DEBATE — ROUND 3: SYNTHESIS

Topic: [The topic being debated]

Full debate transcript so far:
[Round 1 + Round 2 transcripts]

Final synthesis from your voice:
- Where does the council agree?
- Where do you still disagree with others?
- What's your final recommendation given the full discussion?
- Stay true to your voice's cognitive style and anti-patterns
- 50-150 words

Be honest about remaining disagreements — forced consensus is worse than acknowledged tension.
```

**Output:**
```markdown
### Round 3: Synthesis

**Architect (Serena):** [Final synthesis]
**Designer (Aditi):** [Final synthesis]
**Engineer (Marcus):** [Final synthesis]
**Researcher (Ava):** [Final synthesis]
**Verifier (Rook):** [Final synthesis]
```

### Step 5: Council Synthesis

After all rounds complete, synthesize the debate:

```markdown
### Council Synthesis

**Areas of Convergence:**
- [Points where 3+ agents agreed]
- [Shared concerns or recommendations]

**Remaining Disagreements:**
- [Points still contested between agents]
- [Trade-offs that couldn't be resolved]

**Recommended Path:**
[Based on convergence and weight of arguments, the recommended approach is...]
```

## Custom Council Members

If user specifies custom membership, adjust accordingly:

- "Council without Devin" → Skip Verifier (don't load devin_voice.md)
- "Council without researcher" → Skip Perplexity voice
- "Just Cursor and Lovable" → Only Architect + Designer voices
- "Council with security" → Add legacy pentester agent
- "Council with intern" → Add intern agent (fresh perspective)
- "Just architect and engineer" → Only those two voices

## Agent Type Mapping

All 5 default voices run via `general-purpose` subagent_type. Cognitive diversity comes from the voice essence prepended to the prompt, not from different agent infrastructure.

| Council Role | subagent_type | Voice File |
|--------------|--------------|------------|
| Architect | general-purpose | `../Voices/cursor_voice.md` |
| Designer | general-purpose | `../Voices/lovable_voice.md` |
| Engineer | general-purpose | `../Voices/manus_voice.md` |
| Researcher | general-purpose | `../Voices/perplexity_voice.md` |
| Verifier | general-purpose | `../Voices/devin_voice.md` |

## Timing

- Voice load: <1 sec (read 5 files once)
- Round 1: ~10-20 sec (parallel)
- Round 2: ~10-20 sec (parallel)
- Round 3: ~10-20 sec (parallel)
- Synthesis: ~5 sec

**Total: 30-90 seconds for full 5-voice debate**

## Done

Debate complete. The transcript shows the full intellectual journey — with 5 genuinely distinct cognitive styles instead of 4 Claude personas — from initial positions through challenges to synthesis.
