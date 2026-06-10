"""Tests for add_device and update_device."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def _add_heat_detector(call, model_id):
    call(
        "add_device",
        model_id=model_id,
        id="HD",
        comp_id="ROOM1",
        location=[1.2, 1.2, 2.3],
        type="HEAT_DETECTOR",
        setpoint=68,
        rti=50,
    )


def test_add_device_target(call, model_id):
    call(
        "add_material",
        model_id=model_id,
        id="STEEL",
        material="Steel",
        conductivity=0.05,
        density=7850,
        specific_heat=0.46,
        thickness=0.01,
    )
    out = call(
        "add_device",
        model_id=model_id,
        id="T1",
        comp_id="ROOM1",
        location=[1, 1, 1],
        type="PLATE",
        material_id="STEEL",
        normal=[0, 0, 1],
        temperature_depth=0.005,
    )
    assert "Added device 'T1'" in out


def test_add_device_detector(call, model_id):
    out = call(
        "add_device",
        model_id=model_id,
        id="HD",
        comp_id="ROOM1",
        location=[1.2, 1.2, 2.3],
        type="HEAT_DETECTOR",
        setpoint=68,
        rti=50,
    )
    assert "Added device 'HD'" in out


def test_add_device_target_missing_material(call, model_id):
    with pytest.raises(ToolError, match="material_id"):
        call(
            "add_device",
            model_id=model_id,
            id="T2",
            comp_id="ROOM1",
            location=[1, 1, 1],
            type="PLATE",
            normal=[0, 0, 1],
        )


def test_update_device(call, registry, model_id):
    _add_heat_detector(call, model_id)
    out = call("update_device", model_id=model_id, device_id="HD", setpoint=80)
    assert "Updated device 'HD'" in out
    assert registry.get(model_id).model.devices[0].setpoint == 80
