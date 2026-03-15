# Building MyOS

Implementation rules:

1. Always follow MANIFESTO.md as the source of truth.
2. Prefer the thinnest viable design.
3. Do not overbuild.
4. Start with architecture and the smallest real vertical slice.
5. Natural language is the user surface, but all requests must be normalized into MyOS internal protocol.
6. MyOS must remain model-agnostic, protocol-first, terminal-first, and thin.
7. MCP is optional and secondary; it is not the kernel.
8. Fallbacks must be graceful: native capability -> adapter -> MCP -> manual bridge.
9. Preserve readability and composability.
10. When uncertain, choose the thinner architecture.
