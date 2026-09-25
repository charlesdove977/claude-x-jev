# Bench Report Template

Use after `/jev-bench`. Agreement is not accuracy; the disagreement reading is the report.

## File Template

```markdown
## Jev vs {second-judge} · {preset-name} · {item-count} items · {date}

| | Jev {model-version} | {second-judge} |
| --- | --- | --- |
| Per item | {jev-latency}s | {other-latency}s |
| Whole sample | {jev-wall}s | {other-wall}s |
| Cost | ${jev-cost} | ${other-cost} |

| Question | Agreement |
| --- | --- |
| `{question-key}` | {agree}/{n} ({pct}%) |

**By Jev confidence on `{question-key}`:**
- ≥ {threshold}: {n-hi} items, {pct-hi}% agreement
- < {threshold}: {n-lo} items, {pct-lo}% agreement

**Disagreements ({dis-count}), read by hand:**

| Class | Count | Example |
| --- | --- | --- |
| Harmless (same action either way) | {n} | [subject or id] |
| Definition bug (criteria text decided it) | {n} | [subject or id] |
| Jev right | {n} | [subject or id] |
| {second-judge} right | {n} | [subject or id] |
| Unclear | {n} | [subject or id] |

**Recommendation:** [Which side of the line this step belongs on, and the one preset change to make first]
```

## Field Documentation

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| cost/time table | table | yes | From both runs' summaries; state how the second judge was timed |
| agreement table | table | yes | From `jev.py bench` output |
| confidence split | two lines | yes | Computed from the results file; this is the routing evidence |
| disagreement table | table | yes | Every disagreement classified; counts must sum to the total |
| recommendation | one line | yes | Names a preset fix or a division of labor, not only a verdict |

## Section Specifications

### Confidence split
Compute agreement separately for items at or above the preset threshold and below it. If the high side is not clearly better than the low side, the confidence number is not doing its job on this preset and routing on it is not yet safe.

### Disagreement classes
"Harmless" means both labels lead to the same downstream action. "Definition bug" means the criteria text, read literally, supports Jev's answer even though the user wanted the other one; the fix is the text, not the model.
