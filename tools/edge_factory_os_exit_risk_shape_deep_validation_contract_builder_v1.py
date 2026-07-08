#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Exit Risk Shape Deep Validation Contract Builder v1

Purpose:
- Consume Exit Risk Shape Evaluator v1 output.
- Build a read-only deep-validation contract for strict 12/12 exit-shape previews.
- Lock every action gate closed until the complete validation chain passes.

This builder does NOT:
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_exit_risk_shape_evaluator"
    / "exit_risk_shape_evaluator_latest.json"
)

DEEP_VALIDATION_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_exit_risk_shape_evaluator"
    / "exit_risk_shape_deep_validation_queue_latest.json"
)

PREVIEW_CSV = (
    BASE_DIR
    / "edge_factory_os_exit_risk_shape_evaluator"
    / "exit_risk_shape_strict_preview_candidates_for_validation_latest.csv"
)

OUT_DIR = BASE_DIR / "edge_factory_os_research_direction_contracts"
OUT_JSON = OUT_DIR / "exit_risk_shape_deep_validation_contract_latest.json"
OUT_TXT = OUT_DIR / "exit_risk_shape_deep_validation_contract_latest.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_EVALUATOR_STATUS = "EXIT_RISK_SHAPE_EVALUATOR_PREVIEW_FOUND_DEEP_VALIDATION_REQUIRED"
REQUIRED_QUEUE_STATUS = "EXIT_RISK_SHAPE_DEEP_VALIDATION_QUEUE_READY"

RESEARCH_KEY = "EXIT_RISK_SHAPE_DEEP_VALIDATION_V1"
NEXT_MODULE = "edge_factory_os_exit_risk_shape_deep_validation_runner_v1.py"

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def timestamp_compact() -> str:
    return utc_now().strftime("%Y%m%d_%H%M%S")


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def read_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    except Exception:
        return []

    return rows


