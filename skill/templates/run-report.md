# Run Report Template

Use after any `ask`, `route`, `match`, or `verify` run. Short, numbers first, file paths last. Every number comes from the script's summary line or the results file, never from memory.

## File Template

```markdown
## {preset-name} · {item-count} items · {date}

**Summary:** {item-count} items · {wall-seconds}s wall · {mean-latency}s per item · ${cost} · {error-count} errors

| Label | Count | Sure | Unsure |
| --- | --- | --- | --- |
| {label} | {n} | {n-sure} | {n-unsure} |
| … | | | |

**Sure line:** confidence ≥ {threshold} on `{question-key}`. {sure-count} items ({sure-pct}%) cleared it.

**Unsure ({unsure-count}):** [one line on what these tend to be, from reading three of them]

**Rules fired:** {rule-name} × {n}, … (or None)

**Files:** `{results-path}` [and the sure / unsure paths for a route run]

**Next:** [one of: /jev-route to hand the unsure slice to Claude · /jev-tune once N are checked by hand · /jev-watch to schedule it · fix label {label} first, it carried most of the unsure]
```

## Field Documentation

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| `summary` line | text | yes | Verbatim from the script's stderr summary |
| label table | table | yes | Counts from the results file; a row per label per choice question |
| sure line | text | yes | The threshold actually used, and the share that cleared it |
| unsure note | prose | yes | Read three unsure items and say what they have in common |
| rules fired | list | yes | From the `_rules` column; "None" if empty |
| files | paths | yes | Absolute or project-relative, so the user can open them |
| next | one line | yes | One action, not a menu |

## Section Specifications

### Label table
For a `noul`-only run, replace with three rows: confident yes, confident no, unsure. For a `score` run, one row per rounded level, highest first.

### Unsure note
This is the part a person reads. Say what the unsure items look like in one sentence, so the user knows whether to tune, rewrite a label, or just read them.
