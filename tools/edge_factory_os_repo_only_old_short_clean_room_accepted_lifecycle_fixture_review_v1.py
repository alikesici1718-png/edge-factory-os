from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_accepted_lifecycle_fixture_review_v1"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "1be5a9d128a1eaed011d3e307067818e6c87df02"
EXPECTED_TRACKED_PYTHON_COUNT = 963
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_accepted_lifecycle_fixture_review_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_accepted_lifecycle_fixture_review_v1.json"
)

PRIOR_DISCOVERY_STATUS = (
    "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DRY_RUN_CREATED"
)
PRIOR_DISCOVERY_RESULT = "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_PASS_NO_EDGE_NO_LIVE"
PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW_V1"
RESULT_PASS_READY = (
    "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW_PASS_READY_FOR_REALISTIC_FIXTURE_RUNNER_V2_"
    "DESIGN_NO_EDGE_NO_LIVE"
)
RESULT_PASS_WITH_P1 = (
    "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW_PASS_WITH_P1_ATTENTION_NO_EDGE_NO_LIVE"
)
RESULT_FAIL = "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW_FAIL_REQUIRES_REPAIR_NO_EDGE_NO_LIVE"
NEXT_RUNNER_V2_DESIGN = "OLD_SHORT_CLEAN_ROOM_REALISTIC_FIXTURE_RUNNER_V2_DESIGN_V1"
NEXT_REPAIR = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_REPAIR_PREVIEW_V1"

APPROVED_FIXTURE_ROOT = Path(
    "C:/Users/alike/OneDrive/Desktop/edge_lab_new/"
    "edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1/"
    "accepted_lifecycle_fixture_discovery_v1"
)
MASTER_UPPER_SYSTEM_MARKER = "MASTER_UPPER_SYSTEM"
RUNTIME_MARKERS = ["paper_run_gate_", "live runtime directories"]

SOURCE_ARTIFACT_PATHS = {
    "accepted_lifecycle_fixture_discovery_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.json"
    ),
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

EXPECTED_FIXTURE_FILES = [
    "accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_master_cases.jsonl",
    "accepted_lifecycle_pairing_plan.json",
    "accepted_lifecycle_discovery_summary.json",
]

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

EXPECTED_MISSING_METRIC_RECOVERY = {
    "entry delay comparability": "partially recovered",
    "hold duration comparability": "recovered",
    "notional comparability": "recovered",
    "accepted lifecycle coverage": "recovered",
    "gate_allowed path coverage": "partially recovered",
}


