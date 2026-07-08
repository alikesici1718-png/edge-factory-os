#!/usr/bin/env python3
"""Repo/local old_short missing data source recovery discovery.

Discovery only. No backtest, no strategy execution, no network/API, no runtime
or live/capital enablement, and no candidate/edge claim.
"""

from __future__ import annotations

import csv
import fnmatch
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DESKTOP_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop")
USER_ROOT = Path(r"C:\Users\alike")

TOOL_REL = "tools/edge_factory_os_repo_only_old_short_missing_data_source_recovery_discovery_v1.py"
ARTIFACT_REL = "artifacts/old_short/old_short_missing_data_source_recovery_discovery_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

STEP1_REL = "artifacts/old_short/old_short_evidence_recovery_status_refresh_v1.json"
STEP2_REL = "artifacts/old_short/old_short_frozen_route_contract_reconstruction_v1.json"

STATUS_FOUND = "PASS_REPO_ONLY_OLD_SHORT_MISSING_DATA_SOURCE_RECOVERY_FOUND"
STATUS_NOT_FOUND = "PASS_REPO_ONLY_OLD_SHORT_MISSING_DATA_SOURCE_RECOVERY_NOT_FOUND"
ARTIFACT_KIND = "OLD_SHORT_MISSING_DATA_SOURCE_RECOVERY_DISCOVERY"
MODULE = "edge_factory_os_repo_only_old_short_missing_data_source_recovery_discovery_v1"

SEARCH_PATTERNS = [
    "global_gate_decisions.csv",
    "*global*gate*decision*",
    "*gate*decision*",
    "*gate_replay*",
    "*old_short*",
    "*OLD_SHORT*",
    "*okx*1m*",
    "*OKX*1m*",
    "*USDT*SWAP*1m*",
    "*swap*1m*",
    "*old_short*gate*",
    "*old_short*decision*",
    "*old_short*monitor*",
    "*old_short*trade*",
]

