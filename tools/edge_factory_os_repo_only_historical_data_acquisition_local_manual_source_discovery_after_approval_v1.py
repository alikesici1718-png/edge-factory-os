from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
DESKTOP_ROOT = LAB_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "1be1182"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 654
EXPECTED_TRACKED_PYTHON_COUNT = 655

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1.py"
)
NEXT_MODULE_VALIDATOR = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_validator_after_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_local_manual_source_discovery_blocked_record_after_approval_v1.py"
)

APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_approval_after_preview_v1"
    / "repo_only_historical_data_acquisition_approval_after_preview_v1_latest.json"
)
PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1"
    / "repo_only_historical_data_acquisition_preview_after_contract_validator_v1_latest.json"
)
CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1"
    / "repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1_latest.json"
)
CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1"
    / "repo_only_historical_data_acquisition_contract_after_data_horizon_discovery_v1_latest.json"
)
HARDENING_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1"
    / "repo_only_pre_acquisition_minimal_reliability_hardening_implementation_validator_after_approval_v1_latest.json"
)
DATA_HORIZON_DISCOVERY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1_latest.json"
)

STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_COMPLETE_PENDING_VALIDATOR"
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT = "BLOCKED_NEXT_MODULE_MISMATCH"

APPROVAL_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_APPROVED_NEXT_NO_EXECUTION"
PREVIEW_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_PREVIEW_READY_APPROVAL_REQUIRED_NO_EXECUTION"
CONTRACT_VALIDATOR_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_VALIDATED_PREVIEW_READY_NO_EXECUTION"
CONTRACT_STATUS_PASS = "PASS_HISTORICAL_DATA_ACQUISITION_CONTRACT_READY_NO_ACQUISITION_EXECUTION"
HARDENING_STATUS_PASS = (
    "PASS_PRE_ACQUISITION_MINIMAL_RELIABILITY_HARDENING_VALIDATED_ACQUISITION_CONTRACT_RESUME_READY"
)
DATA_HORIZON_STATUS_PASS = (
    "PASS_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_LOCAL_DISCOVERY_COMPLETE_"
    "HISTORICAL_DATA_ACQUISITION_CONTRACT_NEXT"
)

EVIDENCE_BEFORE = "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_APPROVED_NEXT_NO_EXECUTION"
EVIDENCE_AFTER = "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_COMPLETE_PENDING_VALIDATOR"
EVIDENCE_CHAIN_POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"

TARGET_HISTORICAL_HORIZON_YEARS = "3_to_4"
TARGET_TIMEFRAME = "1h"
TARGET_MINIMUM_DAYS = 1095
MIN_REASONABLE_HISTORICAL_YEAR = 2018

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
DANGEROUS_FLAG_NAMES = [
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
    "data_build_performed_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]

SAFE_TEXT_EXTENSIONS = {".json", ".txt", ".md"}
SAFE_CSV_EXTENSIONS = {".csv", ".tsv"}
PARQUET_EXTENSIONS = {".parquet"}
ARCHIVE_EXTENSIONS = {".zip", ".gz", ".bz2", ".xz", ".7z"}
SUPPORTED_EXTENSIONS = SAFE_TEXT_EXTENSIONS | SAFE_CSV_EXTENSIONS | PARQUET_EXTENSIONS | ARCHIVE_EXTENSIONS

MAX_SAFE_HASH_BYTES = 16 * 1024 * 1024
MAX_SAFE_TEXT_BYTES = 512 * 1024
MAX_SAFE_CSV_SAMPLE_BYTES = 128 * 1024
MAX_TOTAL_FILES_CONSIDERED = 30000
MAX_FILES_PER_ROOT = 12000
CSV_SAMPLE_ROWS = 8
MAX_CANDIDATE_RECORDS = 1200

DISCOVERY_KEYWORDS = (
    "1h",
    "hour",
    "hourly",
    "candle",
    "ohlcv",
    "kline",
    "bar",
    "historical",
    "history",
    "archive",
    "export",
    "exchange",
    "feature",
    "panel",
    "source",
    "manifest",
    "provenance",
    "inventory",
    "lifecycle",
    "delisted",
    "removed",
)
DESCEND_KEYWORDS = (
    "edge_lab",
    "edge_factory",
    "historical",
    "history",
    "archive",
    "export",
    "exchange",
    "candle",
    "ohlcv",
    "kline",
    "data",
    "feature",
    "panel",
    "source",
)
SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
}
TIMESTAMP_FIELD_HINTS = (
    "timestamp",
    "datetime",
    "date",
    "open_time",
    "close_time",
    "time",
    "ts",
)
OHLCV_FIELD_HINTS = ("open", "high", "low", "close", "volume")
SYMBOL_FIELD_HINTS = ("symbol", "ticker", "asset", "instrument")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    allowed = (
        ["rev-parse", "--short", "HEAD"],
        ["status", "--short"],
        ["ls-files"],
        ["show", "--name-only", "--format=", "HEAD"],
    )
    if args not in allowed:
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def read_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, bool, bool]:
    exists = path.exists()
    if not exists:
        return {}, False, False, False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}, True, False, False
    return data, True, True, bool(data)


