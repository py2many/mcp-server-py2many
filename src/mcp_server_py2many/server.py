#!/usr/bin/env python3
"""
MCP Server for py2many - Python to multiple languages transpiler.

This server provides tools to transpile Python code to various target languages
using the py2many transpiler. It supports both deterministic translation via
py2many and LLM-assisted translation via the --llm flag.
"""

import asyncio
import re
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
        Tool(
            name="verify_python",
            description="Verify Python code using SMT and z3 solver. "
            "Transpiles Python code using --smt flag and verifies that the inverse "
            "of pre/post conditions are unsat (i.e., the implementation matches the spec). "
            "Returns SAT if a counterexample is found (bug detected), UNSAT if verified.",
            inputSchema={
                "type": "object",
                "properties": {
                    "python_code": {
                        "type": "string",
                        "description": "The Python code to verify",
                    },
                },
                "required": ["python_code"],
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
        cmd = ["uvx", "py2many", f"--{target_language}"]
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


async def run_py2many_verify(python_code: str) -> str:
    """Verify Python code using py2many --smt and z3 solver."""
    # Create a temporary file for the Python code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Run py2many --smt
        cmd = ["uvx", "py2many", "--smt", temp_path]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return f"Error running py2many --smt:\n{result.stderr}"

        # Find the generated SMT file
        smt_path = temp_path.replace(".py", ".smt")
        if not os.path.exists(smt_path):
            return f"Error: SMT file not generated at {smt_path}"

        # Read the SMT file
        with open(smt_path, "r") as f:
            smt_content = f.read()

        # Extract preconditions - look for define-fun with -pre suffix
        pre_conditions = re.findall(r'\(define-fun ([a-zA-Z_][a-zA-Z0-9_-]*-pre)\b', smt_content)

        # Extract variables from precondition definitions for proper function calls
        pre_vars = {}
        for line in smt_content.split('\n'):
            if 'define-fun' in line and '-pre' in line:
                func_match = re.search(r'define-fun\s+([a-zA-Z_][a-zA-Z0-9_-]*-pre)', line)
                if func_match:
                    func_name = func_match.group(1)
                    params_match = re.search(r'define-fun\s+[a-zA-Z_][a-zA-Z0-9_-]*-pre\((.+?)\)\s+Bool', line)
                    if params_match:
                        params_str = params_match.group(1)
                        params = re.findall(r'(\w+)\s+Int', params_str)
                        pre_vars[func_name] = params

        # Build verification query: pre AND not(correct == buggy)
        # Find all assert statements and modify the last one
        lines = smt_content.strip().split('\n')
        new_lines = []
        pre_conditions = []

        for line in lines:
            # Extract precondition if defined
            if '(define-fun ' in line and '-pre ' in line:
                func_match = re.search(r'\(define-fun (\w+-pre)', line)
                if func_match:
                    pre_conditions.append(func_match.group(1))
            new_lines.append(line)

        # Modify the assertion to include preconditions
        verification_lines = []
        has_pre_assertion = False

        for line in new_lines:
            if line.strip().startswith('(assert'):
                # Check if this is the main assertion (not (= ...))
                if 'not (= ' in line or '(not (= ' in line:
                    # Add precondition to the assertion
                    if pre_conditions:
                        # Get the variables for this precondition
                        pre_func = pre_conditions[0]
                        vars_str = ' '.join(pre_vars.get(pre_func, []))
                        if vars_str:
                            pre_call = f"({pre_func} {vars_str})"
                        else:
                            pre_call = pre_func
                        pre_assert = f"(assert (and {pre_call} {line.strip()[8:-1]}))"
                        verification_lines.append(pre_assert)
                        has_pre_assertion = True
                    else:
                        verification_lines.append(line)
                else:
                    verification_lines.append(line)
            else:
                verification_lines.append(line)

        # If no precondition was found, use the original SMT
        if not has_pre_assertion:
            verification_smt = smt_content
        else:
            verification_smt = '\n'.join(verification_lines)

        # Write verification SMT to temp file
        verify_smt_path = temp_path.replace(".py", "_verify.smt")
        with open(verify_smt_path, "w") as f:
            f.write(verification_smt)

        # Run z3
        z3_result = subprocess.run(
            ["z3", verify_smt_path],
            capture_output=True,
            text=True,
            timeout=60,
        )

        z3_output = z3_result.stdout.strip()
        is_sat = "sat" in z3_output.lower()
        is_unsat = "unsat" in z3_output.lower()

        result_parts = []
        result_parts.append(f"=== py2many --smt output ===\n{result.stdout}")
        if result.stderr:
            result_parts.append(f"=== stderr ===\n{result.stderr}")
        result_parts.append(f"=== z3 verification result ===\n{z3_output}")

        if is_sat:
            result_parts.append("\n=== VERIFICATION FAILED ===")
            result_parts.append("SAT means a counterexample was found where the implementation differs from the spec.")
        elif is_unsat:
            result_parts.append("\n=== VERIFICATION PASSED ===")
            result_parts.append("UNSAT means no counterexample exists - the implementation matches the spec.")
        else:
            result_parts.append(f"\n=== UNKNOWN RESULT ===")

        return "\n".join(result_parts)

    except subprocess.TimeoutExpired:
        return "Error: Verification timed out after 60 seconds."
    except Exception as e:
        return f"Error during verification: {str(e)}"
    finally:
        # Clean up temporary files
        try:
            os.unlink(temp_path)
            smt_path = temp_path.replace(".py", ".smt")
            if os.path.exists(smt_path):
                os.unlink(smt_path)
            verify_smt_path = temp_path.replace(".py", "_verify.smt")
            if os.path.exists(verify_smt_path):
                os.unlink(verify_smt_path)
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

    elif name == "verify_python":
        python_code = arguments.get("python_code", "")

        if not python_code:
            return [TextContent(type="text", text="Error: No Python code provided.")]

        result = await run_py2many_verify(python_code)
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
