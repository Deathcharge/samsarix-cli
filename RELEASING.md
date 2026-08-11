# Releasing Samsarix CLI

Releases are built from an immutable tag by GitHub Actions. The workflow checks that the tag matches
the package version, builds the wheel and source archive, validates their metadata, exercises the
installed wheel, records SHA-256 checksums, creates build-provenance attestations, and attaches the
artifacts to a GitHub release. No release artifact should be built on a maintainer workstation and
uploaded manually.

## GitHub release

1. Update `samsarix_cli.__version__`, `CHANGELOG.md`, `CITATION.cff`, and user-facing version claims.
2. Run every check in `CONTRIBUTING.md` and merge the release pull request only after hosted CI is
   green.
3. Create an annotated tag named `v<package-version>` at the verified default-branch commit and push
   the tag.
4. Confirm the Release workflow succeeds, the GitHub release contains the wheel, source archive,
   and `SHA256SUMS`, and `gh attestation verify` accepts the downloaded artifacts for this repository.

Release candidates are marked as prereleases automatically when their version ends in `aN`, `bN`,
or `rcN`.

## PyPI trusted publishing

PyPI publication is deliberately separate from GitHub release creation. It uses OpenID Connect and
stores no long-lived PyPI token in GitHub.

Before the first publication, a Samsarix LLC-controlled PyPI account must configure a pending trusted
publisher with these exact values:

- PyPI project: `samsarix-cli`
- GitHub owner: `Deathcharge`
- GitHub repository: `samsarix-cli`
- workflow: `publish-pypi.yml`
- environment: `pypi`

After the pending publisher exists and the GitHub release is verified, run the `Publish to PyPI`
workflow on the default branch with the existing tag. Verify the resulting project page, metadata,
files, hashes, provenance, and a clean-environment installation. A pending publisher does not reserve
the name until its first successful upload.

PyPI files and versions cannot be replaced. If a published release is defective, yank it on PyPI,
mark the GitHub release accordingly, document the reason, and publish a new version; never reuse the
tag or version number.
