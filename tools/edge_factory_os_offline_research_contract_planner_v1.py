from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_offline_research_contract_planner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

HYPOTHESIS_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_hypothesis_generator_v1"
    / "research_hypothesis_generator_latest.json"
)

ROW_DIAG_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_impulse_long_row_level_diagnostic_v2"
    / "impulse_long_row_level_diagnostic_v2_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"offline_research_contract_planner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
CONTRACT_DIR = RUN_DIR / "contracts"

LATEST_JSON = OUT_ROOT / "offline_research_contract_planner_latest.json"
LATEST_MD = OUT_ROOT / "offline_research_contract_planner_latest.md"


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def safe_slug(text: str) -> str:
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:120] or "unknown"


def to_float(v: Any, default=None):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def to_int(v: Any, default=0):
    try:
        if v is None:
            return default
        return int(float(v))
    except Exception:
        return default


def get_input_summary(hyp_state: Dict[str, Any]) -> Dict[str, Any]:
    return hyp_state.get("input_summary") or {}


def build_contract_for_hypothesis(
    *,
    hypothesis: Dict[str, Any],
    hyp_state: Dict[str, Any],
    row_diag: Dict[str, Any],
    drift_gate_ready: bool,
) -> Dict[str, Any]:
    hypothesis_id = hypothesis.get("hypothesis_id", "UNKNOWN")
    family = hypothesis.get("family", "unknown")
    priority = hypothesis.get("priority")
    severity = hypothesis.get("severity")

    input_summary = get_input_summary(hyp_state)
    primary_ledger = row_diag.get("primary_ledger")
    primary_summary = row_diag.get("primary_summary") or {}

    blocked_until = "none" if drift_gate_ready else "drift_gate_ready"

    common = {
        "contract_schema": "edge_factory_offline_research_contract_draft_v1",
        "created_at_utc": NOW.isoformat(),
        "contract_id": f"offline_research_{safe_slug(hypothesis_id)}_{NOW.strftime('%Y%m%d_%H%M%S')}",
        "source_hypothesis_id": hypothesis_id,
        "priority": priority,
        "severity": severity,
        "family": family,
        "claim": hypothesis.get("claim"),
        "evidence": hypothesis.get("evidence"),
        "source_required_inputs": hypothesis.get("required_inputs"),
        "source_blocked_actions": hypothesis.get("blocked_actions"),
        "primary_ledger": primary_ledger,
        "input_summary_snapshot": input_summary,
        "primary_row_summary_snapshot": {
            "impulse_rows_deduped": primary_summary.get("impulse_rows_deduped"),
            "win_rate": primary_summary.get("win_rate"),
            "pnl_summary": primary_summary.get("pnl_summary"),
            "ret3_bucket_pnl": primary_summary.get("ret3_bucket_pnl"),
            "entry_range_bucket_pnl": primary_summary.get("entry_range_bucket_pnl"),
            "top_loss_symbols": primary_summary.get("top_loss_symbols"),
            "top_win_symbols": primary_summary.get("top_win_symbols"),
        },
        "gate": {
            "drift_gate_ready": drift_gate_ready,
            "blocked_until": blocked_until,
            "offline_contract_execution_allowed_now": bool(drift_gate_ready),
            "runtime_mutation_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "live_or_real_order_allowed": False,
        },
        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
        },
    }

    if hypothesis_id == "RH1_IMPULSE_STRENGTH_THRESHOLD_TOO_LOW":
        common["experiment_design"] = {
            "experiment_type": "threshold_sweep",
            "objective": "Test whether stronger impulse strength thresholds improve impulse_long edge.",
            "target_family": "impulse_long",
            "primary_metric": "net_total_pnl",
            "secondary_metrics": [
                "win_rate",
                "mean_pnl",
                "trade_count",
                "symbol_concentration",
                "max_single_symbol_loss_share",
            ],
            "parameter_grid": {
                "signal_ret3_min_bps": [150, 200, 250, 300, 350, 400],
                "entry_range_max_bps": [None, 100, 150, 250],
                "cost_model": ["current_fee_slip"],
            },
            "baseline": {
                "current_ret3_bucket_pnl": input_summary.get("ret3_bucket_pnl"),
                "current_total_pnl": input_summary.get("total_pnl"),
                "current_win_rate": input_summary.get("win_rate"),
            },
            "pass_condition": {
                "min_trade_count": 8,
                "must_improve_total_pnl": True,
                "must_improve_win_rate": True,
                "must_not_depend_on_single_symbol": True,
            },
            "failure_condition": {
                "negative_after_threshold": True,
                "sample_too_small": True,
                "only_works_by_removing_all_hard_cases": True,
            },
        }

    elif hypothesis_id == "RH2_SYMBOL_OR_EVENT_LOSS_CONCENTRATION":
        top_loss_symbols = input_summary.get("top_loss_symbols") or []
        worst_symbols = [row[0] for row in top_loss_symbols[:3] if isinstance(row, list) and row]

        common["experiment_design"] = {
            "experiment_type": "symbol_concentration_ablation",
            "objective": "Determine whether impulse_long losses are isolated to symbols/events or general family weakness.",
            "target_family": "impulse_long",
            "primary_metric": "net_total_pnl_without_top_loss_symbols",
            "secondary_metrics": [
                "win_rate_without_top_loss_symbols",
                "remaining_trade_count",
                "loss_rotation_check",
                "worst_symbol_share",
            ],
            "symbol_sets": {
                "remove_top_1_loss_symbol": worst_symbols[:1],
                "remove_top_2_loss_symbols": worst_symbols[:2],
                "remove_top_3_loss_symbols": worst_symbols[:3],
            },
            "baseline": {
                "top_loss_symbols": top_loss_symbols,
                "current_total_pnl": input_summary.get("total_pnl"),
                "current_win_rate": input_summary.get("win_rate"),
            },
            "pass_condition": {
                "improves_without_destroying_sample": True,
                "remaining_sample_count_min": 8,
                "loss_does_not_rotate_to_next_symbol": True,
            },
            "failure_condition": {
                "losses_are_distributed": True,
                "removing_symbols_overfits": True,
                "sample_too_small_after_exclusion": True,
            },
        }

    elif hypothesis_id == "RH3_LOW_PRECISION_ENTRY_OR_BAD_REGIME_FILTER":
        common["experiment_design"] = {
            "experiment_type": "regime_bucket_diagnostic",
            "objective": "Find whether impulse_long only works in specific market/regime buckets.",
            "target_family": "impulse_long",
            "primary_metric": "bucket_net_total_pnl",
            "secondary_metrics": [
                "bucket_win_rate",
                "bucket_trade_count",
                "bucket_mean_pnl",
                "bucket_symbol_concentration",
            ],
            "bucket_dimensions": [
                "market_ret_bps",
                "signal_ret3_bps",
                "signal_range_bps",
                "entry_range_bps",
                "entry_vol_quote",
                "exit_hour_utc",
            ],
            "candidate_filters_to_evaluate": [
                "signal_ret3_bps >= 300",
                "entry_range_bps < 100",
                "entry_range_bps < 250",
                "exclude negative market_ret_bps bucket if available",
                "exclude worst exit_hour bucket if stable",
            ],
            "baseline": {
                "current_total_pnl": input_summary.get("total_pnl"),
                "current_win_rate": input_summary.get("win_rate"),
                "entry_range_bucket_pnl": input_summary.get("entry_range_bucket_pnl"),
                "ret3_bucket_pnl": input_summary.get("ret3_bucket_pnl"),
            },
            "pass_condition": {
                "one_or_more_buckets_positive": True,
                "bucket_sample_sufficient": True,
                "same_filter_supported_by_multiple_dimensions": True,
            },
            "failure_condition": {
                "no_bucket_positive_with_sample": True,
                "filters_conflict": True,
                "improvement_due_to_one_symbol_only": True,
            },
        }

    elif hypothesis_id == "RH4_COST_SLIPPAGE_EDGE_TOO_THIN":
        common["experiment_design"] = {
            "experiment_type": "cost_sensitivity_matrix",
            "objective": "Test whether impulse_long has gross edge but loses after realistic fee/slippage.",
            "target_family": "impulse_long",
            "primary_metric": "net_total_pnl_by_cost_scenario",
            "secondary_metrics": [
                "gross_total_return",
                "net_total_return",
                "win_rate_by_cost",
                "mean_pnl_by_cost",
            ],
            "cost_scenarios": [
                {"name": "current", "fee_bps_total": 25, "entry_slip_bps": 25, "exit_slip_bps": 25},
                {"name": "half_slippage", "fee_bps_total": 25, "entry_slip_bps": 12.5, "exit_slip_bps": 12.5},
                {"name": "fee_only", "fee_bps_total": 25, "entry_slip_bps": 0, "exit_slip_bps": 0},
                {"name": "stress", "fee_bps_total": 25, "entry_slip_bps": 35, "exit_slip_bps": 35},
            ],
            "baseline": {
                "gross_minus_net_ret_sum_gap": input_summary.get("gross_minus_net_ret_sum_gap"),
                "current_total_pnl": input_summary.get("total_pnl"),
                "fee_bps_summary": hypothesis.get("evidence", {}).get("fee_bps_summary"),
                "entry_slip_bps_summary": hypothesis.get("evidence", {}).get("entry_slip_bps_summary"),
                "exit_slip_bps_summary": hypothesis.get("evidence", {}).get("exit_slip_bps_summary"),
            },
            "pass_condition": {
                "gross_edge_positive": True,
                "realistic_net_edge_recoverable": True,
            },
            "failure_condition": {
                "negative_even_under_favorable_cost": True,
                "only_positive_under_unrealistic_cost": True,
            },
        }

    else:
        common["experiment_design"] = {
            "experiment_type": "control_or_unmapped_hypothesis",
            "objective": "No executable offline experiment mapped for this hypothesis yet.",
            "control_only": True,
            "notes": "This may be a gate/control hypothesis or requires a new planner mapping.",
        }

    return common


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    hyp_state = load_json(HYPOTHESIS_LATEST)
    row_diag = load_json(ROW_DIAG_V2_LATEST)

    if hyp_state is None:
        critical.append("research_hypothesis_generator_latest_missing")
        hyp_state = {}

    if row_diag is None:
        attention.append("row_level_diagnostic_v2_latest_missing")
        row_diag = {}

    hypotheses = hyp_state.get("research_hypotheses") or []
    drift_gate_ready = bool(hyp_state.get("drift_gate_ready") is True)

    closed = hyp_state.get("closed")
    drift_remaining = hyp_state.get("drift_remaining")
    capital_remaining = hyp_state.get("capital_remaining")

    contracts: List[Dict[str, Any]] = []

    for h in hypotheses:
        if h.get("hypothesis_id") == "RH5_CONTROL_GATE_WAIT_FOR_CLOSED_20":
            info.append("control_gate_hypothesis_not_converted_to_experiment_contract")
            continue

        contract = build_contract_for_hypothesis(
            hypothesis=h,
            hyp_state=hyp_state,
            row_diag=row_diag,
            drift_gate_ready=drift_gate_ready,
        )
        contracts.append(contract)

        contract_path = CONTRACT_DIR / f"{safe_slug(contract['contract_id'])}.json"
        dump_json(contract_path, contract)
        contract["contract_path"] = str(contract_path)

    if critical:
        planner_status = "OFFLINE_RESEARCH_CONTRACT_PLANNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_HYPOTHESIS_INPUT"
        reason = "; ".join(critical)

    elif not contracts:
        planner_status = "OFFLINE_RESEARCH_CONTRACT_PLANNER_NO_CONTRACTS"
        severity = "INFO"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "WAIT_FOR_RESEARCH_HYPOTHESES"
        reason = "no non-control hypotheses converted"

    elif not drift_gate_ready:
        planner_status = "OFFLINE_RESEARCH_CONTRACTS_PREPARED_EXECUTION_BLOCKED_BY_GATE"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_CONTRACTS_QUEUED_UNTIL_DRIFT_GATE_READY"
        reason = f"contract_count={len(contracts)}; drift_gate_ready=False"

    else:
        planner_status = "OFFLINE_RESEARCH_CONTRACTS_READY_FOR_VALIDATION"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_OR_OFFLINE_RESEARCH"
        next_action = "VALIDATE_OFFLINE_RESEARCH_CONTRACTS"
        reason = f"contract_count={len(contracts)}; drift_gate_ready=True"

    manifest = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "planner_status": planner_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "hypothesis_source": str(HYPOTHESIS_LATEST),
        "row_diagnostic_source": str(ROW_DIAG_V2_LATEST),

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "hypothesis_count": len(hypotheses),
        "contract_count": len(contracts),
        "contracts": contracts,

        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "offline_research_contract_planner_v1_state.json"
    out_md = RUN_DIR / "offline_research_contract_planner_v1_report.md"

    dump_json(out_json, manifest)
    dump_json(LATEST_JSON, manifest)

    md_lines = [
        "# EDGE FACTORY OS OFFLINE RESEARCH CONTRACT PLANNER v1",
        "",
        f"planner_status: {planner_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Gate",
        "",
        f"closed: {closed}",
        f"drift_remaining: {drift_remaining}",
        f"capital_remaining: {capital_remaining}",
        f"drift_gate_ready: {drift_gate_ready}",
        "",
        "## Contracts",
        "",
    ]

    for c in contracts:
        md_lines.append(f"- {c['contract_id']} | {c['source_hypothesis_id']} | {c.get('contract_path')}")

    md_lines.extend([
        "",
        "## Safety",
        "",
        "read_only: True",
        "offline_only: True",
        "mutate_runtime_allowed: False",
        "launcher_allowed: False",
        "patch_runtime_allowed: False",
        "active_paper_allowed: False",
        "live_allowed: False",
        "capital_change_allowed: False",
        "family_disable_allowed: False",
        "real_orders_allowed: False",
        "execution_performed: False",
        "",
        f"critical: {critical}",
        f"attention: {attention}",
        f"info: {info}",
    ])

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS OFFLINE RESEARCH CONTRACT PLANNER v1")
    print("=" * 100)
    print(f"planner_status: {planner_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("GATE")
    print("-" * 100)
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print()
    print("CONTRACTS")
    print("-" * 100)
    for c in contracts:
        print(f"{c['contract_id']}")
        print(f"  hypothesis: {c['source_hypothesis_id']}")
        print(f"  experiment_type: {c['experiment_design'].get('experiment_type')}")
        print(f"  execution_allowed_now: {c['gate']['offline_contract_execution_allowed_now']}")
        print(f"  path: {c.get('contract_path')}")
        print()
    print("SAFETY")
    print("-" * 100)
    print("read_only: True")
    print("offline_only: True")
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
