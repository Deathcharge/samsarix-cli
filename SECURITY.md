# Security policy

## Supported scope

The `1.1.x` release-candidate line receives security fixes while it is under evaluation. The initial
`1.0.0` code is unsupported because its installed package was incomplete and its operational
commands were simulations.

## Report a vulnerability

Use GitHub's private vulnerability-reporting or Security Advisory feature for this repository when
available. Do not place credentials, exploit payloads containing private data, or an unpatched
high-impact vulnerability in a public issue. If private reporting is not enabled, open a minimal
public issue requesting a private contact channel without disclosing sensitive details, or email
support@samsarix.com.

Include the affected version, platform, reproduction steps, impact, and any safe mitigation you
have identified. No response-time or bounty commitment is implied.

## Security model

Samsarix CLI is a local code generator. It makes no network requests, executes no generated project,
and only writes to a destination that does not already exist. Optional Git initialization uses an
argument-vector subprocess with no shell and a bounded timeout.

The `.samsarix/project.json` manifest is untrusted: reads are size-bounded, paths must be relative POSIX
paths, traversal and external symlink resolution are rejected, and the file count is capped. The
check command never executes project code.

Generated applications are development starters. Security controls for a public deployment—such as
authentication, authorization, TLS, request limits, production process management, secret storage,
and dependency monitoring—are the generated project's owner's responsibility.
