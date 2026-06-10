"""In-memory registry of CFAST models.

Registry of CFAST models. A CFAST model is built step by step across several tool
calls, each CFASTModel instances are kept in memory, associated with a short model_id,
model.add() returns a new CFASTModel.
"""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from pycfast import CFASTModel


@dataclass
class ModelEntry:
    """A model and the metadata tracked alongside it."""

    model: CFASTModel
    title: str
    last_saved_path: str | None = None
    run_results: dict[str, pd.DataFrame | None] | None = None


class ModelRegistry:
    """Holds the live models for the lifetime of the server process."""

    def __init__(self) -> None:
        self._entries: dict[str, ModelEntry] = {}
        self._counter = 0
        self._work_root: str | None = None

    def work_path(self, model_id: str) -> str:
        """Return the ``.in`` path for ``model_id`` under a shared temp root."""
        if self._work_root is None:
            self._work_root = tempfile.mkdtemp(prefix="cfast_mcp_")
            atexit.register(self.close)
        return os.path.join(self._work_root, f"{model_id}.in")

    def close(self) -> None:
        """Remove the shared temp root, if any. Idempotent."""
        if self._work_root is not None:
            shutil.rmtree(self._work_root, ignore_errors=True)
            self._work_root = None

    def create(self, model: CFASTModel, title: str) -> str:
        """Register a new built model and return its new ``model_id``."""
        self._counter += 1
        model_id = f"m{self._counter}"
        self._entries[model_id] = ModelEntry(model=model, title=title)
        return model_id

    def get(self, model_id: str) -> ModelEntry:
        """Return the entry for ``model_id``, or raise ``KeyError``."""
        try:
            return self._entries[model_id]
        except KeyError:
            known = ", ".join(self._entries) or "(none)"
            raise KeyError(
                f"Unknown model_id '{model_id}'. Known models: {known}. "
                "Create one first with create_model."
            ) from None

    def set(self, model_id: str, model: CFASTModel) -> None:
        """Replace the model instance after an ``add``."""
        self.get(model_id).model = model
