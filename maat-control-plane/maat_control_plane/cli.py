"""MAAT CLI — minimal skeleton. Implements subcommand routing only; logic comes later."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime

from maat_control_plane import __version__
from maat_control_plane.doctor import format_human, report_to_json, run_doctor
from maat_control_plane import governance as governance_cmd


def _cmd_setup(_args: argparse.Namespace) -> int:
	print("maat setup — skeleton (not yet implemented).")
	print("Planned: inspect machine, detect services, propose plan, apply after approval.")
	print("See: docs/MAAT-LAB-CONTROL-PLANE.md")
	return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
	report = run_doctor()
	if getattr(args, "json", False):
		print(json.dumps(report_to_json(report), indent=2))
	else:
		print(format_human(report))
	return 0 if report.overall_status != "fail" else 1


def _cmd_repair(_args: argparse.Namespace) -> int:
	report = {
		"schema": "maat-control-plane/repair-report/v0",
		"timestamp": datetime.now(UTC).isoformat(),
		"status": "skeleton",
		"detail": "No repair actions performed. Implement safe restore from manifest.",
	}
	print(json.dumps(report, indent=2))
	return 0


def _cmd_enroll(_args: argparse.Namespace) -> int:
	print("maat enroll — skeleton (not yet implemented).")
	print("Planned: machine identity, Sentinel registration, MCP endpoints, role install.")
	print("See: docs/MAAT-LAB-CONTROL-PLANE.md")
	return 0


def main() -> None:
	parser = argparse.ArgumentParser(
		prog="maat",
		description="MAAT Lab control plane (setup, doctor, repair, enroll).",
	)
	parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
	sub = parser.add_subparsers(dest="command", required=True)

	p_setup = sub.add_parser("setup", help="Inspect machine and propose/apply lab layout")
	p_setup.set_defaults(func=_cmd_setup)

	p_doc = sub.add_parser("doctor", help="Health and integrity audit (machine truth reader)")
	p_doc.add_argument(
		"--json",
		action="store_true",
		help="Emit machine-readable JSON (schema maat-control-plane/doctor-report/v2.1)",
	)
	p_doc.set_defaults(func=_cmd_doctor)

	p_rep = sub.add_parser("repair", help="Safe repair from manifest (no sacred overwrite)")
	p_rep.set_defaults(func=_cmd_repair)

	p_enr = sub.add_parser("enroll", help="Enroll this host into the lab")
	p_enr.set_defaults(func=_cmd_enroll)

	p_gov = sub.add_parser(
		"governance",
		help="Query maat_governance_events (Guard / Forge / Sentinel)",
	)
	gov_sub = p_gov.add_subparsers(dest="gov_cmd", required=True)

	p_gov_recent = gov_sub.add_parser(
		"recent",
		help="Latest governance rows (newest first)",
	)
	p_gov_recent.add_argument(
		"--limit",
		type=int,
		default=30,
		help="Max rows (default 30, max 500)",
	)
	p_gov_recent.add_argument(
		"--json",
		action="store_true",
		help="Full JSON rows",
	)
	p_gov_recent.set_defaults(func=governance_cmd.cmd_recent)

	p_gov_machine = gov_sub.add_parser(
		"machine",
		help="Rows for one machine_id",
	)
	p_gov_machine.add_argument("machine_id", help="Machine id (e.g. from doctor / Sentinel)")
	p_gov_machine.add_argument("--limit", type=int, default=50)
	p_gov_machine.add_argument("--json", action="store_true")
	p_gov_machine.set_defaults(func=governance_cmd.cmd_machine)

	p_gov_corr = gov_sub.add_parser(
		"correlation",
		help="All rows for one correlation_id (oldest first — lifecycle)",
	)
	p_gov_corr.add_argument(
		"correlation_id",
		help="correlation_id from Guard / Forge / Sentinel responses",
	)
	p_gov_corr.add_argument("--limit", type=int, default=100)
	p_gov_corr.add_argument("--json", action="store_true")
	p_gov_corr.set_defaults(func=governance_cmd.cmd_correlation)

	args = parser.parse_args()
	sys.exit(args.func(args))


if __name__ == "__main__":
	main()
