"""
Sentinel — TehutiGuard's Eyes
A gemma4:e2b agent that continuously monitors system logs,
detects anomalies, and enforces Maat governance.

Watches:
  - /var/log/auth.log     → SSH attempts, sudo, logins
  - /var/log/ufw.log      → Firewall blocks/allows
  - /var/log/syslog        → System events
  - journalctl -u ollama  → Model loads, errors, OOM
  - journalctl -u n8n     → Workflow executions, failures
  - docker logs           → Container health
  - PostgreSQL logs       → Query errors, connection issues
  - OpenClaw logs         → Gateway events

Modes:
  - watch:  Continuous tail, analyze every N seconds
  - scan:   One-shot full scan, return report
  - alert:  Watch + push alerts on severity >= threshold

Maat: Vigilance in service of order.
"""

import asyncio
import aiohttp
import json
import logging
import time
import subprocess
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path

log = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
MODEL = "gemma4:e2b"

# ─── Log Sources ──────────────────────────────────────────────────

LOG_SOURCES = {
    "auth": {
        "path": "/var/log/auth.log",
        "type": "file",
        "severity_keywords": {
            "critical": ["BREAK-IN", "POSSIBLE BREAK", "repeated failures"],
            "high": ["Failed password", "Invalid user", "authentication failure", "COMMAND=/bin/"],
            "medium": ["Accepted password", "session opened", "sudo:"],
            "low": ["session closed", "pam_unix"],
        },
    },
    "ufw": {
        "path": "/var/log/ufw.log",
        "type": "file",
        "severity_keywords": {
            "critical": [],
            "high": ["UFW BLOCK"],
            "medium": ["UFW ALLOW"],
            "low": [],
        },
    },
    "ollama": {
        "cmd": "journalctl -u ollama --no-pager --since '5 min ago' 2>/dev/null",
        "type": "journal",
        "severity_keywords": {
            "critical": ["OOM", "out of memory", "CUDA error", "killed"],
            "high": ["error", "failed", "panic"],
            "medium": ["warning", "slow"],
            "low": ["loaded", "unloaded"],
        },
    },
    "n8n": {
        "cmd": "journalctl -u n8n --no-pager --since '5 min ago' 2>/dev/null",
        "type": "journal",
        "severity_keywords": {
            "critical": ["FATAL", "unhandled"],
            "high": ["ERROR", "failed", "crash"],
            "medium": ["WARN", "timeout", "retry"],
            "low": ["execution started", "execution finished"],
        },
    },
    "docker": {
        "cmd": "docker ps --format '{{.Names}}: {{.Status}}' 2>/dev/null",
        "type": "command",
        "severity_keywords": {
            "critical": ["unhealthy", "Exited", "Restarting"],
            "high": ["health: starting"],
            "medium": [],
            "low": ["healthy", "Up"],
        },
    },
    "syslog": {
        "path": "/var/log/syslog",
        "type": "file",
        "severity_keywords": {
            "critical": ["kernel panic", "Out of memory", "segfault", "hardware error"],
            "high": ["error", "failed", "oom-killer"],
            "medium": ["warning", "deprecated"],
            "low": [],
        },
    },
    "openclaw": {
        "path": str(Path.home() / ".openclaw/logs/commands.log"),
        "type": "file",
        "severity_keywords": {
            "critical": ["FATAL", "unhandled"],
            "high": ["error", "denied", "unauthorized"],
            "medium": ["warning", "timeout"],
            "low": ["approved", "completed"],
        },
    },
}


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LogEvent:
    source: str
    line: str
    severity: Severity
    timestamp: Optional[datetime] = None


@dataclass
class SentinelReport:
    scan_time: datetime
    events: List[LogEvent]
    analysis: str
    threat_level: Severity
    recommendations: List[str]
    stats: Dict[str, Any] = field(default_factory=dict)
    elapsed_ms: int = 0


# ─── Log Collection ───────────────────────────────────────────────

