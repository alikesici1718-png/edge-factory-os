#!/usr/bin/env python
"""Build pilot-only Binance USD-M bookDepth feature diagnostics from existing ZIPs."""

from __future__ import annotations

import bisect
import csv
import io
import json
import math
import os
import statistics
import sys
import zipfile
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
PILOT_SCHEMA_SUMMARY = OUTPUTS_DIR / "orderbook_um_pilot_schema_summary.json"
AVAILABILITY_MANIFEST = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.csv"
BLOCKED_UNSUPPORTED_MD = OUTPUTS_DIR / "orderbook_um_pilot_feature_BLOCKED_UNSUPPORTED_SCHEMA.md"
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_pilot_feature_preview_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_pilot_feature_preview_summary.md"
QUANTILE_CSV = OUTPUTS_DIR / "orderbook_um_pilot_feature_quantile_diagnostics.csv"
QUALITY_MD = OUTPUTS_DIR / "orderbook_um_pilot_feature_quality_report.md"
FEATURE_SAMPLE_CSV = OUTPUTS_DIR / "orderbook_um_pilot_feature_sample.csv"
FEATURE_SAMPLE_PARQUET = OUTPUTS_DIR / "orderbook_um_pilot_feature_sample.parquet"

MAX_SOURCE_ROWS_PER_ZIP = int(os.environ.get("ORDERBOOK_FEATURE_PREVIEW_MAX_SOURCE_ROWS_PER_ZIP", "2000000"))
MAX_FEATURE_SAMPLE_ROWS = int(os.environ.get("ORDERBOOK_FEATURE_PREVIEW_SAMPLE_ROWS", "5000"))
ROLLING_WINDOW = 20
FORWARD_HORIZONS_SECONDS = [10, 30, 60, 300]
MOVE_HORIZONS_SECONDS = [60, 300]
REQUIRED_SCHEMA_COLUMNS = {"timestamp", "percentage", "depth", "notional"}


