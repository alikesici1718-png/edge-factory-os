#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Research Gate Enforcement Validator v1

Purpose:
- Validate that the active research gate enforcement policy is actually enforced.
- Validate that plugin expansion remains blocked after stronger null baseline gate failure.
- Validate that candidate/family/runtime/capital/live/real-order flags remain false.
- Validate router/contract/runner/evaluator artifacts consume or respect the gate policy.
- Queue either null baseline methodology audit or controlled policy-integrated next step.

This validator does NOT:
- run strategy research
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
from typing import Any, Dict, List, Tuple


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

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

ROUTER_SPEC_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "core"
    / "research_router_spec_v1.json"
)

CURRENT_GENERIC_CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "current_research_contract_v1.json"
)

STRONGER_NULL_CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "stronger_null_model_baseline_contract_v1.json"
)

STRONGER_NULL_PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "stronger_null_model_baseline_plugin_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

STRONGER_EVALUATOR_JSON = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_evaluator"
    / "stronger_null_model_baseline_evaluator_latest.json"
)

STRONGER_QUEUE_JSON = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_evaluator"
    / "stronger_null_model_next_queue_latest.json"
)

STRONGER_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_stronger_null_model_baseline_runner"
    / "stronger_null_model_baseline_runner_latest.json"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "research_gate_enforcement_validator_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_research_gate_enforcement_validator"
OUT_JSON = OUT_DIR / "research_gate_enforcement_validator_latest.json"
OUT_TXT = OUT_DIR / "research_gate_enforcement_validator_latest.txt"
OUT_CHECKS_CSV = OUT_DIR / "research_gate_enforcement_checks_latest.csv"
OUT_NEXT_QUEUE_JSON = OUT_DIR / "research_gate_enforcement_next_queue_latest.json"

FRAMEWORK_POLICY_DIR = REPO_DIR / "edge_factory_os_framework" / "policies"
VALIDATION_STATE_JSON = FRAMEWORK_POLICY_DIR / "research_gate_validation_state_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY_FAIL = "RD5_06_NULL_BASELINE_METHOD_AUDIT_AND_REPAIR"
NEXT_MODULE_FAIL = "edge_factory_os_null_baseline_method_audit_v1.py"

NEXT_RESEARCH_KEY_PASS = "RD5_06_POLICY_LOCKED_RESEARCH_SYSTEM_AUDIT"
NEXT_MODULE_PASS = "edge_factory_os_policy_locked_research_system_audit_v1.py"

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


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass"}


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


def add_check(rows: List[Dict[str, Any]], group: str, key: str, passed: bool, observed: Any, required: Any, severity: str = "HARD") -> None:
    rows.append({
        "check_group": group,
        "check_key": key,
        "passed": bool(passed),
        "observed": observed,
        "required": required,
        "severity": severity,
    })


def check_false_flags(rows: List[Dict[str, Any]], group: str, obj: Dict[str, Any], flag_prefix: str = "") -> None:
    for flag in [
        "candidate_generation_allowed",
        "candidate_contract_allowed",
        "family_release_allowed",
        "promotion_allowed",
        "runtime_touch_allowed",
        "launcher_allowed",
        "patch_runtime_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "execution_performed",
    ]:
        if flag in obj:
            add_check(
                rows,
                group,
                f"{flag_prefix}{flag}_false",
                obj.get(flag) is False,
                obj.get(flag),
                False,
                "HARD",
            )


