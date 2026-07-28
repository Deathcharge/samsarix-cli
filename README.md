# Helix CLI

Helix CLI is an offline project generator for developers who want a small, understandable Python
application starter without depending on a hosted Helix service. It creates a new directory from one
of four reviewed templates, can initialize Git, and records enough metadata for `helix check` to
detect a damaged scaffold.

The project is a beta release candidate. The local CLI and generated projects are functional, but
public package publication is blocked by the name and license decisions described under
[Distribution](#distribution) and [License](#license).

## What it creates

| Template | Result | Default run command |
| --- | --- | --- |
| `fastapi` | FastAPI service with a `/health` endpoint | the generated project name |
| `flask` | Flask service with a `/health` endpoint | the generated project name |
| `streamlit` | Small interactive Streamlit application | documented `streamlit run` command |
| `discord` | Minimal slash-command bot with default intents | the generated project name |

Every generated project includes:

- a `src/` package and focused tests;
- a modern `pyproject.toml` with bounded dependency ranges;
- setup, run, check, and platform-specific activation instructions;
- `.helix/project.json` for structural validation;
- no dependency on `helix-unified`, `helix-collective`, private endpoints, or paid APIs; and
- no selected license, leaving that legal choice with the generated project's owner.

## Requirements

- Python 3.11 or newer
- Git, unless every project is created with `--no-git`

Helix itself makes no network requests. Network access is needed only when `pip` downloads Helix or
the dependencies declared by a generated project.

## Install from source

```bash
git clone https://github.com/Deathcharge/helix-cli.git
cd helix-cli
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
source .venv/bin/activate
```

Then install:

```bash
python -m pip install --upgrade pip "setuptools>=83,<84"
python -m pip install .
helix --version
```

Do not install the unrelated `helix-cli` distribution currently present on PyPI and assume it came
from this repository. See [Distribution](#distribution).

## Quick start

List the templates and create the default FastAPI starter:

```bash
helix templates
helix init demo-api --template fastapi
helix check demo-api
cd demo-api
```

Follow the generated `README.md`, or run this standard setup:

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip "setuptools>=83,<84"
python -m pip install -e ".[dev]"
demo-api
```

```bash
# macOS or Linux
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip "setuptools>=83,<84"
python -m pip install -e ".[dev]"
demo-api
```

The final command starts the service on `127.0.0.1:8000`. Open
`http://127.0.0.1:8000/health`; the expected response is `{"status":"ok"}`.

## Commands

```text
helix templates [--json]
helix init DESTINATION [--template NAME] [--name PROJECT_NAME] [--git|--no-git]
helix check [PROJECT] [--json]
helix --version
helix --help
```

`helix init` never overwrites an existing path. It stages every file in a temporary sibling
directory and moves the completed result into place only after all requested work succeeds. Git is
initialized by default, but Helix does not change user identity, stage files, or create a commit.

`helix check` validates bounded JSON and TOML input, rejects manifest path traversal, confirms the
declared generated files still exist, and uses exit code 1 for a failed check. `--json` provides a
stable non-interactive result for scripts and CI.

## Development

```bash
python -m pip install --upgrade pip "setuptools>=83,<84"
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy
pytest --cov=helix_cli --cov-report=term-missing
pip-audit --local --skip-editable
python -m build
python -m twine check dist/*
```

CI runs the meaningful checks on Python 3.11, 3.12, and 3.13, then builds a wheel and source archive,
checks their metadata, installs the wheel into a fresh environment, and exercises `init` and
`check` through the installed command.

## Architecture

- `helix_cli/main.py` exposes the deliberately small Click command surface.
- `helix_cli/templates.py` contains the reviewed built-in starter renderers.
- `helix_cli/scaffold.py` owns name validation, bounded Git execution, atomic writes, and cleanup.
- `helix_cli/validation.py` treats generated-project metadata as untrusted input.
- `tests/` covers commands, all templates, packaging-critical behavior, and adversarial failures.

Helix deliberately does not run arbitrary remote templates. This keeps project creation offline and
avoids the remote-code and template-provenance trust model of general-purpose generators.

## Security and privacy

Helix sends no telemetry, stores no credentials, and does not contact an API. The optional Git
operation invokes the discovered Git executable with an argument list, a 20-second timeout, and no
shell. The Discord template reads its token only from the process environment and disables the
library's default log handler when passing the token.

Generated applications are development starters, not hardened internet deployments. Their owners
remain responsible for authentication, authorization, TLS, rate limits, secret management,
dependency updates, and production server configuration appropriate to their use case. See
[SECURITY.md](SECURITY.md) for reporting and supported-scope details.

## Distribution

The simplest current distribution path is installation from a reviewed Git tag or source checkout.
The `helix-cli` project name on PyPI was registered by another publisher in July 2025, so the owner
must select and verify an available distribution name or establish control before publishing this
repository. No package has been published, no production infrastructure has been changed, and CI
contains no publishing credentials or release job.

The CLI has no hosted operating cost. A plausible sustainability path is paid support or maintained
organization-specific template packs, subject to an owner-approved license and name; the core local
workflow does not need a subscription or usage-based service.

## Limitations

- Templates are intentionally built in; user-defined and remote template sources are not supported.
- `helix check` verifies structure and metadata, not user-edited application semantics.
- Dependency lockfiles are not generated because resolution is platform-specific; applications
  should adopt a lock workflow before production deployment.
- Only the FastAPI template is exercised as a fully installed and running end-to-end sample in local
  release verification; the remaining templates receive generation, syntax, metadata, and focused
  content tests.
- Public package naming and the repository's conflicting license files require owner decisions.

## Contributing and product record

See [CONTRIBUTING.md](CONTRIBUTING.md) for the local workflow and
[docs/PRODUCTIZATION.md](docs/PRODUCTIZATION.md) for the repository audit, decisions, baseline
evidence, acceptance criteria, completed work, and remaining priorities.

## License

This repository currently contains a modified Business Source License 1.1 text in [LICENSE](LICENSE)
and a separate [LICENSE.PROPRIETARY](LICENSE.PROPRIETARY) whose terms refer to Apache License 2.0.
The package metadata therefore uses a custom `LicenseRef` and identifies both files instead of
claiming that this is Apache-licensed or OSI-approved. The owner must obtain legal review and publish
one unambiguous licensing position before a public release. No license text was selected or changed
during productization.