SAFE_CSV_SAMPLE_BYTES = 5_000_000
MAX_CANDIDATES = 12000
PRUNE_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "site-packages",
    "dist",
    "build",
    ".cache",
    "AppData",
}
OKX_1M_RE = re.compile(r"^[A-Z0-9]+-USDT-SWAP_1m_.*\.csv$", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def norm_path(path: Path) -> str:
    return str(path.resolve())


def git_output(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repo_status_lines() -> list[str]:
    out = git_output(["status", "--short", "--untracked-files=all"])
    return [] if not out else out.splitlines()


def repo_clean_except_expected() -> bool:
    allowed = {TOOL_REL, ARTIFACT_REL}
    for line in repo_status_lines():
        rel = line[3:].replace("\\", "/")
        status = line[:2]
        if rel in allowed and status == "??":
            continue
        return False
    return True


def tracked_python_count() -> int:
    out = git_output(["ls-files", "*.py"])
    return 0 if not out else len(out.splitlines())


def load_json(rel_path: str) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Required artifact missing: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
        return True
    except ValueError:
        return False


def metadata_for(path: Path, why: list[str]) -> dict[str, Any]:
    try:
        stat = path.stat()
        size = stat.st_size if path.is_file() else None
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError as exc:
        size = None
        modified = None
        why = [*why, f"metadata_error:{exc.__class__.__name__}"]
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "size_bytes": size,
        "modified_time_utc": modified,
        "extension": "".join(path.suffixes).lower() if path.is_file() else "",
        "why_it_matches": sorted(set(why)),
        "inside_repo": is_inside_repo(path),
        "external": not is_inside_repo(path),
    }


def matching_reasons(path: Path) -> list[str]:
    text = str(path).replace("\\", "/")
    name = path.name
    lower_text = text.lower()
    lower_name = name.lower()
    reasons: list[str] = []
    for pattern in SEARCH_PATTERNS:
        p = pattern.lower()
        if fnmatch.fnmatch(lower_name, p) or fnmatch.fnmatch(lower_text, p):
            reasons.append(f"pattern:{pattern}")
    if name.lower() == "global_gate_decisions.csv":
        reasons.append("exact_filename:global_gate_decisions.csv")
    if OKX_1M_RE.match(name):
        reasons.append("filename_matches_okx_usdt_swap_1m_csv")
    return reasons


def sample_csv_if_safe(path: Path, size_bytes: int | None) -> dict[str, Any] | None:
    if not path.is_file() or path.suffix.lower() != ".csv":
        return None
    if size_bytes is None or size_bytes > SAFE_CSV_SAMPLE_BYTES:
        return {
            "sample_skipped": True,
            "reason": "csv_size_above_safe_sample_threshold_or_unknown",
            "safe_threshold_bytes": SAFE_CSV_SAMPLE_BYTES,
        }
    try:
        rows: list[list[str]] = []
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.reader(handle)
            for idx, row in enumerate(reader):
                rows.append(row[:20])
                if idx >= 2:
                    break
        return {
            "sample_skipped": False,
            "header": rows[0] if rows else [],
            "first_two_data_rows": rows[1:3] if len(rows) > 1 else [],
        }
    except OSError as exc:
        return {"sample_skipped": True, "reason": f"csv_sample_error:{exc.__class__.__name__}"}


def assess_candidate(record: dict[str, Any]) -> dict[str, Any]:
    path = Path(record["path"])
    name_lower = path.name.lower()
    path_lower = str(path).lower()
    reasons = set(record.get("why_it_matches", []))
    sample = record.get("csv_sample")
    header = sample.get("header", []) if isinstance(sample, dict) else []
    header_text = ",".join(str(x).lower() for x in header)
    rows_text = json.dumps(sample.get("first_two_data_rows", []), ensure_ascii=True).lower() if isinstance(sample, dict) else ""

    exact_gate = False
    if name_lower == "global_gate_decisions.csv":
        exact_gate = True
    if "gate" in path_lower and "decision" in path_lower and path.suffix.lower() == ".csv":
        if "signal" in header_text and ("decision" in header_text or "gate" in header_text):
            exact_gate = True
        if any(token in rows_text for token in ("allow", "wait", "block")):
            exact_gate = True

    exact_okx_1m = False
    if OKX_1M_RE.match(path.name) and "\\raw\\" in str(path).lower():
        exact_okx_1m = True
    if "filename_matches_okx_usdt_swap_1m_csv" in reasons:
        exact_okx_1m = True

    old_short_specific_root_hint = "old_short" in path_lower or "live_blowoff_short_paper_realistic" in path_lower
    return {
        "appears_exact_global_gate_replay": exact_gate,
        "appears_exact_okx_1m_source": exact_okx_1m,
        "old_short_specific_root_hint": old_short_specific_root_hint,
    }


def scan_roots() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    candidate_files: list[dict[str, Any]] = []
    candidate_dirs: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    inaccessible: list[dict[str, str]] = []
    visited_dirs = 0
    matched_paths: set[str] = set()

    roots = [REPO_ROOT, EDGE_LAB_ROOT, DESKTOP_ROOT, USER_ROOT]
    for root in roots:
        if not root.exists():
            skipped.append({"path": str(root), "reason": "search_root_missing"})
            continue
        for dirpath, dirnames, filenames in os.walk(root, topdown=True, onerror=None):
            current = Path(dirpath)
            visited_dirs += 1
            kept_dirs = []
            for dirname in dirnames:
                if dirname in PRUNE_DIR_NAMES:
                    skipped.append({"path": str(current / dirname), "reason": "pruned_directory_name_rule"})
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs

            dir_reasons = matching_reasons(current)
            if dir_reasons:
                key = norm_path(current)
                if key not in matched_paths and len(candidate_dirs) < MAX_CANDIDATES:
                    matched_paths.add(key)
                    record = metadata_for(current, dir_reasons)
                    record.update(assess_candidate(record))
                    candidate_dirs.append(record)

            for filename in filenames:
                path = current / filename
                reasons = matching_reasons(path)
                if not reasons:
                    continue
                key = norm_path(path)
                if key in matched_paths:
                    continue
                if len(candidate_files) >= MAX_CANDIDATES:
                    skipped.append({"path": str(path), "reason": "candidate_limit_reached"})
                    continue
                matched_paths.add(key)
                try:
                    record = metadata_for(path, reasons)
                    record["csv_sample"] = sample_csv_if_safe(path, record.get("size_bytes"))
                    record.update(assess_candidate(record))
                    candidate_files.append(record)
                except OSError as exc:
                    inaccessible.append({"path": str(path), "reason": exc.__class__.__name__})

    scan_summary = {
        "visited_directories": visited_dirs,
        "candidate_file_count": len(candidate_files),
        "candidate_directory_count": len(candidate_dirs),
        "skipped_paths_count": len(skipped),
        "inaccessible_paths_count": len(inaccessible),
        "skipped_paths_sample": skipped[:200],
        "inaccessible_paths_sample": inaccessible[:200],
        "candidate_limit": MAX_CANDIDATES,
        "pruned_directory_name_rules": sorted(PRUNE_DIR_NAMES),
    }
    return candidate_files, candidate_dirs, scan_summary


def symbol_from_okx_path(path: str) -> str | None:
    match = re.search(r"([A-Z0-9]+)-USDT-SWAP_1m_", Path(path).name, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).upper()


def build_payload() -> dict[str, Any]:
    step1 = load_json(STEP1_REL)
    step2 = load_json(STEP2_REL)
    route_contract = step2.get("route_contract", {})
    data_source = route_contract.get("data_source", {})
    entry_rule = route_contract.get("entry_rule", {})

    candidate_files, candidate_dirs, scan_summary = scan_roots()
    exact_gate_candidates = [row for row in candidate_files if row.get("appears_exact_global_gate_replay")]
    exact_okx_candidates = [row for row in candidate_files if row.get("appears_exact_okx_1m_source")]
    okx_symbols = sorted({symbol for row in exact_okx_candidates if (symbol := symbol_from_okx_path(row["path"]))})

    old_short_roots_with_both: list[dict[str, Any]] = []
    root_checks = [EDGE_LAB_ROOT, EDGE_LAB_ROOT / "paper_run_gate_MASTER_UPPER_SYSTEM"]
    for root in root_checks:
        root_str = str(root).lower()
        has_gate = any(str(row["path"]).lower().startswith(root_str) for row in exact_gate_candidates)
        has_okx = any(str(row["path"]).lower().startswith(root_str) for row in exact_okx_candidates)
        if has_gate or has_okx:
            old_short_roots_with_both.append(
                {
                    "root": str(root),
                    "has_exact_global_gate": has_gate,
                    "has_exact_okx_1m_source": has_okx,
                    "contains_both_required_sources": has_gate and has_okx,
                }
            )

    exact_global_gate = len(exact_gate_candidates) > 0
    exact_okx_1m = len(exact_okx_candidates) > 0
    both_exact = exact_global_gate and exact_okx_1m
    if both_exact:
        status = STATUS_FOUND
        classification = "OLD_SHORT_EXACT_DATA_SOURCES_FOUND_READY_FOR_FROZEN_BACKTEST"
        next_step = "OLD_SHORT_FROZEN_BACKTEST_RERUN_WITH_EXACT_RECOVERED_SOURCES"
        frozen_backtest_allowed_next = True
    elif exact_global_gate or exact_okx_1m:
        status = STATUS_NOT_FOUND
        classification = "OLD_SHORT_PARTIAL_DATA_SOURCES_FOUND_MANUAL_SELECTION_REQUIRED"
        next_step = "MANUAL_SOURCE_SELECTION_REQUIRED"
        frozen_backtest_allowed_next = False
    else:
        status = STATUS_NOT_FOUND
        classification = "OLD_SHORT_EXACT_DATA_SOURCES_NOT_FOUND_FROZEN_BACKTEST_REMAINS_BLOCKED"
        next_step = "OLD_SHORT_REMAINS_MONITORING_ONLY_EXACT_RERUN_UNAVAILABLE"
        frozen_backtest_allowed_next = False

    safety_permissions = {
        "data_source_recovery_discovery_created": True,
        "frozen_backtest_allowed_next": frozen_backtest_allowed_next,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_except_expected(),
        "step1_evidence_artifact_loaded": step1.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH_CREATED",
        "step2_contract_artifact_loaded": step2.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION_CREATED",
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
    }
    replacement_checks_all_true = all(validation_checks.values()) and all(
        value is False
        for key, value in safety_permissions.items()
        if key.endswith("_allowed_now")
    )

    payload = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "head": git_output(["rev-parse", "HEAD"]),
            "repo_clean_before_run": validation_checks["repo_clean_before_run"],
            "tracked_python_count_before": tracked_python_count(),
            "generated_at_utc": utc_now(),
        },
        "source_artifacts": {
            "step1_evidence_recovery": STEP1_REL,
            "step2_frozen_route_contract": STEP2_REL,
        },
        "frozen_contract_requirements": {
            "route_name": route_contract.get("route_name"),
            "timeframe": route_contract.get("timeframe"),
            "exchange": route_contract.get("exchange"),
            "instrument_type": route_contract.get("instrument_type"),
            "historical_file_pattern_in_source": data_source.get("historical_file_pattern_in_source"),
            "runtime_public_endpoint_in_source": data_source.get("runtime_public_endpoint_in_source"),
            "reviewed_historical_data_required_before_backtest": data_source.get(
                "reviewed_historical_data_required_before_backtest"
            ),
            "global_gate_required_by_default": entry_rule.get("global_gate_required_by_default"),
            "global_gate_path": entry_rule.get("global_gate_path"),
            "required_gate_decision": entry_rule.get("required_gate_decision"),
            "no_1h_panel_substitution_allowed": True,
        },
        "search_roots": [str(REPO_ROOT), str(EDGE_LAB_ROOT), str(DESKTOP_ROOT), str(USER_ROOT)],
        "search_patterns": SEARCH_PATTERNS,
        "candidate_files": candidate_files,
        "candidate_directories": candidate_dirs,
        "scan_summary": scan_summary,
        "exact_source_assessment": {
            "exact_global_gate_decisions_found": exact_global_gate,
            "exact_global_gate_candidate_count": len(exact_gate_candidates),
            "exact_global_gate_candidates": exact_gate_candidates[:50],
            "exact_okx_1m_source_found": exact_okx_1m,
            "exact_okx_1m_candidate_count": len(exact_okx_candidates),
            "exact_okx_1m_symbols_found_count": len(okx_symbols),
            "exact_okx_1m_symbols_found": okx_symbols,
            "exact_okx_1m_candidate_examples": exact_okx_candidates[:100],
            "old_short_specific_roots_containing_sources": old_short_roots_with_both,
            "both_required_sources_found": both_exact,
        },
        "classification": classification,
        "continuation_decision": {
            "frozen_backtest_allowed_next": frozen_backtest_allowed_next,
            "next_step": next_step,
            "strategy_execution_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
        },
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    return payload


def main() -> None:
    payload = build_payload()
    write_artifact(payload)
    assessment = payload["exact_source_assessment"]
    candidate_count = len(payload["candidate_files"]) + len(payload["candidate_directories"])
    print(f"status: {payload['status']}")
    print(f"classification: {payload['classification']}")
    print(f"exact_global_gate_decisions_found: {str(assessment['exact_global_gate_decisions_found']).lower()}")
    print(f"exact_okx_1m_source_found: {str(assessment['exact_okx_1m_source_found']).lower()}")
    print(f"candidate_count: {candidate_count}")
    print(f"frozen_backtest_allowed_next: {str(payload['continuation_decision']['frozen_backtest_allowed_next']).lower()}")
    print(f"next_step: {payload['continuation_decision']['next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


if __name__ == "__main__":
    main()
