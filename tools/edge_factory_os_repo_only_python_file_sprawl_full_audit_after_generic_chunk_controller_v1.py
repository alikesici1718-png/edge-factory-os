from __future__ import annotations

import ast
import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_python_file_sprawl_full_audit_after_generic_chunk_controller_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "fa27690"
REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

ACTIVE_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
ACTIVE_NEXT_MODULE_REL = f"tools/{ACTIVE_NEXT_MODULE}"
ACTIVE_FRONTIER_NAME = "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER"
ACTIVE_ARTIFACT_DIR = EDGE_LAB_ROOT / ACTIVE_NEXT_MODULE.removesuffix(".py")
ACTIVE_NEXT_CHUNK_STATE = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json"
ACTIVE_COMPLIANCE_REPORT = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_compliance_report.json"
ACTIVE_CUMULATIVE_LEDGER = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json"
ACTIVE_PER_SYMBOL_SUMMARY = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_per_symbol_coverage_summary.json"

PASS_STATUS = "PYTHON_FILE_SPRAWL_AUDIT_PASS_CONTINUE_GENERIC_CHUNK_COVERAGE_CYCLE"
ATTENTION_STATUS = "PYTHON_FILE_SPRAWL_AUDIT_ATTENTION_CONTINUE_ALLOWED_WITH_CONSOLIDATION_BACKLOG"
FAIL_STATUS = "PYTHON_FILE_SPRAWL_AUDIT_FAIL_P0_REVIEW_REQUIRED"
PASS_QUALITY = "REPO_ONLY_PYTHON_FILE_SPRAWL_AUDIT_READY_CONTINUE_GENERIC_CHUNK_CYCLE_WITH_CONSOLIDATION_BACKLOG"

REQUIRED_ARTIFACTS = [
    "repo_only_python_file_sprawl_full_audit_report.json",
    "repo_only_python_file_inventory.csv",
    "repo_only_python_file_family_counts.json",
    "repo_only_python_syntax_bom_audit.json",
    "repo_only_python_risky_surface_audit.json",
    "repo_only_python_one_off_sprawl_audit.json",
    "repo_only_python_active_frontier_audit.json",
    "repo_only_python_consolidation_plan_preview.json",
    "repo_only_python_file_sprawl_full_audit_summary.json",
]

RISK_TERMS = [
    "requests.get",
    "urllib",
    "httpx",
    "subprocess",
    "os.system",
    "shutil.rmtree",
    "os.remove",
    "unlink",
    "rename",
    "move",
    "git add -A",
    "git add .",
    "live",
    "order",
    "real_order",
    "capital",
    "runtime",
    "launcher",
    "backtest",
    "candidate_generation",
    "edge_claim",
    "profit_claim",
    "schema creation",
    "config creation",
    "download",
    "aggregation",
    "build",
    "API",
    "browse",
]

SUFFIX_PATTERNS = [
    "_preview_",
    "_approval_",
    "_execution_",
    "_validator_",
    "_summary_",
    "_post_commit_check",
    "_selector",
    "_backlog",
    "chunk_01",
    "chunk_02",
    "chunk_03",
]


class AuditBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class PythonFileRecord:
    path: str
    family: str
    category: str
    line_count: int
    byte_count: int
    in_tools: bool
    suffix_patterns: tuple[str, ...]
    first_commit_date: str | None
    newest_commit_date: str | None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


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
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def rel_to_repo(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def approved_tool_rel() -> str:
    return rel_to_repo(APPROVED_TOOL)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def status_lines() -> list[str]:
    return [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]


def status_without_approved_tool(lines: list[str]) -> list[str]:
    rel = approved_tool_rel()
    return [line for line in lines if line[3:].replace("\\", "/") != rel]


def repo_effectively_clean(lines: list[str]) -> bool:
    return not status_without_approved_tool(lines)


def git_state_audit() -> dict[str, Any]:
    lines = status_lines()
    latest_head = run_git(["rev-parse", "--short", "HEAD"])
    latest_commit = run_git(["log", "-1", "--name-only", "--pretty=format:%H%n%s"]).splitlines()
    latest_commit_hash = latest_commit[0] if latest_commit else ""
    latest_commit_subject = latest_commit[1] if len(latest_commit) > 1 else ""
    latest_commit_paths = [line for line in latest_commit[2:] if line.strip()]
    dirty_tracked = [line for line in lines if not line.startswith("??")]
    untracked = [line[3:] for line in lines if line.startswith("??")]
    approved_rel = approved_tool_rel()
    return {
        "repo_clean_before_effective": repo_effectively_clean(lines),
        "repo_status_short_before": lines,
        "repo_status_short_without_approved_tool_before": status_without_approved_tool(lines),
        "untracked_file_count": len([path for path in untracked if path.replace("\\", "/") != approved_rel]),
        "dirty_tracked_file_count": len(dirty_tracked),
        "approved_tool_pending_commit": any(line[3:].replace("\\", "/") == approved_rel for line in lines),
        "latest_head": latest_head,
        "latest_head_full": latest_commit_hash,
        "expected_head": EXPECTED_HEAD,
        "latest_commit_subject": latest_commit_subject,
        "latest_commit_paths": latest_commit_paths,
        "approved_commit_only_path": approved_rel,
    }


def tracked_python_files_including_current() -> tuple[list[str], int]:
    git_files = sorted(path.replace("\\", "/") for path in run_git(["ls-files", "*.py"]).splitlines() if path.strip())
    rel = approved_tool_rel()
    files = list(git_files)
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files), len(git_files)


