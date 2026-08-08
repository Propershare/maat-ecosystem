@echo off
REM Refresh GITMAAT-CONTEXT.md from shared gitMaat so OpenCode/agents on this PC
REM see current tasks and recent activity from all workstations.
REM Run from workspace root when you open the project (or periodically).

set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
REM Workspace root = parent of maatlangchain (script lives in maatlangchain\scripts)
cd /d "%SCRIPT_DIR%\..\.."
python "%SCRIPT_DIR%\query_gitmaat.py" --out GITMAAT-CONTEXT.md
echo Refreshed GITMAAT-CONTEXT.md in %CD%
