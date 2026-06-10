"""Tools for adding and editing surface connections."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pycfast import SurfaceConnection

from ..errors import ToolError, format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_surface_connection_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_surface_connection and update_surface_connection."""

    @mcp.tool()
    def add_surface_connection(
        model_id: str,
        conn_type: str,
        comp_id: str,
        comp_ids: str,
        fraction: float | None = None,
    ) -> str:
        """
        Add a surface connection between compartments.

        Surface connections transfer heat through solid boundaries between two
        compartments. Both compartments must already exist in the model.
        Unlike other components, a surface connection has no id; refer to it by
        its position (index) when updating. For WALL connections you should add
        one in each direction (comp_id -> comp_ids and comp_ids -> comp_id).

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        conn_type : str
            Type of connection: WALL for horizontal heat transfer through
            vertical surfaces, FLOOR for vertical heat transfer through
            horizontal surfaces.
        comp_id : str
            First compartment id. For WALL, the compartment whose wall area
            fraction is given; for FLOOR, the top compartment (through its
            floor).
        comp_ids : str
            Second compartment id. For FLOOR, the bottom compartment (through
            its ceiling).
        fraction : float or None, optional
            Fraction (0-1) of the first compartment's vertical surface area
            that connects the two compartments. Required for WALL connections;
            must be None for FLOOR connections.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        with guard_warnings() as caught:
            conn = SurfaceConnection(
                conn_type=conn_type,
                comp_id=comp_id,
                comp_ids=comp_ids,
                fraction=fraction,
            )
            new_model = entry.model.add(conn)
        registry.set(model_id, new_model)
        return (
            f"Added surface connection {comp_id!r} -> {comp_ids!r} to "
            f"'{model_id}'.\n{new_model.summary()}{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_surface_connection(
        model_id: str,
        index: int,
        conn_type: str | None = None,
        comp_id: str | None = None,
        comp_ids: str | None = None,
        fraction: float | None = None,
    ) -> str:
        """
        Update an existing surface connection.

        Surface connections have no id, so they are selected by index (their
        0-based position in the order they were added). Only the parameters
        you provide change; any left as None is unchanged.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        index : int
            0-based position of the surface connection to update.
        conn_type : str or None, optional
            Type of connection: WALL or FLOOR. None leaves it unchanged.
        comp_id : str or None, optional
            First compartment id. None leaves it unchanged.
        comp_ids : str or None, optional
            Second compartment id. None leaves it unchanged.
        fraction : float or None, optional
            Fraction (0-1) of connected vertical surface area, for WALL
            connections. None leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        updates = {
            name: value
            for name, value in (
                ("conn_type", conn_type),
                ("comp_id", comp_id),
                ("comp_ids", comp_ids),
                ("fraction", fraction),
            )
            if value is not None
        }
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            new_model = entry.model.update_surface_connection_params(index, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated surface connection #{index} in '{model_id}'."
            f"\n{new_model.summary()}{format_warnings(caught)}"
        )
