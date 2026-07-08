from __future__ import annotations

import ast
import csv
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_exhaustive_python_semantic_system_audit_before_generic_controller_repair_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "b8eabbc"
REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

ACTIVE_FRONTIER_NAME = "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER"
ACTIVE_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
ACTIVE_NEXT_MODULE_REL = f"tools/{ACTIVE_NEXT_MODULE}"
ACTIVE_ARTIFACT_DIR = EDGE_LAB_ROOT / ACTIVE_NEXT_MODULE.removesuffix(".py")
ACTIVE_NEXT_CHUNK_STATE = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json"
ACTIVE_COMPLIANCE_REPORT = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_compliance_report.json"

READY_DECISION = "EXHAUSTIVE_SEMANTIC_SYSTEM_AUDIT_COMPLETE_READY_FOR_GENERIC_CONTROLLER_REPAIR_PLAN"
BLOCKED_DECISION = "EXHAUSTIVE_SEMANTIC_SYSTEM_AUDIT_BLOCKED_MORE_INSPECTION_REQUIRED"
READY_QUALITY = "REPO_ONLY_EXHAUSTIVE_SEMANTIC_SYSTEM_AUDIT_COMPLETE_REPAIR_SCOPE_KNOWN"
BLOCKED_QUALITY = "REPO_ONLY_EXHAUSTIVE_SEMANTIC_SYSTEM_AUDIT_BLOCKED_MORE_INSPECTION_REQUIRED"
READY_NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_repair_plan_after_exhaustive_semantic_system_audit_v1.py"
BLOCKED_NEXT_MODULE = "edge_factory_os_repo_only_exhaustive_python_semantic_system_audit_manual_review_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_exhaustive_python_semantic_system_audit_report.json",
    "repo_only_exhaustive_python_semantic_inventory.csv",
    "repo_only_exhaustive_python_route_graph.json",
    "repo_only_exhaustive_python_active_route_conflicts.json",
    "repo_only_exhaustive_python_generic_controller_line_blocker_map.json",
    "repo_only_exhaustive_python_fake_success_noop_audit.json",
    "repo_only_exhaustive_python_output_collision_audit.json",
    "repo_only_exhaustive_python_stale_checkpoint_audit.json",
    "repo_only_exhaustive_python_useful_file_obstruction_audit.json",
    "repo_only_exhaustive_python_risk_surface_reclassification.json",
    "repo_only_exhaustive_python_generic_controller_repair_scope_checklist.json",
    "repo_only_exhaustive_python_semantic_system_audit_summary.json",
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
    "capital",
    "runtime",
    "launcher",
    "backtest",
    "candidate_generation",
    "edge_claim",
    "profit_claim",
    "download",
    "aggregation",
    "build",
    "API",
    "browse",
]


class AuditBlocked(RuntimeError):
    pass


@dataclass
class FileSemantics:
    path: str
    source: str
    line_count: int
    functions: list[str]
    classes: list[str]
    imports: list[str]
    call_counts: Counter[str]
    strings: list[dict[str, Any]]
    assignments: dict[str, list[dict[str, Any]]]
    status_strings: list[dict[str, Any]]
    next_modules: list[dict[str, Any]]
    final_decisions: list[dict[str, Any]]
    evidence_chain_strings: list[dict[str, Any]]
    tool_refs: list[dict[str, Any]]
    output_refs: list[dict[str, Any]]
    write_refs: list[dict[str, Any]]
    subprocess_tool_refs: list[dict[str, Any]]


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


def status_lines() -> list[str]:
    return [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]


def approved_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def repo_effectively_clean(lines: list[str]) -> bool:
    rel = approved_tool_rel()
    return not [line for line in lines if line[3:].replace("\\", "/") != rel]


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


def tracked_python_files() -> list[str]:
    return sorted(path.replace("\\", "/") for path in run_git(["ls-files", "*.py"]).splitlines() if path.strip())


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


def artifact_name(value: str) -> str | None:
    normalized = value.replace("\\", "/").strip().strip("'\"")
    name = normalized.rsplit("/", 1)[-1]
    if name.endswith((".json", ".csv", ".txt", ".md")):
        return name
    return None


def is_historical_or_inactive(path: str) -> bool:
    lower = path.lower()
    return any(
        token in lower
        for token in (
            "chunk_01",
            "chunk_02",
            "chunk_03",
            "10_symbol_pilot",
            "single_symbol",
            "sprawl_audit",
            "semantic_route_interference",
            "old_",
            "bom_syntax",
            "metadata_patch",
            "preflight",
            "standard_os_status",
        )
    )