def _tail_file(path: str, lines: int = 50) -> List[str]:
    """Tail last N lines from a file."""
    try:
        result = subprocess.run(
            ["tail", "-n", str(lines), path],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
        log.debug(f"Cannot read {path}: {e}")
        return []


def _run_command(cmd: str) -> List[str]:
    """Run a command and return output lines."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except (subprocess.TimeoutExpired, Exception) as e:
        log.debug(f"Command failed: {e}")
        return []


def _classify_line(line: str, severity_keywords: Dict[str, List[str]]) -> Severity:
    """Classify a log line by severity using keyword matching."""
    line_lower = line.lower()
    for sev in ["critical", "high", "medium", "low"]:
        for kw in severity_keywords.get(sev, []):
            if kw.lower() in line_lower:
                return Severity(sev)
    return Severity.LOW


def collect_logs(
    sources: Optional[List[str]] = None,
    tail_lines: int = 50,
    min_severity: Severity = Severity.LOW,
) -> List[LogEvent]:
    """Collect recent log entries from all sources."""
    if sources is None:
        sources = list(LOG_SOURCES.keys())
    
    events = []
    severity_order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
    min_idx = severity_order.index(min_severity)
    
    for src_name in sources:
        src = LOG_SOURCES.get(src_name)
        if not src:
            continue
        
        # Get lines
        if src["type"] == "file":
            lines = _tail_file(src["path"], tail_lines)
        elif src["type"] == "journal":
            lines = _run_command(src["cmd"])
        elif src["type"] == "command":
            lines = _run_command(src["cmd"])
        else:
            continue
        
        # Classify and filter
        for line in lines:
            if not line.strip():
                continue
            sev = _classify_line(line, src["severity_keywords"])
            if severity_order.index(sev) >= min_idx:
                events.append(LogEvent(source=src_name, line=line.strip(), severity=sev))
    
    return events


# ─── LLM Analysis ────────────────────────────────────────────────

SENTINEL_PROMPT = """You are Sentinel, TehutiGuard's vigilant eye. You analyze system logs for security threats, performance issues, and anomalies.

YOUR ROLE:
- Detect intrusion attempts, brute force, unauthorized access
- Spot service failures, crashes, resource exhaustion
- Identify unusual patterns (time-of-day anomalies, new IPs, repeated errors)
- Assess overall system health
- Recommend immediate actions for critical issues

OUTPUT FORMAT (strict JSON):
{
  "threat_level": "low|medium|high|critical",
  "findings": [
    {
      "category": "security|performance|reliability|anomaly",
      "severity": "low|medium|high|critical",
      "description": "what you found",
      "evidence": "the specific log line(s)",
      "action": "recommended action"
    }
  ],
  "system_health": "healthy|degraded|at_risk|critical",
  "summary": "2-3 sentence overall assessment",
  "immediate_actions": ["list of things to do NOW if any"]
}

Be concise. Don't explain what logs are. Focus on WHAT'S WRONG and WHAT TO DO.
If everything looks clean, say so briefly. Don't invent problems."""


async def analyze_logs(events: List[LogEvent], timeout: int = 30) -> Dict[str, Any]:
    """Send collected logs to gemma4:e2b for analysis."""
    if not events:
        return {
            "threat_level": "low",
            "findings": [],
            "system_health": "healthy",
            "summary": "No notable events in recent logs.",
            "immediate_actions": [],
        }
    
    # Group by source and severity for efficient prompt
    grouped = {}
    for e in events:
        key = e.source
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(f"[{e.severity.value.upper()}] {e.line}")
    
    prompt_parts = [f"SYSTEM LOGS TO ANALYZE ({len(events)} events):\n"]
    for src, lines in grouped.items():
        prompt_parts.append(f"\n--- {src.upper()} ({len(lines)} lines) ---")
        # Limit per source to keep prompt manageable
        for line in lines[-30:]:
            prompt_parts.append(line)
    
    prompt = "\n".join(prompt_parts)
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "system": SENTINEL_PROMPT,
        "stream": False,
        "options": {"temperature": 0.3, "num_ctx": 8192},
        "format": "json",
    }
    
    t0 = time.monotonic()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                data = await resp.json()
        
        elapsed = int((time.monotonic() - t0) * 1000)
        response_text = data.get("response", "{}")
        
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                analysis = json.loads(match.group())
            else:
                analysis = {
                    "threat_level": "medium",
                    "summary": response_text[:500],
                    "findings": [],
                    "immediate_actions": [],
                    "system_health": "unknown",
                }
        
        analysis["_meta"] = {
            "tokens": data.get("eval_count", 0),
            "tok_per_sec": round(
                data.get("eval_count", 0) / (data.get("eval_duration", 1) / 1e9), 1
            ),
            "elapsed_ms": elapsed,
            "events_analyzed": len(events),
        }
        
        return analysis
    
    except Exception as e:
        log.error(f"Sentinel analysis failed: {e}")
        return {
            "threat_level": "unknown",
            "summary": f"Analysis failed: {e}",
            "findings": [],
            "immediate_actions": [],
            "system_health": "unknown",
            "_meta": {"error": str(e)},
        }


