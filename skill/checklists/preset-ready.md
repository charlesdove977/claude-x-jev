# Checklist: Preset Ready

Run before the first full run of any new or edited preset. Cheap to pass, expensive to skip.

## Structure
- [ ] `jev.py lint` prints `clean`, or every remaining warning was kept on purpose with a reason
- [ ] Each `choice` question has a catch-all label, or is marked `exhaustive: true` with a reason
- [ ] Each `score` question's criteria is an ordered array, lowest first, each level adding one visible signal
- [ ] Each `noul` instruction is a statement that names its field and can be true or false on the text alone

## Criteria
- [ ] Every label description names something observable in the text; no bare adjectives
- [ ] No label description ends in "etc." or "and so on"
- [ ] No two labels could honestly both apply to one item
- [ ] Instructions name the state fields in backticks

## Reconciliation
- [ ] Every pair of answers that can contradict has a rule
- [ ] Rules were read in order and none undoes an earlier one by accident

## Trial
- [ ] A dry run showed the exact state sent, and nothing private leaves the machine that should not
- [ ] Five items ran and at least four labels looked right to a person
- [ ] The preset lives outside the bundled folder if it was new or edited
