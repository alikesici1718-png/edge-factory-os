from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_offline_research_runner_plan_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

VALIDATOR_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_contract_validator_v1"
    / "offline_research_contract_validator_latest.json"
)

PLANNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_contract_planner_v1"
    / "offline_research_contract_planner_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"offline_research_runner_plan_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "offline_research_runner_plan_latest.json"
LATEST_MD = OUT_ROOT / "offline_research_runner_plan_latest.md"


RUNNER_MAP = {
    "threshold_sweep": {
        "runner_key": "offline_threshold_sweep_runner",
        "runner_module_future": "edge_factory_os_offline_threshold_sweep_runner_v1.py",
        "objective": "Evaluate signal_ret3 threshold variants for impulse_long.",
        "expected_outputs": [
            "threshold_bucket_table",
            "candidate_rule_metrics",
            "sample_size_check",
            "symbol_concentration_check",
            "reject_or_continue_decision",
        ],
    },
    "symbol_concentration_ablation": {
        "runner_key": "offline_symbol_concentration_runner",
        "runner_module_future": "edge_factory_os_symbol_concentration_diagnostic_v1.py",
        "objective": "Test whether top loss symbols dominate impulse_long losses.",
        "expected_outputs": [
            "with_without_top_loss_symbols_table",
            "loss_rotation_check",
            "sample_remaining_check",
            "symbol_guard_research_decision",
        ],
    },
    "regime_bucket_diagnostic": {
        "runner_key": "offline_regime_bucket_runner",
        "runner_module_future": "edge_factory_os_regime_bucket_diagnostic_v1.py",
        "objective": "Find market/regime buckets where impulse_long improves or fails.",
        "expected_outputs": [
            "bucket_metric_table",
            "candidate_filter_table",
            "multi_dimension_support_check",
            "reject_or_continue_decision",
        ],
    },
    "cost_sensitivity_matrix": {
        "runner_key": "offline_cost_sensitivity_runner",
        "runner_module_future": "edge_factory_os_cost_sensitivity_matrix_v1.py",
        "objective": "Check whether impulse_long edge survives fee/slippage assumptions.",
        "expected_outputs": [
            "cost_scenario_matrix",
            "gross_vs_net_edge_check",
            "realistic_execution_viability_decision",
        ],
    },
}


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


def load_contract(path_str: str) -> Optional[Dict[str, Any]]:
    try:
        path = Path(path_str)
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def priority_for_hypothesis(hypothesis_id: str) -> int:
    if hypothesis_id == "RH1_IMPULSE_STRENGTH_THRESHOLD_TOO_LOW":
        return 100
    if hypothesis_id == "RH2_SYMBOL_OR_EVENT_LOSS_CONCENTRATION":
        return 95
    if hypothesis_id == "RH3_LOW_PRECISION_ENTRY_OR_BAD_REGIME_FILTER":
        return 90
    if hypothesis_id == "RH4_COST_SLIPPAGE_EDGE_TOO_THIN":
        return 75
    return 10