class PreviewBlocked(RuntimeError):
    """Raised when the preview must stop closed."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def pilot_dir() -> Path:
    root = data_root()
    if path_is_inside(root, REPO_ROOT):
        raise PreviewBlocked(f"data root resolves inside repo: {root}")
    return root / "binance_um_orderbook_pilot"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_blocked(reason: str, status: str = "BLOCKED_UNSUPPORTED_BOOKDEPTH_SCHEMA") -> None:
    write_text(
        BLOCKED_UNSUPPORTED_MD,
        "\n".join(
            [
                f"# {status}",
                "",
                f"created_at_utc: {utc_now_text()}",
                f"reason: {reason}",
                "replacement_checks_all_true=false",
                "next_module=ORDERBOOK_UM_PILOT_FEATURE_BLOCKER_REVIEW",
                "",
            ]
        ),
    )


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PreviewBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PreviewBlocked(f"input is not a JSON object: {path}")
    return payload


def load_manifest_urls() -> set[str]:
    if not AVAILABILITY_MANIFEST.exists():
        raise PreviewBlocked(f"missing required manifest: {AVAILABILITY_MANIFEST}")
    urls: set[str] = set()
    with AVAILABILITY_MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("status") == "AVAILABLE" and row.get("url"):
                urls.add(row["url"])
    return urls


def resolve_zip_path(download: dict[str, Any], base_pilot_dir: Path) -> Path:
    source_path = Path(str(download.get("local_zip_path", "")))
    file_name = source_path.name
    symbol = str(download.get("symbol", ""))
    candidate = base_pilot_dir / symbol / file_name
    if candidate.exists():
        zip_path = candidate
    elif source_path.exists() and not os.environ.get("EDGE_FACTORY_DATA_ROOT"):
        zip_path = source_path
    else:
        raise PreviewBlocked(f"pilot ZIP not found for {symbol}: {candidate}")
    if path_is_inside(zip_path, REPO_ROOT):
        raise PreviewBlocked(f"pilot ZIP resolves inside repo: {zip_path}")
    if zip_path.suffix.lower() != ".zip":
        raise PreviewBlocked(f"pilot input is not a ZIP: {zip_path}")
    return zip_path


def normalize_header(header: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for column in header:
        normalized = column.strip().lower().replace(" ", "_")
        mapping[normalized] = column
    return mapping


def parse_timestamp(raw: str) -> tuple[str, float] | tuple[None, None]:
    text = str(raw).strip()
    if not text:
        return None, None
    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            return parsed.strftime("%Y-%m-%dT%H:%M:%SZ"), parsed.timestamp()
        except ValueError:
            pass
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        parsed = parsed.astimezone(timezone.utc)
        return parsed.strftime("%Y-%m-%dT%H:%M:%SZ"), parsed.timestamp()
    except ValueError:
        return None, None


def parse_float(raw: Any) -> float | None:
    try:
        value = float(str(raw).strip())
    except (TypeError, ValueError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def row_value(row: dict[str, str], header_map: dict[str, str], name: str) -> str:
    return row.get(header_map[name], "")


def avg_price(depth: float | None, notional: float | None) -> float | None:
    if depth is None or notional is None or depth <= 0:
        return None
    return notional / depth


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def imbalance(bid_depth: float | None, ask_depth: float | None) -> float | None:
    if bid_depth is None or ask_depth is None:
        return None
    total = bid_depth + ask_depth
    if total <= 0:
        return None
    return (bid_depth - ask_depth) / total


def group_feature_row(symbol: str, file_date: str, timestamp: str, epoch_seconds: float, buckets: dict[float, dict[str, float]]) -> dict[str, Any]:
    def bucket_value(pct: float, key: str) -> float | None:
        item = buckets.get(pct)
        if not item:
            return None
        return item.get(key)

    bid_depth_1 = bucket_value(-1.0, "depth")
    ask_depth_1 = bucket_value(1.0, "depth")
    bid_depth_5 = bucket_value(-5.0, "depth")
    ask_depth_5 = bucket_value(5.0, "depth")
    bid_notional_1 = bucket_value(-1.0, "notional")
    ask_notional_1 = bucket_value(1.0, "notional")
    bid_notional_5 = bucket_value(-5.0, "notional")
    ask_notional_5 = bucket_value(5.0, "notional")
    bid_avg_1 = avg_price(bid_depth_1, bid_notional_1)
    ask_avg_1 = avg_price(ask_depth_1, ask_notional_1)
    bid_avg_5 = avg_price(bid_depth_5, bid_notional_5)
    ask_avg_5 = avg_price(ask_depth_5, ask_notional_5)
    mid_1 = None if bid_avg_1 is None or ask_avg_1 is None else (bid_avg_1 + ask_avg_1) / 2.0
    spread_1 = None if bid_avg_1 is None or ask_avg_1 is None else ask_avg_1 - bid_avg_1
    spread_bps_1 = None if mid_1 is None or mid_1 == 0 or spread_1 is None else (spread_1 / mid_1) * 10000.0
    micro_1 = None
    if None not in (bid_avg_1, ask_avg_1, bid_depth_1, ask_depth_1):
        denom = bid_depth_1 + ask_depth_1
        if denom > 0:
            micro_1 = (bid_avg_1 * ask_depth_1 + ask_avg_1 * bid_depth_1) / denom
    return {
        "timestamp": timestamp,
        "timestamp_epoch_seconds": epoch_seconds,
        "symbol": symbol,
        "pilot_file_date": file_date,
        "percentage_bucket_count": len(buckets),
        "bid_depth_pct_1": bid_depth_1,
        "ask_depth_pct_1": ask_depth_1,
        "total_depth_pct_1": None if bid_depth_1 is None or ask_depth_1 is None else bid_depth_1 + ask_depth_1,
        "bid_notional_pct_1": bid_notional_1,
        "ask_notional_pct_1": ask_notional_1,
        "bid_avg_price_pct_1": bid_avg_1,
        "ask_avg_price_pct_1": ask_avg_1,
        "mid_price_proxy_pct1": mid_1,
        "spread_proxy_pct1": spread_1,
        "spread_bps_proxy_pct1": spread_bps_1,
        "imbalance_1": imbalance(bid_depth_1, ask_depth_1),
        "microprice_proxy_pct1": micro_1,
        "bid_depth_pct_5": bid_depth_5,
        "ask_depth_pct_5": ask_depth_5,
        "total_depth_pct_5": None if bid_depth_5 is None or ask_depth_5 is None else bid_depth_5 + ask_depth_5,
        "bid_notional_pct_5": bid_notional_5,
        "ask_notional_pct_5": ask_notional_5,
        "bid_avg_price_pct_5": bid_avg_5,
        "ask_avg_price_pct_5": ask_avg_5,
        "imbalance_5": imbalance(bid_depth_5, ask_depth_5),
    }


def parse_pilot_zip(download: dict[str, Any], zip_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    symbol = str(download.get("symbol", ""))
    file_date = str(download.get("file_date_or_month", ""))
    groups: dict[str, dict[str, Any]] = {}
    source_rows = 0
    malformed_rows = 0
    missing_timestamp_rows = 0
    duplicate_timestamp_bucket_count = 0
    detected_header: list[str] = []
    csv_members: list[str] = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_members) != 1:
            raise PreviewBlocked(f"expected exactly one CSV member in {zip_path}, found {csv_members}")
        with archive.open(csv_members[0], "r") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            reader = csv.DictReader(text)
            detected_header = list(reader.fieldnames or [])
            header_map = normalize_header(detected_header)
            missing_columns = sorted(REQUIRED_SCHEMA_COLUMNS - set(header_map))
            if missing_columns:
                raise PreviewBlocked(f"unsupported bookDepth schema for {zip_path.name}; missing columns: {missing_columns}")
            for row in reader:
                source_rows += 1
                if source_rows > MAX_SOURCE_ROWS_PER_ZIP:
                    raise PreviewBlocked(f"source row cap exceeded for {zip_path.name}")
                timestamp, epoch_seconds = parse_timestamp(row_value(row, header_map, "timestamp"))
                if timestamp is None or epoch_seconds is None:
                    missing_timestamp_rows += 1
                    continue
                pct = parse_float(row_value(row, header_map, "percentage"))
                depth = parse_float(row_value(row, header_map, "depth"))
                notional = parse_float(row_value(row, header_map, "notional"))
                if pct is None or depth is None or notional is None:
                    malformed_rows += 1
                    continue
                pct = float(int(pct)) if abs(pct - int(pct)) < 1e-9 else pct
                group = groups.setdefault(timestamp, {"epoch_seconds": epoch_seconds, "buckets": {}})
                buckets = group["buckets"]
                if pct in buckets:
                    duplicate_timestamp_bucket_count += 1
                buckets[pct] = {"depth": depth, "notional": notional, "avg_price": avg_price(depth, notional)}

    feature_rows = [
        group_feature_row(symbol, file_date, timestamp, payload["epoch_seconds"], payload["buckets"])
        for timestamp, payload in groups.items()
    ]
    feature_rows.sort(key=lambda item: item["timestamp_epoch_seconds"])
    duplicate_timestamp_count = sum(count - 1 for count in Counter(row["timestamp"] for row in feature_rows).values() if count > 1)
    file_summary = {
        "symbol": symbol,
        "file_date_or_month": file_date,
        "zip_path": str(zip_path),
        "zip_bytes": zip_path.stat().st_size,
        "csv_member": csv_members[0] if csv_members else "",
        "source_rows_read": source_rows,
        "feature_rows": len(feature_rows),
        "detected_schema_columns": detected_header,
        "timestamp_min": feature_rows[0]["timestamp"] if feature_rows else None,
        "timestamp_max": feature_rows[-1]["timestamp"] if feature_rows else None,
        "duplicate_timestamp_count": duplicate_timestamp_count,
        "duplicate_timestamp_bucket_count": duplicate_timestamp_bucket_count,
        "missing_timestamp_or_malformed_row_count": missing_timestamp_rows + malformed_rows,
        "missing_timestamp_rows": missing_timestamp_rows,
        "malformed_rows": malformed_rows,
    }
    return feature_rows, file_summary


def add_path_dependent_features(rows: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["symbol"], row["pilot_file_date"]), []).append(row)
    for group_rows in grouped.values():
        group_rows.sort(key=lambda item: item["timestamp_epoch_seconds"])
        imbalance_window: deque[float] = deque(maxlen=ROLLING_WINDOW)
        spread_window: deque[float] = deque(maxlen=ROLLING_WINDOW)
        mid_return_window: deque[float] = deque(maxlen=ROLLING_WINDOW)
        previous: dict[str, Any] | None = None
        for row in group_rows:
            for pct in ["1", "5"]:
                key = f"total_depth_pct_{pct}"
                change_key = f"total_depth_pct{pct}_change"
                pull_key = f"liquidity_pull_proxy_pct{pct}"
                prev_value = None if previous is None else previous.get(key)
                value = row.get(key)
                if value is None or prev_value is None:
                    row[change_key] = None
                    row[pull_key] = None
                else:
                    change = value - prev_value
                    row[change_key] = change
                    row[pull_key] = max(-change, 0.0)
            mid = row.get("mid_price_proxy_pct1")
            prev_mid = None if previous is None else previous.get("mid_price_proxy_pct1")
            if mid is None or prev_mid in (None, 0):
                row["mid_return_1_observation"] = None
            else:
                row["mid_return_1_observation"] = (mid / prev_mid) - 1.0
            if row.get("imbalance_1") is not None:
                imbalance_window.append(row["imbalance_1"])
            if row.get("spread_bps_proxy_pct1") is not None:
                spread_window.append(row["spread_bps_proxy_pct1"])
            if row.get("mid_return_1_observation") is not None:
                mid_return_window.append(row["mid_return_1_observation"])
            row["rolling_imbalance_1_mean_20"] = statistics.fmean(imbalance_window) if imbalance_window else None
            row["rolling_spread_bps_mean_20"] = statistics.fmean(spread_window) if spread_window else None
            row["rolling_mid_return_vol_proxy_20"] = (
                statistics.pstdev(mid_return_window) if len(mid_return_window) >= 2 else None
            )
            previous = row


def add_forward_diagnostics(rows: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["symbol"], row["pilot_file_date"]), []).append(row)
    for group_rows in grouped.values():
        group_rows.sort(key=lambda item: item["timestamp_epoch_seconds"])
        times = [row["timestamp_epoch_seconds"] for row in group_rows]
        mids = [row.get("mid_price_proxy_pct1") for row in group_rows]
        for index, row in enumerate(group_rows):
            mid = row.get("mid_price_proxy_pct1")
            for horizon in FORWARD_HORIZONS_SECONDS:
                row[f"forward_return_{horizon}s"] = None
                if mid not in (None, 0):
                    target = row["timestamp_epoch_seconds"] + horizon
                    future_index = bisect.bisect_left(times, target, lo=index + 1)
                    if future_index < len(group_rows) and mids[future_index] is not None:
                        row[f"forward_return_{horizon}s"] = (mids[future_index] / mid) - 1.0
            for horizon in MOVE_HORIZONS_SECONDS:
                row[f"max_favorable_mid_move_{horizon}s"] = None
                row[f"max_adverse_mid_move_{horizon}s"] = None
                if mid in (None, 0):
                    continue
                end_time = row["timestamp_epoch_seconds"] + horizon
                end_index = bisect.bisect_right(times, end_time, lo=index + 1)
                moves = [(future_mid / mid) - 1.0 for future_mid in mids[index + 1 : end_index] if future_mid is not None]
                if moves:
                    row[f"max_favorable_mid_move_{horizon}s"] = max(moves)
                    row[f"max_adverse_mid_move_{horizon}s"] = min(moves)


def numeric_value(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def positive_rate(values: list[float]) -> float | None:
    return sum(1 for value in values if value > 0) / len(values) if values else None


def quantile_diagnostics(rows: list[dict[str, Any]], feature_columns: list[str]) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    forward_columns = [f"forward_return_{horizon}s" for horizon in FORWARD_HORIZONS_SECONDS]
    total_rows = len(rows)
    for feature in feature_columns:
        if feature in forward_columns or feature in {"timestamp_epoch_seconds"}:
            continue
        values = [(idx, numeric_value(row.get(feature))) for idx, row in enumerate(rows)]
        present = [(idx, value) for idx, value in values if value is not None]
        if not present:
            continue
        unique_count = len({value for _, value in present})
        bucket_count = min(4, unique_count, len(present))
        if bucket_count < 2:
            stability = "too_few_unique_values_for_quantiles"
            bucket_count = 1
        else:
            stability = ""
        present.sort(key=lambda item: item[1])
        buckets: dict[int, list[int]] = {bucket: [] for bucket in range(1, bucket_count + 1)}
        for rank, (idx, _value) in enumerate(present):
            bucket = min(bucket_count, int(rank * bucket_count / len(present)) + 1)
            buckets[bucket].append(idx)
        for bucket, indices in buckets.items():
            feature_values = [numeric_value(rows[idx].get(feature)) for idx in indices]
            feature_values = [value for value in feature_values if value is not None]
            row: dict[str, Any] = {
                "feature": feature,
                "quantile": f"q{bucket}_of_{bucket_count}",
                "count": len(indices),
                "total_rows": total_rows,
                "missing_rate": (total_rows - len(present)) / total_rows if total_rows else None,
                "feature_min": min(feature_values) if feature_values else None,
                "feature_max": max(feature_values) if feature_values else None,
                "stability_warning": stability or ("sample_too_small" if len(indices) < 30 else ""),
            }
            for forward in forward_columns:
                returns = [numeric_value(rows[idx].get(forward)) for idx in indices]
                returns = [value for value in returns if value is not None]
                row[f"mean_{forward}"] = mean(returns)
                row[f"median_{forward}"] = median(returns)
                row[f"positive_rate_{forward}"] = positive_rate(returns)
                row[f"count_{forward}"] = len(returns)
            diagnostics.append(row)
    return diagnostics


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "" if row.get(field) is None else row.get(field, "") for field in fieldnames})


def try_write_parquet(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> tuple[bool, str | None]:
    try:
        import pyarrow as pa  # type: ignore
        import pyarrow.parquet as pq  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return False, f"pyarrow unavailable: {exc}"
    columns: dict[str, list[Any]] = {field: [row.get(field) for row in rows] for field in fieldnames}
    table = pa.Table.from_pydict(columns)
    pq.write_table(table, path)
    return True, None


def unsupported_features() -> list[dict[str, str]]:
    return [
        {
            "feature": "best_bid_best_ask_exact",
            "reason": "pilot schema has timestamp, percentage, depth, notional; it does not expose price levels.",
        },
        {
            "feature": "top_level_bid_quantity_ask_quantity_exact",
            "reason": "pilot schema exposes cumulative percentage-depth rows, not level-1 queue quantities.",
        },
        {
            "feature": "top_5_level_depth_exact",
            "reason": "derived pct_5 depth is available, but exact five book levels are not present.",
        },
        {
            "feature": "top_10_depth",
            "reason": "pilot files do not contain +/-10 percentage buckets or individual top-ten levels.",
        },
        {
            "feature": "exact_microprice",
            "reason": "exact microprice requires best bid/ask and level-1 quantities; only pct_1 proxy is derived.",
        },
    ]


def summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Orderbook UM pilot feature preview v1",
        "",
        f"status: {summary['status']}",
        f"created_at_utc: {summary['created_at_utc']}",
        f"pilot_zips_found: {summary['pilot_zips_found']}",
        f"pilot_zips_parsed: {summary['pilot_zips_parsed']}",
        f"symbols_parsed: {', '.join(summary['symbols_parsed'])}",
        f"suitable_for_next_step: {summary['suitable_for_next_step']}",
        f"next_recommended_step: {summary['next_recommended_step']}",
        "",
        "## Derived features",
    ]
    lines.extend(f"- {feature}" for feature in summary["derived_feature_list"])
    lines.extend(["", "## Unsupported features"])
    for item in summary["unsupported_feature_list"]:
        lines.append(f"- {item['feature']}: {item['reason']}")
    lines.extend(["", "## Outputs"])
    for key, value in summary["output_files"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "replacement_checks_all_true=true", ""])
    return "\n".join(lines)


def quality_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Orderbook UM pilot feature quality report v1",
        "",
        f"status: {summary['status']}",
        f"duplicate_timestamp_count: {summary['duplicate_timestamp_count']}",
        f"missing_timestamp_or_malformed_row_count: {summary['missing_timestamp_or_malformed_row_count']}",
        f"forward_diagnostic_availability: {json.dumps(summary['forward_diagnostic_availability'], sort_keys=True)}",
        "",
        "## Rows parsed per pilot file",
    ]
    for item in summary["pilot_file_summaries"]:
        lines.append(
            f"- {item['symbol']} {item['file_date_or_month']}: source_rows={item['source_rows_read']}, feature_rows={item['feature_rows']}, range={item['timestamp_min']} to {item['timestamp_max']}"
        )
    lines.extend(["", "## Stability warnings"])
    warnings = summary.get("stability_warnings") or []
    lines.extend(f"- {warning}" for warning in warnings)
    if not warnings:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    try:
        schema_summary = load_json(PILOT_SCHEMA_SUMMARY)
        manifest_urls = load_manifest_urls()
        downloads = schema_summary.get("downloads")
        if not isinstance(downloads, list) or not downloads:
            raise PreviewBlocked("pilot schema summary contains no downloads")
        base_pilot_dir = pilot_dir()
        if not base_pilot_dir.exists():
            raise PreviewBlocked(f"pilot directory not found: {base_pilot_dir}")
        all_feature_rows: list[dict[str, Any]] = []
        file_summaries: list[dict[str, Any]] = []
        for download in downloads:
            if not isinstance(download, dict):
                raise PreviewBlocked("invalid download entry in pilot schema summary")
            if download.get("url") not in manifest_urls:
                raise PreviewBlocked(f"pilot URL not present in availability manifest: {download.get('url')}")
            if download.get("checksum_verified") is not True:
                raise PreviewBlocked(f"pilot checksum was not verified in schema summary: {download.get('local_zip_path')}")
            zip_path = resolve_zip_path(download, base_pilot_dir)
            rows, file_summary = parse_pilot_zip(download, zip_path)
            if not rows:
                raise PreviewBlocked(f"no feature rows parsed from {zip_path}")
            all_feature_rows.extend(rows)
            file_summaries.append(file_summary)
        add_path_dependent_features(all_feature_rows)
        add_forward_diagnostics(all_feature_rows)

        identifier_columns = ["timestamp", "symbol", "pilot_file_date"]
        numeric_columns = sorted(
            {
                key
                for row in all_feature_rows
                for key, value in row.items()
                if key not in identifier_columns and numeric_value(value) is not None
            }
        )
        feature_columns = [column for column in numeric_columns if not column.startswith("forward_return_")]
        if not any(column in feature_columns for column in ["mid_price_proxy_pct1", "spread_bps_proxy_pct1", "imbalance_1", "imbalance_5"]):
            write_blocked("schema parsed, but no mid/spread/imbalance feature group could be derived")
            return 2

        sample_rows = all_feature_rows[:MAX_FEATURE_SAMPLE_ROWS]
        sample_fieldnames = identifier_columns + [column for column in numeric_columns if column not in identifier_columns]
        write_csv_rows(FEATURE_SAMPLE_CSV, sample_rows, sample_fieldnames)
        parquet_written, parquet_error = try_write_parquet(FEATURE_SAMPLE_PARQUET, sample_rows, sample_fieldnames)
        diagnostics = quantile_diagnostics(all_feature_rows, feature_columns)
        diagnostic_fields = [
            "feature",
            "quantile",
            "count",
            "total_rows",
            "missing_rate",
            "feature_min",
            "feature_max",
            "stability_warning",
        ]
        for horizon in FORWARD_HORIZONS_SECONDS:
            diagnostic_fields.extend(
                [
                    f"mean_forward_return_{horizon}s",
                    f"median_forward_return_{horizon}s",
                    f"positive_rate_forward_return_{horizon}s",
                    f"count_forward_return_{horizon}s",
                ]
            )
        write_csv_rows(QUANTILE_CSV, diagnostics, diagnostic_fields)
        forward_availability = {
            f"forward_return_{horizon}s": sum(
                1 for row in all_feature_rows if numeric_value(row.get(f"forward_return_{horizon}s")) is not None
            )
            for horizon in FORWARD_HORIZONS_SECONDS
        }
        derived_features = [
            "mid_price_proxy_pct1",
            "spread_proxy_pct1",
            "spread_bps_proxy_pct1",
            "bid_depth_pct_1",
            "ask_depth_pct_1",
            "bid_depth_pct_5",
            "ask_depth_pct_5",
            "imbalance_1",
            "imbalance_5",
            "microprice_proxy_pct1",
            "total_depth_pct1_change",
            "total_depth_pct5_change",
            "liquidity_pull_proxy_pct1",
            "liquidity_pull_proxy_pct5",
            "rolling_imbalance_1_mean_20",
            "rolling_spread_bps_mean_20",
            "rolling_mid_return_vol_proxy_20",
        ]
        derived_features = [feature for feature in derived_features if feature in feature_columns]
        stability_warnings = []
        if len(all_feature_rows) < 500:
            stability_warnings.append("pilot_sample_small_for_stable_distributional_inference")
        if any(value == 0 for value in forward_availability.values()):
            stability_warnings.append("one_or_more_forward_horizons_unavailable")
        summary: dict[str, Any] = {
            "status": "PASS_ORDERBOOK_UM_PILOT_FEATURE_PREVIEW_CREATED",
            "created_at_utc": utc_now_text(),
            "task_name": "ORDERBOOK_UM_PILOT_FEATURE_PREVIEW_V1",
            "data_root": str(data_root()),
            "pilot_zip_directory": str(base_pilot_dir),
            "pilot_zips_found": len(downloads),
            "pilot_zips_parsed": len(file_summaries),
            "symbols_parsed": sorted({item["symbol"] for item in file_summaries}),
            "rows_parsed_per_symbol_day": {
                f"{item['symbol']}|{item['file_date_or_month']}": item["feature_rows"] for item in file_summaries
            },
            "detected_schema_columns": {
                f"{item['symbol']}|{item['file_date_or_month']}": item["detected_schema_columns"] for item in file_summaries
            },
            "derived_feature_list": derived_features,
            "unsupported_feature_list": unsupported_features(),
            "timestamp_range_per_pilot_file": {
                f"{item['symbol']}|{item['file_date_or_month']}": {
                    "min": item["timestamp_min"],
                    "max": item["timestamp_max"],
                }
                for item in file_summaries
            },
            "duplicate_timestamp_count": sum(item["duplicate_timestamp_count"] for item in file_summaries),
            "duplicate_timestamp_bucket_count": sum(item["duplicate_timestamp_bucket_count"] for item in file_summaries),
            "missing_timestamp_or_malformed_row_count": sum(
                item["missing_timestamp_or_malformed_row_count"] for item in file_summaries
            ),
            "forward_diagnostic_availability": forward_availability,
            "feature_group_availability": {
                "mid_proxy": "mid_price_proxy_pct1" in feature_columns,
                "spread_proxy": "spread_bps_proxy_pct1" in feature_columns,
                "imbalance": any(column in feature_columns for column in ["imbalance_1", "imbalance_5"]),
            },
            "pilot_file_summaries": file_summaries,
            "quantile_diagnostic_row_count": len(diagnostics),
            "sample_feature_row_count": len(sample_rows),
            "parquet_written": parquet_written,
            "parquet_error": parquet_error,
            "output_files": {
                "summary_json": str(SUMMARY_JSON),
                "summary_md": str(SUMMARY_MD),
                "quantile_diagnostics_csv": str(QUANTILE_CSV),
                "quality_report_md": str(QUALITY_MD),
                "feature_sample_csv": str(FEATURE_SAMPLE_CSV),
                "feature_sample_parquet": str(FEATURE_SAMPLE_PARQUET) if parquet_written else "",
            },
            "suitable_for_next_step": "PILOT_DEPTH_FEATURE_DIAGNOSTICS_ONLY_NOT_FOR_TRADING_USE",
            "next_recommended_step": "B_ADD_AGGTRADES_PILOT_DATA_FOR_ABSORPTION_DIAGNOSTICS",
            "full_historical_download_attempted": False,
            "raw_zip_extraction_inside_repo": False,
            "replacement_checks_all_true": True,
        }
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_text(SUMMARY_MD, summary_markdown(summary))
        write_text(QUALITY_MD, quality_markdown(summary))
        print(f"status: {summary['status']}")
        print(f"pilot_zips_parsed: {summary['pilot_zips_parsed']}")
        print(f"symbols_parsed: {','.join(summary['symbols_parsed'])}")
        print(f"derived_features: {','.join(summary['derived_feature_list'])}")
        print(f"summary_json: {SUMMARY_JSON}")
        print(f"quantile_diagnostics_csv: {QUANTILE_CSV}")
        print(f"feature_sample_csv: {FEATURE_SAMPLE_CSV}")
        print(f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}")
        print(f"next_recommended_step: {summary['next_recommended_step']}")
        return 0
    except PreviewBlocked as exc:
        write_blocked(str(exc))
        print(f"BLOCKED: {exc}")
        print("status: BLOCKED_UNSUPPORTED_BOOKDEPTH_SCHEMA")
        print("replacement_checks_all_true=false")
        print("next_module=ORDERBOOK_UM_PILOT_FEATURE_BLOCKER_REVIEW")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
