from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "62eb7ce"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_POLICY_APPLICATION_"
    "RESIDUAL_DUPLICATE_DIAGNOSTIC_MATERIAL_CONFLICT_POLICY_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_MATERIAL_DUPLICATE_"
    "CONFLICT_POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
)
COUNTS_INCOMPLETE_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_MATERIAL_DUPLICATE_"
    "GROUP_CLASSIFICATION_REQUIRED"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_MATERIAL_DUPLICATE_"
    "CONFLICT_POLICY_FAILED_REVIEW"
)
TARGET_SYMBOL = "ETH-USDT-SWAP"
EXPECTED_RAW_ETH_ROWS_SCANNED = 1_516_648
EXPECTED_RAW_ETH_UNIQUE_OPEN_TIME_COUNT = 1_516_320
EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT = 325
EXPECTED_RAW_ETH_DUPLICATE_EXTRA_ROW_COUNT = 328
EXPECTED_MISSING_MINUTES_AFTER_DIAGNOSTIC = 0
EXPECTED_ACTIVE_P1_ATTENTION_COUNT = 12
EXPECTED_HOUR_MS = 3_600_000
EXPECTED_COMPLETE_HOUR_ROW_COUNT = 60
AFTER_QUALITY_POLICY_READY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_MATERIAL_CONFLICT_"
    "POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
)
AFTER_QUALITY_CLASSIFICATION_REQUIRED = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_MATERIAL_DUPLICATE_"
    "GROUP_CLASSIFICATION_REQUIRED"
)
NEXT_MODULE_POLICY_READY = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_after_eth_material_conflict_policy_v1.py"
)
NEXT_MODULE_CLASSIFICATION_REQUIRED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_group_classification_after_residual_diagnostic_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_blocked_record_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
RESIDUAL_DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_policy_application_residual_duplicate_diagnostic_after_build_block_v1"
)
ETH_EXACT_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_exact_duplicate_policy_after_diagnostic_v1"
)
ANOMALY_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_eth_policy_v1"
)

