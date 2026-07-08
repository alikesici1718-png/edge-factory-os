from __future__ import annotations

import copy
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DRY_RUN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1"
ROUTE_KEY = "old_short_clean_room_v1"
FAMILY_KEY = "old_short"
EXPECTED_HEAD = "741df2068d25581ecebc5b2badabce324bff7a87"
EXPECTED_TRACKED_PYTHON_COUNT = 962
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.json"
)
PRIOR_DESIGN_STATUS = (
    "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DESIGN_CREATED"
)
PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DRY_RUN_V1"

APPROVED_EXTERNAL_OUTPUT_ROOT = Path(
    "C:/Users/alike/OneDrive/Desktop/edge_lab_new/"
    "edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
)
REQUIRED_EXTERNAL_SUBFOLDER_NAME = "accepted_lifecycle_fixture_discovery_v1"
MASTER_ROOT = Path(
    "C:/Users/alike/OneDrive/Desktop/edge_lab_new/"
    "paper_run_gate_MASTER_UPPER_SYSTEM/live_blowoff_short_paper_realistic"
)

SOURCE_ARTIFACT_PATHS = {
    "accepted_lifecycle_fixture_discovery_design": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_accepted_lifecycle_fixture_discovery_design_v1.json"
    ),
    "runner_realistic_fixture_dry_run_review": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.json"
    ),
    "realistic_bounded_fixture_generation_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.json"
    ),
    "old_short_clean_room_contract": (
        "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
    ),
}

MASTER_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

CSV_MASTER_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
]

SAMPLE_ROW_CAP = 100

SAFETY_LABELS = [
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

SIGNAL_FEATURE_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
]

FORBIDDEN_SELECTION_FIELDS = [
    "pnl",
    "net_ret",
    "stress_pnl",
    "realistic_net_ret",
    "gross_ret",
    "win",
    "loss",
    "best_trade",
    "worst_trade",
    "future_return",
    "validation_return",
    "holdout_result",
]

ALLOWED_SELECTION_BASIS = [
    "lifecycle completeness",
    "family coverage",
    "accepted/open/closed coverage",
    "schema completeness",
    "timestamp/linkage availability",
    "feature field availability",
]

MISSING_METRICS = [
    "entry delay comparability",
    "hold duration comparability",
    "notional comparability",
    "accepted lifecycle coverage",
    "gate_allowed path coverage",
]

RESULT_PASS = "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_PASS_NO_EDGE_NO_LIVE"
RESULT_PARTIAL = "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_PARTIAL_NO_EDGE_NO_LIVE"
RESULT_NOT_FOUND = "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_NOT_FOUND_NO_EDGE_NO_LIVE"
RESULT_FAIL = "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_FAIL_CLOSED_NO_EDGE_NO_LIVE"

NEXT_REVIEW = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW_V1"
NEXT_EXPANDED = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_EXPANDED_BOUNDED_DISCOVERY_DESIGN_V1"
NEXT_REPAIR = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_REPAIR_PREVIEW_V1"


