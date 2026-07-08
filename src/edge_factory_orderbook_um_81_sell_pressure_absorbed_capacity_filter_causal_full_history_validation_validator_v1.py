#!/usr/bin/env python
"""Validate the capacity-filter causal audit output."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_sell_pressure_absorbed_capacity_filter_causal_full_history"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
CAUSAL_AUDIT_JSON = OUTPUTS_DIR / f"{PREFIX}_causal_audit.json"
VALIDATOR_JSON = OUTPUTS_DIR / f"{PREFIX}_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / f"{PREFIX}_validator_report.md"

SCANNER_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_filter_causal_full_history_validation_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_filter_causal_full_history_validation_validator_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_filter_causal_full_history_validation_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_filter_causal_full_history_validation_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_filter_causal_full_history_validation_v1.md"

COMPACT_OUTPUTS = [SUMMARY_JSON, SUMMARY_MD, CAUSAL_AUDIT_JSON]
CODE_AND_REPORT_FILES = [SCANNER_PATH, VALIDATOR_PATH, RUNNER_PATH, VALIDATOR_RUNNER_PATH, DOCS_PATH, SUMMARY_MD, VALIDATOR_MD]

EXPECTED_STATUS = "LOOKAHEAD_BLOCKED_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_FILTER_CAUSAL_FULL_HISTORY_VALIDATION"
EXPECTED_CANDIDATE = "SELL_PRESSURE_ABSORBED@300s"
EXPECTED_SUBSET = "MIN_AROUND_EVENT_NOTIONAL_100000"

FORBIDDEN_PATTERNS = [
    r"\bstrategy\b",
    r"\bbacktest\b",
    r"\bsignal\b",
    r"\bpnl\b",
    r"\borders?\b",
    r"\bprivate endpoints?\b",
    r"\brecommendations?\b",
]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"not a JSON object: {path}")
    return payload


def classify_match(context_text: str) -> str:
    lowered = context_text.lower()
    safety_markers = [
        "no ",
        "not ",
        "without",
        "false",
        "blocked",
        "safety",
        "audit",
        "forbidden_patterns",
        "recommendations_created",
        "orders_created",
        "private_endpoints_used",
    ]
    return "SAFETY_CONTEXT" if any(marker in lowered for marker in safety_markers) else "REAL_BLOCKER"


def scan_forbidden_terms() -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    real_blockers: list[dict[str, Any]] = []
    for path in CODE_AND_REPORT_FILES:
        if not path.exists() or path.is_dir():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, line in enumerate(lines, start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if not re.search(pattern, line, flags=re.IGNORECASE):
                    continue
                context_text = "\n".join(lines[max(0, line_number - 3) : min(len(lines), line_number + 2)])
                classification = "SAFETY_CONTEXT" if "FORBIDDEN_PATTERNS" in line or line.strip().startswith("r\"") else classify_match(context_text)
                item = {
                    "path": str(path.relative_to(REPO_ROOT)),
                    "line": line_number,
                    "term": pattern,
                    "text": line.strip()[:240],
                    "classification": classification,
                }
                matches.append(item)
                if classification == "REAL_BLOCKER":
                    real_blockers.append(item)
    return {"matches": matches, "real_blockers": real_blockers}


def row_level_or_parquet_outputs() -> list[str]:
    allowed = {path.resolve() for path in COMPACT_OUTPUTS + [VALIDATOR_JSON, VALIDATOR_MD]}
    matches: list[str] = []
    for path in OUTPUTS_DIR.glob(f"{PREFIX}*"):
        if path.resolve() in allowed:
            continue
        if path.suffix.lower() in {".parquet", ".jsonl", ".db", ".sqlite", ".duckdb"}:
            matches.append(str(path.relative_to(REPO_ROOT)))
    return matches


def validate() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON)
    audit = load_json(CAUSAL_AUDIT_JSON)
    scan = scan_forbidden_terms()
    row_level_outputs = row_level_or_parquet_outputs()
    checks = {
        "summary_exists": SUMMARY_JSON.exists(),
        "audit_exists": CAUSAL_AUDIT_JSON.exists(),
        "summary_status_lookahead_blocked": summary.get("status") == EXPECTED_STATUS,
        "audit_status_matches_summary": audit.get("status") == summary.get("status"),
        "candidate_locked": summary.get("candidate") == EXPECTED_CANDIDATE,
        "capacity_subset_locked": summary.get("locked_capacity_subset") == EXPECTED_SUBSET,
        "capacity_filter_not_causal": summary.get("capacity_filter_causal") is False,
        "lookahead_blocked_true": summary.get("lookahead_blocked") is True,
        "future_bound_matches_present": bool(summary.get("future_bound_matches")),
        "capacity_filter_usage_matches_present": bool(summary.get("capacity_filter_usage_matches")),
        "full_history_validation_not_run": summary.get("full_history_validation_run") is False,
        "summary_confirms_no_downloads": summary.get("downloads_run") is False,
        "summary_confirms_no_raw_modification": summary.get("raw_data_modified") is False,
        "summary_confirms_no_parquet_dataset": summary.get("full_parquet_dataset_created") is False,
        "summary_confirms_no_row_level_dataset": summary.get("row_level_dataset_created") is False,
        "summary_confirms_no_orders": summary.get("orders_created") is False,
        "summary_confirms_no_private_endpoints": summary.get("private_endpoints_used") is False,
        "all_compact_outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in COMPACT_OUTPUTS),
        "no_row_level_or_parquet_outputs": not row_level_outputs,
        "no_real_prohibited_behavior": not scan["real_blockers"],
    }
    replacement_checks_all_true = all(checks.values())
    status = (
        "PASS_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_FILTER_CAUSAL_FULL_HISTORY_VALIDATOR"
        if replacement_checks_all_true
        else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_FILTER_CAUSAL_FULL_HISTORY_VALIDATION"
    )
    report = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "source_summary_status": summary.get("status", ""),
        "capacity_filter_causal": summary.get("capacity_filter_causal"),
        "lookahead_blocked": summary.get("lookahead_blocked"),
        "full_history_validation_run": summary.get("full_history_validation_run"),
        "lookahead_reason": summary.get("lookahead_reason", ""),
        "future_bound_matches": summary.get("future_bound_matches", []),
        "capacity_filter_usage_matches": summary.get("capacity_filter_usage_matches", []),
        "row_level_or_parquet_outputs": row_level_outputs,
        "prohibited_term_matches": scan["matches"],
        "real_prohibited_behavior_matches": scan["real_blockers"],
        "checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_validator_md(report)
    return report


def write_validator_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sell pressure absorbed capacity filter causal validator v1",
        "",
        f"status: {report['status']}",
        f"source_summary_status: {report.get('source_summary_status', '')}",
        f"capacity_filter_causal: {str(report.get('capacity_filter_causal')).lower()}",
        f"lookahead_blocked: {str(report.get('lookahead_blocked')).lower()}",
        f"full_history_validation_run: {str(report.get('full_history_validation_run')).lower()}",
        f"replacement_checks_all_true: {str(report.get('replacement_checks_all_true', False)).lower()}",
        "",
        "## Checks",
    ]
    for key, value in report.get("checks", {}).items():
        lines.append(f"- {key}: {str(value).lower()}")
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = validate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
