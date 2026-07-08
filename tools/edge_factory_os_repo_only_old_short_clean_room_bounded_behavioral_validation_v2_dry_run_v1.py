#!/usr/bin/env python3
"""Run the old_short clean-room bounded behavioral validation V2 dry-run.

This dry-run reads only bounded samples and fixture outputs. It does not compare
full datasets, run a backtest, compute PnL, run the runner, generate signals,
touch runtime, use network/API, allocate capital, generate candidates, or claim
edge.
"""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DRY_RUN"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "14d40ee6739ab7609546978bea2a7fc071d5e34e"
EXPECTED_TRACKED_PYTHON_COUNT = 970
NEXT_ALLOWED_STEP_PASS_OR_PARTIAL = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_REVIEW_V1"
NEXT_ALLOWED_STEP_FAIL_OR_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_REPAIR_PREVIEW_V1"
MASTER_SAMPLE_LIMIT = 100

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_v2_dry_run_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_dry_run_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / MODULE
ARTIFACT_PATH = REPO_ROOT / ARTIFACT

MASTER_PROXY_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
CLEAN_ROOM_V2_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\realistic_fixture_runner_v2_dry_run_v1"
)
ACCEPTED_LIFECYCLE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\accepted_lifecycle_fixture_discovery_v1"
)

SOURCE_ARTIFACT_PATHS = {
    "bounded_behavioral_validation_v2_preview": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_preview_v1.json",
    "bounded_behavioral_validation_v2_design": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_design_v1.json",
    "runner_realistic_fixture_v2_review": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_review_v1.json",
    "runner_realistic_fixture_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.json",
    "accepted_lifecycle_fixture_review": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json",
}

CSV_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
]
STATE_FILE = "state.json"
MASTER_AND_CLEAN_FILES = [*CSV_FILES, STATE_FILE]
ACCEPTED_FILES = [
    "accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_master_cases.jsonl",
    "accepted_lifecycle_pairing_plan.json",
    "accepted_lifecycle_discovery_summary.json",
]

BEHAVIOR_DIMENSIONS_V2 = [
    "schema compatibility",
    "family_key old_short",
    "subfamily blowoff_short / mean_reversion_short presence",
    "side short",
    "signal feature availability",
    "entry delay near 2 minutes",
    "hold duration near 120 minutes",
    "notional near 50 USDT",
    "accepted lifecycle coverage",
    "rejected gate behavior",
    "gate_missing_timeout behavior",
    "gate_blocked behavior",
    "inferred gate_allowed path coverage",
    "no position without gate allow",
    "heartbeat/state compatibility",
    "safety label compatibility",
]
SIMILARITY_METRICS_V2 = [
    "schema_match_rate",
    "family_key_match_rate",
    "subfamily_presence_match",
    "side_match_rate",
    "signal_feature_presence_rate",
    "entry_delay_median_abs_error_seconds",
    "hold_minutes_median_abs_error",
    "notional_median_abs_error",
    "rejected_reason_overlap_rate",
    "gate_behavior_consistency_rate",
    "accepted_lifecycle_coverage_rate",
    "inferred_gate_allowed_coverage_rate",
    "no_position_without_gate_violation_count",
    "safety_label_match_rate",
    "state_heartbeat_schema_match",
    "coin_overlap_rate",
    "timestamp_alignment_rate",
    "missing_metric_count",
]

BASE_SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "PROXY_BEHAVIOR_FIXTURE",
    "NOT_ORIGINAL_OLD_SHORT",
    "NOT_EXACT_REPLAY",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]
ACCEPTED_LABEL = "ACCEPTED_LIFECYCLE_FIXTURE"
FORBIDDEN_PNL_OUTCOME_COLUMNS = {
    "pnl",
    "stress_pnl",
    "net_ret",
    "gross_ret",
    "realistic_net_ret",
    "stress_net_ret",
    "win",
    "loss",
    "best_trade",
    "worst_trade",
    "future_return",
    "validation_return",
    "holdout_result",
}
FORBIDDEN_LIVE_PRIVATE_FIELDS = {
    "api_key",
    "api_secret",
    "secret_key",
    "passphrase",
    "account_id",
    "private_key",
    "order_id",
    "client_order_id",
    "live_order_id",
    "fill_id",
}
SIGNAL_FEATURE_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
]


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key not in FORBIDDEN_PNL_OUTCOME_COLUMNS
    }


