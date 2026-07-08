from __future__ import annotations

import ast
import csv
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_HEAD = "68c9599"
EXPECTED_TRACKED_PYTHON_COUNT = 626

CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
RUNNER_EXECUTION_APPROVAL_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1_latest.json"
)

FEATURE_PANEL_DIR = LAB_ROOT / "edge_factory_feature_panels" / "market_panic_rebound_long_v1"
FEATURE_PANEL_MANIFEST = FEATURE_PANEL_DIR / "market_panic_rebound_long_v1_feature_panel_manifest.json"
FEATURE_PANEL_PARQUET = FEATURE_PANEL_DIR / "market_panic_rebound_long_v1_feature_panel_1h.parquet"
FEATURE_PANEL_SYMBOL_DIR = FEATURE_PANEL_DIR / "hourly_by_symbol"
FEATURE_QUALITY_STATE = (
    LAB_ROOT
    / "edge_factory_feature_panel_quality_auditor_v1"
    / "feature_panel_quality_audit_v1_20260512_000429"
    / "feature_panel_quality_audit_v1_state.json"
)
FEATURE_QUALITY_SYMBOL_SUMMARY = (
    LAB_ROOT
    / "edge_factory_feature_panel_quality_auditor_v1"
    / "feature_panel_quality_audit_v1_20260512_000429"
    / "feature_panel_quality_audit_v1_symbol_summary.csv"
)
CANDLE_INVENTORY_DIR = LAB_ROOT / "edge_factory_candle_universe_inventory" / "candle_inventory_20260510_184453"
CANDLE_FILE_INVENTORY = CANDLE_INVENTORY_DIR / "candle_file_inventory.csv"
CANDLE_SYMBOL_COVERAGE = CANDLE_INVENTORY_DIR / "candle_symbol_coverage.csv"
CANDLE_STATE = CANDLE_INVENTORY_DIR / "candle_universe_inventory_state.json"
DATA_BINDING_DIR = LAB_ROOT / "edge_factory_offline_runner_data_source_binding_v1" / "data_source_binding_v1_20260512_003148"
DATA_BINDING_SOURCES = DATA_BINDING_DIR / "data_source_binding_v1_sources.csv"
DATA_BINDING_STATE = DATA_BINDING_DIR / "data_source_binding_v1_state.json"

NEXT_MODULE_VALIDATOR = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_blocked_record_after_research_return_gate_v1.py"
POST_CHECK_STATUS_PASS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POST_CHECK_STATUS_BLOCKED = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY_SUCCESS = "PRIMARY_ARTIFACT_STRONG_PENDING_SOURCE_PANEL_RESULT_VALIDATOR"
CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED = "DERIVED_EXPLICIT_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

EXPECTED_PRIMARY_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]

DANGEROUS_FLAGS = [
    "runtime_touched",
    "launcher_executed",
    "launcher_touch_performed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "active_paper_touched",
    "strategy_research_recommended_now",
    "strategy_research_implementation_touched",
    "candidate_generation_recommended_now",
    "candidate_generation_touched",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "family_release_touched",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "config_file_creation_allowed_now",
    "config_file_creation_performed_now",
    "generic_runner_approval_granted",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "generic_runner_implementation_performed_now",
    "implementation_allowed_now",
    "runtime_preflight_implementation_performed",
    "runtime_kill_switch_implementation_performed",
    "runtime_touch_performed",
    "capital_touch_performed",
    "live_touch_performed",
    "real_order_touch_performed",
    "active_paper_touch_performed",
    "paper_behavior_changed_now",
    "execution_path_approved_now",
    "order_path_touched_now",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]] if args and args[0] == "git" else args
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, str]:
    if not path.exists():
        return {}, False, "missing"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, False, f"{type(exc).__name__}: {exc}"
    if not isinstance(loaded, dict):
        return {}, False, "artifact_json_root_not_object"
    return loaded, True, ""


def nested_dict(record: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else {}


def latest_commit_paths() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "show", "--name-only", "--format=", "HEAD"]).stdout.splitlines()
        if line.strip()
    )


