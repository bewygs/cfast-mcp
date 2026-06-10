"""Fixtures for testing the cfast-mcp server."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest
from mcp.server.fastmcp import FastMCP

from cfast_mcp.registry import ModelRegistry
from cfast_mcp.tools import register_tools


@pytest.fixture
def fire_table() -> list[list[float]]:
    """Minimal fire curve ramp from 0 to 1000 kW at 300 s."""
    return [
        [0, 0, 0, 0.3, 0.005, 0.02, 0, 0, 0],
        [300, 1000, 0, 0.3, 0.005, 0.02, 0, 0, 0],
    ]


@pytest.fixture
def registry() -> ModelRegistry:
    return ModelRegistry()


@pytest.fixture
def server(registry: ModelRegistry) -> FastMCP:
    mcp = FastMCP("pycfast-test")
    register_tools(mcp, registry)
    return mcp


@pytest.fixture
def call(server: FastMCP) -> Callable[..., str]:
    """Call a tool by name on the test server and return its text result."""

    def _call(tool: str, **arguments: object) -> str:
        content, _ = asyncio.run(server.call_tool(tool, arguments))
        return content[0].text

    return _call


@pytest.fixture
def model_id(call: Callable[..., str]) -> str:
    """Register a model with one 3.6 x 2.4 x 2.4 m compartment 'ROOM1'."""
    call(
        "create_model",
        title="Test",
        room_id="ROOM1",
        room_width=3.6,
        room_depth=2.4,
        room_height=2.4,
    )
    return "m1"
