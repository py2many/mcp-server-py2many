import asyncio

from .server import main as _main


def main():
    """Run the MCP server."""
    asyncio.run(_main())


if __name__ == "__main__":
    main()
