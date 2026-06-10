"""Tests for add_compartment and update_compartment."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def test_add_compartment_updates_registry(call, registry, model_id):
    call(
        "add_compartment",
        model_id=model_id,
        id="ROOM2",
        width=4,
        depth=3,
        height=2.4,
    )
    # model.add returns a new CFASTModel; the registry must hold the new one
    comps = [c.id for c in registry.get(model_id).model.compartments]
    assert comps == ["ROOM1", "ROOM2"]


def test_update_compartment_attaches_surfaces(call, registry, model_id):
    call(
        "add_material",
        model_id=model_id,
        id="GYPSUM",
        material="Gypsum Board",
        conductivity=0.16,
        density=790,
        specific_heat=0.9,
        thickness=0.016,
    )
    out = call(
        "update_compartment",
        model_id=model_id,
        comp_id="ROOM1",
        ceiling_mat_id="GYPSUM",
        ceiling_thickness=0.016,
        wall_mat_id="GYPSUM",
    )
    assert "Updated compartment 'ROOM1'" in out
    # registry must hold the new model returned by update_compartment_params
    room = registry.get(model_id).model.compartments[0]
    assert room.ceiling_mat_id == "GYPSUM"
    assert room.wall_mat_id == "GYPSUM"


def test_update_compartment_unknown_id(call, model_id):
    with pytest.raises(ToolError, match="must match an existing component"):
        call(
            "update_compartment",
            model_id=model_id,
            comp_id="GHOST",
            width=4.0,
        )
