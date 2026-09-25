<p align="center">
  <img src="https://raw.githubusercontent.com/charlesdove977/claude-x-jev/main/docs/hero-claude-x-jev-16x9.png" alt="Claude x Jev" width="720">
</p>

# Claude x Jev

> **Jev sorts. Claude writes.** Jev is a tiny AI that makes one decision at a time, in a third of a second, for a fraction of a cent, and tells you how sure it is. Claude reads, thinks, and writes. This free [Claude Code](https://claude.ai/code) skill puts the two together so Claude only reads what needs a real brain.

<p>
  <a href="https://start.ccstrategic.io/skool"><img src="https://img.shields.io/badge/Free_Skool_Community-Join_C%26C_Strategic-D97757?style=for-the-badge" alt="Join the free Skool community"></a>
  <a href="https://www.charlieautomates.com/"><img src="https://img.shields.io/badge/charlieautomates.com-Find_Your_Bottleneck-1C1B18?style=for-the-badge" alt="charlieautomates.com"></a>
</p>
<p>
  <a href="https://www.npmjs.com/package/claude-x-jev"><img src="https://img.shields.io/npm/v/claude-x-jev?color=D97757&label=npm" alt="npm version"></a>
  <a href="https://www.npmjs.com/package/claude-x-jev"><img src="https://img.shields.io/npm/dt/claude-x-jev?color=D97757&label=downloads" alt="npm downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/npm/l/claude-x-jev?color=green" alt="MIT license"></a>
  <a href="https://github.com/charlesdove977/claude-x-jev/stargazers"><img src="https://img.shields.io/github/stars/charlesdove977/claude-x-jev?style=flat" alt="stars"></a>
</p>

**Community:** [start.ccstrategic.io/skool](https://start.ccstrategic.io/skool) (free) · **Site:** [charlieautomates.com](https://www.charlieautomates.com/) · **YouTube:** [@charlieautomates](https://youtube.com/@charlieautomates)

---

## Install

```bash
npx claude-x-jev install --with-commands
```

Restart Claude Code, then:

```
/jev-setup        once: one OpenRouter key, one live test call
/jev-classify     sort anything
/jev-route        Jev pre-sorts, Claude reads only the unsure ones
/jev-gate         a 0.3 second safety check in front of tool calls
```

You need `python3` (3.8 or newer) and an [OpenRouter](https://openrouter.ai) API key. Nothing else. Five dollars of credit covers hundreds of thousands of decisions.

---

## What Jev is, in plain words

[Jev](https://openrouter.ai/typesafe/jev-1.13) is made by [TypeSafe](https://typesafe.ai) and lives on OpenRouter. It is not a chat model. You do not prompt it and read a paragraph back.

You hand it a piece of text and a fixed set of choices. It hands back a pick, a probability for every choice, and a confidence number. It answers three kinds of questions:

| Question type | You ask | You get back |
| --- | --- | --- |
| `choice` | Which one of these? | the label, a probability per label, a confidence |
| `noul` | Is this true? | a number from 0 to 1 |
| `score` | Where on this scale? | a position, a probability per level, a confidence |

That is the whole model. It answers in about a third of a second. Input costs about 4 cents per million tokens. Output is free. Same input, same answer, every time. It cannot write a sentence. It cannot explain itself. It can tell you, on every answer, how sure it is.

---

## What Jev does better than Claude

I gave both models the same 216 real emails from my inbox, the same four questions, and the same label definitions.

| | Jev 1.13 | Claude Opus 5.5 |
| --- | --- | --- |
| Per email | **0.3 s** | 1.3 s (24 at a time) |
| All 216 | **65 s one at a time, about 6 s in parallel** | 37 s in 9 parallel batches, 4 min 46 s one after another |
| Cost | **$0.01** | $4.73 |
| Same answer twice | **Always** | Usually |
| Says how sure it is | **Every answer** | Only if asked |
| Runs outside Claude Code | **Yes: cron, n8n, a hook, a script** | Needs a session |

They agreed on 87 to 94 percent of the labels. The number that matters more:

**When Jev said it was at least 70 percent sure (82 percent of the inbox), it matched Claude 95.5 percent of the time. When it was less sure, only 47 percent. And it told us which ones were which.**

- **400 times cheaper.** And it never touches your Claude usage window or your context.
- **No drift.** Same answer every run.
- **A real confidence number.** That number is your routing switch.
- **It cannot make things up.** It has no words to make them up with. On four of the 28 disagreements Claude saw deals that were not there. A debate-club invite became "brand deal, budget stated." Jev did not fall for it.

## What Claude does better

- **Writing.** Every draft, reply, summary, and explanation. Jev returns zero words.
- **Filling gaps in your labels.** Claude used knowledge it was never given. Jev used exactly the words it was given. Eight of the 28 disagreements were affiliate offers that my label text technically excluded. Claude was right. The fix was one sentence in the label.
- **Connecting answers.** Jev answers each question alone. One email came back as `vendor_pitch` and `affiliate_only` and `92% likely to pay` at the same time. Claude sorts that out in its head. This skill sorts it out with a `rules` block in the preset.
- **Memory.** Claude can know the same brand came in through five agencies, or that you quoted a price last month. Jev sees one request.
- **Following a playbook.** Rate cards, tone rules, relationship holds. Jev checks one condition at a time. It cannot read a policy and act on it.

**The split:** Jev sorts, checks, scores, gates, and verifies. Claude reads the unsure slice and writes everything. A person approves what ships.

---

## The 13 commands

| Command | What it does | Question type |
| --- | --- | --- |
| `/jev-setup` | Key in place, one live call verified, model pinned | |
| `/jev-status` | Credits, uptime, latency, and a cost estimate for a batch | |
| `/jev-classify` | Pick-one labels over many items, with confidence | `choice` |
| `/jev-check` | Yes or no over many items | `noul` |
| `/jev-score` | Rank items on a scale you define | `score` |
| `/jev-route` | Jev labels everything; sure items act by label, unsure items go to Claude with full text | `choice` + threshold |
| `/jev-verify` | Check Claude's drafts against the thread and your rules before sending | `choice` + `noul` |
| `/jev-gate` | Approve, block, or escalate a tool call; installs as a PreToolUse hook | `noul` |
| `/jev-match` | Are these two threads the same company? Collapse duplicates | `noul` |
| `/jev-tune` | Pick the confidence threshold from items a person checked | |
| `/jev-lint` | Catch vague labels, missing catch-alls, and contradicting answers before you spend | |
| `/jev-bench` | Jev vs Claude on your own data: agreement, cost, time, disagreements | |
| `/jev-watch` | Run a preset on cron, launchd, or n8n with nobody at the keyboard | |

Every command goes through one file, `skill/scripts/jev.py`. No dependencies. You can call it straight from a terminal too:

```bash
python3 ~/.claude/skills/claude-x-jev/scripts/jev.py status
python3 ~/.claude/skills/claude-x-jev/scripts/jev.py ask   --preset email-triage --input inbox.json --out labels.jsonl
python3 ~/.claude/skills/claude-x-jev/scripts/jev.py route --preset email-triage --input inbox.json --out sorted
python3 ~/.claude/skills/claude-x-jev/scripts/jev.py gate  --state '{"tool":"Bash","tool_input":"{\"command\":\"git push --force\"}","cwd":"/app","task":"fix tests"}'
python3 ~/.claude/skills/claude-x-jev/scripts/jev.py tune  --results labels.jsonl --truth checked.jsonl --question kind
```

---

## How to use it

### 1. Set up (two minutes)
Run `/jev-setup`. It tells you where to get the key (openrouter.ai, then Settings, then Keys), where to put it (`export OPENROUTER_API_KEY=...` in your shell profile), and proves it with one live call that costs a hundredth of a cent. The key is never pasted into chat and never written into the skill.

### 2. Sort something
Run `/jev-classify`. Pick a bundled preset or describe your labels and it writes one. It lints the preset, dry-runs one item so you see exactly what leaves your machine, runs five so you can check them, then runs the batch. You get a JSONL or CSV file with a label, a confidence, and the probabilities for every item, plus one summary line: items, seconds, cost.

### 3. Put Jev in front of Claude
Run `/jev-route`. Same run, but the output is split: `sorted.sure.jsonl` (act on these by label) and `sorted.unsure.items.jsonl` (Claude reads only these, with their full text). On my inbox that meant Claude read 38 emails instead of 216, for about 85 cents instead of $4.73.

### 4. Check Claude's work
Run `/jev-verify`. One item per draft: the thread it answers, your rules, the draft. Jev returns `supported`, `unsupported`, or `declined`, plus rule and tone checks. One failed check bounces the draft back to Claude. Nothing sends.

### 5. Gate tool calls
Run `/jev-gate`. Two questions per call: can this be undone, and does it serve the task. Start in shadow mode (nothing is auto-allowed, dangerous things are still denied), read the log for a few days, then go live at 0.9. If anything errors, the hook prints nothing and exits 0, so Claude Code's own permission prompt shows as usual. It can fail closed to a human. It can never fail open.

```bash
npx claude-x-jev hook --write      # merges the PreToolUse entry into ~/.claude/settings.json, backup kept
export JEV_GATE_APPROVE=1.01       # shadow mode: nothing can reach 1.01, so nothing auto-allows
```

### 6. Tune, then automate
`/jev-tune` sweeps thresholds against items a person checked and prints coverage and precision at each one. `/jev-watch` writes a runner for cron, launchd, or n8n so the sorting happens with nobody at the keyboard.

---

## Presets

A preset is one JSON file: the questions, what each label means, the confidence bars, and the rules that connect answers to each other. Six generic ones ship in `skill/presets/`:

| Preset | Sorts | Questions |
| --- | --- | --- |
| `email-triage` | Inbound email | paid deal / vendor pitch / peer collab / non-pitch · money step · will they pay |
| `comment-triage` | Social comments | question / keyword drop / praise / critique / spam · needs reply · reply value 0 to 3 |
| `lead-qualify` | Form and DM leads | real business · decision maker · heat cold to ready · what they want |
| `draft-verify` | Generated replies | grounded / unsupported / declined · follows rules · tone ok |
| `tool-gate` | Agent tool calls | reversible · serves task |
| `match-entity` | Pairs of threads | same entity · same ask |

They are examples. Copy one to `~/.claude/jev-presets/`, rewrite the labels for your data, run `/jev-lint`. Updates overwrite the bundled folder and never touch yours.

**The label text is the model.** There is no system prompt to rescue a vague label. `frameworks/criteria-writing.md` has the eight rules. `/jev-lint` enforces the floor.

---

## Inside the skill

```
skill/
├── SKILL.md              entry point, 13 commands
├── scripts/jev.py        the one Decisions API caller: ask, route, gate, match, tune, lint, bench, status
├── presets/              6 generic question packs + schema README; presets/user/ is yours and survives updates
├── hooks/pre-tool-gate.sh  PreToolUse hook, fails closed
├── tasks/                one file per command
├── frameworks/           primitives · criteria-writing · cascade · jev-vs-claude (the benchmark)
├── templates/            preset · run-report · bench-report
├── checklists/           setup-complete · preset-ready · before-autoroute
└── context/install.md    the only file setup writes: status, model pin, key location (never the key)
```

---

## One thing to know

Jev lives at `POST https://openrouter.ai/api/alpha/decisions`, outside the `/api/v1` path. Send it to the chat endpoint (including through the OpenRouter MCP's chat tool) and you get HTTP 400: *"is a decisions model and cannot be used with the chat/completions endpoint."* This skill never does that. The MCP is still handy for credits, uptime, and docs, and `/jev-setup` offers it as optional.

---

## Build your own skill like this

This skill was scaffolded with **SkillSmith** and then filled in by hand. SkillSmith is a Claude Code plugin that turns a workflow into a proper skill folder (entry point, tasks, frameworks, templates, checklists) in minutes. If you want to package your own workflow the same way:

- [SkillSmith on GitHub](https://github.com/ChristopherKahler/skillsmith), the plugin itself
- [SkillSmith walkthrough](https://www.charlieautomates.com/free-resources/#skillsmith), how I use it
- [EZ Thumb](https://github.com/charlesdove977/ez-thumb), another skill built the same way, with the same installer pattern
- [BASE](https://github.com/ChristopherKahler/base), the knowledge graph where the rules behind these presets live

## Resources

- [Jev on OpenRouter](https://openrouter.ai/typesafe/jev-1.13), the model page with pricing and uptime
- [OpenRouter's Jev guide and cookbooks](https://openrouter.ai/docs/guides/community/jev): classification, verified cascade, tool-call gating, auto-approving permission prompts
- [TypeSafe docs: the three question types](https://docs.typesafe.ai/primitives) and [reading confidence](https://docs.typesafe.ai/confidence)
- [Jev AI: cheap first-pass sorting before Claude](https://www.charlieautomates.com/free-resources/#jev-first-pass), the write-up on the model itself
- [Claude x Jev write-up](https://www.charlieautomates.com/free-resources/#claude-x-jev) on charlieautomates.com
- [Free Skool community](https://start.ccstrategic.io/skool) for questions, results, and presets worth sharing

## Credits

- **Jev** is built by [TypeSafe](https://typesafe.ai) and served by [OpenRouter](https://openrouter.ai).
- The benchmark numbers come from a 216-email run on 2026-09-25. Reproduce them on your own inbox with `/jev-bench`.
- Built by [Charles J Dove](https://www.charlieautomates.com/).

## License

MIT
