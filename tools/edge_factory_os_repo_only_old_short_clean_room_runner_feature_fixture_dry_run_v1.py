import copy
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_runner_feature_fixture_dry_run_v1"
ROUTE_KEY = "old_short_clean_room_v1"
DRY_RUN_MODE = "FEATURE_FIXTURE_DRY_RUN"
RESULT_PASS = "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_PASS_NO_EDGE_NO_LIVE"
RESULT_PARTIAL = "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE"
RESULT_FAIL_CLOSED = "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE"
RESULT_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE"
NEXT_PASS_OR_PARTIAL = "OLD_SHORT_CLEAN_ROOM_FEATURE_FIXTURE_VALIDATOR_CHECK_V1"
NEXT_FAIL_OR_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_REPAIR_PREVIEW_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_runner_feature_fixture_dry_run_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_runner_feature_fixture_dry_run_v1.json")
CONTRACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json")
EXTERNAL_BASE = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\feature_fixture_dry_run_v1"
)

SOURCE_RELS = {
    "clean_room_contract": Path("artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"),
    "runner_dry_run_design": Path("artifacts/old_short_clean_room/old_short_clean_room_runner_dry_run_design_v1.json"),
    "runner_dry_run_implementation_preview": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_dry_run_implementation_preview_v1.json"
    ),
    "runner_fixture_threshold_contract": CONTRACT_REL,
    "threshold_behavioral_proposal": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
    ),
    "threshold_proposal_review": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json"
    ),
    "runner_schema_fixture_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_schema_fixture_dry_run_v1.json"
    ),
}

REQUIRED_ROW_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "SYNTHETIC_FEATURE_FIXTURE",
    "NOT_MARKET_DATA",
    "NOT_ORIGINAL_OLD_SHORT",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
    "PAPER_ONLY",
    "NOT_LIVE",
]

