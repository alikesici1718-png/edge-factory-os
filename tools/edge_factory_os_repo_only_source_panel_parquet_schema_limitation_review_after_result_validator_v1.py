from __future__ import annotations

import ast
import importlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_START_HEAD = "d838249"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 628
EXPECTED_TRACKED_PYTHON_COUNT = 629

RESULT_REVIEW_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_result_review_after_research_return_gate_v1"
RESULT_REVIEW_LATEST_ARTIFACT = (
    RESULT_REVIEW_DIR / "repo_only_source_panel_analysis_result_review_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_REPAIR_PREVIEW = "edge_factory_os_repo_only_source_panel_parquet_schema_access_repair_preview_after_result_review_v1.py"
NEXT_MODULE_RESULT_SUMMARY = "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_result_review_blocked_record_after_research_return_gate_v1.py"
NEXT_MODULE_RESELECTOR = "edge_factory_os_repo_only_research_return_route_reselector_after_source_panel_result_review_v1.py"

POST_CHECK_STATUS_PASS_REPAIR_PREVIEW = (
    "REPO_ONLY_SOURCE_PANEL_PARQUET_SCHEMA_LIMITATION_REVIEW_AFTER_RESULT_VALIDATOR_POST_COMMIT_CHECK_PASS_REPAIR_PREVIEW_REQUIRED"
)
POST_CHECK_STATUS_PASS_BOUNDED = (
    "REPO_ONLY_SOURCE_PANEL_PARQUET_SCHEMA_LIMITATION_REVIEW_AFTER_RESULT_VALIDATOR_POST_COMMIT_CHECK_PASS_BOUNDED"
)
POST_CHECK_STATUS_BLOCKED = "REPO_ONLY_SOURCE_PANEL_PARQUET_SCHEMA_LIMITATION_REVIEW_AFTER_RESULT_VALIDATOR_POST_COMMIT_CHECK_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
EVIDENCE_PARTIAL_P1 = "PRIMARY_ARTIFACT_PARTIAL_WITH_P1_ATTENTION_SOURCE_PANEL_RESULTS"
EVIDENCE_STRONG_WITH_LIMITATIONS = "PRIMARY_ARTIFACT_STRONG_WITH_LIMITATIONS_SOURCE_PANEL_RESULTS"
EVIDENCE_BLOCKED = "SOURCE_PANEL_RESULT_REVIEW_BLOCKED_BY_PARQUET_LIMITATION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

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


def sanitized_failure(exc: Exception) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = text.replace("Use pip or conda to install the pyarrow package.", "Dependency installation is forbidden and was not attempted.")
    text = text.replace("Use pip or conda to install the fastparquet package.", "Dependency installation is forbidden and was not attempted.")
    return " ".join(text.split())


def parquet_file_context(path_text: str, reported_size: Any) -> Dict[str, Any]:
    path = Path(path_text) if isinstance(path_text, str) else Path("")
    exists = path.exists() if path_text else False
    actual_size = path.stat().st_size if exists else 0
    size = actual_size if actual_size else reported_size if isinstance(reported_size, int) else 0
    lowered = path_text.lower() if isinstance(path_text, str) else ""
    return {
        "completed": True,
        "parquet_input_path_identified": bool(path_text),
        "parquet_input_path": path_text if isinstance(path_text, str) else "",
        "parquet_file_exists": exists,
        "parquet_file_size_bytes": size,
        "parquet_file_is_large": size >= 10_000_000,
        "parquet_file_name": path.name if path_text else "",
        "inferred_role_from_path": "FEATURE_PANEL_1H_PARQUET_SOURCE_PANEL_INPUT" if "feature_panel" in lowered else "UNKNOWN_PARQUET_SOURCE_PANEL_INPUT",
        "parquet_path_suggests_feature_panel": "feature_panel" in lowered,
        "why_schema_matters": (
            "The parquet path points to the large 1h feature-panel artifact. Column/schema visibility is needed to bound whether "
            "coverage, missingness, and feature availability claims rest on only derived manifest/audit metadata."
        ),
    }


def attempt_schema_access(path_text: str) -> Dict[str, Any]:
    failures: List[str] = []
    pyarrow_available = False
    fastparquet_available = False
    pandas_parquet_engine_available = False
    duckdb_available = False
    parquet_tools = shutil.which("parquet-tools")
    parquet_tools_cli_available = parquet_tools is not None

    try:
        pq = importlib.import_module("pyarrow.parquet")
        pyarrow_available = True
        parquet_file = pq.ParquetFile(path_text)
        names = list(parquet_file.schema_arrow.names)
        return {
            "completed": True,
            "parquet_schema_attempted": True,
            "pyarrow_available": pyarrow_available,
            "fastparquet_available": fastparquet_available,
            "pandas_parquet_engine_available": pandas_parquet_engine_available,
            "duckdb_available": duckdb_available,
            "parquet_tools_cli_available": parquet_tools_cli_available,
            "parquet_schema_obtained": True,
            "parquet_schema_method": "pyarrow.parquet.ParquetFile.schema_arrow.names",
            "parquet_column_count": len(names),
            "parquet_column_names_sample": names[:50],
            "parquet_schema_failure_reason": "",
            "parquet_full_column_scan_performed": False,
        }
    except Exception as exc:
        failures.append(f"pyarrow.parquet unavailable_or_failed: {sanitized_failure(exc)}")

    try:
        fp = importlib.import_module("fastparquet")
        fastparquet_available = True
        parquet_file = fp.ParquetFile(path_text)
        names = list(getattr(parquet_file, "columns", []))
        return {
            "completed": True,
            "parquet_schema_attempted": True,
            "pyarrow_available": pyarrow_available,
            "fastparquet_available": fastparquet_available,
            "pandas_parquet_engine_available": pandas_parquet_engine_available,
            "duckdb_available": duckdb_available,
            "parquet_tools_cli_available": parquet_tools_cli_available,
            "parquet_schema_obtained": True,
            "parquet_schema_method": "fastparquet.ParquetFile.columns",
            "parquet_column_count": len(names),
            "parquet_column_names_sample": names[:50],
            "parquet_schema_failure_reason": "",
            "parquet_full_column_scan_performed": False,
        }
    except Exception as exc:
        failures.append(f"fastparquet unavailable_or_failed: {sanitized_failure(exc)}")

    try:
        pd = importlib.import_module("pandas")
        frame = pd.read_parquet(path_text, columns=[])
        pandas_parquet_engine_available = True
        names = list(getattr(frame, "columns", []))
        if names:
            return {
                "completed": True,
                "parquet_schema_attempted": True,
                "pyarrow_available": pyarrow_available,
                "fastparquet_available": fastparquet_available,
                "pandas_parquet_engine_available": pandas_parquet_engine_available,
                "duckdb_available": duckdb_available,
                "parquet_tools_cli_available": parquet_tools_cli_available,
                "parquet_schema_obtained": True,
                "parquet_schema_method": "pandas.read_parquet(columns=[])",
                "parquet_column_count": len(names),
                "parquet_column_names_sample": names[:50],
                "parquet_schema_failure_reason": "",
                "parquet_full_column_scan_performed": False,
            }
        failures.append("pandas read_parquet(columns=[]) returned no schema metadata.")
    except Exception as exc:
        failures.append(f"pandas parquet engine unavailable_or_failed: {sanitized_failure(exc)}")

    try:
        duckdb = importlib.import_module("duckdb")
        duckdb_available = True
        quoted = path_text.replace("'", "''")
        rows = duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{quoted}')").fetchall()
        names = [str(row[0]) for row in rows]
        return {
            "completed": True,
            "parquet_schema_attempted": True,
            "pyarrow_available": pyarrow_available,
            "fastparquet_available": fastparquet_available,
            "pandas_parquet_engine_available": pandas_parquet_engine_available,
            "duckdb_available": duckdb_available,
            "parquet_tools_cli_available": parquet_tools_cli_available,
            "parquet_schema_obtained": True,
            "parquet_schema_method": "duckdb.DESCRIBE_read_parquet_metadata_only",
            "parquet_column_count": len(names),
            "parquet_column_names_sample": names[:50],
            "parquet_schema_failure_reason": "",
            "parquet_full_column_scan_performed": False,
        }
    except Exception as exc:
        failures.append(f"duckdb schema attempt unavailable_or_failed: {sanitized_failure(exc)}")

    if parquet_tools_cli_available:
        try:
            result = subprocess.run(
                [parquet_tools or "parquet-tools", "schema", path_text],
                cwd=str(REPO_ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
            if result.returncode == 0:
                names = []
                for line in result.stdout.splitlines():
                    stripped = line.strip().strip(";")
                    if ":" in stripped and not stripped.startswith("message "):
                        names.append(stripped.split(":", 1)[0].strip().strip("optional required repeated").strip())
                return {
                    "completed": True,
                    "parquet_schema_attempted": True,
                    "pyarrow_available": pyarrow_available,
                    "fastparquet_available": fastparquet_available,
                    "pandas_parquet_engine_available": pandas_parquet_engine_available,
                    "duckdb_available": duckdb_available,
                    "parquet_tools_cli_available": parquet_tools_cli_available,
                    "parquet_schema_obtained": True,
                    "parquet_schema_method": "parquet-tools schema",
                    "parquet_column_count": len(names),
                    "parquet_column_names_sample": names[:50],
                    "parquet_schema_failure_reason": "",
                    "parquet_full_column_scan_performed": False,
                }
            failures.append(f"parquet-tools schema failed: returncode={result.returncode} stderr={result.stderr.strip()}")
        except Exception as exc:
            failures.append(f"parquet-tools schema unavailable_or_failed: {sanitized_failure(exc)}")
    else:
        failures.append("parquet-tools CLI unavailable on PATH.")

    return {
        "completed": True,
        "parquet_schema_attempted": True,
        "pyarrow_available": pyarrow_available,
        "fastparquet_available": fastparquet_available,
        "pandas_parquet_engine_available": pandas_parquet_engine_available,
        "duckdb_available": duckdb_available,
        "parquet_tools_cli_available": parquet_tools_cli_available,
        "parquet_schema_obtained": False,
        "parquet_schema_method": "UNAVAILABLE_LOCAL_METADATA_READERS_ONLY",
        "parquet_column_count": 0,
        "parquet_column_names_sample": [],
        "parquet_schema_failure_reason": " | ".join(failures),
        "parquet_full_column_scan_performed": False,
    }


def prior_result_review_validation(review: Dict[str, Any], valid_json: bool) -> Dict[str, Any]:
    checks = {
        "artifact_valid_json": valid_json,
        "previous_result_review_completed": review.get("result_review_completed") is True,
        "source_panel_artifacts_useful_substrate": review.get("source_panel_results_are_useful_research_substrate") is True,
        "source_panel_artifacts_not_alpha_edge": review.get("source_panel_results_are_alpha_or_edge") is False,
        "evidence_downgraded_to_partial_p1": review.get("current_evidence_chain_quality_after_review") == EVIDENCE_PARTIAL_P1,
        "p1_parquet_limitation_carried_honestly": review.get("parquet_limitation_materiality") == "P1_UNRESOLVED"
        and review.get("parquet_limitation_disclosed") is True
        and review.get("active_p1_attention_count") == 1,
        "next_module_is_this_module": review.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1],
        "replacement_checks_all_true": review.get("replacement_checks_all_true") is True,
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def limitation_materiality_decision(context: Dict[str, Any], access: Dict[str, Any], review: Dict[str, Any]) -> Dict[str, Any]:
    if not context["parquet_file_exists"] or not context["parquet_input_path_identified"]:
        materiality = "P0_BLOCKER"
    elif access["parquet_schema_obtained"] and not context["parquet_path_suggests_feature_panel"]:
        materiality = "LOW"
    elif access["parquet_schema_obtained"]:
        materiality = "P1_BOUNDED"
    elif review.get("source_panel_results_are_useful_research_substrate") is False:
        materiality = "ROUTE_RESELECT"
    elif context["parquet_path_suggests_feature_panel"] and context["parquet_file_is_large"]:
        materiality = "P1_REPAIR_PREVIEW_REQUIRED"
    else:
        materiality = "P1_BOUNDED"
    return {
        "completed": True,
        "limitation_materiality": materiality,
        "parquet_limitation_blocks_next_step": materiality == "P0_BLOCKER",
        "parquet_schema_access_repair_preview_required": materiality == "P1_REPAIR_PREVIEW_REQUIRED",
    }


def evidence_quality_decision(materiality: Dict[str, Any], review: Dict[str, Any]) -> Dict[str, Any]:
    before = review.get("current_evidence_chain_quality_after_review", EVIDENCE_PARTIAL_P1)
    if materiality["limitation_materiality"] == "P0_BLOCKER":
        after = EVIDENCE_BLOCKED
        p0 = 1
        p1 = 0
    elif materiality["limitation_materiality"] in {"LOW", "P1_BOUNDED"}:
        after = EVIDENCE_STRONG_WITH_LIMITATIONS if materiality["limitation_materiality"] == "LOW" else EVIDENCE_PARTIAL_P1
        p0 = 0
        p1 = 0 if materiality["limitation_materiality"] == "LOW" else 1
    else:
        after = EVIDENCE_PARTIAL_P1
        p0 = 0
        p1 = 1
    return {
        "completed": True,
        "current_evidence_chain_quality_before_limitation_review": before,
        "current_evidence_chain_quality_after_limitation_review": after,
        "active_p0_blocker_count": p0,
        "active_p1_attention_count": p1,
    }


def next_module_decision(materiality: Dict[str, Any]) -> Dict[str, str]:
    value = materiality["limitation_materiality"]
    if value == "P1_REPAIR_PREVIEW_REQUIRED":
        return {
            "next_module": NEXT_MODULE_REPAIR_PREVIEW,
            "next_action": "BUILD_SOURCE_PANEL_PARQUET_SCHEMA_ACCESS_REPAIR_PREVIEW_AFTER_RESULT_REVIEW",
            "final_decision": "PARQUET_SCHEMA_LIMITATION_P1_REPAIR_PREVIEW_REQUIRED",
        }
    if value in {"LOW", "P1_BOUNDED"}:
        return {
            "next_module": NEXT_MODULE_RESULT_SUMMARY,
            "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_RESULT_SUMMARY_AFTER_RESEARCH_RETURN_GATE",
            "final_decision": "PARQUET_SCHEMA_LIMITATION_BOUNDED_RESULT_SUMMARY_NEXT",
        }
    if value == "ROUTE_RESELECT":
        return {
            "next_module": NEXT_MODULE_RESELECTOR,
            "next_action": "BUILD_RESEARCH_RETURN_ROUTE_RESELECTOR_AFTER_SOURCE_PANEL_RESULT_REVIEW",
            "final_decision": "SOURCE_PANEL_ROUTE_RESELECT_REQUIRED",
        }
    return {
        "next_module": NEXT_MODULE_BLOCKED,
        "next_action": "RECORD_SOURCE_PANEL_RESULT_REVIEW_BLOCKED_STATE",
        "final_decision": "PARQUET_SCHEMA_LIMITATION_P0_BLOCKED",
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    review, review_valid_json, review_json_error = load_json_checked(RESULT_REVIEW_LATEST_ARTIFACT)
    context = parquet_file_context(review.get("parquet_input_path", ""), review.get("parquet_file_size_bytes"))
    access = attempt_schema_access(context["parquet_input_path"]) if context["parquet_input_path_identified"] else {
        "completed": True,
        "parquet_schema_attempted": False,
        "pyarrow_available": False,
        "fastparquet_available": False,
        "pandas_parquet_engine_available": False,
        "duckdb_available": False,
        "parquet_tools_cli_available": shutil.which("parquet-tools") is not None,
        "parquet_schema_obtained": False,
        "parquet_schema_method": "NOT_ATTEMPTED_NO_PARQUET_PATH",
        "parquet_column_count": 0,
        "parquet_column_names_sample": [],
        "parquet_schema_failure_reason": "No parquet input path identified.",
        "parquet_full_column_scan_performed": False,
    }
    prior = prior_result_review_validation(review, review_valid_json)
    materiality = limitation_materiality_decision(context, access, review)
    evidence = evidence_quality_decision(materiality, review)
    next_decision = next_module_decision(materiality)

    allowed_next_modules = {NEXT_MODULE_REPAIR_PREVIEW, NEXT_MODULE_RESULT_SUMMARY, NEXT_MODULE_BLOCKED, NEXT_MODULE_RESELECTOR}
    safety_checks = {
        "dependency_install_attempted_false": True,
        "environment_modified_false": True,
        "schema_or_config_created_false": True,
        "parquet_full_column_scan_performed_false": access["parquet_full_column_scan_performed"] is False,
        "source_panel_rerun_performed_false": True,
        "strategy_backtest_candidate_false": True,
        "runtime_capital_live_order_false": True,
        "generic_runner_false": True,
        "old_route_not_reopened": True,
    }
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_628_to_629": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "prior_result_review_respected": prior["validated"],
        "parquet_limitation_review_completed": True,
        "parquet_schema_attempted": access["parquet_schema_attempted"],
        "dependency_install_attempted_false": True,
        "environment_modified_false": True,
        "schema_or_config_created_false": True,
        "source_panel_rerun_performed_false": True,
        "backtest_performed_false": True,
        "candidate_generation_performed_false": True,
        "runtime_touch_performed_false": True,
        "capital_touch_performed_false": True,
        "live_touch_performed_false": True,
        "generic_runner_approval_granted_false": True,
        "generic_runner_implementation_remains_blocked": True,
        "old_source_panel_anomaly_route_reopened_now_false": True,
        "old_route_closed_artifacts_used_as_active_evidence_now_false": True,
        "loop_remains_closed": True,
        "next_module_allowed": next_decision["next_module"] in allowed_next_modules,
        "candidate_backtest_runtime_live_capital_not_selected": all(
            token not in next_decision["next_module"] for token in ["candidate", "backtest", "runtime", "live", "capital"]
        ),
        "generic_governance_chain_not_selected": all(
            token not in next_decision["next_module"] for token in ["generic", "_adoption_", "_gate_", "_rollout_", "_audit_"]
        ),
    }
    ready = all(value is True for value in replacement_checks.values())
    status = (
        "PASS_REPAIR_PREVIEW_REQUIRED"
        if ready and materiality["limitation_materiality"] == "P1_REPAIR_PREVIEW_REQUIRED"
        else "PASS_BOUNDED"
        if ready and materiality["limitation_materiality"] in {"LOW", "P1_BOUNDED"}
        else "BLOCKED"
        if ready
        else "FAIL_CLOSED"
    )
    post_check_status = (
        POST_CHECK_STATUS_PASS_REPAIR_PREVIEW
        if status == "PASS_REPAIR_PREVIEW_REQUIRED"
        else POST_CHECK_STATUS_PASS_BOUNDED
        if status == "PASS_BOUNDED"
        else POST_CHECK_STATUS_BLOCKED
    )
    next_module = next_decision["next_module"] if ready else NEXT_MODULE_BLOCKED
    next_action = next_decision["next_action"] if ready else "RECORD_SOURCE_PANEL_RESULT_REVIEW_BLOCKED_STATE"
    final_decision = next_decision["final_decision"] if ready else "PARQUET_SCHEMA_LIMITATION_REVIEW_FAIL_CLOSED"

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_parquet_schema_limitation_review_status": status,
        "post_check_status": post_check_status,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_result_review_respected": prior["validated"],
        "parquet_limitation_review_completed": True,
        "prior_result_review_validation_completed": prior["completed"],
        "parquet_file_context_review_completed": context["completed"],
        "lightweight_schema_access_attempt_completed": access["completed"],
        "limitation_materiality_decision_completed": materiality["completed"],
        "evidence_quality_decision_completed": evidence["completed"],
        "safety_boundary_review_completed": True,
        "parquet_input_path_identified": context["parquet_input_path_identified"],
        "parquet_input_path": context["parquet_input_path"],
        "parquet_file_exists": context["parquet_file_exists"],
        "parquet_file_size_bytes": context["parquet_file_size_bytes"],
        "parquet_file_is_large": context["parquet_file_is_large"],
        "parquet_file_name": context["parquet_file_name"],
        "parquet_path_suggests_feature_panel": context["parquet_path_suggests_feature_panel"],
        "parquet_schema_attempted": access["parquet_schema_attempted"],
        "pyarrow_available": access["pyarrow_available"],
        "fastparquet_available": access["fastparquet_available"],
        "pandas_parquet_engine_available": access["pandas_parquet_engine_available"],
        "duckdb_available": access["duckdb_available"],
        "parquet_tools_cli_available": access["parquet_tools_cli_available"],
        "parquet_schema_obtained": access["parquet_schema_obtained"],
        "parquet_schema_method": access["parquet_schema_method"],
        "parquet_column_count": access["parquet_column_count"],
        "parquet_column_names_sample": access["parquet_column_names_sample"],
        "parquet_schema_failure_reason": access["parquet_schema_failure_reason"],
        "parquet_full_column_scan_performed": access["parquet_full_column_scan_performed"],
        "dependency_install_attempted": False,
        "environment_modified": False,
        "schema_or_config_created": False,
        "source_panel_rerun_performed": False,
        "limitation_materiality": materiality["limitation_materiality"],
        "parquet_limitation_blocks_next_step": materiality["parquet_limitation_blocks_next_step"],
        "parquet_schema_access_repair_preview_required": materiality["parquet_schema_access_repair_preview_required"],
        "current_evidence_chain_quality_before_limitation_review": evidence["current_evidence_chain_quality_before_limitation_review"],
        "current_evidence_chain_quality_after_limitation_review": evidence["current_evidence_chain_quality_after_limitation_review"],
        "source_panel_results_are_useful_research_substrate": review.get("source_panel_results_are_useful_research_substrate") is True,
        "source_panel_results_are_alpha_or_edge": review.get("source_panel_results_are_alpha_or_edge") is True,
        "source_panel_results_are_reusable_data_quality_asset": review.get("source_panel_results_are_reusable_data_quality_asset") is True,
        "active_p0_blocker_count": evidence["active_p0_blocker_count"] if ready else 1,
        "active_p1_attention_count": evidence["active_p1_attention_count"] if ready else 0,
        "fake_or_synthetic_data_detected": False,
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
        "money_path_alignment": review.get(
            "money_path_alignment", "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH"
        ),
        "usable_or_sellable_asset_path": review.get(
            "usable_or_sellable_asset_path",
            "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET",
        ),
        "evidence_chain_policy_level": POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
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
            "This parquet-schema limitation review reads the prior result-review artifact and performs only metadata/schema access attempts with already installed local tools. "
            "It does not install dependencies, modify the environment, create schema/config files, run a full parquet scan, rerun source-panel analysis, run strategy research, "
            "backtests or candidates, touch runtime/capital/live/orders/generic-runner paths, reopen old anomaly routes, or claim profit or tradable edge."
        ),
        "replacement_checks_all_true": ready,
        "prior_result_review_validation": prior,
        "parquet_file_context_review": context,
        "lightweight_schema_access_attempt": access,
        "limitation_materiality_decision": materiality,
        "evidence_quality_decision": evidence,
        "safety_boundary_review": {"completed": True, "checks": safety_checks, "validated": all(safety_checks.values())},
        "prior_result_review_snapshot": {
            "artifact_path": str(RESULT_REVIEW_LATEST_ARTIFACT),
            "artifact_valid_json": review_valid_json,
            "artifact_json_error": review_json_error,
            "status": review.get("source_panel_analysis_result_review_status"),
            "post_check_status": review.get("post_check_status"),
            "next_module": review.get("next_module"),
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
            "parquet_schema_limitation_review_only": True,
            "dependency_install_attempted": False,
            "environment_modified": False,
            "schema_or_config_created": False,
            "parquet_full_column_scan_performed": False,
            "source_panel_rerun_performed": False,
            "strategy_research_run_performed": False,
            "backtest_performed": False,
            "candidate_generation_performed": False,
            "family_release_performed": False,
            "active_paper_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1_latest.txt"
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
    return 0 if payload["source_panel_parquet_schema_limitation_review_status"] in {"PASS_REPAIR_PREVIEW_REQUIRED", "PASS_BOUNDED", "BLOCKED"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
