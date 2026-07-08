from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_research_hypothesis_generator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

ROW_DIAG_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_impulse_long_row_level_diagnostic_v2"
    / "impulse_long_row_level_diagnostic_v2_latest.json"
)

DRIFT_V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_drift_review_v3"
    / "family_drift_review_v3_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"research_hypothesis_generator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "research_hypothesis_generator_latest.json"
LATEST_MD = OUT_ROOT / "research_hypothesis_generator_latest.md"


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


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def make_hypothesis(
    hypothesis_id: str,
    priority: int,
    severity: str,
    family: str,
    claim: str,
    evidence: Dict[str, Any],
    proposed_read_only_test: str,
    expected_output: str,
    rejection_rule: str,
    promotion_rule: str,
    required_inputs: List[str],
    blocked_actions: List[str],
) -> Dict[str, Any]:
    return {
        "hypothesis_id": hypothesis_id,
        "priority": priority,
        "severity": severity,
        "family": family,
        "claim": claim,
        "evidence": evidence,
        "proposed_read_only_test": proposed_read_only_test,
        "expected_output": expected_output,
        "rejection_rule": rejection_rule,
        "promotion_rule": promotion_rule,
        "required_inputs": required_inputs,
        "blocked_actions": blocked_actions,
        "allowed_scope": "READ_ONLY_RESEARCH_PLAN",
        "action_allowed_now": False,
        "runtime_mutation_allowed": False,
        "capital_change_allowed": False,
        "live_or_real_order_allowed": False,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    diag = load_json(ROW_DIAG_V2_LATEST)
    drift = load_json(DRIFT_V3_LATEST)

    if diag is None:
        critical.append("row_level_diagnostic_v2_latest_json_not_found")
        diag = {}

    if drift is None:
        attention.append("family_drift_review_v3_latest_json_not_found")
        drift = {}

    primary_summary = diag.get("primary_summary") or {}
    findings = diag.get("findings") or []

    closed = diag.get("closed")
    drift_remaining = diag.get("drift_remaining")
    capital_remaining = diag.get("capital_remaining")
    drift_gate_ready = bool(diag.get("drift_gate_ready") is True)

    win_rate = to_float(primary_summary.get("win_rate"))
    pnl_sum = to_float(safe_get(primary_summary, ["pnl_summary", "sum"]))
    pnl_mean = to_float(safe_get(primary_summary, ["pnl_summary", "mean"]))
    impulse_rows = to_int(primary_summary.get("impulse_rows_deduped"))

    top_loss_symbols = primary_summary.get("top_loss_symbols") or []
    top_win_symbols = primary_summary.get("top_win_symbols") or []
    ret3_bucket_pnl = primary_summary.get("ret3_bucket_pnl") or {}
    entry_range_bucket_pnl = primary_summary.get("entry_range_bucket_pnl") or {}
    fee_bps_summary = primary_summary.get("fee_bps_summary") or {}
    entry_slip_bps_summary = primary_summary.get("entry_slip_bps_summary") or {}
    exit_slip_bps_summary = primary_summary.get("exit_slip_bps_summary") or {}
    gross_gap = to_float(primary_summary.get("gross_minus_net_ret_sum_gap"))

    hypotheses: List[Dict[str, Any]] = []

    ret3_150_300 = to_float(ret3_bucket_pnl.get("ret3_150_300"))
    ret3_gt_300 = to_float(ret3_bucket_pnl.get("ret3_gt_300"))

    if ret3_150_300 is not None and ret3_gt_300 is not None and ret3_150_300 < 0 and ret3_gt_300 > 0:
        hypotheses.append(
            make_hypothesis(
                hypothesis_id="RH1_IMPULSE_STRENGTH_THRESHOLD_TOO_LOW",
                priority=100,
                severity="HIGH",
                family="impulse_long",
                claim=(
                    "impulse_long may be accepting weak/mid impulse signals that are negative, "
                    "while stronger impulse signals are positive."
                ),
                evidence={
                    "ret3_150_300_bucket_pnl": ret3_150_300,
                    "ret3_gt_300_bucket_pnl": ret3_gt_300,
                    "win_rate": win_rate,
                    "total_pnl": pnl_sum,
                    "sample_rows": impulse_rows,
                },
                proposed_read_only_test=(
                    "Run an offline-only threshold sweep on impulse_long using primary ledger/backtest features: "
                    "compare signal_ret3_bps >= 300 versus 150-300 and lower buckets. Keep fees/slippage identical."
                ),
                expected_output=(
                    "A bucket table with count, win_rate, total_pnl, mean_pnl, drawdown proxy, and symbol concentration."
                ),
                rejection_rule=(
                    "Reject if stronger signal_ret3 bucket does not improve both total_pnl and win_rate out-of-sample."
                ),
                promotion_rule=(
                    "Only consider a candidate rule if it improves row-level and offline backtest metrics without reducing sample too far."
                ),
                required_inputs=[
                    "live_impulse_event_long_paper/closed_trades.csv",
                    "offline/backtest impulse_long trade table with signal_ret3_bps",
                ],
                blocked_actions=[
                    "do_not_change_runtime_threshold",
                    "do_not_change_capital",
                    "do_not_disable_family",
                ],
            )
        )

    if top_loss_symbols:
        worst_symbol = top_loss_symbols[0][0]
        worst_symbol_pnl = to_float(top_loss_symbols[0][1])

        if worst_symbol_pnl is not None and pnl_sum is not None and worst_symbol_pnl < 0:
            hypotheses.append(
                make_hypothesis(
                    hypothesis_id="RH2_SYMBOL_OR_EVENT_LOSS_CONCENTRATION",
                    priority=95,
                    severity="HIGH",
                    family="impulse_long",
                    claim=(
                        "impulse_long losses may be dominated by one or a few symbols/events rather than a uniform strategy failure."
                    ),
                    evidence={
                        "worst_symbol": worst_symbol,
                        "worst_symbol_pnl": worst_symbol_pnl,
                        "total_pnl": pnl_sum,
                        "top_loss_symbols": top_loss_symbols[:10],
                        "top_win_symbols": top_win_symbols[:10],
                    },
                    proposed_read_only_test=(
                        "Build symbol concentration diagnostic: remove top-loss symbol(s), recompute total_pnl/win_rate, "
                        "then test whether the loss came from isolated event risk or repeatable regime weakness."
                    ),
                    expected_output=(
                        "With/without top-loss-symbol performance table and symbol-level attribution."
                    ),
                    rejection_rule=(
                        "Reject symbol-filter idea if excluding the worst symbol does not materially improve robustness "
                        "or if losses rotate across many symbols."
                    ),
                    promotion_rule=(
                        "Only propose a guard if symbol-level/event-level weakness is repeatable in offline evidence."
                    ),
                    required_inputs=[
                        "primary impulse_long closed trades",
                        "symbol-level offline history",
                        "event/regime metadata if available",
                    ],
                    blocked_actions=[
                        "do_not_blacklist_symbol_live",
                        "do_not_change_runtime",
                        "do_not_change_capital",
                    ],
                )
            )

    if win_rate is not None and win_rate < 0.35 and pnl_sum is not None and pnl_sum < 0:
        hypotheses.append(
            make_hypothesis(
                hypothesis_id="RH3_LOW_PRECISION_ENTRY_OR_BAD_REGIME_FILTER",
                priority=90,
                severity="HIGH",
                family="impulse_long",
                claim=(
                    "The current impulse_long entry condition has low realized precision and may need a regime filter."
                ),
                evidence={
                    "win_rate": win_rate,
                    "total_pnl": pnl_sum,
                    "mean_pnl": pnl_mean,
                    "sample_rows": impulse_rows,
                    "findings": findings,
                },
                proposed_read_only_test=(
                    "Split impulse_long by market_ret_bps, signal_range_bps, entry_range_bps, entry_vol_quote, "
                    "exit_hour_utc, and signal_ret buckets. Identify any bucket with acceptable win_rate and positive pnl."
                ),
                expected_output=(
                    "Regime bucket table ranked by total_pnl, win_rate, and sample count."
                ),
                rejection_rule=(
                    "Reject if no regime bucket preserves enough sample while improving total_pnl and win_rate."
                ),
                promotion_rule=(
                    "Only create a candidate filter if multiple independent splits point to the same bad regime."
                ),
                required_inputs=[
                    "primary impulse_long closed trades",
                    "global_closed_trades.csv for feature consistency",
                    "offline feature/backtest panel",
                ],
                blocked_actions=[
                    "do_not_patch_logger",
                    "do_not_patch_runtime",
                    "do_not_start_new_family",
                ],
            )
        )

    if gross_gap is not None and gross_gap > 0:
        hypotheses.append(
            make_hypothesis(
                hypothesis_id="RH4_COST_SLIPPAGE_EDGE_TOO_THIN",
                priority=75,
                severity="MEDIUM",
                family="impulse_long",
                claim=(
                    "The impulse_long edge may be too thin after fee/slippage assumptions."
                ),
                evidence={
                    "gross_minus_net_ret_sum_gap": gross_gap,
                    "fee_bps_summary": fee_bps_summary,
                    "entry_slip_bps_summary": entry_slip_bps_summary,
                    "exit_slip_bps_summary": exit_slip_bps_summary,
                    "total_pnl": pnl_sum,
                },
                proposed_read_only_test=(
                    "Recompute impulse_long performance under cost scenarios: current cost, half slippage, zero extra slippage, "
                    "and stress slippage. Check if edge only exists under unrealistic execution."
                ),
                expected_output=(
                    "Cost sensitivity matrix: pnl/win_rate/mean return by fee+slippage assumption."
                ),
                rejection_rule=(
                    "Reject if strategy is negative even under favorable cost assumptions."
                ),
                promotion_rule=(
                    "Only keep researching if signal has positive gross edge and realistic net edge is recoverable."
                ),
                required_inputs=[
                    "primary impulse_long closed trades",
                    "fee_bps_total",
                    "entry_slip_bps",
                    "exit_slip_bps",
                    "gross_ret",
                    "net_ret",
                ],
                blocked_actions=[
                    "do_not_reduce_cost_assumption_in_runtime",
                    "do_not_change_execution_model_live",
                ],
            )
        )

    if not drift_gate_ready:
        hypotheses.append(
            make_hypothesis(
                hypothesis_id="RH5_CONTROL_GATE_WAIT_FOR_CLOSED_20",
                priority=60,
                severity="CONTROL",
                family="impulse_long",
                claim=(
                    "Research plan can be prepared, but no runtime/capital/family action is allowed before the drift gate."
                ),
                evidence={
                    "closed": closed,
                    "drift_remaining": drift_remaining,
                    "capital_remaining": capital_remaining,
                    "drift_gate_ready": drift_gate_ready,
                },
                proposed_read_only_test=(
                    "Wait for closed>=20 or drift_remaining<=0, then rerun v4, drift review v3, row diagnostic v2, "
                    "and this hypothesis generator."
                ),
                expected_output=(
                    "Gate-ready research decision with the same hypothesis set refreshed from current sample."
                ),
                rejection_rule="N/A control rule.",
                promotion_rule="N/A control rule.",
                required_inputs=[
                    "cycle_operator_v4_latest.json",
                    "family_drift_review_v3_latest.json",
                    "row_level_diagnostic_v2_latest.json",
                ],
                blocked_actions=[
                    "do_not_change_capital",
                    "do_not_disable_family",
                    "do_not_patch_runtime",
                    "do_not_live_trade",
                ],
            )
        )

    hypotheses.sort(key=lambda h: h["priority"], reverse=True)

    if critical:
        generator_status = "RESEARCH_HYPOTHESIS_GENERATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_DIAGNOSTIC_INPUT"
        reason = "; ".join(critical)
    elif not hypotheses:
        generator_status = "RESEARCH_HYPOTHESIS_GENERATOR_NO_HYPOTHESES"
        severity = "INFO"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "CONTINUE_COLLECTING_SAMPLE"
        reason = "no material research hypotheses from current diagnostic"
    elif not drift_gate_ready:
        generator_status = "RESEARCH_HYPOTHESIS_GENERATOR_PRE_THRESHOLD_PLAN_READY"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_COLLECTING_AND_PREPARE_READ_ONLY_RESEARCH_QUEUE"
        reason = f"hypothesis_count={len(hypotheses)}; drift_gate_ready=False"
    else:
        generator_status = "RESEARCH_HYPOTHESIS_GENERATOR_READY_FOR_READ_ONLY_RESEARCH"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "CREATE_OFFLINE_EXPERIMENT_CONTRACTS_FROM_TOP_HYPOTHESES"
        reason = f"hypothesis_count={len(hypotheses)}; drift_gate_ready=True"

    research_queue = [
        {
            "queue_id": f"RQ_{i+1:03d}_{h['hypothesis_id']}",
            "priority": h["priority"],
            "family": h["family"],
            "status": "QUEUED_READ_ONLY_PLAN",
            "hypothesis_id": h["hypothesis_id"],
            "next_step": h["proposed_read_only_test"],
            "blocked_until": "drift_gate_ready" if not drift_gate_ready else "none",
            "mutation_allowed": False,
        }
        for i, h in enumerate(hypotheses)
    ]

    ai_adapter_readiness = {
        "ready_for_api_model_review": bool(hypotheses),
        "recommended_model_role": "read_only_research_reviewer",
        "send_raw_trades_to_api": False,
        "send_only_summarized_state": True,
        "estimated_context_payload": [
            "cycle_operator_v4 summary",
            "family_drift_review_v3 summary",
            "row_level_diagnostic_v2 summary",
            "research_hypotheses",
        ],
        "budget_guard": "manual_call_only_initially",
    }

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "generator_status": generator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "row_diagnostic_source": str(ROW_DIAG_V2_LATEST),
        "drift_source": str(DRIFT_V3_LATEST),

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "input_summary": {
            "impulse_rows": impulse_rows,
            "win_rate": win_rate,
            "total_pnl": pnl_sum,
            "mean_pnl": pnl_mean,
            "top_loss_symbols": top_loss_symbols[:10],
            "top_win_symbols": top_win_symbols[:10],
            "ret3_bucket_pnl": ret3_bucket_pnl,
            "entry_range_bucket_pnl": entry_range_bucket_pnl,
            "gross_minus_net_ret_sum_gap": gross_gap,
        },

        "research_hypotheses": hypotheses,
        "research_queue": research_queue,
        "ai_adapter_readiness": ai_adapter_readiness,

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "family_disable_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "research_hypothesis_generator_v1_state.json"
    out_md = RUN_DIR / "research_hypothesis_generator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS RESEARCH HYPOTHESIS GENERATOR v1",
        "",
        f"generator_status: {generator_status}",
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
        "## Input Summary",
        "",
        json.dumps(result["input_summary"], indent=2, default=str),
        "",
        "## Research Hypotheses",
        "",
    ]

    for h in hypotheses:
        md_lines.append(json.dumps(h, indent=2, default=str))

    md_lines.extend([
        "",
        "## Research Queue",
        "",
        json.dumps(research_queue, indent=2, default=str),
        "",
        "## AI Adapter Readiness",
        "",
        json.dumps(ai_adapter_readiness, indent=2, default=str),
        "",
        "## Safety",
        "",
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
    print("EDGE FACTORY OS RESEARCH HYPOTHESIS GENERATOR v1")
    print("=" * 100)
    print(f"generator_status: {generator_status}")
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
    print("INPUT SUMMARY")
    print("-" * 100)
    print(json.dumps(result["input_summary"], indent=2, default=str))
    print()
    print("RESEARCH HYPOTHESES")
    print("-" * 100)
    for h in hypotheses:
        print(f"{h['hypothesis_id']} | priority={h['priority']} | severity={h['severity']}")
        print(f"claim: {h['claim']}")
        print(f"test: {h['proposed_read_only_test']}")
        print()
    print("RESEARCH QUEUE")
    print("-" * 100)
    for q in research_queue:
        print(q)
    print()
    print("AI ADAPTER READINESS")
    print("-" * 100)
    print(json.dumps(ai_adapter_readiness, indent=2, default=str))
    print()
    print("SAFETY")
    print("-" * 100)
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
