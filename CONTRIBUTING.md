# Contributing

Samsarix CLI favors a small, honest command surface and reviewed built-in templates. A contribution
should improve the complete `templates -> init -> check -> run` journey without introducing a
runtime dependency on a private repository or hosted service.

## Setup

```bash
python -m venv .venv
```

Activate it, then install the development dependencies:

```bash
python -m pip install --upgrade pip "setuptools>=83,<84"
python -m pip install -e ".[dev]"
```

## Required checks

```bash
ruff format --check .
ruff check .
mypy
pytest --cov=samsarix_cli --cov-report=term-missing
pip-audit --local --skip-editable
python -m build
python -m twine check dist/*
```

Run a real generated-project smoke check when changing a template:

```bash
samsarix init smoke-project --template fastapi --no-git
samsarix check smoke-project
```

Use a disposable destination; `samsarix init` intentionally refuses to overwrite it on a later run.

## Contribution expectations

- Add or update command-level and library-level tests.
- Keep help and errors ASCII-safe for Windows consoles.
- Treat project manifests and paths as untrusted input.
- Never add example secrets, fabricated metrics, or commands that claim external side effects they
  do not perform.
- Keep generated projects independent from this repository after creation.
- Update the README, changelog, and productization record when behavior or release scope changes.
- Contributions are accepted under Apache-2.0 as described in section 5 of the license.
- Do not change licensing, ownership, or publication identity without an explicit Samsarix LLC
  decision.
