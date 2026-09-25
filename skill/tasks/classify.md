<purpose>
Put one pick-one question to many items and get back a label, a probability per label, and a confidence for each. The `choice` primitive, end to end: preset, lint, dry run, small run, full run, report.
</purpose>

<user-story>
As an operator with a pile of emails, comments, tickets, or leads, I want every item labelled in seconds for cents, with a confidence number I can threshold, so that I only read the ones the model was unsure about.
</user-story>

<when-to-use>
- "Sort these", "label these", "which bucket", "categorize"
- A queue needs triage before anyone reads it
- Any time a label set can be written down in advance
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/primitives.md (choice request and response shape)
@frameworks/criteria-writing.md (before writing or editing any label)
@templates/preset.md (when a new preset is needed)
@templates/run-report.md (when presenting results)
@checklists/preset-ready.md (before the first full run)
</references>

<steps>

<step name="choose_preset" priority="first">
Run `jev.py presets` and show the list. Ask which fits, or whether a new one is needed. Bundled presets are generic examples; anything the user's data needs that they do not say belongs in a copy under `~/.claude/jev-presets/`, never in the bundled file. Wait for response.

<if condition="a new preset is needed">
Interview in one group: what is one item (paste one), what fields it has, the labels wanted, and one sentence per label on how a human tells it apart. Write the preset from `templates/preset.md` following `frameworks/criteria-writing.md`. Every label gets an observable cue. Add a catch-all or mark the question `exhaustive`.
</if>
</step>

<step name="prepare_input">
Items go in as a JSON array, JSONL, or CSV, one object per item. Field names must match the preset's `state_fields`. Add `_id` if the user has a stable key; otherwise the row index is used. Keep long text under `--max-chars` (default 8000); the question rarely needs more.
</step>

<step name="lint_and_dry_run">
Run `jev.py lint --preset <p>`. Fix every ERROR and read every warning against `frameworks/criteria-writing.md`. Then `jev.py ask --preset <p> --input <file> --dry-run --limit 1` and show the exact state the first item would send. Confirm the right fields, nothing private that should not leave the machine. Wait for response.
</step>

<step name="small_run">
Run five: `jev.py ask --preset <p> --input <file> --limit 5`. Show each item's label, confidence, and the top two probabilities beside a one-line view of the item. Ask whether the labels look right. If two or more are wrong, stop and fix the criteria before spending on the full run. Wait for response.
</step>

<step name="full_run">
Run `jev.py ask --preset <p> --input <file> --out <name>.jsonl` (add `--csv` for a spreadsheet). The script prints one summary line: items, wall time, mean latency, cost, errors, sure versus unsure counts. Read it back.

<if condition="errors are reported">
Show the first five error messages. HTTP 402 is credits; 401 is the key; 429 is rate limiting and already retried. Do not re-run the whole batch; re-run only the failed `_id`s.
</if>
</step>

<step name="report" priority="last">
Present with `templates/run-report.md`: label distribution, sure versus unsure, cost, and where the file is. Offer the natural next moves: `/jev-route` to hand the unsure slice to Claude, `/jev-tune` once some labels are checked by a person, `/jev-watch` to run this on a schedule.
</step>

</steps>

<output>
- A results file (JSONL or CSV) with one row per item: label, confidence, probabilities, `_sure`, cost, latency
- A run report with the label distribution and the unsure count
- A preset that passed lint, saved outside the bundled folder if it was new
</output>

<acceptance-criteria>
- [ ] Preset lint passed with no errors before any paid call
- [ ] A dry run was shown and the state fields confirmed
- [ ] Five items were run and eyeballed before the full batch
- [ ] The full run's summary line was reported verbatim
- [ ] Results were saved to a file the user can open, not left in chat
- [ ] No bundled preset was edited in place
</acceptance-criteria>
