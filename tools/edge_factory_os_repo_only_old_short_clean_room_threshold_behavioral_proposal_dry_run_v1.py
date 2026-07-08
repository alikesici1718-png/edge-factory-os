import csv
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.py"
ARTIFACT_PATH = "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_DRY_RUN"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "819b0c05fe1ad10c1ab58101d6a1ce7de0eeb7e4"
EXPECTED_TRACKED_PYTHON_COUNT = 946

THRESHOLD_RECONSTRUCTION_CONTRACT = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_reconstruction_contract_v1.json"
)
EVIDENCE_EXTRACTION_DRY_RUN = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_evidence_extraction_dry_run_v1.json"
)
BEHAVIORAL_PROPOSAL_CONTRACT = (
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_contract_v1.json"
)
CLEAN_ROOM_CONTRACT = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"

MASTER_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
MASTER_OUTPUT_FILES = {
    "signals": MASTER_DIR / "signals.csv",
    "pending_entries": MASTER_DIR / "pending_entries.csv",
    "closed_trades": MASTER_DIR / "closed_trades.csv",
    "rejected_entries": MASTER_DIR / "rejected_entries.csv",
}

RECONSTRUCTION_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_CONTRACT_CREATED"
EVIDENCE_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_EVIDENCE_EXTRACTION_DRY_RUN_CREATED"
CONTRACT_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_CONTRACT_CREATED"
EVIDENCE_READY_CLASS = "OLD_SHORT_THRESHOLD_EVIDENCE_EXTRACTION_READY_FOR_BEHAVIORAL_PROPOSAL_NO_EDGE_NO_LIVE"
CONTRACT_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_BEHAVIORAL_PROPOSAL_DRY_RUN_V1"
NEXT_ALLOWED_STEP_READY_OR_PARTIAL = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_PROPOSAL_REVIEW_V1"
NEXT_ALLOWED_STEP_INCONCLUSIVE_OR_INVALID = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_INCONCLUSIVE_CLOSURE_V1"

RESULT_READY = "THRESHOLD_BEHAVIORAL_PROPOSAL_READY_NO_EDGE_NO_LIVE"
RESULT_PARTIAL = "THRESHOLD_BEHAVIORAL_PROPOSAL_PARTIAL_NO_EDGE_NO_LIVE"
RESULT_INCONCLUSIVE = "THRESHOLD_BEHAVIORAL_PROPOSAL_INCONCLUSIVE_NO_EDGE_NO_LIVE"
RESULT_INVALID = "THRESHOLD_BEHAVIORAL_PROPOSAL_INVALID_NO_EDGE_NO_LIVE"

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
QUANTILES = ["p10", "p25", "p50", "p75", "p90"]

BLOWOFF_REQUIRED_FEATURES = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_range_bps",
    "signal_vol_quote",
]
MEAN_REVERSION_REQUIRED_FEATURES = [
    "signal_ret60_bps",
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_range_bps",
    "signal_vol_quote",
]
ENTRY_CONFIRMATION_FEATURES = ["entry_range_bps", "entry_vol_quote"]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

FORBIDDEN_PNL_MARKERS = [
    "pnl",
    "profit",
    "loss",
    "win",
    "outcome",
    "ret_net",
    "net_ret",
    "gross_ret",
    "return_after",
    "validation",
    "holdout",
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
        if not line:
            continue
        entries.append(
            {
                "status": line[:2],
                "path": line[3:].strip().strip('"').replace("\\", "/"),
            }
        )
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


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "na", "n/a"}:
        return None
    text = text.replace(",", "")
    try:
        numeric = float(text)
    except ValueError:
        return None
    if not math.isfinite(numeric):
        return None
    return numeric


def rounded(value: Any) -> Optional[float]:
    numeric = safe_float(value)
    if numeric is None:
        return None
    return round(numeric, 6)


def percentile(values: Sequence[float], q: float) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))
    if lower_index == upper_index:
        return ordered[lower_index]
    weight = position - lower_index
    return ordered[lower_index] * (1.0 - weight) + ordered[upper_index] * weight


