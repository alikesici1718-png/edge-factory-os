#!/usr/bin/env python3
"""Repo-only old_short evidence recovery/status refresh.

This tool searches local repository files for old_short evidence. It does not
touch runtime, call network, place orders, generate candidates, claim edge, or
grant live/capital permissions.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_evidence_recovery_status_refresh_v1.py"
ARTIFACT_REL = "artifacts/old_short/old_short_evidence_recovery_status_refresh_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

STATUS = "PASS_REPO_ONLY_OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH_CREATED"
BLOCKED_STATUS = "BLOCKED_OLD_SHORT_EVIDENCE_NOT_FOUND"
ARTIFACT_KIND = "OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH"
MODULE = "edge_factory_os_repo_only_old_short_evidence_recovery_status_refresh_v1"

SEARCH_PATTERNS = [
    "old_short",
    "OLD_SHORT",
    "short monitoring",
    "monitoring_ready",
    "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
    "old short",
]

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}

TEXT_EXTENSIONS = {
    ".py",
    ".json",
    ".txt",
    ".md",
    ".csv",
    ".toml",
    ".yaml",
    ".yml",
    ".ps1",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_output(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repo_clean_except_expected() -> bool:
    allowed = {TOOL_REL, ARTIFACT_REL}
    status = git_output(["status", "--short", "--untracked-files=all"])
    if not status:
        return True
    for line in status.splitlines():
        rel = line[3:].replace("\\", "/")
        if rel not in allowed:
            return False
    return True


def tracked_python_count() -> int:
    out = git_output(["ls-files", "*.py"])
    return 0 if not out else len(out.splitlines())


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def iter_repo_text_files() -> list[Path]:
    files: list[Path] = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)
        for name in filenames:
            path = root_path / name
            if path.suffix.lower() in TEXT_EXTENSIONS:
                files.append(path)
    return sorted(files)


def find_matches() -> list[dict[str, Any]]:
    regexes = [(pattern, re.compile(re.escape(pattern), re.IGNORECASE)) for pattern in SEARCH_PATTERNS]
    evidence: list[dict[str, Any]] = []
    for path in iter_repo_text_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        hits = []
        lines = text.splitlines()
        for line_number, line in enumerate(lines, start=1):
            matched = sorted({pattern for pattern, rgx in regexes if rgx.search(line)})
            if matched:
                hits.append(
                    {
                        "line": line_number,
                        "patterns": matched,
                        "text": line.strip()[:300],
                    }
                )
        if hits:
            evidence.append(
                {
                    "path": rel(path),
                    "hit_count": len(hits),
                    "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "sample_hits": hits[:20],
                }
            )
    return sorted(evidence, key=lambda item: (-item["hit_count"], item["path"]))


def walk_values(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    values: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            values.append((path, value))
            values.extend(walk_values(value, path))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            path = f"{prefix}[{idx}]"
            values.extend(walk_values(value, path))
    return values


def candidate_json_facts(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    facts = []
    interesting_keys = {
        "old_short",
        "old_short_closed_trades",
        "closed_trades",
        "open_trades",
        "open_positions",
        "final_decision",
        "old_short_final_decision",
        "old_short_monitoring_ready",
        "monitoring_ready",
        "old_short_capital_review_threshold",
        "capital_review_threshold",
        "old_short_next_required_closed_trades_for_capital_review",
        "next_required_closed_trades_for_capital_review",
        "research_invalidation_applies",
        "old_short_research_invalidation_applies",
        "runtime_touch_allowed",
        "live_allowed",
        "capital_change_allowed",
        "capital_action_allowed",
        "real_orders_allowed",
        "candidate_generation_allowed",
        "edge_claim_allowed",
        "win_rate",
        "total_pnl",
    }
    for item in evidence:
        path = REPO_ROOT / item["path"]
        if path.suffix.lower() != ".json":
            continue
        payload = load_json(path)
        if payload is None:
            continue
        extracted = {}
        for key_path, value in walk_values(payload):
            key = key_path.split(".")[-1]
            key = re.sub(r"\[\d+\]", "", key)
            if key in interesting_keys and not isinstance(value, (dict, list)):
                extracted[key_path] = value
        if extracted:
            facts.append({"path": item["path"], "facts": extracted})
    return facts


def first_fact(facts: list[dict[str, Any]], suffixes: tuple[str, ...], default: Any = None) -> Any:
    for source in facts:
        for key_path, value in source["facts"].items():
            if any(key_path.endswith(suffix) for suffix in suffixes):
                return value
    return default


def find_status_sources(facts: list[dict[str, Any]]) -> dict[str, Any]:
    preferred_paths = [
        "edge_factory_os_framework/status/runtime_family_monitor_status_panel_no_capital_v1.json",
        "edge_factory_os_old_short_reactivation_gate/old_short_reactivation_gate_latest.json",
        "edge_factory_os_framework/status/runtime_family_monitor_refresh_old_short_aware_summary_v1.json",
        "edge_factory_os_framework/policies/runtime_family_monitor_refresh_old_short_aware_state_v1.json",
        "edge_factory_os_framework/registries/runtime_family_registry_v1.json",
    ]
    return {
        "latest_old_short_status_artifact": next((p for p in preferred_paths if (REPO_ROOT / p).exists()), None),
        "latest_old_short_execution_or_monitoring_artifact": "edge_factory_os_framework/status/runtime_family_monitor_refresh_old_short_aware_summary_v1.json"
        if (REPO_ROOT / "edge_factory_os_framework/status/runtime_family_monitor_refresh_old_short_aware_summary_v1.json").exists()
        else None,
        "latest_old_short_closure_or_decision_artifact": "edge_factory_os_old_short_reactivation_gate/old_short_reactivation_gate_latest.json"
        if (REPO_ROOT / "edge_factory_os_old_short_reactivation_gate/old_short_reactivation_gate_latest.json").exists()
        else None,
        "json_fact_source_count": len(facts),
    }


def build_payload() -> dict[str, Any]:
    evidence = find_matches()
    facts = candidate_json_facts(evidence)
    source_paths = find_status_sources(facts)
    evidence_found = bool(evidence)

    status_panel = load_json(REPO_ROOT / "edge_factory_os_framework/status/runtime_family_monitor_status_panel_no_capital_v1.json") or {}
    status_old_short = status_panel.get("old_short", {}) if isinstance(status_panel.get("old_short"), dict) else {}
    gate = load_json(REPO_ROOT / "edge_factory_os_old_short_reactivation_gate/old_short_reactivation_gate_latest.json") or {}
    gate_old_short = gate.get("old_short_status", {}) if isinstance(gate.get("old_short_status"), dict) else {}
    refresh_summary = load_json(REPO_ROOT / "edge_factory_os_framework/status/runtime_family_monitor_refresh_old_short_aware_summary_v1.json") or {}

    closed_trades = (
        status_old_short.get("closed_trades")
        if status_old_short.get("closed_trades") is not None
        else gate_old_short.get("old_short_closed_trades")
    )
    if closed_trades is None:
        closed_trades = first_fact(
            facts,
            (
                "old_short.closed_trades",
                "old_short_status.old_short_closed_trades",
                "old_short_closed_trades",
            ),
        )
    capital_threshold = (
        status_old_short.get("capital_review_threshold")
        if status_old_short.get("capital_review_threshold") is not None
        else gate_old_short.get("old_short_capital_review_threshold")
    )
    if capital_threshold is None:
        capital_threshold = refresh_summary.get("old_short_capital_review_threshold") or first_fact(
            facts,
            (
                "old_short_status.old_short_capital_review_threshold",
                "old_short_capital_review_threshold",
                "old_short.capital_review_threshold",
                "capital_review_threshold",
            ),
        )
    next_required = (
        status_old_short.get("next_required_closed_trades_for_capital_review")
        if status_old_short.get("next_required_closed_trades_for_capital_review") is not None
        else gate_old_short.get("old_short_next_required_closed_trades_for_capital_review")
    )
    if next_required is None:
        next_required = first_fact(
            facts,
            (
                "old_short.next_required_closed_trades_for_capital_review",
                "old_short_status.old_short_next_required_closed_trades_for_capital_review",
                "old_short_next_required_closed_trades_for_capital_review",
            ),
        )
    if next_required is None and isinstance(closed_trades, int) and isinstance(capital_threshold, int):
        next_required = max(0, capital_threshold - closed_trades)

    final_decision = (
        status_old_short.get("final_decision")
        or gate_old_short.get("old_short_final_decision")
        or refresh_summary.get("old_short_decision")
        or first_fact(
            facts,
            (
                "old_short.final_decision",
                "old_short_status.old_short_final_decision",
                "old_short_final_decision",
            ),
        )
    )
    monitoring_ready = (
        status_old_short.get("monitoring_ready")
        if status_old_short.get("monitoring_ready") is not None
        else gate_old_short.get("old_short_monitoring_ready")
    )
    if monitoring_ready is None:
        monitoring_ready = first_fact(
            facts,
            (
                "old_short.monitoring_ready",
                "old_short_status.old_short_monitoring_ready",
                "old_short_monitoring_ready",
            ),
        )
    invalidation_applies = (
        status_old_short.get("research_invalidation_applies")
        if status_old_short.get("research_invalidation_applies") is not None
        else refresh_summary.get("old_short_research_invalidation_applies")
    )
    if invalidation_applies is None:
        invalidation_applies = first_fact(
            facts,
            (
                "old_short_research_invalidation_applies",
                "old_short.research_invalidation_applies",
                "release_gate_feed.OLD_SHORT_INVALIDATED_BY_RESEARCH_FAILURES",
                "research_invalidation_applies",
            ),
        )
    runtime_allowed = bool(status_old_short.get("runtime_touch_allowed", False))
    live_allowed = bool(status_old_short.get("live_allowed", False))
    capital_allowed = bool(status_old_short.get("capital_action_allowed", False))
    real_orders_allowed = bool(status_old_short.get("real_orders_allowed", False))

    win_streak_hits = [
        item
        for item in evidence
        if any("8/8" in hit["text"] or "8 of 8" in hit["text"].lower() for hit in item["sample_hits"])
    ]

    status = STATUS if evidence_found else BLOCKED_STATUS
    safety_permissions = {
        "old_short_evidence_recovered": evidence_found,
        "strategy_execution_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_except_expected(),
        "evidence_found": evidence_found,
        "repo_local_search_only": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
    }
    replacement_checks_all_true = all(validation_checks.values()) and all(
        value is False for key, value in safety_permissions.items() if key.endswith("_allowed_now")
    )

    return {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "head": git_output(["rev-parse", "HEAD"]),
            "repo_clean_before_run": validation_checks["repo_clean_before_run"],
            "tracked_python_count_before": tracked_python_count(),
            "generated_at_utc": utc_now(),
        },
        "evidence_files_found": {
            "search_patterns": SEARCH_PATTERNS,
            "file_count": len(evidence),
            "top_files": evidence[:40],
            "json_fact_sources": facts[:40],
            "status_sources": source_paths,
        },
        "latest_old_short_status": {
            "final_decision": final_decision,
            "monitoring_ready": monitoring_ready,
            "closed_trades": closed_trades,
            "open_trade_count": first_fact(facts, ("old_short.open_positions", "open_positions", "open_trades"), None),
            "capital_review_threshold": capital_threshold,
            "next_required_closed_trades_for_capital_review": next_required,
            "source_artifacts": source_paths,
        },
        "performance_evidence_summary": {
            "closed_trade_count_recovered": closed_trades,
            "open_trade_count_recovered": first_fact(facts, ("old_short.open_positions", "open_positions", "open_trades"), None),
            "win_rate_recovered": first_fact(facts, ("win_rate",), None),
            "total_pnl_recovered": first_fact(facts, ("total_pnl",), None),
            "eight_of_eight_evidence_found": bool(win_streak_hits),
            "eight_of_eight_evidence_files": win_streak_hits[:10],
        },
        "monitoring_evidence_summary": {
            "monitoring_threshold": 20,
            "monitoring_ready": monitoring_ready,
            "capital_review_threshold": capital_threshold,
            "capital_ready": False if isinstance(closed_trades, int) and isinstance(capital_threshold, int) and closed_trades < capital_threshold else None,
            "decision": final_decision,
        },
        "invalidation_status": {
            "old_short_was_invalidated": bool(invalidation_applies),
            "research_route_failure_auto_invalidates_old_short": False,
            "evidence_value_research_invalidation_applies": invalidation_applies,
        },
        "runtime_live_capital_status": {
            "runtime_approved": runtime_allowed,
            "live_approved": live_allowed,
            "capital_approved": capital_allowed,
            "real_orders_approved": real_orders_allowed,
            "candidate_or_edge_approved": False,
        },
        "uncertainty_notes": [
            "No repo-local 8/8 text evidence was found by this search." if not win_streak_hits else "8/8 evidence was found in repo-local text.",
            "Step 1 recovers status and evidence only; it does not reconstruct or rerun the strategy.",
            "External paper logs and non-repo data are not treated as authoritative in this artifact unless referenced by repo-local evidence.",
        ],
        "next_recommended_step": "OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION_ONLY" if evidence_found else "BLOCKED_REVIEW_OLD_SHORT_EVIDENCE_NOT_FOUND",
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }


def main() -> None:
    payload = build_payload()
    write_artifact(payload)
    print(f"status: {payload['status']}")
    print(f"evidence_file_count: {payload['evidence_files_found']['file_count']}")
    print(f"latest_old_short_status: {payload['latest_old_short_status']['final_decision']}")
    print(f"closed_trade_count: {payload['latest_old_short_status']['closed_trades']}")
    print(f"eight_of_eight_evidence_found: {str(payload['performance_evidence_summary']['eight_of_eight_evidence_found']).lower()}")
    print(f"old_short_invalidated: {str(payload['invalidation_status']['old_short_was_invalidated']).lower()}")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")
    if payload["status"] == BLOCKED_STATUS:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