def validate_all() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    policy = load_json(POLICY_JSON, default={})
    policy_state = load_json(POLICY_STATE_JSON, default={})
    router_spec = load_json(ROUTER_SPEC_JSON, default={})
    generic_contract = load_json(CURRENT_GENERIC_CONTRACT_JSON, default={})
    stronger_contract = load_json(STRONGER_NULL_CONTRACT_JSON, default={})
    stronger_plugin = load_json(STRONGER_NULL_PLUGIN_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    evaluator = load_json(STRONGER_EVALUATOR_JSON, default={})
    queue = load_json(STRONGER_QUEUE_JSON, default={})
    runner = load_json(STRONGER_RUNNER_JSON, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})

    rows: List[Dict[str, Any]] = []

    # Policy active checks
    rules = policy.get("enforced_gate_rules") if isinstance(policy.get("enforced_gate_rules"), dict) else {}

    add_check(
        rows,
        "policy",
        "policy_status_active",
        policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE",
        policy.get("policy_status"),
        "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE",
    )
    add_check(rows, "policy", "strict_policy_key", policy.get("strict_policy_key") == STRICT_POLICY_KEY, policy.get("strict_policy_key"), STRICT_POLICY_KEY)
    add_check(rows, "policy", "canonical_policy_month_count_12", to_int(policy.get("canonical_policy_month_count")) == 12, policy.get("canonical_policy_month_count"), 12)
    add_check(rows, "policy", "minimum_permutation_runs_ge_1000", to_int(rules.get("minimum_permutation_runs")) >= 1000, rules.get("minimum_permutation_runs"), ">=1000")
    add_check(rows, "policy", "required_independent_null_models_ge_8", to_int(rules.get("required_independent_null_models")) >= 8, rules.get("required_independent_null_models"), ">=8")
    add_check(rows, "policy", "plugin_expansion_blocked_before_validation", policy.get("plugin_expansion_allowed_before_policy_validation") is False, policy.get("plugin_expansion_allowed_before_policy_validation"), False)

    check_false_flags(rows, "policy_safety", policy)

    # Policy runtime state checks
    add_check(
        rows,
        "policy_state",
        "state_blocks_plugin_expansion",
        policy_state.get("plugin_expansion_allowed") is False,
        policy_state.get("plugin_expansion_allowed"),
        False,
    )
    add_check(
        rows,
        "policy_state",
        "state_status_active_blocked",
        policy_state.get("state_status") == "RESEARCH_GATE_POLICY_ACTIVE_PLUGIN_EXPANSION_BLOCKED",
        policy_state.get("state_status"),
        "RESEARCH_GATE_POLICY_ACTIVE_PLUGIN_EXPANSION_BLOCKED",
    )
    check_false_flags(rows, "policy_state_safety", policy_state)

    # Guard
    add_check(rows, "guard", "data_quality_guard_pass", guard_feed.get("guard_pass") is True, guard_feed.get("guard_pass"), True)

    # Stronger null result checks
    add_check(
        rows,
        "stronger_runner",
        "policy_gate_pass_false",
        runner.get("policy_gate_pass") is False,
        runner.get("policy_gate_pass"),
        False,
    )
    add_check(
        rows,
        "stronger_runner",
        "policy_gate_fail_count_ge_1",
        to_int(runner.get("policy_gate_fail_count")) >= 1,
        runner.get("policy_gate_fail_count"),
        ">=1",
    )
    add_check(
        rows,
        "stronger_runner",
        "failed_actual_signal_present",
        "ACTUAL_SIGNAL_PRESENT" in (runner.get("failed_gate_keys") if isinstance(runner.get("failed_gate_keys"), list) else []),
        runner.get("failed_gate_keys"),
        "contains ACTUAL_SIGNAL_PRESENT",
    )
    check_false_flags(rows, "stronger_runner_safety", runner)

    # Evaluator must keep expansion blocked
    add_check(
        rows,
        "stronger_evaluator",
        "plugin_expansion_allowed_false",
        evaluator.get("plugin_expansion_allowed") is False,
        evaluator.get("plugin_expansion_allowed"),
        False,
    )
    add_check(
        rows,
        "stronger_evaluator",
        "policy_remains_active",
        evaluator.get("research_gate_policy_remains_active") is True,
        evaluator.get("research_gate_policy_remains_active"),
        True,
    )
    add_check(
        rows,
        "stronger_evaluator",
        "next_module_validator",
        evaluator.get("next_module") == "edge_factory_os_research_gate_enforcement_validator_v1.py",
        evaluator.get("next_module"),
        "edge_factory_os_research_gate_enforcement_validator_v1.py",
    )
    check_false_flags(rows, "stronger_evaluator_safety", evaluator)

    # Queue checks
    add_check(
        rows,
        "queue",
        "queue_top_next_validator",
        queue.get("top_next_module") == "edge_factory_os_research_gate_enforcement_validator_v1.py",
        queue.get("top_next_module"),
        "edge_factory_os_research_gate_enforcement_validator_v1.py",
    )
    add_check(
        rows,
        "queue",
        "queue_plugin_expansion_false",
        queue.get("plugin_expansion_allowed") is False,
        queue.get("plugin_expansion_allowed"),
        False,
    )
    check_false_flags(rows, "queue_safety", queue)

    # Router/spec should not itself allow research/candidate/release
    router_safety = router_spec.get("safety_policy") if isinstance(router_spec.get("safety_policy"), dict) else {}
    add_check(
        rows,
        "router_spec",
        "router_can_generate_candidate_false",
        router_safety.get("router_can_generate_candidate") is False,
        router_safety.get("router_can_generate_candidate"),
        False,
    )
    add_check(
        rows,
        "router_spec",
        "router_can_release_family_false",
        router_safety.get("router_can_release_family") is False,
        router_safety.get("router_can_release_family"),
        False,
    )
    add_check(
        rows,
        "router_spec",
        "router_can_touch_runtime_false",
        router_safety.get("router_can_touch_runtime") is False,
        router_safety.get("router_can_touch_runtime"),
        False,
    )

    # Contract/plugin safety checks
    check_false_flags(rows, "generic_contract_safety", generic_contract)
    check_false_flags(rows, "stronger_contract_safety", stronger_contract)
    check_false_flags(rows, "stronger_plugin_safety", stronger_plugin)

    add_check(
        rows,
        "stronger_contract",
        "contract_requires_policy",
        stronger_contract.get("policy_hash") == policy.get("policy_hash"),
        stronger_contract.get("policy_hash"),
        policy.get("policy_hash"),
    )
    add_check(
        rows,
        "stronger_plugin",
        "plugin_must_consume_policy",
        stronger_plugin.get("must_consume_research_gate_policy") is True,
        stronger_plugin.get("must_consume_research_gate_policy"),
        True,
    )
    add_check(
        rows,
        "stronger_plugin",
        "plugin_expansion_allowed_false",
        stronger_plugin.get("plugin_expansion_allowed") is False,
        stronger_plugin.get("plugin_expansion_allowed"),
        False,
    )

    # Lesson/blocklist presence
    lessons_count = 0
    if isinstance(lesson_index, dict) and isinstance(lesson_index.get("lessons"), list):
        lessons_count = len(lesson_index.get("lessons"))
    elif isinstance(lesson_index, list):
        lessons_count = len(lesson_index)

    blocked_count = 0
    blocked_hashes = []
    if isinstance(blocklist, dict) and isinstance(blocklist.get("blocked_routes"), list):
        blocked_hashes = [x.get("route_hash") for x in blocklist.get("blocked_routes") if isinstance(x, dict)]
        blocked_count = len(blocked_hashes)
    elif isinstance(blocklist, list):
        blocked_hashes = [x.get("route_hash") for x in blocklist if isinstance(x, dict)]
        blocked_count = len(blocked_hashes)

    add_check(rows, "lesson_memory", "lesson_count_positive", lessons_count > 0, lessons_count, ">0")
    add_check(rows, "blocklist", "blocked_route_count_positive", blocked_count > 0, blocked_count, ">0")
    add_check(
        rows,
        "blocklist",
        "stronger_route_hash_blocked",
        evaluator.get("route_hash") in blocked_hashes,
        evaluator.get("route_hash"),
        "present in candidate_route_blocklist",
    )

    context = {
        "policy": policy,
        "policy_state": policy_state,
        "router_spec": router_spec,
        "generic_contract": generic_contract,
        "stronger_contract": stronger_contract,
        "stronger_plugin": stronger_plugin,
        "guard_feed": guard_feed,
        "evaluator": evaluator,
        "queue": queue,
        "runner": runner,
        "lessons_count": lessons_count,
        "blocked_count": blocked_count,
    }

    return rows, context


