# CFAST MCP

An MCP server that lets an LLM build, inspect, run, and analyze [CFAST](https://pages.nist.gov/cfast/) (Consolidated Fire and Smoke Transport, NIST) fire models step by step, via [PyCFAST](https://github.com/bewygs/pycfast).

It exposes tools to add/update compartments, materials, vents, fires, devices, and surface connections, then run the simulation and read results as bounded summaries.

## Installation

Requires **Python 3.10+** and **CFAST 7.7.0+**.

### CFAST

Download and install CFAST from the [NIST CFAST website](https://pages.nist.gov/cfast/) or the [CFAST GitHub repository](https://github.com/firemodels/cfast), and ensure `cfast` is on your `PATH`. If it's installed elsewhere, set the `CFAST` environment variable to the executable path:

```bash
export CFAST="/path/to/your/cfast/executable"
```

### Server

```bash
pip install cfast-mcp
```

## Usage

Add the server to your MCP client configuration:

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

Or run it directly:

```bash
cfast-mcp
```

## Development

```bash
git clone https://github.com/bewygs/cfast-mcp.git
cd cfast-mcp
uv sync --extra dev          # install dev dependencies
uv run pytest                # run tests
uv run ruff check --fix .    # lint
uv run ruff format .         # format
uv run mypy src/              # type-check
```

See [CLAUDE.md](CLAUDE.md) for architecture and contribution details.
