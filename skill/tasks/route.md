<purpose>
The tandem pattern. Jev labels everything; items above the confidence bar are acted on by label; the rest are handed to Claude with their full text. Claude reads the short list, not the whole queue.
</purpose>

<user-story>
As an operator working an inbox or a lead list with Claude, I want the obvious cases pre-sorted for a penny so that Claude's context and my attention go only to the items that need judgment.
</user-story>

<when-to-use>
- Any queue Claude was about to read end to end
- A workflow that already has a "classify, then act" step
- Before drafting replies: sort first, draft only for the right bucket
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/cascade.md (the pattern, the thresholds, the numbers behind them)
@checklists/before-autoroute.md (before any sure label triggers an action without a human look)
@templates/run-report.md
</references>

<steps>

<step name="preset_and_bar" priority="first">
Pick the preset (see `/jev-classify` for making one). Confirm the confidence bar: default 0.7 for choice and score, band 0.2 to 0.8 for noul. If the preset has been tuned (`/jev-tune`), its own thresholds apply. Say which questions block `_sure` and which are informational (threshold 0). Wait for response.
</step>

<step name="run_route">
Run:

    python3 <skill-dir>/scripts/jev.py route --preset <p> --input <file> --out <name>

It writes `<name>.sure.jsonl`, `<name>.unsure.jsonl`, and `<name>.unsure.items.jsonl` (the unsure items with their full original fields plus Jev's answers under `_jev`). Read back the summary line and the label distribution on the sure side.
</step>

<step name="act_on_sure">
For each label on the sure side, state what happens next. Dropping (spam, non_pitch) can be automatic once `checklists/before-autoroute.md` passes. Anything that sends, replies, or writes to a system stays draft-first: Claude drafts, a person approves.

<if condition="the user wants sure labels to trigger actions with no human look">
Run `checklists/before-autoroute.md` first. It requires a shadow batch where the labels were checked by hand. Do not skip it on the first day.
</if>
</step>

<step name="claude_reads_unsure">
Open `<name>.unsure.items.jsonl`. This is the only file Claude reads in full. For each item, Claude decides the label using the same criteria the preset uses, notes where Jev's probabilities pointed, and records the final label. If Claude disagrees with Jev's top choice, say so per item; those disagreements are the tuning set.
</step>

<step name="merge_and_report" priority="last">
Merge the sure labels and Claude's labels into one results file with a `decided_by` column (`jev` or `claude`). Present with `templates/run-report.md`: counts by label, how many Jev decided alone, how many Claude read, the cost line, and the time.

Then save Claude's labels for the unsure items as a truth file for `/jev-tune`, since a person or Claude just labelled exactly the items where the threshold matters.
</step>

</steps>

<output>
- `<name>.sure.jsonl`, `<name>.unsure.jsonl`, `<name>.unsure.items.jsonl`
- One merged results file with `decided_by`
- A truth file for the unsure slice, ready for `/jev-tune`
</output>

<acceptance-criteria>
- [ ] The confidence bar was stated before the run
- [ ] Claude read only the unsure items file, never the full input
- [ ] Every sure-side action that sends or writes stayed draft-first unless the autoroute checklist passed
- [ ] The merged file records who decided each item
- [ ] Claude's labels on the unsure slice were saved as a truth file
</acceptance-criteria>
