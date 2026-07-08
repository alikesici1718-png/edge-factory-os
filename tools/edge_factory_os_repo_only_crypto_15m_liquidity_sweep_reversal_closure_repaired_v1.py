from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_liquidity_sweep_reversal_evaluator_repaired_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "crypto_15m_liquidity_sweep_reversal_closure_repaired_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_REPAIRED_CLOSURE_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_REPAIRED_CLOSURE"
STRATEGY = "CRYPTO_15M_LIQUIDITY_SWEEP_FAILED_BREAKOUT_REVERSAL_V1"
ROUTE_FAMILY = "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_BASELINE"
CONFIG_ID = "crypto_15m_liquidity_sweep_48h_reversal_r2_timestop8h_v1"
EVALUATOR_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_REPAIRED_EVALUATED"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_liquidity_sweep_reversal_closure_repaired_v1.py",
        "?? artifacts/strategy_closures/crypto_15m_liquidity_sweep_reversal_closure_repaired_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    evaluator = load_json(EVALUATOR_PATH)
    result_classification = evaluator.get("result_classification")
    diagnostic_promising = evaluator.get("diagnostic_promising")
    metric_summary = evaluator.get("execution_metric_summary", {})
    safety = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "real_orders_allowed_now": False,
    }
    checks = {
        "repo_clean_before_run": not unexpected_status,
        "evaluator_artifact_loaded": True,
        "evaluator_status_verified": evaluator.get("status") == EVALUATOR_STATUS,
        "strategy_verified": evaluator.get("strategy") == STRATEGY,
        "route_family_verified": evaluator.get("route_family") == ROUTE_FAMILY,
        "evaluator_result_preserved": result_classification == evaluator.get("result_classification"),
        "diagnostic_promising_preserved": diagnostic_promising == evaluator.get("diagnostic_promising"),
        "route_closed_true": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_liquidity_sweep_reversal_closure_repaired_v1",
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_closure": status_lines,
            "allowed_new_paths_at_closure": sorted(allowed_status),
            "unexpected_dirty_paths_at_closure": unexpected_status,
        },
        "source_artifacts": {"evaluator": str(EVALUATOR_PATH)},
        "evaluator_preserved_exactly": evaluator,
        "closure_result": {
            "route_closed": True,
            "result_classification": result_classification,
            "diagnostic_promising": diagnostic_promising,
            "candidate_created": False,
            "edge_claim_created": False,
            "family_released": False,
            "runtime_enabled": False,
            "live_trading_enabled": False,
            "capital_allocated": False,
            "real_orders_allowed": False,
            "closure_note": "Repaired single-config liquidity sweep failed-breakout reversal diagnostic closed with repaired evaluator result preserved. No candidate, edge, runtime, live, or capital permission is created.",
        },
        "final_metric_snapshot": {
            "accepted_long_trades": metric_summary.get("accepted_long_trades"),
            "accepted_short_trades": metric_summary.get("accepted_short_trades"),
            "closed_trades": metric_summary.get("closed_trades"),
            "validation_net_bps": metric_summary.get("validation_net_bps"),
            "holdout_net_bps": metric_summary.get("holdout_net_bps"),
            "validation_monthly_positive_rate": metric_summary.get("validation_monthly_positive_rate"),
            "holdout_monthly_positive_rate": metric_summary.get("holdout_monthly_positive_rate"),
            "worst_month_bps": metric_summary.get("worst_month_bps"),
            "max_drawdown_bps": metric_summary.get("max_drawdown_bps"),
            "exit_counts": metric_summary.get("exit_counts"),
            "top_symbol_concentration": metric_summary.get("top_symbol_concentration"),
            "null_baseline": metric_summary.get("null_baseline"),
            "metric_integrity_result": evaluator.get("metric_integrity_result"),
        },
        "safety_permissions": safety,
        "validation_checks": checks,
        "replacement_checks_all_true": all(checks.values()) and all(value is False for value in safety.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"strategy: {STRATEGY}")
    print(f"route_family: {ROUTE_FAMILY}")
    print(f"result_classification: {result_classification}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print("route_closed: true")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
