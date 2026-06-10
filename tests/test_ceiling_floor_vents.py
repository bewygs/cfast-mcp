"""Tests for add_ceiling_floor_vent and update_ceiling_floor_vent."""

from __future__ import annotations


def _add_hole(call, model_id):
    call(
        "add_ceiling_floor_vent",
        model_id=model_id,
        id="HOLE",
        comp_top="ROOM1",
        comp_bottom="OUTSIDE",
        area=1.0,
    )


def test_add_ceiling_floor_vent(call, model_id):
    out = call(
        "add_ceiling_floor_vent",
        model_id=model_id,
        id="HOLE",
        comp_top="ROOM1",
        comp_bottom="OUTSIDE",
        area=1.0,
    )
    assert "Added ceiling/floor vent 'HOLE'" in out


def test_update_ceiling_floor_vent(call, registry, model_id):
    _add_hole(call, model_id)
    out = call(
        "update_ceiling_floor_vent",
        model_id=model_id,
        vent_id="HOLE",
        area=2.0,
        shape="SQUARE",
    )
    assert "Updated ceiling/floor vent 'HOLE'" in out
    vent = registry.get(model_id).model.ceiling_floor_vents[0]
    assert vent.area == 2.0
    assert vent.shape == "SQUARE"
