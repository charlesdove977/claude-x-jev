<purpose>
Measure instead of assume. Run Jev and a second judge (Claude in this session, or any other results file) over the same items, and report agreement per question, cost, time, and the disagreements with their text.
</purpose>

<user-story>
As an operator deciding whether Jev can take over a step Claude does today, I want a side-by-side on my own data, so that the decision rests on my items and not on someone else's benchmark.
</user-story>

<when-to-use>
- "Can Jev do this instead of Claude", "how accurate is it on my stuff"
- Before moving any step from Claude to Jev
- After a model update, to see whether anything moved
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/jev-vs-claude.md (the reference benchmark and how to read disagreements)
@templates/bench-report.md
</references>

<steps>

<step name="sample" priority="first">
Take 50 to 200 items, random, not the easy ones. Fewer than 50 and the percentages are noise. Say the count and the estimated Claude cost or time before starting; Jev's side is cents. Wait for response.
</step>

<step name="run_jev">
    python3 <skill-dir>/scripts/jev.py ask --preset <p> --input sample.json --out jev.jsonl

Note the summary line: wall time, mean latency, cost.
</step>

<step name="run_claude">
Claude labels the same items in this session, using the preset's exact label names and criteria text, and writes `claude.jsonl` with the same `_id` and question keys. Time it with a timestamp before and after. Work in batches of 20 to 25 so the context holds. Do not look at Jev's answers first.
</step>

<step name="compare">
    python3 <skill-dir>/scripts/jev.py bench --a jev.jsonl --b claude.jsonl --questions <q1,q2>

Then read every disagreement's text and sort them into: harmless (both labels lead to the same action), definition bug (the criteria text decided it), Jev right, Claude right, unclear. This reading is the benchmark; the percentage alone is not.
</step>

<step name="report" priority="last">
Fill `templates/bench-report.md`: the table, the disagreement classes with counts, the confidence cascade (agreement above and below 0.7), and a one-line recommendation: which side of the line this step belongs on, and what to fix in the preset first.
</step>

</steps>

<output>
- `jev.jsonl` and `claude.jsonl` on the same sample
- An agreement table per question with cost and time
- Disagreements classified by hand, and a recommendation
</output>

<acceptance-criteria>
- [ ] Sample was random and at least 50 items
- [ ] Claude labelled blind to Jev's answers
- [ ] Every disagreement was read and classified
- [ ] Agreement was split by Jev confidence, not reported as one number
- [ ] Recommendation names a preset fix, not only a verdict
</acceptance-criteria>
