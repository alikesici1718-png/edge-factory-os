from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_non_impulse_mean_reversion_archetype_runner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "non_impulse_mean_reversion_archetype_contract_latest.json"
)

CANONICAL_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_canonical_month_window_guard_v1"
    / "canonical_month_window_guard_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"non_impulse_mean_reversion_archetype_runner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "non_impulse_mean_reversion_archetype_runner_latest.json"
LATEST_MD = OUT_ROOT / "non_impulse_mean_reversion_archetype_runner_latest.md"

COST_BPS_TOTAL = 75.0


def load_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def fnum(v: Any, default=None):
    try:
        if v is None:
            return default
        x = float(v)
        return x if math.isfinite(x) else default
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def all_auth_false(action_guard: Dict[str, Any]) -> bool:
    auth = action_guard.get("authorization")
    if not isinstance(auth, dict):
        return False
    return all(v is False for v in auth.values())


def month_stats(monthly: Dict[str, float], canonical_months: List[str]) -> Dict[str, Any]:
    vals = []
    ordered = {}

    for month in canonical_months:
        v = fnum(monthly.get(month), None)
        ordered[month] = v
        if v is not None:
            vals.append(v)

    active = len(vals)
    positive = sum(1 for x in vals if x > 0)
    negative = sum(1 for x in vals if x < 0)
    flat = sum(1 for x in vals if x == 0)
    total = float(sum(vals)) if vals else 0.0
    mean = total / active if active else None
    positive_rate = positive / active if active else None

    return {
        "canonical_policy_month_count": len(canonical_months),
        "active_month_count": active,
        "positive_month_count": positive,
        "negative_month_count": negative,
        "flat_month_count": flat,
        "positive_month_rate": positive_rate,
        "total_net_bps": total,
        "mean_month_net_bps": mean,
        "monthly_net_bps": ordered,
        "strict_12_of_12_pass": (
            len(canonical_months) == 12
            and active == 12
            and positive == 12
            and negative == 0
            and positive_rate == 1.0
        ),
    }


def profit_factor(pnls: List[float]) -> Optional[float]:
    gross_pos = sum(x for x in pnls if x > 0)
    gross_neg = abs(sum(x for x in pnls if x < 0))
    if gross_neg == 0:
        return None if gross_pos == 0 else 999.0
    return gross_pos / gross_neg


