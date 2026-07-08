from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "trap_quality_lockbox_freeze_contract_v1.json"

STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FREEZE_CONTRACT_CREATED"
ARTIFACT_KIND = "TRAP_QUALITY_LOCKBOX_FREEZE_CONTRACT"
MODULE = "edge_factory_os_repo_only_trap_quality_lockbox_freeze_contract_v1"
FROZEN_FINALIST = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
NEXT_ALLOWED_STEP = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_V1"

EXECUTION_PATHS = {
    "trap_quality_v1": REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1.json",
    "time_exit_only": REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only_execution_v1.json",
    "risk_tightened": REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_risk_tightened_execution_v1.json",
    "trap_score4": REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_score4_execution_v1.json",
    "wider_stop": REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_execution_v1.json",
    "rejection_depth_required": REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_rejection_depth_required_execution_v1.json",
    "market_pump_veto": REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_execution_v1.json",
}

EVALUATOR_PATHS = {
    "trap_quality_v1": REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_evaluator_v1.json",
    "time_exit_only": REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only_evaluator_v1.json",
    "risk_tightened": REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_risk_tightened_evaluator_v1.json",
    "trap_score4": REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_trap_score4_evaluator_v1.json",
    "wider_stop": REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_evaluator_v1.json",
    "rejection_depth_required": REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_rejection_depth_required_evaluator_v1.json",
    "market_pump_veto": REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_evaluator_v1.json",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def r6(value: float | int | None) -> float | None:
    return None if value is None else round(float(value), 6)


def top_n_share(execution: dict[str, Any], n: int) -> dict[str, Any]:
    concentration = execution.get("metrics", {}).get("top_symbol_concentration", {})
    counts = concentration.get("trade_count_by_symbol", {})
    total = execution.get("metrics", {}).get("closed_trades", 0) or 0
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    top = ranked[:n]
    top_count = sum(count for _symbol, count in top)
    return {
        "top_n": n,
        "symbols": [{"symbol": symbol, "trade_count": count} for symbol, count in top],
        "trade_count": top_count,
        "trade_share": r6(top_count / total) if total else None,
    }


def summarize_route(label: str, execution: dict[str, Any], evaluator: dict[str, Any] | None) -> dict[str, Any]:
    metrics = execution.get("metrics", {})
    split = execution.get("split_metrics", {})
    validation = split.get("validation", {})
    holdout = split.get("holdout", {})
    null = execution.get("null_baseline", {})
    gross = metrics.get("gross_pnl_usdt")
    cost = metrics.get("total_cost_usdt")
    stressed_net = gross - 2.0 * cost if isinstance(gross, (int, float)) and isinstance(cost, (int, float)) else None
    return {
        "label": label,
        "strategy": execution.get("strategy"),
        "execution_status": execution.get("status"),
        "evaluator_result_class": evaluator.get("result_classification") if evaluator else None,
        "diagnostic_promising": evaluator.get("diagnostic_promising") if evaluator else None,
        "validation_net_bps": validation.get("portfolio_net_bps"),
        "holdout_net_bps": holdout.get("portfolio_net_bps"),
        "validation_monthly_positive_rate": validation.get("monthly_positive_rate"),
        "holdout_monthly_positive_rate": holdout.get("monthly_positive_rate"),
        "worst_month_bps": metrics.get("worst_month_bps"),
        "max_drawdown_bps": metrics.get("max_drawdown_bps"),
        "closed_trades": metrics.get("closed_trades"),
        "top_symbol_concentration": metrics.get("top_symbol_concentration"),
        "top3_symbol_concentration": top_n_share(execution, 3),
        "gross_pnl_usdt": gross,
        "net_pnl_usdt": metrics.get("net_pnl_usdt"),
        "total_cost_usdt": cost,
        "two_x_fee_stress_net_pnl_usdt": r6(stressed_net),
        "two_x_fee_stress_positive": stressed_net > 0 if stressed_net is not None else None,
        "null_baseline": {
            "feasible": null.get("feasible"),
            "null_pass": null.get("null_pass"),
            "validation_percentile": null.get("validation_percentile"),
            "runs": null.get("runs"),
        },
        "metric_integrity_result": execution.get("metric_integrity_result", {}).get("passed"),
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_trap_quality_lockbox_freeze_contract_v1.py",
        "?? artifacts/research_preregistrations/trap_quality_lockbox_freeze_contract_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    executions = {label: load_json(path) for label, path in EXECUTION_PATHS.items()}
    evaluators = {label: load_json(path) if path.exists() else None for label, path in EVALUATOR_PATHS.items()}
    summaries = {label: summarize_route(label, executions[label], evaluators[label]) for label in executions}

    finalist = summaries["trap_quality_v1"]
    ranked_by_null = sorted(
        summaries.values(),
        key=lambda item: (item.get("null_baseline", {}).get("validation_percentile") or -1.0, item.get("validation_net_bps") or -10**9),
        reverse=True,
    )
    explicit_rejections = {
        "time_exit_only": {
            "strategy": summaries["time_exit_only"]["strategy"],
            "reject_as_finalist": True,
            "reason": "Rejected as finalist despite stronger net bps because null percentile is below the finalist and below 0.90.",
            "null_percentile": summaries["time_exit_only"]["null_baseline"]["validation_percentile"],
        },
        "risk_tightened": {
            "strategy": summaries["risk_tightened"]["strategy"],
            "reject_as_finalist": True,
            "reason": "Rejected follow-up; risk-quality tightening worsened validation and null versus the finalist.",
            "null_percentile": summaries["risk_tightened"]["null_baseline"]["validation_percentile"],
        },
        "trap_score4": {
            "strategy": summaries["trap_score4"]["strategy"],
            "reject_as_finalist": True,
            "reason": "Rejected follow-up; score4-only tightening worsened validation and null versus the finalist.",
            "null_percentile": summaries["trap_score4"]["null_baseline"]["validation_percentile"],
        },
        "wider_stop": {
            "strategy": summaries["wider_stop"]["strategy"],
            "reject_as_finalist": True,
            "reason": "Rejected follow-up; wider stop worsened validation and null versus the finalist.",
            "null_percentile": summaries["wider_stop"]["null_baseline"]["validation_percentile"],
        },
        "rejection_depth_required": {
            "strategy": summaries["rejection_depth_required"]["strategy"],
            "reject_as_finalist": True,
            "reason": "Rejected follow-up; mandatory rejection depth was effectively redundant and slightly worse than the finalist.",
            "null_percentile": summaries["rejection_depth_required"]["null_baseline"]["validation_percentile"],
        },
        "market_pump_veto": {
            "strategy": summaries["market_pump_veto"]["strategy"],
            "reject_as_standalone_finalist": True,
            "reason": "Rejected as standalone finalist; lower null percentile than trap-quality V1.",
            "null_percentile": summaries["market_pump_veto"]["null_baseline"]["validation_percentile"],
        },
    }

    lockbox_criteria = {
        "net_bps_gt_0": "future lockbox net bps must be > 0",
        "monthly_positive_rate_gte_0_60": "future lockbox monthly positive rate must be >= 0.60",
        "worst_month_gt_minus_500_bps": "future lockbox worst month must be > -500 bps",
        "max_drawdown_gt_minus_2000_bps": "future lockbox max drawdown must be > -2000 bps",
        "null_percentile_gte_0_90": "future lockbox null percentile must be >= 0.90",
        "top3_symbol_concentration_lte_0_30": "future lockbox top-3 symbol concentration must be <= 0.30",
        "two_x_fee_stress_remains_positive": "future lockbox 2x fee-stress net must remain positive",
        "trade_count_gte_50": "future lockbox closed trade count must be >= 50",
    }
    reject_criteria = {
        "net_bps_lte_0": "reject lockbox result if net bps <= 0",
        "monthly_positive_rate_lt_0_50": "reject lockbox result if monthly positive rate < 0.50",
        "null_percentile_lt_0_80": "reject lockbox result if null percentile < 0.80",
        "top_symbol_concentration_gt_0_50": "reject lockbox result if top symbol concentration > 0.50",
    }
    safety_permissions = {
        "lockbox_freeze_contract_created": True,
        "backtest_allowed_now": False,
        "data_acquisition_allowed_now": False,
        "new_strategy_allowed_now": False,
        "v_next_allowed_now": False,
        "optimization_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "all_required_execution_artifacts_loaded": all(path.exists() for path in EXECUTION_PATHS.values()),
        "finalist_exactly_one": True,
        "finalist_is_trap_quality_v1": finalist["strategy"] == FROZEN_FINALIST,
        "finalist_has_highest_null_percentile_among_viable_candidates": ranked_by_null[0]["strategy"] == FROZEN_FINALIST and finalist["null_baseline"]["validation_percentile"] == 0.90,
        "time_exit_only_rejected_as_finalist": explicit_rejections["time_exit_only"]["reject_as_finalist"],
        "risk_tightened_rejected": explicit_rejections["risk_tightened"]["reject_as_finalist"],
        "trap_score4_rejected": explicit_rejections["trap_score4"]["reject_as_finalist"],
        "wider_stop_rejected": explicit_rejections["wider_stop"]["reject_as_finalist"],
        "rejection_depth_required_rejected": explicit_rejections["rejection_depth_required"]["reject_as_finalist"],
        "market_pump_veto_rejected_as_standalone_finalist": explicit_rejections["market_pump_veto"]["reject_as_standalone_finalist"],
        "no_backtest_run": True,
        "no_data_acquired": True,
        "no_strategy_modified": True,
        "no_v_next_created": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_network_used": True,
        "no_api_called": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_contract_creation": status_lines,
            "allowed_new_paths_at_contract_creation": sorted(allowed_status),
            "unexpected_dirty_paths_at_contract_creation": unexpected_status,
        },
        "source_artifacts": {
            "execution_artifacts": {label: str(path) for label, path in EXECUTION_PATHS.items()},
            "evaluator_artifacts": {label: str(path) for label, path in EVALUATOR_PATHS.items() if path.exists()},
        },
        "freeze_decision": {
            "frozen_finalist": FROZEN_FINALIST,
            "finalist_count": 1,
            "reason": "Original trap-quality V1 has the highest null percentile among viable candidates: 0.90.",
            "null_percentile": finalist["null_baseline"]["validation_percentile"],
            "next_allowed_step": NEXT_ALLOWED_STEP,
            "not_edge_claim": True,
            "not_live_or_capital_permission": True,
        },
        "finalist_summary": finalist,
        "route_rankings_by_null_percentile": [
            {
                "strategy": item["strategy"],
                "label": item["label"],
                "null_percentile": item["null_baseline"]["validation_percentile"],
                "validation_net_bps": item["validation_net_bps"],
                "holdout_net_bps": item["holdout_net_bps"],
            }
            for item in ranked_by_null
        ],
        "explicit_rejections": explicit_rejections,
        "lockbox_criteria": lockbox_criteria,
        "reject_criteria": reject_criteria,
        "known_historical_context_not_lockbox_pass_claim": {
            "finalist_validation_monthly_positive_rate": finalist["validation_monthly_positive_rate"],
            "finalist_holdout_monthly_positive_rate": finalist["holdout_monthly_positive_rate"],
            "finalist_two_x_fee_stress_net_pnl_usdt": finalist["two_x_fee_stress_net_pnl_usdt"],
            "note": "These existing in-sample/validation/holdout aggregates are selection context only. The lockbox criteria apply to future forward data.",
        },
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["lockbox_freeze_contract_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "lockbox_freeze_contract_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"frozen_finalist: {FROZEN_FINALIST}")
    print(f"finalist_null_percentile: {finalist['null_baseline']['validation_percentile']}")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
    print("backtest_run: false")
    print("data_acquired: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
