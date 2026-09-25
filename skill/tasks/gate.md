<purpose>
Put a 300-millisecond safety check in front of tool calls. Jev answers two conditions per call, is it reversible and does it serve the task, and the hook approves, denies, or leaves the normal permission prompt in place. Also usable one-off from the command line.
</purpose>

<user-story>
As someone running Claude Code with broad permissions, I want routine commands to pass without a prompt and destructive ones to be stopped or escalated, judged by something faster and cheaper than a second LLM call, so that the prompts I do see are the ones worth seeing.
</user-story>

<when-to-use>
- "Is this safe to run", "gate tool calls", "auto-approve the boring stuff"
- Installing a PreToolUse hook
- Any automation that takes an action on Jev's say-so
</when-to-use>

<context>
@context/install.md
</context>

<references>
@frameworks/cascade.md (gate thresholds: approve at 0.9, block at 0.1, human in between)
@presets/tool-gate.json (the two noul questions)
@hooks/pre-tool-gate.sh (the hook script and its env tunables)
@checklists/before-autoroute.md (before the hook is allowed to auto-allow anything)
</references>

<steps>

<step name="try_it" priority="first">
Show the gate on three canned actions so the user sees the shape of the answers before installing anything:

    python3 <skill-dir>/scripts/jev.py gate --state '{"tool":"Bash","tool_input":"{\"command\":\"pytest tests/\"}","cwd":"/path/to/project","task":"fix the failing date test"}'
    python3 <skill-dir>/scripts/jev.py gate --state '{"tool":"Bash","tool_input":"{\"command\":\"git push --force origin main\"}","cwd":"/path/to/project","task":"fix the failing date test"}'
    python3 <skill-dir>/scripts/jev.py gate --state '{"tool":"Bash","tool_input":"{\"command\":\"npm install left-pad\"}","cwd":"/path/to/project","task":"fix the failing date test"}'

Exit codes: 0 allow, 1 deny, 2 ask. Read back the two probabilities on each. Expect the test run to land near 0.8 to 0.95, the force push near zero, and the unrelated install to be low on `serves_task`. Explain that the numbers move by a few hundredths between runs; they are probabilities, not constants.
</step>

<step name="choose_mode">
Ask with `AskUserQuestion`: (a) one-off checks only, no hook; (b) install the hook in **shadow mode** first (nothing auto-allowed, denies still stop, everything else prompts as usual); (c) install the hook live with approve at 0.9. Recommend (b) for the first few days. Wait for response.
</step>

<step name="install_hook">
Show the settings block before writing it. For the user scope, edit `~/.claude/settings.json` (project scope: `.claude/settings.json`) and merge, never overwrite:

    "hooks": {
      "PreToolUse": [
        { "matcher": "Bash",
          "hooks": [ { "type": "command", "command": "bash ~/.claude/skills/claude-x-jev/hooks/pre-tool-gate.sh" } ] }
      ]
    }

Shadow mode is `JEV_GATE_APPROVE=1.01` in the environment (nothing can reach 1.01, so nothing is auto-allowed; denies at or below `JEV_GATE_BLOCK` still fire). Set `JEV_GATE_TASK` to one line about the current job when possible; it sharpens `serves_task`. Gate more tools with `JEV_GATE_TOOLS=Bash,Write,Edit`.

Wait for the user to confirm the edit. Then restart Claude Code and run one harmless command to see the hook fire. The hook logs every decision to `$TMPDIR/jev-gate.log`.

Record `hook_installed: true` in `context/install.md`.
</step>

<step name="go_live" priority="last">
After a few days in shadow mode, read the log together: how many would have been allowed at 0.9, and were any of those wrong. Run `checklists/before-autoroute.md`. Only then drop `JEV_GATE_APPROVE` to 0.9.

Say the safety property out loud: on any error (no key, no network, bad JSON) the hook prints nothing and exits 0, which leaves Claude Code's own permission prompt exactly as it was. The gate can fail closed to a human; it can never fail open.
</step>

</steps>

<output>
- Three example decisions with their probabilities
- A hook entry in the chosen settings file, in shadow or live mode
- `hook_installed: true` in `context/install.md`
</output>

<acceptance-criteria>
- [ ] The three canned actions were run and their numbers read back
- [ ] The settings block was shown before it was written, and merged rather than overwritten
- [ ] Shadow mode was offered and recommended first
- [ ] The fail-closed property was stated
- [ ] Going live required the before-autoroute checklist
</acceptance-criteria>
