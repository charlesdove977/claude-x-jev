<jev-vs-claude>

## Purpose
Know which side of the line a job belongs on. Both models were given the same 216 emails, the same four questions, the same label text. This is what came back, and what it means for where each one should work.

## The Benchmark (2026-09-25)
216 unanswered inbound emails to a creator's business inbox, 45 days, pulled by the Gmail API. Four questions per email: pitch type (choice), money step (choice), deliverable lane (choice), will-they-pay (noul). Bodies cut at 2,500 characters for both.

| | Jev 1.13 | Claude Opus 5.5 |
| --- | --- | --- |
| Per email | 0.30 s (p50 0.29, max 0.92) | 1.3 s amortized in batches of 24 |
| All 216 | 65 s single file, ~6 s parallel | 37 s in 9 parallel batches, 4 min 46 s sequential |
| Cost | $0.0116 | $4.73 |
| Tokens | 277k in, 0 out | 625k in, 24k out |
| Agreement, pitch type | 87.0% (188/216) | |
| Agreement, money step | 88.0% (190/216) | |
| Agreement, lane | 93.5% (202/216) | |

The 28 pitch-type disagreements, read by hand:

| Class | Count | Verdict |
| --- | --- | --- |
| Newsletter vs sales blast | 13 | Harmless. Both labels drop the email |
| Affiliate-only offers | 8 | Claude followed the playbook; Jev followed the label text literally. Definition bug, fixed by one rule |
| Calendar invite, debate invite, "let's hop on a call", automated drip | 4 | Jev right. Claude saw deals that were not there |
| Marketplace blast and junk | 3 | Unclear either way |

## Where Jev is better
- **Speed and cost.** 400x cheaper, 4x faster per item, and it parallelizes to seconds
- **Consistency.** Same input, same answer. Claude can change its mind between runs
- **Calibrated confidence.** A real probability on every answer. Above 0.7 it matched Claude 95.5 percent; below, 47 percent, and it told us which was which
- **Runs anywhere.** A cron job, an n8n node, a hook. No session, no context window, no usage limit
- **Cannot hallucinate prose.** It has no prose to hallucinate with

## Where Claude is better
- **Writing.** Every draft, reply, summary, and explanation
- **Filling gaps in the label set.** Claude used playbook knowledge it was never given; Jev used the words it was given. This is a strength until the gap is one you did not want filled
- **Cross-question reasoning.** One email got `vendor_pitch` + `affiliate_only` + `pays 0.92` from Jev. Claude reconciled that in its head; Jev needs a rule
- **Memory and context.** Claude can know that the same brand arrived through five agencies, or that a rate was quoted last month. Jev sees one request
- **Applying a playbook.** Relationship holds, rate cards, tone. Jev cannot read a policy document and act on it; it can only check one condition at a time

## Where Claude is worse
- It over-reads. A debate-club invite became "brand deal, budget stated." A calendar notification became "peer collab"
- It costs a session. Reading 216 emails to label them leaves less room for the drafts that actually needed the reading

## The Division
Jev sorts, checks, scores, gates, verifies. Claude reads the unsure slice, writes every draft, holds the context. A person approves what ships. Do not move a job across the line because one side "could probably do it"; move it because the measurement says so.

## Anti-Patterns
- **Benchmarking on agreement alone.** Agreement is not accuracy. Read the disagreements; the 13 harmless ones were half the gap
- **Letting Claude be the ground truth.** It was wrong on at least 4 of 28. Use human labels for tuning where you can
- **Comparing sequential Jev to parallel Claude.** Run both the way you would run them in production, then compare

## Sources
- Full run data, 216 rows with both models' labels: the `jev-vs-claude` report folder in the author's workspace, 2026-09-25. Reproduce with `/jev-bench` on your own inbox
- OpenRouter, "Jev" model page and documentation hub (openrouter.ai/typesafe/jev-1.13)

</jev-vs-claude>
