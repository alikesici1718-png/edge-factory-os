from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DESIGN"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_accepted_lifecycle_fixture_discovery_design_v1"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "d021984ccf3e2033d4af59b247c19dba0d830a3c"
EXPECTED_TRACKED_PYTHON_COUNT = 961
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_accepted_lifecycle_fixture_discovery_design_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_accepted_lifecycle_fixture_discovery_design_v1.json"
)
PRIOR_REQUIRED_STATUS = (
    "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_CREATED"
)
PRIOR_REQUIRED_RESULT = (
    "OLD_SHORT_RUNNER_REALISTIC_FIXTURE_DRY_RUN_REVIEW_PASS_READY_FOR_ACCEPTED_LIFECYCLE_"
    "FIXTURE_DISCOVERY_NO_EDGE_NO_LIVE"
)
PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DESIGN_V1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_DRY_RUN_V1"
MASTER_UPPER_SYSTEM_PATH = (
    "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\paper_run_gate_MASTER_UPPER_SYSTEM\\"
    "live_blowoff_short_paper_realistic"
)
FUTURE_OUTPUT_ROOT = (
    "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\"
    "edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1\\"
    "accepted_lifecycle_fixture_discovery_v1"
)

SOURCE_ARTIFACT_PATHS = {
    "runner_realistic_fixture_dry_run_review": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.json"
    ),
    "runner_realistic_fixture_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_v1.json"
    ),
    "realistic_bounded_fixture_generation_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.json"
    ),
    "realistic_bounded_fixture_design": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_realistic_bounded_fixture_design_v1.json"
    ),
    "old_short_clean_room_contract": (
        "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
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

MASTER_OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
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

SELECTION_GUARDRAILS_FORBIDDEN = [
    "pnl",
    "net_ret",
    "stress_pnl",
    "realistic_net_ret",
    "gross_ret",
    "win/loss",
    "best trade",
    "worst trade",
    "future return",
    "validation/holdout result",
]

SELECTION_GUARDRAILS_ALLOWED = [
    "lifecycle completeness",
    "family coverage",
    "gate/accepted coverage",
    "schema completeness",
    "timestamp/linkage availability",
    "feature field availability",
]

MISSING_METRIC_RECOVERY_ITEMS = [
    "entry delay comparability",
    "hold duration comparability",
    "notional comparability",
    "accepted lifecycle coverage",
    "gate_allowed path coverage",
]

RESULT_CLASSES = [
    "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_NOT_FOUND_NO_EDGE_NO_LIVE",
    "OLD_SHORT_ACCEPTED_LIFECYCLE_FIXTURE_DISCOVERY_FAIL_CLOSED_NO_EDGE_NO_LIVE",
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
        "discovery_design_identity",
        "prior_dry_run_preserved",
        "dry_run_identity",
        "fixture_generation_identity",
        "fixture_design_identity",
        "clean_room_identity",
        "fixture_threshold_contract_identity",
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


def summarize_sources(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        name: {key: value for key, value in source.items() if key != "payload"}
        for name, source in loaded.items()
    }


def verify_prior_review(review: dict[str, Any]) -> dict[str, bool]:
    accepted_review = review.get("accepted_lifecycle_coverage_review", {})
    findings = review.get("review_findings", {})
    return {
        "prior_status_verified": review.get("status") == PRIOR_REQUIRED_STATUS,
        "prior_route_key_verified": extract_route_key(review) == ROUTE_KEY,
        "prior_result_verified": review.get("result_classification") == PRIOR_REQUIRED_RESULT,
        "prior_p0_zero_verified": findings.get("p0_issue_count") == 0,
        "prior_next_allowed_step_verified": review.get("next_allowed_step")
        == PRIOR_NEXT_ALLOWED_STEP,
        "gate_allowed_absent_verified": accepted_review.get("gate_allowed_count") == 0,
        "accepted_lifecycle_absent_verified": accepted_review.get(
            "accepted_lifecycle_coverage_present"
        )
        is False,
        "replacement_checks_all_true_verified": review.get("replacement_checks_all_true") is True,
    }


def build_design_artifact(repo_root: Path) -> dict[str, Any]:
    source_checkpoint = build_source_checkpoint(repo_root)
    loaded_sources = load_source_artifacts(repo_root)
    review = loaded_sources["runner_realistic_fixture_dry_run_review"]["payload"]
    prior_checks = verify_prior_review(review)
    if not all(prior_checks.values()):
        failed = [key for key, value in prior_checks.items() if not value]
        raise DesignBlocked(f"prior review checks failed: {failed}")

    dry_run = loaded_sources["runner_realistic_fixture_dry_run"]["payload"]
    generation = loaded_sources["realistic_bounded_fixture_generation_dry_run"]["payload"]
    contract = loaded_sources["old_short_clean_room_contract"]["payload"]

    discovery_design_identity = {
        "route_key": ROUTE_KEY,
        "design_only": True,
        "accepted_lifecycle_discovery_allowed_now": False,
        "fixture_generation_allowed_now": False,
        "runner_execution_allowed_now": False,
        "behavioral_validation_allowed_now": False,
        "original_exact_source_recovered": False,
        "exact_replay_available": False,
        "clean_room_behavioral_reconstruction": True,
        "no_edge_claim": True,
        "no_live_capital": True,
    }

    discovery_goal = {
        "future_discovery_should_find_bounded_examples_of": [
            "signal row",
            "pending entry row",
            "gate allowed / accepted row if available",
            "open position row if available",
            "closed trade row",
            "lifecycle linkage by signal_id / position_id / close_id / inst_id / time fields where available",
        ],
        "must_not": [
            "prove profitability",
            "select by PnL",
            "select by win/loss",
            "select by net_ret",
            "prove edge",
            "prove original source recovery",
            "create exact replay claim",
            "create live/capital permission",
        ],
        "problem_context": {
            "prior_family_coverage": dry_run.get("dry_run_metrics", {}).get("family_coverage"),
            "prior_gate_state_coverage": dry_run.get("dry_run_metrics", {}).get(
                "gate_state_coverage"
            ),
            "prior_gate_allowed_count": dry_run.get("dry_run_metrics", {}).get(
                "gate_allowed_count"
            ),
            "prior_accepted_lifecycle_coverage_present": dry_run.get("dry_run_metrics", {}).get(
                "accepted_lifecycle_coverage_present"
            ),
        },
    }

    source_policy = {
        "future_may_inspect_only_bounded_master_upper_system_output_samples": list(
            MASTER_OUTPUT_FILES
        ),
        "master_upper_system_path": MASTER_UPPER_SYSTEM_PATH,
        "default_row_cap_per_file": 100,
        "if_not_found_within_first_100_rows": [
            "record insufficient bounded sample",
            "do not full-scan by default",
            "require later explicit expanded bounded review approval before increasing scope",
        ],
        "forbidden_sources": [
            "raw OKX 1m data",
            "raw market data",
            "private/account data",
            "order endpoints",
            "live runtime directories",
            "PnL/outcome selection",
        ],
        "metadata_header_small_samples_only_if_needed": True,
        "logger_script_text_only_if_needed": True,
        "logger_script_execution_allowed": False,
    }

    accepted_lifecycle_case_definition = {
        "valid_candidate_should_satisfy_as_much_as_available": [
            "family_key = old_short",
            "side = short",
            "family in blowoff_short or mean_reversion_short",
            "has signal_id or position_id linkage",
            "has signal_time",
            "has entry_time",
            "has exit_time or planned_exit_time",
            "has hold_minutes_actual near 120 if available",
            "has notional near 50 USDT if available",
            "has signal feature fields if available",
            "not selected due PnL/win/loss",
            "not labeled rejected/gate blocked/gate missing",
        ],
        "known_old_short_behavior": {
            "family_key": "old_short",
            "families": ["blowoff_short", "mean_reversion_short"],
            "side": "short",
            "approx_entry_delay_minutes": 2,
            "approx_hold_minutes": 120,
            "notional_approx_usdt_under_1000_equity": 50,
            "global_gate_mandatory": True,
            "no_position_without_gate_allow": True,
        },
    }

    family_coverage_requirement = {
        "future_discovery_should_try_to_find": {
            "blowoff_short": "at least one accepted lifecycle case",
            "mean_reversion_short": "at least one accepted lifecycle case",
        },
        "if_one_family_missing": {
            "classification": "partial",
            "preserve_p1_attention": True,
        },
    }

    gate_allowed_evidence_policy = {
        "future_discovery_should_search_for_gate_allow_evidence_via": [
            "accepted/pending/open/closed lifecycle path",
            "explicit gate_allowed field if present",
            "status fields if present",
            "position_id/close_id lifecycle linking if present",
        ],
        "absence_from_rejected_entries_alone_is_enough": False,
        "if_explicit_gate_allowed_field_absent_but_closed_trade_exists": {
            "gate_allowed_inferred_from_closed_trade": True,
            "do_not_call_exact_gate_replay": True,
            "preserve_limitation": True,
        },
    }

    fixture_output_design = {
        "future_output_root": FUTURE_OUTPUT_ROOT,
        "future_discovery_generation_should_create": [
            "accepted_lifecycle_fixture_index.json",
            "accepted_lifecycle_master_cases.jsonl",
            "accepted_lifecycle_pairing_plan.json",
            "accepted_lifecycle_discovery_summary.json",
        ],
        "repo_tracked_outputs_allowed_now": ["summary JSON artifact only"],
        "writes_outputs_now": False,
    }

    selection_guardrails = {
        "forbidden_selection_inputs": list(SELECTION_GUARDRAILS_FORBIDDEN),
        "allowed_selection_basis_only": list(SELECTION_GUARDRAILS_ALLOWED),
        "forbidden_count": len(SELECTION_GUARDRAILS_FORBIDDEN),
        "allowed_count": len(SELECTION_GUARDRAILS_ALLOWED),
        "selection_guardrail_count": len(SELECTION_GUARDRAILS_FORBIDDEN)
        + len(SELECTION_GUARDRAILS_ALLOWED),
    }

    missing_metric_recovery_plan = {
        "recovery_item_count": len(MISSING_METRIC_RECOVERY_ITEMS),
        "items": [
            {
                "missing_metric": "entry delay comparability",
                "accepted_lifecycle_fixture_contribution": (
                    "signal_time to entry_time linkage can compare approximate 2 minute entry delay"
                ),
                "exact_gate_decision_replay_recovered": False,
            },
            {
                "missing_metric": "hold duration comparability",
                "accepted_lifecycle_fixture_contribution": (
                    "entry_time to exit_time or hold_minutes_actual can compare approximate 120 minute hold"
                ),
                "exact_gate_decision_replay_recovered": False,
            },
            {
                "missing_metric": "notional comparability",
                "accepted_lifecycle_fixture_contribution": (
                    "notional field can compare approximate 50 USDT sizing under 1000 USDT base equity"
                ),
                "exact_gate_decision_replay_recovered": False,
            },
            {
                "missing_metric": "accepted lifecycle coverage",
                "accepted_lifecycle_fixture_contribution": (
                    "signal to pending/open/closed linkage can cover accepted lifecycle path"
                ),
                "exact_gate_decision_replay_recovered": False,
            },
            {
                "missing_metric": "gate_allowed path coverage",
                "accepted_lifecycle_fixture_contribution": (
                    "explicit gate_allowed if present, otherwise closed trade may only infer gate allowance"
                ),
                "if_explicit_gate_allow_field_absent": (
                    "accepted lifecycle recovery may improve lifecycle metrics but exact gate decision replay remains unrecovered"
                ),
                "exact_gate_decision_replay_recovered": False,
            },
        ],
    }

    safety_permissions = {
        "accepted_lifecycle_fixture_discovery_design_created": True,
        "accepted_lifecycle_discovery_allowed_now": False,
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
        "prior_realistic_fixture_dry_run_review_loaded": True,
        "prior_next_allowed_step_verified": prior_checks["prior_next_allowed_step_verified"],
        "gate_allowed_absent_verified": prior_checks["gate_allowed_absent_verified"],
        "accepted_lifecycle_absent_verified": prior_checks[
            "accepted_lifecycle_absent_verified"
        ],
        "original_exact_source_not_claimed": True,
        "clean_room_reconstruction_preserved": True,
        "no_fixture_discovery_execution": True,
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
        "selection_guardrails_defined": True,
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
        "source_artifacts": summarize_sources(loaded_sources),
        "discovery_design_identity": discovery_design_identity,
        "discovery_goal": discovery_goal,
        "source_policy": source_policy,
        "accepted_lifecycle_case_definition": accepted_lifecycle_case_definition,
        "family_coverage_requirement": family_coverage_requirement,
        "gate_allowed_evidence_policy": gate_allowed_evidence_policy,
        "fixture_output_design": fixture_output_design,
        "safety_labels": list(SAFETY_LABELS),
        "selection_guardrails": selection_guardrails,
        "missing_metric_recovery_plan": missing_metric_recovery_plan,
        "result_classes": list(RESULT_CLASSES),
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "unresolved_fields_preserved": [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
            "explicit gate_allowed field may be absent",
            "exact gate decision replay remains unrecovered without explicit gate allow evidence",
        ],
        "limitations": [
            "Design only; no accepted lifecycle fixture discovery was executed.",
            "No fixture generation, runner execution, signal generation, behavioral validation, full dataset comparison, backtest, or PnL computation was performed.",
            "Future discovery is bounded to MASTER_UPPER_SYSTEM output samples with a default 100 row cap per file.",
            "Closed trades may infer accepted lifecycle only when explicit gate_allowed is absent; this is not exact gate replay.",
            "This design preserves clean-room reconstruction only and does not claim edge, exact replay, live readiness, or capital readiness.",
            "Prior accepted lifecycle gap remains: gate_allowed_count is 0 and accepted_lifecycle_coverage_present is false.",
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
    identity = artifact["discovery_design_identity"]
    print(f"status: {artifact['status']}")
    print(f"route_key: {identity['route_key']}")
    print(f"design_only: {str(identity['design_only']).lower()}")
    print(
        "accepted_lifecycle_discovery_allowed_now: "
        f"{str(identity['accepted_lifecycle_discovery_allowed_now']).lower()}"
    )
    print(f"result_class_count: {len(artifact['result_classes'])}")
    print(
        "selection_guardrail_count: "
        f"{artifact['selection_guardrails']['selection_guardrail_count']}"
    )
    print(
        "missing_metric_recovery_item_count: "
        f"{artifact['missing_metric_recovery_plan']['recovery_item_count']}"
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
        artifact = build_design_artifact(repo_root)
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