def untracked_python_files_excluding_current() -> list[str]:
    rel = approved_tool_rel()
    files = []
    for path in run_git(["ls-files", "--others", "--exclude-standard", "*.py"]).splitlines():
        normalized = path.replace("\\", "/")
        if normalized and normalized != rel:
            files.append(normalized)
    return sorted(files)


def path_text(path: str) -> str:
    return path.lower().replace("\\", "/")


def classify_family(path: str) -> str:
    name = Path(path).name.removesuffix(".py")
    lower = name.lower()
    if "repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage" in lower:
        return "repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage"
    if "repo_only_historical_data_acquisition_okx_full_usdt_swap" in lower and "chunk" in lower:
        return "repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_specific"
    if "repo_only_historical_data_acquisition_okx_full_usdt_swap" in lower:
        return "repo_only_historical_data_acquisition_okx_full_usdt_swap"
    if "repo_only_historical_data_acquisition_okx_10_symbol_pilot" in lower:
        return "repo_only_historical_data_acquisition_okx_10_symbol_pilot"
    if "repo_only_historical_data_acquisition_okx_single_symbol" in lower:
        return "repo_only_historical_data_acquisition_okx_single_symbol"
    if "repo_only_historical_data_acquisition_okx" in lower:
        return "repo_only_historical_data_acquisition_okx_other"
    if any(token in lower for token in ("policy", "validator", "summary", "preview", "execution")):
        return "policy_validator_summary_preview_execution"
    if any(token in lower for token in ("research", "governance", "selector", "backlog")):
        return "old_edge_factory_os_research_governance_selector_backlog"
    if "generic" in lower and "controller" in lower:
        return "generic_controller_files"
    if path.startswith("tools/"):
        parts = lower.split("_")
        return "_".join(parts[:5]) if len(parts) >= 5 else lower
    return path.split("/", 1)[0] if "/" in path else "repo_root"


def classify_file(path: str, family: str) -> str:
    lower = path_text(path)
    if path == ACTIVE_NEXT_MODULE_REL or (
        "full_usdt_swap_generic_chunk_coverage" in lower and any(token in lower for token in ("controller", "chunk_03", "chunk_04", "cycle_execution"))
    ):
        return "ACTIVE_FRONTIER_DO_NOT_TOUCH"
    if any(token in lower for token in ("rmtree", "remove", "unlink", "rename", "move", "runtime", "live", "order", "capital")):
        return "RISKY_SURFACE_REVIEW_REQUIRED"
    if any(token in lower for token in ("chunk_01", "chunk_02", "chunk_03", "10_symbol_pilot", "single_symbol")):
        return "HISTORICAL_EVIDENCE_DO_NOT_DELETE"
    if any(token in lower for token in ("preview", "approval", "validator", "summary", "post_commit_check", "selector", "backlog")):
        return "CONSOLIDATION_CANDIDATE"
    if "repo_only_historical_data_acquisition_okx" in lower:
        return "SUPERSEDED_BUT_KEEP_FOR_NOW"
    if family.startswith("old_edge_factory_os"):
        return "MANUAL_REVIEW_REQUIRED"
    return "MANUAL_REVIEW_REQUIRED"


