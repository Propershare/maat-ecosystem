"""CLI: maat-memory-client doctor"""

from __future__ import annotations

import json
import sys

from .client import MaatMemoryClient


def main() -> None:
    client = MaatMemoryClient()
    report = client.doctor()
    print(json.dumps(report, indent=2, default=str))
    if not report.get("reachable"):
        sys.exit(1)


if __name__ == "__main__":
    main()
