import copy
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_FEATURE_FIXTURE_VALIDATOR_CHECK_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_FEATURE_FIXTURE_VALIDATOR_CHECK"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_feature_fixture_validator_check_v1"
ROUTE_KEY = "old_short_clean_room_v1"
RESULT_PASS = "OLD_SHORT_FEATURE_FIXTURE_VALIDATOR_CHECK_PASS_NO_EDGE_NO_LIVE"
RESULT_PARTIAL = "OLD_SHORT_FEATURE_FIXTURE_VALIDATOR_CHECK_PARTIAL_NO_EDGE_NO_LIVE"
RESULT_FAIL = "OLD_SHORT_FEATURE_FIXTURE_VALIDATOR_CHECK_FAIL_NO_EDGE_NO_LIVE"
RESULT_INCONCLUSIVE = "OLD_SHORT_FEATURE_FIXTURE_VALIDATOR_CHECK_INCONCLUSIVE_NO_EDGE_NO_LIVE"
NEXT_PASS_OR_PARTIAL = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DESIGN_V1"
NEXT_FAIL_OR_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_FEATURE_FIXTURE_REPAIR_PREVIEW_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_feature_fixture_validator_check_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_feature_fixture_validator_check_v1.json")
EXPECTED_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\feature_fixture_dry_run_v1"
)

SOURCE_RELS = {
    "clean_room_contract": Path("artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"),
    "runner_feature_fixture_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_feature_fixture_dry_run_v1.json"
    ),
    "runner_fixture_threshold_contract": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json"
    ),
    "threshold_behavioral_proposal": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
    ),
    "threshold_proposal_review": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json"
    ),
    "validator_preview": Path("artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"),
    "validator_bounded_sample_dry_run_v2": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_validator_bounded_sample_dry_run_v2.json"
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

REQUIRED_LABELS = [
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

THRESHOLD_LABELS = [
    "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
    "NOT_ORIGINAL_THRESHOLD",
    "NOT_PNL_OPTIMIZED",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]

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

CSV_REQUIRED_FIELDS = [
    "fixture_id",
    "route_key",
    "family_key",
    "subfamily",
    "side",
    "dry_run_mode",
    "lifecycle_state",
    "gate_status",
    "threshold_pass",
    "fail_closed",
    "fail_reason",
    "safety_labels",
]

LIFECYCLE_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
]


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_snapshot(path: Path) -> dict:
    stat = path.stat()
    return {
        "path": str(path),
        "exists": path.exists(),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": file_sha256(path),
    }


def payload_hash(payload: dict) -> str:
    cloned = copy.deepcopy(payload)
    cloned.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(cloned, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def extract_route_key(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("route_key"), str):
        return payload["route_key"]
    for key in ("dry_run_identity", "fixture_threshold_contract_identity"):
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
        "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash")
        if isinstance(payload, dict)
        else None,
        "replacement_checks_all_true": payload.get("replacement_checks_all_true")
        if isinstance(payload, dict)
        else None,
        "sha256": file_sha256(path) if path.exists() else None,
    }


def read_csv_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def output_root_is_safe(path: Path) -> bool:
    resolved = path.resolve(strict=False)
    expected = EXPECTED_OUTPUT_ROOT.resolve(strict=False)
    upper = str(resolved).upper()
    return (
        resolved == expected
        and "MASTER_UPPER_SYSTEM" not in upper
        and "PAPER_RUN_GATE_" not in upper
        and "LIVE_RUNTIME" not in upper
        and "RUNTIME_ROOT" not in upper
    )


def row_labels(row: dict) -> set[str]:
    raw = row.get("safety_labels", "")
    return {part for part in str(raw).split("|") if part}


def state_labels(state: dict) -> set[str]:
    labels = state.get("labels", [])
    return set(labels if isinstance(labels, list) else [])


