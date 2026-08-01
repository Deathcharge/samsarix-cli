"""A minimal dependency-free health service."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


def health_payload() -> dict[str, str]:
    """Return the stable service health contract."""
    return {"service": "@@PROJECT_NAME@@", "status": "ok"}


class HealthHandler(BaseHTTPRequestHandler):
    """Serve the health contract and reject unknown routes."""

    server_version = "@@PROJECT_NAME@@/0.1"

    def do_GET(self) -> None:  # noqa: N802 - method name is defined by BaseHTTPRequestHandler
        if self.path != "/health":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        body = json.dumps(health_payload(), separators=(",", ":")).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Use the standard server log format without changing global logging."""
        super().log_message(format, *args)


def main() -> None:
    """Run the development server on the loopback interface."""
    address = ("127.0.0.1", 8000)
    server = ThreadingHTTPServer(address, HealthHandler)
    print(f"@@PROJECT_NAME@@ listening on http://{address[0]}:{address[1]}/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
