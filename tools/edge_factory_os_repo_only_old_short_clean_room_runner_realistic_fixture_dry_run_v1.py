from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_v1"
ROUTE_KEY = "old_short_clean_room_v1"
FAMILY_KEY = "old_short"
EXPECTED_HEAD = "251fef0d780b5a34ac0a1c642b56dccbc0cf95c9"
EXPECTED_TRACKED_PYTHON_COUNT = 959
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_runner_realistic_fixture_dry_run_v1.json"
)

APPROVED_FIXTURE_ROOT = Path(
    "C:/Users/alike/OneDrive/Desktop/edge_lab_new/"
    "edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1/"
    "realistic_bounded_fixture_generation_dry_run_v1"
)
APPROVED_EXTERNAL_OUTPUT_ROOT = Path(
    "C:/Users/alike/OneDrive/Desktop/edge_lab_new/"
    "edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
)
REQUIRED_EXTERNAL_SUBFOLDER_NAME = "realistic_fixture_dry_run_v1"

PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_V1"
NEXT_REVIEW_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_V1"
NEXT_REPAIR_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_REPAIR_PREVIEW_V1"

SOURCE_ARTIFACT_PATHS = {
    "runner_realistic_fixture_dry_run_preview": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_preview_v1.json"
    ),
    "runner_realistic_fixture_dry_run_design": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_design_v1.json"
    ),
    "realistic_bounded_fixture_generation_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.json"
    ),
    "runner_fixture_threshold_contract": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_fixture_threshold_contract_v1.json"
    ),
    "threshold_behavioral_proposal_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
    ),
    "threshold_proposal_review": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_threshold_proposal_review_v1.json"
    ),
    "old_short_clean_room_contract": (
        "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
    ),
}

REQUIRED_FIXTURE_FILES = [
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

THRESHOLD_LABELS = [
    "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
    "NOT_ORIGINAL_THRESHOLD",
    "NOT_PNL_OPTIMIZED",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]

RESULT_PASS = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PASS_NO_EDGE_NO_LIVE"
RESULT_PARTIAL = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE"
RESULT_FAIL_CLOSED = (
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE"
)
RESULT_INCONCLUSIVE = (
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE"
)

SIGNAL_FEATURES = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
]

SENSITIVE_FIELD_MARKERS = [
    "api_key",
    "secret",
    "private_key",
    "account_id",
    "account_key",
    "order_id",
    "client_order_id",
    "live_order",
    "runtime_path",
    "market_data_path",
    "raw_market_data_path",
    "raw_okx_1m_path",
]

RAW_OR_RUNTIME_PATH_MARKERS = [
    "raw_market_data",
    "raw okx 1m",
    "okx_1m",
    "paper_run_gate_",
    "MASTER_UPPER_SYSTEM",
    "live runtime",
]

SIGNALS_HEADER = [
    "fixture_case_id",
    "route_key",
    "family_key",
    "family",
    "side",
    "signal_time",
    "gate_state",
    "threshold_passed",
    "threshold_failed_features",
    *SIGNAL_FEATURES,
    "safety_labels",
]

PENDING_HEADER = [
    "fixture_case_id",
    "route_key",
    "family_key",
    "family",
    "side",
    "signal_time",
    "entry_time",
    "gate_state",
    "paper_only",
    "safety_labels",
]

OPEN_HEADER = [
    "fixture_case_id",
    "route_key",
    "family_key",
    "family",
    "side",
    "entry_time",
    "planned_exit_time",
    "paper_only",
    "safety_labels",
]

CLOSED_HEADER = [
    "fixture_case_id",
    "route_key",
    "family_key",
    "family",
    "side",
    "entry_time",
    "exit_time",
    "planned_exit_time",
    "paper_only",
    "safety_labels",
]

REJECTED_HEADER = [
    "fixture_case_id",
    "route_key",
    "family_key",
    "family",
    "side",
    "signal_time",
    "gate_state",
    "reject_reason",
    "threshold_failed_features",
    "paper_only",
    "safety_labels",
]

HEARTBEAT_HEADER = [
    "fixture_case_id",
    "route_key",
    "family_key",
    "family",
    "heartbeat_kind",
    "paper_only",
    "safety_labels",
]


