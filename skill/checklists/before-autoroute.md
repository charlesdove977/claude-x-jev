# Checklist: Before Autoroute

Run before any sure label triggers an action with no human look, and before a gate hook is allowed to auto-allow. This is the line between "Jev suggested" and "Jev decided".

## Evidence
- [ ] A shadow batch of at least 50 items ran where the labels were checked by a person or by Claude reading each one
- [ ] `/jev-tune` ran on that batch and the preset carries the tuned threshold with its date and truth size
- [ ] Agreement above the threshold was at least the precision the user named for this label's consequences
- [ ] Agreement below the threshold was clearly worse than above it, so the confidence number is doing its job

## Blast radius
- [ ] The automatic action is reversible, or the label only drops and never sends, deletes, or pays
- [ ] Anything that sends, replies, publishes, or writes to a customer-facing system stays draft-first regardless of confidence
- [ ] The model is pinned to a dated slug, not `~jev-latest`

## Operations
- [ ] Every run writes to a dated folder so a bad batch can be found and reversed
- [ ] A 401 or 402 surfaces in a log someone reads, not as an empty output
- [ ] Someone owns re-tuning when the criteria or the model change