def build_plan_step(validation: Dict[str, Any], drift_gate_ready: bool) -> Dict[str, Any]:
    contract_path = validation.get("contract_path")
    contract = load_contract(contract_path) if contract_path else None

    hypothesis_id = validation.get("source_hypothesis_id")
    experiment_type = validation.get("experiment_type")

    runner_spec = RUNNER_MAP.get(str(experiment_type), {
        "runner_key": "unmapped_runner",
        "runner_module_future": None,
        "objective": "No runner mapped yet.",
        "expected_outputs": [],
    })

    execution_allowed_now = bool(
        drift_gate_ready is True
        and validation.get("valid") is True
        and validation.get("severity") in {"OK", "INFO", "ATTENTION"}
    )

    # Even when gate opens, this v1 module only plans. It never executes.
    return {
        "plan_step_id": f"RUN_PLAN_{priority_for_hypothesis(str(hypothesis_id)):03d}_{hypothesis_id}",
        "priority": priority_for_hypothesis(str(hypothesis_id)),
        "source_hypothesis_id": hypothesis_id,
        "experiment_type": experiment_type,
        "contract_path": contract_path,
        "contract_valid": validation.get("valid"),
        "validator_severity": validation.get("severity"),
        "runner_key": runner_spec["runner_key"],
        "runner_module_future": runner_spec["runner_module_future"],
        "objective": runner_spec["objective"],
        "expected_outputs": runner_spec["expected_outputs"],
        "execution_allowed_now": execution_allowed_now,
        "execution_performed": False,
        "blocked_until": "none" if execution_allowed_now else "drift_gate_ready",
        "planned_inputs": {
            "primary_ledger": contract.get("primary_ledger") if contract else None,
            "contract_id": contract.get("contract_id") if contract else None,
            "family": contract.get("family") if contract else None,
            "experiment_design": contract.get("experiment_design") if contract else None,
        },
        "planned_output_dir": str(
            BASE_DIR
            / "edge_factory_os_offline_research_runs"
            / str(hypothesis_id)
        ),
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


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    validator = load_json(VALIDATOR_LATEST)
    planner = load_json(PLANNER_LATEST)

    if validator is None:
        critical.append("validator_latest_missing_or_unreadable")
        validator = {}

    if planner is None:
        attention.append("planner_latest_missing_or_unreadable")
        planner = {}

    validator_status = validator.get("validator_status")
    validator_reason = validator.get("reason")

    drift_gate_ready = bool(validator.get("drift_gate_ready") is True)
    closed = validator.get("closed")
    drift_remaining = validator.get("drift_remaining")
    capital_remaining = validator.get("capital_remaining")

    validations = validator.get("validations") or []
    valid_contracts = [
        v for v in validations
        if v.get("valid") is True
    ]

    invalid_contracts = [
        v for v in validations
        if v.get("valid") is not True
    ]

    if invalid_contracts:
        attention.append(f"invalid_contracts_present:{len(invalid_contracts)}")

    plan_steps = [
        build_plan_step(v, drift_gate_ready)
        for v in valid_contracts
    ]

    plan_steps.sort(key=lambda x: x.get("priority", 0), reverse=True)

    execution_allowed_count = sum(1 for s in plan_steps if s.get("execution_allowed_now") is True)

    if critical:
        plan_status = "OFFLINE_RESEARCH_RUNNER_PLAN_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_VALIDATOR_INPUT"
        reason = "; ".join(critical)

    elif not plan_steps:
        plan_status = "OFFLINE_RESEARCH_RUNNER_PLAN_NO_VALID_CONTRACTS"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "WAIT_FOR_VALID_CONTRACTS"
        reason = "no valid contracts to plan"

    elif not drift_gate_ready:
        plan_status = "OFFLINE_RESEARCH_RUNNER_PLAN_PREPARED_GATE_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNER_PLAN_QUEUED_UNTIL_DRIFT_GATE_READY"
        reason = f"plan_step_count={len(plan_steps)}; drift_gate_ready=False"

    else:
        plan_status = "OFFLINE_RESEARCH_RUNNER_PLAN_READY_FOR_MANUAL_OFFLINE_EXECUTION"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_OR_OFFLINE_RESEARCH"
        next_action = "CREATE_OR_RUN_FIRST_OFFLINE_RESEARCH_RUNNER_MANUALLY"
        reason = f"plan_step_count={len(plan_steps)}; execution_allowed_count={execution_allowed_count}"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "plan_status": plan_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "validator_source": str(VALIDATOR_LATEST),
        "planner_source": str(PLANNER_LATEST),
        "validator_status": validator_status,
        "validator_reason": validator_reason,

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "valid_contract_count": len(valid_contracts),
        "invalid_contract_count": len(invalid_contracts),
        "plan_step_count": len(plan_steps),
        "execution_allowed_count": execution_allowed_count,

        "run_order": plan_steps,

        "runner_modules_needed_future": sorted(
            list({
                step.get("runner_module_future")
                for step in plan_steps
                if step.get("runner_module_future")
            })
        ),

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

    out_json = RUN_DIR / "offline_research_runner_plan_v1_state.json"
    out_md = RUN_DIR / "offline_research_runner_plan_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS OFFLINE RESEARCH RUNNER PLAN v1",
        "",
        f"plan_status: {plan_status}",
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
        "## Plan Summary",
        "",
        f"valid_contract_count: {len(valid_contracts)}",
        f"invalid_contract_count: {len(invalid_contracts)}",
        f"plan_step_count: {len(plan_steps)}",
        f"execution_allowed_count: {execution_allowed_count}",
        "",
        "## Run Order",
        "",
    ]

    for step in plan_steps:
        md_lines.append(
            f"- {step['plan_step_id']} | {step['experiment_type']} | "
            f"runner={step['runner_key']} | allowed_now={step['execution_allowed_now']}"
        )

    md_lines.extend([
        "",
        "## Runner Modules Needed Later",
        "",
        json.dumps(result["runner_modules_needed_future"], indent=2),
        "",
        "## Safety",
        "",
        "read_only: True",
        "offline_only: True",
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
    print("EDGE FACTORY OS OFFLINE RESEARCH RUNNER PLAN v1")
    print("=" * 100)
    print(f"plan_status: {plan_status}")
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
    print("PLAN SUMMARY")
    print("-" * 100)
    print(f"valid_contract_count: {len(valid_contracts)}")
    print(f"invalid_contract_count: {len(invalid_contracts)}")
    print(f"plan_step_count: {len(plan_steps)}")
    print(f"execution_allowed_count: {execution_allowed_count}")
    print()
    print("RUN ORDER")
    print("-" * 100)
    for step in plan_steps:
        print(f"{step['plan_step_id']}")
        print(f"  hypothesis: {step['source_hypothesis_id']}")
        print(f"  experiment_type: {step['experiment_type']}")
        print(f"  runner_key: {step['runner_key']}")
        print(f"  future_module: {step['runner_module_future']}")
        print(f"  execution_allowed_now: {step['execution_allowed_now']}")
        print(f"  blocked_until: {step['blocked_until']}")
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
