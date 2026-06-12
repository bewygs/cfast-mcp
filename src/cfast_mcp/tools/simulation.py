"""Tools for editing the model's simulation environment."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from ..errors import format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_simulation_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register update_simulation."""

    @mcp.tool()
    def update_simulation(
        model_id: str,
        title: str | None = None,
        time_simulation: int | None = None,
        interior_temperature: float | None = None,
        exterior_temperature: float | None = None,
        relative_humidity: float | None = None,
    ) -> str:
        """
        Update the simulation environment (scenario and ambient conditions).

        A model has a single simulation environment, set at create_model;
        this changes only the parameters you provide; any left as None is
        unchanged.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        title : str or None, optional
            Title of the simulation. May consist of letters, numbers, and/or
            symbols and may be up to 50 characters. None leaves it unchanged.
        time_simulation : int or None, optional
            Length of time over which the simulation takes place. Default
            units: s. None leaves it unchanged.
        interior_temperature : float or None, optional
            Initial ambient temperature inside the structure. Default units:
            °C. None leaves it unchanged.
        exterior_temperature : float or None, optional
            Initial ambient temperature outside the structure. Default units:
            °C. None leaves it unchanged.
        relative_humidity : float or None, optional
            Initial relative humidity, only specified for the interior.
            Default units: % RH. None leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        updates = {
            name: value
            for name, value in (
                ("title", title),
                ("time_simulation", time_simulation),
                ("interior_temperature", interior_temperature),
                ("exterior_temperature", exterior_temperature),
                ("relative_humidity", relative_humidity),
            )
            if value is not None
        }
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            new_model = entry.model.update_simulation_params(**updates)
        registry.set(model_id, new_model)
        return (
            f"Updated simulation environment of '{model_id}'."
            f"\n{new_model.summary()}{format_warnings(caught)}"
        )