def infer_panel_candidates() -> List[str]:
    candidates: List[str] = []

    known = [
        BASE_DIR
        / "edge_factory_feature_panels"
        / "post_impulse_drift_long_v1"
        / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet",
    ]

    for p in known:
        if p.exists():
            candidates.append(str(p))

    if candidates:
        return candidates

    roots = [
        BASE_DIR / "edge_factory_feature_panels",
        BASE_DIR / "edge_factory_os_universe",
        BASE_DIR / "edge_factory_universe",
        BASE_DIR,
    ]

    patterns = [
        "**/*feature_panel*.parquet",
        "**/*okx*swap*.parquet",
        "**/*285*.parquet",
        "**/*full*panel*.parquet",
        "**/*panel*.parquet",
    ]

    found: List[Path] = []

    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            try:
                for p in root.glob(pattern):
                    if p.is_file() and p.suffix.lower() == ".parquet":
                        found.append(p)
            except Exception:
                pass

    def score(path: Path) -> int:
        s = str(path).lower()
        value = 0
        for token, weight in [
            ("okx", 20),
            ("swap", 20),
            ("285", 15),
            ("1y", 15),
            ("feature_panel", 12),
            ("dynamic", 8),
            ("full", 8),
            ("panel", 8),
            ("universe", 6),
        ]:
            if token in s:
                value += weight
        try:
            value += min(int(path.stat().st_size / 100_000_000), 25)
        except Exception:
            pass
        return value

    found = sorted(set(found), key=score, reverse=True)
    return [str(p) for p in found[:5]]


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS EXIT RISK SHAPE DEEP VALIDATION CONTRACT BUILDER v1")
    lines.append("=" * 100)

    for k in [
        "builder_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "contract_hash",
        "research_key",
        "validation_queue_id",
        "strict_policy_key",
        "canonical_policy_month_count",
        "strict_preview_row_count",
        "required_validation_count",
        "next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("VALIDATION CHAIN")
    lines.append("-" * 100)
    for item in result.get("required_validation_chain", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("STRICT PREVIEWS")
    lines.append("-" * 100)
    for row in result.get("strict_preview_rows", [])[:10]:
        lines.append(
            f"{row.get('reference_id')} {row.get('side')} {row.get('exit_shape_id')} | "
            f"positive={row.get('positive_months')}/{row.get('canonical_month_count')} | "
            f"total={row.get('total_month_pnl_bps')} | worst={row.get('worst_month_bps')} | "
            f"events={row.get('event_count')} symbols={row.get('symbol_count')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT")
    lines.append("-" * 100)
    lines.append(f"contract_latest_path: {result.get('contract_latest_path')}")
    lines.append(f"summary_path: {result.get('summary_path')}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS EXIT RISK SHAPE DEEP VALIDATION CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {result.get('builder_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"contract_hash: {result.get('contract_hash')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"validation_queue_id: {result.get('validation_queue_id')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"strict_preview_row_count: {result.get('strict_preview_row_count')}")
    print(f"required_validation_count: {result.get('required_validation_count')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('contract_latest_path')}")
    print(f"TXT : {result.get('summary_path')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    evaluator = load_json(EVALUATOR_JSON, default={})
    queue = load_json(DEEP_VALIDATION_QUEUE_JSON, default={})
    preview_csv_rows = read_csv_rows(PREVIEW_CSV)

    evaluator_status = evaluator.get("evaluator_status")
    queue_status = queue.get("queue_status")

    preview_found = bool(evaluator.get("preview_found"))
    deep_validation_required = bool(evaluator.get("deep_validation_required"))
    release_allowed = bool(evaluator.get("release_allowed"))

    strict_preview_rows = queue.get("strict_preview_rows")
    if not isinstance(strict_preview_rows, list) or not strict_preview_rows:
        strict_preview_rows = preview_csv_rows

    canonical_policy_month_count = int(evaluator.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    strict_preview_row_count = len(strict_preview_rows)
    strict_12_exit_shape_preview_count = to_int(evaluator.get("strict_12_exit_shape_preview_count"))

    validation_queue_id = queue.get("validation_queue_id") or evaluator.get("validation_queue_id")

    prerequisite_pass = (
        evaluator_status == REQUIRED_EVALUATOR_STATUS
        and queue_status == REQUIRED_QUEUE_STATUS
        and preview_found is True
        and deep_validation_required is True
        and release_allowed is False
        and canonical_policy_month_count == 12
        and strict_12_exit_shape_preview_count > 0
        and strict_preview_row_count > 0
        and validation_queue_id
    )

    required_validation_chain = [
        {
            "validation_key": "ROUTE_HASH_PREFLIGHT_NO_REPEAT_FAILURE",
            "description": "Confirm this preview route is not identical to a known failed route and has a new validation route hash.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "FULL_UNIVERSE_REPLAY_VALIDATION",
            "description": "Replay the frozen reference + exit shape on the full 1Y 285-symbol panel, rebuilding metrics independently.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "ROLLING_OR_OOS_SPLIT_VALIDATION",
            "description": "Check rolling/train-OOS month stability; preview-only in-sample stability is insufficient.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "COST_SLIPPAGE_SENSITIVITY_VALIDATION",
            "description": "Stress costs/slippage beyond the preview assumptions and require stability to survive.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "SYMBOL_CONCENTRATION_VALIDATION",
            "description": "Reject if the preview is driven by too few symbols or one symbol cluster.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "MONTH_STABILITY_12_OF_12_RECHECK",
            "description": "Recheck canonical 12-of-12 positive months after all validation filters and cost assumptions.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "MAE_MFE_PATH_SANITY_CHECK",
            "description": "Verify MAE/MFE assumptions are not an artifact of conservative/optimistic path approximation.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "RISK_CAPITAL_SAFETY_CHECK",
            "description": "Even after validation, capital/live/paper gates remain blocked until risk policy explicitly passes.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "RELEASE_GATE_REVIEW",
            "description": "Final release gate must independently approve any candidate/family action.",
            "pass_required_for_release": True,
        },
        {
            "validation_key": "EXPLICIT_ACTION_AUTHORIZATION_GUARD",
            "description": "No active paper/live/capital action without explicit downstream authorization.",
            "pass_required_for_release": True,
        },
    ]

    contract_hash_payload = {
        "builder": "edge_factory_os_exit_risk_shape_deep_validation_contract_builder_v1",
        "research_key": RESEARCH_KEY,
        "validation_queue_id": validation_queue_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "strict_preview_rows": strict_preview_rows,
        "required_validation_chain": required_validation_chain,
    }

    contract_hash = stable_hash(contract_hash_payload)
    contract_id = f"EXIT_RISK_SHAPE_DEEP_VALIDATION_CONTRACT_V1_{contract_hash}_{timestamp_compact()}"

    if prerequisite_pass:
        builder_status = "EXIT_RISK_SHAPE_DEEP_VALIDATION_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_EXIT_RISK_SHAPE_DEEP_VALIDATION_RUNNER"
        reason = (
            f"preview_found=True; strict_preview_row_count={strict_preview_row_count}; "
            "release_allowed=False; deep_validation_contract_ready=True"
        )
    else:
        builder_status = "EXIT_RISK_SHAPE_DEEP_VALIDATION_CONTRACT_BLOCKED_PREREQUISITE_NOT_MET"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_EXIT_RISK_SHAPE_EVALUATOR_AND_QUEUE_NO_RELEASE"
        reason = (
            f"evaluator_status={evaluator_status}; queue_status={queue_status}; "
            f"preview_found={preview_found}; deep_validation_required={deep_validation_required}; "
            f"release_allowed={release_allowed}; strict_preview_row_count={strict_preview_row_count}; "
            f"strict_12_exit_shape_preview_count={strict_12_exit_shape_preview_count}; "
            f"validation_queue_id={validation_queue_id}"
        )

    contract = {
        "builder_name": "edge_factory_os_exit_risk_shape_deep_validation_contract_builder_v1",
        "created_at_utc": utc_now_iso(),
        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_id": contract_id if prerequisite_pass else None,
        "contract_hash": contract_hash,
        "research_key": RESEARCH_KEY,
        "validation_queue_id": validation_queue_id,
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "strict_12_exit_shape_preview_count": strict_12_exit_shape_preview_count,
        "strict_preview_row_count": strict_preview_row_count,
        "strict_preview_rows": strict_preview_rows,
        "required_validation_count": len(required_validation_chain),
        "required_validation_chain": required_validation_chain,
        "deep_validation_scope": {
            "route_hash_preflight": True,
            "full_universe_replay": True,
            "rolling_oos_validation": True,
            "cost_slippage_sensitivity": True,
            "symbol_concentration": True,
            "month_stability_recheck": True,
            "mae_mfe_path_sanity": True,
            "risk_capital_safety": True,
            "release_gate_review": True,
            "explicit_action_authorization": True,
        },
        "validation_policy": {
            "preview_is_release": False,
            "candidate_generation_from_this_contract": False,
            "family_release_from_this_contract": False,
            "runtime_change_from_this_contract": False,
            "capital_change_from_this_contract": False,
            "active_paper_from_this_contract": False,
            "live_from_this_contract": False,
            "real_orders_from_this_contract": False,
            "all_required_validations_must_pass_before_any_release_consideration": True,
        },
        "panel_candidates": infer_panel_candidates(),
        "input_evaluator_json": str(EVALUATOR_JSON),
        "input_queue_json": str(DEEP_VALIDATION_QUEUE_JSON),
        "input_preview_csv": str(PREVIEW_CSV),
        "next_module": NEXT_MODULE if prerequisite_pass else None,
        "release_gate_feed": {
            "EXIT_RISK_SHAPE_DEEP_VALIDATION_CONTRACT_READY": prerequisite_pass,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "PREVIEW_FOUND": preview_found,
            "DEEP_VALIDATION_REQUIRED": deep_validation_required,
            "RELEASE_PASS_FROM_THIS_CONTRACT": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_CONTRACT": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_CONTRACT": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_CONTRACT": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_CONTRACT": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_CONTRACT": False,
            "LIVE_ALLOWED_FROM_THIS_CONTRACT": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_CONTRACT": False,
        },
        "contract_latest_path": str(OUT_JSON),
        "summary_path": str(OUT_TXT),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, contract)
    write_text_summary(OUT_TXT, contract)
    print_summary(contract)

    return 0 if prerequisite_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
