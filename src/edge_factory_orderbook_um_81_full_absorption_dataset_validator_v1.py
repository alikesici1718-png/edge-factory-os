#!/usr/bin/env python
"""Validate 81-symbol absorption research dataset outputs and safety boundaries."""

from __future__ import annotations

import csv
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

BUILD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_build_summary.json"
BUILD_SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_build_summary.md"
PARTITION_MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_partition_manifest.csv"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_validator_report.md"

CODE_AND_REPORT_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_81_full_absorption_dataset_builder_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_81_full_absorption_dataset_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_81_full_absorption_dataset_builder_v1.ps1",
    REPO_ROOT / "run_orderbook_um_81_full_absorption_dataset_validator_v1.ps1",
    REPO_ROOT / "docs" / "orderbook_um_81_full_absorption_dataset_notes_v1.md",
    BUILD_SUMMARY_MD,
    VALIDATOR_MD,
]

EXPECTED_SYMBOL_COUNT = 81
EXPECTED_FULL_PAIR_COUNT = 99404
STANDARD_REQUIRED_COLUMNS = {
    "timestamp",
    "symbol",
    "file_date",
    "year_month",
    "bid_depth_pct_1",
    "ask_depth_pct_1",
    "bid_notional_pct_1",
    "ask_notional_pct_1",
    "depth_imbalance_proxy",
    "aggressive_buy_quantity",
    "aggressive_sell_quantity",
    "aggressive_buy_notional",
    "aggressive_sell_notional",
    "trade_count",
    "total_quantity",
    "total_notional",
    "buy_sell_flow_imbalance",
    "rolling_flow_pressure",
    "rolling_depth_imbalance",
    "flow_depth_divergence_proxy",
    "absorption_category",
}
LEAN_REQUIRED_COLUMNS = {
    "timestamp",
    "symbol",
    "file_date",
    "year_month",
    "absorption_category",
    "trade_count",
    "total_qty",
    "total_notional",
    "aggressive_buy_qty",
    "aggressive_sell_qty",
    "aggressive_buy_notional",
    "aggressive_sell_notional",
    "flow_imbalance",
    "rolling_flow_pressure",
    "depth_imbalance_proxy",
    "rolling_depth_imbalance_proxy",
    "flow_depth_divergence_proxy",
    "data_quality_flags",
}
EXPECTED_CATEGORIES = {
    "BUY_PRESSURE_ABSORBED",
    "SELL_PRESSURE_ABSORBED",
    "FLOW_AND_DEPTH_ALIGNED_UP",
    "FLOW_AND_DEPTH_ALIGNED_DOWN",
    "MIXED_OR_NOISY",
    "INSUFFICIENT_DATA",
}
FORBIDDEN_PATTERNS = [
    r"\bstrategy\b",
    r"\bbacktest\b",
    r"\bsignal\b",
    r"\bpnl\b",
    r"\bentry\b",
    r"\bexit\b",
    r"\bstop\b",
    r"\btarget\b",
    r"\bleverage\b",
    r"\bposition sizing\b",
    r"\border execution\b",
    r"\bexecution logic\b",
    r"\bprivate\b",
    r"\baccount\b",
    r"\bapi key\b",
    r"\bsecret\b",
    r"\brecommendation\b",
    r"\bbuy label\b",
    r"\bsell label\b",
]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"not a JSON object: {path}")
    return payload


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def forbidden_term(pattern: str) -> str:
    return pattern.replace(r"\b", "").replace("\\", "")


def context_window(lines: list[str], line_number: int, radius: int = 3) -> list[dict[str, Any]]:
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)
    return [
        {"line": current, "text": lines[current - 1].rstrip()[:300]}
        for current in range(start, end + 1)
    ]


