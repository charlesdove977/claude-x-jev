#!/usr/bin/env node
/**
 * claude-x-jev CLI
 *
 * Installs the claude-x-jev Claude Code skill into the user-global directory
 * (~/.claude/skills/claude-x-jev/) or the current project's .claude/skills/.
 *
 * `update` preserves the operator's own state (context/install.md and
 * presets/user/) so an upgrade never wipes a verified setup or private presets.
 *
 *   npx claude-x-jev install [--project] [--with-commands]
 *   npx claude-x-jev update  [--project] [--with-commands] [--clean]
 *   npx claude-x-jev uninstall [--project]
 *   npx claude-x-jev hook    [--project] [--write]      print or write the PreToolUse gate hook
 *   npx claude-x-jev --version
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const SKILL_NAME = 'claude-x-jev';
const PACKAGE_ROOT = path.resolve(__dirname, '..');
const SKILL_SRC = path.join(PACKAGE_ROOT, 'skill');
const PKG = require(path.join(PACKAGE_ROOT, 'package.json'));

// Written by /jev-setup and by the operator. Preserved across `update`.
const OPERATOR_DATA = [path.join('context', 'install.md'), path.join('presets', 'user')];

const COMMANDS = {
  'jev-setup': 'One-time setup for claude-x-jev: OpenRouter key, one live call, model pin. Routes to the claude-x-jev skill (task setup).',
  'jev-status': 'Credits, uptime, latency and a live Jev ping. Routes to the claude-x-jev skill (task status).',
  'jev-classify': 'Pick-one labels over many items with a confidence per item, via Jev. Routes to the claude-x-jev skill (task classify).',
  'jev-check': 'Yes/no probability over many items, via Jev. Routes to the claude-x-jev skill (task check).',
  'jev-score': 'Rank items on an ordered scale you define, via Jev. Routes to the claude-x-jev skill (task score).',
  'jev-route': 'Jev sorts everything, sure items act by label, unsure items go to Claude with full text. Routes to the claude-x-jev skill (task route).',
  'jev-verify': 'Check Claude\'s drafts against their source thread and your rules before sending. Routes to the claude-x-jev skill (task verify).',
  'jev-gate': 'Approve, block or escalate a tool call; install as a PreToolUse hook. Routes to the claude-x-jev skill (task gate).',
  'jev-match': 'Pairwise same-entity checks to collapse duplicates. Routes to the claude-x-jev skill (task match).',
  'jev-tune': 'Pick a confidence threshold from labelled results. Routes to the claude-x-jev skill (task tune).',
  'jev-lint': 'Check a preset\'s questions and criteria before running it. Routes to the claude-x-jev skill (task lint).',
  'jev-bench': 'Compare Jev against Claude on the same items: agreement, cost, time, disagreements. Routes to the claude-x-jev skill (task bench).',
  'jev-watch': 'Run a preset on a schedule with no Claude session open. Routes to the claude-x-jev skill (task watch).'
};

function userClaudeDir() { return path.join(os.homedir(), '.claude'); }
function projectClaudeDir() { return path.join(process.cwd(), '.claude'); }
function claudeDir(opts) { return opts.project ? projectClaudeDir() : userClaudeDir(); }
function skillTarget(opts) { return path.join(claudeDir(opts), 'skills', SKILL_NAME); }
function commandsDir(opts) { return path.join(claudeDir(opts), 'commands'); }

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else if (entry.isFile()) fs.copyFileSync(s, d);
  }
}

function rmrf(target) {
  if (fs.existsSync(target)) fs.rmSync(target, { recursive: true, force: true });
}

function stashOperatorData(target) {
  const stash = fs.mkdtempSync(path.join(os.tmpdir(), 'claude-x-jev-stash-'));
  let saved = 0;
  for (const rel of OPERATOR_DATA) {
    const from = path.join(target, rel);
    if (!fs.existsSync(from)) continue;
    const to = path.join(stash, rel);
    fs.mkdirSync(path.dirname(to), { recursive: true });
    if (fs.statSync(from).isDirectory()) copyDir(from, to); else fs.copyFileSync(from, to);
    saved += 1;
  }
  return { stash, saved };
}

function restoreOperatorData(stash, target) {
  let restored = 0;
  for (const rel of OPERATOR_DATA) {
    const from = path.join(stash, rel);
    if (!fs.existsSync(from)) continue;
    const to = path.join(target, rel);
    fs.mkdirSync(path.dirname(to), { recursive: true });
    if (fs.statSync(from).isDirectory()) copyDir(from, to); else fs.copyFileSync(from, to);
    restored += 1;
  }
  rmrf(stash);
  return restored;
}

function isConfigured(target) {
  const f = path.join(target, 'context', 'install.md');
  if (!fs.existsSync(f)) return false;
  const fm = fs.readFileSync(f, 'utf8').match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) return false;
  const m = fm[1].match(/^status:\s*(\S+)/m);
  return !!m && m[1].toLowerCase() === 'configured';
}

function commandStub(name, description) {
  const task = name.replace(/^jev-/, '');
  return `---\nname: ${name}\ndescription: ${description}\n---\n\nThis command routes to the \`claude-x-jev\` skill (task \`${task}\`).\n\nRead \`context/install.md\` first. If it says \`status: unconfigured\`, run \`/jev-setup\`.\nIf the skill is not installed at all:\n\n    npx claude-x-jev install --with-commands\n`;
}

function writeCommandStubs(opts) {
  const dir = commandsDir(opts);
  fs.mkdirSync(dir, { recursive: true });
  for (const [name, desc] of Object.entries(COMMANDS)) fs.writeFileSync(path.join(dir, name + '.md'), commandStub(name, desc));
  return { dir, count: Object.keys(COMMANDS).length };
}

function removeCommandStubs(opts) {
  const dir = commandsDir(opts);
  let removed = 0;
  for (const name of Object.keys(COMMANDS)) {
    const p = path.join(dir, name + '.md');
    if (fs.existsSync(p)) { fs.unlinkSync(p); removed += 1; }
  }
  return { dir, removed };
}

function hookEntry(target) {
  return { matcher: 'Bash', hooks: [{ type: 'command', command: `bash "${path.join(target, 'hooks', 'pre-tool-gate.sh')}"` }] };
}

function hook(opts) {
  const target = skillTarget(opts);
  const settingsPath = path.join(claudeDir(opts), 'settings.json');
  const entry = hookEntry(target);
  if (!opts.write) {
    console.log(`Add this to ${settingsPath} (merge into an existing "hooks" object):\n`);
    console.log(JSON.stringify({ hooks: { PreToolUse: [entry] } }, null, 2));
    console.log('\nOr run again with --write to merge it for you. Start in shadow mode: export JEV_GATE_APPROVE=1.01');
    return;
  }
  let settings = {};
  if (fs.existsSync(settingsPath)) {
    try { settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8')); }
    catch (e) { console.error(`[${SKILL_NAME}] ${settingsPath} is not valid JSON; not touching it.`); process.exitCode = 1; return; }
  }
  settings.hooks = settings.hooks || {};
  settings.hooks.PreToolUse = settings.hooks.PreToolUse || [];
  const already = settings.hooks.PreToolUse.some((h) => JSON.stringify(h).includes('pre-tool-gate.sh'));
  if (already) { console.log(`[${SKILL_NAME}] Hook already present in ${settingsPath}`); return; }
  fs.copyFileSync(settingsPath + '', settingsPath + '.bak-claude-x-jev');
  settings.hooks.PreToolUse.push(entry);
  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
  console.log(`[${SKILL_NAME}] Hook written to ${settingsPath} (backup at ${settingsPath}.bak-claude-x-jev)`);
  console.log('Restart Claude Code. Shadow mode first: export JEV_GATE_APPROVE=1.01');
}

function install(opts) {
  const target = skillTarget(opts);
  const exists = fs.existsSync(target);
  if (exists && !opts.force) {
    console.error(`[${SKILL_NAME}] Already installed at:\n  ${target}\n\nRun \`npx claude-x-jev update\` to upgrade (your setup and private presets are preserved), or \`uninstall\` to remove.`);
    process.exitCode = 1;
    return;
  }
  let stash = null, saved = 0;
  if (exists && opts.force) {
    if (!opts.clean) ({ stash, saved } = stashOperatorData(target));
    rmrf(target);
  }
  copyDir(SKILL_SRC, target);
  let restored = 0;
  if (stash) restored = restoreOperatorData(stash, target);
  try { fs.chmodSync(path.join(target, 'scripts', 'jev.py'), 0o755); fs.chmodSync(path.join(target, 'hooks', 'pre-tool-gate.sh'), 0o755); } catch (e) { /* windows */ }

  console.log(`[${SKILL_NAME}] Skill installed:\n  ${target}`);
  if (saved > 0) console.log(`[${SKILL_NAME}] Preserved ${restored} item(s): install state, private presets. Use --clean with update to start over.`);
  if (opts.withCommands) {
    const r = writeCommandStubs(opts);
    console.log(`[${SKILL_NAME}] Command stubs written (${r.count}):\n  ${r.dir}`);
  }
  console.log('');
  console.log('Done. Restart Claude Code, then:');
  if (isConfigured(target)) console.log('  /jev-classify          sort something (already set up)');
  else console.log('  /jev-setup             once: OpenRouter key + one live call');
  console.log('  /jev-route             pre-sort a queue before Claude works it');
  console.log('  /jev-gate              put a 0.3s safety check in front of tool calls');
  console.log('');
  console.log('Needs: python3 (3.8+) and an OpenRouter API key. Nothing else.');
}

