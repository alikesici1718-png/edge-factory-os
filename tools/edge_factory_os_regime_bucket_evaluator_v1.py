from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_regime_bucket_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

REGIME_DIAG_LATEST = (
    BASE_DIR
    / "edge_factory_os_regime_bucket_diagnostic_v1"
    / "regime_bucket_diagnostic_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"regime_bucket_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "regime_bucket_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "regime_bucket_evaluator_latest.md"


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


def summary_total(summary: Dict[str, Any]) -> Optional[float]:
    return fnum(summary.get("total_pnl"))


def summary_wr(summary: Dict[str, Any]) -> Optional[float]:
    return fnum(summary.get("win_rate"))


def summary_count(summary: Dict[str, Any]) -> int:
    return inum(summary.get("trade_count"))


def pick_best_filter(filters: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    valid = []

    for row in filters:
        summary = row.get("selected_summary") or {}
        total = summary_total(summary)

        if total is None:
            continue

        valid.append(row)

    if not valid:
        return None

    return sorted(
        valid,
        key=lambda r: (
            summary_total(r.get("selected_summary") or {}) or -999999,
            summary_count(r.get("selected_summary") or {}),
        ),
        reverse=True,
    )[0]


def find_filter(filters: List[Dict[str, Any]], filter_id: str) -> Optional[Dict[str, Any]]:
    for row in filters:
        if row.get("filter_id") == filter_id:
            return row
    return None


def evaluate_symbol_dependence(selected_summary: Dict[str, Any]) -> Dict[str, Any]:
    top_win_symbols = selected_summary.get("top_win_symbols") or []
    total = summary_total(selected_summary)

    if not top_win_symbols or total in [None, 0]:
        return {
            "symbol_dependence_detected": False,
            "reason": "no_top_win_symbol_or_zero_total",
        }

    top = top_win_symbols[0]

    if not isinstance(top, (list, tuple)) or len(top) < 2:
        return {
            "symbol_dependence_detected": False,
            "reason": "top_win_symbol_unparseable",
        }

    symbol = top[0]
    symbol_pnl = fnum(top[1], 0.0) or 0.0

    share = abs(symbol_pnl) / max(abs(total), 1e-9)

    return {
        "symbol_dependence_detected": share >= 0.70,
        "top_win_symbol": symbol,
        "top_win_symbol_pnl": symbol_pnl,
        "selected_total_pnl": total,
        "top_win_share_abs": share,
        "threshold": 0.70,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    diag = load_json(REGIME_DIAG_LATEST)

    if diag is None:
        critical.append("regime_diagnostic_latest_missing_or_unreadable")
        diag = {}

    diagnostic_status = diag.get("diagnostic_status")
    diagnostic_result = diag.get("diagnostic_result") or {}

    if diagnostic_status != "REGIME_BUCKET_DIAGNOSTIC_COMPLETE":
        critical.append(f"regime_diagnostic_not_complete:{diagnostic_status}")

    baseline = diagnostic_result.get("baseline") or {}
    filters = diagnostic_result.get("candidate_filter_results") or []
    bucket_tables = diagnostic_result.get("bucket_tables") or {}
    available_columns = diagnostic_result.get("available_columns_inferred") or {}

    baseline_count = summary_count(baseline)
    baseline_total = summary_total(baseline)
    baseline_wr = summary_wr(baseline)

    best_filter = pick_best_filter(filters)
    signal_250 = find_filter(filters, "signal_ret3_ge_250")
    signal_300 = find_filter(filters, "signal_ret3_ge_300")

    findings = []

    regime_bucket_pass = False
    promising_filter_found = False
    release_block_reasons = []

    if best_filter:
        selected = best_filter.get("selected_summary") or {}
        excluded = best_filter.get("excluded_summary") or {}

        selected_count = summary_count(selected)
        selected_total = summary_total(selected)
        selected_wr = summary_wr(selected)

        excluded_total = summary_total(excluded)
        excluded_wr = summary_wr(excluded)

        if (
            selected_total is not None
            and baseline_total is not None
            and selected_total > baseline_total
            and selected_total > 0
        ):
            promising_filter_found = True

            findings.append({
                "finding_id": "REGIME_F1_PROMISING_SIGNAL_FILTER",
                "severity": "MEDIUM_HIGH",
                "claim": "A candidate regime/signal filter improved current paper sample performance.",
                "evidence": {
                    "filter_id": best_filter.get("filter_id"),
                    "description": best_filter.get("description"),
                    "baseline_total_pnl": baseline_total,
                    "baseline_win_rate": baseline_wr,
                    "baseline_trade_count": baseline_count,
                    "selected_total_pnl": selected_total,
                    "selected_win_rate": selected_wr,
                    "selected_trade_count": selected_count,
                    "excluded_total_pnl": excluded_total,
                    "excluded_win_rate": excluded_wr,
                },
                "release_gate_effect": "PROMISING_BUT_NOT_PASS",
            })

        if selected_count < 50:
            release_block_reasons.append("selected_sample_below_release_minimum")
            findings.append({
                "finding_id": "REGIME_F2_SELECTED_SAMPLE_TOO_SMALL",
                "severity": "CONTROL",
                "claim": "Best selected regime bucket sample is too small for release.",
                "evidence": {
                    "selected_trade_count": selected_count,
                    "required_release_minimum": 50,
                },
                "release_gate_effect": "BLOCK_REGIME_BUCKET_PASS",
            })

        sym_dep = evaluate_symbol_dependence(selected)

        if sym_dep.get("symbol_dependence_detected"):
            release_block_reasons.append("selected_result_symbol_dependent")
            findings.append({
                "finding_id": "REGIME_F3_SELECTED_RESULT_SYMBOL_DEPENDENT",
                "severity": "MEDIUM_HIGH",
                "claim": "Best selected regime result appears dependent on one top winning symbol.",
                "evidence": sym_dep,
                "release_gate_effect": "BLOCK_SYMBOL_CONCENTRATION_PASS",
            })

        if selected_wr is not None and selected_wr < 0.55:
            release_block_reasons.append("selected_win_rate_below_release_threshold")
            findings.append({
                "finding_id": "REGIME_F4_SELECTED_WIN_RATE_NOT_STRONG_ENOUGH",
                "severity": "MEDIUM",
                "claim": "Best selected regime win rate is not high enough for release.",
                "evidence": {
                    "selected_win_rate": selected_wr,
                    "required_release_win_rate": 0.55,
                },
                "release_gate_effect": "BLOCK_REGIME_BUCKET_PASS",
            })

    else:
        release_block_reasons.append("no_valid_filter_result")
        findings.append({
            "finding_id": "REGIME_F0_NO_VALID_FILTER",
            "severity": "HIGH",
            "claim": "No valid candidate filter result was found.",
            "evidence": {},
            "release_gate_effect": "BLOCK_REGIME_BUCKET_PASS",
        })

    missing_market_columns = []
    for col in ["mkt_ret3_bps", "mkt_ret6_bps", "signal_ret6_bps"]:
        if available_columns.get(col) is not True:
            missing_market_columns.append(col)

    if missing_market_columns:
        release_block_reasons.append("missing_market_or_signal_columns")
        findings.append({
            "finding_id": "REGIME_F5_MISSING_MARKET_OR_SIGNAL_COLUMNS",
            "severity": "ATTENTION",
            "claim": "Regime diagnostic is limited by missing market/signal columns in current ledger.",
            "evidence": {
                "available_columns": available_columns,
                "missing_columns": missing_market_columns,
            },
            "release_gate_effect": "BLOCK_FULL_REGIME_CONFIDENCE",
        })

    # Strict release pass requires large sample, positive selected performance, non-symbol-dependent,
    # sufficient win rate, and all major regime fields.
    if best_filter:
        selected = best_filter.get("selected_summary") or {}
        selected_count = summary_count(selected)
        selected_total = summary_total(selected)
        selected_wr = summary_wr(selected)
        sym_dep = evaluate_symbol_dependence(selected)

        if (
            selected_total is not None and selected_total > 0
            and selected_count >= 50
            and selected_wr is not None and selected_wr >= 0.55
            and not sym_dep.get("symbol_dependence_detected")
            and not missing_market_columns
        ):
            regime_bucket_pass = True

    if critical:
        evaluator_status = "REGIME_BUCKET_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_REGIME_DIAGNOSTIC_INPUT"
        reason = "; ".join(critical)

    elif regime_bucket_pass:
        evaluator_status = "REGIME_BUCKET_EVALUATOR_PASS"
        severity = "OK"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "FEED_PASS_TO_RELEASE_GATE_BUT_DO_NOT_RELEASE_ALONE"
        reason = "regime bucket diagnostic passed strict release criteria"

    elif promising_filter_found:
        evaluator_status = "REGIME_BUCKET_EVALUATOR_PROMISING_BUT_NOT_RELEASE_PASS"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BLOCK_RELEASE_AND_REQUIRE_FULL_UNIVERSE_OOS_CONFIRMATION"
        reason = "promising filter found but release blockers remain"

    else:
        evaluator_status = "REGIME_BUCKET_EVALUATOR_FAIL_OR_INCONCLUSIVE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BLOCK_RELEASE_AND_CONTINUE_RESEARCH"
        reason = "no release-quality regime bucket found"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "regime_diagnostic_source": str(REGIME_DIAG_LATEST),
        "diagnostic_status": diagnostic_status,

        "baseline": {
            "trade_count": baseline_count,
            "win_rate": baseline_wr,
            "total_pnl": baseline_total,
        },

        "available_columns": available_columns,
        "best_filter": best_filter,
        "signal_ret3_ge_250": signal_250,
        "signal_ret3_ge_300": signal_300,

        "release_gate_feed": {
            "REGIME_BUCKET_DIAGNOSTIC_PASS": regime_bucket_pass,
            "status": evaluator_status,
            "promising_filter_found": promising_filter_found,
            "release_block_reasons": sorted(list(set(release_block_reasons))),
            "release_allowed_from_regime_test_alone": False,
        },

        "findings": findings,

        "decision": {
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "family_disable_recommended": False,
            "live_or_real_order_recommended": False,
            "why_no_action": [
                "selected_sample_too_small",
                "symbol_dependence_risk",
                "missing_market_regime_columns",
                "full_universe_offline_backtest_required",
                "OOS_and_month_stability_required",
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

    out_json = RUN_DIR / "regime_bucket_evaluator_v1_state.json"
    out_md = RUN_DIR / "regime_bucket_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS REGIME BUCKET EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Baseline

{json.dumps(result["baseline"], indent=2, default=str)}

## Best Filter

{json.dumps(best_filter, indent=2, default=str)}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

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
    print("EDGE FACTORY OS REGIME BUCKET EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("BASELINE")
    print("-" * 100)
    print(result["baseline"])
    print()
    print("BEST FILTER")
    print("-" * 100)
    print(json.dumps(best_filter, indent=2, default=str))
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
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
