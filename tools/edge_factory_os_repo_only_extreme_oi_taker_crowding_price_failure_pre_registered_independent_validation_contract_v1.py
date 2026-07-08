#!/usr/bin/env python
"""Pre-registration contract for independent validation of the neutral price-failure diagnostic."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_V1"
MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_contract_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/contracts/extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_contract_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "2f0c61e13a8dd99061ba11fb93b030916e949940"

SOURCE_SEMANTICS_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_direction_semantics_review_v1.json"
)
SOURCE_EVALUATOR_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_evaluator_v1.json"
)
SOURCE_ROBUSTNESS_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_runner_v1.json"
)
SOURCE_DIAGNOSTIC_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_diagnostic_v1.json"
)
SOURCE_REFINEMENT_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
)
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_SEMANTICS_RELATIVE_PATH,
    SOURCE_EVALUATOR_RELATIVE_PATH,
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
]

CONTRACT_STATUS_PASS = (
    "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_CREATED"
)
CONTRACT_STATUS_BLOCKED = (
    "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT"
)
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT"

RESULT_READY = (
    "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY"
)
RESULT_ATTENTION = (
    "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_REQUIRES_ATTENTION"
)
RESULT_FAILED = (
    "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_FAILED_STOP"
)

APPROVED_NEUTRAL_LABEL = "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC"
NEXT_VALIDATION_RUNNER = (
    "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER_V1"
)
NEXT_BLOCKER_REVIEW = (
    "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_REVIEW_V1"
)

RESEARCH_SAMPLE_WINDOW = {
    "start": "2023-01-01",
    "end": "2025-12-31",
    "timezone": "UTC",
    "usage": "research_and_evaluation_only_not_independent_validation_result",
}


class ContractBlocked(Exception):
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
        raise ContractBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
            raise ContractBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise ContractBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ContractBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise ContractBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    semantics = read_json_readonly(SOURCE_SEMANTICS_RELATIVE_PATH)
    evaluator = read_json_readonly(SOURCE_EVALUATOR_RELATIVE_PATH)
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_SEMANTICS_RELATIVE_PATH: verify_payload_hash(semantics, "direction semantics review"),
        SOURCE_EVALUATOR_RELATIVE_PATH: verify_payload_hash(evaluator, "robustness evaluator"),
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "robustness runner"),
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "forward-return diagnostic"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
    }
    return semantics, evaluator, robustness, diagnostic, refinement, payload_hashes


def all_forbidden_false(*artifacts: dict[str, Any]) -> bool:
    for artifact in artifacts:
        flags = artifact.get("forbidden_actions_confirmed_false", {})
        if not isinstance(flags, dict):
            return False
        if any(value is not False for value in flags.values()):
            return False
    return True


def explicit_permissions_false(*artifacts: dict[str, Any]) -> bool:
    keys = [
        "strategy_allowed",
        "signal_allowed",
        "candidate_generation_allowed",
        "release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "live_allowed",
    ]
    for artifact in artifacts:
        for key in keys:
            if key in artifact and artifact.get(key) is not False:
                return False
    return True


def selected_short_core(refinement: dict[str, Any]) -> dict[str, Any]:
    selected = refinement.get("selected_clean_event_definitions", [])
    if not isinstance(selected, list):
        raise ContractBlocked("refinement selected_clean_event_definitions is not a list")
    for item in selected:
        if not isinstance(item, dict):
            continue
        if item.get("selection_slot") == "best_short_failure_definition":
            return item
    raise ContractBlocked("missing best_short_failure_definition in refinement artifact")


def validate_inputs(
    semantics: dict[str, Any],
    evaluator: dict[str, Any],
    robustness: dict[str, Any],
    diagnostic: dict[str, Any],
    refinement: dict[str, Any],
) -> dict[str, bool]:
    short_core = selected_short_core(refinement)
    primary_finding = robustness.get("primary_finding", {})
    evaluator_primary = evaluator.get("primary_finding_summary", {})
    gates = robustness.get("primary_robustness_gates", {})
    checks = {
        "semantics_review_relabel_ready": semantics.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_RELABEL_READY",
        "approved_neutral_label_exact": semantics.get("approved_neutral_diagnostic_label") == APPROVED_NEUTRAL_LABEL,
        "semantics_independent_validation_required_true": semantics.get("independent_validation_required") is True,
        "semantics_strategy_allowed_false": semantics.get("strategy_allowed") is False,
        "semantics_signal_allowed_false": semantics.get("signal_allowed") is False,
        "semantics_candidate_generation_allowed_false": semantics.get("candidate_generation_allowed") is False,
        "semantics_release_allowed_false": semantics.get("release_allowed") is False,
        "semantics_scope_lock_no_event_definition_changes": semantics.get("scope_lock", {}).get("event_definition_changes") is False,
        "semantics_scope_lock_no_threshold_changes": semantics.get("scope_lock", {}).get("threshold_changes") is False,
        "semantics_scope_lock_no_return_retesting": semantics.get("scope_lock", {}).get("forward_return_retesting") is False,
        "semantics_scope_lock_no_p_value_recomputation": semantics.get("scope_lock", {}).get("p_value_recomputation") is False,
        "semantics_scope_lock_no_null_rerun": semantics.get("scope_lock", {}).get("null_rerun") is False,
        "evaluator_requires_direction_relabel_attention": evaluator.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROBUSTNESS_EVALUATOR_REQUIRES_DIRECTION_RELABEL_ATTENTION",
        "evaluator_diagnostic_route_promising_true": evaluator.get("diagnostic_route_promising") is True,
        "evaluator_independent_validation_required_true": evaluator.get("independent_validation_required") is True,
        "robustness_promising": robustness.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY",
        "robustness_failed_gates_empty": robustness.get("failed_robustness_gates") == [],
        "robustness_primary_gates_all_true": isinstance(gates, dict) and all(value is True for value in gates.values()),
        "diagnostic_promising": diagnostic.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_PROMISING_DIAGNOSTIC_ONLY",
        "diagnostic_short_core_count_451": diagnostic.get("short_core_event_count") == 451,
        "diagnostic_long_core_count_463": diagnostic.get("long_core_event_count") == 463,
        "diagnostic_strategy_allowed_false": diagnostic.get("strategy_allowed") is False,
        "diagnostic_signal_allowed_false": diagnostic.get("signal_allowed") is False,
        "diagnostic_candidate_generation_allowed_false": diagnostic.get("candidate_generation_allowed") is False,
        "diagnostic_release_allowed_false": diagnostic.get("release_allowed") is False,
        "short_core_refinement_count_451": short_core.get("cooldown_filtered_count") == 451,
        "short_core_refinement_symbols_10": short_core.get("symbol_coverage_count") == 10,
        "short_core_refinement_months_36": short_core.get("month_coverage_count") == 36,
        "short_core_missing_components_zero": short_core.get("missing_component_count") == 0,
        "primary_finding_side_short_core": primary_finding.get("side") == "short_core",
        "primary_finding_horizon_1h": primary_finding.get("horizon") == "1h",
        "primary_finding_valid_451": primary_finding.get("valid_forward_return_count") == 451,
        "primary_finding_mean_negative": isinstance(primary_finding.get("mean"), (int, float))
        and primary_finding.get("mean") < 0,
        "primary_finding_fdr_lte_0_01": isinstance(primary_finding.get("fdr_q"), (int, float))
        and primary_finding.get("fdr_q") <= 0.01,
        "primary_finding_bonferroni_lte_0_01": isinstance(primary_finding.get("bonferroni_p"), (int, float))
        and primary_finding.get("bonferroni_p") <= 0.01,
        "evaluator_primary_all_gates_true": evaluator_primary.get("all_robustness_gates_true") is True,
        "forbidden_action_flags_false": all_forbidden_false(semantics, evaluator, robustness, diagnostic, refinement),
        "explicit_permission_flags_false": explicit_permissions_false(semantics, evaluator, robustness, diagnostic),
    }
    return checks


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_validation_returns": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "independent_validation_run": False,
        "new_return_computation": False,
        "p_value_recomputation": False,
        "null_validation_rerun": False,
        "event_definition_changes": False,
        "threshold_changes": False,
        "prior_artifact_modification": False,
        "artifact_rename": False,
        "history_rewrite": False,
        "release_promotion": False,
    }


def build_frozen_hypothesis(robustness: dict[str, Any], diagnostic: dict[str, Any]) -> dict[str, Any]:
    primary = robustness.get("primary_finding", {})
    month_aware = robustness.get("month_aware_symbol_balanced_null_summary", {}).get("primary_short_core_1h", {})
    observed = diagnostic.get("observed_stats_by_side_and_horizon", {}).get("short_core", {}).get("1h", {})
    return {
        "diagnostic_label": APPROVED_NEUTRAL_LABEL,
        "event_side": "short_core",
        "research_sample_event_count": 451,
        "horizon": "1h",
        "expected_direction": "negative",
        "primary_statistic": "mean_1h_close_to_close_forward_return",
        "primary_null_model_for_validation": "month_aware_symbol_balanced_null",
        "primary_multiple_comparison_scope": "single_pre_registered_primary_test",
        "research_sample_observed_mean": primary.get("mean", observed.get("mean")),
        "research_sample_valid_count": primary.get("valid_forward_return_count", observed.get("valid_forward_return_count")),
        "research_sample_prior_raw_p": primary.get("raw_p"),
        "research_sample_prior_fdr_q": primary.get("fdr_q"),
        "research_sample_prior_bonferroni": primary.get("bonferroni_p"),
        "research_sample_month_aware_fdr_q": month_aware.get("fdr_q"),
        "research_sample_month_aware_bonferroni": month_aware.get("bonferroni_p"),
        "research_sample_month_aware_p_negative_mean": month_aware.get("p_values", {}).get("p_negative_mean"),
        "secondary_tracked_diagnostics": [
            {
                "side": "long_core",
                "horizon": "4h",
                "role": "exploratory_non_primary_record_only",
                "pass_fail_allowed": False,
            },
            {
                "side": "long_core",
                "horizon": "24h",
                "role": "exploratory_non_primary_record_only",
                "pass_fail_allowed": False,
            },
        ],
    }


def build_frozen_event_definition_policy(refinement: dict[str, Any]) -> dict[str, Any]:
    short_core = selected_short_core(refinement)
    return {
        "source_artifact": SOURCE_REFINEMENT_RELATIVE_PATH,
        "source_definition_id": short_core.get("definition_id"),
        "source_selection_slot": short_core.get("selection_slot"),
        "source_meta": short_core.get("meta"),
        "frozen_event_side": "short_core",
        "frozen_cooldown_filtered_count_in_research_sample": short_core.get("cooldown_filtered_count"),
        "no_threshold_changes": True,
        "no_price_failure_rule_changes": True,
        "no_oi_taker_rule_changes": True,
        "no_crowding_confirmation_promotion": True,
        "no_optimization_on_validation_data": True,
        "no_event_definition_edits_based_on_validation_outcomes": True,
        "event_reconstruction_uses_current_or_prior_bar_data_only": True,
        "sparse_crowding_confirmed_variants_are_not_primary": True,
    }


def build_independent_validation_data_policy() -> dict[str, Any]:
    return {
        "research_evaluation_sample_must_not_be_reused_as_independent_result": True,
        "research_evaluation_sample_window": RESEARCH_SAMPLE_WINDOW,
        "independent_validation_must_be_outside_or_untouched_relative_to_research_sample": True,
        "acceptable_independent_validation_sources": [
            {
                "source": "future_or_prospective_public_binance_data_vision",
                "allowed": True,
                "window_rule": "must be after the 2023-01-01 through 2025-12-31 research/evaluation window",
                "runner_requirement": "data acquisition and validation must happen in a separate future runner",
            },
            {
                "source": "untouched_exchange_or_symbol_universe_expansion",
                "allowed": True,
                "freeze_rule": "exchange/symbol universe and symbol list must be registered before inspection or return computation",
            },
            {
                "source": "both_future_public_data_and_frozen_expansion_symbols",
                "allowed": True,
                "freeze_rule": "all windows and symbols must be frozen before validation return computation",
            },
        ],
        "forbidden_independent_validation_sources": [
            "current_2023_2025_research_evaluation_sample_as_final_validation_result",
            "any data inspected or optimized before freeze",
            "private_account_api_key_order_or_live_data",
        ],
        "if_2026_plus_public_data_is_used": "build/acquire/validate in the future runner only",
        "if_expansion_symbols_are_used": "freeze symbol list before return computation",
    }


def build_validation_gates() -> dict[str, Any]:
    return {
        "event_reconstruction_current_or_prior_bar_only": True,
        "input_hashes_must_remain_unchanged": True,
        "public_archive_only_no_private_account_api_key_order_data": True,
        "no_strategy_candidate_release_action": True,
        "minimum_event_count_threshold": {
            "required": True,
            "minimum_recommended_events": 100,
            "preferred_events": 300,
            "decision": "below minimum is inconclusive unless explicitly approved before inspection",
        },
        "primary_observed_mean_must_be_negative": True,
        "primary_null_model": "month_aware_symbol_balanced_null",
        "primary_null_gate": {
            "p_negative_mean_lte": 0.05,
            "applies_to": "short_core 1h only",
        },
        "multiple_comparison_policy": {
            "primary_test_scope": "single_pre_registered_primary_test",
            "record_fdr_and_bonferroni": True,
            "secondary_diagnostics_do_not_affect_pass_fail": True,
        },
        "leave_one_symbol_month_diagnostics": {
            "required_when_enough_events_exist": True,
            "single_symbol_or_month_dependence_must_be_absent": True,
        },
        "arbusdt_missing_archive_sensitivity": {
            "record_if_arbusdt_present": True,
            "must_not_hide_missing_archive_warning": True,
        },
        "data_quality_warnings_must_be_recorded": True,
    }


def build_failure_rules() -> dict[str, Any]:
    return {
        "fail_or_inconclusive_if_event_count_too_low": True,
        "fail_if_primary_direction_reverses": True,
        "fail_if_month_aware_symbol_balanced_p_negative_mean_gt_0_05": True,
        "fail_or_inconclusive_if_data_quality_insufficient": True,
        "fail_if_event_reconstruction_cannot_be_reproduced": True,
        "fail_if_validation_data_was_inspected_or_optimized_before_freeze": True,
        "fail_if_forbidden_actions_occur": True,
        "forbidden_actions": [
            "strategy",
            "signal",
            "backtest",
            "pnl",
            "trade_simulation",
            "optimization_against_validation_returns",
            "candidate_generation",
            "edge_claim",
            "release",
            "runtime_live_capital",
            "order_private_account_api_key",
        ],
    }


def build_future_runner_scope() -> dict[str, Any]:
    return {
        "allowed_next_step": NEXT_VALIDATION_RUNNER,
        "runner_may_only_evaluate_frozen_hypothesis": True,
        "runner_may_not_create_strategy_logic": True,
        "runner_may_not_change_event_definition": True,
        "runner_may_not_optimize_on_validation_returns": True,
        "runner_may_not_authorize_candidate_release_live_or_capital_actions": True,
        "required_primary_test": {
            "label": APPROVED_NEUTRAL_LABEL,
            "side": "short_core",
            "horizon": "1h",
            "expected_direction": "negative",
            "statistic": "mean_1h_close_to_close_forward_return",
            "null_model": "month_aware_symbol_balanced_null",
        },
    }


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
        "contract_status": CONTRACT_STATUS_BLOCKED,
        "status": CONTRACT_STATUS_BLOCKED,
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
        "approved_neutral_diagnostic_label": None,
        "frozen_hypothesis": {},
        "frozen_event_definition_policy": {},
        "independent_validation_data_policy": {},
        "validation_gates": {},
        "failure_rules": {},
        "future_runner_scope": {},
        "research_sample_window": RESEARCH_SAMPLE_WINDOW,
        "independent_validation_required": True,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_BLOCKER_REVIEW,
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
    semantics, evaluator, robustness, diagnostic, refinement, payload_hashes = load_inputs()
    input_artifacts_found = {relative_path: (REPO_ROOT / relative_path).exists() for relative_path in INPUT_ARTIFACT_RELATIVE_PATHS}
    input_checks = validate_inputs(semantics, evaluator, robustness, diagnostic, refinement)

    frozen_hypothesis = build_frozen_hypothesis(robustness, diagnostic)
    frozen_event_definition_policy = build_frozen_event_definition_policy(refinement)
    independent_validation_data_policy = build_independent_validation_data_policy()
    validation_gates = build_validation_gates()
    failure_rules = build_failure_rules()
    future_runner_scope = build_future_runner_scope()

    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise ContractBlocked("INPUT_ARTIFACT_HASH_CHANGED")

    validation_checks = {
        **input_checks,
        "input_artifacts_found": all(input_artifacts_found.values()),
        "input_artifact_hashes_unchanged": input_unchanged,
        "approved_label_frozen": frozen_hypothesis.get("diagnostic_label") == APPROVED_NEUTRAL_LABEL,
        "event_side_short_core_only": frozen_hypothesis.get("event_side") == "short_core",
        "horizon_1h_only": frozen_hypothesis.get("horizon") == "1h",
        "expected_direction_negative": frozen_hypothesis.get("expected_direction") == "negative",
        "single_pre_registered_primary_test": frozen_hypothesis.get("primary_multiple_comparison_scope")
        == "single_pre_registered_primary_test",
        "research_sample_window_frozen": RESEARCH_SAMPLE_WINDOW["start"] == "2023-01-01"
        and RESEARCH_SAMPLE_WINDOW["end"] == "2025-12-31",
        "validation_data_policy_excludes_reuse": independent_validation_data_policy[
            "research_evaluation_sample_must_not_be_reused_as_independent_result"
        ]
        is True,
        "future_runner_scope_no_strategy_logic": future_runner_scope["runner_may_not_create_strategy_logic"] is True,
    }
    result_classification = RESULT_READY if all(validation_checks.values()) else RESULT_ATTENTION
    allowed_next_step = NEXT_VALIDATION_RUNNER if result_classification == RESULT_READY else NEXT_BLOCKER_REVIEW
    artifact = {
        "contract_status": CONTRACT_STATUS_PASS,
        "status": CONTRACT_STATUS_PASS,
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
        "approved_neutral_diagnostic_label": APPROVED_NEUTRAL_LABEL,
        "frozen_hypothesis": frozen_hypothesis,
        "frozen_event_definition_policy": frozen_event_definition_policy,
        "independent_validation_data_policy": independent_validation_data_policy,
        "validation_gates": validation_gates,
        "failure_rules": failure_rules,
        "future_runner_scope": future_runner_scope,
        "research_sample_window": RESEARCH_SAMPLE_WINDOW,
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
    print(f"status: {artifact['contract_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"approved_neutral_diagnostic_label: {artifact['approved_neutral_diagnostic_label']}")
    print(f"frozen_hypothesis: {artifact['frozen_hypothesis']}")
    print(f"independent_validation_data_policy: {artifact['independent_validation_data_policy']}")
    print(f"validation_gates: {artifact['validation_gates']}")
    print(f"failure_rules: {artifact['failure_rules']}")
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
        return 0 if artifact["contract_status"] == CONTRACT_STATUS_PASS else 1
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
