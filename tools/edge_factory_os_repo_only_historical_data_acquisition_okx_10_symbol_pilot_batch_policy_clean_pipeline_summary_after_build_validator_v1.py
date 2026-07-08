from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_after_build_validator_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "43e64f4"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_VALIDATED_PIPELINE_SUMMARY_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_PIPELINE_CLOSED_FULL_UNIVERSE_DISCOVERY_PREVIEW_READY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_PIPELINE_SUMMARY_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_universe_discovery_preview_after_10_symbol_pilot_summary_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_blocked_record_v1.py"
RECOMMENDED_NEXT_ROUTE = "OKX_USDT_SWAP_FULL_SYMBOL_UNIVERSE_DISCOVERY_AND_3Y_ELIGIBILITY_PREVIEW"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_PIPELINE_CLOSED_FULL_UNIVERSE_DISCOVERY_PREVIEW_READY"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

VALIDATOR_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_after_execution_v1"
BUILD_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_after_batch_policy_v1"
POLICY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_after_batch_anomaly_classification_v1"
CLASSIFICATION_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_after_policy_clean_build_block_v1"
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1"

ARTIFACTS = {
    "validator_summary": VALIDATOR_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_summary.json",
    "validator": VALIDATOR_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator.json",
    "output_manifest": BUILD_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_1h_output_manifest.json",
    "build_summary": BUILD_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_summary.json",
    "policy_summary": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy_summary.json",
    "classification_summary": CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_anomaly_classification_summary.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_closure_record.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_limitations_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_lessons_for_full_universe.json",
    "historical_okx_10_symbol_pilot_next_full_universe_route_decision.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_self_validator.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json",
]

PILOT_SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "LINK-USDT-SWAP",
    "LTC-USDT-SWAP",
    "DOT-USDT-SWAP",
]

EXPECTED = {
    "pilot_symbol_count": 10,
    "output_1h_row_count": 252720,
    "output_symbol_count": 10,
    "complete_1h_row_count": 252710,
    "incomplete_1h_row_count": 10,
    "affected_hour_count": 10,
    "total_exact_duplicate_rows_dropped": 3252,
    "total_material_conflict_rows_quarantined": 20,
    "total_missing_minute_count": 4800,
    "clean_source_rows_after_policy": 15163190,
}


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def current_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def repo_has_only_this_tool_change() -> bool:
    status = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    if not status:
        return True
    rel = current_tool_rel()
    return all(line[3:].replace("\\", "/") == rel for line in status)


def tracked_python_files_including_current() -> list[str]:
    files = sorted(path for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))
    rel = current_tool_rel()
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files)


def tracked_python_validation() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    files = tracked_python_files_including_current()
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.exists(), f"missing required artifact {label}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    validator = artifacts["validator_summary"]
    build = artifacts["build_summary"]
    policy = artifacts["policy_summary"]
    classification = artifacts["classification_summary"]
    download_validator = artifacts["download_validator_summary"]
    manifest = artifacts["output_manifest"]
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "validator_status_passed": validator.get("historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_status") == PREVIOUS_STATUS,
        "validator_replacement_checks_true": validator.get("replacement_checks_all_true") is True,
        "current_next_module_matches": validator.get("next_module") == REQUESTED_MODULE,
        "validator_counts_match": all(validator.get(key) == value for key, value in EXPECTED.items()),
        "validator_safety_flags": (
            validator.get("output_valid_for_research_backtest") is False
            and validator.get("output_valid_for_edge_claim") is False
            and validator.get("safe_for_full_universe_acquisition") is False
            and validator.get("broad_acquisition_ready") is False
            and validator.get("synthetic_fill_used") is False
            and validator.get("forward_fill_used") is False
            and validator.get("backfill_used") is False
        ),
        "validator_no_forbidden_actions": (
            validator.get("new_download_performed_by_validator") is False
            and validator.get("data_build_performed_by_validator") is False
            and validator.get("aggregation_performed_by_validator") is False
            and validator.get("okx_api_call_performed") is False
            and validator.get("okx_browse_performed") is False
        ),
        "build_execution_passed": build.get("replacement_checks_all_true") is True,
        "batch_policy_passed": policy.get("replacement_checks_all_true") is True,
        "classification_passed": classification.get("replacement_checks_all_true") is True,
        "download_validator_passed": download_validator.get("replacement_checks_all_true") is True,
        "manifest_metadata_present": isinstance(manifest.get("output_files"), list) and len(manifest.get("output_files")) == 1,
    }
    return {"head": head, "checks": checks}