function uninstall(opts) {
  const target = skillTarget(opts);
  if (!fs.existsSync(target)) { console.log(`[${SKILL_NAME}] Not installed at ${target}`); }
  else { rmrf(target); console.log(`[${SKILL_NAME}] Removed ${target}`); }
  const r = removeCommandStubs(opts);
  if (r.removed) console.log(`[${SKILL_NAME}] Removed ${r.removed} command stub(s) from ${r.dir}`);
  console.log('If you installed the gate hook, remove the PreToolUse entry from settings.json by hand.');
}

function help() {
  console.log(`claude-x-jev v${PKG.version}\n\nUsage:\n  npx claude-x-jev install   [--project] [--with-commands]\n  npx claude-x-jev update    [--project] [--with-commands] [--clean]\n  npx claude-x-jev uninstall [--project]\n  npx claude-x-jev hook      [--project] [--write]\n  npx claude-x-jev --version\n\n  --project        install into ./.claude instead of ~/.claude\n  --with-commands  also write /jev-* command stubs so the commands autocomplete\n  --clean          with update: wipe install state and private presets\n  --write          with hook: merge the PreToolUse entry into settings.json (backup kept)\n`);
}

function main(argv) {
  const args = argv.slice(2);
  const opts = {
    project: args.includes('--project'),
    withCommands: args.includes('--with-commands'),
    clean: args.includes('--clean'),
    write: args.includes('--write'),
    force: false
  };
  const cmd = args.find((a) => !a.startsWith('--'));
  if (args.includes('--version') || args.includes('-v')) { console.log(PKG.version); return; }
  if (!cmd || args.includes('--help') || args.includes('-h')) { help(); return; }
  switch (cmd) {
    case 'install': install(opts); break;
    case 'update': opts.force = true; install(opts); break;
    case 'uninstall': uninstall(opts); break;
    case 'hook': hook(opts); break;
    default: console.error(`Unknown command: ${cmd}\n`); help(); process.exitCode = 1;
  }
}

main(process.argv);
