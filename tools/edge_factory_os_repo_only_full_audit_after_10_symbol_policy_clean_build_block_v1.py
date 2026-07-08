from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_full_audit_after_10_symbol_policy_clean_build_block_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_full_audit_after_10_symbol_policy_clean_build_block_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_HEAD = "a01ba6fd"
EXPECTED_FULL_HEAD = "a01ba6fd555062c6eab44a00b5f1828e9571007d"
KNOWN_ACTIVE_BLOCKED_ROUTE_P0 = 1
DORMANT_REPO_ATTENTION_COUNT = 716

PASS_STATUS = "PASS_REPO_ONLY_FULL_AUDIT_AFTER_10_SYMBOL_POLICY_CLEAN_BUILD_BLOCK_READY_FOR_BATCH_ROUTE_RECORD"
FAIL_STATUS = "FAIL_REPO_ONLY_FULL_AUDIT_NEW_P0_FOUND"
P0_REMEDIATION_MODULE = "edge_factory_os_repo_only_full_audit_p0_remediation_plan_after_10_symbol_policy_clean_build_block_v1.py"
RECOMMENDED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_sol_policy_v1.py"
)
RECOMMENDED_FOLLOWING_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "batch_anomaly_classification_after_policy_clean_build_block_v1.py"
)
EXPECTED_BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "EXECUTION_ANOMALY"
)
EXPECTED_ANOMALY_SYMBOL = "SOL-USDT-SWAP"
EXPECTED_DUPLICATE_OPEN_TIME = 1697108460000

ARTIFACT_DIRS = {
    "btc_single_symbol_policy_clean_pipeline_close": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_policy_clean_pipeline_summary_after_rebuild_validator_v1",
    "ten_symbol_pilot_expansion_preview": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_and_multi_symbol_expansion_preview_after_single_symbol_3_year_summary_v1",
    "ten_symbol_download_execution": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_after_expansion_preview_approval_v1",
    "ten_symbol_download_validator": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1",
    "ten_symbol_build_preview": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_build_preview_after_download_validator_v1",
    "eth_exact_policy_path": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_eth_exact_duplicate_policy_after_diagnostic_v1",
    "eth_material_policy_path": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1",
    "sol_exact_policy_path": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_sol_exact_duplicate_policy_after_diagnostic_v1",
    "latest_blocked_build_route": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_after_sol_exact_duplicate_policy_v1",
    "prior_eth_exact_block": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_after_eth_exact_duplicate_policy_v1",
    "prior_eth_material_block": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_after_eth_material_conflict_policy_v1",
    "eth_block_record": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_blocked_or_anomaly_record_after_eth_policy_v1",
    "eth_material_block_record": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_blocked_or_anomaly_record_after_eth_material_policy_v1",
    "sol_duplicate_diagnostic": LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_sol_duplicate_diagnostic_after_policy_clean_build_anomaly_v1",
}

LATEST_SUMMARY = (
    ARTIFACT_DIRS["latest_blocked_build_route"]
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_summary.json"
)
LATEST_REPORT = (
    ARTIFACT_DIRS["latest_blocked_build_route"]
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_report.json"
)
LATEST_GAP_REPORT = (
    ARTIFACT_DIRS["latest_blocked_build_route"]
    / "historical_okx_10_symbol_pilot_policy_clean_gap_duplicate_report.json"
)
LATEST_MANIFEST = (
    ARTIFACT_DIRS["latest_blocked_build_route"]
    / "historical_okx_10_symbol_pilot_policy_clean_1h_output_manifest.json"
)
LATEST_COMPLIANCE = (
    ARTIFACT_DIRS["latest_blocked_build_route"]
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_compliance_report.json"
)
LATEST_OUTPUT_DIR = ARTIFACT_DIRS["latest_blocked_build_route"] / "pilot_1h_outputs"

REQUIRED_REPORTS = [
    "repo_only_full_audit_after_10_symbol_policy_clean_build_block_report.json",
    "repo_only_full_audit_git_state_report.json",
    "repo_only_full_audit_python_syntax_bom_report.json",
    "repo_only_full_audit_dangerous_flags_report.json",
    "repo_only_full_audit_evidence_chain_report.json",
    "repo_only_full_audit_partial_output_quarantine_report.json",
    "repo_only_full_audit_next_route_report.json",
    "repo_only_full_audit_stale_guard_report.json",
    "repo_only_full_audit_summary.json",
]

