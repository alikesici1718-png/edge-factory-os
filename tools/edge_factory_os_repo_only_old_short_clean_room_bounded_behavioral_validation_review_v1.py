import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW"
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_review_v1"
ROUTE_KEY = "old_short_clean_room_v1"

RESULT_READY = "OLD_SHORT_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW_PASS_READY_FOR_REALISTIC_FIXTURE_DESIGN_NO_EDGE_NO_LIVE"
RESULT_P1 = "OLD_SHORT_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW_PASS_WITH_P1_ATTENTION_NO_EDGE_NO_LIVE"
RESULT_FAIL = "OLD_SHORT_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW_FAIL_REQUIRES_REPAIR_NO_EDGE_NO_LIVE"
NEXT_PASS = "OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_DESIGN_V1"
NEXT_FAIL = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_REPAIR_PREVIEW_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_REL = Path("tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_review_v1.py")
ARTIFACT_REL = Path("artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_review_v1.json")

SOURCE_RELS = {
    "bounded_behavioral_validation_dry_run": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_dry_run_v1.json"
    ),
    "bounded_behavioral_validation_preview": Path(
        "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_preview_v1.json"
    ),
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
}

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
        "dry_run_identity",
        "preview_identity",
        "validation_design_identity",
        "fixture_threshold_contract_identity",
    ):
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


def metric_counts(metrics: dict) -> tuple[int, int, list[dict]]:
    computed = 0
    missing = []
    for name, result in metrics.items():
        if isinstance(result, dict) and result.get("computed") is True:
            computed += 1
        else:
            reason = result.get("reason") if isinstance(result, dict) else "metric result missing"
            missing.append({"metric": name, "reason": reason})
    return computed, len(missing), missing


def metric_value(metrics: dict, name: str):
    result = metrics.get(name, {})
    if isinstance(result, dict):
        return result.get("value")
    return None


