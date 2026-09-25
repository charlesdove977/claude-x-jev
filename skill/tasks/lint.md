<purpose>
Catch definition bugs before they cost a batch. Static checks on a preset's questions, criteria, thresholds and rules, with each warning explained against the criteria-writing rules.
</purpose>

<user-story>
As someone writing my first preset, I want the tool to tell me which label is vague, which question has nowhere for odd items to go, and which pair of answers can contradict, before I spend money finding out.
</user-story>

<when-to-use>
- Before the first run of any new or edited preset
- After a batch with more disagreements than expected
- `ask` refused to run because lint found errors
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/criteria-writing.md (each lint rule and why it exists)
@frameworks/primitives.md (the request shapes lint enforces)
</references>

<steps>

<step name="run" priority="first">
    python3 <skill-dir>/scripts/jev.py lint --preset <name-or-path>

ERROR lines block a run: wrong type, missing criteria, score criteria not an ordered list, thresholds or rules pointing at unknown questions. Warnings are advice.
</step>

<step name="explain_each">
For every line, quote the offending label or instruction and point at the matching rule in `frameworks/criteria-writing.md`. Propose the rewrite in place: an observable cue instead of an adjective, a finished list instead of "etc.", a catch-all or `exhaustive: true`, a rule for a pair of answers that can contradict.
</step>

<step name="apply_and_rerun" priority="last">
Edit the preset (a copy outside the bundled folder if it was bundled). Re-run lint until it prints `clean`. Then run five items through `ask --limit 5` to see the rewritten labels behave.
</step>

</steps>

<output>
- A clean lint
- Rewritten criteria with the reasoning stated per change
</output>

<acceptance-criteria>
- [ ] Every ERROR fixed, every warning either fixed or consciously kept with a reason
- [ ] No bundled preset edited in place
- [ ] Five items run after the rewrite
</acceptance-criteria>
