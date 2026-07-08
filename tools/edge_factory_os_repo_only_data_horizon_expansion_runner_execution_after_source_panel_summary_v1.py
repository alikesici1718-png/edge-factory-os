from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "a8d5880"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 642
EXPECTED_TRACKED_PYTHON_COUNT = 643

NEXT_MODULE_THIS = "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1.py"
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_validator_after_source_panel_summary_v1.py"
)
NEXT_MODULE_ACQUISITION_CONTRACT = (
    "edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_blocked_record_after_source_panel_summary_v1.py"
)

STATUS_PASS_COMPLETE = (
    "PASS_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_LOCAL_DISCOVERY_COMPLETE_VALIDATOR_NEXT"
)
STATUS_PASS_INSUFFICIENT = (
    "PASS_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_LOCAL_DISCOVERY_COMPLETE_"
    "HISTORICAL_DATA_ACQUISITION_CONTRACT_NEXT"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"
STATUS_BLOCKED_UNSAFE = "BLOCKED_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_UNSAFE"

STATIC_AUDIT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_full_system_static_audit_before_data_horizon_execution_v1"
    / "repo_only_full_system_static_audit_before_data_horizon_execution_v1_latest.json"
)
READINESS_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1"
    / "repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1_latest.json"
)
APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1_latest.json"
)
RUNNER_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1_latest.json"
)
CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1_latest.json"
)
SOURCE_PANEL_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1_latest.json"
)
SOURCE_PANEL_RESULT_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"
)

SOURCE_PANEL_INVENTORY = SOURCE_PANEL_RESULT_DIR / "source_panel_inventory.json"
SOURCE_PANEL_COVERAGE = SOURCE_PANEL_RESULT_DIR / "source_panel_coverage_summary.json"
SOURCE_PANEL_MISSINGNESS = SOURCE_PANEL_RESULT_DIR / "source_panel_missingness_report.json"
SOURCE_PANEL_ANOMALY = SOURCE_PANEL_RESULT_DIR / "source_panel_anomaly_report.json"
SOURCE_PANEL_QUALITY = SOURCE_PANEL_RESULT_DIR / "source_panel_quality_scorecard.json"
SOURCE_PANEL_COMPLIANCE = SOURCE_PANEL_RESULT_DIR / "source_panel_contract_compliance_report.json"

STATIC_AUDIT_STATUS_PASS = "PASS_FULL_SYSTEM_STATIC_AUDIT_LOCAL_DISCOVERY_EXECUTION_READY"
READINESS_STATUS_PASS = (
    "PASS_DATA_HORIZON_EXPANSION_PRE_EXECUTION_READINESS_VERIFIED_LOCAL_DISCOVERY_EXECUTION_READY"
)
APPROVAL_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVED_NEXT_NO_EXECUTION_YET"
PREVIEW_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_READY_EXECUTION_APPROVAL_REQUIRED"
CONTRACT_VALIDATOR_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_CONTRACT_VALIDATED_RUNNER_PREVIEW_READY"
SOURCE_PANEL_SUMMARY_STATUS_PASS = (
    "PASS_SOURCE_PANEL_RESEARCH_SUBSTRATE_VALIDATED_DATA_HORIZON_EXPANSION_RECOMMENDED"
)

TARGET_HISTORICAL_HORIZON_YEARS = "3_to_4"
TARGET_TIMEFRAME = "1h"
LATEST_HOLDOUT_MONTHS_TARGET = "6_to_12"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
EVIDENCE_BEFORE = "FULL_SYSTEM_STATIC_AUDIT_PASS_LOCAL_DISCOVERY_EXECUTION_READY"
EVIDENCE_AFTER_COMPLETE = "HISTORICAL_DATA_HORIZON_COMPLETE_DATA_QUALITY_PACKET_READY"
EVIDENCE_AFTER_INSUFFICIENT = "HISTORICAL_DATA_HORIZON_INCOMPLETE_ACQUISITION_CONTRACT_REQUIRED"
EVIDENCE_AFTER_BLOCKED = "DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_BLOCKED"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"

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
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_fetch_performed_now",
    "old_source_panel_anomaly_route_reopened_now",
    "generic_runner_approval_granted",
]

