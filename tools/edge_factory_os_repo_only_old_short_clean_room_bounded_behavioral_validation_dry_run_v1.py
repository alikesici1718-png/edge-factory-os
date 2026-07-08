import copy
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DRY_RUN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_dry_run_v1"
ROUTE_KEY = "old_short_clean_room_v1"
RESULT_PASS = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PASS_NO_EDGE_NO_LIVE"
RESULT_PARTIAL = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PARTIAL_NO_EDGE_NO_LIVE"
RESULT_FAIL = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_FAIL_NO_EDGE_NO_LIVE"
RESULT_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_INCONCLUSIVE_NO_EDGE_NO_LIVE"
NEXT_PARTIAL = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW_V1"
NEXT_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_GENERATION_DESIGN_V1"
NEXT_FAIL = "OLD_SHORT_CLEAN_ROOM_BEHAVIORAL_VALIDATION_REPAIR_PREVIEW_V1"
ROW_LIMIT = 100

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_dry_run_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_dry_run_v1.json")
MASTER_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
CLEAN_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\feature_fixture_dry_run_v1"
)

SOURCE_RELS = {
    "bounded_behavioral_validation_design": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_design_v1.json"
    ),
    "bounded_behavioral_validation_preview": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_preview_v1.json"
    ),
    "runner_feature_fixture_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_feature_fixture_dry_run_v1.json"
    ),
    "feature_fixture_validator_check": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_feature_fixture_validator_check_v1.json"
    ),
    "runner_fixture_threshold_contract": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json"
    ),
    "threshold_behavioral_proposal": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
    ),
}

EXPECTED_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

CSV_FILES = [name for name in EXPECTED_FILES if name.endswith(".csv")]
LIFECYCLE_FILES = ["signals.csv", "pending_entries.csv", "open_positions.csv", "closed_trades.csv", "rejected_entries.csv"]
SIGNAL_FEATURE_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
]
CLEAN_REQUIRED_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "NOT_ORIGINAL_OLD_SHORT",
    "PAPER_ONLY",
    "NOT_LIVE",
    "NOT_EDGE_EVIDENCE",
    "SYNTHETIC_FEATURE_FIXTURE",
    "NOT_MARKET_DATA",
    "NOT_BACKTEST",
    "NOT_REAL_TRADE",
]
UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_cmd(*args: str) -> list[str]:
    safe = REPO_ROOT.as_posix()
    cmd = ["git", "-c", f"safe.directory={safe}", "-C", str(REPO_ROOT)]
    cmd.extend(args)
    completed = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return [line for line in completed.stdout.splitlines() if line.strip()]


