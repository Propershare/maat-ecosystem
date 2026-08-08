# Slop Grep Report — Tehuti Lab (2026-08-08)

**Tool:** `grep -rnE` per `refs/agentic-engineering-doctrine-2026-08-08` §8
**Scope:** Lab Python source (maatlangchain, openclaw, hermes-agent) — excluding venv/site-packages, tests, vendor
**Author:** opencode_staydangerous
**Status:** Baseline scan. **NOT** an audit verdict — patterns are signals, not proof of bugs. Hits must be triaged manually per the doctrine.

---

## 1. Signal: bare `except:` (silently swallows all exceptions)

18 hits across 10 files in maatlangchain:

| File | Line | Pattern |
|------|------|---------|
| maatlangchain/maat_memory/project_discovery.py | 111 | `except:` |
| maatlangchain/maat_memory/project_discovery.py | 220 | `except:` |
| maatlangchain/maat_memory/ldap_integration.py | 105 | `except:` |
| maatlangchain/maat_memory/ldap_integration.py | 134 | `except:` |
| maatlangchain/maat_memory/ldap_integration.py | 191 | `except:` |
| maatlangchain/core/chains/document_processor.py | 178 | `except:` |
| maatlangchain/api/main_original.py | 370, 542, 568 | `except:` (x3) |
| maatlangchain/api/main_backup_rag.py | 397, 575, 601 | `except:` (x3) |
| maatlangchain/scripts/fix_model_import.py | 123, 128, 133 | `except:` (x3) |
| maatlangchain/scripts/find_laptop_ips.py | 25, 38 | `except:` (x2) |
| maatlangchain/scripts/push_to_laptops.py | 41, 115 | `except:` (x2) |
| maatlangchain/scripts/run_rbg_processing_direct.py | 95 | `except:` |

**False-positive notes:**
- `maatlangchain/maat_memory/standards.py:119` matched the string `try_except` inside a docstring or string literal — not actual code.

**Triage backlog (per doctrine §8):**
- `main_original.py` and `main_backup_rag.py` are `.py` files with "backup" in the name sitting next to the live `main.py`. These should be **deleted** (or moved out of the api/ tree). Their `except:` is moot if the files are removed.
- `scripts/*.py` (8 hits across 4 files) are operator scripts — bare `except:` in scripts is **less dangerous** than in library code (a script that fails should exit loud, not silent). Triage: replace with `except Exception as e: log.error(...)` or specific exception types.
- `core/chains/document_processor.py:178` and `maat_memory/{project_discovery,ldap_integration}.py` (5 hits) are **library code** that runs unattended. These should be remediated: catch specific exceptions, log them, and re-raise or fall through.

## 2. Signal: defeated type system (`as any`, `as unknown as any`)

3 hits — all in `hermes-agent/cli.py`:

| File | Line | Pattern |
|------|------|---------|
| hermes-agent/cli.py | 1513 | `def save_config_value(key_path: str, value: any) -> bool:` |

(Other grep hits were in venv site-packages and docstrings — not real code.)

**Analysis:** The `value: any` annotation is invalid Python; `any` is a built-in function, not a type. Should be `value: Any` with `from typing import Any`. This isn't a slop-in-the-sense-of-defeating-types (the type checker would reject it anyway), but it's a sign the file was edited without running mypy. **Triage: low priority. Cosmetic fix.**

## 3. Signal: retry-busy loops (`for ... in range(N):` without body context)

No hits. The grep pattern in doctrine §8 was a placeholder; I refined it. Real pattern would be `for _ in range(N): try: ... except: continue` which is harder to grep generically. Defer this signal until we see actual retry-loop slop.

## 4. Signal: missing Stage 3 evidence (`doc/ADR/`)

Across the entire `~/.n8n` lab repo: **no `doc/ADR/` directory exists in any project**. The doctrine §8 specifies:

```bash
ls doc/ADR/ doc/types/ 2>/dev/null || echo "no ADR/types dir — Stage 3 was skipped"
```

**This is the most important finding.** Every system in the lab (legal AI, hermes, maatbench, openclaw, etc.) was built without a published Stage 3 ADR. ADR-001 (refs/adr-001-information-organ-program-design-2026-08-08) is the **first** Stage 3 artifact in the lab.

**Per doctrine §10:** "Calling a system 'production' without a Stage-3 artifact in doc/ADR/ or equivalent" is a forbidden pattern. **No system in the lab meets this requirement today.** This is a Truth violation under the doctrine and a remediation backlog item.

## 5. Summary

| Pattern | Hits | Triage priority |
|---------|------|-----------------|
| `except:` in library code | 5 | **High** — unattended code, must log |
| `except:` in operator scripts | 13 | Medium — log instead of swallow |
| `except:` in backup `.py` files | 6 (counted in script totals) | **High** — delete the backups |
| Defeated types (`any`) | 1 | Low — cosmetic |
| Retry-busy loops | 0 | n/a |
| Missing Stage 3 ADRs | 100% of systems | **High — doctrine violation** |

## 6. Recommended actions (in order)

1. **Delete `maatlangchain/api/main_original.py` and `main_backup_rag.py`.** They should not be in version control; live code lives in `main.py`. Their existence contradicts the doctrine's "fewer surfaces, deeper governance" principle for the legal organ.
2. **Remediate `except:` in `core/chains/document_processor.py` and `maat_memory/{project_discovery,ldap_integration}.py`.** Replace with specific exception types, log via `maat_memory.log_error()`, and either re-raise or fall through with documented behavior.
3. **Establish `doc/ADR/` per project.** ADR-001 is the template. Each active system (legal, trading, hermes, openclaw, etc.) needs its own Stage 3 ADR before the next change ships.
4. **Schedule weekly grep run** (doctrine §8 cadence). Operator obligation per doctrine §11.5.

## 7. Reproducing this scan

```bash
SLOP_DIRS="/home/suspect/.n8n/maatlangchain/maat_memory \
           /home/suspect/.n8n/maatlangchain/core \
           /home/suspect/.n8n/maatlangchain/api \
           /home/suspect/.n8n/maatlangchain/scripts \
           /home/suspect/.n8n/maatlangchain/tests/unit \
           /home/suspect/.n8n/openclaw \
           /home/suspect/.n8n/hermes-agent"

for d in $SLOP_DIRS; do
  grep -rnE "except\s*:\s*$" "$d" --include="*.py" 2>/dev/null | grep -v __pycache__
done
```
