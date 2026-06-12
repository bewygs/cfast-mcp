"""Convert pycfast exceptions into :class:`ToolError` messages for the MCP client."""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from contextlib import contextmanager

from mcp.server.fastmcp.exceptions import ToolError


@contextmanager
def guard() -> Iterator[None]:
    """Re-raise pycfast errors from the enclosed block as :class:`ToolError`."""
    try:
        yield
    except ToolError:
        raise
    except ValueError as e:
        raise ToolError(_explain_value_error(str(e))) from e
    except FileNotFoundError as e:
        raise ToolError(str(e)) from e
    except IndexError as e:
        raise ToolError(str(e)) from e
    except TypeError as e:
        raise ToolError(f"Invalid argument: {e}") from e


@contextmanager
def guard_warnings() -> Iterator[list[warnings.WarningMessage]]:
    """Use :func:`guard` with capture of pycfast warnings.

    Yields the list of warnings caught in the enclosed block, to be passed
    to :func:`format_warnings`.
    """
    with guard(), warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        yield caught


def format_warnings(caught: list[warnings.WarningMessage]) -> str:
    """Format captured pycfast warnings, or return an empty string."""
    if not caught:
        return ""
    msgs = "\n".join(f"  - {w.message}" for w in caught)
    return f"\n\nWarnings:\n{msgs}"


def _explain_value_error(msg: str) -> str:
    """Append a remediation hint to a known pycfast validation message."""
    hint = ""
    low = msg.lower()
    if "duplicate id" in low:
        hint = " Choose a different id; component ids must be unique within their type."
    elif "does not match any defined compartment" in low:
        hint = " Add that compartment first (add_compartment), then retry."
    elif "does not match any defined material" in low:
        hint = " Add that material first (add_material), then retry."
    elif low.startswith("no ") and "found with" in low:
        hint = " Check the id you passed, it must match an existing component id in the model."
    return msg + hint
