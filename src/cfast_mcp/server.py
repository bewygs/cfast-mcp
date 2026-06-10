"""FastMCP server for CFAST."""

from mcp.server.fastmcp import FastMCP

from .registry import ModelRegistry
from .tools import register_tools


def build_server() -> FastMCP:
    """Create the FastMCP server with a fresh in-memory model registry."""
    mcp = FastMCP("cfast")
    register_tools(mcp, ModelRegistry())
    return mcp


mcp = build_server()


def main() -> None:
    """Console-script entrypoint."""
    mcp.run()


if __name__ == "__main__":
    main()
