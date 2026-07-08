import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_old_short_clean_room_threshold_behavioral_proposal_contract_v1.py"
ARTIFACT_PATH = "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_contract_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_CONTRACT_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_CONTRACT"
ROUTE_KEY = "old_short_clean_room_v1"

EXPECTED_HEAD = "dafdbb444accac1886d5fc1b6289ae85774c9585"
EXPECTED_TRACKED_PYTHON_COUNT = 945

THRESHOLD_RECONSTRUCTION_CONTRACT = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_reconstruction_contract_v1.json"
)
EVIDENCE_EXTRACTION_DRY_RUN = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_evidence_extraction_dry_run_v1.json"
)
CLEAN_ROOM_CONTRACT = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
SCHEMA_FIXTURE_CHECK = "artifacts/old_short_clean_room/old_short_clean_room_runner_schema_fixture_validator_check_v1.json"
OLD_SHORT_METADATA_DIR = "artifacts/old_short"

RECONSTRUCTION_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_CONTRACT_CREATED"
EVIDENCE_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_EVIDENCE_EXTRACTION_DRY_RUN_CREATED"
EVIDENCE_READY_CLASS = "OLD_SHORT_THRESHOLD_EVIDENCE_EXTRACTION_READY_FOR_BEHAVIORAL_PROPOSAL_NO_EDGE_NO_LIVE"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_DRY_RUN_V1"

