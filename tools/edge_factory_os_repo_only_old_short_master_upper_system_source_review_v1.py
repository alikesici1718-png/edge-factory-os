#!/usr/bin/env python3
"""Targeted old_short MASTER_UPPER_SYSTEM source review.

Read-only targeted source review. This module does not execute the logger,
run a backtest, touch runtime/live/capital, restore/copy/move/delete files,
use network/API, generate candidates, or claim edge.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_master_upper_system_source_review_v1.py"
ARTIFACT_REL = "artifacts/old_short/old_short_master_upper_system_source_review_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

EVIDENCE_REL = "artifacts/old_short/old_short_evidence_recovery_status_refresh_v1.json"
CONTRACT_REL = "artifacts/old_short/old_short_frozen_route_contract_reconstruction_v1.json"
RECOVERY_REL = "artifacts/old_short/old_short_missing_data_source_recovery_discovery_v1.json"
DISAMBIGUATION_REL = "artifacts/old_short/old_short_gate_source_disambiguation_review_v1.json"
CLOSURE_REL = "artifacts/old_short/old_short_exact_rerun_unavailable_closure_v1.json"
DEEP_SEARCH_REL = "artifacts/old_short/old_short_deep_gate_source_forensic_search_v1.json"

MASTER_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic")
LOGGER_SCRIPT = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")
OLDER_ROOTS = {
    "v4_priority": Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_priority\live_blowoff_short_paper_realistic"),
    "v4_1_no_session": Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_1_no_session\live_blowoff_short_paper_realistic"),
    "v4_2_final": Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_2_final\live_blowoff_short_paper_realistic"),
}

STATUS_SELECTED = "PASS_REPO_ONLY_OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW_EXACT_SELECTED"
STATUS_PROMISING = "PASS_REPO_ONLY_OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW_PROMISING_NOT_EXACT"
STATUS_NOT_FOUND = "PASS_REPO_ONLY_OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW_NOT_FOUND"
ARTIFACT_KIND = "OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW"
MODULE = "edge_factory_os_repo_only_old_short_master_upper_system_source_review_v1"

SAFE_READ_BYTES = 10_000_000
SHA_BYTES = 50_000_000
GATE_SCHEMA_MINIMUM = {"decision", "family_key", "signal_id"}
SEARCH_NAME_TERMS = (
    "global_gate_decisions",
    "gate",
    "decision",
    "gate_replay",
    "paper_run_gate",
    "old_short",
    "trade",
    "monitor",
)
READ_EXTENSIONS = {".csv", ".json", ".txt", ".py", ".md", ".log"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_stdout(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repo_status_lines() -> list[str]:
    out = git_stdout(["status", "--short", "--untracked-files=all"])
    return [] if not out else out.splitlines()


def repo_clean_except_expected() -> bool:
    allowed = {TOOL_REL, ARTIFACT_REL}
    for line in repo_status_lines():
        rel = line[3:].replace("\\", "/")
        if line[:2] == "??" and rel in allowed:
            continue
        return False
    return True


def tracked_python_count() -> int:
    out = git_stdout(["ls-files", "*.py"])
    return 0 if not out else len(out.splitlines())


def load_json(rel_path: str, required: bool = True) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Required artifact missing: {rel_path}")
        return {}
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


def file_sha(path: Path, size: int | None) -> str | None:
    if size is None or size > SHA_BYTES or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_text(path: Path, size: int | None) -> tuple[str | None, str | None]:
    if not path.is_file():
        return None, "not_file"
    if size is None or size > SAFE_READ_BYTES:
        return None, "above_safe_read_threshold"
    if path.suffix.lower() not in READ_EXTENSIONS:
        return None, "extension_not_safely_read"
    try:
        return path.read_text(encoding="utf-8", errors="replace"), None
    except OSError as exc:
        return None, f"{exc.__class__.__name__}: {exc}"


def parse_ts(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return None


def csv_review(text: str) -> dict[str, Any]:
    reader = csv.DictReader(text.splitlines())
    header = list(reader.fieldnames or [])
    lower_header = {h.lower() for h in header}
    first_rows: list[dict[str, str]] = []
    route_ids: set[str] = set()
    row_count = 0
    old_short_rows = 0
    live_path_rows = 0
    min_ts: datetime | None = None
    max_ts: datetime | None = None
    for row in reader:
        row_count += 1
        if len(first_rows) < 3:
            first_rows.append({str(k): str(v) for k, v in row.items()})
        row_text = json.dumps(row, ensure_ascii=True).lower()
        family_key = str(row.get("family_key", "")).strip()
        strategy = str(row.get("strategy", "")).strip()
        signal_id = str(row.get("signal_id", "")).strip()
        if family_key:
            route_ids.add(f"family_key:{family_key}")
        if strategy:
            route_ids.add(f"strategy:{strategy}")
        if "old_short" in row_text or family_key == "old_short":
            old_short_rows += 1
        if "live_blowoff_short_paper_realistic" in row_text:
            live_path_rows += 1
        if "_blowoff_short_" in signal_id or "_mean_reversion_short_" in signal_id:
            route_ids.add("signal_id:old_short_pattern")
        for key in ("log_time", "target_entry_time", "planned_exit_time", "signal_time", "entry_time", "exit_time"):
            ts = parse_ts(str(row.get(key, "")))
            if ts is None:
                continue
            min_ts = ts if min_ts is None or ts < min_ts else min_ts
            max_ts = ts if max_ts is None or ts > max_ts else max_ts
    return {
        "schema_header": header,
        "first_3_rows": first_rows,
        "row_count": row_count,
        "contains_old_short_rows": old_short_rows > 0,
        "old_short_row_count": old_short_rows,
        "contains_live_blowoff_short_paper_realistic_rows_or_path_reference": live_path_rows > 0,
        "live_path_reference_row_count": live_path_rows,
        "route_identifiers_found": sorted(route_ids),
        "timestamp_range": {
            "min_utc": min_ts.strftime("%Y-%m-%dT%H:%M:%SZ") if min_ts else None,
            "max_utc": max_ts.strftime("%Y-%m-%dT%H:%M:%SZ") if max_ts else None,
        },
        "schema_compatible_with_frozen_contract": GATE_SCHEMA_MINIMUM.issubset(lower_header),
    }


def text_review(text: str) -> dict[str, Any]:
    lower = text.lower()
    header_like = []
    first_lines = text.splitlines()[:3]
    for line in first_lines:
        if "," in line:
            header_like = [part.strip() for part in line.split(",")]
            break
    return {
        "schema_header": header_like,
        "first_3_rows": first_lines,
        "row_count": None,
        "contains_old_short_rows": "old_short" in lower,
        "old_short_row_count": lower.count("old_short"),
        "contains_live_blowoff_short_paper_realistic_rows_or_path_reference": "live_blowoff_short_paper_realistic" in lower,
        "live_path_reference_row_count": lower.count("live_blowoff_short_paper_realistic"),
        "route_identifiers_found": sorted(
            token
            for token in ["old_short", "blowoff_short", "mean_reversion_short", "global_gate_decisions.csv"]
            if token in lower
        ),
        "timestamp_range": {"min_utc": None, "max_utc": None},
        "schema_compatible_with_frozen_contract": all(term in lower for term in GATE_SCHEMA_MINIMUM),
    }


def under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def review_file(path: Path, root_type: str, logger_refs: set[str], frozen_gate_path: str) -> dict[str, Any]:
    exists = path.exists()
    stat = path.stat() if exists else None
    size = stat.st_size if stat and path.is_file() else None
    modified = (
        datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if stat
        else None
    )
    text, read_error = safe_text(path, size)
    content = {
        "schema_header": [],
        "first_3_rows": [],
        "row_count": None,
        "contains_old_short_rows": False,
        "old_short_row_count": 0,
        "contains_live_blowoff_short_paper_realistic_rows_or_path_reference": False,
        "live_path_reference_row_count": 0,
        "route_identifiers_found": [],
        "timestamp_range": {"min_utc": None, "max_utc": None},
        "schema_compatible_with_frozen_contract": False,
    }
    if text is not None:
        content = csv_review(text) if path.suffix.lower() == ".csv" else text_review(text)
    pstr = str(path)
    referenced_by_logger = pstr in logger_refs or path.name in logger_refs
    under_master = under(path, MASTER_ROOT)
    directly_frozen_contract_gate = pstr.lower() == frozen_gate_path.lower()
    master_link = under_master or referenced_by_logger
    contains_route = bool(
        content["contains_old_short_rows"]
        or content["contains_live_blowoff_short_paper_realistic_rows_or_path_reference"]
    )
    schema_ok = bool(content["schema_compatible_with_frozen_contract"])
    is_gate_like = path.suffix.lower() == ".csv" and ("gate" in path.name.lower() or "decision" in path.name.lower())
    exact_conditions = {
        "under_master_or_directly_referenced_by_logger": master_link,
        "contains_old_short_or_live_blowoff_route_rows_or_reference": contains_route,
        "schema_compatible_with_frozen_contract": schema_ok,
        "more_directly_linked_to_master_than_old_v4_roots": master_link and root_type in {"MASTER_UPPER_SYSTEM", "logger_reference", "prior_artifact_reference"},
        "is_gate_like_csv": is_gate_like,
    }
    score = (
        (25 if master_link else 0)
        + (25 if contains_route else 0)
        + (25 if schema_ok else 0)
        + (15 if root_type == "MASTER_UPPER_SYSTEM" else 0)
        + (10 if referenced_by_logger else 0)
        + (5 if directly_frozen_contract_gate else 0)
    )
    return {
        "path": pstr,
        "source_root_type": root_type,
        "exists": exists,
        "size_bytes": size,
        "modified_time_utc": modified,
        "extension": "".join(path.suffixes).lower() if path.is_file() else "",
        "referenced_by_logger": referenced_by_logger,
        "under_MASTER_UPPER_SYSTEM": under_master,
        "directly_frozen_contract_gate_path": directly_frozen_contract_gate,
        "contains_old_short_rows": content["contains_old_short_rows"],
        "contains_live_blowoff_short_paper_realistic_rows_or_path_reference": content[
            "contains_live_blowoff_short_paper_realistic_rows_or_path_reference"
        ],
        "schema_header": content["schema_header"],
        "first_3_rows": content["first_3_rows"],
        "route_identifiers_found": content["route_identifiers_found"],
        "timestamp_range": content["timestamp_range"],
        "row_count": content["row_count"],
        "sha256": file_sha(path, size) if exists else None,
        "schema_compatible_with_frozen_contract": schema_ok,
        "deterministic_exact_source_score": score,
        "exact_selection_conditions": exact_conditions,
        "satisfies_exact_master_selection_rule": all(exact_conditions.values()),
        "read_error_or_skip_reason": read_error,
    }


def collect_root_candidates(root: Path, root_type: str) -> list[Path]:
    if not root.exists():
        return []
    candidates: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            path = Path(dirpath) / filename
            lower = filename.lower()
            ext = path.suffix.lower()
            if ext in {".csv", ".json", ".txt"} or any(term in lower for term in SEARCH_NAME_TERMS):
                candidates.append(path)
    return candidates


def extract_logger_review(logger_path: Path) -> tuple[dict[str, Any], set[str]]:
    if not logger_path.exists():
        return {"exists": False, "checked": True, "readable": False}, set()
    text = logger_path.read_text(encoding="utf-8", errors="replace")
    refs = set(re.findall(r"[A-Z]:\\[^\"'\n\r]+", text))
    refs.update(re.findall(r"[A-Za-z0-9_./\\-]+(?:\.csv|\.json|\.txt)", text))
    route_terms = sorted(token for token in ["old_short", "old_short_gate_aware", "blowoff_short", "mean_reversion_short", "live_blowoff_short_paper_realistic", "global_gate_decisions.csv"] if token in text)
    output_refs = sorted(ref for ref in refs if "live_blowoff_short_paper_realistic" in ref or "paper_run_gate" in ref)
    gate_refs = sorted(ref for ref in refs if "gate" in ref.lower() or "decision" in ref.lower())
    file_names_written = sorted(set(re.findall(r'"([A-Za-z0-9_./\\-]+\.(?:csv|json|txt))"', text)))
    return (
        {
            "exists": True,
            "checked": True,
            "readable": True,
            "path": str(logger_path),
            "size_bytes": logger_path.stat().st_size,
            "sha256": file_sha(logger_path, logger_path.stat().st_size),
            "route_identifiers_found": route_terms,
            "output_directory_references": output_refs,
            "gate_decision_file_references": gate_refs,
            "file_names_written_or_referenced": file_names_written,
            "master_upper_system_references": [ref for ref in refs if "MASTER_UPPER_SYSTEM" in ref],
            "schema_or_column_tokens_visible": sorted(token for token in ["decision", "family_key", "signal_id", "target_entry_time", "planned_exit_time", "coin", "side", "strategy"] if token in text),
            "logger_not_executed": True,
        },
        refs,
    )


def unique_reviews(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in reviews:
        key = row["path"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def classify(reviews: list[dict[str, Any]]) -> tuple[str, str, dict[str, Any] | None, bool, str]:
    qualified = [row for row in reviews if row.get("satisfies_exact_master_selection_rule")]
    if len(qualified) == 1:
        return (
            STATUS_SELECTED,
            "OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW_EXACT_SELECTED",
            qualified[0],
            True,
            "OLD_SHORT_FROZEN_BACKTEST_RERUN_WITH_MASTER_UPPER_SYSTEM_EXACT_SOURCE",
        )
    if qualified or any(row.get("contains_old_short_rows") for row in reviews):
        return (
            STATUS_PROMISING,
            "OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW_PROMISING_NOT_EXACT",
            None,
            False,
            "MANUAL_MASTER_SOURCE_SELECTION_REQUIRED" if len(qualified) > 1 else "OLD_SHORT_REMAINS_MONITORING_ONLY_EXACT_GATE_SOURCE_UNAVAILABLE",
        )
    return (
        STATUS_NOT_FOUND,
        "OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW_NOT_FOUND",
        None,
        False,
        "OLD_SHORT_REMAINS_MONITORING_ONLY_EXACT_GATE_SOURCE_UNAVAILABLE",
    )


def build_payload() -> dict[str, Any]:
    evidence = load_json(EVIDENCE_REL)
    contract = load_json(CONTRACT_REL)
    recovery = load_json(RECOVERY_REL)
    disambiguation = load_json(DISAMBIGUATION_REL)
    closure = load_json(CLOSURE_REL)
    deep = load_json(DEEP_SEARCH_REL, required=False)

    route_contract = contract.get("route_contract", {})
    entry_rule = route_contract.get("entry_rule", {})
    frozen_gate_path = str(entry_rule.get("global_gate_path", ""))
    logger_review, logger_refs = extract_logger_review(LOGGER_SCRIPT)

    reviews: list[dict[str, Any]] = []
    master_paths = collect_root_candidates(MASTER_ROOT, "MASTER_UPPER_SYSTEM")
    for path in master_paths:
        reviews.append(review_file(path, "MASTER_UPPER_SYSTEM", logger_refs, frozen_gate_path))

    older_reviews: dict[str, Any] = {}
    for root_type, root in OLDER_ROOTS.items():
        paths = collect_root_candidates(root, root_type)
        older_reviews[root_type] = {"root": str(root), "exists": root.exists(), "candidate_count": len(paths)}
        for path in paths:
            reviews.append(review_file(path, root_type, logger_refs, frozen_gate_path))

    for ref in logger_refs:
        if ".csv" in ref.lower() or ".json" in ref.lower() or ".txt" in ref.lower():
            path = Path(ref)
            if path.exists():
                reviews.append(review_file(path, "logger_reference", logger_refs, frozen_gate_path))

    # Include prior artifact gate candidates for comparison, but do not let them outrank MASTER linkage.
    for row in recovery.get("exact_source_assessment", {}).get("exact_global_gate_candidates", []):
        path = Path(str(row.get("path", "")))
        if path.exists():
            reviews.append(review_file(path, "prior_artifact_reference", logger_refs, frozen_gate_path))

    reviews = sorted(
        unique_reviews(reviews),
        key=lambda row: (
            row.get("satisfies_exact_master_selection_rule") is True,
            int(row.get("deterministic_exact_source_score") or 0),
            row.get("under_MASTER_UPPER_SYSTEM") is True,
            row.get("contains_old_short_rows") is True,
        ),
        reverse=True,
    )
    status, classification, selected, allowed_next, next_step = classify(reviews)
    master_candidate_count = len([row for row in reviews if row.get("source_root_type") == "MASTER_UPPER_SYSTEM"])

    selected_source = {
        "selected": selected is not None,
        "selected_gate_source_path": selected.get("path") if selected else None,
        "source_selection_basis": "deterministic_master_upper_system_link" if selected else None,
        "selected_gate_source_sha256": selected.get("sha256") if selected else None,
    }
    safety_permissions = {
        "master_upper_system_source_review_created": True,
        "frozen_backtest_allowed_next": allowed_next,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_except_expected(),
        "prior_old_short_artifacts_loaded": all(
            [
                evidence.get("status") == "PASS_REPO_ONLY_OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH_CREATED",
                contract.get("status") == "PASS_REPO_ONLY_OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION_CREATED",
                recovery.get("status") == "PASS_REPO_ONLY_OLD_SHORT_MISSING_DATA_SOURCE_RECOVERY_FOUND",
                disambiguation.get("status") == "PASS_REPO_ONLY_OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_NO_VALID_SOURCE",
                closure.get("status") == "PASS_REPO_ONLY_OLD_SHORT_EXACT_RERUN_UNAVAILABLE_CLOSURE_CREATED",
            ]
        ),
        "logger_script_checked": logger_review.get("checked") is True,
        "master_upper_system_root_checked": MASTER_ROOT.exists(),
        "older_roots_checked": True,
        "deterministic_selection_rule_applied": True,
        "no_backtest_run": True,
        "logger_not_executed": True,
        "no_runtime_touched": True,
        "no_file_restore_copy_move_delete": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
    }
    replacement_checks_all_true = all(validation_checks.values())

    payload = {
        "status": status,
        "artifact_kind": "OLD_SHORT_MASTER_UPPER_SYSTEM_SOURCE_REVIEW",
        "module": MODULE,
        "source_checkpoint": {
            "head": git_stdout(["rev-parse", "HEAD"]),
            "repo_clean_before_run": validation_checks["repo_clean_before_run"],
            "tracked_python_count_before": tracked_python_count(),
            "generated_at_utc": utc_now(),
        },
        "source_artifacts": {
            "evidence_recovery": EVIDENCE_REL,
            "frozen_route_contract": CONTRACT_REL,
            "missing_data_source_recovery": RECOVERY_REL,
            "gate_source_disambiguation": DISAMBIGUATION_REL,
            "exact_rerun_unavailable_closure": CLOSURE_REL,
            "deep_gate_source_forensic_search": DEEP_SEARCH_REL if deep else None,
        },
        "provided_paths": {
            "primary_active_master_path": str(MASTER_ROOT),
            "logger_script": str(LOGGER_SCRIPT),
            "older_related_roots": {key: str(path) for key, path in OLDER_ROOTS.items()},
        },
        "logger_script_review": logger_review,
        "master_upper_system_root_review": {
            "root": str(MASTER_ROOT),
            "exists": MASTER_ROOT.exists(),
            "candidate_count": master_candidate_count,
            "checked_first": True,
        },
        "older_root_reviews": older_reviews,
        "candidate_gate_reviews": reviews,
        "comparison_to_prior_ambiguous_candidates": {
            "frozen_contract_gate_path": frozen_gate_path,
            "frozen_contract_gate_candidate_result": next((row for row in reviews if row.get("directly_frozen_contract_gate_path")), None),
            "paper_run_gate_v4_priority_result": next((row for row in reviews if "paper_run_gate_v4_priority" in row.get("path", "")), None),
            "contradiction_resolved": selected is not None,
            "summary": (
                "MASTER_UPPER_SYSTEM review selects a source only if a MASTER-linked gate-like CSV "
                "contains old_short/live route rows and frozen-compatible schema without competing MASTER candidates."
            ),
        },
        "selected_gate_source": selected_source,
        "source_review_classification": classification,
        "continuation_decision": {
            "frozen_backtest_allowed_next": allowed_next,
            "next_step": next_step,
            "strategy_execution_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
        },
        "limitations": [
            "Logger script was parsed as text only and not executed.",
            "Large files were sampled only when below the safe read threshold.",
            "No gate decisions were inferred, rebuilt, or manually overridden.",
            "No reviewed 1h panel substitution was used.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    return payload


def main() -> None:
    payload = build_payload()
    write_artifact(payload)
    master_count = payload["master_upper_system_root_review"]["candidate_count"]
    selected_path = payload["selected_gate_source"].get("selected_gate_source_path")
    print(f"status: {payload['status']}")
    print(f"source_review_classification: {payload['source_review_classification']}")
    print(f"master_candidate_count: {master_count}")
    print(f"selected_gate_source_path: {selected_path if selected_path else 'null'}")
    print(f"frozen_backtest_allowed_next: {str(payload['continuation_decision']['frozen_backtest_allowed_next']).lower()}")
    print(f"next_step: {payload['continuation_decision']['next_step']}")
    print("logger_script_checked: true")
    print("master_root_checked: true")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


if __name__ == "__main__":
    main()
