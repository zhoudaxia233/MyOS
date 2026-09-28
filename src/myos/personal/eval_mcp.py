"""Evaluation-only MCP surface: two read tools, no resource or prompt handlers."""
from mcp.server.fastmcp import FastMCP

from .mcp import READ, myos_catalog, myos_read


class ReadOnlyEvalMCP(FastMCP):
    def _setup_handlers(self):
        # FastMCP normally advertises resources even when none are registered.
        # Keep those helpers unable to read anything; Codex still exposes them.
        self._mcp_server.list_tools()(self.list_tools)
        self._mcp_server.call_tool(validate_input=False)(self.call_tool)


mcp = ReadOnlyEvalMCP('MyOS evaluation reads')
mcp.tool(annotations=READ)(myos_catalog)
mcp.tool(annotations=READ)(myos_read)

if __name__ == '__main__':
    mcp.run()