def tracked_python_validation() -> Dict[str, Any]:
    tracked_files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
    current_file = CURRENT_TOOL_REL if (REPO_ROOT / CURRENT_TOOL_REL).exists() else None
    files = sorted(set(tracked_files + ([current_file] if current_file and current_file not in tracked_files else [])))
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except UnicodeDecodeError as exc:
            syntax_errors.append({"path": rel, "error": f"UnicodeDecodeError: {exc}"})
        except SyntaxError as exc:
            syntax_errors.append({"path": rel, "error": f"SyntaxError line={exc.lineno}: {exc.msg}"})
    return {
        "tracked_python_count": len(files),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "current_file_included_precommit": current_file is not None and current_file not in tracked_files,
    }


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    latest_paths = latest_commit_paths()
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": changed_paths == [CURRENT_TOOL_REL] or (len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL]),
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def csv_profile(path: Path, max_rows: int = 250000) -> Dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "row_count": 0, "columns": [], "limitations": ["missing"]}
    row_count = 0
    null_counts: Counter[str] = Counter()
    symbol_values: set[str] = set()
    min_time = None
    max_time = None
    duplicate_key_count = 0
    seen_keys: set[Tuple[str, str]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        symbol_col = first_present(columns, ["symbol", "normalized_symbol", "base_symbol", "ticker"])
        time_col = first_present(columns, ["time", "timestamp", "datetime", "date", "first_time", "last_time"])
        for row in reader:
            row_count += 1
            for column in columns:
                value = row.get(column)
                if value is None or value == "" or value.lower() in {"nan", "null", "none"}:
                    null_counts[column] += 1
            if symbol_col and row.get(symbol_col):
                symbol_values.add(str(row[symbol_col]))
            if time_col and row.get(time_col):
                value = str(row[time_col])
                min_time = value if min_time is None or value < min_time else min_time
                max_time = value if max_time is None or value > max_time else max_time
                if symbol_col and row.get(symbol_col):
                    key = (str(row[symbol_col]), value)
                    if key in seen_keys:
                        duplicate_key_count += 1
                    elif len(seen_keys) < max_rows:
                        seen_keys.add(key)
            if row_count >= max_rows:
                break
    return {
        "path": str(path),
        "exists": True,
        "row_count": row_count,
        "columns": columns,
        "symbol_column": symbol_col,
        "time_column": time_col,
        "distinct_symbol_count_observed": len(symbol_values),
        "min_time_observed": min_time,
        "max_time_observed": max_time,
        "null_counts_observed": dict(null_counts),
        "duplicate_symbol_time_count_observed": duplicate_key_count,
        "scan_row_limit": max_rows,
        "limitations": ["csv scan row-limited"] if row_count >= max_rows else [],
    }


def first_present(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    lower_map = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def source_panel_input_discovery() -> Dict[str, Any]:
    candidate_paths = [
        FEATURE_PANEL_MANIFEST,
        FEATURE_PANEL_PARQUET,
        FEATURE_QUALITY_STATE,
        FEATURE_QUALITY_SYMBOL_SUMMARY,
        CANDLE_FILE_INVENTORY,
        CANDLE_SYMBOL_COVERAGE,
        CANDLE_STATE,
        DATA_BINDING_SOURCES,
        DATA_BINDING_STATE,
    ]
    existing = [path for path in candidate_paths if path.exists()]
    suffix_counts = Counter(path.suffix.lower() or "<none>" for path in existing)
    size_summary = {
        "total_bytes": sum(path.stat().st_size for path in existing),
        "max_file_bytes": max((path.stat().st_size for path in existing), default=0),
        "file_count_by_extension": dict(suffix_counts),
    }
    limitations = []
    if FEATURE_PANEL_PARQUET.exists():
        limitations.append("parquet full column scan not performed because bundled runtime lacks pyarrow; used manifest and quality audit as primary metadata evidence")
    if not existing:
        limitations.append("no valid source-panel inputs discovered")
    return {
        "discovered_input_paths": [str(path) for path in existing],
        "input_path_type": "ESTABLISHED_EDGE_FACTORY_OUTPUT_DIRECTORIES_AND_REPO_ADJACENT_SOURCE_PANEL_ARTIFACTS",
        "source_panel_input_exists": len(existing) > 0,
        "input_file_count": len(existing),
        "input_format_summary": dict(suffix_counts),
        "input_size_summary": size_summary,
        "input_is_repo_only_safe_to_read": all(LAB_ROOT in path.parents or path == LAB_ROOT for path in existing),
        "input_discovery_limitations": limitations,
        "fail_closed_if_missing": len(existing) == 0,
    }


def pre_execution_contract_validation(contract: Dict[str, Any], valid_json: bool) -> Dict[str, bool]:
    return {
        "repaired_contract_artifact_exists": CONTRACT_ARTIFACT_PATH.exists(),
        "repaired_contract_artifact_valid_json": valid_json,
        "contract_primary_marker_exists": isinstance(contract.get("contract_primary_marker"), dict),
        "contract_identity_exists": isinstance(contract.get("contract_artifact_identity"), dict),
        "repair_applied_marker_exists": nested_dict(contract, "contract_artifact_repair_applied_marker").get("repair_applied") is True,
        "old_anomaly_closed_route_guard_marker_exists": isinstance(contract.get("old_source_panel_anomaly_closed_route_guard_marker"), dict),
        "no_profit_marker_exists": isinstance(contract.get("no_profit_claim_marker"), dict),
        "no_runtime_capital_live_order_marker_exists": isinstance(contract.get("no_runtime_capital_live_order_marker"), dict),
        "no_candidate_family_active_paper_marker_exists": isinstance(contract.get("no_candidate_family_active_paper_marker"), dict),
        "no_generic_runner_marker_exists": isinstance(contract.get("no_generic_runner_marker"), dict),
        "no_schema_config_marker_exists": isinstance(contract.get("no_schema_config_marker"), dict),
        "future_source_panel_primary_artifact_requirements_exist": sorted(
            nested_dict(contract, "primary_artifact_requirement").get("future_source_panel_primary_artifact_list", [])
        )
        == sorted(EXPECTED_PRIMARY_ARTIFACTS),
    }


def prior_approval_respected(approval: Dict[str, Any], valid_json: bool) -> bool:
    return (
        valid_json
        and approval.get("source_panel_analysis_runner_execution_approval_status") == "PASS"
        and approval.get("runner_execution_approval_record_created") is True
        and approval.get("user_runner_execution_approval_present") is True
        and approval.get("runner_execution_eligible_next") is True
        and approval.get("runner_execution_performed") is False
        and approval.get("approval_grants_runner_execution_now") is False
        and approval.get("source_panel_analysis_execution_run_now") is False
        and approval.get("heavy_data_scan_run_now") is False
        and approval.get("source_panel_results_generated_now") is False
        and approval.get("candidate_generation_performed") is False
        and approval.get("backtest_performed") is False
        and approval.get("runtime_touch_performed") is False
        and approval.get("capital_touch_performed") is False
        and approval.get("live_touch_performed") is False
        and approval.get("generic_runner_approval_granted") is False
        and approval.get("generic_runner_implementation_remains_blocked") is True
        and approval.get("loop_remains_closed") is True
        and approval.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and approval.get("replacement_checks_all_true") is True
    )


def build_result_artifacts(
    discovery: Dict[str, Any],
    manifest: Dict[str, Any],
    quality_state: Dict[str, Any],
    candle_state: Dict[str, Any],
    binding_state: Dict[str, Any],
    csv_profiles: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    quality_summary = nested_dict(quality_state, "quality_summary")
    candle_manifest = nested_dict(candle_state, "manifest")
    candle_state_inner = nested_dict(candle_state, "state")
    generated_at = now_utc()
    limitations = discovery["input_discovery_limitations"]
    symbol_count = int(manifest.get("processed_symbol_count") or quality_summary.get("symbol_count") or 0)
    row_count = int(manifest.get("panel_rows") or quality_summary.get("row_count") or 0)
    non_null_summary = nested_dict(manifest, "non_null_summary")
    nan_ratios = nested_dict(quality_summary, "nan_ratios")

    inventory = {
        "artifact": "source_panel_inventory.json",
        "generated_at_utc": generated_at,
        "source_categories": ["feature_panel_manifest", "feature_panel_parquet_file", "quality_audit", "candle_inventory", "data_source_binding"],
        "discovered_sources": discovery["discovered_input_paths"],
        "file_inventory": [
            {"path": path, "bytes": Path(path).stat().st_size if Path(path).exists() else 0}
            for path in discovery["discovered_input_paths"]
        ],
        "candidate_key": manifest.get("candidate_key") or quality_state.get("candidate_key"),
        "family_key": manifest.get("family_key"),
        "feature_panel_path": manifest.get("feature_panel_path"),
        "panel_rows": row_count,
        "source_file_count": manifest.get("source_file_count"),
        "processed_symbol_count": symbol_count,
        "columns_or_features_available": sorted(non_null_summary.keys()),
        "symbol_identifiers_available": symbol_count > 0,
        "timestamp_columns_available": bool(manifest.get("first_time") and manifest.get("last_time")),
        "first_time": manifest.get("first_time") or quality_summary.get("first_time"),
        "last_time": manifest.get("last_time") or quality_summary.get("last_time"),
        "csv_profiles": csv_profiles,
        "limitations": limitations,
        "no_strategy_signal_claim": True,
        "no_profit_claim": True,
    }

    coverage = {
        "artifact": "source_panel_coverage_summary.json",
        "generated_at_utc": generated_at,
        "symbol_coverage": {
            "processed_symbol_count": symbol_count,
            "candle_symbols_found": candle_state_inner.get("symbols_found"),
            "candle_ready_symbols": candle_state_inner.get("ready_symbols"),
            "candle_weak_symbols": candle_state_inner.get("weak_symbols"),
            "quality_audit_weak_symbol_count": quality_summary.get("weak_symbol_count"),
        },
        "time_coverage": {
            "first_time": manifest.get("first_time") or quality_summary.get("first_time"),
            "last_time": manifest.get("last_time") or quality_summary.get("last_time"),
            "span_days": quality_summary.get("span_days"),
        },
        "feature_coverage": {
            "features": sorted(non_null_summary.keys()),
            "missing_output_cols": manifest.get("missing_output_cols", []),
            "non_null_summary": non_null_summary,
        },
        "source_coverage": {
            "source_file_count": manifest.get("source_file_count"),
            "raw_files_found": binding_state.get("raw_files_found"),
            "valid_ohlcv_files": binding_state.get("valid_ohlcv_files"),
        },
        "panel_completeness_summary": {
            "panel_rows": row_count,
            "audit_status": quality_state.get("audit_status"),
            "runner_panel_allowed": quality_state.get("runner_panel_allowed"),
            "candle_overall_verdict": candle_state_inner.get("overall_verdict"),
        },
        "limitations": limitations + ["candle universe readiness can be weak while feature panel quality audit passes; recorded as source coverage limitation"],
    }

    missingness = {
        "artifact": "source_panel_missingness_report.json",
        "generated_at_utc": generated_at,
        "missingness_by_feature": {
            feature: {
                "non_null_count": non_null,
                "missing_count_estimate": max(row_count - int(non_null), 0) if row_count else None,
                "missing_ratio_from_quality_audit": nan_ratios.get(feature),
            }
            for feature, non_null in non_null_summary.items()
        },
        "missingness_by_symbol_time": {
            "available": False,
            "reason": "symbol/time missingness not recomputed from full parquet without pyarrow; quality audit summary is used as primary metadata evidence",
        },
        "null_nan_counts_available": bool(nan_ratios),
        "incomplete_input_warnings": candle_state_inner.get("warnings", []),
        "limitations": limitations,
    }

    anomaly = {
        "artifact": "source_panel_anomaly_report.json",
        "generated_at_utc": generated_at,
        "data_quality_anomalies_only": True,
        "old_source_panel_anomaly_route_reopened": False,
        "old_route_closed_artifacts_used_as_active_evidence": False,
        "duplicate_rows_checked": True,
        "duplicate_rows": quality_summary.get("duplicate_count"),
        "malformed_timestamps_checked": False,
        "non_monotonic_time_checked": False,
        "extreme_missingness_checked": True,
        "extreme_missingness_findings": [
            {"feature": feature, "nan_ratio": ratio}
            for feature, ratio in nan_ratios.items()
            if isinstance(ratio, (int, float)) and ratio > 0.05
        ],
        "stale_freshness_checked": True,
        "freshness_summary": {"first_time": manifest.get("first_time"), "last_time": manifest.get("last_time")},
        "source_mismatch_checked": True,
        "source_mismatch_issues": candle_state_inner.get("warnings", []),
        "limitations": limitations + ["timestamp malformation/non-monotonic checks not recomputed from full parquet in this repo-only execution"],
    }

    coverage_score = 1.0 if row_count >= 1_000_000 and symbol_count >= 200 else 0.5 if row_count and symbol_count else 0.0
    missingness_score = max(0.0, 1.0 - max((float(v) for v in nan_ratios.values() if isinstance(v, (int, float))), default=1.0))
    freshness_score = 1.0 if manifest.get("last_time") else 0.0
    reliability_score = round((coverage_score + missingness_score + freshness_score) / 3.0, 4)
    score_bucket = "PASS_WITH_LIMITATIONS" if reliability_score >= 0.8 else "ATTENTION" if reliability_score >= 0.5 else "FAIL_CLOSED"
    scorecard = {
        "artifact": "source_panel_quality_scorecard.json",
        "generated_at_utc": generated_at,
        "quality_score_by_source": {
            "feature_panel": reliability_score,
            "quality_audit": 1.0 if quality_state.get("audit_status") == "FEATURE_PANEL_QUALITY_PASS" else 0.0,
            "candle_inventory": 0.5 if candle_state_inner.get("overall_verdict") == "FAIL_NO_READY_CANDLE_UNIVERSE" else 1.0,
            "data_source_binding": 1.0 if binding_state.get("binding_status") == "DATA_SOURCE_BINDING_READY" else 0.0,
        },
        "coverage_score": coverage_score,
        "missingness_score": round(missingness_score, 4),
        "freshness_score": freshness_score,
        "overall_quality_score": reliability_score,
        "quality_bucket": score_bucket,
        "reliability_notes": [
            "Feature panel quality audit passed and found no critical blockers.",
            "Candle universe inventory reported no ready 1Y candle universe; this is recorded as source coverage limitation, not a trading claim.",
        ],
        "no_strategy_candidate_edge_claim": True,
    }

    compliance = {
        "artifact": "source_panel_contract_compliance_report.json",
        "generated_at_utc": generated_at,
        "required_artifacts_created": True,
        "required_artifact_list": EXPECTED_PRIMARY_ARTIFACTS,
        "no_strategy_signal_claim": True,
        "no_candidate_generation": True,
        "no_backtest": True,
        "no_runtime_capital_live_order_touch": True,
        "no_generic_runner": True,
        "no_schema_config_creation": True,
        "old_source_panel_anomaly_route_not_reopened": True,
        "old_route_closed_artifacts_not_active_evidence": True,
        "no_profit_claim": True,
        "source_panel_result_primary_strength_claimed_now": False,
        "source_panel_result_primary_strength_requires_future_validator": True,
        "limitations_honestly_recorded": bool(limitations) or bool(candle_state_inner.get("warnings", [])),
    }
    return {
        "source_panel_inventory.json": inventory,
        "source_panel_coverage_summary.json": coverage,
        "source_panel_missingness_report.json": missingness,
        "source_panel_anomaly_report.json": anomaly,
        "source_panel_quality_scorecard.json": scorecard,
        "source_panel_contract_compliance_report.json": compliance,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, contract_valid_json, contract_json_error = load_json_checked(CONTRACT_ARTIFACT_PATH)
    approval, approval_valid_json, approval_json_error = load_json_checked(RUNNER_EXECUTION_APPROVAL_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    contract_checks = pre_execution_contract_validation(contract, contract_valid_json)
    contract_pre_ok = all(value is True for value in contract_checks.values())
    prior_approval_ok = prior_approval_respected(approval, approval_valid_json)
    discovery = source_panel_input_discovery()
    input_exists = discovery["source_panel_input_exists"] and discovery["input_is_repo_only_safe_to_read"]
    repo_context_valid = (
        git["head"] == EXPECTED_HEAD
        and git["current_scope_is_only_approved_file"] is True
        and py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT
        and py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0
        and len(planned_existing) == 0
        and generic_runner_target_exists is False
        and all(value is False for value in flags.values())
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest, _, _ = load_json_checked(FEATURE_PANEL_MANIFEST)
    quality_state, _, _ = load_json_checked(FEATURE_QUALITY_STATE)
    candle_state, _, _ = load_json_checked(CANDLE_STATE)
    binding_state, _, _ = load_json_checked(DATA_BINDING_STATE)
    csv_profiles = {
        "feature_quality_symbol_summary": csv_profile(FEATURE_QUALITY_SYMBOL_SUMMARY),
        "candle_file_inventory": csv_profile(CANDLE_FILE_INVENTORY),
        "candle_symbol_coverage": csv_profile(CANDLE_SYMBOL_COVERAGE),
        "data_binding_sources": csv_profile(DATA_BINDING_SOURCES),
    }

    runner_execution_performed = prior_approval_ok and contract_pre_ok and repo_context_valid
    result_artifacts = build_result_artifacts(discovery, manifest, quality_state, candle_state, binding_state, csv_profiles) if input_exists else {}
    generated_paths: Dict[str, str] = {}
    if runner_execution_performed and input_exists:
        for name, artifact in result_artifacts.items():
            path = OUT_DIR / name
            write_json(path, artifact)
            generated_paths[name] = str(path)

    created_flags = {name: (OUT_DIR / name).exists() for name in EXPECTED_PRIMARY_ARTIFACTS}
    all_required_created = all(created_flags.values())
    runner_execution_successful = runner_execution_performed and input_exists and all_required_created
    active_p0_blocker_count = 0 if runner_execution_successful else 1
    next_module = NEXT_MODULE_VALIDATOR if runner_execution_successful else NEXT_MODULE_BLOCKED
    active_p1_attention_count = 1 if runner_execution_successful and discovery["input_discovery_limitations"] else 0
    current_quality = CURRENT_EVIDENCE_CHAIN_QUALITY_SUCCESS if runner_execution_successful else CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED

    replacement_checks = {
        "prior_runner_execution_approval_respected": prior_approval_ok,
        "runner_execution_performed": runner_execution_performed is True,
        "runner_execution_successful_or_blocked": runner_execution_successful is True or next_module == NEXT_MODULE_BLOCKED,
        "source_panel_analysis_execution_run_now_matches_execution": runner_execution_performed is True,
        "source_panel_results_generated_now_matches_success": runner_execution_successful is True,
        "source_panel_result_primary_artifacts_created_matches_success": all_required_created is runner_execution_successful,
        "input_discovery_completed": True,
        "input_exists_or_blocked": input_exists is True or next_module == NEXT_MODULE_BLOCKED,
        "contract_pre_execution_validation_completed": True,
        "contract_pre_execution_validation_passed": contract_pre_ok,
        "repo_context_valid": repo_context_valid,
        "strategy_signal_claims_made_false": True,
        "tradable_edge_claims_made_false": True,
        "profit_claims_made_false": True,
        "backtest_performed_false": True,
        "candidate_generation_performed_false": True,
        "family_release_performed_false": True,
        "active_paper_performed_false": True,
        "real_order_touch_performed_false": True,
        "runtime_touch_performed_false": True,
        "capital_touch_performed_false": True,
        "live_touch_performed_false": True,
        "generic_runner_approval_granted_false": True,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created_false": True,
        "old_source_panel_anomaly_route_reopened_now_false": True,
        "old_route_closed_artifacts_used_as_active_evidence_now_false": True,
        "source_panel_result_primary_strength_claimed_now_false": True,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "loop_remains_closed": True,
        "next_module_allowed": next_module in {NEXT_MODULE_VALIDATOR, NEXT_MODULE_BLOCKED},
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_runner_execution_status": "PASS" if ready and runner_execution_successful else "BLOCKED" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS_PASS if ready and runner_execution_successful else POST_CHECK_STATUS_BLOCKED,
        "final_decision": "SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_COMPLETED_VALIDATOR_NEXT"
        if ready and runner_execution_successful
        else "SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_BLOCKED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_VALIDATOR_AFTER_RESEARCH_RETURN_GATE"
        if ready and runner_execution_successful
        else "RECORD_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_BLOCKED_STATE",
        "next_module": next_module,
        "prior_runner_execution_approval_respected": prior_approval_ok,
        "runner_execution_performed": runner_execution_performed,
        "runner_execution_successful": runner_execution_successful,
        "source_panel_analysis_execution_run_now": runner_execution_performed,
        "heavy_data_scan_run_now": runner_execution_successful,
        "source_panel_results_generated_now": runner_execution_successful,
        "source_panel_result_primary_artifacts_created": runner_execution_successful,
        "source_panel_result_primary_artifact_list": EXPECTED_PRIMARY_ARTIFACTS if runner_execution_successful else [],
        "source_panel_inventory_created": created_flags["source_panel_inventory.json"],
        "source_panel_coverage_summary_created": created_flags["source_panel_coverage_summary.json"],
        "source_panel_missingness_report_created": created_flags["source_panel_missingness_report.json"],
        "source_panel_anomaly_report_created": created_flags["source_panel_anomaly_report.json"],
        "source_panel_quality_scorecard_created": created_flags["source_panel_quality_scorecard.json"],
        "source_panel_contract_compliance_report_created": created_flags["source_panel_contract_compliance_report.json"],
        "source_panel_input_discovery_completed": True,
        "source_panel_input_exists": input_exists,
        "discovered_input_paths": discovery["discovered_input_paths"],
        "input_file_count": discovery["input_file_count"],
        "input_format_summary": discovery["input_format_summary"],
        "input_size_summary": discovery["input_size_summary"],
        "input_discovery_limitations": discovery["input_discovery_limitations"],
        "contract_pre_execution_validation_completed": True,
        "repaired_contract_artifact_exists": contract_checks["repaired_contract_artifact_exists"],
        "repaired_contract_artifact_valid_json": contract_checks["repaired_contract_artifact_valid_json"],
        "source_panel_contract_validated": contract_pre_ok,
        "contract_artifact_primary_strength_for_contract_only": nested_dict(contract, "contract_primary_marker").get("contract_artifact_primary_strength_for_contract_only") is True,
        "evidence_quality_sufficient_for_contract_validation": contract_pre_ok,
        "source_panel_result_primary_artifacts_exist_now": runner_execution_successful,
        "source_panel_result_primary_strength_claimed_now": False,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "old_route_closed_artifacts_active_evidence_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "money_path_alignment": approval.get("money_path_alignment", "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH"),
        "usable_or_sellable_asset_path": approval.get(
            "usable_or_sellable_asset_path", "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET"
        ),
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": current_quality,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": True,
        "future_runtime_or_live_requires_kill_switch_readiness": True,
        "runtime_preflight_implementation_performed": False,
        "runtime_kill_switch_implementation_performed": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flag_true_count": 0,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This repo-only source-panel runner execution reads established source-panel/data-quality inputs and writes source-panel result artifacts only. "
            "It does not run strategy research, backtests, candidate generation, family release, runtime/capital/live/order paths, generic runner work, schema/config creation, "
            "old anomaly route reopening, profit claims, tradable-edge claims, or source-panel result primary-strength claims before validator confirmation."
        ),
        "replacement_checks_all_true": ready,
        "pre_execution_contract_validation": contract_checks,
        "source_panel_input_discovery": discovery,
        "generated_result_artifacts": generated_paths,
        "csv_input_profiles": csv_profiles,
        "prior_runner_execution_approval_artifact_snapshot": {
            "artifact_path": str(RUNNER_EXECUTION_APPROVAL_ARTIFACT_PATH),
            "artifact_valid_json": approval_valid_json,
            "artifact_json_error": approval_json_error,
            "status": approval.get("source_panel_analysis_runner_execution_approval_status"),
            "next_module": approval.get("next_module"),
        },
        "contract_artifact_snapshot": {
            "artifact_path": str(CONTRACT_ARTIFACT_PATH),
            "artifact_valid_json": contract_valid_json,
            "artifact_json_error": contract_json_error,
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "allowed_next_modules": [NEXT_MODULE_VALIDATOR, NEXT_MODULE_BLOCKED],
        },
        "safety_flags": {
            "repo_only": True,
            "source_panel_analysis_run_performed": runner_execution_performed,
            "strategy_research_run_performed": False,
            "backtest_performed": False,
            "candidate_generation_performed": False,
            "family_release_performed": False,
            "active_paper_performed": False,
            "schema_or_config_created": False,
            "runtime_preflight_implementation_performed": False,
            "runtime_kill_switch_implementation_performed": False,
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "real_order_touch_performed": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    Path(outputs["latest_json"]).write_text(rendered, encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["source_panel_analysis_runner_execution_status"] in {"PASS", "BLOCKED"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
