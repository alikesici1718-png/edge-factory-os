from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_offline_research_contract_validator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

PLANNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_contract_planner_v1"
    / "offline_research_contract_planner_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"offline_research_contract_validator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "offline_research_contract_validator_latest.json"
LATEST_MD = OUT_ROOT / "offline_research_contract_validator_latest.md"


MUTATION_FLAGS = [
    "mutate_runtime_allowed",
    "launcher_allowed",
    "patch_runtime_allowed",
    "active_paper_allowed",
    "live_allowed",
    "capital_change_allowed",
    "family_disable_allowed",
    "real_orders_allowed",
    "execution_performed",
]


EXPECTED_TYPES = {
    "RH1_IMPULSE_STRENGTH_THRESHOLD_TOO_LOW": "threshold_sweep",
    "RH2_SYMBOL_OR_EVENT_LOSS_CONCENTRATION": "symbol_concentration_ablation",
    "RH3_LOW_PRECISION_ENTRY_OR_BAD_REGIME_FILTER": "regime_bucket_diagnostic",
    "RH4_COST_SLIPPAGE_EDGE_TOO_THIN": "cost_sensitivity_matrix",
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


def nested_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def is_false(v: Any) -> bool:
    return v is False


def check_required(contract: Dict[str, Any], path: List[str], errors: List[str], warnings: List[str], name: str) -> Any:
    value = nested_get(contract, path, None)
    if value is None or value == "" or value == [] or value == {}:
        errors.append(f"missing_required:{name}")
    return value


def validate_contract(contract_path: Path, planner_gate_ready: bool) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    info: List[str] = []

    contract = load_json(contract_path)

    if contract is None:
        return {
            "contract_path": str(contract_path),
            "valid": False,
            "severity": "CRITICAL",
            "source_hypothesis_id": None,
            "experiment_type": None,
            "errors": ["contract_json_unreadable"],
            "warnings": [],
            "info": [],
        }

    schema = check_required(contract, ["contract_schema"], errors, warnings, "contract_schema")
    contract_id = check_required(contract, ["contract_id"], errors, warnings, "contract_id")
    hypothesis_id = check_required(contract, ["source_hypothesis_id"], errors, warnings, "source_hypothesis_id")
    family = check_required(contract, ["family"], errors, warnings, "family")
    experiment_type = check_required(contract, ["experiment_design", "experiment_type"], errors, warnings, "experiment_design.experiment_type")

    if schema != "edge_factory_offline_research_contract_draft_v1":
        errors.append(f"unexpected_schema:{schema}")

    if family != "impulse_long":
        warnings.append(f"unexpected_family:{family}")

    expected_type = EXPECTED_TYPES.get(str(hypothesis_id))

    if expected_type and experiment_type != expected_type:
        errors.append(f"experiment_type_mismatch:expected={expected_type};actual={experiment_type}")

    if hypothesis_id not in EXPECTED_TYPES:
        warnings.append(f"unmapped_or_control_hypothesis:{hypothesis_id}")

    check_required(contract, ["claim"], errors, warnings, "claim")
    check_required(contract, ["evidence"], errors, warnings, "evidence")
    check_required(contract, ["primary_ledger"], errors, warnings, "primary_ledger")
    check_required(contract, ["input_summary_snapshot"], errors, warnings, "input_summary_snapshot")
    check_required(contract, ["primary_row_summary_snapshot"], errors, warnings, "primary_row_summary_snapshot")
    check_required(contract, ["experiment_design", "objective"], errors, warnings, "experiment_design.objective")
    check_required(contract, ["experiment_design", "primary_metric"], errors, warnings, "experiment_design.primary_metric")
    check_required(contract, ["experiment_design", "secondary_metrics"], errors, warnings, "experiment_design.secondary_metrics")
    check_required(contract, ["experiment_design", "baseline"], errors, warnings, "experiment_design.baseline")
    check_required(contract, ["experiment_design", "pass_condition"], errors, warnings, "experiment_design.pass_condition")
    check_required(contract, ["experiment_design", "failure_condition"], errors, warnings, "experiment_design.failure_condition")

    if experiment_type == "threshold_sweep":
        check_required(contract, ["experiment_design", "parameter_grid"], errors, warnings, "threshold_sweep.parameter_grid")
        grid = nested_get(contract, ["experiment_design", "parameter_grid"], {})
        if isinstance(grid, dict):
            if not grid.get("signal_ret3_min_bps"):
                errors.append("threshold_sweep_missing_signal_ret3_min_bps_grid")

    elif experiment_type == "symbol_concentration_ablation":
        check_required(contract, ["experiment_design", "symbol_sets"], errors, warnings, "symbol_concentration_ablation.symbol_sets")

    elif experiment_type == "regime_bucket_diagnostic":
        check_required(contract, ["experiment_design", "bucket_dimensions"], errors, warnings, "regime_bucket_diagnostic.bucket_dimensions")
        check_required(contract, ["experiment_design", "candidate_filters_to_evaluate"], errors, warnings, "regime_bucket_diagnostic.candidate_filters_to_evaluate")

    elif experiment_type == "cost_sensitivity_matrix":
        check_required(contract, ["experiment_design", "cost_scenarios"], errors, warnings, "cost_sensitivity_matrix.cost_scenarios")

    gate = contract.get("gate") or {}

    gate_ready = gate.get("drift_gate_ready")
    blocked_until = gate.get("blocked_until")
    execution_allowed_now = gate.get("offline_contract_execution_allowed_now")

    if gate_ready != planner_gate_ready:
        errors.append(f"gate_ready_mismatch:planner={planner_gate_ready};contract={gate_ready}")

    if planner_gate_ready is False:
        if execution_allowed_now is not False:
            errors.append("execution_should_be_blocked_when_drift_gate_false")
        if blocked_until != "drift_gate_ready":
            errors.append(f"blocked_until_should_be_drift_gate_ready:{blocked_until}")

    if planner_gate_ready is True:
        if execution_allowed_now is not True:
            warnings.append("drift_gate_ready_but_execution_not_enabled")
        if blocked_until not in {"none", None, ""}:
            warnings.append(f"drift_gate_ready_but_blocked_until={blocked_until}")

    safety = contract.get("safety") or {}

    if safety.get("read_only") is not True:
        errors.append("safety_read_only_not_true")

    if safety.get("offline_only") is not True:
        errors.append("safety_offline_only_not_true")

    for flag in MUTATION_FLAGS:
        if safety.get(flag) is not False:
            errors.append(f"safety_flag_not_false:{flag}={safety.get(flag)}")

    gate_mutation_flags = [
        "runtime_mutation_allowed",
        "capital_change_allowed",
        "family_disable_allowed",
        "live_or_real_order_allowed",
    ]

    for flag in gate_mutation_flags:
        if gate.get(flag) is not False:
            errors.append(f"gate_mutation_flag_not_false:{flag}={gate.get(flag)}")

    valid = not errors

    if errors:
        severity = "CRITICAL"
    elif warnings:
        severity = "ATTENTION"
    else:
        severity = "OK"

    if valid:
        info.append("contract_schema_and_safety_valid")

    return {
        "contract_path": str(contract_path),
        "contract_id": contract_id,
        "source_hypothesis_id": hypothesis_id,
        "experiment_type": experiment_type,
        "valid": valid,
        "severity": severity,
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    planner = load_json(PLANNER_LATEST)

    if planner is None:
        critical.append("planner_latest_json_missing_or_unreadable")
        planner = {}

    planner_status = planner.get("planner_status")
    planner_reason = planner.get("reason")
    drift_gate_ready = bool(planner.get("drift_gate_ready") is True)
    contracts_meta = planner.get("contracts") or []

    validations: List[Dict[str, Any]] = []

    for c in contracts_meta:
        path_str = c.get("contract_path")
        if not path_str:
            validations.append({
                "contract_path": None,
                "valid": False,
                "severity": "CRITICAL",
                "errors": ["contract_path_missing_in_manifest"],
                "warnings": [],
                "info": [],
            })
            continue

        path = Path(path_str)

        if not path.exists():
            validations.append({
                "contract_path": str(path),
                "valid": False,
                "severity": "CRITICAL",
                "errors": ["contract_file_missing"],
                "warnings": [],
                "info": [],
            })
            continue

        validations.append(validate_contract(path, drift_gate_ready))

    valid_count = sum(1 for v in validations if v.get("valid") is True)
    invalid_count = sum(1 for v in validations if v.get("valid") is False)
    warning_count = sum(1 for v in validations if v.get("warnings"))

    if not contracts_meta:
        attention.append("no_contracts_in_planner_manifest")

    if critical:
        validator_status = "OFFLINE_RESEARCH_CONTRACT_VALIDATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_PLANNER_MANIFEST"
        reason = "; ".join(critical)

    elif invalid_count > 0:
        validator_status = "OFFLINE_RESEARCH_CONTRACT_VALIDATOR_FAILED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INVALID_CONTRACTS"
        reason = f"invalid_count={invalid_count}; valid_count={valid_count}"

    elif warning_count > 0 and drift_gate_ready is False:
        validator_status = "OFFLINE_RESEARCH_CONTRACTS_VALID_WITH_WARNINGS_GATE_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_VALID_CONTRACTS_QUEUED_UNTIL_DRIFT_GATE_READY"
        reason = f"valid_count={valid_count}; warning_count={warning_count}; drift_gate_ready=False"

    elif drift_gate_ready is False:
        validator_status = "OFFLINE_RESEARCH_CONTRACTS_VALID_GATE_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_VALID_CONTRACTS_QUEUED_UNTIL_DRIFT_GATE_READY"
        reason = f"valid_count={valid_count}; drift_gate_ready=False"

    else:
        validator_status = "OFFLINE_RESEARCH_CONTRACTS_VALID_READY_FOR_OFFLINE_RESEARCH"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_OR_OFFLINE_RESEARCH"
        next_action = "CREATE_OFFLINE_RESEARCH_RUNNER_PLAN"
        reason = f"valid_count={valid_count}; drift_gate_ready=True"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "validator_status": validator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "planner_source": str(PLANNER_LATEST),
        "planner_status": planner_status,
        "planner_reason": planner_reason,

        "closed": planner.get("closed"),
        "drift_remaining": planner.get("drift_remaining"),
        "capital_remaining": planner.get("capital_remaining"),
        "drift_gate_ready": drift_gate_ready,

        "contract_count": len(validations),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "warning_count": warning_count,

        "validations": validations,

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

    out_json = RUN_DIR / "offline_research_contract_validator_v1_state.json"
    out_md = RUN_DIR / "offline_research_contract_validator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS OFFLINE RESEARCH CONTRACT VALIDATOR v1",
        "",
        f"validator_status: {validator_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Gate",
        "",
        f"closed: {planner.get('closed')}",
        f"drift_remaining: {planner.get('drift_remaining')}",
        f"capital_remaining: {planner.get('capital_remaining')}",
        f"drift_gate_ready: {drift_gate_ready}",
        "",
        "## Validation Summary",
        "",
        f"contract_count: {len(validations)}",
        f"valid_count: {valid_count}",
        f"invalid_count: {invalid_count}",
        f"warning_count: {warning_count}",
        "",
        "## Contracts",
        "",
    ]

    for v in validations:
        md_lines.append(
            f"- {v.get('source_hypothesis_id')} | {v.get('experiment_type')} | "
            f"valid={v.get('valid')} | severity={v.get('severity')} | path={v.get('contract_path')}"
        )
        if v.get("errors"):
            md_lines.append(f"  errors: {v.get('errors')}")
        if v.get("warnings"):
            md_lines.append(f"  warnings: {v.get('warnings')}")

    md_lines.extend([
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
    print("EDGE FACTORY OS OFFLINE RESEARCH CONTRACT VALIDATOR v1")
    print("=" * 100)
    print(f"validator_status: {validator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("GATE")
    print("-" * 100)
    print(f"closed: {planner.get('closed')}")
    print(f"drift_remaining: {planner.get('drift_remaining')}")
    print(f"capital_remaining: {planner.get('capital_remaining')}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print()
    print("VALIDATION SUMMARY")
    print("-" * 100)
    print(f"contract_count: {len(validations)}")
    print(f"valid_count: {valid_count}")
    print(f"invalid_count: {invalid_count}")
    print(f"warning_count: {warning_count}")
    print()
    print("CONTRACTS")
    print("-" * 100)
    for v in validations:
        print(f"{v.get('source_hypothesis_id')} | {v.get('experiment_type')} | valid={v.get('valid')} | severity={v.get('severity')}")
        if v.get("errors"):
            print(f"  errors: {v.get('errors')}")
        if v.get("warnings"):
            print(f"  warnings: {v.get('warnings')}")
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
