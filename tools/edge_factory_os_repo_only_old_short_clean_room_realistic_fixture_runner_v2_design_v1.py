from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_REALISTIC_FIXTURE_RUNNER_V2_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_REALISTIC_FIXTURE_RUNNER_V2_DESIGN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_realistic_fixture_runner_v2_design_v1"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "22161dd3729081cafbc72635beb9ecd8b83bce21"
EXPECTED_TRACKED_PYTHON_COUNT = 964
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_realistic_fixture_runner_v2_design_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/old_short_clean_room_realistic_fixture_runner_v2_design_v1.json"
)
PRIOR_REVIEW_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_REVIEW_CREATED"
PRIOR_REVIEW_NEXT_STEP = "OLD_SHORT_CLEAN_ROOM_REALISTIC_FIXTURE_RUNNER_V2_DESIGN_V1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_PREVIEW_V1"

APPROVED_FIXTURE_ROOT = (
    "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\"
    "edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
)
REALISTIC_FIXTURE_ROOT = (
    APPROVED_FIXTURE_ROOT + "\\realistic_bounded_fixture_generation_dry_run_v1"
)
ACCEPTED_LIFECYCLE_FIXTURE_ROOT = (
    APPROVED_FIXTURE_ROOT + "\\accepted_lifecycle_fixture_discovery_v1"
)
FUTURE_V2_OUTPUT_ROOT = (
    "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\"
    "edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1\\"
    "realistic_fixture_runner_v2_dry_run_v1"
)

SOURCE_ARTIFACT_PATHS = {
    "accepted_lifecycle_fixture_review": (
        "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json"
    ),
    "accepted_lifecycle_fixture_discovery_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.json"
    ),
    "runner_realistic_fixture_dry_run_review": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.json"
    ),
    "runner_realistic_fixture_dry_run": (
        "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_dry_run_v1.json"
    ),
    "realistic_bounded_fixture_generation_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.json"
    ),
    "runner_fixture_threshold_contract": (
        "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json"
    ),
    "threshold_proposal_review": (
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json"
    ),
    "old_short_clean_room_contract": (
        "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
    ),
}

EXTERNAL_METADATA_PATHS = {
    "realistic_fixture_index": REALISTIC_FIXTURE_ROOT + "\\fixture_index.json",
    "realistic_fixture_generation_summary": REALISTIC_FIXTURE_ROOT
    + "\\fixture_generation_summary.json",
    "accepted_lifecycle_fixture_index": ACCEPTED_LIFECYCLE_FIXTURE_ROOT
    + "\\accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_discovery_summary": ACCEPTED_LIFECYCLE_FIXTURE_ROOT
    + "\\accepted_lifecycle_discovery_summary.json",
}

REALISTIC_FIXTURE_FILES = [
    "fixture_index.json",
    "master_proxy_cases.jsonl",
    "clean_room_replay_fixture_inputs.jsonl",
    "validation_pair_fixtures.jsonl",
    "fixture_generation_summary.json",
]

ACCEPTED_LIFECYCLE_FIXTURE_FILES = [
    "accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_master_cases.jsonl",
    "accepted_lifecycle_pairing_plan.json",
    "accepted_lifecycle_discovery_summary.json",
]

SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "PROXY_BEHAVIOR_FIXTURE",
    "ACCEPTED_LIFECYCLE_FIXTURE if applicable",
    "NOT_ORIGINAL_OLD_SHORT",
    "NOT_EXACT_REPLAY",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]

FAIL_CLOSED_CONDITIONS = [
    "either fixture package missing",
    "threshold contract missing",
    "route_key mismatch",
    "family_key mismatch",
    "side not short",
    "required feature missing",
    "safety labels missing",
    "fixture uses PnL/outcome selection",
    "raw market data path supplied",
    "runtime path supplied",
    "live/order/private fields detected",
    "output root overlaps MASTER/runtime",
    "no-live guard false",
]

V2_METRICS = [
    "blocked_missing_fixture_case_count",
    "accepted_lifecycle_case_count",
    "processed_case_count",
    "family_coverage",
    "gate_state_coverage",
    "gate_allowed_inferred_count",
    "accepted_lifecycle_coverage_present",
    "entry_delay_computable_count",
    "hold_duration_computable_count",
    "notional_computable_count",
    "rejected_case_count",
    "accepted_case_count",
    "fail_closed_count",
    "generated_output_file_count",
    "safety_label_audit_passed",
    "no_pnl_used",
    "no_market_data_used",
    "no_edge_live_capital",
]

RESULT_CLASSES = [
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]


