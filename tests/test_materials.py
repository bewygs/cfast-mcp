"""Tests for add_material and update_material."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def _add_gypsum(call, model_id):
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


def test_add_material(call, model_id):
    out = call(
        "add_material",
        model_id=model_id,
        id="GYPSUM",
        material="Gypsum Board",
        conductivity=0.16,
        density=790,
        specific_heat=0.9,
        thickness=0.016,
    )
    assert "Added material 'GYPSUM'" in out


def test_update_material_changes_property(call, registry, model_id):
    _add_gypsum(call, model_id)
    out = call(
        "update_material",
        model_id=model_id,
        material_id="GYPSUM",
        conductivity=0.25,
        thickness=0.02,
    )
    assert "Updated material 'GYPSUM'" in out
    mat = registry.get(model_id).model.material_properties[0]
    assert mat.conductivity == 0.25
    assert mat.thickness == 0.02


def test_duplicate_id_rejected(call, model_id):
    kwargs = {
        "model_id": model_id,
        "id": "GYPSUM",
        "material": "Gypsum Board",
        "conductivity": 0.16,
        "density": 790,
        "specific_heat": 0.9,
        "thickness": 0.016,
    }
    call("add_material", **kwargs)
    with pytest.raises(ToolError, match="Duplicate id.*must be unique"):
        call("add_material", **kwargs)