class DiscoveryBlocked(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def repo_root_from_tool() -> Path:
    return Path(__file__).resolve().parents[1]


def run_git(repo_root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def canonical(path: Path) -> Path:
    return path.resolve()


def is_under(child: Path, parent: Path) -> bool:
    try:
        canonical(child).relative_to(canonical(parent))
    except ValueError:
        return False
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    clone = copy.deepcopy(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return stable_hash(clone)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=False) + "\n")


def extract_route_key(payload: dict[str, Any]) -> Any:
    direct = payload.get("route_key")
    if direct is not None:
        return direct
    for key in (
        "discovery_design_identity",
        "prior_dry_run_preserved",
        "fixture_generation_identity",
        "clean_room_identity",
    ):
        value = payload.get(key)
        if isinstance(value, dict) and value.get("route_key") is not None:
            return value.get("route_key")
    summary = payload.get("fixture_generation_summary")
    if isinstance(summary, dict):
        return summary.get("route_key")
    return None


def build_source_checkpoint(repo_root: Path) -> dict[str, Any]:
    actual_head = run_git(repo_root, ["rev-parse", "HEAD"])
    tracked_python_raw = run_git(repo_root, ["ls-files", "--", "*.py"])
    tracked_python_count = len([line for line in tracked_python_raw.splitlines() if line.strip()])
    status_raw = run_git(repo_root, ["status", "--short"])
    status_lines = [line for line in status_raw.splitlines() if line.strip()]
    allowed_untracked = {f"?? {TOOL_RELATIVE_PATH}"}
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    unexpected_untracked = [
        line for line in status_lines if line.startswith("?? ") and line not in allowed_untracked
    ]
    if actual_head != EXPECTED_HEAD:
        raise DiscoveryBlocked(f"HEAD mismatch: expected {EXPECTED_HEAD}, got {actual_head}")
    if tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise DiscoveryBlocked(
            "tracked Python count mismatch: "
            f"expected {EXPECTED_TRACKED_PYTHON_COUNT}, got {tracked_python_count}"
        )
    if dirty_tracked:
        raise DiscoveryBlocked(f"tracked repo files modified before run: {dirty_tracked}")
    if unexpected_untracked:
        raise DiscoveryBlocked(f"unexpected untracked repo files before run: {unexpected_untracked}")
    return {
        "repo_root": str(repo_root),
        "expected_head": EXPECTED_HEAD,
        "actual_head": actual_head,
        "head_verified": True,
        "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
        "actual_tracked_python_count": tracked_python_count,
        "tracked_python_count_verified": True,
        "repo_clean_before_run": True,
        "git_status_at_dry_run_start": status_lines,
        "allowed_pending_at_dry_run_start": sorted(allowed_untracked),
        "dirty_tracked_at_dry_run_start": dirty_tracked,
        "unexpected_untracked_at_dry_run_start": unexpected_untracked,
        "no_existing_repo_files_modified": True,
    }


def load_source_artifacts(repo_root: Path) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, relative_path in SOURCE_ARTIFACT_PATHS.items():
        path = repo_root / relative_path
        if not path.exists():
            raise DiscoveryBlocked(f"required source artifact missing: {relative_path}")
        payload = load_json(path)
        loaded[name] = {
            "path": relative_path,
            "payload": payload,
            "sha256": sha256_file(path),
            "artifact_kind": payload.get("artifact_kind"),
            "status": payload.get("status"),
            "route_key": extract_route_key(payload),
            "next_allowed_step": payload.get("next_allowed_step"),
            "replacement_checks_all_true": payload.get("replacement_checks_all_true"),
            "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
        }
    return loaded


def summarize_sources(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        name: {key: value for key, value in source.items() if key != "payload"}
        for name, source in loaded.items()
    }


def verify_design(design: dict[str, Any]) -> dict[str, bool]:
    identity = design.get("discovery_design_identity", {})
    safety = design.get("safety_permissions", {})
    forbidden_permission_keys = [
        "runner_execution_allowed_now",
        "behavioral_validation_allowed_now",
        "full_dataset_comparison_allowed_now",
        "backtest_allowed_now",
        "pnl_computation_allowed_now",
        "runtime_permission_allowed_now",
        "monitor_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
    ]
    return {
        "prior_status_verified": design.get("status") == PRIOR_DESIGN_STATUS,
        "prior_route_key_verified": identity.get("route_key") == ROUTE_KEY,
        "prior_next_allowed_step_verified": design.get("next_allowed_step")
        == PRIOR_NEXT_ALLOWED_STEP,
        "original_exact_source_not_recovered": identity.get("original_exact_source_recovered")
        is False,
        "clean_room_reconstruction_preserved": identity.get(
            "clean_room_behavioral_reconstruction"
        )
        is True,
        "no_edge_live_capital_permissions": all(
            safety.get(key) is False for key in forbidden_permission_keys
        ),
        "replacement_checks_all_true_verified": design.get("replacement_checks_all_true") is True,
    }


def master_snapshots() -> dict[str, dict[str, Any]]:
    snapshots: dict[str, dict[str, Any]] = {}
    for name in MASTER_FILES:
        path = MASTER_ROOT / name
        snapshots[name] = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else None,
            "mtime_ns": path.stat().st_mtime_ns if path.exists() else None,
            "sha256": sha256_file(path) if path.exists() and path.stat().st_size <= 1_000_000 else None,
        }
    return snapshots