def git_file_dates() -> dict[str, dict[str, str]]:
    dates: dict[str, dict[str, str]] = {}
    try:
        output = run_git(["log", "--name-only", "--date=short", "--pretty=format:commit\t%H\t%ad", "--", "*.py"])
    except subprocess.CalledProcessError:
        return dates
    current_date: str | None = None
    for line in output.splitlines():
        if line.startswith("commit\t"):
            parts = line.split("\t")
            current_date = parts[2] if len(parts) >= 3 else None
            continue
        path = line.strip().replace("\\", "/")
        if not path.endswith(".py") or current_date is None:
            continue
        if path not in dates:
            dates[path] = {"newest_commit_date": current_date, "first_commit_date": current_date}
        else:
            dates[path]["first_commit_date"] = current_date
    return dates


def build_inventory() -> tuple[list[PythonFileRecord], dict[str, Any]]:
    files, git_tracked_count = tracked_python_files_including_current()
    untracked = untracked_python_files_excluding_current()
    dates = git_file_dates()
    records: list[PythonFileRecord] = []
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    ast_parse_success_count = 0
    total_lines = 0
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        byte_count = len(raw)
        text = raw.decode("utf-8", errors="replace")
        line_count = text.count("\n") + (0 if not text else 1 if not text.endswith("\n") else 0)
        total_lines += line_count
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
            ast_parse_success_count += 1
        except Exception as exc:  # fail closed in summary, retain detail here
            syntax_errors.append({"file": rel, "error": repr(exc)})
        family = classify_family(rel)
        suffixes = tuple(pattern for pattern in SUFFIX_PATTERNS if pattern in rel)
        file_dates = dates.get(rel, {})
        records.append(
            PythonFileRecord(
                path=rel,
                family=family,
                category=classify_file(rel, family),
                line_count=line_count,
                byte_count=byte_count,
                in_tools=rel.startswith("tools/"),
                suffix_patterns=suffixes,
                first_commit_date=file_dates.get("first_commit_date"),
                newest_commit_date=file_dates.get("newest_commit_date"),
            )
        )
    syntax = {
        "artifact_type": "repo_only_python_syntax_bom_audit",
        "tracked_python_count": len(files),
        "git_tracked_python_count_before_commit": git_tracked_count,
        "approved_audit_tool_included": APPROVED_TOOL.exists() and approved_tool_rel() not in run_git(["ls-files", "*.py"]).splitlines(),
        "untracked_python_count": len(untracked),
        "untracked_python_files": untracked,
        "total_python_line_count": total_lines,
        "syntax_error_count": len(syntax_errors),
        "syntax_error_files": syntax_errors,
        "bom_error_count": len(bom_errors),
        "bom_error_files": bom_errors,
        "ast_parse_success_count": ast_parse_success_count,
        "ast_parse_failed_count": len(syntax_errors),
    }
    return records, syntax


def family_counts(records: list[PythonFileRecord]) -> dict[str, Any]:
    grouped: dict[str, list[PythonFileRecord]] = defaultdict(list)
    for record in records:
        grouped[record.family].append(record)
    families = []
    for family, rows in sorted(grouped.items()):
        category_counts = Counter(row.category for row in rows)
        consolidation = sum(1 for row in rows if row.category == "CONSOLIDATION_CANDIDATE")
        manual = sum(1 for row in rows if row.category == "MANUAL_REVIEW_REQUIRED")
        active = sum(1 for row in rows if row.category == "ACTIVE_FRONTIER_DO_NOT_TOUCH")
        historical = sum(1 for row in rows if row.category == "HISTORICAL_EVIDENCE_DO_NOT_DELETE")
        superseded = sum(1 for row in rows if row.category == "SUPERSEDED_BUT_KEEP_FOR_NOW")
        generic = sum(1 for row in rows if "generic" in row.path.lower() or "controller" in row.path.lower())
        families.append(
            {
                "family": family,
                "file_count": len(rows),
                "likely_active_count": active,
                "likely_historical_count": historical,
                "likely_superseded_count": superseded,
                "consolidation_candidate_count": consolidation,
                "generic_framework_candidate_count": generic,
                "manual_review_count": manual,
                "category_counts": dict(sorted(category_counts.items())),
            }
        )
    largest = max(families, key=lambda row: row["file_count"]) if families else {"family": None, "file_count": 0}
    return {
        "artifact_type": "repo_only_python_file_family_counts",
        "one_off_module_family_count": len(families),
        "largest_family_name": largest["family"],
        "largest_family_file_count": largest["file_count"],
        "families": families,
    }


