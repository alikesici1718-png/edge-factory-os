from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_full_universe_offline_backtest_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

BACKTEST_LATEST = (
    BASE_DIR
    / "edge_factory_os_full_universe_offline_backtest_v1"
    / "full_universe_offline_backtest_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"full_universe_offline_backtest_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "full_universe_offline_backtest_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "full_universe_offline_backtest_evaluator_latest.md"


RELEASE_MIN_ALL_TRADES = 300
RELEASE_MIN_OOS_TRADES = 75
RELEASE_MIN_TRAIN_MEAN_BPS = 0.0
RELEASE_MIN_OOS_MEAN_BPS = 0.0
RELEASE_MIN_ALL_MEAN_BPS = 0.0
RELEASE_MIN_TRAIN_PF = 1.10
RELEASE_MIN_OOS_PF = 1.10
RELEASE_MIN_OOS_WIN_RATE = 0.45
RELEASE_MIN_ALL_POSITIVE_MONTH_RATE = 0.55
RELEASE_MIN_OOS_POSITIVE_MONTH_RATE = 0.50


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


def fnum(v: Any, default=None):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def inum(v: Any, default=0):
    try:
        if v is None:
            return default
        return int(float(v))
    except Exception:
        return default


def eval_candidate(row: Dict[str, Any]) -> Dict[str, Any]:
    all_s = row.get("summary_all") or {}
    train_s = row.get("summary_train") or {}
    oos_s = row.get("summary_oos") or {}

    checks = {}

    all_trades = inum(all_s.get("trade_count"))
    oos_trades = inum(oos_s.get("trade_count"))

    all_mean = fnum(all_s.get("mean_net_bps"))
    train_mean = fnum(train_s.get("mean_net_bps"))
    oos_mean = fnum(oos_s.get("mean_net_bps"))

    train_pf = fnum(train_s.get("profit_factor"))
    oos_pf = fnum(oos_s.get("profit_factor"))

    oos_wr = fnum(oos_s.get("win_rate"))

    all_pos_month = fnum(all_s.get("positive_month_rate"))
    oos_pos_month = fnum(oos_s.get("positive_month_rate"))

    checks["all_trade_count"] = {
        "pass": all_trades >= RELEASE_MIN_ALL_TRADES,
        "value": all_trades,
        "required": RELEASE_MIN_ALL_TRADES,
    }

    checks["oos_trade_count"] = {
        "pass": oos_trades >= RELEASE_MIN_OOS_TRADES,
        "value": oos_trades,
        "required": RELEASE_MIN_OOS_TRADES,
    }

    checks["all_mean_positive"] = {
        "pass": all_mean is not None and all_mean > RELEASE_MIN_ALL_MEAN_BPS,
        "value": all_mean,
        "required": f">{RELEASE_MIN_ALL_MEAN_BPS}",
    }

    checks["train_mean_positive"] = {
        "pass": train_mean is not None and train_mean > RELEASE_MIN_TRAIN_MEAN_BPS,
        "value": train_mean,
        "required": f">{RELEASE_MIN_TRAIN_MEAN_BPS}",
    }

    checks["oos_mean_positive"] = {
        "pass": oos_mean is not None and oos_mean > RELEASE_MIN_OOS_MEAN_BPS,
        "value": oos_mean,
        "required": f">{RELEASE_MIN_OOS_MEAN_BPS}",
    }

    checks["train_profit_factor"] = {
        "pass": train_pf is not None and train_pf >= RELEASE_MIN_TRAIN_PF,
        "value": train_pf,
        "required": RELEASE_MIN_TRAIN_PF,
    }

    checks["oos_profit_factor"] = {
        "pass": oos_pf is not None and oos_pf >= RELEASE_MIN_OOS_PF,
        "value": oos_pf,
        "required": RELEASE_MIN_OOS_PF,
    }

    checks["oos_win_rate"] = {
        "pass": oos_wr is not None and oos_wr >= RELEASE_MIN_OOS_WIN_RATE,
        "value": oos_wr,
        "required": RELEASE_MIN_OOS_WIN_RATE,
    }

    checks["all_positive_month_rate"] = {
        "pass": all_pos_month is not None and all_pos_month >= RELEASE_MIN_ALL_POSITIVE_MONTH_RATE,
        "value": all_pos_month,
        "required": RELEASE_MIN_ALL_POSITIVE_MONTH_RATE,
    }

    checks["oos_positive_month_rate"] = {
        "pass": oos_pos_month is not None and oos_pos_month >= RELEASE_MIN_OOS_POSITIVE_MONTH_RATE,
        "value": oos_pos_month,
        "required": RELEASE_MIN_OOS_POSITIVE_MONTH_RATE,
    }

    failed = [k for k, v in checks.items() if not v["pass"]]
    passed = [k for k, v in checks.items() if v["pass"]]

    return {
        "candidate_id": row.get("candidate_id"),
        "candidate_quality_release_pass": len(failed) == 0,
        "passed_checks": passed,
        "failed_checks": failed,
        "check_detail": checks,
        "summary_all": all_s,
        "summary_train": train_s,
        "summary_oos": oos_s,
        "symbol_concentration": row.get("symbol_concentration"),
        "params": {
            "threshold_coin_ret3_bps": row.get("threshold_coin_ret3_bps"),
            "hold_hours": row.get("hold_hours"),
            "entry_range_cap_bps": row.get("entry_range_cap_bps"),
            "mkt_filter": row.get("mkt_filter"),
            "cost_bps_total": row.get("cost_bps_total"),
        },
    }


def reason_counts(evals: List[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for e in evals:
        for r in e.get("failed_checks") or []:
            out[r] = out.get(r, 0) + 1
    return dict(sorted(out.items(), key=lambda x: x[1], reverse=True))


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    state = load_json(BACKTEST_LATEST)

    if state is None:
        critical.append("full_universe_backtest_latest_missing_or_unreadable")
        state = {}

    backtest_status = state.get("backtest_status")

    if backtest_status != "FULL_UNIVERSE_OFFLINE_BACKTEST_COMPLETE":
        critical.append(f"full_universe_backtest_not_complete:{backtest_status}")

    ranked = state.get("ranked_top_20") or []

    # Prefer full ranked path if available, not only top 20.
    ranked_path = state.get("ranked_candidates_path")
    full_ranked = ranked

    if ranked_path:
        path = Path(str(ranked_path))
        obj = load_json(path)
        if obj and isinstance(obj.get("ranked"), list):
            full_ranked = obj["ranked"]

    evaluated = [eval_candidate(row) for row in full_ranked]
    pass_candidates = [e for e in evaluated if e.get("candidate_quality_release_pass") is True]

    top_evaluated = evaluated[:20]
    top_pass_candidates = pass_candidates[:20]

    failed_reason_counts = reason_counts(evaluated)

    full_universe_backtest_pass = len(pass_candidates) > 0

    best_candidate = evaluated[0] if evaluated else None
    best_pass_candidate = pass_candidates[0] if pass_candidates else None

    findings = []

    if not full_universe_backtest_pass:
        findings.append({
            "finding_id": "FULL_UNIVERSE_F1_NO_RELEASE_QUALITY_CANDIDATE",
            "severity": "HIGH",
            "claim": "No full-universe candidate satisfied strict release criteria.",
            "evidence": {
                "evaluated_candidate_count": len(evaluated),
                "release_pass_candidate_count": len(pass_candidates),
                "failed_reason_counts": failed_reason_counts,
                "backtest_reason": state.get("reason"),
            },
            "release_gate_effect": "BLOCK_FULL_UNIVERSE_OFFLINE_BACKTEST_PASS",
        })

    if best_candidate:
        findings.append({
            "finding_id": "FULL_UNIVERSE_F2_BEST_RANKED_CANDIDATE_STILL_HAS_FAILURES",
            "severity": "MEDIUM_HIGH",
            "claim": "Best ranked candidate still fails one or more required release checks.",
            "evidence": {
                "candidate_id": best_candidate.get("candidate_id"),
                "failed_checks": best_candidate.get("failed_checks"),
                "summary_all": best_candidate.get("summary_all"),
                "summary_train": best_candidate.get("summary_train"),
                "summary_oos": best_candidate.get("summary_oos"),
            },
            "release_gate_effect": "CONTINUE_BLOCK",
        })

    if critical:
        evaluator_status = "FULL_UNIVERSE_BACKTEST_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_FULL_UNIVERSE_BACKTEST_INPUT"
        reason = "; ".join(critical)

    elif full_universe_backtest_pass:
        evaluator_status = "FULL_UNIVERSE_BACKTEST_EVALUATOR_PASS"
        severity = "OK"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "FEED_PASS_TO_RELEASE_GATE_AND_RUN_OOS_MONTH_STABILITY_VALIDATORS"
        reason = f"pass_candidate_count={len(pass_candidates)}"

    else:
        evaluator_status = "FULL_UNIVERSE_BACKTEST_EVALUATOR_NO_RELEASE_CANDIDATE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BLOCK_RELEASE_AND_RECORD_FULL_UNIVERSE_FAILURE_LESSON"
        reason = f"evaluated_candidate_count={len(evaluated)}; pass_candidate_count=0"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "backtest_source": str(BACKTEST_LATEST),
        "backtest_status": backtest_status,

        "panel_path": state.get("panel_path"),
        "panel_rows": state.get("panel_rows"),
        "panel_symbol_count": state.get("panel_symbol_count"),
        "panel_start": state.get("panel_start"),
        "panel_end": state.get("panel_end"),

        "evaluated_candidate_count": len(evaluated),
        "release_pass_candidate_count": len(pass_candidates),
        "failed_reason_counts": failed_reason_counts,

        "best_candidate": best_candidate,
        "best_pass_candidate": best_pass_candidate,
        "top_evaluated_candidates": top_evaluated,
        "top_pass_candidates": top_pass_candidates,

        "release_gate_feed": {
            "FULL_UNIVERSE_OFFLINE_BACKTEST_PASS": full_universe_backtest_pass,
            "status": evaluator_status,
            "evaluated_candidate_count": len(evaluated),
            "release_pass_candidate_count": len(pass_candidates),
            "release_allowed_from_this_test_alone": False,
        },

        "findings": findings,

        "decision": {
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "family_disable_recommended": False,
            "live_or_real_order_recommended": False,
            "why_no_action": [
                "no_full_universe_release_quality_candidate",
                "OOS_and_month_stability_still_required_even_if_a_candidate_passes_later",
                "release_gate_remains_blocked",
            ],
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

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "full_universe_offline_backtest_evaluator_v1_state.json"
    out_md = RUN_DIR / "full_universe_offline_backtest_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FULL UNIVERSE OFFLINE BACKTEST EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

panel_path: {state.get("panel_path")}  
panel_rows: {state.get("panel_rows")}  
panel_symbol_count: {state.get("panel_symbol_count")}  
panel_start: {state.get("panel_start")}  
panel_end: {state.get("panel_end")}

evaluated_candidate_count: {len(evaluated)}  
release_pass_candidate_count: {len(pass_candidates)}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Failed Reason Counts

{json.dumps(failed_reason_counts, indent=2, default=str)}

## Best Candidate

{json.dumps(best_candidate, indent=2, default=str)[:16000]}

## Findings

{json.dumps(findings, indent=2, default=str)}

## Decision

runtime_change_recommended: False  
capital_change_recommended: False  
family_disable_recommended: False  
live_or_real_order_recommended: False

## Safety

read_only: True  
offline_only: True  
mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: False

critical: {critical}  
attention: {attention}  
info: {info}
"""
    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS FULL UNIVERSE OFFLINE BACKTEST EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("PANEL")
    print("-" * 100)
    print(f"panel_path: {state.get('panel_path')}")
    print(f"panel_rows: {state.get('panel_rows')}")
    print(f"panel_symbol_count: {state.get('panel_symbol_count')}")
    print(f"panel_start: {state.get('panel_start')}")
    print(f"panel_end: {state.get('panel_end')}")
    print()
    print("EVALUATION SUMMARY")
    print("-" * 100)
    print(f"evaluated_candidate_count: {len(evaluated)}")
    print(f"release_pass_candidate_count: {len(pass_candidates)}")
    print(f"failed_reason_counts: {failed_reason_counts}")
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
    print()
    print("BEST CANDIDATE")
    print("-" * 100)
    print(json.dumps(best_candidate, indent=2, default=str)[:8000])
    print()
    print("FINDINGS")
    print("-" * 100)
    for f in findings:
        print(f)
    print()
    print("DECISION")
    print("-" * 100)
    print("runtime_change_recommended: False")
    print("capital_change_recommended: False")
    print("family_disable_recommended: False")
    print("live_or_real_order_recommended: False")
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
