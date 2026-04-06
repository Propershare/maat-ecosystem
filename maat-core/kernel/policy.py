"""
MAAT Policy Engine

Machine-readable moral and operational constitution.
Evaluates rules against (agent_id, action, resource) tuples.

Policies are loaded from maat_policy.schema.json-compliant dicts.
Multiple policies can be active simultaneously (layered).
"""

from __future__ import annotations

from typing import Any


class PolicyEngine:
    """
    Evaluate policies in order. First matching rule wins.
    Default: deny if no rule matches (fail-closed).
    """

    def __init__(self, policies: list[dict] = None):
        self._policies: list[dict] = []
        self._ring_map: dict[str, str] = {
            "owner": "outer-ring",
        }

        for policy in (policies or []):
            self.load_policy(policy)

    def load_policy(self, policy: dict) -> None:
        """Load a MAAT policy document."""
        self._policies.append(policy)

    def register_agent(self, agent_id: str, ring: str) -> None:
        """Register an agent's ring level."""
        self._ring_map[agent_id] = ring

    def get_ring(self, agent_id: str) -> str:
        """Get agent ring. Unknown → inner-ring (fail-closed)."""
        return self._ring_map.get(agent_id, "inner-ring")

    def evaluate(self, agent_id: str, action: str, resource: str = "") -> dict:
        """
        Evaluate all policies for this (agent, action, resource).

        Returns:
            {"allowed": bool, "reason": str, "policy_id": str | None}
        """
        ring = self.get_ring(agent_id)

        # Check each policy in order
        for policy in self._policies:
            for rule in policy.get("rules", []):
                if self._matches(rule["when"], agent_id=agent_id, action=action,
                                 resource=resource, ring=ring):
                    outcome = rule["then"]
                    reason = rule.get("reason", f"Rule {rule['id']} matched")

                    if outcome == "allow":
                        return {"allowed": True, "reason": reason, "policy_id": policy["id"]}
                    elif outcome in ("deny", "require_approval"):
                        return {"allowed": False, "reason": reason, "policy_id": policy["id"]}
                    elif outcome == "escalate":
                        return {"allowed": False, "reason": f"Escalation required: {reason}",
                                "policy_id": policy["id"], "escalate": True}
                    # "log" = continue evaluating

        # No policy → use default ring-based rules
        return self._default_ring_check(ring, action)

    def _matches(self, condition: dict, **context) -> bool:
        """Check if a condition matches the current context."""
        for key, expected in condition.items():
            actual = context.get(key, "")
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif isinstance(expected, str):
                if expected.endswith("*"):
                    if not actual.startswith(expected[:-1]):
                        return False
                elif actual != expected:
                    return False
        return True

    @staticmethod
    def _default_ring_check(ring: str, action: str) -> dict:
        """Default Three-Ring rules when no policy matches."""
        ring_actions = {
            "outer-ring": {"read", "write", "execute", "propose", "memory.write",
                           "memory.read", "tool.*", "task.*"},
            "middle-ring": {"read", "propose", "memory.read", "memory.write"},
            "inner-ring": {"read", "memory.read"},
        }

        allowed_set = ring_actions.get(ring, set())
        allowed = action in allowed_set or any(
            action.startswith(a.rstrip("*")) for a in allowed_set if a.endswith("*")
        )

        return {
            "allowed": allowed,
            "reason": f"{ring} {'can' if allowed else 'cannot'} perform '{action}' (default rule)",
            "policy_id": None,
        }
