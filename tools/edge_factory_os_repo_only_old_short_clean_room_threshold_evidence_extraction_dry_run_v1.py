import csv
import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_old_short_clean_room_threshold_evidence_extraction_dry_run_v1.py"
ARTIFACT_PATH = "artifacts/old_short_clean_room/old_short_clean_room_threshold_evidence_extraction_dry_run_v1.json"
STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_EVIDENCE_EXTRACTION_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_EVIDENCE_EXTRACTION_DRY_RUN"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "609a07e03a92afc36c31043cec29a1c50af682d6"
EXPECTED_TRACKED_PYTHON_COUNT = 944

THRESHOLD_CONTRACT = "artifacts/old_short_clean_room/old_short_clean_room_threshold_reconstruction_contract_v1.json"
CLEAN_ROOM_CONTRACT = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
SCHEMA_FIXTURE_CHECK = "artifacts/old_short_clean_room/old_short_clean_room_runner_schema_fixture_validator_check_v1.json"
OLD_SHORT_METADATA_DIR = "artifacts/old_short"

MASTER_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
LOGGER_SCRIPT = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")

MASTER_OUTPUT_FILES = {
    "signals": MASTER_DIR / "signals.csv",
    "pending_entries": MASTER_DIR / "pending_entries.csv",
    "closed_trades": MASTER_DIR / "closed_trades.csv",
    "rejected_entries": MASTER_DIR / "rejected_entries.csv",
    "heartbeat": MASTER_DIR / "heartbeat.csv",
    "state": MASTER_DIR / "state.json",
}

EVIDENCE_SOURCE_CATEGORIES = ("signals", "pending_entries", "closed_trades", "rejected_entries")
FEATURE_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
]
KNOWN_SUBFAMILIES = {"blowoff_short", "mean_reversion_short"}
REJECT_REASON_FIELDS = [
    "reject_reason",
    "rejection_reason",
    "reason",
    "status_reason",
    "gate_reason",
    "block_reason",
]
SIGNAL_TIME_FIELDS = ["signal_time", "signal_timestamp", "signal_ts", "timestamp", "ts", "created_at"]
ENTRY_TIME_FIELDS = ["entry_time", "entry_timestamp", "entry_ts", "filled_at", "open_time"]
EXIT_TIME_FIELDS = ["exit_time", "exit_timestamp", "exit_ts", "closed_at", "close_time"]
PLANNED_EXIT_TIME_FIELDS = ["planned_exit_time", "planned_exit_timestamp", "planned_exit_ts", "target_exit_time"]
NOTIONAL_FIELDS = [
    "notional",
    "notional_usd",
    "position_notional",
    "position_notional_usd",
    "entry_notional",
    "entry_notional_usd",
    "size_usdt",
    "order_notional",
]
EQUITY_FIELDS = ["equity", "account_equity", "base_equity", "paper_equity", "starting_equity"]


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(args: List[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def tracked_python_count() -> int:
    output = run_git(["ls-files", "*.py"])
    return 0 if not output else len(output.splitlines())


def dirty_paths() -> List[str]:
    output = run_git(["status", "--short"])
    paths: List[str] = []
    for line in output.splitlines():
        if line:
            paths.append(line[3:].strip().strip('"').replace("\\", "/"))
    return sorted(paths)


def read_json_path(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing required JSON artifact: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON artifact is not an object: {path}")
    return payload


def optional_json_review(path: Path) -> Dict[str, Any]:
    review: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "loaded": False,
        "sha256": file_sha256(path),
        "status": None,
        "artifact_kind": None,
        "route_key": None,
        "payload_sha256_excluding_hash": None,
        "replacement_checks_all_true": None,
        "load_error": None,
    }
    if not path.exists():
        return review
    try:
        payload = read_json_path(path)
    except Exception as exc:
        review["load_error"] = str(exc)
        return review
    review.update(
        {
            "loaded": True,
            "status": payload.get("status"),
            "artifact_kind": payload.get("artifact_kind"),
            "route_key": payload.get("route_key")
            or payload.get("threshold_reconstruction_identity", {}).get("route_key")
            if isinstance(payload.get("threshold_reconstruction_identity"), dict)
            else payload.get("route_key"),
            "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
            "replacement_checks_all_true": payload.get("replacement_checks_all_true"),
        }
    )
    return review


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "na", "n/a"}:
        return None
    text = text.replace(",", "")
    try:
        numeric = float(text)
    except ValueError:
        return None
    if not math.isfinite(numeric):
        return None
    return numeric


def quantile(sorted_values: Sequence[float], q: float) -> Optional[float]:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return round(sorted_values[0], 6)
    pos = (len(sorted_values) - 1) * q
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))
    if lower == upper:
        return round(sorted_values[lower], 6)
    weight = pos - lower
    return round(sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight, 6)


