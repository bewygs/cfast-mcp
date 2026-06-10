"""Tests for add_fire and update_fire."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def _add_fire1(call, model_id, fire_table, comp_id="ROOM1"):
    call(
        "add_fire",
        model_id=model_id,
        id="FIRE1",
        comp_id=comp_id,
        fire_id="FIRE1",
        location=[1.8, 1.2],
        data_table=fire_table,
    )


def test_update_fire_changes_curve_and_chemistry(call, registry, model_id, fire_table):
    _add_fire1(call, model_id, fire_table)
    new_curve = [
        [0, 0, 0, 0.3, 0, 0, 0, 0, 0],
        [120, 500, 0, 0.3, 0, 0, 0, 0, 0],
    ]
    out = call(
        "update_fire",
        model_id=model_id,
        id="FIRE1",
        data_table=new_curve,
        carbon=27,
    )
    assert "Updated fire 'FIRE1'" in out
    fire = registry.get(model_id).model.fires[0]
    assert fire.carbon == 27
    assert max(row[1] for row in fire.data_table) == 500


def test_update_fire_move_compartment(call, registry, model_id, fire_table):
    call("add_compartment", model_id=model_id, id="ROOM2", width=4, depth=3, height=2.4)
    _add_fire1(call, model_id, fire_table)
    call("update_fire", model_id=model_id, id="FIRE1", comp_id="ROOM2")
    assert registry.get(model_id).model.fires[0].comp_id == "ROOM2"


def test_add_fire(call, model_id, fire_table):
    out = call(
        "add_fire",
        model_id=model_id,
        id="FIRE1",
        comp_id="ROOM1",
        fire_id="FIRE1",
        location=[1.8, 1.2],
        data_table=fire_table,
    )
    assert "Added fire 'FIRE1'" in out
    assert "Warnings" not in out


def test_add_fire_outside_footprint_warns(call, model_id, fire_table):
    out = call(
        "add_fire",
        model_id=model_id,
        id="FIRE1",
        comp_id="ROOM1",
        fire_id="FIRE1",
        location=[10, 10],  # outside the 3.6 x 2.4 m room
        data_table=fire_table,
    )
    assert "Added fire 'FIRE1'" in out
    assert "Warnings:" in out


def test_add_fire_unknown_compartment(call, model_id, fire_table):
    with pytest.raises(ToolError, match="add_compartment"):
        call(
            "add_fire",
            model_id=model_id,
            id="FIRE1",
            comp_id="NOPE",
            fire_id="FIRE1",
            location=[1, 1],
            data_table=fire_table,
        )