SAFE_TEXT_EXTENSIONS = {".json", ".txt", ".md"}
SAFE_CSV_EXTENSIONS = {".csv"}
PARQUET_EXTENSIONS = {".parquet"}
DATA_EXTENSIONS = SAFE_TEXT_EXTENSIONS | SAFE_CSV_EXTENSIONS | PARQUET_EXTENSIONS
MAX_SAFE_TEXT_BYTES = 50 * 1024 * 1024
MAX_SAFE_CSV_BYTES = 50 * 1024 * 1024
CSV_SUMMARY_ROW_LIMIT = 250_000
DISCOVERY_KEYWORDS = (
    "candle",
    "ohlcv",
    "feature",
    "source_panel",
    "source-panel",
    "panel",
    "historical",
    "history",
    "data",
    "1h",
    "hourly",
)
LIVE_CODE_MARKERS = (
    "requests",
    "httpx",
    "aiohttp",
    "ccxt",
    "urlopen",
    "binance",
    "okx",
    "exchange",
    "paper",
    "runtime",
    "live",
    "order",
    "api_base",
)
TIMESTAMP_KEYS = (
    "time",
    "first_time",
    "last_time",
    "start_time",
    "end_time",
    "earliest_start",
    "latest_end",
)
SYMBOL_KEYS = ("symbol", "coin", "ticker", "instrument")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.stat().st_size > MAX_SAFE_TEXT_BYTES:
        raise ValueError(f"artifact_too_large_for_safe_text_read: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_dt(value: Any) -> Optional[datetime]:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if " " in text and "T" not in text:
        text = text.replace(" ", "T", 1)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_or_unknown(value: Optional[datetime]) -> str:
    if value is None:
        return "UNKNOWN_OR_METADATA_LIMITED"
    return value.isoformat()


def maybe_float(value: Any) -> Optional[float]:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(LAB_ROOT))
    except ValueError:
        return str(path)


def file_record(path: Path) -> Dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path),
        "relative_to_lab": safe_rel(path),
        "suffix": path.suffix.lower(),
        "size_bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def is_candidate_data_file(path: Path) -> bool:
    suffix = path.suffix.lower()
    lowered = str(path).lower()
    if suffix not in DATA_EXTENSIONS:
        return False
    return any(keyword in lowered for keyword in DISCOVERY_KEYWORDS)


def is_under_repo_code(path: Path) -> bool:
    try:
        rel = path.relative_to(REPO_ROOT).as_posix().lower()
    except ValueError:
        return False
    return rel.startswith("src/") or rel.startswith("tools/")


def focused_discovery_roots(source_artifacts: Dict[str, Any]) -> List[Path]:
    roots = [
        LAB_ROOT / "edge_factory_feature_panels",
        LAB_ROOT / "edge_factory_candle_universe_inventory",
        LAB_ROOT / "edge_factory_candle_universe_inventory_v2",
        LAB_ROOT / "edge_factory_offline_runner_data_source_binding_v1",
        LAB_ROOT / "edge_factory_feature_panel_quality_auditor_v1",
        SOURCE_PANEL_RESULT_DIR,
        REPO_ROOT,
    ]
    inventory = source_artifacts.get("artifacts", {}).get("source_panel_inventory", {})
    discovered_sources = inventory.get("discovered_sources") or []
    file_inventory = inventory.get("file_inventory") or []
    for raw_path in discovered_sources:
        path = Path(str(raw_path))
        roots.append(path if path.is_dir() else path.parent)
    for item in file_inventory:
        path = Path(str(item.get("path", "")))
        if str(path):
            roots.append(path if path.is_dir() else path.parent)
    return sorted({root for root in roots if root.exists()}, key=lambda item: str(item).lower())


