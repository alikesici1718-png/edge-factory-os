#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads an offline experiment contract JSON and validates it against the canonical contract schema, checking required fields, safety hard-rules, and metadata completeness.
Outputs a structured validation report JSON to the edge_factory_offline_experiment_contract_validator_v1 workspace directory.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SCHEMA_ROOT = WORKSPACE / "edge_factory_offline_experiment_contract_schema_v1"
OUT_ROOT = WORKSPACE / "edge_factory_offline_experiment_contract_validator_v1"

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def is_empty_value(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, list) and len(v) == 0:
        return True
    if isinstance(v, dict) and len(v) == 0:
        return True
    return False

def nested_get(obj: dict[str, Any], section: str, key: str) -> Any:
    sec = obj.get(section, {})
    if not isinstance(sec, dict):
        return None
    return sec.get(key)

def add_check(rows, check, passed, severity, evidence):
    rows.append({
        "check": check,
        "passed": bool(passed),
        "severity": severity,
        "evidence": str(evidence),
    })

def main() -> int:
    ap = argparse.ArgumentParser(description="Validate an Edge Factory offline experiment contract.")
    ap.add_argument("--contract", default="", help="Path to candidate contract JSON. If omitted, validates latest template structurally.")
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"contract_validator_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    schema_dir = latest_dir(SCHEMA_ROOT, "offline_experiment_contract_schema_v1_")
    schema_path = schema_dir / "offline_experiment_contract_schema_v1.json" if schema_dir else None
    policy_path = schema_dir / "candidate_validation_gate_policy_v1.json" if schema_dir else None
    template_path = schema_dir / "offline_experiment_contract_template_v1.json" if schema_dir else None

    contract_path = Path(args.contract) if args.contract else template_path

    schema = read_json(schema_path)
    policy = read_json(policy_path)
    contract = read_json(contract_path)

    checks = []

    add_check(checks, "schema_loaded", bool(schema) and "__read_error__" not in schema, "CRITICAL", schema_path)
    add_check(checks, "policy_loaded", bool(policy) and "__read_error__" not in policy, "CRITICAL", policy_path)
    add_check(checks, "contract_loaded", bool(contract) and "__read_error__" not in contract, "CRITICAL", contract_path)

    required_sections = schema.get("required_sections", [])
    section_requirements = schema.get("section_requirements", {})

    for section in required_sections:
        exists = section in contract and isinstance(contract.get(section), dict)
        add_check(checks, f"section_exists:{section}", exists, "CRITICAL", section)

        required_keys = section_requirements.get(section, {}).get("required", [])
        for key in required_keys:
            sec_obj = contract.get(section, {})
            exists_key = isinstance(sec_obj, dict) and key in sec_obj
            val = sec_obj.get(key) if isinstance(sec_obj, dict) else None
            non_empty = not is_empty_value(val)

            add_check(
                checks,
                f"field_exists:{section}.{key}",
                exists_key,
                "CRITICAL",
                f"value={val!r}",
            )

            # Empty values are attention, not critical, because template files are allowed to be structurally valid.
            add_check(
                checks,
                f"field_non_empty:{section}.{key}",
                non_empty,
                "ATTENTION",
                f"value={val!r}",
            )

    # Safety invariants.
    hard_rules = schema.get("hard_rules", {})
    add_check(
        checks,
        "hard_rule_offline_only",
        hard_rules.get("offline_only") is True,
        "CRITICAL",
        hard_rules,
    )
    add_check(
        checks,
        "hard_rule_no_live",
        hard_rules.get("does_not_enable_live") is True and hard_rules.get("does_not_place_orders") is True,
        "CRITICAL",
        hard_rules,
    )

    # Policy thresholds.
    thresholds = policy.get("minimum_thresholds", {})
    required_thresholds = [
        "offline_min_trades",
        "offline_min_symbols",
        "walk_forward_min_folds",
        "walk_forward_min_positive_fold_rate",
        "monthly_positive_rate_min",
        "profit_factor_min",
        "market_replay_net_bps_mean_min",
        "shadow_min_closed_trades_before_review",
        "active_paper_min_closed_trades_before_capital_review",
    ]
    for t in required_thresholds:
        add_check(
            checks,
            f"policy_threshold_exists:{t}",
            t in thresholds and thresholds[t] is not None,
            "CRITICAL",
            thresholds.get(t),
        )

    # Candidate classification.
    identity = contract.get("identity", {}) if isinstance(contract.get("identity"), dict) else {}
    candidate_key = identity.get("candidate_key", "")
    is_template = candidate_key in {"example_candidate_key", "", None}

    critical_failed = [x for x in checks if not x["passed"] and x["severity"] == "CRITICAL"]
    attention_failed = [x for x in checks if not x["passed"] and x["severity"] == "ATTENTION"]

    if critical_failed:
        validation_status = "CONTRACT_INVALID_CRITICAL"
    elif is_template:
        validation_status = "TEMPLATE_STRUCTURE_VALID_NOT_A_CANDIDATE"
    elif attention_failed:
        validation_status = "CONTRACT_STRUCTURE_VALID_BUT_INCOMPLETE"
    else:
        validation_status = "CONTRACT_VALID_READY_FOR_OFFLINE_TESTING"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "schema_path": str(schema_path) if schema_path else None,
        "policy_path": str(policy_path) if policy_path else None,
        "contract_path": str(contract_path) if contract_path else None,
        "candidate_key": candidate_key,
        "is_template": is_template,
        "validation_status": validation_status,
        "critical_failed_count": len(critical_failed),
        "attention_failed_count": len(attention_failed),
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Validator does not run experiments.",
            "Validator does not touch MASTER_UPPER_SYSTEM.",
            "Validator does not start processes.",
            "Validator does not place orders.",
            "Validator does not enable live trading.",
        ],
        "checks": checks,
    }

    state_path = out_dir / "offline_experiment_contract_validator_v1_state.json"
    checks_path = out_dir / "offline_experiment_contract_validator_v1_checks.csv"
    report_path = out_dir / "offline_experiment_contract_validator_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(checks).to_csv(checks_path, index=False)

    md = []
    md.append("# Edge Factory Offline Experiment Contract Validator v1")
    md.append("")
    md.append(f"Validation status: `{validation_status}`")
    md.append(f"Candidate key: `{candidate_key}`")
    md.append(f"Is template: `{is_template}`")
    md.append(f"Critical failed: `{len(critical_failed)}`")
    md.append(f"Attention failed: `{len(attention_failed)}`")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("")
    md.append("## Failed checks")
    if critical_failed or attention_failed:
        for x in critical_failed + attention_failed:
            md.append(f"- `{x['severity']}` `{x['check']}` — {x['evidence']}")
    else:
        md.append("- None")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE EXPERIMENT CONTRACT VALIDATOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"schema    : {schema_path}")
    print(f"policy    : {policy_path}")
    print(f"contract  : {contract_path}")
    print(f"candidate : {candidate_key}")
    print(f"is_template: {is_template}")
    print(f"validation_status: {validation_status}")
    print(f"critical_failed: {len(critical_failed)}")
    print(f"attention_failed: {len(attention_failed)}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("FAILED CHECKS")
    print("-" * 100)
    failed = pd.DataFrame([x for x in checks if not x["passed"]])
    if failed.empty:
        print("NONE")
    else:
        print(failed[["severity", "check", "evidence"]].head(60).to_string(index=False))

    print()
    print(f"State : {state_path}")
    print(f"Checks: {checks_path}")
    print(f"Report: {report_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

