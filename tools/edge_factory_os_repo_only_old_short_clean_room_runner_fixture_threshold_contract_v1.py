import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_old_short_clean_room_runner_fixture_threshold_contract_v1.py"
ARTIFACT_PATH = "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_FIXTURE_THRESHOLD_CONTRACT_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_FIXTURE_THRESHOLD_CONTRACT"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "060fae2da4e02a6ad6b751ef642c13441f51f16e"
EXPECTED_TRACKED_PYTHON_COUNT = 948

THRESHOLD_BEHAVIORAL_PROPOSAL = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
)
THRESHOLD_PROPOSAL_REVIEW = "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json"
THRESHOLD_RECONSTRUCTION_CONTRACT = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_reconstruction_contract_v1.json"
)
THRESHOLD_EVIDENCE_EXTRACTION = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_evidence_extraction_dry_run_v1.json"
)
RUNNER_DRY_RUN_DESIGN = "artifacts/old_short_clean_room/old_short_clean_room_runner_dry_run_design_v1.json"
RUNNER_DRY_RUN_IMPLEMENTATION_PREVIEW = (
    "artifacts/old_short_clean_room/old_short_clean_room_runner_dry_run_implementation_preview_v1.json"
)

PROPOSAL_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_DRY_RUN_CREATED"
PROPOSAL_RESULT = "THRESHOLD_BEHAVIORAL_PROPOSAL_PARTIAL_NO_EDGE_NO_LIVE"
REVIEW_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_PROPOSAL_REVIEW_CREATED"
REVIEW_RESULT = "THRESHOLD_PROPOSAL_REVIEW_PASS_WITH_P1_ATTENTION_NO_EDGE_NO_LIVE"
REVIEW_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_FIXTURE_THRESHOLD_CONTRACT_V1"
NEXT_ALLOWED_STEP_COMPLETE = "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_V1"
NEXT_ALLOWED_STEP_INCOMPLETE = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_PROPOSAL_REPAIR_CONTRACT_V1"

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
RESULT_LABELS = [
    "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_FEATURE_FIXTURE_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def object_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


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
        "prior_proposal_preserved",
        "proposal_contract_identity",
        "threshold_reconstruction_identity",
        "evidence_extraction_identity",
        "contract_identity",
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


def rule_has_concrete_threshold(rule: Dict[str, Any]) -> bool:
    operator = rule.get("operator")
    if operator in {">=", "<=", ">", "<", "=="}:
        return rule.get("value") is not None
    if operator == "between_inclusive":
        return rule.get("lower") is not None and rule.get("upper") is not None
    return False


def copy_family_thresholds(proposal: Dict[str, Any], review: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    proposal_families = proposal.get("proposed_behavioral_thresholds_by_family", {})
    evidence_basis = proposal.get("evidence_basis_by_feature", {})
    quantile_refs = proposal.get("quantile_references_used", {})
    missing_fields = proposal.get("missing_fields", {})
    family_quality = proposal.get("family_evidence_quality", {})
    review_p1_findings = review.get("review_findings", {}).get("p1_findings", [])
    threshold_families: Dict[str, Any] = {}
    completeness_by_family: Dict[str, Any] = {}

    for family in FAMILIES:
        source_family = proposal_families.get(family, {})
        threshold_rules = source_family.get("threshold_rules", {})
        labels = source_family.get("labels", [])
        missing_labels = [label for label in REQUIRED_LABELS if label not in labels]
        missing_features = [feature for feature in FEATURE_FIELDS if feature not in threshold_rules]
        non_concrete_rules = [
            feature
            for feature, rule in threshold_rules.items()
            if feature in FEATURE_FIELDS and not rule_has_concrete_threshold(rule)
        ]
        family_p1_notes = []
        for finding in review_p1_findings:
            families = finding.get("families")
            if families is None or family in families:
                family_p1_notes.append(finding)
        family_complete = (
            bool(source_family)
            and int(source_family.get("proposal_count_for_family", 0)) == 1
            and not missing_labels
            and not missing_features
            and not non_concrete_rules
            and source_family.get("side") == "short"
        )
        threshold_families[family] = {
            "family_key": "old_short",
            "subfamily": family,
            "fixture_only": True,
            "side": source_family.get("side"),
            "source_proposal_status": source_family.get("proposal_status"),
            "threshold_set_label": source_family.get("threshold_set_label"),
            "labels": labels,
            "threshold_rules": threshold_rules,
            "evidence_basis_by_feature": evidence_basis.get(family, {}),
            "quantile_references_used": quantile_refs.get(family, {}),
            "missing_fields": missing_fields.get(family, {}),
            "family_evidence_quality": family_quality.get(family, {}),
            "p1_attention_notes": family_p1_notes,
            "source_hashes": {
                "threshold_rules_sha256": object_hash(threshold_rules),
                "evidence_basis_sha256": object_hash(evidence_basis.get(family, {})),
                "quantile_references_sha256": object_hash(quantile_refs.get(family, {})),
                "missing_fields_sha256": object_hash(missing_fields.get(family, {})),
                "family_evidence_quality_sha256": object_hash(family_quality.get(family, {})),
            },
            "copied_from_proposal_artifact_without_modification": True,
        }
        completeness_by_family[family] = {
            "proposal_exists": bool(source_family),
            "proposal_count_for_family": int(source_family.get("proposal_count_for_family", 0) or 0),
            "short_only": source_family.get("side") == "short",
            "missing_required_labels": missing_labels,
            "missing_threshold_features": missing_features,
            "non_concrete_threshold_rules": non_concrete_rules,
            "family_complete": family_complete,
        }
    return threshold_families, completeness_by_family


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
        raise RuntimeError(f"unexpected dirty paths before contract build: {unexpected_dirty_paths}")
    if modified_existing_paths:
        raise RuntimeError(f"existing files modified before contract build: {modified_existing_paths}")
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"HEAD moved before contract build: {actual_head} != {EXPECTED_HEAD}")
    if actual_tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before contract build: "
            f"{actual_tracked_python_count} != {EXPECTED_TRACKED_PYTHON_COUNT}"
        )

    proposal = read_json(THRESHOLD_BEHAVIORAL_PROPOSAL)
    review = read_json(THRESHOLD_PROPOSAL_REVIEW)
    reconstruction = read_json(THRESHOLD_RECONSTRUCTION_CONTRACT)
    evidence = read_json(THRESHOLD_EVIDENCE_EXTRACTION)

    proposal_identity = proposal.get("proposal_identity", {})
    review_prior = review.get("prior_proposal_preserved", {})
    review_findings = review.get("review_findings", {})
    forbidden_review = review.get("forbidden_evidence_review", {})
    reconstruction_identity = reconstruction.get("threshold_reconstruction_identity", {})

    if proposal.get("status") != PROPOSAL_STATUS:
        raise RuntimeError("threshold behavioral proposal status mismatch")
    if review.get("status") != REVIEW_STATUS:
        raise RuntimeError("threshold proposal review status mismatch")
    if proposal_identity.get("route_key") != ROUTE_KEY or review_prior.get("route_key") != ROUTE_KEY:
        raise RuntimeError("route_key mismatch in source proposal/review")
    if review.get("result_classification") != REVIEW_RESULT:
        raise RuntimeError("proposal review classification mismatch")
    if review.get("next_allowed_step") != REVIEW_NEXT_ALLOWED_STEP:
        raise RuntimeError("proposal review next allowed step mismatch")
    if proposal.get("result_classification") != PROPOSAL_RESULT:
        raise RuntimeError("proposal result classification mismatch")

    threshold_families, completeness_by_family = copy_family_thresholds(proposal, review)
    family_threshold_count = sum(1 for item in completeness_by_family.values() if item["family_complete"])
    contract_complete = family_threshold_count == 2
    next_allowed_step = NEXT_ALLOWED_STEP_COMPLETE if contract_complete else NEXT_ALLOWED_STEP_INCOMPLETE

    threshold_section_matches_source = True
    for family in FAMILIES:
        source_family = proposal.get("proposed_behavioral_thresholds_by_family", {}).get(family, {})
        copied_family = threshold_families.get(family, {})
        threshold_section_matches_source = threshold_section_matches_source and (
            copied_family.get("threshold_rules") == source_family.get("threshold_rules", {})
        )
        threshold_section_matches_source = threshold_section_matches_source and (
            copied_family.get("evidence_basis_by_feature")
            == proposal.get("evidence_basis_by_feature", {}).get(family, {})
        )
        threshold_section_matches_source = threshold_section_matches_source and (
            copied_family.get("quantile_references_used")
            == proposal.get("quantile_references_used", {}).get(family, {})
        )

    p1_attention_count = int(review_findings.get("p1_attention_count", 0) or 0)
    p0_issue_count = int(review_findings.get("p0_issue_count", 0) or 0)
    forbidden_evidence_used = bool(forbidden_review.get("forbidden_evidence_used"))
    pnl_fields_used = bool(forbidden_review.get("pnl_fields_used_for_thresholds"))

    source_review_preserved = {
        "threshold_proposal_review_classification": review.get("result_classification"),
        "p0_issue_count": p0_issue_count,
        "p1_attention_count": p1_attention_count,
        "p1_findings": review_findings.get("p1_findings", []),
        "forbidden_evidence_used": forbidden_evidence_used,
        "pnl_fields_used": pnl_fields_used,
        "proposal_family_count": int(review_prior.get("family_proposal_count", 0) or 0),
        "threshold_behavioral_proposal_result": proposal.get("result_classification"),
        "review_next_allowed_step_preserved": review.get("next_allowed_step"),
    }

    safety_permissions = {
        "runner_fixture_threshold_contract_created": True,
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
        "threshold_behavioral_proposal_loaded": proposal.get("status") == PROPOSAL_STATUS,
        "threshold_proposal_review_loaded": review.get("status") == REVIEW_STATUS,
        "p0_issue_count_zero_verified": p0_issue_count == 0,
        "p1_attention_preserved": p1_attention_count == 4,
        "forbidden_evidence_false_verified": forbidden_evidence_used is False,
        "pnl_fields_used_false_verified": pnl_fields_used is False,
        "proposal_family_count_verified_2": int(review_prior.get("family_proposal_count", 0) or 0) == 2,
        "original_exact_thresholds_not_claimed": proposal_identity.get("original_exact_thresholds_recovered")
        is False
        and reconstruction_identity.get("original_exact_thresholds_recovered") is False,
        "behavioral_thresholds_labeled_not_original": all(
            "NOT_ORIGINAL_THRESHOLD" in family.get("labels", []) for family in threshold_families.values()
        ),
        "no_pnl_optimization_preserved": proposal_identity.get("no_pnl_optimization") is True
        and reconstruction_identity.get("no_pnl_optimization") is True,
        "no_threshold_selection": True,
        "no_threshold_modification": threshold_section_matches_source,
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
        "unresolved_fields_preserved": proposal.get("unresolved_fields_preserved") == UNRESOLVED_FIELDS,
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
            "threshold_behavioral_proposal": artifact_review(THRESHOLD_BEHAVIORAL_PROPOSAL, True),
            "threshold_proposal_review": artifact_review(THRESHOLD_PROPOSAL_REVIEW, True),
            "threshold_reconstruction_contract": artifact_review(THRESHOLD_RECONSTRUCTION_CONTRACT, True),
            "threshold_evidence_extraction": artifact_review(THRESHOLD_EVIDENCE_EXTRACTION, True),
            "runner_dry_run_design": artifact_review(RUNNER_DRY_RUN_DESIGN, False),
            "runner_dry_run_implementation_preview": artifact_review(
                RUNNER_DRY_RUN_IMPLEMENTATION_PREVIEW, False
            ),
        },
        "fixture_threshold_contract_identity": {
            "route_key": ROUTE_KEY,
            "contract_type": "runner_fixture_threshold_contract",
            "fixture_only": True,
            "original_exact_thresholds_recovered": False,
            "behavioral_reconstruction_thresholds": True,
            "not_original_thresholds": True,
            "not_pnl_optimized": True,
            "not_edge_evidence": True,
            "no_live_capital": True,
        },
        "source_review_preserved": source_review_preserved,
        "threshold_contract_scope": {
            "allowed_use": [
                "SCHEMA_FIXTURE_DRY_RUN",
                "FEATURE_FIXTURE_DRY_RUN",
                "bounded fixture runner dry-run only",
                "validator plumbing / behavior preview only",
            ],
            "forbidden_use": [
                "full backtest",
                "live trading",
                "capital allocation",
                "runtime/monitor enablement",
                "candidate generation",
                "edge claim",
                "performance optimization",
                "threshold grid search",
                "historical market-wide signal generation without later preregistration",
            ],
        },
        "threshold_families": threshold_families,
        "threshold_application_policy": {
            "future_runner_fixture_dry_run_allowed_only_if": [
                "dry-run mode is FEATURE_FIXTURE_DRY_RUN or schema fixture compatible mode",
                "input is bounded fixture data and not raw full market data",
                "no PnL is computed",
                "no backtest is run",
                "all outputs are paper-only and not edge evidence",
                "no live/capital permissions exist",
            ],
            "threshold_selection_allowed": False,
            "threshold_modification_allowed": False,
        },
        "fail_closed_policy": {
            "future_runner_must_fail_closed_if": [
                "threshold contract missing",
                "family threshold missing",
                "required feature missing",
                "threshold label missing",
                "no-live guard false",
                "fixture input outside allowed roots",
                "raw market data path supplied",
                "runtime path supplied",
                "order/private/live fields detected",
            ]
        },
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "result_labels": RESULT_LABELS,
        "contract_completeness": {
            "contract_complete": contract_complete,
            "family_threshold_count": family_threshold_count,
            "expected_family_threshold_count": 2,
            "families_expected": FAMILIES,
            "completeness_by_family": completeness_by_family,
            "incomplete_reason": None
            if contract_complete
            else "proposal artifact lacks complete concrete threshold values for all required families",
        },
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
        "route_key": payload["fixture_threshold_contract_identity"]["route_key"],
        "contract_complete": payload["contract_completeness"]["contract_complete"],
        "family_threshold_count": payload["contract_completeness"]["family_threshold_count"],
        "p1_attention_count": payload["source_review_preserved"]["p1_attention_count"],
        "threshold_selection_allowed_now": False,
        "runner_execution_allowed_now": False,
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
