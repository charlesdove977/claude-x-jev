<purpose>
Place many items on an ordered scale and get back a weighted position, a probability per level, and a confidence. The `score` primitive. For ranking and prioritizing: lead heat, reply value, urgency, quality.
</purpose>

<user-story>
As an operator with more items than time, I want them ranked on a scale I defined, so that I work the top of the list first and know how sure the ranking is.
</user-story>

<when-to-use>
- "Rank these", "prioritize", "how hot", "how urgent", "rate 1 to 5"
- The levels can be written as an ordered list where each step adds one visible signal
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/primitives.md (score request: criteria is an ORDERED array; response: score, probabilities by index, legend)
@frameworks/criteria-writing.md (rule 7: adjacent levels differ by one observable)
@templates/run-report.md
</references>

<steps>

<step name="define_levels" priority="first">
Write the levels lowest to highest, three to five of them, each naming the one signal that separates it from the level below. Show the list. Wait for response.

<if condition="two adjacent levels differ only by degree words (somewhat, very)">
Merge them or name the concrete signal. Degree words produce scores that hover between levels.
</if>
</step>

<step name="preset">
Write or reuse a preset with a `score` question. `criteria` is a JSON array in order; index 0 is the lowest level. Threshold on confidence (default 0.7).
</step>

<step name="lint_dry_run_small_run">
`lint`, `--dry-run --limit 1`, `--limit 5`. On the five, show the score, the rounded level, and the legend text for that level. Wait for response.
</step>

<step name="full_run">
`jev.py ask --preset <p> --input <file> --out <name>.jsonl`. Read back the summary line.
</step>

<step name="report" priority="last">
Sort by score descending. Show the count per rounded level and the top ten with their score and confidence. Say where the sure line falls. Offer to write the ranked list as CSV for the user's tool of choice.
</step>

</steps>

<output>
- Results file with `score`, `score_conf`, per-level probabilities, and the legend
- A ranked list, top first, with counts per level
</output>

<acceptance-criteria>
- [ ] Levels are an ordered array, lowest first, each step naming one signal
- [ ] Rounded level and raw score were both shown
- [ ] Five items eyeballed before the full run
- [ ] Ranking was delivered as a file, not only in chat
</acceptance-criteria>
