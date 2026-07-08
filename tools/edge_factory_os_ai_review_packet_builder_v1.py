from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List


MODULE = "edge_factory_os_ai_review_packet_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CYCLE_V4_LATEST = (
    BASE_DIR
    / "edge_factory_os_cycle_operator_v4"
    / "cycle_operator_v4_latest.json"
)

DRIFT_V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_drift_review_v3"
    / "family_drift_review_v3_latest.json"
)

ROW_DIAG_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_impulse_long_row_level_diagnostic_v2"
    / "impulse_long_row_level_diagnostic_v2_latest.json"
)

HYPOTHESIS_V1_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_hypothesis_generator_v1"
    / "research_hypothesis_generator_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"ai_review_packet_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "ai_review_packet_latest.json"
LATEST_MD = OUT_ROOT / "ai_review_packet_latest.md"
LATEST_PROMPT = OUT_ROOT / "ai_review_prompt_latest.txt"


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


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def compact_cycle(cycle: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operator_status": cycle.get("operator_status"),
        "severity": cycle.get("severity"),
        "allowed_scope": cycle.get("allowed_scope"),
        "recommended_action": cycle.get("recommended_action"),
        "reason": cycle.get("reason"),
        "closed": cycle.get("closed"),
        "drift_remaining": cycle.get("drift_remaining"),
        "capital_remaining": cycle.get("capital_remaining"),
        "drift_ready": cycle.get("drift_ready"),
        "capital_review_ready": cycle.get("capital_review_ready"),
        "error_ack_applied": cycle.get("error_ack_applied"),
        "error_blocker_effective": cycle.get("error_blocker_effective"),
        "errors_original": cycle.get("errors_original"),
        "new_errors_since_ack_effective": cycle.get("new_errors_since_ack_effective"),
        "runtime_ok": cycle.get("runtime_ok"),
        "process_ok": cycle.get("process_ok"),
        "health_ok": cycle.get("health_ok"),
        "snapshot_mismatch": cycle.get("snapshot_mismatch"),
    }


def compact_drift(drift: Dict[str, Any]) -> Dict[str, Any]:
    profiles = drift.get("family_profiles") or {}
    judgements = drift.get("family_judgements") or {}

    return {
        "review_status": drift.get("review_status"),
        "severity": drift.get("severity"),
        "allowed_review_scope": drift.get("allowed_review_scope"),
        "next_action": drift.get("next_action"),
        "reason": drift.get("reason"),
        "closed": drift.get("closed"),
        "drift_remaining": drift.get("drift_remaining"),
        "capital_remaining": drift.get("capital_remaining"),
        "drift_gate_ready": drift.get("drift_gate_ready"),
        "primary_focus_family": drift.get("primary_focus_family"),
        "impulse_long_profile": profiles.get("impulse_long"),
        "impulse_long_judgement": judgements.get("impulse_long"),
        "old_short_judgement": judgements.get("old_short"),
        "market_relative_short_judgement": judgements.get("market_relative_short"),
        "weak_market_short_judgement": judgements.get("weak_market_short"),
    }


def compact_row_diag(diag: Dict[str, Any]) -> Dict[str, Any]:
    summary = diag.get("primary_summary") or {}

    # No raw trade rows included. Only summaries and aggregates.
    return {
        "diagnostic_status": diag.get("diagnostic_status"),
        "severity": diag.get("severity"),
        "allowed_scope": diag.get("allowed_scope"),
        "next_action": diag.get("next_action"),
        "reason": diag.get("reason"),
        "primary_ledger": diag.get("primary_ledger"),
        "closed": diag.get("closed"),
        "drift_remaining": diag.get("drift_remaining"),
        "capital_remaining": diag.get("capital_remaining"),
        "drift_gate_ready": diag.get("drift_gate_ready"),
        "primary_summary": {
            "available": summary.get("available"),
            "input_rows": summary.get("input_rows"),
            "impulse_rows_deduped": summary.get("impulse_rows_deduped"),
            "win_rate": summary.get("win_rate"),
            "pnl_summary": summary.get("pnl_summary"),
            "net_ret_summary": summary.get("net_ret_summary"),
            "fee_bps_summary": summary.get("fee_bps_summary"),
            "entry_slip_bps_summary": summary.get("entry_slip_bps_summary"),
            "exit_slip_bps_summary": summary.get("exit_slip_bps_summary"),
            "gross_minus_net_ret_sum_gap": summary.get("gross_minus_net_ret_sum_gap"),
            "top_loss_symbols": summary.get("top_loss_symbols"),
            "top_win_symbols": summary.get("top_win_symbols"),
            "ret3_bucket_pnl": summary.get("ret3_bucket_pnl"),
            "entry_range_bucket_pnl": summary.get("entry_range_bucket_pnl"),
            "exit_hour_pnl": summary.get("exit_hour_pnl"),
        },
        "findings": diag.get("findings"),
    }


