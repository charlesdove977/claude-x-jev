<cascade>

## Purpose
A threshold is the whole product. Jev's value is not that it is right 90 percent of the time; it is that it tells you which 80 percent it is right 95 percent of the time on, so a person or a Claude session only reads the rest. This framework is how to set that line and what to run on each side of it.

## The Pattern
```
items ──► Jev (all of them, parallel, seconds, cents)
             │
             ├── sure    (confidence ≥ T, or noul outside the band) ──► act on the label
             │
             └── unsure  (everything else) ──────────────────────────► Claude reads it
                                                                        │
                                                                        └── still unclear ──► human
```
`scripts/jev.py route` writes the two halves to `<out>.sure.jsonl` and `<out>.unsure.jsonl`, plus `<out>.unsure.items.jsonl` carrying the full text so Claude can read the unsure slice without a second fetch.

## What the numbers looked like
216 unanswered inbound emails, one `choice` question on pitch type, Claude Opus as the comparison:

| Jev confidence | Share of inbox | Agreement with Claude |
| --- | --- | --- |
| ≥ 0.9 | 66% | 95.8% |
| ≥ 0.7 | 82% | 95.5% |
| < 0.7 | 18% | 47.4% |

The line at 0.7 gave up nothing in precision versus 0.9 and covered 16 more points of the inbox. That is what `tune` finds for you: the lowest threshold that still meets your precision target.

## Three thresholds, three jobs
- **Route** (`choice` / `score`): confidence ≥ T means act on the label. Start at 0.7. Tune from a labelled run
- **Gate** (`noul`): two numbers. Approve at ≥ 0.9, block at ≤ 0.1, everything between goes to the human. Keep them far apart on purpose so the human only sees the genuinely ambiguous
- **Verify** (`choice` + `noul`): a draft ships only when `grounded = supported` at ≥ 0.8 AND every rule check ≥ 0.9. One failed check is a bounce, not an average

## Reconcile before you threshold
Jev answers each question in a request independently. Rules in the preset run first, then the sure test. A rule-set answer is exempt from the confidence test for that question (it is marked `_by_rule`), because the rule is your judgment, not Jev's.

## Cost of the cascade
Jev on everything plus Claude on the unsure slice: about $0.85 for the 216-email run versus $4.73 for Claude on everything. Time: seconds for Jev plus one Claude pass over 38 items instead of nine passes over 216. The bigger win is context: Claude's session holds 38 emails, not 216.

## Anti-Patterns
- **Averaging checks in a gate.** Three checks at 0.95, 0.95, 0.05 average to 0.65 and look fine. The third one was a hard no
- **One threshold for every question.** A routing question and an informational question need different bars. Set a threshold of 0 on questions that should never block `_sure`
- **Tuning on the items Jev was sure about.** You need the truth for the unsure ones too, or coverage looks free
- **Letting `~jev-latest` move under a tuned threshold.** Pin the dated slug
- **Auto-acting on a sure label the first day.** Run `route` in shadow mode for a batch: act by hand, compare, then flip

## Sources
- OpenRouter cookbook, "Gate tool calls with Jev" and "Jev-verified cascade" (September 2026)
- The 216-email benchmark, 2026-09-25 (frameworks/jev-vs-claude.md)

</cascade>