# ─── Scan Mode ────────────────────────────────────────────────────

async def scan(
    sources: Optional[List[str]] = None,
    tail_lines: int = 50,
    min_severity: Severity = Severity.LOW,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    One-shot scan: collect logs → analyze → return report.
    """
    t0 = time.monotonic()
    
    # Collect
    events = collect_logs(sources=sources, tail_lines=tail_lines, min_severity=min_severity)
    
    # Count by severity
    severity_counts = {}
    for e in events:
        severity_counts[e.severity.value] = severity_counts.get(e.severity.value, 0) + 1
    
    # Analyze (only send medium+ to LLM to save tokens)
    analysis_events = [e for e in events if e.severity in (Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL)]
    analysis = await analyze_logs(analysis_events, timeout=timeout)
    
    elapsed = int((time.monotonic() - t0) * 1000)
    
    return {
        "scan_time": datetime.now().isoformat(),
        "total_events": len(events),
        "severity_counts": severity_counts,
        "analysis": analysis,
        "elapsed_ms": elapsed,
    }


# ─── Watch Mode ───────────────────────────────────────────────────

async def watch(
    interval_seconds: int = 60,
    min_severity: Severity = Severity.MEDIUM,
    alert_callback=None,
    max_cycles: Optional[int] = None,
):
    """
    Continuous monitoring loop. Scans every interval, calls alert_callback on findings.
    
    Args:
        interval_seconds: Seconds between scans
        min_severity: Minimum severity to report
        alert_callback: async fn(report) called when findings exist
        max_cycles: Stop after N cycles (None = infinite)
    """
    cycle = 0
    while max_cycles is None or cycle < max_cycles:
        cycle += 1
        log.info(f"Sentinel watch cycle {cycle}")
        
        report = await scan(min_severity=min_severity, timeout=30)
        
        findings = report.get("analysis", {}).get("findings", [])
        threat_level = report.get("analysis", {}).get("threat_level", "low")
        
        if findings or threat_level in ("high", "critical"):
            if alert_callback:
                await alert_callback(report)
            else:
                # Default: print
                print(f"\n⚠️  SENTINEL ALERT — Threat: {threat_level.upper()}")
                print(f"   Findings: {len(findings)}")
                summary = report.get("analysis", {}).get("summary", "")
                if summary:
                    print(f"   {summary}")
                actions = report.get("analysis", {}).get("immediate_actions", [])
                for a in actions:
                    print(f"   → {a}")
        else:
            log.info(f"Sentinel cycle {cycle}: all clear ({report['total_events']} events, threat: {threat_level})")
        
        await asyncio.sleep(interval_seconds)


# ─── Resource Monitor (bonus — no LLM needed) ────────────────────

def check_resources() -> Dict[str, Any]:
    """Quick resource check — no LLM, pure system calls."""
    resources = {}
    
    # GPU
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        parts = result.stdout.strip().split(", ")
        if len(parts) >= 4:
            resources["gpu"] = {
                "vram_used_mb": int(parts[0]),
                "vram_total_mb": int(parts[1]),
                "utilization_pct": int(parts[2]),
                "temp_c": int(parts[3]),
                "vram_pct": round(int(parts[0]) / int(parts[1]) * 100, 1),
            }
    except Exception:
        pass
    
    # CPU & Memory
    try:
        with open("/proc/loadavg") as f:
            load = f.read().split()
            resources["cpu_load"] = {
                "1min": float(load[0]),
                "5min": float(load[1]),
                "15min": float(load[2]),
            }
        
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = int(parts[1].strip().split()[0])
                    meminfo[key] = val
            
            total = meminfo.get("MemTotal", 1)
            available = meminfo.get("MemAvailable", 0)
            resources["memory"] = {
                "total_mb": total // 1024,
                "available_mb": available // 1024,
                "used_pct": round((1 - available / total) * 100, 1),
            }
    except Exception:
        pass
    
    # Disk
    try:
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True, text=True, timeout=5,
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            resources["disk"] = {
                "total": parts[1],
                "used": parts[2],
                "available": parts[3],
                "used_pct": parts[4],
            }
    except Exception:
        pass
    
    # Services
    services = {}
    for svc in ["ollama", "postgresql@14-main", "redis-server", "n8n", "nginx", "docker"]:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", svc],
                capture_output=True, text=True, timeout=3,
            )
            services[svc] = result.stdout.strip()
        except Exception:
            services[svc] = "unknown"
    resources["services"] = services
    
    # Docker containers
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}:{{.Status}}"],
            capture_output=True, text=True, timeout=5,
        )
        containers = {}
        for line in result.stdout.strip().split("\n"):
            if ":" in line:
                name, status = line.split(":", 1)
                containers[name] = status.strip()
        resources["containers"] = containers
    except Exception:
        pass
    
    return resources


# ─── CLI ──────────────────────────────────────────────────────────

async def _main():
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    
    if mode == "resources":
        print("=" * 60)
        print("SENTINEL — Resource Check (no LLM)")
        print("=" * 60)
        resources = check_resources()
        print(json.dumps(resources, indent=2))
        return
    
    if mode == "scan":
        print("=" * 60)
        print("SENTINEL — Full System Scan")
        print("=" * 60)
        
        report = await scan(tail_lines=100, min_severity=Severity.MEDIUM)
        
        print(f"\nScan time: {report['scan_time']}")
        print(f"Events collected: {report['total_events']}")
        print(f"Severity breakdown: {json.dumps(report['severity_counts'], indent=2)}")
        print(f"Analysis time: {report['elapsed_ms']}ms")
        
        analysis = report.get("analysis", {})
        meta = analysis.pop("_meta", {})
        
        print(f"\n{'─' * 40}")
        print(f"🛡️  THREAT LEVEL: {analysis.get('threat_level', 'unknown').upper()}")
        print(f"🏥 SYSTEM HEALTH: {analysis.get('system_health', 'unknown').upper()}")
        print(f"{'─' * 40}")
        
        print(f"\n📋 SUMMARY: {analysis.get('summary', 'N/A')}")
        
        findings = analysis.get("findings", [])
        if findings:
            print(f"\n🔍 FINDINGS ({len(findings)}):")
            for i, f_item in enumerate(findings, 1):
                sev = f_item.get("severity", "?").upper()
                cat = f_item.get("category", "?")
                desc = f_item.get("description", "?")
                action = f_item.get("action", "")
                print(f"  {i}. [{sev}] ({cat}) {desc}")
                if action:
                    print(f"     → {action}")
        
        actions = analysis.get("immediate_actions", [])
        if actions:
            print(f"\n🚨 IMMEDIATE ACTIONS:")
            for a in actions:
                print(f"  → {a}")
        
        if meta:
            print(f"\n⚡ LLM: {meta.get('tokens', 0)} tokens @ {meta.get('tok_per_sec', 0)} tok/s, "
                  f"{meta.get('elapsed_ms', 0)}ms, {meta.get('events_analyzed', 0)} events analyzed")
    
    elif mode == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"SENTINEL — Watch Mode (every {interval}s)")
        print("Press Ctrl+C to stop")
        await watch(interval_seconds=interval, min_severity=Severity.MEDIUM)
    
    else:
        print(f"Usage: python sentinel.py [scan|watch|resources] [interval_for_watch]")


if __name__ == "__main__":
    asyncio.run(_main())
