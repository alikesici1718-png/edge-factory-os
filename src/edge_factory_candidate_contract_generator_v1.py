#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_candidate_contract_generator_v1"

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def slugify(x: str) -> str:
    x = x.strip().lower()
    x = re.sub(r"[^a-z0-9_]+", "_", x)
    x = re.sub(r"_+", "_", x).strip("_")
    return x or "unnamed_candidate"

def split_csv(x: str) -> list[str]:
    return [a.strip() for a in x.split(",") if a.strip()]

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate an Edge Factory offline experiment contract draft from a human idea.")
    ap.add_argument("--candidate_key", default="")
    ap.add_argument("--family_key", default="")
    ap.add_argument("--side", default="short", choices=["long", "short", "both"])
    ap.add_argument("--edge", default="")
    ap.add_argument("--regime", default="")
    ap.add_argument("--why", default="")
    ap.add_argument("--failure_modes", default="")
    ap.add_argument("--universe", default="OKX USDT swaps ready universe")
    ap.add_argument("--timeframe", default="1h candles")
    ap.add_argument("--lookback_window", default="")
    ap.add_argument("--source_files", default="")
    ap.add_argument("--required_columns", default="")
    ap.add_argument("--entry_rule", default="")
    ap.add_argument("--exit_rule", default="")
    ap.add_argument("--hold_time", default="")
    ap.add_argument("--cooldown", default="")
    ap.add_argument("--max_signals_per_symbol", type=int, default=1)
    ap.add_argument("--max_signals_per_time_bucket", type=int, default=1)
    ap.add_argument("--entry_price_model", default="next_bar_open_or_close_defined_by_runner")
    ap.add_argument("--exit_price_model", default="planned_exit_bar_close")
    ap.add_argument("--fee_bps", type=float, default=5.0)
    ap.add_argument("--slippage_bps", type=float, default=20.0)
    ap.add_argument("--funding_handling", default="ignored unless strategy hold crosses funding and funding data is available")
    ap.add_argument("--in_sample_period", default="")
    ap.add_argument("--out_of_sample_period", default="")
    ap.add_argument("--walk_forward_folds", type=int, default=4)
    ap.add_argument("--max_drawdown_proxy", type=float, default=0.0)
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"candidate_contract_generator_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    schema_dir = latest_dir(WORKSPACE / "edge_factory_offline_experiment_contract_schema_v1", "offline_experiment_contract_schema_v1_")
    template_path = schema_dir / "offline_experiment_contract_template_v1.json" if schema_dir else None
    policy_path = schema_dir / "candidate_validation_gate_policy_v1.json" if schema_dir else None

    template = read_json(template_path)
    policy = read_json(policy_path)

    has_minimum_idea = bool(args.candidate_key and args.family_key and args.edge and args.entry_rule and args.exit_rule and args.hold_time)

    intake = {
        "intake_version": "edge_factory_candidate_idea_intake_v1",
        "created_at": now_iso(),
        "required_to_generate_contract": [
            "candidate_key",
            "family_key",
            "side",
            "plain_english_edge",
            "entry_rule",
            "exit_rule",
            "hold_time"
        ],
        "recommended": [
            "expected_regime",
            "why_it_should_work",
            "failure_modes",
            "required_columns",
            "source_files",
            "lookback_window",
            "cooldown"
        ],
        "example_command": (
            'python -u "C:\\Users\\alike\\edge_factory_candidate_contract_generator_v1.py" '
            '--candidate_key "example_reversal_short" '
            '--family_key "relative_reversal" '
            '--side short '
            '--edge "Coin pumps far above market over 6h and tends to mean-revert over 24h." '
            '--entry_rule "coin_ret6_bps >= 300 and rel_ret_bps >= 600" '
            '--exit_rule "fixed_hold_24h" '
            '--hold_time "24h" '
            '--required_columns "coin_ret6_bps,rel_ret_bps,close,time,symbol"'
        ),
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False
    }

    state: dict[str, Any] = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "generator_status": "",
        "template_path": str(template_path) if template_path else None,
        "policy_path": str(policy_path) if policy_path else None,
        "contract_path": "",
        "intake_path": "",
        "candidate_key": args.candidate_key,
        "family_key": args.family_key,
        "has_minimum_idea": has_minimum_idea,
        "validator_command": "",
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Generator only writes candidate contract drafts.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not promote candidates.",
            "Does not place orders.",
            "Does not enable live trading."
        ]
    }

    intake_path = out_dir / "candidate_idea_intake_form_v1.json"
    intake_path.write_text(json.dumps(intake, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    state["intake_path"] = str(intake_path)

    contract_path = None

    if not template or "__read_error__" in template:
        state["generator_status"] = "CONTRACT_GENERATOR_BLOCKED_TEMPLATE_MISSING_OR_INVALID"
    elif not has_minimum_idea:
        state["generator_status"] = "CONTRACT_GENERATOR_READY_NEEDS_IDEA"
    else:
        contract = deepcopy(template)

        candidate_key = slugify(args.candidate_key)
        family_key = slugify(args.family_key)

        total_cost_bps = float(args.fee_bps) + float(args.slippage_bps)

        contract["identity"] = {
            "candidate_key": candidate_key,
            "family_key": family_key,
            "side": args.side,
            "created_at": now_iso(),
            "owner": "Ali"
        }

        contract["hypothesis"] = {
            "plain_english_edge": args.edge,
            "expected_regime": args.regime,
            "why_it_should_work": args.why,
            "failure_modes": split_csv(args.failure_modes) if args.failure_modes else [
                "edge is regime-specific",
                "costs/slippage may erase expectancy",
                "signal may be duplicate/stale",
                "edge may concentrate in few symbols or months"
            ]
        }

        contract["data_contract"] = {
            "universe": args.universe,
            "timeframe": args.timeframe,
            "lookback_window": args.lookback_window,
            "source_files": split_csv(args.source_files),
            "required_columns": split_csv(args.required_columns),
            "ready_universe_filter": True,
            "deduplication_policy": "candidate_key + symbol + signal_time must be unique"
        }

        contract["signal_contract"] = {
            "entry_rule": args.entry_rule,
            "exit_rule": args.exit_rule,
            "hold_time": args.hold_time,
            "cooldown": args.cooldown,
            "max_signals_per_symbol": args.max_signals_per_symbol,
            "max_signals_per_time_bucket": args.max_signals_per_time_bucket,
            "no_lookahead_statement": "All features must be known at or before signal_time."
        }

        contract["execution_assumptions"] = {
            "entry_price_model": args.entry_price_model,
            "exit_price_model": args.exit_price_model,
            "slippage_bps": args.slippage_bps,
            "latency_assumption": "offline test must use next available bar or explicitly documented signal_time price",
            "liquidity_filter": "must be defined before runner execution",
            "spread_filter": "must be defined before runner execution"
        }

        contract["cost_model"] = {
            "fee_bps": args.fee_bps,
            "slippage_bps": args.slippage_bps,
            "total_cost_bps": total_cost_bps,
            "funding_handling": args.funding_handling
        }

        contract["validation_plan"] = {
            "in_sample_period": args.in_sample_period,
            "out_of_sample_period": args.out_of_sample_period,
            "walk_forward_folds": args.walk_forward_folds,
            "market_replay_required": True,
            "symbol_oos_required": True,
            "month_stability_required": True,
            "parameter_robustness_required": True
        }

        # Keep policy thresholds if available.
        thresholds = policy.get("minimum_thresholds", {}) if isinstance(policy, dict) else {}

        contract["promotion_gates"] = {
            "min_trades": int(thresholds.get("offline_min_trades", 300)),
            "min_symbols": int(thresholds.get("offline_min_symbols", 20)),
            "min_positive_month_rate": float(thresholds.get("monthly_positive_rate_min", 0.55)),
            "min_walk_forward_pass_rate": float(thresholds.get("walk_forward_min_positive_fold_rate", 0.60)),
            "min_profit_factor": float(thresholds.get("profit_factor_min", 1.10)),
            "max_drawdown_proxy": args.max_drawdown_proxy,
            "market_replay_pass_required": True,
            "shadow_runtime_required": True,
            "shadow_duplicate_guard_required": True,
            "manual_approval_required": True
        }

        contract["kill_conditions"] = {
            "negative_oos_expectancy": True,
            "failed_market_replay": True,
            "duplicate_or_stale_shadow": True,
            "insufficient_liquidity": True,
            "live_vs_backtest_drift": True,
            "unexplained_runtime_errors": True
        }

        candidate_dir = out_dir / candidate_key
        candidate_dir.mkdir(parents=True, exist_ok=True)
        contract_path = candidate_dir / f"{candidate_key}_offline_experiment_contract_v1.json"
        contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

        state["generator_status"] = "CONTRACT_DRAFT_CREATED"
        state["contract_path"] = str(contract_path)
        state["candidate_key"] = candidate_key
        state["family_key"] = family_key
        state["validator_command"] = f'python -u "C:\\Users\\alike\\edge_factory_offline_experiment_contract_validator_v1.py" --contract "{contract_path}"'

    state_path = out_dir / "candidate_contract_generator_v1_state.json"
    report_path = out_dir / "candidate_contract_generator_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Candidate Contract Generator v1")
    md.append("")
    md.append(f"Status: `{state['generator_status']}`")
    md.append(f"Candidate: `{state['candidate_key']}`")
    md.append("")
    if state["contract_path"]:
        md.append("## Contract")
        md.append(f"`{state['contract_path']}`")
        md.append("")
        md.append("## Next validation command")
        md.append("```powershell")
        md.append(state["validator_command"])
        md.append("```")
    else:
        md.append("## Intake form")
        md.append(f"`{intake_path}`")
        md.append("")
        md.append("No candidate contract was created because minimum idea fields were not provided.")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY CANDIDATE CONTRACT GENERATOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"generator_status: {state['generator_status']}")
    print(f"candidate_key: {state['candidate_key']}")
    print(f"family_key   : {state['family_key']}")
    print(f"contract    : {state['contract_path']}")
    print(f"intake      : {intake_path}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    if state["validator_command"]:
        print("NEXT VALIDATION COMMAND")
        print("-" * 100)
        print(state["validator_command"])
    else:
        print("NEXT")
        print("-" * 100)
        print("Provide candidate idea args to generate a filled contract.")
    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