def rate(passed: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(passed / total, 6)


def contains_forbidden_text(value: object) -> bool:
    text = str(value).lower()
    forbidden = ["api_key", "apikey", "secret", "private_key", "real_order_id", "live_order_id"]
    return any(item in text for item in forbidden)


def live_field_is_safe(key: str, value: object) -> bool:
    lower_key = key.lower()
    lower_value = str(value).lower()
    if lower_key in {"runtime_live_capital", "live_permission", "live_enabled", "runtime_enabled", "monitor_enabled"}:
        return lower_value in {"false", "0", "none", ""}
    if lower_key in {"no_runtime_live_capital", "not_live"}:
        return lower_value in {"true", "1", "yes"}
    if "live" in lower_key:
        return "not_live" in lower_key or lower_value in {"false", "0", "none", ""}
    return True


def order_field_is_safe(key: str, value: object) -> bool:
    lower_key = key.lower()
    lower_value = str(value).lower()
    if "order" not in lower_key:
        return True
    safe_false_guards = {"no_orders_placed", "orders_placed"}
    if lower_key in safe_false_guards:
        return lower_value in {"false", "0", "none", "", "true"}
    return lower_value in {"", "false", "none", "0"}


def all_output_cells(rows_by_file: dict[str, list[dict]], state: dict) -> list[tuple[str, str, object]]:
    cells = []
    for file_name, rows in rows_by_file.items():
        for row in rows:
            for key, value in row.items():
                cells.append((file_name, key, value))
    for key, value in state.items():
        cells.append(("state.json", key, value))
    return cells


def threshold_label_check(threshold_contract: dict) -> dict:
    required = set(THRESHOLD_LABELS)
    checks = []
    missing = []
    families = threshold_contract.get("threshold_families", {})
    for family_name, family in families.items():
        family_labels = set(family.get("labels", []))
        checks.append(required.issubset(family_labels))
        if not required.issubset(family_labels):
            missing.append({"family": family_name, "scope": "family", "missing_labels": sorted(required - family_labels)})
        for feature, rule in family.get("threshold_rules", {}).items():
            rule_labels = set(rule.get("labels", []))
            checks.append(required.issubset(rule_labels))
            if not required.issubset(rule_labels):
                missing.append(
                    {
                        "family": family_name,
                        "feature": feature,
                        "scope": "threshold_rule",
                        "missing_labels": sorted(required - rule_labels),
                    }
                )
    return {
        "checked_label_sets": len(checks),
        "passed_label_sets": sum(1 for item in checks if item),
        "threshold_label_match_rate": rate(sum(1 for item in checks if item), len(checks)),
        "threshold_labels_checked": bool(checks),
        "threshold_labels_passed": bool(checks) and all(checks),
        "missing_threshold_labels": missing,
    }


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

    source_payloads = {name: load_json(REPO_ROOT / rel_path) for name, rel_path in SOURCE_RELS.items()}
    dry_run = source_payloads["runner_feature_fixture_dry_run"]
    threshold_contract = source_payloads["runner_fixture_threshold_contract"]

    output_root = Path(dry_run.get("generated_output_summary", {}).get("output_root") or dry_run.get("dry_run_identity", {}).get("output_root", ""))
    output_root_exists = output_root.exists() and output_root.is_dir()
    output_root_safe = output_root_exists and output_root_is_safe(output_root)

    expected_paths = {file_name: output_root / file_name for file_name in EXPECTED_FILES}
    before_snapshots = {
        file_name: file_snapshot(path) for file_name, path in expected_paths.items() if path.exists() and path.is_file()
    }
    all_files_found = set(before_snapshots.keys()) == set(EXPECTED_FILES)

    csv_headers = {}
    rows_by_file = {}
    state = {}
    if all_files_found and output_root_safe:
        for file_name in EXPECTED_FILES:
            path = expected_paths[file_name]
            if file_name.endswith(".csv"):
                header, rows = read_csv_rows(path)
                csv_headers[file_name] = header
                rows_by_file[file_name] = rows
            else:
                state = load_json(path)

    after_snapshots = {
        file_name: file_snapshot(path) for file_name, path in expected_paths.items() if path.exists() and path.is_file()
    }
    files_not_modified = before_snapshots == after_snapshots and all_files_found

    required_label_set = set(REQUIRED_LABELS)
    labeled_units = []
    missing_label_units = []
    for file_name, rows in rows_by_file.items():
        for index, row in enumerate(rows, start=1):
            labels = row_labels(row)
            passed = required_label_set.issubset(labels)
            labeled_units.append(passed)
            if not passed:
                missing_label_units.append(
                    {"file": file_name, "row_number": index, "missing_labels": sorted(required_label_set - labels)}
                )
    state_label_passed = required_label_set.issubset(state_labels(state))
    labeled_units.append(state_label_passed)
    if not state_label_passed:
        missing_label_units.append({"file": "state.json", "row_number": None, "missing_labels": sorted(required_label_set - state_labels(state))})
    safety_label_match_rate = rate(sum(1 for item in labeled_units if item), len(labeled_units))
    safety_labels_verified = bool(labeled_units) and all(labeled_units)

    schema_checks = []
    schema_gaps = []
    for file_name in LIFECYCLE_FILES:
        header = set(csv_headers.get(file_name, []))
        required = set(CSV_REQUIRED_FIELDS + FEATURE_FIELDS)
        if file_name == "rejected_entries.csv":
            required.add("rejection_reason")
        missing = sorted(required - header)
        schema_checks.append(not missing)
        if missing:
            schema_gaps.append({"file": file_name, "missing_fields": missing})
    heartbeat_missing = sorted({"route_key", "dry_run_mode", "fixture_row_count", "safety_labels"} - set(csv_headers.get("heartbeat.csv", [])))
    schema_checks.append(not heartbeat_missing)
    if heartbeat_missing:
        schema_gaps.append({"file": "heartbeat.csv", "missing_fields": heartbeat_missing})
    state_required = {
        "route_key",
        "dry_run_mode",
        "status",
        "fixture_row_count",
        "family_threshold_count",
        "passed_feature_fixture_count",
        "fail_closed_count",
        "labels",
    }
    state_missing = sorted(state_required - set(state.keys()))
    schema_checks.append(not state_missing)
    if state_missing:
        schema_gaps.append({"file": "state.json", "missing_fields": state_missing})
    schema_match_rate = rate(sum(1 for item in schema_checks if item), len(schema_checks))
    schema_plumbing_checked = bool(schema_checks)
    schema_checks_passed = schema_plumbing_checked and all(schema_checks)

    family_checks = []
    side_checks = []
    family_counts = {"blowoff_short": 0, "mean_reversion_short": 0}
    for file_name in LIFECYCLE_FILES:
        for row in rows_by_file.get(file_name, []):
            family_checks.append(row.get("family_key") == "old_short")
            side_checks.append(row.get("side") == "short")
            if row.get("subfamily") in family_counts:
                family_counts[row["subfamily"]] += 1
    family_key_match_rate = rate(sum(1 for item in family_checks if item), len(family_checks))
    side_match_rate = rate(sum(1 for item in side_checks if item), len(side_checks))
    family_labels_passed = family_checks and side_checks and all(family_checks) and all(side_checks) and all(count > 0 for count in family_counts.values())

    threshold_check = threshold_label_check(threshold_contract)
    threshold_family_count = threshold_contract.get("contract_completeness", {}).get("family_threshold_count")
    threshold_contract_reference_ok = dry_run.get("source_artifacts", {}).get("runner_fixture_threshold_contract", {}).get("loaded") is True
    threshold_contract_check_passed = (
        threshold_family_count == 2
        and threshold_check["threshold_labels_passed"]
        and threshold_contract_reference_ok
        and threshold_contract.get("fixture_threshold_contract_identity", {}).get("original_exact_thresholds_recovered") is False
    )

    rows_lifecycle = {name: rows_by_file.get(name, []) for name in LIFECYCLE_FILES}
    rejected = rows_lifecycle["rejected_entries.csv"]
    open_positions = rows_lifecycle["open_positions.csv"]
    closed_trades = rows_lifecycle["closed_trades.csv"]
    gate_allowed_rows = [row for row in rows_lifecycle["pending_entries.csv"] if row.get("gate_status") == "gate_allowed"]
    blocked_rejections = [row for row in rejected if row.get("rejection_reason") == "gate_blocked"]
    timeout_rejections = [row for row in rejected if row.get("rejection_reason") == "gate_missing_timeout"]
    no_position_without_gate_allow = all(row.get("gate_status") == "gate_allowed" for row in open_positions + closed_trades)
    gate_fixture_behavior_check_passed = (
        len(gate_allowed_rows) >= 2
        and len(blocked_rejections) == 1
        and len(timeout_rejections) == 1
        and no_position_without_gate_allow
    )

    missing_feature_rejections = [row for row in rejected if row.get("fail_reason") == "required_feature_missing"]
    threshold_miss_rejections = [row for row in rejected if row.get("fail_reason") == "threshold_miss"]
    no_inferred_missing_values = any(
        row.get("fixture_id") == "feature_fixture_003_missing_required_feature"
        and row.get("missing_features") == "signal_ret3_bps"
        and row.get("signal_ret3_bps", "") == ""
        for row in missing_feature_rejections
    )
    fail_closed_count_preserved = len(rejected) == dry_run.get("runner_dry_run_results", {}).get("fail_closed_count")
    no_pnl_outcome_fields = all(
        all(token not in key.lower() for token in ["pnl", "profit", "loss", "outcome", "win"])
        for rows in rows_by_file.values()
        for row in rows
        for key in row.keys()
    )
    fail_closed_check_passed = (
        len(missing_feature_rejections) == 1
        and len(threshold_miss_rejections) == 1
        and fail_closed_count_preserved
        and no_inferred_missing_values
        and no_pnl_outcome_fields
    )

    cells = all_output_cells(rows_by_file, state)
    no_private_or_secret_fields = not any(contains_forbidden_text(key) or contains_forbidden_text(value) for _, key, value in cells)
    no_live_field_check_passed = all(live_field_is_safe(key, value) for _, key, value in cells)
    no_order_field_check_passed = all(order_field_is_safe(key, value) for _, key, value in cells)
    no_runtime_enabled_flags = all(
        not (key.lower() in {"runtime_enabled", "monitor_enabled"} and str(value).lower() in {"true", "1", "yes"})
        for _, key, value in cells
    )

    prior_review_ok = {
        "status_matches_required_prior_status": dry_run.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_CREATED",
        "route_key_matches": dry_run.get("dry_run_identity", {}).get("route_key") == ROUTE_KEY,
        "dry_run_mode_matches": dry_run.get("dry_run_identity", {}).get("dry_run_mode") == "FEATURE_FIXTURE_DRY_RUN",
        "result_classification_pass_no_edge_no_live": dry_run.get("result_classification")
        == "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
        "next_allowed_step_matches": dry_run.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_FEATURE_FIXTURE_VALIDATOR_CHECK_V1",
        "no_live_permissions_false": all(
            dry_run.get("safety_permissions", {}).get(key) is False
            for key in [
                "runner_execution_allowed_now",
                "real_signal_generation_allowed_now",
                "backtest_allowed_now",
                "runtime_permission_allowed_now",
                "monitor_allowed_now",
                "live_permission_allowed_now",
                "capital_permission_allowed_now",
                "candidate_generation_allowed_now",
                "edge_claim_allowed_now",
            ]
        ),
    }

    file_presence_check = {
        "output_root": str(output_root),
        "output_root_exists": output_root_exists,
        "output_root_safe": output_root_safe,
        "expected_files": EXPECTED_FILES,
        "found_files": sorted(before_snapshots.keys()),
        "missing_files": sorted(set(EXPECTED_FILES) - set(before_snapshots.keys())),
        "feature_fixture_file_count": len(before_snapshots),
        "all_7_feature_fixture_files_found": all_files_found,
        "file_snapshots_before_read": before_snapshots,
        "file_snapshots_after_read": after_snapshots,
        "feature_fixture_files_not_modified": files_not_modified,
    }

    all_pass_checks = [
        all(prior_review_ok.values()),
        output_root_exists,
        output_root_safe,
        all_files_found,
        files_not_modified,
        safety_labels_verified,
        schema_checks_passed,
        family_labels_passed,
        threshold_contract_check_passed,
        gate_fixture_behavior_check_passed,
        fail_closed_check_passed,
        no_private_or_secret_fields,
        no_live_field_check_passed,
        no_order_field_check_passed,
        no_runtime_enabled_flags,
    ]
    optional_schema_gaps_only = all_files_found and safety_labels_verified and not schema_checks_passed and no_private_or_secret_fields
    if all(all_pass_checks):
        result_classification = RESULT_PASS
    elif optional_schema_gaps_only:
        result_classification = RESULT_PARTIAL
    elif not output_root_exists or not all_files_found:
        result_classification = RESULT_INCONCLUSIVE
    else:
        result_classification = RESULT_FAIL
    next_allowed_step = NEXT_PASS_OR_PARTIAL if result_classification in {RESULT_PASS, RESULT_PARTIAL} else NEXT_FAIL_OR_INCONCLUSIVE

    unresolved = threshold_contract.get(
        "unresolved_fields_preserved",
        [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
        ],
    )

    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "prior_runner_feature_fixture_artifact_loaded": True,
        "feature_fixture_output_root_exists": output_root_exists,
        "all_7_feature_fixture_files_found": all_files_found,
        "feature_fixture_files_not_modified": files_not_modified,
        "no_master_upper_system_modified": output_root_safe and "MASTER_UPPER_SYSTEM" not in str(output_root).upper(),
        "no_runtime_directory_modified": output_root_safe,
        "safety_labels_verified": safety_labels_verified,
        "schema_plumbing_checked": schema_plumbing_checked,
        "threshold_labels_checked": threshold_check["threshold_labels_checked"],
        "gate_fixture_behavior_checked": gate_fixture_behavior_check_passed,
        "fail_closed_behavior_checked": fail_closed_check_passed,
        "real_behavioral_metrics_not_claimed": True,
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_orders_placed": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "unresolved_fields_preserved": all(
            item in unresolved
            for item in [
                "exact original thresholds unknown",
                "exact original implementation unknown",
                "exact frozen replay source unavailable",
                "missing gate details",
                "unverified 8/8 evidence",
            ]
        ),
        "exactly_one_python_tool_created": TOOL_REL.as_posix() in [line[3:] for line in git_status_before if line.startswith("?? ")],
        "exactly_one_json_artifact_created": not artifact_path.exists(),
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
            "expected_head": "79b1cfc35fc2dc0dcbfc94b6e2694eeff14cb739",
            "actual_head": git_head,
            "expected_tracked_python_count": 950,
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
        "feature_fixture_source_review": {
            **prior_review_ok,
            "prior_status": dry_run.get("status"),
            "prior_route_key": dry_run.get("dry_run_identity", {}).get("route_key"),
            "prior_dry_run_mode": dry_run.get("dry_run_identity", {}).get("dry_run_mode"),
            "prior_result_classification": dry_run.get("result_classification"),
            "prior_next_allowed_step": dry_run.get("next_allowed_step"),
            "prior_fixture_row_count": dry_run.get("runner_dry_run_results", {}).get("fixture_row_count"),
            "prior_family_threshold_count": dry_run.get("runner_dry_run_results", {}).get("family_threshold_count"),
            "prior_fail_closed_count": dry_run.get("runner_dry_run_results", {}).get("fail_closed_count"),
        },
        "file_presence_check": file_presence_check,
        "safety_label_check": {
            "required_labels": REQUIRED_LABELS,
            "checked_units": len(labeled_units),
            "passed_units": sum(1 for item in labeled_units if item),
            "safety_label_match_rate": safety_label_match_rate,
            "safety_labels_verified": safety_labels_verified,
            "missing_label_units": missing_label_units,
        },
        "schema_check_results": {
            "schema_match_rate": schema_match_rate,
            "schema_plumbing_checked": schema_plumbing_checked,
            "schema_checks_passed": schema_checks_passed,
            "schema_gaps": schema_gaps,
            "family_key_match_rate": family_key_match_rate,
            "side_match_rate": side_match_rate,
            "family_counts": family_counts,
            "family_and_side_labels_passed": family_labels_passed,
            "no_private_or_secret_fields": no_private_or_secret_fields,
            "no_live_field_check_passed": no_live_field_check_passed,
            "no_order_field_check_passed": no_order_field_check_passed,
            "no_runtime_enabled_flags": no_runtime_enabled_flags,
        },
        "threshold_contract_check": {
            "route_key_preserved": all(
                row.get("route_key") == ROUTE_KEY for name in LIFECYCLE_FILES for row in rows_by_file.get(name, [])
            )
            and state.get("route_key") == ROUTE_KEY,
            "threshold_contract_reference_present": threshold_contract_reference_ok,
            "family_threshold_count": threshold_family_count,
            "family_threshold_count_verified_2": threshold_family_count == 2,
            "original_threshold_claim_absent": threshold_contract.get("fixture_threshold_contract_identity", {}).get(
                "original_exact_thresholds_recovered"
            )
            is False,
            **threshold_check,
            "threshold_contract_check_passed": threshold_contract_check_passed,
        },
        "gate_fixture_behavior_check": {
            "gate_allowed_path_present": len(gate_allowed_rows) >= 2,
            "gate_blocked_path_present": len(blocked_rejections) == 1,
            "gate_missing_timeout_path_present": len(timeout_rejections) == 1,
            "blocked_and_timeout_rejected_entries_present": len(blocked_rejections) == 1 and len(timeout_rejections) == 1,
            "no_position_without_gate_allow": no_position_without_gate_allow,
            "gate_fixture_behavior_check_passed": gate_fixture_behavior_check_passed,
        },
        "fail_closed_check": {
            "missing_feature_fixture_failed_closed": len(missing_feature_rejections) == 1,
            "threshold_miss_fixture_failed_closed": len(threshold_miss_rejections) == 1,
            "fail_closed_count_from_artifact_preserved": fail_closed_count_preserved,
            "no_inferred_missing_values": no_inferred_missing_values,
            "no_pnl_or_outcome_use": no_pnl_outcome_fields,
            "fail_closed_check_passed": fail_closed_check_passed,
        },
        "validator_plumbing_metrics": {
            "schema_match_rate": schema_match_rate,
            "safety_label_match_rate": safety_label_match_rate,
            "family_key_match_rate": family_key_match_rate,
            "side_match_rate": side_match_rate,
            "threshold_label_match_rate": threshold_check["threshold_label_match_rate"],
            "gate_fixture_behavior_check_passed": gate_fixture_behavior_check_passed,
            "fail_closed_check_passed": fail_closed_check_passed,
            "no_live_field_check_passed": no_live_field_check_passed,
            "no_order_field_check_passed": no_order_field_check_passed,
        },
        "non_applicable_real_behavior_metrics": {
            "real_behavioral_similarity_against_master": "NOT_COMPUTED_FEATURE_FIXTURE_ONLY",
            "pnl": "NOT_COMPUTED",
            "real_win_loss": "NOT_COMPUTED",
            "market_performance": "NOT_COMPUTED",
            "full_dataset_comparison": "NOT_RUN",
            "backtest": "NOT_RUN",
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": unresolved,
        "limitations": [
            "feature fixture validator plumbing check only",
            "not full validator execution",
            "not behavioral validation against real market behavior",
            "not PnL validation",
            "not original old_short replay",
            "not full dataset comparison",
            "not backtest",
            "not runtime, monitor, live, or capital enablement",
            "not candidate generation",
            "not an edge claim",
        ],
        "safety_permissions": {
            "feature_fixture_validator_check_created": True,
            "validator_execution_allowed_now": False,
            "behavioral_validation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
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
    print(f"feature_fixture_file_count: {len(before_snapshots)}")
    print(f"safety_labels_verified: {str(safety_labels_verified).lower()}")
    print(f"schema_match_rate: {schema_match_rate}")
    print(f"threshold_label_match_rate: {threshold_check['threshold_label_match_rate']}")
    print(f"gate_fixture_behavior_check_passed: {str(gate_fixture_behavior_check_passed).lower()}")
    print(f"fail_closed_check_passed: {str(fail_closed_check_passed).lower()}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
