<purpose>
One command that answers "can I run a batch right now": key present, credits left, model uptime and latency, and a live round-trip with its cost.
</purpose>

<user-story>
As an operator about to run a few thousand decisions, I want a five-line health check so that a dead key or an empty balance surfaces before the batch, not halfway through it.
</user-story>

<when-to-use>
- Before any run over a few hundred items
- After an update, a key rotation, or a long gap
- When the user asks about cost, credits, uptime, or latency
</when-to-use>

<context>
@context/install.md
</context>

<references>
@tasks/setup.md (if status reports the key is missing)
</references>

<steps>

<step name="run" priority="first">
Run `python3 <skill-dir>/scripts/jev.py status`. It prints key, credits, model, uptime, and a live ping.
</step>

<step name="interpret">
Report the five lines. Then add judgment:
- Credits under $1: say a large run may fail with HTTP 402 midway; suggest a top-up first
- Uptime under 99% in the last day, or p50 latency over 1 second: say the provider is degraded and a large batch will be slower and may see retries
- Live call over 2 seconds: the network, not the model; retry once before concluding anything

<if condition="the OpenRouter MCP is attached">
Also call its `list-model-endpoints` for `typesafe/jev-1.13` and report the 30-minute request count, which shows whether the model is under load.
</if>
</step>

<step name="estimate" priority="last">
If the user names a batch size, estimate: items × roughly 400 input tokens × $0.042 per million. State it as "about N cents". Then say how long: items × 0.3 seconds sequential, or items ÷ 8 × 0.4 seconds with the default concurrency.
</step>

</steps>

<output>
- Five status lines, read back with judgment
- A cost and time estimate when a batch size is given
</output>

<acceptance-criteria>
- [ ] Every number reported came from the command output, none invented
- [ ] Low credits and degraded uptime were called out when present
- [ ] Any estimate stated its arithmetic
</acceptance-criteria>