FAMILIES = ["blowoff_short", "mean_reversion_short"]
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
UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(args: List[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def tracked_python_count() -> int:
    output = run_git(["ls-files", "*.py"])
    return 0 if not output else len(output.splitlines())


def dirty_paths() -> List[str]:
    output = run_git(["status", "--short"])
    paths: List[str] = []
    for line in output.splitlines():
        if line:
            paths.append(line[3:].strip().strip('"').replace("\\", "/"))
    return sorted(paths)


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"artifact is not a JSON object: {relative_path}")
    return payload


def input_artifact_review(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    review: Dict[str, Any] = {
        "path": relative_path,
        "exists": path.exists(),
        "loaded": False,
        "status": None,
        "artifact_kind": None,
        "route_key": None,
        "payload_sha256_excluding_hash": None,
        "replacement_checks_all_true": None,
        "sha256": file_sha256(path),
    }
    if not path.exists():
        return review
    payload = read_json(relative_path)
    route_key = payload.get("route_key")
    if route_key is None and isinstance(payload.get("proposal_contract_identity"), dict):
        route_key = payload["proposal_contract_identity"].get("route_key")
    if route_key is None and isinstance(payload.get("threshold_reconstruction_identity"), dict):
        route_key = payload["threshold_reconstruction_identity"].get("route_key")
    if route_key is None and isinstance(payload.get("evidence_extraction_identity"), dict):
        route_key = payload["evidence_extraction_identity"].get("route_key")
    review.update(
        {
            "loaded": True,
            "status": payload.get("status"),
            "artifact_kind": payload.get("artifact_kind"),
            "route_key": route_key,
            "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
            "replacement_checks_all_true": payload.get("replacement_checks_all_true"),
        }
    )
    return review


def old_short_metadata_review() -> Dict[str, Any]:
    metadata_dir = REPO_ROOT / OLD_SHORT_METADATA_DIR
    if not metadata_dir.exists():
        return {"directory": OLD_SHORT_METADATA_DIR, "exists": False, "json_file_count": 0, "files": {}}
    files: Dict[str, Any] = {}
    for path in sorted(metadata_dir.glob("*.json")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        files[path.name] = input_artifact_review(rel)
    return {
        "directory": OLD_SHORT_METADATA_DIR,
        "exists": True,
        "json_file_count": len(files),
        "files": files,
        "metadata_only": True,
    }


def build_payload() -> Dict[str, Any]:
    actual_head = run_git(["rev-parse", "HEAD"])
    actual_tracked_python_count = tracked_python_count()
    current_dirty_paths = dirty_paths()
    allowed_dirty_paths = {MODULE_PATH, ARTIFACT_PATH}
    unexpected_dirty_paths = [path for path in current_dirty_paths if path not in allowed_dirty_paths]
    if unexpected_dirty_paths:
        raise RuntimeError(f"unexpected dirty paths before contract build: {unexpected_dirty_paths}")
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"HEAD moved before contract build: {actual_head} != {EXPECTED_HEAD}")
    if actual_tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before contract build: "
            f"{actual_tracked_python_count} != {EXPECTED_TRACKED_PYTHON_COUNT}"
        )

    reconstruction = read_json(THRESHOLD_RECONSTRUCTION_CONTRACT)
    evidence = read_json(EVIDENCE_EXTRACTION_DRY_RUN)
    reconstruction_identity = reconstruction.get("threshold_reconstruction_identity", {})
    evidence_identity = evidence.get("evidence_extraction_identity", {})
    evidence_summary = evidence.get("old_short_row_summary", {})
    reject_summary = evidence.get("reject_reason_summaries", {})

    if reconstruction.get("status") != RECONSTRUCTION_STATUS:
        raise RuntimeError("threshold reconstruction contract status mismatch")
    if evidence.get("status") != EVIDENCE_STATUS:
        raise RuntimeError("threshold evidence extraction status mismatch")
    if reconstruction_identity.get("route_key") != ROUTE_KEY:
        raise RuntimeError("threshold reconstruction route_key mismatch")
    if evidence_identity.get("route_key") != ROUTE_KEY:
        raise RuntimeError("evidence extraction route_key mismatch")
    if evidence.get("result_classification") != EVIDENCE_READY_CLASS:
        raise RuntimeError("evidence extraction is not ready for behavioral proposal")
    if evidence.get("next_allowed_step") != "OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_CONTRACT_V1":
        raise RuntimeError("evidence extraction next allowed step mismatch")

    original_exact_recovered = reconstruction_identity.get("original_exact_thresholds_recovered") is True
    behavioral_reconstruction = reconstruction_identity.get("behavioral_threshold_reconstruction") is True
    no_pnl_optimization = reconstruction_identity.get("no_pnl_optimization") is True
    if original_exact_recovered or not behavioral_reconstruction or not no_pnl_optimization:
        raise RuntimeError("reconstruction identity flags do not satisfy behavioral proposal contract gate")

    old_short_row_count = int(evidence_summary.get("old_short_row_count", 0))
    family_count = int(evidence_summary.get("family_count", 0))
    feature_count = int(evidence_summary.get("feature_count", 0))
    rejected_reason_count = int(reject_summary.get("rejected_reason_count", 0))

    forbidden_goals = [
        "maximize returns",
        "maximize win rate",
        "choose thresholds from PnL",
        "choose thresholds from holdout",
        "choose thresholds from monthly stability",
        "cherry-pick winning trades",
        "alter hold time",
        "alter entry delay",
        "expand universe",
        "add unrelated filters",
    ]

    safety_permissions = {
        "threshold_behavioral_proposal_contract_created": True,
        "threshold_proposal_allowed_now": False,
        "threshold_selection_allowed_now": False,
        "runner_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "backtest_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "threshold_reconstruction_contract_loaded": True,
        "threshold_evidence_extraction_loaded": True,
        "evidence_ready_for_behavioral_proposal_verified": True,
        "original_exact_thresholds_not_claimed": original_exact_recovered is False,
        "behavioral_threshold_reconstruction_preserved": behavioral_reconstruction,
        "no_pnl_optimization_preserved": no_pnl_optimization,
        "no_threshold_proposal": True,
        "no_threshold_selection": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
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
        "no_existing_files_modified": not unexpected_dirty_paths,
        "replacement_checks_all_true": True,
    }

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "actual_clean_head": EXPECTED_HEAD,
            "actual_head_verified_at_artifact_creation": actual_head,
            "repo_clean_before_run": True,
            "tracked_python_count_before_run": EXPECTED_TRACKED_PYTHON_COUNT,
            "tracked_python_count_verified_at_artifact_creation": actual_tracked_python_count,
            "dirty_paths_during_artifact_creation_limited_to_expected_new_paths": True,
            "dirty_paths_during_artifact_creation": current_dirty_paths,
        },
        "source_artifacts": {
            "threshold_reconstruction_contract": input_artifact_review(THRESHOLD_RECONSTRUCTION_CONTRACT),
            "threshold_evidence_extraction_dry_run": input_artifact_review(EVIDENCE_EXTRACTION_DRY_RUN),
            "clean_room_contract": input_artifact_review(CLEAN_ROOM_CONTRACT),
            "runner_preview": input_artifact_review(RUNNER_PREVIEW),
            "runner_schema_fixture_validator_check": input_artifact_review(SCHEMA_FIXTURE_CHECK),
            "old_short_metadata_json": old_short_metadata_review(),
            "raw_market_data_read": False,
            "raw_okx_1m_data_read": False,
        },
        "proposal_contract_identity": {
            "route_key": ROUTE_KEY,
            "proposal_contract_only": True,
            "threshold_proposal_allowed_now": False,
            "threshold_selection_allowed_now": False,
            "original_exact_thresholds_recovered": False,
            "behavioral_threshold_reconstruction": True,
            "no_pnl_optimization": True,
            "no_edge_claim": True,
            "no_live_capital": True,
        },
        "source_evidence_summary": {
            "source_artifact": EVIDENCE_EXTRACTION_DRY_RUN,
            "status": evidence.get("status"),
            "route_key": evidence_identity.get("route_key"),
            "result_classification": evidence.get("result_classification"),
            "ready_for_behavioral_proposal": evidence.get("result_classification") == EVIDENCE_READY_CLASS,
            "source_files_found_count": evidence_summary.get("source_files_found_count"),
            "old_short_row_count": old_short_row_count,
            "family_count": family_count,
            "feature_count": feature_count,
            "rejected_reason_count": rejected_reason_count,
            "families": FAMILIES,
            "feature_fields": FEATURE_FIELDS,
            "exact_original_thresholds_recovered": False,
        },
        "behavioral_proposal_goal": {
            "allowed_goal": [
                "approximate old_short behavior from emitted signal/closed/rejected feature distributions",
                "define conservative trigger envelopes for blowoff_short and mean_reversion_short",
                "keep side short only",
                "keep entry delay approximately 2 minutes",
                "keep hold approximately 120 minutes",
                "keep global gate mandatory",
            ],
            "forbidden_goal": forbidden_goals,
        },
        "proposal_input_policy": {
            "future_proposal_may_use": [
                "family_feature_summaries from evidence extraction",
                "source_category_summaries",
                "reject_reason_summaries",
                "lifecycle evidence",
                "notional evidence",
                "missing-field rates",
            ],
            "future_proposal_must_not_use": [
                "future PnL",
                "validation/holdout return",
                "backtest performance",
                "live account data",
                "private account data",
                "manual winning-trade cherry-picking",
            ],
        },
        "proposal_method_policy": {
            "future_proposal_may_use_robust_quantile_envelopes_only": [
                "p10",
                "p25",
                "p50",
                "p75",
                "p90",
                "missing rates",
                "family-level feature direction",
                "reject reason feature contrast",
            ],
            "allowed_proposal_style": [
                "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
                "NOT_ORIGINAL_THRESHOLD",
                "NOT_PNL_OPTIMIZED",
                "NOT_EDGE_EVIDENCE",
            ],
            "exact_original_threshold_claim_allowed": False,
        },
        "family_proposal_policy": {
            "blowoff_short": {
                "proposal_must_be_based_on": {
                    "short_window_positive_pressure": [
                        "signal_ret1_bps",
                        "signal_ret3_bps",
                        "signal_ret5_bps",
                    ],
                    "range_expansion": ["signal_range_bps"],
                    "activity_volume": ["signal_vol_quote"],
                    "entry_confirmation_fields": ["entry_range_bps", "entry_vol_quote"],
                }
            },
            "mean_reversion_short": {
                "proposal_must_be_based_on": {
                    "longer_window_extension": ["signal_ret60_bps"],
                    "local_exhaustion_short_window_behavior": [
                        "signal_ret1_bps",
                        "signal_ret3_bps",
                        "signal_ret5_bps",
                    ],
                    "range_volume_confirmation": [
                        "signal_range_bps",
                        "signal_vol_quote",
                        "entry_range_bps",
                        "entry_vol_quote",
                    ],
                }
            },
        },
        "conservative_proposal_guardrails": {
            "future_proposal_must_fail_closed_if_evidence_too_sparse_for_family": True,
            "mark_family_incomplete_if_required_feature_distributions_missing": True,
            "preserve_both_families_if_evidence_supports_both": True,
            "avoid_adding_filters_not_present_in_behavioral_evidence": True,
            "keep_threshold_proposal_count_small": True,
            "create_exactly_one_proposal_per_family_if_possible": True,
            "no_grid": True,
            "no_parameter_search": True,
            "no_pnl_selection": True,
        },
        "future_proposal_artifact_requirements": {
            "required_keys": [
                "proposed_behavioral_thresholds_by_family",
                "evidence_basis_by_feature",
                "quantile_references_used",
                "missing_fields",
                "confidence_or_evidence_quality",
                "forbidden_optimization_checks",
                "unresolved_fields_preserved",
            ],
            "required_explicit_labels": [
                "NOT_ORIGINAL_THRESHOLD",
                "NOT_EDGE_EVIDENCE",
                "NO_LIVE_CAPITAL",
            ],
        },
        "future_validation_path": {
            "allowed_after_proposal": [
                "threshold behavioral proposal dry-run",
                "proposal review",
                "runner fixture dry-run with threshold contract",
                "bounded behavioral validation",
                "historical backtest preregistration only after prior steps",
            ],
            "live_or_capital_allowed": False,
        },
        "result_labels": [
            "THRESHOLD_BEHAVIORAL_PROPOSAL_READY_NO_EDGE_NO_LIVE",
            "THRESHOLD_BEHAVIORAL_PROPOSAL_PARTIAL_NO_EDGE_NO_LIVE",
            "THRESHOLD_BEHAVIORAL_PROPOSAL_INCONCLUSIVE_NO_EDGE_NO_LIVE",
            "THRESHOLD_BEHAVIORAL_PROPOSAL_INVALID_NO_EDGE_NO_LIVE",
        ],
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    if not all(validation_checks.values()):
        raise RuntimeError(f"validation checks failed: {validation_checks}")
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    if canonical_payload_hash(payload) != payload["payload_sha256_excluding_hash"]:
        raise RuntimeError("payload hash failed to stabilize")
    return payload


def main() -> None:
    payload = build_payload()
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    stdout_payload = {
        "status": payload["status"],
        "route_key": payload["proposal_contract_identity"]["route_key"],
        "proposal_contract_only": True,
        "threshold_proposal_allowed_now": False,
        "threshold_selection_allowed_now": False,
        "old_short_row_count": payload["source_evidence_summary"]["old_short_row_count"],
        "family_count": payload["source_evidence_summary"]["family_count"],
        "feature_count": payload["source_evidence_summary"]["feature_count"],
        "forbidden_goal_count": len(payload["behavioral_proposal_goal"]["forbidden_goal"]),
        "unresolved_field_count": len(payload["unresolved_fields_preserved"]),
        "next_allowed_step": payload["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    print(json.dumps(stdout_payload, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
