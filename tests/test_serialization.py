"""Tests for the bounded DataFrame summaries."""

from __future__ import annotations

import pandas as pd
import pytest

from cfast_mcp.serialization import (
    MAX_LISTED_COLUMNS,
    MAX_PREVIEW_ROWS,
    preview_key,
    summarize_column,
    summarize_results,
)


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Time": [0, 60, 120, 180],
            "ULT_ROOM1": [20.0, 150.0, 400.0, 350.0],
        }
    )


def test_summarize_results_overview(df):
    out = summarize_results({"compartments": df, "vents": None, "walls": df.iloc[:0]})
    assert "compartments: 4 rows × 2 cols" in out
    assert "vents: (not produced)" in out
    assert "walls: (empty)" in out
    assert "get_results" in out


def test_preview_key_is_bounded():
    wide = pd.DataFrame({f"col{i}": range(100) for i in range(30)})
    out = preview_key("compartments", wide)
    assert f"First {MAX_PREVIEW_ROWS} rows" in out
    assert f"+{30 - MAX_LISTED_COLUMNS} more" in out
    data_rows = [
        line for line in out.split("rows:\n")[1].splitlines() if line[:1].isdigit()
    ]
    assert len(data_rows) == MAX_PREVIEW_ROWS


def test_preview_key_short_frame(df):
    out = preview_key("compartments", df)
    assert "4 rows × 2 cols" in out
    assert "ULT_ROOM1" in out


def test_summarize_column_stats(df):
    out = summarize_column("compartments", "ULT_ROOM1", df)
    assert "min   = 20.0" in out
    assert "max   = 400.0" in out
    assert "final = 350.0" in out
    assert "time of max = 120" in out


def test_summarize_column_missing(df):
    with pytest.raises(KeyError, match="'NOPE' not found.*ULT_ROOM1"):
        summarize_column("compartments", "NOPE", df)
