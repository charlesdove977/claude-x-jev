<criteria-writing>

## Purpose
With a decision model, the criteria text IS the model. There is no system prompt, no examples, no reasoning step to rescue a sloppy label. Every miss in the 216-email benchmark that was Jev's "fault" traced back to a definition: `brand_deal` was written as "wants to PAY", so affiliate-only offers correctly fell into `vendor_pitch`, and eight real deals would have been dropped. Claude papered over the same sloppy definition with outside knowledge; Jev did exactly what it was told.

## The Rules
Each one is a `lint` check in `scripts/jev.py`, so a preset that passes lint has at least met the floor.

### 1. One axis per question
A question sorts along one dimension. "Who wants what" is one axis. "How much money" is another. "Which deliverable" is a third. Three small questions beat one twelve-label monster, and the rules layer reconciles them afterwards.

### 2. Every label names an observable cue
Weak: `vendor_pitch: "Someone trying to sell something."`
Strong: `vendor_pitch: "Sender wants the recipient to buy or pay for a service or tool, or to give up time for a sales call. Money would flow OUT of the recipient."`
The strong version tells Jev what to look for in the text. "Direction of money" is a cue. "Seems salesy" is not.

### 3. Labels are mutually exclusive
If an item can honestly be two labels, split the question or merge the labels. The affiliate case above was a label-boundary bug: affiliate offers sit between "pays you" and "sells to you". The fix was to write into `paid_deal` that affiliate-only offers count, and to add a rule for belt and braces.

### 4. There is somewhere for everything to go
Add a catch-all (`other`, `not_applicable`, `non_pitch`) unless the label set truly covers every input, in which case mark the question `"exhaustive": true`. Without one, an item that fits nothing gets forced into the least-wrong bucket at low confidence, and low confidence is expensive to review.

### 5. Name the field
"Read `body` and `subject`" beats "read the email". Jev references state fields by name; naming them in the instruction anchors the judgment to the right text.

### 6. Noul reads as a statement that can be true
"Does the sender intend to pay the recipient money, as opposed to selling to them?" is checkable. "Is this a good lead?" is not.

### 7. Score levels are ordered and adjacent levels differ by one visible thing
Cold / Warm / Hot / Ready works because each step adds one concrete signal (a named problem, then a timeline or budget, then an ask to buy). Levels that differ by vibe produce scores that hover in the middle.

### 8. Write the reconcile rule at the same time
Two questions that can contradict each other need a rule in the preset the day they are written, not after the first bad batch. "If `money` = affiliate_only then `kind` = paid_deal" took one line and fixed 8 of 28 disagreements.

## Rewriting a label that misbehaves
1. Pull ten items Jev got wrong at high confidence. High-confidence misses are definition bugs; low-confidence misses are ambiguity
2. Read them. Write down the cue a human used to get it right
3. Put that cue into the label text, as an observable, not an adjective
4. Re-run those ten and ten it got right. Both sets must hold
5. Bump the preset version and re-tune the threshold, because rewritten criteria move the confidence distribution

## Anti-Patterns
- **Adjectives as criteria.** "Low quality", "spammy", "legit". Replace each with what you would point at in the text
- **Etc.** Any list ending in "etc." or "and so on" is an unfinished label. Finish it or cut it
- **Copying the label name into its description.** `question: "A question."` gives Jev nothing
- **Fixing a miss by adding a fourteenth label.** Usually the existing labels overlap. Fix the boundary instead
- **Tuning the threshold to hide a bad label.** A threshold trades coverage for precision; it cannot fix a definition that sends items to the wrong bucket confidently

## Sources
- TypeSafe, "How to build with System One" (docs.typesafe.ai/concepts/how-to-build-with-system-one)
- The 216-email Jev vs Claude benchmark, 2026-09-25 (see frameworks/jev-vs-claude.md for the numbers)

</criteria-writing>
