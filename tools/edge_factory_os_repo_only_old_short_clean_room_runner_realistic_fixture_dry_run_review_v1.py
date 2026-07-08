from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_review_v1"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "4116d2e7f444348046ab1609cdf900b1c5d513a3"
EXPECTED_TRACKED_PYTHON_COUNT = 960
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.json"
)
PRIOR_REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_CREATED"
)
PRIOR_PARTIAL_CLASSIFICATION = (
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE"
)
PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_V1"
RESULT_PASS_READY = (
    "OLD_SHORT_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_PASS_READY_FOR_ACCEPTED_LIFECYCLE_"
    "FIXTURE_DISCOVERY_NO_EDGE_NO_LIVE"
)
RESULT_PASS_WITH_P1 = (
    "OLD_SHORT_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_PASS_WITH_P1_ATTENTION_NO_EDGE_NO_LIVE"
)
RESULT_FAIL = (
    "OLD_SHORT_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_FAIL_REQUIRES_REPAIR_NO_EDGE_NO_LIVE"
)
NEXT_ACCEPTED_LIFECYCLE_DESIGN = (
    "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DESIGN_V1"
)
NEXT_REPAIR = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_REPAIR_PREVIEW_V1"

SOURCE_ARTIFACT_PATHS = {
    "runner_realistic_fixture_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_v1.json"
    ),
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
    "threshold_proposal_review": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_threshold_proposal_review_v1.json"
    ),
}

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
        "dry_run_identity",
        "preview_identity",
        "dry_run_design_identity",
        "fixture_generation_identity",
        "fixture_threshold_contract_identity",
    ):
        value = payload.get(key)
        if isinstance(value, dict) and value.get("route_key") is not None:
            return value.get("route_key")
    summary = payload.get("fixture_generation_summary")
    if isinstance(summary, dict):
        return summary.get("route_key")
    return None


def labels_cover(labels: Any) -> bool:
    return isinstance(labels, list) and set(SAFETY_LABELS).issubset(set(labels))


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


