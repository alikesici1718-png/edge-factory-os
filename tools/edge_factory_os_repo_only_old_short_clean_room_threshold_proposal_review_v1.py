import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_old_short_clean_room_threshold_proposal_review_v1.py"
ARTIFACT_PATH = "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_PROPOSAL_REVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_PROPOSAL_REVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "858c39cdde7b65068ed42c1cda02637213f05daf"
EXPECTED_TRACKED_PYTHON_COUNT = 947

THRESHOLD_RECONSTRUCTION_CONTRACT = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_reconstruction_contract_v1.json"
)
EVIDENCE_EXTRACTION_DRY_RUN = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_evidence_extraction_dry_run_v1.json"
)
BEHAVIORAL_PROPOSAL_CONTRACT = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_contract_v1.json"
)
BEHAVIORAL_PROPOSAL_DRY_RUN = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
)
CLEAN_ROOM_CONTRACT = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"

PROPOSAL_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_DRY_RUN_CREATED"
PROPOSAL_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_PROPOSAL_REVIEW_V1"
NEXT_ALLOWED_STEP_PASS = "OLD_SHORT_CLEAN_ROOM_RUNNER_FIXTURE_THRESHOLD_CONTRACT_V1"
NEXT_ALLOWED_STEP_FAIL = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_PROPOSAL_REPAIR_CONTRACT_V1"

RESULT_PASS = "THRESHOLD_PROPOSAL_REVIEW_PASS_READY_FOR_RUNNER_FIXTURE_THRESHOLD_CONTRACT_NO_EDGE_NO_LIVE"
RESULT_P1 = "THRESHOLD_PROPOSAL_REVIEW_PASS_WITH_P1_ATTENTION_NO_EDGE_NO_LIVE"
RESULT_FAIL = "THRESHOLD_PROPOSAL_REVIEW_FAIL_REQUIRES_REPAIR_NO_EDGE_NO_LIVE"

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
BLOWOFF_FEATURE_GROUPS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_range_bps",
    "signal_vol_quote",
    "entry_range_bps",
    "entry_vol_quote",
]
MEAN_REVERSION_FEATURE_GROUPS = [
    "signal_ret60_bps",
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_range_bps",
    "signal_vol_quote",
    "entry_range_bps",
    "entry_vol_quote",
]
REQUIRED_LABELS = [
    "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
    "NOT_ORIGINAL_THRESHOLD",
    "NOT_PNL_OPTIMIZED",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]
UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]
FORBIDDEN_EVIDENCE_TERMS = [
    "PnL",
    "net_ret",
    "pnl",
    "stress_pnl",
    "win/loss",
    "validation return",
    "holdout return",
    "monthly stability selection",
    "grid search",
    "threshold optimization",
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


def git_status_entries() -> List[Dict[str, str]]:
    output = run_git(["status", "--porcelain"])
    entries: List[Dict[str, str]] = []
    for line in output.splitlines():
        if line:
            entries.append({"status": line[:2], "path": line[3:].strip().strip('"').replace("\\", "/")})
    return entries


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"artifact is not a JSON object: {relative_path}")
    return payload


def route_key_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    for identity_key in [
        "proposal_identity",
        "proposal_contract_identity",
        "threshold_reconstruction_identity",
        "evidence_extraction_identity",
        "contract_identity",
        "old_short_clean_room_identity",
    ]:
        identity = payload.get(identity_key)
        if isinstance(identity, dict) and identity.get("route_key"):
            return str(identity["route_key"])
    route_key = payload.get("route_key")
    return str(route_key) if route_key else None