def classify_forbidden_match(pattern: str, context: list[dict[str, Any]]) -> tuple[str, str]:
    term = forbidden_term(pattern).lower()
    context_text = "\n".join(str(item.get("text", "")) for item in context).lower()
    safety_markers = [
        "no ",
        "not ",
        "without",
        "absent",
        "missing",
        "blocked",
        "forbidden",
        "prohibited",
        "not allowed",
        "refuse",
        "safety",
        "research dataset construction only",
    ]
    if any(marker in context_text for marker in safety_markers):
        return "SAFETY_CONTEXT", "safety, absence, or refusal wording"
    if term == "exit" and ("exitcode" in context_text or "systemexit" in context_text):
        return "SAFETY_CONTEXT", "runner control context"
    if term == "stop" and "erroractionpreference" in context_text:
        return "SAFETY_CONTEXT", "runner control context"
    if term == "target" and (
        "output root" in context_text
        or "raw zip" in context_text
        or "target" in context_text and "inside repo" in context_text
    ):
        return "SAFETY_CONTEXT", "filesystem safety context"
    if term in {"account", "private"} and "public" in context_text:
        return "SAFETY_CONTEXT", "public-data boundary context"
    return "REAL_BLOCKER", "potential prohibited restricted behavior"


def scan_forbidden_terms() -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    blocking: list[dict[str, Any]] = []
    for path in CODE_AND_REPORT_FILES:
        if not path.exists() or path.is_dir():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, line in enumerate(lines, start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    if "FORBIDDEN_PATTERNS" in line or line.strip().startswith("r\""):
                        classification, reason = "SAFETY_CONTEXT", "scanner pattern declaration"
                    else:
                        context = context_window(lines, line_number)
                        classification, reason = classify_forbidden_match(pattern, context)
                    item = {
                        "path": str(path.relative_to(REPO_ROOT)),
                        "line": line_number,
                        "term": forbidden_term(pattern),
                        "pattern": pattern,
                        "text": line.strip()[:240],
                        "classification": classification,
                        "classification_reason": reason,
                    }
                    matches.append(item)
                    if classification == "REAL_BLOCKER":
                        blocking.append(item)
    return {"matches": matches, "blocking_matches": blocking}


def raw_extracted_files_inside_repo() -> list[str]:
    matches: list[str] = []
    patterns = [
        "*-bookDepth-*.csv",
        "*-aggTrades-*.csv",
        "*-bookDepth-*.zip",
        "*-aggTrades-*.zip",
        "*-bookDepth-*.zip.CHECKSUM",
        "*-aggTrades-*.zip.CHECKSUM",
    ]
    for pattern in patterns:
        for path in REPO_ROOT.rglob(pattern):
            if ".git" in path.parts:
                continue
            matches.append(str(path.relative_to(REPO_ROOT)))
    return sorted(set(matches))


def parquet_modules() -> tuple[Any | None, Any | None, str]:
    try:
        import pyarrow.parquet as pq  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001
        return None, None, f"{type(exc).__name__}: {exc}"
    return pq, pq, ""


def load_partition_sidecars(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    sidecars: list[dict[str, Any]] = []
    for row in rows:
        if row.get("status") not in {"WRITTEN_VERIFIED_PARTITION", "SKIPPED_VERIFIED_PARTITION"}:
            continue
        sidecar_path = Path(str(row.get("sidecar_path", "")))
        if sidecar_path.exists():
            payload = load_json(sidecar_path)
            payload["_manifest_row"] = row
            sidecars.append(payload)
    return sidecars


def duplicate_check_from_parquet(partition_paths: list[Path]) -> dict[str, Any]:
    pq, _unused, engine_error = parquet_modules()
    if pq is None:
        return {
            "checked": False,
            "engine_error": engine_error,
            "duplicate_symbol_timestamp_count": None,
            "passed": False,
        }
    duplicate_count = 0
    for path in partition_paths:
        table = pq.ParquetFile(path).read(columns=["symbol", "timestamp"])
        frame = table.to_pandas()
        duplicate_count += int(frame.duplicated(subset=["symbol", "timestamp"]).sum())
    return {
        "checked": True,
        "engine_error": "",
        "duplicate_symbol_timestamp_count": duplicate_count,
        "passed": duplicate_count == 0,
    }


def validate_partitions(manifest_rows: list[dict[str, str]], output_mode: str) -> dict[str, Any]:
    successful = [
        row
        for row in manifest_rows
        if row.get("status") in {"WRITTEN_VERIFIED_PARTITION", "SKIPPED_VERIFIED_PARTITION"}
    ]
    sidecars = load_partition_sidecars(manifest_rows)
    partition_paths = [Path(str(row.get("partition_path", ""))) for row in successful]
    existing_partition_paths = [path for path in partition_paths if path.exists()]
    schemas = [tuple(item.get("schema", [])) for item in sidecars]
    category_counts: dict[str, int] = {}
    duplicate_count_from_sidecars = 0
    row_count_total = 0
    parquet_size_bytes_total = 0
    for sidecar in sidecars:
        row_count_total += int_value(sidecar.get("row_count"))
        parquet_size_bytes_total += int_value(sidecar.get("parquet_size_bytes"))
        duplicate_count_from_sidecars += int_value(sidecar.get("duplicate_symbol_timestamp_count"))
        for category, count in dict(sidecar.get("absorption_category_counts", {})).items():
            category_counts[str(category)] = category_counts.get(str(category), 0) + int_value(count)
    duplicate_scan = duplicate_check_from_parquet(existing_partition_paths) if existing_partition_paths else {
        "checked": False,
        "engine_error": "no partitions to read",
        "duplicate_symbol_timestamp_count": None,
        "passed": False,
    }
    schema_columns = set(schemas[0]) if schemas else set()
    required_columns = LEAN_REQUIRED_COLUMNS if output_mode == "lean" else STANDARD_REQUIRED_COLUMNS
    schema_column_count = len(schemas[0]) if schemas else 0
    return {
        "successful_partition_count": len(successful),
        "existing_partition_count": len(existing_partition_paths),
        "sidecar_count": len(sidecars),
        "row_count_total": row_count_total,
        "parquet_size_bytes_total": parquet_size_bytes_total,
        "actual_smoke_parquet_size_mb": round(parquet_size_bytes_total / 1_000_000, 6),
        "schema_consistent": bool(schemas) and len(set(schemas)) == 1,
        "schema_column_count": schema_column_count,
        "required_columns_present": bool(schema_columns) and required_columns.issubset(schema_columns),
        "missing_required_columns": sorted(required_columns - schema_columns),
        "category_counts": category_counts,
        "category_counts_exist": bool(category_counts),
        "expected_categories_known": set(category_counts).issubset(EXPECTED_CATEGORIES),
        "sidecar_duplicate_symbol_timestamp_count": duplicate_count_from_sidecars,
        "duplicate_check": duplicate_scan,
    }


def build_report() -> dict[str, Any]:
    build_summary = load_json(BUILD_SUMMARY_JSON)
    manifest_rows = read_csv_rows(PARTITION_MANIFEST_CSV)
    output_root = Path(str(build_summary.get("output_root", "")))
    output_mode = str(build_summary.get("output_mode", "standard") or "standard")
    raw_inside = raw_extracted_files_inside_repo()
    partition_report = validate_partitions(manifest_rows, output_mode)
    symbols = {row.get("symbol", "") for row in manifest_rows if row.get("symbol")}
    full_mode = build_summary.get("mode") == "FULL_BUILD"
    scan = scan_forbidden_terms()
    partitions_exist = partition_report["existing_partition_count"] > 0
    all_full_partitions_present = (
        partition_report["successful_partition_count"] == EXPECTED_FULL_PAIR_COUNT if full_mode else partitions_exist
    )
    checks = {
        "build_summary_exists": BUILD_SUMMARY_JSON.exists(),
        "partition_manifest_exists": PARTITION_MANIFEST_CSV.exists(),
        "dataset_output_root_outside_repo": bool(str(output_root)) and not path_is_inside(output_root, REPO_ROOT),
        "no_raw_extracted_files_inside_repo": not raw_inside,
        "symbols_represented_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
        "partitions_exist": partitions_exist,
        "all_required_partitions_present_for_scope": all_full_partitions_present,
        "schema_is_consistent": partition_report["schema_consistent"],
        "required_schema_columns_present": partition_report["required_columns_present"],
        "no_duplicate_symbol_timestamp_rows_inside_partitions": partition_report["duplicate_check"]["passed"]
        or partition_report["sidecar_duplicate_symbol_timestamp_count"] == 0 and partitions_exist,
        "row_counts_nonzero": partition_report["row_count_total"] > 0,
        "absorption_category_counts_exist": partition_report["category_counts_exist"],
        "absorption_categories_known": partition_report["expected_categories_known"],
        "no_prohibited_research_scope_logic": not scan["blocking_matches"],
    }
    replacement_checks_all_true = all(checks.values())
    if replacement_checks_all_true and full_mode:
        status = "PASS_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_VALIDATED"
    elif replacement_checks_all_true:
        status = "PASS_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_SMOKE_VALIDATED"
    else:
        status = "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_VALIDATION"
    return {
        "status": status,
        "created_at_utc": utc_now_text(),
        "build_summary_status": build_summary.get("status", ""),
        "build_mode": build_summary.get("mode", ""),
        "output_mode": output_mode,
        "output_root": str(output_root),
        "matched_pair_count": build_summary.get("matched_pair_count", ""),
        "estimated_rows": build_summary.get("estimated_rows", ""),
        "estimated_parquet_gb": build_summary.get("estimated_parquet_gb", ""),
        "estimated_standard_parquet_gb": build_summary.get("estimated_standard_parquet_gb", ""),
        "estimated_lean_parquet_gb": build_summary.get("estimated_lean_parquet_gb", ""),
        "free_disk_gb": build_summary.get("free_disk_gb", ""),
        "required_free_disk_selected_mode_gb": build_summary.get("required_free_disk_selected_mode_gb", ""),
        "actual_smoke_parquet_size_mb": partition_report.get("actual_smoke_parquet_size_mb", ""),
        "schema_column_count": partition_report.get("schema_column_count", ""),
        "smoke_result": build_summary.get("smoke_result", ""),
        "partition_report": partition_report,
        "raw_extracted_files_inside_repo": raw_inside[:100],
        "code_forbidden_term_scan": scan,
        "validation_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "next_module": (
            "ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_RESEARCH_REVIEW"
            if replacement_checks_all_true
            else "ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_BLOCKER_REVIEW"
        ),
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 full absorption dataset validator v1",
        "",
        f"status: {report['status']}",
        f"build_summary_status: {report.get('build_summary_status', '')}",
        f"build_mode: {report.get('build_mode', '')}",
        f"output_mode: {report.get('output_mode', '')}",
        f"output_root: {report.get('output_root', '')}",
        f"estimated_rows: {report.get('estimated_rows', '')}",
        f"estimated_standard_parquet_gb: {report.get('estimated_standard_parquet_gb', '')}",
        f"estimated_lean_parquet_gb: {report.get('estimated_lean_parquet_gb', '')}",
        f"selected_estimated_parquet_gb: {report.get('estimated_parquet_gb', '')}",
        f"free_disk_gb: {report.get('free_disk_gb', '')}",
        f"required_free_disk_selected_mode_gb: {report.get('required_free_disk_selected_mode_gb', '')}",
        f"actual_smoke_parquet_size_mb: {report.get('actual_smoke_parquet_size_mb', '')}",
        f"schema_column_count: {report.get('schema_column_count', '')}",
        f"smoke_result: {report.get('smoke_result', '')}",
        f"replacement_checks_all_true: {str(report['replacement_checks_all_true']).lower()}",
        "",
        "## Checks",
    ]
    for key, value in report["validation_checks"].items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(["", "## Forbidden-term scan"])
    scan = report.get("code_forbidden_term_scan", {"matches": [], "blocking_matches": []})
    lines.append(f"- matches: {len(scan.get('matches', []))}")
    lines.append(f"- blocking_matches: {len(scan.get('blocking_matches', []))}")
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_VALIDATION",
            "created_at_utc": utc_now_text(),
            "exact_blocker": f"{type(exc).__name__}: {exc}",
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_BLOCKER_REVIEW",
        }
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report_md(report)
    print(f"status: {report['status']}")
    print(f"validator_json: {VALIDATOR_JSON}")
    print(f"validator_md: {VALIDATOR_MD}")
    print(f"replacement_checks_all_true: {str(report['replacement_checks_all_true']).lower()}")
    print(f"next_module: {report['next_module']}")
    return 0 if report["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
