"""Tests for create_model, inspect_model, run_model and get_results."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError


def test_create_model(call):
    out = call(
        "create_model",
        title="Test",
        room_id="ROOM1",
        room_width=3.6,
        room_depth=2.4,
        room_height=2.4,
    )
    assert "Created model 'm1'" in out
    assert "ROOM1" in out


def test_unknown_model_id(call):
    with pytest.raises(ToolError, match="Unknown model_id 'm9'"):
        call("inspect_model", model_id="m9")


def test_inspect_model_summary(call, model_id):
    out = call("inspect_model", model_id=model_id)
    assert "ROOM1" in out
    assert "CFAST input file" not in out


def test_inspect_model_input_file(call, model_id):
    out = call("inspect_model", model_id=model_id, show_input_file=True)
    assert "CFAST input file" in out
    assert "&COMP" in out
    assert "\x1b" not in out  # no ANSI codes (pretty_print=False)


def test_get_results_before_run(call, model_id):
    with pytest.raises(ToolError, match="No results yet"):
        call("get_results", model_id=model_id, key="compartments")


def test_get_model_files_empty(call, model_id):
    out = call("get_model_files", model_id=model_id)
    assert "Working directory:" in out
    assert "No files" in out


def test_get_model_files_lists_saved_input(call, model_id):
    call("inspect_model", model_id=model_id, show_input_file=True)
    out = call("get_model_files", model_id=model_id)
    assert "Working directory:" in out
    assert "m1.in" in out