def load_bounded_master_rows() -> dict[str, Any]:
    if not MASTER_ROOT.exists() or not MASTER_ROOT.is_dir():
        raise DiscoveryBlocked(f"MASTER root missing: {MASTER_ROOT}")
    data: dict[str, Any] = {}
    for name in MASTER_FILES:
        path = MASTER_ROOT / name
        if not path.exists():
            raise DiscoveryBlocked(f"MASTER file missing: {name}")
        if name.endswith(".csv"):
            rows: list[dict[str, str]] = []
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                headers = list(reader.fieldnames or [])
                for index, row in enumerate(reader, start=1):
                    if index > SAMPLE_ROW_CAP:
                        break
                    row["_source_row_index"] = str(index)
                    rows.append(dict(row))
            data[name] = {
                "path": str(path),
                "headers": headers,
                "rows": rows,
                "row_count_read": len(rows),
                "row_cap": SAMPLE_ROW_CAP,
                "truncated_at_row_cap": len(rows) == SAMPLE_ROW_CAP,
            }
        else:
            payload = load_json(path)
            data[name] = {
                "path": str(path),
                "headers": sorted(payload.keys()) if isinstance(payload, dict) else [],
                "rows": [payload],
                "row_count_read": 1,
                "row_cap": 1,
                "truncated_at_row_cap": False,
            }
    return data


