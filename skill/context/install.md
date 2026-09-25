---
status: unconfigured
model: typesafe/jev-1.13
key_location: env:OPENROUTER_API_KEY
preset_dir: ~/.claude/jev-presets
configured_on: null
hook_installed: false
---

# Install State

This is the only file `/jev-setup` writes. The frontmatter is the source of truth; the prose below explains the two states.

## unconfigured
No verified key. Every command should stop and route to `/jev-setup` instead of attempting a call. A missing key surfaces as a clear message from `scripts/jev.py`, never as a silent empty result.

## configured
`/jev-setup` made one live Decisions call and it returned an answer. The key lives where `key_location` says (an environment variable by default; the value itself is never written into this file or anywhere in the skill). `model` is the slug every command sends. Pin `typesafe/jev-1.13` for stable thresholds; `~typesafe/jev-latest` tracks new releases and can move your numbers.

## Notes
- `preset_dir` is where the operator's own presets live. The bundled ones under `presets/` are examples and get overwritten on update; `presets/user/` and `preset_dir` are preserved.
- `hook_installed` flips to true when `/jev-gate install` writes the PreToolUse hook into Claude Code settings.
