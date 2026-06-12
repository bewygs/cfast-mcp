"""Tools for adding and editing fires."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pycfast import Fire

from ..errors import format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_fire_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_fire and update_fire."""

    @mcp.tool()
    def add_fire(
        model_id: str,
        id: str,
        comp_id: str,
        fire_id: str,
        location: list[float],
        data_table: list[list[float]],
        carbon: float = 1,
        chlorine: float = 0,
        hydrogen: float = 4,
        nitrogen: float = 0,
        oxygen: float = 0,
        heat_of_combustion: float = 50000,
        radiative_fraction: float = 0.35,
    ) -> str:
        """
        Add a fire to a compartment of a model.

        A fire in CFAST is specified via a time-dependent heat release rate
        (HRR). The compartment comp_id must already exist in the model. Fire
        properties are linearly interpolated between specified time points;
        if the simulation time is longer than the total duration of the fire,
        the final values are continued until the end of the simulation.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        id : str
            Unique name of the fire instance.
        comp_id : str
            Name of the compartment where the fire occurs.
        fire_id : str
            Unique name of the fire definition (fuel composition and HRR
            curve). May be the same as id.
        location : list[float]
            Position [x, y] of the center of the base of the fire relative
            to the front left corner of the compartment. Default units: m.
        data_table : list[list[float]]
            Time-dependent fire properties: one row per time point, with
            columns [TIME (s), HRR (kW), HEIGHT (m), AREA (m²), CO_YIELD,
            SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD], yields in kg/kg.
            Example for a fire growing to 1000 kW at 300 s:
            [[0, 0, 0, 0.3, 0.005, 0.02, 0, 0, 0],
            [300, 1000, 0, 0.3, 0.005, 0.02, 0, 0, 0]].
        carbon : float, optional
            Number of carbon atoms in the fuel molecule. Default value: 1.
        chlorine : float, optional
            Number of chlorine atoms in the fuel molecule; assumed to
            completely react to form HCl. Default value: 0.
        hydrogen : float, optional
            Number of hydrogen atoms in the fuel molecule. Default value: 4.
        nitrogen : float, optional
            Number of nitrogen atoms in the fuel molecule; assumed to
            completely react to form HCN. Default value: 0.
        oxygen : float, optional
            Number of oxygen atoms in the fuel molecule. Default value: 0.
        heat_of_combustion : float, optional
            The energy released per unit mass of fuel consumed. Default
            units: kJ/kg, default value: 50000 kJ/kg.
        radiative_fraction : float, optional
            The fraction of the combustion energy that is emitted in the
            form of thermal radiation. Default units: none, default
            value: 0.35.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings (for
            example a fire located outside the compartment footprint).
        """
        entry = registry.get(model_id)
        with guard_warnings() as caught:
            fire = Fire(
                id=id,
                comp_id=comp_id,
                fire_id=fire_id,
                location=location,
                carbon=carbon,
                chlorine=chlorine,
                hydrogen=hydrogen,
                nitrogen=nitrogen,
                oxygen=oxygen,
                heat_of_combustion=heat_of_combustion,
                radiative_fraction=radiative_fraction,
                data_table=data_table,
            )
            new_model = entry.model.add(fire)
        registry.set(model_id, new_model)
        return (
            f"Added fire '{id}' to '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_fire(
        model_id: str,
        id: str,
        comp_id: str | None = None,
        fire_id: str | None = None,
        location: list[float] | None = None,
        data_table: list[list[float]] | None = None,
        carbon: float | None = None,
        chlorine: float | None = None,
        hydrogen: float | None = None,
        nitrogen: float | None = None,
        oxygen: float | None = None,
        heat_of_combustion: float | None = None,
        radiative_fraction: float | None = None,
    ) -> str:
        """
        Update an existing fire.

        Selects the fire by its instance id and changes only the parameters
        you provide; any left as None is unchanged. The fire instance id is
        the selector and is not changed here. Changing comp_id moves the fire
        to another compartment, which must already exist.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        id : str
            Id of the fire instance to update.
        comp_id : str or None, optional
            Name of the compartment where the fire occurs. None leaves it
            unchanged.
        fire_id : str or None, optional
            Name of the fire definition (fuel composition and HRR curve).
            None leaves it unchanged.
        location : list[float] or None, optional
            Position [x, y] of the center of the base of the fire relative
            to the front left corner of the compartment. Default units: m.
            None leaves it unchanged.
        data_table : list[list[float]] or None, optional
            Time-dependent fire properties: one row per time point, with
            columns [TIME (s), HRR (kW), HEIGHT (m), AREA (m²), CO_YIELD,
            SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD], yields in kg/kg.
            None leaves it unchanged.
        carbon : float or None, optional
            Number of carbon atoms in the fuel molecule. None leaves it
            unchanged.
        chlorine : float or None, optional
            Number of chlorine atoms in the fuel molecule; assumed to
            completely react to form HCl. None leaves it unchanged.
        hydrogen : float or None, optional
            Number of hydrogen atoms in the fuel molecule. None leaves it
            unchanged.
        nitrogen : float or None, optional
            Number of nitrogen atoms in the fuel molecule; assumed to
            completely react to form HCN. None leaves it unchanged.
        oxygen : float or None, optional
            Number of oxygen atoms in the fuel molecule. None leaves it
            unchanged.
        heat_of_combustion : float or None, optional
            The energy released per unit mass of fuel consumed. Default
            units: kJ/kg. None leaves it unchanged.
        radiative_fraction : float or None, optional
            The fraction of the combustion energy that is emitted in the
            form of thermal radiation. Default units: none. None leaves it
            unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings (for
            example a fire located outside the compartment footprint).
        """
        entry = registry.get(model_id)
        updates: dict[str, object] = {
            name: value
            for name, value in (
                ("comp_id", comp_id),
                ("fire_id", fire_id),
                ("location", location),
                ("data_table", data_table),
                ("carbon", carbon),
                ("chlorine", chlorine),
                ("hydrogen", hydrogen),
                ("nitrogen", nitrogen),
                ("oxygen", oxygen),
                ("heat_of_combustion", heat_of_combustion),
                ("radiative_fraction", radiative_fraction),
            )
            if value is not None
        }
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            new_model = entry.model.update_fire_params(id, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated fire '{id}' in '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )
