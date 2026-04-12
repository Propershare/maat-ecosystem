# MAAT Ecosystem — Documentation

## Core Documents

| Document | Description |
|----------|-------------|
| [Ka Architecture Paper](ka-architecture-paper.md) | The full academic paper — framework, organs, comparison, roadmap |
| [Architecture](architecture.md) | Technical architecture — organ diagram, port map, discovery protocol |
| [Ka Audit 2026-04-06](ka-audit-2026-04-06.md) | System audit — organ health, gaps, recommendations, Maat Score |
| [UI Spec](UI-SPEC.md) | Maat Studio UI specification |

## Governance Documents (in soul/)

| Document | Description |
|----------|-------------|
| [Constitution](../soul/constitution.md) | The 42 Laws of Maat — immutable moral foundation |
| [Sacred](../soul/sacred.md) | Sacred principles — what cannot be changed |
| [Default Policy](../soul/policies/default.md) | Default behavioral policy set |

## Operational Documents

| Document | Description |
|----------|-------------|
| [MANIFEST.ka](../MANIFEST.ka) | The DNA — machine-readable body map |
| [Pulse Config](../ka/pulse.yaml) | Ka organ heartbeat and healing rules |
| [Portability](../skeleton/portability.md) | Migration and portability guarantees |
| [Events](../senses/EVENTS.md) | Canonical event taxonomy |
| [Learning](../brain/learning/LEARNING.md) | Learning system documentation |

## Quick Reference

```bash
# Discover the body (host from MANIFEST.ka network.host_example; requires Ka discovery running)
curl http://staydangerous:8010/manifest

# Check organ health
curl http://staydangerous:8010/health

# Connection instructions
curl http://staydangerous:8010/connect
```

Port map: **`MANIFEST.ka`** → `network:`. **HTTP** `:8010` vs **MCP** on organ ports — see root `README.md` § Network.
