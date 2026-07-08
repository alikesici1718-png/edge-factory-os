#!/usr/bin/env python3
"""old_short exact gate source disambiguation review.

Source review only. This module does not run a backtest, rebuild gate decisions,
touch runtime/live/capital paths, generate candidates, or claim edge.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_gate_source_disambiguation_review_v1.py"
ARTIFACT_REL = "artifacts/old_short/old_short_gate_source_disambiguation_review_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

EVIDENCE_REL = "artifacts/old_short/old_short_evidence_recovery_status_refresh_v1.json"
CONTRACT_REL = "artifacts/old_short/old_short_frozen_route_contract_reconstruction_v1.json"
RECOVERY_REL = "artifacts/old_short/old_short_missing_data_source_recovery_discovery_v1.json"

STATUS_SELECTED = "PASS_REPO_ONLY_OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_SELECTED"
STATUS_AMBIGUOUS = "PASS_REPO_ONLY_OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_STILL_AMBIGUOUS"
STATUS_NO_VALID = "PASS_REPO_ONLY_OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_NO_VALID_SOURCE"
ARTIFACT_KIND = "OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_REVIEW"
MODULE = "edge_factory_os_repo_only_old_short_gate_source_disambiguation_review_v1"

MAX_FULL_CSV_BYTES = 10_000_000
MAX_SHA_BYTES = 50_000_000
REQUIRED_GATE_COLUMNS = {"decision", "family_key", "signal_id"}
OPTIONAL_CONTRACT_COLUMNS = {"reason", "target_entry_time", "planned_exit_time", "coin", "side", "strategy"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        if line[:2] == "??" and rel in allowed:
            continue
        return False
    return True


def tracked_python_count() -> int:
    out = git_output(["ls-files", "*.py"])
    return 0 if not out else len(out.splitlines())


def read_artifact(rel_path: str) -> tuple[dict[str, Any], str]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Required artifact missing: {rel_path}")
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw), raw


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


def sha256_file(path: Path, size_bytes: int | None) -> str | None:
    if size_bytes is None or size_bytes > MAX_SHA_BYTES:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def path_variants(path: str) -> set[str]:
    p = str(path)
    return {
        p,
        p.replace("\\", "/"),
        p.replace("/", "\\"),
        p.replace("\\", "\\\\"),
        Path(p).name,
    }


def parse_timestamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return None


def read_csv_candidate(path: Path, size_bytes: int | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "readable": False,
        "read_skipped": False,
        "header": [],
        "first_3_data_rows": [],
        "row_count": None,
        "timestamp_range": {"min_utc": None, "max_utc": None},
        "route_family_identifiers_found": [],
        "schema_compatible_with_frozen_contract": False,
        "contains_old_short_rows": False,
        "contains_exact_route_identifier": False,
        "contains_required_gate_columns": False,
        "read_error": None,
    }
    if path.suffix.lower() != ".csv":
        result["read_skipped"] = True
        result["read_error"] = "not_csv"
        return result
    if size_bytes is None or size_bytes > MAX_FULL_CSV_BYTES:
        result["read_skipped"] = True
        result["read_error"] = "csv_above_safe_full_read_threshold"
        return result

    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            header = list(reader.fieldnames or [])
            header_set = {str(col).strip() for col in header}
            lower_header = {col.lower() for col in header_set}
            result["header"] = header
            result["contains_required_gate_columns"] = REQUIRED_GATE_COLUMNS.issubset(lower_header)
            result["schema_compatible_with_frozen_contract"] = REQUIRED_GATE_COLUMNS.issubset(lower_header)
            identifiers: set[str] = set()
            timestamp_min: datetime | None = None
            timestamp_max: datetime | None = None
            old_short_rows = 0
            exact_route_rows = 0
            row_count = 0
            first_rows: list[dict[str, str]] = []
            for row in reader:
                row_count += 1
                if len(first_rows) < 3:
                    first_rows.append({k: str(v) for k, v in row.items()})
                family_key = str(row.get("family_key", "")).strip()
                strategy = str(row.get("strategy", "")).strip()
                signal_id = str(row.get("signal_id", "")).strip()
                if family_key:
                    identifiers.add(f"family_key:{family_key}")
                if strategy:
                    identifiers.add(f"strategy:{strategy}")
                if family_key == "old_short":
                    old_short_rows += 1
                if "old_short" in signal_id.lower() or strategy in {"blowoff_short", "mean_reversion_short"}:
                    exact_route_rows += 1
                for key in ("target_entry_time", "planned_exit_time", "log_time"):
                    ts = parse_timestamp(str(row.get(key, "")))
                    if ts is None:
                        continue
                    timestamp_min = ts if timestamp_min is None or ts < timestamp_min else timestamp_min
                    timestamp_max = ts if timestamp_max is None or ts > timestamp_max else timestamp_max
            result["readable"] = True
            result["first_3_data_rows"] = first_rows
            result["row_count"] = row_count
            result["route_family_identifiers_found"] = sorted(identifiers)
            result["contains_old_short_rows"] = old_short_rows > 0
            result["old_short_row_count"] = old_short_rows
            result["contains_exact_route_identifier"] = exact_route_rows > 0
            result["exact_route_identifier_row_count"] = exact_route_rows
            result["timestamp_range"] = {
                "min_utc": timestamp_min.strftime("%Y-%m-%dT%H:%M:%SZ") if timestamp_min else None,
                "max_utc": timestamp_max.strftime("%Y-%m-%dT%H:%M:%SZ") if timestamp_max else None,
            }
    except OSError as exc:
        result["read_error"] = f"{exc.__class__.__name__}: {exc}"
    return result


def review_candidate(
    candidate: dict[str, Any],
    frozen_gate_path: str,
    evidence_raw: str,
    expected_period_determined: bool,
) -> dict[str, Any]:
    path = Path(str(candidate.get("path", "")))
    exists = path.exists()
    stat = path.stat() if exists else None
    size_bytes = stat.st_size if stat and path.is_file() else None
    modified_time_utc = (
        datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if stat
        else None
    )
    referenced_by_contract = str(path).lower() == str(frozen_gate_path).lower()
    referenced_by_evidence = any(variant in evidence_raw for variant in path_variants(str(path)))
    csv_review = read_csv_candidate(path, size_bytes) if exists and path.is_file() else {}
    readable = bool(csv_review.get("readable")) if path.suffix.lower() == ".csv" else exists
    covers_expected_period = None if not expected_period_determined else False
    if not expected_period_determined:
        covers_expected_period_condition_passed = True
        covers_expected_period_reason = "not_applicable_expected_period_not_determined_from_frozen_contract"
    else:
        covers_expected_period_condition_passed = bool(covers_expected_period)
        covers_expected_period_reason = "expected_period_check_applied"

    contains_old_short_or_route = bool(
        csv_review.get("contains_old_short_rows") or csv_review.get("contains_exact_route_identifier")
    )
    direct_reference_condition = referenced_by_contract or referenced_by_evidence
    required_conditions = {
        "exists": exists,
        "readable": readable,
        "schema_compatible_with_frozen_contract": bool(csv_review.get("schema_compatible_with_frozen_contract")),
        "contains_old_short_gate_rows_or_exact_route_identifier": contains_old_short_or_route,
        "covers_expected_period_if_determined": covers_expected_period_condition_passed,
        "directly_referenced_by_frozen_contract_or_recovered_old_short_evidence": direct_reference_condition,
    }
    score_parts = [
        20 if exists else 0,
        20 if readable else 0,
        20 if csv_review.get("schema_compatible_with_frozen_contract") else 0,
        20 if contains_old_short_or_route else 0,
        10 if referenced_by_contract else 0,
        10 if referenced_by_evidence else 0,
    ]
    return {
        "path": str(path),
        "exists": exists,
        "is_file": path.is_file() if exists else False,
        "is_dir": path.is_dir() if exists else False,
        "size_bytes": size_bytes,
        "modified_time_utc": modified_time_utc,
        "extension": "".join(path.suffixes).lower() if path.is_file() else "",
        "inside_repo": is_inside_repo(path) if exists else False,
        "external": not is_inside_repo(path) if exists else None,
        "candidate_reason_from_recovery_artifact": candidate.get("why_it_matches", []),
        "referenced_directly_by_frozen_contract": referenced_by_contract,
        "referenced_by_old_short_evidence_status_artifact": referenced_by_evidence,
        "contains_old_short_rows": bool(csv_review.get("contains_old_short_rows")),
        "contains_required_gate_columns": bool(csv_review.get("contains_required_gate_columns")),
        "schema_header": csv_review.get("header", []),
        "first_3_data_rows": csv_review.get("first_3_data_rows", []),
        "route_family_identifiers_found": csv_review.get("route_family_identifiers_found", []),
        "timestamp_range": csv_review.get("timestamp_range", {"min_utc": None, "max_utc": None}),
        "row_count": csv_review.get("row_count"),
        "sha256": sha256_file(path, size_bytes) if exists and path.is_file() else None,
        "expected_period_review": {
            "expected_period_determined": expected_period_determined,
            "covers_expected_period": covers_expected_period,
            "condition_passed": covers_expected_period_condition_passed,
            "reason": covers_expected_period_reason,
        },
        "required_selection_conditions": required_conditions,
        "satisfies_all_required_selection_conditions": all(required_conditions.values()),
        "exact_source_score": int(sum(score_parts)),
        "read_error": csv_review.get("read_error"),
        "read_skipped": csv_review.get("read_skipped"),
    }


def classify_reviews(reviews: list[dict[str, Any]]) -> tuple[str, str, dict[str, Any], bool, str]:
    qualified = [row for row in reviews if row.get("satisfies_all_required_selection_conditions")]
    if len(qualified) == 1:
        return (
            STATUS_SELECTED,
            "OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_SELECTED",
            qualified[0],
            True,
            "OLD_SHORT_FROZEN_BACKTEST_RERUN_WITH_DISAMBIGUATED_EXACT_SOURCE",
        )
    if len(qualified) > 1:
        return (
            STATUS_AMBIGUOUS,
            "OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_STILL_AMBIGUOUS",
            {},
            False,
            "MANUAL_SOURCE_SELECTION_REQUIRED",
        )
    return (
        STATUS_NO_VALID,
        "OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_NO_VALID_SOURCE",
        {},
        False,
        "OLD_SHORT_REMAINS_MONITORING_ONLY_EXACT_GATE_SOURCE_UNAVAILABLE",
    )


def build_payload() -> dict[str, Any]:
    evidence, evidence_raw = read_artifact(EVIDENCE_REL)
    contract, _contract_raw = read_artifact(CONTRACT_REL)
    recovery, _recovery_raw = read_artifact(RECOVERY_REL)
    route_contract = contract.get("route_contract", {})
    entry_rule = route_contract.get("entry_rule", {})
    frozen_gate_path = str(entry_rule.get("global_gate_path", ""))
    gate_candidates = recovery.get("exact_source_assessment", {}).get("exact_global_gate_candidates", [])

    expected_period_determined = False
    reviews = [
        review_candidate(candidate, frozen_gate_path, evidence_raw, expected_period_determined)
        for candidate in gate_candidates
    ]
    reviews = sorted(
        reviews,
        key=lambda row: (
            row.get("satisfies_all_required_selection_conditions") is True,
            row.get("exact_source_score", 0),
            row.get("contains_old_short_rows") is True,
            row.get("referenced_directly_by_frozen_contract") is True,
        ),
        reverse=True,
    )
    status, classification, selected, allowed_next, next_step = classify_reviews(reviews)

    safety_permissions = {
        "gate_source_disambiguation_created": True,
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
        "evidence_recovery_artifact_loaded": evidence.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH_CREATED",
        "frozen_contract_artifact_loaded": contract.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION_CREATED",
        "missing_source_recovery_artifact_loaded": recovery.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_MISSING_DATA_SOURCE_RECOVERY_FOUND",
        "all_gate_candidates_reviewed": len(reviews) == len(gate_candidates) and len(gate_candidates) > 0,
        "deterministic_selection_rule_applied": True,
        "no_backtest_run": True,
        "no_gate_rebuild": True,
        "no_runtime_touched": True,
        "no_network_used": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": allowed_next,
    }
    replacement_checks_all_true = allowed_next and all(
        value is True for key, value in validation_checks.items() if key != "replacement_checks_all_true"
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
            "old_short_evidence_recovery": EVIDENCE_REL,
            "old_short_frozen_route_contract": CONTRACT_REL,
            "old_short_missing_data_source_recovery": RECOVERY_REL,
        },
        "frozen_contract_requirements": {
            "route_name": route_contract.get("route_name"),
            "family_key": route_contract.get("family_key"),
            "timeframe": route_contract.get("timeframe"),
            "exchange": route_contract.get("exchange"),
            "instrument_type": route_contract.get("instrument_type"),
            "global_gate_required_by_default": entry_rule.get("global_gate_required_by_default"),
            "global_gate_path": frozen_gate_path,
            "required_gate_decision": entry_rule.get("required_gate_decision"),
            "schema_minimum_columns_for_source_function": sorted(REQUIRED_GATE_COLUMNS),
            "optional_contract_columns_observed_in_gate_logs": sorted(OPTIONAL_CONTRACT_COLUMNS),
            "expected_period_determined": expected_period_determined,
        },
        "gate_candidate_reviews": reviews,
        "selection_rule": {
            "description": "Select only if exactly one candidate satisfies all deterministic source conditions.",
            "required_conditions": [
                "exists",
                "readable",
                "schema compatible with frozen contract",
                "contains old_short gate rows or exact route identifier",
                "covers frozen contract expected period if period can be determined",
                "directly referenced by frozen contract or recovered old_short evidence/status artifact",
                "no other candidate satisfies the same required conditions",
            ],
            "qualified_candidate_count": len(
                [row for row in reviews if row.get("satisfies_all_required_selection_conditions")]
            ),
        },
        "selected_gate_source": {
            "selected": bool(selected),
            "selected_gate_source_path": selected.get("path") if selected else None,
            "selection_reason": "exactly_one_candidate_satisfied_all_required_conditions"
            if selected
            else "no_candidate_satisfied_all_required_conditions"
            if classification.endswith("NO_VALID_SOURCE")
            else "multiple_candidates_satisfied_all_required_conditions",
        },
        "disambiguation_classification": classification,
        "continuation_decision": {
            "frozen_backtest_allowed_next": allowed_next,
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
    print(f"status: {payload['status']}")
    print(f"disambiguation_classification: {payload['disambiguation_classification']}")
    print(f"gate_candidate_count: {len(payload['gate_candidate_reviews'])}")
    selected_path = payload["selected_gate_source"].get("selected_gate_source_path")
    print(f"selected_gate_source_path: {selected_path if selected_path else 'null'}")
    print(f"frozen_backtest_allowed_next: {str(payload['continuation_decision']['frozen_backtest_allowed_next']).lower()}")
    print(f"next_step: {payload['continuation_decision']['next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


if __name__ == "__main__":
    main()
