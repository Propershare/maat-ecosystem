# Developer Setup

## Prerequisites

- **Python** 3.10+
- **Node.js** 22+
- **npm** 10+
- **Git**

## Quick Start

```bash
# Clone the repository
git clone <repo-url> maat-ecosystem
cd maat-ecosystem

# Python dependencies
pip install ruff pytest

# Node.js dependencies
cd tehuti-guard && npm install && cd ..

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Code Quality

### Python

We use [ruff](https://docs.astral.sh/ruff/) for both linting and formatting.

```bash
# Lint
ruff check .

# Format
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

Configuration lives in [`pyproject.toml`](pyproject.toml) under `[tool.ruff]`.

### TypeScript

TypeScript configuration is in [`tehuti-guard/tsconfig.json`](tehuti-guard/tsconfig.json).

```bash
# Type check
cd tehuti-guard && npx tsc --noEmit

# Test
cd tehuti-guard && npm test
```

## Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. They enforce:

- Ruff linting and formatting
- Trailing whitespace removal
- End-of-file fixing
- YAML validation
- Merge conflict detection
- Private key detection

To run hooks manually:

```bash
pre-commit run --all-files
```

## Testing

### Python Tests

```bash
pytest -x -v
```

### TypeScript Tests

```bash
cd tehuti-guard && npm test
```

## CI Pipeline

The CI pipeline runs automatically on push and pull requests to `main`:

| Job | What it runs |
|-----|-------------|
| `python-lint` | `ruff check` + `ruff format --check` |
| `python-test` | `pytest -x -v` |
| `ts-lint-test` | `tsc --noEmit` + `npm test` |

Pipeline configuration: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