ARTIFACTS = {
    "residual_diagnostic_summary": RESIDUAL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_summary.json",
    "residual_diagnostic": RESIDUAL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic.json",
    "raw_group_report": RESIDUAL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_residual_duplicate_raw_group_report.json",
    "count_audit": RESIDUAL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_policy_application_count_audit.json",
    "route_decision": RESIDUAL_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_residual_duplicate_next_route_decision.json",
    "eth_exact_policy_summary": ETH_EXACT_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_summary.json",
    "eth_exact_drop_policy": ETH_EXACT_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_policy.json",
    "anomaly_summary": ANOMALY_RECORD_DIR / f"{ANOMALY_RECORD_DIR.name}_latest.json",
    "anomaly_blocked_record": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_csv_read_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "rebuild_execution_performed_now": False,
    "output_1h_csv_created_now": False,
    "dedupe_execution_performed_now": False,
    "modified_source_output_created_now": False,
    "row_selection_among_conflicts_performed_now": False,
    "rows_averaged_or_merged_now": False,
    "ohlcv_modification_performed_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_candidate_touched": False,
    "edge_profit_claim_made": False,
    "full_universe_ready_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class PolicyBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PolicyBlocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise PolicyBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_false(payload: dict[str, Any], keys: list[str], label: str) -> None:
    for key in keys:
        require(payload.get(key) is False, f"{label}.{key} must be false")


def validate_prior_artifacts(artifacts: dict[str, dict[str, Any]]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved material conflict policy module")

    summary = artifacts["residual_diagnostic_summary"]
    diagnostic = artifacts["residual_diagnostic"]
    raw_group = artifacts["raw_group_report"]
    count_audit = artifacts["count_audit"]
    route = artifacts["route_decision"]
    exact_policy_summary = artifacts["eth_exact_policy_summary"]
    exact_drop_policy = artifacts["eth_exact_drop_policy"]
    anomaly_summary = artifacts["anomaly_summary"]
    anomaly_blocked = artifacts["anomaly_blocked_record"]

    for label, payload in {"summary": summary, "diagnostic": diagnostic}.items():
        require(
            payload.get(
                "historical_data_acquisition_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_status"
            )
            == PREVIOUS_STATUS,
            f"{label} previous status mismatch",
        )
        require(payload.get("diagnostic_performed") is True, f"{label} diagnostic not performed")
        require(payload.get("target_symbol") == TARGET_SYMBOL, f"{label} target mismatch")
        require(payload.get("raw_eth_rows_scanned") == EXPECTED_RAW_ETH_ROWS_SCANNED, f"{label} raw row count mismatch")
        require(payload.get("raw_eth_unique_open_time_count") == EXPECTED_RAW_ETH_UNIQUE_OPEN_TIME_COUNT, f"{label} unique count mismatch")
        require(payload.get("raw_eth_duplicate_group_count") == EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT, f"{label} duplicate group count mismatch")
        require(payload.get("raw_eth_duplicate_extra_row_count") == EXPECTED_RAW_ETH_DUPLICATE_EXTRA_ROW_COUNT, f"{label} duplicate extra count mismatch")
        require(payload.get("residual_duplicate_after_corrected_policy") is True, f"{label} residual duplicate flag mismatch")
        require(payload.get("residual_duplicate_group_count_after_corrected_policy") == 324, f"{label} residual group count mismatch")
        require(payload.get("second_duplicate_group_discovered") is True, f"{label} second duplicate flag mismatch")
        require(payload.get("material_conflict_discovered") is True, f"{label} material conflict flag mismatch")
        require(payload.get("missing_minute_count_after_corrected_policy") == 0, f"{label} missing minute mismatch")
        require(payload.get("corrected_policy_clean_build_preview_created") is False, f"{label} corrected preview mismatch")
        require(payload.get("approval_grants_future_corrected_policy_clean_build_next") is False, f"{label} corrected approval mismatch")
        require(payload.get("active_p0_blocker_count") == 1, f"{label} P0 count mismatch")
        require(payload.get("active_p1_attention_count") >= EXPECTED_ACTIVE_P1_ATTENTION_COUNT, f"{label} P1 count mismatch")
        require(payload.get("next_module") == REQUESTED_MODULE, f"{label} next module mismatch")
        require(payload.get("replacement_checks_all_true") is True, f"{label} replacement checks mismatch")
        validate_false(
            payload,
            [
                "data_build_performed",
                "aggregation_performed_now",
                "output_csv_created",
                "output_valid_for_research_backtest",
                "output_valid_for_edge_claim",
                "safe_for_full_universe_acquisition",
                "broad_acquisition_ready",
            ],
            label,
        )

    require(raw_group.get("eth_residual_duplicate_raw_group_report_created") is True, "raw group report not created")
    require(len(raw_group.get("duplicate_groups", [])) == EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT, "raw group report group count mismatch")
    require(count_audit.get("eth_policy_application_count_audit_created") is True, "count audit missing")
    require(count_audit.get("previous_count_mismatch_explained") is True, "count audit mismatch explanation missing")
    require(route.get("eth_residual_duplicate_next_route_decision_created") is True, "route decision missing")
    require(route.get("next_module") == REQUESTED_MODULE, "route next module mismatch")

    require(exact_policy_summary.get("target_symbol") == TARGET_SYMBOL, "exact policy target mismatch")
    require(exact_policy_summary.get("exact_duplicate_extra_rows_to_drop") == 1, "exact policy drop count mismatch")
    require(exact_drop_policy.get("target_symbol") == TARGET_SYMBOL, "exact drop policy target mismatch")
    require(exact_drop_policy.get("drop_only_if_all_canonical_fields_identical") is True, "exact drop policy identity rule missing")
    require(anomaly_summary.get("anomaly_symbol") == TARGET_SYMBOL, "anomaly summary target mismatch")
    require(anomaly_summary.get("active_p0_blocker_count") == 1, "anomaly summary P0 mismatch")
    require(anomaly_blocked.get("pilot_policy_clean_build_execution_blocked") is True, "anomaly blocked record state mismatch")


def compute_policy_counts(raw_group_report: dict[str, Any]) -> dict[str, Any]:
    groups = raw_group_report.get("duplicate_groups", [])
    if not isinstance(groups, list) or len(groups) != EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT:
        return {"policy_counts_complete": False, "reason": "duplicate group list missing or incomplete"}

    exact_groups: list[dict[str, Any]] = []
    material_groups: list[dict[str, Any]] = []
    for group in groups:
        required_keys = {
            "open_time",
            "group_size",
            "duplicate_extra_rows",
            "exact_duplicate_group",
            "differing_field_count",
            "raw_rows",
        }
        if not isinstance(group, dict) or not required_keys.issubset(group):
            return {"policy_counts_complete": False, "reason": "duplicate group detail missing required keys"}
        raw_rows = group.get("raw_rows")
        if not isinstance(raw_rows, list) or len(raw_rows) != int(group.get("group_size")):
            return {"policy_counts_complete": False, "reason": "raw row detail incomplete for a duplicate group"}
        if bool(group.get("exact_duplicate_group")):
            exact_groups.append(group)
        else:
            material_groups.append(group)

    exact_extra_rows_to_drop = sum(int(group["group_size"]) - 1 for group in exact_groups)
    material_rows_to_quarantine = sum(int(group["group_size"]) for group in material_groups)
    material_unique_open_time_count = len(material_groups)
    affected_hours = {
        (int(group["open_time"]) // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS for group in material_groups
    }
    total_eth_hour_count = EXPECTED_RAW_ETH_UNIQUE_OPEN_TIME_COUNT // EXPECTED_COMPLETE_HOUR_ROW_COUNT
    affected_hour_count = len(affected_hours)
    expected_complete_hours = total_eth_hour_count - affected_hour_count
    expected_incomplete_hours = affected_hour_count
    expected_clean_source_rows = (
        EXPECTED_RAW_ETH_ROWS_SCANNED - exact_extra_rows_to_drop - material_rows_to_quarantine
    )
    return {
        "policy_counts_complete": True,
        "eth_exact_duplicate_group_count": len(exact_groups),
        "eth_exact_duplicate_extra_rows_to_drop": exact_extra_rows_to_drop,
        "eth_material_conflict_group_count": len(material_groups),
        "eth_material_conflict_rows_to_quarantine": material_rows_to_quarantine,
        "eth_material_conflict_unique_open_time_count": material_unique_open_time_count,
        "eth_expected_clean_source_rows_after_policy": expected_clean_source_rows,
        "eth_expected_complete_1h_rows_after_policy": expected_complete_hours,
        "eth_expected_incomplete_1h_rows_after_policy": expected_incomplete_hours,
        "eth_affected_hour_count_after_policy": affected_hour_count,
        "material_conflict_affected_hour_starts": sorted(affected_hours),
        "exact_duplicate_group_size_counts": {
            str(size): sum(1 for group in exact_groups if int(group["group_size"]) == size)
            for size in sorted({int(group["group_size"]) for group in exact_groups})
        },
        "material_conflict_group_size_counts": {
            str(size): sum(1 for group in material_groups if int(group["group_size"]) == size)
            for size in sorted({int(group["group_size"]) for group in material_groups})
        },
        "material_conflict_groups": [
            {
                "open_time": group["open_time"],
                "open_time_utc": group.get("open_time_utc"),
                "group_size": group["group_size"],
                "differing_field_count": group.get("differing_field_count"),
                "differing_fields": group.get("differing_fields", []),
                "quarantine_all_rows": True,
                "raw_rows": group.get("raw_rows", []),
            }
            for group in material_groups
        ],
    }


def build_payloads(
    generated_at: str,
    artifacts: dict[str, dict[str, Any]],
    exists: dict[str, bool],
    valid: dict[str, bool],
) -> tuple[dict[str, Any], dict[str, Any]]:
    counts = compute_policy_counts(artifacts["raw_group_report"])
    policy_counts_complete = bool(counts.get("policy_counts_complete"))
    additional_group_classification_required = not policy_counts_complete

    if policy_counts_complete:
        status = PASS_STATUS
        material_conflict_policy_created = True
        policy_clean_build_preview_created = True
        policy_clean_build_approval_record_created = True
        approval_grants_future = True
        active_p0_blocker_count = 0
        current_quality = AFTER_QUALITY_POLICY_READY
        next_module = NEXT_MODULE_POLICY_READY
    else:
        status = COUNTS_INCOMPLETE_STATUS
        material_conflict_policy_created = False
        policy_clean_build_preview_created = False
        policy_clean_build_approval_record_created = False
        approval_grants_future = False
        active_p0_blocker_count = 1
        current_quality = AFTER_QUALITY_CLASSIFICATION_REQUIRED
        next_module = NEXT_MODULE_CLASSIFICATION_REQUIRED

    shared = {
        "material_conflict_policy_created": material_conflict_policy_created,
        "target_symbol": TARGET_SYMBOL,
        "raw_eth_rows_scanned": EXPECTED_RAW_ETH_ROWS_SCANNED,
        "raw_eth_unique_open_time_count": EXPECTED_RAW_ETH_UNIQUE_OPEN_TIME_COUNT,
        "raw_eth_duplicate_group_count": EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT,
        "raw_eth_duplicate_extra_row_count": EXPECTED_RAW_ETH_DUPLICATE_EXTRA_ROW_COUNT,
        "eth_exact_duplicate_group_count": counts.get("eth_exact_duplicate_group_count", 0),
        "eth_exact_duplicate_extra_rows_to_drop": counts.get("eth_exact_duplicate_extra_rows_to_drop", 0),
        "eth_material_conflict_group_count": counts.get("eth_material_conflict_group_count", 0),
        "eth_material_conflict_rows_to_quarantine": counts.get("eth_material_conflict_rows_to_quarantine", 0),
        "eth_material_conflict_unique_open_time_count": counts.get("eth_material_conflict_unique_open_time_count", 0),
        "eth_expected_clean_source_rows_after_policy": counts.get("eth_expected_clean_source_rows_after_policy", 0),
        "eth_expected_complete_1h_rows_after_policy": counts.get("eth_expected_complete_1h_rows_after_policy", 0),
        "eth_expected_incomplete_1h_rows_after_policy": counts.get("eth_expected_incomplete_1h_rows_after_policy", 0),
        "eth_affected_hour_count_after_policy": counts.get("eth_affected_hour_count_after_policy", 0),
        "policy_counts_complete": policy_counts_complete,
        "additional_group_classification_required": additional_group_classification_required,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "ohlcv_modification_allowed": False,
        "exact_duplicate_drop_allowed": True,
        "material_conflict_quarantine_required": True,
        "policy_clean_build_preview_created": policy_clean_build_preview_created,
        "policy_clean_build_approval_record_created": policy_clean_build_approval_record_created,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_10_symbol_eth_material_policy_clean_build_next": approval_grants_future,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": EXPECTED_ACTIVE_P1_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_policy": current_quality,
        "next_module": next_module,
    }
    policy = {
        "eth_material_duplicate_conflict_policy_created": material_conflict_policy_created,
        "policy_scope": "ETH_USDT_SWAP_DUPLICATE_GROUP_POLICY_FOR_FUTURE_10_SYMBOL_POLICY_CLEAN_BUILD",
        "exact_duplicate_policy": {
            "drop_only_if_all_fields_identical": True,
            "keep_one_canonical_row": True,
            "drop_group_size_minus_one_extra_rows": True,
            "audit_dropped_exact_duplicate_rows": True,
        },
        "material_conflict_policy": {
            "classify_any_differing_field_as_material_conflict": True,
            "quarantine_all_rows_in_material_conflict_group": True,
            "keep_any_conflicting_row": False,
            "choose_conflicting_row_allowed": False,
            "average_conflicting_rows_allowed": False,
            "merge_conflicting_rows_allowed": False,
            "ohlcv_modification_allowed": False,
            "affected_hour_must_be_incomplete_or_excluded_from_complete_output": True,
        },
        "fill_policy": {
            "synthetic_fill_allowed": False,
            "forward_fill_allowed": False,
            "backfill_allowed": False,
        },
        **shared,
    }
    count_artifact = {
        "eth_duplicate_group_policy_counts_created": True,
        "counts_source_artifact": str(ARTIFACTS["raw_group_report"]),
        "counts_computed_without_full_csv_read": True,
        "counts_computed_without_build_or_aggregation": True,
        "material_conflict_affected_hour_starts": counts.get("material_conflict_affected_hour_starts", []),
        "exact_duplicate_group_size_counts": counts.get("exact_duplicate_group_size_counts", {}),
        "material_conflict_group_size_counts": counts.get("material_conflict_group_size_counts", {}),
        **shared,
    }
    quarantine_policy = {
        "eth_material_conflict_quarantine_policy_created": material_conflict_policy_created,
        "quarantine_all_material_conflict_group_rows": True,
        "material_conflict_groups": counts.get("material_conflict_groups", []),
        "quarantine_execution_performed_now": False,
        "modified_source_output_created_now": False,
        **shared,
    }
    build_preview = {
        "eth_policy_clean_build_preview_created": policy_clean_build_preview_created,
        "preview_only": True,
        "future_build_must_reuse_btc_policy_clean_output_after_revalidation": True,
        "future_build_must_apply_eth_duplicate_policy_from_this_module": True,
        "future_build_must_build_remaining_8_symbols_only_if_clean": True,
        "future_build_must_fail_closed_on_new_sol_xrp_doge_ada_avax_link_ltc_dot_anomalies": True,
        "future_output_pipeline_validation_only": True,
        "future_output_valid_for_research_backtest": False,
        "future_output_valid_for_edge_claim": False,
        "future_full_universe_or_broad_acquisition_ready": False,
        **shared,
    }
    approval_record = {
        "eth_material_policy_clean_build_approval_record_created": policy_clean_build_approval_record_created,
        "approval_grants_policy_now": material_conflict_policy_created,
        "approval_grants_rebuild_now": False,
        "approval_grants_future_10_symbol_eth_material_policy_clean_build_next": approval_grants_future,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": next_module,
        **shared,
    }
    self_validator = {
        "eth_material_duplicate_conflict_policy_self_validator_created": True,
        "preflight_passed": True,
        "required_source_artifacts_exist": all(exists.values()),
        "required_source_artifacts_valid_json": all(valid.values()),
        "policy_counts_complete": policy_counts_complete,
        "additional_group_classification_required": additional_group_classification_required,
        "policy_counts_match_raw_diagnostic": (
            shared["eth_exact_duplicate_group_count"] + shared["eth_material_conflict_group_count"]
            == EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT
            and shared["eth_exact_duplicate_extra_rows_to_drop"]
            + (shared["eth_material_conflict_rows_to_quarantine"] - shared["eth_material_conflict_unique_open_time_count"])
            == EXPECTED_RAW_ETH_DUPLICATE_EXTRA_ROW_COUNT
        )
        if policy_counts_complete
        else False,
        "no_forbidden_actions_now": all(value is False for value in DANGEROUS_FLAGS.values()),
        "next_module_valid": next_module
        in {NEXT_MODULE_POLICY_READY, NEXT_MODULE_CLASSIFICATION_REQUIRED},
    }
    if policy_counts_complete:
        replacement_checks = {
            "material_conflict_policy_created": shared["material_conflict_policy_created"] is True,
            "target_symbol_eth": shared["target_symbol"] == TARGET_SYMBOL,
            "raw_counts_match_diagnostic": shared["raw_eth_rows_scanned"] == EXPECTED_RAW_ETH_ROWS_SCANNED
            and shared["raw_eth_duplicate_group_count"] == EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT
            and shared["raw_eth_duplicate_extra_row_count"] == EXPECTED_RAW_ETH_DUPLICATE_EXTRA_ROW_COUNT,
            "policy_counts_complete": shared["policy_counts_complete"] is True,
            "additional_group_classification_not_required": shared["additional_group_classification_required"] is False,
            "exact_and_material_counts_sum_to_duplicate_groups": shared["eth_exact_duplicate_group_count"]
            + shared["eth_material_conflict_group_count"]
            == EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT,
            "extra_rows_accounted": shared["eth_exact_duplicate_extra_rows_to_drop"]
            + (shared["eth_material_conflict_rows_to_quarantine"] - shared["eth_material_conflict_unique_open_time_count"])
            == EXPECTED_RAW_ETH_DUPLICATE_EXTRA_ROW_COUNT,
            "clean_source_row_count_valid": shared["eth_expected_clean_source_rows_after_policy"]
            == EXPECTED_RAW_ETH_ROWS_SCANNED
            - shared["eth_exact_duplicate_extra_rows_to_drop"]
            - shared["eth_material_conflict_rows_to_quarantine"],
            "affected_hour_counts_valid": shared["eth_expected_incomplete_1h_rows_after_policy"]
            == shared["eth_affected_hour_count_after_policy"]
            and shared["eth_expected_complete_1h_rows_after_policy"]
            + shared["eth_expected_incomplete_1h_rows_after_policy"]
            == EXPECTED_RAW_ETH_UNIQUE_OPEN_TIME_COUNT // EXPECTED_COMPLETE_HOUR_ROW_COUNT,
            "conflict_resolution_forbidden": shared["choose_conflicting_row_allowed"] is False
            and shared["average_conflicting_rows_allowed"] is False
            and shared["merge_conflicting_rows_allowed"] is False
            and shared["ohlcv_modification_allowed"] is False,
            "exact_drop_and_quarantine_policy_valid": shared["exact_duplicate_drop_allowed"] is True
            and shared["material_conflict_quarantine_required"] is True,
            "preview_and_approval_created": shared["policy_clean_build_preview_created"] is True
            and shared["policy_clean_build_approval_record_created"] is True,
            "approval_future_build_next_only": shared[
                "approval_grants_future_10_symbol_eth_material_policy_clean_build_next"
            ]
            is True
            and shared["approval_grants_rebuild_now"] is False,
            "no_build_aggregation_output": shared["data_build_performed"] is False
            and shared["aggregation_performed_now"] is False
            and shared["output_csv_created"] is False,
            "not_research_backtest_edge_full_universe_broad": shared[
                "output_valid_for_research_backtest"
            ]
            is False
            and shared["output_valid_for_edge_claim"] is False
            and shared["safe_for_full_universe_acquisition"] is False
            and shared["broad_acquisition_ready"] is False,
            "p0_clear_p1_attention": shared["active_p0_blocker_count"] == 0
            and shared["active_p1_attention_count"] >= EXPECTED_ACTIVE_P1_ATTENTION_COUNT,
            "next_module_valid": shared["next_module"] == NEXT_MODULE_POLICY_READY,
            "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        }
    else:
        replacement_checks = {
            "material_conflict_policy_not_created": shared["material_conflict_policy_created"] is False,
            "policy_counts_incomplete": shared["policy_counts_complete"] is False,
            "additional_group_classification_required": shared["additional_group_classification_required"] is True,
            "future_build_not_approved": shared[
                "approval_grants_future_10_symbol_eth_material_policy_clean_build_next"
            ]
            is False,
            "p0_remains_active": shared["active_p0_blocker_count"] == 1,
            "next_module_valid": shared["next_module"] == NEXT_MODULE_CLASSIFICATION_REQUIRED,
            "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_status": status,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_policy_run": tracked_python_count(),
        **shared,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy.json": policy,
        "historical_okx_10_symbol_pilot_eth_duplicate_group_policy_counts.json": count_artifact,
        "historical_okx_10_symbol_pilot_eth_material_conflict_quarantine_policy.json": quarantine_policy,
        "historical_okx_10_symbol_pilot_eth_policy_clean_build_preview.json": build_preview,
        "historical_okx_10_symbol_pilot_eth_material_policy_clean_build_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_self_validator.json": self_validator,
        "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_summary.json": summary,
        f"{MODULE_NAME}_latest.json": summary,
    }
    return summary, payloads


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_group_policy_counts.json",
        "historical_okx_10_symbol_pilot_eth_material_conflict_quarantine_policy.json",
        "historical_okx_10_symbol_pilot_eth_policy_clean_build_preview.json",
        "historical_okx_10_symbol_pilot_eth_material_policy_clean_build_approval_record.json",
        "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_self_validator.json",
        "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    policy = loaded["historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy.json"]
    counts = loaded["historical_okx_10_symbol_pilot_eth_duplicate_group_policy_counts.json"]
    approval = loaded["historical_okx_10_symbol_pilot_eth_material_policy_clean_build_approval_record.json"]
    checks = {
        "required_artifacts_exist": True,
        "summary_replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
        "policy_artifact_route_matches_summary": policy.get("next_module") == summary.get("next_module"),
        "count_artifact_complete_matches_summary": counts.get("policy_counts_complete")
        == summary.get("policy_counts_complete"),
        "approval_matches_policy_route": approval.get(
            "approval_grants_future_10_symbol_eth_material_policy_clean_build_next"
        )
        == summary.get("approval_grants_future_10_symbol_eth_material_policy_clean_build_next"),
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_prior_artifacts(artifacts)
    summary, payloads = build_payloads(generated_at, artifacts, exists, valid)
    require(summary["replacement_checks_all_true"] is True, "replacement checks failed")
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    written = validate_written_artifacts(summary)
    require(written["written_artifacts_valid"] is True, f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except PolicyBlocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_status": BLOCKED_STATUS,
            "material_conflict_policy_created": False,
            "target_symbol": TARGET_SYMBOL,
            "raw_eth_rows_scanned": EXPECTED_RAW_ETH_ROWS_SCANNED,
            "raw_eth_unique_open_time_count": EXPECTED_RAW_ETH_UNIQUE_OPEN_TIME_COUNT,
            "raw_eth_duplicate_group_count": EXPECTED_RAW_ETH_DUPLICATE_GROUP_COUNT,
            "raw_eth_duplicate_extra_row_count": EXPECTED_RAW_ETH_DUPLICATE_EXTRA_ROW_COUNT,
            "eth_exact_duplicate_group_count": 0,
            "eth_exact_duplicate_extra_rows_to_drop": 0,
            "eth_material_conflict_group_count": 0,
            "eth_material_conflict_rows_to_quarantine": 0,
            "eth_material_conflict_unique_open_time_count": 0,
            "eth_expected_clean_source_rows_after_policy": 0,
            "eth_expected_complete_1h_rows_after_policy": 0,
            "eth_expected_incomplete_1h_rows_after_policy": 0,
            "eth_affected_hour_count_after_policy": 0,
            "policy_counts_complete": False,
            "additional_group_classification_required": False,
            "choose_conflicting_row_allowed": False,
            "average_conflicting_rows_allowed": False,
            "merge_conflicting_rows_allowed": False,
            "ohlcv_modification_allowed": False,
            "exact_duplicate_drop_allowed": False,
            "material_conflict_quarantine_required": False,
            "policy_clean_build_preview_created": False,
            "policy_clean_build_approval_record_created": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_future_10_symbol_eth_material_policy_clean_build_next": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": EXPECTED_ACTIVE_P1_ATTENTION_COUNT,
            "current_evidence_chain_quality_after_policy": PREVIOUS_STATUS,
            "next_module": NEXT_MODULE_BLOCKED,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked_payload)
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
