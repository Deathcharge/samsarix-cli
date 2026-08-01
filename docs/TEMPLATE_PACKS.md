# Authoring Samsarix template packs

A template pack is a local, declarative directory that Samsarix can inspect and render without
executing template-supplied code. It is intended for a team that wants a version-controlled Python
starter but does not want to operate a developer portal or trust arbitrary scaffolding hooks.

The complete example lives at [`examples/team-service`](../examples/team-service).

## Directory contract

```text
my-pack/
|-- samsarix-template.toml
`-- template/
    |-- README.md
    |-- pyproject.toml
    |-- src/
    |   `-- @@MODULE_NAME@@/
    |       `-- __init__.py
    `-- tests/
        `-- test_app.py
```

`samsarix-template.toml` has exactly four top-level fields:

```toml
schema_version = 1
name = "team-service"
version = "1.0.0"
description = "A short, single-line description."
```

- `name` is a lowercase, kebab-case identifier of at most 64 characters.
- `version` is a 1-64 character release identifier. Increment it when the pack changes.
- `description` is one non-empty line of at most 256 characters.
- `template/` must contain at least one regular UTF-8 text file.

Template paths and contents support only these literal substitutions:

| Placeholder | Example for project `Orders_API` |
| --- | --- |
| `@@PROJECT_NAME@@` | `Orders_API` |
| `@@MODULE_NAME@@` | `orders_api` |
| `@@COMMAND_NAME@@` | `orders-api` |

Unknown placeholders are errors. There are no conditionals, prompts, filters, includes, hook
scripts, or template-language expressions.

## Review and generate

Validate the source pack and record its deterministic SHA-256 digest:

```bash
samsarix inspect-template my-pack
samsarix inspect-template my-pack --json > template-review.json
```

Preview the rendered identity and exact file list. This does not create the destination or its
parent:

```bash
samsarix plan services/orders --template-pack my-pack
samsarix plan services/orders --template-pack my-pack --json > generation-plan.json
```

Generate only after review:

```bash
samsarix init services/orders --template-pack my-pack
samsarix check services/orders
samsarix check services/orders --strict
```

The project manifest records the pack name, version, digest, generated paths, and the SHA-256 digest
of every generated file. The normal check validates structure and provenance metadata. The strict
check additionally reports any generated file whose bytes have changed. A drift report is evidence
of a difference, not a claim that the edit is wrong.

For CI, keep the pack in a reviewed repository or artifact, verify the expected `inspect-template`
digest, save the JSON plan as build evidence, then generate from that exact local directory.

## Safety boundary

Samsarix rejects:

- URLs and non-directory sources;
- symbolic links at the pack root or anywhere in metadata and template content;
- absolute paths, traversal, backslashes, `.git`, `.samsarix`, Windows reserved names, and
  non-portable rendered paths;
- duplicate paths after case-insensitive normalization;
- unknown metadata fields or placeholders;
- non-UTF-8 and non-regular files;
- metadata over 64 KiB, individual files over 1 MiB, total content over 4 MiB, more than 256
  template files, or a rendered manifest over 64 KiB.

Line endings are normalized to LF before the pack digest and generated-file hashes are calculated.
Generation still uses Samsarix's temporary sibling directory and atomic final move, so a failed
write or Git initialization does not leave a partial destination.

These controls limit what Samsarix itself reads and writes. Generated Python is still source code:
review it before installation or execution, just as you would review source copied from any
repository. Samsarix does not fetch dependencies while inspecting, planning, or generating.

## Versioning and distribution

Keep a pack and its review history in source control. Tag pack releases, distribute immutable
archives through an existing internal artifact channel if needed, and have consumers verify the
expected digest before generation. Do not reuse a version for different content: the digest will
expose the difference, but unique versions make support and incident response easier.

Template authors decide whether generated files include a license. The Samsarix CLI Apache-2.0
license applies to Samsarix itself and does not impose a license choice on independently generated
projects.
