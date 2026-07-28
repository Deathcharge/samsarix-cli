# Productization record

Last updated: 2026-07-28

## Repository assessment

The repository began as a 12-file Python CLI with two commits and no tests, CI, changelog, release
automation, or generated artifacts committed. The working tree was clean on `master` at
`0a94f98` before productization, and the only locally available branch was `master` plus its matching
`origin/master` remote reference. Work was moved to `codex/productize-scaffolder` before edits.

The apparent intent was to give developers one CLI for Helix project initialization, configuration,
deployment, monitoring, and project operations. In practice, only file scaffolding performed work.
Every operational command printed fixed success states, dates, URLs, credentials, metrics, backups,
and logs. Generated templates imported an undocumented `helix-collective` distribution and embedded
unverified deployment instructions. The README presented all of this as a stable 1.0 release.

The built package was also structurally broken: `[tool.setuptools] packages = ["helix_cli"]` omitted
`helix_cli.commands`. A clean installation of the resulting wheel failed on `helix --help` with
`ModuleNotFoundError: No module named 'helix_cli.commands'`.

## Chosen product

Helix CLI is now an offline generator for small, independent Python application starters. Its target
user is a Python developer who wants to create a framework-specific project, understand every file,
run it locally, and validate the original scaffold without private Helix knowledge.

The primary journey is:

1. install Helix from a reviewed source checkout or tag;
2. inspect `helix templates`;
3. run `helix init DESTINATION --template fastapi`;
4. run `helix check DESTINATION`;
5. enter the generated project, install `.[dev]`, run its tests, and start its local health endpoint.

This product exists independently of `helix-unified`: it generates ordinary Python projects that no
longer need Helix CLI after creation. Deployment control planes, fleet monitoring, remote state,
project registries, AI orchestration, authentication, billing, and arbitrary remote templates are
deliberately out of scope.

## Evidence-based market and ecosystem decisions

Research was bounded to official or primary sources on 2026-07-28:

