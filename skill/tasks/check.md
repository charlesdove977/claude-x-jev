<purpose>
Put one yes/no question to many items and get back the probability of yes for each. The `noul` primitive. Best for conditions: is this real, does this pay, does this need a reply, is this safe.
</purpose>

<user-story>
As an operator, I want a probability on a single condition across a whole list, so that I can act on the confident yeses and noes and only look at the middle.
</user-story>

<when-to-use>
- The question is a condition, not a category
- A gate or a filter over many items
- "Which of these are actually X"
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/primitives.md (noul semantics: 0.5 is unknown, not medium)
@frameworks/criteria-writing.md (rule 6: a noul reads as a checkable statement)
@frameworks/cascade.md (bands, not single cutoffs)
@templates/run-report.md
</references>

<steps>

<step name="write_the_statement" priority="first">
Turn the user's question into a statement that names the field it judges and can be true or false on the text alone. "Is this a good lead?" becomes "Do `company`, `website`, and `message` describe a real operating business rather than a student or a vendor?" Show it. Wait for response.
</step>

<step name="preset">
Use an existing preset with a noul question, or write a one-question preset with `templates/preset.md`. Set the threshold as a band, for example `{"low": 0.2, "high": 0.8}`. Anything inside the band is unsure.
</step>

<step name="lint_dry_run_small_run">
Same discipline as `/jev-classify`: `lint`, `--dry-run --limit 1`, then `--limit 5` and eyeball. Wait for response after the five.
</step>

<step name="full_run">
`jev.py ask --preset <p> --input <file> --out <name>.jsonl`. Read back the summary line.
</step>

<step name="report" priority="last">
Present three groups: confident yes (above the band), confident no (below), unsure (inside). Give counts and three examples from each edge. Suggest `/jev-tune` is not needed for a noul until there is labelled data; the band is the threshold.
</step>

</steps>

<output>
- Results file with the probability per item and `_sure`
- Three-group report: yes, no, unsure
</output>

<acceptance-criteria>
- [ ] The statement names its fields and is checkable on the text
- [ ] The threshold is a band, not a single cutoff
- [ ] 0.5 was never described as "medium"
- [ ] Five items eyeballed before the full run
</acceptance-criteria>
