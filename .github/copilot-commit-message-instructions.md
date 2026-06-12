# Commit Message Instructions for CFAST MCP

Follow conventional commit format: `<type>: <description>`

## Types
- **DEV**: development tool or utility
- **FIX**: Bug fix  
- **DOC**: Documentation changes
- **BLD**: Dependencies/build system (Makefile, pyproject.toml, ...)
- **STY**: Code formatting
- **TST**: addition or modification of tests
- **MAINT**: maintenance commit (refactoring, typos, etc.)
- **FEAT**: new feature or enhancement
- **CI**: CI/CD workflows
- **REL**: release commit (version bump, changelog update, etc.)
- **chore**: Other maintenance

## Rules
- Use imperative mood ("Add" not "Added")
- Start with capital letter
- No period at end
- Keep under 50 characters
- Reference issues when relevant

## Examples
```
FEAT: add get_model_files tool
FIX: handle run failure in run_model
DOC: update installation guide for uv
TST: add compartment validation tests
CI: migrate workflows to use uv
BLD: bump pycfast minimum to 0.3.0
DEV: add mypy type checking to Makefile
MAINT: refactor registry module
STY: apply ruff formatting rules
```

## Breaking Changes
Add `!` and footer:
```
FEAT!: redesign tool registration interface

BREAKING CHANGE: register_tools() now requires a ModelRegistry instance
```