# CHANGELOG.md
## 2026-04-26: Canonical Architecture Refinement

### Patch Summary

- **Refined canonical architecture** for trust workflow management
- **Clarified staging vs canonical** boundaries
- **Updated documentation** to prevent misinterpretation of paths

### Current State

✅ **Canonical Location:** `/home/suspect/.n8n/workflows/domain/trust/`
✅ **Documentation:** `AGENTS.md` correctly identifies approved paths
✅ **Staging Paths:** `maatlabs/` treated as accidental/temporary only

### Next Steps

1. Place trust-workflow files at `/home/suspect/.n8n/workflows/domain/trust/`
2. Follow existing schema in `workflows/domain/trust/` subdirectories
3. Do not use `maatlabs/` for authoritative content

### References

- See `AGENTS.md` for canonical architecture notice
- See `CHANGELOG.md` for version history