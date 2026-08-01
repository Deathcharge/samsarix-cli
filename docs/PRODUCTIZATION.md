# Productization record

Last updated: 2026-08-01

## Repository assessment

The repository began as a 12-file Python CLI with two commits and no tests, CI, changelog, or release
automation. The worktree was clean on `master` at `0a94f98`; productization moved to
`codex/productize-scaffolder` before edits.

The former Helix-branded code claimed project initialization, configuration, deployment, monitoring,
and project operations. Only file scaffolding performed work. Operational commands printed fixed
success states, dates, URLs, credentials, metrics, backups, and logs. Generated templates imported an
undocumented `helix-collective` distribution and embedded unverified deployment instructions.

The built package was also structurally broken: `[tool.setuptools] packages = ["helix_cli"]` omitted
`helix_cli.commands`. A clean installation of its wheel failed on `helix --help` with
`ModuleNotFoundError`.

## Chosen product and identity

Samsarix CLI is an offline generator for small, independent Python application starters. Its target
users are developers and small platform teams that want to create a reviewed project baseline,
understand every file, and validate its provenance without a private platform or account.

The primary journey is:

1. install Samsarix CLI from a reviewed source checkout, tag, or wheel;
2. inspect a built-in with `samsarix templates` or a local pack with `samsarix inspect-template`;
3. review `samsarix plan DESTINATION` in human or JSON form;
4. run `samsarix init` with a built-in or local pack;
5. run the structural check and, when appropriate, `samsarix check --strict` for baseline drift;
6. install the generated project's development dependencies, run its tests, and start its documented
   local process, such as a health endpoint when the template provides one.

The 2026-07-28 owner decision moved the brand to Samsarix, identified Samsarix LLC as the company,
provided `contact@samsarix.com` and `support@samsarix.com`, requested relevant repository updates,
and authorized commits and a push. The release identity is now:

- product: Samsarix CLI;
- distribution: `samsarix-cli`;
- command: `samsarix`;
- import package: `samsarix_cli`;
- generated-project manifest: `.samsarix/project.json`;
- copyright owner: Samsarix LLC.

The canonical GitHub repository is `Deathcharge/samsarix-cli`; the former Helix slug is retained only through GitHub's redirect and repository history.

## Evidence-based ecosystem and license decisions

Research was bounded to official or primary sources on 2026-07-28:

