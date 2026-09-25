<p align="center">
  <img src="https://raw.githubusercontent.com/charlesdove977/claude-x-jev/main/docs/hero-claude-x-jev.png" alt="Claude x Jev" width="360">
</p>

# Claude x Jev

> **Fast, cheap, typed decisions for [Claude Code](https://claude.ai/code).** Jev sorts, checks, scores, gates and verifies at 0.3 seconds and a fraction of a cent per item, with a confidence number on every answer. Claude keeps the reading, the writing and the judgment.

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
/jev-setup        once: OpenRouter key, one live call, done
/jev-classify     sort anything
/jev-route        Jev pre-sorts, Claude reads only the unsure ones
/jev-gate         a 0.3s safety check in front of tool calls
```

Needs `python3` (3.8+) and an [OpenRouter](https://openrouter.ai) API key. No other dependencies. Five dollars of OpenRouter credit covers hundreds of thousands of decisions.

---

## What Jev is

[Jev](https://openrouter.ai/typesafe/jev-1.13) is a **decision model** from [TypeSafe](https://typesafe.ai), served on OpenRouter. It is not a chat model. You do not prompt it and read prose back. You hand it a piece of text plus a fixed set of choices, and it hands back a **typed answer with probabilities**:

| Primitive | You ask | You get back |
| --- | --- | --- |
| `choice` | Which one of these? | the label, a probability per label, a confidence |
| `noul` | Does this hold? | a probability of yes |
| `score` | Where on this ordered scale? | a weighted position, a probability per level, a confidence |

That is the whole model. It answers in about 300 milliseconds, output tokens are free, input costs about $0.04 per million tokens, and it gives the same answer to the same input every time. It cannot write a sentence. It cannot explain itself. It can tell you, on every single answer, how sure it is.

This skill puts Jev in front of Claude as the sorter.

---

## What Jev does better than Claude

We gave both models the same 216 real inbound emails, the same four questions, the same label definitions.

| | Jev 1.13 | Claude Opus 5.5 |
| --- | --- | --- |
| Per email | **0.3 s** | 1.3 s (batched 24 at a time) |
| All 216 | **65 s single file · ~6 s in parallel** | 37 s in 9 parallel batches · 4 min 46 s sequential |
| Cost | **$0.01** | $4.73 |
| Same answer twice | **Always** | Usually |
| Says how sure it is | **Every answer** | Only if asked |
| Runs outside Claude Code | **Yes: cron, n8n, a hook, a script** | Needs a session |

They agreed on 87 to 94 percent of labels. The number that matters more: **when Jev's confidence was 0.7 or higher (82 percent of the inbox), it matched Claude 95.5 percent of the time. Below that, 47 percent, and Jev flagged every one.** It knows when it does not know.

- **400x cheaper, and it never touches your Claude usage window or context.**
- **Deterministic.** No drift between runs, no mood.
- **Calibrated.** The confidence number is a real routing switch, not decoration.
- **Cannot hallucinate.** It has no prose to hallucinate with. On four of the 28 disagreements Claude saw deals that were not there (a debate-club invite became "brand deal, budget stated"). Jev did not.

## What Claude does better

- **Writing.** Every draft, reply, summary, explanation. Jev returns zero words.
- **Filling gaps in your definitions.** Claude used playbook knowledge it was never given. Jev used the words it was given, literally. Eight of the 28 disagreements were affiliate-only offers that our label text technically excluded. Claude was right; the fix was one sentence in the label.
- **Reasoning across questions.** On one email Jev said `vendor_pitch` and `affiliate_only` and `92% they will pay`. Nothing inside Jev reconciles those. Claude does it in its head; this skill does it with a `rules` block in the preset.
- **Memory and context.** Claude can know the same brand arrived through five agencies, or that a rate was quoted last month. Jev sees one request.
- **Applying a playbook.** Relationship holds, rate cards, tone. Jev checks one condition at a time; it cannot read a policy and act on it.

**The division:** Jev sorts, checks, scores, gates, verifies. Claude reads the unsure slice and writes everything. A person approves what ships.

---

## Commands

| Command | What it does | Primitive |
| --- | --- | --- |
| `/jev-setup` | OpenRouter key in place, one live call verified, model pinned | |
| `/jev-status` | Credits, uptime, latency, one live ping, cost estimate for a batch | |
| `/jev-classify` | Pick-one labels over many items, with confidence | `choice` |
| `/jev-check` | Yes/no probability over many items | `noul` |
| `/jev-score` | Rank items on an ordered scale you define | `score` |
| `/jev-route` | Jev labels everything; sure items act by label, unsure items go to Claude with full text | `choice` + threshold |
| `/jev-verify` | Check Claude's drafts against their source thread and your rules before sending | `choice` + `noul` |
| `/jev-gate` | Approve, block, or escalate a tool call; installable as a Claude Code PreToolUse hook | `noul` |
| `/jev-match` | Pairwise "same company / same ask?" to collapse duplicate threads | `noul` |
| `/jev-tune` | Pick the confidence threshold from labelled results (coverage vs precision table) | |
| `/jev-lint` | Catch vague labels, missing catch-alls, and contradicting answers before you spend | |
| `/jev-bench` | Jev vs Claude on your own data: agreement, cost, time, disagreements read by hand | |
| `/jev-watch` | Run a preset on cron, launchd, or n8n with no Claude session open | |

Every command goes through one file, `skill/scripts/jev.py` (stdlib only), which you can also call directly:

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
`/jev-setup`. It tells you where to get the key (openrouter.ai → Settings → Keys), where to put it (`export OPENROUTER_API_KEY=...` in your shell profile), and proves it with one live call that costs a hundredth of a cent. The key is never pasted into chat and never written into the skill.

### 2. Sort something
`/jev-classify`. Pick a bundled preset or describe your labels and it writes one. It lints the preset, dry-runs one item so you see exactly what leaves your machine, runs five so you can eyeball them, then runs the batch. You get a JSONL or CSV with a label, a confidence, and the probabilities per item, plus one summary line: items, seconds, cost.

### 3. Put Jev in front of Claude
`/jev-route`. Same run, but the output is split: `sorted.sure.jsonl` (act on these by label) and `sorted.unsure.items.jsonl` (Claude reads only these, with their full text). On the benchmark inbox that meant Claude read 38 emails instead of 216, for about 85 cents instead of $4.73.

### 4. Check Claude's work
`/jev-verify`. One item per draft: the thread it answers, your rules, the draft. Jev returns `supported / unsupported / declined` plus rule and tone checks. One failed check bounces the draft back to Claude. Nothing sends.

### 5. Gate tool calls
`/jev-gate`. Two conditions per call, is it reversible and does it serve the task. Start in shadow mode (nothing auto-allowed, dangerous things still denied), read the log for a few days, then go live at 0.9. On any error the hook prints nothing and exits 0, so Claude Code's own permission prompt stays exactly as it was. It can fail closed to a human; it can never fail open.

```bash
npx claude-x-jev hook --write      # merges the PreToolUse entry into ~/.claude/settings.json, backup kept
export JEV_GATE_APPROVE=1.01       # shadow mode: nothing can reach 1.01, so nothing auto-allows
```

### 6. Tune, then automate
`/jev-tune` sweeps thresholds against items a person checked and prints coverage and precision at each. `/jev-watch` writes a runner for cron, launchd, or n8n so the sorting happens with nobody at the keyboard.

---

## Presets

A preset is one JSON file: the questions, the criteria per label, the confidence bars, and the rules that reconcile answers with each other. Six generic ones ship in `skill/presets/`:

| Preset | Sorts | Questions |
| --- | --- | --- |
| `email-triage` | Inbound email | paid deal / vendor pitch / peer collab / non-pitch · money step · will they pay |
| `comment-triage` | Social comments | question / keyword drop / praise / critique / spam · needs reply · reply value 0 to 3 |
| `lead-qualify` | Form and DM leads | real business · decision maker · heat cold to ready · what they want |
| `draft-verify` | Generated replies | grounded / unsupported / declined · follows rules · tone ok |
| `tool-gate` | Agent tool calls | reversible · serves task |
| `match-entity` | Pairs of threads | same entity · same ask |

They are examples. Copy one to `~/.claude/jev-presets/`, rewrite the criteria for your data, run `/jev-lint`. Updates overwrite the bundled folder and never touch yours.

**The criteria text is the model.** There is no system prompt to rescue a vague label. `frameworks/criteria-writing.md` has the eight rules; `/jev-lint` enforces the floor.

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

Built to the Skillsmith skill spec: XML task steps, frameworks with anti-patterns and sources, templates with `{variable}` and `[prose]` placeholders.

---

## One thing to know

Jev lives at `POST https://openrouter.ai/api/alpha/decisions`, outside the `/api/v1` prefix. Send it to the chat endpoint (including through the OpenRouter MCP's chat tool) and you get HTTP 400: *"is a decisions model and cannot be used with the chat/completions endpoint."* This skill never does that. The MCP is still useful for credits, uptime and docs, and `/jev-setup` offers it as optional.

---

## Credits

- **Jev** is built by [TypeSafe](https://typesafe.ai) and served by [OpenRouter](https://openrouter.ai). Their [Jev docs](https://openrouter.ai/docs/guides/community/jev) and cookbooks (classification, verified cascade, tool-call gating, auto-approving permission prompts) shaped the patterns here.
- The benchmark numbers come from a 216-email run on 2026-09-25. Reproduce them on your own inbox with `/jev-bench`.
- Built by [Charles J Dove](https://www.charlieautomates.com/). Questions, results, and presets worth sharing: the free community at [start.ccstrategic.io/skool](https://start.ccstrategic.io/skool).

## License

MIT
