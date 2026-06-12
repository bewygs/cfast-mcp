"""Tools for adding and editing devices (targets and detectors)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pycfast import Device

from ..errors import format_warnings, guard_warnings
from ..registry import ModelRegistry


def register_device_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register add_device and update_device."""

    @mcp.tool()
    def add_device(
        model_id: str,
        id: str,
        comp_id: str,
        location: list[float],
        type: str,
        material_id: str | None = None,
        surface_orientation: str | None = None,
        normal: list[float] | None = None,
        thickness: float | None = None,
        temperature_depth: float = 0.5,
        depth_units: str = "M",
        setpoint: float | None = None,
        rti: float | None = None,
        obscuration: float = 23.93,
        spray_density: float | None = None,
    ) -> str:
        """
        Add a device (target or detector) to a compartment of a model.

        Devices are either targets (PLATE, CYLINDER), which heat up and report
        temperature, or detectors (HEAT_DETECTOR, SMOKE_DETECTOR, SPRINKLER).
        The compartment comp_id must already exist. Required fields depend on
        the type: targets need material_id (already added with add_material)
        and exactly one of normal or surface_orientation; HEAT_DETECTOR and
        SPRINKLER need setpoint and rti (SPRINKLER also spray_density).

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        id : str
            Unique name of the target or detector.
        comp_id : str
            Compartment in which the device is located.
        location : list[float]
            Position [x, y, z] as distances from the left wall, the front
            wall, and the floor. Default units: m.
        type : str
            One of PLATE, CYLINDER (targets), HEAT_DETECTOR, SMOKE_DETECTOR,
            SPRINKLER (detectors).
        material_id : str or None, optional
            What the target is made of; must already exist in the model.
            Required for target types (PLATE, CYLINDER).
        surface_orientation : str or None, optional
            Predefined surface orientation for targets: CEILING, FRONT WALL,
            BACK WALL, LEFT WALL, RIGHT WALL or FLOOR. Provide exactly one of
            surface_orientation or normal for a target.
        normal : list[float] or None, optional
            Unit vector [nx, ny, nz] perpendicular to the exposed target
            surface (e.g. [0, 0, 1] faces the ceiling). Provide exactly one of
            normal or surface_orientation for a target.
        thickness : float or None, optional
            Thickness of the target material; if None, the material's value is
            used. Default units: m.
        temperature_depth : float, optional
            Depth at which the internal target temperature is reported. With
            depth_units="M" (default) an absolute depth in meters from the
            front surface, which must be > 0 and less than the material
            thickness; otherwise a fraction of the thickness in [0, 1].
            Default value: 0.5.
        depth_units : str, optional
            Units for temperature_depth: "M" for meters. Default value: M.
        setpoint : float or None, optional
            Temperature at or above which the link activates. Default units:
            °C. Required for HEAT_DETECTOR and SPRINKLER.
        rti : float or None, optional
            Response Time Index for the sprinkler or detector. Default units:
            (m·s)^(1/2). Required for HEAT_DETECTOR and SPRINKLER.
        obscuration : float, optional
            Obscuration at or above which a SMOKE_DETECTOR activates. Default
            units: %/m, default value: 23.93 %/m.
        spray_density : float or None, optional
            Amount of water dispersed by a sprinkler. Default units: m/s.
            Required for SPRINKLER.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        with guard_warnings() as caught:
            device = Device(
                id=id,
                comp_id=comp_id,
                location=location,
                type=type,
                material_id=material_id,
                surface_orientation=surface_orientation,
                normal=normal,
                thickness=thickness,
                temperature_depth=temperature_depth,
                depth_units=depth_units,
                setpoint=setpoint,
                rti=rti,
                obscuration=obscuration,
                spray_density=spray_density,
            )
            new_model = entry.model.add(device)
        registry.set(model_id, new_model)
        return (
            f"Added device '{id}' to '{model_id}'.\n{new_model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def update_device(
        model_id: str,
        device_id: str,
        comp_id: str | None = None,
        location: list[float] | None = None,
        type: str | None = None,
        material_id: str | None = None,
        surface_orientation: str | None = None,
        normal: list[float] | None = None,
        thickness: float | None = None,
        temperature_depth: float | None = None,
        depth_units: str | None = None,
        setpoint: float | None = None,
        rti: float | None = None,
        obscuration: float | None = None,
        spray_density: float | None = None,
    ) -> str:
        """
        Update an existing device (target or detector).

        Selects the device by device_id and changes only the parameters you
        provide; any left as None is unchanged. The device's id is the
        selector and is not changed here.

        Parameters
        ----------
        model_id : str
            Id of the model to modify.
        device_id : str
            Id of the device to update.
        comp_id : str or None, optional
            Compartment in which the device is located. None leaves it
            unchanged.
        location : list[float] or None, optional
            Position [x, y, z] from the left wall, front wall and floor.
            Default units: m. None leaves it unchanged.
        type : str or None, optional
            One of PLATE, CYLINDER, HEAT_DETECTOR, SMOKE_DETECTOR, SPRINKLER.
            None leaves it unchanged.
        material_id : str or None, optional
            What the target is made of; must already exist. None leaves it
            unchanged.
        surface_orientation : str or None, optional
            Predefined surface orientation for targets. None leaves it
            unchanged.
        normal : list[float] or None, optional
            Unit vector [nx, ny, nz] perpendicular to the target surface. None
            leaves it unchanged.
        thickness : float or None, optional
            Thickness of the target material. Default units: m. None leaves it
            unchanged.
        temperature_depth : float or None, optional
            Depth at which the internal target temperature is reported (meters
            when depth_units="M", else a fraction in [0, 1]). None leaves it
            unchanged.
        depth_units : str or None, optional
            Units for temperature_depth: "M" for meters. None leaves it
            unchanged.
        setpoint : float or None, optional
            Activation temperature for HEAT_DETECTOR and SPRINKLER. Default
            units: °C. None leaves it unchanged.
        rti : float or None, optional
            Response Time Index. Default units: (m·s)^(1/2). None leaves it
            unchanged.
        obscuration : float or None, optional
            Obscuration at or above which a SMOKE_DETECTOR activates. Default
            units: %/m. None leaves it unchanged.
        spray_density : float or None, optional
            Amount of water dispersed by a sprinkler. Default units: m/s. None
            leaves it unchanged.

        Returns
        -------
        str
            Confirmation, the updated model summary, and any warnings.
        """
        entry = registry.get(model_id)
        updates: dict[str, object] = {
            name: value
            for name, value in (
                ("comp_id", comp_id),
                ("location", location),
                ("type", type),
                ("material_id", material_id),
                ("surface_orientation", surface_orientation),
                ("normal", normal),
                ("thickness", thickness),
                ("temperature_depth", temperature_depth),
                ("depth_units", depth_units),
                ("setpoint", setpoint),
                ("rti", rti),
                ("obscuration", obscuration),
                ("spray_density", spray_density),
            )
            if value is not None
        }
        if not updates:
            raise ToolError(
                "No parameters to update; provide at least one field to change."
            )
        with guard_warnings() as caught:
            new_model = entry.model.update_device_params(device_id, **updates)
        registry.set(model_id, new_model)
        return (
            f"Updated device '{device_id}' in '{model_id}'."
            f"\n{new_model.summary()}{format_warnings(caught)}"
        )
