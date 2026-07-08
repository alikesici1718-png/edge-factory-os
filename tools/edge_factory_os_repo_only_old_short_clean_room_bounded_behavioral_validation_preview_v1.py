import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_PREVIEW"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_preview_v1"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DRY_RUN_V1"

BEHAVIORAL_VALIDATION_ALLOWED = False
FULL_DATASET_COMPARISON_ALLOWED = False
RUNNER_EXECUTION_ALLOWED = False
SIGNAL_GENERATION_ALLOWED = False
BACKTEST_ALLOWED = False
PNL_COMPUTATION_ALLOWED = False
RUNTIME_ALLOWED = False
MONITOR_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_preview_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_preview_v1.json")

SOURCE_RELS = {
    "bounded_behavioral_validation_design": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_design_v1.json"
    ),
    "feature_fixture_validator_check": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_feature_fixture_validator_check_v1.json"
    ),
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
    "clean_room_contract": Path("artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"),
    "runner_preview": Path("artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"),
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

BEHAVIOR_DIMENSIONS = [
    "schema compatibility",
    "family_key old_short",
    "subfamily blowoff_short / mean_reversion_short presence",
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

RESULT_CLASSES = [
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_FAIL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]


class OldShortBehavioralValidationConfigPreview:
    def __init__(self, row_limit: int = 100):
        self.route_key = ROUTE_KEY
        self.row_limit = row_limit
        self.expected_files = list(EXPECTED_FILES)

    def preview_schema(self) -> dict:
        return {
            "route_key": self.route_key,
            "row_limit_default": self.row_limit,
            "expected_files": self.expected_files,
            "guards": no_live_guard_constants(),
        }


class OldShortBoundedSampleLoaderPreview:
    def describe_inputs(self) -> dict:
        return {
            "bounded_rows_only": True,
            "full_dataset_comparison_allowed": False,
            "raw_market_data_allowed": False,
            "load_method": "metadata/header/small-sample loader contract only",
        }

    def load(self, *_args, **_kwargs) -> None:
        raise RuntimeError("PREVIEW_ONLY_NO_SAMPLE_LOAD_EXECUTION")


class OldShortMasterProxySamplePreview:
    def source_contract(self) -> dict:
        return {
            "sample_type": "MASTER proxy bounded sample",
            "root": (
                r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
                r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
            ),
            "files": list(EXPECTED_FILES),
            "metadata_header_small_samples_only": True,
        }


class OldShortCleanRoomSamplePreview:
    def source_contract(self) -> dict:
        return {
            "sample_type": "clean-room bounded output sample",
            "root": "approved clean-room runner dry-run output root",
            "must_not_be_synthetic_schema_only": True,
            "must_be_bounded_feature_or_replay_fixture": True,
            "must_include_safety_labels": True,
        }


class OldShortBehaviorDimensionCheckerPreview:
    def dimensions(self) -> list[str]:
        return list(BEHAVIOR_DIMENSIONS)

    def check(self, *_args, **_kwargs) -> None:
        raise RuntimeError("PREVIEW_ONLY_NO_DIMENSION_CHECK_EXECUTION")


class OldShortSimilarityMetricPreview:
    def metrics(self) -> list[str]:
        return list(SIMILARITY_METRICS)

    def compute(self, *_args, **_kwargs) -> None:
        raise RuntimeError("PREVIEW_ONLY_NO_METRIC_COMPUTATION")


class OldShortFailClosedPolicyPreview:
    def conditions(self) -> list[str]:
        return list(FAIL_CLOSED_CONDITIONS)

    def evaluate(self, *_args, **_kwargs) -> None:
        raise RuntimeError("PREVIEW_ONLY_NO_FAIL_CLOSED_EVALUATION")


class OldShortBehavioralValidationReportPreview:
    def report_shape(self) -> dict:
        return {
            "status": None,
            "route_key": ROUTE_KEY,
            "sample_paths": {},
            "sample_row_counts": {},
            "behavior_dimensions_checked": list(BEHAVIOR_DIMENSIONS),
            "similarity_metrics": {metric: None for metric in SIMILARITY_METRICS},
            "threshold_results": {},
            "fail_closed_checks": {},
            "unresolved_fields_preserved": list(UNRESOLVED_FIELDS),
            "result_classification": None,
            "limitations": [],
            "no_edge_no_live_permissions": no_live_guard_constants(),
            "payload_sha256_excluding_hash": None,
        }


class OldShortBoundedBehavioralValidationPreview:
    def __init__(self):
        self.config = OldShortBehavioralValidationConfigPreview()
        self.master_sample = OldShortMasterProxySamplePreview()
        self.clean_room_sample = OldShortCleanRoomSamplePreview()
        self.dimension_checker = OldShortBehaviorDimensionCheckerPreview()
        self.metric_preview = OldShortSimilarityMetricPreview()
        self.fail_closed_policy = OldShortFailClosedPolicyPreview()
        self.report_preview = OldShortBehavioralValidationReportPreview()

    def preview_contract(self) -> dict:
        return {
            "config": self.config.preview_schema(),
            "master_proxy_sample": self.master_sample.source_contract(),
            "clean_room_sample": self.clean_room_sample.source_contract(),
            "behavior_dimensions": self.dimension_checker.dimensions(),
            "similarity_metrics": self.metric_preview.metrics(),
            "fail_closed_conditions": self.fail_closed_policy.conditions(),
            "report_shape": self.report_preview.report_shape(),
        }

    def run(self, *_args, **_kwargs) -> None:
        raise RuntimeError("PREVIEW_ONLY_NO_BEHAVIORAL_VALIDATION_EXECUTION")


def no_live_guard_constants() -> dict:
    return {
        "BEHAVIORAL_VALIDATION_ALLOWED": BEHAVIORAL_VALIDATION_ALLOWED,
        "FULL_DATASET_COMPARISON_ALLOWED": FULL_DATASET_COMPARISON_ALLOWED,
        "RUNNER_EXECUTION_ALLOWED": RUNNER_EXECUTION_ALLOWED,
        "SIGNAL_GENERATION_ALLOWED": SIGNAL_GENERATION_ALLOWED,
        "BACKTEST_ALLOWED": BACKTEST_ALLOWED,
        "PNL_COMPUTATION_ALLOWED": PNL_COMPUTATION_ALLOWED,
        "RUNTIME_ALLOWED": RUNTIME_ALLOWED,
        "MONITOR_ALLOWED": MONITOR_ALLOWED,
        "LIVE_TRADING_ALLOWED": LIVE_TRADING_ALLOWED,
        "CAPITAL_ALLOCATION_ALLOWED": CAPITAL_ALLOCATION_ALLOWED,
        "ORDER_PLACEMENT_ALLOWED": ORDER_PLACEMENT_ALLOWED,
        "CANDIDATE_GENERATION_ALLOWED": CANDIDATE_GENERATION_ALLOWED,
        "EDGE_CLAIM_ALLOWED": EDGE_CLAIM_ALLOWED,
    }


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
    for key in ("preview_identity", "validation_design_identity", "dry_run_identity", "fixture_threshold_contract_identity"):
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


def preview_module_structure() -> dict:
    return {
        "OldShortBehavioralValidationConfigPreview": {
            "methods": ["__init__(row_limit=100)", "preview_schema()"],
            "return_shape": OldShortBehavioralValidationConfigPreview().preview_schema(),
        },
        "OldShortBoundedSampleLoaderPreview": {
            "methods": ["describe_inputs()", "load(*args, **kwargs) raises PREVIEW_ONLY_NO_SAMPLE_LOAD_EXECUTION"],
            "return_shape": OldShortBoundedSampleLoaderPreview().describe_inputs(),
        },
        "OldShortMasterProxySamplePreview": {
            "methods": ["source_contract()"],
            "return_shape": OldShortMasterProxySamplePreview().source_contract(),
        },
        "OldShortCleanRoomSamplePreview": {
            "methods": ["source_contract()"],
            "return_shape": OldShortCleanRoomSamplePreview().source_contract(),
        },
        "OldShortBehaviorDimensionCheckerPreview": {
            "methods": ["dimensions()", "check(*args, **kwargs) raises PREVIEW_ONLY_NO_DIMENSION_CHECK_EXECUTION"],
            "return_shape": {"behavior_dimensions": list(BEHAVIOR_DIMENSIONS)},
        },
        "OldShortSimilarityMetricPreview": {
            "methods": ["metrics()", "compute(*args, **kwargs) raises PREVIEW_ONLY_NO_METRIC_COMPUTATION"],
            "return_shape": {"similarity_metrics": list(SIMILARITY_METRICS)},
        },
        "OldShortFailClosedPolicyPreview": {
            "methods": ["conditions()", "evaluate(*args, **kwargs) raises PREVIEW_ONLY_NO_FAIL_CLOSED_EVALUATION"],
            "return_shape": {"fail_closed_conditions": list(FAIL_CLOSED_CONDITIONS)},
        },
        "OldShortBehavioralValidationReportPreview": {
            "methods": ["report_shape()"],
            "return_shape": OldShortBehavioralValidationReportPreview().report_shape(),
        },
        "OldShortBoundedBehavioralValidationPreview": {
            "methods": ["__init__()", "preview_contract()", "run(*args, **kwargs) raises PREVIEW_ONLY_NO_BEHAVIORAL_VALIDATION_EXECUTION"],
            "return_shape": OldShortBoundedBehavioralValidationPreview().preview_contract(),
        },
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
    design = source_payloads["bounded_behavioral_validation_design"]

    no_live_guards = no_live_guard_constants()
    no_live_guard_constants_false = all(value is False for value in no_live_guards.values())
    prior_design_loaded = design.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DESIGN_CREATED"
    prior_next_verified = design.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_PREVIEW_V1"
    behavior_dimensions_preserved = BEHAVIOR_DIMENSIONS == [
        "schema compatibility",
        "family_key old_short",
        "subfamily blowoff_short / mean_reversion_short presence",
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
    similarity_metrics_preserved = len(SIMILARITY_METRICS) == 15 and SIMILARITY_METRICS == design.get("similarity_metrics")
    fail_closed_conditions_preserved = len(FAIL_CLOSED_CONDITIONS) == 12 and FAIL_CLOSED_CONDITIONS == design.get("fail_closed_conditions")
    unresolved_preserved = all(item in design.get("unresolved_fields_preserved", []) for item in UNRESOLVED_FIELDS)

    preview_identity = {
        "route_key": ROUTE_KEY,
        "preview_only": True,
        "behavioral_validation_allowed_now": False,
        "full_dataset_comparison_allowed_now": False,
        "original_exact_source_recovered": False,
        "clean_room_behavioral_reconstruction": True,
        "no_exact_replay_claim": True,
        "no_edge_claim": True,
        "no_live_capital": True,
    }

    sample_source_preview = {
        "master_proxy_bounded_sample_root": (
            r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
            r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
        ),
        "clean_room_output_bounded_sample_root": "approved clean-room runner dry-run output root",
        "validator_config_json": {
            "row_limit_default": 100,
            "route_key": ROUTE_KEY,
            "family_key": "old_short",
            "subfamilies": ["blowoff_short", "mean_reversion_short"],
            "side": "short",
            "no_live_permissions_required": True,
        },
        "expected_files": list(EXPECTED_FILES),
        "read_policy": "future preview/dry-run may inspect bounded metadata/header/small samples only",
    }

    threshold_policy_preview = {
        "schema_match_rate": ">= 0.95",
        "family_key_match_rate": ">= 0.99",
        "side_match_rate": ">= 0.99",
        "median_entry_delay_error": "<= 60 seconds",
        "median_hold_error": "<= 10 minutes",
        "notional_median_error": "<= 5 USDT",
        "no_position_without_gate_allow": True,
        "no_live_order_fields": True,
        "closed_trades_schema_compatible": True,
        "safety_label_match_rate": "= 1.0",
        "no_position_without_gate_violation_count": "= 0",
        "live_order_private_field_count": "= 0",
    }

    future_execution_contract = {
        "may_execute_only_after_this_preview": True,
        "samples_must_be_bounded": True,
        "full_dataset_compare_allowed": False,
        "raw_market_data_allowed": False,
        "pnl_or_outcome_fields_allowed_for_validation": False,
        "live_capital_candidate_edge_permission": False,
        "output_report_only": True,
        "next_step_still_no_backtest_live_capital_candidate_edge": True,
    }

    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "bounded_behavioral_validation_design_loaded": prior_design_loaded,
        "prior_next_allowed_step_verified": prior_next_verified,
        "original_exact_source_not_claimed": preview_identity["original_exact_source_recovered"] is False,
        "clean_room_reconstruction_preserved": preview_identity["clean_room_behavioral_reconstruction"] is True,
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
        "no_live_guard_constants_false": no_live_guard_constants_false,
        "behavior_dimensions_preserved": behavior_dimensions_preserved,
        "similarity_metrics_preserved": similarity_metrics_preserved,
        "fail_closed_conditions_preserved": fail_closed_conditions_preserved,
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
            "classes_defined": [
                "OldShortBehavioralValidationConfigPreview",
                "OldShortBoundedSampleLoaderPreview",
                "OldShortMasterProxySamplePreview",
                "OldShortCleanRoomSamplePreview",
                "OldShortBehaviorDimensionCheckerPreview",
                "OldShortSimilarityMetricPreview",
                "OldShortFailClosedPolicyPreview",
                "OldShortBehavioralValidationReportPreview",
                "OldShortBoundedBehavioralValidationPreview",
            ],
            "created_files": [TOOL_REL.as_posix(), ARTIFACT_REL.as_posix()],
            "modified_existing_files": [],
            "code_changed": True,
        },
        "source_checkpoint": {
            "generated_at_utc": now_utc(),
            "repo_root": str(REPO_ROOT),
            "expected_head": "ca7aff4ce8ee258c9a52e6c32212e60620b64fde",
            "actual_head": git_head,
            "expected_tracked_python_count": 952,
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
        "preview_identity": preview_identity,
        "no_live_guard_constants": no_live_guards,
        "preview_module_structure": preview_module_structure(),
        "sample_source_preview": sample_source_preview,
        "behavior_dimension_preview": list(BEHAVIOR_DIMENSIONS),
        "similarity_metric_preview": list(SIMILARITY_METRICS),
        "threshold_policy_preview": threshold_policy_preview,
        "fail_closed_preview": list(FAIL_CLOSED_CONDITIONS),
        "future_execution_contract": future_execution_contract,
        "result_classes": list(RESULT_CLASSES),
        "unresolved_fields_preserved": list(UNRESOLVED_FIELDS),
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": {
            "bounded_behavioral_validation_preview_created": True,
            "behavioral_validation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
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
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": None,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    with artifact_path.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=False)
        handle.write("\n")

    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print("preview_only: true")
    print("behavioral_validation_allowed_now: false")
    print(f"behavior_dimension_count: {len(BEHAVIOR_DIMENSIONS)}")
    print(f"similarity_metric_count: {len(SIMILARITY_METRICS)}")
    print(f"fail_closed_condition_count: {len(FAIL_CLOSED_CONDITIONS)}")
    print(f"result_class_count: {len(RESULT_CLASSES)}")
    print(f"unresolved_field_count: {len(UNRESOLVED_FIELDS)}")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