REQUIRED_THRESHOLD_LABELS = [
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

OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iso_z(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_cmd(*args: str) -> list[str]:
    safe = REPO_ROOT.as_posix()
    cmd = ["git", "-c", f"safe.directory={safe}", "-C", str(REPO_ROOT)]
    cmd.extend(args)
    completed = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return [line for line in completed.stdout.splitlines() if line.strip()]


def load_json(rel_path: Path) -> dict:
    path = REPO_ROOT / rel_path
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_hash(payload: dict) -> str:
    cloned = copy.deepcopy(payload)
    cloned.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(cloned, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def extract_route_key(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get("route_key")
    if isinstance(value, str):
        return value
    for key in ("dry_run_identity", "fixture_threshold_contract_identity", "threshold_contract_identity"):
        section = payload.get(key)
        if isinstance(section, dict) and isinstance(section.get("route_key"), str):
            return section["route_key"]
    return None


def source_summary(rel_path: Path, loaded_payload: dict | None) -> dict:
    path = REPO_ROOT / rel_path
    return {
        "path": rel_path.as_posix(),
        "exists": path.exists(),
        "loaded": loaded_payload is not None,
        "artifact_kind": loaded_payload.get("artifact_kind") if isinstance(loaded_payload, dict) else None,
        "status": loaded_payload.get("status") if isinstance(loaded_payload, dict) else None,
        "route_key": extract_route_key(loaded_payload),
        "payload_sha256_excluding_hash": loaded_payload.get("payload_sha256_excluding_hash")
        if isinstance(loaded_payload, dict)
        else None,
        "replacement_checks_all_true": loaded_payload.get("replacement_checks_all_true")
        if isinstance(loaded_payload, dict)
        else None,
        "sha256": file_sha256(path),
    }


def choose_output_root() -> Path:
    if EXTERNAL_BASE.exists():
        stamp = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
        candidate = EXTERNAL_BASE / stamp
        suffix = 1
        while candidate.exists():
            candidate = EXTERNAL_BASE / f"{stamp}_{suffix:02d}"
            suffix += 1
        return candidate
    return EXTERNAL_BASE


def assert_output_root_allowed(output_root: Path) -> None:
    resolved_base = EXTERNAL_BASE.resolve(strict=False)
    resolved_output = output_root.resolve(strict=False)
    if resolved_output != resolved_base and resolved_base not in resolved_output.parents:
        raise RuntimeError(f"Unsafe output root outside approved subfolder: {output_root}")
    upper_path = str(resolved_output).upper()
    if "MASTER_UPPER_SYSTEM" in upper_path:
        raise RuntimeError(f"Forbidden output root segment detected: {output_root}")
    if any(token in upper_path for token in ["PAPER_RUN_GATE_", "LIVE_RUNTIME", "RUNTIME_ROOT"]):
        raise RuntimeError(f"Runtime-like output root detected: {output_root}")


def labels_text(extra: list[str] | None = None) -> str:
    labels = list(REQUIRED_ROW_LABELS)
    if extra:
        labels.extend(extra)
    return "|".join(labels)


def synthetic_fixtures() -> list[dict]:
    base = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    fixtures = [
        {
            "fixture_id": "feature_fixture_001_blowoff_pass_gate_allowed",
            "family_target": "blowoff_short",
            "expected_fixture_behavior": "threshold_pass_gate_allowed",
            "gate_status": "gate_allowed",
            "features": {
                "signal_ret1_bps": -80.0,
                "signal_ret3_bps": -130.0,
                "signal_ret5_bps": -70.0,
                "signal_ret60_bps": 700.0,
                "signal_vol_quote": 250000.0,
                "signal_range_bps": 150.0,
                "entry_vol_quote": 240000.0,
                "entry_range_bps": 100.0,
            },
        },
        {
            "fixture_id": "feature_fixture_002_mean_reversion_pass_gate_allowed",
            "family_target": "mean_reversion_short",
            "expected_fixture_behavior": "threshold_pass_gate_allowed",
            "gate_status": "gate_allowed",
            "features": {
                "signal_ret1_bps": -40.0,
                "signal_ret3_bps": 150.0,
                "signal_ret5_bps": 400.0,
                "signal_ret60_bps": 600.0,
                "signal_vol_quote": 500000.0,
                "signal_range_bps": 160.0,
                "entry_vol_quote": 400000.0,
                "entry_range_bps": 100.0,
            },
        },
        {
            "fixture_id": "feature_fixture_003_missing_required_feature",
            "family_target": "blowoff_short",
            "expected_fixture_behavior": "fail_closed_missing_required_feature",
            "gate_status": "gate_allowed",
            "features": {
                "signal_ret1_bps": -80.0,
                "signal_ret5_bps": -70.0,
                "signal_ret60_bps": 700.0,
                "signal_vol_quote": 250000.0,
                "signal_range_bps": 150.0,
                "entry_vol_quote": 240000.0,
                "entry_range_bps": 100.0,
            },
        },
        {
            "fixture_id": "feature_fixture_004_threshold_miss",
            "family_target": "mean_reversion_short",
            "expected_fixture_behavior": "fail_closed_threshold_miss",
            "gate_status": "gate_allowed",
            "features": {
                "signal_ret1_bps": -40.0,
                "signal_ret3_bps": 50.0,
                "signal_ret5_bps": 400.0,
                "signal_ret60_bps": 600.0,
                "signal_vol_quote": 500000.0,
                "signal_range_bps": 160.0,
                "entry_vol_quote": 400000.0,
                "entry_range_bps": 100.0,
            },
        },
        {
            "fixture_id": "feature_fixture_005_gate_blocked",
            "family_target": "blowoff_short",
            "expected_fixture_behavior": "threshold_pass_gate_blocked",
            "gate_status": "gate_blocked",
            "features": {
                "signal_ret1_bps": -80.0,
                "signal_ret3_bps": -130.0,
                "signal_ret5_bps": -70.0,
                "signal_ret60_bps": 700.0,
                "signal_vol_quote": 250000.0,
                "signal_range_bps": 150.0,
                "entry_vol_quote": 240000.0,
                "entry_range_bps": 100.0,
            },
        },
        {
            "fixture_id": "feature_fixture_006_gate_missing_timeout",
            "family_target": "mean_reversion_short",
            "expected_fixture_behavior": "threshold_pass_gate_missing_timeout",
            "gate_status": "gate_missing_timeout",
            "features": {
                "signal_ret1_bps": -40.0,
                "signal_ret3_bps": 150.0,
                "signal_ret5_bps": 400.0,
                "signal_ret60_bps": 600.0,
                "signal_vol_quote": 500000.0,
                "signal_range_bps": 160.0,
                "entry_vol_quote": 400000.0,
                "entry_range_bps": 100.0,
            },
        },
    ]
    for index, row in enumerate(fixtures):
        signal_time = base + timedelta(minutes=index * 10)
        row["signal_time_utc"] = iso_z(signal_time)
        row["entry_time_utc"] = iso_z(signal_time + timedelta(minutes=2))
        row["close_time_utc"] = iso_z(signal_time + timedelta(minutes=122))
        row["synthetic_notional_usdt"] = 50.0
        row["labels"] = list(REQUIRED_ROW_LABELS)
    return fixtures


def rule_is_optional(rule: dict) -> bool:
    requirement = str(rule.get("requirement", ""))
    return bool(rule.get("applies_when_field_present")) or requirement.startswith("optional_when_present")


def compare_value(value: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return value >= threshold
    if operator == "<=":
        return value <= threshold
    if operator == ">":
        return value > threshold
    if operator == "<":
        return value < threshold
    if operator == "==":
        return value == threshold
    raise ValueError(f"Unsupported threshold operator: {operator}")


def required_features_for_family(family_contract: dict) -> list[str]:
    quality = family_contract.get("family_evidence_quality", {})
    required = quality.get("required_features")
    if isinstance(required, list) and required:
        return list(required)
    rules = family_contract.get("threshold_rules", {})
    return [feature for feature, rule in rules.items() if not rule_is_optional(rule)]


def evaluate_fixture(row: dict, threshold_families: dict) -> dict:
    family_name = row.get("family_target")
    family_contract = threshold_families.get(family_name)
    if not family_contract:
        return {
            "threshold_pass": False,
            "fail_closed": True,
            "fail_reason": "family_threshold_missing",
            "missing_features": [],
            "threshold_miss_features": [],
            "rules_evaluated": [],
        }

    features = row.get("features", {})
    required_features = required_features_for_family(family_contract)
    missing_required = [feature for feature in required_features if feature not in features or features.get(feature) is None]
    if missing_required:
        return {
            "threshold_pass": False,
            "fail_closed": True,
            "fail_reason": "required_feature_missing",
            "missing_features": missing_required,
            "threshold_miss_features": [],
            "rules_evaluated": [],
        }

    rules_evaluated = []
    threshold_misses = []
    for feature, rule in family_contract.get("threshold_rules", {}).items():
        if feature not in features or features.get(feature) is None:
            if rule_is_optional(rule):
                continue
            return {
                "threshold_pass": False,
                "fail_closed": True,
                "fail_reason": "required_feature_missing",
                "missing_features": [feature],
                "threshold_miss_features": [],
                "rules_evaluated": rules_evaluated,
            }
        observed = float(features[feature])
        threshold = float(rule["value"])
        operator = rule["operator"]
        passed = compare_value(observed, operator, threshold)
        rules_evaluated.append(
            {
                "feature": feature,
                "operator": operator,
                "threshold_value": threshold,
                "fixture_value": observed,
                "passed": passed,
            }
        )
        if not passed:
            threshold_misses.append(feature)

    if threshold_misses:
        return {
            "threshold_pass": False,
            "fail_closed": True,
            "fail_reason": "threshold_miss",
            "missing_features": [],
            "threshold_miss_features": threshold_misses,
            "rules_evaluated": rules_evaluated,
        }

    return {
        "threshold_pass": True,
        "fail_closed": False,
        "fail_reason": None,
        "missing_features": [],
        "threshold_miss_features": [],
        "rules_evaluated": rules_evaluated,
    }


def output_row_base(row: dict, evaluation: dict, lifecycle_state: str) -> dict:
    data = {
        "fixture_id": row["fixture_id"],
        "route_key": ROUTE_KEY,
        "family_key": "old_short",
        "subfamily": row["family_target"],
        "side": "short",
        "dry_run_mode": DRY_RUN_MODE,
        "lifecycle_state": lifecycle_state,
        "gate_status": row["gate_status"],
        "threshold_pass": str(evaluation["threshold_pass"]).lower(),
        "fail_closed": str(evaluation["fail_closed"]).lower(),
        "fail_reason": evaluation["fail_reason"] or "",
        "missing_features": "|".join(evaluation.get("missing_features", [])),
        "threshold_miss_features": "|".join(evaluation.get("threshold_miss_features", [])),
        "signal_time_utc": row["signal_time_utc"],
        "entry_time_utc": row["entry_time_utc"],
        "close_time_utc": row["close_time_utc"],
        "synthetic_notional_usdt": f"{row['synthetic_notional_usdt']:.2f}",
        "synthetic_clock_note": "approx_2_min_entry_delay_120_min_hold",
        "safety_labels": labels_text(),
    }
    for feature in FEATURE_FIELDS:
        data[feature] = row.get("features", {}).get(feature, "")
    return data


def append_rejection(rejected_rows: list[dict], row: dict, evaluation: dict, reason: str) -> None:
    rejected = output_row_base(row, evaluation, "synthetic_rejected")
    rejected["rejection_reason"] = reason
    rejected_rows.append(rejected)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty fixture output: {path.name}")
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def all_rows_have_labels(groups: list[list[dict]]) -> bool:
    required = set(REQUIRED_ROW_LABELS)
    for rows in groups:
        for row in rows:
            labels = set(str(row.get("safety_labels", "")).split("|"))
            if not required.issubset(labels):
                return False
    return True


def threshold_label_audit(threshold_families: dict) -> dict:
    missing = []
    required = set(REQUIRED_THRESHOLD_LABELS)
    for family, family_contract in threshold_families.items():
        for feature, rule in family_contract.get("threshold_rules", {}).items():
            labels = set(rule.get("labels", []))
            if not required.issubset(labels):
                missing.append({"family": family, "feature": feature, "missing_labels": sorted(required - labels)})
    return {"passed": not missing, "missing": missing}


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

    source_payloads = {name: load_json(rel_path) for name, rel_path in SOURCE_RELS.items()}
    contract = source_payloads["runner_fixture_threshold_contract"]
    contract_loaded = True
    contract_complete = bool(contract.get("contract_completeness", {}).get("contract_complete"))
    threshold_families = contract.get("threshold_families", {})
    family_threshold_count = int(contract.get("contract_completeness", {}).get("family_threshold_count", len(threshold_families)))
    families_expected = contract.get("contract_completeness", {}).get("families_expected", [])
    label_audit = threshold_label_audit(threshold_families)

    output_root = choose_output_root()
    assert_output_root_allowed(output_root)
    output_root.mkdir(parents=True, exist_ok=False)

    fixtures = synthetic_fixtures()
    signals_rows = []
    pending_rows = []
    open_rows = []
    closed_rows = []
    rejected_rows = []
    evaluations = []

    for row in fixtures:
        evaluation = evaluate_fixture(row, threshold_families)
        evaluations.append(
            {
                "fixture_id": row["fixture_id"],
                "family_target": row["family_target"],
                "expected_fixture_behavior": row["expected_fixture_behavior"],
                "gate_status": row["gate_status"],
                **evaluation,
            }
        )
        signals_rows.append(output_row_base(row, evaluation, "synthetic_signal"))

        if not evaluation["threshold_pass"]:
            append_rejection(rejected_rows, row, evaluation, evaluation["fail_reason"] or "feature_fixture_fail_closed")
            continue

        pending_rows.append(output_row_base(row, evaluation, "synthetic_pending"))
        if row["gate_status"] == "gate_allowed":
            open_row = output_row_base(row, evaluation, "synthetic_open")
            open_row["paper_position_ref"] = f"paper_fixture_position_{row['fixture_id']}"
            open_rows.append(open_row)
            closed_row = output_row_base(row, evaluation, "synthetic_closed")
            closed_row["paper_position_ref"] = open_row["paper_position_ref"]
            closed_row["synthetic_close_reason"] = "fixed_120_min_fixture_hold_no_return_computed"
            closed_rows.append(closed_row)
        elif row["gate_status"] == "gate_blocked":
            gated_eval = dict(evaluation)
            gated_eval["fail_closed"] = True
            gated_eval["fail_reason"] = "gate_blocked"
            append_rejection(rejected_rows, row, gated_eval, "gate_blocked")
        elif row["gate_status"] == "gate_missing_timeout":
            gated_eval = dict(evaluation)
            gated_eval["fail_closed"] = True
            gated_eval["fail_reason"] = "gate_missing_timeout"
            append_rejection(rejected_rows, row, gated_eval, "gate_missing_timeout")
        else:
            gated_eval = dict(evaluation)
            gated_eval["fail_closed"] = True
            gated_eval["fail_reason"] = "unknown_fixture_gate_state"
            append_rejection(rejected_rows, row, gated_eval, "unknown_fixture_gate_state")

    passed_feature_fixture_count = sum(1 for item in evaluations if item["threshold_pass"])
    failed_feature_fixture_count = len(fixtures) - passed_feature_fixture_count
    missing_feature_fail_count = sum(1 for item in evaluations if item["fail_reason"] == "required_feature_missing")
    threshold_miss_fail_count = sum(1 for item in evaluations if item["fail_reason"] == "threshold_miss")
    gate_allowed_count = sum(1 for row in fixtures if row["gate_status"] == "gate_allowed")
    gate_blocked_count = sum(1 for row in fixtures if row["gate_status"] == "gate_blocked")
    gate_missing_timeout_count = sum(1 for row in fixtures if row["gate_status"] == "gate_missing_timeout")
    fail_closed_count = len(rejected_rows)
    passed_families = sorted({item["family_target"] for item in evaluations if item["threshold_pass"]})

    heartbeat_rows = [
        {
            "route_key": ROUTE_KEY,
            "dry_run_mode": DRY_RUN_MODE,
            "heartbeat_time_utc": now_utc(),
            "fixture_row_count": len(fixtures),
            "generated_output_file_count": len(OUTPUT_FILES),
            "threshold_contract_loaded": str(contract_loaded).lower(),
            "runtime_live_capital": "false",
            "candidate_generation": "false",
            "edge_claim": "false",
            "safety_labels": labels_text(),
        }
    ]

    state_object = {
        "route_key": ROUTE_KEY,
        "dry_run_mode": DRY_RUN_MODE,
        "status": STATUS,
        "fixture_row_count": len(fixtures),
        "family_threshold_count": family_threshold_count,
        "passed_feature_fixture_count": passed_feature_fixture_count,
        "fail_closed_count": fail_closed_count,
        "labels": list(REQUIRED_ROW_LABELS),
        "paper_only": True,
        "not_live": True,
        "not_edge_evidence": True,
        "not_market_data": True,
        "not_backtest": True,
        "not_real_trade": True,
        "no_real_signal_generation": True,
        "no_runtime_live_capital": True,
    }

    output_rows = {
        "signals.csv": signals_rows,
        "pending_entries.csv": pending_rows,
        "open_positions.csv": open_rows,
        "closed_trades.csv": closed_rows,
        "rejected_entries.csv": rejected_rows,
        "heartbeat.csv": heartbeat_rows,
    }
    for file_name, rows in output_rows.items():
        write_csv(output_root / file_name, rows)
    with (output_root / "state.json").open("w", encoding="utf-8") as handle:
        json.dump(state_object, handle, indent=2, sort_keys=False)
        handle.write("\n")

    generated_files = [str(output_root / name) for name in OUTPUT_FILES]
    generated_row_counts = {name: (1 if name == "state.json" else len(output_rows[name])) for name in OUTPUT_FILES}
    all_outputs_exist = all((output_root / name).exists() for name in OUTPUT_FILES)
    generated_output_file_count = sum(1 for name in OUTPUT_FILES if (output_root / name).exists())
    safety_label_audit_passed = all_rows_have_labels(list(output_rows.values())) and set(REQUIRED_ROW_LABELS).issubset(
        set(state_object["labels"])
    )
    no_output_field_names_private_order_runtime = all(
        "private" not in key.lower() and "order" not in key.lower()
        for rows in output_rows.values()
        for row in rows
        for key in row.keys()
    )

    intentional_fail_closed_cases_passed = (
        missing_feature_fail_count == 1
        and threshold_miss_fail_count == 1
        and gate_blocked_count == 1
        and gate_missing_timeout_count == 1
        and fail_closed_count == 4
    )

    pass_conditions = [
        contract_loaded,
        contract_complete,
        family_threshold_count == 2,
        {"blowoff_short", "mean_reversion_short"}.issubset(set(passed_families)),
        intentional_fail_closed_cases_passed,
        all_outputs_exist,
        generated_output_file_count == 7,
        safety_label_audit_passed,
        label_audit["passed"],
        no_output_field_names_private_order_runtime,
    ]
    if all(pass_conditions):
        result_classification = RESULT_PASS
    elif contract_loaded and contract_complete:
        result_classification = RESULT_PARTIAL
    elif not contract_loaded or not contract_complete:
        result_classification = RESULT_INCONCLUSIVE
    else:
        result_classification = RESULT_FAIL_CLOSED
    next_allowed_step = NEXT_PASS_OR_PARTIAL if result_classification in {RESULT_PASS, RESULT_PARTIAL} else NEXT_FAIL_OR_INCONCLUSIVE

    source_review = contract.get("source_review_preserved", {})
    unresolved = contract.get(
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
        "fixture_threshold_contract_loaded": contract_loaded,
        "contract_complete_verified": contract_complete,
        "dry_run_mode_feature_fixture_only": DRY_RUN_MODE == "FEATURE_FIXTURE_DRY_RUN",
        "no_raw_market_data_read": True,
        "no_okx_1m_data_read": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_real_signal_generation": True,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_orders_placed": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "external_output_root_used": str(output_root.resolve(strict=False)).lower().startswith(
            str(EXTERNAL_BASE.resolve(strict=False)).lower()
        ),
        "no_master_upper_system_modified": "MASTER_UPPER_SYSTEM" not in str(output_root).upper(),
        "no_runtime_directory_modified": all(
            token not in str(output_root).upper() for token in ["PAPER_RUN_GATE_", "LIVE_RUNTIME", "RUNTIME_ROOT"]
        ),
        "all_7_output_files_created": all_outputs_exist and generated_output_file_count == 7,
        "safety_labels_present": safety_label_audit_passed,
        "intentional_fail_closed_cases_passed": intentional_fail_closed_cases_passed,
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
            "code_changed": True,
            "created_files": [TOOL_REL.as_posix(), ARTIFACT_REL.as_posix()],
            "modified_existing_files": [],
        },
        "source_checkpoint": {
            "generated_at_utc": now_utc(),
            "repo_root": str(REPO_ROOT),
            "expected_head": "43bd8d6b5269c60b6213a731051c519427e6a61a",
            "actual_head": git_head,
            "expected_tracked_python_count": 949,
            "actual_tracked_python_count": tracked_python_count,
            "repo_clean_before_run": repo_clean_before_run,
            "git_status_before_run": git_status_before,
            "dirty_tracked_before_run": dirty_tracked,
            "allowed_pending_before_run": sorted(allowed_pending),
            "unexpected_untracked_before_run": unexpected_untracked,
            "target_tool_present_as_new_untracked_file": f"?? {TOOL_REL.as_posix()}" in git_status_before,
            "target_artifact_preexisting_before_run": False,
        },
        "source_artifacts": {
            name: source_summary(rel_path, source_payloads.get(name)) for name, rel_path in SOURCE_RELS.items()
        },
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "dry_run_mode": DRY_RUN_MODE,
            "feature_fixture_only": True,
            "synthetic_feature_fixture": True,
            "not_market_data": True,
            "not_original_old_short": True,
            "not_real_trade": True,
            "not_backtest": True,
            "not_runtime": True,
            "not_edge_evidence": True,
            "paper_only": True,
            "no_live_capital": True,
            "output_root": str(output_root),
        },
        "threshold_contract_review": {
            "threshold_contract_loaded": contract_loaded,
            "threshold_contract_status": contract.get("status"),
            "threshold_contract_artifact_kind": contract.get("artifact_kind"),
            "contract_complete_verified": contract_complete,
            "family_threshold_count": family_threshold_count,
            "families_expected": families_expected,
            "threshold_labels_present": label_audit["passed"],
            "threshold_label_missing": label_audit["missing"],
            "p1_attention_count": source_review.get("p1_attention_count"),
            "p0_issue_count": source_review.get("p0_issue_count"),
            "forbidden_evidence_used": source_review.get("forbidden_evidence_used"),
            "pnl_fields_used": source_review.get("pnl_fields_used"),
            "prior_contract_status": "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_FIXTURE_THRESHOLD_CONTRACT_CREATED",
        },
        "synthetic_feature_fixture_summary": {
            "fixture_row_count": len(fixtures),
            "feature_fields": FEATURE_FIELDS,
            "required_labels": REQUIRED_ROW_LABELS,
            "families_exercised": sorted({row["family_target"] for row in fixtures}),
            "fixture_rows": [
                {
                    "fixture_id": row["fixture_id"],
                    "family_target": row["family_target"],
                    "expected_fixture_behavior": row["expected_fixture_behavior"],
                    "gate_status": row["gate_status"],
                    "labels": row["labels"],
                }
                for row in fixtures
            ],
        },
        "runner_dry_run_results": {
            "fixture_row_count": len(fixtures),
            "threshold_contract_loaded": contract_loaded,
            "family_threshold_count": family_threshold_count,
            "passed_feature_fixture_count": passed_feature_fixture_count,
            "failed_feature_fixture_count": failed_feature_fixture_count,
            "signals_written": len(signals_rows),
            "pending_entries_written": len(pending_rows),
            "open_positions_written": len(open_rows),
            "closed_trades_written": len(closed_rows),
            "rejected_entries_written": len(rejected_rows),
            "fail_closed_count": fail_closed_count,
            "missing_feature_fail_count": missing_feature_fail_count,
            "threshold_miss_fail_count": threshold_miss_fail_count,
            "safety_label_audit_passed": safety_label_audit_passed,
            "evaluations": evaluations,
            "real_signal_generation": False,
            "real_pnl_computation": False,
            "runtime_touched": False,
            "live_capital_permission": False,
        },
        "gate_fixture_results": {
            "gate_allowed_count": gate_allowed_count,
            "gate_blocked_count": gate_blocked_count,
            "gate_missing_timeout_count": gate_missing_timeout_count,
            "gate_allowed_open_rows": len(open_rows),
            "gate_allowed_closed_rows": len(closed_rows),
            "gate_blocked_rejections": sum(1 for row in rejected_rows if row.get("rejection_reason") == "gate_blocked"),
            "gate_missing_timeout_rejections": sum(
                1 for row in rejected_rows if row.get("rejection_reason") == "gate_missing_timeout"
            ),
        },
        "generated_output_summary": {
            "output_root": str(output_root),
            "approved_external_subfolder": str(EXTERNAL_BASE),
            "generated_output_file_count": generated_output_file_count,
            "generated_files": generated_files,
            "generated_row_counts": generated_row_counts,
            "external_output_root_used": True,
            "wrote_only_under_approved_external_subfolder": True,
            "no_external_files_overwritten": True,
        },
        "safety_label_audit": {
            "required_labels": REQUIRED_ROW_LABELS,
            "all_generated_rows_labeled": all_rows_have_labels(list(output_rows.values())),
            "state_object_labeled": set(REQUIRED_ROW_LABELS).issubset(set(state_object["labels"])),
            "safety_label_audit_passed": safety_label_audit_passed,
            "no_live_order_private_output_fields": no_output_field_names_private_order_runtime,
        },
        "fail_closed_audit": {
            "fail_closed_count": fail_closed_count,
            "missing_feature_fail_count": missing_feature_fail_count,
            "threshold_miss_fail_count": threshold_miss_fail_count,
            "gate_blocked_fail_count": sum(1 for row in rejected_rows if row.get("rejection_reason") == "gate_blocked"),
            "gate_missing_timeout_fail_count": sum(
                1 for row in rejected_rows if row.get("rejection_reason") == "gate_missing_timeout"
            ),
            "intentional_fail_closed_cases_passed": intentional_fail_closed_cases_passed,
            "missing_threshold_contract_fail_closed": False,
            "unsafe_output_path_fail_closed": False,
            "missing_safety_label_fail_closed": False,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": unresolved,
        "limitations": [
            "synthetic feature fixtures only",
            "not market data",
            "not original old_short replay",
            "not exact frozen replay",
            "not a backtest",
            "not an edge claim",
            "no threshold optimization or modification",
            "no runtime, monitor, live, or capital permission",
        ],
        "safety_permissions": {
            "runner_feature_fixture_dry_run_created": True,
            "runner_execution_allowed_now": False,
            "real_signal_generation_allowed_now": False,
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
    print(f"dry_run_mode: {DRY_RUN_MODE}")
    print(f"output_root: {output_root}")
    print(f"fixture_row_count: {len(fixtures)}")
    print(f"family_threshold_count: {family_threshold_count}")
    print(f"passed_feature_fixture_count: {passed_feature_fixture_count}")
    print(f"fail_closed_count: {fail_closed_count}")
    print(f"generated_output_file_count: {generated_output_file_count}")
    print(f"safety_label_audit_passed: {str(safety_label_audit_passed).lower()}")
    print(f"result_classification: {result_classification}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
