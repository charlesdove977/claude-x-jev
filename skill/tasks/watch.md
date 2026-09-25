<purpose>
Run a preset on a schedule with no Claude session open. A small runner script pulls new items, calls `jev.py route`, and drops the sure and unsure files where the next step picks them up. Jev's real edge over a chat model is that it does not need anyone at the keyboard.
</purpose>

<user-story>
As an operator, I want new emails, leads, or comments sorted the moment they arrive, so that when I or Claude open the queue it is already split into act, read, and drop.
</user-story>

<when-to-use>
- "Run this every hour", "keep the inbox sorted", "on cron"
- Handing the sorting step to n8n, launchd, cron, or a CI job
- Any preset that has passed `/jev-tune` and `checklists/before-autoroute.md`
</when-to-use>

<context>
@context/install.md
</context>

<references>
@checklists/before-autoroute.md (nothing scheduled acts on a label until this passed)
@frameworks/cascade.md
</references>

<steps>

<step name="fetch_step" priority="first">
Ask how new items arrive: a script that writes a JSON file, an API pull, a folder, an n8n node. The watcher needs one command that produces `items.json` for the window since the last run. Write that command with the user; Jev does not fetch. Wait for response.
</step>

<step name="runner">
Write a runner (bash or Python, the user's choice) to a path outside the skill, for example `~/jev-jobs/<name>/run.sh`:

    #!/usr/bin/env bash
    set -euo pipefail
    cd "$(dirname "$0")"
    source ~/.zshrc 2>/dev/null || true          # or wherever OPENROUTER_API_KEY lives
    <fetch command> > items.json
    python3 ~/.claude/skills/claude-x-jev/scripts/jev.py route --preset <p> --input items.json --out "runs/$(date +%Y%m%d-%H%M)"
    # next step: act on runs/*.sure.jsonl, queue runs/*.unsure.items.jsonl for Claude or a person

Explain each line. The runner keeps a dated output per run so nothing is overwritten.
</step>

<step name="schedule">
Offer the three common schedulers and write the one they pick:
- cron: `0 * * * * /bin/bash ~/jev-jobs/<name>/run.sh >> ~/jev-jobs/<name>/cron.log 2>&1`
- launchd (macOS): a plist under `~/Library/LaunchAgents/` with `StartInterval` 3600 and `EnvironmentVariables` carrying the key
- n8n: a Schedule Trigger into an Execute Command node running the same runner, then a Read Binary File node on the sure and unsure outputs

Environment is the usual failure: cron does not read `.zshrc`. Put the key in the runner's environment explicitly or source the file.
</step>

<step name="first_run_and_handoff" priority="last">
Run the runner by hand once and read the summary line from its log. Confirm the dated output folder exists with the three files. Then say what consumes each: sure files feed the action step, unsure items feed `/jev-route`'s Claude pass or a person, and the log is where a 402 or a 401 will show up.
</step>

</steps>

<output>
- A runner script outside the skill, with the fetch step and the route call
- A scheduler entry (cron, launchd, or n8n) that runs it
- One manual run verified with its output folder
</output>

<acceptance-criteria>
- [ ] The preset passed `checklists/before-autoroute.md` before anything was scheduled
- [ ] The key is available to the scheduler's environment, not assumed from a shell profile
- [ ] Each run writes to a dated folder
- [ ] The manual first run was verified from its log and files, not assumed
</acceptance-criteria>
