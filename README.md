# mcp-server-py2many

A Model Context Protocol (MCP) server that provides tools for transpiling Python code to multiple programming languages using [py2many](https://github.com/adsharma/py2many).

## Overview

This MCP server exposes tools that allow LLMs to transpile Python code to various target languages including C++, Rust, Go, Kotlin, Dart, Julia, Nim, V, Mojo, D, SMT, and Zig.

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd mcp-server-py2many

# Install dependencies
uv sync

# Run the server
uv run mcp-server-py2many
```

### Using pip

```bash
pip install mcp-server-py2many
```

## Configuration

Add this server to your MCP client configuration:

### Claude Desktop Config

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "py2many": {
      "command": "uvx",
      "args": ["mcp-server-py2many"]
    }
  }
}
```

Or with a local installation:

```json
{
  "mcpServers": {
    "py2many": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-server-py2many", "mcp-server-py2many"]
    }
  }
}
```

## Available Tools

### 1. `transpile_python`

Transpile Python code to another programming language using deterministic rules-based translation.

**Parameters:**
- `python_code` (string, required): The Python code to transpile
- `target_language` (string, required): Target language (cpp, rust, go, kotlin, dart, julia, nim, vlang, mojo, dlang, smt, zig)

### 2. `transpile_python_with_llm`

Transpile Python code using py2many with LLM assistance for better handling of complex idioms.

**Parameters:**
- `python_code` (string, required): The Python code to transpile
- `target_language` (string, required): Target language (cpp, rust, go, kotlin, dart, julia, nim, vlang, mojo, dlang, smt, zig)

### 3. `list_supported_languages`

List all supported target languages for transpilation.

## When to Use Deterministic vs LLM-Assisted Translation

### Use **Deterministic Translation** (`transpile_python`) when:

✅ **Simple, idiomatic Python code**
- Basic control flow (if/else, for/while loops)
- Standard library functions with direct equivalents
- Data structures (lists, dicts, sets)
- Simple functions and classes

✅ **Well-tested patterns**
- Mathematical computations
- String manipulations
- File I/O operations
- Algorithmic implementations

✅ **When reproducibility matters**
- Same input always produces same output
- No external dependencies or API calls
- Clear, deterministic behavior

**Example cases for deterministic:**
```python
# Simple functions
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Data processing
def sum_even_numbers(numbers):
    return sum(n for n in numbers if n % 2 == 0)

# Basic algorithms
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### Use **LLM-Assisted Translation** (`transpile_python_with_llm`) when:

🧠 **Complex Python idioms**
- Decorators and metaclasses
- Complex comprehensions with multiple clauses
- Generator expressions and coroutines
- Dynamic typing patterns

🧠 **Language-specific features need translation**
- Python-specific libraries (numpy, pandas patterns)
- Duck typing and protocol implementations
- Monkey patching and runtime modifications
- Context managers with complex behavior

🧠 **Deterministic translation fails or produces non-idiomatic code**
- Type errors that need semantic understanding
- Non-idiomatic output in target language
- Missing imports or dependencies
- Complex inheritance patterns

🧠 **Target language best practices differ significantly**
- Rust ownership and borrowing patterns
- C++ memory management
- Go concurrency patterns
- Functional programming in target language

**Example cases for LLM-assisted:**
```python
# Complex decorators
def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

# Complex data transformations
def process_data(data):
    return [
        {
            'name': item['name'].upper(),
            'values': [x * 2 for x in item['values'] if x > 0]
        }
        for item in data
        if item.get('active') and len(item.get('values', [])) > 5
    ]

# Dynamic behavior
class DynamicClass:
    def __getattr__(self, name):
        return lambda *args: f"Called {name} with {args}"
```

## Decision Flowchart

```
Is your Python code...
│
├─ Simple functions/algorithms?
│  └─ Yes → Use deterministic ✓
│
├─ Standard data structures and control flow?
│  └─ Yes → Use deterministic ✓
│
├─ Complex decorators, metaclasses, dynamic behavior?
│  └─ Yes → Use LLM-assisted 🧠
│
├─ Heavy use of Python-specific idioms?
│  └─ Yes → Use LLM-assisted 🧠
│
├─ Did deterministic translation fail?
│  └─ Yes → Try LLM-assisted 🧠
│
└─ Need idiomatic target language output?
   └─ Yes → Use LLM-assisted 🧠
```

## Supported Languages

| Language | Code | Notes |
|----------|------|-------|
| C++ | `cpp` | Full support with STL containers |
| Rust | `rust` | Ownership-aware translation |
| Go | `go` | Idiomatic Go code generation |
| Kotlin | `kotlin` | JVM-compatible output |
| Dart | `dart` | Flutter-friendly |
| Julia | `julia` | Scientific computing focus |
| Nim | `nim` | Systems programming |
| V | `vlang` | Simple, fast compilation |
| Mojo | `mojo` | AI/ML performance computing |
| D | `dlang` | Systems programming |
| Zig | `zig` | Modern systems programming |

### Design by Contract with SMT

SMT (Satisfiability Modulo Theories) support in py2many enables **Design by Contract** programming—writing specifications that can be formally verified using Z3 or other SMT solvers. Unlike other target languages, SMT output is not meant to be a direct end-user programming language, but rather a specification language for verification.

**Key Concepts:**
- **Pre-conditions**: Constraints that must hold before a function executes
- **Post-conditions**: Constraints that must hold after a function executes
- **Refinement types**: Types with additional constraints (e.g., `int` where `1 < x < 1000`)

**Example: Mathematical Equations with Constraints**

Python source with pre-conditions:
```python
from py2many.smt import check_sat, default_value, get_value
from py2many.smt import pre as smt_pre

x: int = default_value(int)
y: int = default_value(int)
z: float = default_value(float)


def equation(x: int, y: int) -> bool:
    if smt_pre:
        assert x > 2        # pre-condition
        assert y < 10       # pre-condition
        assert x + 2 * y == 7  # constraint equation
    True


def fequation(z: float) -> bool:
    if smt_pre:
        assert 9.8 + 2 * z == z + 9.11
    True


assert equation(x, y)
assert fequation(z)
check_sat()
get_value((x, y, z))
```

Generated SMT-LIB 2.0 output:
```smt
(declare-const x Int)
(declare-const y Int)
(declare-const z Real)

(define-fun equation-pre ((x Int) (y Int)) Bool
  (and
    (> x 2)
    (< y 10)
    (= (+ x (* 2 y)) 7)))

(define-fun equation ((x Int) (y Int))  Bool
  true)

(assert (and
          (equation-pre  x y)
          (equation x y)))

(check-sat)
(get-value (x y z))
```

When run with `z3 -smt2 equations.smt`, the solver proves the constraints are satisfiable and returns values: `x = 7, y = 0, z = -0.69`.

**Use Cases:**
- **Static verification**: Prove correctness before deployment
- **Refinement types**: Enforce range constraints on integers (e.g., `UserId` must be `0 < id < 1000`)
- **Protocol verification**: Ensure state machines follow valid transitions
- **Security properties**: Verify input sanitization pre-conditions

**Further Reading:**
- [PySMT: Design by Contract in Python](https://adsharma.github.io/pysmt/) - How py2many enables refinement types and formal verification
- [Agentic Transpilers](https://adsharma.github.io/agentic-transpilers) - Architecture for multi-level transpilation with verification
- [equations.py source](https://github.com/py2many/py2many/blob/main/tests/cases/equations.py) - Python test case
- [equations.smt output](https://github.com/py2many/py2many/blob/main/tests/expected/equations.smt) - Generated SMT-LIB

## Examples

### Example 1: Simple Function (Deterministic)

```python
# Python input
def greet(name):
    return f"Hello, {name}!"

# C++ output (via transpile_python)
#include <iostream>
#include <string>

std::string greet(std::string name) {
    return "Hello, " + name + "!";
}
```

### Example 2: Complex Data Processing (LLM-Assisted)

```python
# Python input with complex comprehensions
def analyze_sales(data):
    return {
        region: {
            'total': sum(s['amount'] for s in sales),
            'count': len(sales),
            'avg': sum(s['amount'] for s in sales) / len(sales)
        }
        for region, sales in data.items()
        if any(s['amount'] > 1000 for s in sales)
    }

# Better results with LLM-assisted translation for idiomatic target language
```

## Development

```bash
# Install development dependencies
uv sync

# Run the server
uv run mcp-server-py2many

# Test the server manually
uv run python -m mcp_server_py2many
```

## How It Works

1. The MCP server receives a request with Python code and target language
2. Creates a temporary Python file with the code
3. Runs `py2many --{language}` (or with `--llm` flag) on the file
4. Captures the generated output and any errors
5. Returns the transpiled code to the LLM client

## Limitations

- Not all Python features are supported in all target languages
- Some Python standard library functions may not have direct equivalents
- Complex dynamic Python code may require manual adjustments after transpilation
- LLM-assisted mode requires an LLM API key configured for py2many

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please open issues and pull requests on the repository.

## Related Projects

- [py2many](https://github.com/adsharma/py2many) - The transpiler this MCP server wraps
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol specification
