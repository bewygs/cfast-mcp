"""MCP server exposing the pycfast / CFAST API."""

from importlib.metadata import version

from .registry import ModelRegistry
from .server import build_server, mcp

__all__ = ["ModelRegistry", "build_server", "mcp"]

__version__ = version("cfast-mcp")
__author__ = "WYGAS Benoît"