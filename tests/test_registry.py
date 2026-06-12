"""Tests for the in-memory model registry."""

from __future__ import annotations

import os

import pytest

from cfast_mcp.registry import ModelRegistry


def test_create_returns_incrementing_ids():
    registry = ModelRegistry()
    assert registry.create(object()) == "m1"
    assert registry.create(object()) == "m2"


def test_get_returns_entry():
    registry = ModelRegistry()
    model = object()
    model_id = registry.create(model)
    entry = registry.get(model_id)
    assert entry.model is model
    assert entry.last_saved_path is None
    assert entry.run_results is None


def test_get_unknown_id_raises_with_known_ids():
    registry = ModelRegistry()
    registry.create(object())
    with pytest.raises(KeyError, match="Unknown model_id 'm9'.*m1"):
        registry.get("m9")


def test_set_replaces_model():
    registry = ModelRegistry()
    model_id = registry.create(object())
    new_model = object()
    registry.set(model_id, new_model)
    assert registry.get(model_id).model is new_model


def test_work_path_lazy_named_and_shared():
    registry = ModelRegistry()
    registry.create(object())
    assert registry._work_root is None  # no temp dir until first use
    p1 = registry.work_path("m1")
    assert os.path.basename(p1) == "m1.in"
    assert os.path.isdir(os.path.dirname(p1))
    p2 = registry.work_path("m2")
    assert os.path.dirname(p2) == os.path.dirname(p1)  # all models share one root
    registry.close()


def test_close_removes_root_and_is_idempotent():
    registry = ModelRegistry()
    root = os.path.dirname(registry.work_path("m1"))
    assert os.path.isdir(root)
    registry.close()
    assert not os.path.isdir(root)
    assert registry._work_root is None
    registry.close()  # safe to call again
