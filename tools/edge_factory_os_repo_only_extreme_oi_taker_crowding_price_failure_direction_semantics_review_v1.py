#!/usr/bin/env python
"""Direction semantics and neutral relabel review for the refined price-failure diagnostic."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_direction_semantics_review_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_direction_semantics_review_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "bf2c17741888b738f5fe31990434c0ae4f12d7b5"

SOURCE_EVALUATOR_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_evaluator_v1.json"
SOURCE_ROBUSTNESS_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_runner_v1.json"
SOURCE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_diagnostic_v1.json"
SOURCE_REFINEMENT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_EVALUATOR_RELATIVE_PATH,
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
]

SEMANTICS_STATUS_PASS = "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_CREATED"
SEMANTICS_STATUS_BLOCKED = "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW"
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW"

RESULT_READY = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_RELABEL_READY"
RESULT_ATTENTION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_REQUIRES_MANUAL_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_FAILED_STOP"

NEXT_INDEPENDENT_VALIDATION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_V1"
APPROVED_NEUTRAL_LABEL = "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC"
OPTIONAL_ALIASES = [
    "SHORT_CORE_NEGATIVE_1H_DRIFT_DIAGNOSTIC",
    "SHORT_PRESSURE_CONTINUATION_AFTER_PRICE_FAILURE_DIAGNOSTIC",
]


class SemanticsReviewBlocked(Exception):
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
        raise SemanticsReviewBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
            raise SemanticsReviewBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise SemanticsReviewBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SemanticsReviewBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise SemanticsReviewBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    evaluator = read_json_readonly(SOURCE_EVALUATOR_RELATIVE_PATH)
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_EVALUATOR_RELATIVE_PATH: verify_payload_hash(evaluator, "robustness evaluator"),
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "robustness runner"),
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "forward-return diagnostic"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
    }
    return evaluator, robustness, diagnostic, refinement, payload_hashes


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
        "event_definition_changes": False,
        "threshold_changes": False,
        "forward_return_retesting": False,
        "p_value_recomputation": False,
        "null_rerun": False,
        "release_promotion": False,
    }


def validate_inputs(evaluator: dict[str, Any], robustness: dict[str, Any], diagnostic: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "evaluator_requires_direction_relabel": evaluator.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROBUSTNESS_EVALUATOR_REQUIRES_DIRECTION_RELABEL_ATTENTION",
        "diagnostic_route_promising_true": evaluator.get("diagnostic_route_promising") is True,
        "independent_validation_required_true": evaluator.get("independent_validation_required") is True,
        "strategy_allowed_false": evaluator.get("strategy_allowed") is False,
        "signal_allowed_false": evaluator.get("signal_allowed") is False,
        "candidate_generation_allowed_false": evaluator.get("candidate_generation_allowed") is False,
        "release_allowed_false": evaluator.get("release_allowed") is False,
        "robustness_promising": robustness.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY",
        "diagnostic_promising": diagnostic.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_PROMISING_DIAGNOSTIC_ONLY",
    }
    if not all(checks.values()):
        raise SemanticsReviewBlocked(f"input validation failed: {checks}")
    return checks


def blocked_artifact(reason: str, audit: dict[str, Any] | None = None, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "semantics_review_status": SEMANTICS_STATUS_BLOCKED,
        "status": SEMANTICS_STATUS_BLOCKED,
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
        "prior_evaluator_summary": {},
        "direction_semantics_issue": f"BLOCKED: {reason}",
        "direction_relabel_required": False,
        "approved_neutral_diagnostic_label": None,
        "optional_aliases": [],
        "mechanism_interpretation": {},
        "scope_lock": {},
        "independent_validation_required": True,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_BLOCKER_REVIEW_V1",
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
    evaluator, robustness, diagnostic, refinement, payload_hashes = load_inputs()
    input_checks = validate_inputs(evaluator, robustness, diagnostic)
    primary = evaluator.get("primary_finding_summary", {})
    robustness_gates = evaluator.get("robustness_gate_summary", {})
    direction_issue = {
        "previous_event_name": "short_core / short price failure",
        "observed_robust_effect": "negative 1h forward return",
        "observed_mean": primary.get("observed_mean"),
        "valid_count": primary.get("valid_count"),
        "old_label_risk": "The old short_core price-failure wording can imply a short squeeze or upward reversal, while the robust diagnostic effect is negative.",
        "neutral_label_needed": True,
    }
    mechanism = {
        "cautious_interpretation": "This may represent delayed downside continuation after extreme short-pressure and price-failure conditions.",
        "must_not_call_short_squeeze": True,
        "must_not_call_tradable_edge": True,
        "must_not_convert_to_signal_without_independent_validation": True,
        "expected_direction_for_future_contract": "negative",
        "frozen_horizon_for_future_contract": "short_core 1h",
    }
    scope_lock = {
        "event_definition_changes": False,
        "threshold_changes": False,
        "forward_return_retesting": False,
        "p_value_recomputation": False,
        "null_rerun": False,
        "optimization": False,
        "strategy_candidate_release_action": False,
        "prior_artifacts_modified": False,
        "prior_files_renamed": False,
        "history_rewritten": False,
    }
    next_validation_contract_requirements = {
        "freeze_neutral_diagnostic_label": APPROVED_NEUTRAL_LABEL,
        "freeze_event_definitions": True,
        "freeze_horizon": "short_core 1h",
        "freeze_expected_direction": "negative",
        "require_independent_holdout_or_prospective_validation": True,
        "prevent_strategy_candidate_release_action": True,
    }
    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise SemanticsReviewBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    validation_checks = {
        **input_checks,
        "input_artifact_hashes_unchanged": input_unchanged,
        "direction_relabel_required_true": True,
        "neutral_label_exact": APPROVED_NEUTRAL_LABEL == "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC",
        "scope_lock_all_false_for_actions": all(value is False for value in scope_lock.values()),
        "no_strategy_signal_candidate_release_permissions": True,
    }
    result_classification = RESULT_READY if all(validation_checks.values()) else RESULT_ATTENTION
    allowed_next_step = NEXT_INDEPENDENT_VALIDATION if result_classification == RESULT_READY else "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_MANUAL_REVIEW_V1"
    artifact = {
        "semantics_review_status": SEMANTICS_STATUS_PASS,
        "status": SEMANTICS_STATUS_PASS,
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
        "prior_evaluator_summary": {
            "status": evaluator.get("evaluator_status"),
            "result_classification": evaluator.get("result_classification"),
            "diagnostic_route_promising": evaluator.get("diagnostic_route_promising"),
            "independent_validation_required": evaluator.get("independent_validation_required"),
            "primary_finding_summary": primary,
            "robustness_gate_summary": robustness_gates,
            "direction_semantics_status": evaluator.get("direction_semantics_status"),
            "suggested_neutral_diagnostic_label": evaluator.get("suggested_neutral_diagnostic_label"),
        },
        "direction_semantics_issue": direction_issue,
        "direction_relabel_required": True,
        "approved_neutral_diagnostic_label": APPROVED_NEUTRAL_LABEL,
        "optional_aliases": OPTIONAL_ALIASES,
        "mechanism_interpretation": mechanism,
        "scope_lock": scope_lock,
        "next_validation_contract_requirements": next_validation_contract_requirements,
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
    print(f"status: {artifact['semantics_review_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"direction_relabel_required: {bool_text(bool(artifact['direction_relabel_required']))}")
    print(f"approved_neutral_diagnostic_label: {artifact['approved_neutral_diagnostic_label']}")
    print(f"optional_aliases: {artifact['optional_aliases']}")
    print(f"mechanism_interpretation: {artifact['mechanism_interpretation']}")
    print(f"scope_lock: {artifact['scope_lock']}")
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
        return 0 if artifact["semantics_review_status"] == SEMANTICS_STATUS_PASS else 1
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
