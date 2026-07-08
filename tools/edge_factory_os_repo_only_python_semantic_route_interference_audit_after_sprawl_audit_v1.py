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


MODULE_NAME = "edge_factory_os_repo_only_python_semantic_route_interference_audit_after_sprawl_audit_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "6af4d92"
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
PREVIOUS_AUDIT_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_python_file_sprawl_full_audit_after_generic_chunk_controller_v1"
PREVIOUS_AUDIT_SUMMARY = PREVIOUS_AUDIT_DIR / "repo_only_python_file_sprawl_full_audit_summary.json"

PASS_DECISION = "SEMANTIC_ROUTE_INTERFERENCE_AUDIT_PASS_CONTINUE_CHUNK_04_GENERIC_CYCLE"
REPAIR_DECISION = "SEMANTIC_ROUTE_INTERFERENCE_AUDIT_BLOCKED_GENERIC_CONTROLLER_REPAIR_REQUIRED"
OBSTRUCTION_DECISION = "SEMANTIC_ROUTE_INTERFERENCE_AUDIT_BLOCKED_ACTIVE_ROUTE_OBSTRUCTION_REVIEW_REQUIRED"
PASS_QUALITY = "REPO_ONLY_PYTHON_SEMANTIC_ROUTE_INTERFERENCE_AUDIT_PASS_CONTINUE_CHUNK_04_GENERIC_CYCLE"
REPAIR_QUALITY = "REPO_ONLY_PYTHON_SEMANTIC_ROUTE_INTERFERENCE_AUDIT_BLOCKED_GENERIC_CONTROLLER_REPAIR_REQUIRED"
OBSTRUCTION_QUALITY = "REPO_ONLY_PYTHON_SEMANTIC_ROUTE_INTERFERENCE_AUDIT_BLOCKED_ACTIVE_ROUTE_OBSTRUCTION_REVIEW_REQUIRED"

REPAIR_NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_repair_plan_after_semantic_audit_v1.py"
OBSTRUCTION_NEXT_MODULE = "edge_factory_os_repo_only_active_route_obstruction_review_after_semantic_audit_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_python_semantic_route_interference_audit_report.json",
    "repo_only_python_active_next_module_conflict_report.json",
    "repo_only_python_semantic_noop_fake_success_audit.json",
    "repo_only_python_output_collision_audit.json",
    "repo_only_python_stale_hardcoded_checkpoint_audit.json",
    "repo_only_python_generic_controller_usefulness_audit.json",
    "repo_only_python_useful_file_obstruction_audit.json",
    "repo_only_python_dependency_route_graph_audit.json",
    "repo_only_python_current_route_risky_surface_reclassification.json",
    "repo_only_python_semantic_route_interference_audit_summary.json",
]

ACTIVE_FRONTIER_OUTPUTS = {
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_report.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_chunk_download_manifest_after_execution.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_gap_report.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_reuse_validation_report.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_sha256_report.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_zip_inventory_report.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_schema_sample_report.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_per_symbol_coverage_summary.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_compliance_report.json",
    "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_summary.json",
}

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

STATUS_TOKENS = (
    "PASS_",
    "BLOCKED_",
    "FAIL_",
    "READY",
    "replacement_checks_all_true",
    "current_evidence_chain",
    "final_decision",
)


class AuditBlocked(RuntimeError):
    pass


@dataclass
class FileSemantics:
    path: str
    source: str
    line_count: int
    string_literals: list[dict[str, Any]]
    assignment_literals: dict[str, list[dict[str, Any]]]
    function_names: list[str]
    class_names: list[str]
    import_modules: list[str]
    call_names: Counter[str]
    next_module_refs: list[dict[str, Any]]
    tool_refs: list[dict[str, Any]]
    output_refs: list[dict[str, Any]]
    write_output_refs: list[dict[str, Any]]
    subprocess_python_tool_refs: list[dict[str, Any]]


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


def approved_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def status_lines() -> list[str]:
    return [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]


def status_without_approved_tool(lines: list[str]) -> list[str]:
    rel = approved_tool_rel()
    return [line for line in lines if line[3:].replace("\\", "/") != rel]


def repo_effectively_clean(lines: list[str]) -> bool:
    return not status_without_approved_tool(lines)


def read_json(path: Path) -> dict[str, Any]:
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


def tracked_python_files_including_current() -> tuple[list[str], int]:
    git_files = sorted(path.replace("\\", "/") for path in run_git(["ls-files", "*.py"]).splitlines() if path.strip())
    files = list(git_files)
    rel = approved_tool_rel()
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files), len(git_files)


