import asyncio
import json
import os
import subprocess
import sys


def test_cli_real_process_is_read_only_on_empty_install(tmp_path):
    result = subprocess.run([sys.executable, '-m', 'myos', '--data', str(tmp_path / 'empty'), 'catalog'], capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {'core': [], 'index': []}
    assert not (tmp_path / 'empty').exists()


def test_freeform_text_is_not_a_command(tmp_path):
    result = subprocess.run([sys.executable, '-m', 'myos', '--data', str(tmp_path / 'empty'), 'write me a story'], capture_output=True, text=True)
    assert result.returncode != 0
    assert not (tmp_path / 'empty').exists()


def test_cli_errors_without_traceback(tmp_path):
    result = subprocess.run([sys.executable, '-m', 'myos', '--data', str(tmp_path / 'empty'), 'read', 'missing'], capture_output=True, text=True)
    assert result.returncode == 2
    assert 'Traceback' not in result.stderr


def test_installed_stdio_canonical_entrypoint(tmp_path):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    async def run():
        config = StdioServerParameters(command=sys.executable, args=['-m', 'myos.personal.mcp'], env=dict(os.environ, MYOS_DATA_DIR=str(tmp_path / 'private')))
        async with stdio_client(config) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                listing = await session.list_tools()
                assert {t.name for t in listing.tools} == {'myos_catalog', 'myos_read', 'myos_put', 'myos_references'}
                for tool in listing.tools:
                    assert tool.annotations.readOnlyHint is (tool.name != 'myos_put')
                catalog = next(t for t in listing.tools if t.name == 'myos_catalog')
                assert 'apply only when their applicability fits' in catalog.description  # core is visible, not applied to everything
                assert 'every boundary that could cover the task' in catalog.description
                result = await session.call_tool('myos_catalog', {})
                assert not result.isError
                assert not (tmp_path / 'private').exists()
    asyncio.run(run())
