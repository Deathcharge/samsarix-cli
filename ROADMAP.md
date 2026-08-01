# Samsarix CLI roadmap

This roadmap separates four gates: merge, release, publication, and flagship adoption. Passing one does not imply the next.

## Product boundary

Portfolio role: **standalone product candidate**. Develop this as a focused standalone product with its own distribution and support boundary. Integrate with the flagship through versioned contracts, not shared private source.
Planned repository identity: `Deathcharge/samsarix-cli` (ready).

Current disposition: the productization and repository-coordinate pull requests are merged. The
reviewable team-template slice is implemented and verified for `1.2.0rc1`; package publication and
flagship adoption remain separate owner decisions.

## Competitive product thesis

Research was refreshed against primary product documentation on 2026-08-01:

- [uv `init`](https://docs.astral.sh/uv/concepts/projects/init/) is the baseline for fast generic
  Python application and library creation. Samsarix should not compete on environment management.
- [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/advanced/index.html) supports rich
  prompts, replay, extensions, and executable hooks. It is flexible, but teams must own a larger
  template and code-execution trust surface.
- [Copier](https://copier.readthedocs.io/en/v9.4.1/configuring/) supports questions and smart updates,
  while tasks, migrations, and extensions require explicit trust because they can execute arbitrary
  code.
- [Cruft](https://cruft.github.io/cruft/) adds update, diff, and CI freshness workflows to
  Cookiecutter projects by retaining template source and commit metadata.
- [GitHub template repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
  copy a repository quickly but create unrelated history and do not retain an update relationship.
- [Backstage Software Templates](https://backstage.io/docs/features/software-templates/) provide
  organization templates, an input review step, execution status, and publishing actions, but require
  a deployed developer portal and integrations.

The defensible Samsarix wedge is **safe, inspectable team scaffolding without a control plane**:

- built-in starters for immediate use;
- local declarative template packs for organization standards;
- no hooks, migrations, shell commands, network fetches, or arbitrary template extensions;
- a deterministic generation plan that can be reviewed as text or JSON before any write;
- recorded template identity and digest for provenance;
- structural checks by default and opt-in generated-content drift checks for CI or audits.

This is intentionally narrower than Cookiecutter or Copier and much lighter than Backstage. The
target users are security-conscious individuals and small platform teams that want repeatable
standards without operating a portal or executing template-supplied code.

## Release 1.2 slice: reviewable team templates

### Required workflows

1. A template author creates a bounded local pack containing metadata and UTF-8 template files.
2. A developer runs `samsarix inspect-template PACK` to validate its schema and see its digest.
3. A developer or CI job runs `samsarix plan DESTINATION --template-pack PACK --json` to review the
   exact file plan without creating a directory.
4. `samsarix init` generates the project atomically from either a built-in template or the pack and
   records versioned provenance plus per-file generated hashes.
5. `samsarix check` validates the project structure; `samsarix check --strict` additionally reports
   files changed since generation without executing project code.

### Safety and compatibility constraints

- Accept local directories only; reject URLs, symlinks, path traversal, reserved generator paths,
  unknown placeholders, non-UTF-8 content, duplicate rendered paths, oversized files, and excessive
  file counts.
- Support only explicit `@@PROJECT_NAME@@`, `@@MODULE_NAME@@`, and `@@COMMAND_NAME@@` substitution.
- Preserve existing `1.1.0rc2` manifests and built-in CLI behavior.
- Keep generation all-or-nothing and keep plan/inspection operations read-only.
- Add no runtime dependency beyond Click and the Python standard library.

### Acceptance evidence

- [x] Human and JSON contract tests for inspection and planning.
- [x] Adversarial template-pack tests for traversal, links/reparse points, encoding, bounds,
  collisions, and tokens.
- [x] Compatibility tests for old manifests plus strict drift tests for new manifests.
- [x] Installed-wheel smoke for built-in and local-pack generation.
- [x] Generated sample install, test, lint, format, and live endpoint evidence where applicable.
- [x] Exact-head Python 3.11-3.13 CI, artifact checks, dependency audit, and rollback path recorded in
  the pull request.

## Stabilize the productized default

- Keep the default branch buildable from a clean checkout and preserve exact-head CI evidence.
- Keep Samsarix LLC branding, package identity, license metadata, and compatibility aliases internally consistent.
- Preserve the pre-productization default under a rollback ref before merging; do not delete legacy history.
- Review priority: review branch plus owner approval of name and Apache license before tagged wheel publication.

## Later release candidates

- Add conflict-aware template updates only after provenance and drift semantics are proven.
- Run a small user pilot against the exact packaged artifact.
- Instrument only truthful, privacy-respecting product signals and define support ownership.
- Promote from prerelease only after recovery, upgrade, and failure paths are demonstrated.

## Samsarix adoption

- Define a public API, event, schema, artifact, or deployment contract before connecting to Samsarix Unified.
- Add a consumer-owned contract fixture covering authentication, privacy, limits, errors, and version compatibility.
- Make one implementation canonical; remove or freeze duplicate behavior only after parity and rollback are proven.
- Record an owner, support level, compatibility window, and measurable adoption signal.

## Completion evidence

A milestone is complete only when its exact commit, commands and results, artifact digest, consumer or deployment, and rollback path are recorded in a pull request or release record. README claims must not exceed that evidence.
