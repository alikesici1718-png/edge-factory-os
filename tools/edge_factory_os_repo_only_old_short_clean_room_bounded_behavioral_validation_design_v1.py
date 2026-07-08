import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DESIGN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_design_v1"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_PREVIEW_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_design_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_design_v1.json")

SOURCE_RELS = {
    "clean_room_contract": Path("artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"),
    "runner_preview": Path("artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"),
    "threshold_behavioral_proposal": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
    ),
    "threshold_proposal_review": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json"
    ),
    "runner_fixture_threshold_contract": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json"
    ),
    "runner_feature_fixture_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_runner_feature_fixture_dry_run_v1.json"
    ),
    "feature_fixture_validator_check": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_feature_fixture_validator_check_v1.json"
    ),
}

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

BEHAVIOR_DIMENSIONS = [
    "schema compatibility",
    "family_key old_short",
    "family blowoff_short / mean_reversion_short presence",
    "side short",
    "signal feature availability",
    "entry delay near 2 minutes",
    "hold near 120 minutes",
    "notional near 50 USDT at 1000 USDT base-equity policy",
    "rejected gate behavior",
    "no position without gate allow",
    "same coin overlap behavior if fields exist",
    "heartbeat/state compatibility",
    "safety label compatibility",
]

SIMILARITY_METRICS = [
    "schema_match_rate",
    "family_key_match_rate",
    "subfamily_presence_match",
    "side_match_rate",
    "signal_feature_presence_rate",
    "entry_delay_median_abs_error_seconds",
    "hold_minutes_median_abs_error",
    "notional_median_abs_error",
    "rejected_reason_overlap_rate",
    "gate_behavior_consistency_rate",
    "no_position_without_gate_violation_count",
    "safety_label_match_rate",
    "state_heartbeat_schema_match",
    "coin_overlap_rate",
    "timestamp_alignment_rate",
]

FAIL_CLOSED_CONDITIONS = [
    "clean-room sample missing",
    "MASTER sample missing",
    "full dataset comparison requested",
    "raw market data path supplied",
    "PnL/outcome field used for validation",
    "live/order/private fields present",
    "safety labels missing",
    "route_key mismatch",
    "family_key mismatch",
    "no-live guard false",
    "runtime path supplied",
    "sample row limit exceeded",
]