def load_json_file(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_artifact(rel_path: Path) -> dict:
    return load_json_file(REPO_ROOT / rel_path)


def payload_hash(payload: dict) -> str:
    cloned = copy.deepcopy(payload)
    cloned.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(cloned, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def external_snapshot(path: Path, include_hash: bool) -> dict:
    stat = path.stat()
    snap = {"exists": True, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    if include_hash:
        snap["sha256"] = file_hash(path)
    return snap


def extract_route_key(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("route_key"), str):
        return payload["route_key"]
    for key in ("dry_run_identity", "preview_identity", "validation_design_identity", "fixture_threshold_contract_identity"):
        section = payload.get(key)
        if isinstance(section, dict) and isinstance(section.get("route_key"), str):
            return section["route_key"]
    return None


def source_summary(rel_path: Path, payload: dict | None) -> dict:
    path = REPO_ROOT / rel_path
    return {
        "path": rel_path.as_posix(),
        "exists": path.exists(),
        "loaded": payload is not None,
        "artifact_kind": payload.get("artifact_kind") if isinstance(payload, dict) else None,
        "status": payload.get("status") if isinstance(payload, dict) else None,
        "route_key": extract_route_key(payload),
        "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash") if isinstance(payload, dict) else None,
        "replacement_checks_all_true": payload.get("replacement_checks_all_true") if isinstance(payload, dict) else None,
        "sha256": file_hash(path) if path.exists() else None,
    }


def read_csv_bounded(path: Path, limit: int | None) -> tuple[list[str], list[dict], bool]:
    rows = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        for row in reader:
            if limit is not None and len(rows) >= limit:
                return header, rows, True
            rows.append(row)
    return header, rows, False


def read_sample_root(root: Path, bounded_master: bool) -> dict:
    result = {
        "root": str(root),
        "exists": root.exists() and root.is_dir(),
        "files": {},
        "all_expected_files_found": False,
        "row_limit": ROW_LIMIT if bounded_master else None,
    }
    if not result["exists"]:
        return result
    for file_name in EXPECTED_FILES:
        path = root / file_name
        if not path.exists() or not path.is_file():
            result["files"][file_name] = {"exists": False, "headers": [], "rows": [], "row_count_read": 0}
            continue
        if file_name.endswith(".csv"):
            header, rows, truncated = read_csv_bounded(path, ROW_LIMIT if bounded_master else None)
            result["files"][file_name] = {
                "exists": True,
                "headers": header,
                "rows": rows,
                "row_count_read": len(rows),
                "row_limit_applied": bounded_master,
                "truncated_at_row_limit": truncated,
            }
        else:
            state = load_json_file(path)
            result["files"][file_name] = {
                "exists": True,
                "headers": sorted(state.keys()) if isinstance(state, dict) else [],
                "state": state,
                "row_count_read": 1,
                "row_limit_applied": False,
                "truncated_at_row_limit": False,
            }
    result["all_expected_files_found"] = all(result["files"].get(name, {}).get("exists") for name in EXPECTED_FILES)
    return result


def rows_for(sample: dict, file_name: str) -> list[dict]:
    return list(sample.get("files", {}).get(file_name, {}).get("rows", []))


def headers_for(sample: dict, file_name: str) -> set[str]:
    return set(sample.get("files", {}).get(file_name, {}).get("headers", []))


def state_for(sample: dict) -> dict:
    state = sample.get("files", {}).get("state.json", {}).get("state", {})
    return state if isinstance(state, dict) else {}


def route_rows(sample: dict) -> list[dict]:
    all_rows = []
    for file_name in LIFECYCLE_FILES:
        all_rows.extend(rows_for(sample, file_name))
    return all_rows


def median(values: list[float]) -> float | None:
    clean = sorted(value for value in values if value is not None)
    if not clean:
        return None
    middle = len(clean) // 2
    if len(clean) % 2:
        return clean[middle]
    return (clean[middle - 1] + clean[middle]) / 2.0


def parse_float(value: object) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_time(value: object) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value)
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def clean_labels(row: dict) -> set[str]:
    return {part for part in str(row.get("safety_labels", "")).split("|") if part}


def rate(passed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(passed / total, 6)


def metric(computed: bool, value, reason: str | None = None) -> dict:
    item = {"computed": computed, "value": value if computed else None}
    if not computed:
        item["reason"] = reason or "metric not computable from bounded samples"
    return item


def schema_match_rate(master: dict, clean: dict) -> dict:
    checks = []
    details = []
    for file_name in EXPECTED_FILES:
        master_headers = headers_for(master, file_name)
        clean_headers = headers_for(clean, file_name)
        exists = master.get("files", {}).get(file_name, {}).get("exists") and clean.get("files", {}).get(file_name, {}).get("exists")
        if file_name == "state.json":
            passed = bool(exists and state_for(master) and state_for(clean))
        elif file_name == "heartbeat.csv":
            passed = bool(exists and master_headers and clean_headers)
        else:
            semantic_checks = [
                "family_key" in master_headers and "family_key" in clean_headers,
                "side" in master_headers and "side" in clean_headers,
                ("family" in master_headers or "subfamily" in master_headers) and "subfamily" in clean_headers,
                all(feature in master_headers and feature in clean_headers for feature in SIGNAL_FEATURE_FIELDS)
                if file_name in {"signals.csv", "pending_entries.csv", "open_positions.csv", "closed_trades.csv", "rejected_entries.csv"}
                else True,
            ]
            passed = bool(exists and all(semantic_checks))
        checks.append(passed)
        details.append({"file": file_name, "schema_semantic_compatible": passed})
    return {"metric": metric(True, rate(sum(1 for item in checks if item), len(checks))), "details": details}


def family_key_rate(sample: dict) -> tuple[int, int]:
    rows = [row for row in route_rows(sample) if "family_key" in row]
    return sum(1 for row in rows if row.get("family_key") == "old_short"), len(rows)


def side_rate(sample: dict) -> tuple[int, int]:
    rows = [row for row in route_rows(sample) if "side" in row]
    return sum(1 for row in rows if row.get("side") == "short"), len(rows)


def subfamily_values(sample: dict, preferred_field: str) -> set[str]:
    values = set()
    fallback = "family" if preferred_field == "subfamily" else "subfamily"
    for row in route_rows(sample):
        value = row.get(preferred_field) or row.get(fallback)
        if value:
            values.add(value)
    return values


def feature_presence_rate(master: dict, clean: dict) -> dict:
    checks = []
    for file_name in LIFECYCLE_FILES:
        master_headers = headers_for(master, file_name)
        clean_headers = headers_for(clean, file_name)
        for feature in SIGNAL_FEATURE_FIELDS:
            checks.append(feature in master_headers and feature in clean_headers)
    return metric(True, rate(sum(1 for item in checks if item), len(checks)))


def entry_delay_seconds(sample: dict, master_sample: bool) -> list[float]:
    values = []
    if master_sample:
        for file_name in ["signals.csv", "pending_entries.csv", "open_positions.csv", "closed_trades.csv", "rejected_entries.csv"]:
            for row in rows_for(sample, file_name):
                minutes = parse_float(row.get("entry_delay_minutes"))
                if minutes is not None:
                    values.append(minutes * 60.0)
        return values
    for file_name in LIFECYCLE_FILES:
        for row in rows_for(sample, file_name):
            signal_time = parse_time(row.get("signal_time_utc"))
            entry_time = parse_time(row.get("entry_time_utc"))
            if signal_time and entry_time:
                values.append((entry_time - signal_time).total_seconds())
    return values


def hold_minutes(sample: dict, master_sample: bool) -> list[float]:
    values = []
    if master_sample:
        for file_name in ["signals.csv", "pending_entries.csv", "open_positions.csv", "rejected_entries.csv"]:
            for row in rows_for(sample, file_name):
                minutes = parse_float(row.get("hold_minutes"))
                if minutes is not None:
                    values.append(minutes)
        for row in rows_for(sample, "closed_trades.csv"):
            minutes = parse_float(row.get("hold_minutes_actual") or row.get("hold_minutes"))
            if minutes is not None:
                values.append(minutes)
        return values
    for file_name in LIFECYCLE_FILES:
        for row in rows_for(sample, file_name):
            entry_time = parse_time(row.get("entry_time_utc"))
            close_time = parse_time(row.get("close_time_utc"))
            if entry_time and close_time:
                values.append((close_time - entry_time).total_seconds() / 60.0)
    return values


def notional_values(sample: dict, master_sample: bool) -> list[float]:
    values = []
    field = "notional" if master_sample else "synthetic_notional_usdt"
    for file_name in LIFECYCLE_FILES:
        for row in rows_for(sample, file_name):
            value = parse_float(row.get(field))
            if value is not None:
                values.append(value)
    return values


def clean_safety_label_metric(clean: dict) -> dict:
    required = set(CLEAN_REQUIRED_LABELS)
    units = []
    missing = []
    for file_name in CSV_FILES:
        for index, row in enumerate(rows_for(clean, file_name), start=1):
            labels = clean_labels(row)
            passed = required.issubset(labels)
            units.append(passed)
            if not passed:
                missing.append({"file": file_name, "row_number": index, "missing": sorted(required - labels)})
    state_labels = set(state_for(clean).get("labels", []))
    state_passed = required.issubset(state_labels)
    units.append(state_passed)
    if not state_passed:
        missing.append({"file": "state.json", "row_number": None, "missing": sorted(required - state_labels)})
    return {
        "metric": metric(True, rate(sum(1 for item in units if item), len(units))),
        "verified": bool(units) and all(units),
        "missing_label_units": missing,
    }


def no_unsafe_fields(master: dict, clean: dict) -> dict:
    unsafe = []
    pnl_or_outcome_fields_seen_but_not_used = []
    allowed_order_guard_fields = {"no_orders_placed"}
    allowed_live_guard_fields = {
        "runtime_live_capital",
        "no_runtime_live_capital",
        "not_live",
        "live_permission_allowed_now",
        "live_trading_allowed",
    }
    for sample_name, sample in [("MASTER", master), ("clean_room", clean)]:
        for file_name in EXPECTED_FILES:
            for header in headers_for(sample, file_name):
                lower = header.lower()
                if "private" in lower or "api_key" in lower or "apikey" in lower or "secret" in lower:
                    unsafe.append({"sample": sample_name, "file": file_name, "field": header, "kind": "private_or_api"})
                if "order" in lower and lower not in allowed_order_guard_fields:
                    unsafe.append({"sample": sample_name, "file": file_name, "field": header, "kind": "order_field"})
                if "live" in lower and lower not in allowed_live_guard_fields:
                    unsafe.append({"sample": sample_name, "file": file_name, "field": header, "kind": "live_field"})
                if any(token in lower for token in ["pnl", "net_ret", "gross_ret", "outcome", "win", "loss"]):
                    pnl_or_outcome_fields_seen_but_not_used.append({"sample": sample_name, "file": file_name, "field": header})
    return {
        "no_live_order_private_fields": not unsafe,
        "unsafe_fields": unsafe,
        "pnl_or_outcome_fields_seen_but_not_used": pnl_or_outcome_fields_seen_but_not_used,
        "pnl_or_outcome_fields_used_for_validation": False,
    }


def gate_behavior(master: dict, clean: dict) -> dict:
    master_rejected = rows_for(master, "rejected_entries.csv")
    clean_rejected = rows_for(clean, "rejected_entries.csv")
    clean_open_closed = rows_for(clean, "open_positions.csv") + rows_for(clean, "closed_trades.csv")
    no_position_without_gate = all(row.get("gate_status") == "gate_allowed" for row in clean_open_closed)
    checks = [
        len(master_rejected) > 0,
        len(clean_rejected) > 0,
        any(row.get("rejection_reason") == "gate_blocked" for row in clean_rejected),
        any(row.get("rejection_reason") == "gate_missing_timeout" for row in clean_rejected),
        no_position_without_gate,
    ]
    return {
        "gate_behavior_consistency_rate": metric(True, rate(sum(1 for item in checks if item), len(checks))),
        "no_position_without_gate_violation_count": metric(True, 0 if no_position_without_gate else 1),
        "master_rejected_rows_sampled": len(master_rejected),
        "clean_rejected_rows": len(clean_rejected),
        "no_position_without_gate_allow": no_position_without_gate,
    }


def rejected_reason_overlap(master: dict, clean: dict) -> dict:
    master_reasons = {row.get("reason") for row in rows_for(master, "rejected_entries.csv") if row.get("reason")}
    clean_reasons = {
        row.get("rejection_reason") or row.get("fail_reason")
        for row in rows_for(clean, "rejected_entries.csv")
        if row.get("rejection_reason") or row.get("fail_reason")
    }
    if not master_reasons or not clean_reasons:
        return metric(False, None, "bounded samples do not expose comparable rejected reason fields")
    overlap = len(master_reasons & clean_reasons)
    union = len(master_reasons | clean_reasons)
    return metric(True, rate(overlap, union))


def state_heartbeat_match(master: dict, clean: dict) -> dict:
    checks = [
        bool(headers_for(master, "heartbeat.csv")),
        bool(headers_for(clean, "heartbeat.csv")),
        bool(state_for(master)),
        bool(state_for(clean)),
    ]
    return metric(True, rate(sum(1 for item in checks if item), len(checks)))


def absolute_error_metric(master_values: list[float], clean_values: list[float], unit: str) -> dict:
    master_median = median(master_values)
    clean_median = median(clean_values)
    if master_median is None or clean_median is None:
        return metric(False, None, f"{unit} not comparable in bounded samples")
    return metric(True, round(abs(clean_median - master_median), 6))


def build_metrics(master: dict, clean: dict) -> dict:
    schema = schema_match_rate(master, clean)
    safety = clean_safety_label_metric(clean)
    master_family_good, master_family_total = family_key_rate(master)
    clean_family_good, clean_family_total = family_key_rate(clean)
    master_side_good, master_side_total = side_rate(master)
    clean_side_good, clean_side_total = side_rate(clean)
    master_subfamilies = subfamily_values(master, "family")
    clean_subfamilies = subfamily_values(clean, "subfamily")
    expected_subfamilies = {"blowoff_short", "mean_reversion_short"}
    subfamily_presence = {
        "master_subfamilies": sorted(master_subfamilies),
        "clean_room_subfamilies": sorted(clean_subfamilies),
        "expected_subfamilies": sorted(expected_subfamilies),
        "value": rate(len(clean_subfamilies & expected_subfamilies), len(expected_subfamilies)),
        "note": "MASTER bounded proxy root is blowoff_short-only, so this metric is limited for mean_reversion_short.",
    }
    gate = gate_behavior(master, clean)
    metrics = {
        "schema_match_rate": schema["metric"],
        "family_key_match_rate": metric(
            master_family_total + clean_family_total > 0,
            rate(master_family_good + clean_family_good, master_family_total + clean_family_total),
            "family_key field absent from bounded samples",
        ),
        "subfamily_presence_match": metric(True, subfamily_presence["value"]),
        "side_match_rate": metric(
            master_side_total + clean_side_total > 0,
            rate(master_side_good + clean_side_good, master_side_total + clean_side_total),
            "side field absent from bounded samples",
        ),
        "signal_feature_presence_rate": feature_presence_rate(master, clean),
        "entry_delay_median_abs_error_seconds": absolute_error_metric(
            entry_delay_seconds(master, True), entry_delay_seconds(clean, False), "entry delay"
        ),
        "hold_minutes_median_abs_error": absolute_error_metric(hold_minutes(master, True), hold_minutes(clean, False), "hold minutes"),
        "notional_median_abs_error": absolute_error_metric(notional_values(master, True), notional_values(clean, False), "notional"),
        "rejected_reason_overlap_rate": rejected_reason_overlap(master, clean),
        "gate_behavior_consistency_rate": gate["gate_behavior_consistency_rate"],
        "no_position_without_gate_violation_count": gate["no_position_without_gate_violation_count"],
        "safety_label_match_rate": safety["metric"],
        "state_heartbeat_schema_match": state_heartbeat_match(master, clean),
        "coin_overlap_rate": metric(False, None, "clean-room synthetic feature fixture has no coin or inst_id field"),
        "timestamp_alignment_rate": metric(False, None, "synthetic fixture has no shared signal ids or aligned timestamps with MASTER sample"),
    }
    return {
        "metrics": metrics,
        "schema_details": schema["details"],
        "safety_details": safety,
        "subfamily_presence_details": subfamily_presence,
        "gate_details": gate,
    }


def snapshot_root(root: Path, include_hash: bool) -> dict:
    snaps = {}
    for file_name in EXPECTED_FILES:
        path = root / file_name
        if path.exists() and path.is_file():
            snaps[file_name] = external_snapshot(path, include_hash)
    return snaps


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_REL
    git_status_before = git_cmd("status", "--short")
    artifact_untracked_before_run = f"?? {ARTIFACT_REL.as_posix()}" in git_status_before
    if artifact_path.exists() and not artifact_untracked_before_run:
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_REL.as_posix()}")

    allowed_pending = {f"?? {TOOL_REL.as_posix()}"}
    if artifact_untracked_before_run:
        allowed_pending.add(f"?? {ARTIFACT_REL.as_posix()}")
    dirty_tracked = [line for line in git_status_before if not line.startswith("?? ")]
    unexpected_untracked = [line for line in git_status_before if line.startswith("?? ") and line not in allowed_pending]
    repo_clean_before_run = not dirty_tracked and not unexpected_untracked
    git_head = git_cmd("rev-parse", "HEAD")[0]
    tracked_python_count = len(git_cmd("ls-files", "*.py"))

    source_payloads = {name: load_artifact(rel_path) for name, rel_path in SOURCE_RELS.items()}
    preview = source_payloads["bounded_behavioral_validation_preview"]
    dry_run_source = source_payloads["runner_feature_fixture_dry_run"]
    prior_preview_loaded = preview.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_PREVIEW_CREATED"
    prior_next_verified = preview.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DRY_RUN_V1"

    master_before = snapshot_root(MASTER_ROOT, include_hash=False)
    clean_before = snapshot_root(CLEAN_ROOT, include_hash=True)
    master = read_sample_root(MASTER_ROOT, bounded_master=True)
    clean = read_sample_root(CLEAN_ROOT, bounded_master=False)
    master_after = snapshot_root(MASTER_ROOT, include_hash=False)
    clean_after = snapshot_root(CLEAN_ROOT, include_hash=True)
    external_files_not_modified = master_before == master_after and clean_before == clean_after

    metrics_bundle = build_metrics(master, clean)
    metrics = metrics_bundle["metrics"]
    computed_metric_count = sum(1 for item in metrics.values() if item["computed"])
    missing_metric_count = len(metrics) - computed_metric_count
    safety = metrics_bundle["safety_details"]
    unsafe_field_review = no_unsafe_fields(master, clean)

    clean_sample_is_synthetic = (
        dry_run_source.get("dry_run_identity", {}).get("synthetic_feature_fixture") is True
        or metrics["safety_label_match_rate"]["value"] == 1.0
    )
    enough_behavioral_metrics = computed_metric_count >= 10
    core_checks_pass = (
        master["all_expected_files_found"]
        and clean["all_expected_files_found"]
        and safety["verified"]
        and unsafe_field_review["no_live_order_private_fields"]
        and metrics["schema_match_rate"]["computed"]
        and metrics["schema_match_rate"]["value"] >= 0.95
        and metrics_bundle["gate_details"]["no_position_without_gate_allow"]
    )
    if not master["exists"] or not clean["exists"] or not master["all_expected_files_found"] or not clean["all_expected_files_found"]:
        result_classification = RESULT_INCONCLUSIVE
        next_allowed_step = NEXT_INCONCLUSIVE
    elif not core_checks_pass:
        result_classification = RESULT_FAIL
        next_allowed_step = NEXT_FAIL
    elif clean_sample_is_synthetic and enough_behavioral_metrics:
        result_classification = RESULT_PARTIAL
        next_allowed_step = NEXT_PARTIAL
    elif clean_sample_is_synthetic:
        result_classification = RESULT_INCONCLUSIVE
        next_allowed_step = NEXT_INCONCLUSIVE
    else:
        result_classification = RESULT_PASS
        next_allowed_step = NEXT_PARTIAL

    unresolved_preserved = all(item in preview.get("unresolved_fields_preserved", []) for item in UNRESOLVED_FIELDS)
    master_file_count = sum(1 for info in master["files"].values() if info.get("exists"))
    clean_file_count = sum(1 for info in clean["files"].values() if info.get("exists"))
    sample_row_limit_enforced = all(
        info.get("row_count_read", 0) <= ROW_LIMIT
        for name, info in master["files"].items()
        if name.endswith(".csv") and info.get("exists")
    )

    behavior_dimension_results = {
        "schema compatibility": metrics["schema_match_rate"],
        "family_key old_short": metrics["family_key_match_rate"],
        "subfamily blowoff_short / mean_reversion_short presence": metrics["subfamily_presence_match"],
        "side short": metrics["side_match_rate"],
        "signal feature availability": metrics["signal_feature_presence_rate"],
        "entry delay near 2 minutes if comparable fields exist": metrics["entry_delay_median_abs_error_seconds"],
        "hold near 120 minutes if comparable fields exist": metrics["hold_minutes_median_abs_error"],
        "notional near 50 USDT if comparable fields exist": metrics["notional_median_abs_error"],
        "rejected gate behavior": metrics["gate_behavior_consistency_rate"],
        "no position without gate allow": metrics["no_position_without_gate_violation_count"],
        "heartbeat/state compatibility": metrics["state_heartbeat_schema_match"],
        "safety label compatibility": metrics["safety_label_match_rate"],
    }

    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "bounded_behavioral_validation_preview_loaded": prior_preview_loaded,
        "prior_next_allowed_step_verified": prior_next_verified,
        "master_sample_loaded_bounded": master["exists"] and master["all_expected_files_found"],
        "clean_room_feature_fixture_loaded": clean["exists"] and clean["all_expected_files_found"],
        "sample_row_limit_enforced": sample_row_limit_enforced,
        "no_full_dataset_comparison": True,
        "no_raw_market_data_read": True,
        "no_okx_1m_data_read": True,
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
        "synthetic_fixture_limitation_preserved": clean_sample_is_synthetic and result_classification != RESULT_PASS,
        "unresolved_fields_preserved": unresolved_preserved,
        "exactly_one_python_tool_created": TOOL_REL.as_posix() in [line[3:] for line in git_status_before if line.startswith("?? ")],
        "exactly_one_json_artifact_created": (not artifact_path.exists()) or artifact_untracked_before_run,
        "no_existing_repo_files_modified": not dirty_tracked,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())
    replacement_checks_all_true = all(validation_checks.values())

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": {
            "name": MODULE_NAME,
            "path": TOOL_REL.as_posix(),
            "standard_library_only": True,
            "created_files": [TOOL_REL.as_posix(), ARTIFACT_REL.as_posix()],
            "modified_existing_files": [],
            "code_changed": True,
        },
        "source_checkpoint": {
            "generated_at_utc": now_utc(),
            "repo_root": str(REPO_ROOT),
            "expected_head": "d830e92a20e9a6bd3f449f811dfd7f7a1c8f3841",
            "actual_head": git_head,
            "expected_tracked_python_count": 953,
            "actual_tracked_python_count": tracked_python_count,
            "repo_clean_before_run": repo_clean_before_run,
            "git_status_before_run": git_status_before,
            "dirty_tracked_before_run": dirty_tracked,
            "allowed_pending_before_run": sorted(allowed_pending),
            "unexpected_untracked_before_run": unexpected_untracked,
        },
        "source_artifacts": {
            name: source_summary(rel_path, source_payloads.get(name)) for name, rel_path in SOURCE_RELS.items()
        },
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "bounded_behavioral_validation_dry_run_only": True,
            "full_dataset_comparison": False,
            "backtest": False,
            "runner_execution": False,
            "signal_generation": False,
            "pnl_computation": False,
            "not_edge_evidence": True,
            "no_live_capital": True,
            "master_sample_row_limit_per_csv": ROW_LIMIT,
            "clean_room_sample_type": "synthetic_feature_fixture",
        },
        "master_sample_review": {
            "root": str(MASTER_ROOT),
            "bounded_read": True,
            "row_limit_per_csv": ROW_LIMIT,
            "file_count": master_file_count,
            "all_expected_files_found": master["all_expected_files_found"],
            "file_summaries": {
                name: {
                    "exists": info.get("exists"),
                    "headers": info.get("headers", []),
                    "row_count_read": info.get("row_count_read", 0),
                    "row_limit_applied": info.get("row_limit_applied", False),
                    "truncated_at_row_limit": info.get("truncated_at_row_limit", False),
                }
                for name, info in master["files"].items()
            },
            "snapshots_before": master_before,
            "snapshots_after": master_after,
        },
        "clean_room_sample_review": {
            "root": str(CLEAN_ROOT),
            "feature_fixture_only": True,
            "synthetic_feature_fixture": clean_sample_is_synthetic,
            "file_count": clean_file_count,
            "all_expected_files_found": clean["all_expected_files_found"],
            "file_summaries": {
                name: {
                    "exists": info.get("exists"),
                    "headers": info.get("headers", []),
                    "row_count_read": info.get("row_count_read", 0),
                    "row_limit_applied": info.get("row_limit_applied", False),
                }
                for name, info in clean["files"].items()
            },
            "snapshots_before": clean_before,
            "snapshots_after": clean_after,
            "external_files_not_modified": external_files_not_modified,
        },
        "safety_label_review": {
            "required_clean_room_labels": CLEAN_REQUIRED_LABELS,
            "safety_label_match_rate": metrics["safety_label_match_rate"],
            "safety_labels_verified": safety["verified"],
            "missing_label_units": safety["missing_label_units"],
            **unsafe_field_review,
        },
        "behavior_dimension_results": behavior_dimension_results,
        "similarity_metric_results": metrics,
        "synthetic_fixture_limitations": {
            "clean_room_sample_is_synthetic_feature_fixture": clean_sample_is_synthetic,
            "real_clean_room_runner_output_from_market_candles_available": False,
            "full_behavioral_pass_allowed_from_synthetic_fixture": False,
            "real_behavioral_equivalence_proven": False,
            "profitability_or_edge_proven": False,
            "live_readiness_proven": False,
            "limitation_preserved": result_classification != RESULT_PASS,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "limitations": [
            "MASTER sample read is bounded to header plus at most first 100 rows per CSV",
            "clean-room sample is a synthetic feature fixture, not market-candle runner output",
            "no real behavioral equivalence is claimed",
            "PnL/outcome fields in MASTER closed_trades are not used for validation",
            "no full dataset comparison, backtest, runtime, live, capital, candidate, or edge permission",
        ],
        "safety_permissions": {
            "bounded_behavioral_validation_dry_run_created": True,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": None,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    with artifact_path.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=False)
        handle.write("\n")

    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"result_classification: {result_classification}")
    print(f"master_sample_file_count: {master_file_count}")
    print(f"clean_room_sample_file_count: {clean_file_count}")
    print(f"computed_metric_count: {computed_metric_count}")
    print(f"missing_metric_count: {missing_metric_count}")
    print(f"safety_label_match_rate: {metrics['safety_label_match_rate']['value']}")
    print(f"schema_match_rate: {metrics['schema_match_rate']['value']}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
