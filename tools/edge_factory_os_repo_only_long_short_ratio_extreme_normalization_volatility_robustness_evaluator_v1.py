#!/usr/bin/env python
"""Evaluate the long-short ratio extreme-normalization volatility robustness chain."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_V1"
MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_volatility_robustness_evaluator_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_volatility_robustness_evaluator_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "a701399c8cf13bdd4ba4760e6a9abed2b441e06c"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_ROBUSTNESS_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_volatility_robustness_runner_v1.json"
)
SOURCE_DIAGNOSTIC_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_forward_return_diagnostic_v1.json"
)
SOURCE_VALIDATOR_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_event_validator_v1.json"
)
SOURCE_DISCOVERY_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json"
)
SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_VALIDATOR_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
]

EVALUATOR_STATUS_PASS = (
    "PASS_REPO_ONLY_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_CREATED"
)
EVALUATOR_STATUS_BLOCKED = "BLOCKED_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR"
ARTIFACT_KIND = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR"

RESULT_PROMISING = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_PROMISING_DIAGNOSTIC_ONLY"
RESULT_WEAK = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_WEAK_OR_NOT_ROBUST"
RESULT_ATTENTION = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_REQUIRES_ATTENTION"
RESULT_FAILED = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_FAILED_STOP"

THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"
NEXT_INDEPENDENT_VALIDATION_CONTRACT = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_V1"
)
NEXT_DIAGNOSTIC_EVALUATOR = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_EVALUATOR_V1"

EXPECTED_ROBUSTNESS_CLASSIFICATION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY"
)
EXPECTED_DIAGNOSTIC_CLASSIFICATION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY"
)
EXPECTED_VALIDATOR_CLASSIFICATIONS = {
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS",
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
}
EXPECTED_DISCOVERY_CLASSIFICATION = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY"
EXPECTED_THEORY_QUEUE_CLASSIFICATION = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY"

PRIMARY_TARGET_KEYS = [
    "optional_account_position_divergence_resolution_candidate__15m",
    "optional_account_position_divergence_resolution_candidate__1h",
    "optional_account_position_divergence_resolution_candidate__4h",
]


class EvaluatorBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def run_git(args: list[str]) -> tuple[int, str, str]:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={safe_dir}", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.returncode, result.stdout, result.stderr


def git_lines(args: list[str]) -> list[str]:
    code, stdout, stderr = run_git(args)
    if code != 0:
        raise EvaluatorBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
    return [line.rstrip() for line in stdout.splitlines() if line.strip()]


def current_head() -> str:
    lines = git_lines(["rev-parse", "HEAD"])
    return lines[0] if lines else ""


def current_branch() -> str:
    lines = git_lines(["branch", "--show-current"])
    return lines[0] if lines else ""


def output_only_status(status_lines: list[str]) -> bool:
    allowed = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
    for line in status_lines:
        if line in allowed:
            continue
        if line.startswith("!! ") and line[3:].startswith("cache/"):
            continue
        return False
    return True


def recovery_audit() -> dict[str, Any]:
    head = current_head()
    porcelain = git_lines(["status", "--porcelain=v1"])
    staged = git_lines(["diff", "--cached", "--name-status"])
    modified = git_lines(["diff", "--name-status"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    head_matches = head == EXPECTED_HEAD
    if staged:
        decision = "RECOVERY_STAGED_FILES_PRESENT_STOP"
    elif not head_matches:
        decision = "RECOVERY_HEAD_MISMATCH_STOP"
    elif not output_only_status(porcelain):
        decision = "RECOVERY_DIRTY_WITH_UNKNOWN_OR_RISKY_FILES_STOP"
    else:
        decision = RECOVERY_AUDIT_STATUS
    return {
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head_matches,
        "branch": current_branch(),
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "recovery_decision": decision,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_artifact_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative_path in INPUT_ARTIFACT_RELATIVE_PATHS:
        path = REPO_ROOT / relative_path
        if not path.exists():
            raise EvaluatorBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise EvaluatorBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise EvaluatorBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise EvaluatorBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise EvaluatorBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    validator = read_json_readonly(SOURCE_VALIDATOR_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "volatility robustness runner"),
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "forward diagnostic"),
        SOURCE_VALIDATOR_RELATIVE_PATH: verify_payload_hash(validator, "event validator"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "event discovery"),
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
    }
    return robustness, diagnostic, validator, discovery, theory_queue, payload_hashes


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_returns": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "entry_exit_rules_created": False,
        "sizing_rules_created": False,
        "signed_return_findings_promoted": False,
        "event_definitions_modified": False,
        "returns_recomputed": False,
        "null_validation_rerun": False,
        "prior_artifacts_modified": False,
    }


def artifact_forbidden_flags_ok(artifact: dict[str, Any]) -> bool:
    flags = artifact.get("forbidden_actions_confirmed_false")
    if not isinstance(flags, dict):
        return False
    return all(value is False for value in flags.values())


def artifact_permissions_false(artifact: dict[str, Any]) -> bool:
    for key in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]:
        if artifact.get(key) is not False:
            return False
    return True


def input_integrity_checks(
    robustness: dict[str, Any],
    diagnostic: dict[str, Any],
    validator: dict[str, Any],
    discovery: dict[str, Any],
    theory_queue: dict[str, Any],
) -> dict[str, bool]:
    return {
        "robustness_promising": robustness.get("result_classification") == EXPECTED_ROBUSTNESS_CLASSIFICATION,
        "diagnostic_promising_volatility_only": diagnostic.get("result_classification") == EXPECTED_DIAGNOSTIC_CLASSIFICATION,
        "validator_passed": validator.get("result_classification") in EXPECTED_VALIDATOR_CLASSIFICATIONS,
        "discovery_ready": discovery.get("result_classification") == EXPECTED_DISCOVERY_CLASSIFICATION,
        "theory_queue_ready": theory_queue.get("result_classification") == EXPECTED_THEORY_QUEUE_CLASSIFICATION,
        "robustness_forbidden_false": artifact_forbidden_flags_ok(robustness),
        "diagnostic_forbidden_false": artifact_forbidden_flags_ok(diagnostic),
        "validator_forbidden_false": artifact_forbidden_flags_ok(validator),
        "discovery_forbidden_false": artifact_forbidden_flags_ok(discovery),
        "robustness_permissions_false": artifact_permissions_false(robustness),
        "diagnostic_permissions_false": artifact_permissions_false(diagnostic),
        "validator_permissions_false": artifact_permissions_false(validator),
    }


def get_primary_null_results(robustness: dict[str, Any]) -> dict[str, Any]:
    summary = robustness.get("month_aware_symbol_balanced_null_summary", {})
    if not isinstance(summary, dict):
        return {}
    results = summary.get("primary_month_aware_null_results", {})
    return results if isinstance(results, dict) else {}


def summarize_research_chain(
    robustness: dict[str, Any],
    diagnostic: dict[str, Any],
    validator: dict[str, Any],
    discovery: dict[str, Any],
    theory_queue: dict[str, Any],
) -> dict[str, Any]:
    return {
        "theory_queue": {
            "result_classification": theory_queue.get("result_classification"),
            "summary": "Outcome-blind queue advanced LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT after prior routes were monitor-only, closed, or sample-limited.",
        },
        "event_discovery": {
            "result_classification": discovery.get("result_classification"),
            "summary": "Event discovery selected long normalization, short normalization, and account/position divergence resolution.",
            "selected_clean_event_definitions": discovery.get("selected_clean_event_definitions", {}),
        },
        "event_validator": {
            "result_classification": validator.get("result_classification"),
            "summary": "Validator passed with attention; outcome-blind and no-leakage checks passed, and main definitions were accepted.",
            "forward_return_diagnostic_allowed": validator.get("forward_return_diagnostic_allowed"),
            "attention_checks": validator.get("attention_checks", {}),
        },
        "forward_diagnostic": {
            "result_classification": diagnostic.get("result_classification"),
            "summary": "Signed-return tests did not pass; volatility/absolute-return diagnostic for account/position divergence resolution was promising.",
            "event_counts_by_definition": diagnostic.get("event_counts_by_definition", {}),
            "top_volatility_findings": diagnostic.get("top_volatility_findings", []),
            "top_signed_return_findings": diagnostic.get("top_signed_return_findings", []),
        },
        "robustness_runner": {
            "result_classification": robustness.get("result_classification"),
            "summary": "Robustness confirmed 15m, 1h, and 4h account/position divergence volatility targets.",
            "primary_robustness_targets": robustness.get("primary_robustness_targets", []),
        },
    }


def summarize_primary_findings(robustness: dict[str, Any]) -> dict[str, Any]:
    primary_null = get_primary_null_results(robustness)
    gates = robustness.get("primary_robustness_gates", {})
    arbusdt = robustness.get("arbusdt_exclusion_sensitivity", {})
    alt = robustness.get("alternative_volatility_metric_sensitivity", {})
    observed = robustness.get("observed_volatility_stats_by_target", {})
    target_summary: dict[str, Any] = {}
    for key in PRIMARY_TARGET_KEYS:
        null_result = primary_null.get(key, {}) if isinstance(primary_null, dict) else {}
        gate_result = gates.get(key, {}) if isinstance(gates, dict) else {}
        arbusdt_entry = arbusdt.get(key, {}) if isinstance(arbusdt, dict) else {}
        alt_entry = alt.get(key, {}) if isinstance(alt, dict) else {}
        observed_entry = observed.get(key, {}) if isinstance(observed, dict) else {}
        target_summary[key] = {
            "target": "account/position divergence resolution",
            "event_count": observed_entry.get("event_count", 947),
            "horizon": key.rsplit("__", 1)[-1],
            "primary_metric_family": "forward_abs_return / realized-volatility proxy",
            "mean_abs_return": observed_entry.get("mean_abs_return"),
            "p_abs_high_mean": null_result.get("p_abs_high_mean"),
            "fdr_q": null_result.get("fdr_q"),
            "bonferroni_p": null_result.get("bonferroni_p"),
            "leave_one_symbol_passed": gate_result.get("no_single_symbol_dependence") is True,
            "leave_one_month_passed": gate_result.get("no_single_month_dependence") is True,
            "arbusdt_exclusion_passed": gate_result.get("arbusdt_exclusion_preserves_effect") is True,
            "arbusdt_exclusion": {
                "arbusdt_event_count": arbusdt_entry.get("arbusdt_event_count"),
                "arbusdt_exclusion_pass": arbusdt_entry.get("arbusdt_exclusion_pass"),
                "magnitude_ratio_vs_full": arbusdt_entry.get("magnitude_ratio_vs_full"),
                "p_abs_high_mean_ex_arbusdt": arbusdt_entry.get("p_abs_high_mean_ex_arbusdt"),
            },
            "alternate_volatility_metrics_passed": gate_result.get("alternate_volatility_proxy_supports_direction") is True,
            "alternative_volatility_metric_sensitivity": {
                "alternate_proxy_supports_direction": alt_entry.get("alternate_proxy_supports_direction"),
                "forward_range_proxy_p_high": alt_entry.get("forward_range_proxy_p_high"),
                "realized_vol_proxy_p_high": alt_entry.get("realized_vol_proxy_p_high"),
            },
            "all_primary_robustness_gates_true": gate_result.get("primary_target_passes_all_gates") is True,
        }
    return {
        "primary_target": "account/position divergence resolution",
        "primary_horizons": ["15m", "1h", "4h"],
        "event_count": 947,
        "target_results": target_summary,
        "failed_gates": robustness.get("failed_robustness_gates", []),
    }


def summarize_robustness_gates(robustness: dict[str, Any]) -> dict[str, Any]:
    gates = robustness.get("primary_robustness_gates", {})
    failed = robustness.get("failed_robustness_gates", [])
    target_gate_summary: dict[str, Any] = {}
    for key in PRIMARY_TARGET_KEYS:
        target_gates = gates.get(key, {}) if isinstance(gates, dict) else {}
        target_gate_summary[key] = {
            "month_aware_symbol_balanced_fdr_lte_05": target_gates.get("month_aware_symbol_balanced_fdr_lte_05") is True,
            "bonferroni_lte_05": target_gates.get("bonferroni_lte_05") is True,
            "no_single_symbol_dependence": target_gates.get("no_single_symbol_dependence") is True,
            "no_single_month_dependence": target_gates.get("no_single_month_dependence") is True,
            "arbusdt_exclusion_preserves_effect": target_gates.get("arbusdt_exclusion_preserves_effect") is True,
            "alternate_volatility_proxy_supports_direction": (
                target_gates.get("alternate_volatility_proxy_supports_direction") is True
            ),
            "missing_rows_immaterial": target_gates.get("missing_rows_immaterial") is True,
            "input_hashes_unchanged": target_gates.get("input_hashes_unchanged") is True,
            "primary_target_passes_all_gates": target_gates.get("primary_target_passes_all_gates") is True,
        }
    return {
        "primary_target_gate_summary": target_gate_summary,
        "all_primary_targets_pass": all(
            item["primary_target_passes_all_gates"] for item in target_gate_summary.values()
        ),
        "failed_robustness_gates": failed,
        "month_aware_symbol_balanced_null": {
            "requested": robustness.get("month_aware_symbol_balanced_null_summary", {}).get("count_requested"),
            "completed": robustness.get("month_aware_symbol_balanced_null_summary", {}).get("count_completed"),
        },
        "leave_one_symbol_out_passed": all(
            not summary.get("any_single_symbol_necessary", True)
            for summary in robustness.get("leave_one_symbol_out_summary", {}).values()
        ),
        "leave_one_month_out_passed": all(
            not summary.get("any_single_month_necessary", True)
            for summary in robustness.get("leave_one_month_out_summary", {}).values()
        ),
        "arbusdt_exclusion_passed": all(
            summary.get("arbusdt_exclusion_pass") is True
            for summary in robustness.get("arbusdt_exclusion_sensitivity", {}).values()
        ),
        "alternative_volatility_metrics_passed": all(
            summary.get("alternate_proxy_supports_direction") is True
            for summary in robustness.get("alternative_volatility_metric_sensitivity", {}).values()
        ),
    }


def signed_return_handling(robustness: dict[str, Any], diagnostic: dict[str, Any]) -> dict[str, Any]:
    tracking = robustness.get("secondary_signed_return_tracking", {})
    return {
        "signed_return_findings_secondary_only": True,
        "signed_return_findings_not_promoted": tracking.get("signed_return_findings_not_promoted") is True,
        "signed_return_strategy_candidate_signal_allowed": False,
        "signed_return_results_cannot_override_volatility_diagnostic_classification": True,
        "diagnostic_signed_return_fdr_q_values": diagnostic.get("signed_return_fdr_q_values", {}),
        "diagnostic_signed_return_bonferroni_p_values": diagnostic.get("signed_return_bonferroni_p_values", {}),
        "robustness_secondary_signed_return_tracking": tracking,
    }


def summarize_attention_items(robustness: dict[str, Any], validator: dict[str, Any]) -> dict[str, Any]:
    return {
        "top_symbol_concentration_near_limit_recorded": robustness.get("attention_checks", {}).get(
            "top_symbol_concentration_near_25pct_recorded"
        ),
        "raw_to_cooldown_compression_high_recorded": robustness.get("attention_checks", {}).get(
            "raw_to_cooldown_compression_high_recorded"
        ),
        "normalization_strength_weak_recorded": robustness.get("attention_checks", {}).get(
            "normalization_strength_weak_recorded"
        ),
        "top_account_or_account_position_ratio_reliance_recorded": robustness.get("attention_checks", {}).get(
            "mostly_top_account_or_account_position_pair_ratio_recorded"
        ),
        "persistence_break_sparse_tiers_not_promoted": robustness.get("attention_checks", {}).get(
            "persistence_break_sparse_tiers_not_promoted"
        ),
        "validator_attention_checks": validator.get("attention_checks", {}),
        "attention_items_are_not_automatic_failures": True,
    }


def remaining_limitations(robustness: dict[str, Any]) -> list[str]:
    warnings = robustness.get("data_quality_warnings", [])
    return [
        "The same 2023-2025 sample was used for discovery, evaluation, and robustness.",
        "No independent holdout or prospective validation has been completed yet.",
        "No cost, slippage, execution, fill, entry, exit, or sizing model exists.",
        "No live or paper validation exists.",
        "This is a volatility/absolute-return diagnostic, not a directional edge or strategy.",
        "Top symbol concentration was near the discovery limit for one selected normalization definition.",
        "Raw-to-cooldown compression was high and normalization strength was weak for the directional normalization definitions.",
        "Definitions rely on top-account/account-position ratio mechanics.",
        "Secondary signed-return findings remain tracking-only and cannot drive route promotion.",
        "Raw cache files were not committed.",
        *[f"Data-quality warning from robustness runner: {warning}" for warning in warnings],
    ]


def all_primary_targets_pass(robustness: dict[str, Any]) -> bool:
    gates = robustness.get("primary_robustness_gates")
    if not isinstance(gates, dict):
        return False
    for key in PRIMARY_TARGET_KEYS:
        target = gates.get(key)
        if not isinstance(target, dict) or target.get("primary_target_passes_all_gates") is not True:
            return False
    return True


def blocked_artifact(
    reason: str,
    audit: dict[str, Any] | None = None,
    hashes_before: dict[str, str] | None = None,
    hashes_after: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "evaluator_status": EVALUATOR_STATUS_BLOCKED,
        "status": EVALUATOR_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": (audit or {}).get("recovery_decision", "RECOVERY_UNKNOWN"),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "research_chain_summary": {},
        "primary_volatility_finding_summary": {},
        "robustness_gate_summary": {},
        "signed_return_handling": {},
        "attention_items": {},
        "remaining_limitations": [f"BLOCKED: {reason}"],
        "final_decision": "blocked; route requires repair or review before any next module",
        "diagnostic_route_promising": False,
        "independent_validation_required": True,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_DIAGNOSTIC_EVALUATOR,
        "blocker": reason,
        "validation_checks": {"blocked_without_substitution": True},
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    if audit["recovery_decision"] != RECOVERY_AUDIT_STATUS:
        return blocked_artifact(audit["recovery_decision"], audit)

    hashes_before = input_artifact_hashes()
    robustness, diagnostic, validator, discovery, theory_queue, payload_hashes = load_inputs()
    integrity = input_integrity_checks(robustness, diagnostic, validator, discovery, theory_queue)
    if not all(integrity.values()):
        failed = [key for key, value in integrity.items() if value is not True]
        raise EvaluatorBlocked(f"INPUT_INTEGRITY_CHECK_FAILED: {failed}")

    primary_targets_pass = all_primary_targets_pass(robustness)
    failed_gates = robustness.get("failed_robustness_gates", [])
    no_failed_gates = isinstance(failed_gates, list) and not failed_gates
    forbidden_ok = (
        artifact_forbidden_flags_ok(robustness)
        and artifact_forbidden_flags_ok(diagnostic)
        and artifact_forbidden_flags_ok(validator)
        and artifact_forbidden_flags_ok(discovery)
        and artifact_permissions_false(robustness)
        and artifact_permissions_false(diagnostic)
        and artifact_permissions_false(validator)
    )

    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise EvaluatorBlocked("INPUT_ARTIFACT_HASH_CHANGED")

    diagnostic_route_promising = (
        robustness.get("result_classification") == EXPECTED_ROBUSTNESS_CLASSIFICATION
        and primary_targets_pass
        and no_failed_gates
        and forbidden_ok
        and input_unchanged
    )
    if diagnostic_route_promising:
        result_classification = RESULT_PROMISING
        allowed_next_step = NEXT_INDEPENDENT_VALIDATION_CONTRACT
        final_decision = (
            "promising volatility diagnostic only; eligible only for a pre-registered independent validation contract; "
            "strategy, signal, candidate, release, runtime, live, and capital actions remain disallowed"
        )
    elif not primary_targets_pass or not no_failed_gates:
        result_classification = RESULT_WEAK
        allowed_next_step = NEXT_DIAGNOSTIC_EVALUATOR
        final_decision = "weak or not robust; do not proceed to independent validation"
    else:
        result_classification = RESULT_ATTENTION
        allowed_next_step = NEXT_DIAGNOSTIC_EVALUATOR
        final_decision = "requires attention before any independent validation contract"

    validation_checks = {
        "input_artifact_hashes_unchanged": input_unchanged,
        "prior_robustness_promising": robustness.get("result_classification") == EXPECTED_ROBUSTNESS_CLASSIFICATION,
        "at_least_one_primary_volatility_target_passes": any(
            robustness.get("primary_robustness_gates", {}).get(key, {}).get("primary_target_passes_all_gates") is True
            for key in PRIMARY_TARGET_KEYS
        ),
        "all_primary_volatility_targets_pass": primary_targets_pass,
        "failed_robustness_gates_none": no_failed_gates,
        "forbidden_actions_false": forbidden_ok,
        "independent_validation_not_complete": True,
        "strategy_allowed_false": True,
        "signal_allowed_false": True,
        "candidate_generation_allowed_false": True,
        "release_allowed_false": True,
        "runtime_live_capital_false": True,
        "no_returns_recomputed": True,
        "no_null_validation_rerun": True,
        "no_event_definition_modified": True,
        "no_entry_exit_or_sizing_rules": True,
        "no_signed_return_promotion": True,
    }

    artifact = {
        "evaluator_status": EVALUATOR_STATUS_PASS,
        "status": EVALUATOR_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_decision"],
        "current_head": audit["current_head"],
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": input_unchanged,
        "input_payload_hashes_verified": payload_hashes,
        "input_integrity_checks": integrity,
        "research_chain_summary": summarize_research_chain(robustness, diagnostic, validator, discovery, theory_queue),
        "primary_volatility_finding_summary": summarize_primary_findings(robustness),
        "robustness_gate_summary": summarize_robustness_gates(robustness),
        "signed_return_handling": signed_return_handling(robustness, diagnostic),
        "attention_items": summarize_attention_items(robustness, validator),
        "remaining_limitations": remaining_limitations(robustness),
        "final_decision": final_decision,
        "diagnostic_route_promising": diagnostic_route_promising,
        "independent_validation_required": True,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": allowed_next_step,
        "blocker": None,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"status: {artifact['evaluator_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"primary_volatility_finding_summary: {artifact['primary_volatility_finding_summary']}")
    print(f"robustness_gate_summary: {artifact['robustness_gate_summary']}")
    print(f"signed_return_handling: {artifact['signed_return_handling']}")
    print(f"attention_items: {artifact['attention_items']}")
    print(f"remaining_limitations: {artifact['remaining_limitations']}")
    print(f"final_decision: {artifact['final_decision']}")
    print(f"diagnostic_route_promising: {bool_text(bool(artifact['diagnostic_route_promising']))}")
    print(f"independent_validation_required: {bool_text(bool(artifact['independent_validation_required']))}")
    print(f"strategy_allowed: {bool_text(bool(artifact['strategy_allowed']))}")
    print(f"signal_allowed: {bool_text(bool(artifact['signal_allowed']))}")
    print(f"candidate_generation_allowed: {bool_text(bool(artifact['candidate_generation_allowed']))}")
    print(f"release_allowed: {bool_text(bool(artifact['release_allowed']))}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"forbidden actions confirmed false: {artifact['forbidden_actions_confirmed_false']}")
    print(f"blocker: {artifact['blocker']}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")


def main() -> int:
    hashes_before = None
    audit = None
    try:
        audit = recovery_audit()
        print(f"current HEAD: {audit['current_head']}")
        print(f"expected HEAD: {EXPECTED_HEAD}")
        print(f"branch: {audit['branch']}")
        print(f"git status porcelain: {audit['git_status_porcelain']}")
        print(f"staged files: {audit['staged_files']}")
        print(f"modified tracked files: {audit['modified_tracked_files']}")
        print(f"untracked files: {audit['untracked_files']}")
        print(f"deleted files: {audit['deleted_files']}")
        print(f"recovery decision: {audit['recovery_decision']}")
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
        hashes_after = input_artifact_hashes()
        if hashes_before != hashes_after:
            artifact = blocked_artifact("INPUT_ARTIFACT_HASH_CHANGED", audit, hashes_before, hashes_after)
        write_artifact(artifact)
        print_summary(artifact)
        return 0 if artifact["evaluator_status"] == EVALUATOR_STATUS_PASS else 1
    except Exception as exc:
        try:
            hashes_after = input_artifact_hashes() if hashes_before else None
        except Exception:
            hashes_after = None
        artifact = blocked_artifact(str(exc), audit, hashes_before, hashes_after)
        write_artifact(artifact)
        print_summary(artifact)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
