#!/usr/bin/env python3
"""
MCP Server for py2many - Python to multiple languages transpiler.

This server provides tools to transpile Python code to various target languages
using the py2many transpiler. It supports both deterministic translation via
py2many and LLM-assisted translation via the --llm flag.
"""

import asyncio
import subprocess
import tempfile
import os
from typing import Literal

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Supported languages by py2many
SUPPORTED_LANGUAGES = {
    "cpp": "C++",
    "rust": "Rust",
    "go": "Go",
    "kotlin": "Kotlin",
    "dart": "Dart",
    "julia": "Julia",
    "nim": "Nim",
    "vlang": "V",
    "mojo": "Mojo",
    "dlang": "D",
    "zig": "Zig",
}

app = Server("mcp-server-py2many")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available transpiler tools."""
    return [
        Tool(
            name="transpile_python",
            description="Transpile Python code to another programming language using py2many. "
            "Use deterministic translation for simple, well-structured Python code. "
            "For complex code or when the deterministic translation fails, consider using "
            "the transpile_python_with_llm tool instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "python_code": {
                        "type": "string",
                        "description": "The Python code to transpile",
                    },
                    "target_language": {
                        "type": "string",
                        "enum": list(SUPPORTED_LANGUAGES.keys()),
                        "description": f"Target language. Supported: {', '.join(SUPPORTED_LANGUAGES.values())}",
                    },
                },
                "required": ["python_code", "target_language"],
            },
        ),
        Tool(
            name="transpile_python_with_llm",
            description="Transpile Python code to another language using py2many with LLM assistance. "
            "Use this for complex Python code, when dealing with language-specific idioms, "
            "or when the deterministic translation produces incorrect or non-idiomatic results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "python_code": {
                        "type": "string",
                        "description": "The Python code to transpile",
                    },
                    "target_language": {
                        "type": "string",
                        "enum": list(SUPPORTED_LANGUAGES.keys()),
                        "description": f"Target language. Supported: {', '.join(SUPPORTED_LANGUAGES.values())}",
                    },
                },
                "required": ["python_code", "target_language"],
            },
        ),
        Tool(
            name="list_supported_languages",
            description="List all supported target languages for transpilation",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


async def run_py2many(
    python_code: str,
    target_language: Literal["cpp", "rust", "go", "kotlin", "dart", "julia", "nim", "vlang", "mojo", "dlang", "zig"],
    use_llm: bool = False,
) -> str:
    """Run py2many transpiler on the given Python code."""
    # Create a temporary file for the Python code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Build the command
        cmd = ["py2many", f"--{target_language}"]
        if use_llm:
            cmd.append("--llm")
        cmd.append(temp_path)

        # Run py2many
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Determine the output file path
        base_path = temp_path.replace(".py", "")
        extension_map = {
            "cpp": ".cpp",
            "rust": ".rs",
            "go": ".go",
            "kotlin": ".kt",
            "dart": ".dart",
            "julia": ".jl",
            "nim": ".nim",
            "vlang": ".v",
            "mojo": ".mojo",
            "dlang": ".d",
            "zig": ".zig",
        }
        output_path = base_path + extension_map.get(target_language, ".txt")

        # Read the output file if it exists
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                output_code = f.read()
        else:
            output_code = ""

        # Combine stdout, stderr, and output code
        output_parts = []
        if result.stdout:
            output_parts.append(f"=== stdout ===\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"=== stderr ===\n{result.stderr}")
        if output_code:
            output_parts.append(f"=== Generated {target_language.upper()} code ===\n{output_code}")

        if not output_parts:
            return "No output generated."

        return "\n\n".join(output_parts)

    except subprocess.TimeoutExpired:
        return "Error: Transpilation timed out after 60 seconds."
    except Exception as e:
        return f"Error during transpilation: {str(e)}"
    finally:
        # Clean up temporary files
        try:
            os.unlink(temp_path)
            # Also clean up output file if it exists
            base_path = temp_path.replace(".py", "")
            for ext in [".cpp", ".rs", ".go", ".kt", ".dart", ".jl", ".nim", ".v", ".mojo", ".d", ".zig"]:
                output_file = base_path + ext
                if os.path.exists(output_file):
                    os.unlink(output_file)
        except OSError:
            pass


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "list_supported_languages":
        languages_text = "\n".join(
            [f"- {code}: {name}" for code, name in SUPPORTED_LANGUAGES.items()]
        )
        return [TextContent(type="text", text=f"Supported languages:\n\n{languages_text}")]

    elif name == "transpile_python":
        python_code = arguments.get("python_code", "")
        target_language = arguments.get("target_language", "")

        if not python_code:
            return [TextContent(type="text", text="Error: No Python code provided.")]
        if target_language not in SUPPORTED_LANGUAGES:
            return [
                TextContent(
                    type="text",
                    text=f"Error: Unsupported target language '{target_language}'. "
                    f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}",
                )
            ]

        result = await run_py2many(python_code, target_language, use_llm=False)
        return [TextContent(type="text", text=result)]

    elif name == "transpile_python_with_llm":
        python_code = arguments.get("python_code", "")
        target_language = arguments.get("target_language", "")

        if not python_code:
            return [TextContent(type="text", text="Error: No Python code provided.")]
        if target_language not in SUPPORTED_LANGUAGES:
            return [
                TextContent(
                    type="text",
                    text=f"Error: Unsupported target language '{target_language}'. "
                    f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}",
                )
            ]

        result = await run_py2many(python_code, target_language, use_llm=True)
        return [TextContent(type="text", text=result)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
