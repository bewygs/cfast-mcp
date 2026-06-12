"""Tests for the guard() error-translation layer."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from cfast_mcp.errors import guard


def test_no_exception_passes_through():
    with guard():
        x = 1 + 1
    assert x == 2


def test_duplicate_id_gets_hint():
    with pytest.raises(ToolError, match="must be unique"):
        with guard():
            raise ValueError("Duplicate id 'GYPSUM' found in material_properties.")


def test_unknown_compartment_gets_hint():
    with pytest.raises(ToolError, match="add_compartment"):
        with guard():
            raise ValueError(
                "Fire 'F1': comp_id='NOPE' does not match any defined compartment."
            )


def test_unknown_material_gets_hint():
    with pytest.raises(ToolError, match="add_material"):
        with guard():
            raise ValueError(
                "Compartment 'ROOM1': 'GYPSUM' does not match any defined material."
            )


def test_unrecognized_value_error_kept_verbatim():
    with pytest.raises(ToolError, match="^some other validation failure$"):
        with guard():
            raise ValueError("some other validation failure")


def test_type_error_prefixed():
    with pytest.raises(ToolError, match="Invalid argument"):
        with guard():
            raise TypeError("id must be a string.")


def test_file_not_found_converted():
    with pytest.raises(ToolError, match="no such file"):
        with guard():
            raise FileNotFoundError("no such file")


def test_tool_error_reraised_unchanged():
    with pytest.raises(ToolError, match="^already clean$"):
        with guard():
            raise ToolError("already clean")
