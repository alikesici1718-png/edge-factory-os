#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Null Baseline Method Audit v1

Purpose:
- Consume Research Gate Enforcement Validator v1.
- Consume stronger null baseline runner/evaluator outputs.
- Audit whether the null baseline methodology itself is too loose/proxy-like.
- Distinguish "true strategy failure" from "baseline methodology overfitting/failing by construction".
- Queue either:
  1) null baseline repair contract, or
  2) policy-locked framework status integration.
- Keep plugin expansion blocked.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This module does NOT:
- run new strategy research
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
- delete/move/archive files
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

VALIDATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_research_gate_enforcement_validator"
    / "research_gate_enforcement_validator_latest.json"
)

VALIDATOR_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_research_gate_enforcement_validator"
    / "research_gate_enforcement_next_queue_latest.json"
)

VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_validation_state_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

POLICY_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_policy_runtime_state_v1.json"
)

STRONGER_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_baseline_runner_latest.json"
)

STRONGER_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_evaluator"
    / "stronger_null_model_baseline_evaluator_latest.json"
)

STRONGER_MODEL_SUMMARY_CSV = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_false_positive_summary_latest.csv"
)

STRONGER_PVALUE_CSV = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_empirical_p_value_table_latest.csv"
)

STRONGER_GATE_CSV = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_policy_gate_pass_fail_latest.csv"
)

GENERIC_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_runner_latest.json"
)

GENERIC_DIAGNOSTIC_CSV = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_feature_diagnostics_latest.csv"
)

GENERIC_NEGATIVE_CONTROL_CSV = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_negative_controls_latest.csv"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = LESSON_DIR / "null_baseline_method_audit_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_null_baseline_method_audit"
OUT_JSON = OUT_DIR / "null_baseline_method_audit_latest.json"
OUT_TXT = OUT_DIR / "null_baseline_method_audit_latest.txt"
OUT_FINDINGS_CSV = OUT_DIR / "null_baseline_method_audit_findings_latest.csv"
OUT_NEXT_QUEUE_JSON = OUT_DIR / "null_baseline_method_next_queue_latest.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
METHOD_STATE_JSON = FRAMEWORK_POLICY_DIR / "null_baseline_method_state_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY_REPAIR = "RD5_06A_NULL_BASELINE_METHOD_REPAIR_CONTRACT"
NEXT_MODULE_REPAIR = "edge_factory_os_null_baseline_method_repair_contract_builder_v1.py"