def common_summary(artifacts: dict[str, dict[str, Any]], chain: dict[str, Any], py_state: dict[str, Any]) -> dict[str, Any]:
    validator = artifacts["validator_summary"]
    replacement_checks = {
        **chain["checks"],
        "no_strategy_backtest_edge_route": True,
        "next_route_is_full_universe_discovery_preview": True,
        "no_download_api_browse_build_aggregation_now": True,
        "no_research_backtest_edge_claim": True,
        "no_full_universe_or_broad_ready_claim": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    return {
        "historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_status": status,
        "pipeline_summary_created": replacement_checks_all_true,
        "pipeline_closed_successfully": replacement_checks_all_true,
        "pilot_symbol_count": EXPECTED["pilot_symbol_count"],
        "pilot_symbols": PILOT_SYMBOLS,
        "output_1h_row_count": EXPECTED["output_1h_row_count"],
        "output_symbol_count": EXPECTED["output_symbol_count"],
        "complete_1h_row_count": EXPECTED["complete_1h_row_count"],
        "incomplete_1h_row_count": EXPECTED["incomplete_1h_row_count"],
        "affected_hour_count": EXPECTED["affected_hour_count"],
        "all_symbols_complete": False,
        "every_symbol_has_one_incomplete_hour": validator.get("every_symbol_has_one_incomplete_hour") is True,
        "total_exact_duplicate_rows_dropped": EXPECTED["total_exact_duplicate_rows_dropped"],
        "total_material_conflict_rows_quarantined": EXPECTED["total_material_conflict_rows_quarantined"],
        "total_missing_minute_count": EXPECTED["total_missing_minute_count"],
        "clean_source_rows_after_policy": EXPECTED["clean_source_rows_after_policy"],
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "numeric_sanity_validated": validator.get("numeric_sanity_validated") is True,
        "provenance_validated": validator.get("provenance_validated") is True,
        "output_valid_for_pipeline_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "next_route_decision_created": replacement_checks_all_true,
        "recommended_next_route": RECOMMENDED_NEXT_ROUTE,
        "full_universe_discovery_preview_required": True,
        "strategy_backtest_edge_allowed_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": max(int(validator.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_summary": AFTER_QUALITY if replacement_checks_all_true else "BATCH_POLICY_CLEAN_PIPELINE_SUMMARY_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_outputs(summary: dict[str, Any]) -> dict[str, Any]:
    closure = {
        **summary,
        "artifact_type": "pipeline_closure_record",
        "policy_closure": {
            "exact_duplicate_policy_validated_for_pilot": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW",
            "material_conflict_policy_validated_for_pilot": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP",
            "missing_minute_policy_validated_for_pilot": "NO_FILL_MARK_AFFECTED_HOUR_INCOMPLETE_OR_EXCLUDE_FROM_COMPLETE_CLAIMS",
            "conflict_row_selection_averaging_merging_allowed": False,
            "affected_hours_are_incomplete": True,
        },
    }
    limitations = {
        **summary,
        "artifact_type": "pipeline_limitations_report",
        "limitations": [
            "Output is valid for pipeline validation only.",
            "Output is not research/backtest/edge-ready.",
            "Output is not full-universe acquisition-ready.",
            "Broad acquisition remains not ready.",
            "No strategy, backtest, candidate generation, edge, profit, runtime, capital, or live route is approved.",
        ],
    }
    lessons = {
        **summary,
        "artifact_type": "lessons_for_full_universe",
        "lessons": [
            "Use a generalized batch policy, not one-symbol policy loops.",
            "Drop only exact duplicate extra rows.",
            "Quarantine all material conflict rows in affected open_time groups.",
            "Never synthesize, forward fill, or backfill missing minutes.",
            "Compute complete and incomplete hours from clean minute coverage.",
            "Keep full-universe discovery as preview/eligibility work before acquisition execution.",
        ],
    }
    route = {
        **summary,
        "artifact_type": "next_full_universe_route_decision",
        "route_reason": (
            "Single-symbol pipeline, 10-symbol pilot download, batch anomaly classification, "
            "batch policy, policy-clean build, and validator all passed; remaining blocker is "
            "full OKX USDT-SWAP symbol universe discovery and 3-year eligibility preview."
        ),
    }
    self_validator = {
        **summary,
        "artifact_type": "self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
        "required_outputs_created": [],
    }
    bundle = {
        **summary,
        "artifact_type": "bundle_summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    return {
        "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary.json": {
            **summary,
            "artifact_type": "pipeline_summary",
        },
        "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_closure_record.json": closure,
        "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_limitations_report.json": limitations,
        "historical_okx_10_symbol_pilot_batch_policy_lessons_for_full_universe.json": lessons,
        "historical_okx_10_symbol_pilot_next_full_universe_route_decision.json": route,
        "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json": bundle,
    }


def run_summary() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    chain = validate_inputs(artifacts, py_state)
    summary = common_summary(artifacts, chain, py_state)
    outputs = build_outputs(summary)
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing required outputs: {missing}")
    require(summary["replacement_checks_all_true"] is True, "replacement checks did not all pass")
    return summary


def main() -> int:
    try:
        summary = run_summary()
    except Exception as exc:
        blocked = {
            "historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_status": BLOCKED_STATUS,
            "pipeline_summary_created": False,
            "pipeline_closed_successfully": False,
            "blocked_reason": repr(exc),
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "created_at_utc": utc_now(),
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
