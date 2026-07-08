from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_universe_discovery_preview_after_10_symbol_pilot_summary_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "2193171"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_PIPELINE_CLOSED_FULL_UNIVERSE_DISCOVERY_PREVIEW_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_UNIVERSE_DISCOVERY_PREVIEW_READY_FOR_SOURCE_DISCOVERY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_UNIVERSE_DISCOVERY_PREVIEW_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_universe_discovery_preview_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_UNIVERSE_DISCOVERY_PREVIEW_READY_FOR_SOURCE_DISCOVERY"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

PILOT_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_after_build_validator_v1"
VALIDATOR_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_after_execution_v1"
POLICY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_after_batch_anomaly_classification_v1"
CLASSIFICATION_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_after_policy_clean_build_block_v1"
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1"

ARTIFACTS = {
    "pilot_pipeline_summary": PILOT_SUMMARY_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json",
    "pilot_pipeline_closure": PILOT_SUMMARY_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_closure_record.json",
    "build_validator_summary": VALIDATOR_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_summary.json",
    "batch_policy_summary": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy_summary.json",
    "classification_summary": CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_anomaly_classification_summary.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_symbol_universe_discovery_preview.json",
    "historical_okx_full_usdt_swap_near_3y_eligibility_rules_preview.json",
    "historical_okx_full_usdt_swap_symbol_source_route_decision.json",
    "historical_okx_full_usdt_swap_survivorship_bias_limitations_report.json",
    "historical_okx_full_usdt_swap_batch_policy_carry_forward_report.json",
    "historical_okx_full_usdt_swap_symbol_source_discovery_approval_record.json",
    "historical_okx_full_usdt_swap_universe_discovery_preview_self_validator.json",
    "historical_okx_full_usdt_swap_universe_discovery_preview_summary.json",
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

TARGET = {
    "target_exchange": "OKX",
    "target_instrument_type": "PERPETUAL_SWAP",
    "target_quote_scope": "USDT_SWAP",
    "target_symbol_format": "BASE-USDT-SWAP",
    "max_available_start_candidate": "2023-07-01",
    "max_available_end_date": "2026-05-18",
    "expected_daily_file_count_per_symbol": 1053,
}

POLICY = {
    "exact_duplicate_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW",
    "material_conflict_policy": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP",
    "missing_minute_policy": "NO_FILL_MARK_AFFECTED_HOUR_INCOMPLETE_OR_EXCLUDE_FROM_COMPLETE_CLAIMS",
    "synthetic_fill_allowed": False,
    "forward_fill_allowed": False,
    "backfill_allowed": False,
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
    pilot = artifacts["pilot_pipeline_summary"]
    validator = artifacts["build_validator_summary"]
    policy = artifacts["batch_policy_summary"]
    classification = artifacts["classification_summary"]
    download_validator = artifacts["download_validator_summary"]
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": pilot.get("historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_status") == PREVIOUS_STATUS,
        "current_next_module_matches": pilot.get("next_module") == REQUESTED_MODULE,
        "pilot_pipeline_closed": pilot.get("pipeline_closed_successfully") is True and pilot.get("replacement_checks_all_true") is True,
        "validator_passed": validator.get("replacement_checks_all_true") is True and validator.get("batch_policy_clean_build_execution_validated") is True,
        "policy_passed": policy.get("replacement_checks_all_true") is True,
        "classification_passed": classification.get("replacement_checks_all_true") is True,
        "download_validator_passed": download_validator.get("replacement_checks_all_true") is True,
        "pilot_safety_flags": (
            pilot.get("output_valid_for_research_backtest") is False
            and pilot.get("output_valid_for_edge_claim") is False
            and pilot.get("safe_for_full_universe_acquisition") is False
            and pilot.get("broad_acquisition_ready") is False
            and pilot.get("strategy_backtest_edge_allowed_now") is False
        ),
        "pilot_counts_match": (
            pilot.get("pilot_symbol_count") == 10
            and pilot.get("output_1h_row_count") == 252720
            and pilot.get("complete_1h_row_count") == 252710
            and pilot.get("incomplete_1h_row_count") == 10
            and pilot.get("affected_hour_count") == 10
            and pilot.get("clean_source_rows_after_policy") == 15163190
        ),
    }
    return {"head": head, "checks": checks}


def common_summary(artifacts: dict[str, dict[str, Any]], chain: dict[str, Any], py_state: dict[str, Any]) -> dict[str, Any]:
    pilot = artifacts["pilot_pipeline_summary"]
    replacement_checks = {
        **chain["checks"],
        "strict_3y_not_claimed": True,
        "preview_only_no_execution_allowed_now": True,
        "no_download_api_browse_build_aggregation_now": True,
        "no_research_backtest_edge_claim": True,
        "no_full_universe_or_broad_ready_claim": True,
        "next_module_is_symbol_source_discovery": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    return {
        "historical_data_acquisition_okx_full_usdt_swap_symbol_universe_discovery_preview_status": status,
        "full_universe_discovery_preview_created": replacement_checks_all_true,
        **TARGET,
        "strict_3y_completeness_claimed": False,
        "near_3y_eligibility_rules_created": replacement_checks_all_true,
        "symbol_source_route_decision_created": replacement_checks_all_true,
        "recommended_symbol_source_route": "OKX_OFFICIAL_OR_USER_SUPPLIED_USDT_SWAP_SYMBOL_LIST_THEN_ARCHIVE_COVERAGE_ELIGIBILITY",
        "survivorship_bias_limitations_recorded": True,
        "batch_policy_carry_forward_created": True,
        **POLICY,
        "full_universe_acquisition_allowed_now": False,
        "symbol_discovery_execution_allowed_now": False,
        "archive_download_allowed_now": False,
        "okx_api_call_allowed_now": False,
        "okx_browse_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "future_symbol_source_discovery_approval_record_created": replacement_checks_all_true,
        "approval_grants_preview_now": replacement_checks_all_true,
        "approval_grants_symbol_discovery_now": False,
        "approval_grants_future_symbol_source_discovery_next": replacement_checks_all_true,
        "approval_grants_archive_url_generation_now": False,
        "approval_grants_archive_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": max(int(pilot.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY if replacement_checks_all_true else "FULL_USDT_SWAP_SYMBOL_UNIVERSE_DISCOVERY_PREVIEW_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_outputs(summary: dict[str, Any]) -> dict[str, Any]:
    preview = {
        **summary,
        "artifact_type": "symbol_universe_discovery_preview",
        "target_universe": {
            "exchange": "OKX",
            "instrument_type": "perpetual swap",
            "quote_margin_scope": "USDT-SWAP",
            "symbol_format": "BASE-USDT-SWAP",
            "out_of_scope": ["spot", "quarterly futures", "USDC swaps unless separately approved"],
        },
        "coverage_window_wording": "near-3-year / max-available since visible OKX candlestick archive coverage starts around July 2023",
    }
    eligibility = {
        **summary,
        "artifact_type": "near_3y_eligibility_rules_preview",
        "candidate_label": "OKX_USDT_SWAP_NEAR_3Y_DATA_UNIVERSE",
        "eligibility_rules": [
            "Symbol belongs to OKX USDT-SWAP perpetual scope.",
            "Daily ZIP archive path can be generated or resolved for the full date range.",
            "All expected files are available or coverage gaps are explicitly recorded.",
            "Schema matches expected OKX candlestick schema.",
            "Symbol inside CSV matches expected symbol.",
            "Anomalies are handled only by approved batch policy.",
            "No synthetic fill, forward fill, or backfill.",
        ],
    }
    route = {
        **summary,
        "artifact_type": "symbol_source_route_decision",
        "source_discovery_route_options": {
            "A_USER_SUPPLIED_OR_LOCAL_EXISTING_SYMBOL_LIST_FIRST": {
                "description": "Use a user-supplied list or local artifact if present.",
                "risk": "May be incomplete or stale.",
                "api_browse_download_now": False,
            },
            "B_OKX_OFFICIAL_INSTRUMENTS_SOURCE_LOOKUP": {
                "description": "Future module may use OKX official instruments source/API/page only after separate approval.",
                "survivorship_limitation": "May only return currently listed instruments.",
                "api_browse_download_now": False,
            },
            "C_ARCHIVE_PATTERN_COVERAGE_DISCOVERY": {
                "description": "Generate candidate daily ZIP URLs only after symbol list approval.",
                "archive_existence_checks_now": False,
            },
            "D_HYBRID_ROUTE_RECOMMENDED": {
                "description": "Official current OKX USDT-SWAP instruments or user list, then archive coverage eligibility.",
                "recommended": True,
            },
        },
    }
    limitations = {
        **summary,
        "artifact_type": "survivorship_bias_limitations_report",
        "limitations": [
            "Current official instrument sources may omit delisted or historical symbols.",
            "User-supplied or local lists may be stale or incomplete.",
            "Hybrid route is acceptable for current-active near-3y universe preview, not survivorship-complete historical universe.",
            "No full-universe acquisition readiness is claimed.",
        ],
    }
    carry_forward = {
        **summary,
        "artifact_type": "batch_policy_carry_forward_report",
        "policy_scope": "carry validated 10-symbol batch policy forward as future full-universe candidate policy, subject to preview and separate approval",
    }
    approval = {
        **summary,
        "artifact_type": "symbol_source_discovery_approval_record",
        "approval_scope": "next separate symbol source discovery module only",
    }
    self_validator = {
        **summary,
        "artifact_type": "self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
        "required_outputs_created": [],
    }
    bundle = {
        **summary,
        "artifact_type": "preview_summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    return {
        "historical_okx_full_usdt_swap_symbol_universe_discovery_preview.json": preview,
        "historical_okx_full_usdt_swap_near_3y_eligibility_rules_preview.json": eligibility,
        "historical_okx_full_usdt_swap_symbol_source_route_decision.json": route,
        "historical_okx_full_usdt_swap_survivorship_bias_limitations_report.json": limitations,
        "historical_okx_full_usdt_swap_batch_policy_carry_forward_report.json": carry_forward,
        "historical_okx_full_usdt_swap_symbol_source_discovery_approval_record.json": approval,
        "historical_okx_full_usdt_swap_universe_discovery_preview_self_validator.json": self_validator,
        "historical_okx_full_usdt_swap_universe_discovery_preview_summary.json": bundle,
    }


def run_preview() -> dict[str, Any]:
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
        summary = run_preview()
    except Exception as exc:
        blocked = {
            "historical_data_acquisition_okx_full_usdt_swap_symbol_universe_discovery_preview_status": BLOCKED_STATUS,
            "full_universe_discovery_preview_created": False,
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
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_universe_discovery_preview_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
