#!/usr/bin/env python
"""Evaluate the refined extreme OI/taker price-failure robustness chain."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_EVALUATOR_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_forward_return_robustness_evaluator_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_evaluator_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "a6e1732d315369d5760ff42f5ae6a6229246b4ea"

SOURCE_ROBUSTNESS_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_runner_v1.json"
SOURCE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_diagnostic_v1.json"
SOURCE_REFINEMENT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_discovery_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

EVALUATOR_STATUS_PASS = "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_EVALUATOR_CREATED"
EVALUATOR_STATUS_BLOCKED = "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_EVALUATOR"
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_EVALUATOR"

RESULT_PROMISING = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROBUSTNESS_EVALUATOR_PROMISING_DIAGNOSTIC_ONLY"
RESULT_WEAK = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROBUSTNESS_EVALUATOR_WEAK_OR_NOT_ROBUST"
RESULT_RELABEL = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROBUSTNESS_EVALUATOR_REQUIRES_DIRECTION_RELABEL_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROBUSTNESS_EVALUATOR_FAILED_STOP"

NEXT_INDEPENDENT_VALIDATION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_V1"
NEXT_DIRECTION_REVIEW = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_V1"
NEXT_WEAK_EVALUATOR = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR_V1"

DIRECTION_ALIGNED = "DIRECTION_SEMANTICS_ALIGNED"
DIRECTION_COUNTERINTUITIVE = "DIRECTION_SEMANTICS_COUNTERINTUITIVE_REQUIRES_RELABEL"
DIRECTION_UNCLEAR = "DIRECTION_SEMANTICS_UNCLEAR_ATTENTION"


class EvaluatorBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def git_base_args() -> list[str]:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    return ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={safe_dir}"]


def run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        [*git_base_args(), *args],
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
        if line.startswith("!! ") and line[3:].startswith("cache/binance_public_kline_forward_return_diagnostic_v1/"):
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
        decision = "RECOVERY_AUDIT_CLEAN_CONTINUE"
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
        "git_clean_before": not porcelain and not staged and not modified and not untracked and not deleted,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_artifact_hashes() -> dict[str, str]:
    hashes = {}
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


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise EvaluatorBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "robustness runner"),
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "forward-return diagnostic"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "event discovery"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    return robustness, diagnostic, refinement, discovery, dataset, kline, payload_hashes


def all_forbidden_false(*artifacts: dict[str, Any]) -> bool:
    for artifact in artifacts:
        flags = artifact.get("forbidden_actions_confirmed_false", {})
        if not isinstance(flags, dict):
            return False
        if any(value is not False for value in flags.values()):
            return False
    return True


def explicit_permissions_false(*artifacts: dict[str, Any]) -> bool:
    keys = ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]
    for artifact in artifacts:
        for key in keys:
            if key in artifact and artifact.get(key) is not False:
                return False
    return True


def build_research_chain_summary(
    robustness: dict[str, Any],
    diagnostic: dict[str, Any],
    refinement: dict[str, Any],
    discovery: dict[str, Any],
) -> dict[str, Any]:
    selected = refinement.get("selected_clean_event_definitions", [])
    selected_counts = {
        item.get("selection_slot", item.get("definition_id", "unknown")): {
            "definition_id": item.get("definition_id"),
            "cooldown_filtered_count": item.get("cooldown_filtered_count"),
            "raw_event_count": item.get("raw_event_count"),
            "target_event_count_band": item.get("target_event_count_band"),
        }
        for item in selected
        if isinstance(item, dict)
    }
    return {
        "broad_oi_taker_crowding_route": {
            "status": "failed_robustness_before_this_refined_route",
            "summary": "The broad OI/taker/crowding forward-return route was weak/not robust, so this evaluator does not revive it.",
        },
        "strict_price_failure_discovery": {
            "status": discovery.get("discovery_status"),
            "result_classification": discovery.get("result_classification"),
            "summary": "The initial strict price-failure discovery was clean but too sparse.",
        },
        "event_definition_refinement": {
            "status": refinement.get("refinement_status"),
            "result_classification": refinement.get("result_classification"),
            "selected_counts": selected_counts,
            "summary": "Refinement relaxed contemporaneous gates without using future returns and produced usable long_core 463 and short_core 451 cooldown-filtered definitions.",
        },
        "direct_forward_return_diagnostic": {
            "status": diagnostic.get("diagnostic_status"),
            "result_classification": diagnostic.get("result_classification"),
            "summary": "The direct diagnostic identified short_core 1h as the only strong multiple-comparison-adjusted result.",
            "fdr_q_values": diagnostic.get("fdr_q_values"),
            "bonferroni_p_values": diagnostic.get("bonferroni_p_values"),
        },
        "robustness_runner": {
            "status": robustness.get("robustness_status"),
            "result_classification": robustness.get("result_classification"),
            "summary": "Robustness confirmed short_core 1h under month-aware symbol-balanced null, leave-one-symbol-out, leave-one-month-out, and ARBUSDT exclusion.",
        },
    }


def build_primary_finding_summary(robustness: dict[str, Any], diagnostic: dict[str, Any]) -> dict[str, Any]:
    primary = robustness.get("primary_finding", {})
    month_aware = robustness.get("month_aware_symbol_balanced_null_summary", {}).get("primary_short_core_1h", {})
    gates = robustness.get("primary_robustness_gates", {})
    observed = diagnostic.get("observed_stats_by_side_and_horizon", {}).get("short_core", {}).get("1h", {})
    return {
        "side": "short_core",
        "horizon": "1h",
        "observed_mean": primary.get("mean", observed.get("mean")),
        "valid_count": primary.get("valid_forward_return_count", observed.get("valid_forward_return_count")),
        "event_count": observed.get("event_count", diagnostic.get("short_core_event_count")),
        "prior_fdr_q": primary.get("fdr_q"),
        "prior_bonferroni": primary.get("bonferroni_p"),
        "prior_raw_p": primary.get("raw_p"),
        "month_aware_fdr_q": month_aware.get("fdr_q"),
        "month_aware_bonferroni": month_aware.get("bonferroni_p"),
        "month_aware_p_two_sided": month_aware.get("p_values", {}).get("p_two_sided"),
        "month_aware_p_negative_mean": month_aware.get("p_values", {}).get("p_negative_mean"),
        "leave_one_symbol_passed": gates.get("leave_one_symbol_no_single_symbol_necessary") is True,
        "leave_one_month_passed": gates.get("leave_one_month_no_single_month_necessary") is True,
        "arbusdt_exclusion_passed": gates.get("arbusdt_exclusion_direction_preserved") is True
        and gates.get("arbusdt_exclusion_magnitude_ratio_gte_0_50") is True,
        "all_robustness_gates_true": all(value is True for value in gates.values()),
    }


def direction_semantics(primary_summary: dict[str, Any]) -> tuple[str, str | None, str]:
    side = primary_summary.get("side")
    mean = primary_summary.get("observed_mean")
    if side != "short_core" or not isinstance(mean, (int, float)):
        return DIRECTION_UNCLEAR, None, "Side or observed mean is unavailable for a clean semantics check."
    if mean < 0:
        return (
            DIRECTION_COUNTERINTUITIVE,
            "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC",
            "The label 'short_core price failure' implies short pressure failed to continue downward, but the observed 1h close-to-close drift is negative; this is better treated as a neutral delayed-downside-continuation diagnostic until independently reviewed.",
        )
    return (
        DIRECTION_ALIGNED,
        "SHORT_CORE_PRICE_FAILURE_REBOUND_DIAGNOSTIC",
        "The short_core price-failure label is semantically aligned with a non-negative forward drift.",
    )


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_future_returns": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "release": False,
        "entry_exit_rules": False,
        "sizing_rules": False,
        "event_definition_modified_on_forward_returns": False,
    }


def build_remaining_limitations(kline: dict[str, Any]) -> list[str]:
    missing_archives = kline.get("kline_data_quality", {}).get("missing_archives", [])
    return [
        "The same broad 2023-2025 sample was used for event research and diagnostic evaluation.",
        "No independent holdout or prospective validation has been completed yet.",
        "No cost, slippage, or execution model exists in this route.",
        "No entry, exit, or position-sizing rules exist in this route.",
        "No live or paper validation has been performed or authorized.",
        "Sparse crowding-confirmed variants were not primary tests.",
        "358/360 kline archive availability warning remains.",
        f"Missing ARBUSDT 2023-01 and 2023-02 remains recorded: {missing_archives}",
        "ARBUSDT exclusion passed, but that does not replace independent validation.",
        "The direction semantics are counterintuitive and require neutral relabel/review before any independent validation contract is acted on.",
    ]


def blocked_artifact(reason: str, audit: dict[str, Any] | None = None, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
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
        "primary_finding_summary": {},
        "robustness_gate_summary": {},
        "direction_semantics_status": DIRECTION_UNCLEAR,
        "suggested_neutral_diagnostic_label": None,
        "remaining_limitations": [f"BLOCKED: {reason}"],
        "final_decision": "blocked",
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
        "allowed_next_step": NEXT_WEAK_EVALUATOR,
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    if audit["recovery_decision"] != "RECOVERY_AUDIT_CLEAN_CONTINUE":
        return blocked_artifact(audit["recovery_decision"], audit)
    hashes_before = input_artifact_hashes()
    robustness, diagnostic, refinement, discovery, dataset, kline, payload_hashes = load_inputs()
    input_artifacts_found = {relative_path: (REPO_ROOT / relative_path).exists() for relative_path in INPUT_ARTIFACT_RELATIVE_PATHS}
    if not all(input_artifacts_found.values()):
        raise EvaluatorBlocked(f"missing input artifacts: {input_artifacts_found}")

    robustness_status_ok = robustness.get("result_classification") == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY"
    gates = robustness.get("primary_robustness_gates", {})
    gates_all_true = isinstance(gates, dict) and all(value is True for value in gates.values())
    forbidden_ok = all_forbidden_false(robustness, diagnostic, refinement) and explicit_permissions_false(robustness, diagnostic)
    research_chain = build_research_chain_summary(robustness, diagnostic, refinement, discovery)
    primary_summary = build_primary_finding_summary(robustness, diagnostic)
    direction_status, suggested_label, direction_note = direction_semantics(primary_summary)
    diagnostic_route_promising = robustness_status_ok and gates_all_true and forbidden_ok
    independent_validation_required = True
    if not diagnostic_route_promising:
        result_classification = RESULT_WEAK
        allowed_next_step = NEXT_WEAK_EVALUATOR
        final_decision = "weak_or_not_robust; do not proceed without route review"
    elif direction_status == DIRECTION_COUNTERINTUITIVE:
        result_classification = RESULT_RELABEL
        allowed_next_step = NEXT_DIRECTION_REVIEW
        final_decision = (
            "promising diagnostic evidence, but direction semantics are counterintuitive; perform neutral relabel/review before any independent validation contract"
        )
    else:
        result_classification = RESULT_PROMISING
        allowed_next_step = NEXT_INDEPENDENT_VALIDATION
        final_decision = "promising diagnostic only; eligible only for pre-registered independent/prospective validation"
    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise EvaluatorBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    validation_checks = {
        "input_artifacts_found": all(input_artifacts_found.values()),
        "input_artifact_hashes_unchanged": input_unchanged,
        "prior_robustness_promising": robustness_status_ok,
        "primary_robustness_gates_all_true": gates_all_true,
        "forbidden_action_flags_false": forbidden_ok,
        "strategy_allowed_false": True,
        "signal_allowed_false": True,
        "candidate_generation_allowed_false": True,
        "release_allowed_false": True,
        "runtime_live_capital_false": True,
        "artifacts_data_builds_not_written": True,
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
        "input_artifacts_found": input_artifacts_found,
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": input_unchanged,
        "input_payload_hashes_verified": payload_hashes,
        "research_chain_summary": research_chain,
        "primary_finding_summary": primary_summary,
        "robustness_gate_summary": {
            "primary_robustness_gates": gates,
            "all_primary_gates_true": gates_all_true,
            "failed_robustness_gates": robustness.get("failed_robustness_gates", []),
            "leave_one_symbol_passed": gates.get("leave_one_symbol_no_single_symbol_necessary") is True,
            "leave_one_month_passed": gates.get("leave_one_month_no_single_month_necessary") is True,
            "arbusdt_exclusion_passed": gates.get("arbusdt_exclusion_direction_preserved") is True
            and gates.get("arbusdt_exclusion_magnitude_ratio_gte_0_50") is True,
            "month_aware_symbol_balanced_passed": gates.get("month_aware_symbol_balanced_null_fdr_q_lte_0_05") is True,
            "bonferroni_passed": gates.get("bonferroni_lte_0_05") is True,
        },
        "direction_semantics_status": direction_status,
        "suggested_neutral_diagnostic_label": suggested_label,
        "direction_semantics_note": direction_note,
        "remaining_limitations": build_remaining_limitations(kline),
        "final_decision": final_decision,
        "diagnostic_route_promising": diagnostic_route_promising,
        "independent_validation_required": independent_validation_required,
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
    print(f"primary_finding_summary: {artifact['primary_finding_summary']}")
    print(f"robustness_gate_summary: {artifact['robustness_gate_summary']}")
    print(f"direction_semantics_status: {artifact['direction_semantics_status']}")
    print(f"suggested_neutral_diagnostic_label: {artifact['suggested_neutral_diagnostic_label']}")
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
    hashes_after = None
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
