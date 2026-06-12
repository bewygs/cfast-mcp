# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An MCP server built around [pycfast](https://github.com/bewygs/pycfast), a Python interface for CFAST (Consolidated Fire and Smoke Transport, NIST). It exposes tools that let an LLM build a CFAST model step by step, inspect it, run it, and read results.

## Commands

```bash
uv sync --extra dev         # Install package + dev dependencies (Python 3.10+)
uv run cfast-mcp            # Run the server (console script)
uv run main.py              # Run the server (repo-root shim)
uv run mcp dev main.py      # MCP inspector UI
uv run ruff check --fix .   # Lint
uv run ruff format .        # Format
uv run mypy src/            # Type-check
uv run pytest               # Run all tests (CFAST-dependent ones skip if no binary)
uv run pytest -m local      # Run only the tests requiring the CFAST binary
uv run pytest --cov         # Coverage
```

Run a single test:
```bash
uv run pytest tests/test_model.py::test_create_model -v
```

Pre-commit hooks run `ruff check --fix` and `ruff format`.

## Architecture

```
main.py                       # repo-root shim — re-exports server.mcp for `mcp dev`
src/cfast_mcp/
  server.py                   # builds FastMCP("cfast"), registers tools, main()
  registry.py                 # ModelRegistry: model_id -> ModelEntry, in memory
  errors.py                   # guard(): pycfast exceptions -> ToolError with hints
  serialization.py            # bounded DataFrame summaries (never full dumps)
  tools/                       # the 22 @mcp.tool() definitions, one module per component
    __init__.py                # register_tools(): wires all sub-registrars
    model.py                    # create_model, inspect_model, run_model, get_results, get_model_files
    simulation.py               # update_simulation
    materials.py                # add_material, update_material
    compartments.py             # add_compartment, update_compartment
    wall_vents.py                # add_wall_vent, update_wall_vent
    ceiling_floor_vents.py       # add_ceiling_floor_vent, update_ceiling_floor_vent
    mechanical_vents.py          # add_mechanical_vent, update_mechanical_vent
    fires.py                     # add_fire, update_fire
    devices.py                   # add_device, update_device
    surface_connections.py       # add_surface_connection, update_surface_connection
```

The tool inventory is the module list above; each tool's own docstring is the source of truth for its parameters. The non-obvious behaviours are in the constraints below.

### Tool behaviours and constraints inherited from pycfast

- Every `update_*` tool is a partial edit: only the parameters you pass change.
- Vent endpoints accepting the `"OUTSIDE"` sentinel: wall vent `comp_b`, ceiling/floor vent `comp_bottom`, mechanical vent `comp_from`/`comp_to`.
- Re-pointing a vent's connection in an `update_*` tool requires passing both endpoints together (wall: `comp_a`+`comp_b`; ceiling/floor: `comp_top`+`comp_bottom`; mechanical: `comp_from`+`comp_to`).
- `SurfaceConnection` has no id — `update_surface_connection` selects by 0-based index.
- `add_fire` `data_table` columns: TIME, HRR, HEIGHT, AREA, CO_YIELD, SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD.
- `Device` is either a target (`PLATE`/`CYLINDER`) or a detector (`HEAT_DETECTOR`/`SMOKE_DETECTOR`/`SPRINKLER`); pycfast validates per-type requirements.

- The registry is stateful: a `model_id` (`m1`, `m2`, ...) is returned at creation and passed to every subsequent tool. It lives for the server process lifetime only.
- `CFASTModel` is immutable: `model.add(component)` returns a new model. Every `add_*` tool must reassign with `registry.set(model_id, ...)`.
- A model cannot be empty: `CFASTModel.__init__` requires at least one compartment and validates immediately, so `create_model` takes the first compartment's parameters directly.
- `add()` validates dependencies on every call. Required order: materials, then compartments, then wall vents and fires. `guard()` in `errors.py` turns the resulting `ValueError` into a message saying what to add first.
- `view_cfast_input_file()` requires a prior `save()`. `inspect_model(show_input_file=True)` saves first and passes `pretty_print=False` to avoid ANSI codes in MCP responses.
- Generated `.in`/output files live in a single per-process temp directory owned by the registry (`work_path`/`close`), created lazily on the first `save()`/`run()` and removed at interpreter exit. Each model's files are named `{model_id}.*`. `run_model` reports the directory and `get_model_files` lists it.
- `run()` raises on CFAST process failure, but on timeout it only warns and returns whatever output CSVs it can read — always a dict with every key, values possibly `None`/empty. `run_model` raises `ToolError` (including the captured warnings) when no output set is usable; partial results are reported as success with the timeout warning appended.
- pycfast has no component-removal methods; do not implement `remove_*` tools.
- Component ids must be unique within their type; duplicates raise `ValueError("Duplicate id ...")`.
- `face` for wall vents: `FRONT`, `REAR`, `LEFT`, `RIGHT` (not `BACK`).
- CFAST names (title, material names) should be alphanumeric; `sanitize_cfast_title_and_material` exists in pycfast if needed.
- `run()` resolves the CFAST binary via the `cfast_exe` parameter, the `CFAST` environment variable, then `cfast` on the PATH. `model.run(timeout=...)` takes seconds.

### Tests

- Unit tests (`test_errors.py`, `test_registry.py`, `test_serialization.py`): pure helpers, no MCP involved.
- Integration tests (one file per component, e.g. `test_model.py`, `test_compartments.py`, `test_fires.py`, ...): tools called in process through `FastMCP.call_tool` (see `tests/conftest.py`); no CFAST binary needed.
- End-to-end tests (`test_run.py`): real CFAST run; marked `@pytest.mark.local` and skipped automatically when the binary is unavailable.

Do not retest pycfast's own validation or the mcp library — only the tool layer (argument handling, registry updates, error translation).

## Standards

- Ruff: line-length 88, rules E, W, F, I, B, C4, UP, D (numpy docstrings)
- MyPy: strict options, Python 3.11 target
- Tool docstrings are the LLM interface: numpydoc, with units and defaults written as in pycfast ("Default units: m, default value: 0 m"). Reuse pycfast's own parameter descriptions where possible.

## Future scope

Deliberate omissions (kept simple, can be added uniformly later): the vent open/close-criterion machinery (`open_close_criterion`/`time`/`fraction`/`set_point`/`device_id`/`pre_fraction`/`post_fraction`) on all vent types; the triggered-ignition `Fire` fields (`ignition_criterion`/`set_point`/`device_id`); the DIAG-only device fields (`adiabatic`, `convection_coefficients`); multi-layer compartment materials; the remaining `SimulationEnvironment` parameters (`print`, `smokeview`, `spreadsheet`, `init_pressure`, `adiabatic`, `max_time_step`, `lower_oxygen_limit`) — `spreadsheet` (CSV output interval, hence the time resolution of `get_results`) is the priority candidate; the remaining `Compartment` parameters (`shaft`, `hall`, `leak_area_ratio`, `cross_sect_areas`/`cross_sect_heights`). Known pycfast limitation: `update_material_params`'s selector parameter is named `material`, which shadows the descriptive-name field, so `update_material` cannot edit the name (only thermophysical props).

Possible future change: return a compact confirmation (per-type counts) from `add_*`/`update_*` instead of the full `model.summary()`, to cut token cost on large models (`inspect_model` already provides the full view).

Still out of scope: `import_model_from_file`, `list_models`/`delete_model`, MCP Resources and Prompts.
