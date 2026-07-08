#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

OUT_ROOT = WORKSPACE / "edge_factory_strict_validation_learning_finalizer_v1"
RESEARCH_MEMORY_ROOT = WORKSPACE / "edge_factory_os_research_learning_controller_v1"
MASTER_MEMORY = RESEARCH_MEMORY_ROOT / "edge_factory_research_learning_memory_master.jsonl"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def safe_float(x: Any, default: float | None = None) -> float | None:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default

def classify_strict_failure(strict: dict[str, Any]) -> dict[str, Any]:
    status = strict.get("validation_status", "UNKNOWN")
    metrics = strict.get("metrics", {}) if isinstance(strict.get("metrics"), dict) else {}

    full = metrics.get("full_cooldown", {}) or {}
    ins = metrics.get("in_sample_cooldown", {}) or {}
    oos = metrics.get("out_of_sample_cooldown", {}) or {}
    no_cd = metrics.get("full_no_cooldown_reference", {}) or {}

    full_pf = safe_float(full.get("profit_factor"), 0.0)
    full_mean = safe_float(full.get("mean_net_bps"), 0.0)
    full_median = safe_float(full.get("median_net_bps"), 0.0)

    is_pf = safe_float(ins.get("profit_factor"), 0.0)
    is_mean = safe_float(ins.get("mean_net_bps"), 0.0)

    oos_pf = safe_float(oos.get("profit_factor"), 0.0)
    oos_mean = safe_float(oos.get("mean_net_bps"), 0.0)

    no_cd_pf = safe_float(no_cd.get("profit_factor"), 0.0)
    no_cd_mean = safe_float(no_cd.get("mean_net_bps"), 0.0)

    positive_month_rate = safe_float(strict.get("positive_month_rate"), 0.0)
    positive_pf_month_rate = safe_float(strict.get("positive_pf_month_rate"), 0.0)

    tags = []
    lessons = []
    hard_blocks = []
    redesign_requirements = []

    if status == "STRICT_VALIDATION_FAIL_ARCHIVE_OR_REDESIGN":
        tags.append("strict_validation_failed")
        lessons.append("A diagnostic top combo is not enough; strict validation must pass before full-run.")
        hard_blocks.append("NO_FULL_RUN_FOR_THIS_STRICT_RULE")

    if full_pf is not None and full_pf < 1.0:
        tags.append("full_period_profit_factor_below_one")
        lessons.append("Full-period PF below 1 means no durable edge across the tested year.")
        hard_blocks.append("BLOCK_FULL_RUN_FULL_PF_BELOW_ONE")

    if full_mean is not None and full_mean < 0:
        tags.append("full_period_negative_mean")
        lessons.append("Full-period mean net return is negative; expectancy is not acceptable.")
        hard_blocks.append("BLOCK_FULL_RUN_NEGATIVE_FULL_MEAN")

    if full_median is not None and full_median < 0:
        tags.append("full_period_negative_median")
        lessons.append("Negative median means typical trade loses even if some subperiods look good.")

    if is_pf is not None and is_pf < 1.0:
        tags.append("in_sample_failed")
        lessons.append("In-sample failed after thresholds were fit; this is a strong overfit warning.")

    if oos_pf is not None and oos_pf > 1.0 and oos_mean is not None and oos_mean > 0:
        tags.append("oos_positive_but_not_sufficient")
        lessons.append("OOS can be positive while full/in-sample stability fails; do not promote from OOS alone.")

    if positive_month_rate is not None and positive_month_rate < 0.55:
        tags.append("monthly_stability_failed")
        lessons.append("Low positive month rate indicates regime/localized performance, not robust edge.")
        hard_blocks.append("BLOCK_PROMOTION_MONTH_STABILITY_FAILED")

    if no_cd_pf is not None and no_cd_pf < 1.0:
        tags.append("no_cooldown_reference_failed")
        lessons.append("Removing cooldown did not rescue the rule; failure is not just cooldown artifact.")

    redesign_requirements.extend([
        "Do not retune only thresholds/hold on the same feature set.",
        "Require genuinely new explanatory feature before retesting this family.",
        "Potential new evidence examples: volatility compression after impulse, follow-through filter, sector/market breadth confirmation, rejection of pump-and-dump candles, liquidity quality filter.",
        "Any redesigned variant must repeat strict validation with IS-fitted thresholds only.",
        "Do not create active paper from diagnostic-only evidence."
    ])

    return {
        "failure_tags": sorted(set(tags)),
        "lessons": sorted(set(lessons)),
        "hard_blocks": sorted(set(hard_blocks)),
        "redesign_requirements": redesign_requirements,
        "observed": {
            "full_pf": full_pf,
            "full_mean_net_bps": full_mean,
            "full_median_net_bps": full_median,
            "in_sample_pf": is_pf,
            "in_sample_mean_net_bps": is_mean,
            "oos_pf": oos_pf,
            "oos_mean_net_bps": oos_mean,
            "no_cooldown_pf": no_cd_pf,
            "no_cooldown_mean_net_bps": no_cd_mean,
            "positive_month_rate": positive_month_rate,
            "positive_pf_month_rate": positive_pf_month_rate,
        }
    }