def summarize_checks(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    hard_rows = [x for x in rows if x.get("severity") == "HARD"]
    failed = [x for x in hard_rows if not bool(x.get("passed"))]
    passed = [x for x in hard_rows if bool(x.get("passed"))]

    group_counts: Dict[str, Dict[str, int]] = {}
    for row in rows:
        g = str(row.get("check_group"))
        if g not in group_counts:
            group_counts[g] = {"pass": 0, "fail": 0}
        if bool(row.get("passed")):
            group_counts[g]["pass"] += 1
        else:
            group_counts[g]["fail"] += 1

    return {
        "check_count": len(rows),
        "hard_check_count": len(hard_rows),
        "hard_pass_count": len(passed),
        "hard_fail_count": len(failed),
        "failed_check_keys": [x.get("check_key") for x in failed],
        "failed_checks": failed,
        "group_counts": group_counts,
        "validator_pass": len(failed) == 0,
    }


def build_validation_state(result_stub: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "state_name": "edge_factory_os_research_gate_validation_state_v1",
        "created_at_utc": utc_now_iso(),
        "validation_state": (
            "RESEARCH_GATE_ENFORCEMENT_VALIDATED_PLUGIN_EXPANSION_BLOCKED"
            if summary.get("validator_pass")
            else "RESEARCH_GATE_ENFORCEMENT_VALIDATION_FAILED_REVIEW_REQUIRED"
        ),
        "validator_pass": bool(summary.get("validator_pass")),
        "hard_fail_count": summary.get("hard_fail_count"),
        "failed_check_keys": summary.get("failed_check_keys"),
        "policy_hash": result_stub.get("policy_hash"),
        "plugin_expansion_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "next_recommended_research_key": (
            NEXT_RESEARCH_KEY_FAIL
            if summary.get("validator_pass")
            else NEXT_RESEARCH_KEY_FAIL
        ),
        "next_module": (
            NEXT_MODULE_FAIL
            if summary.get("validator_pass")
            else NEXT_MODULE_FAIL
        ),
        "notes": (
            "Enforcement is active and plugin expansion remains blocked; next step is methodology audit/repair."
            if summary.get("validator_pass")
            else
            "Enforcement validation failed; next step is still methodology audit/repair, no plugin expansion."
        ),
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESEARCH GATE ENFORCEMENT VALIDATOR v1")
    lines.append("=" * 100)

    for key in [
        "validator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "validator_pass",
        "check_count",
        "hard_check_count",
        "hard_pass_count",
        "hard_fail_count",
        "failed_check_keys",
        "policy_hash",
        "plugin_expansion_allowed",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "next_recommended_research_key",
        "next_module",
        "lesson_id",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("FAILED CHECKS")
    lines.append("-" * 100)
    for row in result.get("failed_checks", []):
        lines.append(
            f"{row.get('check_group')} | {row.get('check_key')} | observed={row.get('observed')} | required={row.get('required')}"
        )

    lines.append("")
    lines.append("GROUP COUNTS")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("group_counts", {}), indent=2, ensure_ascii=False))

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
        "checks_csv",
        "next_queue_json",
        "validation_state_json",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESEARCH GATE ENFORCEMENT VALIDATOR v1")
    print("=" * 100)
    print(f"validator_status: {result.get('validator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"validator_pass: {result.get('validator_pass')}")
    print(f"check_count: {result.get('check_count')}")
    print(f"hard_check_count: {result.get('hard_check_count')}")
    print(f"hard_pass_count: {result.get('hard_pass_count')}")
    print(f"hard_fail_count: {result.get('hard_fail_count')}")
    print(f"failed_check_keys: {result.get('failed_check_keys')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
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
    print(f"CSV : {result.get('checks_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_POLICY_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    check_rows, context = validate_all()
    summary = summarize_checks(check_rows)
    write_csv(OUT_CHECKS_CSV, check_rows)

    policy = context["policy"]
    evaluator = context["evaluator"]
    runner = context["runner"]

    validator_pass = bool(summary["validator_pass"])

    if validator_pass:
        validator_status = "RESEARCH_GATE_ENFORCEMENT_VALIDATOR_PASS_PLUGIN_EXPANSION_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_action = "BUILD_NULL_BASELINE_METHOD_AUDIT_OR_REPAIR_NO_RELEASE"
        reason = (
            "Research gate enforcement is active and safety blocks are validated. "
            "Plugin expansion remains blocked; next step is null baseline methodology audit/repair."
        )
        next_key = NEXT_RESEARCH_KEY_FAIL
        next_module = NEXT_MODULE_FAIL
        return_code = 0
    else:
        validator_status = "RESEARCH_GATE_ENFORCEMENT_VALIDATOR_FAIL_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_RESEARCH_GATE_ENFORCEMENT_FAILURES_NO_RELEASE"
        reason = (
            f"Research gate enforcement validation failed; failed_checks={summary.get('failed_check_keys')}. "
            "No plugin expansion or candidate/release allowed."
        )
        next_key = NEXT_RESEARCH_KEY_FAIL
        next_module = NEXT_MODULE_FAIL
        return_code = 2

    lesson_payload = {
        "validator_status": validator_status,
        "validator_pass": validator_pass,
        "policy_hash": policy.get("policy_hash"),
        "failed_check_keys": summary.get("failed_check_keys"),
        "source_route_hash": evaluator.get("route_hash"),
    }
    lesson_id = f"LESSON_RESEARCH_GATE_VALIDATOR_{stable_hash(lesson_payload)}"

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "RESEARCH_GATE_ENFORCEMENT_VALIDATED",
        "validator_status": validator_status,
        "validator_pass": validator_pass,
        "policy_hash": policy.get("policy_hash"),
        "policy_status": policy.get("policy_status"),
        "source_runner_status": runner.get("runner_status"),
        "source_evaluator_status": evaluator.get("evaluator_status"),
        "source_route_hash": evaluator.get("route_hash"),
        "check_count": summary.get("check_count"),
        "hard_check_count": summary.get("hard_check_count"),
        "hard_fail_count": summary.get("hard_fail_count"),
        "failed_check_keys": summary.get("failed_check_keys"),
        "plugin_expansion_allowed": False,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "source_checks_csv": str(OUT_CHECKS_CSV),
    }

    block_record = {
        "route_hash": evaluator.get("route_hash"),
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "blocked_reason": "RESEARCH_GATE_ENFORCEMENT_VALIDATED_PLUGIN_EXPANSION_BLOCKED",
        "research_branch": "RESEARCH_GATE_ENFORCEMENT_VALIDATOR",
        "policy_hash": policy.get("policy_hash"),
        "validator_pass": validator_pass,
        "plugin_expansion_allowed": False,
        "reopen_requirements": [
            "null baseline methodology audit completed",
            "gate validator pass",
            "policy state permits next research scope",
            "data quality guard pass",
            "no blocked route hash reuse",
            "no candidate/family/runtime/capital/live action",
        ],
    }

    write_json(SPECIFIC_LESSON_PATH, lesson_record)
    lesson_append_status = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

    blocklist_append_status = None
    if evaluator.get("route_hash"):
        blocklist_append_status = append_blocklist_record(BLOCKLIST_PATH, block_record)

    result_stub = {
        "policy_hash": policy.get("policy_hash"),
    }
    validation_state = build_validation_state(result_stub, summary)
    write_json(VALIDATION_STATE_JSON, validation_state)

    next_queue = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESEARCH_GATE_ENFORCEMENT_NEXT_QUEUE_READY" if validator_pass else "RESEARCH_GATE_ENFORCEMENT_NEXT_QUEUE_REVIEW_REQUIRED",
        "source_validator": "edge_factory_os_research_gate_enforcement_validator_v1",
        "validator_pass": validator_pass,
        "policy_hash": policy.get("policy_hash"),
        "plugin_expansion_allowed": False,
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_direction_queue": [
            {
                "research_key": next_key,
                "priority": 100,
                "next_module_recommendation": next_module,
                "allowed_scope": "READ_ONLY_RESEARCH",
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
                "research_key": "RD5_07_FRAMEWORK_STATUS_PANEL_AND_STACK_INTEGRATION",
                "priority": 70,
                "next_module_recommendation": "edge_factory_os_framework_status_panel_builder_v1.py",
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "why": "Expose policy state and blocked research status to standard stack/control tower.",
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
        "validator_name": "edge_factory_os_research_gate_enforcement_validator_v1",
        "created_at_utc": utc_now_iso(),
        "validator_status": validator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "validator_pass": validator_pass,
        "check_count": summary.get("check_count"),
        "hard_check_count": summary.get("hard_check_count"),
        "hard_pass_count": summary.get("hard_pass_count"),
        "hard_fail_count": summary.get("hard_fail_count"),
        "failed_check_keys": summary.get("failed_check_keys"),
        "failed_checks": summary.get("failed_checks"),
        "group_counts": summary.get("group_counts"),
        "policy_hash": policy.get("policy_hash"),
        "policy_status": policy.get("policy_status"),
        "source_runner_status": runner.get("runner_status"),
        "source_evaluator_status": evaluator.get("evaluator_status"),
        "source_route_hash": evaluator.get("route_hash"),
        "plugin_expansion_allowed": False,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "lesson_id": lesson_id,
        "lesson_written": True,
        "lesson_append_status": lesson_append_status,
        "blocklist_written": bool(evaluator.get("route_hash")),
        "blocklist_append_status": blocklist_append_status,
        "validation_state": validation_state,
        "release_gate_feed": {
            "RESEARCH_GATE_ENFORCEMENT_VALIDATOR_RAN": True,
            "RESEARCH_GATE_ENFORCEMENT_VALIDATOR_PASS": validator_pass,
            "PLUGIN_EXPANSION_ALLOWED": False,
            "RESEARCH_GATE_POLICY_REMAINS_ACTIVE": True,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RELEASE_PASS_FROM_THIS_VALIDATOR": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_VALIDATOR": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_VALIDATOR": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_VALIDATOR": False,
            "LIVE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_VALIDATOR": False,
        },
        "input_paths": {
            "policy_json": str(POLICY_JSON),
            "policy_state_json": str(POLICY_STATE_JSON),
            "router_spec_json": str(ROUTER_SPEC_JSON),
            "generic_contract_json": str(CURRENT_GENERIC_CONTRACT_JSON),
            "stronger_null_contract_json": str(STRONGER_NULL_CONTRACT_JSON),
            "stronger_null_plugin_json": str(STRONGER_NULL_PLUGIN_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "stronger_evaluator_json": str(STRONGER_EVALUATOR_JSON),
            "stronger_queue_json": str(STRONGER_QUEUE_JSON),
            "stronger_runner_json": str(STRONGER_RUNNER_JSON),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "checks_csv": str(OUT_CHECKS_CSV),
        "next_queue_json": str(OUT_NEXT_QUEUE_JSON),
        "validation_state_json": str(VALIDATION_STATE_JSON),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
