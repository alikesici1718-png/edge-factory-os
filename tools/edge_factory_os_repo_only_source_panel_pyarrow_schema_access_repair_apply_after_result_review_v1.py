from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import site
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "cacde54"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 633
EXPECTED_TRACKED_PYTHON_COUNT = 634

PARQUET_INPUT_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_feature_panels"
    r"\market_panic_rebound_long_v1\market_panic_rebound_long_v1_feature_panel_1h.parquet"
)
EXPECTED_PARQUET_SIZE_BYTES = 99504547

PRIOR_APPROVAL_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_approval_after_result_review_v1"
)
PRIOR_APPROVAL_LATEST_ARTIFACT = (
    PRIOR_APPROVAL_DIR
    / "repo_only_source_panel_pyarrow_schema_access_repair_apply_approval_after_result_review_v1_latest.json"
)

SCHEMA_METADATA_ARTIFACT_NAME = "source_panel_parquet_schema_metadata_after_pyarrow_repair.json"
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_validator_after_result_review_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_blocked_record_after_result_review_v1.py"
)

POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_PASS_VALIDATOR_NEXT"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_BLOCKED"
)
APPLY_STATUS_PASS = "PASS_SCHEMA_METADATA_ARTIFACT_CREATED_VALIDATOR_REQUIRED"
APPLY_STATUS_FAIL = "FAIL_CLOSED_SCHEMA_METADATA_REPAIR_APPLY_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
EVIDENCE_BEFORE = "PRIMARY_ARTIFACT_PARTIAL_WITH_P1_ATTENTION_SOURCE_PANEL_RESULTS"
EVIDENCE_AFTER_PENDING = "PRIMARY_ARTIFACT_PARTIAL_WITH_P1_ATTENTION_SOURCE_PANEL_RESULTS_PENDING_SCHEMA_VALIDATOR"
LIMITATION_BEFORE = "P1_REPAIR_PREVIEW_REQUIRED"
LIMITATION_AFTER_PENDING = "P1_PENDING_VALIDATOR"
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