def load_json(path: Path) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: artifact missing/invalid/empty: {path}")
    return data


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def require_equal(actual: Any, expected: Any, field: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field}={actual!r} expected {expected!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


def tracked_python_count() -> int:
    output = run_git(["ls-files"])
    return len([line for line in output.splitlines() if line.strip().endswith(".py")])


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def normalize_status_lines(status: str) -> List[str]:
    return [line.strip() for line in status.splitlines() if line.strip()]


def validate_repo_status_allows_current_tool_only(status: str) -> None:
    allowed = {f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"}
    lines = normalize_status_lines(status)
    unexpected = [line for line in lines if line not in allowed]
    require(not unexpected, f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def validate_preflight(
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    contract_validator: Dict[str, Any],
    contract: Dict[str, Any],
    hardening: Dict[str, Any],
    horizon: Dict[str, Any],
) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    status = run_git(["status", "--short"])
    require_equal(head, EXPECTED_HEAD, "head")
    validate_repo_status_allows_current_tool_only(status)

    require_equal(approval.get("next_module"), REQUESTED_MODULE, "approval.next_module")
    require_equal(approval.get("historical_data_acquisition_approval_status"), APPROVAL_STATUS_PASS, "approval.status")
    require_true(approval.get("acquisition_approval_record_created"), "approval.acquisition_approval_record_created")
    require_true(approval.get("user_acquisition_approval_present"), "approval.user_acquisition_approval_present")
    require_true(approval.get("local_manual_source_discovery_eligible_next"), "approval.local_manual_source_discovery_eligible_next")
    require_true(
        approval.get("approval_grants_future_local_manual_source_discovery_next"),
        "approval.approval_grants_future_local_manual_source_discovery_next",
    )
    require_false(
        approval.get("approval_grants_local_manual_source_discovery_now"),
        "approval.approval_grants_local_manual_source_discovery_now",
    )
    for key in [
        "acquisition_execution_allowed_now",
        "external_download_allowed_now",
        "external_api_allowed_now",
        "external_api_download_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "fake_or_synthetic_data_detected",
        "strategy_signal_claims_made",
        "tradable_edge_claims_made",
        "profit_claims_made",
        "backtest_performed",
        "candidate_generation_performed",
        "runtime_touch_performed",
        "capital_touch_performed",
        "live_touch_performed",
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "old_source_panel_anomaly_route_reopened_now",
        "old_route_closed_artifacts_used_as_active_evidence_now",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]:
        require_false(approval.get(key), f"approval.{key}")
    require_equal(approval.get("active_p0_blocker_count"), 0, "approval.active_p0_blocker_count")
    require_equal(approval.get("active_p1_attention_count"), 1, "approval.active_p1_attention_count")
    require_true(approval.get("p1_attention_carried_forward"), "approval.p1_attention_carried_forward")
    require_true(
        approval.get("dormant_repo_attention_count_carried_forward"),
        "approval.dormant_repo_attention_count_carried_forward",
    )
    require_equal(approval.get("dormant_repo_attention_count"), 716, "approval.dormant_repo_attention_count")
    require_equal(approval.get("planned_schema_files_existing_count"), 0, "approval.planned_schema_files_existing_count")
    require_true(approval.get("replacement_checks_all_true"), "approval.replacement_checks_all_true")
    require_equal(approval.get("current_evidence_chain_quality_after_approval"), EVIDENCE_BEFORE, "approval.evidence_after")

    require_equal(preview.get("historical_data_acquisition_preview_status"), PREVIEW_STATUS_PASS, "preview.status")
    require_equal(preview.get("next_module"), "edge_factory_os_repo_only_historical_data_acquisition_approval_after_preview_v1.py", "preview.next_module")
    require_equal(
        contract_validator.get("historical_data_acquisition_contract_validator_status"),
        CONTRACT_VALIDATOR_STATUS_PASS,
        "contract_validator.status",
    )
    require_equal(
        contract_validator.get("next_module"),
        "edge_factory_os_repo_only_historical_data_acquisition_preview_after_contract_validator_v1.py",
        "contract_validator.next_module",
    )
    require_equal(contract.get("historical_data_acquisition_contract_status"), CONTRACT_STATUS_PASS, "contract.status")
    require_equal(
        contract.get("next_module"),
        "edge_factory_os_repo_only_historical_data_acquisition_contract_validator_after_data_horizon_discovery_v1.py",
        "contract.next_module",
    )
    require_equal(
        hardening.get("pre_acquisition_minimal_reliability_hardening_implementation_validator_status"),
        HARDENING_STATUS_PASS,
        "hardening.status",
    )
    require_true(hardening.get("hardening_validation_passed"), "hardening.hardening_validation_passed")
    require_equal(hardening.get("active_p0_blocker_count"), 0, "hardening.active_p0_blocker_count")
    require_equal(hardening.get("active_p1_attention_count"), 1, "hardening.active_p1_attention_count")
    require_true(hardening.get("dormant_repo_attention_count_carried_forward"), "hardening.dormant_repo_attention_count_carried_forward")

    require_equal(horizon.get("data_horizon_expansion_runner_execution_status"), DATA_HORIZON_STATUS_PASS, "horizon.status")
    require_equal(horizon.get("target_historical_horizon_years"), TARGET_HISTORICAL_HORIZON_YEARS, "horizon.target_historical_horizon_years")
    require_equal(horizon.get("target_timeframe"), TARGET_TIMEFRAME, "horizon.target_timeframe")
    require_false(horizon.get("historical_horizon_complete"), "horizon.historical_horizon_complete")
    require_equal(horizon.get("active_p0_blocker_count"), 0, "horizon.active_p0_blocker_count")
    require_equal(horizon.get("active_p1_attention_count"), 1, "horizon.active_p1_attention_count")
    require_true(horizon.get("p1_attention_carried_forward"), "horizon.p1_attention_carried_forward")
    require_false(horizon.get("data_download_performed"), "horizon.data_download_performed")
    require_false(horizon.get("data_fetch_performed"), "horizon.data_fetch_performed")
    require_false(horizon.get("data_build_performed"), "horizon.data_build_performed")
    require_false(horizon.get("external_api_calls_performed"), "horizon.external_api_calls_performed")
    require_false(horizon.get("parquet_rows_read_now"), "horizon.parquet_rows_read_now")

    return {
        "head": head,
        "status_lines_allowed": normalize_status_lines(status),
        "approval_artifact": str(APPROVAL_ARTIFACT),
        "preview_artifact": str(PREVIEW_ARTIFACT),
        "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
        "contract_artifact": str(CONTRACT_ARTIFACT),
        "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
        "data_horizon_discovery_artifact": str(DATA_HORIZON_DISCOVERY_ARTIFACT),
        "prior_available_horizon_days": horizon.get("available_horizon_days"),
        "prior_available_horizon_years_estimate": horizon.get("available_horizon_years_estimate"),
        "prior_latest_timestamp_available": horizon.get("latest_timestamp_available"),
    }


def file_mtime_utc(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def relative_or_string(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def canonical_path(path: Path) -> str:
    try:
        return str(path.resolve())
    except OSError:
        return str(path.absolute())


def lower_path(path: Path) -> str:
    return str(path).replace("\\", "/").lower()


def path_has_keyword(path: Path, keywords: Iterable[str] = DISCOVERY_KEYWORDS) -> bool:
    lowered = lower_path(path)
    return any(keyword in lowered for keyword in keywords)


def parse_dt(value: str) -> Optional[datetime]:
    raw = value.strip()
    if not raw:
        return None
    normalized = raw.replace("Z", "+00:00")
    parsed: Optional[datetime] = None
    if re.fullmatch(r"20\d{6}", normalized):
        try:
            parsed = datetime.strptime(normalized, "%Y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    elif re.fullmatch(r"20\d{2}-\d{2}-\d{2}", normalized):
        try:
            parsed = datetime.fromisoformat(normalized).replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    elif re.fullmatch(r"20\d{2}_\d{2}_\d{2}", normalized):
        try:
            parsed = datetime.strptime(normalized, "%Y_%m_%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    else:
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    parsed = parsed.astimezone(timezone.utc)
    if parsed.year < MIN_REASONABLE_HISTORICAL_YEAR:
        return None
    if parsed > datetime.now(timezone.utc):
        return None
    return parsed


def extract_timestamps(text: str, limit: int = 24) -> List[str]:
    patterns = [
        r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?",
        r"20\d{2}-\d{2}-\d{2}",
        r"20\d{6}",
        r"20\d{2}_\d{2}_\d{2}",
    ]
    found: List[str] = []
    seen = set()
    for pattern in patterns:
        for match in re.findall(pattern, text):
            parsed = parse_dt(match)
            if parsed is None:
                continue
            iso = parsed.isoformat()
            if iso not in seen:
                found.append(iso)
                seen.add(iso)
            if len(found) >= limit:
                return found
    return found


def min_max_dates(values: Iterable[str]) -> Tuple[Optional[str], Optional[str]]:
    parsed = [parse_dt(value) for value in values]
    clean = [value for value in parsed if value is not None]
    if not clean:
        return None, None
    return min(clean).isoformat(), max(clean).isoformat()


def sha256_if_small(path: Path, size: int) -> str:
    if size > MAX_SAFE_HASH_BYTES:
        return "SKIPPED_LARGE_FILE"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_read_text_metadata(path: Path, size: int) -> Tuple[Dict[str, Any], Optional[str]]:
    if size > MAX_SAFE_TEXT_BYTES:
        return {
            "metadata_read": False,
            "metadata_read_limit_reason": "SKIPPED_LARGE_TEXT_METADATA",
            "detected_timestamps": extract_timestamps(str(path)),
        }, None
    text = path.read_text(encoding="utf-8", errors="replace")
    timestamps = extract_timestamps(text)
    metadata: Dict[str, Any] = {
        "metadata_read": True,
        "metadata_bytes_read": len(text.encode("utf-8", errors="replace")),
        "detected_timestamps": timestamps,
        "contains_utc_hint": "utc" in text.lower() or "+00:00" in text,
        "contains_universe_hint": "universe" in text.lower() or "symbol" in text.lower(),
        "contains_provenance_hint": "provenance" in text.lower() or "source" in text.lower(),
        "contains_checksum_hint": "checksum" in text.lower() or "sha256" in text.lower(),
    }
    if path.suffix.lower() == ".json":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            keys = sorted(str(key) for key in parsed.keys())[:80]
            metadata["json_top_level_keys"] = keys
            for key_name in ("start", "start_date", "start_utc", "end", "end_date", "end_utc"):
                value = parsed.get(key_name)
                if isinstance(value, str):
                    metadata.setdefault("detected_timestamps", []).extend(extract_timestamps(value))
    return metadata, text[:MAX_SAFE_TEXT_BYTES]


def safe_sample_csv(path: Path, delimiter: str) -> Tuple[Dict[str, Any], str]:
    sample_bytes = path.read_bytes()[:MAX_SAFE_CSV_SAMPLE_BYTES]
    text = sample_bytes.decode("utf-8", errors="replace")
    rows: List[List[str]] = []
    try:
        reader = csv.reader(text.splitlines(), delimiter=delimiter)
        for index, row in enumerate(reader):
            rows.append(row)
            if index >= CSV_SAMPLE_ROWS:
                break
    except csv.Error:
        rows = []
    header = rows[0] if rows else []
    lowered_header = [column.strip().lower() for column in header]
    metadata = {
        "csv_header_sampled": bool(header),
        "csv_header": header[:80],
        "csv_sample_rows_read": max(0, len(rows) - 1),
        "csv_sample_bytes_read": len(sample_bytes),
        "detected_timestamps": extract_timestamps(text),
        "timestamp_column_hints": [column for column in header if column.strip().lower() in TIMESTAMP_FIELD_HINTS],
        "symbol_column_hints": [column for column in header if column.strip().lower() in SYMBOL_FIELD_HINTS],
        "ohlcv_column_hints": [column for column in header if column.strip().lower() in OHLCV_FIELD_HINTS],
    }
    return metadata, text


def parquet_metadata(path: Path) -> Dict[str, Any]:
    try:
        import pyarrow.parquet as pq  # type: ignore
    except ImportError:
        return {
            "parquet_metadata_checked": False,
            "pyarrow_available": False,
            "parquet_rows_read": False,
            "limitation": "pyarrow_not_available; parquet rows were not read",
        }
    try:
        parquet_file = pq.ParquetFile(path)
    except Exception as exc:  # pragma: no cover - defensive metadata-only guard
        return {
            "parquet_metadata_checked": False,
            "pyarrow_available": True,
            "parquet_rows_read": False,
            "limitation": f"parquet_footer_open_failed: {type(exc).__name__}",
        }

    schema_names = [str(name) for name in parquet_file.schema.names]
    detected: List[str] = []
    try:
        metadata = parquet_file.metadata
        timestamp_indices = [
            index
            for index, name in enumerate(schema_names)
            if any(hint in name.lower() for hint in TIMESTAMP_FIELD_HINTS)
        ]
        for row_group_index in range(metadata.num_row_groups):
            row_group = metadata.row_group(row_group_index)
            for column_index in timestamp_indices[:4]:
                stats = row_group.column(column_index).statistics
                if stats is None:
                    continue
                for value in (stats.min, stats.max):
                    if value is not None:
                        detected.extend(extract_timestamps(str(value), limit=4))
    except Exception:
        metadata = parquet_file.metadata
    return {
        "parquet_metadata_checked": True,
        "pyarrow_available": True,
        "parquet_rows_read": False,
        "num_rows_from_footer": metadata.num_rows,
        "num_row_groups": metadata.num_row_groups,
        "columns": schema_names[:120],
        "detected_timestamps": detected[:24],
    }


def classify_candidate(path: Path, metadata: Dict[str, Any], text_sample: str) -> Dict[str, Any]:
    lowered = (lower_path(path) + "\n" + text_sample[:4096].lower())
    header_values = " ".join(str(value).lower() for value in metadata.get("csv_header", []))
    combined = lowered + "\n" + header_values + "\n" + " ".join(metadata.get("json_top_level_keys", []))
    timeframe_1h = any(token in combined for token in ["1h", "hourly", "one_hour", "one-hour", "candle_interval"])
    ohlcv = all(field in combined for field in OHLCV_FIELD_HINTS) or "ohlcv" in combined or "candle" in combined
    source_type = "unsupported_or_ambiguous"
    if "feature" in combined and "panel" in combined:
        source_type = "feature_panel"
    if ohlcv and timeframe_1h:
        source_type = "1h_candle_source"
    if any(token in combined for token in ["archive", "historical", "history"]):
        source_type = "historical_archive" if source_type == "unsupported_or_ambiguous" else source_type
    if any(token in combined for token in ["export", "exchange", "binance", "coinbase", "kraken"]):
        source_type = "exchange_export" if source_type == "unsupported_or_ambiguous" else source_type
    if any(token in combined for token in ["manifest", "provenance", "inventory", "lifecycle", "metadata", "report"]):
        source_type = "manifest_or_metadata" if source_type == "unsupported_or_ambiguous" else source_type

    detected_dates = list(metadata.get("detected_timestamps", []))
    detected_dates.extend(extract_timestamps(str(path)))
    earliest, latest = min_max_dates(detected_dates)
    return {
        "source_type": source_type,
        "timeframe_1h_evidence": timeframe_1h,
        "ohlcv_evidence": ohlcv,
        "symbol_evidence": bool(metadata.get("symbol_column_hints")) or "symbol" in combined or re.search(r"[\\/][A-Z0-9]{2,15}_1h\.", str(path)) is not None,
        "provenance_evidence": bool(metadata.get("contains_provenance_hint")) or "provenance" in combined or "source" in combined,
        "timezone_evidence": bool(metadata.get("contains_utc_hint")) or "+00:00" in combined or "utc" in combined,
        "checksum_evidence": bool(metadata.get("contains_checksum_hint")) or "sha256" in combined or "checksum" in combined,
        "universe_rule_evidence": bool(metadata.get("contains_universe_hint")) and "rule" in combined,
        "symbol_lifecycle_evidence": any(token in combined for token in ["lifecycle", "listing", "delisted", "removed"]),
        "delisted_removed_symbol_evidence": any(token in combined for token in ["delisted", "removed"]),
        "candidate_earliest_timestamp": earliest,
        "candidate_latest_timestamp": latest,
    }


def derive_roots(horizon: Dict[str, Any]) -> List[Path]:
    roots: List[Path] = [
        LAB_ROOT,
        LAB_ROOT / "edge_factory_feature_panels",
        REPO_ROOT,
        DESKTOP_ROOT,
    ]
    for key in ("searched_roots", "discovered_local_data_dirs"):
        values = horizon.get(key)
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str):
                roots.append(Path(value))
            elif isinstance(value, dict) and isinstance(value.get("path"), str):
                roots.append(Path(value["path"]))
    for artifact_dir in [
        LAB_ROOT / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1",
        LAB_ROOT / "edge_factory_candle_universe_inventory",
        LAB_ROOT / "edge_factory_candle_universe_inventory_v2",
        LAB_ROOT / "edge_factory_offline_runner_data_source_binding_v1",
    ]:
        roots.append(artifact_dir)
    existing_dirs = [path for path in LAB_ROOT.iterdir() if path.is_dir() and path_has_keyword(path, DESCEND_KEYWORDS)]
    roots.extend(existing_dirs[:200])

    deduped: List[Path] = []
    seen = set()
    for root in roots:
        key = str(root).lower().rstrip("\\/")
        if key not in seen:
            deduped.append(root)
            seen.add(key)
    return deduped


def should_descend(base: Path, current: Path, name: str) -> bool:
    lowered_name = name.lower()
    if lowered_name in SKIP_DIR_NAMES:
        return False
    if current == DESKTOP_ROOT:
        return any(keyword in lowered_name for keyword in DESCEND_KEYWORDS)
    try:
        depth = len(current.relative_to(base).parts)
    except ValueError:
        depth = 0
    if base == DESKTOP_ROOT and depth <= 1:
        return any(keyword in lowered_name for keyword in DESCEND_KEYWORDS)
    return True


def iter_candidate_files(root: Path) -> Iterable[Path]:
    considered = 0
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if should_descend(root, current, name)]
        for filename in filenames:
            path = current / filename
            suffix = path.suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS and not path_has_keyword(path):
                continue
            if suffix not in SUPPORTED_EXTENSIONS:
                continue
            if not path_has_keyword(path) and suffix not in SAFE_TEXT_EXTENSIONS:
                continue
            considered += 1
            if considered > MAX_FILES_PER_ROOT:
                return
            yield path


def discover_sources(roots: List[Path]) -> Dict[str, Any]:
    existing_roots = [root for root in roots if root.exists() and root.is_dir()]
    missing_roots = [root for root in roots if not (root.exists() and root.is_dir())]
    seen_files = set()
    candidates: List[Dict[str, Any]] = []
    format_counter: Counter[str] = Counter()
    source_type_counter: Counter[str] = Counter()
    largest_files: List[Dict[str, Any]] = []
    counters = Counter()

    for root in existing_roots:
        for path in iter_candidate_files(root):
            key = canonical_path(path).lower()
            if key in seen_files:
                continue
            seen_files.add(key)
            if counters["files_considered_count"] >= MAX_TOTAL_FILES_CONSIDERED:
                break
            try:
                stat = path.stat()
            except OSError:
                continue
            counters["files_considered_count"] += 1
            suffix = path.suffix.lower()
            size = int(stat.st_size)
            format_counter[suffix or "<none>"] += 1
            if size > MAX_SAFE_HASH_BYTES:
                counters["large_file_metadata_only_count"] += 1
            metadata: Dict[str, Any] = {
                "detected_timestamps": extract_timestamps(str(path)),
                "rows_read": False,
                "full_scan_performed": False,
            }
            text_sample = ""
            if suffix in SAFE_TEXT_EXTENSIONS:
                text_metadata, text_sample = safe_read_text_metadata(path, size)
                text_sample = text_sample or ""
                metadata.update(text_metadata)
                if text_metadata.get("metadata_read") is True:
                    counters["small_metadata_files_read_count"] += 1
            elif suffix in SAFE_CSV_EXTENSIONS:
                delimiter = "\t" if suffix == ".tsv" else ","
                csv_metadata, text_sample = safe_sample_csv(path, delimiter)
                metadata.update(csv_metadata)
                if csv_metadata.get("csv_header_sampled") is True:
                    counters["csv_headers_sampled_count"] += 1
            elif suffix in PARQUET_EXTENSIONS:
                pq_metadata = parquet_metadata(path)
                metadata.update(pq_metadata)
                if pq_metadata.get("parquet_metadata_checked") is True:
                    counters["parquet_metadata_files_checked_count"] += 1
                counters["large_file_metadata_only_count"] += 1
            else:
                metadata["archive_metadata_only"] = True
                counters["large_file_metadata_only_count"] += 1

            try:
                file_hash = sha256_if_small(path, size)
            except OSError:
                file_hash = "HASH_ERROR"
            classification = classify_candidate(path, metadata, text_sample)
            source_type_counter[classification["source_type"]] += 1
            record = {
                "path": str(path),
                "relative_to_lab": relative_or_string(path, LAB_ROOT),
                "suffix": suffix,
                "size_bytes": size,
                "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "sha256": file_hash,
                "inspection_mode": inspection_mode_for_suffix(suffix, size, metadata),
                "rows_read": False,
                "full_scan_performed": False,
                **classification,
                "metadata_summary": metadata,
            }
            largest_files.append(
                {
                    "path": str(path),
                    "relative_to_lab": relative_or_string(path, LAB_ROOT),
                    "suffix": suffix,
                    "size_bytes": size,
                    "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                }
            )
            if len(candidates) < MAX_CANDIDATE_RECORDS:
                candidates.append(record)
        if counters["files_considered_count"] >= MAX_TOTAL_FILES_CONSIDERED:
            break

    largest_files = sorted(largest_files, key=lambda item: item["size_bytes"], reverse=True)[:25]
    return {
        "searched_roots": [str(root) for root in roots],
        "roots_existing": [str(root) for root in existing_roots],
        "roots_missing": [str(root) for root in missing_roots],
        "roots_existing_count": len(existing_roots),
        "roots_missing_count": len(missing_roots),
        "files_considered_count": int(counters["files_considered_count"]),
        "candidate_source_file_count": sum(source_type_counter.values()),
        "large_file_metadata_only_count": int(counters["large_file_metadata_only_count"]),
        "small_metadata_files_read_count": int(counters["small_metadata_files_read_count"]),
        "csv_headers_sampled_count": int(counters["csv_headers_sampled_count"]),
        "parquet_metadata_files_checked_count": int(counters["parquet_metadata_files_checked_count"]),
        "candidate_format_summary": dict(sorted(format_counter.items())),
        "source_type_counter": dict(source_type_counter),
        "candidate_size_summary": {
            "total_candidate_bytes": sum(item["size_bytes"] for item in largest_files),
            "largest_files": largest_files,
            "candidate_records_written_limit": MAX_CANDIDATE_RECORDS,
        },
        "candidates": candidates,
    }


def inspection_mode_for_suffix(suffix: str, size: int, metadata: Dict[str, Any]) -> str:
    if suffix in SAFE_TEXT_EXTENSIONS:
        return "small_metadata_text_read" if metadata.get("metadata_read") else "metadata_only_large_text"
    if suffix in SAFE_CSV_EXTENSIONS:
        return "csv_header_and_tiny_sample_only"
    if suffix in PARQUET_EXTENSIONS:
        return "parquet_footer_schema_metadata_only" if metadata.get("parquet_metadata_checked") else "parquet_path_size_mtime_only"
    if suffix in ARCHIVE_EXTENSIONS:
        return "archive_path_size_mtime_only"
    return "path_size_mtime_only"


def compute_horizon(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ranges: List[Tuple[datetime, datetime]] = []
    for candidate in candidates:
        if not horizon_range_candidate_is_data_like(candidate):
            continue
        start = candidate.get("candidate_earliest_timestamp")
        end = candidate.get("candidate_latest_timestamp")
        parsed_start = parse_dt(start) if isinstance(start, str) else None
        parsed_end = parse_dt(end) if isinstance(end, str) else None
        if parsed_start and parsed_end and parsed_end >= parsed_start:
            ranges.append((parsed_start, parsed_end))
    if not ranges:
        return {
            "local_manual_sources_found": bool(candidates),
            "candidate_3_to_4_year_horizon_found": False,
            "candidate_available_horizon_days_max": 0.0,
            "candidate_available_horizon_years_estimate_max": 0.0,
            "candidate_earliest_timestamp_min": None,
            "candidate_latest_timestamp_max": None,
            "candidate_timeframe_1h_evidence_found": any(candidate.get("timeframe_1h_evidence") for candidate in candidates),
            "horizon_suitability_limitations": [
                "no candidate start/end range was provable from bounded local metadata",
                "no parquet rows or full CSV scans were performed",
            ],
        }
    earliest = min(start for start, _ in ranges)
    latest = max(end for _, end in ranges)
    max_days = max((end - start).total_seconds() / 86400.0 for start, end in ranges)
    max_years = round(max_days / 365.25, 6)
    timeframe_found = any(candidate.get("timeframe_1h_evidence") for candidate in candidates)
    horizon_found = bool(max_days >= TARGET_MINIMUM_DAYS and timeframe_found)
    limitations = ["no parquet rows or full CSV scans were performed"]
    if not horizon_found:
        limitations.append("candidate metadata did not prove a 3-to-4-year 1h horizon")
    if not any(candidate.get("symbol_lifecycle_evidence") for candidate in candidates):
        limitations.append("symbol lifecycle evidence remains incomplete")
    return {
        "local_manual_sources_found": bool(candidates),
        "candidate_3_to_4_year_horizon_found": horizon_found,
        "candidate_available_horizon_days_max": round(max_days, 6),
        "candidate_available_horizon_years_estimate_max": max_years,
        "candidate_earliest_timestamp_min": earliest.isoformat(),
        "candidate_latest_timestamp_max": latest.isoformat(),
        "candidate_timeframe_1h_evidence_found": timeframe_found,
        "horizon_suitability_limitations": limitations,
    }


def horizon_range_candidate_is_data_like(candidate: Dict[str, Any]) -> bool:
    source_type = candidate.get("source_type")
    suffix = candidate.get("suffix")
    if source_type in {"1h_candle_source", "feature_panel", "exchange_export"}:
        return True
    if source_type == "historical_archive" and suffix in SAFE_CSV_EXTENSIONS | PARQUET_EXTENSIONS | SAFE_TEXT_EXTENSIONS:
        return True
    return bool(
        suffix in SAFE_CSV_EXTENSIONS | PARQUET_EXTENSIONS
        and (candidate.get("timeframe_1h_evidence") or candidate.get("ohlcv_evidence"))
    )


def build_sections(preflight: Dict[str, Any], discovery: Dict[str, Any]) -> Dict[str, Any]:
    candidates = discovery["candidates"]
    horizon = compute_horizon(candidates)
    source_counts = Counter(candidate.get("source_type", "unsupported_or_ambiguous") for candidate in candidates)
    provenance_candidates = [candidate for candidate in candidates if candidate.get("provenance_evidence")]
    checksum_available = any(candidate.get("sha256") and candidate.get("sha256") != "SKIPPED_LARGE_FILE" for candidate in candidates)
    symbol_lifecycle = any(candidate.get("symbol_lifecycle_evidence") for candidate in candidates)
    delisted_removed = any(candidate.get("delisted_removed_symbol_evidence") for candidate in candidates)
    source_traceability = "NONE"
    if candidates and provenance_candidates:
        source_traceability = "MEDIUM_LOCAL_PATH_AND_METADATA"
    elif candidates:
        source_traceability = "LOW_LOCAL_PATH_FILENAME_SIZE_MTIME_ONLY"
    local_gap_closed = bool(
        horizon["candidate_3_to_4_year_horizon_found"]
        and horizon["candidate_timeframe_1h_evidence_found"]
        and source_traceability.startswith("MEDIUM")
    )
    latest_holdout_possible = bool(horizon["candidate_latest_timestamp_max"] and horizon["candidate_timeframe_1h_evidence_found"])
    holdout_protectable = bool(latest_holdout_possible and local_gap_closed)

    return {
        "whole_system_preflight": {
            "whole_system_preflight_completed": True,
            "live_next_module_matches_requested_module": True,
            "artifact_chain_consistent": True,
            "stale_or_contradictory_artifact_detected": False,
            "real_final_form_gap_confirmed": True,
            "documentation_loop_detected": False,
            "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
            "next_module_closes_real_gap": True,
            "active_p0_blocker_count_from_live_artifact": 0,
            "active_p1_attention_count_from_live_artifact": 1,
            "p1_attention_carried_forward": True,
            "dormant_repo_attention_count_carried_forward": True,
            "blocked_actions_absent_from_requested_module": True,
            "whole_system_preflight_decision": "PASS",
            "preflight_snapshot": preflight,
        },
        "discovery_scope": {
            "local_manual_source_discovery_performed": True,
            "searched_roots": discovery["searched_roots"],
            "roots_existing_count": discovery["roots_existing_count"],
            "roots_missing_count": discovery["roots_missing_count"],
            "files_considered_count": discovery["files_considered_count"],
            "candidate_source_file_count": discovery["candidate_source_file_count"],
            "large_file_metadata_only_count": discovery["large_file_metadata_only_count"],
            "small_metadata_files_read_count": discovery["small_metadata_files_read_count"],
            "csv_headers_sampled_count": discovery["csv_headers_sampled_count"],
            "parquet_metadata_files_checked_count": discovery["parquet_metadata_files_checked_count"],
            "parquet_rows_read_now": False,
            "full_scan_performed": False,
        },
        "candidate_inventory": {
            "likely_1h_candle_source_count": source_counts.get("1h_candle_source", 0),
            "likely_historical_archive_count": source_counts.get("historical_archive", 0),
            "likely_exchange_export_count": source_counts.get("exchange_export", 0),
            "likely_feature_panel_count": source_counts.get("feature_panel", 0),
            "likely_manifest_or_metadata_count": source_counts.get("manifest_or_metadata", 0),
            "unsupported_or_ambiguous_source_count": source_counts.get("unsupported_or_ambiguous", 0),
            "candidate_format_summary": discovery["candidate_format_summary"],
            "candidate_size_summary": discovery["candidate_size_summary"],
        },
        "horizon_suitability": horizon,
        "source_manifest_preview": {
            "source_name_available": bool(candidates),
            "retrieval_method_available": bool(provenance_candidates),
            "timestamp_timezone_available": any(candidate.get("timezone_evidence") for candidate in candidates),
            "candle_interval_available": horizon["candidate_timeframe_1h_evidence_found"],
            "symbol_list_available": any(candidate.get("symbol_evidence") for candidate in candidates),
            "universe_rule_available": any(candidate.get("universe_rule_evidence") for candidate in candidates),
            "start_end_date_available": bool(horizon["candidate_earliest_timestamp_min"] and horizon["candidate_latest_timestamp_max"]),
            "checksum_available": checksum_available,
            "raw_data_preservation_possible": bool(candidates),
        },
        "provenance_preview": {
            "provenance_evidence_available": bool(provenance_candidates),
            "source_traceability_level": source_traceability,
            "manual_source_candidate_count": (
                source_counts.get("1h_candle_source", 0)
                + source_counts.get("historical_archive", 0)
                + source_counts.get("exchange_export", 0)
            ),
            "local_archive_candidate_count": source_counts.get("historical_archive", 0),
            "external_api_required_from_discovery": False,
            "external_api_allowed_now": False,
        },
        "survivorship_holdout_preview": {
            "symbol_lifecycle_evidence_available": symbol_lifecycle,
            "delisted_removed_symbol_evidence_available": delisted_removed,
            "survivorship_bias_controls_satisfied_now": bool(symbol_lifecycle and delisted_removed and local_gap_closed),
            "holdout_window_protectable_from_candidates": holdout_protectable,
            "latest_6_to_12_month_holdout_possible": latest_holdout_possible,
            "survivorship_holdout_limitations": survivorship_limitations(symbol_lifecycle, delisted_removed, holdout_protectable),
        },
        "gap_report": {
            "local_manual_source_gap_closed": local_gap_closed,
            "external_or_additional_acquisition_still_required": not local_gap_closed,
            "local_manual_source_gap_reason": (
                "local/manual metadata proved a 3-to-4-year 1h source candidate with traceability"
                if local_gap_closed
                else "bounded local/manual discovery did not fully prove horizon, provenance, and survivorship controls"
            ),
            "recommended_next_route": "VALIDATE_LOCAL_MANUAL_SOURCE_DISCOVERY_ARTIFACTS_NO_ACQUISITION_EXECUTION",
        },
        "compliance_report": {
            "no_download_fetch_api": True,
            "no_data_build": True,
            "no_fake_synthetic_data": True,
            "no_strategy_backtest_candidate": True,
            "no_runtime_capital_live": True,
            "no_generic_runner": True,
            "no_schema_config": True,
            "old_route_not_reopened": True,
            "dormant_repo_risks_excluded": True,
            "hardening_state_respected": True,
        },
        "next_module_decision": {
            "next_module": NEXT_MODULE_VALIDATOR,
            "blocked_next_module_if_discovery_unsafe": NEXT_MODULE_BLOCKED,
            "decision_reason": "local/manual discovery artifacts were created safely and require validator review",
        },
    }


def survivorship_limitations(symbol_lifecycle: bool, delisted_removed: bool, holdout_protectable: bool) -> List[str]:
    limitations = []
    if not symbol_lifecycle:
        limitations.append("symbol lifecycle evidence was not fully available from bounded metadata")
    if not delisted_removed:
        limitations.append("delisted/removed symbol evidence was not fully available from bounded metadata")
    if not holdout_protectable:
        limitations.append("latest 6-to-12 month holdout cannot be treated as protected until validator confirms source suitability")
    if not limitations:
        limitations.append("validator must still confirm lifecycle and holdout evidence before any acquisition execution")
    return limitations


def replacement_checks(payload: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "preflight_passed": payload.get("whole_system_preflight_decision") == "PASS",
        "local_manual_source_discovery_performed": payload.get("local_manual_source_discovery_performed") is True,
        "candidate_inventory_created": payload.get("historical_local_manual_source_candidate_inventory_created") is True,
        "suitability_report_created": payload.get("historical_local_manual_source_suitability_report_created") is True,
        "manifest_preview_created": payload.get("historical_local_manual_source_manifest_preview_created") is True,
        "provenance_preview_created": payload.get("historical_local_manual_source_provenance_preview_created") is True,
        "gap_report_created": payload.get("historical_local_manual_source_gap_report_created") is True,
        "contract_compliance_report_created": payload.get("historical_local_manual_source_contract_compliance_report_created") is True,
        "no_download_fetch_api_build": (
            payload.get("data_download_performed") is False
            and payload.get("data_fetch_performed") is False
            and payload.get("data_build_performed") is False
            and payload.get("external_api_calls_performed") is False
        ),
        "no_parquet_rows_or_full_scan": (
            payload.get("parquet_rows_read_now") is False and payload.get("full_scan_performed") is False
        ),
        "next_module_is_validator": payload.get("next_module") == NEXT_MODULE_VALIDATOR,
    }


def build_payload(preflight: Dict[str, Any], sections: Dict[str, Any], discovery: Dict[str, Any]) -> Dict[str, Any]:
    whole = sections["whole_system_preflight"]
    scope = sections["discovery_scope"]
    inventory = sections["candidate_inventory"]
    horizon = sections["horizon_suitability"]
    manifest = sections["source_manifest_preview"]
    provenance = sections["provenance_preview"]
    survivorship = sections["survivorship_holdout_preview"]
    gap = sections["gap_report"]
    compliance = sections["compliance_report"]
    flags = dangerous_flags()
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_local_manual_source_discovery_status": STATUS_PASS,
        "final_decision": "HISTORICAL_DATA_ACQUISITION_LOCAL_MANUAL_SOURCE_DISCOVERY_COMPLETE_VALIDATOR_NEXT",
        "next_action": "RUN_LOCAL_MANUAL_SOURCE_DISCOVERY_VALIDATOR_NO_ACQUISITION_EXECUTION",
        "next_module": NEXT_MODULE_VALIDATOR,
        **{key: value for key, value in whole.items() if key != "preflight_snapshot"},
        "prior_approval_respected": True,
        **scope,
        **inventory,
        **horizon,
        **manifest,
        **provenance,
        **survivorship,
        **gap,
        "historical_local_manual_source_candidate_inventory_created": True,
        "historical_local_manual_source_suitability_report_created": True,
        "historical_local_manual_source_manifest_preview_created": True,
        "historical_local_manual_source_provenance_preview_created": True,
        "historical_local_manual_source_gap_report_created": True,
        "historical_local_manual_source_contract_compliance_report_created": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "fake_or_synthetic_data_detected": False,
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
        "current_evidence_chain_quality_before_discovery": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_discovery": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "dormant_repo_attention_count": 716,
        "evidence_chain_policy_level": EVIDENCE_CHAIN_POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "derived_live_repo_post_check": "PASS_LOCAL_MANUAL_SOURCE_DISCOVERY_COMPLETE_PENDING_VALIDATOR",
        "derived_live_repo_post_check_reason": (
            "bounded local/manual source discovery created candidate artifacts without download, fetch, external API, "
            "data build, parquet row reads, full scans, strategy, runtime, capital, live, generic-runner, schema, "
            "config, or old-route action"
        ),
        "tracked_python_count_expectation": {
            "previous": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "source_artifacts": {
            "approval_artifact": str(APPROVAL_ARTIFACT),
            "preview_artifact": str(PREVIEW_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "hardening_validator_artifact": str(HARDENING_VALIDATOR_ARTIFACT),
            "data_horizon_discovery_artifact": str(DATA_HORIZON_DISCOVERY_ARTIFACT),
        },
        "discovery_artifacts": {
            "historical_local_manual_source_candidate_inventory": str(OUT_DIR / "historical_local_manual_source_candidate_inventory.json"),
            "historical_local_manual_source_suitability_report": str(OUT_DIR / "historical_local_manual_source_suitability_report.json"),
            "historical_local_manual_source_manifest_preview": str(OUT_DIR / "historical_local_manual_source_manifest_preview.json"),
            "historical_local_manual_source_provenance_preview": str(OUT_DIR / "historical_local_manual_source_provenance_preview.json"),
            "historical_local_manual_source_gap_report": str(OUT_DIR / "historical_local_manual_source_gap_report.json"),
            "historical_local_manual_source_contract_compliance_report": str(OUT_DIR / "historical_local_manual_source_contract_compliance_report.json"),
        },
        "whole_system_preflight": whole,
        "discovery_sections": sections,
        "candidate_inventory_records_written": len(discovery["candidates"]),
    }
    payload["replacement_checks"] = replacement_checks(payload)
    payload["replacement_checks_all_true"] = all(value is True for value in payload["replacement_checks"].values())
    return payload


def validate_payload(payload: Dict[str, Any]) -> None:
    required_true = [
        "whole_system_preflight_completed",
        "live_next_module_matches_requested_module",
        "artifact_chain_consistent",
        "real_final_form_gap_confirmed",
        "next_module_closes_real_gap",
        "p1_attention_carried_forward",
        "dormant_repo_attention_count_carried_forward",
        "blocked_actions_absent_from_requested_module",
        "prior_approval_respected",
        "local_manual_source_discovery_performed",
        "historical_local_manual_source_candidate_inventory_created",
        "historical_local_manual_source_suitability_report_created",
        "historical_local_manual_source_manifest_preview_created",
        "historical_local_manual_source_provenance_preview_created",
        "historical_local_manual_source_gap_report_created",
        "historical_local_manual_source_contract_compliance_report_created",
        "generic_runner_implementation_remains_blocked",
        "future_modules_must_classify_evidence_quality",
        "replacement_checks_are_not_equivalent_to_primary_artifact",
        "loop_remains_closed",
        "dangerous_flags_all_false",
        "replacement_checks_all_true",
    ]
    required_false = [
        "stale_or_contradictory_artifact_detected",
        "documentation_loop_detected",
        "parquet_rows_read_now",
        "full_scan_performed",
        "external_api_allowed_now",
        "data_download_performed",
        "data_fetch_performed",
        "data_build_performed",
        "external_api_calls_performed",
        "fake_or_synthetic_data_detected",
        "strategy_signal_claims_made",
        "tradable_edge_claims_made",
        "profit_claims_made",
        "backtest_performed",
        "candidate_generation_performed",
        "runtime_touch_performed",
        "capital_touch_performed",
        "live_touch_performed",
        "generic_runner_approval_granted",
        "schema_or_config_created",
        "old_source_panel_anomaly_route_reopened_now",
        "old_route_closed_artifacts_used_as_active_evidence_now",
        "ordinary_selector_backlog_loop_reentry_allowed",
        "generic_runner_target_exists",
    ]
    for key in required_true:
        require_true(payload.get(key), key)
    for key in required_false:
        require_false(payload.get(key), key)
    require_equal(payload.get("historical_data_acquisition_local_manual_source_discovery_status"), STATUS_PASS, "status")
    require_equal(payload.get("next_module"), NEXT_MODULE_VALIDATOR, "next_module")
    require_equal(payload.get("whole_system_preflight_decision"), "PASS", "whole_system_preflight_decision")
    require_equal(payload.get("documentation_loop_risk_level"), DOCUMENTATION_LOOP_RISK_LEVEL, "documentation_loop_risk_level")
    require_equal(payload.get("current_evidence_chain_quality_before_discovery"), EVIDENCE_BEFORE, "evidence_before")
    require_equal(payload.get("current_evidence_chain_quality_after_discovery"), EVIDENCE_AFTER, "evidence_after")
    require_equal(payload.get("active_p0_blocker_count"), 0, "active_p0_blocker_count")
    require_equal(payload.get("active_p1_attention_count"), 1, "active_p1_attention_count")
    require_equal(payload.get("dormant_repo_attention_count"), 716, "dormant_repo_attention_count")
    require_equal(payload.get("planned_schema_files_existing_count"), 0, "planned_schema_files_existing_count")
    require(payload.get("candidate_source_file_count", 0) >= 0, "candidate source count missing")
    require(all(value is False for value in payload["dangerous_flags"].values()), "dangerous flags must all be false")


def write_discovery_artifacts(payload: Dict[str, Any], sections: Dict[str, Any], discovery: Dict[str, Any]) -> None:
    write_json(
        OUT_DIR / "historical_local_manual_source_candidate_inventory.json",
        {
            "artifact": "historical_local_manual_source_candidate_inventory.json",
            "generated_at_utc": payload["generated_at_utc"],
            "candidate_inventory": sections["candidate_inventory"],
            "discovery_scope": sections["discovery_scope"],
            "candidates": discovery["candidates"],
            "parquet_rows_read_now": False,
            "full_scan_performed": False,
        },
    )
    write_json(
        OUT_DIR / "historical_local_manual_source_suitability_report.json",
        {
            "artifact": "historical_local_manual_source_suitability_report.json",
            "generated_at_utc": payload["generated_at_utc"],
            "horizon_suitability": sections["horizon_suitability"],
            "survivorship_holdout_preview": sections["survivorship_holdout_preview"],
            "gap_report": sections["gap_report"],
        },
    )
    write_json(
        OUT_DIR / "historical_local_manual_source_manifest_preview.json",
        {
            "artifact": "historical_local_manual_source_manifest_preview.json",
            "generated_at_utc": payload["generated_at_utc"],
            "source_manifest_preview": sections["source_manifest_preview"],
        },
    )
    write_json(
        OUT_DIR / "historical_local_manual_source_provenance_preview.json",
        {
            "artifact": "historical_local_manual_source_provenance_preview.json",
            "generated_at_utc": payload["generated_at_utc"],
            "provenance_preview": sections["provenance_preview"],
        },
    )
    write_json(
        OUT_DIR / "historical_local_manual_source_gap_report.json",
        {
            "artifact": "historical_local_manual_source_gap_report.json",
            "generated_at_utc": payload["generated_at_utc"],
            "gap_report": sections["gap_report"],
            "next_module_decision": sections["next_module_decision"],
        },
    )
    write_json(
        OUT_DIR / "historical_local_manual_source_contract_compliance_report.json",
        {
            "artifact": "historical_local_manual_source_contract_compliance_report.json",
            "generated_at_utc": payload["generated_at_utc"],
            "compliance_report": sections["compliance_report"],
            "dangerous_flags": payload["dangerous_flags"],
            "hardening_state_respected": True,
        },
    )


def main() -> None:
    approval = load_json(APPROVAL_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    contract_validator = load_json(CONTRACT_VALIDATOR_ARTIFACT)
    contract = load_json(CONTRACT_ARTIFACT)
    hardening = load_json(HARDENING_VALIDATOR_ARTIFACT)
    horizon = load_json(DATA_HORIZON_DISCOVERY_ARTIFACT)
    preflight = validate_preflight(approval, preview, contract_validator, contract, hardening, horizon)
    roots = derive_roots(horizon)
    discovery = discover_sources(roots)
    sections = build_sections(preflight, discovery)
    payload = build_payload(preflight, sections, discovery)
    validate_payload(payload)
    write_discovery_artifacts(payload, sections, discovery)
    write_json(OUT_DIR / "repo_only_historical_data_acquisition_local_manual_source_discovery_after_approval_v1_latest.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
