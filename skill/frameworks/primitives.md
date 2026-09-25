<primitives>

## Purpose
Jev answers exactly three kinds of question. Every command in this skill is one of them wrapped in a routing pattern. Know what each one returns before you write a single criterion, because the return shape decides what your code can branch on.

## The Endpoint
```
POST https://openrouter.ai/api/alpha/decisions
Authorization: Bearer $OPENROUTER_API_KEY
{ "model": "typesafe/jev-1.13", "state": { ...your fields... }, "questions": { ...one or more... } }
```
It is outside `/api/v1`. The chat endpoint rejects Jev with HTTP 400 ("is a decisions model"). SDK users set `serverURL` to `https://openrouter.ai`, not the default base URL. Output tokens are free; you pay per input token (about $0.04 per million in September 2026). Context is 32,000 tokens per request.

`state` is a JSON object. Name fields in plain snake_case and refer to them in instructions with backticks: "Read `body`". Every question in one request sees the same state and is answered in parallel.

## Choice: which one of these?
```json
"kind": { "type": "choice", "instructions": "What is the sender after? Judge by the direction money flows.",
          "criteria": { "paid_deal": "...", "vendor_pitch": "...", "non_pitch": "..." } }
```
Returns `choice` (the label), `probabilities` (one per label, sum to 1), `confidence` (how concentrated the distribution is). A confidence of 1.0 with probabilities {a: 1, b: 0} is a clean call. A confidence of 0.33 means the mass is spread; route it to a human or to Claude.

`criteria` is an object. Order does not matter. Labels are snake_case and become the values your code compares against, so keep them stable across versions.

## Noul: does this hold?
```json
"pays": { "type": "noul", "instructions": "Does the sender intend to pay the recipient money, as opposed to selling to them?" }
```
Returns `noul`, a probability of yes from 0 to 1. No criteria. Near 0.5 means "cannot tell", not "medium". Threshold it as a band: below 0.2 is a confident no, above 0.8 a confident yes, the middle is unsure.

Use noul for gates and verifications where each question is one condition that must hold.

## Score: where on this scale?
```json
"heat": { "type": "score", "instructions": "How close is `message` to a buying decision?",
          "criteria": [ "Cold: browsing", "Warm: names a problem", "Hot: names a timeline or budget", "Ready: asks to buy" ] }
```
`criteria` is an ORDERED array; index 0 is the lowest level. Returns `score` (probability-weighted position, e.g. 1.99 sits on level 2), `probabilities` keyed by index, `confidence`, and `legend` echoing your levels. Round the score for a bucket, or threshold the raw value for a ranking.

Sending criteria as an object here returns a 400 ("expected array, received object"). Sending a choice's criteria as an array returns the mirror error.

## Reading a response
```json
{ "answers": { "kind": { "type": "choice", "choice": "paid_deal", "confidence": 0.89, "probabilities": {...} },
               "pays": { "type": "noul", "noul": 0.92 } },
  "usage": { "input_tokens": 432, "output_tokens": 71, "cost": 0.000018 }, "model": "typesafe/jev-1.13-20260917" }
```
`scripts/jev.py` flattens this to `kind`, `kind_conf`, `kind_probs`, `pays` per item, then applies the preset's rules and the sure test. Always read `usage.cost`; a response with no cost is rejected, never counted as free.

## Anti-Patterns
- **Asking Jev to explain.** It cannot. If you need a reason, ask a second noul that names the reason as a condition
- **One giant question.** "Classify this email into one of these 14 buckets" spreads probability thin. Split into two or three orthogonal questions and reconcile with rules
- **Treating 0.5 noul as "medium".** It is "unknown". Route it
- **Trusting `~typesafe/jev-latest` with tuned thresholds.** A new release moves probabilities by hundredths. Pin the dated slug when numbers matter
- **Stuffing the whole document into state.** You pay per input token and the model reads everything. Send the fields the question names, truncated

## Sources
- OpenRouter, "Jev" guide and tutorial (openrouter.ai/docs/guides/community/jev), September 2026
- TypeSafe, System One primitives and confidence docs (docs.typesafe.ai/primitives, docs.typesafe.ai/confidence)
- Live probes against `typesafe/jev-1.13-20260917` on 2026-09-25 for the exact error strings above

</primitives>
