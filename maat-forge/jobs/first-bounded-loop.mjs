#!/usr/bin/env node
/**
 * First MAAT Forge bounded loop — safe cage:
 * - Tehuti Guard preflight (POST /decision) unless SKIP_GUARD_PREFLIGHT=1
 * - Reads tail of MAAT_IMMUNE_LOG (if set)
 * - Writes a timestamped JSON report under reports/
 * - Emits a stub repair.candidate_generated record (no filesystem repair)
 *
 * Run from lab root: node maat-forge/jobs/first-bounded-loop.mjs
 */

import { randomUUID } from "node:crypto";
import { appendFile, mkdir, readFile, stat } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
	blockConstitutionalRisk,
	buildDecisionEnvelope,
	buildForgePreflightMemoryRow,
	buildPreflightDecisionRecord,
	classifyGuardFetchError,
	defaultGuardBaseUrl,
	getForgeMachineId,
	guardPreflightSkipped,
	logForgeGovernanceRowSync,
	postGuardDecision,
} from "../lib/guard-preflight.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FORGE_ROOT = join(__dirname, "..");
const DEFAULT_REPORT_DIR = join(FORGE_ROOT, "reports");

const immuneLog = process.env.MAAT_IMMUNE_LOG?.trim();
const reportDir = process.env.FORGE_REPORT_DIR?.trim() || DEFAULT_REPORT_DIR;

/** Explicit v1 classification for this template job (read logs + reports only). */
const JOB_RISK_CLASS = "low_risk";
const JOB_TYPE = "first_bounded_loop";
const REQUESTED_ACTION = "read_immune_tail_write_report";
const TARGET_CLASS = "reports_non_sacred";

function logPreflightDecisionLine(preflightDecision) {
	const line = JSON.stringify({
		ts: new Date().toISOString(),
		source: "maat-forge",
		event: "forge.preflight_decision",
		preflight_decision: preflightDecision,
	});
	console.log(line);
}

function logForgeMemoryPreflight(preflightDecision, taskId, sessionId) {
	logForgeGovernanceRowSync(
		buildForgePreflightMemoryRow(preflightDecision, taskId, sessionId),
	);
}

async function tailFile(path, maxLines = 50) {
	try {
		const s = await stat(path);
		if (!s.isFile()) {
			return "";
		}
		const raw = await readFile(path, "utf-8");
		const lines = raw.trimEnd().split("\n");
		return lines.slice(-maxLines).join("\n");
	} catch {
		return "";
	}
}

