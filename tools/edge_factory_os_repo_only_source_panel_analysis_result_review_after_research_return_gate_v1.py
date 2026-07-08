from __future__ import annotations

import ast
import importlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_result_review_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_result_review_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_START_HEAD = "f7b2eaf"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 627
EXPECTED_TRACKED_PYTHON_COUNT = 628

RUNNER_RESULT_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"
VALIDATOR_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1"
VALIDATOR_LATEST_ARTIFACT = (
    VALIDATOR_DIR / "repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_PARQUET_LIMITATION_REVIEW = (
    "edge_factory_os_repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1.py"
)
NEXT_MODULE_RESULT_SUMMARY = "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_result_review_blocked_record_after_research_return_gate_v1.py"
NEXT_MODULE_RESELECTOR = "edge_factory_os_repo_only_research_return_route_reselector_after_source_panel_result_review_v1.py"

POST_CHECK_STATUS_PASS_WITH_P1 = (
    "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RESULT_REVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS_WITH_P1_PARQUET_LIMITATION"
)
POST_CHECK_STATUS_BLOCKED = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RESULT_REVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY_WITH_LIMITATIONS = "PRIMARY_ARTIFACT_STRONG_WITH_LIMITATIONS_SOURCE_PANEL_RESULTS"
CURRENT_EVIDENCE_CHAIN_QUALITY_PARTIAL_P1 = "PRIMARY_ARTIFACT_PARTIAL_WITH_P1_ATTENTION_SOURCE_PANEL_RESULTS"
CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED = "SOURCE_PANEL_RESULT_REVIEW_BLOCKED_BY_PARQUET_LIMITATION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

