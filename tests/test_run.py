"""Tests for run_model and get_results against a real CFAST run."""

from __future__ import annotations

import os
import shutil

import pytest
from mcp.server.fastmcp.exceptions import ToolError

pytestmark = [
    pytest.mark.local,
    pytest.mark.skipif(
        not (os.environ.get("CFAST") or shutil.which("cfast")),
        reason="CFAST binary not available",
    ),
]


@pytest.fixture
def ran_model(call, model_id, fire_table) -> str:
    """Build and run a one-room + door + fire model; return its model_id."""
    call(
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
    call(
        "add_fire",
        model_id=model_id,
        id="FIRE1",
        comp_id="ROOM1",
        fire_id="FIRE1",
        location=[1.8, 1.2],
        data_table=fire_table,
    )
    out = call("run_model", model_id=model_id)
    assert "Run complete" in out
    assert "compartments" in out
    return model_id


def test_get_results_end_to_end(call, registry, ran_model):
    df = registry.get(ran_model).run_results["compartments"]
    column = next(str(c) for c in df.columns if "ULT" in str(c).upper())

    # the real CFAST column survives the run -> registry -> get_results path
    preview = call("get_results", model_id=ran_model, key="compartments")
    assert column in preview

    # per-column stats run on real CFAST output: the fire heats the upper layer
    # well above the 20 °C ambient (the format itself is covered by test_serialization)
    call("get_results", model_id=ran_model, key="compartments", column=column)
    assert df[column].max() > 50


def test_get_results_unknown_key(call, ran_model):
    with pytest.raises(ToolError, match="Unknown result key"):
        call("get_results", model_id=ran_model, key="nope")
