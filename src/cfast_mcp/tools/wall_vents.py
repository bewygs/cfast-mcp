"""Tools for adding and editing wall vents."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pycfast import WallVent

from ..errors import ToolError, format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_wall_vent_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_wall_vent and update_wall_vent."""

    @mcp.tool()
    def add_wall_vent(
        model_id: str,
        id: str,
        comp_a: str,
        comp_b: str,
        bottom: float,
        height: float,
        width: float,
        face: str,
        offset: float = 0,
    ) -> str:
        """
        Add a wall vent (door, window or opening) between two compartments.

        Wall vents connect compartments that physically overlap in elevation,
        or connect a compartment to the outside. Both compartments must
        already exist in the model; comp_b may be "OUTSIDE" to vent to the
        exterior. All specifications of the vent are made relative to the
        floor of the first compartment.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        id : str
            Unique name of the vent.
        comp_a : str
            First compartment id; the reference for all vent specifications.
        comp_b : str
            Second compartment id, or "OUTSIDE" for the exterior.
        bottom : float
            Position of the bottom of the opening relative to the floor of
            the first compartment. Default units: m.
        height : float
            Height of the opening relative to the bottom of the opening.
            Default units: m.
        width : float
            Width of the opening. Default units: m.
        face : str
            The wall on which the vent is positioned. Choices are FRONT,
            REAR, LEFT, RIGHT; Front and Rear faces are parallel to the
            X axis, Left and Right to the Y axis.
        offset : float, optional
            For visualization only, the horizontal distance between the near
            edge of the vent and the origin of the axis defined by the
            selected face. Default units: m, default value: 0 m.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        face_u = face.upper()
        if face_u not in {"FRONT", "REAR", "LEFT", "RIGHT"}:
            raise ToolError(
                f"face must be one of FRONT, REAR, LEFT, RIGHT — got {face!r}."
            )
        entry = registry.get(model_id)
        with guard_warnings() as caught:
            vent = WallVent(
                id=id,
                comps_ids=[comp_a, comp_b],
                bottom=bottom,
                height=height,
                width=width,
                face=face_u,
                offset=offset,
            )
            new_model = entry.model.add(vent)
        registry.set(model_id, new_model)
        return (
            f"Added wall vent '{id}' to '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_wall_vent(
        model_id: str,
        vent_id: str,
        comp_a: str | None = None,
        comp_b: str | None = None,
        bottom: float | None = None,
        height: float | None = None,
        width: float | None = None,
        face: str | None = None,
        offset: float | None = None,
    ) -> str:
        """
        Update an existing wall vent.

        Selects the vent by vent_id and changes only the parameters you
        provide; any left as None is unchanged. The vent's id is the selector
        and is not changed here.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        vent_id : str
            Id of the wall vent to update.
        comp_a : str or None, optional
            First compartment id; the reference for all vent specifications.
            To change the connection, provide both comp_a and comp_b. None
            leaves the connection unchanged.
        comp_b : str or None, optional
            Second compartment id, or "OUTSIDE" for the exterior. To change
            the connection, provide both comp_a and comp_b. None leaves the
            connection unchanged.
        bottom : float or None, optional
            Position of the bottom of the opening relative to the floor of
            the first compartment. Default units: m. None leaves it
            unchanged.
        height : float or None, optional
            Height of the opening relative to the bottom of the opening.
            Default units: m. None leaves it unchanged.
        width : float or None, optional
            Width of the opening. Default units: m. None leaves it unchanged.
        face : str or None, optional
            The wall on which the vent is positioned: FRONT, REAR, LEFT or
            RIGHT. None leaves it unchanged.
        offset : float or None, optional
            For visualization only, the horizontal distance between the near
            edge of the vent and the origin of the axis defined by the
            selected face. Default units: m. None leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        if (comp_a is None) != (comp_b is None):
            raise ToolError(
                "To change the connection, provide both comp_a and comp_b "
                "(comp_b may be 'OUTSIDE')."
            )
        updates: dict[str, object] = {
            name: value
            for name, value in (
                ("bottom", bottom),
                ("height", height),
                ("width", width),
                ("offset", offset),
            )
            if value is not None
        }
        if face is not None:
            face_u = face.upper()
            if face_u not in {"FRONT", "REAR", "LEFT", "RIGHT"}:
                raise ToolError(
                    f"face must be one of FRONT, REAR, LEFT, RIGHT — got {face!r}."
                )
            updates["face"] = face_u
        if comp_a is not None and comp_b is not None:
            updates["comps_ids"] = [comp_a, comp_b]
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            new_model = entry.model.update_wall_vent_params(vent_id, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated wall vent '{vent_id}' in '{model_id}'."
            f"\n{new_model.summary()}{format_warnings(caught)}"
        )
