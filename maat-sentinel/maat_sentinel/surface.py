"""Read latest doctor posture, recent immune events, presence; derived unified view."""

from __future__ import annotations

from typing import Any

from maat_sentinel import store
from maat_sentinel.envelope import unwrap_row


def _mid_from_payload(data: dict[str, Any]) -> str:
    return str(data.get("machine_id") or "")


def latest_doctor_snapshot(machine_id: str) -> dict[str, Any] | None:
    last: dict[str, Any] | None = None
    for row in store.iter_jsonl("doctor_snapshots"):
        data = unwrap_row(row)
        if _mid_from_payload(data) == machine_id:
            last = data
    return last


def recent_immune_events(machine_id: str, limit: int = 50) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in store.iter_jsonl("immune_events"):
        data = unwrap_row(row)
        if _mid_from_payload(data) == machine_id:
            out.append(data)
    return out[-limit:]


def latest_presence(machine_id: str) -> dict[str, Any] | None:
    last: dict[str, Any] | None = None
    for row in store.iter_jsonl("presence"):
        data = unwrap_row(row)
        if _mid_from_payload(data) == machine_id:
            last = _normalize_presence_display(data)
    return last


def _normalize_presence_display(data: dict[str, Any]) -> dict[str, Any]:
    """Legacy: map last_heartbeat / product_name / runtime_active into canonical keys."""
    out = dict(data)
    if "last_seen_at" not in out and "last_heartbeat" in out:
        out["last_seen_at"] = out["last_heartbeat"]
    if "runtime" not in out and "product_name" in out:
        out["runtime"] = out["product_name"]
    if "status" not in out and "runtime_active" in out:
        out["status"] = "active" if out.get("runtime_active") else "idle"
    return out


def _immune_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    constitutional = 0
    critical = 0
    blocked = 0
    last_ts: str | None = None
    for e in events:
        sev = str(e.get("severity") or "").lower()
        if sev == "constitutional":
            constitutional += 1
        if sev == "critical":
            critical += 1
        if e.get("blocked") is True:
            blocked += 1
        ts = str(e.get("timestamp") or "")
        if ts and (last_ts is None or ts > last_ts):
            last_ts = ts
    return {
        "recent_constitutional_count": constitutional,
        "recent_critical_count": critical,
        "recent_blocked_count": blocked,
        "last_immune_event_at": last_ts,
    }


def _derive_machine_status(
    doctor: dict[str, Any] | None,
    immune_recent: list[dict[str, Any]],
) -> tuple[str, str, bool]:
    """
    Returns (machine_status, risk_summary, requires_human_review).
    machine_status: operational | degraded | unsafe | constitutional_breach
    """
    posture = (doctor or {}).get("machine_trust_posture") or ""
    posture = str(posture).lower()
    def _constitutional_signal(e: dict[str, Any]) -> bool:
        if str(e.get("severity") or "").lower() == "constitutional":
            return True
        tags = e.get("tags") or []
        return any("constitutional" in str(t).lower() for t in tags)

    breach_immune = any(_constitutional_signal(e) for e in immune_recent)
    blocked_any = any(e.get("blocked") for e in immune_recent)

    if posture == "constitutional_breach" or breach_immune:
        return (
            "constitutional_breach",
            "Doctor posture or immune events indicate constitutional risk",
            True,
        )
    if posture == "unsafe":
        return ("unsafe", "Doctor reports unsafe overall status", True)
    if posture == "degraded" or blocked_any:
        summary = "Immune blocks or doctor warnings present" if blocked_any else "Doctor degraded posture"
        return ("degraded", summary, blocked_any or posture == "degraded")
    return ("operational", "No elevated signals in recent window", False)


def unified_view(machine_id: str, immune_limit: int = 20) -> dict[str, Any]:
    doctor = latest_doctor_snapshot(machine_id)
    immune_recent = recent_immune_events(machine_id, limit=immune_limit)
    presence = latest_presence(machine_id)
    immune_summary = _immune_summary(immune_recent)
    machine_status, risk_summary, requires_human_review = _derive_machine_status(
        doctor,
        immune_recent,
    )

    return {
        "schema": "maat-sentinel/unified-view/v1",
        "machine_id": machine_id,
        "machine_status": machine_status,
        "risk_summary": risk_summary,
        "requires_human_review": requires_human_review,
        "immune_summary": immune_summary,
        "doctor": doctor,
        "immune_recent": immune_recent,
        "presence": presence,
    }


def all_machine_ids() -> list[str]:
    seen: set[str] = set()
    for name in ("doctor_snapshots", "immune_events", "presence"):
        for row in store.iter_jsonl(name):
            data = unwrap_row(row)
            mid = _mid_from_payload(data)
            if mid:
                seen.add(mid)
    return sorted(seen)


def alerts() -> list[dict[str, Any]]:
    """Machines that need attention (derived; not durable maat-memory)."""
    out: list[dict[str, Any]] = []
    for mid in all_machine_ids():
        uv = unified_view(mid, immune_limit=50)
        if uv.get("requires_human_review") or uv.get("machine_status") in (
            "constitutional_breach",
            "unsafe",
        ):
            out.append(
                {
                    "machine_id": mid,
                    "machine_status": uv.get("machine_status"),
                    "risk_summary": uv.get("risk_summary"),
                    "requires_human_review": uv.get("requires_human_review"),
                },
            )
    return out