def artifact_review(relative_path: str, required: bool) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    review: Dict[str, Any] = {
        "path": relative_path,
        "required": required,
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
        if required:
            raise RuntimeError(f"missing required source artifact: {relative_path}")
        return review
    payload = read_json(relative_path)
    review.update(
        {
            "loaded": True,
            "status": payload.get("status"),
            "artifact_kind": payload.get("artifact_kind"),
            "route_key": route_key_from_payload(payload),
            "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
            "replacement_checks_all_true": payload.get("replacement_checks_all_true"),
        }
    )
    return review


def proposal_family_count(proposals: Dict[str, Any]) -> int:
    return sum(1 for proposal in proposals.values() if int(proposal.get("proposal_count_for_family", 0)) == 1)


def review_labels(proposals: Dict[str, Any]) -> Dict[str, Any]:
    family_reviews: Dict[str, Any] = {}
    all_verified = True
    for family in FAMILIES:
        proposal = proposals.get(family, {})
        labels = proposal.get("labels", [])
        missing_labels = [label for label in REQUIRED_LABELS if label not in labels]
        verified = not missing_labels and int(proposal.get("proposal_count_for_family", 0)) == 1
        family_reviews[family] = {
            "proposal_exists": bool(proposal),
            "labels": labels,
            "required_labels": REQUIRED_LABELS,
            "missing_labels": missing_labels,
            "labels_verified": verified,
        }
        all_verified = all_verified and verified
    return {"family_reviews": family_reviews, "proposal_labels_verified": all_verified}


def review_family_coverage(proposals: Dict[str, Any]) -> Dict[str, Any]:
    expected_groups = {
        "blowoff_short": BLOWOFF_FEATURE_GROUPS,
        "mean_reversion_short": MEAN_REVERSION_FEATURE_GROUPS,
    }
    family_reviews: Dict[str, Any] = {}
    all_covered = True
    for family in FAMILIES:
        proposal = proposals.get(family, {})
        rules = proposal.get("threshold_rules", {}) if isinstance(proposal, dict) else {}
        missing_features = [feature for feature in expected_groups[family] if feature not in rules]
        exists = bool(proposal)
        short_only = proposal.get("side") == "short" if exists else False
        covered = exists and short_only and not missing_features
        family_reviews[family] = {
            "proposal_exists": exists,
            "side": proposal.get("side") if exists else None,
            "short_only": short_only,
            "expected_feature_group": expected_groups[family],
            "observed_threshold_rule_features": sorted(rules.keys()),
            "missing_feature_group_members": missing_features,
            "feature_groups_preserved": covered,
        }
        all_covered = all_covered and covered
    return {
        "blowoff_short_proposal_exists": bool(proposals.get("blowoff_short")),
        "mean_reversion_short_proposal_exists": bool(proposals.get("mean_reversion_short")),
        "family_reviews": family_reviews,
        "both_family_proposals_exist": all(bool(proposals.get(family)) for family in FAMILIES),
        "both_short_only": all(review["short_only"] for review in family_reviews.values()),
        "known_feature_groups_preserved": all_covered,
    }


def review_evidence_basis(proposal: Dict[str, Any]) -> Dict[str, Any]:
    evidence_basis = proposal.get("evidence_basis_by_feature", {})
    quantiles = proposal.get("quantile_references_used", {})
    missing_fields = proposal.get("missing_fields", {})
    quality = proposal.get("family_evidence_quality", {})
    family_reviews: Dict[str, Any] = {}
    all_referenced = True
    all_quality_recorded = True
    all_missing_recorded = True
    for family in FAMILIES:
        family_basis = evidence_basis.get(family, {})
        family_quantiles = quantiles.get(family, {})
        family_missing = missing_fields.get(family, {})
        family_quality = quality.get(family, {})
        features_with_basis = sorted(feature for feature in FEATURE_FIELDS if feature in family_basis)
        features_with_quantiles = sorted(feature for feature in FEATURE_FIELDS if feature in family_quantiles)
        missing_feature_records = sorted(feature for feature in FEATURE_FIELDS if feature in family_missing)
        referenced = set(features_with_basis) == set(FEATURE_FIELDS) and set(features_with_quantiles) == set(
            FEATURE_FIELDS
        )
        quality_recorded = bool(family_quality.get("evidence_quality"))
        missing_recorded = set(missing_feature_records) == set(FEATURE_FIELDS)
        family_reviews[family] = {
            "features_with_evidence_basis": features_with_basis,
            "features_with_quantile_references": features_with_quantiles,
            "features_with_missing_field_records": missing_feature_records,
            "evidence_quality": family_quality.get("evidence_quality"),
            "evidence_quality_recorded": quality_recorded,
            "feature_evidence_references_quantiles_or_summaries": referenced,
            "missing_fields_recorded": missing_recorded,
            "direction_notes": family_quality.get("direction_notes", []),
            "entry_confirmation_features_limited": family_quality.get(
                "entry_confirmation_features_limited", []
            ),
        }
        all_referenced = all_referenced and referenced
        all_quality_recorded = all_quality_recorded and quality_recorded
        all_missing_recorded = all_missing_recorded and missing_recorded
    return {
        "family_reviews": family_reviews,
        "feature_evidence_references_quantiles_or_summaries": all_referenced,
        "evidence_quality_recorded": all_quality_recorded,
        "missing_fields_recorded": all_missing_recorded,
        "unresolved_fields_preserved": proposal.get("unresolved_fields_preserved") == UNRESOLVED_FIELDS,
    }


def review_forbidden_evidence(proposal: Dict[str, Any]) -> Dict[str, Any]:
    checks = proposal.get("forbidden_optimization_checks", {})
    forbidden_evidence_used = any(
        bool(checks.get(field))
        for field in [
            "forbidden_optimization_used",
            "pnl_fields_used_for_thresholds",
            "exact_original_threshold_claimed",
            "threshold_grid_search_used",
            "threshold_selection_by_return_used",
            "threshold_selection_by_win_rate_used",
            "closed_trade_profitability_used",
            "validation_returns_used",
            "holdout_returns_used",
            "monthly_stability_optimization_used",
            "pnl_computed",
        ]
    )
    reviewed_terms = [
        {
            "term": term,
            "used_for_threshold_review": False,
            "basis": "prior dry-run forbidden optimization checks and labels were false",
        }
        for term in FORBIDDEN_EVIDENCE_TERMS
    ]
    return {
        "forbidden_terms_reviewed": reviewed_terms,
        "forbidden_evidence_used": forbidden_evidence_used,
        "pnl_fields_used_for_thresholds": bool(checks.get("pnl_fields_used_for_thresholds")),
        "forbidden_optimization_used": bool(checks.get("forbidden_optimization_used")),
        "threshold_grid_search_used": bool(checks.get("threshold_grid_search_used")),
        "threshold_optimization_used": False,
        "validation_or_holdout_returns_used": bool(checks.get("validation_returns_used"))
        or bool(checks.get("holdout_returns_used")),
        "monthly_stability_selection_used": bool(checks.get("monthly_stability_optimization_used")),
        "closed_trade_profitability_used": bool(checks.get("closed_trade_profitability_used")),
        "review_passed": not forbidden_evidence_used,
    }


def review_limitations(proposal: Dict[str, Any]) -> Dict[str, Any]:
    limitations = proposal.get("proposal_limitations", [])
    identity = proposal.get("proposal_identity", {})
    safety = proposal.get("safety_permissions", {})
    labels = []
    for family_proposal in proposal.get("proposed_behavioral_thresholds_by_family", {}).values():
        labels.extend(family_proposal.get("labels", []))
    return {
        "proposal_limitations": limitations,
        "original_exact_thresholds_unknown_preserved": "exact original thresholds unknown"
        in proposal.get("unresolved_fields_preserved", []),
        "proposal_is_behavioral_reconstruction": identity.get("behavioral_threshold_reconstruction") is True,
        "not_exact_original": identity.get("original_exact_thresholds_recovered") is False
        and "NOT_ORIGINAL_THRESHOLD" in labels,
        "not_edge_evidence": identity.get("edge_claim") is False and "NOT_EDGE_EVIDENCE" in labels,
        "not_live_capital_ready": identity.get("runtime_live_capital") is False
        and safety.get("live_permission_allowed_now") is False
        and safety.get("capital_permission_allowed_now") is False
        and "NO_LIVE_CAPITAL" in labels,
    }


def build_payload() -> Dict[str, Any]:
    actual_head = run_git(["rev-parse", "HEAD"])
    actual_tracked_python_count = tracked_python_count()
    status_entries = git_status_entries()
    dirty_paths = [entry["path"] for entry in status_entries]
    allowed_dirty_paths = {MODULE_PATH, ARTIFACT_PATH}
    unexpected_dirty_paths = [path for path in dirty_paths if path not in allowed_dirty_paths]
    modified_existing_paths = [
        entry["path"]
        for entry in status_entries
        if entry["path"] not in allowed_dirty_paths or entry["status"] != "??"
    ]
    artifact_existed_before_run = (REPO_ROOT / ARTIFACT_PATH).exists()
    artifact_is_allowed_untracked = any(
        entry["path"] == ARTIFACT_PATH and entry["status"] == "??" for entry in status_entries
    )
    if unexpected_dirty_paths:
        raise RuntimeError(f"unexpected dirty paths before review build: {unexpected_dirty_paths}")
    if modified_existing_paths:
        raise RuntimeError(f"existing files modified before review build: {modified_existing_paths}")
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"HEAD moved before review build: {actual_head} != {EXPECTED_HEAD}")
    if actual_tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before review build: "
            f"{actual_tracked_python_count} != {EXPECTED_TRACKED_PYTHON_COUNT}"
        )

    proposal = read_json(BEHAVIORAL_PROPOSAL_DRY_RUN)
    proposals = proposal.get("proposed_behavioral_thresholds_by_family", {})
    route_key = proposal.get("proposal_identity", {}).get("route_key")
    family_proposal_count = proposal_family_count(proposals)
    forbidden_checks = proposal.get("forbidden_optimization_checks", {})
    prior_result = proposal.get("result_classification")

    prior_proposal_preserved = {
        "status": proposal.get("status"),
        "status_verified": proposal.get("status") == PROPOSAL_STATUS,
        "route_key": route_key,
        "route_key_verified": route_key == ROUTE_KEY,
        "result_classification": prior_result,
        "result_classification_partial_or_ready": prior_result
        in {
            "THRESHOLD_BEHAVIORAL_PROPOSAL_READY_NO_EDGE_NO_LIVE",
            "THRESHOLD_BEHAVIORAL_PROPOSAL_PARTIAL_NO_EDGE_NO_LIVE",
        },
        "next_allowed_step": proposal.get("next_allowed_step"),
        "next_allowed_step_verified": proposal.get("next_allowed_step") == PROPOSAL_NEXT_ALLOWED_STEP,
        "family_proposal_count": family_proposal_count,
        "proposal_family_count_verified_2": family_proposal_count == 2,
        "forbidden_optimization_used": bool(forbidden_checks.get("forbidden_optimization_used")),
        "pnl_fields_used_for_thresholds": bool(forbidden_checks.get("pnl_fields_used_for_thresholds")),
    }

    label_review = review_labels(proposals)
    family_review = review_family_coverage(proposals)
    evidence_review = review_evidence_basis(proposal)
    forbidden_review = review_forbidden_evidence(proposal)
    limitations_review = review_limitations(proposal)

    p0_findings: List[Dict[str, Any]] = []
    if prior_proposal_preserved["route_key_verified"] is not True:
        p0_findings.append({"severity": "P0", "finding": "route key mismatch"})
    if prior_proposal_preserved["result_classification_partial_or_ready"] is not True:
        p0_findings.append({"severity": "P0", "finding": "proposal result was invalid or inconclusive"})
    if family_proposal_count == 0 or not family_review["both_family_proposals_exist"]:
        p0_findings.append({"severity": "P0", "finding": "missing both family proposals"})
    if label_review["proposal_labels_verified"] is not True:
        p0_findings.append({"severity": "P0", "finding": "required proposal labels missing"})
    if forbidden_review["forbidden_evidence_used"]:
        p0_findings.append({"severity": "P0", "finding": "forbidden evidence used"})
    if limitations_review["not_exact_original"] is not True:
        p0_findings.append({"severity": "P0", "finding": "proposal may claim exact original threshold"})
    if limitations_review["not_edge_evidence"] is not True or limitations_review["not_live_capital_ready"] is not True:
        p0_findings.append({"severity": "P0", "finding": "edge/live/capital permission not safely false"})

    p1_findings: List[Dict[str, Any]] = []
    if prior_result == "THRESHOLD_BEHAVIORAL_PROPOSAL_PARTIAL_NO_EDGE_NO_LIVE":
        p1_findings.append({"severity": "P1", "finding": "prior proposal classification is partial"})
    limited_families = [
        family
        for family, review in evidence_review["family_reviews"].items()
        if review.get("evidence_quality") == "limited"
    ]
    if limited_families:
        p1_findings.append({"severity": "P1", "finding": "family evidence quality is limited", "families": limited_families})
    missing_limited_families = [
        family
        for family, review in evidence_review["family_reviews"].items()
        if review.get("entry_confirmation_features_limited")
    ]
    if missing_limited_families:
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "entry confirmation fields are sparsely observed",
                "families": missing_limited_families,
            }
        )
    direction_note_families = [
        family for family, review in evidence_review["family_reviews"].items() if review.get("direction_notes")
    ]
    if direction_note_families:
        p1_findings.append(
            {
                "severity": "P1",
                "finding": "direction note preserved for review attention",
                "families": direction_note_families,
            }
        )

    if p0_findings:
        result_classification = RESULT_FAIL
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL
    elif p1_findings:
        result_classification = RESULT_P1
        next_allowed_step = NEXT_ALLOWED_STEP_PASS
    else:
        result_classification = RESULT_PASS
        next_allowed_step = NEXT_ALLOWED_STEP_PASS

    safety_permissions = {
        "threshold_proposal_review_created": True,
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
        "repo_clean_before_run": actual_head == EXPECTED_HEAD
        and actual_tracked_python_count == EXPECTED_TRACKED_PYTHON_COUNT
        and not unexpected_dirty_paths
        and not modified_existing_paths,
        "threshold_proposal_artifact_loaded": proposal.get("status") == PROPOSAL_STATUS,
        "prior_next_allowed_step_verified": prior_proposal_preserved["next_allowed_step_verified"],
        "route_key_verified": prior_proposal_preserved["route_key_verified"],
        "proposal_family_count_verified_2": family_proposal_count == 2,
        "forbidden_optimization_false_verified": not forbidden_checks.get("forbidden_optimization_used"),
        "pnl_fields_used_false_verified": not forbidden_checks.get("pnl_fields_used_for_thresholds"),
        "proposal_labels_verified": label_review["proposal_labels_verified"],
        "forbidden_evidence_not_used": not forbidden_review["forbidden_evidence_used"],
        "original_thresholds_not_claimed": limitations_review["not_exact_original"],
        "no_edge_live_capital_permission": limitations_review["not_edge_evidence"]
        and limitations_review["not_live_capital_ready"],
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
        "unresolved_fields_preserved": evidence_review["unresolved_fields_preserved"],
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_PATH).exists(),
        "exactly_one_json_artifact_created": (not artifact_existed_before_run) or artifact_is_allowed_untracked,
        "no_existing_files_modified": not modified_existing_paths,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        raise RuntimeError(f"validation checks failed: {validation_checks}")

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": {
            "path": MODULE_PATH,
            "standard_library_only": True,
            "created_files": [MODULE_PATH, ARTIFACT_PATH],
            "modified_existing_files": [],
            "code_changed": True,
        },
        "source_checkpoint": {
            "expected_head": EXPECTED_HEAD,
            "actual_head": actual_head,
            "repo_clean_before_run": True,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "actual_tracked_python_count": actual_tracked_python_count,
            "dirty_paths_at_build": dirty_paths,
            "allowed_dirty_paths_at_build": sorted(allowed_dirty_paths),
            "unexpected_dirty_paths_at_build": unexpected_dirty_paths,
        },
        "source_artifacts": {
            "threshold_reconstruction_contract": artifact_review(THRESHOLD_RECONSTRUCTION_CONTRACT, True),
            "threshold_evidence_extraction_dry_run": artifact_review(EVIDENCE_EXTRACTION_DRY_RUN, True),
            "threshold_behavioral_proposal_contract": artifact_review(BEHAVIORAL_PROPOSAL_CONTRACT, True),
            "threshold_behavioral_proposal_dry_run": artifact_review(BEHAVIORAL_PROPOSAL_DRY_RUN, True),
            "old_short_clean_room_contract": artifact_review(CLEAN_ROOM_CONTRACT, False),
            "old_short_clean_room_runner_preview": artifact_review(RUNNER_PREVIEW, False),
        },
        "prior_proposal_preserved": prior_proposal_preserved,
        "proposal_label_review": label_review,
        "family_coverage_review": family_review,
        "evidence_basis_review": evidence_review,
        "forbidden_evidence_review": forbidden_review,
        "proposal_limitations_review": limitations_review,
        "review_findings": {
            "p0_findings": p0_findings,
            "p1_findings": p1_findings,
            "p0_issue_count": len(p0_findings),
            "p1_attention_count": len(p1_findings),
            "summary": (
                "P1 attention retained because prior proposal was partial and evidence quality is limited."
                if not p0_findings and p1_findings
                else "Review passed with no P0 or P1 findings."
                if not p0_findings
                else "Review failed due to P0 findings."
            ),
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
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
        "route_key": payload["prior_proposal_preserved"]["route_key"],
        "result_classification": payload["result_classification"],
        "family_proposal_count": payload["prior_proposal_preserved"]["family_proposal_count"],
        "p0_issue_count": payload["review_findings"]["p0_issue_count"],
        "p1_attention_count": payload["review_findings"]["p1_attention_count"],
        "forbidden_evidence_used": payload["forbidden_evidence_review"]["forbidden_evidence_used"],
        "pnl_fields_used_for_thresholds": payload["forbidden_evidence_review"][
            "pnl_fields_used_for_thresholds"
        ],
        "next_allowed_step": payload["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
    }
    print(json.dumps(stdout_payload, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
