"""Tests for add_mechanical_vent and update_mechanical_vent."""

from __future__ import annotations


def _add_fan(call, model_id):
    call(
        "add_mechanical_vent",
        model_id=model_id,
        id="FAN",
        comp_from="ROOM1",
        comp_to="OUTSIDE",
        flow=0.5,
        area=[0.1, 0.1],
    )


def test_add_mechanical_vent(call, model_id):
    out = call(
        "add_mechanical_vent",
        model_id=model_id,
        id="FAN",
        comp_from="ROOM1",
        comp_to="OUTSIDE",
        flow=0.5,
        area=[0.1, 0.1],
    )
    assert "Added mechanical vent 'FAN'" in out


def test_update_mechanical_vent(call, registry, model_id):
    _add_fan(call, model_id)
    out = call("update_mechanical_vent", model_id=model_id, vent_id="FAN", flow=1.2)
    assert "Updated mechanical vent 'FAN'" in out
    assert registry.get(model_id).model.mechanical_vents[0].flow == 1.2