class DryRunBlocked(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def canonical_path(path: Path) -> Path:
    return path.resolve()


def is_under(child: Path, parent: Path) -> bool:
    child_resolved = canonical_path(child)
    parent_resolved = canonical_path(parent)
    try:
        child_resolved.relative_to(parent_resolved)
    except ValueError:
        return False
    return True


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    clone = copy.deepcopy(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clone, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise DryRunBlocked(f"invalid JSONL in {path.name} line {line_number}: {exc}") from exc
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def extract_route_key(payload: dict[str, Any]) -> Any:
    direct = payload.get("route_key")
    if direct is not None:
        return direct
    for key in (
        "preview_identity",
        "dry_run_design_identity",
        "fixture_generation_identity",
        "fixture_threshold_contract_identity",
        "proposal_identity",
        "prior_proposal_preserved",
        "clean_room_identity",
    ):
        value = payload.get(key)
        if isinstance(value, dict) and value.get("route_key") is not None:
            return value.get("route_key")
    summary = payload.get("fixture_generation_summary")
    if isinstance(summary, dict):
        return summary.get("route_key")
    return None


def labels_present(labels: Any, required: list[str]) -> bool:
    if not isinstance(labels, list):
        return False
    return set(required).issubset(set(labels))


def detect_forbidden_keys(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_lower = str(key).lower()
            child_path = f"{path}.{key}" if path else str(key)
            if any(marker in key_lower for marker in SENSITIVE_FIELD_MARKERS):
                findings.append(child_path)
            findings.extend(detect_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(detect_forbidden_keys(child, f"{path}[{index}]"))
    return findings


def detect_forbidden_fixture_paths(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            findings.extend(detect_forbidden_fixture_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(detect_forbidden_fixture_paths(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lower_value = value.lower()
        path_like = ":\\" in value or ":/" in value or "\\" in value or "/" in value
        if not path_like:
            return findings
        for marker in RAW_OR_RUNTIME_PATH_MARKERS:
            marker_lower = marker.lower()
            if marker_lower in lower_value and marker not in SAFETY_LABELS:
                findings.append(path)
                break
    return findings


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rule_is_optional_when_present(rule: dict[str, Any]) -> bool:
    requirement = str(rule.get("requirement", ""))
    return "optional_when_present" in requirement


def compare_value(value: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return value >= threshold
    if operator == "<=":
        return value <= threshold
    if operator == ">":
        return value > threshold
    if operator == "<":
        return value < threshold
    if operator in ("=", "=="):
        return value == threshold
    raise DryRunBlocked(f"unsupported threshold operator: {operator}")


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
        raise DryRunBlocked(f"HEAD mismatch: expected {EXPECTED_HEAD}, got {actual_head}")
    if tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise DryRunBlocked(
            "tracked Python count mismatch: "
            f"expected {EXPECTED_TRACKED_PYTHON_COUNT}, got {tracked_python_count}"
        )
    if dirty_tracked:
        raise DryRunBlocked(f"tracked repo files modified before run: {dirty_tracked}")
    if unexpected_untracked:
        raise DryRunBlocked(f"unexpected untracked repo files before run: {unexpected_untracked}")
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
            raise DryRunBlocked(f"required source artifact missing: {relative_path}")
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


def validate_prior_artifacts(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    preview = loaded["runner_realistic_fixture_dry_run_preview"]["payload"]
    design = loaded["runner_realistic_fixture_dry_run_design"]["payload"]
    generation = loaded["realistic_bounded_fixture_generation_dry_run"]["payload"]
    threshold = loaded["runner_fixture_threshold_contract"]["payload"]

    if preview.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PREVIEW_CREATED":
        raise DryRunBlocked("prior preview status mismatch")
    if preview.get("next_allowed_step") != PRIOR_NEXT_ALLOWED_STEP:
        raise DryRunBlocked("prior preview next_allowed_step mismatch")
    if extract_route_key(preview) != ROUTE_KEY:
        raise DryRunBlocked("prior preview route_key mismatch")
    if design.get("next_allowed_step") != "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PREVIEW_V1":
        raise DryRunBlocked("prior design next_allowed_step mismatch")
    if extract_route_key(design) != ROUTE_KEY:
        raise DryRunBlocked("prior design route_key mismatch")
    if extract_route_key(generation) != ROUTE_KEY:
        raise DryRunBlocked("prior fixture generation route_key mismatch")

    threshold_identity = threshold.get("fixture_threshold_contract_identity", {})
    completeness = threshold.get("contract_completeness", {})
    if extract_route_key(threshold) != ROUTE_KEY:
        raise DryRunBlocked("threshold contract route_key mismatch")
    if completeness.get("contract_complete") is not True:
        raise DryRunBlocked("threshold contract incomplete")
    if completeness.get("family_threshold_count") != 2:
        raise DryRunBlocked("threshold family count is not 2")
    if threshold_identity.get("original_exact_thresholds_recovered") is not False:
        raise DryRunBlocked("threshold contract claims original exact thresholds")
    for family in ("blowoff_short", "mean_reversion_short"):
        family_contract = threshold.get("threshold_families", {}).get(family, {})
        if not labels_present(family_contract.get("labels"), THRESHOLD_LABELS):
            raise DryRunBlocked(f"threshold labels missing for {family}")
        if family_contract.get("side") != "short":
            raise DryRunBlocked(f"threshold side is not short for {family}")

    for name, loaded_source in loaded.items():
        payload = loaded_source["payload"]
        permissions = payload.get("safety_permissions", {})
        forbidden_true = [
            key
            for key, value in permissions.items()
            if key.endswith("_allowed_now")
            and key
            in {
                "runner_execution_allowed_now",
                "signal_generation_allowed_now",
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
            }
            and value is not False
        ]
        if forbidden_true:
            raise DryRunBlocked(f"forbidden permissions true in {name}: {forbidden_true}")

    return {
        "prior_preview_status": preview.get("status"),
        "prior_preview_next_allowed_step": preview.get("next_allowed_step"),
        "prior_preview_route_key": extract_route_key(preview),
        "prior_design_status": design.get("status"),
        "threshold_contract_complete": True,
        "family_threshold_count": 2,
        "original_exact_source_recovered": False,
        "no_edge_live_capital_permissions": True,
    }


def load_fixture_package() -> dict[str, Any]:
    if not APPROVED_FIXTURE_ROOT.exists():
        raise DryRunBlocked(f"fixture root missing: {APPROVED_FIXTURE_ROOT}")
    if not APPROVED_FIXTURE_ROOT.is_dir():
        raise DryRunBlocked(f"fixture root is not a directory: {APPROVED_FIXTURE_ROOT}")

    fixture_root = canonical_path(APPROVED_FIXTURE_ROOT)
    approved_root = canonical_path(APPROVED_FIXTURE_ROOT)
    if fixture_root != approved_root:
        raise DryRunBlocked("fixture root is not the approved root")

    missing_files = [
        name for name in REQUIRED_FIXTURE_FILES if not (APPROVED_FIXTURE_ROOT / name).exists()
    ]
    if missing_files:
        raise DryRunBlocked(f"fixture files missing: {missing_files}")

    fixture_index = load_json(APPROVED_FIXTURE_ROOT / "fixture_index.json")
    master_proxy_cases = load_jsonl(APPROVED_FIXTURE_ROOT / "master_proxy_cases.jsonl")
    replay_inputs = load_jsonl(APPROVED_FIXTURE_ROOT / "clean_room_replay_fixture_inputs.jsonl")
    validation_pairs = load_jsonl(APPROVED_FIXTURE_ROOT / "validation_pair_fixtures.jsonl")
    fixture_summary = load_json(APPROVED_FIXTURE_ROOT / "fixture_generation_summary.json")

    if fixture_index.get("route_key") != ROUTE_KEY:
        raise DryRunBlocked("fixture_index route_key mismatch")
    if fixture_summary.get("route_key") != ROUTE_KEY:
        raise DryRunBlocked("fixture_generation_summary route_key mismatch")

    for file_name in REQUIRED_FIXTURE_FILES:
        file_path = canonical_path(APPROVED_FIXTURE_ROOT / file_name)
        if not is_under(file_path, APPROVED_FIXTURE_ROOT):
            raise DryRunBlocked(f"fixture file outside approved root: {file_path}")

    return {
        "fixture_index": fixture_index,
        "master_proxy_cases": master_proxy_cases,
        "clean_room_replay_fixture_inputs": replay_inputs,
        "validation_pair_fixtures": validation_pairs,
        "fixture_generation_summary": fixture_summary,
        "fixture_file_hashes": {
            name: sha256_file(APPROVED_FIXTURE_ROOT / name) for name in REQUIRED_FIXTURE_FILES
        },
    }


def validate_fixture_safety(package: dict[str, Any]) -> dict[str, Any]:
    fixture_objects: list[dict[str, Any]] = []
    fixture_objects.extend(package["master_proxy_cases"])
    fixture_objects.extend(package["clean_room_replay_fixture_inputs"])
    fixture_objects.extend(package["validation_pair_fixtures"])

    missing_label_cases = [
        obj.get("fixture_case_id")
        or obj.get("clean_room_replay_input_id")
        or obj.get("fixture_pair_id")
        or "unknown_fixture"
        for obj in fixture_objects
        if not labels_present(obj.get("safety_labels"), SAFETY_LABELS)
    ]
    if missing_label_cases:
        raise DryRunBlocked(f"fixture safety labels missing: {missing_label_cases}")

    forbidden_keys = detect_forbidden_keys(fixture_objects)
    if forbidden_keys:
        raise DryRunBlocked(f"private/account/order/live fields detected: {forbidden_keys}")

    forbidden_paths = detect_forbidden_fixture_paths(fixture_objects)
    if forbidden_paths:
        raise DryRunBlocked(f"raw market or runtime path supplied in fixture: {forbidden_paths}")

    return {
        "fixture_rows_checked": len(fixture_objects),
        "safety_label_audit_passed": True,
        "missing_label_cases": [],
        "private_account_order_live_fields_detected": [],
        "raw_market_or_runtime_paths_detected": [],
    }


def threshold_required_features(threshold_rules: dict[str, Any]) -> list[str]:
    required: list[str] = []
    for feature, rule in threshold_rules.items():
        if not isinstance(rule, dict):
            continue
        if not rule_is_optional_when_present(rule):
            required.append(feature)
    return sorted(required)


def evaluate_thresholds(
    replay_case: dict[str, Any],
    family_contract: dict[str, Any],
) -> dict[str, Any]:
    features = replay_case.get("signal_features", {})
    if not isinstance(features, dict):
        raise DryRunBlocked(f"signal_features is not an object for {replay_case.get('fixture_case_id')}")
    threshold_rules = family_contract.get("threshold_rules", {})
    if not isinstance(threshold_rules, dict) or not threshold_rules:
        raise DryRunBlocked(f"threshold missing for family {replay_case.get('family')}")

    required_features = threshold_required_features(threshold_rules)
    missing_required = [feature for feature in required_features if feature not in features]
    if missing_required:
        return {
            "threshold_evaluated": False,
            "threshold_passed": False,
            "missing_required_features": missing_required,
            "failed_features": [],
            "passed_features": [],
        }

    failed_features: list[str] = []
    passed_features: list[str] = []
    for feature, rule in threshold_rules.items():
        if not isinstance(rule, dict):
            continue
        if feature not in features:
            if rule_is_optional_when_present(rule):
                continue
            failed_features.append(feature)
            continue
        observed = parse_float(features.get(feature))
        threshold = parse_float(rule.get("value"))
        operator = str(rule.get("operator", ""))
        if observed is None or threshold is None:
            failed_features.append(feature)
            continue
        if compare_value(observed, operator, threshold):
            passed_features.append(feature)
        else:
            failed_features.append(feature)

    return {
        "threshold_evaluated": True,
        "threshold_passed": not failed_features,
        "missing_required_features": [],
        "failed_features": failed_features,
        "passed_features": passed_features,
    }


def derive_gate_state(replay_case: dict[str, Any], master_by_id: dict[str, dict[str, Any]]) -> str:
    master_id = replay_case.get("paired_master_fixture_case_id")
    master_case = master_by_id.get(str(master_id), {})
    gate_state = master_case.get("gate_state")
    if gate_state in {"gate_blocked", "gate_missing_timeout", "gate_allowed"}:
        return str(gate_state)
    if gate_state == "gate_allowed_or_not_applicable":
        return "gate_allowed_or_not_applicable"
    if replay_case.get("reject_reason") == "global_gate_timeout_gate_file_missing":
        return "gate_missing_timeout"
    if replay_case.get("reject_reason"):
        return "gate_blocked"
    return "gate_absent"


def validate_replay_case(replay_case: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if replay_case.get("route_key") != ROUTE_KEY:
        reasons.append("route_key mismatch")
    if replay_case.get("family_key") != FAMILY_KEY:
        reasons.append("family_key mismatch")
    if replay_case.get("side") != "short":
        reasons.append("side not short")
    if not labels_present(replay_case.get("safety_labels"), SAFETY_LABELS):
        reasons.append("safety labels missing")
    return reasons


def process_fixture_cases(
    package: dict[str, Any],
    threshold_contract: dict[str, Any],
) -> dict[str, Any]:
    master_by_id = {
        str(row.get("fixture_case_id")): row for row in package["master_proxy_cases"]
    }
    family_contracts = threshold_contract.get("threshold_families", {})

    processed_cases: list[dict[str, Any]] = []
    signals_rows: list[dict[str, Any]] = []
    pending_rows: list[dict[str, Any]] = []
    open_rows: list[dict[str, Any]] = []
    closed_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    heartbeat_rows: list[dict[str, Any]] = []

    missing_feature_fail_count = 0
    threshold_miss_fail_count = 0
    fail_closed_count = 0
    gate_blocked_count = 0
    gate_missing_timeout_count = 0
    gate_allowed_count = 0
    passed_case_count = 0
    rejected_case_count = 0
    processed_family_set: set[str] = set()
    observed_gate_states: set[str] = set()
    accepted_lifecycle_coverage_present = False

    for replay_case in package["clean_room_replay_fixture_inputs"]:
        case_id = str(replay_case.get("fixture_case_id"))
        family = str(replay_case.get("family"))
        gate_state = derive_gate_state(replay_case, master_by_id)
        validation_failures = validate_replay_case(replay_case)

        case_record: dict[str, Any] = {
            "fixture_case_id": case_id,
            "route_key": replay_case.get("route_key"),
            "family_key": replay_case.get("family_key"),
            "family": family,
            "side": replay_case.get("side"),
            "gate_state": gate_state,
            "safety_labels_present": labels_present(replay_case.get("safety_labels"), SAFETY_LABELS),
            "validation_failures": validation_failures,
            "threshold_evaluated": False,
            "threshold_passed": None,
            "missing_required_features": [],
            "threshold_failed_features": [],
            "paper_output_action": None,
            "result": None,
        }

        if validation_failures:
            fail_closed_count += 1
            case_record["result"] = "fail_closed"
            processed_cases.append(case_record)
            continue

        if family == "heartbeat_state":
            heartbeat_rows.append(
                {
                    "fixture_case_id": case_id,
                    "route_key": ROUTE_KEY,
                    "family_key": FAMILY_KEY,
                    "family": family,
                    "heartbeat_kind": "state_fixture",
                    "paper_only": "true",
                    "safety_labels": "|".join(SAFETY_LABELS),
                }
            )
            case_record["paper_output_action"] = "heartbeat.csv/state.json"
            case_record["result"] = "processed_heartbeat_state"
            processed_cases.append(case_record)
            continue

        processed_family_set.add(family)
        if gate_state in {"gate_blocked", "gate_missing_timeout"}:
            observed_gate_states.add(gate_state)
        if gate_state == "gate_blocked":
            gate_blocked_count += 1
        elif gate_state == "gate_missing_timeout":
            gate_missing_timeout_count += 1
        elif gate_state == "gate_allowed":
            gate_allowed_count += 1
            accepted_lifecycle_coverage_present = True
        elif gate_state not in {"gate_allowed_or_not_applicable", "gate_absent"}:
            fail_closed_count += 1
            case_record["result"] = "fail_closed_unsupported_gate_state"
            processed_cases.append(case_record)
            continue

        family_contract = family_contracts.get(family)
        if not isinstance(family_contract, dict):
            threshold_miss_fail_count += 1
            fail_closed_count += 1
            case_record["result"] = "fail_closed_threshold_missing"
            processed_cases.append(case_record)
            continue

        threshold_result = evaluate_thresholds(replay_case, family_contract)
        case_record["threshold_evaluated"] = threshold_result["threshold_evaluated"]
        case_record["threshold_passed"] = threshold_result["threshold_passed"]
        case_record["missing_required_features"] = threshold_result["missing_required_features"]
        case_record["threshold_failed_features"] = threshold_result["failed_features"]

        if threshold_result["missing_required_features"]:
            missing_feature_fail_count += 1
            fail_closed_count += 1
            case_record["result"] = "fail_closed_missing_required_feature"
            processed_cases.append(case_record)
            continue

        features = replay_case.get("signal_features", {})
        signals_rows.append(
            {
                "fixture_case_id": case_id,
                "route_key": ROUTE_KEY,
                "family_key": FAMILY_KEY,
                "family": family,
                "side": "short",
                "signal_time": replay_case.get("signal_time"),
                "gate_state": gate_state,
                "threshold_passed": str(threshold_result["threshold_passed"]).lower(),
                "threshold_failed_features": "|".join(threshold_result["failed_features"]),
                **{feature: features.get(feature, "") for feature in SIGNAL_FEATURES},
                "safety_labels": "|".join(SAFETY_LABELS),
            }
        )

        reject_reason = replay_case.get("reject_reason")
        if not threshold_result["threshold_passed"]:
            reject_reason = "threshold_contract_not_satisfied"
        if gate_state in {"gate_blocked", "gate_missing_timeout"}:
            reject_reason = replay_case.get("reject_reason") or gate_state

        if reject_reason:
            rejected_case_count += 1
            rejected_rows.append(
                {
                    "fixture_case_id": case_id,
                    "route_key": ROUTE_KEY,
                    "family_key": FAMILY_KEY,
                    "family": family,
                    "side": "short",
                    "signal_time": replay_case.get("signal_time"),
                    "gate_state": gate_state,
                    "reject_reason": reject_reason,
                    "threshold_failed_features": "|".join(threshold_result["failed_features"]),
                    "paper_only": "true",
                    "safety_labels": "|".join(SAFETY_LABELS),
                }
            )
            case_record["paper_output_action"] = "rejected_entries.csv"
            case_record["result"] = "rejected"
        elif gate_state == "gate_allowed":
            passed_case_count += 1
            pending_rows.append(
                {
                    "fixture_case_id": case_id,
                    "route_key": ROUTE_KEY,
                    "family_key": FAMILY_KEY,
                    "family": family,
                    "side": "short",
                    "signal_time": replay_case.get("signal_time"),
                    "entry_time": replay_case.get("entry_time"),
                    "gate_state": gate_state,
                    "paper_only": "true",
                    "safety_labels": "|".join(SAFETY_LABELS),
                }
            )
            if replay_case.get("entry_time"):
                open_rows.append(
                    {
                        "fixture_case_id": case_id,
                        "route_key": ROUTE_KEY,
                        "family_key": FAMILY_KEY,
                        "family": family,
                        "side": "short",
                        "entry_time": replay_case.get("entry_time"),
                        "planned_exit_time": replay_case.get("planned_exit_time"),
                        "paper_only": "true",
                        "safety_labels": "|".join(SAFETY_LABELS),
                    }
                )
            if replay_case.get("exit_time"):
                closed_rows.append(
                    {
                        "fixture_case_id": case_id,
                        "route_key": ROUTE_KEY,
                        "family_key": FAMILY_KEY,
                        "family": family,
                        "side": "short",
                        "entry_time": replay_case.get("entry_time"),
                        "exit_time": replay_case.get("exit_time"),
                        "planned_exit_time": replay_case.get("planned_exit_time"),
                        "paper_only": "true",
                        "safety_labels": "|".join(SAFETY_LABELS),
                    }
                )
            case_record["paper_output_action"] = "paper_open_closed_lifecycle"
            case_record["result"] = "paper_lifecycle_written"
        else:
            if threshold_result["threshold_passed"]:
                passed_case_count += 1
            case_record["paper_output_action"] = "signals.csv_only_no_explicit_gate_allowed"
            case_record["result"] = "processed_no_explicit_gate_allowed"

        processed_cases.append(case_record)

    gate_results = {
        "gate_blocked_count": gate_blocked_count,
        "gate_missing_timeout_count": gate_missing_timeout_count,
        "gate_allowed_count": gate_allowed_count,
        "observed_gate_state_coverage": sorted(observed_gate_states),
        "accepted_lifecycle_coverage_present": accepted_lifecycle_coverage_present,
        "gate_allowed_absent_policy_applied": gate_allowed_count == 0,
    }

    return {
        "processed_fixture_cases": processed_cases,
        "gate_fixture_results": gate_results,
        "output_rows": {
            "signals.csv": signals_rows,
            "pending_entries.csv": pending_rows,
            "open_positions.csv": open_rows,
            "closed_trades.csv": closed_rows,
            "rejected_entries.csv": rejected_rows,
            "heartbeat.csv": heartbeat_rows,
        },
        "counts": {
            "fixture_case_count": len(package["clean_room_replay_fixture_inputs"]),
            "processed_case_count": len(processed_cases),
            "family_coverage": sorted(processed_family_set),
            "gate_state_coverage": sorted(observed_gate_states),
            "passed_case_count": passed_case_count,
            "rejected_case_count": rejected_case_count,
            "fail_closed_count": fail_closed_count,
            "missing_feature_fail_count": missing_feature_fail_count,
            "threshold_miss_fail_count": threshold_miss_fail_count,
            "gate_blocked_count": gate_blocked_count,
            "gate_missing_timeout_count": gate_missing_timeout_count,
            "gate_allowed_count": gate_allowed_count,
            "accepted_lifecycle_coverage_present": accepted_lifecycle_coverage_present,
        },
    }


def choose_output_root() -> Path:
    base = APPROVED_EXTERNAL_OUTPUT_ROOT
    required = base / REQUIRED_EXTERNAL_SUBFOLDER_NAME
    base.mkdir(parents=True, exist_ok=True)
    if not is_under(required, base):
        raise DryRunBlocked("required output subfolder is outside approved external output root")
    if not required.exists():
        return required
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    versioned = base / f"{REQUIRED_EXTERNAL_SUBFOLDER_NAME}_{timestamp}"
    if versioned.exists():
        raise DryRunBlocked(f"versioned output root already exists: {versioned}")
    return versioned


def audit_output_labels(output_rows: dict[str, list[dict[str, Any]]], state_payload: dict[str, Any]) -> bool:
    for rows in output_rows.values():
        for row in rows:
            labels = str(row.get("safety_labels", "")).split("|")
            if not set(SAFETY_LABELS).issubset(set(labels)):
                return False
    return labels_present(state_payload.get("safety_labels"), SAFETY_LABELS)


def write_external_outputs(
    output_root: Path,
    output_rows: dict[str, list[dict[str, Any]]],
    state_payload: dict[str, Any],
    report_payload: dict[str, Any],
) -> dict[str, Any]:
    if not is_under(output_root, APPROVED_EXTERNAL_OUTPUT_ROOT):
        raise DryRunBlocked("output root is outside approved external output root")
    output_root.mkdir(parents=False, exist_ok=False)

    output_files = {
        "signals.csv": (SIGNALS_HEADER, output_rows["signals.csv"]),
        "pending_entries.csv": (PENDING_HEADER, output_rows["pending_entries.csv"]),
        "open_positions.csv": (OPEN_HEADER, output_rows["open_positions.csv"]),
        "closed_trades.csv": (CLOSED_HEADER, output_rows["closed_trades.csv"]),
        "rejected_entries.csv": (REJECTED_HEADER, output_rows["rejected_entries.csv"]),
        "heartbeat.csv": (HEARTBEAT_HEADER, output_rows["heartbeat.csv"]),
    }

    written_files: dict[str, dict[str, Any]] = {}
    for file_name, (headers, rows) in output_files.items():
        path = output_root / file_name
        write_csv(path, headers, rows)
        written_files[file_name] = {
            "path": str(path),
            "row_count": len(rows),
            "sha256": sha256_file(path),
        }

    state_path = output_root / "state.json"
    write_json(state_path, state_payload)
    written_files["state.json"] = {
        "path": str(state_path),
        "row_count": 1,
        "sha256": sha256_file(state_path),
    }

    report_path = output_root / "runner_realistic_fixture_dry_run_report.json"
    write_json(report_path, report_payload)
    written_files["runner_realistic_fixture_dry_run_report.json"] = {
        "path": str(report_path),
        "row_count": 1,
        "sha256": sha256_file(report_path),
    }

    return {
        "output_root": str(output_root),
        "approved_external_output_root": str(APPROVED_EXTERNAL_OUTPUT_ROOT),
        "generated_output_file_count": len(written_files),
        "files": written_files,
        "all_outputs_under_approved_root": all(
            is_under(Path(info["path"]), APPROVED_EXTERNAL_OUTPUT_ROOT)
            for info in written_files.values()
        ),
        "wrote_to_master_upper_system": False,
        "wrote_to_runtime_directory": False,
        "overwrote_existing_external_files": False,
    }


def summarize_sources(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        name: {
            key: value
            for key, value in source.items()
            if key not in {"payload"}
        }
        for name, source in loaded.items()
    }


def determine_classification(counts: dict[str, Any], safety_label_audit_passed: bool) -> str:
    if counts["fail_closed_count"] > 0 or not safety_label_audit_passed:
        return RESULT_FAIL_CLOSED
    both_families = set(counts["family_coverage"]) == {"blowoff_short", "mean_reversion_short"}
    blocked_missing = {"gate_blocked", "gate_missing_timeout"}.issubset(
        set(counts["gate_state_coverage"])
    )
    if both_families and blocked_missing:
        if counts["accepted_lifecycle_coverage_present"]:
            return RESULT_PASS
        return RESULT_PARTIAL
    if counts["processed_case_count"] > 0:
        return RESULT_INCONCLUSIVE
    return RESULT_FAIL_CLOSED


def build_dry_run_artifact(repo_root: Path) -> dict[str, Any]:
    source_checkpoint = build_source_checkpoint(repo_root)
    loaded_sources = load_source_artifacts(repo_root)
    prior_review = validate_prior_artifacts(loaded_sources)
    fixture_package = load_fixture_package()
    fixture_safety = validate_fixture_safety(fixture_package)
    threshold_contract = loaded_sources["runner_fixture_threshold_contract"]["payload"]
    processing = process_fixture_cases(fixture_package, threshold_contract)
    counts = processing["counts"]

    output_root = choose_output_root()
    accepted_lifecycle_coverage = {
        "accepted_lifecycle_coverage_present": counts["accepted_lifecycle_coverage_present"],
        "gate_allowed_count": counts["gate_allowed_count"],
        "open_positions_rows_written": len(processing["output_rows"]["open_positions.csv"]),
        "closed_trades_rows_written": len(processing["output_rows"]["closed_trades.csv"]),
        "limitation": (
            "gate_allowed/open-close lifecycle coverage absent; classification is PARTIAL at best"
            if counts["gate_allowed_count"] == 0
            else "gate_allowed fixture coverage present"
        ),
        "no_open_closed_lifecycle_equivalence_claim": counts["gate_allowed_count"] == 0,
    }

    dry_run_metrics = {
        **counts,
        "generated_output_file_count": 8,
        "safety_label_audit_passed": True,
        "no_pnl_used": True,
        "no_market_data_used": True,
        "no_edge_live_capital": True,
    }
    result_classification = determine_classification(counts, True)
    next_allowed_step = (
        NEXT_REVIEW_STEP
        if result_classification in {RESULT_PASS, RESULT_PARTIAL}
        else NEXT_REPAIR_STEP
    )

    state_payload = {
        "route_key": ROUTE_KEY,
        "artifact_kind": ARTIFACT_KIND,
        "result_classification": result_classification,
        "output_root": str(output_root),
        "paper_only": True,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "dry_run_metrics": dry_run_metrics,
        "safety_labels": list(SAFETY_LABELS),
    }

    external_report_payload = {
        "status": STATUS,
        "artifact_kind": "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REPORT",
        "route_key": ROUTE_KEY,
        "result_classification": result_classification,
        "processed_fixture_cases": processing["processed_fixture_cases"],
        "gate_fixture_results": processing["gate_fixture_results"],
        "dry_run_metrics": dry_run_metrics,
        "accepted_lifecycle_coverage": accepted_lifecycle_coverage,
        "safety_labels": list(SAFETY_LABELS),
        "no_backtest_runtime_live_capital": True,
    }

    safety_output_labels_passed = audit_output_labels(processing["output_rows"], state_payload)
    if not safety_output_labels_passed:
        raise DryRunBlocked("output safety label audit failed before write")

    generated_output_summary = write_external_outputs(
        output_root,
        processing["output_rows"],
        state_payload,
        external_report_payload,
    )

    dry_run_metrics["generated_output_file_count"] = generated_output_summary[
        "generated_output_file_count"
    ]

    fixture_summary = fixture_package["fixture_generation_summary"]
    fixture_package_review = {
        "fixture_root": str(APPROVED_FIXTURE_ROOT),
        "fixture_root_is_approved": True,
        "required_fixture_files": list(REQUIRED_FIXTURE_FILES),
        "required_fixture_files_loaded": True,
        "fixture_file_hashes": fixture_package["fixture_file_hashes"],
        "fixture_case_count": fixture_summary.get("fixture_case_count"),
        "clean_room_replay_fixture_input_count": len(
            fixture_package["clean_room_replay_fixture_inputs"]
        ),
        "master_proxy_case_count": len(fixture_package["master_proxy_cases"]),
        "validation_pair_fixture_count": len(fixture_package["validation_pair_fixtures"]),
        "family_coverage": fixture_summary.get("family_coverage", counts["family_coverage"]),
        "gate_state_coverage": fixture_summary.get(
            "gate_state_coverage", counts["gate_state_coverage"]
        ),
        "no_pnl_selection_confirmed": fixture_summary.get("no_pnl_selection_confirmed") is True,
        "no_raw_market_data_confirmed": fixture_summary.get("no_raw_market_data_confirmed")
        is True,
    }

    threshold_completeness = threshold_contract.get("contract_completeness", {})
    threshold_contract_review = {
        "threshold_contract_loaded": True,
        "route_key": ROUTE_KEY,
        "contract_complete": threshold_completeness.get("contract_complete") is True,
        "family_threshold_count": threshold_completeness.get("family_threshold_count"),
        "family_threshold_count_verified_2": threshold_completeness.get("family_threshold_count")
        == 2,
        "families_expected": threshold_completeness.get("families_expected"),
        "required_labels": list(THRESHOLD_LABELS),
        "required_labels_verified": True,
        "threshold_selection_allowed": False,
        "pnl_optimization_allowed": False,
    }

    safety_label_audit = {
        **fixture_safety,
        "output_rows_checked": sum(len(rows) for rows in processing["output_rows"].values()),
        "output_safety_label_audit_passed": safety_output_labels_passed,
        "safety_labels_present": True,
        "required_labels": list(SAFETY_LABELS),
    }

    safety_permissions = {
        "runner_realistic_fixture_dry_run_created": True,
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
        "prior_realistic_fixture_dry_run_preview_loaded": True,
        "prior_next_allowed_step_verified": prior_review["prior_preview_next_allowed_step"]
        == PRIOR_NEXT_ALLOWED_STEP,
        "fixture_package_loaded": True,
        "threshold_contract_loaded": True,
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
        "external_output_root_used": generated_output_summary["all_outputs_under_approved_root"],
        "no_master_upper_system_modified": not generated_output_summary[
            "wrote_to_master_upper_system"
        ],
        "no_runtime_directory_modified": not generated_output_summary[
            "wrote_to_runtime_directory"
        ],
        "output_files_created": generated_output_summary["generated_output_file_count"] == 8,
        "safety_labels_present": safety_label_audit["safety_labels_present"],
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": source_checkpoint["no_existing_repo_files_modified"],
        "replacement_checks_all_true": True,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())

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
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "realistic_fixture_dry_run_only": True,
            "not_real_market_execution": True,
            "not_full_runner_execution_on_historical_data": True,
            "not_full_dataset_comparison": True,
            "not_backtest": True,
            "not_pnl_computation": True,
            "not_runtime_enablement": True,
            "not_live_trading": True,
            "not_capital_allocation": True,
            "not_candidate_generation": True,
            "not_edge_claim": True,
            "original_exact_source_recovered": False,
            "clean_room_behavioral_reconstruction": True,
        },
        "fixture_package_review": fixture_package_review,
        "threshold_contract_review": threshold_contract_review,
        "processed_fixture_cases": processing["processed_fixture_cases"],
        "gate_fixture_results": processing["gate_fixture_results"],
        "generated_output_summary": generated_output_summary,
        "dry_run_metrics": dry_run_metrics,
        "accepted_lifecycle_coverage": accepted_lifecycle_coverage,
        "safety_label_audit": safety_label_audit,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
            "gate_allowed/open-close lifecycle coverage absent unless later fixture adds it",
        ],
        "limitations": [
            "Realistic fixture dry-run only; not real market execution.",
            "No raw market data, raw OKX 1m data, full dataset comparison, backtest, or PnL computation was used.",
            "No runtime, monitor, live, capital, private API, order placement, candidate generation, or edge claim was enabled.",
            "Closed-trade proxy examples are not treated as accepted lifecycle coverage without an explicit gate_allowed fixture.",
            "Accepted open-close lifecycle coverage is absent, so PARTIAL classification is expected.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash_excluding_hash(artifact)
    return artifact


def write_artifact_once(repo_root: Path, artifact: dict[str, Any]) -> None:
    artifact_path = repo_root / ARTIFACT_RELATIVE_PATH
    if artifact_path.exists():
        raise DryRunBlocked(f"target artifact already exists: {ARTIFACT_RELATIVE_PATH}")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(artifact_path, artifact)


def print_summary(artifact: dict[str, Any]) -> None:
    metrics = artifact["dry_run_metrics"]
    print(f"status: {artifact['status']}")
    print(f"route_key: {artifact['dry_run_identity']['route_key']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"output_root: {artifact['generated_output_summary']['output_root']}")
    print(f"fixture_case_count: {metrics['fixture_case_count']}")
    print(f"processed_case_count: {metrics['processed_case_count']}")
    print(f"family_coverage: {','.join(metrics['family_coverage'])}")
    print(f"gate_state_coverage: {','.join(metrics['gate_state_coverage'])}")
    print(f"gate_allowed_count: {metrics['gate_allowed_count']}")
    print(
        "accepted_lifecycle_coverage_present: "
        f"{str(metrics['accepted_lifecycle_coverage_present']).lower()}"
    )
    print(f"fail_closed_count: {metrics['fail_closed_count']}")
    print(f"generated_output_file_count: {metrics['generated_output_file_count']}")
    print(
        "safety_label_audit_passed: "
        f"{str(metrics['safety_label_audit_passed']).lower()}"
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
        artifact = build_dry_run_artifact(repo_root)
        if not artifact["replacement_checks_all_true"]:
            raise DryRunBlocked("replacement checks are not all true")
        write_artifact_once(repo_root, artifact)
        print_summary(artifact)
        return 0
    except DryRunBlocked as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: {exc.reason}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2
    except Exception as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: unexpected dry-run failure: {exc}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2


if __name__ == "__main__":
    sys.exit(main())