- [uv `init`](https://docs.astral.sh/uv/concepts/projects/init/) already provides generic Python
  application/library initialization, so Samsarix focuses on reviewed framework starters.
- [Cookiecutter](https://cookiecutter.readthedocs.io/) is a mature general template engine. Samsarix
  avoids arbitrary remote template evaluation and its larger provenance surface.
- [Copier](https://copier.readthedocs.io/en/stable/updating/) supports project updates. Safe template
  upgrades are valuable but are not required for the first credible release.
- [PyPA's metadata guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
  supports SPDX license expressions and `license-files`; metadata now uses `Apache-2.0` and ships
  `LICENSE`, `NOTICE`, and the brand policy.
- [Setuptools discovery guidance](https://setuptools.pypa.io/en/stable/userguide/package_discovery.html)
  confirms why the former explicit package list omitted subpackages.
- [PyPI's `helix-cli` record](https://pypi.org/project/helix-cli/) belongs to another publisher.
  Direct checks for both `samsarix-cli` and `samsarix` returned no project record on 2026-07-28.
  Availability can change and is not secured until publication or reservation.
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) requires preservation of relevant
  notices and a shipped `NOTICE`, grants an explicit patent license, and grants no trademark rights.
- [GNU's license overview](https://www.gnu.org/licenses/) describes GPL as copyleft and AGPL's extra
  source obligation for network-interactive software. The latter is not a meaningful advantage for
  this offline CLI.
- [MariaDB's BSL 1.1 page](https://mariadb.com/bsl11/) explicitly states that BSL is not open source
  before its change date. The former repository text also had ambiguous use limits and conflicted
  with a proprietary file.

Apache-2.0 plus `NOTICE` and a separate brand policy is the recommended balance for this developer
tool: broad commercial and open-source adoption, durable attribution requirements, patent clarity,
and no implied Samsarix endorsement. GPLv3 would be preferable only if reciprocal publication of
distributed derivatives outweighed adoption; AGPLv3 would be preferable for network software where
server modifications must be offered to users. BSL or a proprietary dual-license model would protect
commercial exclusivity more strongly, but would make this small local generator harder to adopt and
require a deliberately operated commercial-license program.

This is an engineering recommendation, not a substitute for qualified legal advice about title,
trademark clearance, contributor provenance, or company-specific risk.

## Key product and architecture decisions

- Preserve all four evidenced starter categories as conventional standalone projects.
- Keep Click as the sole runtime dependency and Python 3.11 as the minimum.
- Stage generation in a sibling temporary directory and atomically rename it; never overwrite an
  existing destination.
- Initialize a real empty Git repository by default without changing identity, staging, or committing.
- Store a bounded `.samsarix/project.json` manifest. `samsarix check` validates structure but never
  executes generated code or trusts manifest paths.
- Accept bounded local UTF-8 template packs while rejecting links/reparse points, traversal,
  non-portable paths, unknown placeholders, unbounded trees, and reserved generator paths.
- Provide a read-only exact plan and record template/version/digest plus generated-file hashes.
- Keep templates in Python source so the wheel has no fragile package-data dependency.
- Do not generate a license, secret-filled `.env`, cloud assets, or production deployment claims.
- Do not retain a legacy `helix` executable or import alias: rc1 was unreleased, and a clean break
  prevents a permanent dual identity and collision with the occupied PyPI name.

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
| `python -m helix_cli.main --help` | exit 1; CP1252 `UnicodeEncodeError` |
| `python -m pip wheel . --no-deps` | exit 0; wheel omitted `commands/` |
| clean-wheel `helix --help` | exit 1; `ModuleNotFoundError: helix_cli.commands` |

No baseline claim is recorded as passing when it did not.

## Findings and disposition

| Priority | Finding | Disposition |
| --- | --- | --- |
| P0 | Installed wheel omitted every command module | Fixed with recursive discovery and wheel smoke tests |
| P0 | Help crashed on common Windows console encoding | Fixed with an ASCII-safe surface and regression test |
| P0 | Advertised commands fabricated operational success/data | Fixed by removing them and narrowing the product |
| P0 | Generated code required imaginary infrastructure | Fixed; generated projects are independent |
| P0 | No tests or CI protected installation and primary journey | Fixed with command/library/adversarial tests and CI |
| P1 | Scaffold used risky process/filesystem behavior | Fixed with bounded argument-vector Git and atomic writes |
| P1 | Metadata claimed stability and contradictory licensing | Fixed with beta metadata and one standard license |
| P1 | Runtime dependencies were mostly unused | Fixed; Click is the only runtime dependency |
| P1 | README documented nonexistent behavior | Rewritten around verified behavior |
| P1 | PyPI identity collided with another publisher | Fixed in source with `samsarix-cli`; external reservation remains |
| P2 | Generated projects do not receive template updates | Deferred; safe merge semantics need a separate design |
| P2 | Only selected samples receive installed/running smoke validation | Improved with installed `team-service`; all built-ins receive generation and syntax tests |
| P1 | Pack enumeration could traverse an unbounded empty directory tree | Fixed with a 1,024-entry bound applied during traversal |
| P1 | Windows junctions could bypass symbolic-link-only checks | Fixed by rejecting filesystem reparse points |

## Implementation checklist

- [x] Preserve and record the initial clean worktree.
- [x] Remove simulated operational surfaces.
- [x] Implement portable name validation, atomic generation, and recovery.
- [x] Generate independent FastAPI, Flask, Streamlit, and Discord projects.
- [x] Add useful `--help`, `--version`, `templates`, `init`, and `check` behavior.
- [x] Bound Git execution and untrusted manifest/TOML reads.
- [x] Add command, template, failure, and adversarial tests.
- [x] Correct package discovery, metadata, and development dependencies.
- [x] Add CI, changelog, security policy, contribution guide, and accurate README.
- [x] Apply the Samsarix identity and working company contacts.
- [x] Replace conflicting terms with Apache-2.0, `NOTICE`, and a brand policy.
- [x] Obtain green GitHub-hosted Python 3.11-3.13 CI on the pushed branch.
- [x] Add non-executing local packs, deterministic plans, provenance, and strict drift checks.
- [x] Add an independently runnable team pack and installed-wheel workflow coverage.
- [x] Bound total pack traversal and reject symbolic links plus Windows reparse points.
- [ ] Reserve/publish `samsarix-cli` through an owner-controlled PyPI organization/account.

## Release acceptance criteria

- `samsarix --help` and `samsarix --version` work from an installed wheel on Windows.
- `samsarix init` produces a complete project or leaves no destination behind.
- Existing paths are never overwritten.
- The generated FastAPI project installs, tests, starts, and returns its health payload.
- Every template renders valid TOML and syntactically valid Python.
- `samsarix check` returns meaningful output and exit codes for valid and damaged projects.
- Format, lint, strict type check, 90%+ branch coverage, dependency audit, build, metadata check,
  artifact inspection, and fresh-wheel smoke pass.
- The wheel and sdist expose only Samsarix runtime identity and ship the correct license/notice files.
- Documentation makes no claim of publication, production deployment, or private infrastructure.
- No locally actionable P0 remains.

## Verification history

The pre-rebrand `1.1.0rc1` candidate passed format, Ruff lint, strict mypy, 44 tests with 94.66%
branch coverage, build, Twine metadata checks, wheel/sdist inspection, isolated-wheel CLI smoke, a
generated FastAPI install/test/lint/format run, a live HTTP 200 health check, and an isolated
dependency audit with no known vulnerabilities after bootstrap-tool upgrades.

The `1.1.0rc2` rebrand was verified on Windows with Python 3.11.9:

| Command/check | Actual result |
| --- | --- |
| `python -m ruff format .` / `python -m ruff check .` | 1 file normalized; lint exit 0 |
| `python -m mypy` | exit 0; no issues in 13 source/test files |
| `python -m pytest --cov=samsarix_cli --cov-report=term-missing` | exit 0; 44 passed; 94.66% branch coverage |
| `git diff --check` | exit 0; no whitespace errors |
| `python -m build --outdir <isolated>` | exit 0; rc2 wheel built from rc2 sdist |
| `python -m twine check <isolated>/*` | exit 0; wheel and sdist passed |
| artifact inspection | only `samsarix_cli` runtime modules; license/notice and project docs present |
| fresh-wheel `samsarix --version` / `--help` / `templates --json` | exit 0; version `1.1.0rc2`; four templates |
| fresh-wheel `samsarix init ...` / `samsarix check ... --json` | exit 0; 7-file FastAPI project; `valid: true` |
| installed metadata | `samsarix-cli`, `Apache-2.0`, Samsarix LLC contact; no `helix` executable/import |
| generated-project editable install and `pytest` | exit 0; 1 passed |
| generated-project Ruff lint/format | exit 0; all checks passed; 4 files already formatted |
| live generated `/health` request | HTTP 200; `{"status":"ok"}`; orderly application shutdown |
| pip-audit OSV against fresh wheel environment | exit 0; no known vulnerabilities |
| canonical Apache text comparison | exact normalized text and SHA-256 match with Apache's official file |
| GitHub Actions Python 3.11, 3.12, 3.13 quality jobs | exit 0; format, lint, mypy, tests, and audits passed |
| GitHub Actions package job | exit 0; build, Twine check, and installed-wheel smoke passed |

The first dependency-audit attempt against pip-audit's PyPI backend ended before results when its TLS
connection was reset (`WinError 10054`). The OSV retry succeeded; the network failure was not treated
as a passing audit. Python 3.12/3.13 were not available locally, so those versions were verified by
GitHub-hosted CI. The first hosted run passed but warned that the pinned action versions used the
deprecated Node 20 runtime; the workflow was then updated to the official Node 24-based major
versions and rerun.

The `1.2.0rc1` team-template candidate was verified on Windows and on GitHub-hosted Linux:

| Command/check | Actual result |
| --- | --- |
| `ruff format --check .` / `ruff check .` | exit 0; 19 files formatted; lint passed |
| Python 3.11 `mypy` | exit 0; no issues in 19 source/test files |
| `pytest --cov=samsarix_cli --cov-report=term-missing` | exit 0; 76 passed; 91.93% branch coverage |
| generated `team-service` tests and Ruff checks | exit 0; 1 passed; lint/format passed |
| generated FastAPI tests and Ruff checks | exit 0; 1 passed; lint/format passed |
| live generated FastAPI `/health` | HTTP 200; `{"status":"ok"}` |
| local build and Twine metadata check | rc1 wheel/sdist built; both passed Twine |
| wheel artifact inspection | runtime package/commands and license files present; tests/examples excluded |
| sdist artifact inspection | authoring docs, tests, and complete `team-service` pack present |
| installed-wheel CLI journeys | version/help, inspect, plan, built-in/local init, and strict checks passed |
| GitHub Actions push and PR runs at `e1350a6` | all Python 3.11-3.13 quality jobs and package jobs passed |
| hosted installed-wheel team-pack journey | inspect, plan, init, strict check, install, test, lint, format passed |
| hosted dependency audits | passed on Python 3.11, 3.12, and 3.13 |

The local package index did not respond while creating a new dependency environment, so two local
pip installation attempts exhausted their 3- and 5-minute command bounds. The local wheel was
therefore built without isolation for artifact inspection and installed with dependencies from the
existing Python 3.11 environment. Exact isolated builds, dependency resolution, audits, and a fresh
generated-project install passed in the GitHub package/quality jobs; the local index timeouts are not
counted as passing checks.

An app-backed Codex Security workspace also failed during launcher setup. A manual repository pass
covered the template/manifest trust boundaries and found the unbounded-tree, junction, and
placeholder-contract hardening addressed in this release, but no app-generated security report is
claimed.

## Known risks and deferred work

1. **Name control (P1):** a PyPI 404 is evidence of current availability, not ownership; Samsarix LLC
   must reserve or publish the distribution before another party does.
2. **Framework depth (P2):** expand installed smoke checks across all built-ins as maintenance value
   grows.
3. **Template evolution (P2):** design explicit diff/merge semantics before offering upgrades.
4. **Legal review (owner-controlled):** counsel should confirm title/provenance and desired trademark
   protection before a major commercial launch. This does not block an honest Apache-2.0 release.

Framework dependency ranges are bounded but not locked in generated projects. Owners need a lock and
update policy before production deployment. Generated applications expose development servers only;
production security and operations remain outside this generator's scope.

## Security, privacy, reliability, and cost

Samsarix CLI makes no network requests, collects no telemetry, persists no secrets, and has no hosted
operating cost. Project creation refuses overwrite, avoids a shell, times out Git, limits manifest and
TOML size/file count, and rejects traversal or resolved external paths. The Discord starter requests
default intents and validates its token without logging or storing it.

Generated frameworks can incur infrastructure cost their owner later chooses, but the starter does
not select a cloud, AI provider, database, paid service, or recurring job. Paid support and private
reviewed template maintenance are plausible without making the open core account-dependent.

## Release disposition

**Verified release candidate with one publication gate.** The product has no known actionable P0,
and exact-head hosted multi-version quality/package CI passes. The remaining distribution gate is
owner-controlled PyPI name reservation/publication. Formal legal/trademark review remains prudent
before a major commercial launch but does not require more local product code.