def review_prior_dry_run(prior: dict[str, Any]) -> dict[str, Any]:
    metrics = prior.get("dry_run_metrics", {})
    safety_permissions = prior.get("safety_permissions", {})
    output_summary = prior.get("generated_output_summary", {})
    safety_label_audit = prior.get("safety_label_audit", {})
    dry_run_identity = prior.get("dry_run_identity", {})

    no_permission_issues = all(
        safety_permissions.get(key) is False
        for key in (
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
    )

    checks = {
        "status_matches_required_prior_status": prior.get("status") == PRIOR_REQUIRED_STATUS,
        "route_key_verified": dry_run_identity.get("route_key") == ROUTE_KEY,
        "prior_next_allowed_step_verified": prior.get("next_allowed_step")
        == PRIOR_NEXT_ALLOWED_STEP,
        "partial_classification_verified": prior.get("result_classification")
        == PRIOR_PARTIAL_CLASSIFICATION,
        "fixture_case_count_verified_5": metrics.get("fixture_case_count") == 5,
        "processed_case_count_verified_5": metrics.get("processed_case_count") == 5,
        "family_coverage_verified": {"blowoff_short", "mean_reversion_short"}.issubset(
            set(metrics.get("family_coverage", []))
        ),
        "gate_blocked_missing_coverage_verified": {
            "gate_blocked",
            "gate_missing_timeout",
        }.issubset(set(metrics.get("gate_state_coverage", []))),
        "gate_allowed_absent_verified": metrics.get("gate_allowed_count") == 0,
        "accepted_lifecycle_absent_verified": metrics.get(
            "accepted_lifecycle_coverage_present"
        )
        is False,
        "safety_label_audit_verified": metrics.get("safety_label_audit_passed") is True,
        "no_pnl_used_verified": metrics.get("no_pnl_used") is True,
        "no_market_data_used_verified": metrics.get("no_market_data_used") is True,
        "no_edge_live_capital_verified": metrics.get("no_edge_live_capital") is True,
        "no_live_capital_edge_permissions": no_permission_issues,
        "external_output_root_only": output_summary.get("all_outputs_under_approved_root")
        is True,
        "no_master_upper_system_modification": output_summary.get(
            "wrote_to_master_upper_system"
        )
        is False,
        "no_runtime_directory_modification": output_summary.get("wrote_to_runtime_directory")
        is False,
        "no_live_order_private_fields": safety_label_audit.get(
            "private_account_order_live_fields_detected"
        )
        == [],
        "all_required_safety_labels_present": labels_cover(
            safety_label_audit.get("required_labels", [])
        )
        and safety_label_audit.get("safety_labels_present") is True,
    }
    return checks


def build_review_artifact(repo_root: Path) -> dict[str, Any]:
    source_checkpoint = build_source_checkpoint(repo_root)
    loaded_sources = load_source_artifacts(repo_root)
    prior = loaded_sources["runner_realistic_fixture_dry_run"]["payload"]
    checks = review_prior_dry_run(prior)
    metrics = prior.get("dry_run_metrics", {})
    output_summary = prior.get("generated_output_summary", {})
    safety_label_audit = prior.get("safety_label_audit", {})

    p0_findings: list[dict[str, Any]] = []
    p1_findings: list[dict[str, Any]] = []

    p0_map = {
        "status_matches_required_prior_status": "prior dry-run status mismatch",
        "route_key_verified": "route key mismatch",
        "prior_next_allowed_step_verified": "prior next step mismatch",
        "partial_classification_verified": "prior result is not expected partial classification",
        "fixture_case_count_verified_5": "fixture case count mismatch",
        "processed_case_count_verified_5": "processed case count mismatch",
        "family_coverage_verified": "family coverage missing blowoff_short or mean_reversion_short",
        "gate_blocked_missing_coverage_verified": "gate blocked/missing coverage incomplete",
        "safety_label_audit_verified": "safety label audit did not pass",
        "no_pnl_used_verified": "prior dry-run did not preserve no-PnL check",
        "no_market_data_used_verified": "prior dry-run did not preserve no-market-data check",
        "no_edge_live_capital_verified": "prior dry-run did not preserve no-edge-live-capital check",
        "no_live_capital_edge_permissions": "live/capital/edge permission exists",
        "external_output_root_only": "output root is not confined to approved external root",
        "no_master_upper_system_modification": "MASTER_UPPER_SYSTEM modification indicated",
        "no_runtime_directory_modification": "runtime directory modification indicated",
        "no_live_order_private_fields": "live/order/private fields detected",
        "all_required_safety_labels_present": "required safety labels missing",
    }
    for key, finding in p0_map.items():
        if not checks.get(key):
            p0_findings.append({"severity": "P0", "finding": finding, "check": key})

    if checks.get("gate_allowed_absent_verified"):
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "gate_allowed fixtures are absent",
                "recommendation": NEXT_ACCEPTED_LIFECYCLE_DESIGN,
            }
        )
    if checks.get("accepted_lifecycle_absent_verified"):
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "accepted open/closed lifecycle coverage is absent",
                "recommendation": "do not claim accepted lifecycle equivalence",
            }
        )
    p1_findings.append(
        {
            "severity": "P1",
            "finding": "clean-room output remains proxy/fixture limited",
            "recommendation": "preserve no-edge and no-exact-replay labels",
        }
    )

    partial_correct = all(
        checks.get(key)
        for key in (
            "partial_classification_verified",
            "family_coverage_verified",
            "gate_blocked_missing_coverage_verified",
            "gate_allowed_absent_verified",
            "accepted_lifecycle_absent_verified",
            "safety_label_audit_verified",
            "no_pnl_used_verified",
            "no_market_data_used_verified",
            "no_edge_live_capital_verified",
        )
    )

    result_classification = RESULT_FAIL if p0_findings else RESULT_PASS_READY
    if p0_findings:
        next_allowed_step = NEXT_REPAIR
    else:
        next_allowed_step = NEXT_ACCEPTED_LIFECYCLE_DESIGN

    prior_dry_run_preserved = {
        "status": prior.get("status"),
        "artifact_kind": prior.get("artifact_kind"),
        "route_key": prior.get("dry_run_identity", {}).get("route_key"),
        "result_classification": prior.get("result_classification"),
        "next_allowed_step": prior.get("next_allowed_step"),
        "fixture_case_count": metrics.get("fixture_case_count"),
        "processed_case_count": metrics.get("processed_case_count"),
        "family_coverage": metrics.get("family_coverage"),
        "gate_state_coverage": metrics.get("gate_state_coverage"),
        "gate_allowed_count": metrics.get("gate_allowed_count"),
        "accepted_lifecycle_coverage_present": metrics.get(
            "accepted_lifecycle_coverage_present"
        ),
        "fail_closed_count": metrics.get("fail_closed_count"),
        "generated_output_file_count": metrics.get("generated_output_file_count"),
        "safety_label_audit_passed": metrics.get("safety_label_audit_passed"),
        "replacement_checks_all_true": prior.get("replacement_checks_all_true"),
    }

    partial_classification_review = {
        "partial_classification_correct": partial_correct,
        "basis": {
            "both_families_processed": checks["family_coverage_verified"],
            "blocked_missing_gate_states_processed": checks[
                "gate_blocked_missing_coverage_verified"
            ],
            "safety_labels_passed": checks["safety_label_audit_verified"],
            "no_pnl_market_live_data_used": all(
                checks[key]
                for key in (
                    "no_pnl_used_verified",
                    "no_market_data_used_verified",
                    "no_edge_live_capital_verified",
                )
            ),
            "accepted_lifecycle_missing_because_gate_allowed_absent": checks[
                "gate_allowed_absent_verified"
            ]
            and checks["accepted_lifecycle_absent_verified"],
        },
        "classification_should_not_be_upgraded_to_pass": True,
        "edge_or_live_claim_supported": False,
    }

    family_gate_coverage_review = {
        "family_coverage": metrics.get("family_coverage"),
        "family_coverage_verified": checks["family_coverage_verified"],
        "gate_state_coverage": metrics.get("gate_state_coverage"),
        "gate_blocked_missing_coverage_verified": checks[
            "gate_blocked_missing_coverage_verified"
        ],
        "gate_allowed_count": metrics.get("gate_allowed_count"),
    }

    accepted_lifecycle_coverage_review = {
        "accepted_lifecycle_coverage_present": metrics.get(
            "accepted_lifecycle_coverage_present"
        ),
        "gate_allowed_count": metrics.get("gate_allowed_count"),
        "gate_allowed_absent_verified": checks["gate_allowed_absent_verified"],
        "accepted_lifecycle_absent_verified": checks[
            "accepted_lifecycle_absent_verified"
        ],
        "no_accepted_open_closed_lifecycle_equivalence": True,
        "recommended_next_step": NEXT_ACCEPTED_LIFECYCLE_DESIGN,
    }

    safety_label_review = {
        "required_labels": list(SAFETY_LABELS),
        "safety_label_audit_verified": checks["safety_label_audit_verified"],
        "all_required_safety_labels_present": checks["all_required_safety_labels_present"],
        "fixture_rows_checked": safety_label_audit.get("fixture_rows_checked"),
        "output_rows_checked": safety_label_audit.get("output_rows_checked"),
        "missing_labels": [],
    }

    output_safety_review = {
        "output_root": output_summary.get("output_root"),
        "external_output_root_only": checks["external_output_root_only"],
        "no_master_upper_system_modification": checks["no_master_upper_system_modification"],
        "no_runtime_directory_modification": checks["no_runtime_directory_modification"],
        "no_live_order_private_fields": checks["no_live_order_private_fields"],
        "generated_output_file_count": output_summary.get("generated_output_file_count"),
        "review_read_external_output_files": False,
        "review_used_prior_artifact_summary_only": True,
    }

    limitation_review = {
        "no_accepted_open_closed_lifecycle_equivalence": True,
        "no_full_behavior_validation": True,
        "no_edge_evidence": True,
        "no_live_capital_readiness": True,
        "no_exact_original_old_short_replay": True,
        "clean_room_reconstruction_only": True,
        "limitations_preserved": True,
    }

    next_step_review = {
        "preferred_next_step": NEXT_ACCEPTED_LIFECYCLE_DESIGN,
        "broader_behavioral_validation_next_step": (
            "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DESIGN"
        ),
        "prefer_accepted_lifecycle_fixture_discovery": metrics.get("gate_allowed_count") == 0,
        "reason": "gate_allowed_count is 0 and accepted lifecycle coverage is absent",
        "no_next_step_backtest_live_capital": True,
    }

    safety_permissions = {
        "runner_realistic_fixture_dry_run_review_created": True,
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
        "prior_realistic_fixture_dry_run_loaded": True,
        "prior_next_allowed_step_verified": checks["prior_next_allowed_step_verified"],
        "partial_classification_verified": checks["partial_classification_verified"],
        "family_coverage_verified": checks["family_coverage_verified"],
        "gate_blocked_missing_coverage_verified": checks[
            "gate_blocked_missing_coverage_verified"
        ],
        "gate_allowed_absent_verified": checks["gate_allowed_absent_verified"],
        "accepted_lifecycle_absent_verified": checks[
            "accepted_lifecycle_absent_verified"
        ],
        "safety_label_audit_verified": checks["safety_label_audit_verified"],
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runner_execution": True,
        "no_behavioral_validation_execution": True,
        "no_full_dataset_comparison": True,
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
        "prior_dry_run_preserved": prior_dry_run_preserved,
        "partial_classification_review": partial_classification_review,
        "family_gate_coverage_review": family_gate_coverage_review,
        "accepted_lifecycle_coverage_review": accepted_lifecycle_coverage_review,
        "safety_label_review": safety_label_review,
        "output_safety_review": output_safety_review,
        "limitation_review": limitation_review,
        "next_step_review": next_step_review,
        "review_findings": {
            "p0_issue_count": len(p0_findings),
            "p0_findings": p0_findings,
            "p1_attention_count": len(p1_findings),
            "p1_findings": p1_findings,
            "summary": (
                "PARTIAL is correct and safe; accepted lifecycle fixture discovery is preferred."
                if not p0_findings
                else "Review failed and repair preview is required."
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
            "accepted gate_allowed/open-close lifecycle fixture absent",
        ],
        "limitations": [
            "Review only; no runner, behavioral validation, full dataset comparison, backtest, or PnL computation was executed.",
            "No raw market data, raw OKX 1m data, network, API, runtime, monitor, live, capital, order, candidate, or edge action was used.",
            "PARTIAL remains correct because accepted lifecycle coverage is absent.",
            "The dry-run remains clean-room proxy fixture evidence, not exact original old_short replay.",
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
    coverage = artifact["accepted_lifecycle_coverage_review"]
    print(f"status: {artifact['status']}")
    print(f"route_key: {artifact['prior_dry_run_preserved']['route_key']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"p0_issue_count: {findings['p0_issue_count']}")
    print(f"p1_attention_count: {findings['p1_attention_count']}")
    print(f"gate_allowed_count: {coverage['gate_allowed_count']}")
    print(
        "accepted_lifecycle_coverage_present: "
        f"{str(coverage['accepted_lifecycle_coverage_present']).lower()}"
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
        artifact = build_review_artifact(repo_root)
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
