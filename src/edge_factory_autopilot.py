from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


# =============================================================================
# EDGE FACTORY AUTOPILOT
# =============================================================================
#
# This is the upper-level "knows what to do next" layer.
#
# It does NOT place real orders.
# It does NOT blindly modify running systems.
#
# What it does:
#   1) Inspects the whole Edge Factory workspace.
#   2) Reads master optimizer / portfolio / live / bad-day outputs.
#   3) Scores what stage the factory is in.
#   4) Creates a prioritized next-action queue.
#   5) Produces machine-readable decisions:
#        - family lifecycle: CORE / DIVERSIFIER / CAPPED / BACKUP / DISABLE / NEED_MORE_DATA
#        - next research task
#        - missing artifact
#        - whether to run an offline script
#   6) Optional --execute-safe mode can run safe offline scripts only.
#
# Usage:
#   python "C:\Users\alike\edge_factory_autopilot.py"
#
# Optional:
#   python "C:\Users\alike\edge_factory_autopilot.py" --execute-safe
#
# Outputs:
#   edge_lab_new\edge_factory_autopilot\
#       AUTOPILOT_REPORT.txt
#       next_actions.csv
#       family_lifecycle.csv
#       workspace_inventory.json
#       autopilot_state.json
#       recommended_system.json
# =============================================================================


DEFAULT_BASE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_USER_DIR = r"C:\Users\alike"


@dataclass
class Action:
    priority: int
    action_id: str
    category: str
    status: str
    reason: str
    command: str = ""
    output_expected: str = ""
    safe_to_execute: bool = True


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def path_age_hours(p: Path) -> float | None:
    if not p.exists():
        return None
    return (datetime.now().timestamp() - p.stat().st_mtime) / 3600.0