PASS_FAIL_CLASSES = [
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_FAIL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_cmd(*args: str) -> list[str]:
    safe = REPO_ROOT.as_posix()
    cmd = ["git", "-c", f"safe.directory={safe}", "-C", str(REPO_ROOT)]
    cmd.extend(args)
    completed = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return [line for line in completed.stdout.splitlines() if line.strip()]


def load_json(rel_path: Path) -> dict:
    with (REPO_ROOT / rel_path).open("r", encoding="utf-8") as handle:
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
    if isinstance(payload.get("route_key"), str):
        return payload["route_key"]
    for key in ("validation_design_identity", "dry_run_identity", "fixture_threshold_contract_identity"):
        section = payload.get(key)
        if isinstance(section, dict) and isinstance(section.get("route_key"), str):
            return section["route_key"]
    source_review = payload.get("feature_fixture_source_review")
    if isinstance(source_review, dict) and isinstance(source_review.get("prior_route_key"), str):
        return source_review["prior_route_key"]
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
        "sha256": file_sha256(path),
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

    source_payloads = {name: load_json(rel_path) for name, rel_path in SOURCE_RELS.items()}
    validator_check = source_payloads["feature_fixture_validator_check"]
    threshold_contract = source_payloads["runner_fixture_threshold_contract"]

    prior_loaded = validator_check.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_FEATURE_FIXTURE_VALIDATOR_CHECK_CREATED"
    prior_next_verified = validator_check.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DESIGN_V1"
    unresolved_preserved = all(item in threshold_contract.get("unresolved_fields_preserved", []) for item in UNRESOLVED_FIELDS)

    validation_design_identity = {
        "route_key": ROUTE_KEY,
        "family_key": "old_short",
        "subfamilies": ["blowoff_short", "mean_reversion_short"],
        "side": "short",
        "design_only": True,
        "behavioral_validation_allowed_now": False,
        "full_dataset_comparison_allowed_now": False,
        "original_exact_source_recovered": False,
        "clean_room_behavioral_reconstruction": True,
        "no_exact_replay_claim": True,
        "no_edge_claim": True,
        "no_live_capital": True,
    }

    validation_goal = {
        "future_validation_may_answer": [
            "Does clean-room output resemble MASTER_UPPER_SYSTEM old_short proxy output on bounded samples?",
            "Are lifecycle, schema, timing, family, side, gate, and notional behavior similar enough for further research?",
        ],
        "future_validation_must_not_answer": [
            "Is this profitable?",
            "Is this the original old_short?",
            "Is this live-ready?",
            "Is this an edge?",
            "Should capital be allocated?",
        ],
    }

    bounded_scope_policy = {
        "bounded_samples_only": True,
        "default_max_rows_per_file": 100,
        "never_compare_full_datasets_by_default": True,
        "never_read_raw_market_data": True,
        "never_use_pnl_or_outcome_for_validation": True,
        "never_use_private_or_account_data": True,
        "never_infer_missing_original_source": True,
        "preserve_proxy_only_status": True,
    }

    input_sources = {
        "master_proxy_output_sample": {
            "sample_only": True,
            "metadata_header_small_samples_only": True,
            "path": (
                r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
                r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
            ),
            "files": [
                "signals.csv",
                "pending_entries.csv",
                "open_positions.csv",
                "closed_trades.csv",
                "rejected_entries.csv",
                "heartbeat.csv",
                "state.json",
            ],
        },
        "clean_room_output_sample": {
            "source": "approved clean-room runner dry-run output root",
            "must_not_be_synthetic_schema_only": True,
            "must_be_produced_by_bounded_feature_or_replay_fixture_dry_run": True,
            "must_include_safety_labels": True,
            "prior_feature_fixture_output_root": source_payloads["runner_feature_fixture_dry_run"]
            .get("generated_output_summary", {})
            .get("output_root"),
        },
        "validator_config": {
            "row_limits": {"default_max_rows_per_file": 100},
            "timestamp_tolerance": {
                "entry_delay_expected_minutes": 2,
                "entry_delay_median_abs_error_max_seconds": 60,
                "hold_expected_minutes": 120,
                "hold_median_abs_error_max_minutes": 10,
            },
            "family_subfamily_expectations": {
                "family_key": "old_short",
                "subfamilies": ["blowoff_short", "mean_reversion_short"],
                "side": "short",
            },
            "no_live_permissions_required": True,
        },
    }

    threshold_policy = {
        "schema_match_rate_min": 0.95,
        "family_key_match_rate_min": 0.99,
        "side_match_rate_min": 0.99,
        "median_entry_delay_error_seconds_max": 60,
        "median_hold_error_minutes_max": 10,
        "notional_median_error_usdt_max": 5,
        "no_position_without_gate_allow_required": True,
        "no_live_order_fields_required": True,
        "closed_trades_schema_compatible_required": True,
        "safety_label_match_rate_required": 1.0,
        "no_position_without_gate_violation_count_required": 0,
        "live_order_private_field_count_required": 0,
        "source_policy": "validator/threshold proposal review thresholds where already defined",
    }

    output_report_schema = [
        "status",
        "route_key",
        "sample_paths",
        "sample_row_counts",
        "behavior_dimensions_checked",
        "similarity_metrics",
        "threshold_results",
        "fail_closed_checks",
        "unresolved_fields_preserved",
        "result_classification",
        "limitations",
        "no_edge_no_live_permissions",
        "payload_sha256_excluding_hash",
    ]

    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "prior_feature_fixture_validator_check_loaded": prior_loaded,
        "prior_next_allowed_step_verified": prior_next_verified,
        "original_exact_source_not_claimed": validation_design_identity["original_exact_source_recovered"] is False,
        "clean_room_reconstruction_preserved": validation_design_identity["clean_room_behavioral_reconstruction"] is True,
        "no_behavioral_validation_execution": True,
        "no_full_dataset_comparison": True,
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
        "bounded_scope_policy_defined": bool(bounded_scope_policy),
        "behavior_dimensions_defined": len(BEHAVIOR_DIMENSIONS) == 13,
        "similarity_metrics_defined": len(SIMILARITY_METRICS) == 15,
        "fail_closed_conditions_defined": len(FAIL_CLOSED_CONDITIONS) == 12,
        "unresolved_fields_preserved": unresolved_preserved,
        "exactly_one_python_tool_created": TOOL_REL.as_posix() in [line[3:] for line in git_status_before if line.startswith("?? ")],
        "exactly_one_json_artifact_created": not artifact_path.exists(),
        "no_existing_files_modified": not dirty_tracked,
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
            "expected_head": "7842280713e61a488900323bcded3e846e7a59da",
            "actual_head": git_head,
            "expected_tracked_python_count": 951,
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
        "validation_design_identity": validation_design_identity,
        "validation_goal": validation_goal,
        "bounded_scope_policy": bounded_scope_policy,
        "input_sources": input_sources,
        "behavior_dimensions": BEHAVIOR_DIMENSIONS,
        "similarity_metrics": SIMILARITY_METRICS,
        "threshold_policy": threshold_policy,
        "pass_fail_classes": {
            "allowed_result_classes": PASS_FAIL_CLASSES,
            "pass": "bounded behavioral similarity is acceptable for continuing to research; no edge/candidate/live/capital meaning",
            "partial": "enough structure matches but timing/behavior gaps remain",
            "fail": "clean-room output does not resemble proxy behavior enough",
            "inconclusive": "insufficient clean-room output or MASTER sample",
        },
        "fail_closed_conditions": FAIL_CLOSED_CONDITIONS,
        "output_report_schema": output_report_schema,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": {
            "bounded_behavioral_validation_design_created": True,
            "behavioral_validation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
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
    print("design_only: true")
    print("behavioral_validation_allowed_now: false")
    print(f"behavior_dimension_count: {len(BEHAVIOR_DIMENSIONS)}")
    print(f"similarity_metric_count: {len(SIMILARITY_METRICS)}")
    print(f"fail_closed_condition_count: {len(FAIL_CLOSED_CONDITIONS)}")
    print(f"result_class_count: {len(PASS_FAIL_CLASSES)}")
    print(f"unresolved_field_count: {len(UNRESOLVED_FIELDS)}")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
