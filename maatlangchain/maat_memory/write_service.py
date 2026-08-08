#!/usr/bin/env python3
"""
Maat Memory Write Service — mediated writes that stamp content_origin.

Holds PGVECTOR_DB_URL. Agents authenticate with a memory token; they never
receive the DSN and cannot declare content_origin.

  MAAT_CREDENTIAL_ROLE=broker
  PGVECTOR_DB_URL=...
  MAAT_MEMORY_TOKEN_REGISTRY=~/.maat/credentials/memory-agent-tokens.json
  MAAT_MEMORY_WRITE_HOST=127.0.0.1
  MAAT_MEMORY_WRITE_PORT=8023

  uvicorn maat_memory.write_service:app --host 127.0.0.1 --port 8023
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

# Ensure package import when run as script
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from maat_memory.write_mediation import (  # noqa: E402
    MediatedWriter,
    MediationError,
    TokenRegistry,
)

DEFAULT_REGISTRY = Path.home() / ".maat" / "credentials" / "memory-agent-tokens.json"

app = FastAPI(
    title="Maat Memory Write Service",
    description="Stamps content_origin from authenticated identity. No client-claimed trust.",
    version="1.0.0",
)

_memory = None
_registry: TokenRegistry | None = None


def _get_registry() -> TokenRegistry:
    global _registry
    if _registry is None:
        path = Path(os.environ.get("MAAT_MEMORY_TOKEN_REGISTRY", str(DEFAULT_REGISTRY)))
        _registry = TokenRegistry.load(path)
    return _registry


def _get_memory():
    global _memory
    if _memory is None:
        os.environ.setdefault("MAAT_CREDENTIAL_ROLE", "broker")
        if not os.environ.get("PGVECTOR_DB_URL"):
            from maat_memory.paths import get_pgvector_db_url

            url = get_pgvector_db_url()
            if url:
                os.environ["PGVECTOR_DB_URL"] = url
        from maat_memory.memory_postgres import MaatMemoryPostgres

        _memory = MaatMemoryPostgres()
    return _memory


def principal_from_auth(
    authorization: Optional[str] = Header(default=None),
    x_maat_memory_token: Optional[str] = Header(default=None, alias="X-Maat-Memory-Token"),
):
    token = x_maat_memory_token or authorization
    try:
        return _get_registry().resolve(token)
    except MediationError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


class TaskIn(BaseModel):
    title: str
    description: str = ""
    status: str = "pending"
    priority: str = "medium"
    # Forbidden — present only so we can refuse explicitly
    content_origin: Optional[str] = Field(default=None, description="MUST be omitted")
    origin: Optional[str] = Field(default=None, description="MUST be omitted")
    agent: Optional[str] = Field(default=None, description="ignored; identity from token")


class DecisionIn(BaseModel):
    context: str
    decision_made: str
    rationale: str
    options_considered: Optional[List[str]] = None
    content_origin: Optional[str] = None
    origin: Optional[str] = None
    agent: Optional[str] = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "maat-memory-write", "stamps_origin": True}


@app.get("/v1/whoami")
def whoami(principal=Depends(principal_from_auth)) -> dict[str, Any]:
    return {
        "agent_id": principal.agent_id,
        "kind": principal.kind.value,
        "stamped_origin": principal.stamped_origin().value,
    }


@app.post("/v1/tasks")
def create_task(body: TaskIn, principal=Depends(principal_from_auth)) -> dict[str, Any]:
    if body.content_origin is not None or body.origin is not None:
        raise HTTPException(
            status_code=400,
            detail="content_origin/origin must not be supplied — mediator stamps from identity",
        )
    writer = MediatedWriter(_get_memory(), principal)
    tid = writer.log_task(
        body.title,
        body.description,
        status=body.status,
        priority=body.priority,
    )
    return {
        "ok": True,
        "task_id": tid,
        "agent_id": principal.agent_id,
        "content_origin": writer.origin.value,
    }


@app.post("/v1/decisions")
def create_decision(body: DecisionIn, principal=Depends(principal_from_auth)) -> dict[str, Any]:
    if body.content_origin is not None or body.origin is not None:
        raise HTTPException(
            status_code=400,
            detail="content_origin/origin must not be supplied — mediator stamps from identity",
        )
    writer = MediatedWriter(_get_memory(), principal)
    did = writer.log_decision(
        body.context,
        body.decision_made,
        body.rationale,
        options_considered=body.options_considered,
    )
    return {
        "ok": True,
        "decision_id": did,
        "agent_id": principal.agent_id,
        "content_origin": writer.origin.value,
    }


def main() -> None:
    import uvicorn

    host = os.environ.get("MAAT_MEMORY_WRITE_HOST", "127.0.0.1")
    port = int(os.environ.get("MAAT_MEMORY_WRITE_PORT", "8023"))
    uvicorn.run(
        "maat_memory.write_service:app",
        host=host,
        port=port,
        factory=False,
    )


if __name__ == "__main__":
    # When executed as file, re-export module path
    import uvicorn

    host = os.environ.get("MAAT_MEMORY_WRITE_HOST", "127.0.0.1")
    port = int(os.environ.get("MAAT_MEMORY_WRITE_PORT", "8023"))
    uvicorn.run(app, host=host, port=port)
