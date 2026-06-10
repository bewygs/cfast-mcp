"""Tests for add_surface_connection and update_surface_connection."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def _add_wall_conn(call, model_id):
    call("add_compartment", model_id=model_id, id="ROOM2", width=4, depth=3, height=2.4)
    call(
        "add_surface_connection",
        model_id=model_id,
        conn_type="WALL",
        comp_id="ROOM1",
        comp_ids="ROOM2",
        fraction=0.25,
    )


def test_add_surface_connection(call, model_id):
    call("add_compartment", model_id=model_id, id="ROOM2", width=4, depth=3, height=2.4)
    out = call(
        "add_surface_connection",
        model_id=model_id,
        conn_type="WALL",
        comp_id="ROOM1",
        comp_ids="ROOM2",
        fraction=0.25,
    )
    assert "Added surface connection" in out


def test_add_surface_connection_wall_without_fraction(call, model_id):
    call("add_compartment", model_id=model_id, id="ROOM2", width=4, depth=3, height=2.4)
    with pytest.raises(ToolError, match="requires a fraction"):
        call(
            "add_surface_connection",
            model_id=model_id,
            conn_type="WALL",
            comp_id="ROOM1",
            comp_ids="ROOM2",
        )


def test_update_surface_connection(call, registry, model_id):
    _add_wall_conn(call, model_id)
    out = call("update_surface_connection", model_id=model_id, index=0, fraction=0.5)
    assert "Updated surface connection #0" in out
    assert registry.get(model_id).model.surface_connections[0].fraction == 0.5


def test_update_surface_connection_bad_index(call, model_id):
    _add_wall_conn(call, model_id)
    with pytest.raises(ToolError, match="out of range"):
        call("update_surface_connection", model_id=model_id, index=9, fraction=0.5)
