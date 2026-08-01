"""Health-contract tests."""

from @@MODULE_NAME@@.main import health_payload


def test_health_payload_is_stable() -> None:
    assert health_payload() == {"service": "@@PROJECT_NAME@@", "status": "ok"}
