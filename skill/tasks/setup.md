<purpose>
Get one working OpenRouter key into the environment, prove it with a live Decisions call, pin the model, and record the result in `context/install.md`. Two minutes, once.
</purpose>

<user-story>
As a Claude Code user installing claude-x-jev, I want setup to tell me exactly where to get the key and where to put it, and to prove the connection works before I trust any result, so that the first real run is never the first time something fails.
</user-story>

<when-to-use>
- First run after `npx claude-x-jev install`
- `context/install.md` says `status: unconfigured`
- A run failed with "OPENROUTER_API_KEY is not set" or HTTP 401
</when-to-use>

<context>
@context/install.md
</context>

<references>
@checklists/setup-complete.md (before flipping status: configured)
@frameworks/primitives.md (if the user asks what Jev actually is before committing)
</references>

<steps>

<step name="announce" priority="first">
Say what will happen in four lines: get an OpenRouter key, put it in the shell environment, run one live call, pin the model. Say the key is never pasted into this chat and never written into the skill. Then check `python3 --version` (3.8 or newer is required; nothing else is).
</step>

<step name="check_existing">
Run `printenv OPENROUTER_API_KEY | cut -c1-8` in Bash. If it prints `sk-or-v1`, the key is already in place; skip to `verify`. If empty, continue.
</step>

<step name="get_key">
Give these exact instructions and then wait:

1. Sign in at https://openrouter.ai (Google or GitHub login works)
2. Add credits at https://openrouter.ai/settings/credits. Five dollars covers hundreds of thousands of Jev decisions; the same balance also pays for any chat model you route through OpenRouter
3. Create a key at https://openrouter.ai/settings/keys. Name it `claude-x-jev`. No spend limit is needed for Jev, but set one if the key will also serve chat models
4. Put it in the shell so every terminal and Claude Code session sees it:
   - macOS / Linux: append `export OPENROUTER_API_KEY=sk-or-v1-...` to `~/.zshrc` or `~/.bashrc`, then `source` that file
   - Windows: `setx OPENROUTER_API_KEY "sk-or-v1-..."` in PowerShell, then open a new terminal
5. Restart Claude Code so its Bash tool inherits the variable

Wait for the user to say the key is in place. Do not ask them to paste it.
</step>

<step name="verify">
Run:

    python3 <skill-dir>/scripts/jev.py status

Read the five lines back to the user: key present, credits left, model and provider, uptime and latency, and the live call result with its cost. The live call sends the word "ping" and asks one noul question; it costs about a hundredth of a cent.

<if condition="status fails with 401">
The key is wrong or was not exported into this session. Ask them to open a fresh terminal, run `echo $OPENROUTER_API_KEY | cut -c1-8`, and restart Claude Code. Wait for response.
</if>

<if condition="status shows credits under $1">
Say plainly that Jev is cheap but not free, and that a zero balance fails every call with HTTP 402. Suggest topping up before a large run.
</if>
</step>

<step name="optional_mcp">
Offer, do not require, the OpenRouter MCP. It gives `/jev-status` richer data (credits, endpoint uptime, docs search) but it cannot call Jev itself, because the MCP's chat tool uses the chat endpoint and Jev lives on the decisions endpoint. If they want it:

    claude mcp add --transport http openrouter https://mcp.openrouter.ai/mcp --header "Authorization: Bearer $OPENROUTER_API_KEY"

Then restart Claude Code. Record the answer either way.
</step>

<step name="pin_model">
Ask with `AskUserQuestion`: pin `typesafe/jev-1.13` (stable; thresholds you tune stay valid) or track `~typesafe/jev-latest` (newest release; probabilities can shift by hundredths on an update). Recommend the pin. Wait for response.
</step>

<step name="write_install" priority="last">
Update the frontmatter of `context/install.md` with a surgical Edit: `model`, `key_location`, `preset_dir`, `configured_on` (today's date). Run `checklists/setup-complete.md`. Flip `status: configured` last, only after every line passes, and mirror `configured: true` into the `SKILL.md` frontmatter.

Close with the three commands most people want next: `/jev-classify` for a labelled sort, `/jev-route` to pre-sort a queue before Claude works it, `/jev-gate` to put a safety check in front of tool calls.
</step>

</steps>

<output>
- `OPENROUTER_API_KEY` verified live, never written to disk by this skill
- `context/install.md` with `status: configured`, the pinned model, and the date
- `configured: true` in `SKILL.md`
</output>

<acceptance-criteria>
- [ ] `python3` 3.8+ confirmed
- [ ] The key was placed by the user in their shell, never pasted into chat or into any skill file
- [ ] `jev.py status` returned a live answer with a cost
- [ ] Credit balance was read back to the user
- [ ] MCP was offered as optional and its limitation (cannot call Jev) was stated
- [ ] Model choice was made explicitly and recorded
- [ ] `status: configured` flipped last, after the checklist passed
</acceptance-criteria>
