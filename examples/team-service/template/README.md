# @@PROJECT_NAME@@

A dependency-free HTTP health service generated from the Samsarix CLI `team-service` pack.

## Set up

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

Activate `.venv` using the command for your shell, then run:

```bash
@@COMMAND_NAME@@
```

Open <http://127.0.0.1:8000/health>. The response is:

```json
{"service":"@@PROJECT_NAME@@","status":"ok"}
```

## Verify

```bash
pytest
ruff format --check .
ruff check .
samsarix check --strict .
```

The last command verifies the generated baseline. It will report intentional edits to generated
files as drift, so use the default `samsarix check .` when only the structure matters.

## Production boundary

This starter is a development baseline. Add your organization's authentication, authorization,
TLS, observability, deployment, rate-limit, and dependency-management standards before exposing it
to untrusted traffic.

## License

No license is selected for generated code. Choose terms appropriate for your organization before
distribution.
