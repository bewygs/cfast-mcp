"""
Repo-root entrypoint.

Can be run with:
    uv run cfast-mcp          # console script (see pyproject [project.scripts])
    uv run main.py            # repo-root shim
    uv run mcp dev main.py    # MCP inspector

"""

from cfast_mcp.server import main, mcp  # noqa: F401  (mcp re-exported for `mcp dev`)

if __name__ == "__main__":
    main()
