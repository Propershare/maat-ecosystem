from __future__ import annotations

import json
import os
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest import mock

from tehuti_guard.server import GuardHandler


class GuardAuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), GuardHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()

    def request(self, token: str | None = None) -> tuple[int, dict]:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        req = urllib.request.Request(f"{self.base}/health", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_configured_token_rejects_missing_credentials(self) -> None:
        with mock.patch.dict(os.environ, {"TEHUTI_GUARD_TOKEN": "test-token"}, clear=False):
            status, body = self.request()

        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "unauthorized")

    def test_configured_token_accepts_matching_bearer_credential(self) -> None:
        with mock.patch.dict(os.environ, {"TEHUTI_GUARD_TOKEN": "test-token"}, clear=False):
            status, body = self.request("test-token")

        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])


if __name__ == "__main__":
    unittest.main()
