# Checklist: Setup Complete

Run before flipping `status: configured` in `context/install.md`. Every line must pass. A partial setup stays `unconfigured` on purpose so the next run resumes it.

## Environment
- [ ] `python3 --version` reports 3.8 or newer
- [ ] `OPENROUTER_API_KEY` is present in the shell that Claude Code's Bash tool uses
- [ ] The key was never pasted into chat and never written into any file under the skill

## Connection
- [ ] `jev.py status` printed a live-call line with a cost
- [ ] Credit balance was read back to the user
- [ ] The user was told what a 401 and a 402 mean

## Choices recorded
- [ ] Model pin chosen (`typesafe/jev-1.13` or `~typesafe/jev-latest`) and written to `context/install.md`
- [ ] MCP offered as optional, with its limitation stated (it cannot call Jev)
- [ ] `preset_dir` written, and the user knows bundled presets are examples that updates overwrite

## Handoff
- [ ] `configured: true` mirrored into `SKILL.md`
- [ ] `status: configured` flipped last
- [ ] User told the three most likely next commands