- [uv `init`](https://docs.astral.sh/uv/concepts/projects/init/) already provides excellent generic
  Python application and library initialization. Helix therefore focuses on small reviewed
  framework starters instead of duplicating package/environment management.
- [Cookiecutter](https://cookiecutter.readthedocs.io/) is a mature general project-template engine.
  Helix avoids arbitrary remote template evaluation and its larger trust/configuration surface.
- [Copier](https://copier.readthedocs.io/en/stable/updating/) supports updating generated projects.
  Template upgrades are a valuable P2 direction, but safe merging is not required for the first
  credible release.
- [PyPA's current metadata guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
  recommends SPDX expressions and `license-files`; because the repository's two license documents
  conflict, metadata now uses a custom `LicenseRef` and ships both rather than claiming Apache.
- [Setuptools package-discovery guidance](https://setuptools.pypa.io/en/stable/userguide/package_discovery.html)
  confirms that the former explicit package list disabled discovery and omitted subpackages.
- [PyPI's `helix-cli` record](https://pypi.org/project/helix-cli/) shows that a different publisher
  uploaded version 0.1.0 on 2025-07-07. Public naming is therefore an owner-controlled release gate.

No evidence supports a claim of product-market fit. This release candidate is coherent and suitable
for real-user validation.

The sole runtime dependency, Click, identifies itself with the OSI-approved BSD license classifier.
Development-only tools are not redistributed in the wheel. No dependency-license issue was found,
but the repository's own conflicting license texts prevent a final compatibility/legal conclusion.

## Key product and architecture decisions

- Keep `helix` as the local command while treating the public distribution name as unresolved.
- Preserve all four evidenced starter categories, but remove their imaginary Helix dependency and
  make each a conventional standalone project.
- Reduce the runtime dependency set from six packages to Click alone.
- Support Python 3.11+ so safe TOML parsing uses the standard library.
- Stage generation in a sibling temporary directory and atomically rename it; never support force
  overwrite in the release candidate.
- Initialize a real empty Git repository by default without changing identity or making a synthetic
  commit. Allow `--no-git` and fail with a recovery instruction if Git is unavailable.
- Store a bounded `.helix/project.json` manifest. `helix check` validates structure but never executes
  generated code or treats the manifest as trusted.
- Require the current patched setuptools 83.x line for isolated builds and document upgrading the
  clean environment's pip/setuptools bootstrap tools before installation.
- Keep templates in Python source so the wheel has no fragile package-data dependency.
- Do not generate a license, secret-filled `.env`, Docker/Kubernetes assets, cloud configuration, or
  deployment claims.

## Assumptions

- The repository owner wants the strongest product supported by existing code, not compatibility
  with misleading simulated commands.
- A source-installed release candidate is useful while naming and licensing are decided.
- Built-in templates are preferable to remote templates at this maturity and security posture.
- Python 3.11 is an acceptable minimum for a newly honest release in 2026.

## Baseline command results

All baseline commands were run on Windows with Python 3.11.9 before implementation:

| Command | Actual result |
| --- | --- |
| `git status --short --branch` | exit 0; clean `master...origin/master` |
| `python -m pytest` | exit 1; collected 0 tests |
| `python -m black --check .` | exit 1; 6 files would be reformatted |
| `python -m flake8 helix_cli` | failed with extensive whitespace and line-length violations |
| `python -m mypy helix_cli` | exit 0; 8 source files checked |
| `python -m build` | exit 1; `build` was absent from documented development dependencies |
| `python -m helix_cli.main --help` | exit 1; CP1252 `UnicodeEncodeError` on the DNA emoji |
| `python -m helix_cli.main --version` | exit 0 with a runpy double-import warning |
| `python -m pip wheel . --no-deps` | exit 0; wheel contained `main.py` but omitted `commands/` |
| clean-wheel `helix --help` | exit 1; `ModuleNotFoundError: helix_cli.commands` |

No baseline lint, test, help, or installed-package claim is recorded as passing when it did not.

## Findings and disposition

| Priority | Finding | Disposition |
| --- | --- | --- |
| P0 | Installed wheel omitted every command module | Fixed with explicit recursive discovery and wheel tests |
| P0 | Help crashed on common Windows console encoding | Fixed by an ASCII-safe command surface and regression test |
| P0 | Core advertised commands fabricated operational success/data | Fixed by removing them and narrowing the product |
| P0 | Generated code required imaginary infrastructure/package APIs | Fixed; generated projects are independent |
| P0 | No tests or CI protected installation and primary journey | Fixed with command/library/adversarial tests and CI |
| P1 | Scaffold changed cwd, invoked shell text, created fake Git identity/commit | Fixed with bounded argument-vector subprocess and no commit |
| P1 | Existing destination and partial-write behavior lacked robust recovery | Fixed with refusal, staging, atomic move, and cleanup tests |
| P1 | Metadata claimed production stability and Apache licensing | Fixed locally; final legal position remains owner-blocked |
| P1 | Runtime dependencies were mostly unused | Fixed; Click is the only runtime dependency |
| P1 | Python 3.11 venv bootstrap pip/setuptools had current advisories | Fixed in setup/CI guidance and build bounds |
| P1 | README documented commands, packages, and production state that did not exist | Rewritten around verified behavior |
| P1 | PyPI distribution identity conflicts with an existing publisher | Owner decision required before public publication |
| P2 | Generated projects do not receive future template updates | Deferred; safe merge semantics require separate design |
| P2 | Only one framework receives installed/running release smoke validation | Deferred; generation and syntax checks cover all four |
| P2 | No shell completion artifacts | Deferred until naming and command surface stabilize |

## Implementation checklist

- [x] Preserve and record the initial clean worktree.
- [x] Remove simulated operational surfaces.
- [x] Implement strict, portable project-name validation.
- [x] Implement all-or-nothing file generation and recovery.
- [x] Generate independent FastAPI, Flask, Streamlit, and Discord projects.
- [x] Add useful `--help`, `--version`, `templates`, `init`, and `check` behavior.
- [x] Add human and JSON output for discovery and validation.
- [x] Bound Git execution and untrusted manifest/TOML reads.
- [x] Test all templates, ordinary failures, and adversarial manifest cases.
- [x] Audit the isolated release environment after upgrading bootstrap tooling.
- [x] Correct package discovery, metadata, and development dependencies.
- [x] Add CI, changelog, security policy, contribution guide, and accurate README.
- [ ] Resolve the public distribution name with the owner.
- [ ] Resolve conflicting license terms with owner/legal review.
- [ ] Run external CI on Python 3.12 and 3.13 after pushing a review branch.

## Release acceptance criteria

- `helix --help` and `helix --version` work from an installed wheel on Windows.
- `helix init` produces a complete project or leaves no destination behind.
- Existing paths are never overwritten.
- The documented FastAPI project installs, tests, starts, and returns its health payload.
- Every template renders valid TOML and syntactically valid Python.
- `helix check` returns meaningful output and exit codes for valid and damaged projects.
- Format, lint, strict type check, tests with at least 90% branch coverage, dependency audit, build, metadata check,
  wheel contents, and fresh-wheel smoke all pass.
- Documentation makes no claim of PyPI ownership, production deployment, or private Helix service.
- No locally actionable P0 remains.
- Owner-controlled name and license gates are called out before public release.

## Final verification results

Final local verification ran on Windows with Python 3.11.9 against the final source and rebuilt
`1.1.0rc1` artifacts:

| Command | Actual result |
| --- | --- |
| `python -m ruff format --check .` | exit 0; 13 files already formatted |
| `python -m ruff check .` | exit 0; all checks passed |
| `python -m mypy` | exit 0; no issues in 13 source files |
| `python -m pytest --cov=helix_cli --cov-report=term-missing` | exit 0; 44 passed; 94.66% branch coverage |
| `git diff --check` | exit 0; no whitespace errors |
| `python -m build` | exit 0; built wheel and sdist in isolated setuptools 83.x environments |
| `python -m twine check dist/*` | exit 0; wheel and sdist passed |
| `python -m zipfile -l dist\\helix_cli-1.1.0rc1-py3-none-any.whl` | exit 0; all command/core modules and both license files present |
| `tar -tf dist\\helix_cli-1.1.0rc1.tar.gz` | exit 0; code, tests, changelog, contribution/security docs, and this record present |
| isolated-wheel `helix --version` / `helix --help` | exit 0; version `1.1.0rc1`; ASCII-safe command surface |
| isolated-wheel `helix init ... --template fastapi --no-git` | exit 0; 7-file independent project created |
| isolated-wheel `helix check ...` | exit 0; project valid |
| generated-project `python -m pip install -e "...[dev]"` | exit 0 using the generated setuptools 83.x build bound |
| generated-project `python -m pytest` | exit 0; 1 passed |
| generated-project `python -m ruff check .` | exit 0; all checks passed |
| generated-project `python -m ruff format --check .` | exit 0; 4 files formatted |
| generated `final-smoke` plus `Invoke-RestMethod http://127.0.0.1:8000/health` | HTTP 200; `{"status":"ok"}`; clean application shutdown on Ctrl+C |
| `python -m pip_audit --path <isolated site-packages> --progress-spinner off --timeout 20` | exit 0; no known vulnerabilities; local unpublished projects skipped by name |

The first isolated vulnerability audit correctly failed on the Python 3.11 venv's bundled pip 24.0
and setuptools 65.5.0. After adding the documented upgrade step and requiring setuptools 83.x, the
same audit passed with pip 26.1.2 and setuptools 83.0.0. This failure was not suppressed.

Not run locally: Python 3.12/3.13 jobs, GitHub-hosted CI, TestPyPI/PyPI publication, or a production
deployment. Only Python 3.11 is installed here; external CI requires a pushed branch, and publication
or deployment is explicitly blocked by owner decisions and credentials.

## Completed work

The implementation now replaces the facade CLI with a bounded local product; reduces dependency,
packaging, and security surface; makes the main journey reversible and automation-friendly; adds a
real release verification system; and rewrites product, user, contribution, change, and security
documentation around implemented behavior.

## Deferred and owner-blocked work

Owner action is required before public publication:

1. **Distribution name:** choose an available PyPI name or demonstrate authorized control of the
   existing `helix-cli` project. Update `[project].name`, installation docs, and release workflow;
   verify the final name on TestPyPI and PyPI without spending or publishing from this task.
2. **License:** reconcile `LICENSE` and `LICENSE.PROPRIETARY` with qualified legal review. Replace the
   custom metadata reference only after one governing position is approved; verify sdist/wheel
   metadata and README language afterward.
3. **External CI/release protection:** push the review branch, require the CI workflow, configure
   trusted publishing only after the name/license gates, and verify a tagged dry run. Credentials and
   repository settings were not fabricated or changed.

P2 template-update semantics, additional installed framework smoke jobs, completion scripts, and a
plugin contract remain deferred because they do not block first user validation.

## Known risks

- Framework dependency ranges are bounded but not locked in generated projects; owners need a lock
  and update policy before production deployment.
- Built-in source templates are intentionally coupled to CLI releases. Existing generated projects
  do not auto-update, which avoids surprising user-code rewrites but leaves maintenance manual.
- Git availability and filesystem rename semantics vary; failure paths are tested locally on Windows
  and CI is designed to add Linux/multiple-Python evidence.
- Generated applications expose development servers only. Production exposure needs product-specific
  security and operations work outside this generator's scope.

## Security, privacy, reliability, and cost

Helix makes no network requests, collects no telemetry, persists no secrets, and has no hosted
operating cost. Project creation is local and bounded. It refuses destructive overwrite, avoids the
shell, times out Git, limits manifest/TOML size and file count, and rejects traversal or resolved
external paths. The Discord starter requests default intents and validates its token without logging
or storing it.

Generated frameworks can incur whatever infrastructure cost their owner later chooses, but the
starter does not select a cloud, AI provider, database, paid service, or recurring job. A support or
maintained-template business is plausible after licensing; a usage subscription is not justified by
this local product.

## Proposed release and sustainability model

After the owner resolves naming and licensing, publish signed/tagged source plus a wheel and sdist
through trusted publishing, protected by CI and an installed-wheel smoke test. Keep the core local
generator usable without an account. If there is validated demand, sell support and private reviewed
template maintenance rather than adding a hosted dependency to manufacture recurring revenue.

## Release disposition

**Release-candidate with named external gates.** The local product has no known actionable P0 and its
primary journey is verified from the installed wheel through a live health request. It should not be
published publicly until the owner resolves the occupied PyPI name, reconciles the license files,
and obtains green GitHub-hosted Python 3.11-3.13 CI evidence on the review branch.
