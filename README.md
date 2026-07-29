# Samsarix CLI

Samsarix CLI is an offline project generator from Samsarix LLC for developers who want a small,
understandable Python application starter. It creates a new directory from one of four reviewed
templates, can initialize Git, and records enough metadata for `samsarix check` to detect a damaged
scaffold.

The project is a beta release candidate. The local CLI, distributions, generated FastAPI journey,
and GitHub-hosted Python 3.11-3.13 CI are verified; public PyPI publication remains an external
release step.

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
- `.samsarix/project.json` for structural validation;
- no dependency on this repository, a private service, or a paid API; and
- no selected license, leaving that legal choice with the generated project's owner.

## Requirements

- Python 3.11 or newer
- Git, unless every project is created with `--no-git`

Samsarix CLI makes no network requests. Network access is needed only when `pip` downloads the CLI
or dependencies declared by a generated project.

## Install from source

The GitHub repository still uses its pre-rebrand path:

```bash
git clone https://github.com/Deathcharge/samsarix-cli.git
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
samsarix --version
```

The `samsarix-cli` distribution is not yet published on PyPI. Until an official release is linked
from this repository, install from a reviewed source tag rather than a similarly named package.

## Quick start

List the templates and create the default FastAPI starter:

```bash
samsarix templates
samsarix init demo-api --template fastapi
samsarix check demo-api
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
samsarix templates [--json]
samsarix init DESTINATION [--template NAME] [--name PROJECT_NAME] [--git|--no-git]
samsarix check [PROJECT] [--json]
samsarix --version
samsarix --help
```

`samsarix init` never overwrites an existing path. It stages every file in a temporary sibling
directory and moves the completed result into place only after all requested work succeeds. Git is
initialized by default, but Samsarix CLI does not change user identity, stage files, or create a
commit.

`samsarix check` validates bounded JSON and TOML input, rejects manifest path traversal, confirms the
declared generated files still exist, and uses exit code 1 for a failed check. `--json` provides a
stable non-interactive result for scripts and CI.

## Development

```bash
python -m pip install --upgrade pip "setuptools>=83,<84"
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy
pytest --cov=samsarix_cli --cov-report=term-missing
pip-audit --local --skip-editable
python -m build
python -m twine check dist/*
```

CI runs those checks on Python 3.11, 3.12, and 3.13, builds a wheel and source archive, validates
their metadata, installs the wheel into a fresh environment, and exercises `init` and `check` through
the installed command.

## Architecture

- `samsarix_cli/main.py` exposes the deliberately small Click command surface.
- `samsarix_cli/templates.py` contains the reviewed built-in starter renderers.
- `samsarix_cli/scaffold.py` owns name validation, bounded Git execution, atomic writes, and cleanup.
- `samsarix_cli/validation.py` treats generated-project metadata as untrusted input.
- `tests/` covers commands, all templates, packaging-critical behavior, and adversarial failures.

Samsarix CLI deliberately does not run arbitrary remote templates. This keeps project creation
offline and avoids the remote-code and template-provenance trust model of general-purpose generators.

## Security and privacy

Samsarix CLI sends no telemetry, stores no credentials, and does not contact an API. The optional Git
operation invokes the discovered Git executable with an argument list, a 20-second timeout, and no
shell. The Discord template reads its token only from the process environment and disables the
library's default log handler when passing the token.

Generated applications are development starters, not hardened internet deployments. Their owners
remain responsible for authentication, authorization, TLS, rate limits, secret management,
dependency updates, and production server configuration. Report vulnerabilities privately as
described in [SECURITY.md](SECURITY.md), or email
[support@samsarix.com](mailto:support@samsarix.com).

## Distribution and sustainability

The intended distribution name is `samsarix-cli`; both that name and `samsarix` returned no current
PyPI project record when checked on 2026-07-28. A name is not secured until Samsarix LLC publishes or
reserves it, so availability must be checked again immediately before release. No package has been
published and CI contains no publishing credential or release job.

The CLI has no hosted operating cost. A plausible sustainability path is paid support and maintained
organization-specific template packs while keeping the core local workflow account-free.

## Limitations

- Templates are intentionally built in; user-defined and remote template sources are not supported.
- `samsarix check` verifies structure and metadata, not user-edited application semantics.
- Dependency lockfiles are not generated because resolution is platform-specific; applications
  should adopt a lock workflow before production deployment.
- Only the FastAPI template is exercised as a fully installed and running end-to-end sample in local
  release verification; all templates receive generation, syntax, metadata, and focused tests.
- Renaming the legacy GitHub repository path and reserving the PyPI name remain owner-controlled.

## Contributing and contact

See [CONTRIBUTING.md](CONTRIBUTING.md) for the local workflow and
[docs/PRODUCTIZATION.md](docs/PRODUCTIZATION.md) for the audit, decisions, verification evidence, and
remaining priorities. General inquiries can be sent to
[contact@samsarix.com](mailto:contact@samsarix.com); support and security reports can be sent to
[support@samsarix.com](mailto:support@samsarix.com).

## License and brand

Copyright 2026 Samsarix LLC. Licensed under the [Apache License 2.0](LICENSE). Redistributions must
preserve the license and applicable attribution notices, including [NOTICE](NOTICE). The license does
not grant rights to use Samsarix brand identifiers to imply sponsorship or endorsement; see
[TRADEMARKS.md](TRADEMARKS.md).