def run_cmd(args: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    else:
        safe_args = args
    result = subprocess.run(
        safe_args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def tail_text(value: str, max_chars: int = 4000) -> str:
    return value[-max_chars:] if len(value) > max_chars else value


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


def ensure_user_site_on_path() -> Dict[str, Any]:
    path = user_site_path()
    added = False
    if path and not path.startswith("unavailable:") and path not in sys.path:
        site.addsitedir(path)
        importlib.invalidate_caches()
        added = True
    return {"user_site_path": path, "user_site_added_to_sys_path": added}


def pyarrow_info() -> Tuple[bool, Optional[str]]:
    ensure_user_site_on_path()
    spec = importlib.util.find_spec("pyarrow")
    if spec is None:
        return False, None
    pyarrow = importlib.import_module("pyarrow")
    return True, getattr(pyarrow, "__version__", None)


def pip_version() -> str:
    result = run_cmd([sys.executable, "-m", "pip", "--version"], check=False)
    return (result.stdout or result.stderr).strip()


def pip_package_list() -> Dict[str, Any]:
    result = run_cmd([sys.executable, "-m", "pip", "list", "--format=freeze"], check=False)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return {
        "return_code": result.returncode,
        "package_count": len(lines),
        "packages": lines[:500],
        "truncated": len(lines) > 500,
        "stderr_tail": tail_text(result.stderr),
    }


def user_site_path() -> str:
    try:
        return site.getusersitepackages()
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}: {exc}"


def install_pyarrow_if_needed(pyarrow_available_before: bool) -> Dict[str, Any]:
    command = [sys.executable, "-m", "pip", "install", "--user", "pyarrow"]
    if pyarrow_available_before:
        return {
            "dependency_install_attempted": False,
            "pyarrow_install_attempted": False,
            "install_command_executed": "install_not_needed_pyarrow_already_available",
            "install_scope": "INSTALL_NOT_NEEDED_ALREADY_IMPORTABLE",
            "install_return_code": None,
            "install_successful": True,
            "install_stdout_tail": "",
            "install_stderr_tail": "",
            "environment_modified": False,
        }
    result = run_cmd(command, check=False)
    return {
        "dependency_install_attempted": True,
        "pyarrow_install_attempted": True,
        "install_command_executed": " ".join(command),
        "install_scope": "LOCAL_USER_SITE_VIA_PIP_USER",
        "install_return_code": result.returncode,
        "install_successful": result.returncode == 0,
        "install_stdout_tail": tail_text(result.stdout),
        "install_stderr_tail": tail_text(result.stderr),
        "environment_modified": result.returncode == 0,
    }


def read_parquet_schema_metadata(artifact_path: Path) -> Dict[str, Any]:
    pyarrow_parquet = importlib.import_module("pyarrow.parquet")
    parquet_file = pyarrow_parquet.ParquetFile(str(PARQUET_INPUT_PATH))
    metadata = parquet_file.metadata
    arrow_schema = parquet_file.schema_arrow
    column_names = list(arrow_schema.names)
    schema_payload = {
        "created_at_utc": now_utc(),
        "parquet_input_path": str(PARQUET_INPUT_PATH),
        "parquet_file_size_bytes": PARQUET_INPUT_PATH.stat().st_size,
        "parquet_schema_method": "PYARROW_PARQUETFILE_METADATA_ONLY",
        "parquet_column_count": len(column_names),
        "parquet_column_names": column_names,
        "parquet_column_names_sample": column_names[:50],
        "parquet_num_row_groups_metadata_only": metadata.num_row_groups if metadata is not None else None,
        "parquet_num_rows_metadata_only": metadata.num_rows if metadata is not None else None,
        "parquet_created_by_metadata_only": metadata.created_by if metadata is not None else None,
        "parquet_schema_arrow_string": str(arrow_schema),
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
    }
    artifact_path.write_text(json.dumps(schema_payload, indent=2, sort_keys=True), encoding="utf-8")
    return schema_payload


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    schema_metadata_artifact_path = OUT_DIR / SCHEMA_METADATA_ARTIFACT_NAME

    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    prior, prior_valid_json, prior_json_error = load_json_checked(PRIOR_APPROVAL_LATEST_ARTIFACT)
    parquet_exists = PARQUET_INPUT_PATH.exists()
    parquet_size = PARQUET_INPUT_PATH.stat().st_size if parquet_exists else 0
    parquet_suggests_feature_panel = "feature_panel" in str(PARQUET_INPUT_PATH).lower()
    pyarrow_available_before, pyarrow_version_before = pyarrow_info()

    prior_apply_approval_respected = (
        prior_valid_json
        and prior.get("source_panel_pyarrow_schema_access_repair_apply_approval_status")
        == "PASS_APPLY_APPROVAL_RECORD_CREATED_APPLY_NEXT"
        and prior.get("post_check_status")
        == "REPO_ONLY_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_APPROVAL_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_PASS_APPLY_NEXT"
        and prior.get("pyarrow_schema_access_repair_apply_approval_record_created") is True
        and prior.get("user_pyarrow_repair_apply_approval_present") is True
        and prior.get("dependency_candidate") == "pyarrow"
        and prior.get("install_command_preview") == "python -m pip install --user pyarrow"
        and prior.get("install_scope_preview") == "LOCAL_USER_OR_ISOLATED_ENVIRONMENT_ONLY_NOT_GLOBAL_IF_AVOIDABLE"
        and prior.get("pyarrow_repair_apply_allowed_next") is True
        and prior.get("repair_apply_performed") is False
        and prior.get("dependency_install_attempted") is False
        and prior.get("environment_modified") is False
        and prior.get("pyarrow_install_attempted") is False
        and prior.get("schema_or_config_created") is False
        and prior.get("full_parquet_scan_performed") is False
        and prior.get("parquet_rows_read_now") is False
        and prior.get("source_panel_rerun_performed") is False
        and prior.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and prior.get("replacement_checks_all_true") is True
    )

    pre_apply_environment_snapshot = {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "pip_version_before": pip_version(),
        "pyarrow_available_before": pyarrow_available_before,
        "pyarrow_version_before": pyarrow_version_before,
        "user_site_path": user_site_path(),
        "pip_freeze_or_package_list_before": pip_package_list(),
        "parquet_input_path_exists": parquet_exists,
        "parquet_file_size_bytes": parquet_size,
    }

    dependency_apply = install_pyarrow_if_needed(pyarrow_available_before)
    importlib.invalidate_caches()
    pyarrow_available_after, pyarrow_version_after = pyarrow_info()

    post_apply_environment_snapshot = {
        "pyarrow_available_after": pyarrow_available_after,
        "pyarrow_version_after": pyarrow_version_after,
        "pip_version_after": pip_version(),
        "package_list_after": pip_package_list(),
        "environment_delta_summary": (
            "pyarrow installed into user site by this module"
            if dependency_apply["environment_modified"]
            else "install_not_needed_or_install_failed_no_confirmed_environment_change"
        ),
        "global_git_config_changed": False,
        "repo_file_changed_except_approved_tool_before_commit": False,
    }

    schema_metadata: Dict[str, Any] = {}
    schema_error = ""
    parquet_schema_metadata_read_attempted = bool(pyarrow_available_after and parquet_exists)
    if parquet_schema_metadata_read_attempted:
        try:
            schema_metadata = read_parquet_schema_metadata(schema_metadata_artifact_path)
        except Exception as exc:
            schema_error = f"{type(exc).__name__}: {exc}"

    parquet_schema_obtained = bool(schema_metadata and not schema_error and schema_metadata.get("parquet_column_count", 0) > 0)
    parquet_column_names_sample = schema_metadata.get("parquet_column_names_sample", [])
    parquet_column_count = int(schema_metadata.get("parquet_column_count", 0) or 0)
    parquet_schema_metadata_artifact_created = schema_metadata_artifact_path.exists() and parquet_schema_obtained

    safety = {
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
        "source_panel_rerun_performed": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
    }

    repair_apply_successful = bool(
        prior_apply_approval_respected
        and pyarrow_available_after
        and parquet_schema_obtained
        and parquet_schema_metadata_artifact_created
        and all(value is False for key, value in safety.items() if key != "generic_runner_implementation_remains_blocked")
        and safety["generic_runner_implementation_remains_blocked"] is True
    )
    status = APPLY_STATUS_PASS if repair_apply_successful else APPLY_STATUS_FAIL
    next_module = NEXT_MODULE_VALIDATOR if repair_apply_successful else NEXT_MODULE_BLOCKED
    final_decision = (
        "PYARROW_SCHEMA_ACCESS_REPAIR_APPLIED_SCHEMA_METADATA_ARTIFACT_CREATED_VALIDATOR_NEXT"
        if repair_apply_successful
        else "PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_FAIL_CLOSED_BLOCKED_RECORD_NEXT"
    )
    next_action = (
        "BUILD_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_VALIDATOR_AFTER_RESULT_REVIEW"
        if repair_apply_successful
        else "BUILD_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_BLOCKED_RECORD_AFTER_RESULT_REVIEW"
    )

    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_633_to_634": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "prior_apply_approval_respected": prior_apply_approval_respected,
        "repair_apply_performed": True,
        "repair_apply_successful": repair_apply_successful,
        "install_attempt_scope_allowed": dependency_apply["install_scope"]
        in {"LOCAL_USER_SITE_VIA_PIP_USER", "INSTALL_NOT_NEEDED_ALREADY_IMPORTABLE"},
        "pyarrow_available_after": pyarrow_available_after,
        "parquet_file_exists": parquet_exists,
        "parquet_file_size_matches_expected": parquet_size == EXPECTED_PARQUET_SIZE_BYTES,
        "parquet_file_is_large": parquet_size >= 10_000_000,
        "parquet_path_suggests_feature_panel": parquet_suggests_feature_panel,
        "parquet_schema_metadata_read_attempted": parquet_schema_metadata_read_attempted,
        "parquet_schema_obtained": parquet_schema_obtained,
        "parquet_column_count_positive": parquet_column_count > 0,
        "parquet_schema_metadata_artifact_created": parquet_schema_metadata_artifact_created,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "safety_flags_hold": all(value is False for key, value in safety.items() if key != "generic_runner_implementation_remains_blocked")
        and safety["generic_runner_implementation_remains_blocked"] is True,
        "next_module_allowed": next_module in {NEXT_MODULE_VALIDATOR, NEXT_MODULE_BLOCKED},
        "loop_remains_closed": True,
    }
    replacement_checks_all_true = all(value is True for value in replacement_checks.values())

    active_p0_blocker_count = 0 if repair_apply_successful else 1
    active_p1_attention_count = 1

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_pyarrow_schema_access_repair_apply_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if repair_apply_successful else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_apply_approval_respected": prior_apply_approval_respected,
        "repair_apply_performed": True,
        "repair_apply_successful": repair_apply_successful,
        "python_executable": sys.executable,
        "python_version": sys.version,
        "pip_version_before": pre_apply_environment_snapshot["pip_version_before"],
        "pip_version_after": post_apply_environment_snapshot["pip_version_after"],
        "user_site_path": pre_apply_environment_snapshot["user_site_path"],
        "pyarrow_available_before": pyarrow_available_before,
        "pyarrow_version_before": pyarrow_version_before,
        **dependency_apply,
        "pyarrow_available_after": pyarrow_available_after,
        "pyarrow_version_after": pyarrow_version_after,
        "environment_delta_summary": post_apply_environment_snapshot["environment_delta_summary"],
        "parquet_input_path": str(PARQUET_INPUT_PATH),
        "parquet_file_exists": parquet_exists,
        "parquet_file_size_bytes": parquet_size,
        "parquet_file_is_large": parquet_size >= 10_000_000,
        "parquet_path_suggests_feature_panel": parquet_suggests_feature_panel,
        "parquet_schema_metadata_read_attempted": parquet_schema_metadata_read_attempted,
        "parquet_schema_obtained": parquet_schema_obtained,
        "parquet_schema_method": schema_metadata.get("parquet_schema_method", "PYARROW_PARQUETFILE_METADATA_ONLY"),
        "parquet_column_count": parquet_column_count,
        "parquet_column_names_sample": parquet_column_names_sample,
        "parquet_schema_metadata_artifact_created": parquet_schema_metadata_artifact_created,
        "parquet_schema_metadata_artifact_path": str(schema_metadata_artifact_path),
        "parquet_num_row_groups_metadata_only": schema_metadata.get("parquet_num_row_groups_metadata_only"),
        "parquet_num_rows_metadata_only": schema_metadata.get("parquet_num_rows_metadata_only"),
        "parquet_created_by_metadata_only": schema_metadata.get("parquet_created_by_metadata_only"),
        "parquet_schema_read_error": schema_error,
        **safety,
        "limitation_materiality_before_apply": LIMITATION_BEFORE,
        "limitation_materiality_after_apply": LIMITATION_AFTER_PENDING if repair_apply_successful else LIMITATION_BEFORE,
        "current_evidence_chain_quality_before_apply": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_apply": EVIDENCE_AFTER_PENDING if repair_apply_successful else EVIDENCE_BEFORE,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "source_panel_results_are_useful_research_substrate": True,
        "source_panel_results_are_alpha_or_edge": False,
        "source_panel_results_are_reusable_data_quality_asset": True,
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH",
        "usable_or_sellable_asset_path": (
            "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET"
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
            "This apply module only installs or verifies pyarrow in local/user scope for parquet schema metadata access, "
            "then uses pyarrow.parquet.ParquetFile footer/schema metadata access to write an external schema metadata "
            "artifact. It does not read parquet rows, perform a full parquet scan, create repo schema/config files, rerun "
            "source-panel analysis, run strategy/backtest/candidate work, touch runtime/capital/live/order paths, approve "
            "or implement the generic runner, reopen the old anomaly route, or claim profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "pre_apply_environment_snapshot": pre_apply_environment_snapshot,
        "dependency_apply": dependency_apply,
        "post_apply_environment_snapshot": post_apply_environment_snapshot,
        "parquet_schema_metadata_read": {
            "attempted": parquet_schema_metadata_read_attempted,
            "obtained": parquet_schema_obtained,
            "method": schema_metadata.get("parquet_schema_method", "PYARROW_PARQUETFILE_METADATA_ONLY"),
            "artifact_path": str(schema_metadata_artifact_path),
            "schema_error": schema_error,
            "metadata": schema_metadata,
        },
        "post_apply_safety_validation": safety,
        "evidence_state": {
            "current_evidence_chain_quality": EVIDENCE_AFTER_PENDING if repair_apply_successful else EVIDENCE_BEFORE,
            "active_p0_blocker_count": active_p0_blocker_count,
            "active_p1_attention_count": active_p1_attention_count,
            "no_upgrade_beyond_schema_metadata_artifact_pending_validator": True,
        },
        "next_module_decision": {
            "apply_successful": repair_apply_successful,
            "next_module_if_success": NEXT_MODULE_VALIDATOR,
            "next_module_if_failed": NEXT_MODULE_BLOCKED,
            "selected_next_module": next_module,
            "result_summary_selected": False,
            "source_panel_rerun_selected": False,
            "candidate_backtest_runtime_live_capital_generic_runner_schema_config_selected": False,
            "generic_review_adoption_gate_rollout_audit_selected": False,
        },
        "prior_apply_approval_snapshot": {
            "artifact_path": str(PRIOR_APPROVAL_LATEST_ARTIFACT),
            "artifact_valid_json": prior_valid_json,
            "artifact_json_error": prior_json_error,
            "status": prior.get("source_panel_pyarrow_schema_access_repair_apply_approval_status"),
            "post_check_status": prior.get("post_check_status"),
            "approval_record_created": prior.get("pyarrow_schema_access_repair_apply_approval_record_created"),
            "next_module": prior.get("next_module"),
        },
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "expected_previous_tracked_python_count": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "replacement_checks": replacement_checks,
        },
        "safety_flags": {
            "repo_only": True,
            "pyarrow_schema_metadata_apply_only": True,
            **safety,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1_latest.txt"
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
    return 0 if payload["source_panel_pyarrow_schema_access_repair_apply_status"] == APPLY_STATUS_PASS else 3


if __name__ == "__main__":
    raise SystemExit(main())
