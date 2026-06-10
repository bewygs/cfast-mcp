"""Tests for add_wall_vent and update_wall_vent."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def _add_door(call, model_id, comp_b="OUTSIDE"):
    call(
        "add_wall_vent",
        model_id=model_id,
        id="DOOR",
        comp_a="ROOM1",
        comp_b=comp_b,
        bottom=0,
        height=2.0,
        width=0.9,
        face="FRONT",
    )


def test_update_wall_vent_geometry(call, registry, model_id):
    _add_door(call, model_id)
    out = call(
        "update_wall_vent",
        model_id=model_id,
        vent_id="DOOR",
        width=1.2,
        face="left",
    )
    assert "Updated wall vent 'DOOR'" in out
    vent = registry.get(model_id).model.wall_vents[0]
    assert vent.width == 1.2
    assert vent.face == "LEFT"


def test_update_wall_vent_change_connection(call, registry, model_id):
    call("add_compartment", model_id=model_id, id="ROOM2", width=4, depth=3, height=2.4)
    _add_door(call, model_id)
    call(
        "update_wall_vent",
        model_id=model_id,
        vent_id="DOOR",
        comp_a="ROOM1",
        comp_b="ROOM2",
    )
    assert registry.get(model_id).model.wall_vents[0].comps_ids == ["ROOM1", "ROOM2"]


def test_update_wall_vent_partial_connection_rejected(call, model_id):
    _add_door(call, model_id)
    with pytest.raises(ToolError, match="both comp_a and comp_b"):
        call("update_wall_vent", model_id=model_id, vent_id="DOOR", comp_a="ROOM1")


def test_update_wall_vent_invalid_face(call, model_id):
    _add_door(call, model_id)
    with pytest.raises(ToolError, match="FRONT, REAR, LEFT, RIGHT"):
        call("update_wall_vent", model_id=model_id, vent_id="DOOR", face="BACK")


def test_add_wall_vent_to_outside(call, model_id):
    out = call(
        "add_wall_vent",
        model_id=model_id,
        id="DOOR",
        comp_a="ROOM1",
        comp_b="OUTSIDE",
        bottom=0,
        height=2.0,
        width=0.9,
        face="FRONT",
    )
    assert "Added wall vent 'DOOR'" in out


def test_add_wall_vent_invalid_face(call, model_id):
    with pytest.raises(ToolError, match="FRONT, REAR, LEFT, RIGHT"):
        call(
            "add_wall_vent",
            model_id=model_id,
            id="DOOR",
            comp_a="ROOM1",
            comp_b="OUTSIDE",
            bottom=0,
            height=2.0,
            width=0.9,
            face="INVALID",
        )