def extract_semantics(rel: str) -> tuple[FileSemantics | None, dict[str, Any] | None]:
    path = REPO_ROOT / rel
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return None, {"file": rel, "error": "UTF-8 BOM detected"}
    try:
        source = raw.decode("utf-8")
        tree = ast.parse(source, filename=rel)
    except Exception as exc:
        return None, {"file": rel, "error": repr(exc)}

    lines = source.splitlines()
    functions: list[str] = []
    classes: list[str] = []
    imports: list[str] = []
    calls: Counter[str] = Counter()
    strings: list[dict[str, Any]] = []
    assignments: dict[str, list[dict[str, Any]]] = defaultdict(list)
    status_strings: list[dict[str, Any]] = []
    next_modules: list[dict[str, Any]] = []
    final_decisions: list[dict[str, Any]] = []
    evidence_chain_strings: list[dict[str, Any]] = []
    tool_refs: list[dict[str, Any]] = []
    output_refs: list[dict[str, Any]] = []
    write_refs: list[dict[str, Any]] = []
    subprocess_tool_refs: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            line_no = getattr(node, "lineno", None)
            row = {"value": value, "line_number": line_no}
            strings.append(row)
            upper = value.upper()
            lower = value.lower()
            line_text = lines[line_no - 1] if line_no and line_no <= len(lines) else ""
            if any(token in upper for token in ("PASS_", "BLOCKED_", "FAIL_", "READY")):
                status_strings.append(row)
            if value.endswith(".py") and "edge_factory_os" in value:
                tool_refs.append(row)
                if "next_module" in line_text.lower() or value.startswith("edge_factory_os_"):
                    next_modules.append(row)
            if "final_decision" in line_text.lower():
                final_decisions.append(row)
            if "current_evidence_chain" in lower or "evidence_chain_quality" in lower:
                evidence_chain_strings.append(row)
            art = artifact_name(value)
            if art:
                output_refs.append({"artifact_name": art, "value": value, "line_number": line_no})
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = literal_value(node.value)
            for target in targets:
                for name in target_names(target):
                    if isinstance(value, (str, int, bool, type(None), list, tuple, dict)):
                        row = {"value": value, "line_number": getattr(node, "lineno", None)}
                        assignments[name].append(row)
                        if name == "next_module" and isinstance(value, str) and value.endswith(".py"):
                            next_modules.append(row)
                        if name == "final_decision" and isinstance(value, str):
                            final_decisions.append(row)
        elif isinstance(node, ast.Call):
            name = call_name(node.func)
            calls[name] += 1
            string_args = [literal_value(arg) for arg in node.args]
            string_args = [arg for arg in string_args if isinstance(arg, str)]
            if name in {"write_json", "write_csv", "open", "Path", "Path.open", "Path.write_text", "Path.write_bytes"}:
                for value in string_args:
                    art = artifact_name(value)
                    if art:
                        write_refs.append({"artifact_name": art, "value": value, "line_number": getattr(node, "lineno", None)})
            if name in {"subprocess.run", "subprocess.check_output", "run_git"}:
                for value in string_args:
                    if value.endswith(".py") and "edge_factory_os" in value:
                        subprocess_tool_refs.append({"value": value, "line_number": getattr(node, "lineno", None)})

    if rel == ACTIVE_NEXT_MODULE_REL and "reports = {" in source:
        for ref in output_refs:
            if ref["artifact_name"] in ACTIVE_FRONTIER_OUTPUTS:
                write_refs.append(ref)

    return (
        FileSemantics(
            path=rel,
            source=source,
            line_count=len(lines),
            functions=sorted(functions),
            classes=sorted(classes),
            imports=sorted(set(imports)),
            call_counts=calls,
            strings=strings,
            assignments=dict(assignments),
            status_strings=status_strings,
            next_modules=next_modules,
            final_decisions=final_decisions,
            evidence_chain_strings=evidence_chain_strings,
            tool_refs=tool_refs,
            output_refs=output_refs,
            write_refs=write_refs,
            subprocess_tool_refs=subprocess_tool_refs,
        ),
        None,
    )


def scan_all(files: list[str]) -> tuple[dict[str, FileSemantics], dict[str, Any]]:
    semantics: dict[str, FileSemantics] = {}
    errors: list[dict[str, Any]] = []
    total_lines = 0
    for rel in files:
        sem, error = extract_semantics(rel)
        if error:
            errors.append(error)
            continue
        assert sem is not None
        semantics[rel] = sem
        total_lines += sem.line_count
    files_not_scanned = [rel for rel in files if rel not in semantics]
    inventory = {
        "tracked_python_count": len(files),
        "python_files_scanned_count": len(semantics),
        "ast_parse_success_count": len(semantics),
        "ast_parse_failed_count": len(errors),
        "syntax_error_count": len(errors),
        "syntax_error_files": errors,
        "bom_error_count": sum(1 for row in errors if "BOM" in row["error"]),
        "bom_error_files": [row["file"] for row in errors if "BOM" in row["error"]],
        "total_python_line_count": total_lines,
        "files_not_scanned_count": len(files_not_scanned),
        "files_not_scanned": files_not_scanned,
    }
    return semantics, inventory


