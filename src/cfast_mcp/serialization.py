"""Text summaries of CFAST run results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

MAX_PREVIEW_ROWS = 5
MAX_LISTED_COLUMNS = 12


def _list_columns(df: pd.DataFrame) -> str:
    """Return the first ``MAX_LISTED_COLUMNS`` column names of ``df``."""
    cols = list(df.columns)
    shown = ", ".join(map(str, cols[:MAX_LISTED_COLUMNS]))
    if len(cols) > MAX_LISTED_COLUMNS:
        shown += f", … (+{len(cols) - MAX_LISTED_COLUMNS} more)"
    return shown


def summarize_results(results: dict[str, pd.DataFrame | None]) -> str:
    """Return an overview of every output key from a run."""
    lines = ["Run results:"]
    for key, df in results.items():
        if df is None:
            lines.append(f"  {key}: (not produced)")
        elif df.empty:
            lines.append(f"  {key}: (empty)")
        else:
            lines.append(
                f"  {key}: {df.shape[0]} rows × {df.shape[1]} cols; "
                f"columns: {_list_columns(df)}"
            )
    lines.append(
        "\nUse get_results(model_id, key) to preview a key, or "
        "get_results(model_id, key, column) for min/max/final stats."
    )
    return "\n".join(lines)


def preview_key(key: str, df: pd.DataFrame) -> str:
    """Return shape, columns and a bounded ``head`` for one result key."""
    head = df.head(MAX_PREVIEW_ROWS).to_string(max_cols=MAX_LISTED_COLUMNS)
    return (
        f"'{key}': {df.shape[0]} rows × {df.shape[1]} cols\n"
        f"Columns: {_list_columns(df)}\n\n"
        f"First {min(MAX_PREVIEW_ROWS, len(df))} rows:\n{head}"
    )


def summarize_column(key: str, column: str, df: pd.DataFrame) -> str:
    """Return min / max / final value (and time of max) for a single column."""
    if column not in df.columns:
        raise KeyError(
            f"Column '{column}' not found in '{key}'. "
            f"Available (first {MAX_LISTED_COLUMNS}): {_list_columns(df)}"
        )

    series = df[column]
    if series.dtype.kind not in "biufc":
        raise ValueError(
            f"Column '{column}' in '{key}' is not numeric; "
            "preview the key without a column instead."
        )
    idx_max = series.idxmax()
    lines = [
        f"'{key}' / column '{column}':",
        f"  min   = {series.min()}",
        f"  max   = {series.max()}",
        f"  final = {series.iloc[-1]}",
    ]
    time_col = next(
        (c for c in df.columns if str(c).strip().lower() in {"time", "time (s)"}), None
    )
    if time_col is not None:
        lines.append(
            f"  time of max = {df[time_col].loc[idx_max]} (from column '{time_col}')"
        )
    return "\n".join(lines)
