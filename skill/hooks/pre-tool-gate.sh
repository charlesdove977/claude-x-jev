#!/usr/bin/env bash
# claude-x-jev · PreToolUse hook
#
# Claude Code pipes the tool call as JSON on stdin. This script asks Jev two yes/no
# questions from presets/tool-gate.json (is it reversible, does it serve the task) and
# prints a permissionDecision: allow when both clear the bar, deny when either is near
# zero, ask otherwise. On ANY failure (no key, network, bad JSON) it prints nothing and
# exits 0, which leaves Claude Code's normal permission prompt exactly as it was.
#
# Install (from the skill): /jev-gate install
# Or by hand, in ~/.claude/settings.json:
#   "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command",
#     "command": "bash ~/.claude/skills/claude-x-jev/hooks/pre-tool-gate.sh" } ] } ] }
#
# Tunables (env):
#   JEV_GATE_TOOLS     comma list of tools to gate       (default: Bash)
#   JEV_GATE_APPROVE   allow when every check >= this    (default: 0.9)
#   JEV_GATE_BLOCK     deny when any check <= this       (default: 0.1)
#   JEV_GATE_TASK      one line on what the agent is doing, improves the serves_task check
#   JEV_SKILL_DIR      where the skill is installed      (default: ~/.claude/skills/claude-x-jev)

SKILL_DIR="${JEV_SKILL_DIR:-$HOME/.claude/skills/claude-x-jev}"
SCRIPT="$SKILL_DIR/scripts/jev.py"
[ -f "$SCRIPT" ] || exit 0

python3 "$SCRIPT" gate --hook \
  --preset tool-gate \
  --tools "${JEV_GATE_TOOLS:-Bash}" \
  --approve "${JEV_GATE_APPROVE:-0.9}" \
  --block "${JEV_GATE_BLOCK:-0.1}" \
  ${JEV_GATE_TASK:+--task "$JEV_GATE_TASK"} \
  2>>"${TMPDIR:-/tmp}/jev-gate.log"
exit 0
