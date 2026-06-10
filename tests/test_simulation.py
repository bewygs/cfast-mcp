"""Tests for update_simulation."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def test_update_simulation_changes_params(call, registry, model_id):
    out = call(
        "update_simulation",
        model_id=model_id,
        time_simulation=1800,
        interior_temperature=25,
    )
    assert "Updated simulation environment" in out
    env = registry.get(model_id).model.simulation_environment
    assert env.time_simulation == 1800
    assert env.interior_temperature == 25


def test_update_simulation_no_params(call, model_id):
    with pytest.raises(ToolError, match="No parameters to update"):
        call("update_simulation", model_id=model_id)
