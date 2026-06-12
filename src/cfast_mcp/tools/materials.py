"""Tools for adding and editing materials."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pycfast import Material

from ..errors import format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_material_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_material and update_material."""

    @mcp.tool()
    def add_material(
        model_id: str,
        id: str,
        material: str,
        conductivity: float,
        density: float,
        specific_heat: float,
        thickness: float,
        emissivity: float = 0.9,
    ) -> str:
        """
        Add a material to a model.

        A compartment can reference this material by id for its ceiling,
        wall or floor surfaces, or a target.

        Parameters
        ----------
        model_id : str
            Id of the model to modify, as returned by create_model.
        id : str
            A one-word (no more than 8 characters) unique identifier for the
            material, used in other inputs to reference it.
        material : str
            A descriptive name for the material.
        conductivity : float
            Thermal conductivity for the material. Default units: W/(m·K).
        density : float
            Density for the material. Default units: kg/m³.
        specific_heat : float
            Specific heat for the material. Default units: kJ/(kg·K).
        thickness : float
            Thickness of the material. Default units: m.
        emissivity : float, optional
            Emissivity of the material surface; the fraction of radiation
            that is absorbed by the material. Default units: none, default
            value: 0.9.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        with guard_warnings() as caught:
            entry = registry.get(model_id)
            mat = Material(
                id=id,
                material=material,
                conductivity=conductivity,
                density=density,
                specific_heat=specific_heat,
                thickness=thickness,
                emissivity=emissivity,
            )
            new_model = entry.model.add(mat)
        registry.set(model_id, new_model)
        return (
            f"Added material '{id}' to '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_material(
        model_id: str,
        material_id: str,
        conductivity: float | None = None,
        density: float | None = None,
        specific_heat: float | None = None,
        thickness: float | None = None,
        emissivity: float | None = None,
    ) -> str:
        """
        Update thermophysical properties of an existing material.

        Selects the material by material_id and changes only the parameters
        you provide; any left as None is unchanged. The material's id is the
        selector and is not changed here.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        material_id : str
            Id of the material to update.
        conductivity : float or None, optional
            Thermal conductivity for the material. Default units: W/(m·K).
            None leaves it unchanged.
        density : float or None, optional
            Density for the material. Default units: kg/m³. None leaves it
            unchanged.
        specific_heat : float or None, optional
            Specific heat for the material. Default units: kJ/(kg·K). None
            leaves it unchanged.
        thickness : float or None, optional
            Thickness of the material. Default units: m. None leaves it
            unchanged.
        emissivity : float or None, optional
            Emissivity of the material surface; the fraction of radiation
            that is absorbed by the material. Default units: none. None
            leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        updates = {
            name: value
            for name, value in (
                ("conductivity", conductivity),
                ("density", density),
                ("specific_heat", specific_heat),
                ("thickness", thickness),
                ("emissivity", emissivity),
            )
            if value is not None
        }
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            entry = registry.get(model_id)
            new_model = entry.model.update_material_params(material_id, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated material '{material_id}' in '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )
