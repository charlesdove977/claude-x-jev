# Presets

A preset is one JSON file: the questions Jev answers, the criteria for each label, the confidence bars that decide what counts as "sure", and the rules that reconcile answers with each other.

Bundled presets are generic examples. Copy one, rename it, and rewrite the criteria for your own data.

## Where presets are looked up (first match wins)

1. `$JEV_PRESET_DIR`
2. `./.claude/jev-presets/` in the current project
3. `~/.claude/jev-presets/` for the user
4. `presets/user/` inside the installed skill (preserved across `update`)
5. `presets/` inside the installed skill (bundled examples)

Your private presets belong in 2, 3 or 4. Never edit the bundled ones in place; an update overwrites them.

## Schema

```json
{
  "name": "email-triage",
  "description": "one line",
  "model": "typesafe/jev-1.13",
  "state_fields": ["from", "subject", "body"],
  "display_fields": ["from", "subject"],
  "questions": {
    "kind":  { "type": "choice", "instructions": "...", "criteria": { "label": "what makes an item this label", "other": "catch-all" } },
    "pays":  { "type": "noul",   "instructions": "a yes/no statement that names the field it judges" },
    "heat":  { "type": "score",  "instructions": "...", "criteria": ["lowest level", "next level", "highest level"] }
  },
  "thresholds": { "kind": 0.7, "pays": { "low": 0.2, "high": 0.8 } },
  "rules": [
    { "name": "affiliate_is_a_deal", "when": { "money": "affiliate_only" }, "set": { "kind": "paid_deal" } },
    { "name": "high_pay_prob", "when": { "pays": { "gte": 0.85 } }, "set": { "kind": "paid_deal" } }
  ]
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `questions` | yes | Keyed by a short snake_case name. `choice` criteria is an object; `score` criteria is an ORDERED list (index 0 = lowest); `noul` has no criteria. |
| `state_fields` | no | Which item fields are sent to Jev. Default: every field not starting with `_`. Keep it tight; you pay per input token. |
| `display_fields` | no | Item fields copied into the output rows so a human can read them without joining back. |
| `thresholds` | no | Per question. `choice`/`score`: minimum confidence. `noul`: a band; probabilities inside `(low, high)` count as unsure. Default 0.7 and 0.2..0.8. |
| `rules` | no | Run in order after the answers come back. `when` conditions all must hold (`"q": "value"`, or `{"gte": x}`, `{"lte": x}`, `{"equals": v}`). `set` overwrites answers and marks them `_by_rule`. |

## Why rules exist

Jev answers every question in a request in parallel and in isolation. On one email it can say `kind = vendor_pitch`, `money = affiliate_only`, and `pays = 0.92` at the same time. Nothing inside Jev reconciles those. A rule does. Write one for every pair of answers that can contradict.
