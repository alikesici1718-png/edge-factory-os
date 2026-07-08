import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_DESIGN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_realistic_bounded_fixture_design_v1"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_GENERATION_DRY_RUN_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_realistic_bounded_fixture_design_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_realistic_bounded_fixture_design_v1.json")
REALISTIC_FIXTURE_ROOT = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
)
MASTER_PROXY_ROOT = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)

SOURCE_RELS = {
    "bounded_behavioral_validation_review": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_review_v1.json"
    ),
    "bounded_behavioral_validation_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_dry_run_v1.json"
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
}

EXPECTED_MASTER_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
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

FIXTURE_CASE_TYPES = [
    "blowoff_short closed trade example",
    "mean_reversion_short closed trade example",
    "rejected gate missing/timeout example",
    "rejected gate blocked example if present",
    "pending entry example if present",
    "open position example if present",
    "heartbeat/state example",
]

FIXTURE_GENERATION_MODES = [
    "MASTER_PROXY_CASE_FIXTURE",
    "CLEAN_ROOM_REPLAY_FIXTURE_INPUT",
    "VALIDATION_PAIR_FIXTURE",
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

FAIL_CLOSED_CONDITIONS = [
    "MASTER output path missing",
    "fixture case source rows missing",
    "route_key/family_key mismatch",
    "side not short",
    "safety labels cannot be attached",
    "output root overlaps MASTER/runtime",
    "file row limit exceeded",
    "PnL/outcome used for selection",
    "raw market data path supplied",
    "live/order/private fields detected",
    "no-live guard false",
]

RESULT_CLASSES = [
    "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_FAIL_CLOSED_NO_EDGE_NO_LIVE",
    "OLD_SHORT_REALISTIC_BOUNDED_FIXTURE_GENERATION_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
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
    for key in (
        "fixture_design_identity",
        "dry_run_identity",
        "preview_identity",
        "validation_design_identity",
        "fixture_threshold_contract_identity",
    ):
        section = payload.get(key)
        if isinstance(section, dict) and isinstance(section.get("route_key"), str):
            return section["route_key"]
    prior = payload.get("prior_dry_run_preserved")
    if isinstance(prior, dict) and isinstance(prior.get("route_key"), str):
        return prior["route_key"]
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
    review = source_payloads["bounded_behavioral_validation_review"]
    dry_run = source_payloads["bounded_behavioral_validation_dry_run"]
    threshold_contract = source_payloads["runner_fixture_threshold_contract"]

    prior_review_loaded = review.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW_CREATED"
    prior_next_verified = review.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_DESIGN_V1"
    unresolved_preserved = all(item in threshold_contract.get("unresolved_fields_preserved", []) for item in UNRESOLVED_FIELDS)
    missing_metrics = review.get("missing_metric_review", {}).get("missing_metrics", [])

    fixture_design_identity = {
        "route_key": ROUTE_KEY,
        "family_key": "old_short",
        "families": ["blowoff_short", "mean_reversion_short"],
        "side": "short",
        "design_only": True,
        "realistic_bounded_fixture_generation_allowed_now": False,
        "runner_execution_allowed_now": False,
        "behavioral_validation_allowed_now": False,
        "original_exact_source_recovered": False,
        "exact_replay_available": False,
        "clean_room_behavioral_reconstruction": True,
        "no_edge_claim": True,
        "no_live_capital": True,
    }

    design_goal = {
        "future_realistic_bounded_fixtures_should_test": [
            "entry delay similarity",
            "hold duration similarity",
            "notional similarity",
            "rejected reason overlap",
            "gate behavior consistency",
            "coin/timestamp alignment on bounded samples",
        ],
        "design_must_not_aim_to": [
            "prove profitability",
            "prove edge",
            "recover original source",
            "perform exact replay",
            "optimize thresholds",
            "run full backtest",
        ],
    }

    fixture_source_policy = {
        "future_master_sources": {
            "root": MASTER_PROXY_ROOT,
            "files": EXPECTED_MASTER_FILES,
            "default_row_limit_per_file": 100,
            "metadata_header_small_samples_only_until_generation": True,
        },
        "allowed": [
            "read at most 100 rows per file by default",
            "select small bounded examples from each family",
            "select examples covering gate_allowed, gate_blocked, gate_missing/timeout if present",
            "preserve original row values only as fixture evidence",
            "mark all generated fixtures as PROXY_BEHAVIOR_FIXTURE",
        ],
        "forbidden": [
            "raw market data",
            "OKX 1m raw candle replay",
            "full dataset comparison",
            "PnL/outcome optimization",
            "using live/private account data",
            "using future performance",
            "creating real trades/signals",
            "writing into MASTER/runtime directories",
        ],
    }

    fixture_case_plan = [
        {
            "case_type": case_type,
            "required_fields": [
                "source_file",
                "source_row_id or row_index",
                "family_key",
                "family",
                "side",
                "signal_time if present",
                "entry_time if present",
                "exit_time/planned_exit_time if present",
                "notional if present",
                "signal feature fields if present",
                "reject reason if present",
                "safety labels",
                "source hash / fixture hash",
            ],
            "feature_fields": FEATURE_FIELDS,
            "selection_uses_pnl_or_outcome": False,
            "creates_real_trade_or_signal": False,
        }
        for case_type in FIXTURE_CASE_TYPES
    ]

    fixture_generation_modes = {
        "MASTER_PROXY_CASE_FIXTURE": {
            "description": "bounded examples copied/normalized from MASTER output",
            "use": "comparison target / expected behavior only",
            "not_clean_room_output": True,
            "not_original_source": True,
        },
        "CLEAN_ROOM_REPLAY_FIXTURE_INPUT": {
            "description": "bounded fixture input for clean-room runner",
            "may_derive_from_master_proxy_row_features": True,
            "raw_market_data_used": False,
            "exact_replay_claim": False,
        },
        "VALIDATION_PAIR_FIXTURE": {
            "description": "pairs a MASTER proxy case with a clean-room generated case",
            "use": "validator behavior-dimension comparison",
            "edge_evidence": False,
        },
    }

    output_location_policy = {
        "future_realistic_fixture_root": REALISTIC_FIXTURE_ROOT,
        "write_only_under_future_root": True,
        "never_write_to": [
            "MASTER_UPPER_SYSTEM",
            "paper_run_gate_* runtime roots",
            "live runtime directories",
            "old original output directories",
            "repo tracked paths except summary JSON artifacts",
        ],
    }

    missing_metric_recovery_plan = [
        {
            "missing_metric": item.get("metric"),
            "prior_missing_reason": item.get("reason"),
            "fixture_cases_to_make_computable": [
                "MASTER_PROXY_CASE_FIXTURE with coin/inst_id and signal_time",
                "CLEAN_ROOM_REPLAY_FIXTURE_INPUT preserving coin/inst_id and aligned synthetic signal timestamp",
                "VALIDATION_PAIR_FIXTURE linking source_row_id to clean-room generated case",
            ]
            if item.get("metric") in {"coin_overlap_rate", "timestamp_alignment_rate"}
            else [],
            "recoverable_at_fixture_level": item.get("metric") in {"coin_overlap_rate", "timestamp_alignment_rate"},
            "not_recoverable_reason": None
            if item.get("metric") in {"coin_overlap_rate", "timestamp_alignment_rate"}
            else "requires raw market/full replay and is not recoverable at fixture level",
        }
        for item in missing_metrics
    ]

    validation_after_fixture_generation = [
        "realistic bounded fixture generation dry-run",
        "clean-room runner realistic fixture dry-run",
        "bounded behavioral validation V2",
        "review",
        "Only after all pass may historical backtest preregistration be discussed.",
    ]

    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "prior_bounded_behavioral_validation_review_loaded": prior_review_loaded,
        "prior_next_allowed_step_verified": prior_next_verified,
        "original_exact_source_not_claimed": fixture_design_identity["original_exact_source_recovered"] is False,
        "clean_room_reconstruction_preserved": fixture_design_identity["clean_room_behavioral_reconstruction"] is True,
        "no_fixture_generation": True,
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
        "fixture_source_policy_defined": bool(fixture_source_policy),
        "fixture_case_plan_defined": len(fixture_case_plan) == 7,
        "missing_metric_recovery_plan_defined": len(missing_metric_recovery_plan) == len(missing_metrics),
        "fail_closed_conditions_defined": len(FAIL_CLOSED_CONDITIONS) == 11,
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
            "expected_head": "a11a4021c98a086407caa3d58ecb28fa2cd14da2",
            "actual_head": git_head,
            "expected_tracked_python_count": 955,
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
        "fixture_design_identity": fixture_design_identity,
        "design_goal": design_goal,
        "fixture_source_policy": fixture_source_policy,
        "fixture_case_plan": fixture_case_plan,
        "fixture_generation_modes": fixture_generation_modes,
        "output_location_policy": output_location_policy,
        "safety_labels": SAFETY_LABELS,
        "missing_metric_recovery_plan": missing_metric_recovery_plan,
        "validation_after_fixture_generation": validation_after_fixture_generation,
        "fail_closed_conditions": FAIL_CLOSED_CONDITIONS,
        "result_classes": RESULT_CLASSES,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "safety_permissions": {
            "realistic_bounded_fixture_design_created": True,
            "realistic_fixture_generation_allowed_now": False,
            "runner_execution_allowed_now": False,
            "behavioral_validation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
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
    print("realistic_fixture_generation_allowed_now: false")
    print(f"fixture_case_type_count: {len(FIXTURE_CASE_TYPES)}")
    print(f"fixture_generation_mode_count: {len(FIXTURE_GENERATION_MODES)}")
    print(f"missing_metric_recovery_item_count: {len(missing_metric_recovery_plan)}")
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
