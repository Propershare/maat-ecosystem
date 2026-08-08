/**
 * Tehuti Guard v1 preflight for MAAT Forge — POST /decision before risky work.
 * Risk classes: low_risk | medium_risk | high_risk | constitutional_risk
 * constitutional_risk never runs autonomously (blocked locally; no execution).
 */

import { spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { hostname } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const _FORGE_LIB_DIR = dirname(fileURLToPath(import.meta.url));
const _FORGE_ROOT = join(_FORGE_LIB_DIR, "..");
const DEFAULT_GOVERNANCE_SCRIPT = join(
	_FORGE_ROOT,
	"..",
	"maatlangchain",
	"scripts",
	"log_governance_event.py",
);

/** @typedef {"low_risk"|"medium_risk"|"high_risk"|"constitutional_risk"} ForgeRiskClass */

/**
 * @param {string} forgeClass
 * @returns {"low"|"medium"|"high"}
 */
export function mapForgeRiskToGuardRisk(forgeClass) {
	switch (forgeClass) {
		case "low_risk":
			return "low";
		case "medium_risk":
			return "medium";
		case "high_risk":
			return "high";
		case "constitutional_risk":
			throw new Error(
				"constitutional_risk cannot be mapped to Guard execution — block locally",
			);
		default:
			return "medium";
	}
}

export function getForgeMachineId() {
	const m = process.env.MAAT_MACHINE_ID?.trim();
	if (m) {
		return m;
	}
	const d = process.env.MAAT_DEVICE_ID?.trim();
	if (d) {
		return d;
	}
	return hostname();
}

export function getForgeAgentId() {
	return (
		process.env.FORGE_AGENT_ID?.trim() ||
		process.env.MAAT_AGENT_ID?.trim() ||
		"maat-forge"
	);
}

/**
 * Build JSON body for POST /decision (Guard reads machine_id, actor, action; forge_meta is optional echo).
 * @param {{
 *   machineId?: string,
 *   agentId?: string,
 *   sessionId: string,
 *   taskId: string,
 *   jobType: string,
 *   requestedAction: string,
 *   targetClass: string,
 *   riskClass: ForgeRiskClass,
 *   origin?: string,
 *   correlationId?: string,
 * }} opts
 */
export function buildDecisionEnvelope(opts) {
	const {
		machineId = getForgeMachineId(),
		agentId = getForgeAgentId(),
		sessionId,
		taskId,
		jobType,
		requestedAction,
		targetClass,
		riskClass,
		origin = "maat-forge",
		correlationId = process.env.FORGE_CORRELATION_ID?.trim() || `corr-${randomUUID()}`,
	} = opts;

	if (riskClass === "constitutional_risk") {
		throw new Error("buildDecisionEnvelope: use blockConstitutionalRisk instead");
	}

	const actionRisk = mapForgeRiskToGuardRisk(riskClass);

	return {
		machine_id: machineId,
		correlation_id: correlationId,
		actor: {
			id: agentId,
			role: `${origin}|session=${sessionId}|task=${taskId}`,
		},
		action: {
			kind: jobType,
			resource: String(targetClass),
			risk: actionRisk,
		},
		forge_meta: {
			session_id: sessionId,
			task_id: taskId,
			job_type: jobType,
			requested_action: requestedAction,
			target_class: targetClass,
			risk_hint: riskClass,
			origin,
			correlation_id: correlationId,
		},
	};
}

/**
 * @param {ForgeRiskClass} riskClass
 * @returns {{ blocked: true, reason: string, riskClass: ForgeRiskClass }}
 */
export function blockConstitutionalRisk(riskClass) {
	if (riskClass !== "constitutional_risk") {
		return null;
	}
	return {
		blocked: true,
		reason:
			"constitutional_risk jobs must not run autonomously — human / non-forge path only",
		riskClass,
	};
}

/**
 * @param {string} baseUrl Tehuti Guard base (no trailing path), e.g. http://127.0.0.1:8013
 * @param {Record<string, unknown>} envelope
 * @param {{ timeoutMs?: number }} [options]
 * @returns {Promise<{ allowed: boolean, raw: Record<string, unknown>, status: number }>}
 */
export async function postGuardDecision(baseUrl, envelope, options = {}) {
	const timeoutMs = options.timeoutMs ?? 20_000;
	const url = `${baseUrl.replace(/\/$/, "")}/decision`;
	const res = await fetch(url, {
		method: "POST",
		headers: { "Content-Type": "application/json; charset=utf-8" },
		body: JSON.stringify(envelope),
		signal: AbortSignal.timeout(timeoutMs),
	});
	const text = await res.text();
	let raw = {};
	try {
		raw = text ? JSON.parse(text) : {};
	} catch {
		raw = { error: "invalid_json", body: text.slice(0, 500) };
	}
	const decision = String(raw.decision || "").toLowerCase();
	const allowed = decision === "allow" && res.ok;
	return { allowed, raw, status: res.status };
}

export function defaultGuardBaseUrl() {
	return process.env.TEHUTI_GUARD_URL?.trim() || "http://127.0.0.1:8013";
}

export function guardPreflightSkipped() {
	const v = process.env.SKIP_GUARD_PREFLIGHT?.trim().toLowerCase();
	return v === "1" || v === "true" || v === "yes";
}

/**
 * Classify fetch/network failures for tagging (Sentinel/Memory can distinguish infra vs policy).
 * @param {unknown} err
 * @returns {{ message: string, tags: string[] }}
 */
export function classifyGuardFetchError(err) {
	const tags = ["guard_unreachable", "stack_unavailable"];
	const name =
		err && typeof err === "object" && err !== null && "name" in err
			? String(/** @type {{ name?: string }} */ (err).name)
			: "";
	const code =
		err && typeof err === "object" && err !== null && "code" in err
			? String(/** @type {{ code?: string }} */ (err).code)
			: "";
	const msg = err instanceof Error ? err.message : String(err);
	if (name === "TimeoutError" || name === "AbortError" || /timeout/i.test(msg)) {
		tags.push("request_timeout");
	}
	if (code === "ECONNREFUSED" || /ECONNREFUSED/i.test(msg)) {
		tags.push("connection_refused");
	}
	if (code === "ENOTFOUND" || /ENOTFOUND/i.test(msg)) {
		tags.push("dns_failure");
	}
	return { message: msg, tags };
}

/**
 * Machine-readable preflight record — emit on every Forge run (allow, deny, skip, error, block).
 * @param {{
 *   envelopeSent?: object | null,
 *   decisionReceived?: object | null,
 *   machineId: string,
 *   jobType: string,
 *   riskClass: string,
 *   outcome: "allow"|"deny"|"blocked_constitutional"|"skipped"|"error",
 *   reason?: string | null,
 *   guardUrl?: string | null,
 *   httpStatus?: number | null,
 *   tags?: string[],
 *   explanationId?: string | null,
 *   matchedRules?: string[] | null,
 *   correlationId?: string | null,
 * }} p
 */
export function buildPreflightDecisionRecord(p) {
	const {
		envelopeSent = null,
		decisionReceived = null,
		machineId,
		jobType,
		riskClass,
		outcome,
		reason = null,
		guardUrl = null,
		httpStatus = null,
		tags = [],
		explanationId = null,
		matchedRules = null,
		correlationId = null,
	} = p;
	return {
		schema: "maat-forge/preflight_decision/v1",
		timestamp: new Date().toISOString(),
		machine_id: machineId,
		job_type: jobType,
		risk_class: riskClass,
		envelope_sent: envelopeSent,
		decision_received: decisionReceived,
		outcome,
		reason,
		guard_url: guardUrl,
		http_status: httpStatus,
		tags: [...tags],
		explanation_id: explanationId,
		matched_rules: matchedRules,
		correlation_id: correlationId,
	};
}

/**
 * Compact row for maat-memory `maat_governance_events` (no full envelope dump).
 * @param {ReturnType<typeof buildPreflightDecisionRecord>} preflightDecision
 */
export function buildForgePreflightMemoryRow(preflightDecision, taskId, sessionId) {
	const dr = preflightDecision.decision_received;
	const env = preflightDecision.envelope_sent;
	const forgeMeta =
		env && typeof env === "object" && env.forge_meta != null ? env.forge_meta : null;
	return {
		record_type: "forge_preflight",
		source_service: "maat-forge",
		timestamp: preflightDecision.timestamp,
		machine_id: preflightDecision.machine_id,
		job_type: preflightDecision.job_type,
		risk_class: preflightDecision.risk_class,
		outcome: preflightDecision.outcome,
		reason: preflightDecision.reason,
		http_status: preflightDecision.http_status,
		tags: preflightDecision.tags,
		explanation_id: preflightDecision.explanation_id ?? null,
		matched_rules: preflightDecision.matched_rules ?? null,
		correlation_id: preflightDecision.correlation_id ?? null,
		task_id: taskId,
		session_id: sessionId,
		guard_decision:
			dr && typeof dr === "object" && typeof dr.decision === "string" ? dr.decision : null,
		policy_version:
			dr && typeof dr === "object" && dr.policy_version != null
				? String(dr.policy_version)
				: null,
		forge_meta: forgeMeta,
	};
}

export function forgeGovernanceMemoryEnabled() {
	const a = process.env.FORGE_LOG_MEMORY?.trim().toLowerCase();
	const b = process.env.MAAT_GOVERNANCE_MEMORY?.trim().toLowerCase();
	return a === "1" || a === "true" || b === "1" || b === "true";
}

/** Writes one row via maatlangchain/scripts/log_governance_event.py (PostgreSQL). */
export function logForgeGovernanceRowSync(row) {
	if (!forgeGovernanceMemoryEnabled()) {
		return;
	}
	const script = process.env.MAAT_LOG_GOVERNANCE_SCRIPT?.trim() || DEFAULT_GOVERNANCE_SCRIPT;
	const py = process.env.PYTHON?.trim() || "python3";
	const r = spawnSync(py, [script], {
		input: JSON.stringify({ ...row, _agent: "maat-forge" }),
		encoding: "utf-8",
		maxBuffer: 1024 * 1024,
	});
	if (r.status !== 0) {
		console.error(
			"[maat-forge] governance memory log failed:",
			r.stderr || r.signal || r.error,
		);
	}
}
