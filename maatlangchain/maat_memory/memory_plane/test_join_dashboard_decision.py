"""Deterministic decision-binding tests for the localhost join dashboard."""

from __future__ import annotations

import copy
import sys
import unittest
from unittest.mock import patch

_ML = "/mnt/data_drive/maatlangchain"
if _ML not in sys.path:
    sys.path.insert(0, _ML)

from maat_memory.memory_plane.join_dashboard_server import (  # noqa: E402
    _decision_preflight,
    _guard_health,
    _guard_join_allow,
    _join_schema_card,
)


def _preview() -> tuple[dict, dict]:
    row = {
        "request_id": "260bee29-f6ea-42cc-b520-976747fc8b3d",
        "requesting_agent_id": "cursor_digest_test",
        "principal_id": "imhotep",
        "machine_id": "staydangerous-a7:9d:74:d2:4b:2c",
        "working_on": "prove digest-bound join",
        "risk_level": "medium",
    }
    preview = {
        "request_id": row["request_id"],
        "who": {
            "agent_id": row["requesting_agent_id"],
            "principal_claimed": "imhotep",
            "runtime": "cursor",
            "machine_id": row["machine_id"],
            "workspace_root_guess": "/mnt/data_drive/guess-must-not-count",
        },
        "proven_facts": {
            "workspace_root_declared": {
                "value": "/mnt/data_drive",
                "state": "proven",
            },
            "cwd": {
                "value": "/mnt/data_drive/tehuti-control-center",
                "state": "proven",
            },
            "git_branch": {
                "value": "tehuti/fork-bootstrap",
                "state": "proven",
            },
            "git_commit": {"value": "835c0c9e8", "state": "proven"},
            "forbidden_paths_acknowledged": {
                "value": [".env.broker", "MAAT_OPERATOR_TOKEN"],
                "state": "proven",
            },
        },
        "wants": {
            "chore": row["working_on"],
            "requested_scopes": ["manifest:read"],
            "requested_mcps": ["git-status"],
            "requested_organs": ["discovery"],
            "message": "one item, one decision",
        },
        "registry_delta": {
            "mcps": [{"name": "git-status", "state": "registered"}],
            "scopes": [{"name": "manifest:read", "state": "allowed_default"}],
            "forbidden_ack": [],
        },
        "if_allowed_receives": ["membership identity"],
        "if_allowed_does_NOT_receive": ["master KA"],
        "expires_at": "2026-07-31T00:00:00+00:00",
        "correlation_id": "joinreq:digest-test",
    }
    return preview, row


class TestJoinDashboardDecisionBinding(unittest.TestCase):
    def test_digest_is_deterministic_and_covers_requested_organs(self):
        preview, row = _preview()
        first = _join_schema_card(preview, row)
        second = _join_schema_card(copy.deepcopy(preview), copy.deepcopy(row))
        digest = first["schema_card"]["request_digest"]

        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, second["schema_card"]["request_digest"])

        changed = copy.deepcopy(preview)
        changed["wants"]["requested_organs"].append("memory")
        changed_digest = _join_schema_card(changed, row)["schema_card"][
            "request_digest"
        ]
        self.assertNotEqual(digest, changed_digest)

    def test_guessed_workspace_does_not_complete_where(self):
        preview, row = _preview()
        preview["proven_facts"]["workspace_root_declared"] = {
            "value": None,
            "state": "unreported",
        }
        schema = _join_schema_card(preview, row)

        self.assertEqual(schema["schema_status"], "unproven")
        self.assertIn("workspace_root", schema["schema_gaps"])
        self.assertTrue(schema["allow_disabled"])

    def test_missing_and_changed_digests_fail_closed(self):
        preview, row = _preview()
        preview["schema"] = _join_schema_card(preview, row)
        digest = preview["schema"]["schema_card"]["request_digest"]

        status, body = _decision_preflight(preview, None, allow=True)
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "request_digest_required")

        status, body = _decision_preflight(
            preview, "0" * len(digest), allow=True
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "item_changed")

    def test_allow_needs_where_but_bound_deny_remains(self):
        preview, row = _preview()
        preview["proven_facts"]["cwd"] = {"value": None, "state": "unreported"}
        preview["schema"] = _join_schema_card(preview, row)
        digest = preview["schema"]["partial"]["request_digest"]

        status, body = _decision_preflight(preview, digest, allow=True)
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "allow_disabled")
        self.assertIn("cwd", body["schema_gaps"])

        status, body = _decision_preflight(preview, digest, allow=False)
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])

    def test_proven_preview_accepts_exact_digest(self):
        preview, row = _preview()
        preview["schema"] = _join_schema_card(preview, row)
        digest = preview["schema"]["schema_card"]["request_digest"]

        status, body = _decision_preflight(preview, digest, allow=True)
        self.assertEqual(status, 200)
        self.assertEqual(body["request_digest"], digest)

    @patch(
        "maat_memory.memory_plane.join_dashboard_server._guard_call",
        side_effect=[
            (200, {"ok": True, "service": "tehuti-guard-api", "version": "1"}),
            (200, {"policy_version": "guard@1"}),
        ],
    )
    def test_guard_health_requires_health_and_policy(self, _guard_call):
        health = _guard_health()
        self.assertTrue(health["ok"])
        self.assertEqual(health["schema_status"], "proven")
        self.assertFalse(health["approve_disabled"])

    @patch(
        "maat_memory.memory_plane.join_dashboard_server._guard_call",
        return_value=(0, {"ok": False, "error": "guard_unreachable"}),
    )
    def test_guard_degradation_is_named_and_disables_approve(self, _guard_call):
        health = _guard_health()
        self.assertFalse(health["ok"])
        self.assertEqual(health["schema_status"], "unproven")
        self.assertEqual(health["organ"], "tehuti-guard")
        self.assertEqual(health["reason"], "guard_unreachable")
        self.assertTrue(health["approve_disabled"])

    @patch(
        "maat_memory.memory_plane.join_dashboard_server._guard_call",
        return_value=(
            200,
            {
                "decision": "review",
                "reason": "Sentinel posture unavailable",
                "policy_version": "guard@1",
            },
        ),
    )
    def test_guard_review_never_becomes_allow(self, _guard_call):
        preview, row = _preview()
        preview["schema"] = _join_schema_card(preview, row)
        receipt = _guard_join_allow(preview, "operator reason", "operator")
        self.assertFalse(receipt["ok"])
        self.assertTrue(receipt["approve_disabled"])
        self.assertEqual(receipt["decision"], "review")


if __name__ == "__main__":
    unittest.main()