class DesignBlocked(RuntimeError):
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    clone = copy.deepcopy(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clone, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def extract_route_key(payload: dict[str, Any]) -> Any:
    direct = payload.get("route_key")
    if direct is not None:
        return direct
    for key in (
        "v2_design_identity",
        "prior_discovery_preserved",
        "discovery_identity",
        "dry_run_identity",
        "fixture_generation_identity",
        "fixture_threshold_contract_identity",
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
        raise DesignBlocked(f"HEAD mismatch: expected {EXPECTED_HEAD}, got {actual_head}")
    if tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise DesignBlocked(
            "tracked Python count mismatch: "
            f"expected {EXPECTED_TRACKED_PYTHON_COUNT}, got {tracked_python_count}"
        )
    if dirty_tracked:
        raise DesignBlocked(f"tracked repo files modified before run: {dirty_tracked}")
    if unexpected_untracked:
        raise DesignBlocked(f"unexpected untracked repo files before run: {unexpected_untracked}")
    return {
        "repo_root": str(repo_root),
        "expected_head": EXPECTED_HEAD,
        "actual_head": actual_head,
        "head_verified": True,
        "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
        "actual_tracked_python_count": tracked_python_count,
        "tracked_python_count_verified": True,
        "repo_clean_before_run": True,
        "git_status_at_design_start": status_lines,
        "allowed_pending_at_design_start": sorted(allowed_untracked),
        "dirty_tracked_at_design_start": dirty_tracked,
        "unexpected_untracked_at_design_start": unexpected_untracked,
        "no_existing_files_modified": True,
    }


def load_source_artifacts(repo_root: Path) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, relative_path in SOURCE_ARTIFACT_PATHS.items():
        path = repo_root / relative_path
        if not path.exists():
            raise DesignBlocked(f"required source artifact missing: {relative_path}")
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


def load_external_metadata() -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for name, raw_path in EXTERNAL_METADATA_PATHS.items():
        path = Path(raw_path)
        if not path.exists():
            raise DesignBlocked(f"required external fixture metadata missing: {raw_path}")
        payload = load_json(path)
        metadata[name] = {
            "path": raw_path,
            "exists": True,
            "loaded": True,
            "route_key": extract_route_key(payload),
            "sha256": sha256_file(path),
            "summary": {
                key: payload.get(key)
                for key in (
                    "status",
                    "fixture_package_kind",
                    "fixture_case_count",
                    "family_coverage",
                    "gate_state_coverage",
                    "accepted_lifecycle_candidate_count",
                    "gate_allowed_inferred_count",
                )
                if key in payload
            },
        }
    return metadata


def summarize_sources(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        name: {key: value for key, value in source.items() if key != "payload"}
        for name, source in loaded.items()
    }


def verify_prior_review(review: dict[str, Any]) -> dict[str, bool]:
    prior = review.get("prior_discovery_preserved", {})
    gate_review = review.get("gate_allowed_evidence_review", {})
    findings = review.get("review_findings", {})
    return {
        "status_verified": review.get("status") == PRIOR_REVIEW_STATUS,
        "route_key_verified": prior.get("route_key") == ROUTE_KEY,
        "prior_next_allowed_step_verified": review.get("next_allowed_step")
        == PRIOR_REVIEW_NEXT_STEP,
        "accepted_lifecycle_candidate_count_verified_2": prior.get(
            "accepted_lifecycle_candidate_count"
        )
        == 2,
        "gate_allowed_inferred_count_verified_2": prior.get("gate_allowed_inferred_count")
        == 2,
        "exact_gate_replay_not_claimed": gate_review.get("exact_gate_replay_recovered")
        is False,
        "p0_zero_verified": findings.get("p0_issue_count") == 0,
        "replacement_checks_all_true_verified": review.get("replacement_checks_all_true") is True,
    }


def build_artifact(repo_root: Path) -> dict[str, Any]:
    source_checkpoint = build_source_checkpoint(repo_root)
    loaded_sources = load_source_artifacts(repo_root)
    external_metadata = load_external_metadata()
    review = loaded_sources["accepted_lifecycle_fixture_review"]["payload"]
    discovery = loaded_sources["accepted_lifecycle_fixture_discovery_dry_run"]["payload"]
    realistic_runner_v1 = loaded_sources["runner_realistic_fixture_dry_run"]["payload"]
    realistic_generation = loaded_sources["realistic_bounded_fixture_generation_dry_run"]["payload"]
    threshold = loaded_sources["runner_fixture_threshold_contract"]["payload"]
    prior_checks = verify_prior_review(review)
    if not all(prior_checks.values()):
        failed = [key for key, value in prior_checks.items() if not value]
        raise DesignBlocked(f"prior accepted lifecycle review checks failed: {failed}")

    accepted_candidate_count = review["prior_discovery_preserved"]["accepted_lifecycle_candidate_count"]
    gate_allowed_inferred_count = review["prior_discovery_preserved"]["gate_allowed_inferred_count"]
    accepted_family_coverage = review["prior_discovery_preserved"]["family_coverage"]
    v1_gate_coverage = realistic_runner_v1.get("dry_run_metrics", {}).get("gate_state_coverage", [])

    v2_design_identity = {
        "route_key": ROUTE_KEY,
        "design_only": True,
        "v2_realistic_fixture_runner_allowed_now": False,
        "original_exact_source_recovered": False,
        "exact_gate_replay_recovered": False,
        "accepted_lifecycle_gate_allow_inferred": True,
        "clean_room_behavioral_reconstruction": True,
        "no_edge_claim": True,
        "no_live_capital": True,
    }

    input_fixture_policy_v2 = {
        "approved_external_fixture_root": APPROVED_FIXTURE_ROOT,
        "future_may_read": {
            "realistic_bounded_fixture_package": {
                "root": REALISTIC_FIXTURE_ROOT,
                "files": list(REALISTIC_FIXTURE_FILES),
                "metadata_from_current_package": external_metadata[
                    "realistic_fixture_generation_summary"
                ]["summary"],
            },
            "accepted_lifecycle_fixture_package": {
                "root": ACCEPTED_LIFECYCLE_FIXTURE_ROOT,
                "files": list(ACCEPTED_LIFECYCLE_FIXTURE_FILES),
                "metadata_from_current_package": external_metadata[
                    "accepted_lifecycle_discovery_summary"
                ]["summary"],
            },
        },
        "must_not_read": [
            "raw market data",
            "raw OKX 1m data",
            "full MASTER output",
            "runtime directories",
            "private/account data",
        ],
        "package_count": 2,
    }

    v2_case_types = [
        "blowoff_short blocked/missing gate fixture",
        "mean_reversion_short blocked/missing gate fixture",
        "blowoff_short accepted lifecycle fixture",
        "mean_reversion_short accepted lifecycle fixture",
        "heartbeat/state fixture",
    ]

    accepted_lifecycle_policy = {
        "gate_allowed_inferred_from_closed_trade_unless_explicit_gate_allow_field_exists": True,
        "do_not_claim_exact_gate_replay": True,
        "do_not_claim_original_source_recovery": True,
        "accepted_lifecycle_can_test": [
            "entry delay",
            "hold duration",
            "notional",
            "closed trade schema",
            "lifecycle linking",
        ],
        "accepted_lifecycle_cannot_prove": [
            "profitability",
            "edge",
            "live readiness",
            "exact gate decision replay",
        ],
        "accepted_lifecycle_candidate_count": accepted_candidate_count,
        "gate_allowed_inferred_count": gate_allowed_inferred_count,
        "exact_gate_replay_recovered": False,
    }

    runner_processing_plan_v2 = {
        "future_steps": [
            "load threshold contract",
            "load both fixture packages",
            "validate all safety labels",
            "process blocked/missing gate cases into rejected_entries",
            "process accepted lifecycle cases into paper-only accepted/open/closed lifecycle outputs",
            "preserve inferred gate allow limitation",
            "write paper-only output files",
            "build report",
            "fail closed on missing required features/labels/thresholds",
        ],
        "threshold_contract_complete_now": threshold.get("contract_completeness", {}).get(
            "contract_complete"
        )
        is True,
        "family_threshold_count_now": threshold.get("contract_completeness", {}).get(
            "family_threshold_count"
        ),
        "runner_execution_now": False,
    }

    output_policy_v2 = {
        "future_output_root": FUTURE_V2_OUTPUT_ROOT,
        "future_output_files": [
            "signals.csv",
            "pending_entries.csv",
            "open_positions.csv",
            "closed_trades.csv",
            "rejected_entries.csv",
            "heartbeat.csv",
            "state.json",
            "runner_realistic_fixture_v2_dry_run_report.json",
        ],
        "must_never_write_to": [
            "MASTER_UPPER_SYSTEM",
            "paper_run_gate_* runtime roots",
            "live runtime directories",
            "old original output directories",
            "repo tracked paths except summary JSON artifacts",
        ],
        "writes_now": False,
    }

    result_classes_v2 = {
        "classes": list(RESULT_CLASSES),
        "pass_if": [
            "both families processed",
            "blocked/missing gate cases processed",
            "accepted lifecycle cases processed",
            "accepted lifecycle coverage present",
            "safety labels pass",
            "no PnL/market/live data used",
        ],
        "partial_if": "accepted lifecycle exists but one family or one fixture type missing",
        "fail_closed_if": "safety/root/threshold/route checks fail",
        "inconclusive_if": "fixtures insufficient",
    }

    safety_permissions = {
        "realistic_fixture_runner_v2_design_created": True,
        "v2_runner_dry_run_allowed_now": False,
        "runner_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
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
        "accepted_lifecycle_fixture_review_loaded": True,
        "prior_next_allowed_step_verified": prior_checks["prior_next_allowed_step_verified"],
        "accepted_lifecycle_candidate_count_verified_2": prior_checks[
            "accepted_lifecycle_candidate_count_verified_2"
        ],
        "gate_allowed_inferred_count_verified_2": prior_checks[
            "gate_allowed_inferred_count_verified_2"
        ],
        "exact_gate_replay_not_claimed": prior_checks["exact_gate_replay_not_claimed"],
        "original_exact_source_not_claimed": True,
        "clean_room_reconstruction_preserved": True,
        "no_v2_runner_execution": True,
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
        "input_fixture_policy_defined": True,
        "accepted_lifecycle_policy_defined": True,
        "fail_closed_conditions_defined": len(FAIL_CLOSED_CONDITIONS) == 13,
        "result_classes_defined": len(RESULT_CLASSES) == 4,
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
        "source_artifacts": {
            **summarize_sources(loaded_sources),
            "external_fixture_metadata": external_metadata,
        },
        "v2_design_identity": v2_design_identity,
        "input_fixture_policy_v2": input_fixture_policy_v2,
        "v2_case_types": v2_case_types,
        "accepted_lifecycle_policy": accepted_lifecycle_policy,
        "runner_processing_plan_v2": runner_processing_plan_v2,
        "output_policy_v2": output_policy_v2,
        "safety_labels": list(SAFETY_LABELS),
        "fail_closed_conditions_v2": {
            "condition_count": len(FAIL_CLOSED_CONDITIONS),
            "conditions": list(FAIL_CLOSED_CONDITIONS),
        },
        "v2_metrics": {
            "metric_count": len(V2_METRICS),
            "required_report_metrics": list(V2_METRICS),
            "current_fixture_context": {
                "blocked_missing_fixture_case_count": realistic_generation.get(
                    "fixture_generation_summary", {}
                ).get("fixture_case_count"),
                "accepted_lifecycle_case_count": accepted_candidate_count,
                "family_coverage": sorted(set(accepted_family_coverage)),
                "gate_state_coverage": v1_gate_coverage,
                "gate_allowed_inferred_count": gate_allowed_inferred_count,
                "accepted_lifecycle_coverage_present": accepted_candidate_count > 0,
            },
        },
        "result_classes_v2": result_classes_v2,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "unresolved_fields_preserved": [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
            "explicit gate_allowed field absent in accepted lifecycle fixtures",
            "exact gate decision replay remains unrecovered",
        ],
        "limitations": [
            "Design only; no V2 runner dry-run was executed.",
            "Accepted lifecycle gate allowance is inferred from closed trade lifecycle and direct linkage, not exact gate replay.",
            "Original old_short source and exact replay remain unrecovered.",
            "No runner execution, signal generation, behavioral validation, full dataset comparison, backtest, PnL, runtime, live, capital, candidate generation, or edge claim was performed.",
            "Future V2 dry-run must keep outputs paper-only and fail closed on unsafe roots, missing labels, or PnL/outcome selection.",
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
        raise DesignBlocked(f"target artifact already exists: {ARTIFACT_RELATIVE_PATH}")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=False)
        handle.write("\n")


def print_summary(artifact: dict[str, Any]) -> None:
    identity = artifact["v2_design_identity"]
    policy = artifact["accepted_lifecycle_policy"]
    print(f"status: {artifact['status']}")
    print(f"route_key: {identity['route_key']}")
    print(f"design_only: {str(identity['design_only']).lower()}")
    print(f"accepted_lifecycle_candidate_count: {policy['accepted_lifecycle_candidate_count']}")
    print(f"gate_allowed_inferred_count: {policy['gate_allowed_inferred_count']}")
    print(
        "exact_gate_replay_recovered: "
        f"{str(policy['exact_gate_replay_recovered']).lower()}"
    )
    print(f"result_class_count: {len(artifact['result_classes_v2']['classes'])}")
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
            raise DesignBlocked("replacement checks are not all true")
        write_artifact_once(repo_root, artifact)
        print_summary(artifact)
        return 0
    except DesignBlocked as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: {exc.reason}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2
    except Exception as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: unexpected design failure: {exc}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2


if __name__ == "__main__":
    sys.exit(main())