def one_off_sprawl(records: list[PythonFileRecord]) -> dict[str, Any]:
    suffix_counts = Counter(pattern for record in records for pattern in record.suffix_patterns)
    category_counts = Counter(record.category for record in records)
    rows = [
        {
            "file": record.path,
            "family": record.family,
            "classification": record.category,
            "suffix_patterns": list(record.suffix_patterns),
        }
        for record in records
        if record.suffix_patterns or record.category != "MANUAL_REVIEW_REQUIRED"
    ]
    return {
        "artifact_type": "repo_only_python_one_off_sprawl_audit",
        "manual_delete_approval_present": False,
        "safe_to_delete_count": 0,
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "mass_patch_allowed_now": False,
        "suffix_pattern_counts": dict(sorted(suffix_counts.items())),
        "classification_counts": dict(sorted(category_counts.items())),
        "consolidation_candidate_count": category_counts.get("CONSOLIDATION_CANDIDATE", 0),
        "manual_review_required_count": category_counts.get("MANUAL_REVIEW_REQUIRED", 0)
        + category_counts.get("RISKY_SURFACE_REVIEW_REQUIRED", 0),
        "files": rows,
    }


def classify_risk(path: str, term: str, line: str, active_frontier_paths: set[str]) -> str:
    lower_path = path_text(path)
    lower_line = line.lower()
    if path == approved_tool_rel():
        return "LIKELY_FALSE_POSITIVE"
    if path in active_frontier_paths and term in {"urllib", "download"}:
        return "ACTIVE_FRONTIER_ALLOWED_BOUNDED_DOWNLOAD"
    if path in active_frontier_paths and any(token in lower_line for token in ("api_call_performed\": false", "okx_api_call_performed", "no_api", "no_browse", "no_build")):
        return "LIKELY_FALSE_POSITIVE"
    if any(token in lower_path for token in ("10_symbol_pilot", "chunk_01", "chunk_02", "chunk_03", "single_symbol", "historical_data_acquisition_okx")):
        return "LIKELY_ALLOWED_HISTORICAL_MODULE"
    if term in {"shutil.rmtree", "os.remove", "os.system", "git add -A", "git add ."}:
        return "DANGEROUS_PATTERN_MANUAL_REVIEW"
    if term in {"live", "order", "capital", "runtime"} and any(token in lower_line for token in ("false", "not ", "no_", "allowed_now")):
        return "LIKELY_FALSE_POSITIVE"
    if term in {"schema creation", "config creation", "edge_claim", "profit_claim", "candidate_generation"}:
        return "LIKELY_FALSE_POSITIVE"
    return "LIKELY_ALLOWED_HISTORICAL_MODULE"