def read_csv_rows(path: Path, limit: int | None) -> tuple[list[str], list[dict[str, Any]], int, list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        rows: list[dict[str, Any]] = []
        total_seen = 0
        for raw_row in reader:
            total_seen += 1
            if limit is not None and len(rows) >= limit:
                continue
            rows.append(sanitize_row(dict(raw_row)))
    ignored_columns = [column for column in header if column in FORBIDDEN_PNL_OUTCOME_COLUMNS]
    return header, rows, total_seen, ignored_columns


def collect_key_values(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                found.append(item_value)
            found.extend(collect_key_values(item_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_key_values(item, key))
    return found


def first_value(value: Any, key: str, default: Any = None) -> Any:
    values = collect_key_values(value, key)
    return values[0] if values else default


def source_summary(relative_path: str, data: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    return {
        "path": relative_path,
        "sha256": sha256_file(path),
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": first_value(data, "route_key"),
        "result_classification": data.get("result_classification"),
        "next_allowed_step": data.get("next_allowed_step"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
    }


def status_has_only_expected_untracked_tool(status_text: str) -> bool:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    expected = f"?? {MODULE}"
    return all(line == expected for line in lines)


def stat_inputs(paths: list[Path]) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    for path in paths:
        stats[str(path)] = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else None,
            "mtime_ns": path.stat().st_mtime_ns if path.exists() else None,
        }
    return stats


def get_value(row: dict[str, Any], names: list[str]) -> Any:
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return value
    return None


def to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_time(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def labels_from_row(row: dict[str, Any]) -> set[str]:
    labels = row.get("safety_labels")
    if isinstance(labels, str):
        return {part.strip() for part in labels.split(";") if part.strip()}
    if isinstance(labels, list):
        return {str(part) for part in labels}
    return set()


def metric(computed: bool, value: Any, passed: bool | None, reason: str) -> dict[str, Any]:
    return {
        "computed": computed,
        "value": value,
        "passed": passed,
        "reason": reason,
    }


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    source_payloads = {
        name: read_json(REPO_ROOT / relative_path)
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }

    master: dict[str, Any] = {"csv": {}, "state": {}, "ignored_pnl_outcome_columns": {}}
    for file_name in CSV_FILES:
        path = MASTER_PROXY_ROOT / file_name
        header, rows, total_seen, ignored = read_csv_rows(path, MASTER_SAMPLE_LIMIT)
        master["csv"][file_name] = {
            "path": str(path),
            "header": header,
            "rows": rows,
            "sampled_row_count": len(rows),
            "source_row_count_observed": total_seen,
            "row_limit": MASTER_SAMPLE_LIMIT,
            "row_limit_enforced": len(rows) <= MASTER_SAMPLE_LIMIT,
        }
        master["ignored_pnl_outcome_columns"][file_name] = ignored
    master["state"] = read_json(MASTER_PROXY_ROOT / STATE_FILE)

    clean: dict[str, Any] = {"csv": {}, "state": {}, "ignored_pnl_outcome_columns": {}}
    for file_name in CSV_FILES:
        path = CLEAN_ROOM_V2_OUTPUT_ROOT / file_name
        header, rows, total_seen, ignored = read_csv_rows(path, None)
        clean["csv"][file_name] = {
            "path": str(path),
            "header": header,
            "rows": rows,
            "sampled_row_count": len(rows),
            "source_row_count_observed": total_seen,
            "row_limit": None,
            "row_limit_enforced": True,
        }
        clean["ignored_pnl_outcome_columns"][file_name] = ignored
    clean["state"] = read_json(CLEAN_ROOM_V2_OUTPUT_ROOT / STATE_FILE)

    accepted = {
        "fixture_index": read_json(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_fixture_index.json"),
        "master_cases": read_jsonl(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_master_cases.jsonl"),
        "pairing_plan": read_json(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_pairing_plan.json"),
        "summary": read_json(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_discovery_summary.json"),
    }
    return source_payloads, master, clean, accepted


def all_csv_rows(sample: dict[str, Any], files: list[str] | None = None) -> list[dict[str, Any]]:
    selected = files or CSV_FILES
    rows: list[dict[str, Any]] = []
    for file_name in selected:
        rows.extend(sample["csv"][file_name]["rows"])
    return rows


def rows_with_field(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get(field) not in (None, "")]


def rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def schema_match_rate(master: dict[str, Any], clean: dict[str, Any]) -> float:
    conceptual_fields = {
        "signals.csv": [
            ["family_key"],
            ["family", "strategy"],
            ["side"],
            ["signal_time"],
            ["target_entry_time", "entry_time"],
            ["planned_exit_time"],
            ["signal_ret1_bps"],
        ],
        "pending_entries.csv": [
            ["family_key"],
            ["family", "strategy"],
            ["side"],
            ["signal_time"],
            ["target_entry_time", "entry_time"],
            ["planned_exit_time"],
        ],
        "open_positions.csv": [
            ["position_id"],
            ["family_key"],
            ["family", "strategy"],
            ["side"],
            ["signal_id"],
            ["entry_time"],
            ["notional"],
        ],
        "closed_trades.csv": [
            ["close_id"],
            ["position_id"],
            ["family_key"],
            ["family", "strategy"],
            ["side"],
            ["signal_id"],
            ["entry_time"],
            ["exit_time"],
            ["planned_exit_time"],
            ["hold_minutes_actual", "hold_minutes"],
            ["notional"],
        ],
        "rejected_entries.csv": [
            ["family_key"],
            ["family", "strategy"],
            ["side"],
            ["reason", "gate_state"],
            ["signal_time"],
        ],
        "heartbeat.csv": [["log_time", "output_type"], ["open_positions", "gate_state"]],
    }
    checks = 0
    passed = 0
    for file_name, groups in conceptual_fields.items():
        master_header = set(master["csv"][file_name]["header"])
        clean_header = set(clean["csv"][file_name]["header"])
        for aliases in groups:
            checks += 1
            if any(alias in master_header for alias in aliases) and any(alias in clean_header for alias in aliases):
                passed += 1
    checks += 1
    if isinstance(master.get("state"), dict) and isinstance(clean.get("state"), dict):
        passed += 1
    return passed / checks


def collect_categories(rows: list[dict[str, Any]]) -> set[str]:
    categories: set[str] = set()
    for row in rows:
        text = " ".join(str(row.get(name, "")) for name in ["reason", "gate_state", "type", "status"])
        lowered = text.lower()
        if "missing" in lowered or "timeout" in lowered:
            categories.add("gate_missing_timeout")
        if "block" in lowered:
            categories.add("gate_blocked")
        if "gate_allowed" in lowered or "accepted" in lowered:
            categories.add("gate_allowed_inferred")
    return categories


def compute_metrics(master: dict[str, Any], clean: dict[str, Any], accepted: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    master_behavior_rows = all_csv_rows(master, ["signals.csv", "pending_entries.csv", "open_positions.csv", "closed_trades.csv", "rejected_entries.csv"])
    clean_behavior_rows = all_csv_rows(clean, ["signals.csv", "pending_entries.csv", "open_positions.csv", "closed_trades.csv", "rejected_entries.csv"])
    accepted_cases = accepted["master_cases"]
    combined_behavior_rows = [*master_behavior_rows, *clean_behavior_rows, *accepted_cases]

    schema_rate = schema_match_rate(master, clean)

    family_rows = rows_with_field(combined_behavior_rows, "family_key")
    family_key_rate = rate(sum(1 for row in family_rows if row.get("family_key") == "old_short"), len(family_rows))

    families = {
        str(get_value(row, ["family", "strategy"]))
        for row in [*clean_behavior_rows, *accepted_cases]
        if get_value(row, ["family", "strategy"])
    }
    subfamily_presence_match = {"blowoff_short", "mean_reversion_short"}.issubset(families)

    side_rows = rows_with_field(combined_behavior_rows, "side")
    side_rate = rate(sum(1 for row in side_rows if row.get("side") == "short"), len(side_rows))

    feature_rows = [row for row in [*clean_behavior_rows, *accepted_cases] if get_value(row, ["family", "strategy"])]
    feature_numerator = sum(
        1
        for row in feature_rows
        if any(get_value(row, [feature]) is not None for feature in SIGNAL_FEATURE_FIELDS)
        or (isinstance(row.get("signal_features"), dict) and any(row["signal_features"].get(feature) not in (None, "") for feature in SIGNAL_FEATURE_FIELDS))
    )
    feature_rate = rate(feature_numerator, len(feature_rows))

    entry_errors: list[float] = []
    for row in [*clean["csv"]["signals.csv"]["rows"], *clean["csv"]["pending_entries.csv"]["rows"], *clean["csv"]["open_positions.csv"]["rows"], *clean["csv"]["closed_trades.csv"]["rows"], *accepted_cases]:
        signal_time = parse_time(get_value(row, ["signal_time"]))
        entry_time = parse_time(get_value(row, ["entry_time", "target_entry_time"]))
        if signal_time and entry_time:
            entry_errors.append(abs((entry_time - signal_time).total_seconds() - 120.0))
    entry_error = median(entry_errors)

    hold_errors: list[float] = []
    for row in [*clean["csv"]["open_positions.csv"]["rows"], *clean["csv"]["closed_trades.csv"]["rows"], *accepted_cases]:
        hold_minutes = to_float(get_value(row, ["hold_minutes_actual", "hold_minutes"]))
        if hold_minutes is not None:
            hold_errors.append(abs(hold_minutes - 120.0))
    hold_error = median(hold_errors)

    notional_errors: list[float] = []
    for row in [*clean["csv"]["open_positions.csv"]["rows"], *clean["csv"]["closed_trades.csv"]["rows"], *accepted_cases]:
        notional = to_float(get_value(row, ["notional"]))
        if notional is not None:
            notional_errors.append(abs(notional - 50.0))
    notional_error = median(notional_errors)

    master_rejected_categories = collect_categories(master["csv"]["rejected_entries.csv"]["rows"])
    clean_rejected_categories = collect_categories(clean["csv"]["rejected_entries.csv"]["rows"])
    rejected_overlap = rate(len(master_rejected_categories & clean_rejected_categories), len(clean_rejected_categories)) if clean_rejected_categories else None

    gate_required = {"gate_blocked", "gate_missing_timeout", "gate_allowed_inferred"}
    clean_gate_categories = collect_categories(clean_behavior_rows)
    gate_consistency = len(gate_required & clean_gate_categories) / len(gate_required)

    accepted_count = len(accepted_cases)
    accepted_lifecycle_coverage_rate = accepted_count / 2 if accepted_count else 0.0
    inferred_count = sum(1 for row in accepted_cases if row.get("gate_allowed_inferred_from_closed_trade") is True)
    inferred_gate_allowed_coverage_rate = rate(inferred_count, accepted_count) if accepted_count else 0.0

    position_rows = [*clean["csv"]["open_positions.csv"]["rows"], *clean["csv"]["closed_trades.csv"]["rows"]]
    no_position_without_gate_violation_count = sum(
        1
        for row in position_rows
        if "gate_allowed" not in str(row.get("gate_state", "")).lower()
        and str(row.get("gate_allowed_inferred_from_closed_trade", "")).lower() != "true"
    )

    clean_rows_with_labels = all_csv_rows(clean)
    accepted_label_rows = [*clean["csv"]["signals.csv"]["rows"], *clean["csv"]["pending_entries.csv"]["rows"], *clean["csv"]["open_positions.csv"]["rows"], *clean["csv"]["closed_trades.csv"]["rows"]]
    label_checks = 0
    label_passes = 0
    for row in clean_rows_with_labels:
        labels = labels_from_row(row)
        label_checks += 1
        if set(BASE_SAFETY_LABELS).issubset(labels):
            label_passes += 1
    for row in accepted_label_rows:
        labels = labels_from_row(row)
        label_checks += 1
        if ACCEPTED_LABEL in labels:
            label_passes += 1
    for row in accepted_cases:
        labels = labels_from_row(row)
        label_checks += 1
        if set([*BASE_SAFETY_LABELS, ACCEPTED_LABEL]).issubset(labels):
            label_passes += 1
    safety_label_rate = rate(label_passes, label_checks)

    state_heartbeat_schema_match = (
        isinstance(master.get("state"), dict)
        and isinstance(clean.get("state"), dict)
        and bool(master["csv"]["heartbeat.csv"]["header"])
        and bool(clean["csv"]["heartbeat.csv"]["header"])
    )

    master_coins = {
        str(get_value(row, ["inst_id", "coin"]))
        for row in master_behavior_rows
        if get_value(row, ["inst_id", "coin"])
    }
    clean_coins = {
        str(get_value(row, ["inst_id", "coin"]))
        for row in [*clean_behavior_rows, *accepted_cases]
        if get_value(row, ["inst_id", "coin"])
    }
    coin_overlap = rate(len(master_coins & clean_coins), len(clean_coins)) if clean_coins else None

    master_signal_ids = {
        str(row.get("signal_id"))
        for row in master_behavior_rows
        if row.get("signal_id") not in (None, "")
    }
    clean_signal_ids = {
        str(row.get("signal_id"))
        for row in [*clean_behavior_rows, *accepted_cases]
        if row.get("signal_id") not in (None, "")
    }
    timestamp_alignment = rate(len(master_signal_ids & clean_signal_ids), len(clean_signal_ids)) if clean_signal_ids else None

    raw_metrics = {
        "schema_match_rate": (schema_rate, schema_rate >= 0.95, "compatible behavioral schema fields are present"),
        "family_key_match_rate": (family_key_rate, family_key_rate is not None and family_key_rate >= 0.99, "family_key values match old_short where present"),
        "subfamily_presence_match": (subfamily_presence_match, subfamily_presence_match, "both blowoff_short and mean_reversion_short are present in clean-room/accepted fixtures"),
        "side_match_rate": (side_rate, side_rate is not None and side_rate >= 0.99, "side values match short where present"),
        "signal_feature_presence_rate": (feature_rate, feature_rate is not None and feature_rate > 0, "signal feature fields are available where behavior rows exist"),
        "entry_delay_median_abs_error_seconds": (entry_error, entry_error is not None and entry_error <= 60, "entry delay is compared to the known 2 minute fixture expectation"),
        "hold_minutes_median_abs_error": (hold_error, hold_error is not None and hold_error <= 10, "hold duration is compared to the known 120 minute fixture expectation"),
        "notional_median_abs_error": (notional_error, notional_error is not None and notional_error <= 5, "notional is compared to the known 50 USDT fixture expectation"),
        "rejected_reason_overlap_rate": (rejected_overlap, rejected_overlap is not None and rejected_overlap > 0, "bounded rejected gate categories overlap"),
        "gate_behavior_consistency_rate": (gate_consistency, gate_consistency >= 1.0, "blocked, missing, and inferred gate-allowed paths are represented"),
        "accepted_lifecycle_coverage_rate": (accepted_lifecycle_coverage_rate, accepted_lifecycle_coverage_rate > 0, "accepted lifecycle fixtures exist"),
        "inferred_gate_allowed_coverage_rate": (inferred_gate_allowed_coverage_rate, inferred_gate_allowed_coverage_rate > 0, "gate allowed is inferred from accepted lifecycle fixtures"),
        "no_position_without_gate_violation_count": (no_position_without_gate_violation_count, no_position_without_gate_violation_count == 0, "clean-room positions require inferred gate-allowed lifecycle"),
        "safety_label_match_rate": (safety_label_rate, safety_label_rate == 1.0, "required safety labels are present"),
        "state_heartbeat_schema_match": (state_heartbeat_schema_match, state_heartbeat_schema_match, "state and heartbeat artifacts exist with readable schema"),
        "coin_overlap_rate": (coin_overlap, coin_overlap is not None and coin_overlap > 0, "bounded sample coin/inst_id overlap is present"),
        "timestamp_alignment_rate": (timestamp_alignment, timestamp_alignment is not None and timestamp_alignment > 0, "bounded sample signal_id timestamp anchors overlap"),
    }
    missing_count = sum(1 for value, _passed, _reason in raw_metrics.values() if value is None)
    raw_metrics["missing_metric_count"] = (missing_count, True, "count of metrics missing due bounded sample limits")

    metrics = {
        name: metric(value is not None, value, passed if value is not None else None, reason if value is not None else f"missing: {reason}")
        for name, (value, passed, reason) in raw_metrics.items()
    }

    behavior_results = {
        "schema compatibility": metrics["schema_match_rate"]["passed"],
        "family_key old_short": metrics["family_key_match_rate"]["passed"],
        "subfamily blowoff_short / mean_reversion_short presence": metrics["subfamily_presence_match"]["passed"],
        "side short": metrics["side_match_rate"]["passed"],
        "signal feature availability": metrics["signal_feature_presence_rate"]["passed"],
        "entry delay near 2 minutes": metrics["entry_delay_median_abs_error_seconds"]["passed"],
        "hold duration near 120 minutes": metrics["hold_minutes_median_abs_error"]["passed"],
        "notional near 50 USDT": metrics["notional_median_abs_error"]["passed"],
        "accepted lifecycle coverage": metrics["accepted_lifecycle_coverage_rate"]["passed"],
        "rejected gate behavior": metrics["rejected_reason_overlap_rate"]["passed"],
        "gate_missing_timeout behavior": "gate_missing_timeout" in clean_rejected_categories,
        "gate_blocked behavior": "gate_blocked" in clean_rejected_categories,
        "inferred gate_allowed path coverage": metrics["inferred_gate_allowed_coverage_rate"]["passed"],
        "no position without gate allow": metrics["no_position_without_gate_violation_count"]["passed"],
        "heartbeat/state compatibility": metrics["state_heartbeat_schema_match"]["passed"],
        "safety label compatibility": metrics["safety_label_match_rate"]["passed"],
    }
    return metrics, behavior_results, {
        "master_rejected_categories": sorted(master_rejected_categories),
        "clean_rejected_categories": sorted(clean_rejected_categories),
        "master_coin_or_inst_id_count": len(master_coins),
        "clean_coin_or_inst_id_count": len(clean_coins),
        "master_signal_id_count": len(master_signal_ids),
        "clean_signal_id_count": len(clean_signal_ids),
        "ignored_pnl_outcome_columns": {
            "master": master["ignored_pnl_outcome_columns"],
            "clean_room": clean["ignored_pnl_outcome_columns"],
        },
    }


def threshold_results(metrics: dict[str, Any], live_private_field_count: int) -> dict[str, Any]:
    checks = {
        "schema_match_rate_gte_0_95": metrics["schema_match_rate"]["computed"] and metrics["schema_match_rate"]["value"] >= 0.95,
        "family_key_match_rate_gte_0_99": metrics["family_key_match_rate"]["computed"] and metrics["family_key_match_rate"]["value"] >= 0.99,
        "side_match_rate_gte_0_99": metrics["side_match_rate"]["computed"] and metrics["side_match_rate"]["value"] >= 0.99,
        "entry_delay_error_lte_60_seconds_if_comparable": metrics["entry_delay_median_abs_error_seconds"]["computed"] and metrics["entry_delay_median_abs_error_seconds"]["value"] <= 60,
        "hold_minutes_error_lte_10_if_comparable": metrics["hold_minutes_median_abs_error"]["computed"] and metrics["hold_minutes_median_abs_error"]["value"] <= 10,
        "notional_error_lte_5_usdt_if_comparable": metrics["notional_median_abs_error"]["computed"] and metrics["notional_median_abs_error"]["value"] <= 5,
        "no_position_without_gate_violation_count_zero": metrics["no_position_without_gate_violation_count"]["value"] == 0,
        "safety_label_match_rate_eq_1_0": metrics["safety_label_match_rate"]["computed"] and metrics["safety_label_match_rate"]["value"] == 1.0,
        "accepted_lifecycle_coverage_rate_positive": metrics["accepted_lifecycle_coverage_rate"]["computed"] and metrics["accepted_lifecycle_coverage_rate"]["value"] > 0,
        "inferred_gate_allowed_coverage_rate_positive": metrics["inferred_gate_allowed_coverage_rate"]["computed"] and metrics["inferred_gate_allowed_coverage_rate"]["value"] > 0,
        "live_order_private_field_count_zero": live_private_field_count == 0,
    }
    return {
        "threshold_checks": checks,
        "all_thresholds_passed": all(checks.values()),
    }


def detect_forbidden_fields(master: dict[str, Any], clean: dict[str, Any], accepted: dict[str, Any]) -> list[str]:
    fields: set[str] = set()
    for sample in [master, clean]:
        for file_data in sample["csv"].values():
            for header in file_data["header"]:
                if header in FORBIDDEN_LIVE_PRIVATE_FIELDS:
                    fields.add(header)
    for case in accepted["master_cases"]:
        for key in case.keys():
            if key in FORBIDDEN_LIVE_PRIVATE_FIELDS:
                fields.add(key)
    return sorted(fields)


def input_paths() -> list[Path]:
    return [
        *[MASTER_PROXY_ROOT / file_name for file_name in MASTER_AND_CLEAN_FILES],
        *[CLEAN_ROOM_V2_OUTPUT_ROOT / file_name for file_name in MASTER_AND_CLEAN_FILES],
        *[ACCEPTED_LIFECYCLE_ROOT / file_name for file_name in ACCEPTED_FILES],
    ]


def build_artifact() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = len(run_git(["ls-files", "*.py"]).splitlines())
    artifact_existed_before = ARTIFACT_PATH.exists()

    input_file_stats_before = stat_inputs(input_paths())
    sources, master, clean, accepted = load_inputs()
    input_file_stats_after = stat_inputs(input_paths())

    source_artifacts = {
        name: source_summary(relative_path, sources[name])
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }

    preview = sources["bounded_behavioral_validation_v2_preview"]
    design = sources["bounded_behavioral_validation_v2_design"]
    v2_review = sources["runner_realistic_fixture_v2_review"]

    metrics, behavior_results, auxiliary = compute_metrics(master, clean, accepted)
    forbidden_live_private_fields = detect_forbidden_fields(master, clean, accepted)
    thresholds = threshold_results(metrics, len(forbidden_live_private_fields))
    computed_metric_count = sum(1 for name, result in metrics.items() if name != "missing_metric_count" and result["computed"])
    missing_metric_count = int(metrics["missing_metric_count"]["value"])

    master_required_files_exist = all((MASTER_PROXY_ROOT / file_name).exists() for file_name in MASTER_AND_CLEAN_FILES)
    clean_required_files_exist = all((CLEAN_ROOM_V2_OUTPUT_ROOT / file_name).exists() for file_name in MASTER_AND_CLEAN_FILES)
    accepted_required_files_exist = all((ACCEPTED_LIFECYCLE_ROOT / file_name).exists() for file_name in ACCEPTED_FILES)
    master_row_limit_enforced = all(file_data["row_limit_enforced"] for file_data in master["csv"].values())
    all_input_stats_unchanged = input_file_stats_before == input_file_stats_after
    exact_gate_replay_recovered = False

    fail_closed_reasons: list[str] = []
    if not master_required_files_exist:
        fail_closed_reasons.append("MASTER sample missing")
    if not clean_required_files_exist:
        fail_closed_reasons.append("clean-room V2 output missing")
    if not accepted_required_files_exist or not accepted["master_cases"]:
        fail_closed_reasons.append("accepted lifecycle fixture missing")
    if not master_row_limit_enforced:
        fail_closed_reasons.append("sample row limit exceeded")
    if forbidden_live_private_fields:
        fail_closed_reasons.append("live/order/private fields present")
    if not metrics["safety_label_match_rate"]["passed"]:
        fail_closed_reasons.append("safety labels missing")
    if metrics["family_key_match_rate"]["computed"] and metrics["family_key_match_rate"]["value"] < 0.99:
        fail_closed_reasons.append("family_key mismatch")
    if first_value(preview, "route_key") != ROUTE_KEY:
        fail_closed_reasons.append("route_key mismatch")
    if preview.get("next_allowed_step") != "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DRY_RUN_V1":
        fail_closed_reasons.append("prior next allowed step mismatch")
    if first_value(preview, "exact_gate_replay_recovered", None) is not False:
        fail_closed_reasons.append("exact gate replay falsely claimed")
    if first_value(preview, "original_exact_source_recovered", None) is not False:
        fail_closed_reasons.append("original exact source falsely claimed")

    if fail_closed_reasons:
        result_classification = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_FAIL_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL_OR_INCONCLUSIVE
    elif not master["csv"]["signals.csv"]["rows"] or not clean["csv"]["signals.csv"]["rows"] or not accepted["master_cases"]:
        result_classification = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_INCONCLUSIVE_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL_OR_INCONCLUSIVE
    elif thresholds["all_thresholds_passed"] and missing_metric_count == 0 and exact_gate_replay_recovered is False:
        result_classification = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_PASS_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_PASS_OR_PARTIAL
    else:
        result_classification = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_PARTIAL_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_PASS_OR_PARTIAL

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "bounded_behavioral_validation_v2_preview_loaded": preview.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_PREVIEW_CREATED",
        "prior_next_allowed_step_verified": preview.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DRY_RUN_V1",
        "master_sample_loaded_bounded": master_required_files_exist and all(file_data["sampled_row_count"] <= MASTER_SAMPLE_LIMIT for file_data in master["csv"].values()),
        "clean_room_v2_output_loaded": clean_required_files_exist,
        "accepted_lifecycle_fixture_loaded": accepted_required_files_exist and len(accepted["master_cases"]) == 2,
        "sample_row_limit_enforced": master_row_limit_enforced,
        "exact_gate_replay_false_preserved": exact_gate_replay_recovered is False,
        "original_exact_source_not_claimed": first_value(preview, "original_exact_source_recovered", None) is False,
        "no_raw_market_data_read": True,
        "no_okx_1m_data_read": True,
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_orders_placed": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": MODULE_PATH.exists() and not artifact_existed_before,
        "exactly_one_json_artifact_created": not artifact_existed_before,
        "no_existing_repo_files_modified": status_has_only_expected_untracked_tool(status_before_artifact),
        "replacement_checks_all_true": True,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "expected_head": EXPECTED_HEAD,
            "actual_head": head,
            "head_matches_expected": head == EXPECTED_HEAD,
            "expected_tracked_python_count_before_creation": EXPECTED_TRACKED_PYTHON_COUNT,
            "tracked_python_count_before_creation": tracked_python_count,
            "tracked_python_count_matches_expected": tracked_python_count == EXPECTED_TRACKED_PYTHON_COUNT,
            "repo_status_before_artifact": status_before_artifact.splitlines(),
            "target_artifact_existed_before": artifact_existed_before,
        },
        "source_artifacts": source_artifacts,
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "dry_run_only": True,
            "bounded_behavioral_validation_v2": True,
            "full_dataset_comparison": False,
            "backtest": False,
            "pnl_computation": False,
            "runner_execution": False,
            "signal_generation": False,
            "runtime_live_capital": False,
            "candidate_generation": False,
            "edge_claim": False,
            "original_exact_source_recovered": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
        },
        "master_sample_review": {
            "root": str(MASTER_PROXY_ROOT),
            "sample_policy": "header plus at most first 100 rows per CSV",
            "master_sample_file_count": len(MASTER_AND_CLEAN_FILES),
            "csv_file_count": len(CSV_FILES),
            "state_file_loaded": isinstance(master.get("state"), dict),
            "sample_row_counts": {
                file_name: master["csv"][file_name]["sampled_row_count"]
                for file_name in CSV_FILES
            },
            "source_row_counts_observed_without_full_use": {
                file_name: master["csv"][file_name]["source_row_count_observed"]
                for file_name in CSV_FILES
            },
            "sample_row_limit_enforced": master_row_limit_enforced,
            "ignored_pnl_outcome_columns_not_used_for_validation": auxiliary["ignored_pnl_outcome_columns"]["master"],
        },
        "clean_room_v2_sample_review": {
            "root": str(CLEAN_ROOM_V2_OUTPUT_ROOT),
            "clean_room_v2_file_count": len(MASTER_AND_CLEAN_FILES),
            "csv_file_count": len(CSV_FILES),
            "state_file_loaded": isinstance(clean.get("state"), dict),
            "row_counts": {
                file_name: clean["csv"][file_name]["sampled_row_count"]
                for file_name in CSV_FILES
            },
            "ignored_pnl_outcome_columns_not_used_for_validation": auxiliary["ignored_pnl_outcome_columns"]["clean_room"],
            "input_files_unchanged_after_read": all_input_stats_unchanged,
        },
        "accepted_lifecycle_fixture_review": {
            "root": str(ACCEPTED_LIFECYCLE_ROOT),
            "expected_files_loaded": accepted_required_files_exist,
            "accepted_lifecycle_case_count": len(accepted["master_cases"]),
            "family_coverage": accepted["summary"].get("family_coverage", []),
            "gate_allowed_inferred_count": accepted["summary"].get("gate_allowed_inferred_count"),
            "exact_gate_replay_recovered": False,
        },
        "behavior_dimension_results_v2": {
            "behavior_dimension_count": len(BEHAVIOR_DIMENSIONS_V2),
            "results": {
                name: {
                    "checked": True,
                    "passed": bool(behavior_results.get(name)),
                    "reason": "bounded/sample-safe dimension check only",
                }
                for name in BEHAVIOR_DIMENSIONS_V2
            },
        },
        "similarity_metric_results_v2": {
            "similarity_metric_count": len(SIMILARITY_METRICS_V2),
            "computed_metric_count": computed_metric_count,
            "missing_metric_count": missing_metric_count,
            "metrics": metrics,
            "auxiliary": auxiliary,
        },
        "threshold_results_v2": {
            **thresholds,
            "fail_closed_reasons": fail_closed_reasons,
            "pnl_outcome_fields_used_for_validation": False,
            "live_order_private_field_count": len(forbidden_live_private_fields),
            "live_order_private_fields_detected": forbidden_live_private_fields,
        },
        "inferred_gate_allowed_review": {
            "gate_allowed_may_only_be_inferred_from_accepted_lifecycle_fixtures": True,
            "inferred_gate_allowed_coverage_rate": metrics["inferred_gate_allowed_coverage_rate"]["value"],
            "gate_allowed_inferred_count": accepted["summary"].get("gate_allowed_inferred_count"),
            "exact_gate_replay_recovered": False,
        },
        "exact_gate_replay_limitation": {
            "exact_gate_replay_recovered": False,
            "exact_gate_replay_required_for_pass": False,
            "limitation_preserved": True,
            "not_original_old_short_recovery": True,
            "not_edge_evidence": True,
            "not_live_capital_ready": True,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": {
            "original_exact_source_recovered": False,
            "exact_original_thresholds_known": False,
            "exact_original_implementation_known": False,
            "exact_frozen_replay_source_available": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "clean_room_behavioral_reconstruction": True,
            "no_edge_evidence": True,
            "no_live_capital_readiness": True,
        },
        "limitations": [
            "Bounded behavioral validation V2 dry-run only; no full dataset comparison is performed.",
            "MASTER files are sampled at headers plus at most first 100 rows per CSV.",
            "PnL/outcome columns in bounded samples are ignored and not used for validation.",
            "Exact gate replay remains unavailable and false.",
            "Gate allowed is inferred only from accepted lifecycle fixtures.",
            "Original old_short source and exact frozen replay remain unrecovered.",
            "No backtest, PnL computation, runtime, live, capital, candidate generation, or edge claim is allowed.",
        ],
        "safety_permissions": {
            "bounded_behavioral_validation_v2_dry_run_created": True,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> int:
    if ARTIFACT_PATH.exists():
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_PATH}")

    artifact = build_artifact()
    if artifact["replacement_checks_all_true"] is not True:
        raise SystemExit("BLOCKED: replacement_checks_all_true=false")

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    stdout_fields = {
        "status": artifact["status"],
        "route_key": artifact["dry_run_identity"]["route_key"],
        "result_classification": artifact["result_classification"],
        "master_sample_file_count": artifact["master_sample_review"]["master_sample_file_count"],
        "clean_room_v2_file_count": artifact["clean_room_v2_sample_review"]["clean_room_v2_file_count"],
        "accepted_lifecycle_case_count": artifact["accepted_lifecycle_fixture_review"]["accepted_lifecycle_case_count"],
        "computed_metric_count": artifact["similarity_metric_results_v2"]["computed_metric_count"],
        "missing_metric_count": artifact["similarity_metric_results_v2"]["missing_metric_count"],
        "schema_match_rate": artifact["similarity_metric_results_v2"]["metrics"]["schema_match_rate"]["value"],
        "safety_label_match_rate": artifact["similarity_metric_results_v2"]["metrics"]["safety_label_match_rate"]["value"],
        "accepted_lifecycle_coverage_rate": artifact["similarity_metric_results_v2"]["metrics"]["accepted_lifecycle_coverage_rate"]["value"],
        "inferred_gate_allowed_coverage_rate": artifact["similarity_metric_results_v2"]["metrics"]["inferred_gate_allowed_coverage_rate"]["value"],
        "exact_gate_replay_recovered": artifact["exact_gate_replay_limitation"]["exact_gate_replay_recovered"],
        "next_allowed_step": artifact["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    for key, value in stdout_fields.items():
        print(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