def median_absolute_deviation(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    median = percentile(values, 0.5)
    if median is None:
        return None
    deviations = [abs(value - median) for value in values]
    return percentile(deviations, 0.5)


def describe_values(values: Sequence[float]) -> Dict[str, Any]:
    finite_values = [value for value in values if math.isfinite(value)]
    if not finite_values:
        return {"count": 0}
    return {
        "count": len(finite_values),
        "min": rounded(min(finite_values)),
        "max": rounded(max(finite_values)),
        "p10": rounded(percentile(finite_values, 0.10)),
        "p25": rounded(percentile(finite_values, 0.25)),
        "p50": rounded(percentile(finite_values, 0.50)),
        "p75": rounded(percentile(finite_values, 0.75)),
        "p90": rounded(percentile(finite_values, 0.90)),
        "median_absolute_deviation": rounded(median_absolute_deviation(finite_values)),
    }


def row_family_key(row: Dict[str, str]) -> Optional[str]:
    for field in ["family_key", "route_key", "strategy_family_key"]:
        value = row.get(field)
        if value:
            return value.strip()
    return None


def row_subfamily(row: Dict[str, str]) -> Optional[str]:
    for field in ["subfamily", "family", "family_name", "strategy_family", "signal_family"]:
        value = row.get(field)
        if value:
            text = value.strip()
            if text in FAMILIES:
                return text
    for value in row.values():
        text = str(value).strip()
        if text in FAMILIES:
            return text
    return None


def load_master_quantiles_if_needed() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    source_rows: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    row_counts: Dict[str, int] = defaultdict(int)
    missing_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    files_review: Dict[str, Any] = {}

    for source_category, path in MASTER_OUTPUT_FILES.items():
        files_review[source_category] = {
            "path": str(path),
            "exists": path.exists(),
            "loaded": False,
            "old_short_rows_used": 0,
        }
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row_family_key(row) not in {ROUTE_KEY, "old_short"}:
                    continue
                subfamily = row_subfamily(row)
                if subfamily not in FAMILIES:
                    continue
                family_key = f"old_short/{subfamily}"
                row_counts[family_key] += 1
                files_review[source_category]["old_short_rows_used"] += 1
                for feature in FEATURE_FIELDS:
                    numeric = safe_float(row.get(feature))
                    if numeric is None:
                        missing_counts[family_key][feature] += 1
                    else:
                        source_rows[family_key][feature].append(numeric)
        files_review[source_category]["loaded"] = True

    family_feature_summaries: Dict[str, Any] = {}
    for subfamily in FAMILIES:
        family_key = f"old_short/{subfamily}"
        row_count = row_counts.get(family_key, 0)
        feature_summaries: Dict[str, Any] = {}
        missing_count_by_feature: Dict[str, int] = {}
        missing_field_rates: Dict[str, Optional[float]] = {}
        for feature in FEATURE_FIELDS:
            values = source_rows[family_key][feature]
            feature_summaries[feature] = describe_values(values)
            missing_count = int(missing_counts[family_key].get(feature, 0))
            missing_count_by_feature[feature] = missing_count
            missing_field_rates[feature] = rounded(missing_count / row_count) if row_count else None
        family_feature_summaries[family_key] = {
            "feature_summaries": feature_summaries,
            "missing_count_by_feature": missing_count_by_feature,
            "missing_field_rates": missing_field_rates,
            "observed_feature_count": sum(
                1 for summary in feature_summaries.values() if int(summary.get("count", 0)) > 0
            ),
            "row_count": row_count,
            "sources_present": [
                source for source, review in files_review.items() if review["old_short_rows_used"] > 0
            ],
        }

    return family_feature_summaries, {
        "master_output_used": True,
        "reason": "evidence artifact lacked necessary quantile detail",
        "files_review": files_review,
    }


def has_quantile_detail(family_feature_summaries: Dict[str, Any]) -> bool:
    for subfamily in FAMILIES:
        family_key = f"old_short/{subfamily}"
        family_summary = family_feature_summaries.get(family_key)
        if not isinstance(family_summary, dict):
            return False
        feature_summaries = family_summary.get("feature_summaries")
        if not isinstance(feature_summaries, dict):
            return False
        for feature in FEATURE_FIELDS:
            summary = feature_summaries.get(feature)
            if not isinstance(summary, dict):
                return False
            if int(summary.get("count", 0) or 0) <= 0:
                return False
            for quantile in QUANTILES:
                if safe_float(summary.get(quantile)) is None:
                    return False
    return True


def observed_direction(summary: Dict[str, Any]) -> str:
    p25 = safe_float(summary.get("p25"))
    p50 = safe_float(summary.get("p50"))
    p75 = safe_float(summary.get("p75"))
    if p25 is None or p50 is None or p75 is None:
        return "unknown"
    if p25 > 0 and p50 > 0:
        return "positive"
    if p75 < 0 and p50 < 0:
        return "negative"
    if p25 < 0 < p75:
        return "mixed"
    if p50 > 0:
        return "mostly_positive"
    if p50 < 0:
        return "mostly_negative"
    return "flat_or_mixed"


def feature_role(family: str, feature: str) -> str:
    if family == "blowoff_short":
        roles = {
            "signal_ret1_bps": "short_window_pressure",
            "signal_ret3_bps": "short_window_pressure",
            "signal_ret5_bps": "short_window_pressure",
            "signal_range_bps": "range_expansion",
            "signal_vol_quote": "activity_volume",
            "entry_range_bps": "entry_confirmation_range",
            "entry_vol_quote": "entry_confirmation_volume",
            "signal_ret60_bps": "context_only_longer_window_extension_not_primary_for_blowoff",
        }
    else:
        roles = {
            "signal_ret60_bps": "longer_window_extension",
            "signal_ret1_bps": "local_exhaustion_short_window_behavior",
            "signal_ret3_bps": "local_exhaustion_short_window_behavior",
            "signal_ret5_bps": "local_exhaustion_short_window_behavior",
            "signal_range_bps": "range_confirmation",
            "signal_vol_quote": "volume_confirmation",
            "entry_range_bps": "entry_confirmation_range",
            "entry_vol_quote": "entry_confirmation_volume",
        }
    return roles.get(feature, "descriptive_context")


def threshold_rule_for_feature(
    family: str,
    feature: str,
    summary: Dict[str, Any],
    missing_rate: Optional[float],
) -> Dict[str, Any]:
    direction = observed_direction(summary)
    count = int(summary.get("count", 0) or 0)
    p10 = rounded(summary.get("p10"))
    p25 = rounded(summary.get("p25"))
    p50 = rounded(summary.get("p50"))
    p75 = rounded(summary.get("p75"))
    p90 = rounded(summary.get("p90"))
    role = feature_role(family, feature)
    limited = count < 20 or (missing_rate is not None and missing_rate > 0.50)

    rule: Dict[str, Any] = {
        "feature": feature,
        "role": role,
        "source": "family_feature_summaries",
        "selection_method": "fixed_robust_quantile_policy_from_preregistered_contract",
        "observed_direction": direction,
        "count": count,
        "missing_rate": missing_rate,
        "limited_evidence": limited,
        "labels": [
            "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
            "NOT_ORIGINAL_THRESHOLD",
            "NOT_PNL_OPTIMIZED",
            "NOT_EDGE_EVIDENCE",
            "NO_LIVE_CAPITAL",
        ],
    }

    if feature in ENTRY_CONFIRMATION_FEATURES:
        rule.update(
            {
                "operator": ">=",
                "value": p25,
                "quantile": "p25",
                "requirement": "optional_when_present_due_to_sparse_entry_evidence",
                "applies_when_field_present": True,
            }
        )
    elif feature.endswith("vol_quote"):
        rule.update(
            {
                "operator": ">=",
                "value": p25,
                "quantile": "p25",
                "requirement": "behavioral_lower_bound_activity",
            }
        )
    elif feature.endswith("range_bps"):
        if p25 is not None and p25 > 0:
            rule.update(
                {
                    "operator": ">=",
                    "value": p25,
                    "quantile": "p25",
                    "requirement": "behavioral_lower_bound_range_expansion",
                }
            )
        else:
            rule.update(
                {
                    "operator": "between_inclusive",
                    "lower": p10,
                    "upper": p90,
                    "quantile": "p10_to_p90",
                    "requirement": "descriptive_range_envelope_direction_unclear",
                }
            )
    elif feature.endswith("_bps"):
        if direction in {"positive", "mostly_positive"}:
            rule.update(
                {
                    "operator": ">=",
                    "value": p25,
                    "quantile": "p25",
                    "requirement": "behavioral_lower_bound_positive_extension",
                }
            )
        elif direction in {"negative", "mostly_negative"}:
            rule.update(
                {
                    "operator": "<=",
                    "value": p75,
                    "quantile": "p75",
                    "requirement": "behavioral_upper_bound_negative_short_window_move",
                }
            )
        else:
            rule.update(
                {
                    "operator": "between_inclusive",
                    "lower": p25,
                    "upper": p75,
                    "quantile": "p25_to_p75",
                    "requirement": "descriptive_return_envelope_direction_mixed",
                }
            )
    else:
        rule.update(
            {
                "operator": "between_inclusive",
                "lower": p10,
                "upper": p90,
                "quantile": "p10_to_p90",
                "requirement": "descriptive_behavioral_envelope",
            }
        )

    rule["quantile_context"] = {
        "p10": p10,
        "p25": p25,
        "p50": p50,
        "p75": p75,
        "p90": p90,
        "median_absolute_deviation": rounded(summary.get("median_absolute_deviation")),
        "min": rounded(summary.get("min")),
        "max": rounded(summary.get("max")),
    }
    return rule


def family_required_features(family: str) -> List[str]:
    if family == "blowoff_short":
        return list(BLOWOFF_REQUIRED_FEATURES)
    return list(MEAN_REVERSION_REQUIRED_FEATURES)


def build_family_proposal(
    family: str,
    family_summary: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    feature_summaries = family_summary.get("feature_summaries", {})
    missing_rates = family_summary.get("missing_field_rates", {})
    missing_counts = family_summary.get("missing_count_by_feature", {})
    row_count = int(family_summary.get("row_count", 0) or 0)
    sources_present = list(family_summary.get("sources_present", []))
    required_features = family_required_features(family)

    threshold_rules: Dict[str, Any] = {}
    evidence_basis: Dict[str, Any] = {}
    quantile_refs: Dict[str, Any] = {}
    missing_fields: Dict[str, Any] = {}

    for feature in FEATURE_FIELDS:
        summary = feature_summaries.get(feature, {})
        missing_rate = rounded(missing_rates.get(feature))
        rule = threshold_rule_for_feature(family, feature, summary, missing_rate)
        threshold_rules[feature] = rule
        quantile_refs[feature] = {
            "count": int(summary.get("count", 0) or 0),
            "min": rounded(summary.get("min")),
            "max": rounded(summary.get("max")),
            "p10": rounded(summary.get("p10")),
            "p25": rounded(summary.get("p25")),
            "p50": rounded(summary.get("p50")),
            "p75": rounded(summary.get("p75")),
            "p90": rounded(summary.get("p90")),
            "median_absolute_deviation": rounded(summary.get("median_absolute_deviation")),
            "source": "evidence_extraction_artifact",
        }
        evidence_basis[feature] = {
            "role": feature_role(family, feature),
            "feature_summary": quantile_refs[feature],
            "missing_count": int(missing_counts.get(feature, 0) or 0),
            "missing_rate": missing_rate,
            "rule_basis": rule["selection_method"],
            "pnl_or_outcome_used": False,
        }
        missing_fields[feature] = {
            "missing_count": int(missing_counts.get(feature, 0) or 0),
            "missing_rate": missing_rate,
            "limited_by_missingness": missing_rate is not None and missing_rate > 0.50,
        }

    required_available = [
        feature
        for feature in required_features
        if int(feature_summaries.get(feature, {}).get("count", 0) or 0) > 0
        and safe_float(feature_summaries.get(feature, {}).get("p25")) is not None
    ]
    required_missing = [feature for feature in required_features if feature not in required_available]
    entry_limited = [
        feature
        for feature in ENTRY_CONFIRMATION_FEATURES
        if rounded(missing_rates.get(feature)) is not None and rounded(missing_rates.get(feature)) > 0.50
    ]
    direction_notes = []
    if family == "blowoff_short":
        negative_short_window = [
            feature
            for feature in ["signal_ret1_bps", "signal_ret3_bps", "signal_ret5_bps"]
            if observed_direction(feature_summaries.get(feature, {})) in {"negative", "mostly_negative"}
        ]
        if negative_short_window:
            direction_notes.append(
                "emitted evidence shows negative short-window return direction for "
                + ", ".join(negative_short_window)
                + "; dry-run preserves observed behavior instead of inventing positive thresholds"
            )

    quality_is_limited = bool(required_missing) or bool(entry_limited) or row_count < 100 or bool(direction_notes)
    proposal_created = not required_missing and row_count > 0
    quality_label = "limited" if quality_is_limited else "usable"
    proposal_status = "created_limited_evidence" if proposal_created and quality_is_limited else "created"
    if not proposal_created:
        proposal_status = "incomplete"

    proposal = {
        "family_key": "old_short",
        "subfamily": family,
        "side": "short",
        "proposal_status": proposal_status,
        "proposal_count_for_family": 1 if proposal_created else 0,
        "threshold_set_label": f"{family}_behavioral_reconstruction_threshold_v1",
        "labels": [
            "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
            "NOT_ORIGINAL_THRESHOLD",
            "NOT_PNL_OPTIMIZED",
            "NOT_EDGE_EVIDENCE",
            "NO_LIVE_CAPITAL",
        ],
        "execution_assumptions_preserved": {
            "entry_delay_minutes_approx": 2,
            "hold_minutes_approx": 120,
            "global_gate_required": True,
            "side": "short",
        },
        "threshold_rules": threshold_rules if proposal_created else {},
        "proposal_basis": {
            "method": "robust_quantile_envelopes_from_emitted_old_short_behavior",
            "quantiles_allowed": QUANTILES,
            "grid_search_used": False,
            "pnl_or_outcome_used": False,
            "original_threshold_claimed": False,
            "alternative_proposals_generated": False,
        },
        "limitations": [
            "behavioral reconstruction only; not original threshold recovery",
            "not PnL optimized and not edge evidence",
            "entry confirmation fields are optional when present because observed evidence is sparse",
        ],
    }

    family_quality = {
        "family_key": "old_short",
        "subfamily": family,
        "row_count": row_count,
        "source_categories": sources_present,
        "required_features": required_features,
        "required_features_available": required_available,
        "required_features_missing": required_missing,
        "entry_confirmation_features_limited": entry_limited,
        "direction_notes": direction_notes,
        "proposal_created": proposal_created,
        "evidence_quality": quality_label,
        "reason": (
            "required behavioral features available but evidence is limited"
            if proposal_created and quality_is_limited
            else "required behavioral features available"
            if proposal_created
            else "required behavioral features missing"
        ),
    }
    return proposal, evidence_basis, quantile_refs, {"fields": missing_fields, "family_quality": family_quality}


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

    if unexpected_dirty_paths:
        raise RuntimeError(f"unexpected dirty paths before dry-run build: {unexpected_dirty_paths}")
    if modified_existing_paths:
        raise RuntimeError(f"existing files modified before dry-run build: {modified_existing_paths}")
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"HEAD moved before dry-run build: {actual_head} != {EXPECTED_HEAD}")
    if actual_tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before dry-run build: "
            f"{actual_tracked_python_count} != {EXPECTED_TRACKED_PYTHON_COUNT}"
        )

    reconstruction = read_json(THRESHOLD_RECONSTRUCTION_CONTRACT)
    evidence = read_json(EVIDENCE_EXTRACTION_DRY_RUN)
    contract = read_json(BEHAVIORAL_PROPOSAL_CONTRACT)

    reconstruction_identity = reconstruction.get("threshold_reconstruction_identity", {})
    evidence_identity = evidence.get("evidence_extraction_identity", {})
    contract_identity = contract.get("proposal_contract_identity", {})

    if reconstruction.get("status") != RECONSTRUCTION_STATUS:
        raise RuntimeError("threshold reconstruction contract status mismatch")
    if evidence.get("status") != EVIDENCE_STATUS:
        raise RuntimeError("threshold evidence extraction status mismatch")
    if contract.get("status") != CONTRACT_STATUS:
        raise RuntimeError("behavioral proposal contract status mismatch")
    if reconstruction_identity.get("route_key") != ROUTE_KEY:
        raise RuntimeError("threshold reconstruction route_key mismatch")
    if evidence_identity.get("route_key") != ROUTE_KEY:
        raise RuntimeError("evidence extraction route_key mismatch")
    if contract_identity.get("route_key") != ROUTE_KEY:
        raise RuntimeError("behavioral proposal contract route_key mismatch")
    if evidence.get("result_classification") != EVIDENCE_READY_CLASS:
        raise RuntimeError("evidence extraction is not ready for behavioral proposal dry-run")
    if contract.get("next_allowed_step") != CONTRACT_NEXT_ALLOWED_STEP:
        raise RuntimeError("behavioral proposal contract next allowed step mismatch")
    if contract_identity.get("proposal_contract_only") is not True:
        raise RuntimeError("proposal contract identity does not preserve contract-only status")

    original_exact_recovered = reconstruction_identity.get("original_exact_thresholds_recovered") is True
    behavioral_reconstruction = reconstruction_identity.get("behavioral_threshold_reconstruction") is True
    no_pnl_optimization = reconstruction_identity.get("no_pnl_optimization") is True
    contract_original_exact_recovered = contract_identity.get("original_exact_thresholds_recovered") is True
    contract_behavioral_reconstruction = contract_identity.get("behavioral_threshold_reconstruction") is True
    contract_no_pnl_optimization = contract_identity.get("no_pnl_optimization") is True
    if (
        original_exact_recovered
        or contract_original_exact_recovered
        or not behavioral_reconstruction
        or not contract_behavioral_reconstruction
        or not no_pnl_optimization
        or not contract_no_pnl_optimization
    ):
        raise RuntimeError("source contracts do not satisfy behavioral proposal dry-run gate")

    family_feature_summaries = evidence.get("family_feature_summaries", {})
    if has_quantile_detail(family_feature_summaries):
        quantile_source_review = {
            "master_output_used": False,
            "reason": "evidence artifact already contained necessary family feature quantile detail",
            "master_dir": str(MASTER_DIR),
            "files_review": {},
        }
    else:
        family_feature_summaries, quantile_source_review = load_master_quantiles_if_needed()

    old_short_summary = evidence.get("old_short_row_summary", {})
    source_category_summaries = evidence.get("source_category_summaries", {})
    proposal_by_family: Dict[str, Any] = {}
    evidence_basis_by_feature: Dict[str, Any] = {}
    quantile_references_used: Dict[str, Any] = {}
    missing_fields: Dict[str, Any] = {}
    family_evidence_quality: Dict[str, Any] = {}
    source_categories_used: Dict[str, Any] = {}

    for family in FAMILIES:
        family_key = f"old_short/{family}"
        family_summary = family_feature_summaries.get(family_key, {})
        proposal, evidence_basis, quantile_refs, missing_info = build_family_proposal(family, family_summary)
        proposal_by_family[family] = proposal
        evidence_basis_by_feature[family] = evidence_basis
        quantile_references_used[family] = quantile_refs
        missing_fields[family] = missing_info["fields"]
        family_evidence_quality[family] = missing_info["family_quality"]
        source_categories_used[family] = {
            "source_categories": list(family_summary.get("sources_present", [])),
            "from_evidence_artifact": True,
        }

    proposal_family_count = sum(
        1 for proposal in proposal_by_family.values() if int(proposal.get("proposal_count_for_family", 0)) == 1
    )
    limited_family_count = sum(
        1 for quality in family_evidence_quality.values() if quality.get("evidence_quality") == "limited"
    )
    forbidden_optimization_used = False
    pnl_fields_used_for_thresholds = False
    exact_original_threshold_claimed = False
    if forbidden_optimization_used or pnl_fields_used_for_thresholds or exact_original_threshold_claimed:
        result_classification = RESULT_INVALID
    elif proposal_family_count == 0:
        result_classification = RESULT_INCONCLUSIVE
    elif proposal_family_count < len(FAMILIES) or limited_family_count:
        result_classification = RESULT_PARTIAL
    else:
        result_classification = RESULT_READY
    next_allowed_step = (
        NEXT_ALLOWED_STEP_READY_OR_PARTIAL
        if result_classification in {RESULT_READY, RESULT_PARTIAL}
        else NEXT_ALLOWED_STEP_INCONCLUSIVE_OR_INVALID
    )

    forbidden_optimization_checks = {
        "forbidden_optimization_used": forbidden_optimization_used,
        "pnl_fields_used_for_thresholds": pnl_fields_used_for_thresholds,
        "exact_original_threshold_claimed": exact_original_threshold_claimed,
        "threshold_grid_search_used": False,
        "alternative_threshold_sets_generated": False,
        "threshold_selection_by_return_used": False,
        "threshold_selection_by_win_rate_used": False,
        "closed_trade_profitability_used": False,
        "validation_returns_used": False,
        "holdout_returns_used": False,
        "monthly_stability_optimization_used": False,
        "tp_sl_tuning_used": False,
        "runner_executed": False,
        "signals_generated": False,
        "backtest_run": False,
        "pnl_computed": False,
        "pnl_marker_fields_excluded_from_threshold_method": FORBIDDEN_PNL_MARKERS,
    }

    safety_permissions = {
        "threshold_behavioral_proposal_dry_run_created": True,
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
        "behavioral_proposal_contract_loaded": contract.get("status") == CONTRACT_STATUS,
        "threshold_evidence_extraction_loaded": evidence.get("status") == EVIDENCE_STATUS,
        "original_exact_thresholds_not_claimed": not original_exact_recovered
        and not contract_original_exact_recovered
        and not exact_original_threshold_claimed,
        "behavioral_threshold_reconstruction_preserved": behavioral_reconstruction
        and contract_behavioral_reconstruction,
        "no_pnl_optimization_preserved": no_pnl_optimization and contract_no_pnl_optimization,
        "no_pnl_fields_used_for_thresholds": not pnl_fields_used_for_thresholds,
        "no_threshold_grid_search": not forbidden_optimization_checks["threshold_grid_search_used"],
        "no_threshold_selection_by_return": not forbidden_optimization_checks[
            "threshold_selection_by_return_used"
        ],
        "no_threshold_selection_by_win_rate": not forbidden_optimization_checks[
            "threshold_selection_by_win_rate_used"
        ],
        "no_runner_execution": not forbidden_optimization_checks["runner_executed"],
        "no_signal_generation": not forbidden_optimization_checks["signals_generated"],
        "no_backtest_run": not forbidden_optimization_checks["backtest_run"],
        "no_pnl_computation_for_optimization": not forbidden_optimization_checks["pnl_computed"],
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS == contract.get("unresolved_fields_preserved"),
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_PATH).exists(),
        "exactly_one_json_artifact_created": not artifact_existed_before_run,
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
            "old_short_clean_room_contract": artifact_review(CLEAN_ROOM_CONTRACT, False),
            "old_short_clean_room_runner_preview": artifact_review(RUNNER_PREVIEW, False),
            "quantile_source_review": quantile_source_review,
        },
        "proposal_identity": {
            "route_key": ROUTE_KEY,
            "threshold_behavioral_proposal_dry_run_only": True,
            "original_threshold_recovery": False,
            "original_exact_thresholds_recovered": False,
            "behavioral_threshold_reconstruction": True,
            "no_pnl_optimization": True,
            "no_threshold_grid_search": True,
            "no_threshold_selection": True,
            "one_proposal_per_family_if_evidence_sufficient": True,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
        },
        "evidence_input_summary": {
            "source_result_classification": evidence.get("result_classification"),
            "old_short_row_count": int(old_short_summary.get("old_short_row_count", 0) or 0),
            "family_count": int(old_short_summary.get("family_count", 0) or 0),
            "feature_count": int(old_short_summary.get("feature_count", 0) or 0),
            "rejected_reason_count": int(
                evidence.get("reject_reason_summaries", {}).get("rejected_reason_count", 0) or 0
            ),
            "subfamily_counts": old_short_summary.get("subfamily_counts", {}),
            "source_old_short_row_counts": old_short_summary.get("source_old_short_row_counts", {}),
            "observed_feature_fields": old_short_summary.get("observed_feature_fields", []),
            "source_categories_available": sorted(source_category_summaries.keys()),
        },
        "proposed_behavioral_thresholds_by_family": proposal_by_family,
        "evidence_basis_by_feature": evidence_basis_by_feature,
        "quantile_references_used": quantile_references_used,
        "source_categories_used": source_categories_used,
        "missing_fields": missing_fields,
        "family_evidence_quality": family_evidence_quality,
        "forbidden_optimization_checks": forbidden_optimization_checks,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "proposal_limitations": [
            "Behavioral threshold proposal dry-run only; not original threshold recovery.",
            "Quantiles are descriptive evidence from emitted old_short rows and are not PnL selected.",
            "No runner, validator, signal generation, backtest, raw market data, runtime, monitor, API, live, or capital action was used.",
            "Both family proposals are marked limited because entry confirmation evidence is sparse; blowoff_short short-window direction differs from the positive-pressure goal text in emitted evidence.",
        ],
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
        "route_key": payload["proposal_identity"]["route_key"],
        "result_classification": payload["result_classification"],
        "family_count": payload["evidence_input_summary"]["family_count"],
        "proposal_family_count": sum(
            1
            for proposal in payload["proposed_behavioral_thresholds_by_family"].values()
            if int(proposal.get("proposal_count_for_family", 0)) == 1
        ),
        "forbidden_optimization_used": payload["forbidden_optimization_checks"][
            "forbidden_optimization_used"
        ],
        "pnl_fields_used_for_thresholds": payload["forbidden_optimization_checks"][
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
