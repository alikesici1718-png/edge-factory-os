#!/usr/bin/env python3
"""Read-only baseline research sanity execution for the OKX 88-symbol 1h panel.

This diagnostic module streams the validated 1h panel only. It does not read
original 1m sources, build/aggregate data, search strategies, optimize,
generate candidates, claim edge, or touch runtime/live/capital.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_after_preview_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_after_preview_v1"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_v1"
READINESS_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_after_pipeline_summary_v1"
)
PIPELINE_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1"
)
VALIDATOR_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1"
)
BUILD_EXECUTION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
)

PREVIEW = PREVIEW_DIR / "repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate.json"
READINESS_GATE = READINESS_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_readiness_gate.json"
PIPELINE_SUMMARY = PIPELINE_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary.json"
VALIDATOR_SUMMARY = VALIDATOR_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json"
OUTPUT_MANIFEST = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
OUTPUT_SCHEMA = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json"
PROVENANCE = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_provenance_manifest.json"

EXPECTED_HEAD = "fe3e0ef"
EXPECTED_ROWS_PER_SYMBOL = 25272
EXPECTED_SYMBOL_COUNT = 88
EXPECTED_OUTPUT_ROWS = 2223936
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_EXECUTED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_EXECUTION_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_after_execution_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_EXECUTED_SUMMARY_READY"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_EXECUTION_BLOCKED_REVIEW_REQUIRED"
EXTREME_RETURN_ABS_THRESHOLD = 0.25


class RunningStats:
    def __init__(self) -> None:
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.min_value: float | None = None
        self.max_value: float | None = None

    def add(self, value: float) -> None:
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        self.m2 += delta * (value - self.mean)
        self.min_value = value if self.min_value is None else min(self.min_value, value)
        self.max_value = value if self.max_value is None else max(self.max_value, value)

    def as_dict(self) -> dict[str, Any]:
        variance = self.m2 / (self.count - 1) if self.count > 1 else 0.0
        return {
            "count": self.count,
            "max": self.max_value,
            "mean": self.mean if self.count else None,
            "min": self.min_value,
            "std": math.sqrt(variance) if self.count else None,
        }


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed = {
        f"?? {TOOL_REL.as_posix()}",
        f" M {TOOL_REL.as_posix()}",
        f"A  {TOOL_REL.as_posix()}",
    }
    unexpected = [line for line in lines if line.replace("\\", "/") not in allowed]
    return not unexpected, unexpected


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def safe_float(value: str) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def month_key(hour_open_time_utc: str) -> str:
    return hour_open_time_utc[:7]


def stream_panel_diagnostics(output_file: Path) -> dict[str, Any]:
    monthly: dict[str, dict[str, Any]] = {}
    incomplete_by_month: dict[str, int] = defaultdict(int)
    incomplete_by_symbol: dict[str, int] = defaultdict(int)
    incomplete_examples: list[dict[str, Any]] = []
    per_symbol: dict[str, dict[str, Any]] = {}
    return_stats_by_symbol: dict[str, RunningStats] = defaultdict(RunningStats)
    global_return_stats = RunningStats()
    volume_stats_by_symbol: dict[str, RunningStats] = defaultdict(RunningStats)
    global_volume_stats = RunningStats()

    row_count = 0
    complete_count = 0
    incomplete_count = 0
    finite_return_count = 0
    nan_inf_return_count = 0
    extreme_return_count = 0
    negative_volume_count = 0
    zero_volume_count = 0
    volume_value_count = 0
    first_hour: str | None = None
    last_hour: str | None = None
    volume_fields: list[str] = []

    with output_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"symbol", "hour_open_time_utc", "close", "complete_1h", "source_row_count"}
        missing_required = sorted(required - set(reader.fieldnames or []))
        if missing_required:
            raise RuntimeError(f"validated panel output missing required fields: {missing_required}")
        volume_fields = [field for field in ["vol", "vol_ccy", "vol_quote", "volume"] if field in (reader.fieldnames or [])]
        primary_volume_field = volume_fields[0] if volume_fields else None

        for row in reader:
            row_count += 1
            symbol = row["symbol"]
            hour = row["hour_open_time_utc"]
            month = month_key(hour)
            complete = parse_bool(row["complete_1h"])
            close = safe_float(row["close"])

            first_hour = hour if first_hour is None else min(first_hour, hour)
            last_hour = hour if last_hour is None else max(last_hour, hour)

            month_entry = monthly.setdefault(month, {"row_count": 0, "complete_1h_row_count": 0, "incomplete_1h_row_count": 0, "symbols": set()})
            month_entry["row_count"] += 1
            month_entry["symbols"].add(symbol)
            if complete:
                complete_count += 1
                month_entry["complete_1h_row_count"] += 1
            else:
                incomplete_count += 1
                month_entry["incomplete_1h_row_count"] += 1
                incomplete_by_month[month] += 1
                incomplete_by_symbol[symbol] += 1
                if len(incomplete_examples) < 20:
                    incomplete_examples.append({"symbol": symbol, "hour_open_time_utc": hour, "source_row_count": row.get("source_row_count")})

            symbol_entry = per_symbol.setdefault(
                symbol,
                {
                    "row_count": 0,
                    "complete_1h_row_count": 0,
                    "incomplete_1h_row_count": 0,
                    "first_hour": hour,
                    "last_hour": hour,
                    "previous_close": None,
                },
            )
            symbol_entry["row_count"] += 1
            symbol_entry["first_hour"] = min(symbol_entry["first_hour"], hour)
            symbol_entry["last_hour"] = max(symbol_entry["last_hour"], hour)
            if complete:
                symbol_entry["complete_1h_row_count"] += 1
            else:
                symbol_entry["incomplete_1h_row_count"] += 1

            previous_close = symbol_entry["previous_close"]
            if previous_close is not None:
                if close is None or previous_close <= 0:
                    nan_inf_return_count += 1
                else:
                    ret = close / previous_close - 1.0
                    if math.isfinite(ret):
                        finite_return_count += 1
                        return_stats_by_symbol[symbol].add(ret)
                        global_return_stats.add(ret)
                        if abs(ret) >= EXTREME_RETURN_ABS_THRESHOLD:
                            extreme_return_count += 1
                    else:
                        nan_inf_return_count += 1
            if close is not None:
                symbol_entry["previous_close"] = close

            if primary_volume_field:
                volume_value = safe_float(row.get(primary_volume_field, ""))
                if volume_value is None:
                    continue
                volume_value_count += 1
                volume_stats_by_symbol[symbol].add(volume_value)
                global_volume_stats.add(volume_value)
                if volume_value < 0:
                    negative_volume_count += 1
                if volume_value == 0:
                    zero_volume_count += 1

    monthly_rows = []
    for month, entry in sorted(monthly.items()):
        monthly_rows.append(
            {
                "month": month,
                "row_count": entry["row_count"],
                "complete_1h_row_count": entry["complete_1h_row_count"],
                "incomplete_1h_row_count": entry["incomplete_1h_row_count"],
                "symbol_count": len(entry["symbols"]),
            }
        )

    per_symbol_rows = []
    per_symbol_output_row_count_valid = True
    for symbol, entry in sorted(per_symbol.items()):
        row_count_for_symbol = entry["row_count"]
        per_symbol_output_row_count_valid = per_symbol_output_row_count_valid and row_count_for_symbol == EXPECTED_ROWS_PER_SYMBOL
        per_symbol_rows.append(
            {
                "symbol": symbol,
                "row_count": row_count_for_symbol,
                "complete_1h_row_count": entry["complete_1h_row_count"],
                "incomplete_1h_row_count": entry["incomplete_1h_row_count"],
                "finite_return_count": return_stats_by_symbol[symbol].count,
                "first_hour": entry["first_hour"],
                "last_hour": entry["last_hour"],
            }
        )

    return {
        "all_hours_complete": incomplete_count == 0,
        "complete_1h_row_count": complete_count,
        "expected_rows_per_symbol": EXPECTED_ROWS_PER_SYMBOL,
        "extreme_return_abs_threshold": EXTREME_RETURN_ABS_THRESHOLD,
        "extreme_return_diagnostic_count": extreme_return_count,
        "finite_return_count": finite_return_count,
        "first_hour_open_time_utc": first_hour,
        "global_return_distribution": global_return_stats.as_dict(),
        "global_volume_distribution": global_volume_stats.as_dict() if volume_fields else None,
        "incomplete_1h_row_count": incomplete_count,
        "incomplete_by_month": dict(sorted(incomplete_by_month.items())),
        "incomplete_by_symbol": dict(sorted(incomplete_by_symbol.items())),
        "incomplete_examples": incomplete_examples,
        "last_hour_open_time_utc": last_hour,
        "monthly_rows": monthly_rows,
        "nan_inf_return_count": nan_inf_return_count,
        "negative_volume_row_count": negative_volume_count,
        "output_1h_row_count": row_count,
        "output_symbol_count": len(per_symbol),
        "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        "per_symbol_return_distribution": {symbol: stats.as_dict() for symbol, stats in sorted(return_stats_by_symbol.items())},
        "per_symbol_rows": per_symbol_rows,
        "primary_volume_field": volume_fields[0] if volume_fields else None,
        "volume_fields": volume_fields,
        "volume_liquidity_sanity_created": bool(volume_fields),
        "volume_value_count": volume_value_count,
        "zero_volume_row_count": zero_volume_count,
    }


def write_monthly_csv(path: Path, monthly_rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["month", "row_count", "complete_1h_row_count", "incomplete_1h_row_count", "symbol_count"],
        )
        writer.writeheader()
        writer.writerows(monthly_rows)


def build_execution() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    required_paths = [PREVIEW, READINESS_GATE, PIPELINE_SUMMARY, VALIDATOR_SUMMARY, OUTPUT_MANIFEST, OUTPUT_SCHEMA, PROVENANCE]
    artifacts_exist = {path.name: path.exists() for path in required_paths}

    preview = read_json(PREVIEW)
    readiness = read_json(READINESS_GATE)
    pipeline = read_json(PIPELINE_SUMMARY)
    validator = read_json(VALIDATOR_SUMMARY)
    manifest = read_json(OUTPUT_MANIFEST)
    schema = read_json(OUTPUT_SCHEMA)
    provenance = read_json(PROVENANCE)
    output_file = Path(manifest.get("output_file", ""))

    preview_confirmed = (
        preview.get("research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_status")
        == "PASS_REPO_ONLY_RESEARCH_BACKTEST_PREVIEW_AFTER_OKX_88_SYMBOL_1H_PANEL_READINESS_GATE_CREATED"
        and preview.get("replacement_checks_all_true") is True
        and preview.get("approval_grants_future_read_only_panel_baseline_research_execution_next") is True
    )
    guardrails_confirmed = (
        preview.get("strategy_search_allowed_now") is False
        and preview.get("candidate_generation_allowed_now") is False
        and preview.get("edge_claim_allowed_now") is False
        and preview.get("runtime_live_capital_allowed_now") is False
        and preview.get("future_execution_may_generate_candidates") is False
        and preview.get("future_execution_may_claim_edge") is False
    )
    panel_ok = (
        preview.get("read_only_research_panel_ready") is True
        and preview.get("output_valid_for_research_backtest") is True
        and preview.get("output_valid_for_edge_claim") is False
        and output_file.exists()
        and manifest.get("output_is_pipeline_validation_only") is True
    )
    if not (preview_confirmed and guardrails_confirmed and panel_ok and repo_clean):
        raise RuntimeError("preflight failed before panel diagnostics")

    diagnostics = stream_panel_diagnostics(output_file)

    monthly_coverage_created = True
    incomplete_hour_created = True
    return_distribution_created = True
    volume_created = diagnostics["volume_liquidity_sanity_created"]

    checks = {
        "artifacts_exist": all(artifacts_exist.values()),
        "guardrails_confirmed": guardrails_confirmed,
        "head_matches_expected": head == EXPECTED_HEAD,
        "holdout_rules_preserved": (
            preview.get("holdout_policy_required") is True
            and preview.get("holdout_registry_valid_for_this_panel") is False
            and preview.get("holdout_registry_creation_required_before_strategy_search") is True
            and preview.get("strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel") is True
            and preview.get("baseline_diagnostics_allowed_without_holdout") is True
        ),
        "no_forbidden_execution_actions": True,
        "no_original_source_read": True,
        "output_counts_match": (
            diagnostics["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS
            and diagnostics["output_symbol_count"] == EXPECTED_SYMBOL_COUNT
            and diagnostics["complete_1h_row_count"] == 2223843
            and diagnostics["incomplete_1h_row_count"] == 93
            and diagnostics["per_symbol_output_row_count_valid"] is True
        ),
        "preview_confirmed": preview_confirmed,
        "readiness_pipeline_validator_consistent": (
            readiness.get("output_valid_for_research_backtest") is True
            and pipeline.get("output_valid_for_edge_claim") is False
            and validator.get("numeric_sanity_validated") is True
            and schema.get("pipeline_validation_only") is True
            and provenance.get("provenance_entry_count") == 92664
        ),
        "repo_clean": repo_clean,
        "return_sanity": return_distribution_created and diagnostics["nan_inf_return_count"] == 0,
    }
    replacement_checks_all_true = all(checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    summary = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": preview.get("active_p1_attention_count", 0),
        "aggregation_performed_now": False,
        "all_hours_complete": diagnostics["all_hours_complete"],
        "baseline_diagnostics_allowed_without_holdout": True,
        "baseline_research_sanity_execution_performed": replacement_checks_all_true,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "complete_1h_row_count": diagnostics["complete_1h_row_count"],
        "cost_slippage_policy_required": True,
        "current_evidence_chain_quality_after_execution": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "expected_rows_per_symbol": EXPECTED_ROWS_PER_SYMBOL,
        "extreme_return_diagnostic_count": diagnostics["extreme_return_diagnostic_count"],
        "family_release_allowed_now": False,
        "finite_return_count": diagnostics["finite_return_count"],
        "future_execution_may_claim_edge": False,
        "future_execution_may_generate_candidates": False,
        "holdout_policy_required": True,
        "holdout_registry_creation_required_before_strategy_search": True,
        "holdout_registry_valid_for_this_panel": False,
        "incomplete_1h_row_count": diagnostics["incomplete_1h_row_count"],
        "incomplete_hour_diagnostics_created": incomplete_hour_created,
        "monthly_coverage_diagnostics_created": monthly_coverage_created,
        "nan_inf_return_count": diagnostics["nan_inf_return_count"],
        "next_module": next_module,
        "null_baseline_required": True,
        "okx_88_symbol_1h_panel_baseline_research_sanity_execution_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "original_1m_source_read_performed": False,
        "original_source_full_csv_read_performed": False,
        "output_1h_row_count": diagnostics["output_1h_row_count"],
        "output_symbol_count": diagnostics["output_symbol_count"],
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": True,
        "panel_output_read_performed": True,
        "per_symbol_output_row_count_valid": diagnostics["per_symbol_output_row_count_valid"],
        "preview_confirmed": preview_confirmed,
        "read_only_research_panel_ready": True,
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "return_distribution_sanity_created": return_distribution_created,
        "runtime_live_capital_allowed_now": False,
        "selected_symbol_count": preview.get("selected_symbol_count"),
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel": True,
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "volume_liquidity_sanity_created": volume_created,
    }

    return {
        "diagnostics": diagnostics,
        "summary": summary,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    diagnostics = outputs["diagnostics"]
    summary = outputs["summary"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_report.json", summary)
    write_monthly_csv(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_monthly_coverage_diagnostics.csv", diagnostics["monthly_rows"])
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_incomplete_hour_diagnostics.json",
        {
            "incomplete_1h_row_count": diagnostics["incomplete_1h_row_count"],
            "incomplete_by_month": diagnostics["incomplete_by_month"],
            "incomplete_by_symbol": diagnostics["incomplete_by_symbol"],
            "incomplete_examples": diagnostics["incomplete_examples"],
        },
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_return_distribution_sanity.json",
        {
            "extreme_return_abs_threshold": diagnostics["extreme_return_abs_threshold"],
            "extreme_return_diagnostic_count": diagnostics["extreme_return_diagnostic_count"],
            "finite_return_count": diagnostics["finite_return_count"],
            "global_return_distribution": diagnostics["global_return_distribution"],
            "nan_inf_return_count": diagnostics["nan_inf_return_count"],
            "per_symbol_return_distribution": diagnostics["per_symbol_return_distribution"],
        },
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_volume_liquidity_sanity.json",
        {
            "global_volume_distribution": diagnostics["global_volume_distribution"],
            "negative_volume_row_count": diagnostics["negative_volume_row_count"],
            "primary_volume_field": diagnostics["primary_volume_field"],
            "volume_fields": diagnostics["volume_fields"],
            "volume_liquidity_sanity_created": diagnostics["volume_liquidity_sanity_created"],
            "volume_value_count": diagnostics["volume_value_count"],
            "zero_volume_row_count": diagnostics["zero_volume_row_count"],
        },
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_null_cost_holdout_readiness_report.json",
        {
            "cost_slippage_policy_required": True,
            "holdout_policy_required": True,
            "holdout_registry_creation_required_before_strategy_search": True,
            "holdout_registry_valid_for_this_panel": False,
            "null_baseline_required": True,
            "strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel": True,
        },
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_route_eligibility_report.json",
        {
            "baseline_diagnostics_allowed_without_holdout": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "next_module": summary["next_module"],
            "runtime_live_capital_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
    )
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_summary.json", summary)


def main() -> int:
    outputs = build_execution()
    write_outputs(outputs)
    print(json.dumps(outputs["summary"], indent=2, sort_keys=True))
    return 0 if outputs["summary"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
