# CFAST MCP

[![CI Status](https://github.com/bewygs/cfast-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/bewygs/cfast-mcp/actions/workflows/test.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/bewygs/cfast-mcp/main.svg)](https://results.pre-commit.ci/latest/github/bewygs/cfast-mcp/main)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![MyPy Checked](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/python/mypy)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cfast-mcp)](https://pypi.org/project/cfast-mcp/)
[![PyPI](https://img.shields.io/pypi/v/cfast-mcp)](https://pypi.org/project/cfast-mcp/)
[![codecov](https://codecov.io/gh/bewygs/cfast-mcp/graph/badge.svg?token=6D621ZUJFT)](https://codecov.io/gh/bewygs/cfast-mcp)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/bewygs/cfast-mcp/blob/main/LICENSE)

**CFAST MCP** is an [MCP](https://modelcontextprotocol.io/) server that lets an AI assistant build, run, and analyze [**CFAST**](https://pages.nist.gov/cfast/) (Consolidated Fire and Smoke Transport, NIST) fire simulations through conversation. It is built on top of [**PyCFAST**](https://github.com/bewygs/pycfast) and exposes the **CFAST** model as a set of tools. The AI assistant is able to create a model, add compartments, materials, vents, fires and devices step by step, run CFAST, and make summaries of the results.

## Example

Ask your assistant something like:

> Create a 4 m × 3 m × 2.5 m room with a door (0.9 × 2 m) to the outside and a fire
> growing to 1 MW in 300 s. Run it and give me the peak upper-layer temperature then
> show me the folder where you create the file, so I can inspect it.

Results will probably look like this:

<img width="1920" height="944" alt="image" src="https://github.com/user-attachments/assets/9f4c87b3-c722-4153-b75b-53c75f9cb70e" />

## Tools

| Group | Tools |
|---|---|
| Create & configure | `create_model`, `update_simulation` |
| Components | `add_*` / `update_*` for materials, compartments, wall vents, ceiling/floor vents, mechanical vents, fires, devices (targets & detectors), surface connections |
| Inspect | `inspect_model` (summary, optional `.in` file), `get_model_files` |
| Run & results | `run_model`, `get_results` (bounded previews and per-column min/max/final stats) |

Results are returned to the AI assistant as small text summaries. The generated files (`.in`, output `.csv`, logs) are written in a temporary directory while the session is active. Use `get_model_files` to locate them if you want to open them directly.

> **Note:** models live in memory for the lifetime of the server process. Restarting the server (or your MCP client) will delete them.

## Installation

Requires **Python 3.10+** and **CFAST 7.7.0+**.

### uvx (Recommended)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then add `cfast-mcp` directly in your client configuration:

```json
{
  "mcpServers": {
    "cfast": {
      "command": "uvx",
      "args": ["cfast-mcp"],
      "env": { "CFAST": "/path/to/your/cfast/executable" }
    }
  }
}
```

### Claude Code

If you use [Claude Code](https://claude.ai/code), a single command registers the server:

```bash
claude mcp add cfast -e CFAST=/path/to/your/cfast/executable -- cfast-mcp
```

### Pip

Create a virtual environment and install from PyPI:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install cfast-mcp
```

Then add `cfast-mcp` to your client configuration:

```json
{
  "mcpServers": {
    "cfast": {
      "command": "cfast-mcp",
      "env": { "CFAST": "/path/to/your/cfast/executable" }
    }
  }
}
```

### CFAST Installation

Download and install CFAST from the [NIST CFAST website](https://pages.nist.gov/cfast/) or the [CFAST GitHub repository](https://github.com/firemodels/cfast). Follow the installation instructions for your operating system and ensure `cfast` is available in your `PATH`. If CFAST is installed in a non-standard location, you can manually specify the path by setting the `CFAST` environment variable to point to the CFAST executable.

```bash
export CFAST="/path/to/your/cfast/executable"   # Linux/macOS
set CFAST="C:\path\to\cfast.exe"                # Windows (cmd)
$env:CFAST="C:\path\to\cfast.exe"               # Windows (PowerShell)
```

## Development

```bash
git clone https://github.com/bewygs/cfast-mcp.git
cd cfast-mcp
uv sync --extra dev          # install dev dependencies
uv run pytest                # run tests
uv run ruff check --fix .    # lint
uv run mypy src/             # type-check
```
