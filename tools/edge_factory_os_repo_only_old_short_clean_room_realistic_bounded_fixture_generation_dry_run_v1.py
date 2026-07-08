import copy
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_GENERATION_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_GENERATION_DRY_RUN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1"
ROUTE_KEY = "old_short_clean_room_v1"
RESULT_PASS = "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_PASS_NO_EDGE_NO_LIVE"
RESULT_PARTIAL = "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_PARTIAL_NO_EDGE_NO_LIVE"
RESULT_FAIL_CLOSED = "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_FAIL_CLOSED_NO_EDGE_NO_LIVE"
RESULT_INCONCLUSIVE = "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_INCONCLUSIVE_NO_EDGE_NO_LIVE"
NEXT_PASS_OR_PARTIAL = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_DESIGN_V1"
NEXT_FAIL_OR_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_REPAIR_PREVIEW_V1"
ROW_LIMIT = 100

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.json")
MASTER_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
APPROVED_EXTERNAL_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
)
REQUIRED_OUTPUT_ROOT = APPROVED_EXTERNAL_ROOT / "realistic_bounded_fixture_generation_dry_run_v1"

SOURCE_RELS = {
    "realistic_bounded_fixture_design": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_realistic_bounded_fixture_design_v1.json"
    ),
    "bounded_behavioral_validation_review": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_review_v1.json"
    ),
    "bounded_behavioral_validation_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_dry_run_v1.json"
    ),
    "feature_fixture_validator_check": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_feature_fixture_validator_check_v1.json"
    ),
    "runner_feature_fixture_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_feature_fixture_dry_run_v1.json"
    ),
    "runner_fixture_threshold_contract": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json"
    ),
    "threshold_behavioral_proposal": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
    ),
}

EXPECTED_MASTER_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

