<purpose>
Check Claude's drafts before they ship. Jev reads each draft against the thread it answers and the rules it must follow, and returns grounded / unsupported / declined plus rule and tone checks. One failed check bounces the draft back to Claude.
</purpose>

<user-story>
As an operator sending replies Claude wrote, I want a fast, cheap, independent check that each draft only says things the thread and my rules support, so that a wrong number or a broken policy never reaches a customer.
</user-story>

<when-to-use>
- After Claude drafts replies, before the send gate
- Any generated text that must match a source: quotes, prices, dates, commitments
- A rule list exists (rate card, tone rules, never-say list) that every draft must obey
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/cascade.md (verify thresholds: one failed check is a bounce, never an average)
@presets/draft-verify.json (the bundled verification preset; copy and extend its rules text)
@templates/run-report.md
</references>

<steps>

<step name="build_items" priority="first">
One item per draft with three fields: `thread` (what the other party said, latest message first, trimmed), `rules` (the policy text the draft must obey, as a short numbered list), `draft` (the full draft). `_id` is the draft's own id. Keep `rules` identical across items in a batch so results compare.
</step>

<step name="run">
    python3 <skill-dir>/scripts/jev.py ask --preset draft-verify --input drafts.json --out verify.jsonl

Read back the summary line.
</step>

<step name="triage">
A draft passes only when `grounded = supported` with confidence at or above 0.8 AND `follows_rules` at or above 0.9 AND `tone_ok` at or above 0.8. Everything else bounces. List the bounced drafts with the failing check and its number.
</step>

<step name="claude_fixes">
For each bounced draft, Claude re-reads the thread and the rules, names the specific sentence that is unsupported or off-rule, rewrites it, and re-runs verify on that item only. Two bounces on the same draft means a person decides.
</step>

<step name="report" priority="last">
Present: passed count, bounced count with reasons, cost. Passed drafts move to the normal approval step; verification is a check, not a send.
</step>

</steps>

<output>
- `verify.jsonl` with per-draft verdicts
- A bounce list with the failing check per draft
- Rewritten drafts re-verified, or escalated after two bounces
</output>

<acceptance-criteria>
- [ ] Every item carried `thread`, `rules`, and `draft`
- [ ] Pass required every check to clear its bar; no averaging
- [ ] Bounced drafts were fixed by Claude and re-verified individually
- [ ] Verification never sent anything
</acceptance-criteria>
