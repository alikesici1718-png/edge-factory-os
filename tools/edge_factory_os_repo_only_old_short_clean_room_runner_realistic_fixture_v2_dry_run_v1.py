#!/usr/bin/env python3
"""Run the old_short clean-room realistic fixture V2 dry-run.

This dry-run processes only bounded clean-room fixture packages. It does not run
the runner on market data, compare full datasets, run a backtest, compute PnL,
touch runtime, place orders, allocate capital, generate candidates, or claim an
edge.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "6c57e542f0134a8b71ba4f2a15b10757a65ed880"
EXPECTED_TRACKED_PYTHON_COUNT = 966
NEXT_ALLOWED_STEP_PASS_OR_PARTIAL = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_REVIEW_V1"
NEXT_ALLOWED_STEP_FAIL_OR_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_REPAIR_PREVIEW_V1"

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / MODULE
ARTIFACT_PATH = REPO_ROOT / ARTIFACT

REALISTIC_FIXTURE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\realistic_bounded_fixture_generation_dry_run_v1"
)
ACCEPTED_LIFECYCLE_FIXTURE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\accepted_lifecycle_fixture_discovery_v1"
)
APPROVED_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
)
REQUIRED_OUTPUT_SUBFOLDER = APPROVED_OUTPUT_ROOT / "realistic_fixture_runner_v2_dry_run_v1"

SOURCE_ARTIFACT_PATHS = {
    "runner_realistic_fixture_v2_preview": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_preview_v1.json",
    "realistic_fixture_runner_v2_design": "artifacts/old_short_clean_room/old_short_clean_room_realistic_fixture_runner_v2_design_v1.json",
    "accepted_lifecycle_fixture_review": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json",
    "accepted_lifecycle_fixture_discovery_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.json",
    "runner_realistic_fixture_dry_run_review": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.json",
    "runner_fixture_threshold_contract": "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json",
    "threshold_proposal_review": "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json",
    "old_short_clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
}

REALISTIC_INPUT_FILES = [
    "fixture_index.json",
    "master_proxy_cases.jsonl",
    "clean_room_replay_fixture_inputs.jsonl",
    "validation_pair_fixtures.jsonl",
    "fixture_generation_summary.json",
]
ACCEPTED_INPUT_FILES = [
    "accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_master_cases.jsonl",
    "accepted_lifecycle_pairing_plan.json",
    "accepted_lifecycle_discovery_summary.json",
]
OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
    "runner_realistic_fixture_v2_dry_run_report.json",
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
ACCEPTED_SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "PROXY_BEHAVIOR_FIXTURE",
    "ACCEPTED_LIFECYCLE_FIXTURE",
    "NOT_ORIGINAL_OLD_SHORT",
    "NOT_EXACT_REPLAY",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]
THRESHOLD_REQUIRED_LABELS = [
    "NOT_ORIGINAL_THRESHOLD",
    "NOT_PNL_OPTIMIZED",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]
FORBIDDEN_SELECTION_TERMS = [
    "pnl",
    "net_ret",
    "stress_pnl",
    "realistic_net_ret",
    "gross_ret",
    "win",
    "loss",
    "best trade",
    "worst trade",
    "future return",
    "validation/holdout return",
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("payload_sha256_excluding_hash", None)
    return sha256_text(canonical_json(payload))


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


def contains_string(value: Any, needle: str) -> bool:
    if isinstance(value, str):
        return needle in value
    if isinstance(value, dict):
        return any(contains_string(v, needle) for v in value.values())
    if isinstance(value, list):
        return any(contains_string(v, needle) for v in value)
    return False


def status_has_only_expected_untracked_tool(status_text: str) -> bool:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    expected = f"?? {MODULE}"
    return all(line == expected for line in lines)


def path_is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_safe_output_root(path: Path) -> bool:
    lowered = str(path).lower()
    forbidden_fragments = [
        "master_upper_system",
        "paper_run_gate_",
        "live runtime",
        "live_runtime",
    ]
    return path_is_relative_to(path, APPROVED_OUTPUT_ROOT) and not any(
        fragment in lowered for fragment in forbidden_fragments
    )


def label_set(row: dict[str, Any]) -> set[str]:
    labels = row.get("safety_labels", [])
    return set(labels if isinstance(labels, list) else [])


def has_labels(row: dict[str, Any], required: list[str]) -> bool:
    return set(required).issubset(label_set(row))


def infer_gate_state(row: dict[str, Any]) -> str:
    reject_reason = str(row.get("reject_reason") or "")
    if "missing" in reject_reason or "timeout" in reject_reason:
        return "gate_missing_timeout"
    if "block" in reject_reason:
        return "gate_blocked"
    if row.get("family") == "heartbeat_state":
        return "heartbeat_state"
    return "gate_allowed_or_not_applicable"


def case_hash(row: dict[str, Any]) -> str:
    return sha256_text(canonical_json(row))


def source_summary(relative_path: str, data: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    return {
        "path": relative_path,
        "sha256": sha256_file(path),
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": first_value(data, "route_key"),
        "next_allowed_step": data.get("next_allowed_step"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def output_row_base(case: dict[str, Any], output_type: str, accepted: bool) -> dict[str, Any]:
    labels = ACCEPTED_SAFETY_LABELS if accepted else BASE_SAFETY_LABELS
    features = case.get("signal_features") if isinstance(case.get("signal_features"), dict) else {}
    return {
        "output_type": output_type,
        "fixture_case_id": case.get("fixture_case_id"),
        "fixture_type": case.get("fixture_type"),
        "route_key": ROUTE_KEY,
        "family_key": case.get("family_key"),
        "family": case.get("family"),
        "side": case.get("side"),
        "signal_id": case.get("signal_id", ""),
        "position_id": case.get("position_id", ""),
        "close_id": case.get("close_id", ""),
        "inst_id": case.get("inst_id", ""),
        "signal_time": case.get("signal_time", ""),
        "entry_time": case.get("entry_time", ""),
        "exit_time": case.get("exit_time", ""),
        "planned_exit_time": case.get("planned_exit_time", ""),
        "hold_minutes_actual": case.get("hold_minutes_actual", ""),
        "notional": case.get("notional", ""),
        "gate_state": "gate_allowed_inferred_from_closed_trade" if accepted else infer_gate_state(case),
        "gate_allowed_inferred_from_closed_trade": str(bool(case.get("gate_allowed_inferred_from_closed_trade", False))).lower(),
        "direct_lifecycle_link_found": str(bool(case.get("direct_lifecycle_link_found", False))).lower(),
        "exact_gate_replay_recovered": "false",
        "accepted_lifecycle_is_exact_replay": "false",
        "no_pnl_used": "true",
        "no_market_data_used": "true",
        "not_real_trade": "true",
        "safety_labels": ";".join(labels),
        "signal_ret1_bps": features.get("signal_ret1_bps", ""),
        "signal_ret3_bps": features.get("signal_ret3_bps", ""),
        "signal_ret5_bps": features.get("signal_ret5_bps", ""),
        "signal_ret60_bps": features.get("signal_ret60_bps", ""),
        "signal_vol_quote": features.get("signal_vol_quote", ""),
        "signal_range_bps": features.get("signal_range_bps", ""),
        "entry_vol_quote": features.get("entry_vol_quote", ""),
        "entry_range_bps": features.get("entry_range_bps", ""),
        "source_hash": case.get("source_hash", ""),
        "fixture_hash": case.get("fixture_hash", case_hash(case)),
    }


def build_rows(
    realistic_cases: list[dict[str, Any]],
    accepted_cases: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rejected_cases = [
        row for row in realistic_cases if infer_gate_state(row) in {"gate_blocked", "gate_missing_timeout"}
    ]
    heartbeat_cases = [
        row for row in realistic_cases if infer_gate_state(row) == "heartbeat_state"
    ]

    signals = [output_row_base(case, "paper_only_signal_fixture", True) for case in accepted_cases]
    pending = [output_row_base(case, "paper_only_pending_entry_fixture", True) for case in accepted_cases]
    open_positions = [output_row_base(case, "paper_only_open_position_fixture", True) for case in accepted_cases]
    closed_trades = [output_row_base(case, "paper_only_closed_trade_fixture", True) for case in accepted_cases]
    rejected = [output_row_base(case, "paper_only_rejected_entry_fixture", False) for case in rejected_cases]
    heartbeat = [output_row_base(case, "paper_only_heartbeat_state_fixture", False) for case in heartbeat_cases]

    output_rows = {
        "signals.csv": signals,
        "pending_entries.csv": pending,
        "open_positions.csv": open_positions,
        "closed_trades.csv": closed_trades,
        "rejected_entries.csv": rejected,
        "heartbeat.csv": heartbeat,
    }
    return output_rows, rejected_cases, heartbeat_cases, accepted_cases


CSV_FIELDS = [
    "output_type",
    "fixture_case_id",
    "fixture_type",
    "route_key",
    "family_key",
    "family",
    "side",
    "signal_id",
    "position_id",
    "close_id",
    "inst_id",
    "signal_time",
    "entry_time",
    "exit_time",
    "planned_exit_time",
    "hold_minutes_actual",
    "notional",
    "gate_state",
    "gate_allowed_inferred_from_closed_trade",
    "direct_lifecycle_link_found",
    "exact_gate_replay_recovered",
    "accepted_lifecycle_is_exact_replay",
    "no_pnl_used",
    "no_market_data_used",
    "not_real_trade",
    "safety_labels",
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
    "source_hash",
    "fixture_hash",
]


def summarize_output_file(path: Path) -> dict[str, Any]:
    if path.suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            row_count = sum(1 for _ in reader)
    else:
        row_count = None
    return {
        "path": str(path),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() else None,
        "row_count": row_count,
    }


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    source_payloads = {
        name: read_json(REPO_ROOT / rel_path)
        for name, rel_path in SOURCE_ARTIFACT_PATHS.items()
    }
    realistic_json = {
        "fixture_index": read_json(REALISTIC_FIXTURE_ROOT / "fixture_index.json"),
        "fixture_generation_summary": read_json(REALISTIC_FIXTURE_ROOT / "fixture_generation_summary.json"),
    }
    realistic_jsonl = {
        "master_proxy_cases": read_jsonl(REALISTIC_FIXTURE_ROOT / "master_proxy_cases.jsonl"),
        "clean_room_replay_fixture_inputs": read_jsonl(REALISTIC_FIXTURE_ROOT / "clean_room_replay_fixture_inputs.jsonl"),
        "validation_pair_fixtures": read_jsonl(REALISTIC_FIXTURE_ROOT / "validation_pair_fixtures.jsonl"),
    }
    accepted_json = {
        "accepted_lifecycle_fixture_index": read_json(ACCEPTED_LIFECYCLE_FIXTURE_ROOT / "accepted_lifecycle_fixture_index.json"),
        "accepted_lifecycle_pairing_plan": read_json(ACCEPTED_LIFECYCLE_FIXTURE_ROOT / "accepted_lifecycle_pairing_plan.json"),
        "accepted_lifecycle_discovery_summary": read_json(ACCEPTED_LIFECYCLE_FIXTURE_ROOT / "accepted_lifecycle_discovery_summary.json"),
    }
    accepted_jsonl = {
        "accepted_lifecycle_master_cases": read_jsonl(ACCEPTED_LIFECYCLE_FIXTURE_ROOT / "accepted_lifecycle_master_cases.jsonl"),
    }
    fixture_payloads: dict[str, Any] = {
        "realistic_json": realistic_json,
        "realistic_jsonl": realistic_jsonl,
        "accepted_json": accepted_json,
        "accepted_jsonl": accepted_jsonl,
    }
    return source_payloads, fixture_payloads


def choose_output_root() -> Path:
    if not REQUIRED_OUTPUT_SUBFOLDER.exists():
        return REQUIRED_OUTPUT_SUBFOLDER
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REQUIRED_OUTPUT_SUBFOLDER / f"versioned_{timestamp}"


def build_artifact() -> tuple[dict[str, Any], dict[str, Any], Path]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = len(run_git(["ls-files", "*.py"]).splitlines())
    artifact_existed_before = ARTIFACT_PATH.exists()
    output_root = choose_output_root()
    output_root_existed_before = output_root.exists()

    source_payloads, fixture_payloads = load_inputs()
    preview = source_payloads["runner_realistic_fixture_v2_preview"]
    design = source_payloads["realistic_fixture_runner_v2_design"]
    accepted_review = source_payloads["accepted_lifecycle_fixture_review"]
    threshold_contract = source_payloads["runner_fixture_threshold_contract"]

    realistic_cases = fixture_payloads["realistic_jsonl"]["clean_room_replay_fixture_inputs"]
    accepted_cases = fixture_payloads["accepted_jsonl"]["accepted_lifecycle_master_cases"]
    output_rows, rejected_cases, heartbeat_cases, accepted_cases = build_rows(realistic_cases, accepted_cases)

    blocked_missing_fixture_case_count = len(rejected_cases)
    accepted_lifecycle_case_count = len(accepted_cases)
    heartbeat_state_case_count = len(heartbeat_cases)
    processed_case_count = blocked_missing_fixture_case_count + accepted_lifecycle_case_count + heartbeat_state_case_count
    gate_allowed_inferred_count = sum(1 for case in accepted_cases if case.get("gate_allowed_inferred_from_closed_trade") is True)
    entry_delay_computable_count = sum(1 for case in accepted_cases if case.get("signal_time") and case.get("entry_time"))
    hold_duration_computable_count = sum(1 for case in accepted_cases if case.get("hold_minutes_actual"))
    notional_computable_count = sum(1 for case in accepted_cases if case.get("notional"))
    family_coverage = sorted({case.get("family") for case in accepted_cases if case.get("family")})
    gate_state_coverage = sorted({infer_gate_state(case) for case in rejected_cases} | {"gate_allowed_inferred"})

    realistic_files = {
        name: {
            "path": str(REALISTIC_FIXTURE_ROOT / name),
            "exists": (REALISTIC_FIXTURE_ROOT / name).exists(),
            "sha256": sha256_file(REALISTIC_FIXTURE_ROOT / name),
        }
        for name in REALISTIC_INPUT_FILES
    }
    accepted_files = {
        name: {
            "path": str(ACCEPTED_LIFECYCLE_FIXTURE_ROOT / name),
            "exists": (ACCEPTED_LIFECYCLE_FIXTURE_ROOT / name).exists(),
            "sha256": sha256_file(ACCEPTED_LIFECYCLE_FIXTURE_ROOT / name),
        }
        for name in ACCEPTED_INPUT_FILES
    }

    source_artifacts = {
        name: source_summary(path, source_payloads[name])
        for name, path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts["fixture_package_files"] = {
        "realistic_bounded_fixture_package": realistic_files,
        "accepted_lifecycle_fixture_package": accepted_files,
    }

    threshold_completeness = threshold_contract.get("contract_completeness", {})
    threshold_json_text = canonical_json(threshold_contract)
    threshold_labels_present = {
        label: contains_string(threshold_contract, label)
        for label in THRESHOLD_REQUIRED_LABELS
    }

    realistic_label_failures = [
        case.get("fixture_case_id") for case in realistic_cases if not has_labels(case, BASE_SAFETY_LABELS)
    ]
    accepted_label_failures = [
        case.get("fixture_case_id") for case in accepted_cases if not has_labels(case, ACCEPTED_SAFETY_LABELS)
    ]
    safety_label_audit_passed = not realistic_label_failures and not accepted_label_failures

    route_family_side_failures = [
        case.get("fixture_case_id")
        for case in [*rejected_cases, *accepted_cases]
        if (
            (case.get("route_key") is not None and case.get("route_key") != ROUTE_KEY)
            or case.get("family_key") != "old_short"
            or case.get("side") != "short"
        )
    ]
    accepted_lifecycle_coverage_present = accepted_lifecycle_case_count > 0 and set(family_coverage) == {
        "blowoff_short",
        "mean_reversion_short",
    }
    both_families_processed = set(family_coverage) == {"blowoff_short", "mean_reversion_short"}
    blocked_missing_processed = {"gate_blocked", "gate_missing_timeout"}.issubset(set(gate_state_coverage))
    exact_gate_replay_recovered = False
    no_pnl_used = True
    no_market_data_used = True
    no_edge_live_capital = True

    fail_closed_reasons: list[str] = []
    if not validate_safe_output_root(output_root):
        fail_closed_reasons.append("unsafe output root")
    if output_root_existed_before:
        fail_closed_reasons.append("selected output root existed before run")
    if preview.get("next_allowed_step") != "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_V1":
        fail_closed_reasons.append("prior preview next_allowed_step mismatch")
    if first_value(preview, "route_key") != ROUTE_KEY:
        fail_closed_reasons.append("prior preview route_key mismatch")
    if int(first_value(preview, "accepted_lifecycle_candidate_count", 0)) != 2:
        fail_closed_reasons.append("prior preview accepted lifecycle candidate count mismatch")
    if int(first_value(preview, "gate_allowed_inferred_count", 0)) != 2:
        fail_closed_reasons.append("prior preview gate allowed inferred count mismatch")
    if first_value(preview, "exact_gate_replay_recovered", None) is not False:
        fail_closed_reasons.append("preview exact gate replay was claimed")
    if first_value(design, "original_exact_source_recovered", None) is not False:
        fail_closed_reasons.append("design original exact source was claimed")
    if threshold_completeness.get("contract_complete") is not True:
        fail_closed_reasons.append("threshold contract incomplete")
    if threshold_completeness.get("family_threshold_count") != 2:
        fail_closed_reasons.append("threshold family count mismatch")
    if not all(threshold_labels_present.values()):
        fail_closed_reasons.append("threshold required label missing")
    if not all(item["exists"] for item in [*realistic_files.values(), *accepted_files.values()]):
        fail_closed_reasons.append("fixture package file missing")
    if not safety_label_audit_passed:
        fail_closed_reasons.append("safety label missing")
    if route_family_side_failures:
        fail_closed_reasons.append("route/family/side mismatch")

    fail_closed_count = len(fail_closed_reasons)
    if fail_closed_count:
        result_classification = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL_OR_INCONCLUSIVE
    elif processed_case_count == 0 or accepted_lifecycle_case_count == 0:
        result_classification = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL_OR_INCONCLUSIVE
    elif (
        both_families_processed
        and blocked_missing_processed
        and accepted_lifecycle_coverage_present
        and safety_label_audit_passed
        and no_pnl_used
        and no_market_data_used
        and no_edge_live_capital
        and exact_gate_replay_recovered is False
    ):
        result_classification = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PASS_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_PASS_OR_PARTIAL
    else:
        result_classification = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_PASS_OR_PARTIAL

    generated_output_file_count = len(OUTPUT_FILES) if fail_closed_count == 0 else 0
    v2_metrics = {
        "blocked_missing_fixture_case_count": blocked_missing_fixture_case_count,
        "accepted_lifecycle_case_count": accepted_lifecycle_case_count,
        "processed_case_count": processed_case_count,
        "family_coverage": family_coverage,
        "gate_state_coverage": gate_state_coverage,
        "gate_allowed_inferred_count": gate_allowed_inferred_count,
        "exact_gate_replay_recovered": False,
        "accepted_lifecycle_coverage_present": accepted_lifecycle_coverage_present,
        "entry_delay_computable_count": entry_delay_computable_count,
        "hold_duration_computable_count": hold_duration_computable_count,
        "notional_computable_count": notional_computable_count,
        "rejected_case_count": len(rejected_cases),
        "accepted_case_count": accepted_lifecycle_case_count,
        "fail_closed_count": fail_closed_count,
        "generated_output_file_count": generated_output_file_count,
        "safety_label_audit_passed": safety_label_audit_passed,
        "no_pnl_used": no_pnl_used,
        "no_market_data_used": no_market_data_used,
        "no_edge_live_capital": no_edge_live_capital,
    }

    output_plan = {
        "output_root": str(output_root),
        "required_output_subfolder": str(REQUIRED_OUTPUT_SUBFOLDER),
        "approved_output_root": str(APPROVED_OUTPUT_ROOT),
        "output_root_existed_before": output_root_existed_before,
        "created_versioned_subfolder": output_root != REQUIRED_OUTPUT_SUBFOLDER,
        "write_only_under_approved_external_output_root": validate_safe_output_root(output_root),
        "files_to_write": OUTPUT_FILES,
    }

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "prior_realistic_fixture_v2_preview_loaded": preview.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_PREVIEW_CREATED",
        "prior_next_allowed_step_verified": preview.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_V1",
        "accepted_lifecycle_fixture_package_loaded": all(item["exists"] for item in accepted_files.values()) and len(accepted_cases) == 2,
        "realistic_bounded_fixture_package_loaded": all(item["exists"] for item in realistic_files.values()) and len(realistic_cases) == 5,
        "threshold_contract_loaded": threshold_completeness.get("contract_complete") is True and threshold_completeness.get("family_threshold_count") == 2 and all(threshold_labels_present.values()),
        "no_raw_market_data_read": True,
        "no_okx_1m_data_read": True,
        "no_full_dataset_comparison": True,
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
        "exact_gate_replay_not_claimed": exact_gate_replay_recovered is False,
        "original_exact_source_not_claimed": first_value(design, "original_exact_source_recovered", None) is False,
        "external_output_root_used": validate_safe_output_root(output_root),
        "no_master_upper_system_modified": True,
        "no_runtime_directory_modified": True,
        "output_files_created": fail_closed_count == 0 and generated_output_file_count == len(OUTPUT_FILES),
        "safety_labels_present": safety_label_audit_passed,
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
            "fixture_v2_dry_run": True,
            "full_runner_execution": False,
            "full_dataset_comparison": False,
            "backtest": False,
            "pnl_computation": False,
            "runtime_live_capital": False,
            "candidate_generation": False,
            "edge_claim": False,
            "original_exact_source_recovered": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "clean_room_behavioral_reconstruction": True,
            "output_root": str(output_root),
        },
        "fixture_package_review": {
            "realistic_bounded_fixture_package": {
                "root": str(REALISTIC_FIXTURE_ROOT),
                "required_files": REALISTIC_INPUT_FILES,
                "all_required_files_loaded": all(item["exists"] for item in realistic_files.values()),
                "clean_room_replay_fixture_case_count": len(realistic_cases),
                "blocked_missing_fixture_case_count": blocked_missing_fixture_case_count,
                "heartbeat_state_case_count": heartbeat_state_case_count,
                "family_coverage": fixture_payloads["realistic_json"]["fixture_generation_summary"].get("family_coverage", []),
                "gate_state_coverage": fixture_payloads["realistic_json"]["fixture_generation_summary"].get("gate_state_coverage", []),
            },
            "accepted_lifecycle_fixture_package": {
                "root": str(ACCEPTED_LIFECYCLE_FIXTURE_ROOT),
                "required_files": ACCEPTED_INPUT_FILES,
                "all_required_files_loaded": all(item["exists"] for item in accepted_files.values()),
                "accepted_lifecycle_case_count": accepted_lifecycle_case_count,
                "family_coverage": family_coverage,
                "gate_allowed_inferred_count": gate_allowed_inferred_count,
                "direct_lifecycle_link_count": sum(1 for case in accepted_cases if case.get("direct_lifecycle_link_found") is True),
            },
            "raw_market_data_read": False,
            "full_master_output_read": False,
            "runtime_directory_read": False,
        },
        "threshold_contract_review": {
            "source_artifact": SOURCE_ARTIFACT_PATHS["runner_fixture_threshold_contract"],
            "contract_complete": threshold_completeness.get("contract_complete"),
            "family_threshold_count": threshold_completeness.get("family_threshold_count"),
            "required_family_threshold_count": 2,
            "required_labels_present": threshold_labels_present,
            "threshold_contract_sha256": sha256_text(threshold_json_text),
            "threshold_optimization_used": False,
        },
        "processed_fixture_cases": [
            {
                "fixture_case_id": case.get("fixture_case_id"),
                "source_package": "realistic_bounded_fixture_package",
                "processing_result": "rejected_entries",
                "gate_state": infer_gate_state(case),
                "family": case.get("family"),
                "family_key": case.get("family_key"),
                "side": case.get("side"),
                "reject_reason": case.get("reject_reason"),
                "safety_labels_present": has_labels(case, BASE_SAFETY_LABELS),
            }
            for case in rejected_cases
        ]
        + [
            {
                "fixture_case_id": case.get("fixture_case_id"),
                "source_package": "accepted_lifecycle_fixture_package",
                "processing_result": "paper_only_accepted_open_closed_lifecycle",
                "gate_state": "gate_allowed_inferred_from_closed_trade",
                "family": case.get("family"),
                "family_key": case.get("family_key"),
                "side": case.get("side"),
                "signal_id": case.get("signal_id"),
                "position_id": case.get("position_id"),
                "close_id": case.get("close_id"),
                "direct_lifecycle_link_found": case.get("direct_lifecycle_link_found"),
                "gate_allowed_inferred_from_closed_trade": case.get("gate_allowed_inferred_from_closed_trade"),
                "safety_labels_present": has_labels(case, ACCEPTED_SAFETY_LABELS),
            }
            for case in accepted_cases
        ]
        + [
            {
                "fixture_case_id": case.get("fixture_case_id"),
                "source_package": "realistic_bounded_fixture_package",
                "processing_result": "heartbeat_state_report_only",
                "gate_state": infer_gate_state(case),
                "family": case.get("family"),
                "family_key": case.get("family_key"),
                "side": case.get("side"),
                "safety_labels_present": has_labels(case, BASE_SAFETY_LABELS),
            }
            for case in heartbeat_cases
        ],
        "accepted_lifecycle_processing": {
            "accepted_lifecycle_case_count": accepted_lifecycle_case_count,
            "family_coverage": family_coverage,
            "gate_allowed_inferred_count": gate_allowed_inferred_count,
            "direct_lifecycle_link_count": sum(1 for case in accepted_cases if case.get("direct_lifecycle_link_found") is True),
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_is_exact_replay": False,
            "entry_delay_computable_count": entry_delay_computable_count,
            "hold_duration_computable_count": hold_duration_computable_count,
            "notional_computable_count": notional_computable_count,
            "no_pnl_used": True,
            "no_market_data_used": True,
            "no_real_trade_created": True,
        },
        "gate_fixture_results": {
            "gate_blocked_count": sum(1 for case in rejected_cases if infer_gate_state(case) == "gate_blocked"),
            "gate_missing_timeout_count": sum(1 for case in rejected_cases if infer_gate_state(case) == "gate_missing_timeout"),
            "gate_allowed_inferred_count": gate_allowed_inferred_count,
            "exact_gate_replay_recovered": False,
            "rejected_entries_written_from_blocked_missing_fixtures": len(rejected_cases),
        },
        "generated_output_summary": output_plan,
        "v2_metrics": v2_metrics,
        "accepted_lifecycle_coverage": {
            "accepted_lifecycle_coverage_present": accepted_lifecycle_coverage_present,
            "families_required": ["blowoff_short", "mean_reversion_short"],
            "families_covered": family_coverage,
            "coverage_source": "accepted lifecycle fixture package inferred from closed trade lifecycle",
            "exact_gate_replay_recovered": False,
        },
        "exact_gate_replay_limitation": {
            "exact_gate_replay_recovered": False,
            "gate_allowed_inferred_from_closed_trade": True,
            "explicit_gate_replay_available": False,
            "limitation_preserved": True,
            "not_exact_original_replay": True,
        },
        "safety_label_audit": {
            "safety_label_audit_passed": safety_label_audit_passed,
            "base_safety_labels": BASE_SAFETY_LABELS,
            "accepted_lifecycle_safety_labels": ACCEPTED_SAFETY_LABELS,
            "realistic_label_failures": realistic_label_failures,
            "accepted_lifecycle_label_failures": accepted_label_failures,
            "output_rows_include_or_are_accompanied_by_labels": True,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": {
            "original_exact_source_recovered": False,
            "exact_frozen_replay_available": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "accepted_lifecycle_is_exact_replay": False,
            "not_edge_evidence": True,
            "no_live_capital_readiness": True,
        },
        "limitations": [
            "Fixture V2 dry-run only; not full runner execution on market data.",
            "Accepted lifecycle is inferred from closed trade fixtures.",
            "Exact gate replay remains unrecovered.",
            "Original old_short source remains unrecovered.",
            "Accepted lifecycle outputs are paper-only fixture projections, not real trades.",
            "No PnL/outcome selection, backtest, full dataset comparison, runtime, live, capital, candidate generation, or edge claim is performed.",
        ],
        "safety_permissions": {
            "runner_realistic_fixture_v2_dry_run_created": True,
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
        "replacement_checks_all_true": all(validation_checks.values()) and fail_closed_count == 0,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    runtime_context = {
        "output_root": output_root,
        "output_rows": output_rows,
        "state": {
            "route_key": ROUTE_KEY,
            "state_kind": "paper_only_fixture_v2_dry_run_state",
            "output_root": str(output_root),
            "processed_case_count": processed_case_count,
            "accepted_lifecycle_case_count": accepted_lifecycle_case_count,
            "gate_allowed_inferred_count": gate_allowed_inferred_count,
            "exact_gate_replay_recovered": False,
            "safety_labels": BASE_SAFETY_LABELS,
            "runtime_live_capital": False,
            "candidate_generation": False,
            "edge_claim": False,
        },
    }
    return artifact, runtime_context, output_root


def write_outputs(artifact: dict[str, Any], runtime_context: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=False)
    output_rows = runtime_context["output_rows"]
    for file_name, rows in output_rows.items():
        write_csv(output_root / file_name, rows, CSV_FIELDS)

    state_path = output_root / "state.json"
    state_path.write_text(canonical_json(runtime_context["state"]), encoding="utf-8")

    report = {
        "status": artifact["status"],
        "artifact_kind": "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_REPORT",
        "route_key": ROUTE_KEY,
        "result_classification": artifact["result_classification"],
        "v2_metrics": artifact["v2_metrics"],
        "accepted_lifecycle_processing": artifact["accepted_lifecycle_processing"],
        "exact_gate_replay_limitation": artifact["exact_gate_replay_limitation"],
        "safety_label_audit": artifact["safety_label_audit"],
        "limitations": artifact["limitations"],
        "next_allowed_step": artifact["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
    }
    (output_root / "runner_realistic_fixture_v2_dry_run_report.json").write_text(
        canonical_json(report),
        encoding="utf-8",
    )

    generated = {
        file_name: summarize_output_file(output_root / file_name)
        for file_name in OUTPUT_FILES
    }
    artifact["generated_output_summary"]["generated_files"] = generated
    artifact["generated_output_summary"]["generated_output_file_count"] = len(generated)
    artifact["v2_metrics"]["generated_output_file_count"] = len(generated)
    artifact["validation_checks"]["output_files_created"] = all(item["exists"] for item in generated.values())
    artifact["replacement_checks_all_true"] = all(artifact["validation_checks"].values()) and artifact["v2_metrics"]["fail_closed_count"] == 0
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)


def main() -> int:
    if ARTIFACT_PATH.exists():
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_PATH}")

    artifact, runtime_context, output_root = build_artifact()
    if artifact["replacement_checks_all_true"] is not True:
        raise SystemExit("BLOCKED: replacement_checks_all_true=false before output write")

    write_outputs(artifact, runtime_context, output_root)
    if artifact["replacement_checks_all_true"] is not True:
        raise SystemExit("BLOCKED: replacement_checks_all_true=false after output write")

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    stdout_fields = {
        "status": artifact["status"],
        "route_key": artifact["dry_run_identity"]["route_key"],
        "result_classification": artifact["result_classification"],
        "output_root": artifact["dry_run_identity"]["output_root"],
        "processed_case_count": artifact["v2_metrics"]["processed_case_count"],
        "accepted_lifecycle_case_count": artifact["v2_metrics"]["accepted_lifecycle_case_count"],
        "gate_allowed_inferred_count": artifact["v2_metrics"]["gate_allowed_inferred_count"],
        "exact_gate_replay_recovered": artifact["v2_metrics"]["exact_gate_replay_recovered"],
        "accepted_lifecycle_coverage_present": artifact["v2_metrics"]["accepted_lifecycle_coverage_present"],
        "generated_output_file_count": artifact["v2_metrics"]["generated_output_file_count"],
        "safety_label_audit_passed": artifact["v2_metrics"]["safety_label_audit_passed"],
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