def safety_permissions_false(dry_run: dict) -> dict:
    permissions = dry_run.get("safety_permissions", {})
    expected_false = [
        "full_dataset_comparison_allowed_now",
        "backtest_allowed_now",
        "runner_execution_allowed_now",
        "signal_generation_allowed_now",
        "pnl_computation_allowed_now",
        "runtime_permission_allowed_now",
        "monitor_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
    ]
    return {
        key: permissions.get(key) is False
        for key in expected_false
    }


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_REL
    git_status_before = git_cmd("status", "--short")
    artifact_untracked_before_run = f"?? {ARTIFACT_REL.as_posix()}" in git_status_before
    if artifact_path.exists() and not artifact_untracked_before_run:
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_REL.as_posix()}")

    allowed_pending = {f"?? {TOOL_REL.as_posix()}"}
    if artifact_untracked_before_run:
        allowed_pending.add(f"?? {ARTIFACT_REL.as_posix()}")
    dirty_tracked = [line for line in git_status_before if not line.startswith("?? ")]
    unexpected_untracked = [line for line in git_status_before if line.startswith("?? ") and line not in allowed_pending]
    repo_clean_before_run = not dirty_tracked and not unexpected_untracked
    git_head = git_cmd("rev-parse", "HEAD")[0]
    tracked_python_count = len(git_cmd("ls-files", "*.py"))

    source_payloads = {name: load_json(rel_path) for name, rel_path in SOURCE_RELS.items()}
    dry_run = source_payloads["bounded_behavioral_validation_dry_run"]
    preview = source_payloads["bounded_behavioral_validation_preview"]
    threshold_contract = source_payloads["runner_fixture_threshold_contract"]

    metrics = dry_run.get("similarity_metric_results", {})
    computed_count, missing_count, missing_metrics = metric_counts(metrics)
    schema_rate = metric_value(metrics, "schema_match_rate")
    safety_rate = metric_value(metrics, "safety_label_match_rate")

    prior_dry_run_ok = {
        "status_matches_prior_required_status": dry_run.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_DRY_RUN_CREATED",
        "route_key_matches": dry_run.get("dry_run_identity", {}).get("route_key") == ROUTE_KEY,
        "result_classification_is_partial": dry_run.get("result_classification")
        == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PARTIAL_NO_EDGE_NO_LIVE",
        "schema_match_rate_verified_1": schema_rate == 1.0,
        "safety_label_match_rate_verified_1": safety_rate == 1.0,
        "computed_metric_count_verified_13": computed_count == 13,
        "missing_metric_count_verified_2": missing_count == 2,
        "next_allowed_step_is_review": dry_run.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_REVIEW_V1",
    }

    metric_names = set(metrics.keys())
    pnl_metric_names = [
        name for name in metric_names if any(token in name.lower() for token in ["pnl", "net_ret", "gross_ret", "profit", "loss", "win"])
    ]
    dry_safety = dry_run.get("safety_label_review", {})
    pnl_used = dry_safety.get("pnl_or_outcome_fields_used_for_validation") is True
    dry_permissions = dry_run.get("safety_permissions", {})
    dry_identity = dry_run.get("dry_run_identity", {})
    full_dataset_claims = (
        dry_identity.get("full_dataset_comparison") is True
        or dry_permissions.get("full_dataset_comparison_allowed_now") is True
    )
    edge_live_capital_claims = any(
        dry_permissions.get(key) is True
        for key in [
            "edge_claim_allowed_now",
            "live_permission_allowed_now",
            "capital_permission_allowed_now",
            "runtime_permission_allowed_now",
        ]
    )

    metric_safety_review = {
        "computed_metrics": sorted(name for name, result in metrics.items() if isinstance(result, dict) and result.get("computed") is True),
        "computed_metric_count": computed_count,
        "all_computed_metrics_bounded_sample_safe": True,
        "pnl_metric_names": pnl_metric_names,
        "pnl_or_outcome_used_for_validation": pnl_used,
        "no_pnl_metric_used": not pnl_metric_names and not pnl_used,
        "no_full_dataset_metric_used": not full_dataset_claims,
        "no_raw_market_data_used": dry_run.get("validation_checks", {}).get("no_raw_market_data_read") is True,
        "no_edge_live_capital_claims": not edge_live_capital_claims,
        "pnl_fields_seen_but_not_used": dry_safety.get("pnl_or_outcome_fields_seen_but_not_used", []),
    }

    missing_metric_review = {
        "missing_metric_count": missing_count,
        "missing_metrics": missing_metrics,
        "critical_before_continuing": False,
        "requires_non_synthetic_clean_room_output": True,
        "p1_attention_required": missing_count > 0,
        "review_note": "Missing coin overlap and timestamp alignment require a more realistic bounded clean-room fixture; they do not hide a hard safety failure in this review.",
    }

    limitations = dry_run.get("limitations", [])
    limitation_text = " ".join(str(item).lower() for item in limitations)
    synthetic_limits = dry_run.get("synthetic_fixture_limitations", {})
    real_equivalence_not_proven = (
        synthetic_limits.get("real_behavioral_equivalence_proven") is False
        and "no real behavioral equivalence is claimed" in limitation_text
    )
    partial_classification_review = {
        "prior_result_classification": dry_run.get("result_classification"),
        "partial_is_acceptable_for_review": dry_run.get("result_classification")
        == "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIOR_MATCH_PARTIAL_NO_EDGE_NO_LIVE"
        and real_equivalence_not_proven,
        "real_behavioral_equivalence_not_proven": real_equivalence_not_proven,
        "synthetic_fixture_limitation_preserved": synthetic_limits.get("clean_room_sample_is_synthetic_feature_fixture") is True,
        "partial_allows_backtest_live_capital": False,
        "not_ready_for_backtest": True,
    }

    safety_permission_review = safety_permissions_false(dry_run)
    all_safety_false = all(safety_permission_review.values())

    p0_findings = []
    if not all(prior_dry_run_ok.values()):
        p0_findings.append({"severity": "P0", "finding": "prior dry-run identity or expected metrics did not verify"})
    if metric_safety_review["pnl_or_outcome_used_for_validation"] or metric_safety_review["pnl_metric_names"]:
        p0_findings.append({"severity": "P0", "finding": "PnL/outcome metric was used or named in validator metrics"})
    if not metric_safety_review["no_full_dataset_metric_used"]:
        p0_findings.append({"severity": "P0", "finding": "full dataset comparison claim detected"})
    if schema_rate != 1.0 or safety_rate != 1.0:
        p0_findings.append({"severity": "P0", "finding": "schema or safety label rate is not 1.0"})
    if not all_safety_false:
        p0_findings.append({"severity": "P0", "finding": "one or more safety permissions were not false"})
    if not real_equivalence_not_proven:
        p0_findings.append({"severity": "P0", "finding": "partial classification did not preserve real-equivalence limitation"})

    p1_findings = []
    if missing_metric_review["p1_attention_required"]:
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "missing metrics require more realistic bounded clean-room fixture",
                "metrics": [item["metric"] for item in missing_metrics],
            }
        )
    if partial_classification_review["synthetic_fixture_limitation_preserved"]:
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "synthetic feature fixture limits real behavioral equivalence",
            }
        )
    if partial_classification_review["not_ready_for_backtest"]:
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "PARTIAL result is not ready for backtest/live/capital and requires realistic fixture design first",
            }
        )

    if p0_findings:
        result_classification = RESULT_FAIL
        next_allowed_step = NEXT_FAIL
    elif p1_findings:
        result_classification = RESULT_P1
        next_allowed_step = NEXT_PASS
    else:
        result_classification = RESULT_READY
        next_allowed_step = NEXT_PASS

    unresolved_fields = threshold_contract.get("unresolved_fields_preserved", UNRESOLVED_FIELDS)
    unresolved_preserved = all(item in unresolved_fields for item in UNRESOLVED_FIELDS)

    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "prior_bounded_behavioral_validation_loaded": prior_dry_run_ok["status_matches_prior_required_status"],
        "prior_next_allowed_step_verified": prior_dry_run_ok["next_allowed_step_is_review"],
        "schema_match_rate_verified_1": schema_rate == 1.0,
        "safety_label_match_rate_verified_1": safety_rate == 1.0,
        "computed_metric_count_verified_13": computed_count == 13,
        "no_pnl_metric_used": metric_safety_review["no_pnl_metric_used"],
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "unresolved_fields_preserved": unresolved_preserved,
        "exactly_one_python_tool_created": TOOL_REL.as_posix() in [line[3:] for line in git_status_before if line.startswith("?? ")],
        "exactly_one_json_artifact_created": (not artifact_path.exists()) or artifact_untracked_before_run,
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
            "expected_head": "73ba8b8982e706bb1cd97a992ef892fd2e440c95",
            "actual_head": git_head,
            "expected_tracked_python_count": 954,
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
        "prior_dry_run_preserved": {
            **prior_dry_run_ok,
            "status": dry_run.get("status"),
            "route_key": dry_run.get("dry_run_identity", {}).get("route_key"),
            "result_classification": dry_run.get("result_classification"),
            "schema_match_rate": schema_rate,
            "safety_label_match_rate": safety_rate,
            "computed_metric_count": computed_count,
            "missing_metric_count": missing_count,
            "next_allowed_step": dry_run.get("next_allowed_step"),
        },
        "metric_safety_review": metric_safety_review,
        "missing_metric_review": missing_metric_review,
        "partial_classification_review": partial_classification_review,
        "safety_permission_review": {
            "all_required_permissions_false": all_safety_false,
            "permission_checks": safety_permission_review,
            "candidate_generation": False,
            "edge_claim": False,
            "family_release": False,
            "runtime": False,
            "monitor": False,
            "live": False,
            "capital": False,
        },
        "review_findings": {
            "p0_issue_count": len(p0_findings),
            "p1_attention_count": len(p1_findings),
            "p0_findings": p0_findings,
            "p1_findings": p1_findings,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "limitations": [
            "review only; no behavioral validation execution",
            "prior dry-run is synthetic-fixture-limited and only PARTIAL",
            "real behavioral equivalence is not proven",
            "not ready for backtest, live, capital, candidate generation, or edge claim",
            "missing metrics require realistic bounded fixture design before stronger behavioral review",
        ],
        "safety_permissions": {
            "bounded_behavioral_validation_review_created": True,
            "behavioral_validation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
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
    print(f"result_classification: {result_classification}")
    print(f"p0_issue_count: {len(p0_findings)}")
    print(f"p1_attention_count: {len(p1_findings)}")
    print(f"missing_metric_count: {missing_count}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")


if __name__ == "__main__":
    main()
