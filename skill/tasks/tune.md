<purpose>
Pick the confidence threshold from data instead of a guess. Sweep thresholds over a labelled run, print coverage and precision at each, and write the winner back into the preset.
</purpose>

<user-story>
As an operator about to let a sure label trigger an action, I want to know what share of items that bar covers and how often it is right, so that "auto" means a number I chose.
</user-story>

<when-to-use>
- After the first `/jev-route` where Claude or a person labelled the unsure slice
- After rewriting any criteria (the confidence distribution moves)
- Before flipping any label from draft-first to automatic
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/cascade.md (coverage versus precision; the 216-email table)
@frameworks/criteria-writing.md (when no threshold reaches the target, fix the label instead)
</references>

<steps>

<step name="gather_truth" priority="first">
Two files with matching `_id`s: the results of an `ask` or `route` run, and a truth file with the right label per item under the same question key. Best truth: a person's decisions. Second best: Claude's labels from `/jev-route` on the unsure slice plus a sample of the sure slice, stated as such. Truth on only the sure items makes coverage look free; include unsure ones.

<if condition="fewer than 40 truth rows">
Say the sweep will be noisy and the recommendation provisional. Proceed, but do not write the threshold into the preset yet.
</if>
</step>

<step name="sweep">
    python3 <skill-dir>/scripts/jev.py tune --results run.jsonl --truth truth.jsonl --question <q> --target 0.95

It prints overall accuracy, then coverage, precision and auto-wrong count at each threshold from 0.50 to 0.95, and recommends the lowest threshold that meets the precision target. Read the table back.
</step>

<step name="decide">
Ask the user what precision they need for this label to act alone. Dropping spam can live at 90 percent; sending a quote cannot. Re-run with that `--target`. Wait for response.

<if condition="no threshold reaches the target">
The label needs rewriting, not the bar raising. Pull the high-confidence wrong items, read them, and go to `frameworks/criteria-writing.md`. Re-run the batch after the rewrite, then tune again.
</if>
</step>

<step name="write_back" priority="last">
Edit the preset's `thresholds` for that question, bump its `version`, and note the date and the truth size in its `description` or a `tuned` field. Re-run `lint`. Say plainly: a tuned threshold is valid for this preset text and this model pin; either changing means tuning again.
</step>

</steps>

<output>
- The coverage / precision table
- A threshold written into the preset with its provenance
</output>

<acceptance-criteria>
- [ ] Truth included unsure items, not only the sure slice
- [ ] The precision target was the user's choice for this label's consequences
- [ ] A label that could not meet target was sent back to criteria, not hidden by a higher bar
- [ ] The preset records when and on how much data it was tuned
</acceptance-criteria>