def read_json(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    except Exception:
        return pd.DataFrame()


def bool_exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def numeric(x: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


class EdgeFactoryAutopilot:
    def __init__(self, base_dir: str, user_dir: str, execute_safe: bool = False) -> None:
        self.base = Path(base_dir)
        self.user_dir = Path(user_dir)
        self.out = self.base / "edge_factory_autopilot"
        self.out.mkdir(parents=True, exist_ok=True)
        self.execute_safe = execute_safe

        self.paths = {
            "normalized_trades": self.base / "portfolio_family_overlap_validation" / "normalized_trades.csv",
            "portfolio_report": self.base / "portfolio_family_overlap_validation" / "validator_report.txt",
            "offline_optimizer_report": self.base / "edge_factory_offline_optimizer" / "priority_allocator_backtest" / "priority_allocator_report.txt",
            "master_report": self.base / "edge_factory_master_optimizer" / "MASTER_REPORT.txt",
            "master_decision": self.base / "edge_factory_master_optimizer" / "MASTER_DECISION.json",
            "recommended_sim": self.base / "edge_factory_master_optimizer" / "recommended_sim_trades.csv",
            "recommended_family_pnl": self.base / "edge_factory_master_optimizer" / "recommended_family_pnl.csv",
            "recommended_daily_pnl": self.base / "edge_factory_master_optimizer" / "recommended_daily_pnl.csv",
            "bad_day_report": self.base / "edge_factory_bad_day_investigation" / "BAD_DAY_REPORT.txt",
            "bad_day_guards": self.base / "edge_factory_bad_day_investigation" / "bad_day_guard_candidates.csv",
            "master_run": self.base / "paper_run_gate_MASTER_RECOMMENDED",
            "master_live_scorecard": self.base / "paper_run_gate_MASTER_RECOMMENDED" / "live_decision_dashboard" / "family_live_scorecard.csv",
            "master_health_snapshot": self.base / "paper_run_gate_MASTER_RECOMMENDED" / "global_risk_manager" / "global_risk_snapshot.csv",
        }

        self.scripts = {
            "portfolio_validator": self.user_dir / "portfolio_family_overlap_validator.py",
            "master_optimizer": self.user_dir / "edge_factory_master_optimizer.py",
            "bad_day_investigator": self.user_dir / "edge_factory_bad_day_investigator.py",
            "health_check": self.user_dir / "edge_factory_live_health_check_v5.py",
            "performance_analyzer": self.user_dir / "edge_factory_live_performance_analyzer_v3.py",
            "decision_dashboard": self.user_dir / "edge_factory_live_decision_dashboard.py",
        }

        self.actions: list[Action] = []
        self.inventory: dict[str, Any] = {}

    def inventory_workspace(self) -> dict[str, Any]:
        inv: dict[str, Any] = {
            "timestamp_utc": now_iso(),
            "base_dir": str(self.base),
            "user_dir": str(self.user_dir),
            "paths": {},
            "scripts": {},
        }

        for k, p in self.paths.items():
            inv["paths"][k] = {
                "path": str(p),
                "exists": p.exists(),
                "is_file": p.is_file(),
                "is_dir": p.is_dir(),
                "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
                "age_hours": path_age_hours(p) if p.exists() else None,
            }

        for k, p in self.scripts.items():
            inv["scripts"][k] = {
                "path": str(p),
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
            }

        self.inventory = inv
        return inv

    def add_action(self, priority: int, action_id: str, category: str, status: str, reason: str, command: str = "", output_expected: str = "", safe_to_execute: bool = True) -> None:
        self.actions.append(Action(priority, action_id, category, status, reason, command, output_expected, safe_to_execute))

    def evaluate_pipeline(self) -> None:
        p = self.paths
        s = self.scripts

        # Stage 1: normalized portfolio data.
        if not bool_exists(p["normalized_trades"]):
            if bool_exists(s["portfolio_validator"]):
                self.add_action(
                    100,
                    "RUN_PORTFOLIO_VALIDATOR",
                    "missing_artifact",
                    "required",
                    "normalized_trades.csv yok. Üst akıl geçmiş trade havuzu olmadan karar veremez.",
                    f'python "{s["portfolio_validator"]}"',
                    str(p["normalized_trades"]),
                )
            else:
                self.add_action(
                    100,
                    "CREATE_PORTFOLIO_VALIDATOR",
                    "missing_script",
                    "blocked",
                    "portfolio_family_overlap_validator.py yok. Önce geçmiş aile trade havuzu üretilecek script lazım.",
                    safe_to_execute=False,
                )
            return

        # Stage 2: master optimizer.
        if not bool_exists(p["master_decision"]) or not bool_exists(p["master_report"]):
            if bool_exists(s["master_optimizer"]):
                self.add_action(
                    95,
                    "RUN_MASTER_OPTIMIZER",
                    "optimizer",
                    "required",
                    "Master decision yok veya eksik. Aile/limit/priority final kararı için master optimizer çalışmalı.",
                    f'python "{s["master_optimizer"]}"',
                    str(p["master_decision"]),
                )
            else:
                self.add_action(
                    95,
                    "CREATE_MASTER_OPTIMIZER",
                    "missing_script",
                    "blocked",
                    "edge_factory_master_optimizer.py yok. Üst sistemin beyni bu script.",
                    safe_to_execute=False,
                )
            return

        # Stage 3: bad-day investigation.
        if not bool_exists(p["bad_day_report"]):
            if bool_exists(s["bad_day_investigator"]):
                self.add_action(
                    90,
                    "RUN_BAD_DAY_INVESTIGATOR",
                    "risk_research",
                    "required",
                    "Master sistem çıktı ama kötü gün analizi yok. En büyük kalan risk kötü gün rejimleri.",
                    f'python "{s["bad_day_investigator"]}"',
                    str(p["bad_day_report"]),
                )
            else:
                self.add_action(
                    90,
                    "CREATE_BAD_DAY_INVESTIGATOR",
                    "missing_script",
                    "blocked",
                    "edge_factory_bad_day_investigator.py yok. Kötü günleri açıklayan modül lazım.",
                    safe_to_execute=False,
                )

        # Stage 4: master recommended paper observability.
        if p["master_run"].exists():
            if bool_exists(s["health_check"]):
                self.add_action(
                    60,
                    "RUN_MASTER_HEALTH_CHECK",
                    "live_observability",
                    "optional",
                    "MASTER_RECOMMENDED run klasörü var. Health-check ile risk ihlali var mı bakılmalı.",
                    f'python "{s["health_check"]}" --base_dir "{p["master_run"]}"',
                    str(p["master_health_snapshot"]),
                )
            if bool_exists(s["decision_dashboard"]):
                self.add_action(
                    55,
                    "RUN_MASTER_DASHBOARD",
                    "live_observability",
                    "optional",
                    "MASTER_RECOMMENDED run klasörü var. Dashboard aile kararlarını güncelleyebilir.",
                    f'python "{s["decision_dashboard"]}" --base_dir "{p["master_run"]}"',
                    str(p["master_live_scorecard"]),
                )
        else:
            self.add_action(
                40,
                "MASTER_PAPER_NOT_RUNNING",
                "deployment",
                "informational",
                "MASTER_RECOMMENDED paper run klasörü yok. Şu an autopilot offline araştırma modunda.",
                safe_to_execute=False,
            )

    def evaluate_master_decision(self) -> tuple[pd.DataFrame, dict]:
        decision = read_json(self.paths["master_decision"])
        family_rows = []

        rec = decision.get("recommended_config", {})
        actions = decision.get("family_actions", {})
        chosen = decision.get("chosen_scenario", "")

        # Load richer PnL if exists.
        fam_pnl = read_csv(self.paths["recommended_family_pnl"])
        pnl_map = {}
        if not fam_pnl.empty and "family_key" in fam_pnl.columns:
            for _, r in fam_pnl.iterrows():
                pnl_map[str(r["family_key"])] = r.to_dict()

        for fam in rec.get("enabled_families", []):
            act = actions.get(fam, {})
            pnl = pnl_map.get(fam, {})
            row = {
                "family_key": fam,
                "lifecycle": act.get("action", "UNKNOWN"),
                "enabled": True,
                "max_per_family": rec.get("max_per_family", {}).get(fam, ""),
                "priority": rec.get("family_priority", {}).get(fam, ""),
                "capital_fraction": rec.get("capital_fraction", {}).get(fam, ""),
                "trades": act.get("trades", pnl.get("trades", "")),
                "pnl": act.get("pnl", pnl.get("pnl", "")),
                "avg_ret": act.get("avg_ret", pnl.get("avg_ret", "")),
                "win_rate": pnl.get("win_rate", ""),
                "worst_trade": pnl.get("worst_trade", ""),
                "reason": "",
            }

            if fam == "old_short":
                row["reason"] = "Ana motor. Marginal testte çıkarılınca sistem çöktü."
            elif fam == "impulse_long":
                row["reason"] = "Diversifier. Priority yüksek olmalı; bloklanan impulse sinyalleri değerliydi."
            elif fam == "market_relative_short":
                row["reason"] = "Kendi PnL zayıf ama portföyden çıkarılınca sistem düşüyor; capped kalsın."
            elif fam == "weak_market_short":
                row["reason"] = "Tek başına ana motor değil; backup-only ve küçük notional."

            family_rows.append(row)

        for fam in rec.get("disabled_families", []):
            family_rows.append({
                "family_key": fam,
                "lifecycle": "DISABLED",
                "enabled": False,
                "max_per_family": 0,
                "priority": 0,
                "capital_fraction": 0,
                "trades": "",
                "pnl": "",
                "avg_ret": "",
                "win_rate": "",
                "worst_trade": "",
                "reason": "Master optimizer ve live early sonuçlar sonrası gereksiz/yük bindirici.",
            })

        df = pd.DataFrame(family_rows)
        return df, {"chosen_scenario": chosen, "recommended_config": rec, "raw_decision": decision}

    def evaluate_bad_day_layer(self) -> None:
        guards = read_csv(self.paths["bad_day_guards"])
        if guards.empty:
            if bool_exists(self.paths["bad_day_report"]):
                self.add_action(
                    75,
                    "BAD_DAY_GUARD_EMPTY_OR_WEAK",
                    "risk_research",
                    "needs_review",
                    "Bad-day raporu var ama guard aday tablosu boş/zayıf. Rapor manuel yorumlanmalı.",
                    safe_to_execute=False,
                )
            return

        # Find a guard that improves or at least removes bad-day trades without killing too much.
        g = guards.copy()
        for col in ["pnl_delta", "bad_day_removed_share", "kept_share", "kept_pf", "utility"]:
            if col in g.columns:
                g[col] = pd.to_numeric(g[col], errors="coerce")

        candidates = g[
            (g.get("bad_day_removed_share", 0) > 0.20)
            & (g.get("kept_share", 0) > 0.50)
            & (g.get("kept_pf", 0) > 1.20)
        ].copy()

        if not candidates.empty:
            best = candidates.sort_values("utility", ascending=False).iloc[0].to_dict()
            self.add_action(
                85,
                "PROMOTE_BAD_DAY_GUARD_RESEARCH",
                "risk_research",
                "candidate_found",
                f"Bad-day guard adayı bulundu: {best.get('guard')} | bad_day_removed_share={best.get('bad_day_removed_share')} | pnl_delta={best.get('pnl_delta')}",
                output_expected="guard should be retested in allocator, not blindly enabled",
                safe_to_execute=False,
            )
        else:
            self.add_action(
                65,
                "NO_SAFE_BAD_DAY_GUARD_YET",
                "risk_research",
                "informational",
                "Guard adayları kötü günleri azaltıyor olabilir ama getiri/koruma dengesi henüz ana sisteme koyacak kadar temiz değil.",
                safe_to_execute=False,
            )

    def evaluate_live_scorecard(self) -> None:
        score = read_csv(self.paths["master_live_scorecard"])
        if score.empty:
            return

        for _, r in score.iterrows():
            fam = str(r.get("family_key", ""))
            decision = str(r.get("decision", ""))
            closed = int(numeric(r.get("closed_trades", 0), 0))
            pnl = numeric(r.get("realized_pnl", 0), 0)
            pf = numeric(r.get("profit_factor", 0), 0)

            if decision in {"DISABLE_CANDIDATE", "WATCH_FOR_DISABLE"} and closed >= 30:
                self.add_action(
                    92,
                    f"LIVE_REVIEW_{fam}",
                    "live_lifecycle",
                    "urgent_review",
                    f"{fam} live scorecard {decision}: closed={closed}, pnl={pnl}, pf={pf}. Disable/reduce adayı olabilir.",
                    safe_to_execute=False,
                )
            elif decision in {"PROMOTE_CANDIDATE"} and closed >= 100:
                self.add_action(
                    70,
                    f"LIVE_PROMOTE_REVIEW_{fam}",
                    "live_lifecycle",
                    "review",
                    f"{fam} live scorecard promote adayı: closed={closed}, pnl={pnl}, pf={pf}. Notional artırmadan önce offline/live uyumu kontrol edilmeli.",
                    safe_to_execute=False,
                )

    def execute_actions(self) -> list[dict]:
        results = []
        if not self.execute_safe:
            return results

        # Execute only highest-priority required safe actions, one by one.
        for a in sorted(self.actions, key=lambda x: -x.priority):
            if not a.safe_to_execute:
                continue
            if a.status not in {"required", "optional"}:
                continue
            if not a.command:
                continue

            # Only run offline/reporter scripts, never launch paper windows.
            forbidden = ["start_edge_factory", "powershell", "send", "order"]
            if any(f in a.command.lower() for f in forbidden):
                continue

            print(f"[EXECUTE] {a.action_id}: {a.command}")
            try:
                proc = subprocess.run(a.command, shell=True, cwd=str(self.user_dir), capture_output=True, text=True, timeout=60 * 60)
                results.append({
                    "action_id": a.action_id,
                    "returncode": proc.returncode,
                    "stdout_tail": proc.stdout[-4000:],
                    "stderr_tail": proc.stderr[-4000:],
                })
            except Exception as e:
                results.append({
                    "action_id": a.action_id,
                    "returncode": -1,
                    "error": f"{type(e).__name__}: {e}",
                })

            # Do one action per autopilot run to keep the loop controlled.
            break

        return results

    def run(self) -> None:
        self.inventory_workspace()
        self.evaluate_pipeline()

        family_df = pd.DataFrame()
        decision_info = {}
        if bool_exists(self.paths["master_decision"]):
            family_df, decision_info = self.evaluate_master_decision()

        self.evaluate_bad_day_layer()
        self.evaluate_live_scorecard()

        # De-duplicate actions by action_id, keeping highest priority.
        seen = {}
        for a in self.actions:
            prev = seen.get(a.action_id)
            if prev is None or a.priority > prev.priority:
                seen[a.action_id] = a
        self.actions = sorted(seen.values(), key=lambda a: -a.priority)

        exec_results = self.execute_actions()

        # Save outputs.
        (self.out / "workspace_inventory.json").write_text(json.dumps(self.inventory, indent=2, default=str), encoding="utf-8")
        pd.DataFrame([asdict(a) for a in self.actions]).to_csv(self.out / "next_actions.csv", index=False)
        if not family_df.empty:
            family_df.to_csv(self.out / "family_lifecycle.csv", index=False)
        (self.out / "recommended_system.json").write_text(json.dumps(decision_info, indent=2, default=str), encoding="utf-8")
        (self.out / "execute_results.json").write_text(json.dumps(exec_results, indent=2, default=str), encoding="utf-8")

        state = {
            "timestamp_utc": now_iso(),
            "execute_safe": self.execute_safe,
            "top_action": asdict(self.actions[0]) if self.actions else None,
            "action_count": len(self.actions),
            "family_lifecycle_rows": len(family_df),
            "exec_results_count": len(exec_results),
        }
        (self.out / "autopilot_state.json").write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")

        report = self.make_report(family_df, decision_info, exec_results)
        (self.out / "AUTOPILOT_REPORT.txt").write_text(report, encoding="utf-8")
        print(report)

    def make_report(self, family_df: pd.DataFrame, decision_info: dict, exec_results: list[dict]) -> str:
        lines = []
        lines.append("EDGE FACTORY AUTOPILOT REPORT")
        lines.append("=" * 120)
        lines.append(f"timestamp_utc: {now_iso()}")
        lines.append(f"base_dir: {self.base}")
        lines.append(f"execute_safe: {self.execute_safe}")
        lines.append("")

        lines.append("PIPELINE ARTIFACTS")
        lines.append("-" * 120)
        for k, p in self.paths.items():
            exists = p.exists()
            age = path_age_hours(p) if exists else None
            lines.append(f"{'OK' if exists else 'MISSING':8} {k:28} {p} age_h={'' if age is None else round(age, 2)}")

        lines.append("")
        lines.append("SCRIPT INVENTORY")
        lines.append("-" * 120)
        for k, p in self.scripts.items():
            lines.append(f"{'OK' if p.exists() else 'MISSING':8} {k:28} {p}")

        if decision_info:
            lines.append("")
            lines.append("RECOMMENDED SYSTEM SUMMARY")
            lines.append("-" * 120)
            rec = decision_info.get("recommended_config", {})
            lines.append(f"chosen_scenario: {decision_info.get('chosen_scenario')}")
            lines.append(json.dumps(rec, indent=2, default=str))

        if not family_df.empty:
            lines.append("")
            lines.append("FAMILY LIFECYCLE")
            lines.append("-" * 120)
            lines.append(family_df.to_string(index=False))

        lines.append("")
        lines.append("NEXT ACTION QUEUE")
        lines.append("-" * 120)
        if self.actions:
            action_df = pd.DataFrame([asdict(a) for a in self.actions])
            show_cols = ["priority", "action_id", "category", "status", "reason", "command"]
            lines.append(action_df[show_cols].head(30).to_string(index=False))
        else:
            lines.append("No actions. System state is stable.")

        if exec_results:
            lines.append("")
            lines.append("EXECUTION RESULTS")
            lines.append("-" * 120)
            lines.append(json.dumps(exec_results, indent=2, default=str))

        lines.append("")
        lines.append("AUTOPILOT INTERPRETATION")
        lines.append("-" * 120)
        if self.actions:
            top = self.actions[0]
            lines.append(f"Top priority: {top.action_id} [{top.status}]")
            lines.append(top.reason)
        else:
            lines.append("Autopilot has no urgent action. Keep collecting data or expand discovery universe.")

        lines.append("")
        lines.append("NEXT FILES TO SEND")
        lines.append("-" * 120)
        lines.append(str(self.out / "AUTOPILOT_REPORT.txt"))
        lines.append(str(self.out / "next_actions.csv"))
        lines.append(str(self.out / "family_lifecycle.csv"))

        return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Edge Factory Autopilot - upper-level self-directed research controller.")
    ap.add_argument("--base_dir", default=DEFAULT_BASE)
    ap.add_argument("--user_dir", default=DEFAULT_USER_DIR)
    ap.add_argument("--execute-safe", action="store_true", help="Run only safe offline/reporting scripts. Never starts launchers.")
    args = ap.parse_args()

    bot = EdgeFactoryAutopilot(args.base_dir, args.user_dir, execute_safe=args.execute_safe)
    bot.run()


if __name__ == "__main__":
    main()