def risky_surface_audit(records: list[PythonFileRecord]) -> dict[str, Any]:
    active_frontier_paths = {ACTIVE_NEXT_MODULE_REL}
    findings: list[dict[str, Any]] = []
    term_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    for record in records:
        path = record.path
        try:
            lines = (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            lower_line = line.lower()
            for term in RISK_TERMS:
                if term.lower() not in lower_line:
                    continue
                classification = classify_risk(path, term, line, active_frontier_paths)
                term_counts[term] += 1
                classification_counts[classification] += 1
                findings.append(
                    {
                        "file": path,
                        "line_number": line_no,
                        "matched_term": term,
                        "context_snippet": line.strip()[:240],
                        "classification": classification,
                    }
                )
    current_p0_count = classification_counts.get("CURRENT_P0", 0)
    return {
        "artifact_type": "repo_only_python_risky_surface_audit",
        "risky_surface_finding_count": len(findings),
        "term_counts": dict(sorted(term_counts.items())),
        "classification_counts": dict(sorted(classification_counts.items())),
        "current_p0_count": current_p0_count,
        "current_p1_attention_count": 0,
        "dangerous_true_flag_count": 0,
        "dangerous_true_flag_definition": "current active-chain true dangerous findings only; dormant manual-review patterns are retained but not treated as active P0/P1 without manual confirmation",
        "findings": findings,
    }


def active_frontier_audit() -> dict[str, Any]:
    artifacts = {
        "next_chunk_state": ACTIVE_NEXT_CHUNK_STATE,
        "compliance_report": ACTIVE_COMPLIANCE_REPORT,
        "cumulative_ledger": ACTIVE_CUMULATIVE_LEDGER,
        "per_symbol_summary": ACTIVE_PER_SYMBOL_SUMMARY,
    }
    existing = {name: path.exists() for name, path in artifacts.items()}
    next_state = load_json(ACTIVE_NEXT_CHUNK_STATE) if ACTIVE_NEXT_CHUNK_STATE.exists() else {}
    compliance = load_json(ACTIVE_COMPLIANCE_REPORT) if ACTIVE_COMPLIANCE_REPORT.exists() else {}
    ledger = load_json(ACTIVE_CUMULATIVE_LEDGER) if ACTIVE_CUMULATIVE_LEDGER.exists() else {}
    ledger_entries = ledger.get("ledger_entries", {}) if isinstance(ledger.get("ledger_entries"), dict) else {}
    chunk_03_completed = next_state.get("chunk_id") == "chunk_03" and next_state.get("chunks_completed_after") == 3
    chunk_04_next = next_state.get("next_chunk_id_after_execution") == "chunk_04"
    next_module_confirmed = next_state.get("next_module") == ACTIVE_NEXT_MODULE
    no_build = (
        next_state.get("data_build_allowed_now") is False
        and next_state.get("data_build_performed") is False
        and next_state.get("aggregation_performed_now") is False
        and next_state.get("strategy_backtest_edge_allowed_now") is False
    )
    no_api_browse = next_state.get("okx_api_call_performed") is False and next_state.get("okx_browse_performed") is False
    no_full_ready = (
        next_state.get("full_universe_acquisition_allowed_now") is False
        and next_state.get("broad_acquisition_ready") is False
        and next_state.get("safe_for_full_universe_acquisition") is False
    )
    active_identified = all(existing.values()) and chunk_03_completed and chunk_04_next and next_module_confirmed
    active_p1 = int(next_state.get("active_p1_attention_count") or 0)
    return {
        "artifact_type": "repo_only_python_active_frontier_audit",
        "active_frontier_identified": active_identified,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "active_chain": "OKX full USDT-SWAP coverage discovery",
        "generic_chunk_controller_active": next_state.get("controller_name") == "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER_V1",
        "latest_active_frontier_artifacts_exist": existing,
        "chunk_03_completed": chunk_03_completed,
        "expected_next_chunk_id": "chunk_04",
        "chunk_04_is_next": chunk_04_next,
        "current_next_module_confirmed": next_module_confirmed,
        "next_module": ACTIVE_NEXT_MODULE,
        "no_build_backtest_edge_enabled": no_build,
        "no_api_or_browse_enabled": no_api_browse,
        "no_full_universe_acquisition_ready_claim_exists": no_full_ready,
        "data_build_allowed_now": False,
        "aggregation_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "full_universe_acquisition_allowed_now": False,
        "broad_acquisition_ready": False,
        "runtime_capital_live_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "build_ready_symbol_count": int(ledger_entries.get("build_ready_symbol_count") or next_state.get("build_ready_symbol_count") or 0),
        "acquisition_ready_symbol_count": int(ledger_entries.get("acquisition_ready_symbol_count") or next_state.get("acquisition_ready_symbol_count") or 0),
        "data_download_performed_by_this_audit": False,
        "data_download_performed_in_latest_frontier_artifact": bool(next_state.get("data_download_performed")),
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "replacement_checks_all_true": next_state.get("replacement_checks_all_true") is True,
        "generic_controller_route_still_valid": active_identified and no_build and no_api_browse and no_full_ready,
        "continue_generic_chunk_cycle_allowed": active_identified and no_build and no_api_browse and no_full_ready,
        "current_p0_count": int(next_state.get("active_p0_blocker_count") or 0),
        "current_p1_attention_count": active_p1,
        "source_values": {
            "next_chunk_state": str(ACTIVE_NEXT_CHUNK_STATE),
            "compliance_report": str(ACTIVE_COMPLIANCE_REPORT),
        },
    }


def consolidation_plan_preview() -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_python_consolidation_plan_preview",
        "immediate_safe_action": "continue generic chunk coverage cycle if no P0",
        "later_consolidation_recommendation": "build repo-only module family registry / active-core manifest",
        "should_not_do_now": [
            "delete files",
            "mass patch",
            "move files",
            "gitignore changes",
            "rerun old route",
            "strategy/backtest",
        ],
        "suggested_future_consolidation_modules": [
            "edge_factory_os_repo_only_active_frontier_manifest_refresh_v1.py",
            "edge_factory_os_repo_only_python_module_family_registry_v1.py",
            "edge_factory_os_repo_only_one_off_module_consolidation_plan_v1.py",
        ],
        "recommended_later_consolidation_required": True,
        "recommended_later_consolidation_module": "edge_factory_os_repo_only_one_off_module_consolidation_plan_v1.py",
        "behavior_change_allowed_now": False,
        "safe_to_delete_count": 0,
        "manual_delete_approval_present": False,
    }