async function main() {
	await mkdir(reportDir, { recursive: true });
	const iso = new Date().toISOString().replace(/[:.]/g, "-");
	const reportPath = join(reportDir, `forge-first-loop-${iso}.json`);

	const taskId = process.env.FORGE_TASK_ID?.trim() || `task-${iso}-${randomUUID().slice(0, 8)}`;
	const sessionId =
		process.env.FORGE_SESSION_ID?.trim() || `forge-session-${process.pid}-${randomUUID().slice(0, 8)}`;
	const machineId = getForgeMachineId();

	const envelopeBase = {
		sessionId,
		taskId,
		jobType: JOB_TYPE,
		requestedAction: REQUESTED_ACTION,
		targetClass: TARGET_CLASS,
		riskClass: JOB_RISK_CLASS,
	};

	const constitutional = blockConstitutionalRisk(JOB_RISK_CLASS);
	if (constitutional) {
		const preflightDecision = buildPreflightDecisionRecord({
			envelopeSent: null,
			decisionReceived: null,
			machineId,
			jobType: JOB_TYPE,
			riskClass: JOB_RISK_CLASS,
			outcome: "blocked_constitutional",
			reason: constitutional.reason,
			tags: ["constitutional_local_block"],
		});
		const blocked = {
			schema: "maat-forge/first-bounded-loop/v2",
			generatedAt: new Date().toISOString(),
			preflight_decision: preflightDecision,
			guard: { preflight: "blocked", ...constitutional },
		};
		await appendFile(reportPath, `${JSON.stringify(blocked, null, 2)}\n`, "utf-8");
		logPreflightDecisionLine(preflightDecision);
		logForgeMemoryPreflight(preflightDecision, taskId, sessionId);
		console.error("[maat-forge] constitutional_risk — job not started:", constitutional.reason);
		process.exit(2);
	}

	let guardOutcome = { skipped: true, reason: "not_run" };
	/** @type {ReturnType<typeof buildPreflightDecisionRecord> | null} */
	let preflightDecision = null;

	if (guardPreflightSkipped()) {
		console.error(
			"[maat-forge] WARNING: SKIP_GUARD_PREFLIGHT set — Tehuti Guard preflight bypassed (dev only).",
		);
		const envelope = buildDecisionEnvelope(envelopeBase);
		const guardUrl = defaultGuardBaseUrl();
		guardOutcome = { skipped: true, reason: "SKIP_GUARD_PREFLIGHT", guardUrl };
		preflightDecision = buildPreflightDecisionRecord({
			envelopeSent: envelope,
			decisionReceived: null,
			machineId,
			jobType: JOB_TYPE,
			riskClass: JOB_RISK_CLASS,
			outcome: "skipped",
			reason: "SKIP_GUARD_PREFLIGHT",
			guardUrl,
			httpStatus: null,
			tags: ["preflight_skipped", "dev_bypass"],
			correlationId:
				envelope.correlation_id != null ? String(envelope.correlation_id) : null,
		});
	} else {
		const envelope = buildDecisionEnvelope(envelopeBase);
		const guardUrl = defaultGuardBaseUrl();
		let allowed = false;
		let raw = {};
		let status = 0;
		try {
			({ allowed, raw, status } = await postGuardDecision(guardUrl, envelope));
		} catch (err) {
			const { message, tags } = classifyGuardFetchError(err);
			guardOutcome = {
				skipped: false,
				guardUrl,
				error: message,
				preflight: "error",
			};
			preflightDecision = buildPreflightDecisionRecord({
				envelopeSent: envelope,
				decisionReceived: null,
				machineId,
				jobType: JOB_TYPE,
				riskClass: JOB_RISK_CLASS,
				outcome: "error",
				reason: message,
				guardUrl,
				httpStatus: null,
				tags,
				correlationId:
					envelope.correlation_id != null ? String(envelope.correlation_id) : null,
			});
			const blockedArtifact = {
				schema: "maat-forge/first-bounded-loop/v2",
				generatedAt: new Date().toISOString(),
				preflight_decision: preflightDecision,
				guard: { preflight: "error", outcome: guardOutcome, envelope },
			};
			await appendFile(reportPath, `${JSON.stringify(blockedArtifact, null, 2)}\n`, "utf-8");
			logPreflightDecisionLine(preflightDecision);
			logForgeMemoryPreflight(preflightDecision, taskId, sessionId);
			console.error("[maat-forge] Guard preflight request failed:", message);
			const sinkLine = JSON.stringify({
				ts: new Date().toISOString(),
				source: "maat-forge",
				event: "forge.guard_preflight_error",
				severity: "warning",
				detail: message,
				meta: {
					reportPath,
					taskId,
					sessionId,
					tags: preflightDecision.tags,
				},
			});
			console.log(sinkLine);
			process.exit(2);
		}
		const guardTags = Array.isArray(raw.tags) ? raw.tags.map(String) : [];
		preflightDecision = buildPreflightDecisionRecord({
			envelopeSent: envelope,
			decisionReceived: raw,
			machineId,
			jobType: JOB_TYPE,
			riskClass: JOB_RISK_CLASS,
			outcome: allowed ? "allow" : "deny",
			reason: raw.reason != null ? String(raw.reason) : null,
			guardUrl,
			httpStatus: status,
			tags: allowed ? guardTags : [...guardTags, "policy_rejection"],
			explanationId:
				raw.explanation_id != null ? String(raw.explanation_id) : null,
			matchedRules: Array.isArray(raw.matched_rules) ? raw.matched_rules : null,
			correlationId:
				raw.correlation_id != null
					? String(raw.correlation_id)
					: envelope.correlation_id != null
						? String(envelope.correlation_id)
						: null,
		});
		guardOutcome = {
			skipped: false,
			guardUrl,
			httpStatus: status,
			decision: raw.decision,
			severity: raw.severity,
			reason: raw.reason,
			tags: raw.tags,
			blocking_actions: raw.blocking_actions,
			policy_version: raw.policy_version,
		};
		if (!allowed) {
			const blockedArtifact = {
				schema: "maat-forge/first-bounded-loop/v2",
				generatedAt: new Date().toISOString(),
				preflight_decision: preflightDecision,
				guard: { preflight: "denied", outcome: guardOutcome, envelope },
			};
			await appendFile(reportPath, `${JSON.stringify(blockedArtifact, null, 2)}\n`, "utf-8");
			logPreflightDecisionLine(preflightDecision);
			logForgeMemoryPreflight(preflightDecision, taskId, sessionId);
			console.error(
				`[maat-forge] Guard blocked job: decision=${raw.decision} reason=${raw.reason || status}`,
			);
			const sinkLine = JSON.stringify({
				ts: new Date().toISOString(),
				source: "maat-forge",
				event: "forge.guard_preflight_blocked",
				severity: raw.severity || "warning",
				detail: String(raw.reason || "guard_denied"),
				meta: {
					reportPath,
					taskId,
					sessionId,
					decision: raw.decision,
					tags: preflightDecision.tags,
				},
			});
			console.log(sinkLine);
			process.exit(2);
		}
	}

	const logTail = immuneLog ? await tailFile(immuneLog, 80) : "";

	const artifact = {
		schema: "maat-forge/first-bounded-loop/v4",
		generatedAt: new Date().toISOString(),
		taskId,
		sessionId,
		preflight_decision: preflightDecision,
		guard: { preflight: guardOutcome },
		input: {
			maatImmuneLogPath: immuneLog || null,
			logTailChars: logTail.length,
		},
		immune: {
			// Stub: production would parse JSONL and score anomalies
			summary: logTail
				? "Immune log tail captured for analyst review."
				: "MAAT_IMMUNE_LOG unset — no immune log input.",
		},
		repair: {
			status: "candidate_stub",
			detail:
				"No automated repair applied. Per MAAT-IMMUNE-SYSTEM.md, promotion requires human approval; sacred paths are never mutated by this job.",
			event: "repair.candidate_generated",
			severity: "info",
			/** What class of repair this job would eventually propose (v1 stub = non-sacred only). */
			proposed_target_class: "prompt_adjustment",
			proposed_target_classes_allowed: [
				"prompt_adjustment",
				"scoring_adjustment",
				"routing_adjustment",
				"config_adjustment",
			],
			proposed_target_classes_forbidden: ["sacred_mutation"],
		},
	};

	await appendFile(reportPath, `${JSON.stringify(artifact, null, 2)}\n`, "utf-8");

	if (preflightDecision) {
		logPreflightDecisionLine(preflightDecision);
		logForgeMemoryPreflight(preflightDecision, taskId, sessionId);
	}

	// Optional: append one line for gitMaat / unified pipeline (stdout contract)
	const sinkLine = JSON.stringify({
		ts: new Date().toISOString(),
		source: "maat-forge",
		event: "repair.candidate_generated",
		severity: "info",
		detail: "first-bounded-loop completed",
		meta: { reportPath },
	});
	console.log(sinkLine);

	return reportPath;
}

main()
	.then((p) => {
		console.error(`[maat-forge] report written: ${p}`);
		process.exit(0);
	})
	.catch((e) => {
		console.error("[maat-forge] job failed:", e);
		process.exit(1);
	});
