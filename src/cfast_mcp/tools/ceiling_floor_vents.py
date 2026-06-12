"""Tools for adding and editing ceiling/floor (vertical flow) vents."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pycfast import CeilingFloorVent

from ..errors import format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_ceiling_floor_vent_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_ceiling_floor_vent and update_ceiling_floor_vent."""

    @mcp.tool()
    def add_ceiling_floor_vent(
        model_id: str,
        id: str,
        comp_top: str,
        comp_bottom: str,
        area: float,
        type: str = "FLOOR",
        shape: str = "ROUND",
        offsets: list[float] | None = None,
    ) -> str:
        """
        Add a ceiling/floor vent (vertical flow opening) between compartments.

        Vertical flow vents connect compartments stacked in elevation, or a
        compartment to the outside (e.g. a hole in a roof). Both compartments
        must already exist in the model; comp_bottom may be "OUTSIDE".

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        id : str
            Unique name of the vent.
        comp_top : str
            Top compartment id, where the vent is in the floor.
        comp_bottom : str
            Bottom compartment id, where the vent is in the ceiling, or
            "OUTSIDE" for the exterior.
        area : float
            Cross-sectional area of the vent opening. Default units: m².
        type : str, optional
            Type of ceiling/floor vent: FLOOR or CEILING. Default value:
            FLOOR.
        shape : str, optional
            Shape factor used to compute the effective diameter and flow
            coefficients: ROUND or SQUARE. Default value: ROUND.
        offsets : list[float] or None, optional
            For visualization only, [x_offset, y_offset] horizontal distances
            between the center of the vent and the origin of the X and Y axes
            in the upper compartment. Default units: m, default value:
            [0, 0] m.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        with guard_warnings() as caught:
            entry = registry.get(model_id)
            vent = CeilingFloorVent(
                id=id,
                comps_ids=[comp_top, comp_bottom],
                area=area,
                type=type,
                shape=shape,
                offsets=offsets,
            )
            new_model = entry.model.add(vent)
        registry.set(model_id, new_model)
        return (
            f"Added ceiling/floor vent '{id}' to '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_ceiling_floor_vent(
        model_id: str,
        vent_id: str,
        comp_top: str | None = None,
        comp_bottom: str | None = None,
        area: float | None = None,
        type: str | None = None,
        shape: str | None = None,
        offsets: list[float] | None = None,
    ) -> str:
        """
        Update an existing ceiling/floor vent.

        Selects the vent by vent_id and changes only the parameters you
        provide; any left as None is unchanged. The vent's id is the selector
        and is not changed here.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        vent_id : str
            Id of the ceiling/floor vent to update.
        comp_top : str or None, optional
            Top compartment id, where the vent is in the floor. To change the
            connection, provide both comp_top and comp_bottom. None leaves the
            connection unchanged.
        comp_bottom : str or None, optional
            Bottom compartment id, or "OUTSIDE". To change the connection,
            provide both comp_top and comp_bottom. None leaves the connection
            unchanged.
        area : float or None, optional
            Cross-sectional area of the vent opening. Default units: m². None
            leaves it unchanged.
        type : str or None, optional
            Type of ceiling/floor vent: FLOOR or CEILING. None leaves it
            unchanged.
        shape : str or None, optional
            Shape factor: ROUND or SQUARE. None leaves it unchanged.
        offsets : list[float] or None, optional
            For visualization only, [x_offset, y_offset]. Default units: m.
            None leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        if (comp_top is None) != (comp_bottom is None):
            raise ToolError(
                "To change the connection, provide both comp_top and comp_bottom "
                "(comp_bottom may be 'OUTSIDE')."
            )
        updates: dict[str, object] = {
            name: value
            for name, value in (
                ("area", area),
                ("type", type),
                ("shape", shape),
                ("offsets", offsets),
            )
            if value is not None
        }
        if comp_top is not None and comp_bottom is not None:
            updates["comps_ids"] = [comp_top, comp_bottom]
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            entry = registry.get(model_id)
            new_model = entry.model.update_ceiling_floor_vent_params(vent_id, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated ceiling/floor vent '{vent_id}' in '{model_id}'."
            f"\n{new_model.summary()}{format_warnings(caught)}"
        )