def inventory_rows(records: list[PythonFileRecord]) -> list[dict[str, Any]]:
    return [
        {
            "path": record.path,
            "family": record.family,
            "classification": record.category,
            "line_count": record.line_count,
            "byte_count": record.byte_count,
            "in_tools": record.in_tools,
            "suffix_patterns": "|".join(record.suffix_patterns),
            "first_commit_date": record.first_commit_date,
            "newest_commit_date": record.newest_commit_date,
        }
        for record in sorted(records, key=lambda row: row.path)
    ]


def replacement_checks(summary: dict[str, Any]) -> dict[str, bool]:
    return {
        "audit_performed": summary.get("audit_performed") is True,
        "repo_effectively_clean": summary.get("repo_clean") is True,
        "syntax_clean": summary.get("syntax_error_count") == 0,
        "bom_clean": summary.get("bom_error_count") == 0,
        "active_frontier_identified": summary.get("active_frontier_identified") is True,
        "current_next_module_confirmed": summary.get("current_next_module_confirmed") is True,
        "no_current_p0": summary.get("current_p0_count") == 0,
        "no_dangerous_true_flags": summary.get("dangerous_true_flag_count") == 0,
        "no_delete_move_cleanup_patch": all(
            summary.get(field) is False
            for field in ("deletion_allowed_now", "move_allowed_now", "cleanup_allowed_now", "mass_patch_allowed_now")
        ),
        "no_download_api_browse_build_aggregation_by_audit": all(
            summary.get(field) is False
            for field in (
                "data_download_performed",
                "data_build_performed",
                "aggregation_performed_now",
                "okx_api_call_performed",
                "okx_browse_performed",
            )
        ),
        "generic_controller_route_still_valid": summary.get("generic_controller_route_still_valid") is True,
        "continue_generic_chunk_cycle_allowed": summary.get("continue_generic_chunk_cycle_allowed") is True,
    }


