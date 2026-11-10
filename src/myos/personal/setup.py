"""Connect MyOS to the assistants on this computer: the Skill, the tools and the MyOS block; nothing else changes.

Every step is listed before anything is written, and a step already in place is left alone, so running it again is
safe. Instruction files and the Codex configuration are the owner's: each is backed up in the data directory before
its first change, a linked file or a damaged block is reported instead of touched, and an existing tool registration
is kept as it is.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from . import sync
from .store import compile_block

SKILL = Path(__file__).resolve().parents[1] / 'skill'
# name: (label, folder in the home directory, instruction file)
HOSTS = {'claude': ('Claude Code', '.claude', 'CLAUDE.md'), 'codex': ('Codex', '.codex', 'AGENTS.md')}
STEPS = {'skill': 'Skill', 'block': 'MyOS block', 'tools': 'Tools'}


def setup(store, home, *, hosts=None, claude=None, server=None, apply=False):
    """Plan, and with `apply` carry out, the connection of each assistant. `claude` is the Claude Code executable, if any."""
    home = Path(home)
    if unknown := set(hosts or []) - HOSTS.keys():
        raise ValueError(f"Unknown assistant: {', '.join(sorted(unknown))}; choose from {', '.join(HOSTS)}")
    hosts = list(hosts) if hosts else [name for name, (_, folder, _) in HOSTS.items() if (home / folder).is_dir()]
    if not hosts:
        raise ValueError('No assistant found: neither ~/.claude nor ~/.codex exists. Install Claude Code or Codex, or pass --host')
    server = server or [sys.executable, '-m', 'myos.personal.mcp']
    files = {name: (home / HOSTS[name][1]).resolve() / HOSTS[name][2] for name in hosts}
    env = {'MYOS_DATA_DIR': str(store.root), 'MYOS_SYNC_TARGETS': os.pathsep.join(str(files[name]) for name in hosts)}
    steps = []
    for name in hosts:
        folder = home / HOSTS[name][1]
        tools = claude_tools(claude, env, server, apply) if name == 'claude' else codex_tools(store, folder / 'config.toml', env, server, apply)
        for step, (target, status, detail) in (('skill', skill(folder / 'skills' / 'myos', apply)),
                                               ('block', block(store, folder / HOSTS[name][2], apply)), ('tools', tools)):
            steps.append({'host': name, 'step': step, 'target': str(target), 'status': status, 'detail': detail})
    return {'steps': steps, 'applied': apply, 'data': str(store.root)}


def finished(apply):
    return 'done' if apply else 'todo'


def skill(dest, apply):
    if dest.is_symlink():
        return dest, 'ok', f'linked to {dest.resolve()}; left as it is'
    wanted = {p.relative_to(SKILL): p.read_bytes() for p in SKILL.rglob('*') if p.is_file()}
    if all((dest / rel).is_file() and (dest / rel).read_bytes() == body for rel, body in wanted.items()):
        return dest, 'ok', 'in place'
    detail = 'update to this version' if dest.exists() else 'install'
    if apply:
        shutil.copytree(SKILL, dest, dirs_exist_ok=True)
    return dest, finished(apply), detail


def block(store, path, apply):
    if path.is_symlink():
        return path, 'blocked', f'is a link; add the block to the real file yourself: myos compile >> {shlex.quote(str(path.resolve()))}'
    text = sync.read_exact(path) if path.is_file() else ''
    if any(begin in text for begin, _ in sync.MARKERS):
        try:
            sync.block_span(text, path)
        except ValueError:
            return path, 'blocked', 'holds a damaged MyOS block (a BEGIN or END marker is missing or doubled); repair it by hand'
        return path, 'ok', 'has the MyOS block'
    detail = 'add the MyOS block at the end; the rest of the file stays as it is' if text else 'create with the MyOS block'
    if apply:
        compiled = store.compile() if store.path.exists() else compile_block([])
        gap = '' if not text or text.endswith('\n\n') else '\n' if text.endswith('\n') else '\n\n'
        if text:
            sync.save_backup(store, path.parent.resolve() / path.name, text)
            sync.replace(path, text + gap + compiled)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(compiled, encoding='utf-8')
    return path, finished(apply), detail


def claude_tools(claude, env, server, apply):
    command = ['mcp', 'add', '--scope', 'user', 'myos', *[part for key, value in env.items() for part in ('-e', f'{key}={value}')], '--', *server]
    shown = shlex.join(['claude', *command])
    if claude is None:
        return 'claude', 'manual', f'Claude Code command not found; run this yourself: {shown}'
    if subprocess.run([claude, 'mcp', 'get', 'myos'], capture_output=True, text=True).returncode == 0:
        return 'claude mcp', 'ok', 'already registered; to replace it: claude mcp remove myos -s user, then run setup again'
    if apply:
        added = subprocess.run([claude, *command], capture_output=True, text=True)
        if added.returncode:
            return 'claude mcp', 'blocked', f'{(added.stderr or added.stdout).strip()[:300]}; run this yourself: {shown}'
    return 'claude mcp', finished(apply), 'register the MyOS tools for every project'


def codex_tools(store, config, env, server, apply):
    text = config.read_text(encoding='utf-8') if config.is_file() else ''
    try:
        servers = tomllib.loads(text).get('mcp_servers', {})
    except tomllib.TOMLDecodeError as exc:
        return config, 'blocked', f'cannot be read as TOML ({exc}); fix it, then run setup again'
    if 'myos' in servers:
        return config, 'ok', 'already registered'
    if apply:
        section = (f'[mcp_servers.myos]\ncommand = {json.dumps(server[0])}\nargs = {json.dumps(server[1:])}\n\n'
                   '[mcp_servers.myos.env]\n' + ''.join(f'{key} = {json.dumps(value)}\n' for key, value in env.items()))
        if text:
            sync.save_backup(store, config.parent.resolve() / config.name, text)
            sync.replace(config, text + ('' if text.endswith('\n\n') else '\n' if text.endswith('\n') else '\n\n') + section)
        else:
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text(section, encoding='utf-8')
    return config, finished(apply), 'register the MyOS tools'


def render(result, home):
    """The plan or the outcome as plain text for the person running it."""
    marks = {'ok': 'ok  ', 'todo': 'will', 'done': 'done', 'manual': 'you ', 'blocked': 'stop'}
    short = lambda target: target.replace(str(Path(home).resolve()), '~').replace(str(home), '~')
    lines = ['MyOS setup' + ('' if result['applied'] else ': the plan. Nothing was changed.'), f"  Your entries are kept in {short(result['data'])}", '']
    for name in dict.fromkeys(step['host'] for step in result['steps']):
        lines.append(HOSTS[name][0])
        # A command to run by hand keeps its full paths: a shell does not expand ~ inside KEY=~/path arguments.
        lines += [f"  [{marks[s['status']]}] {STEPS[s['step']]:<11} {short(s['target'])}: {s['detail'] if s['status'] == 'manual' else short(s['detail'])}"
                  for s in result['steps'] if s['host'] == name]
        lines.append('')
    left = [s for s in result['steps'] if s['status'] in ('manual', 'blocked')]
    if not result['applied']:
        lines.append('Nothing to do: everything is in place.' if all(s['status'] == 'ok' for s in result['steps'])
                     else 'To make these changes, run: myos setup --yes')
    else:
        if left:
            lines.append('Steps marked [you ] or [stop] still need you; run setup again afterwards to check.')
        lines.append('Restart your assistant. Then, in a new session, say: "Set up MyOS with me."')
    return '\n'.join(lines)