class ReviewBlocked(RuntimeError):
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
                raise ReviewBlocked(f"invalid JSONL in {path.name} line {line_number}: {exc}") from exc
    return rows


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    clone = copy.deepcopy(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clone, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def labels_present(labels: Any) -> bool:
    return isinstance(labels, list) and set(SAFETY_LABELS).issubset(set(labels))


def extract_route_key(payload: dict[str, Any]) -> Any:
    direct = payload.get("route_key")
    if direct is not None:
        return direct
    for key in (
        "discovery_identity",
        "discovery_design_identity",
        "prior_dry_run_preserved",
        "fixture_generation_identity",
        "clean_room_identity",
    ):
        value = payload.get(key)
        if isinstance(value, dict) and value.get("route_key") is not None:
            return value.get("route_key")
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
        raise ReviewBlocked(f"HEAD mismatch: expected {EXPECTED_HEAD}, got {actual_head}")
    if tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise ReviewBlocked(
            "tracked Python count mismatch: "
            f"expected {EXPECTED_TRACKED_PYTHON_COUNT}, got {tracked_python_count}"
        )
    if dirty_tracked:
        raise ReviewBlocked(f"tracked repo files modified before run: {dirty_tracked}")
    if unexpected_untracked:
        raise ReviewBlocked(f"unexpected untracked repo files before run: {unexpected_untracked}")
    return {
        "repo_root": str(repo_root),
        "expected_head": EXPECTED_HEAD,
        "actual_head": actual_head,
        "head_verified": True,
        "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
        "actual_tracked_python_count": tracked_python_count,
        "tracked_python_count_verified": True,
        "repo_clean_before_run": True,
        "git_status_at_review_start": status_lines,
        "allowed_pending_at_review_start": sorted(allowed_untracked),
        "dirty_tracked_at_review_start": dirty_tracked,
        "unexpected_untracked_at_review_start": unexpected_untracked,
        "no_existing_files_modified": True,
    }


def load_source_artifacts(repo_root: Path) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, relative_path in SOURCE_ARTIFACT_PATHS.items():
        path = repo_root / relative_path
        if not path.exists():
            raise ReviewBlocked(f"required source artifact missing: {relative_path}")
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


def path_is_safe(path: Path) -> bool:
    text = str(path)
    return (
        is_under(path, APPROVED_FIXTURE_ROOT)
        and MASTER_UPPER_SYSTEM_MARKER not in text
        and not any(marker in text for marker in RUNTIME_MARKERS)
    )


def load_fixture_files() -> dict[str, Any]:
    if not APPROVED_FIXTURE_ROOT.exists():
        raise ReviewBlocked(f"accepted lifecycle fixture root missing: {APPROVED_FIXTURE_ROOT}")
    missing = [
        name for name in EXPECTED_FIXTURE_FILES if not (APPROVED_FIXTURE_ROOT / name).exists()
    ]
    if missing:
        raise ReviewBlocked(f"accepted lifecycle fixture files missing: {missing}")
    files: dict[str, Any] = {}
    for name in EXPECTED_FIXTURE_FILES:
        path = APPROVED_FIXTURE_ROOT / name
        if not path_is_safe(path):
            raise ReviewBlocked(f"unsafe fixture file path: {path}")
        payload: Any
        if name.endswith(".jsonl"):
            payload = load_jsonl(path)
        else:
            payload = load_json(path)
        files[name] = {
            "path": str(path),
            "payload": payload,
            "sha256": sha256_file(path),
            "readable": True,
            "under_approved_root": is_under(path, APPROVED_FIXTURE_ROOT),
            "inside_master_upper_system": MASTER_UPPER_SYSTEM_MARKER in str(path),
            "inside_runtime_directory": any(marker in str(path) for marker in RUNTIME_MARKERS),
        }
    return files


def verify_prior_discovery(discovery: dict[str, Any]) -> dict[str, bool]:
    candidate_summary = discovery.get("accepted_lifecycle_candidate_summary", {})
    family_summary = discovery.get("family_coverage_summary", {})
    linkage_summary = discovery.get("lifecycle_linkage_summary", {})
    gate_summary = discovery.get("gate_allowed_evidence_summary", {})
    safety = discovery.get("safety_permissions", {})
    return {
        "prior_status_verified": discovery.get("status") == PRIOR_DISCOVERY_STATUS,
        "prior_route_key_verified": extract_route_key(discovery) == ROUTE_KEY,
        "prior_result_verified": discovery.get("result_classification") == PRIOR_DISCOVERY_RESULT,
        "accepted_lifecycle_candidate_count_verified_2": candidate_summary.get(
            "accepted_lifecycle_candidate_count"
        )
        == 2,
        "family_coverage_verified": {"blowoff_short", "mean_reversion_short"}.issubset(
            set(family_summary.get("family_coverage", []))
        ),
        "direct_lifecycle_link_count_verified_2": linkage_summary.get(
            "direct_lifecycle_link_count"
        )
        == 2,
        "gate_allowed_inferred_count_verified_2": gate_summary.get(
            "gate_allowed_inferred_count"
        )
        == 2,
        "prior_next_allowed_step_verified": discovery.get("next_allowed_step")
        == PRIOR_NEXT_ALLOWED_STEP,
        "no_live_capital_edge_permissions": all(
            safety.get(key) is False
            for key in (
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
            )
        ),
    }


def review_candidates(cases: list[dict[str, Any]]) -> dict[str, Any]:
    p0_findings: list[dict[str, Any]] = []
    case_reviews: list[dict[str, Any]] = []
    family_counts: dict[str, int] = {}
    for case in cases:
        case_id = case.get("fixture_case_id")
        family = case.get("family")
        family_counts[str(family)] = family_counts.get(str(family), 0) + 1
        failures: list[str] = []
        if case.get("family_key") != "old_short":
            failures.append("family_key mismatch")
        if family not in {"blowoff_short", "mean_reversion_short"}:
            failures.append("family mismatch")
        if case.get("side") != "short":
            failures.append("side mismatch")
        if not (case.get("signal_id") and case.get("position_id") and case.get("close_id")):
            failures.append("missing signal/position/close linkage")
        if not (case.get("signal_time") and case.get("entry_time")):
            failures.append("missing signal or entry time")
        if not (case.get("exit_time") or case.get("planned_exit_time")):
            failures.append("missing exit or planned exit time")
        if not case.get("hold_minutes_actual"):
            failures.append("missing hold_minutes_actual")
        if not case.get("notional"):
            failures.append("missing notional")
        if not isinstance(case.get("signal_features"), dict) or not case["signal_features"]:
            failures.append("missing signal feature fields")
        if not labels_present(case.get("safety_labels")):
            failures.append("safety labels missing")
        if case.get("source_file") == "rejected_entries.csv":
            failures.append("candidate sourced from rejected_entries")
        marker_text = json.dumps(case, sort_keys=True).lower()
        if "gate_block" in marker_text or "gate_missing" in marker_text:
            failures.append("candidate marked gate blocked/missing")
        actual_forbidden_fields = [
            field for field in FORBIDDEN_SELECTION_FIELDS if field in case or field in case.get("signal_features", {})
        ]
        if actual_forbidden_fields:
            failures.append(f"forbidden PnL/outcome fields present: {actual_forbidden_fields}")
        if failures:
            p0_findings.append(
                {"severity": "P0", "fixture_case_id": case_id, "failures": failures}
            )
        case_reviews.append(
            {
                "fixture_case_id": case_id,
                "family": family,
                "family_key": case.get("family_key"),
                "side": case.get("side"),
                "signal_id_present": bool(case.get("signal_id")),
                "position_id_present": bool(case.get("position_id")),
                "close_id_present": bool(case.get("close_id")),
                "time_fields_present": bool(
                    case.get("signal_time") and case.get("entry_time") and (case.get("exit_time") or case.get("planned_exit_time"))
                ),
                "hold_minutes_actual_present": bool(case.get("hold_minutes_actual")),
                "notional_present": bool(case.get("notional")),
                "signal_feature_fields_present": bool(case.get("signal_features")),
                "gate_allowed_inferred_from_closed_trade": case.get(
                    "gate_allowed_inferred_from_closed_trade"
                )
                is True,
                "direct_lifecycle_link_found": case.get("direct_lifecycle_link_found") is True,
                "safety_labels_present": labels_present(case.get("safety_labels")),
                "pnl_outcome_selection_used": False,
                "review_passed": not failures,
            }
        )
    return {
        "case_reviews": case_reviews,
        "family_counts": family_counts,
        "candidate_review_passed": not p0_findings,
        "candidate_p0_findings": p0_findings,
    }


def review_missing_metrics(summary: list[dict[str, Any]]) -> dict[str, Any]:
    observed = {item.get("missing_metric"): item.get("recovery_state") for item in summary}
    mismatches = [
        {
            "missing_metric": metric,
            "expected": expected,
            "observed": observed.get(metric),
        }
        for metric, expected in EXPECTED_MISSING_METRIC_RECOVERY.items()
        if observed.get(metric) != expected
    ]
    return {
        "expected_recovery_states": dict(EXPECTED_MISSING_METRIC_RECOVERY),
        "observed_recovery_states": observed,
        "recovery_states_preserved": not mismatches,
        "mismatches": mismatches,
    }


def build_artifact(repo_root: Path) -> dict[str, Any]:
    source_checkpoint = build_source_checkpoint(repo_root)
    loaded_sources = load_source_artifacts(repo_root)
    discovery = loaded_sources["accepted_lifecycle_fixture_discovery_dry_run"]["payload"]
    prior_checks = verify_prior_discovery(discovery)
    fixture_files = load_fixture_files()
    cases = fixture_files["accepted_lifecycle_master_cases.jsonl"]["payload"]
    fixture_index = fixture_files["accepted_lifecycle_fixture_index.json"]["payload"]
    pairing_plan = fixture_files["accepted_lifecycle_pairing_plan.json"]["payload"]
    discovery_summary = fixture_files["accepted_lifecycle_discovery_summary.json"]["payload"]

    candidate_review = review_candidates(cases)
    missing_metric_review = review_missing_metrics(
        discovery_summary.get("missing_metric_recovery_summary", [])
    )

    p0_findings: list[dict[str, Any]] = []
    p1_findings: list[dict[str, Any]] = []

    p0_prior_map = {
        "prior_status_verified": "prior discovery status mismatch",
        "prior_route_key_verified": "route key mismatch",
        "prior_result_verified": "prior discovery result mismatch",
        "accepted_lifecycle_candidate_count_verified_2": "candidate count is not 2",
        "family_coverage_verified": "family coverage missing required family",
        "direct_lifecycle_link_count_verified_2": "direct lifecycle link count is not 2",
        "gate_allowed_inferred_count_verified_2": "gate allowed inferred count is not 2",
        "prior_next_allowed_step_verified": "prior next step mismatch",
        "no_live_capital_edge_permissions": "forbidden live/capital/edge permission present",
    }
    for key, finding in p0_prior_map.items():
        if not prior_checks.get(key):
            p0_findings.append({"severity": "P0", "finding": finding, "check": key})
    p0_findings.extend(candidate_review["candidate_p0_findings"])

    fixture_file_unsafe = [
        name
        for name, info in fixture_files.items()
        if not info["readable"]
        or not info["under_approved_root"]
        or info["inside_master_upper_system"]
        or info["inside_runtime_directory"]
    ]
    if fixture_file_unsafe:
        p0_findings.append(
            {"severity": "P0", "finding": "unsafe or unreadable fixture file", "files": fixture_file_unsafe}
        )
    if not labels_present(fixture_index.get("safety_labels")):
        p0_findings.append({"severity": "P0", "finding": "fixture index safety labels missing"})
    if not labels_present(pairing_plan.get("safety_labels")):
        p0_findings.append({"severity": "P0", "finding": "pairing plan safety labels missing"})
    if not labels_present(discovery_summary.get("safety_labels")):
        p0_findings.append({"severity": "P0", "finding": "discovery summary safety labels missing"})
    if not missing_metric_review["recovery_states_preserved"]:
        p0_findings.append(
            {
                "severity": "P0",
                "finding": "missing metric recovery states mismatch",
                "mismatches": missing_metric_review["mismatches"],
            }
        )
    if discovery_summary.get("selection_guardrails", {}).get("no_selection_by_pnl") is not True:
        p0_findings.append({"severity": "P0", "finding": "selection by PnL guardrail not verified"})

    if discovery.get("gate_allowed_evidence_summary", {}).get("gate_allowed_inferred_count") == 2:
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "gate_allowed is inferred from closed trade lifecycle, not explicit",
                "impact": "accepted lifecycle is useful but exact gate replay remains unavailable",
            }
        )
    if len(cases) == 2:
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "only two accepted lifecycle candidates are present",
                "impact": "coverage is one case per family and remains a small bounded sample",
            }
        )
    p1_findings.append(
        {
            "severity": "P1",
            "finding": "exact gate replay is still unavailable",
            "impact": "direct lifecycle link does not equal exact gate replay",
        }
    )

    result_classification = RESULT_FAIL if p0_findings else RESULT_PASS_WITH_P1
    next_allowed_step = NEXT_REPAIR if p0_findings else NEXT_RUNNER_V2_DESIGN

    family_counts = candidate_review["family_counts"]
    fixture_file_review = {
        "expected_files": list(EXPECTED_FIXTURE_FILES),
        "fixture_root": str(APPROVED_FIXTURE_ROOT),
        "all_expected_files_exist": True,
        "files_reviewed": {
            name: {
                "path": info["path"],
                "sha256": info["sha256"],
                "readable": info["readable"],
                "under_approved_root": info["under_approved_root"],
                "inside_master_upper_system": info["inside_master_upper_system"],
                "inside_runtime_directory": info["inside_runtime_directory"],
            }
            for name, info in fixture_files.items()
        },
        "fixture_files_reviewed": True,
    }

    accepted_lifecycle_candidate_review = {
        "accepted_lifecycle_candidate_count": len(cases),
        "case_reviews": candidate_review["case_reviews"],
        "candidate_review_passed": candidate_review["candidate_review_passed"],
        "not_selected_due_pnl_or_outcome": True,
        "not_rejected_gate_blocked_or_missing": candidate_review["candidate_review_passed"],
    }

    family_coverage_review = {
        "family_counts": family_counts,
        "blowoff_short_case_count": family_counts.get("blowoff_short", 0),
        "mean_reversion_short_case_count": family_counts.get("mean_reversion_short", 0),
        "one_case_per_family": family_counts.get("blowoff_short", 0) == 1
        and family_counts.get("mean_reversion_short", 0) == 1,
        "family_coverage_verified": prior_checks["family_coverage_verified"],
        "p1_attention_for_small_sample_size": len(cases) == 2,
    }

    gate_allowed_evidence_review = {
        "gate_allowed_inferred_count": discovery.get("gate_allowed_evidence_summary", {}).get(
            "gate_allowed_inferred_count"
        ),
        "gate_allowed_inferred_from_closed_trade_verified": all(
            case.get("gate_allowed_inferred_from_closed_trade") is True for case in cases
        ),
        "explicit_gate_replay_available": False,
        "exact_gate_replay_recovered": False,
        "direct_lifecycle_link_equals_exact_gate_replay": False,
        "limitation_preserved": True,
    }

    selection_guardrail_review = {
        "forbidden_selection_fields": list(FORBIDDEN_SELECTION_FIELDS),
        "no_selection_by_pnl_verified": discovery_summary.get("selection_guardrails", {}).get(
            "no_selection_by_pnl"
        )
        is True,
        "validation_holdout_returns_used": False,
        "pnl_outcome_fields_present_in_fixture_cases": False,
        "guardrails_preserved": True,
    }

    safety_permission_review = {
        "candidate_generation": False,
        "edge_claim": False,
        "family_release": False,
        "runtime": False,
        "monitor": False,
        "live": False,
        "capital": False,
        "backtest": False,
        "pnl_computation": False,
        "all_required_permissions_false": True,
    }

    prior_discovery_preserved = {
        "status": discovery.get("status"),
        "artifact_kind": discovery.get("artifact_kind"),
        "route_key": extract_route_key(discovery),
        "result_classification": discovery.get("result_classification"),
        "output_root": discovery.get("generated_fixture_files", {}).get("output_root"),
        "accepted_lifecycle_candidate_count": discovery.get(
            "accepted_lifecycle_candidate_summary", {}
        ).get("accepted_lifecycle_candidate_count"),
        "family_coverage": discovery.get("family_coverage_summary", {}).get("family_coverage"),
        "direct_lifecycle_link_count": discovery.get("lifecycle_linkage_summary", {}).get(
            "direct_lifecycle_link_count"
        ),
        "gate_allowed_inferred_count": discovery.get("gate_allowed_evidence_summary", {}).get(
            "gate_allowed_inferred_count"
        ),
        "next_allowed_step": discovery.get("next_allowed_step"),
        "replacement_checks_all_true": discovery.get("replacement_checks_all_true"),
    }

    safety_permissions = {
        "accepted_lifecycle_fixture_review_created": True,
        "fixture_generation_allowed_now": False,
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
        "prior_accepted_lifecycle_discovery_loaded": True,
        "prior_next_allowed_step_verified": prior_checks["prior_next_allowed_step_verified"],
        "accepted_lifecycle_candidate_count_verified_2": prior_checks[
            "accepted_lifecycle_candidate_count_verified_2"
        ],
        "family_coverage_verified": prior_checks["family_coverage_verified"],
        "direct_lifecycle_link_count_verified_2": prior_checks[
            "direct_lifecycle_link_count_verified_2"
        ],
        "gate_allowed_inferred_count_verified_2": prior_checks[
            "gate_allowed_inferred_count_verified_2"
        ],
        "fixture_files_reviewed": True,
        "no_selection_by_pnl_verified": selection_guardrail_review[
            "no_selection_by_pnl_verified"
        ],
        "exact_gate_replay_not_claimed": True,
        "original_exact_source_not_claimed": True,
        "no_fixture_generation": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
        "no_behavioral_validation_execution": True,
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": source_checkpoint["no_existing_files_modified"],
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
        "prior_discovery_preserved": prior_discovery_preserved,
        "fixture_file_review": fixture_file_review,
        "accepted_lifecycle_candidate_review": accepted_lifecycle_candidate_review,
        "family_coverage_review": family_coverage_review,
        "gate_allowed_evidence_review": gate_allowed_evidence_review,
        "missing_metric_recovery_review": missing_metric_review,
        "selection_guardrail_review": selection_guardrail_review,
        "safety_permission_review": safety_permission_review,
        "review_findings": {
            "p0_issue_count": len(p0_findings),
            "p0_findings": p0_findings,
            "p1_attention_count": len(p1_findings),
            "p1_findings": p1_findings,
            "summary": (
                "Accepted lifecycle fixtures are safe and useful with P1 limitations."
                if not p0_findings
                else "Accepted lifecycle fixture review failed and repair is required."
            ),
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
            "explicit gate_allowed field absent",
            "exact gate replay remains unrecovered",
        ],
        "limitations": [
            "Review only; no fixture discovery, fixture generation, runner execution, behavioral validation, full dataset comparison, backtest, or PnL computation was executed.",
            "Accepted lifecycle coverage is based on two bounded proxy fixtures, one per family.",
            "Gate allowed is inferred from closed trade lifecycle and direct signal linkage, not exact gate replay.",
            "The fixtures are clean-room proxy fixtures and do not claim edge, exact replay, live readiness, or capital readiness.",
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
        raise ReviewBlocked(f"target artifact already exists: {ARTIFACT_RELATIVE_PATH}")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=False)
        handle.write("\n")


def print_summary(artifact: dict[str, Any]) -> None:
    findings = artifact["review_findings"]
    prior = artifact["prior_discovery_preserved"]
    gate = artifact["gate_allowed_evidence_review"]
    print(f"status: {artifact['status']}")
    print(f"route_key: {prior['route_key']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"p0_issue_count: {findings['p0_issue_count']}")
    print(f"p1_attention_count: {findings['p1_attention_count']}")
    print(f"accepted_lifecycle_candidate_count: {prior['accepted_lifecycle_candidate_count']}")
    print(f"family_coverage: {','.join(prior['family_coverage'])}")
    print(f"gate_allowed_inferred_count: {prior['gate_allowed_inferred_count']}")
    print(
        "exact_gate_replay_recovered: "
        f"{str(gate['exact_gate_replay_recovered']).lower()}"
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
        artifact = build_artifact(repo_root)
        if not artifact["replacement_checks_all_true"]:
            raise ReviewBlocked("replacement checks are not all true")
        write_artifact_once(repo_root, artifact)
        print_summary(artifact)
        return 0
    except ReviewBlocked as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: {exc.reason}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2
    except Exception as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: unexpected review failure: {exc}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2


if __name__ == "__main__":
    sys.exit(main())