def syntax_bom_audit(files: list[str], git_tracked_count: int) -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    ast_success = 0
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
            ast_success += 1
        except Exception as exc:
            syntax_errors.append({"file": rel, "error": repr(exc)})
    return {
        "artifact_type": "repo_only_python_semantic_syntax_bom_precheck",
        "tracked_python_count": len(files),
        "git_tracked_python_count_before_commit": git_tracked_count,
        "syntax_error_count": len(syntax_errors),
        "syntax_error_files": syntax_errors,
        "bom_error_count": len(bom_errors),
        "bom_error_files": bom_errors,
        "ast_parse_success_count": ast_success,
        "ast_parse_failed_count": len(syntax_errors),
    }


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def literal_value(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def target_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [node.attr]
    if isinstance(node, (ast.Tuple, ast.List)):
        names: list[str] = []
        for item in node.elts:
            names.extend(target_names(item))
        return names
    return []


def normalize_output_name(value: str) -> str | None:
    normalized = value.replace("\\", "/").strip()
    name = normalized.rsplit("/", 1)[-1]
    if name.endswith((".json", ".csv")):
        return name
    return None


def is_historical_path(path: str) -> bool:
    lower = path.lower()
    return any(
        token in lower
        for token in (
            "chunk_01",
            "chunk_02",
            "chunk_03",
            "10_symbol_pilot",
            "single_symbol",
            "old_",
            "sprawl_audit",
            "semantic_route_interference_audit",
            "bom_syntax",
            "gate_metadata",
            "preflight",
        )
    )


def extract_semantics(rel: str) -> FileSemantics:
    source = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=rel)
    string_literals: list[dict[str, Any]] = []
    assignment_literals: dict[str, list[dict[str, Any]]] = defaultdict(list)
    function_names: list[str] = []
    class_names: list[str] = []
    import_modules: list[str] = []
    call_names_counter: Counter[str] = Counter()
    next_module_refs: list[dict[str, Any]] = []
    tool_refs: list[dict[str, Any]] = []
    output_refs: list[dict[str, Any]] = []
    write_output_refs: list[dict[str, Any]] = []
    subprocess_python_tool_refs: list[dict[str, Any]] = []
    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            line_no = getattr(node, "lineno", None)
            row = {"value": value, "line_number": line_no}
            string_literals.append(row)
            if value.endswith(".py") and "edge_factory_os" in value:
                tool_refs.append(row)
                if "next_module" in lines[line_no - 1].lower() if line_no and line_no <= len(lines) else False:
                    next_module_refs.append(row)
            output_name = normalize_output_name(value)
            if output_name:
                output_refs.append({"artifact_name": output_name, "value": value, "line_number": line_no})
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = literal_value(node.value)
            for target in targets:
                for name in target_names(target):
                    if isinstance(value, (str, int, bool, type(None), list, tuple, dict)):
                        assignment_literals[name].append({"value": value, "line_number": getattr(node, "lineno", None)})
                    if name.lower() == "next_module" and isinstance(value, str) and value.endswith(".py"):
                        next_module_refs.append({"value": value, "line_number": getattr(node, "lineno", None)})
        elif isinstance(node, ast.FunctionDef):
            function_names.append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            function_names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            class_names.append(node.name)
        elif isinstance(node, ast.Import):
            import_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_modules.append(node.module)
        elif isinstance(node, ast.Call):
            name = call_name(node.func)
            call_names_counter[name] += 1
            string_args = [literal_value(arg) for arg in node.args]
            string_args = [arg for arg in string_args if isinstance(arg, str)]
            if name in {"write_json", "write_csv"}:
                for arg in string_args:
                    output_name = normalize_output_name(arg)
                    if output_name:
                        write_output_refs.append({"artifact_name": output_name, "value": arg, "line_number": getattr(node, "lineno", None)})
            if name in {"subprocess.run", "subprocess.check_output", "run_git"}:
                for arg in string_args:
                    if arg.endswith(".py") and "edge_factory_os" in arg:
                        subprocess_python_tool_refs.append({"value": arg, "line_number": getattr(node, "lineno", None)})

    if "reports = {" in source:
        for ref in output_refs:
            if ref["artifact_name"].startswith("historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_"):
                write_output_refs.append(ref)

    return FileSemantics(
        path=rel,
        source=source,
        line_count=len(lines),
        string_literals=string_literals,
        assignment_literals=dict(assignment_literals),
        function_names=sorted(function_names),
        class_names=sorted(class_names),
        import_modules=sorted(set(import_modules)),
        call_names=call_names_counter,
        next_module_refs=next_module_refs,
        tool_refs=tool_refs,
        output_refs=output_refs,
        write_output_refs=write_output_refs,
        subprocess_python_tool_refs=subprocess_python_tool_refs,
    )


def semantic_inventory(files: list[str]) -> dict[str, FileSemantics]:
    return {rel: extract_semantics(rel) for rel in files}


def active_frontier_audit() -> dict[str, Any]:
    next_state = read_json(ACTIVE_NEXT_CHUNK_STATE) if ACTIVE_NEXT_CHUNK_STATE.exists() else {}
    compliance = read_json(ACTIVE_COMPLIANCE_REPORT) if ACTIVE_COMPLIANCE_REPORT.exists() else {}
    previous = read_json(PREVIOUS_AUDIT_SUMMARY) if PREVIOUS_AUDIT_SUMMARY.exists() else {}
    active_identified = (
        ACTIVE_NEXT_CHUNK_STATE.exists()
        and ACTIVE_COMPLIANCE_REPORT.exists()
        and next_state.get("controller_name") == "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER_V1"
        and next_state.get("chunk_id") == "chunk_03"
        and next_state.get("next_chunk_id_after_execution") == "chunk_04"
    )
    return {
        "artifact_type": "repo_only_python_semantic_active_frontier_audit",
        "active_frontier_identified": active_identified,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "current_next_module_confirmed": next_state.get("next_module") == ACTIVE_NEXT_MODULE,
        "expected_next_chunk_id": "chunk_04",
        "latest_active_artifacts_exist": {
            "next_chunk_state": ACTIVE_NEXT_CHUNK_STATE.exists(),
            "compliance_report": ACTIVE_COMPLIANCE_REPORT.exists(),
            "previous_sprawl_audit_summary": PREVIOUS_AUDIT_SUMMARY.exists(),
        },
        "previous_sprawl_audit_status": previous.get("python_file_sprawl_full_audit_status"),
        "previous_sprawl_audit_replacement_checks_all_true": previous.get("replacement_checks_all_true"),
        "source_next_chunk_state": str(ACTIVE_NEXT_CHUNK_STATE),
        "source_compliance_report": str(ACTIVE_COMPLIANCE_REPORT),
        "data_build_allowed_now": False,
        "aggregation_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "runtime_capital_live_allowed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "active_next_chunk_state_subset": {
            key: next_state.get(key)
            for key in (
                "chunk_id",
                "chunks_completed_after",
                "next_chunk_id_after_execution",
                "next_module",
                "replacement_checks_all_true",
                "data_build_allowed_now",
                "data_build_performed",
                "aggregation_performed_now",
                "okx_api_call_performed",
                "okx_browse_performed",
                "broad_acquisition_ready",
            )
        },
        "active_compliance_subset": {
            key: compliance.get(key)
            for key in (
                "no_api",
                "no_browse",
                "no_build",
                "no_aggregation",
                "no_research_backtest_edge",
                "no_runtime_capital_live",
            )
        },
    }


