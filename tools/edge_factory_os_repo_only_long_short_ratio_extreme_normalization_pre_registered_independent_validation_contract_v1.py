#!/usr/bin/env python
"""Pre-registration contract for long-short ratio normalization validation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_V1"
MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_"
    "pre_registered_independent_validation_contract_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/contracts/long_short_ratio_extreme_normalization_"
    "pre_registered_independent_validation_contract_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "4b4a036fca5c719ddaa7718871b64d7c88096835"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_EVALUATOR_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_volatility_robustness_evaluator_v1.json"
)
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
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_EVALUATOR_RELATIVE_PATH,
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_VALIDATOR_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
]

CONTRACT_STATUS_PASS = (
    "PASS_REPO_ONLY_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_CREATED"
)
CONTRACT_STATUS_BLOCKED = (
    "BLOCKED_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT"
)
ARTIFACT_KIND = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT"

RESULT_READY = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY"
RESULT_ATTENTION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_REQUIRES_ATTENTION"
)
RESULT_FAILED = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_FAILED_STOP"

EXPECTED_EVALUATOR_CLASSIFICATION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_PROMISING_DIAGNOSTIC_ONLY"
)
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

THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"
NEXT_VALIDATION_RUNNER = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER_V1"
)
NEXT_CONTRACT_REVIEW = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_REVIEW_V1"
)

RESEARCH_SAMPLE_WINDOW = {
    "start": "2023-01-01",
    "end": "2025-12-31",
    "timezone": "UTC",
    "usage": "research_evaluation_and_robustness_only_not_independent_validation",
}

PRIMARY_EVENT = {
    "event_id": "optional_account_position_divergence_resolution_candidate",
    "event_label": "account/position divergence resolution",
    "research_sample_event_count": 947,
}

PRIMARY_TARGETS = [
    {
        **PRIMARY_EVENT,
        "horizon": "15m",
        "research_sample_mean_abs_return": 0.004701931375964501,
        "prior_p_abs_high_mean": 0.000999000999000999,
        "prior_fdr_q": 0.000999000999000999,
        "prior_bonferroni_p": 0.002997002997002997,
    },
    {
        **PRIMARY_EVENT,
        "horizon": "1h",
        "research_sample_mean_abs_return": 0.008151963600828729,
        "prior_p_abs_high_mean": 0.000999000999000999,
        "prior_fdr_q": 0.000999000999000999,
        "prior_bonferroni_p": 0.002997002997002997,
    },
    {
        **PRIMARY_EVENT,
        "horizon": "4h",
        "research_sample_mean_abs_return": 0.015145698846520991,
        "prior_p_abs_high_mean": 0.000999000999000999,
        "prior_fdr_q": 0.000999000999000999,
        "prior_bonferroni_p": 0.002997002997002997,
    },
]


class ContractBlocked(Exception):
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


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise ContractBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise ContractBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    evaluator = read_json_readonly(SOURCE_EVALUATOR_RELATIVE_PATH)
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    validator = read_json_readonly(SOURCE_VALIDATOR_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_EVALUATOR_RELATIVE_PATH: verify_payload_hash(evaluator, "volatility robustness evaluator"),
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "volatility robustness runner"),
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "forward diagnostic"),
        SOURCE_VALIDATOR_RELATIVE_PATH: verify_payload_hash(validator, "event validator"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "event discovery"),
    }
    return evaluator, robustness, diagnostic, validator, discovery, payload_hashes


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


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_validation_outcomes": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "validation_run": False,
        "new_returns_computed": False,
        "p_values_recomputed": False,
        "null_validation_rerun": False,
        "event_definitions_modified": False,
        "threshold_changes": False,
        "ratio_source_changes": False,
        "normalization_strength_changes": False,
        "cooldown_changes": False,
        "persistence_break_tier_promoted": False,
        "signed_return_findings_promoted": False,
        "prior_artifacts_modified": False,
        "prior_artifacts_renamed": False,
        "history_rewritten": False,
    }


def input_integrity_checks(
    evaluator: dict[str, Any],
    robustness: dict[str, Any],
    diagnostic: dict[str, Any],
    validator: dict[str, Any],
    discovery: dict[str, Any],
) -> dict[str, bool]:
    return {
        "evaluator_promising_diagnostic_only": evaluator.get("result_classification")
        == EXPECTED_EVALUATOR_CLASSIFICATION,
        "diagnostic_route_promising_true": evaluator.get("diagnostic_route_promising") is True,
        "independent_validation_required_true": evaluator.get("independent_validation_required") is True,
        "evaluator_strategy_false": evaluator.get("strategy_allowed") is False,
        "evaluator_signal_false": evaluator.get("signal_allowed") is False,
        "evaluator_candidate_generation_false": evaluator.get("candidate_generation_allowed") is False,
        "evaluator_release_false": evaluator.get("release_allowed") is False,
        "robustness_promising": robustness.get("result_classification") == EXPECTED_ROBUSTNESS_CLASSIFICATION,
        "robustness_failed_gates_empty": robustness.get("failed_robustness_gates") == [],
        "diagnostic_promising_volatility_only": diagnostic.get("result_classification") == EXPECTED_DIAGNOSTIC_CLASSIFICATION,
        "validator_passed": validator.get("result_classification") in EXPECTED_VALIDATOR_CLASSIFICATIONS,
        "discovery_ready": discovery.get("result_classification") == EXPECTED_DISCOVERY_CLASSIFICATION,
        "forbidden_flags_false": all(
            artifact_forbidden_flags_ok(artifact)
            for artifact in [evaluator, robustness, diagnostic, validator, discovery]
            if "forbidden_actions_confirmed_false" in artifact
        ),
        "permissions_false": all(
            artifact_permissions_false(artifact)
            for artifact in [evaluator, robustness, diagnostic, validator]
        ),
    }


def frozen_hypothesis() -> dict[str, Any]:
    return {
        "diagnostic_family": THEORY_ID,
        "primary_event": PRIMARY_EVENT,
        "event_count_in_research_sample": 947,
        "primary_metric_family": "forward_abs_return / realized-volatility proxy",
        "primary_horizons": ["15m", "1h", "4h"],
        "expected_direction": "future_absolute_return_or_realized_volatility_higher_than_null",
        "primary_null_model": "month-aware symbol-balanced null",
        "primary_p_value": "p_abs_high_mean",
        "primary_test_scope": "three_pre_registered_primary_volatility_tests",
        "primary_targets": PRIMARY_TARGETS,
        "signed_return_findings": {
            "role": "secondary_tracking_only",
            "pass_fail_allowed": False,
            "strategy_candidate_signal_allowed": False,
        },
    }


def frozen_event_definition_policy() -> dict[str, Any]:
    return {
        "source_of_truth": [SOURCE_DISCOVERY_RELATIVE_PATH, SOURCE_VALIDATOR_RELATIVE_PATH],
        "event_definition_must_be_reconstructed_exactly": True,
        "primary_event": "account/position divergence resolution",
        "primary_definition_id": "account_position_pair medium 1h cooldown 24h",
        "threshold_changes_allowed": False,
        "ratio_source_changes_allowed": False,
        "normalization_strength_changes_allowed": False,
        "cooldown_changes_allowed": False,
        "persistence_break_tier_promotion_allowed": False,
        "signed_return_promotion_allowed": False,
        "optimization_on_validation_data_allowed": False,
        "event_definition_edits_based_on_validation_outcomes_allowed": False,
        "event_reconstruction_uses_current_or_prior_observations_only": True,
    }


def independent_validation_data_policy() -> dict[str, Any]:
    return {
        "acceptable_independent_validation_sources": [
            "2026+ public Binance Data Vision data",
            "pre-frozen untouched symbol_or_universe_expansion",
            "both, only if frozen before inspecting validation outcomes",
        ],
        "research_evaluation_sample_window": RESEARCH_SAMPLE_WINDOW,
        "research_evaluation_sample_must_not_be_reused_as_independent_validation": True,
        "independent_validation_must_be_outside_or_untouched_relative_to_research_sample": True,
        "if_2026_plus_public_data_is_used": (
            "data acquisition and validation must happen in a separate future runner"
        ),
        "if_expansion_symbols_are_used": (
            "symbol list must be frozen before return or volatility computation"
        ),
        "private_account_api_key_order_data_allowed": False,
        "validation_outcome_inspection_before_freeze_allowed": False,
    }


def validation_gates() -> dict[str, Any]:
    return {
        "event_reconstruction_current_or_prior_observations_only": True,
        "input_hashes_must_be_unchanged": True,
        "public_archive_only": True,
        "private_account_api_key_order_data_allowed": False,
        "strategy_candidate_release_action_allowed": False,
        "sufficient_event_count_for_at_least_one_primary_horizon_required": True,
        "observed_primary_volatility_metric_higher_than_null_required": True,
        "p_abs_high_mean_lte_0_05_for_at_least_one_primary_horizon_required": True,
        "all_15m_1h_4h_targets_must_be_reported": True,
        "fdr_and_bonferroni_recorded_across_three_primary_tests": True,
        "leave_one_symbol_diagnostics_required_when_enough_events": True,
        "leave_one_month_diagnostics_required_when_enough_months": True,
        "single_symbol_or_month_dependence_must_be_absent_when_testable": True,
        "arbusdt_missing_archive_sensitivity_recorded_if_relevant": True,
        "alternate_volatility_proxy_sensitivity_recorded_when_feasible": True,
        "data_quality_warnings_recorded": True,
    }


def minimum_sample_rules() -> dict[str, Any]:
    return {
        "normal_evaluation_threshold": "primary_event_validation_event_count >= 100",
        "attention_or_inconclusive_band": "50 <= primary_event_validation_event_count <= 99",
        "attention_band_rule": "classify as attention/inconclusive unless effect and robustness are extremely clear; do not pass automatically",
        "inconclusive_insufficient_sample_threshold": "primary_event_validation_event_count < 50",
        "symbol_coverage_must_be_recorded": True,
        "month_coverage_must_be_recorded": True,
    }


def failure_rules() -> dict[str, Any]:
    return {
        "event_count_too_low": "inconclusive_or_fail_depending_on_severity",
        "volatility_effect_disappears": "fail",
        "p_abs_high_mean_fails": "fail",
        "data_quality_insufficient": "data_quality_attention_or_inconclusive",
        "event_reconstruction_not_reproducible": "failed_stop",
        "validation_data_inspected_or_optimized_before_freezing": "failed_stop",
        "forbidden_actions_occur": "failed_stop",
        "signed_return_only_result": "cannot_pass_primary_volatility_validation",
    }


def future_runner_scope() -> dict[str, Any]:
    return {
        "allowed_next_step": NEXT_VALIDATION_RUNNER,
        "may_evaluate_only_frozen_hypothesis": True,
        "may_create_strategy_logic": False,
        "may_create_signal_logic": False,
        "may_create_candidate_logic": False,
        "may_create_release_logic": False,
        "may_create_live_or_capital_logic": False,
        "may_change_event_definition": False,
        "may_change_thresholds_or_horizons": False,
        "may_promote_signed_return_findings": False,
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
        "theory_id": THEORY_ID,
        "frozen_hypothesis": {},
        "frozen_event_definition_policy": {},
        "independent_validation_data_policy": {},
        "validation_gates": {},
        "minimum_sample_rules": {},
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
        "allowed_next_step": NEXT_CONTRACT_REVIEW,
        "blocker": reason,
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
    evaluator, robustness, diagnostic, validator, discovery, payload_hashes = load_inputs()
    integrity = input_integrity_checks(evaluator, robustness, diagnostic, validator, discovery)
    if not all(integrity.values()):
        failed = [key for key, value in integrity.items() if value is not True]
        raise ContractBlocked(f"INPUT_INTEGRITY_CHECK_FAILED: {failed}")

    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise ContractBlocked("INPUT_ARTIFACT_HASH_CHANGED")

    validation_checks = {
        "input_artifact_hashes_unchanged": input_unchanged,
        "robustness_evaluator_promising": evaluator.get("result_classification") == EXPECTED_EVALUATOR_CLASSIFICATION,
        "diagnostic_route_promising": evaluator.get("diagnostic_route_promising") is True,
        "independent_validation_required": evaluator.get("independent_validation_required") is True,
        "strategy_allowed_false": True,
        "signal_allowed_false": True,
        "candidate_generation_allowed_false": True,
        "release_allowed_false": True,
        "runtime_live_capital_false": True,
        "no_validation_run": True,
        "no_new_returns_computed": True,
        "no_p_values_recomputed": True,
        "no_null_validation_rerun": True,
        "no_event_definitions_modified": True,
        "no_signed_return_promotion": True,
    }
    result_classification = RESULT_READY if all(validation_checks.values()) else RESULT_ATTENTION
    allowed_next_step = NEXT_VALIDATION_RUNNER if result_classification == RESULT_READY else NEXT_CONTRACT_REVIEW

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
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": input_unchanged,
        "input_payload_hashes_verified": payload_hashes,
        "input_integrity_checks": integrity,
        "theory_id": THEORY_ID,
        "frozen_hypothesis": frozen_hypothesis(),
        "frozen_event_definition_policy": frozen_event_definition_policy(),
        "independent_validation_data_policy": independent_validation_data_policy(),
        "validation_gates": validation_gates(),
        "minimum_sample_rules": minimum_sample_rules(),
        "failure_rules": failure_rules(),
        "future_runner_scope": future_runner_scope(),
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
    print(f"theory_id: {artifact['theory_id']}")
    print(f"frozen_hypothesis: {artifact['frozen_hypothesis']}")
    print(f"independent_validation_data_policy: {artifact['independent_validation_data_policy']}")
    print(f"validation_gates: {artifact['validation_gates']}")
    print(f"minimum_sample_rules: {artifact['minimum_sample_rules']}")
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