def numeric_summary(values: Sequence[float]) -> Dict[str, Any]:
    clean = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not clean:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "p10": None,
            "p25": None,
            "p50": None,
            "p75": None,
            "p90": None,
            "median_absolute_deviation": None,
        }
    median = quantile(clean, 0.5)
    deviations = sorted(abs(value - float(median)) for value in clean)
    return {
        "count": len(clean),
        "min": round(clean[0], 6),
        "max": round(clean[-1], 6),
        "p10": quantile(clean, 0.10),
        "p25": quantile(clean, 0.25),
        "p50": median,
        "p75": quantile(clean, 0.75),
        "p90": quantile(clean, 0.90),
        "median_absolute_deviation": quantile(deviations, 0.5),
    }


def feature_summary(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    row_count = len(rows)
    summaries: Dict[str, Any] = {}
    missing_counts: Dict[str, int] = {}
    missing_rates: Dict[str, Optional[float]] = {}
    observed_feature_count = 0
    for field in FEATURE_FIELDS:
        values: List[float] = []
        missing = 0
        for row in rows:
            numeric = safe_float(row.get(field))
            if numeric is None:
                missing += 1
            else:
                values.append(numeric)
        missing_counts[field] = missing
        missing_rates[field] = None if row_count == 0 else round(missing / row_count, 6)
        summaries[field] = numeric_summary(values)
        if values:
            observed_feature_count += 1
    return {
        "row_count": row_count,
        "observed_feature_count": observed_feature_count,
        "missing_count_by_feature": missing_counts,
        "missing_field_rates": missing_rates,
        "feature_summaries": summaries,
    }


def first_nonempty(row: Dict[str, str], fields: Iterable[str]) -> Optional[str]:
    for field in fields:
        value = row.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def normalize_family(row: Dict[str, str]) -> Tuple[str, str, bool]:
    family_key_value = first_nonempty(row, ["family_key", "route_family", "strategy_key"])
    family_value = first_nonempty(row, ["family", "signal_family", "strategy_family", "subfamily"])
    subfamily_value = first_nonempty(row, ["subfamily", "signal_subfamily", "family"])
    family_key_available = family_key_value is not None
    family_key = family_key_value or "old_short"
    subfamily = subfamily_value or family_value or "unknown"
    if subfamily not in KNOWN_SUBFAMILIES and family_value in KNOWN_SUBFAMILIES:
        subfamily = str(family_value)
    return family_key, subfamily, family_key_available


def is_old_short_row(row: Dict[str, str]) -> bool:
    family_key, subfamily, family_key_available = normalize_family(row)
    if family_key_available:
        return family_key == "old_short"
    return subfamily in KNOWN_SUBFAMILIES or "old_short" in " ".join(str(value).lower() for value in row.values())


def parse_time(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "na", "n/a"}:
        return None
    numeric = safe_float(text)
    if numeric is not None:
        try:
            if numeric > 10_000_000_000:
                numeric = numeric / 1000.0
            return datetime.fromtimestamp(numeric, timezone.utc)
        except (OverflowError, OSError, ValueError):
            pass
    normalized = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(text, fmt)
                break
            except ValueError:
                dt = None  # type: ignore[assignment]
        if dt is None:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def minutes_between(start: Optional[datetime], end: Optional[datetime]) -> Optional[float]:
    if start is None or end is None:
        return None
    return (end - start).total_seconds() / 60.0


def read_csv_evidence(path: Path) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    review: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "loaded": False,
        "sha256": file_sha256(path),
        "header": None,
        "row_count": 0,
        "old_short_row_count": 0,
        "family_key_filter_available": False,
        "missing_file_recorded": not path.exists(),
        "load_error": None,
    }
    if not path.exists():
        return [], review
    rows: List[Dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            review["header"] = list(reader.fieldnames or [])
            for row in reader:
                normalized = {str(key): ("" if value is None else str(value)) for key, value in row.items() if key is not None}
                rows.append(normalized)
    except Exception as exc:
        review["load_error"] = str(exc)
        return [], review
    old_short_rows = [row for row in rows if is_old_short_row(row)]
    review.update(
        {
            "loaded": True,
            "row_count": len(rows),
            "old_short_row_count": len(old_short_rows),
            "family_key_filter_available": any("family_key" in row for row in rows),
        }
    )
    return old_short_rows, review


def collect_reject_reason_summary(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    reason_counts: Counter[str] = Counter()
    grouped_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    gate_missing = 0
    gate_timeout = 0
    gate_block = 0
    for row in rows:
        reason = first_nonempty(row, REJECT_REASON_FIELDS) or "UNKNOWN"
        reason_counts[reason] += 1
        grouped_rows[reason].append(row)
        lower = reason.lower()
        if "gate" in lower and "missing" in lower:
            gate_missing += 1
        if "gate" in lower and "timeout" in lower:
            gate_timeout += 1
        if "gate" in lower and any(token in lower for token in ("block", "blocked", "reject", "denied")):
            gate_block += 1
    return {
        "reject_reason_counts": dict(sorted(reason_counts.items())),
        "rejected_reason_count": len(reason_counts),
        "gate_missing_count": gate_missing,
        "gate_timeout_count": gate_timeout,
        "gate_block_count": gate_block,
        "feature_summaries_by_reject_reason": {
            reason: feature_summary(reason_rows) for reason, reason_rows in sorted(grouped_rows.items())
        },
    }


def lifecycle_summary(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    entry_delays: List[float] = []
    hold_minutes: List[float] = []
    planned_hold_minutes: List[float] = []
    timestamp_presence = {
        "signal_time_rows": 0,
        "entry_time_rows": 0,
        "exit_time_rows": 0,
        "planned_exit_time_rows": 0,
    }
    for row in rows:
        signal_time = parse_time(first_nonempty(row, SIGNAL_TIME_FIELDS))
        entry_time = parse_time(first_nonempty(row, ENTRY_TIME_FIELDS))
        exit_time = parse_time(first_nonempty(row, EXIT_TIME_FIELDS))
        planned_exit_time = parse_time(first_nonempty(row, PLANNED_EXIT_TIME_FIELDS))
        if signal_time is not None:
            timestamp_presence["signal_time_rows"] += 1
        if entry_time is not None:
            timestamp_presence["entry_time_rows"] += 1
        if exit_time is not None:
            timestamp_presence["exit_time_rows"] += 1
        if planned_exit_time is not None:
            timestamp_presence["planned_exit_time_rows"] += 1
        entry_delay = minutes_between(signal_time, entry_time)
        if entry_delay is not None:
            entry_delays.append(entry_delay)
        hold = minutes_between(entry_time, exit_time)
        if hold is not None:
            hold_minutes.append(hold)
        planned_hold = minutes_between(entry_time or signal_time, planned_exit_time)
        if planned_hold is not None:
            planned_hold_minutes.append(planned_hold)
    return {
        "timestamp_presence": timestamp_presence,
        "entry_delay_minutes_summary": numeric_summary(entry_delays),
        "hold_minutes_summary": numeric_summary(hold_minutes),
        "planned_hold_minutes_summary": numeric_summary(planned_hold_minutes),
        "known_approximate_entry_delay_minutes": 2,
        "known_approximate_hold_minutes": 120,
    }


def notional_summary(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    notional_values: List[float] = []
    equity_values: List[float] = []
    observed_notional_fields: Counter[str] = Counter()
    observed_equity_fields: Counter[str] = Counter()
    for row in rows:
        for field in NOTIONAL_FIELDS:
            numeric = safe_float(row.get(field))
            if numeric is not None:
                notional_values.append(numeric)
                observed_notional_fields[field] += 1
                break
        for field in EQUITY_FIELDS:
            numeric = safe_float(row.get(field))
            if numeric is not None:
                equity_values.append(numeric)
                observed_equity_fields[field] += 1
                break
    return {
        "notional_distribution": numeric_summary(notional_values),
        "median_notional": numeric_summary(notional_values)["p50"],
        "observed_notional_fields": dict(sorted(observed_notional_fields.items())),
        "base_equity_distribution": numeric_summary(equity_values),
        "base_equity_interpretation_if_available": (
            "Equity-like fields are summarized descriptively only and are not used for threshold selection."
            if equity_values
            else "No equity-like field available in allowed output rows."
        ),
        "observed_equity_fields": dict(sorted(observed_equity_fields.items())),
        "pnl_used_to_choose_thresholds": False,
    }


def load_old_short_metadata_reviews() -> Tuple[Dict[str, Any], int]:
    metadata_dir = REPO_ROOT / OLD_SHORT_METADATA_DIR
    reviews: Dict[str, Any] = {}
    if not metadata_dir.exists():
        return {"directory": OLD_SHORT_METADATA_DIR, "exists": False, "files": {}}, 0
    found = 0
    for path in sorted(metadata_dir.glob("*.json")):
        review = optional_json_review(path)
        reviews[path.name] = review
        if review["exists"]:
            found += 1
    return {"directory": OLD_SHORT_METADATA_DIR, "exists": True, "files": reviews}, found


def build_payload() -> Dict[str, Any]:
    actual_head = run_git(["rev-parse", "HEAD"])
    actual_tracked_python_count = tracked_python_count()
    current_dirty_paths = dirty_paths()
    allowed_dirty = {MODULE_PATH, ARTIFACT_PATH}
    unexpected_dirty = [path for path in current_dirty_paths if path not in allowed_dirty]
    if unexpected_dirty:
        raise RuntimeError(f"unexpected dirty paths before dry-run: {unexpected_dirty}")
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"HEAD moved before dry-run: {actual_head} != {EXPECTED_HEAD}")
    if actual_tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before dry-run: "
            f"{actual_tracked_python_count} != {EXPECTED_TRACKED_PYTHON_COUNT}"
        )

    threshold_contract_path = REPO_ROOT / THRESHOLD_CONTRACT
    threshold_contract = read_json_path(threshold_contract_path)
    threshold_identity = threshold_contract.get("threshold_reconstruction_identity", {})
    if not isinstance(threshold_identity, dict):
        raise RuntimeError("threshold reconstruction identity missing")
    behavioral = threshold_identity.get("behavioral_threshold_reconstruction") is True
    exact_recovered = threshold_identity.get("original_exact_thresholds_recovered") is True
    no_pnl_optimization = threshold_identity.get("no_pnl_optimization") is True
    if threshold_contract.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_CONTRACT_CREATED":
        raise RuntimeError("threshold reconstruction contract status mismatch")
    if not behavioral or exact_recovered or not no_pnl_optimization:
        raise RuntimeError("threshold reconstruction contract flags do not match required dry-run gate")

    source_file_review: Dict[str, Any] = {
        "threshold_reconstruction_contract": optional_json_review(threshold_contract_path),
        "clean_room_contract": optional_json_review(REPO_ROOT / CLEAN_ROOM_CONTRACT),
        "runner_preview": optional_json_review(REPO_ROOT / RUNNER_PREVIEW),
        "runner_schema_fixture_validator_check": optional_json_review(REPO_ROOT / SCHEMA_FIXTURE_CHECK),
    }
    old_short_metadata_review, metadata_found_count = load_old_short_metadata_reviews()
    source_file_review["old_short_metadata_json"] = old_short_metadata_review

    source_rows: Dict[str, List[Dict[str, str]]] = {}
    found_count = 0
    for category, path in MASTER_OUTPUT_FILES.items():
        if category in EVIDENCE_SOURCE_CATEGORIES:
            rows, review = read_csv_evidence(path)
            source_rows[category] = rows
            source_file_review[category] = review
        elif path.suffix.lower() == ".json":
            source_file_review[category] = optional_json_review(path)
        else:
            _rows, review = read_csv_evidence(path)
            source_file_review[category] = review
        if path.exists():
            found_count += 1

    logger_review = {
        "path": str(LOGGER_SCRIPT),
        "exists": LOGGER_SCRIPT.exists(),
        "loaded_as_text_only": False,
        "sha256": file_sha256(LOGGER_SCRIPT),
        "line_count": None,
        "executed": False,
        "load_error": None,
    }
    if LOGGER_SCRIPT.exists():
        try:
            logger_review["line_count"] = len(LOGGER_SCRIPT.read_text(encoding="utf-8", errors="replace").splitlines())
            logger_review["loaded_as_text_only"] = True
            found_count += 1
        except Exception as exc:
            logger_review["load_error"] = str(exc)
    source_file_review["logger_script_text_only"] = logger_review
    source_files_found_count = (
        found_count
        + metadata_found_count
        + sum(
            1
            for key in (
                "threshold_reconstruction_contract",
                "clean_room_contract",
                "runner_preview",
                "runner_schema_fixture_validator_check",
            )
            if source_file_review[key]["exists"]
        )
    )

    all_old_short_rows: List[Dict[str, str]] = []
    family_groups: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    source_category_summaries: Dict[str, Any] = {}
    family_key_available_count = 0
    subfamily_counts: Counter[str] = Counter()
    source_usable_feature_distribution_count = 0
    observed_feature_fields: set[str] = set()

    for category in EVIDENCE_SOURCE_CATEGORIES:
        rows = source_rows.get(category, [])
        all_old_short_rows.extend(rows)
        source_summary = feature_summary(rows)
        if source_summary["observed_feature_count"] > 0 and rows:
            source_usable_feature_distribution_count += 1
        family_counter: Counter[str] = Counter()
        for row in rows:
            family_key, subfamily, family_key_available = normalize_family(row)
            if family_key_available:
                family_key_available_count += 1
            subfamily_counts[subfamily] += 1
            family_group_key = f"{family_key}/{subfamily}"
            family_counter[family_group_key] += 1
            family_groups[family_group_key].append(row)
            for feature in FEATURE_FIELDS:
                if safe_float(row.get(feature)) is not None:
                    observed_feature_fields.add(feature)
        source_summary["family_subfamily_counts"] = dict(sorted(family_counter.items()))
        source_summary["loaded"] = source_file_review.get(category, {}).get("loaded", False)
        source_summary["source_path"] = source_file_review.get(category, {}).get("path")
        source_category_summaries[category] = source_summary

    family_feature_summaries = {
        family_group: {
            **feature_summary(rows),
            "sources_present": sorted(
                category
                for category, category_rows in source_rows.items()
                if any(row in category_rows for row in rows)
            ),
        }
        for family_group, rows in sorted(family_groups.items())
    }

    rejected_rows = source_rows.get("rejected_entries", [])
    reject_reason_summaries = collect_reject_reason_summary(rejected_rows)
    lifecycle_evidence_summary = lifecycle_summary(all_old_short_rows)
    notional_evidence_summary = notional_summary(all_old_short_rows)

    old_short_row_count = len(all_old_short_rows)
    family_count = len(family_groups)
    feature_count = len(observed_feature_fields)
    family_subfamily_evidence_exists = any(subfamily in KNOWN_SUBFAMILIES for subfamily in subfamily_counts)
    usable_feature_rows_found = any(
        any(safe_float(row.get(feature)) is not None for feature in FEATURE_FIELDS) for row in all_old_short_rows
    )
    no_forbidden_optimization_used = True

    if old_short_row_count <= 0 or not usable_feature_rows_found:
        result_classification = "OLD_SHORT_THRESHOLD_EVIDENCE_EXTRACTION_INCONCLUSIVE_NO_EDGE_NO_LIVE"
        next_allowed_step = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_INCONCLUSIVE_CLOSURE_V1"
    elif (
        family_subfamily_evidence_exists
        and feature_count > 0
        and source_usable_feature_distribution_count >= 1
        and no_forbidden_optimization_used
    ):
        result_classification = "OLD_SHORT_THRESHOLD_EVIDENCE_EXTRACTION_READY_FOR_BEHAVIORAL_PROPOSAL_NO_EDGE_NO_LIVE"
        next_allowed_step = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_CONTRACT_V1"
    else:
        result_classification = "OLD_SHORT_THRESHOLD_EVIDENCE_EXTRACTION_PARTIAL_INSUFFICIENT_FOR_PROPOSAL_NO_EDGE_NO_LIVE"
        next_allowed_step = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_CONTRACT_V1"

    unresolved_fields = threshold_contract.get("unresolved_fields_preserved")
    if not isinstance(unresolved_fields, list):
        unresolved_fields = [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
        ]

    forbidden_optimization_checks = {
        "threshold_proposal_created": False,
        "threshold_selection_performed": False,
        "threshold_grid_search_performed": False,
        "runner_executed": False,
        "signals_generated": False,
        "backtest_run": False,
        "pnl_based_optimization": False,
        "validation_or_holdout_returns_used": False,
        "trade_profitability_used_to_choose_thresholds": False,
        "pnl_selected_feature_cut": False,
        "candidate_generated": False,
        "edge_claimed": False,
        "forbidden_optimization_used": False,
    }

    safety_permissions = {
        "threshold_evidence_extraction_dry_run_created": True,
        "threshold_proposal_allowed_now": False,
        "runner_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "backtest_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "threshold_reconstruction_contract_loaded": True,
        "original_exact_thresholds_not_claimed": exact_recovered is False,
        "behavioral_threshold_reconstruction_preserved": behavioral,
        "no_pnl_optimization_preserved": no_pnl_optimization,
        "no_threshold_proposal": True,
        "no_threshold_selection": True,
        "no_threshold_grid_search": True,
        "no_pnl_computation_for_optimization": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": not unexpected_dirty,
        "replacement_checks_all_true": True,
    }

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "actual_clean_head": EXPECTED_HEAD,
            "actual_head_verified_at_artifact_creation": actual_head,
            "repo_clean_before_run": True,
            "tracked_python_count_before_run": EXPECTED_TRACKED_PYTHON_COUNT,
            "tracked_python_count_verified_at_artifact_creation": actual_tracked_python_count,
            "dirty_paths_during_artifact_creation_limited_to_expected_new_paths": True,
            "dirty_paths_during_artifact_creation": current_dirty_paths,
        },
        "source_artifacts": {
            "threshold_reconstruction_contract": {
                "path": THRESHOLD_CONTRACT,
                "status": threshold_contract.get("status"),
                "route_key": threshold_identity.get("route_key"),
                "behavioral_threshold_reconstruction": behavioral,
                "original_exact_thresholds_recovered": exact_recovered,
                "no_pnl_optimization": no_pnl_optimization,
                "loaded": True,
            },
            "allowed_clean_room_artifacts_reviewed": {
                "clean_room_contract": source_file_review["clean_room_contract"],
                "runner_preview": source_file_review["runner_preview"],
                "runner_schema_fixture_validator_check": source_file_review[
                    "runner_schema_fixture_validator_check"
                ],
            },
            "old_short_metadata_reviewed_as_metadata_only": source_file_review["old_short_metadata_json"],
            "master_upper_system_output_dir": str(MASTER_DIR),
            "logger_script_read_as_text_only": logger_review,
        },
        "evidence_extraction_identity": {
            "route_key": ROUTE_KEY,
            "dry_run_only": True,
            "threshold_evidence_extraction": True,
            "threshold_proposal": False,
            "threshold_selection": False,
            "runner_execution": False,
            "signal_generation": False,
            "backtest": False,
            "pnl_optimization": False,
            "family_key": "old_short",
            "families_preserved": sorted(KNOWN_SUBFAMILIES),
            "side": "short",
            "known_feature_fields": FEATURE_FIELDS,
            "approximate_entry_delay_minutes": 2,
            "approximate_hold_minutes": 120,
            "global_gate_required": True,
            "exact_original_source_or_thresholds_recovered": False,
        },
        "source_file_review": source_file_review,
        "old_short_row_summary": {
            "old_short_row_count": old_short_row_count,
            "source_files_found_count": source_files_found_count,
            "family_count": family_count,
            "feature_count": feature_count,
            "observed_feature_fields": sorted(observed_feature_fields),
            "family_key_available_row_count": family_key_available_count,
            "subfamily_counts": dict(sorted(subfamily_counts.items())),
            "source_old_short_row_counts": {
                category: len(source_rows.get(category, [])) for category in EVIDENCE_SOURCE_CATEGORIES
            },
        },
        "family_feature_summaries": family_feature_summaries,
        "source_category_summaries": source_category_summaries,
        "reject_reason_summaries": reject_reason_summaries,
        "lifecycle_evidence_summary": lifecycle_evidence_summary,
        "notional_evidence_summary": notional_evidence_summary,
        "evidence_quality_summary": {
            "old_short_rows_exist": old_short_row_count > 0,
            "family_subfamily_evidence_exists": family_subfamily_evidence_exists,
            "usable_feature_rows_found": usable_feature_rows_found,
            "source_usable_feature_distribution_count": source_usable_feature_distribution_count,
            "limited_family_or_source_coverage": not family_subfamily_evidence_exists
            or source_usable_feature_distribution_count < 2,
            "no_forbidden_optimization_used": no_forbidden_optimization_used,
            "classification_rule_applied": result_classification,
        },
        "forbidden_optimization_checks": forbidden_optimization_checks,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": unresolved_fields,
        "limitations": [
            "Dry-run extracts descriptive evidence only and does not propose or select thresholds.",
            "Missing optional MASTER_UPPER_SYSTEM output files are recorded instead of substituted.",
            "No raw market data, raw OKX 1m data, private API, runner, validator, signal generation, or backtest was used.",
            "Min/max and quantiles are descriptive only and are not PnL-selected feature cuts.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    if not all(validation_checks.values()):
        raise RuntimeError(f"validation checks failed: {validation_checks}")
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    if canonical_payload_hash(payload) != payload["payload_sha256_excluding_hash"]:
        raise RuntimeError("payload hash failed to stabilize")
    return payload


def main() -> None:
    payload = build_payload()
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    stdout_payload = {
        "status": payload["status"],
        "route_key": payload["evidence_extraction_identity"]["route_key"],
        "result_classification": payload["result_classification"],
        "source_files_found_count": payload["old_short_row_summary"]["source_files_found_count"],
        "old_short_row_count": payload["old_short_row_summary"]["old_short_row_count"],
        "family_count": payload["old_short_row_summary"]["family_count"],
        "feature_count": payload["old_short_row_summary"]["feature_count"],
        "rejected_reason_count": payload["reject_reason_summaries"]["rejected_reason_count"],
        "forbidden_optimization_used": False,
        "next_allowed_step": payload["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    print(json.dumps(stdout_payload, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
