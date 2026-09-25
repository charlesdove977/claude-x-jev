# Preset Template

Use when creating a new question set. Save the result outside the bundled folder: `~/.claude/jev-presets/{preset-name}.json` for the user, or `.claude/jev-presets/` in a project. Run `jev.py lint --preset <path>` before the first run.

## File Template

```json
{
  "name": "{preset-name}",
  "version": 1,
  "description": "[One line: what items this sorts and what the answers are used for]",
  "model": "typesafe/jev-1.13",
  "state_fields": ["{field-1}", "{field-2}"],
  "display_fields": ["{field-1}"],
  "questions": {
    "{question-key}": {
      "type": "choice",
      "instructions": "[What to judge, naming the fields in backticks, and the one cue that separates the labels]",
      "criteria": {
        "{label-a}": "[Observable cue that makes an item this label]",
        "{label-b}": "[Observable cue that makes an item this label]",
        "other": "[What lands here: anything the labels above do not describe]"
      }
    },
    "{condition-key}": {
      "type": "noul",
      "instructions": "[A statement that names its field and can be true or false on the text alone]"
    },
    "{scale-key}": {
      "type": "score",
      "instructions": "[Where does the item fall, lowest to highest, on this scale]",
      "criteria": [
        "[Lowest level and its signal]",
        "[Next level and the one signal it adds]",
        "[Highest level and its signal]"
      ]
    }
  },
  "thresholds": {
    "{question-key}": 0.7,
    "{condition-key}": { "low": 0.2, "high": 0.8 },
    "{scale-key}": 0.7
  },
  "rules": [
    { "name": "{rule-name}", "when": { "{condition-key}": { "gte": 0.85 } }, "set": { "{question-key}": "{label-a}" } }
  ]
}
```

## Field Documentation

| Field | Type | Required | Purpose | Example |
| --- | --- | --- | --- | --- |
| `name` | string | yes | Preset id; matches the filename | `email-triage` |
| `version` | integer | no | Bump when criteria change, so tuned thresholds are known-stale | `2` |
| `description` | string | yes | One line for `jev.py presets` | `Sort inbound email by who wants what` |
| `model` | string | no | Slug sent on every call; pin the dated release when thresholds matter | `typesafe/jev-1.13` |
| `state_fields` | array | no | Item fields sent to Jev; default is every non-underscore field | `["from","subject","body"]` |
| `display_fields` | array | no | Item fields copied into output rows for humans | `["from","subject"]` |
| `questions` | object | yes | One entry per question; keys are snake_case and become output columns | see template |
| `thresholds` | object | no | Per question. Number for choice/score confidence; `{low, high}` band for noul; `0` makes a question informational | `{"kind": 0.7}` |
| `rules` | array | no | Reconcile answers in order; `when` all must hold, `set` overwrites | see template |

## Section Specifications

### questions.{key}.type
`choice` (criteria is an object), `noul` (no criteria), or `score` (criteria is an ORDERED array, index 0 lowest). Any other shape returns HTTP 400 from the API and an ERROR from lint.

### questions.{key}.instructions
Plain sentence. Name the state fields in backticks. Say the cue that separates the labels. Under 15 characters trips a lint warning.

### questions.{key}.criteria
Every label description names something observable in the text. No adjectives, no "etc.". Include a catch-all or set `"exhaustive": true` on the question.

### thresholds
The bar for `_sure`. Start at 0.7 and the 0.2 to 0.8 band; replace with `/jev-tune` output once there is labelled data. A threshold of 0 removes that question from the sure test.

### rules
Write one for every pair of answers that can contradict. Jev never reconciles its own answers. Conditions: `"q": "value"`, `{"gte": n}`, `{"lte": n}`, `{"equals": v}`. A rule-set answer is marked `_by_rule` and skips the confidence test.