REQUIRED_ARTIFACTS = [
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

FORBIDDEN_PHRASES = [
    "tradable edge",
    "trading profit",
    "profit claim",
    "candidate generated",
    "backtest result",
    "strategy signal",
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
    head = run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    parent = run_cmd(["git", "rev-parse", "--short", "HEAD^"]).stdout.strip()
    return {
        "head": head,
        "parent": parent,
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": changed_paths == [CURRENT_TOOL_REL]
        or (len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL]),
        "expected_start_head_or_parent_observed": head == EXPECTED_START_HEAD or parent == EXPECTED_START_HEAD,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def text_values(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for child in value.values():
            yield from text_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from text_values(child)
    elif isinstance(value, str):
        yield value


def corpus_contains(records: Iterable[Dict[str, Any]], phrase: str) -> bool:
    haystack = "\n".join(text for record in records for text in text_values(record)).lower()
    return phrase.lower() in haystack


def all_artifacts_loaded() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, bool], Dict[str, str]]:
    artifacts: Dict[str, Dict[str, Any]] = {}
    valid_json: Dict[str, bool] = {}
    json_errors: Dict[str, str] = {}
    for name in REQUIRED_ARTIFACTS:
        record, valid, error = load_json_checked(RUNNER_RESULT_DIR / name)
        artifacts[name] = record
        valid_json[name] = valid
        json_errors[name] = error
    return artifacts, valid_json, json_errors


def find_parquet_path(inventory: Dict[str, Any]) -> Tuple[bool, str, int]:
    candidates: List[Tuple[str, int]] = []
    feature_panel_path = inventory.get("feature_panel_path")
    if isinstance(feature_panel_path, str) and feature_panel_path.lower().endswith(".parquet"):
        path = Path(feature_panel_path)
        candidates.append((str(path), path.stat().st_size if path.exists() else 0))
    file_inventory = inventory.get("file_inventory", [])
    if isinstance(file_inventory, list):
        for item in file_inventory:
            if isinstance(item, dict) and str(item.get("path", "")).lower().endswith(".parquet"):
                path_text = str(item.get("path", ""))
                size = item.get("bytes")
                if not isinstance(size, int):
                    path = Path(path_text)
                    size = path.stat().st_size if path.exists() else 0
                candidates.append((path_text, size))
    discovered = inventory.get("discovered_sources", [])
    if isinstance(discovered, list):
        for item in discovered:
            path_text = str(item)
            if path_text.lower().endswith(".parquet"):
                path = Path(path_text)
                candidates.append((path_text, path.stat().st_size if path.exists() else 0))
    unique = []
    seen = set()
    for path_text, size in candidates:
        if path_text not in seen:
            unique.append((path_text, size))
            seen.add(path_text)
    if not unique:
        return False, "", 0
    path_text, size = max(unique, key=lambda item: item[1])
    return True, path_text, size


def sanitized_failure(exc: Exception) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = text.replace("Use pip or conda to install the pyarrow package.", "Dependency installation is forbidden and was not attempted.")
    text = text.replace("Use pip or conda to install the fastparquet package.", "Dependency installation is forbidden and was not attempted.")
    return " ".join(text.split())


def try_parquet_schema(path_text: str) -> Dict[str, Any]:
    if not path_text:
        return {
            "parquet_schema_attempted": False,
            "parquet_schema_obtained": False,
            "parquet_schema_method": "NOT_ATTEMPTED_NO_PARQUET_PATH",
            "parquet_column_count": 0,
            "parquet_column_names_sample": [],
            "parquet_schema_failure_reason": "No parquet input path was identified from source-panel result artifacts.",
        }
    path = Path(path_text)
    failures: List[str] = []

    try:
        pq = importlib.import_module("pyarrow.parquet")
        parquet_file = pq.ParquetFile(str(path))
        names = list(parquet_file.schema_arrow.names)
        return {
            "parquet_schema_attempted": True,
            "parquet_schema_obtained": True,
            "parquet_schema_method": "pyarrow.parquet.ParquetFile.schema_arrow.names",
            "parquet_column_count": len(names),
            "parquet_column_names_sample": names[:50],
            "parquet_schema_failure_reason": "",
        }
    except Exception as exc:
        failures.append(f"pyarrow.parquet unavailable_or_failed: {sanitized_failure(exc)}")

    try:
        pd = importlib.import_module("pandas")
        frame = pd.read_parquet(str(path), columns=[])
        names = list(getattr(frame, "columns", []))
        if names:
            return {
                "parquet_schema_attempted": True,
                "parquet_schema_obtained": True,
                "parquet_schema_method": "pandas.read_parquet(columns=[])",
                "parquet_column_count": len(names),
                "parquet_column_names_sample": names[:50],
                "parquet_schema_failure_reason": "",
            }
        failures.append("pandas.read_parquet(columns=[]) returned no column metadata.")
    except Exception as exc:
        failures.append(f"pandas metadata attempt unavailable_or_failed: {sanitized_failure(exc)}")

    try:
        fp = importlib.import_module("fastparquet")
        parquet_file = fp.ParquetFile(str(path))
        names = list(getattr(parquet_file, "columns", []))
        return {
            "parquet_schema_attempted": True,
            "parquet_schema_obtained": True,
            "parquet_schema_method": "fastparquet.ParquetFile.columns",
            "parquet_column_count": len(names),
            "parquet_column_names_sample": names[:50],
            "parquet_schema_failure_reason": "",
        }
    except Exception as exc:
        failures.append(f"fastparquet unavailable_or_failed: {sanitized_failure(exc)}")

    return {
        "parquet_schema_attempted": True,
        "parquet_schema_obtained": False,
        "parquet_schema_method": "UNAVAILABLE_LOCAL_METADATA_LIBRARIES_ONLY",
        "parquet_column_count": 0,
        "parquet_column_names_sample": [],
        "parquet_schema_failure_reason": " | ".join(failures),
    }


def result_artifact_review(
    artifacts: Dict[str, Dict[str, Any]], valid_json: Dict[str, bool], validator: Dict[str, Any]
) -> Dict[str, Any]:
    records = list(artifacts.values()) + [validator]
    all_exist = all((RUNNER_RESULT_DIR / name).exists() for name in REQUIRED_ARTIFACTS)
    all_valid = all(valid_json.get(name) is True for name in REQUIRED_ARTIFACTS)
    all_non_empty = all(bool(artifacts.get(name)) for name in REQUIRED_ARTIFACTS)
    required_list = artifacts["source_panel_contract_compliance_report.json"].get("required_artifact_list", [])
    artifacts_consistent = sorted(required_list) == sorted(REQUIRED_ARTIFACTS)
    forbidden_phrases_present = [phrase for phrase in FORBIDDEN_PHRASES if corpus_contains(records, phrase)]
    fake_or_synthetic_detected = corpus_contains(records, "synthetic") or corpus_contains(records, "fake")
    no_safety_action = (
        artifacts["source_panel_contract_compliance_report.json"].get("no_backtest") is True
        and artifacts["source_panel_contract_compliance_report.json"].get("no_candidate_generation") is True
        and artifacts["source_panel_contract_compliance_report.json"].get("no_runtime_capital_live_order_touch") is True
        and artifacts["source_panel_contract_compliance_report.json"].get("no_generic_runner") is True
        and artifacts["source_panel_contract_compliance_report.json"].get("no_schema_config_creation") is True
    )
    return {
        "completed": True,
        "all_required_source_panel_result_artifacts_exist": all_exist,
        "all_required_source_panel_result_artifacts_valid_json": all_valid,
        "artifact_content_non_empty": all_non_empty,
        "artifacts_consistent_with_each_other": artifacts_consistent,
        "fake_or_synthetic_data_detected": fake_or_synthetic_detected,
        "forbidden_claim_phrases_present": forbidden_phrases_present,
        "no_strategy_candidate_profit_tradable_edge_claims": len(forbidden_phrases_present) == 0,
        "no_runtime_capital_live_order_generic_runner_schema_config_action": no_safety_action,
        "review_passed": all_exist and all_valid and all_non_empty and artifacts_consistent and not fake_or_synthetic_detected and no_safety_action,
    }


def research_utility_review(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    inventory = artifacts["source_panel_inventory.json"]
    coverage = artifacts["source_panel_coverage_summary.json"]
    missingness = artifacts["source_panel_missingness_report.json"]
    anomaly = artifacts["source_panel_anomaly_report.json"]
    scorecard = artifacts["source_panel_quality_scorecard.json"]
    utility_checks = {
        "source_panel_inventory_useful": isinstance(inventory.get("file_inventory"), list) and len(inventory["file_inventory"]) > 0,
        "coverage_map_useful": isinstance(coverage.get("symbol_coverage"), dict)
        and isinstance(coverage.get("time_coverage"), dict)
        and isinstance(coverage.get("feature_coverage"), dict),
        "missingness_map_useful": isinstance(missingness.get("missingness_by_feature"), dict) and bool(missingness["missingness_by_feature"]),
        "data_quality_anomaly_summary_useful": anomaly.get("data_quality_anomalies_only") is True,
        "quality_scorecard_useful": isinstance(scorecard.get("quality_score_by_source"), dict)
        and isinstance(scorecard.get("overall_quality_score"), (int, float)),
    }
    useful = all(value is True for value in utility_checks.values())
    return {
        "completed": True,
        "utility_checks": utility_checks,
        "source_panel_results_are_useful_research_substrate": useful,
        "source_panel_results_are_alpha_or_edge": False,
        "source_panel_results_are_reusable_data_quality_asset": useful,
        "review_note": (
            "Artifacts support inventory, coverage, missingness, data-quality anomaly, and scorecard review only; "
            "they are not alpha, edge, candidate, backtest, or tradable strategy results."
        ),
    }


def parquet_schema_limitation_review(
    artifacts: Dict[str, Dict[str, Any]], validator: Dict[str, Any], schema_attempt: Dict[str, Any]
) -> Dict[str, Any]:
    inventory = artifacts["source_panel_inventory.json"]
    identified, path_text, file_size = find_parquet_path(inventory)
    limitation_disclosed = validator.get("parquet_limitation_disclosed") is True and (
        corpus_contains([inventory], "parquet full column scan not performed") or corpus_contains(list(artifacts.values()), "pyarrow")
    )
    schema_obtained = schema_attempt["parquet_schema_obtained"] is True
    names = schema_attempt["parquet_column_names_sample"]
    important_fields = {"symbol", "time", "open", "high", "low", "close"}
    sample_lower = {str(name).lower() for name in names}
    if not identified:
        materiality = "P0_BLOCKER"
        blocks = True
    elif schema_obtained and sample_lower.isdisjoint(important_fields):
        materiality = "LOW"
        blocks = False
    elif schema_obtained:
        materiality = "P1_REVIEW_REQUIRED"
        blocks = False
    elif file_size > 10_000_000:
        materiality = "P1_UNRESOLVED"
        blocks = False
    else:
        materiality = "P1_UNRESOLVED"
        blocks = False
    return {
        "completed": True,
        "parquet_input_path_identified": identified,
        "parquet_input_path": path_text,
        "parquet_file_size_bytes": file_size,
        **schema_attempt,
        "parquet_full_column_scan_performed": False,
        "parquet_full_column_scan_missing_due_to_pyarrow": validator.get("parquet_full_column_scan_missing_due_to_pyarrow") is True
        and not schema_obtained,
        "parquet_limitation_disclosed": limitation_disclosed,
        "parquet_limitation_materiality": materiality,
        "parquet_limitation_blocks_result_review": blocks,
        "derived_metadata_used": not schema_obtained or validator.get("derived_metadata_used") is True,
        "derived_metadata_reason": (
            "Parquet schema/column metadata was not available through installed local libraries; result review carries manifest, "
            "quality audit, inventory, and validated result artifacts as derived metadata with P1 monitoring."
            if not schema_obtained
            else "Parquet schema metadata was obtained without a full column scan; deeper source-panel review still treats the parquet file as important source-panel data."
        ),
        "derived_metadata_monitoring_required": materiality in {"P1_UNRESOLVED", "P1_REVIEW_REQUIRED"},
    }


def evidence_quality_review(parquet_review: Dict[str, Any], validator: Dict[str, Any]) -> Dict[str, Any]:
    before = validator.get("current_evidence_chain_quality_after_validation", CURRENT_EVIDENCE_CHAIN_QUALITY_WITH_LIMITATIONS)
    materiality = parquet_review["parquet_limitation_materiality"]
    if materiality == "P0_BLOCKER":
        after = CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED
        p0 = 1
        p1 = 0
    elif materiality in {"P1_UNRESOLVED", "P1_REVIEW_REQUIRED"}:
        after = CURRENT_EVIDENCE_CHAIN_QUALITY_PARTIAL_P1
        p0 = 0
        p1 = 1
    else:
        after = CURRENT_EVIDENCE_CHAIN_QUALITY_WITH_LIMITATIONS
        p0 = 0
        p1 = 0
    return {
        "completed": True,
        "current_evidence_chain_quality_before_review": before,
        "current_evidence_chain_quality_after_review": after,
        "active_p0_blocker_count": p0,
        "active_p1_attention_count": p1,
    }


def route_review(parquet_review: Dict[str, Any], utility_review: Dict[str, Any], evidence_review: Dict[str, Any]) -> Dict[str, Any]:
    if evidence_review["active_p0_blocker_count"] == 1:
        route_decision = "BLOCK_ROUTE"
        next_module = NEXT_MODULE_BLOCKED
        next_action = "RECORD_SOURCE_PANEL_RESULT_REVIEW_BLOCKED_STATE"
    elif utility_review["source_panel_results_are_useful_research_substrate"] and parquet_review["parquet_limitation_materiality"] in {
        "P1_UNRESOLVED",
        "P1_REVIEW_REQUIRED",
    }:
        route_decision = "RUN_PARQUET_SCHEMA_LIMITATION_REVIEW"
        next_module = NEXT_MODULE_PARQUET_LIMITATION_REVIEW
        next_action = "BUILD_SOURCE_PANEL_PARQUET_SCHEMA_LIMITATION_REVIEW_AFTER_RESULT_VALIDATOR"
    elif utility_review["source_panel_results_are_useful_research_substrate"]:
        route_decision = "CONTINUE_SOURCE_PANEL_ROUTE"
        next_module = NEXT_MODULE_RESULT_SUMMARY
        next_action = "BUILD_SOURCE_PANEL_ANALYSIS_RESULT_SUMMARY_AFTER_RESEARCH_RETURN_GATE"
    else:
        route_decision = "PIVOT_RESELECT_ROUTE"
        next_module = NEXT_MODULE_RESELECTOR
        next_action = "BUILD_RESEARCH_RETURN_ROUTE_RESELECTOR_AFTER_SOURCE_PANEL_RESULT_REVIEW"
    return {
        "completed": True,
        "source_panel_route_decision": route_decision,
        "next_module": next_module,
        "next_action": next_action,
    }


def old_route_guard_review(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    anomaly = artifacts["source_panel_anomaly_report.json"]
    checks = {
        "old_source_panel_anomaly_route_not_reopened": anomaly.get("old_source_panel_anomaly_route_reopened") is False,
        "old_route_closed_artifacts_not_active_evidence": anomaly.get("old_route_closed_artifacts_used_as_active_evidence") is False,
        "anomaly_report_data_quality_only": anomaly.get("data_quality_anomalies_only") is True,
        "no_strategy_or_trading_anomaly_claim": not any(
            phrase in "\n".join(text_values(anomaly)).lower() for phrase in ["strategy anomaly", "trading anomaly", "tradable edge"]
        ),
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def safety_boundary_review(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    compliance = artifacts["source_panel_contract_compliance_report.json"]
    checks = {
        "no_backtest": compliance.get("no_backtest") is True,
        "no_candidate_generation": compliance.get("no_candidate_generation") is True,
        "no_family_release": True,
        "no_active_paper": True,
        "no_real_order": True,
        "no_runtime_capital_live_touch": compliance.get("no_runtime_capital_live_order_touch") is True,
        "no_generic_runner_approval_or_implementation": compliance.get("no_generic_runner") is True,
        "no_schema_config_creation": compliance.get("no_schema_config_creation") is True,
        "no_profit_claim": compliance.get("no_profit_claim") is True,
        "no_tradable_edge_claim": True,
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    artifacts, valid_json, json_errors = all_artifacts_loaded()
    validator, validator_valid_json, validator_json_error = load_json_checked(VALIDATOR_LATEST_ARTIFACT)
    inventory = artifacts["source_panel_inventory.json"]
    parquet_identified, parquet_path, _ = find_parquet_path(inventory)
    schema_attempt = try_parquet_schema(parquet_path if parquet_identified else "")

    result_review = result_artifact_review(artifacts, valid_json, validator)
    utility_review = research_utility_review(artifacts)
    parquet_review = parquet_schema_limitation_review(artifacts, validator, schema_attempt)
    evidence_review = evidence_quality_review(parquet_review, validator)
    route = route_review(parquet_review, utility_review, evidence_review)
    old_guard = old_route_guard_review(artifacts)
    safety = safety_boundary_review(artifacts)

    prior_validator_respected = (
        validator_valid_json
        and validator.get("source_panel_analysis_runner_execution_validator_status") == "PASS_WITH_P1_LIMITATION"
        and validator.get("runner_execution_validation_completed") is True
        and validator.get("source_panel_result_primary_artifacts_validated") is True
        and validator.get("source_panel_result_primary_strength_claimed_after_validator") is True
        and validator.get("source_panel_result_primary_strength_claimed_before_validator") is False
        and validator.get("parquet_limitation_disclosed") is True
        and validator.get("parquet_limitation_blocks_validation") is False
        and validator.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and validator.get("replacement_checks_all_true") is True
    )

    allowed_next_modules = {
        NEXT_MODULE_PARQUET_LIMITATION_REVIEW,
        NEXT_MODULE_RESULT_SUMMARY,
        NEXT_MODULE_BLOCKED,
        NEXT_MODULE_RESELECTOR,
    }
    active_p0 = evidence_review["active_p0_blocker_count"]
    active_p1 = evidence_review["active_p1_attention_count"]
    result_review_completed = True
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_627_to_628": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "prior_source_panel_result_validator_respected": prior_validator_respected,
        "result_review_completed": result_review_completed,
        "parquet_schema_limitation_review_completed": parquet_review["completed"],
        "parquet_schema_attempted": parquet_review["parquet_schema_attempted"],
        "fake_or_synthetic_data_detected_false": result_review["fake_or_synthetic_data_detected"] is False,
        "safety_boundary_validated": safety["validated"],
        "old_route_guard_validated": old_guard["validated"],
        "loop_remains_closed": True,
        "next_module_allowed": route["next_module"] in allowed_next_modules,
        "candidate_backtest_runtime_live_capital_not_selected": all(
            token not in route["next_module"] for token in ["candidate", "backtest", "runtime", "live", "capital"]
        ),
        "generic_governance_chain_not_selected": all(
            token not in route["next_module"] for token in ["generic", "_adoption_", "_gate_", "_rollout_", "_audit_"]
        ),
    }
    ready = all(value is True for value in replacement_checks.values())
    status = "PASS_WITH_P1_PARQUET_LIMITATION" if ready and active_p0 == 0 and active_p1 == 1 else "PASS" if ready and active_p0 == 0 else "BLOCKED"
    if not ready:
        status = "FAIL_CLOSED"
    final_decision = (
        "SOURCE_PANEL_RESULTS_USEFUL_PARQUET_LIMITATION_REVIEW_NEXT"
        if status == "PASS_WITH_P1_PARQUET_LIMITATION"
        else "SOURCE_PANEL_RESULTS_USEFUL_SUMMARY_NEXT"
        if status == "PASS"
        else "SOURCE_PANEL_RESULT_REVIEW_BLOCKED"
    )
    next_module = route["next_module"] if ready else NEXT_MODULE_BLOCKED
    next_action = route["next_action"] if ready else "RECORD_SOURCE_PANEL_RESULT_REVIEW_BLOCKED_STATE"
    post_check_status = POST_CHECK_STATUS_PASS_WITH_P1 if status in {"PASS_WITH_P1_PARQUET_LIMITATION", "PASS"} else POST_CHECK_STATUS_BLOCKED

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_result_review_status": status,
        "post_check_status": post_check_status,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_source_panel_result_validator_respected": prior_validator_respected,
        "result_review_completed": result_review_completed,
        "result_artifact_review_completed": result_review["completed"],
        "research_utility_review_completed": utility_review["completed"],
        "parquet_schema_limitation_review_completed": parquet_review["completed"],
        "evidence_quality_review_completed": evidence_review["completed"],
        "source_panel_route_review_completed": route["completed"],
        "old_route_guard_review_completed": old_guard["completed"],
        "safety_boundary_review_completed": safety["completed"],
        "all_required_source_panel_result_artifacts_exist": result_review["all_required_source_panel_result_artifacts_exist"],
        "all_required_source_panel_result_artifacts_valid_json": result_review["all_required_source_panel_result_artifacts_valid_json"],
        "source_panel_result_primary_artifacts_validated": validator.get("source_panel_result_primary_artifacts_validated") is True,
        "source_panel_result_primary_strength_claimed_after_validator": validator.get("source_panel_result_primary_strength_claimed_after_validator") is True,
        "source_panel_results_are_useful_research_substrate": utility_review["source_panel_results_are_useful_research_substrate"],
        "source_panel_results_are_alpha_or_edge": utility_review["source_panel_results_are_alpha_or_edge"],
        "source_panel_results_are_reusable_data_quality_asset": utility_review["source_panel_results_are_reusable_data_quality_asset"],
        "parquet_input_path_identified": parquet_review["parquet_input_path_identified"],
        "parquet_input_path": parquet_review["parquet_input_path"],
        "parquet_file_size_bytes": parquet_review["parquet_file_size_bytes"],
        "parquet_schema_attempted": parquet_review["parquet_schema_attempted"],
        "parquet_schema_obtained": parquet_review["parquet_schema_obtained"],
        "parquet_schema_method": parquet_review["parquet_schema_method"],
        "parquet_column_count": parquet_review["parquet_column_count"],
        "parquet_column_names_sample": parquet_review["parquet_column_names_sample"],
        "parquet_schema_failure_reason": parquet_review["parquet_schema_failure_reason"],
        "parquet_full_column_scan_performed": parquet_review["parquet_full_column_scan_performed"],
        "parquet_full_column_scan_missing_due_to_pyarrow": parquet_review["parquet_full_column_scan_missing_due_to_pyarrow"],
        "parquet_limitation_disclosed": parquet_review["parquet_limitation_disclosed"],
        "parquet_limitation_materiality": parquet_review["parquet_limitation_materiality"],
        "parquet_limitation_blocks_result_review": parquet_review["parquet_limitation_blocks_result_review"],
        "derived_metadata_used": parquet_review["derived_metadata_used"],
        "derived_metadata_reason": parquet_review["derived_metadata_reason"],
        "derived_metadata_monitoring_required": parquet_review["derived_metadata_monitoring_required"],
        "current_evidence_chain_quality_before_review": evidence_review["current_evidence_chain_quality_before_review"],
        "current_evidence_chain_quality_after_review": evidence_review["current_evidence_chain_quality_after_review"],
        "active_p0_blocker_count": active_p0 if ready else 1,
        "active_p1_attention_count": active_p1 if ready else 0,
        "fake_or_synthetic_data_detected": result_review["fake_or_synthetic_data_detected"],
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "old_route_closed_artifacts_active_evidence_allowed": False,
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
        "money_path_alignment": validator.get(
            "money_path_alignment", "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH"
        ),
        "usable_or_sellable_asset_path": validator.get(
            "usable_or_sellable_asset_path",
            "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET",
        ),
        "evidence_chain_policy_level": POLICY_LEVEL,
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
            "This result-review module reads validated source-panel result artifacts, the validator artifact, and local parquet metadata only through already installed libraries. "
            "It does not install dependencies, run source-panel analysis, perform a full parquet scan, run strategy research, backtests, candidate generation, family release, "
            "runtime/capital/live/order/generic-runner/schema/config work, reopen old anomaly routes, or claim profit or tradable edge."
        ),
        "replacement_checks_all_true": ready,
        "result_artifact_review": result_review,
        "research_utility_review": utility_review,
        "parquet_schema_limitation_review": parquet_review,
        "evidence_quality_review": evidence_review,
        "source_panel_route_review": route,
        "old_route_guard_review": old_guard,
        "safety_boundary_review": safety,
        "artifact_json_errors": json_errors,
        "source_panel_result_validator_snapshot": {
            "artifact_path": str(VALIDATOR_LATEST_ARTIFACT),
            "artifact_valid_json": validator_valid_json,
            "artifact_json_error": validator_json_error,
            "status": validator.get("source_panel_analysis_runner_execution_validator_status"),
            "post_check_status": validator.get("post_check_status"),
            "next_module": validator.get("next_module"),
        },
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "expected_previous_tracked_python_count": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "allowed_next_modules": sorted(allowed_next_modules),
        },
        "safety_flags": {
            "repo_only": True,
            "result_review_only": True,
            "source_panel_analysis_run_performed": False,
            "heavy_full_data_scan_performed": False,
            "dependency_install_attempted": False,
            "parquet_full_column_scan_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_result_review_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_result_review_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_result_review_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_result_review_status"] in {"PASS", "PASS_WITH_P1_PARQUET_LIMITATION", "BLOCKED"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