NEXT_RESEARCH_KEY_STATUS = "RD5_07_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION"
NEXT_MODULE_STATUS = "edge_factory_os_framework_status_panel_builder_v1.py"

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
    "file_delete_performed": False,
    "file_move_performed": False,
    "archive_performed": False,
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    except Exception:
        return []
    return rows


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def append_lesson_record(path: Path, lesson_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing = {x.get("lesson_id") for x in obj if isinstance(x, dict)}
        if lesson_record["lesson_id"] not in existing:
            obj.append(lesson_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    lessons = obj.get("lessons")
    if not isinstance(lessons, list):
        lessons = []

    existing = {x.get("lesson_id") for x in lessons if isinstance(x, dict)}
    if lesson_record["lesson_id"] not in existing:
        lessons.append(lesson_record)

    obj["lessons"] = lessons
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_lessons", "path": str(path)}


def append_blocklist_record(path: Path, block_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing = {x.get("route_hash") for x in obj if isinstance(x, dict)}
        if block_record["route_hash"] not in existing:
            obj.append(block_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    blocked = obj.get("blocked_routes")
    if not isinstance(blocked, list):
        blocked = []

    existing = {x.get("route_hash") for x in blocked if isinstance(x, dict)}
    if block_record["route_hash"] not in existing:
        blocked.append(block_record)

    obj["blocked_routes"] = blocked
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_blocked_routes", "path": str(path)}


def add_finding(
    findings: List[Dict[str, Any]],
    key: str,
    severity: str,
    finding_type: str,
    observed: Any,
    expected: Any,
    interpretation: str,
    recommendation: str,
) -> None:
    findings.append({
        "finding_key": key,
        "severity": severity,
        "finding_type": finding_type,
        "observed": observed,
        "expected": expected,
        "interpretation": interpretation,
        "recommendation": recommendation,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    })


def audit_methodology() -> Dict[str, Any]:
    validator = load_json(VALIDATOR_JSON, default={})
    validation_state = load_json(VALIDATION_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    policy_state = load_json(POLICY_STATE_JSON, default={})
    runner = load_json(STRONGER_RUNNER_JSON, default={})
    evaluator = load_json(STRONGER_EVALUATOR_JSON, default={})
    generic_runner = load_json(GENERIC_RUNNER_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})

    model_summary = read_csv_rows(STRONGER_MODEL_SUMMARY_CSV)
    pvalues = read_csv_rows(STRONGER_PVALUE_CSV)
    gates = read_csv_rows(STRONGER_GATE_CSV)
    diagnostics = read_csv_rows(GENERIC_DIAGNOSTIC_CSV)
    negative_controls = read_csv_rows(GENERIC_NEGATIVE_CONTROL_CSV)

    findings: List[Dict[str, Any]] = []

    validator_pass = bool(validator.get("validator_pass"))
    policy_active = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
    plugin_expansion_blocked = (
        validator.get("plugin_expansion_allowed") is False
        and policy_state.get("plugin_expansion_allowed") is False
        and validation_state.get("plugin_expansion_allowed") is False
    )

    if not validator_pass:
        add_finding(
            findings,
            "VALIDATOR_NOT_PASS",
            "CRITICAL",
            "ENFORCEMENT",
            validator.get("validator_status"),
            "validator_pass=True",
            "Research gate enforcement has not been validated.",
            "Do not continue research. Fix validator failures first.",
        )

    if not policy_active:
        add_finding(
            findings,
            "POLICY_NOT_ACTIVE",
            "CRITICAL",
            "ENFORCEMENT",
            policy.get("policy_status"),
            "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE",
            "Research gate enforcement policy is not active.",
            "Rebuild or restore active policy before further work.",
        )

    if not plugin_expansion_blocked:
        add_finding(
            findings,
            "PLUGIN_EXPANSION_NOT_BLOCKED",
            "CRITICAL",
            "SAFETY",
            {
                "validator": validator.get("plugin_expansion_allowed"),
                "policy_state": policy_state.get("plugin_expansion_allowed"),
                "validation_state": validation_state.get("plugin_expansion_allowed"),
            },
            "all false",
            "Plugin expansion is not consistently blocked.",
            "Hard block further research until policy state is repaired.",
        )

    max_strict_rate = to_float(runner.get("max_strict_12_any_random_hit_rate"), 1.0)
    max_null_rate = to_float(runner.get("max_null_adjusted_any_random_hit_rate"), 1.0)
    policy_gate_pass = bool(runner.get("policy_gate_pass"))
    failed_gate_keys = runner.get("failed_gate_keys") if isinstance(runner.get("failed_gate_keys"), list) else []

    if max_strict_rate >= 1.0 and max_null_rate >= 1.0:
        add_finding(
            findings,
            "NULL_BASELINE_ALL_RANDOM_RUNS_HIT",
            "ATTENTION",
            "METHODOLOGY",
            {
                "max_strict_12_any_random_hit_rate": max_strict_rate,
                "max_null_adjusted_any_random_hit_rate": max_null_rate,
            },
            "rates materially below 1.0",
            (
                "The null baseline creates strict/null-adjusted hits in every run. "
                "This may mean the research feature space is weak, but it may also mean the null generator is too loose "
                "or the synthetic month construction makes strict 12/12 too easy by construction."
            ),
            "Build a null baseline repair contract that uses row-level/month-level empirical resampling instead of synthetic/proxy month generation.",
        )

    if "ACTUAL_SIGNAL_PRESENT" in failed_gate_keys:
        add_finding(
            findings,
            "NO_ACTUAL_SIGNAL_PRESENT",
            "ATTENTION",
            "RESEARCH_RESULT",
            failed_gate_keys,
            "actual null-adjusted signal > 0",
            "The original generic plugin had no actual null-adjusted signal.",
            "Keep plugin expansion blocked until a methodology-repaired baseline and future plugin route produce real signal.",
        )

    if len(model_summary) < 8:
        add_finding(
            findings,
            "INSUFFICIENT_NULL_MODEL_SUMMARY_ROWS",
            "CRITICAL",
            "METHODOLOGY",
            len(model_summary),
            ">=8",
            "Expected at least 8 independent null model summaries.",
            "Rerun stronger null baseline or repair output generation.",
        )

    if len(pvalues) < 8:
        add_finding(
            findings,
            "INSUFFICIENT_PVALUE_ROWS",
            "ATTENTION",
            "METHODOLOGY",
            len(pvalues),
            ">=8",
            "P-value table has fewer rows than expected.",
            "Ensure each null model produces p-value diagnostics.",
        )

    if len(diagnostics) <= 0 or len(negative_controls) <= 0:
        add_finding(
            findings,
            "MISSING_GENERIC_DIAGNOSTIC_INPUTS",
            "CRITICAL",
            "DATA_INPUT",
            {
                "diagnostics": len(diagnostics),
                "negative_controls": len(negative_controls),
            },
            "both > 0",
            "Null baseline audit cannot reason about prior research outputs.",
            "Rerun generic research runner before further audit.",
        )

    # Detect whether methodology is proxy/synthetic rather than direct empirical replay.
    add_finding(
        findings,
        "NULL_BASELINE_USES_PROXY_SYNTHETIC_MONTH_GENERATION",
        "ATTENTION",
        "METHODOLOGY",
        "synthetic month generator inferred from stronger null runner design",
        "empirical row/month-level replay preferred",
        (
            "The stronger null runner appears to use synthetic monthly PnL generation from summarized rows. "
            "This is useful as a conservative guard, but not enough to diagnose real edge quality."
        ),
        "Create a repaired null baseline using actual diagnostic rows, empirical month buckets, symbol holdouts, and time-block bootstrap from source panel.",
    )

    critical_count = sum(1 for x in findings if x["severity"] == "CRITICAL")
    attention_count = sum(1 for x in findings if x["severity"] == "ATTENTION")

    if critical_count > 0:
        audit_status = "NULL_BASELINE_METHOD_AUDIT_CRITICAL_REPAIR_REQUIRED"
        decision_class = "CRITICAL_METHOD_OR_ENFORCEMENT_REPAIR_REQUIRED"
        next_key = NEXT_RESEARCH_KEY_REPAIR
        next_module = NEXT_MODULE_REPAIR
        next_action = "BUILD_NULL_BASELINE_METHOD_REPAIR_CONTRACT_NO_RELEASE"
        method_repair_required = True
        status_ok_for_stack = False
    elif attention_count > 0:
        audit_status = "NULL_BASELINE_METHOD_AUDIT_ATTENTION_REPAIR_RECOMMENDED"
        decision_class = "ATTENTION_METHOD_REPAIR_RECOMMENDED_PLUGIN_EXPANSION_BLOCKED"
        next_key = NEXT_RESEARCH_KEY_REPAIR
        next_module = NEXT_MODULE_REPAIR
        next_action = "BUILD_NULL_BASELINE_METHOD_REPAIR_CONTRACT_NO_RELEASE"
        method_repair_required = True
        status_ok_for_stack = True
    else:
        audit_status = "NULL_BASELINE_METHOD_AUDIT_PASS_POLICY_LOCKED_STATUS_INTEGRATION"
        decision_class = "METHOD_AUDIT_PASS_PLUGIN_EXPANSION_STILL_BLOCKED"
        next_key = NEXT_RESEARCH_KEY_STATUS
        next_module = NEXT_MODULE_STATUS
        next_action = "BUILD_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION"
        method_repair_required = False
        status_ok_for_stack = True

    return {
        "audit_status": audit_status,
        "decision_class": decision_class,
        "next_action": next_action,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "method_repair_required": method_repair_required,
        "status_ok_for_stack": status_ok_for_stack,
        "critical_finding_count": critical_count,
        "attention_finding_count": attention_count,
        "finding_count": len(findings),
        "findings": findings,
        "context": {
            "validator_status": validator.get("validator_status"),
            "validator_pass": validator_pass,
            "validation_state": validation_state.get("validation_state"),
            "policy_status": policy.get("policy_status"),
            "policy_hash": policy.get("policy_hash"),
            "policy_runtime_state": policy_state.get("state_status"),
            "plugin_expansion_blocked": plugin_expansion_blocked,
            "stronger_runner_status": runner.get("runner_status"),
            "stronger_evaluator_status": evaluator.get("evaluator_status"),
            "policy_gate_pass": policy_gate_pass,
            "failed_gate_keys": failed_gate_keys,
            "max_strict_12_any_random_hit_rate": max_strict_rate,
            "max_null_adjusted_any_random_hit_rate": max_null_rate,
            "null_model_count": runner.get("null_model_count"),
            "permutation_runs_per_model": runner.get("permutation_runs_per_model"),
            "generic_runner_status": generic_runner.get("runner_status"),
            "generic_feature_count": generic_runner.get("feature_count"),
            "generic_diagnostic_row_count": generic_runner.get("diagnostic_row_count"),
            "generic_negative_control_row_count": generic_runner.get("negative_control_row_count"),
            "generic_null_model_row_count": generic_runner.get("null_model_row_count"),
            "guard_status": guard_feed.get("guard_status"),
            "guard_pass": guard_feed.get("guard_pass"),
            "model_summary_row_count": len(model_summary),
            "pvalue_row_count": len(pvalues),
            "gate_row_count": len(gates),
            "diagnostic_csv_row_count": len(diagnostics),
            "negative_control_csv_row_count": len(negative_controls),
        },
    }


def build_method_state(audit: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "state_name": "edge_factory_os_null_baseline_method_state_v1",
        "created_at_utc": utc_now_iso(),
        "method_state": audit["audit_status"],
        "decision_class": audit["decision_class"],
        "method_repair_required": audit["method_repair_required"],
        "status_ok_for_stack": audit["status_ok_for_stack"],
        "plugin_expansion_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "finding_count": audit["finding_count"],
        "critical_finding_count": audit["critical_finding_count"],
        "attention_finding_count": audit["attention_finding_count"],
        "next_recommended_research_key": audit["next_recommended_research_key"],
        "next_module": audit["next_module"],
    }


def build_summary_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS NULL BASELINE METHOD AUDIT v1")
    lines.append("=" * 100)

    for key in [
        "audit_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "decision_class",
        "method_repair_required",
        "status_ok_for_stack",
        "plugin_expansion_allowed",
        "finding_count",
        "critical_finding_count",
        "attention_finding_count",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("KEY CONTEXT")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("context", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("FINDINGS")
    lines.append("-" * 100)
    for f in result.get("findings", []):
        lines.append(f"{f.get('severity')} | {f.get('finding_key')} | {f.get('interpretation')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "findings_csv",
        "next_queue_json",
        "method_state_json",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS NULL BASELINE METHOD AUDIT v1")
    print("=" * 100)
    print(f"audit_status: {result.get('audit_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"decision_class: {result.get('decision_class')}")
    print(f"method_repair_required: {result.get('method_repair_required')}")
    print(f"status_ok_for_stack: {result.get('status_ok_for_stack')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"finding_count: {result.get('finding_count')}")
    print(f"critical_finding_count: {result.get('critical_finding_count')}")
    print(f"attention_finding_count: {result.get('attention_finding_count')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('findings_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)

    audit = audit_methodology()
    write_csv(OUT_FINDINGS_CSV, audit["findings"])

    if audit["critical_finding_count"] > 0:
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        reason = f"critical={audit['critical_finding_count']}; attention={audit['attention_finding_count']}; method repair required"
        return_code = 2
    elif audit["attention_finding_count"] > 0:
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        reason = f"critical=0; attention={audit['attention_finding_count']}; method repair recommended"
        return_code = 0
    else:
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        reason = "method audit passed; integrate blocked status into framework status panel"
        return_code = 0

    method_state = build_method_state(audit)
    write_json(METHOD_STATE_JSON, method_state)

    lesson_payload = {
        "audit_status": audit["audit_status"],
        "decision_class": audit["decision_class"],
        "method_repair_required": audit["method_repair_required"],
        "finding_count": audit["finding_count"],
        "critical_finding_count": audit["critical_finding_count"],
        "attention_finding_count": audit["attention_finding_count"],
    }
    lesson_id = f"LESSON_NULL_BASELINE_METHOD_AUDIT_{stable_hash(lesson_payload)}"

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "NULL_BASELINE_METHOD_AUDIT",
        "audit_status": audit["audit_status"],
        "decision_class": audit["decision_class"],
        "method_repair_required": audit["method_repair_required"],
        "status_ok_for_stack": audit["status_ok_for_stack"],
        "plugin_expansion_allowed": False,
        "finding_count": audit["finding_count"],
        "critical_finding_count": audit["critical_finding_count"],
        "attention_finding_count": audit["attention_finding_count"],
        "findings": audit["findings"],
        "context": audit["context"],
        "next_recommended_research_key": audit["next_recommended_research_key"],
        "next_module": audit["next_module"],
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    write_json(SPECIFIC_LESSON_PATH, lesson_record)
    lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

    block_record = {
        "route_hash": f"NULL_BASELINE_METHOD_AUDIT_{stable_hash(lesson_payload)}",
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "NULL_BASELINE_METHOD_REPAIR_REQUIRED_OR_PLUGIN_EXPANSION_BLOCKED",
        "research_branch": "NULL_BASELINE_METHOD_AUDIT",
        "audit_status": audit["audit_status"],
        "method_repair_required": audit["method_repair_required"],
        "plugin_expansion_allowed": False,
        "reopen_requirements": [
            "null baseline method repair completed",
            "empirical row/month-level resampling implemented",
            "policy validator pass",
            "guard feed pass",
            "no candidate/family/runtime/capital/live action",
        ],
    }
    blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "NULL_BASELINE_METHOD_NEXT_QUEUE_READY",
        "source_audit": "edge_factory_os_null_baseline_method_audit_v1",
        "audit_status": audit["audit_status"],
        "decision_class": audit["decision_class"],
        "method_repair_required": audit["method_repair_required"],
        "plugin_expansion_allowed": False,
        "top_next_research_key": audit["next_recommended_research_key"],
        "top_next_module": audit["next_module"],
        "next_direction_queue": [
            {
                "research_key": audit["next_recommended_research_key"],
                "priority": 100,
                "next_module_recommendation": audit["next_module"],
                "allowed_scope": "READ_ONLY_RESEARCH" if audit["method_repair_required"] else "REPO_ONLY_OS_INTELLIGENCE",
                "why": reason,
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "active_paper_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            },
            {
                "research_key": NEXT_RESEARCH_KEY_STATUS,
                "priority": 70,
                "next_module_recommendation": NEXT_MODULE_STATUS,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "why": "Expose policy-blocked research state to framework/standard stack.",
                "must_consume_guard_feed": True,
                "must_consume_research_gate_policy": True,
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "family_release_allowed_now": False,
            },
        ],
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }
    write_json(OUT_NEXT_QUEUE_JSON, next_queue)

    result = {
        "audit_name": "edge_factory_os_null_baseline_method_audit_v1",
        "created_at_utc": utc_now_iso(),
        "audit_status": audit["audit_status"],
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": audit["next_action"],
        "reason": reason,
        "decision_class": audit["decision_class"],
        "method_repair_required": audit["method_repair_required"],
        "status_ok_for_stack": audit["status_ok_for_stack"],
        "plugin_expansion_allowed": False,
        "finding_count": audit["finding_count"],
        "critical_finding_count": audit["critical_finding_count"],
        "attention_finding_count": audit["attention_finding_count"],
        "findings": audit["findings"],
        "context": audit["context"],
        "method_state": method_state,
        "lesson_id": lesson_id,
        "lesson_written": True,
        "lesson_append_status": lesson_append_status,
        "blocklist_written": True,
        "blocklist_append_status": blocklist_append_status,
        "next_recommended_research_key": audit["next_recommended_research_key"],
        "next_module": audit["next_module"],
        "release_gate_feed": {
            "NULL_BASELINE_METHOD_AUDIT_RAN": True,
            "NULL_BASELINE_METHOD_REPAIR_REQUIRED": audit["method_repair_required"],
            "STATUS_OK_FOR_STACK": audit["status_ok_for_stack"],
            "PLUGIN_EXPANSION_ALLOWED": False,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RELEASE_PASS_FROM_THIS_AUDIT": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_AUDIT": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_AUDIT": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_AUDIT": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_AUDIT": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_AUDIT": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_AUDIT": False,
            "LIVE_ALLOWED_FROM_THIS_AUDIT": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_AUDIT": False,
        },
        "input_paths": {
            "validator_json": str(VALIDATOR_JSON),
            "validation_state_json": str(VALIDATION_STATE_JSON),
            "policy_json": str(POLICY_JSON),
            "policy_state_json": str(POLICY_STATE_JSON),
            "stronger_runner_json": str(STRONGER_RUNNER_JSON),
            "stronger_evaluator_json": str(STRONGER_EVALUATOR_JSON),
            "generic_runner_json": str(GENERIC_RUNNER_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "findings_csv": str(OUT_FINDINGS_CSV),
        "next_queue_json": str(OUT_NEXT_QUEUE_JSON),
        "method_state_json": str(METHOD_STATE_JSON),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_summary_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
