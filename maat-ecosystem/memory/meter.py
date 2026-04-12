#!/usr/bin/env python3
"""
Memory Meter — Bank capacity and health monitoring.

Reads banks.yaml, queries each active bank, reports metrics.
Called by the Ka organ on the pulse interval.

Usage:
    python3 meter.py              # Full report
    python3 meter.py --json       # JSON output for Ka organ
    python3 meter.py --bank primary  # Single bank
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Find config
MEMORY_ROOT = Path(__file__).parent
BANKS_CONFIG = MEMORY_ROOT / "banks.yaml"


def load_banks_config():
    """Load banks.yaml."""
    try:
        import yaml
        with open(BANKS_CONFIG) as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: basic YAML parsing for simple cases
        print("⚠️  PyYAML not installed — install with: pip install pyyaml")
        return None
    except FileNotFoundError:
        return None


def check_postgres_bank(config):
    """Check Postgres bank health and capacity."""
    try:
        import psycopg2
        url = config.get("url", "").replace("${PGVECTOR_DB_URL}", 
              os.environ.get("PGVECTOR_DB_URL", ""))
        
        if not url:
            return {"status": "error", "error": "No database URL configured"}
        
        start = time.time()
        conn = psycopg2.connect(url)
        latency_connect = (time.time() - start) * 1000
        
        cur = conn.cursor()
        
        # Get table sizes
        cur.execute("""
            SELECT relname, n_live_tup 
            FROM pg_stat_user_tables 
            WHERE schemaname = 'public'
            ORDER BY n_live_tup DESC
        """)
        tables = {row[0]: row[1] for row in cur.fetchall()}
        
        # Get database size
        cur.execute("SELECT pg_database_size(current_database())")
        db_size = cur.fetchone()[0]
        
        # Get latest entry timestamp
        latest = None
        for table in ['maat_conversations', 'maat_tasks', 'maat_decisions', 'maat_learnings']:
            try:
                cur.execute(f"SELECT MAX(created_at) FROM {table}")
                row = cur.fetchone()
                if row and row[0]:
                    if latest is None or row[0] > latest:
                        latest = row[0]
            except Exception:
                conn.rollback()
        
        freshness = None
        if latest:
            freshness = (datetime.now(timezone.utc) - latest.replace(tzinfo=timezone.utc)).total_seconds()
        
        cur.close()
        conn.close()
        
        total_rows = sum(tables.values())
        
        return {
            "status": "healthy",
            "latency_ms": round(latency_connect, 1),
            "total_rows": total_rows,
            "tables": tables,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "freshness_seconds": round(freshness) if freshness else None,
            "breakdown": {
                "conversations": tables.get("maat_conversations", 0),
                "tasks": tables.get("maat_tasks", 0),
                "decisions": tables.get("maat_decisions", 0),
                "learnings": tables.get("maat_learnings", 0),
                "changes": tables.get("maat_changes", 0),
                "errors": tables.get("maat_errors", 0),
                "sessions": tables.get("maat_sessions", 0),
                "audit": tables.get("maat_audit", 0),
            }
        }
        
    except ImportError:
        return {"status": "error", "error": "psycopg2 not installed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_sqlite_bank(config):
    """Check SQLite bank health."""
    try:
        import sqlite3
        path = config.get("path", "memory/archive/archive.db")
        
        if not Path(path).exists():
            return {"status": "empty", "note": "Archive not yet created"}
        
        start = time.time()
        conn = sqlite3.connect(path)
        latency = (time.time() - start) * 1000
        
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        
        total = 0
        table_counts = {}
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            table_counts[table] = count
            total += count
        
        file_size = Path(path).stat().st_size
        
        conn.close()
        
        return {
            "status": "healthy",
            "latency_ms": round(latency, 1),
            "total_rows": total,
            "tables": table_counts,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_meter_report(bank_filter=None):
    """Generate full meter report."""
    report = {
        "organ": "memory",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "banks": {},
        "alerts": [],
    }
    
    # Check primary (Postgres)
    if bank_filter is None or bank_filter == "primary":
        url = os.environ.get("PGVECTOR_DB_URL", "")
        if url:
            report["banks"]["primary"] = check_postgres_bank({"url": url})
        else:
            report["banks"]["primary"] = {"status": "unconfigured"}
    
    # Check archive (SQLite)
    if bank_filter is None or bank_filter == "archive":
        archive_path = MEMORY_ROOT / "archive" / "archive.db"
        report["banks"]["archive"] = check_sqlite_bank({"path": str(archive_path)})
    
    # Generate alerts
    for bank_name, bank_data in report["banks"].items():
        if bank_data.get("status") == "error":
            report["alerts"].append({
                "bank": bank_name,
                "level": "critical",
                "message": f"Bank {bank_name}: {bank_data.get('error', 'unknown error')}"
            })
        
        latency = bank_data.get("latency_ms", 0)
        if latency > 1000:
            report["alerts"].append({
                "bank": bank_name,
                "level": "warning",
                "message": f"Bank {bank_name} slow: {latency}ms"
            })
        
        freshness = bank_data.get("freshness_seconds")
        if freshness and freshness > 3600:
            report["alerts"].append({
                "bank": bank_name,
                "level": "info",
                "message": f"Bank {bank_name} stale: no writes in {freshness}s"
            })
    
    # Overall status
    statuses = [b.get("status") for b in report["banks"].values()]
    if all(s == "healthy" for s in statuses):
        report["overall"] = "healthy"
    elif any(s == "error" for s in statuses):
        report["overall"] = "degraded"
    else:
        report["overall"] = "unknown"
    
    return report


def print_human_report(report):
    """Print human-readable meter report."""
    print("╔══════════════════════════════════════════╗")
    print("║        MEMORY BANK METER                 ║")
    print(f"║  Status: {report['overall']:>10}                    ║")
    print("╚══════════════════════════════════════════╝")
    print()
    
    for bank_name, bank_data in report["banks"].items():
        status_icon = "✅" if bank_data["status"] == "healthy" else "❌" if bank_data["status"] == "error" else "⚠️"
        print(f"  {status_icon} {bank_name}")
        
        if "total_rows" in bank_data:
            print(f"     Rows: {bank_data['total_rows']:,}")
        if "db_size_mb" in bank_data:
            print(f"     Size: {bank_data['db_size_mb']} MB")
        if "file_size_mb" in bank_data:
            print(f"     Size: {bank_data['file_size_mb']} MB")
        if "latency_ms" in bank_data:
            print(f"     Latency: {bank_data['latency_ms']}ms")
        if "freshness_seconds" in bank_data:
            fresh = bank_data["freshness_seconds"]
            if fresh:
                if fresh < 60:
                    print(f"     Freshness: {fresh}s ago")
                elif fresh < 3600:
                    print(f"     Freshness: {fresh//60}m ago")
                else:
                    print(f"     Freshness: {fresh//3600}h ago")
        
        if "breakdown" in bank_data:
            print("     Breakdown:")
            for key, val in bank_data["breakdown"].items():
                if val > 0:
                    print(f"       {key}: {val:,}")
        print()
    
    if report["alerts"]:
        print("  ⚠️  Alerts:")
        for alert in report["alerts"]:
            print(f"     [{alert['level']}] {alert['message']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    
    bank_filter = None
    for i, arg in enumerate(args):
        if arg == "--bank" and i + 1 < len(args):
            bank_filter = args[i + 1]
    
    report = get_meter_report(bank_filter)
    
    if "--json" in args:
        print(json.dumps(report, indent=2, default=str))
    else:
        print_human_report(report)
