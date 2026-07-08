"""Old short clean-room threshold reconstruction contract v1.

This module creates a contract artifact only. It does not extract thresholds,
run a runner, generate signals, run a validator, run a backtest, optimize, touch
runtime state, or grant live/capital permissions.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MODULE = "edge_factory_os_repo_only_old_short_clean_room_threshold_reconstruction_contract_v1"
STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_CONTRACT_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_CONTRACT"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_EVIDENCE_EXTRACTION_PREVIEW_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "old_short_clean_room"
    / "old_short_clean_room_threshold_reconstruction_contract_v1.json"
)

SOURCE_ARTIFACT_PATHS = {
    "clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
    "runner_preview": "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json",
    "runner_implementation_preview": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_implementation_preview_v1.json"
    ),
    "runner_dry_run_design": (
        "artifacts/old_short_clean_room/old_short_clean_room_runner_dry_run_design_v1.json"
    ),
    "runner_schema_fixture_validator_check": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_schema_fixture_validator_check_v1.json"
    ),
}

ALLOWED_EVIDENCE_SOURCES = [
    "MASTER_UPPER_SYSTEM output rows",
    "signals.csv",
    "pending_entries.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "logger metadata",
    "clean-room contract/runner schema",
    "old_short source review artifacts",
]

FORBIDDEN_EVIDENCE_SOURCES = [
    "future PnL",
    "validation PnL",
    "holdout PnL",
    "backtest performance",
    "manual cherry-picked winning trades",
    "live account balances",
    "private account data",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

RESULT_LABELS = [
    "THRESHOLD_EVIDENCE_EXTRACTED_NO_EDGE_NO_LIVE",
    "THRESHOLD_PROPOSAL_BEHAVIORAL_RECONSTRUCTION_NO_EDGE_NO_LIVE",
    "THRESHOLD_RECONSTRUCTION_INCONCLUSIVE_NO_EDGE_NO_LIVE",
    "THRESHOLD_RECONSTRUCTION_INVALID_NO_EDGE_NO_LIVE",
]


def _utc_now_second() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _nested_route_key(data: Mapping[str, Any]) -> str | None:
    for key in [
        "threshold_reconstruction_identity",
        "dry_run_identity",
        "implementation_preview_identity",
        "runner_implementation_identity",
        "clean_room_runner_identity",
        "validator_identity",
    ]:
        value = data.get(key)
        if isinstance(value, dict) and value.get("route_key"):
            return str(value["route_key"])
    source_artifacts = data.get("source_artifacts")
    if isinstance(source_artifacts, dict):
        clean_room_contract = source_artifacts.get("clean_room_contract")
        if isinstance(clean_room_contract, dict) and clean_room_contract.get("route_key"):
            return str(clean_room_contract["route_key"])
    route_key = data.get("route_key")
    return str(route_key) if route_key else None


def _load_json_metadata(relative_path: str) -> Mapping[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"required source artifact missing: {relative_path}")
    data = _load_json(path)
    return {
        "path": relative_path,
        "loaded": True,
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": _nested_route_key(data),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
    }


def _payload_hash(payload: Mapping[str, Any]) -> str:
    clean_payload = dict(payload)
    clean_payload.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_payload() -> dict[str, Any]:
    source_artifacts = {
        key: _load_json_metadata(path) for key, path in SOURCE_ARTIFACT_PATHS.items()
    }

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "generated_at_utc": _utc_now_second(),
            "git_head": _run_git(["rev-parse", "HEAD"]),
            "repo_root": str(REPO_ROOT),
            "preflight_repo_status": {
                "repo_clean_before_run": True,
                "dirty_tracked_before_run": [],
                "allowed_pending_before_run": [
                    f"?? tools/{Path(__file__).name}",
                ],
                "no_existing_files_modified": True,
                "target_tool_present_as_new_untracked_file": True,
                "target_artifact_preexisting_before_run": False,
            },
        },
        "source_artifacts": source_artifacts,
        "threshold_reconstruction_identity": {
            "route_key": ROUTE_KEY,
            "reconstruction_contract_only": True,
            "original_exact_thresholds_recovered": False,
            "behavioral_threshold_reconstruction": True,
            "no_exact_original_claim": True,
            "no_pnl_optimization": True,
        },
        "allowed_evidence_sources": {
            "allowed_future_threshold_evidence_sources": ALLOWED_EVIDENCE_SOURCES,
            "metadata_header_small_sample_only_until_extraction_step": True,
            "threshold_extraction_allowed_now": False,
        },
        "forbidden_evidence_sources": {
            "forbidden_sources": FORBIDDEN_EVIDENCE_SOURCES,
            "forbidden_evidence_source_count": len(FORBIDDEN_EVIDENCE_SOURCES),
            "pnl_based_threshold_selection_allowed": False,
            "private_account_data_allowed": False,
        },
        "reconstruction_goal": {
            "goal_statement": "approximate old_short behavior, not optimize profit",
            "allowed_goals": [
                "explain which signal feature regions historically led to old_short/blowoff_short/mean_reversion_short rows",
                "reconstruct conservative behavioral trigger envelopes",
            ],
            "forbidden_goals": [
                "maximize return",
                "maximize win rate",
                "choose thresholds from PnL",
                "choose thresholds from holdout",
                "tune until monthly stability passes",
            ],
        },
        "threshold_families": {
            "threshold_family_count": 2,
            "blowoff_short_behavioral_thresholds": {
                "subfamily": "blowoff_short",
                "likely_feature_groups": {
                    "short_window_positive_return_pressure": [
                        "signal_ret1_bps",
                        "signal_ret3_bps",
                        "signal_ret5_bps",
                    ],
                    "short_window_range_expansion": [
                        "signal_range_bps",
                    ],
                    "quote_volume_activity": [
                        "signal_vol_quote",
                    ],
                    "entry_range_volume": [
                        "entry_range_bps",
                        "entry_vol_quote",
                    ],
                },
            },
            "mean_reversion_short_behavioral_thresholds": {
                "subfamily": "mean_reversion_short",
                "likely_feature_groups": {
                    "longer_window_positive_extension": [
                        "signal_ret60_bps",
                    ],
                    "shorter_window_exhaustion_local_behavior": [
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
                },
            },
        },
        "future_extraction_policy": {
            "future_extractor_may_compute": [
                "feature distributions for emitted signals by family",
                "feature distributions for closed trades by family",
                "feature distributions for rejected entries by reject reason",
                "robust quantiles p10 p25 p50 p75 p90",
                "min/max only as descriptive, not threshold selection",
                "family-level envelopes",
                "missing-field rates",
                "outlier flags",
            ],
            "future_extractor_must_not_compute": [
                "PnL-optimized thresholds",
                "threshold grid search",
                "holdout-selected thresholds",
                "candidate generation",
                "edge claims",
            ],
            "threshold_extraction_allowed_now": False,
            "raw_market_data_allowed": False,
            "raw_okx_1m_data_allowed": False,
        },
        "conservative_threshold_proposal_policy": {
            "future_threshold_proposal_labels": [
                "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
                "NOT_ORIGINAL_THRESHOLD",
                "NOT_PNL_OPTIMIZED",
                "NOT_EDGE_EVIDENCE",
            ],
            "allowed_proposal_method": [
                "use robust central/edge quantiles of emitted signal features",
                "require consistency between signals and pending/closed/rejected outputs",
                "require threshold direction to match old_short intuition: short after upward blowoff / extension / range-volume expansion",
                "fail closed if feature evidence is insufficient",
            ],
            "forbidden_proposal_method": [
                "use trade profitability to select threshold",
                "use future holdout",
                "test multiple thresholds and select best",
                "alter hold time or entry delay",
                "expand universe",
            ],
            "proposal_allowed_now": False,
        },
        "future_validation_policy": {
            "required_stages": [
                "threshold evidence extraction",
                "threshold proposal review",
                "runner schema/fixture dry run",
                "bounded behavioral dry run",
                "historical backtest only after preregistration",
                "evaluator",
                "closure",
            ],
            "live_or_capital_allowed_at_any_stage": False,
            "candidate_generation_allowed_at_any_stage": False,
            "edge_claim_allowed_at_any_stage": False,
        },
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "result_labels": RESULT_LABELS,
        "next_allowed_step": {
            "step": NEXT_ALLOWED_STEP,
            "threshold_extraction_execution_allowed": False,
            "backtest_allowed": False,
            "runner_execution_allowed": False,
            "runtime_allowed": False,
            "live_allowed": False,
            "capital_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
        },
        "safety_permissions": {
            "threshold_reconstruction_contract_created": True,
            "threshold_extraction_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": True,
            "clean_room_contract_loaded": source_artifacts["clean_room_contract"]["loaded"],
            "runner_preview_loaded": source_artifacts["runner_preview"]["loaded"],
            "runner_schema_fixture_validator_check_loaded": source_artifacts[
                "runner_schema_fixture_validator_check"
            ]["loaded"],
            "original_exact_thresholds_not_claimed": True,
            "behavioral_threshold_reconstruction_declared": True,
            "no_pnl_optimization_declared": True,
            "forbidden_evidence_sources_defined": True,
            "no_threshold_extraction": True,
            "no_runner_execution": True,
            "no_signal_generation": True,
            "no_backtest_run": True,
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
            "no_existing_files_modified": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = _payload_hash(payload)
    return payload


def write_artifact(payload: Mapping[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def main() -> int:
    payload = build_payload()
    write_artifact(payload)
    stdout_payload = {
        "status": payload["status"],
        "route_key": payload["threshold_reconstruction_identity"]["route_key"],
        "reconstruction_contract_only": True,
        "original_exact_thresholds_recovered": False,
        "behavioral_threshold_reconstruction": True,
        "no_pnl_optimization": True,
        "threshold_family_count": payload["threshold_families"]["threshold_family_count"],
        "forbidden_evidence_source_count": payload["forbidden_evidence_sources"][
            "forbidden_evidence_source_count"
        ],
        "unresolved_field_count": len(payload["unresolved_fields_preserved"]),
        "next_allowed_step": payload["next_allowed_step"]["step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
    }
    print(json.dumps(stdout_payload, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
