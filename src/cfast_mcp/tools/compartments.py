"""Tools for adding and editing compartments."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pycfast import Compartment

from ..errors import format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_compartment_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_compartment and update_compartment."""

    @mcp.tool()
    def add_compartment(
        model_id: str,
        id: str,
        width: float,
        depth: float,
        height: float,
        ceiling_mat_id: str | None = None,
        ceiling_thickness: float | None = None,
        wall_mat_id: str | None = None,
        wall_thickness: float | None = None,
        floor_mat_id: str | None = None,
        floor_thickness: float | None = None,
        origin_x: float = 0,
        origin_y: float = 0,
        origin_z: float = 0,
    ) -> str:
        """
        Add a compartment to a model.

        Any surface material id given (ceiling, wall, floor) must already
        exist in the model — add it first with add_material. If the
        thermophysical properties of a surface are not included, CFAST
        treats it as adiabatic (no heat transfer).

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        id : str
            Unique alphanumeric name of the compartment, referenced later by
            fires and wall vents.
        width : float
            Width of the compartment as measured on the X axis from its
            origin. Default units: m.
        depth : float
            Depth of the compartment as measured on the Y axis from its
            origin. Default units: m.
        height : float
            Height of the compartment as measured on the Z axis from its
            origin. Default units: m.
        ceiling_mat_id : str or None, optional
            Material id defining the ceiling surface. Default value: Off.
        ceiling_thickness : float or None, optional
            Thickness of the ceiling surface. Default units: m, default
            value: thickness of the material.
        wall_mat_id : str or None, optional
            Material id defining the wall surfaces. Default value: Off.
        wall_thickness : float or None, optional
            Thickness of the wall surfaces. Default units: m, default value:
            thickness of the material.
        floor_mat_id : str or None, optional
            Material id defining the floor surface. Default value: Off.
        floor_thickness : float or None, optional
            Thickness of the floor surface. Default units: m, default value:
            thickness of the material.
        origin_x : float, optional
            Absolute x coordinate of the lower, left, front corner of the
            room. Negative values are not allowed. Default units: m, default
            value: 0.0 m.
        origin_y : float, optional
            Absolute y coordinate of the lower, left, front corner of the
            room. Negative values are not allowed. Default units: m, default
            value: 0.0 m.
        origin_z : float, optional
            Height of the floor of the compartment with respect to the
            station elevation. Default units: m, default value: 0.0 m.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        with guard_warnings() as caught:
            entry = registry.get(model_id)
            comp = Compartment(
                id=id,
                width=width,
                depth=depth,
                height=height,
                ceiling_mat_id=ceiling_mat_id,
                ceiling_thickness=ceiling_thickness,
                wall_mat_id=wall_mat_id,
                wall_thickness=wall_thickness,
                floor_mat_id=floor_mat_id,
                floor_thickness=floor_thickness,
                origin_x=origin_x,
                origin_y=origin_y,
                origin_z=origin_z,
            )
            new_model = entry.model.add(comp)
        registry.set(model_id, new_model)
        return (
            f"Added compartment '{id}' to '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_compartment(
        model_id: str,
        comp_id: str,
        width: float | None = None,
        depth: float | None = None,
        height: float | None = None,
        ceiling_mat_id: str | None = None,
        ceiling_thickness: float | None = None,
        wall_mat_id: str | None = None,
        wall_thickness: float | None = None,
        floor_mat_id: str | None = None,
        floor_thickness: float | None = None,
        origin_x: float | None = None,
        origin_y: float | None = None,
        origin_z: float | None = None,
    ) -> str:
        """
        Update parameters of an existing compartment.

        Selects the compartment by comp_id and changes only the parameters
        you provide; any left as None is unchanged. Use this to attach
        surface materials to the first compartment (created bare by
        create_model) or to revise any compartment later. Any surface
        material id given must already exist in the model — add it first
        with add_material. The compartment's id itself is the selector and
        is not changed here.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        comp_id : str
            Id of the compartment to update.
        width : float or None, optional
            New width of the compartment as measured on the X axis from its
            origin. Default units: m. None leaves it unchanged.
        depth : float or None, optional
            New depth of the compartment as measured on the Y axis from its
            origin. Default units: m. None leaves it unchanged.
        height : float or None, optional
            New height of the compartment as measured on the Z axis from its
            origin. Default units: m. None leaves it unchanged.
        ceiling_mat_id : str or None, optional
            Material id defining the ceiling surface. None leaves it
            unchanged.
        ceiling_thickness : float or None, optional
            Thickness of the ceiling surface. Default units: m. None leaves
            it unchanged.
        wall_mat_id : str or None, optional
            Material id defining the wall surfaces. None leaves it unchanged.
        wall_thickness : float or None, optional
            Thickness of the wall surfaces. Default units: m. None leaves it
            unchanged.
        floor_mat_id : str or None, optional
            Material id defining the floor surface. None leaves it unchanged.
        floor_thickness : float or None, optional
            Thickness of the floor surface. Default units: m. None leaves it
            unchanged.
        origin_x : float or None, optional
            Absolute x coordinate of the lower, left, front corner of the
            room. Negative values are not allowed. Default units: m. None
            leaves it unchanged.
        origin_y : float or None, optional
            Absolute y coordinate of the lower, left, front corner of the
            room. Negative values are not allowed. Default units: m. None
            leaves it unchanged.
        origin_z : float or None, optional
            Height of the floor of the compartment with respect to the
            station elevation. Default units: m. None leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        updates = {
            name: value
            for name, value in (
                ("width", width),
                ("depth", depth),
                ("height", height),
                ("ceiling_mat_id", ceiling_mat_id),
                ("ceiling_thickness", ceiling_thickness),
                ("wall_mat_id", wall_mat_id),
                ("wall_thickness", wall_thickness),
                ("floor_mat_id", floor_mat_id),
                ("floor_thickness", floor_thickness),
                ("origin_x", origin_x),
                ("origin_y", origin_y),
                ("origin_z", origin_z),
            )
            if value is not None
        }
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            entry = registry.get(model_id)
            new_model = entry.model.update_compartment_params(comp_id, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated compartment '{comp_id}' in '{model_id}'."
            f"\n{new_model.summary()}{format_warnings(caught)}"
        )
