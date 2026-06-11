"""Tools for model lifecycle: create, inspect, run and read results."""

from __future__ import annotations

import os
import warnings

from mcp.server.fastmcp import FastMCP
from pycfast import CFASTModel, Compartment, SimulationEnvironment

from ..errors import ToolError, format_warnings, guard_warnings
from ..registry import ModelRegistry
from ..serialization import preview_key, summarize_column, summarize_results


def _safe_basename(title: str) -> str:
    """Return a filesystem-safe ``.in`` basename derived from the title."""
    safe = "".join(c if c.isalnum() else "_" for c in title) or "model"
    return f"{safe}.in"


def register_model_tools(mcp: FastMCP, registry: ModelRegistry) -> None:
    """Register create_model, inspect_model, run_model and get_results."""

    @mcp.tool()
    def create_model(
        title: str,
        room_id: str,
        room_width: float,
        room_depth: float,
        room_height: float,
        time_simulation: int = 900,
        interior_temperature: float = 20,
        exterior_temperature: float = 20,
        relative_humidity: float = 50,
    ) -> str:
        """
        Create a new CFAST model with its first compartment and register it.

        A CFAST model must contain at least one compartment, so creation
        includes the first one. Add materials, further compartments, wall
        vents and fires with the add_* tools, then use inspect_model and
        run_model.

        Parameters
        ----------
        title : str
            Title of the simulation. May consist of letters, numbers, and/or
            symbols and may be up to 50 characters.
        room_id : str
            Unique alphanumeric name of the first compartment, referenced
            later by fires and wall vents.
        room_width : float
            Width of the compartment as measured on the X axis from its
            origin. Default units: m.
        room_depth : float
            Depth of the compartment as measured on the Y axis from its
            origin. Default units: m.
        room_height : float
            Height of the compartment as measured on the Z axis from its
            origin. Default units: m.
        time_simulation : int, optional
            Length of time over which the simulation takes place. Default
            units: s, default value: 900 s.
        interior_temperature : float, optional
            Initial ambient temperature inside the structure. Default
            units: °C, default value: 20 °C.
        exterior_temperature : float, optional
            Initial ambient temperature outside the structure. Default
            units: °C, default value: 20 °C.
        relative_humidity : float, optional
            Initial relative humidity, only specified for the interior.
            Default units: % RH, default value: 50 %.

        Returns
        -------
        str
            The new model_id, the model summary, and any warnings.
        """
        with guard_warnings() as caught:
            env = SimulationEnvironment(
                title=title,
                time_simulation=time_simulation,
                interior_temperature=interior_temperature,
                exterior_temperature=exterior_temperature,
                relative_humidity=relative_humidity,
            )
            room = Compartment(
                id=room_id,
                width=room_width,
                depth=room_depth,
                height=room_height,
            )
            model = CFASTModel(
                simulation_environment=env,
                compartments=[room],
                file_name=_safe_basename(title),
            )
        model_id = registry.create(model, title)
        return (
            f"Created model '{model_id}' (title: {title!r}).\n{model.summary()}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def inspect_model(model_id: str, show_input_file: bool = False) -> str:
        """
        Return a model summary, and optionally the CFAST input file.

        Parameters
        ----------
        model_id : str
            Id of the model to inspect.
        show_input_file : bool, optional
            If True, save the model and return the contents of the generated
            CFAST input (``.in``) file after the summary. Default
            value: False.

        Returns
        -------
        str
            The model summary, optionally followed by the input file.
        """
        entry = registry.get(model_id)
        summary: str = entry.model.summary()
        if not show_input_file:
            return summary

        with guard_warnings() as caught:
            entry.last_saved_path = entry.model.save(
                file_name=registry.work_path(model_id)
            )
            content: str = entry.model.view_cfast_input_file(pretty_print=False)
        return (
            f"{summary}\n\nCFAST input file ({entry.last_saved_path}):\n{content}"
            f"{format_warnings(caught)}"
        )

    @mcp.tool()
    def run_model(model_id: str, timeout: int = 120) -> str:
        """
        Run the CFAST simulation for a model and summarize the outputs.

        Requires the CFAST executable, resolved via the CFAST environment
        variable or ``cfast`` on the PATH. Results are stored in the registry
        so get_results can read them without re-running.

        Parameters
        ----------
        model_id : str
            Id of the model to run.
        timeout : int, optional
            Maximum CFAST run time. Default units: s, default value: 120 s.

        Returns
        -------
        str
            A bounded summary of the produced output sets.
        """
        entry = registry.get(model_id)
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                results = entry.model.run(
                    file_name=registry.work_path(model_id), timeout=timeout
                )
        except Exception as e:
            raise ToolError(f"CFAST run failed: {e}") from e

        produced = [k for k, v in results.items() if v is not None and not v.empty]
        if not produced:
            raise ToolError(
                "CFAST ran but produced no usable output (all output sets are "
                "missing or empty). Check the model with "
                "inspect_model(show_input_file=True), or increase the timeout."
                f"{format_warnings(caught)}"
            )

        entry.run_results = results
        workdir = os.path.dirname(registry.work_path(model_id))
        header = (
            f"Run complete for '{model_id}'. "
            f"Produced {len(produced)} non-empty output set(s).\n"
            f"Files in: {workdir} (use get_results to read them, or "
            "get_model_files to list them)."
        )
        return f"{header}\n\n{summarize_results(results)}{format_warnings(caught)}"

    @mcp.tool()
    def get_results(model_id: str, key: str, column: str | None = None) -> str:
        """
        Read stored run results for a model (bounded; never a full dump).

        Call run_model first. Without a column, returns a small preview
        (shape, columns, first rows) of the key. With a column, returns
        min / max / final value and time of max for that column — for
        example an upper-layer temperature column such as "ULT_1" in the
        "compartments" output.

        Parameters
        ----------
        model_id : str
            Id of the model whose results to read.
        key : str
            Output set, one of: compartments, devices, masses, vents, walls,
            zone, diagnostics.
        column : str or None, optional
            Column name within the key. If None, a bounded preview of the
            key is returned instead.

        Returns
        -------
        str
            Either a bounded preview of the key or single-column statistics.
        """
        entry = registry.get(model_id)
        if entry.run_results is None:
            raise ToolError("No results yet. Run the model first with run_model.")

        if key not in entry.run_results:
            available = ", ".join(entry.run_results)
            raise ToolError(f"Unknown result key '{key}'. Available: {available}")

        df = entry.run_results[key]
        if df is None or df.empty:
            raise ToolError(f"Result key '{key}' was not produced or is empty.")

        if column is None:
            return preview_key(key, df)
        try:
            return summarize_column(key, column, df)
        except KeyError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    def get_model_files(model_id: str) -> str:
        """
        List the on-disk files for a model and their directory.

        Use this to locate the input (``.in``), output (``.csv``) and log
        files so you can open them yourself. Files appear once the model is
        saved or run (run_model, or inspect_model with show_input_file=True);
        before then the directory is empty.

        Parameters
        ----------
        model_id : str
            Id of the model whose files to locate.

        Returns
        -------
        str
            The working directory and the names of the files belonging to
            the model.
        """
        registry.get(model_id)
        workdir = os.path.dirname(registry.work_path(model_id))
        names = sorted(
            name
            for name in os.listdir(workdir)
            if name.startswith((f"{model_id}.", f"{model_id}_"))
        )
        if not names:
            return (
                f"Working directory: {workdir}\n"
                f"No files for '{model_id}' yet — run_model or "
                "inspect_model(show_input_file=True) writes them."
            )
        listing = "\n".join(f"  {name}" for name in names)
        return f"Working directory: {workdir}\nFiles:\n{listing}"
