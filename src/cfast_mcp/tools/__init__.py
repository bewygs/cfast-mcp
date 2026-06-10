"""
MCP tool definitions for building, running and reading CFAST models.

Each tool operates on a model stored in a :class:`~cfast_mcp.registry.ModelRegistry`
and wraps pycfast calls with :mod:`cfast_mcp.errors`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..registry import ModelRegistry
from .ceiling_floor_vents import register_ceiling_floor_vent_tools
from .compartments import register_compartment_tools
from .devices import register_device_tools
from .fires import register_fire_tools
from .materials import register_material_tools
from .mechanical_vents import register_mechanical_vent_tools
from .model import register_model_tools
from .simulation import register_simulation_tools
from .surface_connections import register_surface_connection_tools
from .wall_vents import register_wall_vent_tools


def register_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register all tools on ``mcp``, sharing the ``registry``."""
    register_model_tools(mcp, registry)
    register_simulation_tools(mcp, registry)
    register_material_tools(mcp, registry)
    register_compartment_tools(mcp, registry)
    register_wall_vent_tools(mcp, registry)
    register_ceiling_floor_vent_tools(mcp, registry)
    register_mechanical_vent_tools(mcp, registry)
    register_fire_tools(mcp, registry)
    register_device_tools(mcp, registry)
    register_surface_connection_tools(mcp, registry)
