# Episodic Memory — 2026-07-26
timestamp: 2026-07-26T12:47:03.063951+00:00
source: hermes-agent

2026-07-26 — Built Hermes Desktop ↔ Lab Brain bridge. Added @method('maat.artifacts.list') to tui_gateway/server.py that queries maat_artifacts table from Postgres. Modified ArtifactsView in apps/desktop/src/app/artifacts/index.tsx to fetch lab brain artifacts alongside session-scanned ones. Rebuilt desktop app (hermes desktop --force-build). 42 artifacts now visible in the artifacts grid — workflowware packages, guard decisions, audit reports, command centers, trade logs from all lab machines. Wrote MAAT audit to semantic memory identifying token waste, missing push protocol, and ring enforcement gaps. Proposed architecture: push protocol replaces scan, ring model for visibility, multi-machine sync via existing maat_machines/maat_storage_roots schema.
