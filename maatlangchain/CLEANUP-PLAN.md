# Root .md Files Cleanup Plan

## 🎯 Goal

Clean root directory to only essential files, organize documentation, archive completed work.

## 📋 Actions

### 1. Delete Outdated Files (5 files)
```bash
rm OPencode-AGENT-IDENTIFICATION.md
rm OPencode-NEXT-TASK.md
rm OPencode-OC1-NEXT-TASK.md
rm OPencode-PROMPT-SHORT.md
rm STATUS-AND-NEXT-ACTION.md
```

### 2. Archive Completed Files (13 files)
```bash
mv CRUSH-CLEANUP-COMPLETE.md docs/archive/
mv CRUSH-TO-MAAT-SYNC.md docs/archive/
mv CLEANUP-SUMMARY.md docs/archive/
mv COMPLETE-RESTORATION-SUMMARY.md docs/archive/
mv FIX-DEPRECATION-WARNINGS.md docs/archive/
mv QUALITY-FIXES.md docs/archive/
mv OPENWEBUI-FIX-SUMMARY.md docs/archive/
mv TEST-SUITE-COMPLETE.md docs/archive/
mv API-AUTHENTICATION-COMPLETE.md docs/archive/
mv API-ENDPOINTS-COMPLETE.md docs/archive/
mv MAAT-BALANCE-CHECK.md docs/archive/
mv MAAT-BALANCE-SUMMARY.md docs/archive/
mv OPTIMIZATION-IMPLEMENTATION.md docs/archive/
```

### 3. Move Documentation to docs/ (6 files)
```bash
mv AUTO-SETUP-GUIDE.md docs/
mv GITMAAT-COMPLETE.md docs/
mv ZERO-CONFIG-SYSTEM.md docs/
mv MAAT-MEMORY-POSTGRES-COMPLETE.md docs/
mv LANGCHAIN-MIGRATION-PLAN.md docs/
mv PRODUCTION-TOOLS-ANALYSIS.md docs/
mv KNOWLEDGE-BASE-LOCATION.md docs/
```

### 4. Consolidate Onboarding (5 files → 2 files)
- Merge ONBOARDING-SUMMARY.md, ONE-COMMAND-SETUP.md, SIMPLE-COPY-INSTRUCTIONS.md, PUSH-SCRIPTS-README.md into ONBOARDING-GUIDE.md
- Merge WINDOWS-SETUP.md into WINDOWS-QUICK-START.md

## ✅ Final Root Structure

**Essential Files (6):**
- AGENTS.md
- PROMPT-NEXT-ACTION.md
- AGENTS-MAAT-MEMORY.md
- AGENT-COORDINATION.md
- AGENT-FILE-GUIDE.md
- MAATLANGCHAIN-VALUE-PROPOSITION.md

**Onboarding (2):**
- ONBOARDING-GUIDE.md
- WINDOWS-QUICK-START.md

**Total:** 8 files in root (down from 35)

## 🚀 Ready to Build

After cleanup, core system is ready:
- ✅ Maat Memory (gitMaat) working
- ✅ Auto-setup working
- ✅ Project discovery working
- ✅ Maat Standards working
- ✅ Task coordination (Maat Law) in place

