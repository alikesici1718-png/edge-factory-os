#!/usr/bin/env python
"""Validate anti-overfit alpha search protocol outputs."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "edge_factory_anti_overfit_alpha_search"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
FIXED_GRID_JSON = OUTPUTS_DIR / f"{PREFIX}_fixed_grid.json"
FOLD_PLAN_CSV = OUTPUTS_DIR / f"{PREFIX}_fold_plan.csv"
TRIAL_LOG_CSV = OUTPUTS_DIR / f"{PREFIX}_trial_log.csv"
RANKED_CANDIDATES_CSV = OUTPUTS_DIR / f"{PREFIX}_ranked_candidates.csv"
REJECTED_CANDIDATES_CSV = OUTPUTS_DIR / f"{PREFIX}_rejected_candidates.csv"
PROMOTED_CANDIDATES_CSV = OUTPUTS_DIR / f"{PREFIX}_promoted_candidates.csv"
WALK_FORWARD_RESULTS_CSV = OUTPUTS_DIR / f"{PREFIX}_walk_forward_results.csv"
MULTIPLE_TESTING_JSON = OUTPUTS_DIR / f"{PREFIX}_multiple_testing_report.json"
VALIDATOR_JSON = OUTPUTS_DIR / f"{PREFIX}_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / f"{PREFIX}_validator_report.md"

PROTOCOL_PATH = REPO_ROOT / "src" / "edge_factory_anti_overfit_alpha_search_protocol_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_anti_overfit_alpha_search_protocol_validator_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_anti_overfit_alpha_search_protocol_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_anti_overfit_alpha_search_protocol_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_anti_overfit_alpha_search_protocol_v1.md"

EXPECTED_CATEGORIES = [
    "BUY_PRESSURE_ABSORBED",
    "SELL_PRESSURE_ABSORBED",
    "FLOW_AND_DEPTH_ALIGNED_UP",
    "FLOW_AND_DEPTH_ALIGNED_DOWN",
]
EXPECTED_HORIZONS = [30, 60, 120, 300, 600]
EXPECTED_COOLDOWNS = [300, 600, 900, 1200]
EXPECTED_DELAYS = [0, 1, 3, 5, 10]
EXPECTED_COSTS = [0.0, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0]
EXPECTED_SUBSETS = [
    "ALL",
    "EXCLUDE_THIN",
    "HIGH_ONLY",
    "HIGH_MEDIUM",
    "TOP_10_BY_DISCOVERY_NOTIONAL",
    "TOP_20_BY_DISCOVERY_NOTIONAL",
    "TOP_40_BY_DISCOVERY_NOTIONAL",
    "MIN_AROUND_EVENT_NOTIONAL_5000",
    "MIN_AROUND_EVENT_NOTIONAL_10000",
    "MIN_AROUND_EVENT_NOTIONAL_25000",
    "MIN_AROUND_EVENT_NOTIONAL_50000",
    "MIN_AROUND_EVENT_NOTIONAL_100000",
]
EXPECTED_FOLD_COUNT = 11
EXPECTED_BASE_GRID_COUNT = 960
EXPECTED_FULL_GRID_COUNT = 33_600
MAX_COMPACT_OUTPUT_BYTES = 25_000_000

COMPACT_OUTPUTS = [
    SUMMARY_JSON,
    SUMMARY_MD,
    FIXED_GRID_JSON,
    FOLD_PLAN_CSV,
    TRIAL_LOG_CSV,
    RANKED_CANDIDATES_CSV,
    REJECTED_CANDIDATES_CSV,
    PROMOTED_CANDIDATES_CSV,
    WALK_FORWARD_RESULTS_CSV,
    MULTIPLE_TESTING_JSON,
]

CODE_AND_REPORT_FILES = [
    PROTOCOL_PATH,
    VALIDATOR_PATH,
    RUNNER_PATH,
    VALIDATOR_RUNNER_PATH,
    DOCS_PATH,
    SUMMARY_MD,
    VALIDATOR_MD,
]

FORBIDDEN_PATTERNS = [
    r"\bccxt\b",
    r"\bcreate_order\b",
    r"\bmarket_order\b",
    r"\blimit_order\b",
    r"\bfutures_create_order\b",
    r"\bprivate\s+endpoint\b",
    r"\bapi[_-]?key\b",
    r"\bsecret\b",
    r"\bleverage\b",
    r"\bposition\s+sizing\b",
    r"\bstop[_-]?loss\b",
    r"\btake[_-]?profit\b",
    r"\bpnl\s+curve\b",
    r"\blive\s+trading\b",
    r"\bpaper\s+trading\b",
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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def context_window(lines: list[str], line_number: int, radius: int = 2) -> str:
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)
    return "\n".join(lines[current - 1].rstrip()[:300] for current in range(start, end + 1)).lower()


def scan_forbidden_terms() -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    real_blockers: list[dict[str, Any]] = []
    safety_markers = [
        "no ",
        "not ",
        "false",
        "forbidden",
        "prohibited",
        "diagnostic",
        "research",
        "safety",
        "without",
        "never",
        "trading_or_order_logic",
        "private_endpoint_logic",
    ]
    for path in CODE_AND_REPORT_FILES:
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, line in enumerate(lines, start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if not re.search(pattern, line, flags=re.IGNORECASE):
                    continue
                context = context_window(lines, line_number)
                is_safety = any(marker in context for marker in safety_markers) or "FORBIDDEN_PATTERNS" in context
                item = {
                    "path": str(path.relative_to(REPO_ROOT)),
                    "line": line_number,
                    "pattern": pattern,
                    "classification": "SAFETY_CONTEXT" if is_safety else "REAL_BLOCKER",
                    "text": line.strip()[:240],
                }
                matches.append(item)
                if not is_safety:
                    real_blockers.append(item)
    return {"matches": matches, "real_blockers": real_blockers}


def raw_data_inside_repo() -> list[str]:
    matches: list[str] = []
    for pattern in ["*-bookDepth-*.csv", "*-aggTrades-*.csv", "*-bookDepth-*.zip", "*-aggTrades-*.zip"]:
        for path in REPO_ROOT.rglob(pattern):
            if ".git" in path.parts:
                continue
            matches.append(str(path.relative_to(REPO_ROOT)))
            if len(matches) >= 100:
                return matches
    return matches


def row_level_outputs() -> list[str]:
    allowed = {path.resolve() for path in COMPACT_OUTPUTS + [VALIDATOR_JSON, VALIDATOR_MD]}
    matches: list[str] = []
    for path in OUTPUTS_DIR.glob(f"{PREFIX}*"):
        if path.resolve() in allowed:
            continue
        if path.suffix.lower() in {".parquet", ".jsonl", ".sqlite", ".duckdb", ".db"}:
            matches.append(str(path.relative_to(REPO_ROOT)))
    return matches


def validate() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON)
    grid = load_json(FIXED_GRID_JSON)
    multiple = load_json(MULTIPLE_TESTING_JSON)
    fold_rows = read_csv_rows(FOLD_PLAN_CSV)
    trial_rows = read_csv_rows(TRIAL_LOG_CSV)
    rejected_rows = read_csv_rows(REJECTED_CANDIDATES_CSV)
    promoted_rows = read_csv_rows(PROMOTED_CANDIDATES_CSV)
    walk_rows = read_csv_rows(WALK_FORWARD_RESULTS_CSV)
    scan = scan_forbidden_terms()
    raw_inside = raw_data_inside_repo()
    row_level = row_level_outputs()
    compact_sizes = {path.name: path.stat().st_size for path in COMPACT_OUTPUTS if path.exists()}

    full_search_run = bool(summary.get("full_search_run"))
    fixed_grid_ok = (
        grid.get("categories") == EXPECTED_CATEGORIES
        and grid.get("horizons_seconds") == EXPECTED_HORIZONS
        and grid.get("cooldowns_seconds") == EXPECTED_COOLDOWNS
        and grid.get("delays_seconds") == EXPECTED_DELAYS
        and grid.get("costs_bps") == EXPECTED_COSTS
        and grid.get("capacity_subsets") == EXPECTED_SUBSETS
        and int_value(grid.get("base_candidate_count")) == EXPECTED_BASE_GRID_COUNT
        and int_value(grid.get("full_stress_grid_count")) == EXPECTED_FULL_GRID_COUNT
    )
    fold_plan_ok = len(fold_rows) == EXPECTED_FOLD_COUNT
    test_not_used_in_discovery = not bool(summary.get("test_used_in_discovery"))
    direction_locked = bool(summary.get("direction_locked"))
    promotion_limits_enforced = bool(summary.get("promotion_limits_enforced"))
    env_gate_respected = bool(summary.get("env_gate_respected", True)) if not full_search_run else True
    rejected_logged = bool(summary.get("rejected_candidates_logged")) or not full_search_run
    no_downloads = summary.get("downloads_run") is False
    no_row_dataset = summary.get("row_level_dataset_created") is False and not row_level
    raw_outside = bool(summary.get("raw_roots_outside_repo")) and not raw_inside
    compact_outputs = all(size <= MAX_COMPACT_OUTPUT_BYTES for size in compact_sizes.values())
    no_trading_logic = (
        summary.get("trading_or_order_logic") is False
        and summary.get("private_endpoint_logic") is False
        and not scan["real_blockers"]
    )
    multiple_testing_ok = (
        multiple.get("fixed_grid_sha256") == grid.get("fixed_grid_sha256")
        and int_value(multiple.get("base_candidate_count")) == EXPECTED_BASE_GRID_COUNT
        and int_value(multiple.get("full_stress_grid_count")) == EXPECTED_FULL_GRID_COUNT
    )

    promotion_limit_violations: list[dict[str, Any]] = []
    if full_search_run:
        by_fold_stage: dict[tuple[str, str], int] = {}
        for row in promoted_rows:
            key = (str(row.get("fold_id", "")), str(row.get("promotion_stage", "")))
            by_fold_stage[key] = by_fold_stage.get(key, 0) + 1
        for (fold_id, stage), count in by_fold_stage.items():
            limit = 20 if stage == "PROMOTED_TO_VALIDATION" else 5 if stage == "PROMOTED_TO_TEST" else 999
            if count > limit:
                promotion_limit_violations.append({"fold_id": fold_id, "stage": stage, "count": count, "limit": limit})
    promotion_limits_ok = promotion_limits_enforced and not promotion_limit_violations

    checks = {
        "required_outputs_exist": all(path.exists() for path in COMPACT_OUTPUTS),
        "fixed_grid_unchanged": fixed_grid_ok,
        "fold_plan_count": fold_plan_ok,
        "test_not_used_in_discovery": test_not_used_in_discovery,
        "direction_locked": direction_locked,
        "promotion_limits_enforced": promotion_limits_ok,
        "env_gate_respected": env_gate_respected,
        "rejected_candidates_logged": rejected_logged,
        "no_downloads": no_downloads,
        "no_row_level_dataset": no_row_dataset,
        "raw_data_outside_repo": raw_outside,
        "outputs_compact": compact_outputs,
        "no_trading_order_private_api_logic": no_trading_logic,
        "multiple_testing_report_consistent": multiple_testing_ok,
    }
    status = "PASS_ANTI_OVERFIT_ALPHA_SEARCH_PROTOCOL_VALIDATOR" if all(checks.values()) else "FAIL_ANTI_OVERFIT_ALPHA_SEARCH_PROTOCOL_VALIDATOR"
    return {
        "status": status,
        "created_at_utc": utc_now_text(),
        "summary_status": summary.get("status", ""),
        "summary_classification": summary.get("final_classification", ""),
        "full_search_run": full_search_run,
        "fixed_grid_full_stress_grid_count": grid.get("full_stress_grid_count", 0),
        "fold_count": len(fold_rows),
        "trial_log_rows": len(trial_rows),
        "rejected_candidate_rows": len(rejected_rows),
        "promoted_candidate_rows": len(promoted_rows),
        "walk_forward_rows": len(walk_rows),
        "checks": checks,
        "promotion_limit_violations": promotion_limit_violations,
        "forbidden_scan": scan,
        "raw_data_inside_repo_matches": raw_inside,
        "row_level_output_matches": row_level,
        "compact_output_sizes_bytes": compact_sizes,
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Anti-overfit alpha search protocol validator v1",
        "",
        f"status: {report['status']}",
        f"summary_status: {report.get('summary_status', '')}",
        f"summary_classification: {report.get('summary_classification', '')}",
        f"full_search_run: {str(report['full_search_run']).lower()}",
        f"fixed_grid_full_stress_grid_count: {report['fixed_grid_full_stress_grid_count']}",
        f"fold_count: {report['fold_count']}",
        "",
        "## Checks",
    ]
    for name, passed in report["checks"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    if report["promotion_limit_violations"]:
        lines.append("")
        lines.append("## Promotion Limit Violations")
        for item in report["promotion_limit_violations"]:
            lines.append(f"- fold={item['fold_id']} stage={item['stage']} count={item['count']} limit={item['limit']}")
    lines.append("")
    lines.append("Diagnostics only. Validator found no real trading, order, private endpoint, or row-level dataset output when all checks pass.")
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        report = validate()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "FAIL_ANTI_OVERFIT_ALPHA_SEARCH_PROTOCOL_VALIDATOR",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "checks": {},
        }
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report_md(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
