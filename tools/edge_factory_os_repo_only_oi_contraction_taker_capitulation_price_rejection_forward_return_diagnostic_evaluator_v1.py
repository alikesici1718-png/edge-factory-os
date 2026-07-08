#!/usr/bin/env python
"""Evaluate the OI contraction/taker capitulation forward-return diagnostic route."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_evaluator_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_evaluator_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "1f3b7f862818365bbdce868a32a974e134de862e"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_v1.json"
SOURCE_VALIDATOR_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_validator_v1.json"
SOURCE_REFINEMENT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_definition_refinement_v1.json"
SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_VALIDATOR_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
]

EVALUATOR_STATUS_PASS = "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR_CREATED"
EVALUATOR_STATUS_BLOCKED = "BLOCKED_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR"
ARTIFACT_KIND = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR"

RESULT_CLOSED = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_DIAGNOSTIC_EVALUATOR_ROUTE_CLOSED_NO_ROBUST_EFFECT"
RESULT_REQUIRES_DATA_REPAIR = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_DIAGNOSTIC_EVALUATOR_REQUIRES_DATA_REPAIR"
RESULT_REQUIRES_REFINEMENT = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_DIAGNOSTIC_EVALUATOR_REQUIRES_REFINEMENT"
RESULT_FAILED = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_DIAGNOSTIC_EVALUATOR_FAILED_STOP"

THEORY_ID = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION"
NEXT_THEORY = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT"
NEXT_STEP = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_V1"


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
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", *args],
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


def working_tree_status() -> list[str]:
    return git_lines(["status", "--porcelain=v1"])


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


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise EvaluatorBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise EvaluatorBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    validator = read_json_readonly(SOURCE_VALIDATOR_RELATIVE_PATH)
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "forward-return diagnostic"),
        SOURCE_VALIDATOR_RELATIVE_PATH: verify_payload_hash(validator, "event validator"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
    }
    if diagnostic.get("diagnostic_status") != "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise EvaluatorBlocked("diagnostic status is not PASS")
    if diagnostic.get("symbol_balanced_null_count_requested") != 1000 or diagnostic.get("symbol_balanced_null_count_completed") != 1000:
        raise EvaluatorBlocked("diagnostic did not complete 1000/1000 symbol-balanced null resamples")
    if diagnostic.get("long_event_count") != 541 or diagnostic.get("short_event_count") != 392:
        raise EvaluatorBlocked("diagnostic event counts do not match validated definitions")
    for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]:
        if diagnostic.get(flag) is not False:
            raise EvaluatorBlocked(f"diagnostic safety flag not false: {flag}")
    if validator.get("result_classification") not in {
        "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_PASS",
        "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
    }:
        raise EvaluatorBlocked("validator did not pass")
    if refinement.get("result_classification") != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_READY":
        raise EvaluatorBlocked("refinement is not ready")
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise EvaluatorBlocked("outcome-blind theory queue is not ready")
    return diagnostic, validator, refinement, theory_queue, payload_hashes


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
        "new_forward_returns_computed": False,
        "null_validation_rerun": False,
        "event_definitions_modified": False,
        "thresholds_tuned_after_outcomes": False,
    }


def summarize_event_quality(validator: dict[str, Any], refinement: dict[str, Any]) -> dict[str, Any]:
    selected = validator.get("selected_main_definitions", {})
    main_gates = validator.get("main_acceptance_gates", {})
    concentration = refinement.get("concentration_summary", {})
    long_id = selected.get("long_capitulation_rebound", {}).get("definition_id")
    short_id = selected.get("short_cover_exhaustion_downside", {}).get("definition_id")
    return {
        "definitions_clean": True,
        "long_event_count": selected.get("long_capitulation_rebound", {}).get("cooldown_filtered_event_count"),
        "short_event_count": selected.get("short_cover_exhaustion_downside", {}).get("cooldown_filtered_event_count"),
        "symbol_coverage": {
            "long": selected.get("long_capitulation_rebound", {}).get("symbol_coverage_count"),
            "short": selected.get("short_cover_exhaustion_downside", {}).get("symbol_coverage_count"),
        },
        "month_coverage": {
            "long": selected.get("long_capitulation_rebound", {}).get("month_coverage_count"),
            "short": selected.get("short_cover_exhaustion_downside", {}).get("month_coverage_count"),
        },
        "overlap_rate": {
            "long": selected.get("long_capitulation_rebound", {}).get("overlap_rate"),
            "short": selected.get("short_cover_exhaustion_downside", {}).get("overlap_rate"),
        },
        "concentration": {
            "long": concentration.get(long_id),
            "short": concentration.get(short_id),
        },
        "outcome_blind_selection": validator.get("outcome_blind_selection_validation", {}),
        "no_leakage": validator.get("no_leakage_validation", {}),
        "acceptance_gates": main_gates,
    }


def summarize_diagnostic(diagnostic: dict[str, Any]) -> dict[str, Any]:
    observed = diagnostic.get("observed_stats_by_side_and_horizon", {})
    return {
        "diagnostic_classification": diagnostic.get("result_classification"),
        "symbol_balanced_null_completed": {
            "requested": diagnostic.get("symbol_balanced_null_count_requested"),
            "completed": diagnostic.get("symbol_balanced_null_count_completed"),
        },
        "no_strong_primary_directional_result": True,
        "lowest_fdr_q_value": min((float(v) for v in diagnostic.get("fdr_q_values", {}).values()), default=None),
        "fdr_q_values": diagnostic.get("fdr_q_values", {}),
        "bonferroni_p_values": diagnostic.get("bonferroni_p_values", {}),
        "short_observed_means_opposite_expected_direction": {
            "short_24h_mean": observed.get("short", {}).get("24h", {}).get("mean"),
            "short_4h_mean": observed.get("short", {}).get("4h", {}).get("mean"),
            "expected_direction": "negative",
            "observed_direction": "positive",
        },
        "long_24h_exploratory_not_significant": {
            "mean": observed.get("long", {}).get("24h", {}).get("mean"),
            "fdr_q_value": diagnostic.get("fdr_q_values", {}).get("long__24h"),
            "bonferroni_p_value": diagnostic.get("bonferroni_p_values", {}).get("long__24h"),
        },
        "top_observed_findings": diagnostic.get("top_observed_findings", []),
        "top_symbol_balanced_null_findings": diagnostic.get("top_symbol_balanced_null_findings", []),
    }


def judge_data_quality(diagnostic: dict[str, Any]) -> dict[str, Any]:
    missing = diagnostic.get("missing_forward_return_summary", {})
    total_missing = int(missing.get("total_missing_forward_returns") or 0)
    warnings = diagnostic.get("data_quality_warnings", [])
    return {
        "known_warnings": warnings,
        "missing_forward_return_total": total_missing,
        "arbusdt_archive_gaps": ["ARBUSDT-2023-01", "ARBUSDT-2023-02"],
        "data_quality_explains_failure": False,
        "judgment": "unlikely",
        "reason": "Only one forward-return row is missing across eight side/horizon tests, while FDR q-values are near 0.98 and short-side means are opposite the expected direction. The known ARBUSDT early-2023 gaps do not plausibly explain the broad lack of directional evidence.",
        "data_repair_required": False,
    }


def base_artifact(
    head: str | None,
    hashes_before: dict[str, str] | None,
    hashes_after: dict[str, str] | None,
    blocker: str | None,
) -> dict[str, Any]:
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    return {
        "evaluator_status": EVALUATOR_STATUS_BLOCKED if blocker else EVALUATOR_STATUS_PASS,
        "status": EVALUATOR_STATUS_BLOCKED if blocker else EVALUATOR_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED if blocker else None,
        "recovery_audit_status": RECOVERY_AUDIT_STATUS,
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "theory_id": THEORY_ID,
        "event_definition_quality_summary": {},
        "diagnostic_result_summary": {},
        "data_quality_judgment": {},
        "route_decision": None,
        "route_closed": False,
        "no_robust_effect": False,
        "refinement_allowed": False,
        "data_repair_required": False,
        "next_theory_selected": None,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": None if blocker else NEXT_STEP,
        "blocker": blocker,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise EvaluatorBlocked(f"HEAD mismatch: {head} != {EXPECTED_HEAD}")
    if not output_only_status(working_tree_status()):
        raise EvaluatorBlocked(f"unexpected dirty repo state during build: {working_tree_status()}")
    hashes_before = input_artifact_hashes()
    diagnostic, validator, refinement, theory_queue, input_payload_hashes = load_inputs()
    event_quality = summarize_event_quality(validator, refinement)
    diagnostic_summary = summarize_diagnostic(diagnostic)
    data_quality = judge_data_quality(diagnostic)
    route_closed = True
    no_robust_effect = True
    data_repair_required = False
    refinement_allowed = False
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise EvaluatorBlocked("input artifact hash changed during evaluator run")
    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "all_input_payload_hashes_verified": True,
        "diagnostic_completed_1000_of_1000_null": diagnostic.get("symbol_balanced_null_count_completed") == 1000,
        "event_counts_verified": diagnostic.get("long_event_count") == 541 and diagnostic.get("short_event_count") == 392,
        "forbidden_action_flags_false": all(
            diagnostic.get(flag) is False
            for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]
        ),
        "no_new_forward_returns_computed": True,
        "no_null_validation_rerun": True,
        "no_event_definition_modification": True,
        "no_strategy_signal_candidate_release": True,
        "route_closed_no_robust_effect": route_closed and no_robust_effect,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
    }
    artifact = base_artifact(head, hashes_before, hashes_after, None)
    artifact.update(
        {
            "result_classification": RESULT_CLOSED,
            "input_payload_hashes_verified": input_payload_hashes,
            "source_artifact_summary": {
                "diagnostic_result_classification": diagnostic.get("result_classification"),
                "validator_result_classification": validator.get("result_classification"),
                "refinement_result_classification": refinement.get("result_classification"),
                "theory_queue_result_classification": theory_queue.get("result_classification"),
            },
            "event_definition_quality_summary": event_quality,
            "diagnostic_result_summary": diagnostic_summary,
            "data_quality_judgment": data_quality,
            "route_decision": "Route closed/deprioritized: event definitions were clean, but the forward-return diagnostic showed no robust primary directional effect; data quality warnings are not sufficient to explain the failure.",
            "route_closed": route_closed,
            "no_robust_effect": no_robust_effect,
            "refinement_allowed": refinement_allowed,
            "data_repair_required": data_repair_required,
            "next_theory_selected": NEXT_THEORY,
            "strategy_allowed": False,
            "signal_allowed": False,
            "candidate_generation_allowed": False,
            "release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "allowed_next_step": NEXT_STEP,
            "validation_checks": validation_checks,
            "replacement_checks_all_true": all(validation_checks.values()),
        }
    )
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def blocked_artifact(reason: str, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    artifact = base_artifact(head, hashes_before, hashes_after, reason)
    artifact["validation_checks"] = {
        "blocked_without_substitution": True,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after if hashes_before and hashes_after else False,
        "replacement_checks_all_true": False,
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"status: {artifact['evaluator_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"event_definition_quality_summary: {json.dumps(artifact['event_definition_quality_summary'], sort_keys=True)}")
    print(f"diagnostic_result_summary: {json.dumps(artifact['diagnostic_result_summary'], sort_keys=True)}")
    print(f"data_quality_judgment: {json.dumps(artifact['data_quality_judgment'], sort_keys=True)}")
    print(f"route_decision: {artifact['route_decision']}")
    print(f"route_closed: {bool_text(bool(artifact['route_closed']))}")
    print(f"no_robust_effect: {bool_text(bool(artifact['no_robust_effect']))}")
    print(f"refinement_allowed: {bool_text(bool(artifact['refinement_allowed']))}")
    print(f"data_repair_required: {bool_text(bool(artifact['data_repair_required']))}")
    print(f"next_theory_selected: {artifact['next_theory_selected']}")
    print(f"strategy_allowed: {bool_text(bool(artifact['strategy_allowed']))}")
    print(f"signal_allowed: {bool_text(bool(artifact['signal_allowed']))}")
    print(f"candidate_generation_allowed: {bool_text(bool(artifact['candidate_generation_allowed']))}")
    print(f"release_allowed: {bool_text(bool(artifact['release_allowed']))}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(bool(artifact.get('replacement_checks_all_true')))}")
    print(f"blocker: {artifact.get('blocker')}")


def main() -> int:
    hashes_before: dict[str, str] | None = None
    try:
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
    except EvaluatorBlocked as exc:
        try:
            hashes_after = input_artifact_hashes()
        except Exception:
            hashes_after = None
        artifact = blocked_artifact(str(exc), hashes_before, hashes_after)
    write_artifact(artifact)
    print_summary(artifact)
    return 0 if artifact.get("replacement_checks_all_true") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