def make_rules() -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []

    # Long mean reversion after drops / overextension.
    for ret_col in ["coin_ret3_bps", "coin_ret6_bps"]:
        for threshold in [100, 150, 200, 250, 350, 500]:
            for max_range in [None, 150, 250, 400]:
                for hold in [3, 6, 12, 24]:
                    rules.append({
                        "archetype_key": "drop_rebound_long",
                        "side": "long",
                        "ret_col": ret_col,
                        "threshold": threshold,
                        "range_max_bps": max_range,
                        "range_min_bps": None,
                        "liq_filter": None,
                        "hold_hours": hold,
                        "logic": f"{ret_col} <= -{threshold}; long rebound hold {hold}h",
                    })

    # Short mean reversion after positive overextension.
    for ret_col in ["coin_ret3_bps", "coin_ret6_bps"]:
        for threshold in [100, 150, 200, 250, 350, 500]:
            for max_range in [None, 150, 250, 400]:
                for hold in [3, 6, 12, 24]:
                    rules.append({
                        "archetype_key": "pump_reversion_short",
                        "side": "short",
                        "ret_col": ret_col,
                        "threshold": threshold,
                        "range_max_bps": max_range,
                        "range_min_bps": None,
                        "liq_filter": None,
                        "hold_hours": hold,
                        "logic": f"{ret_col} >= {threshold}; short reversion hold {hold}h",
                    })

    # Range shock reversion, both sides.
    for direction in ["drop", "pump"]:
        for ret_col in ["coin_ret3_bps", "coin_ret6_bps"]:
            for threshold in [100, 200, 350]:
                for range_min in [150, 250, 400]:
                    for hold in [3, 6, 12]:
                        rules.append({
                            "archetype_key": "range_shock_reversion_long" if direction == "drop" else "range_shock_reversion_short",
                            "side": "long" if direction == "drop" else "short",
                            "ret_col": ret_col,
                            "threshold": threshold,
                            "range_max_bps": None,
                            "range_min_bps": range_min,
                            "liq_filter": None,
                            "hold_hours": hold,
                            "logic": (
                                f"{ret_col} <= -{threshold} and range >= {range_min}; long range-shock rebound"
                                if direction == "drop"
                                else f"{ret_col} >= {threshold} and range >= {range_min}; short range-shock fade"
                            ),
                        })

    # Low liquidity shock reversion.
    for direction in ["drop", "pump"]:
        for ret_col in ["coin_ret3_bps", "coin_ret6_bps"]:
            for threshold in [150, 250, 350]:
                for hold in [3, 6, 12]:
                    rules.append({
                        "archetype_key": "low_liq_shock_reversion_long" if direction == "drop" else "low_liq_shock_reversion_short",
                        "side": "long" if direction == "drop" else "short",
                        "ret_col": ret_col,
                        "threshold": threshold,
                        "range_max_bps": None,
                        "range_min_bps": None,
                        "liq_filter": "low_liq",
                        "hold_hours": hold,
                        "logic": (
                            f"low liquidity and {ret_col} <= -{threshold}; long shock rebound"
                            if direction == "drop"
                            else f"low liquidity and {ret_col} >= {threshold}; short shock fade"
                        ),
                    })

    return rules


def apply_rule(df, rule: Dict[str, Any], liq_q25: float):
    ret_col = rule["ret_col"]
    threshold = float(rule["threshold"])

    if rule["side"] == "long":
        mask = df[ret_col] <= -threshold
    else:
        mask = df[ret_col] >= threshold

    if rule.get("range_max_bps") is not None:
        mask = mask & (df["entry_range_bps"] <= float(rule["range_max_bps"]))

    if rule.get("range_min_bps") is not None:
        mask = mask & (df["entry_range_bps"] >= float(rule["range_min_bps"]))

    if rule.get("liq_filter") == "low_liq":
        mask = mask & (df["entry_vol_quote"] <= liq_q25)

    return mask


