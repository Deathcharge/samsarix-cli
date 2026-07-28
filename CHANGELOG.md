# Changelog

All notable changes to this project will be documented here. The format follows Keep a Changelog,
and versions follow Python's PEP 440 representation of semantic release stages.

## [1.1.0rc2] - 2026-07-28

### Changed

- Rebranded the distribution, command, import package, manifests, and documentation from Helix to
  Samsarix CLI.
- Set Samsarix LLC as the project owner and added working general and support contacts.
- Replaced contradictory source-available/proprietary terms with the standard Apache License 2.0,
  an attribution `NOTICE`, and a separate brand-use policy.
- Selected the currently unclaimed `samsarix-cli` PyPI distribution name; publication remains an
  owner-controlled release action and the legacy GitHub repository path remains unchanged.

## [1.1.0rc1] - 2026-07-28

### Added

- Atomic, offline project generation for FastAPI, Flask, Streamlit, and Discord starters.
- `helix templates` with human-readable and JSON output.
- `helix check` with machine-readable output and adversarial manifest validation.
- Command, generation, failure-path, and security-boundary tests.
- Cross-version CI, distribution checks, and installed-wheel smoke coverage.
- Productization, security, and contribution documentation.

### Changed

- Narrowed the product from an unimplemented ecosystem control plane to an independently useful
  local project scaffolder.
- Reduced runtime dependencies to Click.
- Corrected package discovery, maturity metadata, Python support, and license metadata.
- Replaced synthetic Git identity and commit behavior with an empty, explicit repository init.

### Removed

- Deployment, monitoring, project-management, configuration, and ecosystem-statistic commands that
  displayed fabricated state or success without integrations.
- Generated references to an undocumented `helix-collective` package, private infrastructure, dummy
  API keys, and unsupported production deployment instructions.

## [1.0.0] - 2026-04-09

- Initial repository import. This version was not a credible public release: its built wheel omitted
  the command package, and most advertised commands returned simulated data.