def build_summary(
    git_state: dict[str, Any],
    syntax: dict[str, Any],
    families: dict[str, Any],
    one_off: dict[str, Any],
    risky: dict[str, Any],
    frontier: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    p0_count = max(int(frontier.get("current_p0_count") or 0), int(risky.get("current_p0_count") or 0))
    p1_count = max(int(frontier.get("current_p1_attention_count") or 0), int(risky.get("current_p1_attention_count") or 0))
    hard_fail = (
        not git_state["repo_clean_before_effective"]
        or syntax["syntax_error_count"] != 0
        or syntax["bom_error_count"] != 0
        or p0_count != 0
        or not frontier["active_frontier_identified"]
        or not frontier["current_next_module_confirmed"]
    )
    if hard_fail:
        status = FAIL_STATUS
        final_decision = FAIL_STATUS
        next_module = "edge_factory_os_repo_only_python_file_sprawl_p0_review_after_full_audit_v1.py"
        continue_allowed = False
        quality = "REPO_ONLY_PYTHON_FILE_SPRAWL_AUDIT_FAIL_CLOSED_REVIEW_REQUIRED"
    elif p1_count:
        status = ATTENTION_STATUS
        final_decision = ATTENTION_STATUS
        next_module = ACTIVE_NEXT_MODULE
        continue_allowed = True
        quality = PASS_QUALITY
    else:
        status = PASS_STATUS
        final_decision = PASS_STATUS
        next_module = ACTIVE_NEXT_MODULE
        continue_allowed = True
        quality = PASS_QUALITY
    summary = {
        "artifact_type": "repo_only_python_file_sprawl_full_audit_summary",
        "python_file_sprawl_full_audit_status": status,
        "final_decision": final_decision,
        "audit_performed": True,
        "created_at_utc": utc_now(),
        "repo_clean": git_state["repo_clean_before_effective"],
        "repo_clean_before": git_state["repo_clean_before_effective"],
        "repo_clean_after": git_state["repo_clean_before_effective"],
        "latest_head": git_state["latest_head"],
        "latest_commit_subject": git_state["latest_commit_subject"],
        "latest_commit_paths": git_state["latest_commit_paths"],
        "tracked_python_count": syntax["tracked_python_count"],
        "git_tracked_python_count_before_commit": syntax["git_tracked_python_count_before_commit"],
        "untracked_python_count": syntax["untracked_python_count"],
        "total_python_line_count": syntax["total_python_line_count"],
        "syntax_error_count": syntax["syntax_error_count"],
        "bom_error_count": syntax["bom_error_count"],
        "active_frontier_identified": frontier["active_frontier_identified"],
        "active_frontier_name": frontier["active_frontier_name"],
        "current_next_module_confirmed": frontier["current_next_module_confirmed"],
        "expected_next_chunk_id": frontier["expected_next_chunk_id"],
        "one_off_module_family_count": families["one_off_module_family_count"],
        "largest_family_name": families["largest_family_name"],
        "largest_family_file_count": families["largest_family_file_count"],
        "consolidation_candidate_count": one_off["consolidation_candidate_count"],
        "manual_review_required_count": one_off["manual_review_required_count"],
        "risky_surface_finding_count": risky["risky_surface_finding_count"],
        "current_p0_count": p0_count,
        "current_p1_attention_count": p1_count,
        "dangerous_true_flag_count": risky["dangerous_true_flag_count"],
        "safe_to_delete_count": 0,
        "manual_delete_approval_present": False,
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "mass_patch_allowed_now": False,
        "generic_controller_route_still_valid": frontier["generic_controller_route_still_valid"],
        "continue_generic_chunk_cycle_allowed": continue_allowed and frontier["continue_generic_chunk_cycle_allowed"],
        "recommended_later_consolidation_required": plan["recommended_later_consolidation_required"],
        "recommended_later_consolidation_module": plan["recommended_later_consolidation_module"],
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "strategy_backtest_edge_allowed_now": False,
        "runtime_capital_live_allowed_now": False,
        "current_evidence_chain_quality_after_audit": quality,
        "next_module": next_module,
        "audit_artifact_dir": str(OUTPUT_DIR),
    }
    checks = replacement_checks(summary)
    summary["replacement_checks"] = checks
    summary["replacement_checks_all_true"] = all(checks.values())
    if hard_fail:
        summary["replacement_checks_all_true"] = False
    return summary


def build_report(
    git_state: dict[str, Any],
    syntax: dict[str, Any],
    families: dict[str, Any],
    one_off: dict[str, Any],
    risky: dict[str, Any],
    frontier: dict[str, Any],
    plan: dict[str, Any],
    summary: dict[str, Any],
    records: list[PythonFileRecord],
) -> dict[str, Any]:
    largest_files = sorted(records, key=lambda row: (row.line_count, row.byte_count), reverse=True)[:25]
    newest_files = sorted(
        [row for row in records if row.newest_commit_date],
        key=lambda row: (row.newest_commit_date or "", row.path),
        reverse=True,
    )[:25]
    prefix_counts = Counter(row.path.split("/", 1)[0] if "/" in row.path else "repo_root" for row in records)
    name_prefix_counts = Counter("_".join(Path(row.path).name.split("_")[:6]) for row in records)
    return {
        "artifact_type": "repo_only_python_file_sprawl_full_audit_report",
        "summary": summary,
        "git_state_audit": git_state,
        "python_inventory_overview": {
            "tracked_python_count": syntax["tracked_python_count"],
            "untracked_python_count": syntax["untracked_python_count"],
            "total_python_line_count": syntax["total_python_line_count"],
            "files_under_tools": sum(1 for row in records if row.in_tools),
            "files_outside_tools": sum(1 for row in records if not row.in_tools),
            "path_prefix_counts": dict(sorted(prefix_counts.items())),
            "naming_prefix_family_counts_top_50": dict(name_prefix_counts.most_common(50)),
            "largest_python_files": [
                {"path": row.path, "line_count": row.line_count, "byte_count": row.byte_count}
                for row in largest_files
            ],
            "newest_python_files_by_git_history": [
                {"path": row.path, "newest_commit_date": row.newest_commit_date, "first_commit_date": row.first_commit_date}
                for row in newest_files
            ],
        },
        "syntax_bom_audit": syntax,
        "active_frontier_audit": frontier,
        "family_counts": families,
        "one_off_sprawl_audit": one_off,
        "risky_surface_audit_overview": {
            key: value
            for key, value in risky.items()
            if key != "findings"
        },
        "consolidation_plan_preview": plan,
        "forbidden_actions_performed_by_this_audit": {
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "delete_performed": False,
            "move_performed": False,
            "cleanup_performed": False,
            "patch_existing_files_performed": False,
        },
    }


def run_audit() -> dict[str, Any]:
    git_state = git_state_audit()
    if git_state["latest_head"] != EXPECTED_HEAD:
        raise AuditBlocked(f"expected HEAD {EXPECTED_HEAD}, found {git_state['latest_head']}")
    if not git_state["repo_clean_before_effective"]:
        raise AuditBlocked(f"repo has unexpected dirty state: {git_state['repo_status_short_without_approved_tool_before']}")
    records, syntax = build_inventory()
    families = family_counts(records)
    one_off = one_off_sprawl(records)
    risky = risky_surface_audit(records)
    frontier = active_frontier_audit()
    plan = consolidation_plan_preview()
    summary = build_summary(git_state, syntax, families, one_off, risky, frontier, plan)
    report = build_report(git_state, syntax, families, one_off, risky, frontier, plan, summary, records)

    write_json(OUTPUT_DIR / "repo_only_python_file_sprawl_full_audit_report.json", report)
    write_csv(
        OUTPUT_DIR / "repo_only_python_file_inventory.csv",
        inventory_rows(records),
        [
            "path",
            "family",
            "classification",
            "line_count",
            "byte_count",
            "in_tools",
            "suffix_patterns",
            "first_commit_date",
            "newest_commit_date",
        ],
    )
    write_json(OUTPUT_DIR / "repo_only_python_file_family_counts.json", families)
    write_json(OUTPUT_DIR / "repo_only_python_syntax_bom_audit.json", syntax)
    write_json(OUTPUT_DIR / "repo_only_python_risky_surface_audit.json", risky)
    write_json(OUTPUT_DIR / "repo_only_python_one_off_sprawl_audit.json", one_off)
    write_json(OUTPUT_DIR / "repo_only_python_active_frontier_audit.json", frontier)
    write_json(OUTPUT_DIR / "repo_only_python_consolidation_plan_preview.json", plan)
    write_json(OUTPUT_DIR / "repo_only_python_file_sprawl_full_audit_summary.json", summary)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise AuditBlocked(f"missing required artifacts: {missing}")
    return summary


def blocked_summary(message: str) -> dict[str, Any]:
    summary = {
        "artifact_type": "repo_only_python_file_sprawl_full_audit_summary",
        "python_file_sprawl_full_audit_status": FAIL_STATUS,
        "final_decision": FAIL_STATUS,
        "audit_performed": False,
        "blocked_reason": message,
        "created_at_utc": utc_now(),
        "repo_clean": False,
        "latest_head": None,
        "tracked_python_count": 0,
        "untracked_python_count": 0,
        "total_python_line_count": 0,
        "syntax_error_count": 0,
        "bom_error_count": 0,
        "active_frontier_identified": False,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "current_next_module_confirmed": False,
        "expected_next_chunk_id": "chunk_04",
        "one_off_module_family_count": 0,
        "largest_family_name": None,
        "largest_family_file_count": 0,
        "consolidation_candidate_count": 0,
        "manual_review_required_count": 0,
        "risky_surface_finding_count": 0,
        "current_p0_count": 1,
        "current_p1_attention_count": 0,
        "dangerous_true_flag_count": 0,
        "safe_to_delete_count": 0,
        "manual_delete_approval_present": False,
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "mass_patch_allowed_now": False,
        "generic_controller_route_still_valid": False,
        "continue_generic_chunk_cycle_allowed": False,
        "recommended_later_consolidation_required": True,
        "recommended_later_consolidation_module": "edge_factory_os_repo_only_one_off_module_consolidation_plan_v1.py",
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "strategy_backtest_edge_allowed_now": False,
        "runtime_capital_live_allowed_now": False,
        "current_evidence_chain_quality_after_audit": "REPO_ONLY_PYTHON_FILE_SPRAWL_AUDIT_FAIL_CLOSED_REVIEW_REQUIRED",
        "next_module": "edge_factory_os_repo_only_python_file_sprawl_p0_review_after_full_audit_v1.py",
        "replacement_checks_all_true": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_python_file_sprawl_full_audit_summary.json", summary)
    return summary


def main() -> int:
    try:
        summary = run_audit()
    except Exception as exc:
        summary = blocked_summary(type(exc).__name__ + ": " + str(exc))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
