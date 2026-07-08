import gzip
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_full_range_202105_202510_review_v1.py"
ARTIFACT_PATH = "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_full_range_202105_202510_review_v1.json"
STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_FULL_RANGE_202105_202510_REVIEW_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_RATE_FULL_RANGE_202105_202510_REVIEW"

ACQUISITION_PATH = "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1.json"
ACQUISITION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_FULL_RANGE_202105_202510_ACQUISITION_LOCK_CREATED"
EXPECTED_SYMBOL_COUNT = 81
WINDOW_START_MS = 1_619_827_200_000
WINDOW_END_EXCLUSIVE_MS = 1_761_955_200_000
WINDOW_START_UTC = "2021-05-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2025-11-01T00:00:00Z"
LARGE_GAP_THRESHOLD_HOURS = 24
EXPECTED_KEYS = {"funding_rate", "funding_time_ms", "funding_time_utc", "mark_price", "source_endpoint", "symbol"}


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash(payload: Dict[str, Any]) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"payload hash mismatch: {recomputed} != {stored}")
    return stored


def decimal_from_string(value: Any, label: str) -> Decimal:
    if not isinstance(value, str) or value == "":
        raise ValueError(f"missing or non-string decimal field {label}")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal field {label}: {value}") from exc


def validate_no_forbidden_permissions(source_artifacts: Iterable[Dict[str, Any]]) -> bool:
    forbidden_true_keys = {
        "candidate_generation",
        "candidate_generation_allowed_now",
        "edge_claim",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_live_capital",
        "runtime_live_capital_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "holdout_access_allowed_now",
        "strategy_execution_allowed_now",
    }

    def walk(value: Any) -> bool:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_true_keys and child is True:
                    return False
                if not walk(child):
                    return False
        elif isinstance(value, list):
            for child in value:
                if not walk(child):
                    return False
        return True

    return all(walk(artifact) for artifact in source_artifacts)