DANGEROUS_KEYS = {
    "runtime",
    "runtime_touched",
    "runtime_touch_performed",
    "capital",
    "capital_changed",
    "capital_touch_performed",
    "live",
    "live_touch_performed",
    "real_orders",
    "real_order_touch_performed",
    "live_or_real_orders",
    "launcher",
    "launcher_executed",
    "active_paper",
    "strategy_research_allowed",
    "strategy_research_recommended_now",
    "backtest_allowed",
    "backtest_performed",
    "candidate_generation_allowed",
    "candidate_generation_touched",
    "candidate_generation_recommended_now",
    "edge_claim",
    "edge_profit_claim_made",
    "profit_claim",
    "full_universe_acquisition_allowed_now",
    "full_universe_ready_claim_made",
    "safe_for_full_universe_acquisition",
    "broad_acquisition_ready",
    "broad_acquisition_ready_claim_made",
    "source_manifest_acquisition_ready",
    "output_valid_for_research_backtest",
    "output_valid_for_edge_claim",
}

STALE_GUARD_NAMES = {"EXPECTED_HEAD", "EXPECTED_FULL_HEAD", "EXPECTED_PARENT_HEAD", "CURRENT_TOOL_REL", "REQUESTED_MODULE"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    safe_args = args
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    result = subprocess.run(
        safe_args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {"_non_dict_json": True}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def list_tracked_python() -> list[str]:
    files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
    if (REPO_ROOT / CURRENT_TOOL_REL).exists() and CURRENT_TOOL_REL not in files:
        files.append(CURRENT_TOOL_REL)
    return sorted(files)


def git_state() -> dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = sorted(line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? "))
    dirty_tracked = sorted(line[3:].replace("\\", "/") for line in status_lines if not line.startswith("?? "))
    head_full = run_cmd(["git", "rev-parse", "HEAD"]).stdout.strip()
    parent_full = run_cmd(["git", "rev-parse", "HEAD^"]).stdout.strip()
    untracked_only_current_tool = untracked in ([], [CURRENT_TOOL_REL])
    repo_clean_for_audit = len(dirty_tracked) == 0 and untracked_only_current_tool
    return {
        "head": head_full[:7],
        "head_full": head_full,
        "parent": parent_full[:7],
        "parent_full": parent_full,
        "expected_head": EXPECTED_HEAD,
        "current_tool_rel": CURRENT_TOOL_REL,
        "status_porcelain": status_lines,
        "dirty_tracked_paths": dirty_tracked,
        "untracked_paths": untracked,
        "untracked_only_current_tool": untracked_only_current_tool,
        "repo_clean": repo_clean_for_audit,
        "raw_git_status_clean": len(status_lines) == 0,
        "repo_clean_before_tool_creation": head_full == EXPECTED_FULL_HEAD and repo_clean_for_audit,
        "current_head_path_guard_passed": head_full == EXPECTED_FULL_HEAD
        and (REPO_ROOT / CURRENT_TOOL_REL).exists()
        and CURRENT_TOOL_REL.endswith("edge_factory_os_repo_only_full_audit_after_10_symbol_policy_clean_build_block_v1.py"),
    }


def tracked_python_validation() -> dict[str, Any]:
    files = list_tracked_python()
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    non_utf8_errors: list[dict[str, str]] = []
    accidental_binary: list[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        if b"\x00" in data[:4096]:
            accidental_binary.append(rel)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            non_utf8_errors.append({"path": rel, "error": str(exc)})
            syntax_errors.append({"path": rel, "error": f"UnicodeDecodeError: {exc}"})
            continue
        try:
            ast.parse(text, filename=rel)
        except SyntaxError as exc:
            syntax_errors.append({"path": rel, "error": f"SyntaxError line={exc.lineno}: {exc.msg}"})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "non_utf8_error_count": len(non_utf8_errors),
        "accidental_binary_data_file_in_tracked_code_path_count": len(accidental_binary),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "non_utf8_errors": non_utf8_errors,
        "accidental_binary_data_files": accidental_binary,
    }


def json_artifact_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in ARTIFACT_DIRS.values():
        if directory.exists():
            paths.extend(sorted(directory.glob("*.json")))
    return sorted(set(paths), key=lambda path: str(path).lower())


def dangerous_flag_scan(paths: list[Path]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    def walk(obj: Any, source: Path, parts: list[str]) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_name = str(key)
                normalized = key_name.lower()
                current = [*parts, key_name]
                if normalized in DANGEROUS_KEYS and value is True:
                    findings.append(
                        {
                            "artifact": str(source),
                            "json_path": ".".join(current),
                            "key": key_name,
                            "value": True,
                            "issue_class": "DANGEROUS_TRUE_FLAG",
                            "severity": "P0",
                        }
                    )
                walk(value, source, current)
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, source, [*parts, str(index)])

    artifacts_scanned = 0
    unreadable: list[dict[str, str]] = []
    for path in paths:
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            unreadable.append({"artifact": str(path), "error": repr(exc)})
            continue
        artifacts_scanned += 1
        walk(loaded, path, [])
    return {
        "artifacts_scanned_count": artifacts_scanned,
        "unreadable_artifact_count": len(unreadable),
        "unreadable_artifacts": unreadable,
        "dangerous_true_flag_count": len(findings),
        "dangerous_true_flags": findings,
        "false_positive_metadata_strings_ignored": True,
    }


def evidence_chain_report() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    for label, directory in ARTIFACT_DIRS.items():
        jsons = sorted(path.name for path in directory.glob("*.json")) if directory.exists() else []
        checks[label] = {
            "directory": str(directory),
            "exists": directory.exists(),
            "json_artifact_count": len(jsons),
            "sample_json_artifacts": jsons[:8],
        }
    return {
        "chain_start": "btc_single_symbol_policy_clean_pipeline_close",
        "chain_end": "latest_blocked_build_route",
        "chain_nodes": checks,
        "missing_chain_node_count": sum(1 for item in checks.values() if not item["exists"] or item["json_artifact_count"] == 0),
        "current_evidence_chain_quality_after_audit": "REPO_ONLY_FULL_AUDIT_AFTER_10_SYMBOL_POLICY_CLEAN_BUILD_BLOCK_READY_FOR_BATCH_ANOMALY_ROUTE",
    }


def latest_blocked_route_report() -> dict[str, Any]:
    summary = load_json(LATEST_SUMMARY)
    gap = load_json(LATEST_GAP_REPORT)
    manifest = load_json(LATEST_MANIFEST)
    compliance = load_json(LATEST_COMPLIANCE)
    blocked_reason = str(summary.get("blocked_reason", ""))
    duplicate_open_time = EXPECTED_DUPLICATE_OPEN_TIME if str(EXPECTED_DUPLICATE_OPEN_TIME) in blocked_reason else None
    if duplicate_open_time is None:
        for payload in (summary, gap):
            value = payload.get("known_sol_duplicate_open_time") or payload.get("duplicate_open_time")
            if value == EXPECTED_DUPLICATE_OPEN_TIME:
                duplicate_open_time = EXPECTED_DUPLICATE_OPEN_TIME
                break
    blocked_confirmed = (
        summary.get("historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_status")
        == EXPECTED_BLOCKED_STATUS
        and summary.get("replacement_checks_all_true") is False
        and summary.get("active_p0_blocker_count") == KNOWN_ACTIVE_BLOCKED_ROUTE_P0
        and summary.get("anomaly_symbols") == [EXPECTED_ANOMALY_SYMBOL]
        and summary.get("duplicate_open_time_count_total") == 1
        and duplicate_open_time == EXPECTED_DUPLICATE_OPEN_TIME
    )
    dangerous_claims_absent = (
        summary.get("output_valid_for_research_backtest") is False
        and summary.get("output_valid_for_edge_claim") is False
        and summary.get("safe_for_full_universe_acquisition") is False
        and summary.get("broad_acquisition_ready") is False
        and compliance.get("output_valid_for_research_backtest") is False
        and compliance.get("output_valid_for_edge_claim") is False
        and compliance.get("safe_for_full_universe_acquisition") is False
        and compliance.get("broad_acquisition_ready") is False
    )
    return {
        "summary_artifact": str(LATEST_SUMMARY),
        "report_artifact": str(LATEST_REPORT),
        "gap_artifact": str(LATEST_GAP_REPORT),
        "manifest_artifact": str(LATEST_MANIFEST),
        "compliance_artifact": str(LATEST_COMPLIANCE),
        "summary_exists": bool(summary),
        "gap_report_exists": bool(gap),
        "manifest_exists": bool(manifest),
        "latest_blocked_route_confirmed": blocked_confirmed,
        "latest_anomaly_symbol": EXPECTED_ANOMALY_SYMBOL if summary.get("anomaly_symbols") == [EXPECTED_ANOMALY_SYMBOL] else None,
        "latest_unapproved_duplicate_open_time": duplicate_open_time,
        "replacement_checks_all_true_latest": summary.get("replacement_checks_all_true"),
        "duplicate_open_time_count_total": summary.get("duplicate_open_time_count_total"),
        "active_p0_blocker_count_latest": summary.get("active_p0_blocker_count"),
        "active_p1_attention_count_latest": summary.get("active_p1_attention_count", 0),
        "output_csv_created": summary.get("output_csv_created"),
        "output_manifest_created": summary.get("output_manifest_created"),
        "blocked_reason": blocked_reason,
        "dangerous_claims_absent": dangerous_claims_absent,
        "no_research_backtest_edge_full_universe_or_broad_acquisition_claim": dangerous_claims_absent,
        "next_module": summary.get("next_module"),
        "raw_summary": summary,
    }


def partial_output_report(blocked: dict[str, Any]) -> dict[str, Any]:
    summary = blocked["raw_summary"]
    output_csv_created = summary.get("output_csv_created") is True
    output_manifest_created = summary.get("output_manifest_created") is True
    output_files = sorted(path.name for path in LATEST_OUTPUT_DIR.glob("*.csv")) if LATEST_OUTPUT_DIR.exists() else []
    partial_created = output_csv_created and not output_manifest_created
    partial_trusted = any(
        value is True
        for value in [
            summary.get("partial_output_trusted"),
            summary.get("output_trusted"),
            summary.get("build_ready"),
            summary.get("acquisition_ready"),
            summary.get("source_manifest_acquisition_ready"),
        ]
    )
    return {
        "partial_output_created_in_blocked_route": partial_created,
        "output_csv_created": output_csv_created,
        "output_manifest_created": output_manifest_created,
        "output_directory": str(LATEST_OUTPUT_DIR),
        "output_directory_exists": LATEST_OUTPUT_DIR.exists(),
        "output_csv_metadata_count": len(output_files),
        "output_csv_metadata_names": output_files,
        "partial_output_trusted": partial_trusted,
        "partial_output_quarantine_required": partial_created,
        "partial_output_allowed_for_validator": False,
        "partial_output_allowed_for_research_backtest_edge": False,
        "partial_output_must_not_feed_validator": True,
        "partial_output_must_not_feed_research_backtest_edge": True,
        "partial_output_must_be_quarantined_by_next_record_module": True,
        "trusted_partial_output_claim_count": 1 if partial_trusted else 0,
    }


def next_route_report(blocked: dict[str, Any]) -> dict[str, Any]:
    observed_next = blocked.get("next_module")
    sol_only_loop_risk = observed_next not in {RECOMMENDED_NEXT_MODULE, RECOMMENDED_FOLLOWING_MODULE} and "sol_" in str(observed_next).lower()
    return {
        "observed_latest_next_module": observed_next,
        "recommended_next_module": RECOMMENDED_NEXT_MODULE,
        "recommended_following_module": RECOMMENDED_FOLLOWING_MODULE,
        "latest_next_module_is_record_module": observed_next == RECOMMENDED_NEXT_MODULE,
        "one_symbol_policy_loop_should_continue": False,
        "per_symbol_policy_loop_terminated": True,
        "batch_anomaly_classification_required": True,
        "bad_next_route": observed_next != RECOMMENDED_NEXT_MODULE,
        "sol_only_loop_reentry_detected": sol_only_loop_risk,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
    }


def stale_guard_report() -> dict[str, Any]:
    stale_items: list[dict[str, Any]] = []
    current_items: list[dict[str, Any]] = []
    for rel in list_tracked_python():
        path = REPO_ROOT / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except Exception:
            continue
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                value_node = node.value
            elif isinstance(node, ast.AnnAssign):
                names = [node.target.id] if isinstance(node.target, ast.Name) else []
                value_node = node.value
            else:
                continue
            if not any(name in STALE_GUARD_NAMES for name in names):
                continue
            try:
                value = ast.literal_eval(value_node)
            except Exception:
                continue
            for name in names:
                if name not in STALE_GUARD_NAMES:
                    continue
                item = {"path": rel, "name": name, "value": value}
                if rel == CURRENT_TOOL_REL:
                    current_items.append(item)
                elif name in {"EXPECTED_HEAD", "EXPECTED_FULL_HEAD", "EXPECTED_PARENT_HEAD"} and value not in {EXPECTED_HEAD, EXPECTED_FULL_HEAD}:
                    stale_items.append({**item, "classification": "STALE_GUARD_ATTENTION"})
                elif name in {"CURRENT_TOOL_REL", "REQUESTED_MODULE"} and isinstance(value, str) and value != CURRENT_TOOL_REL and rel.endswith(value):
                    stale_items.append({**item, "classification": "HISTORICAL_PATH_GUARD_ATTENTION"})
    current_head_path_guard_passed = any(
        item["name"] == "EXPECTED_HEAD" and item["value"] == EXPECTED_HEAD for item in current_items
    ) and any(item["name"] == "CURRENT_TOOL_REL" and item["value"] == CURRENT_TOOL_REL for item in current_items)
    return {
        "stale_guard_attention_count": len(stale_items),
        "stale_guard_items_sample": stale_items[:40],
        "current_tool_guard_items": current_items,
        "current_head_path_guard_passed": current_head_path_guard_passed,
        "stale_guards_classified_as_attention_not_current_failure": True,
    }


def build_payloads() -> dict[str, dict[str, Any]]:
    git = git_state()
    py = tracked_python_validation()
    artifact_paths = json_artifact_paths()
    dangerous = dangerous_flag_scan(artifact_paths)
    chain = evidence_chain_report()
    blocked = latest_blocked_route_report()
    partial = partial_output_report(blocked)
    route = next_route_report(blocked)
    stale = stale_guard_report()

    new_p0_reasons: list[str] = []
    if not git["repo_clean"]:
        new_p0_reasons.append("repo dirty or untracked files present")
    if py["syntax_error_count"] or py["bom_error_count"] or py["non_utf8_error_count"] or py["accidental_binary_data_file_in_tracked_code_path_count"]:
        new_p0_reasons.append("tracked Python syntax/BOM/UTF-8/binary check failed")
    if dangerous["dangerous_true_flag_count"]:
        new_p0_reasons.append("dangerous true flag found")
    if not blocked["latest_blocked_route_confirmed"]:
        new_p0_reasons.append("latest blocked route not confirmed")
    if not blocked["dangerous_claims_absent"]:
        new_p0_reasons.append("latest blocked route contains forbidden research/backtest/edge/acquisition claim")
    if partial["partial_output_trusted"]:
        new_p0_reasons.append("partial output trusted claim found")
    if partial["partial_output_allowed_for_validator"] or partial["partial_output_allowed_for_research_backtest_edge"]:
        new_p0_reasons.append("partial output allowed downstream")
    if route["bad_next_route"]:
        new_p0_reasons.append("latest route does not point to blocked/anomaly record module")
    if not stale["current_head_path_guard_passed"] or not git["current_head_path_guard_passed"]:
        new_p0_reasons.append("current head/path guard failed")
    if chain["missing_chain_node_count"]:
        new_p0_reasons.append("evidence chain node missing")

    fail = bool(new_p0_reasons)
    full_audit_status = FAIL_STATUS if fail else PASS_STATUS
    next_module = P0_REMEDIATION_MODULE if fail else RECOMMENDED_NEXT_MODULE
    replacement_checks_all_true = not fail

    active_p1_attention_count = int(stale["stale_guard_attention_count"]) + (1 if partial["partial_output_quarantine_required"] else 0)
    summary = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "full_audit_status": full_audit_status,
        "audit_performed": True,
        "repo_clean": git["repo_clean"],
        "tracked_python_count": py["tracked_python_count"],
        "syntax_error_count": py["syntax_error_count"],
        "bom_error_count": py["bom_error_count"],
        "dangerous_true_flag_count": dangerous["dangerous_true_flag_count"],
        "active_p0_blocker_count": KNOWN_ACTIVE_BLOCKED_ROUTE_P0 if not fail else KNOWN_ACTIVE_BLOCKED_ROUTE_P0 + len(new_p0_reasons),
        "active_p1_attention_count": active_p1_attention_count,
        "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
        "latest_blocked_route_confirmed": blocked["latest_blocked_route_confirmed"],
        "latest_anomaly_symbol": blocked["latest_anomaly_symbol"],
        "latest_unapproved_duplicate_open_time": blocked["latest_unapproved_duplicate_open_time"],
        "replacement_checks_all_true_latest": blocked["replacement_checks_all_true_latest"],
        "partial_output_created_in_blocked_route": partial["partial_output_created_in_blocked_route"],
        "partial_output_trusted": partial["partial_output_trusted"],
        "partial_output_quarantine_required": partial["partial_output_quarantine_required"],
        "partial_output_allowed_for_validator": partial["partial_output_allowed_for_validator"],
        "partial_output_allowed_for_research_backtest_edge": partial["partial_output_allowed_for_research_backtest_edge"],
        "one_symbol_policy_loop_should_continue": route["one_symbol_policy_loop_should_continue"],
        "batch_anomaly_classification_required": route["batch_anomaly_classification_required"],
        "stale_guard_attention_count": stale["stale_guard_attention_count"],
        "current_head_path_guard_passed": git["current_head_path_guard_passed"] and stale["current_head_path_guard_passed"],
        "recommended_next_module": RECOMMENDED_NEXT_MODULE,
        "recommended_following_module": RECOMMENDED_FOLLOWING_MODULE,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "current_evidence_chain_quality_after_audit": chain["current_evidence_chain_quality_after_audit"],
        "next_module": next_module,
        "replacement_checks_all_true": replacement_checks_all_true,
        "known_active_blocked_route_p0_preserved": True,
        "new_p0_reasons": new_p0_reasons,
        "report_files": REQUIRED_REPORTS,
    }

    git_report = {**git, "approved_tool_only_before_commit": git["status_porcelain"] in ([], [f"?? {CURRENT_TOOL_REL}"])}
    py_report = py
    dangerous_report = dangerous
    chain_report = chain
    partial_report = partial
    route_report = route
    stale_report = stale
    full_report = {
        "summary": summary,
        "git_state_report": git_report,
        "python_syntax_bom_report": py_report,
        "dangerous_flags_report": dangerous_report,
        "evidence_chain_report": chain_report,
        "partial_output_quarantine_report": partial_report,
        "next_route_report": route_report,
        "stale_guard_report": stale_report,
        "artifact_paths_scanned": [str(path) for path in artifact_paths],
    }
    return {
        "repo_only_full_audit_after_10_symbol_policy_clean_build_block_report.json": full_report,
        "repo_only_full_audit_git_state_report.json": git_report,
        "repo_only_full_audit_python_syntax_bom_report.json": py_report,
        "repo_only_full_audit_dangerous_flags_report.json": dangerous_report,
        "repo_only_full_audit_evidence_chain_report.json": chain_report,
        "repo_only_full_audit_partial_output_quarantine_report.json": partial_report,
        "repo_only_full_audit_next_route_report.json": route_report,
        "repo_only_full_audit_stale_guard_report.json": stale_report,
        "repo_only_full_audit_summary.json": summary,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payloads = build_payloads()
    for filename, payload in payloads.items():
        write_json(OUT_DIR / filename, payload)
    print(json.dumps(payloads["repo_only_full_audit_summary.json"], indent=2, sort_keys=True))
    return 0 if payloads["repo_only_full_audit_summary.json"]["replacement_checks_all_true"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
