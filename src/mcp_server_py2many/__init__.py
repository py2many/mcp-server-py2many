#!/usr/bin/env python3
"""
MCP Server for py2many - Python to multiple languages transpiler.
"""

import asyncio
from mcp_server_py2many.server import main

if __name__ == "__main__":
    asyncio.run(main())