def main() -> int:
    out_dir = OUT_ROOT / f"strict_validation_learning_finalizer_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    strict_state_path = latest_file(
        WORKSPACE / "edge_factory_post_impulse_strict_validation_v1",
        "post_impulse_strict_validation_v1_state.json"
    )
    strict = read_json(strict_state_path)

    blockers = []
    if not strict_state_path or not strict_state_path.exists():
        blockers.append("STRICT_VALIDATION_STATE_NOT_FOUND")
    if "__read_error__" in strict:
        blockers.append("STRICT_VALIDATION_STATE_READ_ERROR")

    candidate_key = strict.get("candidate_key", "UNKNOWN")
    base_candidate_key = strict.get("base_candidate_key", "UNKNOWN")
    family_key = strict.get("family_key", "UNKNOWN")
    validation_status = strict.get("validation_status", "UNKNOWN")

    classification = classify_strict_failure(strict)

    if blockers:
        finalizer_status = "STRICT_VALIDATION_LEARNING_FINALIZER_BLOCKED"
        lifecycle_status = "NO_UPDATE"
        next_action = "FIX_STRICT_VALIDATION_INPUT"
    elif validation_status == "STRICT_VALIDATION_FAIL_ARCHIVE_OR_REDESIGN":
        finalizer_status = "STRICT_VALIDATION_FAILURE_RECORDED"
        lifecycle_status = "ARCHIVE_WAIT_REDESIGN_REQUIRED"
        next_action = "UPDATE_SELECTOR_MEMORY_AND_MOVE_TO_NEXT_RESEARCH_TASK"
    elif "PASS" in validation_status:
        finalizer_status = "STRICT_VALIDATION_PASS_RECORDED"
        lifecycle_status = "OFFLINE_VALIDATED_WAITING_NEXT_GATE"
        next_action = "CREATE_RESULT_TO_LIFECYCLE_INPUT"
    else:
        finalizer_status = "STRICT_VALIDATION_UNKNOWN_RECORDED"
        lifecycle_status = "REVIEW_REQUIRED"
        next_action = "MANUAL_REVIEW_STRICT_VALIDATION_STATUS"

    memory_entry = {
        "created_at": now_iso(),
        "source": "strict_validation_learning_finalizer_v1",
        "strict_state_path": str(strict_state_path) if strict_state_path else None,
        "candidate_key": candidate_key,
        "base_candidate_key": base_candidate_key,
        "family_key": family_key,
        "validation_status": validation_status,
        "lifecycle_status": lifecycle_status,
        "decision": "STRICT_VALIDATION_FAIL" if validation_status == "STRICT_VALIDATION_FAIL_ARCHIVE_OR_REDESIGN" else validation_status,
        "metrics": strict.get("metrics", {}),
        "gate_blockers": strict.get("gate_blockers", []),
        "warnings": strict.get("warnings", []),
        "failure_tags": classification["failure_tags"],
        "lessons": classification["lessons"],
        "hard_blocks": classification["hard_blocks"],
        "redesign_requirements": classification["redesign_requirements"],
        "observed": classification["observed"],
        "full_run_allowed": False,
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

    if not blockers:
        append_jsonl(MASTER_MEMORY, memory_entry)

    memory_rows = read_jsonl(MASTER_MEMORY)

    archive_policy = {
        "policy_version": "edge_factory_candidate_archive_policy_v1",
        "generated_at": now_iso(),
        "candidate_updates": {
            candidate_key: {
                "lifecycle_status": lifecycle_status,
                "exact_rule_blocked": validation_status == "STRICT_VALIDATION_FAIL_ARCHIVE_OR_REDESIGN",
                "full_run_allowed": False,
                "promotion_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "capital_change_allowed": False,
                "reason": classification["lessons"],
                "gate_blockers": strict.get("gate_blockers", []),
                "warnings": strict.get("warnings", []),
            },
            base_candidate_key: {
                "lifecycle_status": "ARCHIVE_WAIT_UNLESS_NEW_FEATURE_EVIDENCE",
                "exact_original_rule_blocked": True,
                "threshold_only_retune_blocked": True,
                "reason": [
                    "Base candidate was weak/mixed.",
                    "Strict top diagnostic variant failed full validation.",
                    "Do not continue hand-optimizing this family without new evidence."
                ],
            }
        },
        "family_updates": {
            family_key: {
                "research_status": "COOLDOWN_REQUIRES_NEW_FEATURE_EVIDENCE",
                "blocked_actions": [
                    "threshold_only_retest",
                    "active_paper",
                    "live",
                    "capital_change",
                    "promotion"
                ],
                "allowed_actions": [
                    "record_learning",
                    "select_next_candidate",
                    "return only if new feature hypothesis exists"
                ]
            }
        }
    }

    selector_blocklist = {
        "blocklist_version": "edge_factory_learning_selector_blocklist_v1",
        "generated_at": now_iso(),
        "exact_candidate_blocks": [
            {
                "candidate_key": candidate_key,
                "reason": "strict_validation_failed",
                "until": "new_feature_evidence",
            },
            {
                "candidate_key": base_candidate_key,
                "reason": "base weak and strict redesign failed",
                "until": "new_feature_evidence",
            }
        ],
        "family_cooldowns": [
            {
                "family_key": family_key,
                "reason": "strict validation failed after diagnostic overfit catch",
                "until": "new non-threshold feature hypothesis",
            }
        ],
        "general_rules": [
            {
                "rule_key": "diagnostic_top_combo_requires_strict_validation",
                "policy": "A candidate found by threshold/hold search cannot be full-run, promoted, or papered unless strict validation passes."
            },
            {
                "rule_key": "oos_positive_not_enough",
                "policy": "OOS positive alone is insufficient if full/in-sample/month stability fails."
            },
            {
                "rule_key": "threshold_only_retune_limit",
                "policy": "After strict validation fail, do not continue threshold-only tuning on same candidate family."
            }
        ]
    }

    research_directive = {
        "directive_version": "edge_factory_next_research_directive_v1",
        "generated_at": now_iso(),
        "current_decision": {
            "candidate_key": candidate_key,
            "action": "ARCHIVE_WAIT_REDESIGN_REQUIRED",
            "do_not_continue_manual_optimization": True
        },
        "next_os_focus": [
            "Update learning-aware selector to read strict validation blocklist.",
            "Select next orthogonal candidate from Idea Bank or seed new candidates.",
            "Prefer candidates with different failure mode from panic rebound and post impulse threshold-only drift.",
            "Improve OS meta-controller so failures automatically feed selector, lifecycle, and research queue."
        ],
        "next_candidate_preference": [
            "extreme_blowoff_reversion_short_v1 only if duplicate/stale shadow safeguards exist",
            "new candidate ideas with different features",
            "avoid market_relative_continuation_short_v1 if it overlaps active market_relative_short",
            "avoid relative_weakness_snapback_long_v1 without stabilization because learned policy blocks it"
        ],
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False
    }

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "finalizer_status": finalizer_status,
        "candidate_key": candidate_key,
        "base_candidate_key": base_candidate_key,
        "family_key": family_key,
        "validation_status": validation_status,
        "lifecycle_status": lifecycle_status,
        "next_action": next_action,
        "blockers": blockers,
        "classification": classification,
        "memory_count": len(memory_rows),
        "master_memory": str(MASTER_MEMORY),
        "archive_policy_path": "",
        "selector_blocklist_path": "",
        "research_directive_path": "",
        "full_run_allowed": False,
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Finalizer only writes learning/policy artifacts.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital.",
            "Does not create active paper family."
        ],
    }

    archive_policy_path = out_dir / "candidate_archive_policy_v1.json"
    selector_blocklist_path = out_dir / "learning_selector_blocklist_v1.json"
    research_directive_path = out_dir / "next_research_directive_v1.json"
    state_path = out_dir / "strict_validation_learning_finalizer_v1_state.json"
    memory_csv = out_dir / "research_learning_memory_snapshot_after_strict_validation.csv"
    report_path = out_dir / "strict_validation_learning_finalizer_v1_report.md"

    archive_policy_path.write_text(json.dumps(archive_policy, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    selector_blocklist_path.write_text(json.dumps(selector_blocklist, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    research_directive_path.write_text(json.dumps(research_directive, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    state["archive_policy_path"] = str(archive_policy_path)
    state["selector_blocklist_path"] = str(selector_blocklist_path)
    state["research_directive_path"] = str(research_directive_path)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    flat = []
    for r in memory_rows:
        obs = r.get("observed", {}) if isinstance(r.get("observed"), dict) else {}
        flat.append({
            "created_at": r.get("created_at"),
            "source": r.get("source"),
            "candidate_key": r.get("candidate_key"),
            "base_candidate_key": r.get("base_candidate_key"),
            "family_key": r.get("family_key"),
            "decision": r.get("decision"),
            "validation_status": r.get("validation_status"),
            "lifecycle_status": r.get("lifecycle_status"),
            "failure_tags": ",".join(r.get("failure_tags", [])),
            "full_pf": obs.get("full_pf"),
            "full_mean_net_bps": obs.get("full_mean_net_bps"),
            "full_median_net_bps": obs.get("full_median_net_bps"),
            "positive_month_rate": obs.get("positive_month_rate"),
        })

    pd.DataFrame(flat).to_csv(memory_csv, index=False)

    md = []
    md.append("# Edge Factory Strict Validation Learning Finalizer v1")
    md.append("")
    md.append(f"Finalizer status: `{finalizer_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Base candidate: `{base_candidate_key}`")
    md.append(f"Family: `{family_key}`")
    md.append(f"Validation status: `{validation_status}`")
    md.append(f"Lifecycle status: `{lifecycle_status}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Lessons")
    for x in classification["lessons"]:
        md.append(f"- {x}")
    md.append("")
    md.append("## Hard blocks")
    for x in classification["hard_blocks"]:
        md.append(f"- `{x}`")
    md.append("")
    md.append("## Safety")
    md.append("- full_run_allowed: `False`")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY STRICT VALIDATION LEARNING FINALIZER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"finalizer_status: {finalizer_status}")
    print(f"candidate : {candidate_key}")
    print(f"base      : {base_candidate_key}")
    print(f"family    : {family_key}")
    print(f"validation_status: {validation_status}")
    print(f"lifecycle_status : {lifecycle_status}")
    print(f"memory_count: {len(memory_rows)}")
    print(f"next_action: {next_action}")
    print("full_run_allowed: False")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("FAILURE TAGS")
    print("-" * 100)
    for x in classification["failure_tags"]:
        print("-", x)
    print()
    print("LESSONS")
    print("-" * 100)
    for x in classification["lessons"]:
        print("-", x)
    print()
    print("HARD BLOCKS")
    print("-" * 100)
    for x in classification["hard_blocks"]:
        print("-", x)
    print()
    print(f"State    : {state_path}")
    print(f"Archive  : {archive_policy_path}")
    print(f"Blocklist: {selector_blocklist_path}")
    print(f"Directive: {research_directive_path}")
    print(f"Memory   : {MASTER_MEMORY}")
    print(f"CSV      : {memory_csv}")
    print(f"Report   : {report_path}")

if __name__ == "__main__":
    main()
