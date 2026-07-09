"""
Manages and enforces capital allocation policy across active strategy families by reading master optimizer, guarded allocator, and lifecycle outputs. Reads family lifecycle state and sizing contracts, applies baseline allocation rules, optionally launches logger processes via subprocess, and writes capital governor decisions and a recommended system configuration.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_BASE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_USER_DIR = r"C:\Users\alike"
DEFAULT_MASTER_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_master_optimizer"
DEFAULT_GUARDED_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_guarded_allocator_optimizer"

LOGGER_SCRIPTS = {
    "old_short": "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": "market_relative_live_paper_logger.py",
    "weak_market_short": "weak_market_breakdown_short_live_paper_logger.py",
}

BASELINE_POLICY = {
    "old_short": {"lifecycle": "CORE_ENGINE", "priority": 100, "max_positions": 3, "capital_fraction": 0.05, "role": "main alpha engine"},
    "impulse_long": {"lifecycle": "HIGH_PRIORITY_DIVERSIFIER", "priority": 150, "max_positions": 2, "capital_fraction": 0.05, "role": "long/diversifier and bad-day stabilizer"},
    "market_relative_short": {"lifecycle": "KEEP_CAPPED_REDUCED_SIZE", "priority": 70, "max_positions": 3, "capital_fraction": 0.025, "role": "capped short family; keep but half-size"},
    "weak_market_short": {"lifecycle": "BACKUP_ONLY", "priority": 30, "max_positions": 2, "capital_fraction": 0.025, "role": "backup-only short continuation"},
    "session_short": {"lifecycle": "DISABLED", "priority": 0, "max_positions": 0, "capital_fraction": 0.0, "role": "disabled"},
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    except Exception:
        return pd.DataFrame()


def read_json(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def numeric(x: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def find_best_guarded(guarded_dir: Path) -> tuple[dict, pd.DataFrame]:
    summary = read_csv(guarded_dir / "guarded_scenario_summary.csv")
    if summary.empty:
        return {}, summary
    if "guard_utility" in summary.columns:
        summary["guard_utility"] = pd.to_numeric(summary["guard_utility"], errors="coerce")
        summary = summary.sort_values("guard_utility", ascending=False)
    return summary.iloc[0].to_dict(), summary


def audit_logger_help(user_dir: Path) -> pd.DataFrame:
    rows = []
    sizing_keywords = [
        "--notional", "--base_notional", "--trade_notional", "--capital_fraction",
        "--position_size", "--size", "--risk_fraction", "--fixed_notional", "--paper_notional",
    ]
    for family, script in LOGGER_SCRIPTS.items():
        path = user_dir / script
        row = {
            "family_key": family, "script": str(path), "exists": path.exists(),
            "help_ok": False, "supports_sizing_arg": False, "matched_args": "", "error": "",
        }
        if not path.exists():
            row["error"] = "script_missing"
            rows.append(row)
            continue
        try:
            proc = subprocess.run(["python", str(path), "--help"], capture_output=True, text=True, timeout=20)
            txt = (proc.stdout or "") + "\n" + (proc.stderr or "")
            row["help_ok"] = len(txt) > 0
            matches = [kw for kw in sizing_keywords if kw in txt]
            row["supports_sizing_arg"] = bool(matches)
            row["matched_args"] = ",".join(matches)
            if not txt:
                row["error"] = "empty_help"
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"
        rows.append(row)
    return pd.DataFrame(rows)


def build_blueprint(master_dir: Path, best: dict) -> dict:
    master_decision = read_json(master_dir / "MASTER_DECISION.json")
    chosen_guard = str(best.get("scenario", "UNKNOWN"))
    return {
        "system_name": "EDGE_FACTORY_UPPER_SYSTEM_v1",
        "source_decisions": {
            "master_optimizer_chosen": master_decision.get("chosen_scenario", "UNKNOWN"),
            "guarded_optimizer_chosen": chosen_guard,
        },
        "thesis": (
            "The next upgrade is not another hard filter. Guarded optimizer says the best upper-system "
            "improvement is capital weighting: keep market_relative_short for portfolio structure but run it at half size."
        ),
        "enabled_families": ["old_short", "impulse_long", "market_relative_short", "weak_market_short"],
        "disabled_families": ["session_short"],
        "risk": {
            "global_max_positions": 6, "max_short_positions": 5, "max_long_positions": 2,
            "pending_grace_minutes": 180, "poll_seconds": 60,
        },
        "family_policy": BASELINE_POLICY,
        "weak_market_backup_only": True,
        "guards": {
            "active_hard_filters": [],
            "active_daily_trade_caps": {},
            "active_coin_blacklist": [],
            "capital_weighting": {"market_relative_short": "HALF_SIZE"},
            "notes": [
                "Do not enable current coin blacklist yet; likely overfit until OOS tested.",
                "Do not enable current simple daily caps yet; they cut edge too much.",
                "Market-relative half-size improves drawdown and final equity in guarded allocator test.",
            ],
        },
        "best_guarded_metrics": {
            "scenario": chosen_guard,
            "final_equity": numeric(best.get("final_equity")),
            "portfolio_total_return": numeric(best.get("portfolio_total_return")),
            "portfolio_max_drawdown": numeric(best.get("portfolio_max_drawdown")),
            "profit_factor": numeric(best.get("profit_factor")),
            "worst_day_pnl": numeric(best.get("worst_day_pnl")),
            "worst_5_day_sum": numeric(best.get("worst_5_day_sum")),
            "worst_30_day_sum": numeric(best.get("worst_30_day_sum")),
            "accepted_trades": int(numeric(best.get("accepted_trades"), 0)),
        },
        "implementation_requirement": (
            "The live/paper logger layer must actually support per-family notional or capital_fraction. "
            "If current loggers use fixed notional, writing capital_fraction into config is not enough."
        ),
        "next_system_layer": "position_sizing_contract",
    }


def build_family_policy_df(blueprint: dict) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "family_key": fam,
            "lifecycle": pol["lifecycle"],
            "enabled": fam in blueprint["enabled_families"],
            "priority": pol["priority"],
            "max_positions": pol["max_positions"],
            "capital_fraction": pol["capital_fraction"],
            "role": pol["role"],
        }
        for fam, pol in blueprint["family_policy"].items()
    ])


def build_gap_df(audit: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if audit.empty:
        rows.append({
            "gap_id": "LOGGER_SIZING_UNKNOWN",
            "severity": "HIGH",
            "status": "unknown",
            "problem": "Logger sizing capability was not audited.",
            "required_fix": "Run edge_factory_capital_governor.py --audit-loggers.",
        })
    else:
        for _, r in audit.iterrows():
            fam = str(r["family_key"])
            if not bool(r.get("supports_sizing_arg", False)):
                rows.append({
                    "gap_id": f"{fam}_SIZING_ARG_MISSING",
                    "severity": "HIGH" if fam == "market_relative_short" else "MEDIUM",
                    "status": "needs_fix",
                    "problem": f"{fam} logger help did not show a sizing/notional argument.",
                    "required_fix": "Add per-family notional/capital_fraction support or a sizing-aware wrapper.",
                })
    rows.append({
        "gap_id": "BAD_DAY_GUARD_NOT_PROMOTED",
        "severity": "MEDIUM",
        "status": "intentional",
        "problem": "Bad-day guards reduce some losses but cut too much PnL.",
        "required_fix": "Keep researching regime-level guard; do not enable current simple filters blindly.",
    })
    rows.append({
        "gap_id": "COIN_BLACKLIST_OVERFIT_RISK",
        "severity": "MEDIUM",
        "status": "watch",
        "problem": "Bad coin blacklist improves some worst days but is likely overfit.",
        "required_fix": "Only promote blacklist after OOS/time-split validation.",
    })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Edge Factory Capital Governor")
    ap.add_argument("--base_dir", default=DEFAULT_BASE)
    ap.add_argument("--user_dir", default=DEFAULT_USER_DIR)
    ap.add_argument("--master_dir", default=DEFAULT_MASTER_DIR)
    ap.add_argument("--guarded_dir", default=DEFAULT_GUARDED_DIR)
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--audit-loggers", action="store_true")
    args = ap.parse_args()

    base = Path(args.base_dir)
    user_dir = Path(args.user_dir)
    master_dir = Path(args.master_dir)
    guarded_dir = Path(args.guarded_dir)
    out = Path(args.out_dir) if args.out_dir else base / "edge_factory_capital_governor"
    out.mkdir(parents=True, exist_ok=True)

    best, summary = find_best_guarded(guarded_dir)
    if not best:
        raise FileNotFoundError(
            f"Cannot find guarded_scenario_summary.csv in {guarded_dir}. "
            "Run edge_factory_guarded_allocator_optimizer.py first."
        )

    blueprint = build_blueprint(master_dir, best)
    policy_df = build_family_policy_df(blueprint)
    audit_df = audit_logger_help(user_dir) if args.audit_loggers else pd.DataFrame()
    gap_df = build_gap_df(audit_df)

    (out / "upper_system_blueprint.json").write_text(json.dumps(blueprint, indent=2, default=str), encoding="utf-8")
    policy_df.to_csv(out / "family_capital_policy.csv", index=False)
    gap_df.to_csv(out / "implementation_gap.csv", index=False)
    if not audit_df.empty:
        audit_df.to_csv(out / "logger_capability_audit.csv", index=False)
    summary.head(30).to_csv(out / "guarded_top_scenarios_snapshot.csv", index=False)

    show = [
        "scenario", "guard_utility", "final_equity", "portfolio_total_return",
        "portfolio_max_drawdown", "profit_factor", "worst_day_pnl",
        "worst_5_day_sum", "worst_30_day_sum", "accepted_trades",
    ]

    report = []
    report.append("EDGE FACTORY CAPITAL GOVERNOR REPORT")
    report.append("=" * 120)
    report.append(f"out_dir: {out}")
    report.append("")
    report.append("CHOSEN UPPER SYSTEM")
    report.append("-" * 120)
    report.append(json.dumps(blueprint, indent=2, default=str))
    report.append("")
    report.append("FAMILY CAPITAL POLICY")
    report.append("-" * 120)
    report.append(policy_df.to_string(index=False))
    report.append("")
    report.append("IMPLEMENTATION GAP")
    report.append("-" * 120)
    report.append(gap_df.to_string(index=False))
    report.append("")
    report.append("LOGGER CAPABILITY AUDIT")
    report.append("-" * 120)
    report.append(audit_df.to_string(index=False) if not audit_df.empty else "Not run. Use --audit-loggers.")
    report.append("")
    report.append("TOP GUARDED SCENARIOS SNAPSHOT")
    report.append("-" * 120)
    report.append(summary[[c for c in show if c in summary.columns]].head(30).to_string(index=False))
    report.append("")
    report.append("NEXT AUTOPILOT STEP")
    report.append("-" * 120)
    report.append(
        "Build/verify a position_sizing_contract layer. The next upgrade is making family capital weights executable and auditable."
    )

    (out / "CAPITAL_GOVERNOR_REPORT.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))


if __name__ == "__main__":
    main()