def evaluate_rule(df, rule: Dict[str, Any], canonical_months: List[str], liq_q25: float) -> Dict[str, Any]:
    import pandas as pd

    hold = int(rule["hold_hours"])
    side = rule["side"]

    future_col = f"future_close_{hold}h"
    gross_col = f"gross_{side}_{hold}h_bps"
    net_col = f"net_{side}_{hold}h_bps"

    dfx = df.copy()
    dfx[future_col] = dfx.groupby("symbol")["close"].shift(-hold)

    long_gross = ((dfx[future_col] / dfx["close"]) - 1.0) * 10000.0
    if side == "long":
        dfx[gross_col] = long_gross
    else:
        dfx[gross_col] = -long_gross

    dfx[net_col] = dfx[gross_col] - COST_BPS_TOTAL

    mask = apply_rule(dfx, rule, liq_q25)
    trades = dfx[mask].dropna(subset=[net_col]).copy()

    if len(trades) == 0:
        return {
            "rule": rule,
            "run_ok": False,
            "reason": "no_trades",
        }

    monthly = trades.groupby("month")[net_col].sum().to_dict()
    mstats = month_stats(monthly, canonical_months)

    pnls = [float(x) for x in trades[net_col].dropna().tolist()]
    wins = sum(1 for x in pnls if x > 0)
    losses = sum(1 for x in pnls if x < 0)
    win_rate = wins / len(pnls) if pnls else None
    pf = profit_factor(pnls)

    symbol_pnl = (
        trades.groupby("symbol")[net_col]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    top_symbol_pnl = list(symbol_pnl.items())[:10]
    worst_symbol_pnl = list(symbol_pnl.items())[-10:]

    total = float(sum(pnls))
    mean = total / len(pnls) if pnls else None

    # Preview score: not release. Strict 12/12 dominates, then positive months, PF, sample.
    score = 0.0
    score += 5000 if mstats["strict_12_of_12_pass"] else 0
    score += (mstats["positive_month_count"] or 0) * 300
    score -= (mstats["negative_month_count"] or 0) * 350
    score += min(len(pnls), 3000) * 0.2
    score += max(total, -50000) * 0.02
    score += (pf or 0) * 100 if pf is not None and pf < 900 else 0
    score += (win_rate or 0) * 300

    return {
        "rule": rule,
        "run_ok": True,
        "trade_count": int(len(trades)),
        "symbol_count": int(trades["symbol"].nunique()),
        "all_total_net_bps": total,
        "all_mean_net_bps": mean,
        "win_rate": win_rate,
        "profit_factor": pf,
        "wins": wins,
        "losses": losses,
        "month_stats": mstats,
        "top_symbol_pnl": top_symbol_pnl,
        "worst_symbol_pnl": worst_symbol_pnl,
        "diagnostic_score": score,
        "strict_12_of_12_preview_pass": bool(mstats["strict_12_of_12_pass"]),
        "release_quality_pass": False,
        "candidate_generation_allowed": False,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(CONTRACT_LATEST)
    canonical_guard = load_json(CANONICAL_GUARD_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)

    if not isinstance(contract, dict):
        critical.append("non_impulse_mean_reversion_contract_latest_missing")
        contract = {}

    if not isinstance(canonical_guard, dict):
        critical.append("canonical_guard_missing")
        canonical_guard = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_policy_missing")
        strict_policy = {}

    if not isinstance(action_guard, dict):
        critical.append("action_guard_missing")
        action_guard = {}

    if contract.get("research_key") != "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_SEARCH_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if canonical_guard.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical_guard.get('guard_status')}")

    canonical_months = safe_get(canonical_guard, ["month_window", "canonical_policy_months"], [])
    if not isinstance(canonical_months, list) or len(canonical_months) != 12:
        critical.append(f"canonical_months_not_12:{canonical_months}")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    if not all_auth_false(action_guard):
        critical.append("authorization_not_all_false")

    for p in [
        ["required_runner_behavior", "candidate_generation_allowed_now"],
        ["required_runner_behavior", "candidate_contract_allowed_now"],
        ["required_runner_behavior", "family_release_allowed_now"],
        ["required_runner_behavior", "runtime_change_allowed_now"],
        ["required_runner_behavior", "capital_change_allowed_now"],
    ]:
        if safe_get(contract, p) is not False:
            critical.append(f"contract_action_flag_not_false:{'.'.join(p)}")

    panel_path = safe_get(contract, ["universe_context", "panel_path"])
    panel = Path(str(panel_path)) if panel_path else None

    if panel is None or not panel.exists():
        critical.append(f"panel_not_found:{panel_path}")

    if critical:
        runner_status = "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_RUNNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CONTRACT_OR_GUARD_INPUTS"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,
            "critical": critical,
            "attention": attention,
            "info": info,
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

        dump_json(RUN_DIR / "non_impulse_mean_reversion_archetype_runner_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS NON IMPULSE MEAN REVERSION ARCHETYPE RUNNER v1")
        print("=" * 100)
        print(f"runner_status: {runner_status}")
        print(f"severity: {severity}")
        print(f"reason: {reason}")
        print(f"latest_json: {LATEST_JSON}")
        print("=" * 100)
        return 2

    import pandas as pd

    df = pd.read_parquet(panel)
    required_cols = [
        "time",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "entry_vol_quote",
        "entry_range_bps",
        "coin_ret3_bps",
        "coin_ret6_bps",
        "mkt_ret3_bps",
        "mkt_ret6_bps",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"panel_missing_required_columns:{missing}")

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    df = df.dropna(subset=["time", "symbol", "close"])
    df = df.sort_values(["symbol", "time"]).reset_index(drop=True)
    df["month"] = df["time"].dt.to_period("M").astype(str)

    liq_q25 = float(df["entry_vol_quote"].quantile(0.25))

    rules = make_rules()
    results: List[Dict[str, Any]] = []

    for i, rule in enumerate(rules, start=1):
        try:
            row = evaluate_rule(df, rule, canonical_months, liq_q25)
            row["rule_index"] = i
            results.append(row)
        except Exception as exc:
            attention.append(f"rule_eval_failed:{i}:{rule.get('archetype_key')}:{exc}")

    ok_results = [r for r in results if r.get("run_ok")]
    ok_results.sort(
        key=lambda x: (
            1 if x.get("strict_12_of_12_preview_pass") else 0,
            x.get("diagnostic_score") or 0,
        ),
        reverse=True,
    )

    strict_preview = [r for r in ok_results if r.get("strict_12_of_12_preview_pass") is True]

    scoreboard_json = RUN_DIR / "non_impulse_mean_reversion_archetype_scoreboard.json"
    scoreboard_csv = RUN_DIR / "non_impulse_mean_reversion_archetype_scoreboard.csv"

    dump_json(scoreboard_json, {"scoreboard": ok_results[:1000]})

    flat_rows = []
    for r in ok_results:
        rule = r.get("rule") or {}
        ms = r.get("month_stats") or {}
        flat_rows.append({
            "diagnostic_score": r.get("diagnostic_score"),
            "strict_12_of_12_preview_pass": r.get("strict_12_of_12_preview_pass"),
            "archetype_key": rule.get("archetype_key"),
            "side": rule.get("side"),
            "ret_col": rule.get("ret_col"),
            "threshold": rule.get("threshold"),
            "range_max_bps": rule.get("range_max_bps"),
            "range_min_bps": rule.get("range_min_bps"),
            "liq_filter": rule.get("liq_filter"),
            "hold_hours": rule.get("hold_hours"),
            "trade_count": r.get("trade_count"),
            "symbol_count": r.get("symbol_count"),
            "all_total_net_bps": r.get("all_total_net_bps"),
            "all_mean_net_bps": r.get("all_mean_net_bps"),
            "win_rate": r.get("win_rate"),
            "profit_factor": r.get("profit_factor"),
            "positive_month_count": ms.get("positive_month_count"),
            "negative_month_count": ms.get("negative_month_count"),
            "positive_month_rate": ms.get("positive_month_rate"),
            "mean_month_net_bps": ms.get("mean_month_net_bps"),
        })

    pd.DataFrame(flat_rows).to_csv(scoreboard_csv, index=False)

    if strict_preview:
        runner_status = "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_RUNNER_STRICT_PREVIEW_FOUND"
        next_action = "EVALUATE_NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_RESULTS_PREFLIGHT_ONLY"
        reason = f"rules_tested={len(rules)}; strict_12_preview_count={len(strict_preview)}"
    else:
        runner_status = "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_RUNNER_NO_STRICT_PREVIEW_FOUND"
        next_action = "EVALUATE_NON_IMPULSE_MEAN_REVERSION_RESULTS_AND_ROTATE_IF_FAILED"
        reason = f"rules_tested={len(rules)}; strict_12_preview_count=0"

    severity = "ATTENTION"
    allowed_scope = "READ_ONLY_RESEARCH"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "runner_status": runner_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "contract_source": str(CONTRACT_LATEST),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "research_key": contract.get("research_key"),

        "panel_summary": {
            "panel_path": str(panel),
            "row_count": int(len(df)),
            "symbol_count": int(df["symbol"].nunique()),
            "start": str(df["time"].min()),
            "end": str(df["time"].max()),
            "raw_month_count": int(df["month"].nunique()),
        },

        "canonical_month_window": {
            "canonical_policy_month_count": len(canonical_months),
            "canonical_policy_months": canonical_months,
            "raw_calendar_month_count": safe_get(canonical_guard, ["month_window", "raw_calendar_month_count"]),
            "boundary_partial_months": safe_get(canonical_guard, ["month_window", "boundary_partial_months"]),
        },

        "strict_policy": {
            "policy_key": strict_policy.get("policy_key"),
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"]),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"]),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"]),
        },

        "search_summary": {
            "rules_tested": len(rules),
            "ok_result_count": len(ok_results),
            "strict_12_preview_count": len(strict_preview),
            "archetype_keys_tested": sorted(set(r.get("rule", {}).get("archetype_key") for r in ok_results)),
        },

        "top_results": ok_results[:40],
        "strict_12_preview_results": strict_preview[:20],

        "outputs": {
            "scoreboard_json": str(scoreboard_json),
            "scoreboard_csv": str(scoreboard_csv),
        },

        "release_gate_feed": {
            "NON_IMPULSE_MEAN_REVERSION_ARCHETYPE_RUNNER_RAN": True,
            "CANONICAL_MONTH_WINDOW_CONSUMED": True,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12",
            "RULES_TESTED": len(rules),
            "STRICT_12_OF_12_PREVIEW_FOUND": bool(strict_preview),
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "ACTIVE_PAPER_ALLOWED": False,
            "LIVE_ALLOWED": False,
            "REAL_ORDERS_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_RUNNER": False,
            "status": runner_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "active_paper_recommended": False,
            "live_or_real_order_recommended": False,
            "next_module": "edge_factory_os_non_impulse_mean_reversion_archetype_evaluator_v1.py",
            "why_no_action": [
                "runner_is_research_only",
                "strict_preview_if_any_requires_evaluator_and_full_chain",
                "action_prerequisite_guard_blocks_all_actions",
                "no_runtime_or_capital_action_allowed",
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
            "execution_performed": True,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "non_impulse_mean_reversion_archetype_runner_v1_state.json"
    out_md = RUN_DIR / "non_impulse_mean_reversion_archetype_runner_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS NON IMPULSE MEAN REVERSION ARCHETYPE RUNNER v1

runner_status: {runner_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Search Summary

{json.dumps(result["search_summary"], indent=2, default=str)}

## Top Results

{json.dumps(ok_results[:20], indent=2, default=str)[:24000]}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Decision

{json.dumps(result["decision"], indent=2, default=str)}

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
execution_performed: True

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS NON IMPULSE MEAN REVERSION ARCHETYPE RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {runner_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("SEARCH SUMMARY")
    print("-" * 100)
    print(json.dumps(result["search_summary"], indent=2, default=str))
    print()
    print("TOP RESULTS")
    print("-" * 100)
    for row in ok_results[:10]:
        rule = row.get("rule", {})
        ms = row.get("month_stats", {})
        print({
            "score": row.get("diagnostic_score"),
            "archetype": rule.get("archetype_key"),
            "side": rule.get("side"),
            "ret_col": rule.get("ret_col"),
            "threshold": rule.get("threshold"),
            "hold": rule.get("hold_hours"),
            "trades": row.get("trade_count"),
            "total": row.get("all_total_net_bps"),
            "pf": row.get("profit_factor"),
            "win_rate": row.get("win_rate"),
            "positive_months": ms.get("positive_month_count"),
            "negative_months": ms.get("negative_month_count"),
            "strict_12": row.get("strict_12_of_12_preview_pass"),
        })
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
    print()
    print("DECISION")
    print("-" * 100)
    print(json.dumps(result["decision"], indent=2, default=str))
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
    print("execution_performed: True")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