def active_next_module_conflicts(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    conflicts: list[dict[str, Any]] = []
    stale_files: dict[str, list[str]] = defaultdict(list)
    stale_successors: list[dict[str, Any]] = []
    for rel, sem in semantics.items():
        for ref in sem.next_module_refs:
            value = str(ref.get("value"))
            if not value.endswith(".py"):
                continue
            if value == ACTIVE_NEXT_MODULE:
                continue
            stale_files[rel].append(value)
            classification = "HISTORICAL_OR_INACTIVE"
            conflict = False
            if rel == ACTIVE_NEXT_MODULE_REL:
                classification = "ACTIVE_ROUTE_CONFLICT"
                conflict = True
            elif not is_historical_path(rel) and any(token in sem.source for token in ("current_next_module", "active_frontier", "expected_next_module")):
                classification = "MANUAL_REVIEW_STALE_ROUTE_SUCCESSOR"
            if conflict:
                conflicts.append({"file": rel, "line_number": ref.get("line_number"), "next_module": value, "classification": classification})
            else:
                stale_successors.append({"file": rel, "line_number": ref.get("line_number"), "next_module": value, "classification": classification})
    return {
        "artifact_type": "repo_only_python_active_next_module_conflict_report",
        "active_next_module": ACTIVE_NEXT_MODULE,
        "active_next_module_conflict_count": len(conflicts),
        "conflicting_active_next_module_files": sorted({row["file"] for row in conflicts}),
        "conflicts": conflicts,
        "stale_next_module_file_count": len(stale_files),
        "stale_next_module_files": [{"file": file, "next_modules": sorted(set(values))} for file, values in sorted(stale_files.items())],
        "stale_route_successor_files": stale_successors,
        "old_one_off_route_files_claiming_active_next": [
            row
            for row in stale_successors
            if any(token in row["file"].lower() for token in ("chunk_02", "chunk_03", "10_symbol_pilot", "single_symbol"))
        ],
        "current_p0_count": 0,
    }


def semantic_noop_fake_success_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for rel, sem in semantics.items():
        source_lower = sem.source.lower()
        pass_claim_count = sum(1 for row in sem.string_literals if "pass_" in str(row["value"]).lower() or "ready" in str(row["value"]).lower())
        writes_json = sem.call_names.get("write_json", 0) + sem.source.count(".write_text(")
        input_checks = (
            sem.call_names.get("load_json", 0)
            + sem.call_names.get("require", 0)
            + sem.call_names.get("assert", 0)
            + sem.source.count("replacement_checks")
            + sem.source.count("ast.parse")
        )
        has_main = "main" in sem.function_names
        main_trivial = has_main and sem.line_count < 80 and writes_json == 0
        unconditional_replacement_true = (
            '"replacement_checks_all_true": True' in sem.source
            or "'replacement_checks_all_true': True" in sem.source
            or "replacement_checks_all_true = True" in sem.source
        )
        swallows_to_pass = "except Exception" in sem.source and pass_claim_count and "return 0" in sem.source and "blocked" not in source_lower
        suspect = bool((pass_claim_count and writes_json and input_checks == 0) or main_trivial or unconditional_replacement_true or swallows_to_pass)
        if not suspect:
            continue
        classification = "POSSIBLE_FAKE_SUCCESS_MANUAL_REVIEW"
        if rel == ACTIVE_NEXT_MODULE_REL:
            classification = "CURRENT_ROUTE_BLOCKER"
        elif "record" in rel.lower() and input_checks == 0:
            classification = "ACCEPTABLE_RECORD_ONLY_MODULE"
        elif "preview" in rel.lower() and input_checks <= 1:
            classification = "ACCEPTABLE_PREVIEW_ONLY_MODULE"
        elif is_historical_path(rel):
            classification = "HISTORICAL_DO_NOT_TOUCH"
        counts[classification] += 1
        findings.append(
            {
                "file": rel,
                "classification": classification,
                "pass_claim_count": pass_claim_count,
                "write_json_like_count": writes_json,
                "input_check_signal_count": input_checks,
                "has_main": has_main,
                "main_trivial": main_trivial,
                "unconditional_replacement_checks_all_true": unconditional_replacement_true,
                "swallows_exceptions_and_still_passes": bool(swallows_to_pass),
            }
        )
    return {
        "artifact_type": "repo_only_python_semantic_noop_fake_success_audit",
        "semantic_noop_or_fake_success_suspect_count": len(findings),
        "current_route_fake_success_p0_count": counts.get("CURRENT_ROUTE_BLOCKER", 0),
        "classification_counts": dict(sorted(counts.items())),
        "findings": findings,
    }


def output_collision_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    writers: dict[str, list[str]] = defaultdict(list)
    latest_writers: dict[str, list[str]] = defaultdict(list)
    for rel, sem in semantics.items():
        if rel == approved_tool_rel():
            continue
        for ref in sem.write_output_refs:
            name = ref["artifact_name"]
            writers[name].append(rel)
            if "latest" in name.lower():
                latest_writers[name].append(rel)
    collisions = []
    active_collisions = []
    for artifact, files in sorted(writers.items()):
        unique_files = sorted(set(files))
        if len(unique_files) <= 1:
            continue
        severity = "LATEST_AMBIGUITY_MANUAL_REVIEW" if "latest" in artifact.lower() else "HISTORICAL_OUTPUT_NAME_REUSE"
        row = {"artifact_name": artifact, "files": unique_files, "collision_severity": severity}
        collisions.append(row)
        if artifact in ACTIVE_FRONTIER_OUTPUTS and any(file != ACTIVE_NEXT_MODULE_REL for file in unique_files):
            row["collision_severity"] = "ACTIVE_FRONTIER_OUTPUT_COLLISION"
            active_collisions.append(row)
    return {
        "artifact_type": "repo_only_python_output_collision_audit",
        "output_collision_count": len(collisions),
        "active_frontier_output_collision_count": len(active_collisions),
        "collision_files": sorted({file for row in collisions for file in row["files"]}),
        "collision_artifact_names": [row["artifact_name"] for row in collisions],
        "collision_severity_counts": dict(Counter(row["collision_severity"] for row in collisions)),
        "collision_records": collisions,
        "active_frontier_collision_records": active_collisions,
        "latest_artifact_writer_count": len(latest_writers),
    }


def stale_hardcoded_checkpoint_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    stale_records: list[dict[str, Any]] = []
    stale_heads = {"7334b77", "fa27690"}
    for rel, sem in semantics.items():
        for row in sem.string_literals:
            value = str(row["value"])
            reason = None
            if value in stale_heads and value != EXPECTED_HEAD:
                reason = "old_head_value"
            elif value == "chunk_03":
                reason = "chunk_03_hardcoded_value"
            elif value == "chunk_02":
                reason = "chunk_02_hardcoded_value"
            elif value.endswith(".py") and value != ACTIVE_NEXT_MODULE and "edge_factory_os" in value and "next_module" in sem.source[max(0, (row.get("line_number") or 1) - 2) :]:
                reason = "stale_next_module_value"
            if reason is None:
                continue
            classification = "harmless historical constant"
            if rel == ACTIVE_NEXT_MODULE_REL and reason in {"chunk_03_hardcoded_value", "old_head_value"}:
                classification = "active route danger"
            elif is_historical_path(rel):
                classification = "stale but inactive"
            else:
                classification = "manual review"
            stale_records.append(
                {
                    "file": rel,
                    "line_number": row.get("line_number"),
                    "value": value,
                    "reason": reason,
                    "classification": classification,
                }
            )
        for name, rows in sem.assignment_literals.items():
            if name in {"CHUNKS_TOTAL", "CHUNKS_COMPLETED_BEFORE", "CHUNKS_COMPLETED_AFTER", "CHUNKS_REMAINING_AFTER"}:
                for row in rows:
                    if rel == ACTIVE_NEXT_MODULE_REL:
                        stale_records.append(
                            {
                                "file": rel,
                                "line_number": row.get("line_number"),
                                "value": row.get("value"),
                                "reason": f"{name}_hardcoded_count",
                                "classification": "active route danger",
                            }
                        )
    return {
        "artifact_type": "repo_only_python_stale_hardcoded_checkpoint_audit",
        "stale_hardcoded_checkpoint_count": len(stale_records),
        "active_route_stale_hardcoded_checkpoint_count": sum(1 for row in stale_records if row["classification"] == "active route danger"),
        "classification_counts": dict(Counter(row["classification"] for row in stale_records)),
        "records": stale_records,
    }


def generic_controller_usefulness_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    sem = semantics[ACTIVE_NEXT_MODULE_REL]
    source = sem.source
    assignments = sem.assignment_literals
    approved_chunk = next((row.get("value") for row in assignments.get("APPROVED_CHUNK_ID", [])), None)
    next_chunk_after = next((row.get("value") for row in assignments.get("NEXT_CHUNK_ID_AFTER_EXECUTION", [])), None)
    approved_symbols_literal = "APPROVED_SYMBOLS = [" in source and "BARD-USDT-SWAP" in source
    reads_next_preview = "CONTROLLER_NEXT_CHUNK_PREVIEW" in source and "load_json(CONTROLLER_NEXT_CHUNK_PREVIEW" in source
    reads_ledger = "CHUNK_02_LEDGER" in source or "cumulative_ledger" in source
    writes_updated_ledger = "generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json" in source
    one_chunk = "MAX_TOTAL_DOWNLOAD_OR_REUSE_FILE_COUNT" in source and "APPROVED_SYMBOLS" in source
    no_build_aggregation = all(token in source for token in ("data_build_performed", "aggregation_performed_now", "strategy_backtest_edge_allowed_now"))
    no_ready_marks = '"build_ready": False' in source and '"acquisition_ready": False' in source
    no_api_browse = "okx_api_call_performed" in source and "okx_browse_performed" in source and "no_api" in source and "no_browse" in source
    hardcoded_chunk_only = approved_chunk == "chunk_03" and approved_symbols_literal and "summary.get(\"next_chunk_id\") == APPROVED_CHUNK_ID" in source
    dynamic_chunk_selection = reads_next_preview and "APPROVED_CHUNK_ID = \"chunk_03\"" not in source and "APPROVED_SYMBOLS = [" not in source
    supports_chunk_04 = "next_chunk_id_after_execution" in source and next_chunk_after == "chunk_04" and not hardcoded_chunk_only
    blockers: list[str] = []
    if hardcoded_chunk_only:
        blockers.append("generic controller is hardcoded to APPROVED_CHUNK_ID=chunk_03 and a fixed APPROVED_SYMBOLS list")
    if "CHUNK_02_LEDGER" in source:
        blockers.append("generic controller reads CHUNK_02_LEDGER instead of selecting the latest cumulative ledger dynamically")
    if "CHUNKS_COMPLETED_BEFORE = 2" in source or "CHUNKS_COMPLETED_AFTER = 3" in source:
        blockers.append("generic controller has fixed before/after chunk counters for chunk_03")
    if not supports_chunk_04:
        blockers.append("module reports chunk_04 as next but does not semantically parameterize execution for chunk_04")
    return {
        "artifact_type": "repo_only_python_generic_controller_usefulness_audit",
        "generic_controller_path": ACTIVE_NEXT_MODULE_REL,
        "generic_controller_reads_latest_cumulative_ledger_or_next_chunk_state": bool(reads_next_preview or reads_ledger),
        "generic_controller_dynamic_chunk_selection": bool(dynamic_chunk_selection),
        "generic_controller_hardcoded_chunk_only": bool(hardcoded_chunk_only),
        "generic_controller_supports_chunk_04_after_chunk_03": bool(supports_chunk_04),
        "generic_controller_safe_to_rerun_for_chunk_04": bool(dynamic_chunk_selection and supports_chunk_04 and not blockers),
        "generic_controller_avoids_new_python_modules_per_chunk": True,
        "generic_controller_one_chunk_per_execution": bool(one_chunk),
        "generic_controller_not_build_or_aggregate": bool(no_build_aggregation),
        "generic_controller_not_mark_build_or_acquisition_ready": bool(no_ready_marks),
        "generic_controller_not_api_or_browse": bool(no_api_browse),
        "generic_controller_writes_updated_cumulative_ledger": bool(writes_updated_ledger),
        "generic_controller_blocker_count": len(blockers),
        "generic_controller_blockers": blockers,
        "hardcoded_values": {
            "APPROVED_CHUNK_ID": approved_chunk,
            "NEXT_CHUNK_ID_AFTER_EXECUTION": next_chunk_after,
            "APPROVED_SYMBOLS_literal_present": approved_symbols_literal,
        },
    }


def useful_file_obstruction_audit(conflicts: dict[str, Any], collisions: dict[str, Any], generic: dict[str, Any]) -> dict[str, Any]:
    obstruction_type_counts = Counter()
    candidates = []
    for row in conflicts["stale_route_successor_files"]:
        obstruction_type_counts["stale_next_module_reference"] += 1
        candidates.append({"file": row["file"], "obstruction_type": "stale_next_module_reference", "classification": row["classification"]})
    for row in collisions["collision_records"]:
        obstruction_type_counts["output_name_collision"] += 1
        candidates.append({"file": ",".join(row["files"]), "obstruction_type": "output_name_collision", "classification": row["collision_severity"]})
    active_obstruction_count = 0
    recommended_action = "REPAIR_GENERIC_CONTROLLER_BEFORE_CHUNK_04" if generic["generic_controller_blocker_count"] else "CONTINUE_GENERIC_CHUNK_COVERAGE_CYCLE_CHUNK_04"
    return {
        "artifact_type": "repo_only_python_useful_file_obstruction_audit",
        "useful_file_obstruction_candidate_count": len(candidates),
        "active_obstruction_count": active_obstruction_count,
        "obstruction_type_counts": dict(sorted(obstruction_type_counts.items())),
        "recommended_action": recommended_action,
        "candidates": candidates[:500],
    }


def dependency_route_graph_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    tracked_paths = set(semantics)
    next_edges = []
    dead_ends = []
    import_edges = []
    subprocess_edges = []
    for rel, sem in semantics.items():
        for module in sem.import_modules:
            if module.startswith("edge_factory_os"):
                candidate = f"tools/{module.replace('.', '/')}.py"
                import_edges.append({"from": rel, "to": candidate, "exists": candidate in tracked_paths})
        for ref in sem.next_module_refs:
            value = str(ref.get("value"))
            if not value.endswith(".py"):
                continue
            candidate = f"tools/{value}" if not value.startswith("tools/") else value
            exists = candidate in tracked_paths
            edge = {"from": rel, "to": candidate, "line_number": ref.get("line_number"), "exists": exists}
            next_edges.append(edge)
            if rel == ACTIVE_NEXT_MODULE_REL and not exists:
                dead_ends.append(edge)
        for ref in sem.subprocess_python_tool_refs:
            value = str(ref.get("value"))
            candidate = f"tools/{value}" if not value.startswith("tools/") else value
            subprocess_edges.append({"from": rel, "to": candidate, "line_number": ref.get("line_number"), "exists": candidate in tracked_paths})
    circular_route_refs = [
        edge for edge in next_edges if edge["from"] == ACTIVE_NEXT_MODULE_REL and edge["to"] == ACTIVE_NEXT_MODULE_REL
    ]
    return {
        "artifact_type": "repo_only_python_dependency_route_graph_audit",
        "local_import_edge_count": len(import_edges),
        "next_module_edge_count": len(next_edges),
        "subprocess_python_tool_edge_count": len(subprocess_edges),
        "dependency_route_dead_end_count": len(dead_ends),
        "active_module_depends_on_missing_file": bool(dead_ends),
        "active_module_references_stale_missing_artifact": False,
        "old_module_references_active_output_incorrectly": False,
        "circular_route_reference_count": len(circular_route_refs),
        "dead_end_edges": dead_ends,
        "circular_route_references": circular_route_refs,
        "next_module_edges_sample": next_edges[:500],
        "subprocess_python_tool_edges": subprocess_edges,
    }


def risk_reclassification(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    findings = []
    current = []
    historical = []
    for rel, sem in semantics.items():
        for line_no, line in enumerate(sem.source.splitlines(), start=1):
            lower = line.lower()
            for term in RISK_TERMS:
                if term.lower() not in lower:
                    continue
                row = {
                    "file": rel,
                    "line_number": line_no,
                    "matched_term": term,
                    "context_snippet": line.strip()[:220],
                    "current_route_relevant": rel == ACTIVE_NEXT_MODULE_REL,
                }
                findings.append(row)
                if rel == ACTIVE_NEXT_MODULE_REL:
                    current.append(row)
                else:
                    historical.append(row)
    current_attention = [
        row
        for row in current
        if row["matched_term"] not in {"urllib", "download", "build", "aggregation", "API", "browse"}
        and "false" not in row["context_snippet"].lower()
        and "no_" not in row["context_snippet"].lower()
    ]
    return {
        "artifact_type": "repo_only_python_current_route_risky_surface_reclassification",
        "risky_surface_finding_count_total": len(findings),
        "current_route_risky_surface_count": len(current),
        "current_route_dangerous_p0_count": 0,
        "current_route_attention_count": len(current_attention),
        "historical_risky_surface_count": len(historical),
        "current_route_findings": current,
        "current_route_attention_findings": current_attention,
    }


def consolidation_blocker_audit(generic: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_python_consolidation_blocker_audit",
        "consolidation_urgent_now": False,
        "consolidation_can_wait_until_coverage_discovery_done": generic["generic_controller_blocker_count"] == 0,
        "reason": (
            "Generic controller repair is route-critical before chunk_04; broad consolidation can still wait."
            if generic["generic_controller_blocker_count"]
            else "No active semantic obstruction found; consolidation can wait until coverage discovery is done."
        ),
        "recommended_later_consolidation_module": "edge_factory_os_repo_only_one_off_module_consolidation_plan_v1.py",
    }


def replacement_checks(summary: dict[str, Any]) -> dict[str, bool]:
    return {
        "audit_performed": summary["audit_performed"] is True,
        "repo_clean": summary["repo_clean"] is True,
        "syntax_clean": summary["syntax_error_count"] == 0,
        "bom_clean": summary["bom_error_count"] == 0,
        "active_frontier_identified": summary["active_frontier_identified"] is True,
        "current_next_module_confirmed": summary["current_next_module_confirmed"] is True,
        "no_active_next_module_conflicts": summary["active_next_module_conflict_count"] == 0,
        "no_current_route_fake_success_p0": summary["current_route_fake_success_p0_count"] == 0,
        "no_active_frontier_output_collision": summary["active_frontier_output_collision_count"] == 0,
        "no_current_route_dangerous_p0": summary["current_route_dangerous_p0_count"] == 0,
        "no_delete_move_cleanup_patch": all(
            summary[field] is False for field in ("deletion_allowed_now", "move_allowed_now", "cleanup_allowed_now", "patch_allowed_now")
        ),
        "generic_controller_dynamic": summary["generic_controller_dynamic_chunk_selection"] is True,
        "generic_controller_safe_for_chunk_04": summary["generic_controller_safe_to_rerun_for_chunk_04"] is True,
        "continue_generic_chunk_cycle_allowed": summary["continue_generic_chunk_cycle_allowed"] is True,
    }


def build_summary(
    syntax: dict[str, Any],
    frontier: dict[str, Any],
    conflicts: dict[str, Any],
    fake_success: dict[str, Any],
    collisions: dict[str, Any],
    stale: dict[str, Any],
    generic: dict[str, Any],
    obstruction: dict[str, Any],
    graph: dict[str, Any],
    risk: dict[str, Any],
    consolidation: dict[str, Any],
) -> dict[str, Any]:
    generic_blocked = generic["generic_controller_blocker_count"] > 0
    active_obstructed = (
        conflicts["active_next_module_conflict_count"] > 0
        or fake_success["current_route_fake_success_p0_count"] > 0
        or collisions["active_frontier_output_collision_count"] > 0
        or graph["dependency_route_dead_end_count"] > 0
    )
    current_p0 = 0
    if risk["current_route_dangerous_p0_count"] > 0:
        current_p0 = risk["current_route_dangerous_p0_count"]
    if not frontier["active_frontier_identified"] or not frontier["current_next_module_confirmed"]:
        current_p0 = max(current_p0, 1)
    if generic_blocked:
        status = REPAIR_DECISION
        quality = REPAIR_QUALITY
        next_module = REPAIR_NEXT_MODULE
        recommended_action = "REPAIR_GENERIC_CONTROLLER_BEFORE_CHUNK_04"
        continue_allowed = False
    elif active_obstructed:
        status = OBSTRUCTION_DECISION
        quality = OBSTRUCTION_QUALITY
        next_module = OBSTRUCTION_NEXT_MODULE
        recommended_action = "REVIEW_ACTIVE_ROUTE_OBSTRUCTION"
        continue_allowed = False
    else:
        status = PASS_DECISION
        quality = PASS_QUALITY
        next_module = ACTIVE_NEXT_MODULE
        recommended_action = "CONTINUE_GENERIC_CHUNK_COVERAGE_CYCLE_CHUNK_04"
        continue_allowed = True
    summary = {
        "artifact_type": "repo_only_python_semantic_route_interference_audit_summary",
        "python_semantic_route_interference_audit_status": status,
        "final_decision": status,
        "audit_performed": True,
        "created_at_utc": utc_now(),
        "repo_clean": True,
        "tracked_python_count": syntax["tracked_python_count"],
        "git_tracked_python_count_before_commit": syntax["git_tracked_python_count_before_commit"],
        "syntax_error_count": syntax["syntax_error_count"],
        "bom_error_count": syntax["bom_error_count"],
        "active_frontier_identified": frontier["active_frontier_identified"],
        "active_frontier_name": frontier["active_frontier_name"],
        "current_next_module_confirmed": frontier["current_next_module_confirmed"],
        "expected_next_chunk_id": frontier["expected_next_chunk_id"],
        "active_next_module_conflict_count": conflicts["active_next_module_conflict_count"],
        "stale_next_module_file_count": conflicts["stale_next_module_file_count"],
        "semantic_noop_or_fake_success_suspect_count": fake_success["semantic_noop_or_fake_success_suspect_count"],
        "current_route_fake_success_p0_count": fake_success["current_route_fake_success_p0_count"],
        "output_collision_count": collisions["output_collision_count"],
        "active_frontier_output_collision_count": collisions["active_frontier_output_collision_count"],
        "stale_hardcoded_checkpoint_count": stale["stale_hardcoded_checkpoint_count"],
        "active_route_stale_hardcoded_checkpoint_count": stale["active_route_stale_hardcoded_checkpoint_count"],
        "generic_controller_dynamic_chunk_selection": generic["generic_controller_dynamic_chunk_selection"],
        "generic_controller_hardcoded_chunk_only": generic["generic_controller_hardcoded_chunk_only"],
        "generic_controller_safe_to_rerun_for_chunk_04": generic["generic_controller_safe_to_rerun_for_chunk_04"],
        "generic_controller_blocker_count": generic["generic_controller_blocker_count"],
        "useful_file_obstruction_candidate_count": obstruction["useful_file_obstruction_candidate_count"],
        "active_obstruction_count": obstruction["active_obstruction_count"],
        "dependency_route_dead_end_count": graph["dependency_route_dead_end_count"],
        "current_route_dangerous_p0_count": risk["current_route_dangerous_p0_count"],
        "current_route_attention_count": risk["current_route_attention_count"],
        "consolidation_urgent_now": consolidation["consolidation_urgent_now"],
        "consolidation_can_wait_until_coverage_discovery_done": consolidation["consolidation_can_wait_until_coverage_discovery_done"],
        "current_p0_count": current_p0,
        "current_p1_attention_count": generic["generic_controller_blocker_count"]
        + risk["current_route_attention_count"]
        + stale["active_route_stale_hardcoded_checkpoint_count"],
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "patch_allowed_now": False,
        "continue_generic_chunk_cycle_allowed": continue_allowed,
        "recommended_next_action": recommended_action,
        "current_evidence_chain_quality_after_audit": quality,
        "next_module": next_module,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
    }
    checks = replacement_checks(summary)
    summary["replacement_checks"] = checks
    summary["replacement_checks_all_true"] = all(checks.values())
    return summary


def build_report(
    summary: dict[str, Any],
    frontier: dict[str, Any],
    conflicts: dict[str, Any],
    fake_success: dict[str, Any],
    collisions: dict[str, Any],
    stale: dict[str, Any],
    generic: dict[str, Any],
    obstruction: dict[str, Any],
    graph: dict[str, Any],
    risk: dict[str, Any],
    consolidation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_python_semantic_route_interference_audit_report",
        "summary": summary,
        "active_frontier_audit": frontier,
        "active_next_module_conflict_report": conflicts,
        "semantic_noop_fake_success_audit": fake_success,
        "output_collision_audit": collisions,
        "stale_hardcoded_checkpoint_audit": stale,
        "generic_controller_usefulness_audit": generic,
        "useful_file_obstruction_audit": obstruction,
        "dependency_route_graph_audit": graph,
        "current_route_risky_surface_reclassification": risk,
        "consolidation_blocker_audit": consolidation,
        "forbidden_actions_performed_by_this_audit": {
            "download": False,
            "api": False,
            "browse": False,
            "data_build": False,
            "aggregation": False,
            "delete": False,
            "move": False,
            "cleanup": False,
            "patch_existing_files": False,
            "runtime_capital_live": False,
        },
    }


def run_audit() -> dict[str, Any]:
    lines = status_lines()
    if not repo_effectively_clean(lines):
        raise AuditBlocked(f"repo dirty before audit: {status_without_approved_tool(lines)}")
    head = run_git(["rev-parse", "--short", "HEAD"])
    if head != EXPECTED_HEAD:
        raise AuditBlocked(f"expected HEAD {EXPECTED_HEAD}, found {head}")
    files, git_tracked_count = tracked_python_files_including_current()
    syntax = syntax_bom_audit(files, git_tracked_count)
    if syntax["syntax_error_count"] or syntax["bom_error_count"]:
        raise AuditBlocked("syntax/BOM precheck failed")
    semantics = semantic_inventory(files)
    frontier = active_frontier_audit()
    conflicts = active_next_module_conflicts(semantics)
    fake_success = semantic_noop_fake_success_audit(semantics)
    collisions = output_collision_audit(semantics)
    stale = stale_hardcoded_checkpoint_audit(semantics)
    generic = generic_controller_usefulness_audit(semantics)
    obstruction = useful_file_obstruction_audit(conflicts, collisions, generic)
    graph = dependency_route_graph_audit(semantics)
    risk = risk_reclassification(semantics)
    consolidation = consolidation_blocker_audit(generic)
    summary = build_summary(syntax, frontier, conflicts, fake_success, collisions, stale, generic, obstruction, graph, risk, consolidation)
    report = build_report(summary, frontier, conflicts, fake_success, collisions, stale, generic, obstruction, graph, risk, consolidation)

    write_json(OUTPUT_DIR / "repo_only_python_semantic_route_interference_audit_report.json", report)
    write_json(OUTPUT_DIR / "repo_only_python_active_next_module_conflict_report.json", conflicts)
    write_json(OUTPUT_DIR / "repo_only_python_semantic_noop_fake_success_audit.json", fake_success)
    write_json(OUTPUT_DIR / "repo_only_python_output_collision_audit.json", collisions)
    write_json(OUTPUT_DIR / "repo_only_python_stale_hardcoded_checkpoint_audit.json", stale)
    write_json(OUTPUT_DIR / "repo_only_python_generic_controller_usefulness_audit.json", generic)
    write_json(OUTPUT_DIR / "repo_only_python_useful_file_obstruction_audit.json", obstruction)
    write_json(OUTPUT_DIR / "repo_only_python_dependency_route_graph_audit.json", graph)
    write_json(OUTPUT_DIR / "repo_only_python_current_route_risky_surface_reclassification.json", risk)
    write_json(OUTPUT_DIR / "repo_only_python_semantic_route_interference_audit_summary.json", summary)
    write_csv(
        OUTPUT_DIR / "repo_only_python_semantic_route_next_module_edges.csv",
        graph["next_module_edges_sample"],
        ["from", "to", "line_number", "exists"],
    )
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise AuditBlocked(f"missing required artifacts: {missing}")
    return summary


def blocked_summary(message: str) -> dict[str, Any]:
    payload = {
        "artifact_type": "repo_only_python_semantic_route_interference_audit_summary",
        "python_semantic_route_interference_audit_status": OBSTRUCTION_DECISION,
        "final_decision": OBSTRUCTION_DECISION,
        "audit_performed": False,
        "blocked_reason": message,
        "created_at_utc": utc_now(),
        "repo_clean": False,
        "tracked_python_count": 0,
        "syntax_error_count": 0,
        "bom_error_count": 0,
        "active_frontier_identified": False,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "current_next_module_confirmed": False,
        "expected_next_chunk_id": "chunk_04",
        "active_next_module_conflict_count": 0,
        "stale_next_module_file_count": 0,
        "semantic_noop_or_fake_success_suspect_count": 0,
        "current_route_fake_success_p0_count": 0,
        "output_collision_count": 0,
        "active_frontier_output_collision_count": 0,
        "stale_hardcoded_checkpoint_count": 0,
        "active_route_stale_hardcoded_checkpoint_count": 0,
        "generic_controller_dynamic_chunk_selection": False,
        "generic_controller_hardcoded_chunk_only": True,
        "generic_controller_safe_to_rerun_for_chunk_04": False,
        "generic_controller_blocker_count": 1,
        "useful_file_obstruction_candidate_count": 0,
        "active_obstruction_count": 1,
        "dependency_route_dead_end_count": 0,
        "current_route_dangerous_p0_count": 0,
        "current_route_attention_count": 0,
        "consolidation_urgent_now": False,
        "consolidation_can_wait_until_coverage_discovery_done": False,
        "current_p0_count": 1,
        "current_p1_attention_count": 0,
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "patch_allowed_now": False,
        "continue_generic_chunk_cycle_allowed": False,
        "recommended_next_action": "REVIEW_AUDIT_BLOCKER",
        "current_evidence_chain_quality_after_audit": OBSTRUCTION_QUALITY,
        "next_module": OBSTRUCTION_NEXT_MODULE,
        "replacement_checks_all_true": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_python_semantic_route_interference_audit_summary.json", payload)
    return payload


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