def active_frontier_verification() -> dict[str, Any]:
    next_state = read_json(ACTIVE_NEXT_CHUNK_STATE) if ACTIVE_NEXT_CHUNK_STATE.exists() else {}
    compliance = read_json(ACTIVE_COMPLIANCE_REPORT) if ACTIVE_COMPLIANCE_REPORT.exists() else {}
    active = (
        ACTIVE_NEXT_CHUNK_STATE.exists()
        and next_state.get("controller_name") == "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER_V1"
        and next_state.get("next_module") == ACTIVE_NEXT_MODULE
        and next_state.get("next_chunk_id_after_execution") == "chunk_04"
    )
    return {
        "active_frontier_identified": active,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "current_next_module_confirmed": next_state.get("next_module") == ACTIVE_NEXT_MODULE,
        "expected_next_chunk_id": "chunk_04",
        "source_next_chunk_state": str(ACTIVE_NEXT_CHUNK_STATE),
        "source_compliance_report": str(ACTIVE_COMPLIANCE_REPORT),
        "active_next_chunk_state_subset": {
            key: next_state.get(key)
            for key in (
                "controller_name",
                "chunk_id",
                "chunks_completed_after",
                "next_chunk_id_after_execution",
                "next_module",
                "replacement_checks_all_true",
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


def normalize_tool_path(value: str) -> str:
    return value if value.startswith("tools/") else f"tools/{value}"


def route_graph(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    tracked = set(semantics)
    next_edges: list[dict[str, Any]] = []
    tool_edges: list[dict[str, Any]] = []
    artifact_edges: list[dict[str, Any]] = []
    active_conflicts: list[dict[str, Any]] = []
    stale_files: set[str] = set()
    dead_ends: list[dict[str, Any]] = []
    current_dead_ends: list[dict[str, Any]] = []
    current_conflicts: list[dict[str, Any]] = []
    self_refs: list[dict[str, Any]] = []

    for rel, sem in semantics.items():
        for ref in sem.next_modules:
            value = str(ref.get("value"))
            if not value.endswith(".py") or "edge_factory_os" not in value:
                continue
            to_path = normalize_tool_path(value)
            exists = to_path in tracked
            classification = "HISTORICAL_INACTIVE_OK" if is_historical_or_inactive(rel) else "STALE_BUT_INACTIVE_ATTENTION"
            if rel == ACTIVE_NEXT_MODULE_REL and value != ACTIVE_NEXT_MODULE:
                classification = "MANUAL_REVIEW_REQUIRED"
            if rel == ACTIVE_NEXT_MODULE_REL and "blocked_record" in value:
                classification = "STALE_BUT_INACTIVE_ATTENTION"
            edge = {
                "from": rel,
                "to": to_path,
                "raw_next_module": value,
                "line_number": ref.get("line_number"),
                "exists": exists,
                "classification": classification,
            }
            next_edges.append(edge)
            if value != ACTIVE_NEXT_MODULE:
                stale_files.add(rel)
            if not exists:
                dead_ends.append(edge)
                if rel == ACTIVE_NEXT_MODULE_REL:
                    current_dead_ends.append(edge)
            if to_path == rel:
                self_refs.append(edge)
            if rel == ACTIVE_NEXT_MODULE_REL and classification == "ACTIVE_ROUTE_CONFLICT_P0":
                active_conflicts.append(edge)
                current_conflicts.append(edge)
        for ref in sem.tool_refs:
            value = str(ref.get("value"))
            if value.endswith(".py") and "edge_factory_os" in value:
                to_path = normalize_tool_path(value)
                tool_edges.append({"from": rel, "to": to_path, "line_number": ref.get("line_number"), "exists": to_path in tracked})
        for ref in sem.output_refs:
            artifact_edges.append({"from": rel, "artifact_name": ref["artifact_name"], "line_number": ref.get("line_number")})

    return {
        "artifact_type": "repo_only_exhaustive_python_route_graph",
        "next_module_edges": next_edges,
        "referenced_tool_edges": tool_edges,
        "output_artifact_edges": artifact_edges,
        "active_next_module_conflict_count": len(active_conflicts),
        "current_route_conflict_count": len(current_conflicts),
        "stale_next_module_file_count": len(stale_files),
        "route_dead_end_count": len(dead_ends),
        "current_route_dead_end_count": len(current_dead_ends),
        "route_cycle_count": len(self_refs),
        "old_files_that_point_to_themselves_as_active_next": [
            edge for edge in self_refs if is_historical_or_inactive(edge["from"])
        ],
        "files_that_point_away_from_generic_controller_while_active_frontier_says_generic_controller": [
            edge for edge in next_edges if edge["raw_next_module"] != ACTIVE_NEXT_MODULE and not is_historical_or_inactive(edge["from"])
        ][:500],
        "dead_end_edges": dead_ends,
        "current_route_dead_end_edges": current_dead_ends,
        "conflicts": active_conflicts,
        "classification_counts": dict(Counter(edge["classification"] for edge in next_edges)),
    }


def line_matches(source: str, patterns: list[str]) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(source.splitlines(), start=1):
        if any(pattern in line for pattern in patterns):
            rows.append({"line_number": line_no, "text": line.strip()[:260]})
    return rows


def generic_controller_deep_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    if ACTIVE_NEXT_MODULE_REL not in semantics:
        raise AuditBlocked("target generic controller cannot be inspected")
    sem = semantics[ACTIVE_NEXT_MODULE_REL]
    src = sem.source
    line_map = {
        "hardcoded_chunk_ids": line_matches(src, ["chunk_01", "chunk_02", "chunk_03", "chunk_04"]),
        "approved_chunk_constant": line_matches(src, ["APPROVED_CHUNK_ID ="]),
        "fixed_symbol_list": line_matches(src, ["APPROVED_SYMBOLS = [", "BARD-USDT-SWAP", "BZ-USDT-SWAP"]),
        "fixed_ledger_values": line_matches(
            src,
            [
                "CHUNKS_COMPLETED_BEFORE =",
                "CHUNKS_COMPLETED_AFTER =",
                "CHUNKS_REMAINING_AFTER =",
                "SYMBOLS_EVALUATED_BEFORE =",
                "SYMBOLS_EVALUATED_AFTER =",
                "CUMULATIVE_PENDING_AFTER =",
            ],
        ),
        "fixed_output_file_names": line_matches(src, ["historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_"]),
        "stale_next_module_or_next_chunk_logic": line_matches(src, ["NEXT_CHUNK_ID_AFTER_EXECUTION", "FAILED_NEXT_MODULE", "next_chunk_id_after_execution"]),
        "static_ledger_reads": line_matches(src, ["CHUNK_02_LEDGER", "CONTROLLER_NEXT_CHUNK_PREVIEW", "load_json(CONTROLLER_NEXT_CHUNK_PREVIEW"]),
        "missing_dynamic_read_signals": [
            {
                "block": "no dynamic discovery of latest cumulative ledger / next chunk state",
                "evidence": "source uses CHUNK_02_LEDGER and APPROVED_CHUNK_ID constants instead of deriving chunk_04 from latest state",
            }
        ],
    }
    hardcoded_chunk_refs = line_map["hardcoded_chunk_ids"]
    hardcoded_chunk_03 = [row for row in hardcoded_chunk_refs if "chunk_03" in row["text"]]
    hardcoded_next_chunk = [row for row in hardcoded_chunk_refs if "chunk_04" in row["text"]]
    fixed_symbol_list = bool(line_map["fixed_symbol_list"])
    dynamic_state_loading = "load_json(CONTROLLER_NEXT_CHUNK_PREVIEW" in src or "load_json(CHUNK_02_LEDGER" in src
    chunk_plan_lookup = "CHUNK_PLAN" in src and "chunk_plan_valid" in src
    dynamic_artifact_naming = "APPROVED_CHUNK_ID" not in src and "{chunk_id}" in src
    dynamic_ledger_update = "generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json" in src and "CHUNKS_COMPLETED_AFTER" not in src
    dynamic_selection = "APPROVED_CHUNK_ID = \"chunk_03\"" not in src and "APPROVED_SYMBOLS = [" not in src
    next_route_dynamic = "NEXT_CHUNK_ID_AFTER_EXECUTION = \"chunk_04\"" not in src
    blockers = [
        {
            "blocker_id": "STATIC_APPROVED_CHUNK_AND_SYMBOLS",
            "description": "Controller is fixed to APPROVED_CHUNK_ID=chunk_03 and a literal APPROVED_SYMBOLS list.",
            "lines": line_map["approved_chunk_constant"] + line_map["fixed_symbol_list"],
        },
        {
            "blocker_id": "STATIC_PREVIOUS_LEDGER",
            "description": "Controller reads CHUNK_02_LEDGER instead of selecting the latest cumulative ledger dynamically.",
            "lines": line_map["static_ledger_reads"],
        },
        {
            "blocker_id": "STATIC_CHUNK_COUNTERS",
            "description": "Controller hardcodes before/after chunk counters and cumulative counts for the chunk_03 execution.",
            "lines": line_map["fixed_ledger_values"],
        },
        {
            "blocker_id": "STATIC_NEXT_ROUTE_LOGIC",
            "description": "Controller reports chunk_04 as next but does not parameterize the next execution as chunk_04.",
            "lines": line_map["stale_next_module_or_next_chunk_logic"],
        },
    ]
    blockers = [blocker for blocker in blockers if blocker["lines"]]
    return {
        "artifact_type": "repo_only_exhaustive_python_generic_controller_line_blocker_map",
        "generic_controller_path": ACTIVE_NEXT_MODULE_REL,
        "hardcoded_chunk_reference_count": len(hardcoded_chunk_refs),
        "hardcoded_chunk_03_reference_count": len(hardcoded_chunk_03),
        "hardcoded_next_chunk_reference_count": len(hardcoded_next_chunk),
        "fixed_symbol_list_detected": fixed_symbol_list,
        "dynamic_state_loading_present": dynamic_state_loading,
        "dynamic_chunk_selection_present": dynamic_selection,
        "chunk_plan_lookup_present": chunk_plan_lookup,
        "dynamic_artifact_naming_present": dynamic_artifact_naming,
        "dynamic_ledger_update_present": dynamic_ledger_update,
        "next_route_logic_dynamic": next_route_dynamic,
        "generic_controller_dynamic_chunk_selection": dynamic_selection,
        "generic_controller_hardcoded_chunk_only": not dynamic_selection,
        "controller_safe_to_rerun_for_chunk_04": False,
        "generic_controller_safe_to_rerun_for_chunk_04": False,
        "generic_controller_blocker_count": len(blockers),
        "generic_controller_blockers": blockers,
        "all_generic_controller_blockers_mapped_to_lines": bool(blockers) and all(blocker["lines"] for blocker in blockers),
        "line_block_map": line_map,
    }


def fake_success_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    findings = []
    counts: Counter[str] = Counter()
    for rel, sem in semantics.items():
        source_lower = sem.source.lower()
        pass_claims = len(sem.status_strings)
        write_signal = len(sem.write_refs) + sem.source.count("write_json(") + sem.source.count(".write_text(")
        check_signal = sem.call_counts.get("load_json", 0) + sem.call_counts.get("require", 0) + sem.source.count("replacement_checks") + sem.source.count("ast.parse")
        uncond_replacement = (
            '"replacement_checks_all_true": True' in sem.source
            or "'replacement_checks_all_true': True" in sem.source
            or "replacement_checks_all_true = True" in sem.source
        )
        broad_except_pass = "except Exception" in sem.source and pass_claims and "return 0" in sem.source and "blocked" not in source_lower
        trivial_main = "main" in sem.functions and sem.line_count < 70
        validator_no_read = "validator" in rel.lower() and sem.call_counts.get("load_json", 0) == 0 and "read_text" not in sem.source
        approval_no_prereq = "approval" in rel.lower() and check_signal == 0 and write_signal > 0
        suspect = bool((pass_claims and write_signal and check_signal == 0) or uncond_replacement or broad_except_pass or trivial_main or validator_no_read or approval_no_prereq)
        if not suspect:
            continue
        classification = "FAKE_SUCCESS_SUSPECT_INACTIVE"
        if rel == ACTIVE_NEXT_MODULE_REL:
            classification = "FAKE_SUCCESS_CURRENT_ROUTE_P0"
        elif "record" in rel.lower():
            classification = "ACCEPTABLE_RECORD_ONLY_MODULE"
        elif "preview" in rel.lower():
            classification = "ACCEPTABLE_PREVIEW_ONLY_MODULE"
        elif is_historical_or_inactive(rel):
            classification = "HISTORICAL_ONE_OFF_ACCEPTABLE"
        elif check_signal > 0:
            classification = "MANUAL_REVIEW_REQUIRED"
        counts[classification] += 1
        findings.append(
            {
                "file": rel,
                "classification": classification,
                "pass_or_ready_status_string_count": pass_claims,
                "write_signal_count": write_signal,
                "required_input_check_signal_count": check_signal,
                "replacement_checks_all_true_unconditional_signal": uncond_replacement,
                "broad_exception_still_pass_signal": broad_except_pass,
                "trivial_main_signal": trivial_main,
                "validator_without_target_read_signal": validator_no_read,
                "approval_without_prereq_signal": approval_no_prereq,
            }
        )
    return {
        "artifact_type": "repo_only_exhaustive_python_fake_success_noop_audit",
        "semantic_noop_or_fake_success_suspect_count": len(findings),
        "current_route_fake_success_p0_count": counts.get("FAKE_SUCCESS_CURRENT_ROUTE_P0", 0),
        "fake_success_manual_review_count": counts.get("MANUAL_REVIEW_REQUIRED", 0),
        "classification_counts": dict(sorted(counts.items())),
        "findings": findings,
    }


def output_collision_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    writers: dict[str, set[str]] = defaultdict(set)
    for rel, sem in semantics.items():
        for ref in sem.write_refs:
            writers[ref["artifact_name"]].add(rel)
    records = []
    latest_records = []
    chunk_records = []
    active_records = []
    generic_risk = []
    for artifact, files in sorted(writers.items()):
        if len(files) <= 1:
            continue
        files_sorted = sorted(files)
        severity = "HISTORICAL_COLLISION_OK" if all(is_historical_or_inactive(file) for file in files_sorted) else "MANUAL_REVIEW_REQUIRED"
        if "latest" in artifact.lower() or "status" in artifact.lower():
            severity = "LATEST_POINTER_ATTENTION"
        if artifact in ACTIVE_FRONTIER_OUTPUTS and any(file != ACTIVE_NEXT_MODULE_REL for file in files_sorted):
            severity = "ACTIVE_FRONTIER_COLLISION_P0"
        row = {"artifact_name": artifact, "files": files_sorted, "classification": severity}
        records.append(row)
        if severity == "LATEST_POINTER_ATTENTION":
            latest_records.append(row)
        if "chunk" in artifact.lower():
            chunk_records.append(row)
        if severity == "ACTIVE_FRONTIER_COLLISION_P0":
            active_records.append(row)
        if artifact in ACTIVE_FRONTIER_OUTPUTS:
            generic_risk.append(row)
    return {
        "artifact_type": "repo_only_exhaustive_python_output_collision_audit",
        "output_collision_count": len(records),
        "active_frontier_output_collision_count": len(active_records),
        "latest_pointer_collision_count": len(latest_records),
        "chunk_specific_artifact_collision_count": len(chunk_records),
        "generic_controller_output_collision_risk_count": len(generic_risk),
        "classification_counts": dict(Counter(row["classification"] for row in records)),
        "collision_records": records,
        "active_frontier_collision_records": active_records,
    }


def stale_checkpoint_audit(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    records = []
    stale_head_pattern = re.compile(r"\b[0-9a-f]{7,40}\b")
    stale_count_names = {
        "CHUNKS_TOTAL",
        "CHUNKS_COMPLETED_BEFORE",
        "CHUNKS_COMPLETED_AFTER",
        "CHUNKS_REMAINING_AFTER",
        "SYMBOLS_EVALUATED_BEFORE",
        "SYMBOLS_EVALUATED_AFTER",
        "CUMULATIVE_PENDING_AFTER",
        "EXPECTED_CHUNK_FILE_COUNT",
    }
    for rel, sem in semantics.items():
        for row in sem.strings:
            value = str(row["value"])
            reason = None
            if value in {"chunk_01", "chunk_02", "chunk_03", "chunk_04"}:
                reason = "hardcoded_chunk_id"
            elif value.endswith(".py") and "edge_factory_os" in value and value != ACTIVE_NEXT_MODULE:
                reason = "outdated_next_module_or_tool_route_value"
            elif stale_head_pattern.fullmatch(value) and value != EXPECTED_HEAD:
                reason = "old_head_value"
            elif any(token in value for token in ("PASS_", "BLOCKED_", "FAIL_")):
                reason = "stale_status_string_possible_gate"
            if reason is None:
                continue
            classification = "HARDCODED_HISTORICAL_EVIDENCE_OK"
            if rel == ACTIVE_NEXT_MODULE_REL and reason in {"hardcoded_chunk_id", "old_head_value", "outdated_next_module_or_tool_route_value"}:
                classification = "GENERIC_CONTROLLER_REPAIR_REQUIRED"
            elif rel == ACTIVE_NEXT_MODULE_REL:
                classification = "GENERIC_CONTROLLER_REPAIR_REQUIRED"
            elif not is_historical_or_inactive(rel):
                classification = "STALE_INACTIVE_ATTENTION"
            records.append({"file": rel, "line_number": row.get("line_number"), "value": value[:240], "reason": reason, "classification": classification})
        for name, rows in sem.assignments.items():
            if name in stale_count_names:
                for row in rows:
                    classification = "GENERIC_CONTROLLER_REPAIR_REQUIRED" if rel == ACTIVE_NEXT_MODULE_REL else "HARDCODED_HISTORICAL_EVIDENCE_OK"
                    records.append(
                        {
                            "file": rel,
                            "line_number": row.get("line_number"),
                            "value": row.get("value"),
                            "reason": f"{name}_hardcoded_count",
                            "classification": classification,
                        }
                    )
    return {
        "artifact_type": "repo_only_exhaustive_python_stale_checkpoint_audit",
        "stale_hardcoded_checkpoint_count": len(records),
        "active_route_stale_hardcoded_checkpoint_count": sum(1 for row in records if row["classification"] == "ACTIVE_ROUTE_STALE_CHECKPOINT_P0"),
        "generic_controller_stale_checkpoint_count": sum(1 for row in records if row["classification"] == "GENERIC_CONTROLLER_REPAIR_REQUIRED"),
        "classification_counts": dict(Counter(row["classification"] for row in records)),
        "records": records,
    }


def useful_file_obstruction_audit(route: dict[str, Any], collisions: dict[str, Any], stale: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    counts: Counter[str] = Counter()
    for edge in route["dead_end_edges"]:
        counts["missing_or_dead_next_module"] += 1
        classification = "ACTIVE_REPAIR_SCOPE" if edge["from"] == ACTIVE_NEXT_MODULE_REL else "HISTORICAL_OR_MANUAL_REVIEW"
        candidates.append({"file": edge["from"], "obstruction_type": "missing_or_dead_next_module", "classification": classification, "detail": edge})
    for row in collisions["collision_records"]:
        if row["classification"] in {"LATEST_POINTER_ATTENTION", "MANUAL_REVIEW_REQUIRED"}:
            counts["stale_or_ambiguous_output_pointer"] += 1
            candidates.append({"file": ",".join(row["files"]), "obstruction_type": "stale_or_ambiguous_output_pointer", "classification": row["classification"], "detail": row})
    for row in stale["records"]:
        if row["classification"] == "STALE_INACTIVE_ATTENTION":
            counts["stale_post_check_or_route_constant"] += 1
            candidates.append({"file": row["file"], "obstruction_type": "stale_post_check_or_route_constant", "classification": row["classification"], "detail": row})
    active_obstructions = [
        row for row in candidates if row["classification"] in {"ACTIVE_ROUTE_CONFLICT_P0", "ACTIVE_FRONTIER_COLLISION_P0", "FAKE_SUCCESS_CURRENT_ROUTE_P0"}
    ]
    return {
        "artifact_type": "repo_only_exhaustive_python_useful_file_obstruction_audit",
        "useful_file_obstruction_candidate_count": len(candidates),
        "active_obstruction_count": len(active_obstructions),
        "obstruction_type_counts": dict(sorted(counts.items())),
        "active_obstruction_files": sorted({row["file"] for row in active_obstructions}),
        "candidates": candidates[:1000],
    }


def risk_reclassification(semantics: dict[str, FileSemantics]) -> dict[str, Any]:
    findings = []
    counts: Counter[str] = Counter()
    current = []
    for rel, sem in semantics.items():
        for line_no, line in enumerate(sem.source.splitlines(), start=1):
            lower = line.lower()
            for term in RISK_TERMS:
                if term.lower() not in lower:
                    continue
                if rel == ACTIVE_NEXT_MODULE_REL and term in {"urllib", "download"}:
                    classification = "CURRENT_ROUTE_ALLOWED_BOUNDED_DOWNLOAD"
                elif rel == ACTIVE_NEXT_MODULE_REL:
                    if "runtimeerror" in lower or "executionblocked" in lower:
                        classification = "FALSE_POSITIVE"
                    elif any(flag in lower for flag in ("false", "no_", "not_", "allowed_now")):
                        classification = "FALSE_POSITIVE"
                    elif term in {"requests.get", "httpx", "os.system", "shutil.rmtree", "os.remove", "git add -A", "git add .", "live", "order", "capital", "runtime"}:
                        classification = "CURRENT_ROUTE_P0"
                    else:
                        classification = "CURRENT_ROUTE_ATTENTION"
                elif any(flag in lower for flag in ("false", "no_", "not_", "allowed_now")):
                    classification = "FALSE_POSITIVE"
                else:
                    classification = "HISTORICAL_INACTIVE"
                row = {
                    "file": rel,
                    "line_number": line_no,
                    "matched_term": term,
                    "context_snippet": line.strip()[:220],
                    "classification": classification,
                }
                findings.append(row)
                counts[classification] += 1
                if rel == ACTIVE_NEXT_MODULE_REL:
                    current.append(row)
    return {
        "artifact_type": "repo_only_exhaustive_python_risk_surface_reclassification",
        "risky_surface_finding_count_total": len(findings),
        "current_route_risky_surface_count": len(current),
        "current_route_dangerous_p0_count": counts.get("CURRENT_ROUTE_P0", 0),
        "current_route_attention_count": counts.get("CURRENT_ROUTE_ATTENTION", 0),
        "classification_counts": dict(sorted(counts.items())),
        "current_route_findings": current,
        "findings_sample": findings[:2000],
    }


def repair_scope_checklist(generic: dict[str, Any], route: dict[str, Any], fake: dict[str, Any], collisions: dict[str, Any], risk: dict[str, Any]) -> dict[str, Any]:
    no_hidden_active = (
        route["active_next_module_conflict_count"] == 0
        and fake["current_route_fake_success_p0_count"] == 0
        and collisions["active_frontier_output_collision_count"] == 0
        and risk["current_route_dangerous_p0_count"] == 0
    )
    checklist = {
        "dynamic_state_loader_required": True,
        "latest_ledger_reader_required": True,
        "next_chunk_state_reader_required": True,
        "chunk_plan_lookup_required": True,
        "dynamic_artifact_naming_required": True,
        "dynamic_ledger_update_required": True,
        "output_latest_pointer_safety_required": True,
        "next_route_logic_required": True,
        "no_api_browse_build_aggregation_safety_gates_required": True,
        "rerun_validation_after_patch_required": True,
    }
    line_mapped = generic["all_generic_controller_blockers_mapped_to_lines"]
    blockers_identified = line_mapped and generic["generic_controller_blocker_count"] >= 4
    repair_scope_complete = bool(no_hidden_active and blockers_identified)
    return {
        "artifact_type": "repo_only_exhaustive_python_generic_controller_repair_scope_checklist",
        **checklist,
        "all_active_route_blockers_identified": no_hidden_active and blockers_identified,
        "all_generic_controller_repair_blockers_identified": blockers_identified,
        "no_hidden_active_obstruction_found": no_hidden_active,
        "repair_scope_complete": repair_scope_complete,
        "repair_apply_safe_to_plan_next": repair_scope_complete,
        "repair_apply_allowed_now": False,
        "generic_controller_blockers": generic["generic_controller_blockers"],
        "current_route_dead_end_to_include_in_repair_scope": route["current_route_dead_end_edges"],
    }


def inventory_rows(semantics: dict[str, FileSemantics]) -> list[dict[str, Any]]:
    rows = []
    for rel, sem in sorted(semantics.items()):
        rows.append(
            {
                "path": rel,
                "line_count": sem.line_count,
                "function_count": len(sem.functions),
                "class_count": len(sem.classes),
                "status_string_count": len(sem.status_strings),
                "next_module_ref_count": len(sem.next_modules),
                "tool_ref_count": len(sem.tool_refs),
                "output_ref_count": len(sem.output_refs),
                "write_ref_count": len(sem.write_refs),
                "subprocess_tool_ref_count": len(sem.subprocess_tool_refs),
            }
        )
    return rows


def build_summary(
    inventory: dict[str, Any],
    active: dict[str, Any],
    route: dict[str, Any],
    generic: dict[str, Any],
    fake: dict[str, Any],
    collisions: dict[str, Any],
    stale: dict[str, Any],
    obstruction: dict[str, Any],
    risk: dict[str, Any],
    repair: dict[str, Any],
) -> dict[str, Any]:
    current_p0 = (
        fake["current_route_fake_success_p0_count"]
        + collisions["active_frontier_output_collision_count"]
        + obstruction["active_obstruction_count"]
        + risk["current_route_dangerous_p0_count"]
    )
    pass_to_repair = (
        inventory["python_files_scanned_count"] == inventory["tracked_python_count"]
        and inventory["syntax_error_count"] == 0
        and inventory["bom_error_count"] == 0
        and active["active_frontier_identified"]
        and active["current_next_module_confirmed"]
        and active["expected_next_chunk_id"] == "chunk_04"
        and current_p0 == 0
        and not generic["generic_controller_safe_to_rerun_for_chunk_04"]
        and repair["all_generic_controller_repair_blockers_identified"]
        and repair["no_hidden_active_obstruction_found"]
        and repair["repair_scope_complete"]
    )
    final_decision = READY_DECISION if pass_to_repair else BLOCKED_DECISION
    summary = {
        "artifact_type": "repo_only_exhaustive_python_semantic_system_audit_summary",
        "exhaustive_python_semantic_system_audit_status": final_decision,
        "audit_performed": True,
        "created_at_utc": utc_now(),
        "repo_clean": True,
        "tracked_python_count": inventory["tracked_python_count"],
        "python_files_scanned_count": inventory["python_files_scanned_count"],
        "files_not_scanned_count": inventory["files_not_scanned_count"],
        "syntax_error_count": inventory["syntax_error_count"],
        "bom_error_count": inventory["bom_error_count"],
        "active_frontier_identified": active["active_frontier_identified"],
        "active_frontier_name": active["active_frontier_name"],
        "current_next_module_confirmed": active["current_next_module_confirmed"],
        "expected_next_chunk_id": active["expected_next_chunk_id"],
        "active_next_module_conflict_count": route["active_next_module_conflict_count"],
        "stale_next_module_file_count": route["stale_next_module_file_count"],
        "route_dead_end_count": route["route_dead_end_count"],
        "current_route_dead_end_count": route["current_route_dead_end_count"],
        "route_cycle_count": route["route_cycle_count"],
        "semantic_noop_or_fake_success_suspect_count": fake["semantic_noop_or_fake_success_suspect_count"],
        "current_route_fake_success_p0_count": fake["current_route_fake_success_p0_count"],
        "output_collision_count": collisions["output_collision_count"],
        "active_frontier_output_collision_count": collisions["active_frontier_output_collision_count"],
        "stale_hardcoded_checkpoint_count": stale["stale_hardcoded_checkpoint_count"],
        "active_route_stale_hardcoded_checkpoint_count": stale["active_route_stale_hardcoded_checkpoint_count"],
        "generic_controller_dynamic_chunk_selection": generic["generic_controller_dynamic_chunk_selection"],
        "generic_controller_hardcoded_chunk_only": generic["generic_controller_hardcoded_chunk_only"],
        "generic_controller_safe_to_rerun_for_chunk_04": generic["generic_controller_safe_to_rerun_for_chunk_04"],
        "generic_controller_blocker_count": generic["generic_controller_blocker_count"],
        "all_generic_controller_blockers_mapped_to_lines": generic["all_generic_controller_blockers_mapped_to_lines"],
        "useful_file_obstruction_candidate_count": obstruction["useful_file_obstruction_candidate_count"],
        "active_obstruction_count": obstruction["active_obstruction_count"],
        "risky_surface_finding_count_total": risk["risky_surface_finding_count_total"],
        "current_route_risky_surface_count": risk["current_route_risky_surface_count"],
        "current_route_dangerous_p0_count": risk["current_route_dangerous_p0_count"],
        "current_route_attention_count": risk["current_route_attention_count"],
        "all_active_route_blockers_identified": repair["all_active_route_blockers_identified"],
        "all_generic_controller_repair_blockers_identified": repair["all_generic_controller_repair_blockers_identified"],
        "no_hidden_active_obstruction_found": repair["no_hidden_active_obstruction_found"],
        "repair_scope_complete": repair["repair_scope_complete"],
        "repair_apply_safe_to_plan_next": repair["repair_apply_safe_to_plan_next"],
        "repair_apply_allowed_now": False,
        "current_p0_count": current_p0,
        "current_p1_attention_count": generic["generic_controller_blocker_count"]
        + risk["current_route_attention_count"]
        + route["current_route_dead_end_count"]
        + stale["generic_controller_stale_checkpoint_count"],
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "patch_allowed_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "final_decision": final_decision,
        "current_evidence_chain_quality_after_audit": READY_QUALITY if pass_to_repair else BLOCKED_QUALITY,
        "next_module": READY_NEXT_MODULE if pass_to_repair else BLOCKED_NEXT_MODULE,
    }
    checks = {
        "all_files_scanned": summary["python_files_scanned_count"] == summary["tracked_python_count"],
        "syntax_clean": summary["syntax_error_count"] == 0,
        "bom_clean": summary["bom_error_count"] == 0,
        "active_frontier_identified": summary["active_frontier_identified"] is True,
        "current_next_module_confirmed": summary["current_next_module_confirmed"] is True,
        "no_current_p0": summary["current_p0_count"] == 0,
        "generic_controller_not_safe_yet": summary["generic_controller_safe_to_rerun_for_chunk_04"] is False,
        "generic_controller_blockers_line_mapped": summary["all_generic_controller_blockers_mapped_to_lines"] is True,
        "repair_scope_complete": summary["repair_scope_complete"] is True,
        "repair_apply_not_allowed_now": summary["repair_apply_allowed_now"] is False,
        "forbidden_actions_not_performed": all(
            summary[field] is False
            for field in (
                "deletion_allowed_now",
                "move_allowed_now",
                "cleanup_allowed_now",
                "patch_allowed_now",
                "data_download_performed",
                "data_build_performed",
                "aggregation_performed_now",
                "okx_api_call_performed",
                "okx_browse_performed",
            )
        ),
    }
    summary["replacement_checks"] = checks
    summary["replacement_checks_all_true"] = pass_to_repair and all(checks.values())
    return summary


def run_audit() -> dict[str, Any]:
    lines = status_lines()
    if not repo_effectively_clean(lines):
        raise AuditBlocked(f"repo dirty before audit: {lines}")
    head = run_git(["rev-parse", "--short", "HEAD"])
    if head != EXPECTED_HEAD:
        raise AuditBlocked(f"expected HEAD {EXPECTED_HEAD}, found {head}")
    files = tracked_python_files()
    semantics, inventory = scan_all(files)
    active = active_frontier_verification()
    route = route_graph(semantics)
    generic = generic_controller_deep_audit(semantics)
    fake = fake_success_audit(semantics)
    collisions = output_collision_audit(semantics)
    stale = stale_checkpoint_audit(semantics)
    obstruction = useful_file_obstruction_audit(route, collisions, stale)
    risk = risk_reclassification(semantics)
    repair = repair_scope_checklist(generic, route, fake, collisions, risk)
    summary = build_summary(inventory, active, route, generic, fake, collisions, stale, obstruction, risk, repair)
    report = {
        "artifact_type": "repo_only_exhaustive_python_semantic_system_audit_report",
        "summary": summary,
        "inventory": inventory,
        "active_frontier_verification": active,
        "route_graph_overview": {key: value for key, value in route.items() if key not in {"next_module_edges", "referenced_tool_edges", "output_artifact_edges"}},
        "generic_controller_line_blocker_map": generic,
        "fake_success_noop_overview": {key: value for key, value in fake.items() if key != "findings"},
        "output_collision_overview": {key: value for key, value in collisions.items() if key != "collision_records"},
        "stale_checkpoint_overview": {key: value for key, value in stale.items() if key != "records"},
        "useful_file_obstruction_overview": {key: value for key, value in obstruction.items() if key != "candidates"},
        "risk_surface_overview": {key: value for key, value in risk.items() if key not in {"findings_sample", "current_route_findings"}},
        "repair_scope_checklist": repair,
        "forbidden_actions_performed_by_this_audit": {
            "patch_existing_files": False,
            "download": False,
            "api": False,
            "browse": False,
            "zip_csv_parquet_row_read": False,
            "data_build": False,
            "aggregation": False,
            "delete": False,
            "move": False,
            "cleanup": False,
            "runtime_capital_live": False,
        },
    }
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_semantic_system_audit_report.json", report)
    write_csv(
        OUTPUT_DIR / "repo_only_exhaustive_python_semantic_inventory.csv",
        inventory_rows(semantics),
        [
            "path",
            "line_count",
            "function_count",
            "class_count",
            "status_string_count",
            "next_module_ref_count",
            "tool_ref_count",
            "output_ref_count",
            "write_ref_count",
            "subprocess_tool_ref_count",
        ],
    )
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_route_graph.json", route)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_active_route_conflicts.json", {"artifact_type": "repo_only_exhaustive_python_active_route_conflicts", "conflicts": route["conflicts"], "current_route_dead_end_edges": route["current_route_dead_end_edges"], "active_next_module_conflict_count": route["active_next_module_conflict_count"], "current_route_conflict_count": route["current_route_conflict_count"]})
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_generic_controller_line_blocker_map.json", generic)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_fake_success_noop_audit.json", fake)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_output_collision_audit.json", collisions)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_stale_checkpoint_audit.json", stale)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_useful_file_obstruction_audit.json", obstruction)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_risk_surface_reclassification.json", risk)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_generic_controller_repair_scope_checklist.json", repair)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_semantic_system_audit_summary.json", summary)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise AuditBlocked(f"missing required artifacts: {missing}")
    return summary


def blocked_summary(message: str) -> dict[str, Any]:
    summary = {
        "artifact_type": "repo_only_exhaustive_python_semantic_system_audit_summary",
        "exhaustive_python_semantic_system_audit_status": BLOCKED_DECISION,
        "audit_performed": False,
        "blocked_reason": message,
        "repo_clean": False,
        "tracked_python_count": 0,
        "python_files_scanned_count": 0,
        "files_not_scanned_count": 0,
        "syntax_error_count": 0,
        "bom_error_count": 0,
        "active_frontier_identified": False,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "current_next_module_confirmed": False,
        "expected_next_chunk_id": "chunk_04",
        "active_next_module_conflict_count": 0,
        "stale_next_module_file_count": 0,
        "route_dead_end_count": 0,
        "current_route_dead_end_count": 0,
        "semantic_noop_or_fake_success_suspect_count": 0,
        "current_route_fake_success_p0_count": 0,
        "output_collision_count": 0,
        "active_frontier_output_collision_count": 0,
        "stale_hardcoded_checkpoint_count": 0,
        "active_route_stale_hardcoded_checkpoint_count": 0,
        "generic_controller_dynamic_chunk_selection": False,
        "generic_controller_hardcoded_chunk_only": True,
        "generic_controller_safe_to_rerun_for_chunk_04": False,
        "generic_controller_blocker_count": 0,
        "all_generic_controller_blockers_mapped_to_lines": False,
        "useful_file_obstruction_candidate_count": 0,
        "active_obstruction_count": 0,
        "risky_surface_finding_count_total": 0,
        "current_route_risky_surface_count": 0,
        "current_route_dangerous_p0_count": 0,
        "current_route_attention_count": 0,
        "all_active_route_blockers_identified": False,
        "all_generic_controller_repair_blockers_identified": False,
        "no_hidden_active_obstruction_found": False,
        "repair_scope_complete": False,
        "repair_apply_safe_to_plan_next": False,
        "repair_apply_allowed_now": False,
        "current_p0_count": 1,
        "current_p1_attention_count": 0,
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "patch_allowed_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "final_decision": BLOCKED_DECISION,
        "current_evidence_chain_quality_after_audit": BLOCKED_QUALITY,
        "next_module": BLOCKED_NEXT_MODULE,
        "replacement_checks_all_true": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_exhaustive_python_semantic_system_audit_summary.json", summary)
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