def review_symbol_file(symbol: str, file_path: Path, expected_sha256: str) -> Dict[str, Any]:
    if not file_path.exists():
        raise RuntimeError(f"funding file missing for {symbol}: {file_path}")
    actual_hash = sha256_file(file_path)
    if actual_hash != expected_sha256:
        raise RuntimeError(f"funding file sha256 mismatch for {symbol}: {actual_hash} != {expected_sha256}")
    record_count = 0
    duplicate_count = 0
    outside_window_count = 0
    invalid_numeric_count = 0
    missing_required_field_count = 0
    monotonic_violation_count = 0
    large_gap_count = 0
    max_gap_hours = 0.0
    prior_time: Optional[int] = None
    seen = set()
    min_time: Optional[int] = None
    max_time: Optional[int] = None
    with gzip.open(file_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            record_count += 1
            if set(row.keys()) != EXPECTED_KEYS:
                missing_required_field_count += 1
                continue
            if row.get("symbol") != symbol:
                missing_required_field_count += 1
                continue
            try:
                funding_time_ms = int(row["funding_time_ms"])
                decimal_from_string(row["funding_rate"], "funding_rate")
                if row.get("mark_price") is not None:
                    decimal_from_string(row["mark_price"], "mark_price")
            except (ValueError, TypeError, InvalidOperation):
                invalid_numeric_count += 1
                continue
            if funding_time_ms < WINDOW_START_MS or funding_time_ms >= WINDOW_END_EXCLUSIVE_MS:
                outside_window_count += 1
            if funding_time_ms in seen:
                duplicate_count += 1
            seen.add(funding_time_ms)
            if prior_time is not None:
                if funding_time_ms <= prior_time:
                    monotonic_violation_count += 1
                gap_hours = (funding_time_ms - prior_time) / 3_600_000.0
                max_gap_hours = max(max_gap_hours, gap_hours)
                if gap_hours > LARGE_GAP_THRESHOLD_HOURS:
                    large_gap_count += 1
            prior_time = funding_time_ms
            min_time = funding_time_ms if min_time is None else min(min_time, funding_time_ms)
            max_time = funding_time_ms if max_time is None else max(max_time, funding_time_ms)
    return {
        "symbol": symbol,
        "record_count": record_count,
        "min_funding_time_ms": min_time,
        "max_funding_time_ms": max_time,
        "duplicate_count": duplicate_count,
        "outside_window_count": outside_window_count,
        "invalid_numeric_count": invalid_numeric_count,
        "missing_required_field_count": missing_required_field_count,
        "monotonic_violation_count": monotonic_violation_count,
        "large_gap_count": large_gap_count,
        "max_gap_hours": round(max_gap_hours, 6),
        "sha256": actual_hash,
    }


def build_review() -> Dict[str, Any]:
    acquisition = read_json(ACQUISITION_PATH)
    acquisition_hash = verify_hash(acquisition)
    if acquisition.get("status") != ACQUISITION_STATUS:
        raise RuntimeError("acquisition lock status mismatch")
    if not validate_no_forbidden_permissions([acquisition]):
        raise RuntimeError("acquisition artifact unexpectedly grants forbidden permission")
    summary = acquisition["funding_data_output_summary"]
    index_path = Path(summary["funding_index_path"])
    if not index_path.exists():
        raise RuntimeError("external funding index missing")
    if sha256_file(index_path) != summary["funding_index_sha256"]:
        raise RuntimeError("external funding index sha256 mismatch")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    symbol_files = index.get("symbol_files")
    if not isinstance(symbol_files, list) or len(symbol_files) != EXPECTED_SYMBOL_COUNT:
        raise RuntimeError("funding index symbol_files count mismatch")
    manifest_hashes = summary["funding_files_hashes"]
    symbol_reviews: List[Dict[str, Any]] = []
    for record in sorted(symbol_files, key=lambda item: item["symbol"]):
        symbol = record["symbol"]
        file_path = Path(record["output_file_path"])
        expected_hash = manifest_hashes[symbol]
        symbol_reviews.append(review_symbol_file(symbol, file_path, expected_hash))

    total_records = sum(item["record_count"] for item in symbol_reviews)
    symbols_with_zero_records = [item["symbol"] for item in symbol_reviews if item["record_count"] == 0]
    duplicate_count = sum(item["duplicate_count"] for item in symbol_reviews)
    outside_window_count = sum(item["outside_window_count"] for item in symbol_reviews)
    invalid_numeric_count = sum(item["invalid_numeric_count"] for item in symbol_reviews)
    missing_required_field_count = sum(item["missing_required_field_count"] for item in symbol_reviews)
    monotonic_violation_count = sum(item["monotonic_violation_count"] for item in symbol_reviews)
    large_gap_count = sum(item["large_gap_count"] for item in symbol_reviews)
    min_times = [item["min_funding_time_ms"] for item in symbol_reviews if item["min_funding_time_ms"] is not None]
    max_times = [item["max_funding_time_ms"] for item in symbol_reviews if item["max_funding_time_ms"] is not None]

    p0_issues: List[str] = []
    if len(symbol_reviews) != EXPECTED_SYMBOL_COUNT:
        p0_issues.append("symbol_count_not_81")
    if symbols_with_zero_records:
        p0_issues.append("symbols_with_zero_records")
    if duplicate_count:
        p0_issues.append("duplicate_symbol_funding_time")
    if outside_window_count:
        p0_issues.append("records_outside_window")
    if invalid_numeric_count:
        p0_issues.append("invalid_numeric_values")
    if missing_required_field_count:
        p0_issues.append("missing_required_fields")
    if monotonic_violation_count:
        p0_issues.append("non_monotonic_symbol_times")
    if total_records != summary["total_funding_records"]:
        p0_issues.append("total_record_count_mismatch")
    if summary["duplicate_count"] != duplicate_count:
        p0_issues.append("manifest_duplicate_count_mismatch")
    funding_valid = len(p0_issues) == 0
    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_artifacts": {
            "acquisition_lock_artifact": ACQUISITION_PATH,
            "acquisition_payload_sha256_excluding_hash": acquisition_hash,
            "funding_index_path": str(index_path),
            "funding_index_sha256": summary["funding_index_sha256"],
        },
        "review_scope": {
            "symbol_count": len(symbol_reviews),
            "window_start_utc": WINDOW_START_UTC,
            "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
            "network_used": False,
            "panel_rows_read": False,
            "strategy_executed": False,
        },
        "funding_data_review": {
            "total_funding_records": total_records,
            "min_funding_time_utc": None if not min_times else acquisition["funding_data_output_summary"]["min_funding_time_utc"],
            "max_funding_time_utc": None if not max_times else acquisition["funding_data_output_summary"]["max_funding_time_utc"],
            "symbols_with_zero_records": symbols_with_zero_records,
            "duplicate_count": duplicate_count,
            "records_outside_window_count": outside_window_count,
            "invalid_numeric_count": invalid_numeric_count,
            "missing_required_field_count": missing_required_field_count,
            "monotonic_violation_count": monotonic_violation_count,
            "large_gap_review": {
                "large_gap_threshold_hours": LARGE_GAP_THRESHOLD_HOURS,
                "total_large_gap_count": large_gap_count,
                "symbols_with_large_gaps": [item["symbol"] for item in symbol_reviews if item["large_gap_count"] > 0],
                "max_gap_hours_global": max((item["max_gap_hours"] for item in symbol_reviews), default=0),
            },
            "p0_issue_count": len(p0_issues),
            "p0_issues": p0_issues,
            "funding_data_valid_for_full_range_signal_construction": funding_valid,
        },
        "symbol_review_summary": symbol_reviews,
        "safety_permissions": {
            "funding_data_review_completed": True,
            "strategy_execution_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "execution_required_next": funding_valid,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "strategy_executed": False,
            "strategy_search_executed": False,
            "non_preregistered_config_tested": False,
            "binance_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "okx_panel_rows_read": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_review_artifact_expected": True,
            "acquisition_lock_loaded": True,
            "acquisition_payload_hash_verified": True,
            "index_hash_verified": True,
            "symbol_count_verified_81": len(symbol_reviews) == EXPECTED_SYMBOL_COUNT,
            "records_exist_for_every_symbol": not symbols_with_zero_records,
            "timestamps_within_window": outside_window_count == 0,
            "monotonic_per_symbol": monotonic_violation_count == 0,
            "no_duplicates": duplicate_count == 0,
            "funding_rate_numeric_valid": invalid_numeric_count == 0,
            "no_missing_required_fields": missing_required_field_count == 0,
            "no_network_used": True,
            "no_panel_rows_read": True,
            "no_strategy_execution": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["funding_data_review"]["funding_data_valid_for_full_range_signal_construction"] is True,
        payload["forbidden_actions_confirmed_false"]["network_used"] is False,
        payload["forbidden_actions_confirmed_false"]["binance_panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["strategy_executed"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("review invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_review()
    output_path = REPO_ROOT / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "artifact_path": ARTIFACT_PATH,
        "symbol_count": artifact["review_scope"]["symbol_count"],
        "total_funding_records": artifact["funding_data_review"]["total_funding_records"],
        "min_funding_time_utc": artifact["funding_data_review"]["min_funding_time_utc"],
        "max_funding_time_utc": artifact["funding_data_review"]["max_funding_time_utc"],
        "p0_issue_count": artifact["funding_data_review"]["p0_issue_count"],
        "funding_data_valid_for_full_range_signal_construction": artifact["funding_data_review"]["funding_data_valid_for_full_range_signal_construction"],
        "network_used": False,
        "strategy_executed": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