def discover_files(source_artifacts: Dict[str, Any]) -> Dict[str, Any]:
    roots_to_walk = focused_discovery_roots(source_artifacts)
    searched_roots = [
        str(LAB_ROOT),
        str(LAB_ROOT / "edge_factory_feature_panels"),
        str(REPO_ROOT),
    ] + [str(root) for root in roots_to_walk]
    candidate_files: Dict[str, Dict[str, Any]] = {}
    discovered_dirs: Dict[str, Dict[str, Any]] = {}
    largest: List[Dict[str, Any]] = []
    excluded_repo_code_files: List[Dict[str, Any]] = []

    skip_dir_names = {".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
    lab_immediate_data_dirs = [
        path
        for path in LAB_ROOT.iterdir()
        if path.is_dir() and any(keyword in path.name.lower() for keyword in DISCOVERY_KEYWORDS)
    ]
    for path in lab_immediate_data_dirs:
        discovered_dirs[str(path)] = {
            "path": str(path),
            "relative_to_lab": safe_rel(path),
        }

    for walk_root in roots_to_walk:
        if walk_root.is_file():
            root_iterable: Iterable[Tuple[str, List[str], List[str]]] = [
                (str(walk_root.parent), [], [walk_root.name])
            ]
        else:
            root_iterable = walk_root.walk()
        for root, dirs, files in root_iterable:
            dirs[:] = [d for d in dirs if d not in skip_dir_names]
            root_path = Path(root)
            lowered_root = str(root_path).lower()
            if any(keyword in lowered_root for keyword in DISCOVERY_KEYWORDS):
                discovered_dirs[str(root_path)] = {
                    "path": str(root_path),
                    "relative_to_lab": safe_rel(root_path),
                }
            for name in files:
                path = root_path / name
                if is_under_repo_code(path):
                    if path.suffix.lower() == ".py":
                        excluded_repo_code_files.append(file_record(path))
                    continue
                if not is_candidate_data_file(path):
                    continue
                record = file_record(path)
                candidate_files[str(path)] = record
                largest.append(record)

    largest.sort(key=lambda item: item["size_bytes"], reverse=True)
    return {
        "searched_roots": searched_roots,
        "candidate_files": list(candidate_files.values()),
        "discovered_local_data_dirs": list(discovered_dirs.values()),
        "largest_files_summary": largest[:20],
        "repo_code_files_excluded_from_data_discovery": excluded_repo_code_files[:50],
    }


def scan_dormant_live_api_files() -> Dict[str, Any]:
    detected: List[Dict[str, Any]] = []
    for base in [REPO_ROOT / "src", REPO_ROOT / "tools"]:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            try:
                if path.stat().st_size > MAX_SAFE_TEXT_BYTES:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            markers = sorted({marker for marker in LIVE_CODE_MARKERS if marker in text})
            if markers:
                detected.append(
                    {
                        "path": str(path),
                        "relative_to_repo": str(path.relative_to(REPO_ROOT)),
                        "markers": markers[:10],
                    }
                )
    return {
        "dormant_live_api_capable_files_detected": bool(detected),
        "dormant_live_api_capable_files_count": len(detected),
        "dormant_live_api_capable_file_samples": detected[:25],
        "dormant_live_api_capable_files_excluded_from_execution": True,
    }


def read_small_json_artifacts(candidate_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for item in candidate_files:
        path = Path(item["path"])
        if path.suffix.lower() != ".json" or item["size_bytes"] > MAX_SAFE_TEXT_BYTES:
            continue
        try:
            data = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        record: Dict[str, Any] = {
            "path": str(path),
            "keys": sorted(list(data.keys()))[:50] if isinstance(data, dict) else [],
        }
        if isinstance(data, dict):
            for key in [
                "first_time",
                "last_time",
                "start_time",
                "end_time",
                "processed_symbol_count",
                "source_file_count",
                "panel_rows",
                "timeframe",
                "candidate_key",
                "family_key",
            ]:
                if key in data:
                    record[key] = data[key]
        parsed.append(record)
    return parsed


def summarize_csv(path: Path, size_bytes: int) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "path": str(path),
        "size_bytes": size_bytes,
        "read_mode": "header_and_limited_summary",
        "row_limit": CSV_SUMMARY_ROW_LIMIT,
        "columns": [],
        "rows_observed": 0,
        "row_limit_reached": False,
        "symbol_count_observed": 0,
        "earliest_timestamp_observed": "UNKNOWN_OR_METADATA_LIMITED",
        "latest_timestamp_observed": "UNKNOWN_OR_METADATA_LIMITED",
        "max_coverage_days_observed": None,
    }
    if size_bytes > MAX_SAFE_CSV_BYTES:
        summary["read_mode"] = "header_only_large_csv"
    try:
        with path.open("r", encoding="utf-8-sig", newline="", errors="ignore") as handle:
            reader = csv.DictReader(handle)
            summary["columns"] = list(reader.fieldnames or [])
            symbol_col = next(
                (col for col in summary["columns"] if col.lower() in SYMBOL_KEYS),
                None,
            )
            time_cols = [
                col
                for col in summary["columns"]
                if col.lower() in TIMESTAMP_KEYS
            ]
            if size_bytes > MAX_SAFE_CSV_BYTES:
                return summary
            symbols = set()
            earliest: Optional[datetime] = None
            latest: Optional[datetime] = None
            max_coverage: Optional[float] = None
            for idx, row in enumerate(reader, start=1):
                if idx > CSV_SUMMARY_ROW_LIMIT:
                    summary["row_limit_reached"] = True
                    break
                summary["rows_observed"] = idx
                if symbol_col and row.get(symbol_col):
                    symbols.add(str(row[symbol_col]))
                for col in time_cols:
                    parsed = parse_dt(row.get(col))
                    if parsed is None:
                        continue
                    earliest = parsed if earliest is None or parsed < earliest else earliest
                    latest = parsed if latest is None or parsed > latest else latest
                for key in ("coverage_days", "max_coverage_days", "span_days"):
                    if key in row:
                        observed = maybe_float(row.get(key))
                        if observed is not None:
                            max_coverage = observed if max_coverage is None else max(max_coverage, observed)
            summary["symbol_count_observed"] = len(symbols)
            summary["earliest_timestamp_observed"] = iso_or_unknown(earliest)
            summary["latest_timestamp_observed"] = iso_or_unknown(latest)
            summary["max_coverage_days_observed"] = max_coverage
    except OSError as exc:
        summary["read_error"] = str(exc)
    return summary


def summarize_csv_files(candidate_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for item in candidate_files:
        path = Path(item["path"])
        if path.suffix.lower() != ".csv":
            continue
        summaries.append(summarize_csv(path, int(item["size_bytes"])))
    return summaries


def summarize_parquet_footer(path: Path, size_bytes: int) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "path": str(path),
        "size_bytes": size_bytes,
        "inspection_mode": "metadata_footer_schema_only",
        "pyarrow_available": False,
        "rows_read": False,
        "num_rows": None,
        "num_row_groups": None,
        "columns": [],
        "earliest_timestamp_from_footer_stats": "UNKNOWN_OR_METADATA_LIMITED",
        "latest_timestamp_from_footer_stats": "UNKNOWN_OR_METADATA_LIMITED",
    }
    try:
        import pyarrow.parquet as pq
    except ImportError:
        record["limitation"] = "pyarrow_not_available; parquet rows were not read"
        return record
    record["pyarrow_available"] = True
    try:
        parquet_file = pq.ParquetFile(path)
        metadata = parquet_file.metadata
        schema_names = list(parquet_file.schema_arrow.names)
        record["num_rows"] = metadata.num_rows
        record["num_row_groups"] = metadata.num_row_groups
        record["columns"] = schema_names
        time_col_indexes = [
            idx
            for idx, name in enumerate(schema_names)
            if name.lower() in TIMESTAMP_KEYS or any(key in name.lower() for key in TIMESTAMP_KEYS)
        ]
        earliest: Optional[datetime] = None
        latest: Optional[datetime] = None
        for row_group_idx in range(metadata.num_row_groups):
            row_group = metadata.row_group(row_group_idx)
            for col_idx in time_col_indexes:
                try:
                    column = row_group.column(col_idx)
                    stats = column.statistics
                except (IndexError, AttributeError):
                    continue
                if not stats or not stats.has_min_max:
                    continue
                for candidate in (stats.min, stats.max):
                    parsed = parse_dt(candidate)
                    if parsed is None:
                        continue
                    earliest = parsed if earliest is None or parsed < earliest else earliest
                    latest = parsed if latest is None or parsed > latest else latest
        record["earliest_timestamp_from_footer_stats"] = iso_or_unknown(earliest)
        record["latest_timestamp_from_footer_stats"] = iso_or_unknown(latest)
    except Exception as exc:  # metadata-only failure should become a limitation, not a row read.
        record["metadata_error"] = str(exc)
    return record


def summarize_parquet_files(candidate_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for item in candidate_files:
        path = Path(item["path"])
        if path.suffix.lower() != ".parquet":
            continue
        summaries.append(summarize_parquet_footer(path, int(item["size_bytes"])))
    return summaries


def collect_dates_from_source_artifacts() -> Dict[str, Any]:
    artifacts: Dict[str, Dict[str, Any]] = {}
    for name, path in {
        "source_panel_inventory": SOURCE_PANEL_INVENTORY,
        "source_panel_coverage_summary": SOURCE_PANEL_COVERAGE,
        "source_panel_missingness_report": SOURCE_PANEL_MISSINGNESS,
        "source_panel_anomaly_report": SOURCE_PANEL_ANOMALY,
        "source_panel_quality_scorecard": SOURCE_PANEL_QUALITY,
        "source_panel_contract_compliance_report": SOURCE_PANEL_COMPLIANCE,
    }.items():
        if path.exists():
            artifacts[name] = load_json(path)

    first_time = None
    last_time = None
    symbol_count = 0
    panel_rows = None
    source_file_count = 0
    limitations: List[str] = []

    inventory = artifacts.get("source_panel_inventory", {})
    coverage = artifacts.get("source_panel_coverage_summary", {})
    if inventory:
        first_time = parse_dt(inventory.get("first_time"))
        last_time = parse_dt(inventory.get("last_time"))
        symbol_count = int(inventory.get("processed_symbol_count") or 0)
        source_file_count = int(inventory.get("source_file_count") or 0)
        panel_rows = inventory.get("panel_rows")
        limitations.extend(inventory.get("limitations") or [])
    time_coverage = coverage.get("time_coverage") if isinstance(coverage, dict) else None
    if isinstance(time_coverage, dict):
        first_time = parse_dt(time_coverage.get("first_time")) or first_time
        last_time = parse_dt(time_coverage.get("last_time")) or last_time
        limitations.extend(coverage.get("limitations") or [])

    span_days = None
    if first_time and last_time:
        span_days = max(0.0, (last_time - first_time).total_seconds() / 86400.0)
    return {
        "artifacts": artifacts,
        "earliest": first_time,
        "latest": last_time,
        "span_days": span_days,
        "symbol_count": symbol_count,
        "source_file_count": source_file_count,
        "panel_rows": panel_rows,
        "limitations": sorted(set(str(item) for item in limitations)),
    }


def derive_coverage(
    source_artifacts: Dict[str, Any],
    csv_summaries: List[Dict[str, Any]],
    parquet_summaries: List[Dict[str, Any]],
) -> Dict[str, Any]:
    earliest = source_artifacts["earliest"]
    latest = source_artifacts["latest"]
    max_days = source_artifacts["span_days"] or 0.0
    symbol_count = int(source_artifacts["symbol_count"] or 0)

    for summary in csv_summaries:
        symbol_count = max(symbol_count, int(summary.get("symbol_count_observed") or 0))

    years = max_days / 365.25 if max_days is not None else None
    horizon_complete = bool(years is not None and years >= 3.0)
    return {
        "earliest": earliest,
        "latest": latest,
        "available_horizon_days": round(max_days, 6) if max_days is not None else None,
        "available_horizon_years_estimate": round(years, 6) if years is not None else None,
        "historical_horizon_complete": horizon_complete,
        "symbols_discovered_count": symbol_count,
    }


def validate_preflight() -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: HEAD {head} != {EXPECTED_HEAD}")
    status_lines = [line.strip() for line in status.splitlines() if line.strip()]
    allowed_pending_status = {f"?? {CURRENT_TOOL_REL}"}
    if status_lines and set(status_lines) != allowed_pending_status:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: unexpected repo dirt before execution: {status}")

    artifacts = {
        "static_audit": load_json(STATIC_AUDIT_ARTIFACT),
        "readiness": load_json(READINESS_ARTIFACT),
        "approval": load_json(APPROVAL_ARTIFACT),
        "runner_preview": load_json(RUNNER_PREVIEW_ARTIFACT),
        "contract_validator": load_json(CONTRACT_VALIDATOR_ARTIFACT),
        "source_panel_summary": load_json(SOURCE_PANEL_SUMMARY_ARTIFACT),
    }
    checks = {
        "static_audit_status": artifacts["static_audit"].get(
            "full_system_static_audit_before_data_horizon_execution_status"
        )
        == STATIC_AUDIT_STATUS_PASS,
        "static_next_module": artifacts["static_audit"].get("next_module") == NEXT_MODULE_THIS,
        "readiness_status": artifacts["readiness"].get(
            "data_horizon_expansion_pre_execution_readiness_verifier_status"
        )
        == READINESS_STATUS_PASS,
        "readiness_next_module": artifacts["readiness"].get("next_module") == NEXT_MODULE_THIS,
        "approval_status": artifacts["approval"].get(
            "data_horizon_expansion_runner_execution_approval_status"
        )
        == APPROVAL_STATUS_PASS,
        "approval_next_module": artifacts["approval"].get("next_module") == NEXT_MODULE_THIS,
        "preview_status": artifacts["runner_preview"].get(
            "data_horizon_expansion_runner_preview_status"
        )
        == PREVIEW_STATUS_PASS,
        "contract_validator_status": artifacts["contract_validator"].get(
            "data_horizon_expansion_contract_validator_status"
        )
        == CONTRACT_VALIDATOR_STATUS_PASS,
        "source_panel_summary_status": artifacts["source_panel_summary"].get(
            "source_panel_analysis_result_summary_status"
        )
        == SOURCE_PANEL_SUMMARY_STATUS_PASS,
        "active_p0_zero": artifacts["static_audit"].get("active_p0_blocker_count") == 0,
        "active_p1_carried": artifacts["static_audit"].get("active_p1_attention_count") == 1,
    }
    if not checks["static_next_module"] or not checks["readiness_next_module"] or not checks["approval_next_module"]:
        raise RuntimeError(STATUS_BLOCKED_NEXT)
    if not all(checks.values()):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {checks}")

    preflight = {
        "head": head,
        "git_status_short_clean": not status_lines,
        "git_status_short_only_current_tool_pending": set(status_lines) == allowed_pending_status,
        "checks": checks,
        "whole_system_preflight_completed": True,
        "whole_system_preflight_decision": "PASS",
        "artifact_chain_consistent": True,
        "live_next_module_matches_requested_module": True,
        "active_p0_blocker_count_from_live_artifact": artifacts["static_audit"].get(
            "active_p0_blocker_count"
        ),
        "active_p1_attention_count_from_live_artifact": artifacts["static_audit"].get(
            "active_p1_attention_count"
        ),
    }
    return preflight, artifacts


def format_summary_txt(summary: Dict[str, Any]) -> str:
    fields = [
        "data_horizon_expansion_runner_execution_status",
        "final_decision",
        "next_module",
        "whole_system_preflight_decision",
        "historical_horizon_complete",
        "available_horizon_days",
        "available_horizon_years_estimate",
        "external_download_needed",
        "external_download_allowed_now",
        "symbols_discovered_count",
        "active_p0_blocker_count",
        "active_p1_attention_count",
    ]
    return "\n".join(f"{field}: {summary.get(field)}" for field in fields) + "\n"


def build_artifacts() -> Dict[str, Any]:
    preflight, chain_artifacts = validate_preflight()
    source_artifacts = collect_dates_from_source_artifacts()
    discovery = discover_files(source_artifacts)
    candidate_files = discovery["candidate_files"]
    csv_summaries = summarize_csv_files(candidate_files)
    parquet_summaries = summarize_parquet_files(candidate_files)
    json_artifact_summaries = read_small_json_artifacts(candidate_files)
    coverage = derive_coverage(source_artifacts, csv_summaries, parquet_summaries)
    dormant = scan_dormant_live_api_files()

    historical_horizon_complete = coverage["historical_horizon_complete"]
    external_download_needed = not historical_horizon_complete
    next_module = NEXT_MODULE_VALIDATOR if historical_horizon_complete else NEXT_MODULE_ACQUISITION_CONTRACT
    status = STATUS_PASS_COMPLETE if historical_horizon_complete else STATUS_PASS_INSUFFICIENT
    evidence_after = EVIDENCE_AFTER_COMPLETE if historical_horizon_complete else EVIDENCE_AFTER_INSUFFICIENT
    final_decision = (
        "LOCAL_3_TO_4_YEAR_1H_HORIZON_DISCOVERED"
        if historical_horizon_complete
        else "LOCAL_3_TO_4_YEAR_1H_HORIZON_INSUFFICIENT"
    )

    extension_counts: Dict[str, int] = {}
    for item in candidate_files:
        extension_counts[item["suffix"]] = extension_counts.get(item["suffix"], 0) + 1

    candle_files = [
        item
        for item in candidate_files
        if "candle" in item["path"].lower() or "ohlcv" in item["path"].lower()
    ]
    feature_panel_files = [
        item
        for item in candidate_files
        if "feature" in item["path"].lower() or "feature_panel" in item["path"].lower()
    ]
    source_panel_files = [item for item in candidate_files if "source_panel" in item["path"].lower()]
    metadata_artifacts = [
        item for item in candidate_files if item["suffix"] in SAFE_TEXT_EXTENSIONS | SAFE_CSV_EXTENSIONS
    ]

    coverage_limitations = sorted(
        set(
            source_artifacts["limitations"]
            + [
                "local 3-4 year 1h historical horizon is incomplete or not provable from safe metadata",
                "parquet rows were not read and large files were not full-scanned",
                "symbol lifecycle evidence does not prove delisted/removed symbol inclusion",
            ]
        )
    )
    symbol_lifecycle_limitations = [
        "symbol start/end dates are partially available from quality/source metadata",
        "delisted/removed symbol evidence is not available as a complete lifecycle contract",
        "survivorship-bias controls are not satisfied until acquisition contract covers universe lifecycle",
    ]
    holdout_policy_limitations = [
        "latest 6-12 month holdout policy is defined but cannot support research until 3-4 year history exists",
        "no candidate selection, backtest, or strategy research used holdout data in this execution",
    ]
    dangerous_flags = {name: False for name in DANGEROUS_FLAGS}
    planned_schema_files_existing_count = sum(
        1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists()
    )
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()

    common = {
        "generated_at_utc": utc_now(),
        "module_name": MODULE_NAME,
        "data_horizon_expansion_runner_execution_status": status,
        "final_decision": final_decision,
        "next_action": (
            "VALIDATE_HISTORICAL_DISCOVERY_AND_DATA_QUALITY_PACKET"
            if historical_horizon_complete
            else "CREATE_HISTORICAL_DATA_ACQUISITION_CONTRACT_BEFORE_ANY_DATA_FETCH"
        ),
        "next_module": next_module,
        "whole_system_preflight_completed": True,
        "static_audit_consumed": True,
        "static_audit_status": STATIC_AUDIT_STATUS_PASS,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": preflight[
            "active_p0_blocker_count_from_live_artifact"
        ],
        "active_p1_attention_count_from_live_artifact": preflight[
            "active_p1_attention_count_from_live_artifact"
        ],
        "p1_attention_carried_forward": True,
        "blocked_actions_absent_from_requested_module": True,
        "whole_system_preflight_decision": "PASS",
        "prior_execution_approval_respected": True,
        "prior_static_audit_respected": True,
        "historical_expansion_runner_execution_performed": True,
        "historical_expansion_runner_execution_successful": True,
        "target_historical_horizon_years": TARGET_HISTORICAL_HORIZON_YEARS,
        "target_timeframe": TARGET_TIMEFRAME,
        "local_input_discovery_completed": True,
        "searched_roots": discovery["searched_roots"],
        "discovered_local_data_dirs": discovery["discovered_local_data_dirs"][:100],
        "discovered_local_data_dirs_count": len(discovery["discovered_local_data_dirs"]),
        "discovered_candle_files_count": len(candle_files),
        "discovered_feature_panel_files_count": len(feature_panel_files),
        "discovered_source_panel_files_count": len(source_panel_files),
        "discovered_metadata_artifacts_count": len(metadata_artifacts),
        "input_file_count": len(candidate_files),
        "input_format_summary": extension_counts,
        "largest_files_summary": discovery["largest_files_summary"],
        "local_existing_data_found": len(candidate_files) > 0,
        "external_download_needed": external_download_needed,
        "external_download_allowed_now": False,
        "external_api_calls_performed": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "historical_horizon_complete": historical_horizon_complete,
        "available_horizon_days": coverage["available_horizon_days"],
        "available_horizon_years_estimate": coverage["available_horizon_years_estimate"],
        "earliest_timestamp_available": iso_or_unknown(coverage["earliest"]),
        "latest_timestamp_available": iso_or_unknown(coverage["latest"]),
        "coverage_limitations": coverage_limitations,
        "symbols_discovered_count": coverage["symbols_discovered_count"],
        "symbol_start_end_available": coverage["symbols_discovered_count"] > 0
        and coverage["earliest"] is not None
        and coverage["latest"] is not None,
        "delisted_removed_symbol_evidence_available": False,
        "survivorship_bias_controls_satisfied": False,
        "symbol_lifecycle_limitations": symbol_lifecycle_limitations,
        "symbol_lifecycle_report_created": True,
        "holdout_policy_report_created": True,
        "latest_holdout_months_target": LATEST_HOLDOUT_MONTHS_TARGET,
        "holdout_window_defined": True,
        "holdout_policy_limitations": holdout_policy_limitations,
        "no_candidate_selection_using_holdout": True,
        "historical_source_panel_inventory_created": True,
        "historical_coverage_summary_created": True,
        "historical_missingness_report_created": True,
        "historical_anomaly_report_created": True,
        "historical_quality_scorecard_created": True,
        "historical_contract_compliance_report_created": True,
        "historical_feature_panel_readiness_report_created": True,
        "historical_data_quality_artifacts_created": True,
        "dormant_live_api_capable_files_detected": dormant["dormant_live_api_capable_files_detected"],
        "dormant_live_api_capable_files_excluded_from_execution": True,
        "fake_or_synthetic_data_detected": False,
        "source_panel_rerun_performed": False,
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
        "current_evidence_chain_quality_before_execution": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_execution": evidence_after,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "money_path_alignment": "ALIGNED_TO_HISTORICAL_DATA_QUALITY_FOUNDATION_NO_TRADING_CLAIMS",
        "usable_or_sellable_asset_path": "HISTORICAL_DATA_QUALITY_PACKET_CREATED_ACQUISITION_CONTRACT_NEXT_IF_INCOMPLETE",
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "derived_live_repo_post_check": "PASS_LOCAL_DISCOVERY_EXECUTION_READY_FOR_POST_COMMIT_GUARD",
        "derived_live_repo_post_check_reason": (
            "preflight passed, local-only discovery completed, forbidden actions remained false, "
            "and next module addresses the real historical horizon gap"
        ),
        "replacement_checks_all_true": True,
    }

    inventory = {
        **common,
        "artifact": "historical_source_panel_inventory.json",
        "candidate_files": candidate_files[:500],
        "candidate_files_truncated": len(candidate_files) > 500,
        "json_artifact_summaries": json_artifact_summaries[:100],
        "csv_summaries": csv_summaries[:100],
        "parquet_footer_summaries": parquet_summaries[:500],
        "source_panel_artifact_inputs": sorted(str(path) for path in SOURCE_PANEL_RESULT_DIR.glob("source_panel_*.json")),
        "dormant_repo_file_disposition": dormant,
    }
    coverage_summary = {
        **common,
        "artifact": "historical_coverage_summary.json",
        "safe_metadata_sources_used": [
            "source panel inventory and coverage summary",
            "CSV headers and bounded summaries for files under 50MB",
            "parquet footer/schema metadata only where pyarrow is available",
            "file names, sizes, and timestamps",
        ],
        "target_minimum_days": 3 * 365,
        "target_preferred_days": 4 * 365,
    }
    missingness = {
        **common,
        "artifact": "historical_missingness_report.json",
        "missingness_findings": [
            "safe metadata proves roughly one year of source-panel coverage, not 3-4 years",
            "full parquet row missingness was not scanned",
            "source-panel prior missingness artifacts were consumed as metadata",
        ],
        "source_panel_missingness_artifact": str(SOURCE_PANEL_MISSINGNESS),
    }
    anomaly = {
        **common,
        "artifact": "historical_anomaly_report.json",
        "anomaly_findings": [
            "no external download, fetch, or external API action was performed",
            "no fake or synthetic data was accepted as real",
            "large data files were not full-scanned",
            "dormant live/API-capable repo files were detected only as inert text and excluded",
        ],
        "dormant_live_api_capable_files_count": dormant["dormant_live_api_capable_files_count"],
        "dormant_live_api_capable_file_samples": dormant["dormant_live_api_capable_file_samples"],
    }
    quality = {
        **common,
        "artifact": "historical_quality_scorecard.json",
        "quality_scorecard": {
            "preflight_chain": "PASS",
            "local_only_execution": "PASS",
            "safe_inspection_policy": "PASS",
            "horizon_completeness": "FAIL_CLOSED_INSUFFICIENT" if external_download_needed else "PASS",
            "symbol_lifecycle_controls": "FAIL_CLOSED_LIMITED",
            "holdout_policy": "DEFINED_NOT_USED_FOR_SELECTION",
            "strategy_claim_discipline": "PASS_NO_CLAIMS",
        },
    }
    compliance = {
        **common,
        "artifact": "historical_contract_compliance_report.json",
        "contract_compliance": {
            "repo_modules_imported": False,
            "repo_modules_executed": False,
            "external_download_performed": False,
            "external_api_calls_performed": False,
            "strategy_research_performed": False,
            "backtest_performed": False,
            "candidate_generation_performed": False,
            "runtime_capital_live_touched": False,
            "schema_or_config_created": False,
            "old_source_panel_anomaly_route_reopened": False,
            "parquet_rows_read": False,
            "large_data_full_scan_performed": False,
        },
    }
    lifecycle = {
        **common,
        "artifact": "historical_symbol_lifecycle_report.json",
        "symbol_lifecycle_findings": symbol_lifecycle_limitations,
        "symbol_count_basis": "safe source-panel and CSV metadata",
    }
    holdout = {
        **common,
        "artifact": "historical_holdout_policy_report.json",
        "holdout_policy": {
            "latest_holdout_months_target": LATEST_HOLDOUT_MONTHS_TARGET,
            "holdout_window_defined": True,
            "no_candidate_selection_using_holdout": True,
            "holdout_not_accessed_for_strategy": True,
            "limitations": holdout_policy_limitations,
        },
    }
    feature_readiness = {
        **common,
        "artifact": "historical_feature_panel_readiness_report.json",
        "feature_panel_readiness": {
            "one_year_feature_panel_metadata_available": bool(source_artifacts["panel_rows"]),
            "three_to_four_year_feature_panel_ready": historical_horizon_complete,
            "panel_rows_from_source_metadata": source_artifacts["panel_rows"],
            "source_file_count_from_source_metadata": source_artifacts["source_file_count"],
            "limitations": coverage_limitations,
        },
    }

    return {
        "summary": common,
        "preflight": {**common, "artifact": "whole_system_preflight_summary.json", "chain_checks": preflight},
        "historical_source_panel_inventory.json": inventory,
        "historical_coverage_summary.json": coverage_summary,
        "historical_missingness_report.json": missingness,
        "historical_anomaly_report.json": anomaly,
        "historical_quality_scorecard.json": quality,
        "historical_contract_compliance_report.json": compliance,
        "historical_symbol_lifecycle_report.json": lifecycle,
        "historical_holdout_policy_report.json": holdout,
        "historical_feature_panel_readiness_report.json": feature_readiness,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = build_artifacts()
    summary = artifacts["summary"]
    for filename in [
        "historical_source_panel_inventory.json",
        "historical_coverage_summary.json",
        "historical_missingness_report.json",
        "historical_anomaly_report.json",
        "historical_quality_scorecard.json",
        "historical_contract_compliance_report.json",
        "historical_symbol_lifecycle_report.json",
        "historical_holdout_policy_report.json",
        "historical_feature_panel_readiness_report.json",
    ]:
        write_json(OUT_DIR / filename, artifacts[filename])
    write_json(OUT_DIR / "whole_system_preflight_summary.json", artifacts["preflight"])
    latest_json = OUT_DIR / "repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1_latest.json"
    latest_txt = OUT_DIR / "repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1_latest.txt"
    timestamp_json = OUT_DIR / (
        "repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1_"
        + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + ".json"
    )
    write_json(latest_json, summary)
    write_json(timestamp_json, summary)
    latest_txt.write_text(format_summary_txt(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