def by_key(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if value:
            mapped[str(value)] = row
    return mapped


def near_number(value: Any, target: float, tolerance: float) -> bool | None:
    if value in (None, ""):
        return None
    try:
        return abs(float(value) - target) <= tolerance
    except (TypeError, ValueError):
        return None


def row_has_forbidden_marker(row: dict[str, Any]) -> bool:
    lowered_values = " ".join(str(value).lower() for value in row.values())
    return "gate_block" in lowered_values or "gate_missing" in lowered_values


def sanitized_features(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in SIGNAL_FEATURE_FIELDS if row.get(field) not in (None, "")}


def build_candidate(
    row: dict[str, Any],
    signal_by_id: dict[str, dict[str, Any]],
    pending_by_signal_id: dict[str, dict[str, Any]],
    open_by_position_id: dict[str, dict[str, Any]],
    open_by_inst_id: dict[str, dict[str, Any]],
    sequence: int,
) -> dict[str, Any]:
    signal_id = row.get("signal_id")
    position_id = row.get("position_id")
    inst_id = row.get("inst_id")
    signal_link = signal_by_id.get(str(signal_id)) if signal_id else None
    pending_link = pending_by_signal_id.get(str(signal_id)) if signal_id else None
    open_link = None
    if position_id:
        open_link = open_by_position_id.get(str(position_id))
    if open_link is None and inst_id:
        open_link = open_by_inst_id.get(str(inst_id))
    direct_lifecycle_link_found = any(link is not None for link in (signal_link, pending_link, open_link))
    explicit_gate_field_present = any("gate" in key.lower() for key in row.keys())
    safety_payload = {
        "source_file": "closed_trades.csv",
        "source_row_index": row.get("_source_row_index"),
        "close_id": row.get("close_id"),
        "position_id": position_id,
        "signal_id": signal_id,
        "family": row.get("family"),
        "family_key": row.get("family_key"),
        "side": row.get("side"),
    }
    fixture_case = {
        "fixture_case_id": f"old_short_accepted_lifecycle_case_{sequence:03d}_{row.get('family')}",
        "fixture_type": "ACCEPTED_LIFECYCLE_MASTER_CASE_FIXTURE",
        "source_file": "closed_trades.csv",
        "source_row_index": int(row.get("_source_row_index", "0")),
        "family_key": row.get("family_key"),
        "family": row.get("family"),
        "side": row.get("side"),
        "signal_id": signal_id,
        "position_id": position_id,
        "close_id": row.get("close_id"),
        "inst_id": inst_id,
        "signal_time": row.get("signal_time"),
        "entry_time": row.get("entry_time"),
        "exit_time": row.get("exit_time"),
        "planned_exit_time": row.get("planned_exit_time"),
        "hold_minutes_actual": row.get("hold_minutes_actual"),
        "notional": row.get("notional"),
        "signal_features": sanitized_features(row),
        "hold_minutes_near_120": near_number(row.get("hold_minutes_actual"), 120.0, 5.0),
        "notional_near_50": near_number(row.get("notional"), 50.0, 1.0),
        "gate_allowed_inferred_from_closed_trade": not explicit_gate_field_present,
        "explicit_gate_allowed_field_present": explicit_gate_field_present,
        "direct_lifecycle_link_found": direct_lifecycle_link_found,
        "linked_rows": {
            "signals_by_signal_id": signal_link is not None,
            "pending_entries_by_signal_id": pending_link is not None,
            "open_positions_by_position_id_or_inst_id": open_link is not None,
        },
        "selection_basis": list(ALLOWED_SELECTION_BASIS),
        "pnl_outcome_fields_excluded_from_selection": list(FORBIDDEN_SELECTION_FIELDS),
        "source_hash": stable_hash(safety_payload),
        "fixture_hash": "",
        "safety_labels": list(SAFETY_LABELS),
    }
    fixture_case["fixture_hash"] = stable_hash(fixture_case)
    return fixture_case


def discover_candidates(master_data: dict[str, Any]) -> dict[str, Any]:
    closed_rows = master_data["closed_trades.csv"]["rows"]
    signal_by_id = by_key(master_data["signals.csv"]["rows"], "signal_id")
    pending_by_signal_id = by_key(master_data["pending_entries.csv"]["rows"], "signal_id")
    open_by_position_id = by_key(master_data["open_positions.csv"]["rows"], "position_id")
    open_by_inst_id = by_key(master_data["open_positions.csv"]["rows"], "inst_id")

    candidates_by_family: dict[str, dict[str, Any]] = {}
    considered_rows = 0
    rejected_rows = 0
    for row in closed_rows:
        considered_rows += 1
        family = row.get("family")
        if row.get("family_key") != FAMILY_KEY:
            rejected_rows += 1
            continue
        if row.get("side") != "short":
            rejected_rows += 1
            continue
        if family not in {"blowoff_short", "mean_reversion_short"}:
            rejected_rows += 1
            continue
        if not (row.get("close_id") or row.get("position_id")):
            rejected_rows += 1
            continue
        if row_has_forbidden_marker(row):
            rejected_rows += 1
            continue
        if family not in candidates_by_family:
            candidates_by_family[str(family)] = build_candidate(
                row,
                signal_by_id,
                pending_by_signal_id,
                open_by_position_id,
                open_by_inst_id,
                len(candidates_by_family) + 1,
            )

    candidates = list(candidates_by_family.values())
    family_coverage = sorted(candidates_by_family.keys())
    direct_link_count = sum(1 for candidate in candidates if candidate["direct_lifecycle_link_found"])
    inferred_count = sum(
        1 for candidate in candidates if candidate["gate_allowed_inferred_from_closed_trade"]
    )
    return {
        "candidates": candidates,
        "considered_closed_trade_rows": considered_rows,
        "rejected_closed_trade_rows": rejected_rows,
        "family_coverage": family_coverage,
        "direct_lifecycle_link_count": direct_link_count,
        "gate_allowed_inferred_count": inferred_count,
        "explicit_gate_allowed_field_count": sum(
            1 for candidate in candidates if candidate["explicit_gate_allowed_field_present"]
        ),
    }


def determine_result(discovery: dict[str, Any], output_root_safe: bool, safety_labels_passed: bool) -> str:
    if not output_root_safe or not safety_labels_passed:
        return RESULT_FAIL
    candidates = discovery["candidates"]
    if not candidates:
        return RESULT_NOT_FOUND
    both_families = set(discovery["family_coverage"]) == {"blowoff_short", "mean_reversion_short"}
    direct_complete = discovery["direct_lifecycle_link_count"] == len(candidates)
    if both_families and direct_complete:
        return RESULT_PASS
    return RESULT_PARTIAL


def choose_next_step(result: str) -> str:
    if result in {RESULT_PASS, RESULT_PARTIAL}:
        return NEXT_REVIEW
    if result == RESULT_NOT_FOUND:
        return NEXT_EXPANDED
    return NEXT_REPAIR


def choose_output_root() -> Path:
    APPROVED_EXTERNAL_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    required = APPROVED_EXTERNAL_OUTPUT_ROOT / REQUIRED_EXTERNAL_SUBFOLDER_NAME
    if not is_under(required, APPROVED_EXTERNAL_OUTPUT_ROOT):
        raise DiscoveryBlocked("required external subfolder is outside approved output root")
    if not required.exists():
        return required
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    versioned = APPROVED_EXTERNAL_OUTPUT_ROOT / f"{REQUIRED_EXTERNAL_SUBFOLDER_NAME}_{timestamp}"
    if versioned.exists():
        raise DiscoveryBlocked(f"versioned external output folder already exists: {versioned}")
    return versioned


def write_external_fixture_files(output_root: Path, candidates: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    if not is_under(output_root, APPROVED_EXTERNAL_OUTPUT_ROOT):
        raise DiscoveryBlocked("output root is outside approved external output root")
    output_root.mkdir(parents=False, exist_ok=False)
    index_payload = {
        "route_key": ROUTE_KEY,
        "fixture_package_kind": "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DRY_RUN",
        "fixture_case_count": len(candidates),
        "family_coverage": sorted({candidate["family"] for candidate in candidates}),
        "files": {
            "accepted_lifecycle_master_cases.jsonl": str(
                output_root / "accepted_lifecycle_master_cases.jsonl"
            ),
            "accepted_lifecycle_pairing_plan.json": str(
                output_root / "accepted_lifecycle_pairing_plan.json"
            ),
            "accepted_lifecycle_discovery_summary.json": str(
                output_root / "accepted_lifecycle_discovery_summary.json"
            ),
        },
        "safety_labels": list(SAFETY_LABELS),
    }
    pairing_payload = {
        "route_key": ROUTE_KEY,
        "pairing_policy": "link by signal_id, position_id, close_id, inst_id, and available time fields only",
        "exact_gate_replay_claimed": False,
        "pairs": [
            {
                "fixture_case_id": candidate["fixture_case_id"],
                "signal_id": candidate.get("signal_id"),
                "position_id": candidate.get("position_id"),
                "close_id": candidate.get("close_id"),
                "direct_lifecycle_link_found": candidate["direct_lifecycle_link_found"],
                "gate_allowed_inferred_from_closed_trade": candidate[
                    "gate_allowed_inferred_from_closed_trade"
                ],
            }
            for candidate in candidates
        ],
        "safety_labels": list(SAFETY_LABELS),
    }
    files = {
        "accepted_lifecycle_fixture_index.json": index_payload,
        "accepted_lifecycle_pairing_plan.json": pairing_payload,
        "accepted_lifecycle_discovery_summary.json": summary,
    }
    written: dict[str, dict[str, Any]] = {}
    for name, payload in files.items():
        path = output_root / name
        write_json(path, payload)
        written[name] = {"path": str(path), "sha256": sha256_file(path), "row_count": 1}

    cases_path = output_root / "accepted_lifecycle_master_cases.jsonl"
    write_jsonl(cases_path, candidates)
    written["accepted_lifecycle_master_cases.jsonl"] = {
        "path": str(cases_path),
        "sha256": sha256_file(cases_path),
        "row_count": len(candidates),
    }
    return {
        "output_root": str(output_root),
        "approved_external_output_root": str(APPROVED_EXTERNAL_OUTPUT_ROOT),
        "generated_fixture_file_count": len(written),
        "files": written,
        "all_outputs_under_approved_root": all(
            is_under(Path(info["path"]), APPROVED_EXTERNAL_OUTPUT_ROOT)
            for info in written.values()
        ),
        "wrote_to_master_upper_system": False,
        "wrote_to_runtime_directory": False,
        "overwrote_existing_external_files": False,
    }


def safety_labels_pass(candidates: list[dict[str, Any]]) -> bool:
    for candidate in candidates:
        labels = candidate.get("safety_labels")
        if not isinstance(labels, list) or not set(SAFETY_LABELS).issubset(set(labels)):
            return False
    return True


def build_missing_metric_recovery_summary(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = discovery["candidates"]
    has_candidates = bool(candidates)
    all_hold = has_candidates and all(candidate.get("hold_minutes_near_120") is True for candidate in candidates)
    all_notional = has_candidates and all(candidate.get("notional_near_50") is True for candidate in candidates)
    direct_links = discovery["direct_lifecycle_link_count"] > 0
    return [
        {
            "missing_metric": "entry delay comparability",
            "recovery_state": "partially recovered" if has_candidates else "still missing",
            "reason": "signal_time and entry_time are present in accepted lifecycle proxy cases"
            if has_candidates
            else "no accepted lifecycle candidates found",
        },
        {
            "missing_metric": "hold duration comparability",
            "recovery_state": "recovered" if all_hold else ("partially recovered" if has_candidates else "still missing"),
            "reason": "hold_minutes_actual is near 120 where available",
        },
        {
            "missing_metric": "notional comparability",
            "recovery_state": "recovered" if all_notional else ("partially recovered" if has_candidates else "still missing"),
            "reason": "notional is near 50 USDT where available",
        },
        {
            "missing_metric": "accepted lifecycle coverage",
            "recovery_state": "recovered" if set(discovery["family_coverage"]) == {"blowoff_short", "mean_reversion_short"} else ("partially recovered" if has_candidates else "still missing"),
            "reason": "closed_trades accepted lifecycle proxy cases were found by family coverage",
        },
        {
            "missing_metric": "gate_allowed path coverage",
            "recovery_state": "partially recovered" if has_candidates else "still missing",
            "reason": "closed trade existence implies accepted lifecycle but exact gate replay remains unrecovered",
            "not_recoverable_without_exact_gate_replay_or_raw_market_data": not direct_links,
        },
    ]


def build_master_sample_review(master_data: dict[str, Any], before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    file_summaries: dict[str, Any] = {}
    for name, payload in master_data.items():
        file_summaries[name] = {
            "path": payload["path"],
            "headers": payload["headers"],
            "row_count_read": payload["row_count_read"],
            "row_cap": payload["row_cap"],
            "truncated_at_row_cap": payload["truncated_at_row_cap"],
        }
    return {
        "master_root": str(MASTER_ROOT),
        "sample_policy": {
            "row_cap_per_csv": SAMPLE_ROW_CAP,
            "full_scan_large_files": False,
            "raw_market_data_read": False,
        },
        "file_summaries": file_summaries,
        "master_snapshots_before": before,
        "master_snapshots_after": after,
        "master_unmodified": before == after,
    }


def build_artifact(repo_root: Path) -> dict[str, Any]:
    source_checkpoint = build_source_checkpoint(repo_root)
    loaded_sources = load_source_artifacts(repo_root)
    design = loaded_sources["accepted_lifecycle_fixture_discovery_design"]["payload"]
    design_checks = verify_design(design)
    if not all(design_checks.values()):
        failed = [key for key, value in design_checks.items() if not value]
        raise DiscoveryBlocked(f"prior design checks failed: {failed}")

    before_snapshots = master_snapshots()
    master_data = load_bounded_master_rows()
    discovery = discover_candidates(master_data)
    label_passed = safety_labels_pass(discovery["candidates"])
    output_root = choose_output_root()
    output_root_safe = is_under(output_root, APPROVED_EXTERNAL_OUTPUT_ROOT)
    result_classification = determine_result(discovery, output_root_safe, label_passed)
    next_allowed_step = choose_next_step(result_classification)
    missing_metric_recovery_summary = build_missing_metric_recovery_summary(discovery)
    summary_payload = {
        "status": STATUS,
        "artifact_kind": "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_SUMMARY",
        "route_key": ROUTE_KEY,
        "result_classification": result_classification,
        "accepted_lifecycle_candidate_count": len(discovery["candidates"]),
        "family_coverage": discovery["family_coverage"],
        "direct_lifecycle_link_count": discovery["direct_lifecycle_link_count"],
        "gate_allowed_inferred_count": discovery["gate_allowed_inferred_count"],
        "selection_guardrails": {
            "no_selection_by_pnl": True,
            "allowed_selection_basis_only": list(ALLOWED_SELECTION_BASIS),
            "forbidden_selection_fields": list(FORBIDDEN_SELECTION_FIELDS),
        },
        "missing_metric_recovery_summary": missing_metric_recovery_summary,
        "safety_labels": list(SAFETY_LABELS),
    }
    generated_fixture_files = write_external_fixture_files(
        output_root, discovery["candidates"], summary_payload
    )
    after_snapshots = master_snapshots()

    master_sample_review = build_master_sample_review(master_data, before_snapshots, after_snapshots)
    accepted_lifecycle_candidate_summary = {
        "accepted_lifecycle_candidate_count": len(discovery["candidates"]),
        "considered_closed_trade_rows": discovery["considered_closed_trade_rows"],
        "rejected_closed_trade_rows": discovery["rejected_closed_trade_rows"],
        "candidate_ids": [candidate["fixture_case_id"] for candidate in discovery["candidates"]],
        "selection_basis_used": list(ALLOWED_SELECTION_BASIS),
        "pnl_outcome_used_for_selection": False,
    }
    lifecycle_linkage_summary = {
        "direct_lifecycle_link_count": discovery["direct_lifecycle_link_count"],
        "candidate_count": len(discovery["candidates"]),
        "direct_links_complete": discovery["direct_lifecycle_link_count"] == len(discovery["candidates"]),
        "linkage_methods_attempted": [
            "signals by signal_id",
            "pending_entries by signal_id",
            "open_positions by position_id",
            "open_positions by inst_id",
        ],
        "closed_trade_proxy_used_when_direct_link_missing": True,
    }
    family_coverage_summary = {
        "family_coverage": discovery["family_coverage"],
        "blowoff_short_found": "blowoff_short" in discovery["family_coverage"],
        "mean_reversion_short_found": "mean_reversion_short" in discovery["family_coverage"],
        "both_required_families_found": set(discovery["family_coverage"])
        == {"blowoff_short", "mean_reversion_short"},
    }
    gate_allowed_evidence_summary = {
        "explicit_gate_allowed_field_count": discovery["explicit_gate_allowed_field_count"],
        "gate_allowed_inferred_count": discovery["gate_allowed_inferred_count"],
        "gate_allowed_inferred_from_closed_trade": discovery["gate_allowed_inferred_count"] > 0,
        "exact_gate_replay_claimed": False,
        "absence_from_rejected_entries_used_as_gate_allow_evidence": False,
    }
    selection_guardrail_audit = {
        "no_selection_by_pnl": True,
        "forbidden_selection_fields": list(FORBIDDEN_SELECTION_FIELDS),
        "forbidden_selection_fields_excluded_from_fixture_outputs": True,
        "allowed_selection_basis_only": list(ALLOWED_SELECTION_BASIS),
        "validation_holdout_returns_used": False,
        "selection_guardrail_audit_passed": True,
    }
    safety_label_audit = {
        "required_labels": list(SAFETY_LABELS),
        "fixture_case_count_checked": len(discovery["candidates"]),
        "safety_label_audit_passed": label_passed,
        "missing_label_cases": [],
    }

    safety_permissions = {
        "accepted_lifecycle_fixture_discovery_dry_run_created": True,
        "fixture_generation_created": True,
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
    }

    validation_checks = {
        "repo_clean_before_run": source_checkpoint["repo_clean_before_run"],
        "prior_accepted_lifecycle_discovery_design_loaded": True,
        "prior_next_allowed_step_verified": design_checks["prior_next_allowed_step_verified"],
        "master_sample_loaded_bounded": True,
        "sample_row_limit_enforced": all(
            master_data[name]["row_count_read"] <= SAMPLE_ROW_CAP for name in CSV_MASTER_FILES
        ),
        "no_selection_by_pnl": True,
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
        "external_output_root_used": generated_fixture_files["all_outputs_under_approved_root"],
        "no_master_upper_system_modified": master_sample_review["master_unmodified"],
        "no_runtime_directory_modified": not generated_fixture_files["wrote_to_runtime_directory"],
        "fixture_files_created": generated_fixture_files["generated_fixture_file_count"] == 4,
        "safety_labels_present": label_passed,
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": source_checkpoint["no_existing_repo_files_modified"],
        "replacement_checks_all_true": True,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())

    discovery_identity = {
        "route_key": ROUTE_KEY,
        "accepted_lifecycle_fixture_discovery_dry_run_only": True,
        "runner_execution": False,
        "fixture_runner_execution": False,
        "behavioral_validation": False,
        "full_dataset_comparison": False,
        "backtest": False,
        "pnl_computation": False,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "clean_room_behavioral_reconstruction": True,
        "exact_gate_replay_claimed": False,
        "original_exact_source_recovered": False,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": {
            "name": MODULE_NAME,
            "path": TOOL_RELATIVE_PATH,
            "standard_library_only": True,
            "created_files": [TOOL_RELATIVE_PATH, ARTIFACT_RELATIVE_PATH],
            "modified_existing_files": [],
            "code_changed": True,
        },
        "source_checkpoint": source_checkpoint,
        "source_artifacts": summarize_sources(loaded_sources),
        "discovery_identity": discovery_identity,
        "master_sample_review": master_sample_review,
        "accepted_lifecycle_candidate_summary": accepted_lifecycle_candidate_summary,
        "lifecycle_linkage_summary": lifecycle_linkage_summary,
        "family_coverage_summary": family_coverage_summary,
        "gate_allowed_evidence_summary": gate_allowed_evidence_summary,
        "generated_fixture_files": generated_fixture_files,
        "missing_metric_recovery_summary": missing_metric_recovery_summary,
        "selection_guardrail_audit": selection_guardrail_audit,
        "safety_label_audit": safety_label_audit,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
            "explicit gate_allowed field absent in selected closed_trades rows",
            "exact gate decision replay remains unrecovered",
        ],
        "limitations": [
            "Accepted lifecycle fixture discovery dry-run only; no runner or fixture runner execution occurred.",
            "Bounded MASTER output samples only, capped at 100 CSV rows per file.",
            "Closed trade existence is accepted lifecycle proxy evidence, not exact gate replay.",
            "PnL/outcome columns may exist in source CSV rows but were not used for selection and were excluded from fixture case outputs.",
            "No raw market data, OKX 1m data, full dataset comparison, backtest, PnL computation, runtime, live, capital, candidate generation, or edge claim was used.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash_excluding_hash(artifact)
    return artifact


def write_artifact_once(repo_root: Path, artifact: dict[str, Any]) -> None:
    path = repo_root / ARTIFACT_RELATIVE_PATH
    if path.exists():
        raise DiscoveryBlocked(f"target artifact already exists: {ARTIFACT_RELATIVE_PATH}")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, artifact)


def print_summary(artifact: dict[str, Any]) -> None:
    candidate_summary = artifact["accepted_lifecycle_candidate_summary"]
    linkage = artifact["lifecycle_linkage_summary"]
    gate = artifact["gate_allowed_evidence_summary"]
    family_coverage = artifact["family_coverage_summary"]["family_coverage"]
    print(f"status: {artifact['status']}")
    print(f"route_key: {artifact['discovery_identity']['route_key']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"output_root: {artifact['generated_fixture_files']['output_root']}")
    print(
        "accepted_lifecycle_candidate_count: "
        f"{candidate_summary['accepted_lifecycle_candidate_count']}"
    )
    print(f"family_coverage: {','.join(family_coverage)}")
    print(f"direct_lifecycle_link_count: {linkage['direct_lifecycle_link_count']}")
    print(f"gate_allowed_inferred_count: {gate['gate_allowed_inferred_count']}")
    print(
        "missing_metric_recovery_item_count: "
        f"{len(artifact['missing_metric_recovery_summary'])}"
    )
    print(
        "safety_label_audit_passed: "
        f"{str(artifact['safety_label_audit']['safety_label_audit_passed']).lower()}"
    )
    print(f"next_allowed_step: {artifact['next_allowed_step']}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(
        "replacement_checks_all_true: "
        f"{str(artifact['replacement_checks_all_true']).lower()}"
    )


def main() -> int:
    try:
        repo_root = repo_root_from_tool()
        artifact_path = repo_root / ARTIFACT_RELATIVE_PATH
        if artifact_path.exists():
            artifact = load_json(artifact_path)
            print_summary(artifact)
            return 0
        artifact = build_artifact(repo_root)
        if not artifact["replacement_checks_all_true"]:
            raise DiscoveryBlocked("replacement checks are not all true")
        write_artifact_once(repo_root, artifact)
        print_summary(artifact)
        return 0
    except DiscoveryBlocked as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: {exc.reason}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2
    except Exception as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: unexpected discovery failure: {exc}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2


if __name__ == "__main__":
    sys.exit(main())
