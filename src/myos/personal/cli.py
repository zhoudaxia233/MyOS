"""Small deterministic adapter for portable cognition assets."""
import argparse
import json
import os
import sqlite3
from datetime import date
from pathlib import Path

from .evaluate import DEFAULT_MODEL, DEFAULT_REVIEWER, EFFORTS, SKILL, evaluate
from .store import CASES_DIR, Store
from . import sync
from .tracing import Trace, show, trace_dir
from .view import MAP_NAME, PIPELINE_NAME, render_map, render_pipeline, write_private


def main(argv=None):
    parser = argparse.ArgumentParser(description='MyOS personal cognition assets. Use the MyOS Skill for learning and application.')
    parser.add_argument('--data', type=Path, default=Path(os.environ.get('MYOS_DATA_DIR', Path.home() / '.local/share/myos')))
    parser.add_argument('--verbose', action='store_true', help='Save full private arguments, payloads, record/source text and outputs to local traces (default off; catalog/read/references/put only)')
    commands = parser.add_subparsers(dest='command', required=True)
    migration = commands.add_parser('migrate', help='Import legacy sources to a new isolated data directory')
    migration.add_argument('--source', type=Path, action='append', required=True)
    references = commands.add_parser('references', help='List preserved sources or read an archived source')
    references.add_argument('path', nargs='?')
    catalog = commands.add_parser('catalog', help='Core assets in full plus an index of the rest; no semantic ranking')
    catalog.add_argument('--purpose', help='One-line summary of the request, recorded only in traces')
    read = commands.add_parser('read')
    read.add_argument('id')
    read.add_argument('--history', action='store_true')
    put = commands.add_parser('put', help='Append a host-authorized revision')
    put.add_argument('payload', type=Path, help='JSON containing asset, expected_revision, authorization')
    check = commands.add_parser('check', help='Validate revisions and preserved migration sources')
    check.add_argument('--strict', action='store_true')
    compile_parser = commands.add_parser('compile', help="Print core assets in full and one line per other adopted asset as a Markdown block for a host's always-loaded instructions")
    compile_parser.add_argument('--target', type=Path, action='append', help='Host instruction file holding a MyOS block (repeatable; default: MYOS_SYNC_TARGETS)')
    action = compile_parser.add_mutually_exclusive_group()
    action.add_argument('--write', action='store_true', help='Replace the MyOS block in every target; back up each changed file first')
    action.add_argument('--dry-run', action='store_true', help='Show the diff for every target without writing')
    action.add_argument('--list-targets', action='store_true', help='List targets and whether each holds exactly one MyOS block')
    action.add_argument('--revert', action='store_true', help='Restore every target from its latest backup')
    view = commands.add_parser('view', help='Write a read-only HTML map of the store')
    view.add_argument('--out', type=Path, help='HTML path outside the data directory (default: myos-view.html in it); replaces only an earlier MyOS page')
    evaluation = commands.add_parser('eval', help='Compare answers without and with MyOS on private test cases; never changes the store')
    evaluation.add_argument('--suite', type=Path, help='Directory holding cases/ (default: evals in the data directory)')
    evaluation.add_argument('--name', default=date.today().isoformat(), help='Run name; rerunning a name resumes it (default: today)')
    evaluation.add_argument('--model', action='append', help=f'Answering model (repeatable; default {DEFAULT_MODEL})')
    evaluation.add_argument('--reviewer', default=DEFAULT_REVIEWER, help='Blind reviewer model')
    evaluation.add_argument('--effort', default='medium', choices=EFFORTS, help='Reasoning effort for answers (default medium)')
    evaluation.add_argument('--review-effort', default='high', choices=EFFORTS, help='Reasoning effort for the reviewer (default high)')
    evaluation.add_argument('--repeat', type=int, default=1, help='Answers per case, setup and model')
    evaluation.add_argument('--jobs', type=int, default=3, help='Concurrent host calls (reviews use at most 2)')
    evaluation.add_argument('--case', action='append', help='Only this case id (repeatable)')
    evaluation.add_argument('--asset', action='append', help='Only cases testing this entry, plus negative controls (repeatable)')
    evaluation.add_argument('--skill', type=Path, default=SKILL, help='Skill directory for the daily setup')
    evaluation.add_argument('--host', default='claude', help='Claude Code executable')
    trace_parser = commands.add_parser('trace', help='Inspect saved snapshots without querying the store or a model')
    trace_commands = trace_parser.add_subparsers(dest='trace_command', required=True)
    trace_show = trace_commands.add_parser('show')
    trace_show.add_argument('--dir', type=Path, default=trace_dir())
    trace_show.add_argument('--file', type=Path)
    trace_show.add_argument('--run')
    trace_show.add_argument('--group', help='Filter by the external MYOS_TRACE_GROUP label')
    trace_show.add_argument('--call', help='Show all saved input/output events for this call ID')
    trace_show.add_argument('--html', action='store_true', help='Write the selected calls as a read-only HTML pipeline instead of JSON')
    trace_show.add_argument('--out', type=Path, help='HTML path outside the trace directory (default: pipeline.html in it); replaces only an earlier MyOS page')
    args = parser.parse_args(argv)
    if args.command == 'trace':
        try:
            timeline = show(args.dir, file=args.file, run=args.run, call=args.call, group=args.group, include_events=args.html)
            if args.html:
                written = write_private(args.out or args.dir / PIPELINE_NAME, render_pipeline(timeline), kind='pipeline', private_root=args.dir, default_name=PIPELINE_NAME)
                print(json.dumps({'written': str(written), 'calls': len(timeline['calls'])}, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(timeline, ensure_ascii=False, indent=2))
            return 0
        except (ValueError, OSError) as exc:
            parser.exit(2, f'{exc}\n')
    store = Store(args.data.expanduser().resolve())
    parameters = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items() if k not in ('verbose', 'command')}
    parameters = {k: [str(v) for v in value] if isinstance(value, list) else value for k, value in parameters.items()}
    trace = Trace(args.verbose and args.command in ('catalog', 'read', 'references', 'put'), 'cli', args.command, parameters)
    trace.emit('store_selected', root=str(store.root))
    stage = 'handler'
    try:
        if args.command == 'migrate':
            from .migrate import migrate
            result = migrate(args.source, store.root)
        elif args.command == 'references':
            result = trace.invoke(store.references, {'path': args.path})
        elif args.command == 'catalog':
            result = trace.invoke(store.catalog, {})
        elif args.command == 'read':
            result = trace.invoke(store.read, {'asset_id': args.id, 'history': args.history})
        elif args.command == 'put':
            stage = 'payload_file_read'
            payload_text = args.payload.read_text()
            trace.emit('payload_file', text=payload_text)
            stage = 'payload_json_decode'
            payload = json.loads(payload_text)
            stage = 'handler'
            result = trace.invoke(store.put, payload)
            if (host_sync := sync.after_put(store)) is not None:
                result['host_sync'] = host_sync
        elif args.command == 'compile':
            targets = args.target or sync.env_targets()
            if args.write or args.dry_run:
                result = sync.sync(store, targets, dry_run=args.dry_run)
            elif args.list_targets:
                result = sync.list_targets(store, targets)
            elif args.revert:
                result = sync.revert(store, targets)
            else:
                result = store.compile()
        elif args.command == 'eval':
            result = evaluate(store, (args.suite or store.root / CASES_DIR.parent).expanduser().resolve(), args.name,
                              models=args.model or [DEFAULT_MODEL], reviewer=args.reviewer, effort=args.effort, review_effort=args.review_effort, repeat=max(1, args.repeat),
                              jobs=args.jobs, only=args.case, assets=args.asset, skill=args.skill.expanduser(), host=args.host)
        elif args.command == 'view':
            written = write_private(args.out or store.root / MAP_NAME, render_map(store), kind='map', private_root=store.root, default_name=MAP_NAME)
            result = {'written': str(written)}
        else:
            result = store.check(strict=args.strict)
        stage = 'cli_output_serialization'
        output = result.rstrip('\n') if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2)
        stage = 'cli_stdout_write'
        print(output)
        trace.emit('cli_stdout', text=output + '\n', capture_boundary='text accepted by Python stdout.write; delivery to downstream reader not verified')
        trace.emit('completed', status='success', completion_boundary='CLI adapter return')
        return 0
    except BaseException as exc:
        trace.emit('completed', status='failed', failure_stage=stage, error_type=type(exc).__name__, error=str(exc))
        if isinstance(exc, (ValueError, OSError, sqlite3.Error)):
            parser.exit(2, f'{exc}\n')
        raise
    finally:
        trace.close()


if __name__ == '__main__':
    raise SystemExit(main())
