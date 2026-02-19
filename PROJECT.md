# mcp-server-py2many

**Status:** In Development  
**Last Updated:** 2026-02-19

This MCP server provides Python-to-multiple-languages transpilation using py2many.

## Quick Start

```bash
# Install and run
uv sync
uv run mcp-server-py2many
```

## Available Tools

- `transpile_python` - Deterministic translation for simple Python code
- `transpile_python_with_llm` - LLM-assisted translation for complex idioms
- `list_supported_languages` - Show supported target languages

## When to Use Which Mode?

See [README.md](README.md) for detailed guidance on choosing between deterministic and LLM-assisted translation.

**Quick Rule:**
- Simple functions, algorithms, data structures → **Deterministic** ✓
- Decorators, dynamic behavior, complex idioms → **LLM-Assisted** 🧠

## Project Structure

```
mcp-server-py2many/
├── src/mcp_server_py2many/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py          # Main MCP server implementation
├── examples/
│   ├── simple_deterministic.py      # Examples for deterministic mode
│   └── complex_llm_assisted.py      # Examples for LLM-assisted mode
├── pyproject.toml
└── README.md              # Full documentation
```

## Development

```bash
# Format code
uv run ruff format .

# Type check
uv run mypy src/

# Run tests
uv run pytest
```
