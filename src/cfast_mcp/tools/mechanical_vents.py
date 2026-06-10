"""Tools for adding and editing mechanical (fan/HVAC) vents."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pycfast import MechanicalVent

from ..errors import ToolError, format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_mechanical_vent_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_mechanical_vent and update_mechanical_vent."""

    @mcp.tool()
    def add_mechanical_vent(
        model_id: str,
        id: str,
        comp_from: str,
        comp_to: str,
        flow: float,
        area: list[float] | None = None,
        heights: list[float] | None = None,
        orientations: list[str] | None = None,
        cutoffs: list[float] | None = None,
        offsets: list[float] | None = None,
        filter_time: float = 0,
        filter_efficiency: float = 0,
    ) -> str:
        """
        Add a mechanical vent between two compartments.

        Mechanical ventilation moves air at a user-specified volume flow
        between two compartments, or between a compartment and the outside.
        Both compartments must already exist in the model; comp_from or
        comp_to may be "OUTSIDE".

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        id : str
            Unique name of the mechanical ventilation system.
        comp_from : str
            Compartment from which the fan flow originates, or "OUTSIDE".
        comp_to : str
            Compartment to which the fan flow terminates, or "OUTSIDE".
        flow : float
            Constant volumetric flow rate of the fan. Default units: m³/s.
        area : list[float] or None, optional
            Cross-sectional area of the opening for each connection
            [area_from, area_to]. Default units: m², default value: [0, 0] m².
        heights : list[float] or None, optional
            Height of the midpoint of the duct opening above the floor for
            each connection [height_from, height_to]. Default units: m,
            default value: [0, 0] m.
        orientations : list[str] or None, optional
            Flow orientation for each connection, HORIZONTAL or VERTICAL. A
            horizontal diffuser implies vertical flow through the ceiling or
            floor; a vertical diffuser implies horizontal flow through a wall.
            Default value: ["VERTICAL", "VERTICAL"].
        cutoffs : list[float] or None, optional
            Pressure control values [begin_drop_off_pressure,
            zero_flow_pressure]: above the first the flow drops off, above the
            second it is zero. Default units: Pa, default value: [200, 300] Pa.
        offsets : list[float] or None, optional
            For visualization only, [x_offset, y_offset] horizontal distances
            between the center of the vent and the origin of the X and Y axes
            in the first compartment. Default units: m, default value:
            [0, 0] m.
        filter_time : float, optional
            Time at which mechanical vent filtering begins. Default units: s,
            default value: 0 s.
        filter_efficiency : float, optional
            Portion of soot and trace species mass removed from the flow,
            specified as a percentage (0-100). Default value: 0.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        with guard_warnings() as caught:
            vent = MechanicalVent(
                id=id,
                comps_ids=[comp_from, comp_to],
                area=area,
                heights=heights,
                orientations=orientations,
                flow=flow,
                cutoffs=cutoffs,
                offsets=offsets,
                filter_time=filter_time,
                filter_efficiency=filter_efficiency,
            )
            new_model = entry.model.add(vent)
        registry.set(model_id, new_model)
        return (
            f"Added mechanical vent '{id}' to '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_mechanical_vent(
        model_id: str,
        vent_id: str,
        comp_from: str | None = None,
        comp_to: str | None = None,
        flow: float | None = None,
        area: list[float] | None = None,
        heights: list[float] | None = None,
        orientations: list[str] | None = None,
        cutoffs: list[float] | None = None,
        offsets: list[float] | None = None,
        filter_time: float | None = None,
        filter_efficiency: float | None = None,
    ) -> str:
        """
        Update an existing mechanical vent.

        Selects the vent by vent_id and changes only the parameters you
        provide; any left as None is unchanged. The vent's id is the selector
        and is not changed here.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        vent_id : str
            Id of the mechanical vent to update.
        comp_from : str or None, optional
            Compartment from which the fan flow originates, or "OUTSIDE". To
            change the connection, provide both comp_from and comp_to. None
            leaves the connection unchanged.
        comp_to : str or None, optional
            Compartment to which the fan flow terminates, or "OUTSIDE". To
            change the connection, provide both comp_from and comp_to. None
            leaves the connection unchanged.
        flow : float or None, optional
            Constant volumetric flow rate of the fan. Default units: m³/s.
            None leaves it unchanged.
        area : list[float] or None, optional
            Cross-sectional area of the opening for each connection
            [area_from, area_to]. Default units: m². None leaves it unchanged.
        heights : list[float] or None, optional
            Height of the midpoint of the duct opening above the floor for
            each connection [height_from, height_to]. Default units: m. None
            leaves it unchanged.
        orientations : list[str] or None, optional
            Flow orientation for each connection, HORIZONTAL or VERTICAL. None
            leaves it unchanged.
        cutoffs : list[float] or None, optional
            Pressure control values [begin_drop_off_pressure,
            zero_flow_pressure]. Default units: Pa. None leaves it unchanged.
        offsets : list[float] or None, optional
            For visualization only, [x_offset, y_offset]. Default units: m.
            None leaves it unchanged.
        filter_time : float or None, optional
            Time at which mechanical vent filtering begins. Default units: s.
            None leaves it unchanged.
        filter_efficiency : float or None, optional
            Portion of soot and trace species mass removed (0-100 %). None
            leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        if (comp_from is None) != (comp_to is None):
            raise ToolError(
                "To change the connection, provide both comp_from and comp_to "
                "(either may be 'OUTSIDE')."
            )
        updates: dict[str, object] = {
            name: value
            for name, value in (
                ("flow", flow),
                ("area", area),
                ("heights", heights),
                ("orientations", orientations),
                ("cutoffs", cutoffs),
                ("offsets", offsets),
                ("filter_time", filter_time),
                ("filter_efficiency", filter_efficiency),
            )
            if value is not None
        }
        if comp_from is not None and comp_to is not None:
            updates["comps_ids"] = [comp_from, comp_to]
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            new_model = entry.model.update_mechanical_vent_params(vent_id, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated mechanical vent '{vent_id}' in '{model_id}'."
            f"\n{new_model.summary()}{format_warnings(caught)}"
        )