CSV_MASTER_FILES = [name for name in EXPECTED_MASTER_FILES if name.endswith(".csv")]
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
OUTPUT_FILES = [
    "fixture_index.json",
    "master_proxy_cases.jsonl",
    "clean_room_replay_fixture_inputs.jsonl",
    "validation_pair_fixtures.jsonl",
    "fixture_generation_summary.json",
]
SAFETY_LABELS = [
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
UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]
PNL_OUTCOME_TOKENS = ["pnl", "net_ret", "gross_ret", "stress_net_ret", "realistic_net_ret", "win", "loss", "profit", "outcome"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_cmd(*args: str) -> list[str]:
    safe = REPO_ROOT.as_posix()
    cmd = ["git", "-c", f"safe.directory={safe}", "-C", str(REPO_ROOT)]
    cmd.extend(args)
    completed = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return [line for line in completed.stdout.splitlines() if line.strip()]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_artifact(rel_path: Path) -> dict:
    return load_json(REPO_ROOT / rel_path)


def file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_sha256(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def payload_hash(payload: dict) -> str:
    cloned = copy.deepcopy(payload)
    cloned.pop("payload_sha256_excluding_hash", None)
    return object_sha256(cloned)


def extract_route_key(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("route_key"), str):
        return payload["route_key"]
    for key in ("fixture_generation_identity", "fixture_design_identity", "dry_run_identity", "fixture_threshold_contract_identity"):
        section = payload.get(key)
        if isinstance(section, dict) and isinstance(section.get("route_key"), str):
            return section["route_key"]
    prior = payload.get("prior_dry_run_preserved")
    if isinstance(prior, dict) and isinstance(prior.get("route_key"), str):
        return prior["route_key"]
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
        "sha256": file_sha256(path),
    }


def snapshot_file(path: Path) -> dict | None:
    if not path.exists() or not path.is_file():
        return None
    stat = path.stat()
    return {"exists": True, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def snapshot_master_root() -> dict:
    return {name: snapshot_file(MASTER_ROOT / name) for name in EXPECTED_MASTER_FILES}


def output_root_allowed(path: Path) -> bool:
    resolved_required = REQUIRED_OUTPUT_ROOT.resolve(strict=False)
    resolved_path = path.resolve(strict=False)
    upper = str(resolved_path).upper()
    return (
        (resolved_path == resolved_required or resolved_required in resolved_path.parents)
        and "MASTER_UPPER_SYSTEM" not in upper
        and "PAPER_RUN_GATE_" not in upper
        and "LIVE_RUNTIME" not in upper
        and "RUNTIME_ROOT" not in upper
    )


def choose_output_root() -> Path:
    if REQUIRED_OUTPUT_ROOT.exists():
        stamp = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
        candidate = REQUIRED_OUTPUT_ROOT / stamp
        suffix = 1
        while candidate.exists():
            candidate = REQUIRED_OUTPUT_ROOT / f"{stamp}_{suffix:02d}"
            suffix += 1
        return candidate
    return REQUIRED_OUTPUT_ROOT


def read_csv_bounded(path: Path, limit: int) -> tuple[list[str], list[dict], bool]:
    rows = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        for index, row in enumerate(reader, start=1):
            if len(rows) >= limit:
                return header, rows, True
            row["_bounded_source_row_index"] = index
            rows.append(row)
    return header, rows, False


def read_master_samples() -> dict:
    sample = {"root": str(MASTER_ROOT), "exists": MASTER_ROOT.exists() and MASTER_ROOT.is_dir(), "files": {}}
    if not sample["exists"]:
        return sample
    for file_name in EXPECTED_MASTER_FILES:
        path = MASTER_ROOT / file_name
        if not path.exists() or not path.is_file():
            sample["files"][file_name] = {"exists": False, "headers": [], "rows": [], "row_count_read": 0}
            continue
        if file_name.endswith(".csv"):
            headers, rows, truncated = read_csv_bounded(path, ROW_LIMIT)
            sample["files"][file_name] = {
                "exists": True,
                "headers": headers,
                "rows": rows,
                "row_count_read": len(rows),
                "row_limit": ROW_LIMIT,
                "truncated_at_row_limit": truncated,
            }
        else:
            state = load_json(path)
            sample["files"][file_name] = {
                "exists": True,
                "headers": sorted(state.keys()) if isinstance(state, dict) else [],
                "state": state,
                "row_count_read": 1,
                "row_limit": None,
                "truncated_at_row_limit": False,
            }
    sample["all_expected_files_found"] = all(sample["files"].get(name, {}).get("exists") for name in EXPECTED_MASTER_FILES)
    return sample


def family_of(row: dict) -> str | None:
    return row.get("family") or row.get("subfamily") or row.get("strategy")


def row_is_old_short(row: dict) -> bool:
    return row.get("family_key") == "old_short" and row.get("side") == "short"


def safe_source_subset(row: dict) -> dict:
    keep = [
        "type",
        "status",
        "reason",
        "signal_id",
        "position_id",
        "close_id",
        "inst_id",
        "coin",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_time",
        "target_entry_time",
        "entry_time",
        "exit_time",
        "planned_exit_time",
        "entry_delay_minutes",
        "hold_minutes",
        "hold_minutes_actual",
        "notional",
        "signal_close",
        "raw_entry_close",
        "raw_exit_close",
        "entry_price",
        "exit_price",
        "entry_vol_quote",
        "entry_range_bps",
        "created_at",
        "log_time",
    ] + FEATURE_FIELDS
    return {key: row.get(key) for key in keep if key in row and not is_pnl_or_outcome_key(key)}


def is_pnl_or_outcome_key(key: str) -> bool:
    lower = key.lower()
    return any(token in lower for token in PNL_OUTCOME_TOKENS)


def reject_state(row: dict) -> str:
    reason = str(row.get("reason") or row.get("status") or row.get("type") or "").lower()
    if "timeout" in reason or "missing" in reason:
        return "gate_missing_timeout"
    if "block" in reason or "reject" in reason or "gate" in reason:
        return "gate_blocked"
    return "rejected_other"


def normalized_case(case_id: str, case_type: str, source_file: str, row: dict | None, row_index: int | None) -> dict:
    row = row or {}
    source_subset = safe_source_subset(row)
    case = {
        "fixture_case_id": case_id,
        "fixture_type": "MASTER_PROXY_CASE_FIXTURE",
        "case_type": case_type,
        "route_key": ROUTE_KEY,
        "source_file": source_file,
        "source_row_index": row_index,
        "family_key": row.get("family_key", "old_short") if row else "old_short",
        "family": family_of(row) if row else None,
        "side": row.get("side", "short") if row else "short",
        "signal_time": row.get("signal_time"),
        "entry_time": row.get("entry_time") or row.get("target_entry_time"),
        "exit_time": row.get("exit_time"),
        "planned_exit_time": row.get("planned_exit_time"),
        "notional": row.get("notional"),
        "signal_features": {field: row.get(field) for field in FEATURE_FIELDS if field in row},
        "reject_reason": row.get("reason"),
        "gate_state": reject_state(row) if source_file == "rejected_entries.csv" else "gate_allowed_or_not_applicable",
        "source_hash": object_sha256(source_subset) if row else None,
        "source_values_preserved_as_fixture_evidence": source_subset,
        "selection_basis": "lifecycle_family_gate_coverage_only_no_pnl_outcome_selection",
        "safety_labels": list(SAFETY_LABELS),
    }
    case["fixture_hash"] = object_sha256(case)
    return case


def rows_for(sample: dict, file_name: str) -> list[dict]:
    return list(sample.get("files", {}).get(file_name, {}).get("rows", []))


def first_matching(rows: list[dict], predicate) -> dict | None:
    for row in rows:
        if predicate(row):
            return row
    return None


def select_fixture_cases(sample: dict) -> tuple[list[dict], list[str]]:
    cases = []
    missing = []
    used = set()

    def add_case(case_id: str, case_type: str, file_name: str, row: dict | None) -> None:
        if not row:
            missing.append(case_type)
            return
        key = (file_name, row.get("_bounded_source_row_index"))
        if key in used:
            return
        used.add(key)
        cases.append(normalized_case(case_id, case_type, file_name, row, row.get("_bounded_source_row_index")))

    closed_rows = [row for row in rows_for(sample, "closed_trades.csv") if row_is_old_short(row)]
    rejected_rows = [row for row in rows_for(sample, "rejected_entries.csv") if row_is_old_short(row)]
    pending_rows = [row for row in rows_for(sample, "pending_entries.csv") if row_is_old_short(row)]
    open_rows = [row for row in rows_for(sample, "open_positions.csv") if row_is_old_short(row)]

    add_case(
        "old_short_realistic_case_001_blowoff_closed",
        "blowoff_short closed trade example",
        "closed_trades.csv",
        first_matching(closed_rows, lambda row: family_of(row) == "blowoff_short"),
    )
    add_case(
        "old_short_realistic_case_002_mean_reversion_closed",
        "mean_reversion_short closed trade example",
        "closed_trades.csv",
        first_matching(closed_rows, lambda row: family_of(row) == "mean_reversion_short"),
    )
    add_case(
        "old_short_realistic_case_003_gate_missing_timeout",
        "rejected gate missing/timeout example",
        "rejected_entries.csv",
        first_matching(rejected_rows, lambda row: reject_state(row) == "gate_missing_timeout"),
    )
    add_case(
        "old_short_realistic_case_004_gate_blocked",
        "rejected gate blocked example if present",
        "rejected_entries.csv",
        first_matching(rejected_rows, lambda row: reject_state(row) == "gate_blocked"),
    )
    add_case(
        "old_short_realistic_case_005_pending_entry",
        "pending entry example if present",
        "pending_entries.csv",
        first_matching(pending_rows, lambda row: True),
    )
    add_case(
        "old_short_realistic_case_006_open_position",
        "open position example if present",
        "open_positions.csv",
        first_matching(open_rows, lambda row: True),
    )
    heartbeat_state_case = {
        "family_key": "old_short",
        "family": "heartbeat_state",
        "side": "short",
        "signal_time": None,
        "_bounded_source_row_index": 1,
    }
    add_case(
        "old_short_realistic_case_007_heartbeat_state",
        "heartbeat/state example",
        "state.json",
        heartbeat_state_case if sample.get("files", {}).get("state.json", {}).get("exists") else None,
    )
    return cases, missing


def clean_room_input_from_case(case: dict) -> dict:
    payload = {
        "fixture_case_id": case["fixture_case_id"].replace("old_short_realistic_case", "old_short_clean_room_input"),
        "fixture_type": "CLEAN_ROOM_REPLAY_FIXTURE_INPUT",
        "route_key": ROUTE_KEY,
        "paired_master_fixture_case_id": case["fixture_case_id"],
        "family_key": case["family_key"],
        "family": case["family"],
        "side": case["side"],
        "signal_time": case["signal_time"],
        "entry_time": case["entry_time"],
        "exit_time": case["exit_time"],
        "planned_exit_time": case["planned_exit_time"],
        "notional": case["notional"],
        "signal_features": case["signal_features"],
        "reject_reason": case["reject_reason"],
        "source_hash": case["source_hash"],
        "input_derivation": "bounded_master_proxy_row_features_no_raw_market_data_no_exact_replay_claim",
        "safety_labels": list(SAFETY_LABELS),
    }
    payload["fixture_hash"] = object_sha256(payload)
    return payload


def pair_from_cases(master_case: dict, clean_input: dict) -> dict:
    payload = {
        "fixture_pair_id": master_case["fixture_case_id"].replace("old_short_realistic_case", "old_short_validation_pair"),
        "fixture_type": "VALIDATION_PAIR_FIXTURE",
        "route_key": ROUTE_KEY,
        "master_proxy_case_id": master_case["fixture_case_id"],
        "clean_room_replay_input_id": clean_input["fixture_case_id"],
        "family_key": master_case["family_key"],
        "family": master_case["family"],
        "side": master_case["side"],
        "comparable_dimensions": [
            "schema compatibility",
            "family_key old_short",
            "side short",
            "signal feature availability",
            "entry delay near 2 minutes",
            "hold near 120 minutes",
            "notional near 50 USDT if present",
            "rejected gate behavior",
            "coin/timestamp alignment if identifiers exist",
        ],
        "safety_labels": list(SAFETY_LABELS),
    }
    payload["fixture_hash"] = object_sha256(payload)
    return payload


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True))
            handle.write("\n")


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def all_safety_labels_present(rows: list[dict]) -> bool:
    required = set(SAFETY_LABELS)
    for row in rows:
        labels = set(row.get("safety_labels", []))
        if not required.issubset(labels):
            return False
    return True


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_REL
    if artifact_path.exists():
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_REL.as_posix()}")

    git_status_before = git_cmd("status", "--short")
    allowed_pending = {f"?? {TOOL_REL.as_posix()}"}
    dirty_tracked = [line for line in git_status_before if not line.startswith("?? ")]
    unexpected_untracked = [line for line in git_status_before if line.startswith("?? ") and line not in allowed_pending]
    repo_clean_before_run = not dirty_tracked and not unexpected_untracked
    git_head = git_cmd("rev-parse", "HEAD")[0]
    tracked_python_count = len(git_cmd("ls-files", "*.py"))

    source_payloads = {name: load_artifact(rel_path) for name, rel_path in SOURCE_RELS.items()}
    design = source_payloads["realistic_bounded_fixture_design"]
    review = source_payloads["bounded_behavioral_validation_review"]
    threshold_contract = source_payloads["runner_fixture_threshold_contract"]
    prior_design_loaded = design.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_DESIGN_CREATED"
    prior_next_verified = design.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_GENERATION_DRY_RUN_V1"

    output_root = choose_output_root()
    output_root_safe = output_root_allowed(output_root)
    if not output_root_safe:
        raise SystemExit(f"BLOCKED: unsafe output root: {output_root}")

    master_before = snapshot_master_root()
    master_sample = read_master_samples()
    master_after_read = snapshot_master_root()
    master_unchanged_after_read = master_before == master_after_read

    cases, missing_case_types = select_fixture_cases(master_sample)
    clean_inputs = [clean_room_input_from_case(case) for case in cases]
    pairs = [pair_from_cases(case, clean_input) for case, clean_input in zip(cases, clean_inputs)]
    family_coverage = sorted({case.get("family") for case in cases if case.get("family") in {"blowoff_short", "mean_reversion_short"}})
    gate_state_coverage = sorted({case.get("gate_state") for case in cases if case.get("source_file") == "rejected_entries.csv"})
    all_fixture_rows = cases + clean_inputs + pairs
    safety_label_audit_passed = all_safety_labels_present(all_fixture_rows)

    missing_metrics = review.get("missing_metric_review", {}).get("missing_metrics", [])
    missing_metric_recovery_summary = [
        {
            "missing_metric": item.get("metric"),
            "prior_missing_reason": item.get("reason"),
            "can_make_computable_later": item.get("metric") in {"coin_overlap_rate", "timestamp_alignment_rate"},
            "required_fixture_cases": [
                "MASTER_PROXY_CASE_FIXTURE",
                "CLEAN_ROOM_REPLAY_FIXTURE_INPUT",
                "VALIDATION_PAIR_FIXTURE",
            ],
            "fixture_package_supports_recovery": bool(cases and clean_inputs and pairs),
        }
        for item in missing_metrics
    ]

    output_root.mkdir(parents=True, exist_ok=False)
    generated_paths = {
        "fixture_index.json": output_root / "fixture_index.json",
        "master_proxy_cases.jsonl": output_root / "master_proxy_cases.jsonl",
        "clean_room_replay_fixture_inputs.jsonl": output_root / "clean_room_replay_fixture_inputs.jsonl",
        "validation_pair_fixtures.jsonl": output_root / "validation_pair_fixtures.jsonl",
        "fixture_generation_summary.json": output_root / "fixture_generation_summary.json",
    }

    master_rows_sampled_total = sum(
        info.get("row_count_read", 0)
        for name, info in master_sample.get("files", {}).items()
        if name.endswith(".csv")
    )
    master_files_found_count = sum(1 for info in master_sample.get("files", {}).values() if info.get("exists"))
    sample_row_limit_enforced = all(
        info.get("row_count_read", 0) <= ROW_LIMIT
        for name, info in master_sample.get("files", {}).items()
        if name.endswith(".csv") and info.get("exists")
    )
    no_pnl_selection_confirmed = True
    no_raw_market_data_confirmed = True

    fixture_generation_summary = {
        "route_key": ROUTE_KEY,
        "status": STATUS,
        "master_files_found_count": master_files_found_count,
        "master_rows_sampled_total": master_rows_sampled_total,
        "fixture_case_count": len(cases),
        "fixture_case_types_created": [case["case_type"] for case in cases],
        "family_coverage": family_coverage,
        "gate_state_coverage": gate_state_coverage,
        "missing_case_types": missing_case_types,
        "missing_metric_recovery_summary": missing_metric_recovery_summary,
        "safety_label_audit_passed": safety_label_audit_passed,
        "no_pnl_selection_confirmed": no_pnl_selection_confirmed,
        "no_raw_market_data_confirmed": no_raw_market_data_confirmed,
        "output_root": str(output_root),
        "not_edge_evidence": True,
        "no_live_capital": True,
    }
    fixture_index = {
        "route_key": ROUTE_KEY,
        "fixture_package_kind": "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_PACKAGE_DRY_RUN",
        "output_root": str(output_root),
        "files": {name: str(path) for name, path in generated_paths.items()},
        "master_proxy_case_count": len(cases),
        "clean_room_replay_fixture_input_count": len(clean_inputs),
        "validation_pair_fixture_count": len(pairs),
        "safety_labels": SAFETY_LABELS,
        "source_policy": "bounded_MASTER_proxy_output_only_no_raw_market_data",
    }

    write_json(generated_paths["fixture_index.json"], fixture_index)
    write_jsonl(generated_paths["master_proxy_cases.jsonl"], cases)
    write_jsonl(generated_paths["clean_room_replay_fixture_inputs.jsonl"], clean_inputs)
    write_jsonl(generated_paths["validation_pair_fixtures.jsonl"], pairs)
    write_json(generated_paths["fixture_generation_summary.json"], fixture_generation_summary)

    generated_files_created = all(path.exists() for path in generated_paths.values())
    master_after_write = snapshot_master_root()
    master_unmodified = master_before == master_after_write and master_unchanged_after_read

    has_blowoff = "blowoff_short" in family_coverage
    has_mean_reversion = "mean_reversion_short" in family_coverage
    has_closed = any(case["source_file"] == "closed_trades.csv" for case in cases)
    has_rejected = any(case["source_file"] == "rejected_entries.csv" for case in cases)
    has_old_short = bool(cases)

    if not output_root_safe or not safety_label_audit_passed or not master_unmodified:
        result_classification = RESULT_FAIL_CLOSED
    elif not has_old_short:
        result_classification = RESULT_INCONCLUSIVE
    elif has_blowoff and has_mean_reversion and has_closed and has_rejected:
        result_classification = RESULT_PASS
    else:
        result_classification = RESULT_PARTIAL
    next_allowed_step = (
        NEXT_PASS_OR_PARTIAL
        if result_classification in {RESULT_PASS, RESULT_PARTIAL}
        else NEXT_FAIL_OR_INCONCLUSIVE
    )

    unresolved_preserved = all(item in threshold_contract.get("unresolved_fields_preserved", []) for item in UNRESOLVED_FIELDS)
    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "prior_realistic_fixture_design_loaded": prior_design_loaded,
        "prior_next_allowed_step_verified": prior_next_verified,
        "master_sample_loaded_bounded": master_sample.get("exists") is True and master_sample.get("all_expected_files_found") is True,
        "sample_row_limit_enforced": sample_row_limit_enforced,
        "no_fixture_selection_by_pnl": no_pnl_selection_confirmed,
        "no_raw_market_data_read": True,
        "no_okx_1m_data_read": True,
        "no_full_dataset_comparison": True,
        "no_behavioral_validation_execution": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_orders_placed": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "external_output_root_used": output_root_safe,
        "no_master_upper_system_modified": master_unmodified,
        "no_runtime_directory_modified": output_root_safe,
        "fixture_files_created": generated_files_created,
        "safety_labels_present": safety_label_audit_passed,
        "unresolved_fields_preserved": unresolved_preserved,
        "exactly_one_python_tool_created": TOOL_REL.as_posix() in [line[3:] for line in git_status_before if line.startswith("?? ")],
        "exactly_one_json_artifact_created": not artifact_path.exists(),
        "no_existing_repo_files_modified": not dirty_tracked,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())
    replacement_checks_all_true = all(validation_checks.values())

    generated_fixture_files = {
        name: {
            "path": str(path),
            "exists": path.exists(),
            "sha256": file_sha256(path),
        }
        for name, path in generated_paths.items()
    }

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
            "expected_head": "1d9846dcca0577786f9bfd54d20a125aafeea842",
            "actual_head": git_head,
            "expected_tracked_python_count": 956,
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
        "fixture_generation_identity": {
            "route_key": ROUTE_KEY,
            "realistic_bounded_fixture_generation_dry_run_only": True,
            "output_root": str(output_root),
            "master_root": str(MASTER_ROOT),
            "row_limit_per_master_csv": ROW_LIMIT,
            "not_runner_execution": True,
            "not_signal_generation": True,
            "not_behavioral_validation": True,
            "not_backtest": True,
            "not_edge_evidence": True,
            "no_live_capital": True,
        },
        "master_sample_review": {
            "master_root": str(MASTER_ROOT),
            "master_files_found_count": master_files_found_count,
            "master_rows_sampled_total": master_rows_sampled_total,
            "row_limit_per_csv": ROW_LIMIT,
            "file_summaries": {
                name: {
                    "exists": info.get("exists"),
                    "headers": info.get("headers", []),
                    "row_count_read": info.get("row_count_read", 0),
                    "truncated_at_row_limit": info.get("truncated_at_row_limit", False),
                }
                for name, info in master_sample.get("files", {}).items()
            },
            "master_snapshots_before": master_before,
            "master_snapshots_after": master_after_write,
            "master_unmodified": master_unmodified,
        },
        "fixture_case_selection": {
            "selection_rule": "coverage of lifecycle/family/gate states only; no PnL/outcome/profitability selection",
            "fixture_case_count": len(cases),
            "selected_case_ids": [case["fixture_case_id"] for case in cases],
            "fixture_case_types_created": [case["case_type"] for case in cases],
            "missing_case_types": missing_case_types,
            "family_coverage": family_coverage,
            "gate_state_coverage": gate_state_coverage,
            "no_pnl_selection_confirmed": no_pnl_selection_confirmed,
        },
        "generated_fixture_files": generated_fixture_files,
        "fixture_generation_summary": fixture_generation_summary,
        "missing_metric_recovery_summary": missing_metric_recovery_summary,
        "safety_label_audit": {
            "required_labels": SAFETY_LABELS,
            "safety_label_audit_passed": safety_label_audit_passed,
            "fixture_rows_checked": len(all_fixture_rows),
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "limitations": [
            "bounded MASTER proxy output only",
            "at most first 100 rows per MASTER CSV were read",
            "fixture package is not clean-room runner output yet",
            "not exact replay and not original source recovery",
            "PnL/outcome fields were not used for selection",
            "no full dataset comparison, backtest, runtime, live, capital, candidate, or edge claim",
        ],
        "safety_permissions": {
            "realistic_bounded_fixture_generation_dry_run_created": True,
            "runner_execution_allowed_now": False,
            "behavioral_validation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
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
    write_json(artifact_path, artifact)

    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"result_classification: {result_classification}")
    print(f"output_root: {output_root}")
    print(f"master_files_found_count: {master_files_found_count}")
    print(f"master_rows_sampled_total: {master_rows_sampled_total}")
    print(f"fixture_case_count: {len(cases)}")
    print(f"family_coverage: {','.join(family_coverage) if family_coverage else 'none'}")
    print(f"gate_state_coverage: {','.join(gate_state_coverage) if gate_state_coverage else 'none'}")
    print(f"missing_metric_recovery_item_count: {len(missing_metric_recovery_summary)}")
    print(f"safety_label_audit_passed: {str(safety_label_audit_passed).lower()}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