def compact_hypotheses(hyp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generator_status": hyp.get("generator_status"),
        "severity": hyp.get("severity"),
        "allowed_scope": hyp.get("allowed_scope"),
        "next_action": hyp.get("next_action"),
        "reason": hyp.get("reason"),
        "closed": hyp.get("closed"),
        "drift_remaining": hyp.get("drift_remaining"),
        "capital_remaining": hyp.get("capital_remaining"),
        "drift_gate_ready": hyp.get("drift_gate_ready"),
        "input_summary": hyp.get("input_summary"),
        "research_hypotheses": hyp.get("research_hypotheses"),
        "research_queue": hyp.get("research_queue"),
        "ai_adapter_readiness": hyp.get("ai_adapter_readiness"),
    }


def build_prompt(packet: Dict[str, Any]) -> str:
    return f"""You are a read-only research reviewer for Edge Factory OS.

Your job:
1. Review the summarized OS state.
2. Evaluate whether the research hypotheses are logically supported by the evidence.
3. Suggest better read-only tests if needed.
4. Identify missing evidence.
5. Do NOT recommend live trading, capital change, runtime patching, family disabling, or real orders.
6. Do NOT assume raw trades are available; use only the summarized payload.
7. If drift_gate_ready is false, explicitly say no mutation is allowed.

Important safety constraints:
- runtime_mutation_allowed = false
- capital_change_allowed = false
- live_or_real_order_allowed = false
- family_disable_allowed = false
- active_paper_change_allowed = false
- output must be advisory only
- output should produce research review, not trade instructions

Expected output format:
- verdict
- supported hypotheses
- weak hypotheses
- missing evidence
- recommended read-only tests
- what must remain blocked
- concise next action

Payload:
{json.dumps(packet, indent=2, default=str)}
"""


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    cycle = load_json(CYCLE_V4_LATEST)
    drift = load_json(DRIFT_V3_LATEST)
    row_diag = load_json(ROW_DIAG_V2_LATEST)
    hypotheses = load_json(HYPOTHESIS_V1_LATEST)

    if cycle is None:
        critical.append("cycle_operator_v4_latest_missing")
        cycle = {}

    if drift is None:
        critical.append("family_drift_review_v3_latest_missing")
        drift = {}

    if row_diag is None:
        critical.append("row_level_diagnostic_v2_latest_missing")
        row_diag = {}

    if hypotheses is None:
        critical.append("research_hypothesis_generator_v1_latest_missing")
        hypotheses = {}

    packet = {
        "packet_type": "EDGE_FACTORY_OS_AI_REVIEW_PACKET_V1",
        "created_at_utc": NOW.isoformat(),
        "model_role": "read_only_research_reviewer",
        "send_raw_trades_to_api": False,
        "send_only_summarized_state": True,
        "budget_guard": "manual_call_only_initially",
        "max_monthly_budget_usd_user_stated": 30,
        "sources": {
            "cycle_operator_v4": str(CYCLE_V4_LATEST),
            "family_drift_review_v3": str(DRIFT_V3_LATEST),
            "row_level_diagnostic_v2": str(ROW_DIAG_V2_LATEST),
            "research_hypothesis_generator_v1": str(HYPOTHESIS_V1_LATEST),
        },
        "cycle_operator_v4_summary": compact_cycle(cycle),
        "family_drift_review_v3_summary": compact_drift(drift),
        "row_level_diagnostic_v2_summary": compact_row_diag(row_diag),
        "research_hypothesis_generator_v1_summary": compact_hypotheses(hypotheses),
        "safety_contract": {
            "runtime_mutation_allowed": False,
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

    drift_gate_ready = bool(
        safe_get(packet, ["research_hypothesis_generator_v1_summary", "drift_gate_ready"], False)
    )

    research_hypotheses = (
        packet.get("research_hypothesis_generator_v1_summary", {}).get("research_hypotheses") or []
    )

    if critical:
        packet_status = "AI_REVIEW_PACKET_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        next_action = "FIX_MISSING_PACKET_INPUTS"
        reason = "; ".join(critical)
    elif not research_hypotheses:
        packet_status = "AI_REVIEW_PACKET_BUILDER_NO_HYPOTHESES"
        severity = "INFO"
        next_action = "WAIT_FOR_RESEARCH_HYPOTHESES"
        reason = "no research hypotheses to review"
    elif not drift_gate_ready:
        packet_status = "AI_REVIEW_PACKET_READY_PRE_THRESHOLD"
        severity = "ATTENTION"
        next_action = "OPTIONAL_MANUAL_AI_REVIEW_OR_WAIT_FOR_DRIFT_GATE"
        reason = f"hypothesis_count={len(research_hypotheses)}; drift_gate_ready=False"
    else:
        packet_status = "AI_REVIEW_PACKET_READY_GATE_OPEN"
        severity = "ATTENTION"
        next_action = "OPTIONAL_MANUAL_AI_REVIEW_BEFORE_OFFLINE_CONTRACTS"
        reason = f"hypothesis_count={len(research_hypotheses)}; drift_gate_ready=True"

    prompt = build_prompt(packet)

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),
        "packet_status": packet_status,
        "severity": severity,
        "next_action": next_action,
        "reason": reason,
        "packet": packet,
        "prompt_path": str(LATEST_PROMPT),
        "api_call_performed": False,
        "api_key_required": False,
        "estimated_use": "manual_review_packet_only_no_cost",
        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "ai_review_packet_builder_v1_state.json"
    out_md = RUN_DIR / "ai_review_packet_builder_v1_report.md"
    out_prompt = RUN_DIR / "ai_review_prompt_v1.txt"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    out_prompt.write_text(prompt, encoding="utf-8")
    LATEST_PROMPT.write_text(prompt, encoding="utf-8")

    md = f"""# EDGE FACTORY OS AI REVIEW PACKET BUILDER v1

packet_status: {packet_status}  
severity: {severity}  
next_action: {next_action}  
reason: {reason}

api_call_performed: False  
api_key_required: False  
send_raw_trades_to_api: False  
send_only_summarized_state: True  
budget_guard: manual_call_only_initially

prompt_path: {LATEST_PROMPT}

## Safety

runtime_mutation_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: False

## Packet Preview

{json.dumps(packet, indent=2, default=str)[:12000]}

critical: {critical}  
attention: {attention}  
info: {info}
"""
    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS AI REVIEW PACKET BUILDER v1")
    print("=" * 100)
    print(f"packet_status: {packet_status}")
    print(f"severity: {severity}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("AI / COST")
    print("-" * 100)
    print("api_call_performed: False")
    print("api_key_required: False")
    print("send_raw_trades_to_api: False")
    print("send_only_summarized_state: True")
    print("budget_guard: manual_call_only_initially")
    print("estimated_use: manual_review_packet_only_no_cost")
    print()
    print("PACKET SUMMARY")
    print("-" * 100)
    print(f"cycle_status: {packet['cycle_operator_v4_summary'].get('operator_status')}")
    print(f"drift_status: {packet['family_drift_review_v3_summary'].get('review_status')}")
    print(f"row_diag_status: {packet['row_level_diagnostic_v2_summary'].get('diagnostic_status')}")
    print(f"hypothesis_status: {packet['research_hypothesis_generator_v1_summary'].get('generator_status')}")
    print(f"hypothesis_count: {len(research_hypotheses)}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print()
    print("SAFETY")
    print("-" * 100)
    print("runtime_mutation_allowed: False")
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
    print(f"latest_prompt: {LATEST_PROMPT}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
