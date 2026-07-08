#!/usr/bin/env python
"""Build a disk-safe 81-symbol bookDepth plus aggTrades absorption research dataset."""

from __future__ import annotations

import bisect
import csv
import hashlib
import io
import json
import os
import shutil
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

BOOKDEPTH_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_download_summary.json"
AGGTRADES_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_download_summary.json"
AGGTRADES_VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_download_validator_report.json"
BOOKDEPTH_COVERAGE_CSV = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_symbol_coverage.csv"
AGGTRADES_COVERAGE_CSV = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_symbol_coverage.csv"
BOOKDEPTH_FILE_STATUS_CSV = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_file_status.csv"
AGGTRADES_FILE_STATUS_CSV = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_file_status.csv"

BUILD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_build_summary.json"
BUILD_SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_build_summary.md"
PARTITION_MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_81_full_absorption_dataset_partition_manifest.csv"

DEFAULT_BOOKDEPTH_RAW_ROOT = Path(r"C:\edge_factory_external_data\binance_um_81_full_bookdepth_raw")
DEFAULT_AGGTRADES_RAW_ROOT = Path(r"C:\edge_factory_external_data\binance_um_81_full_matching_aggtrades_raw")
DEFAULT_OUTPUT_ROOT = Path(r"C:\edge_factory_external_data\binance_um_81_full_absorption_dataset_v1")

OUTPUT_ROOT_ENV = "ABSORPTION_DATASET_OUTPUT_ROOT"
FULL_BUILD_ENV = "ORDERBOOK_81_FULL_ABSORPTION_BUILD"
LEAN_MODE_ENV = "ORDERBOOK_81_FULL_ABSORPTION_LEAN_MODE"
SMOKE_LIMIT_ENV = "ABSORPTION_DATASET_SMOKE_PARTITIONS"
ESTIMATE_SAMPLE_ENV = "ABSORPTION_DATASET_ESTIMATE_SAMPLE_DAYS"

EXPECTED_SYMBOL_COUNT = 81
EXPECTED_MATCHING_FILE_COUNT = 99404
PROGRESS_INTERVAL_SECONDS = 30
ROLLING_WINDOW_ROWS = 12
STANDARD_COMPRESSED_BYTES_PER_ROW = 350
LEAN_COMPRESSED_BYTES_PER_ROW = 100
DISK_FREE_MULTIPLIER = 1.25

BUCKETS = [1, 2, 3, 4, 5]
STANDARD_OUTPUT_MODE = "standard"
LEAN_OUTPUT_MODE = "lean"
BASE_SCHEMA = [
    "timestamp",
    "symbol",
    "file_date",
    "year_month",
    "bid_depth_pct_1",
    "bid_depth_pct_2",
    "bid_depth_pct_3",
    "bid_depth_pct_4",
    "bid_depth_pct_5",
    "ask_depth_pct_1",
    "ask_depth_pct_2",
    "ask_depth_pct_3",
    "ask_depth_pct_4",
    "ask_depth_pct_5",
    "bid_notional_pct_1",
    "bid_notional_pct_2",
    "bid_notional_pct_3",
    "bid_notional_pct_4",
    "bid_notional_pct_5",
    "ask_notional_pct_1",
    "ask_notional_pct_2",
    "ask_notional_pct_3",
    "ask_notional_pct_4",
    "ask_notional_pct_5",
    "bid_depth_total_proxy",
    "ask_depth_total_proxy",
    "bid_notional_total_proxy",
    "ask_notional_total_proxy",
    "depth_imbalance_proxy",
    "spread_proxy",
    "mid_proxy",
    "microprice_proxy",
    "aggressive_buy_quantity",
    "aggressive_buy_notional",
    "aggressive_sell_quantity",
    "aggressive_sell_notional",
    "trade_count",
    "total_quantity",
    "total_notional",
    "buy_sell_flow_imbalance",
    "rolling_flow_pressure",
    "rolling_depth_imbalance",
    "flow_depth_divergence_proxy",
    "absorption_category",
]
LEAN_SCHEMA = [
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
    "spread_proxy",
    "microprice_proxy",
    "data_quality_flags",
]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def output_root() -> Path:
    return Path(os.environ.get(OUTPUT_ROOT_ENV, str(DEFAULT_OUTPUT_ROOT))).expanduser()


def selected_output_mode() -> str:
    return LEAN_OUTPUT_MODE if os.environ.get(LEAN_MODE_ENV, "").strip().upper() == "YES" else STANDARD_OUTPUT_MODE


def schema_for_mode(output_mode: str) -> list[str]:
    return LEAN_SCHEMA if output_mode == LEAN_OUTPUT_MODE else BASE_SCHEMA


def schema_hash_for_mode(output_mode: str) -> str:
    return hashlib.sha256(",".join(schema_for_mode(output_mode)).encode("utf-8")).hexdigest()


def partitions_root_for_mode(root: Path, output_mode: str) -> Path:
    return root / ("lean_partitions" if output_mode == LEAN_OUTPUT_MODE else "partitions")


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"not a JSON object: {path}")
    return payload


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def bool_value(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def safe_div(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def existing_parent(path: Path) -> Path:
    current = path
    while not current.exists() and current.parent != current:
        current = current.parent
    return current


def free_disk_bytes(path: Path) -> int:
    probe = existing_parent(path)
    return int(shutil.disk_usage(str(probe)).free)


def parquet_modules() -> tuple[Any | None, Any | None, str]:
    try:
        import pyarrow as pa  # type: ignore[import-not-found]
        import pyarrow.parquet as pq  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001
        return None, None, f"{type(exc).__name__}: {exc}"
    return pa, pq, ""


def assert_output_root_safe(root: Path) -> None:
    if path_is_inside(root, REPO_ROOT):
        raise ValueError(f"output root resolves inside repo: {root}")


def verified_file_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_csv_rows(path):
        if bool_value(row.get("checksum_verified")) and Path(row.get("local_zip_path", "")).exists():
            rows.append(row)
    return rows


def pair_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("symbol", ""), row.get("file_date", "")


def build_input_pairs() -> list[dict[str, Any]]:
    book_rows = {pair_key(row): row for row in verified_file_rows(BOOKDEPTH_FILE_STATUS_CSV)}
    agg_rows = {pair_key(row): row for row in verified_file_rows(AGGTRADES_FILE_STATUS_CSV)}
    pairs: list[dict[str, Any]] = []
    output_mode = selected_output_mode()
    suffix = "absorption-lean.parquet" if output_mode == LEAN_OUTPUT_MODE else "absorption.parquet"
    partition_root = partitions_root_for_mode(output_root(), output_mode)
    for symbol, file_date in sorted(set(book_rows) & set(agg_rows)):
        year_month = file_date[:7]
        partition = (
            partition_root
            / f"symbol={symbol}"
            / f"year_month={year_month}"
            / f"{symbol}-{file_date}-{suffix}"
        )
        pairs.append(
            {
                "symbol": symbol,
                "file_date": file_date,
                "year_month": year_month,
                "output_mode": output_mode,
                "bookdepth_zip_path": book_rows[(symbol, file_date)]["local_zip_path"],
                "aggtrades_zip_path": agg_rows[(symbol, file_date)]["local_zip_path"],
                "bookdepth_size_bytes": int_value(book_rows[(symbol, file_date)].get("observed_size_bytes")),
                "aggtrades_size_bytes": int_value(agg_rows[(symbol, file_date)].get("observed_size_bytes")),
                "partition_path": str(partition),
                "sidecar_path": str(partition.with_suffix(".parquet.json")),
            }
        )
    return pairs


def iter_zip_csv_rows(zip_path: Path) -> Iterable[dict[str, str]]:
    with zipfile.ZipFile(zip_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"expected exactly one CSV in {zip_path}, found {len(csv_names)}")
        with archive.open(csv_names[0], "r") as raw_handle:
            text_handle = io.TextIOWrapper(raw_handle, encoding="utf-8", newline="")
            yield from csv.DictReader(text_handle)


def parse_book_timestamp(value: str) -> tuple[int, str]:
    parsed = datetime.fromisoformat(value.replace(" ", "T")).replace(tzinfo=timezone.utc)
    timestamp_ms = int(parsed.timestamp() * 1000)
    return timestamp_ms, parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def empty_feature_row(symbol: str, file_date: str, year_month: str, timestamp: str) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for column in BASE_SCHEMA:
        if column in {"timestamp", "symbol", "file_date", "year_month"}:
            continue
        if column == "absorption_category":
            row[column] = "INSUFFICIENT_DATA"
        elif column in {
            "depth_imbalance_proxy",
            "spread_proxy",
            "mid_proxy",
            "microprice_proxy",
            "buy_sell_flow_imbalance",
            "rolling_flow_pressure",
            "rolling_depth_imbalance",
            "flow_depth_divergence_proxy",
        }:
            row[column] = None
        elif column == "trade_count":
            row[column] = 0
        else:
            row[column] = 0.0
    row["timestamp"] = timestamp
    row["symbol"] = symbol
    row["file_date"] = file_date
    row["year_month"] = year_month
    return {column: row[column] for column in BASE_SCHEMA}


def read_bookdepth_features(pair: dict[str, Any]) -> tuple[list[int], list[dict[str, Any]]]:
    by_timestamp: dict[int, dict[str, Any]] = {}
    symbol = str(pair["symbol"])
    file_date = str(pair["file_date"])
    year_month = str(pair["year_month"])
    for item in iter_zip_csv_rows(Path(str(pair["bookdepth_zip_path"]))):
        timestamp_ms, timestamp_text = parse_book_timestamp(str(item.get("timestamp", "")))
        feature_row = by_timestamp.setdefault(
            timestamp_ms,
            empty_feature_row(symbol, file_date, year_month, timestamp_text),
        )
        percentage = int(float_value(item.get("percentage")))
        bucket = abs(percentage)
        if bucket not in BUCKETS:
            continue
        side = "bid" if percentage < 0 else "ask" if percentage > 0 else ""
        if not side:
            continue
        feature_row[f"{side}_depth_pct_{bucket}"] += float_value(item.get("depth"))
        feature_row[f"{side}_notional_pct_{bucket}"] += float_value(item.get("notional"))

    timestamps = sorted(by_timestamp)
    rows = [by_timestamp[timestamp_ms] for timestamp_ms in timestamps]
    for row in rows:
        row["bid_depth_total_proxy"] = sum(float(row[f"bid_depth_pct_{bucket}"]) for bucket in BUCKETS)
        row["ask_depth_total_proxy"] = sum(float(row[f"ask_depth_pct_{bucket}"]) for bucket in BUCKETS)
        row["bid_notional_total_proxy"] = sum(float(row[f"bid_notional_pct_{bucket}"]) for bucket in BUCKETS)
        row["ask_notional_total_proxy"] = sum(float(row[f"ask_notional_pct_{bucket}"]) for bucket in BUCKETS)
        total_notional = row["bid_notional_total_proxy"] + row["ask_notional_total_proxy"]
        row["depth_imbalance_proxy"] = safe_div(
            row["bid_notional_total_proxy"] - row["ask_notional_total_proxy"],
            total_notional,
        )
    return timestamps, rows


def add_trade_flow(pair: dict[str, Any], timestamps: list[int], rows: list[dict[str, Any]]) -> None:
    if not timestamps:
        return
    for item in iter_zip_csv_rows(Path(str(pair["aggtrades_zip_path"]))):
        transact_ms = int_value(item.get("transact_time"), -1)
        row_index = bisect.bisect_right(timestamps, transact_ms) - 1
        if row_index < 0:
            continue
        row = rows[row_index]
        price = float_value(item.get("price"))
        quantity = float_value(item.get("quantity"))
        notional = price * quantity
        row["trade_count"] += 1
        row["total_quantity"] += quantity
        row["total_notional"] += notional
        if bool_value(item.get("is_buyer_maker")):
            row["aggressive_sell_quantity"] += quantity
            row["aggressive_sell_notional"] += notional
        else:
            row["aggressive_buy_quantity"] += quantity
            row["aggressive_buy_notional"] += notional


def add_rolling_features(rows: list[dict[str, Any]]) -> None:
    for index, row in enumerate(rows):
        flow_difference = row["aggressive_buy_notional"] - row["aggressive_sell_notional"]
        row["buy_sell_flow_imbalance"] = safe_div(flow_difference, row["total_notional"])
        start = max(0, index - ROLLING_WINDOW_ROWS + 1)
        window = rows[start : index + 1]
        buy_notional = sum(float(item["aggressive_buy_notional"]) for item in window)
        sell_notional = sum(float(item["aggressive_sell_notional"]) for item in window)
        total_notional = buy_notional + sell_notional
        depth_values = [
            item["depth_imbalance_proxy"]
            for item in window
            if item.get("depth_imbalance_proxy") is not None
        ]
        row["rolling_flow_pressure"] = safe_div(buy_notional - sell_notional, total_notional)
        row["rolling_depth_imbalance"] = (
            sum(float(value) for value in depth_values) / len(depth_values) if depth_values else None
        )
        if row["rolling_flow_pressure"] is None or row["rolling_depth_imbalance"] is None:
            row["flow_depth_divergence_proxy"] = None
        else:
            row["flow_depth_divergence_proxy"] = row["rolling_flow_pressure"] - row["rolling_depth_imbalance"]
        row["absorption_category"] = absorption_category(row)


def absorption_category(row: dict[str, Any]) -> str:
    flow = row.get("rolling_flow_pressure")
    depth = row.get("rolling_depth_imbalance")
    if flow is None or depth is None:
        return "INSUFFICIENT_DATA"
    flow_value = float(flow)
    depth_value = float(depth)
    threshold = 0.15
    if abs(flow_value) < 0.05 and abs(depth_value) < 0.05:
        return "MIXED_OR_NOISY"
    if flow_value >= threshold and depth_value <= -threshold:
        return "BUY_PRESSURE_ABSORBED"
    if flow_value <= -threshold and depth_value >= threshold:
        return "SELL_PRESSURE_ABSORBED"
    if flow_value >= threshold and depth_value >= threshold:
        return "FLOW_AND_DEPTH_ALIGNED_UP"
    if flow_value <= -threshold and depth_value <= -threshold:
        return "FLOW_AND_DEPTH_ALIGNED_DOWN"
    return "MIXED_OR_NOISY"


def build_feature_rows(pair: dict[str, Any]) -> list[dict[str, Any]]:
    timestamps, rows = read_bookdepth_features(pair)
    add_trade_flow(pair, timestamps, rows)
    add_rolling_features(rows)
    return rows


def data_quality_flags(row: dict[str, Any]) -> str:
    flags: list[str] = ["DEPTH_OK"]
    if int_value(row.get("trade_count")) == 0:
        flags.append("NO_TRADE_FLOW")
    if row.get("spread_proxy") is None:
        flags.append("SPREAD_UNAVAILABLE")
    if row.get("microprice_proxy") is None:
        flags.append("MICROPRICE_UNAVAILABLE")
    if row.get("depth_imbalance_proxy") is None:
        flags.append("DEPTH_IMBALANCE_UNAVAILABLE")
    return "|".join(flags)


def lean_feature_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": row.get("timestamp"),
        "symbol": row.get("symbol"),
        "file_date": row.get("file_date"),
        "year_month": row.get("year_month"),
        "absorption_category": row.get("absorption_category"),
        "trade_count": int_value(row.get("trade_count")),
        "total_qty": float_value(row.get("total_quantity")),
        "total_notional": float_value(row.get("total_notional")),
        "aggressive_buy_qty": float_value(row.get("aggressive_buy_quantity")),
        "aggressive_sell_qty": float_value(row.get("aggressive_sell_quantity")),
        "aggressive_buy_notional": float_value(row.get("aggressive_buy_notional")),
        "aggressive_sell_notional": float_value(row.get("aggressive_sell_notional")),
        "flow_imbalance": row.get("buy_sell_flow_imbalance"),
        "rolling_flow_pressure": row.get("rolling_flow_pressure"),
        "depth_imbalance_proxy": row.get("depth_imbalance_proxy"),
        "rolling_depth_imbalance_proxy": row.get("rolling_depth_imbalance"),
        "flow_depth_divergence_proxy": row.get("flow_depth_divergence_proxy"),
        "spread_proxy": row.get("spread_proxy"),
        "microprice_proxy": row.get("microprice_proxy"),
        "data_quality_flags": data_quality_flags(row),
    }


def rows_for_output_mode(rows: list[dict[str, Any]], output_mode: str) -> list[dict[str, Any]]:
    if output_mode == LEAN_OUTPUT_MODE:
        return [lean_feature_row(row) for row in rows]
    return rows


def row_schema_hash(rows: list[dict[str, Any]], output_mode: str) -> str:
    return schema_hash_for_mode(output_mode)


def table_for_rows(pa: Any, rows: list[dict[str, Any]], output_mode: str) -> Any:
    if output_mode != LEAN_OUTPUT_MODE:
        return pa.Table.from_pylist(rows)
    columns = {
        "timestamp": pa.array([row["timestamp"] for row in rows], type=pa.string()),
        "symbol": pa.array([row["symbol"] for row in rows], type=pa.dictionary(pa.int32(), pa.string())),
        "file_date": pa.array([row["file_date"] for row in rows], type=pa.string()),
        "year_month": pa.array([row["year_month"] for row in rows], type=pa.dictionary(pa.int32(), pa.string())),
        "absorption_category": pa.array(
            [row["absorption_category"] for row in rows],
            type=pa.dictionary(pa.int32(), pa.string()),
        ),
        "trade_count": pa.array([row["trade_count"] for row in rows], type=pa.uint32()),
        "total_qty": pa.array([row["total_qty"] for row in rows], type=pa.float32()),
        "total_notional": pa.array([row["total_notional"] for row in rows], type=pa.float32()),
        "aggressive_buy_qty": pa.array([row["aggressive_buy_qty"] for row in rows], type=pa.float32()),
        "aggressive_sell_qty": pa.array([row["aggressive_sell_qty"] for row in rows], type=pa.float32()),
        "aggressive_buy_notional": pa.array([row["aggressive_buy_notional"] for row in rows], type=pa.float32()),
        "aggressive_sell_notional": pa.array([row["aggressive_sell_notional"] for row in rows], type=pa.float32()),
        "flow_imbalance": pa.array([row["flow_imbalance"] for row in rows], type=pa.float32()),
        "rolling_flow_pressure": pa.array([row["rolling_flow_pressure"] for row in rows], type=pa.float32()),
        "depth_imbalance_proxy": pa.array([row["depth_imbalance_proxy"] for row in rows], type=pa.float32()),
        "rolling_depth_imbalance_proxy": pa.array(
            [row["rolling_depth_imbalance_proxy"] for row in rows],
            type=pa.float32(),
        ),
        "flow_depth_divergence_proxy": pa.array(
            [row["flow_depth_divergence_proxy"] for row in rows],
            type=pa.float32(),
        ),
        "spread_proxy": pa.array([row["spread_proxy"] for row in rows], type=pa.float32()),
        "microprice_proxy": pa.array([row["microprice_proxy"] for row in rows], type=pa.float32()),
        "data_quality_flags": pa.array(
            [row["data_quality_flags"] for row in rows],
            type=pa.dictionary(pa.int32(), pa.string()),
        ),
    }
    return pa.table({column: columns[column] for column in LEAN_SCHEMA})


def category_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(row.get("absorption_category", "")) for row in rows))


def duplicate_symbol_timestamp_count(rows: list[dict[str, Any]]) -> int:
    seen: set[tuple[str, str]] = set()
    duplicate_count = 0
    for row in rows:
        key = str(row.get("symbol", "")), str(row.get("timestamp", ""))
        if key in seen:
            duplicate_count += 1
        seen.add(key)
    return duplicate_count


def sidecar_is_valid(partition_path: Path, sidecar_path: Path, output_mode: str) -> bool:
    if not partition_path.exists() or not sidecar_path.exists():
        return False
    try:
        sidecar = load_json(sidecar_path)
    except Exception:
        return False
    return (
        int_value(sidecar.get("row_count")) > 0
        and sidecar.get("sha256") == sha256_file(partition_path)
        and sidecar.get("output_mode", STANDARD_OUTPUT_MODE) == output_mode
        and sidecar.get("schema_hash") == schema_hash_for_mode(output_mode)
    )


def write_parquet_partition(
    rows: list[dict[str, Any]],
    partition_path: Path,
    sidecar_path: Path,
    output_mode: str,
) -> dict[str, Any]:
    pa, pq, engine_error = parquet_modules()
    if pa is None or pq is None:
        raise RuntimeError(f"parquet engine unavailable: {engine_error}")
    output_rows = rows_for_output_mode(rows, output_mode)
    partition_path.parent.mkdir(parents=True, exist_ok=True)
    table = table_for_rows(pa, output_rows, output_mode)
    tmp_path = partition_path.with_suffix(".tmp.parquet")
    compression = "zstd"
    try:
        pq.write_table(table, tmp_path, compression="zstd")
    except Exception:
        compression = "snappy"
        pq.write_table(table, tmp_path, compression="snappy")
    tmp_path.replace(partition_path)
    partition_size_bytes = partition_path.stat().st_size
    digest = sha256_file(partition_path)
    duplicate_count = duplicate_symbol_timestamp_count(output_rows)
    metadata = {
        "created_at_utc": utc_now_text(),
        "path": str(partition_path),
        "output_mode": output_mode,
        "row_count": len(output_rows),
        "schema": schema_for_mode(output_mode),
        "schema_column_count": len(schema_for_mode(output_mode)),
        "schema_hash": row_schema_hash(output_rows, output_mode),
        "sha256": digest,
        "compression": compression,
        "parquet_size_bytes": partition_size_bytes,
        "parquet_size_mb": round(partition_size_bytes / 1_000_000, 6),
        "duplicate_symbol_timestamp_count": duplicate_count,
        "absorption_category_counts": category_counts(output_rows),
    }
    sidecar_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metadata


def estimate_from_samples(pairs: list[dict[str, Any]], sample_limit: int) -> dict[str, Any]:
    if sample_limit <= 0:
        sample_limit = 1
    if len(pairs) <= sample_limit:
        selected_pairs = pairs
    elif sample_limit == 1:
        selected_pairs = [pairs[len(pairs) // 2]]
    else:
        selected_pairs = [
            pairs[round(index * (len(pairs) - 1) / (sample_limit - 1))]
            for index in range(sample_limit)
        ]
    sampled: list[dict[str, Any]] = []
    for pair in selected_pairs:
        try:
            timestamps, rows = read_bookdepth_features(pair)
        except Exception as exc:  # noqa: BLE001
            sampled.append(
                {
                    "symbol": pair["symbol"],
                    "file_date": pair["file_date"],
                    "row_count": 0,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        sampled.append(
            {
                "symbol": pair["symbol"],
                "file_date": pair["file_date"],
                "row_count": len(rows),
                "bookdepth_timestamp_count": len(timestamps),
            }
        )
    positive_counts = [int(item["row_count"]) for item in sampled if int(item.get("row_count") or 0) > 0]
    average_rows = sum(positive_counts) / len(positive_counts) if positive_counts else 288.0
    estimated_rows = int(round(average_rows * len(pairs)))
    return {
        "sample_limit": sample_limit,
        "sampled_pairs": sampled,
        "average_rows_per_pair": average_rows,
        "estimated_output_rows": estimated_rows,
    }


def estimate_parquet_size_gb(
    estimated_rows: int,
    book_summary: dict[str, Any],
    agg_summary: dict[str, Any],
    compressed_bytes_per_row: int,
    minimum_input_fraction: float,
) -> float:
    row_based_bytes = estimated_rows * compressed_bytes_per_row
    input_bytes = int_value(book_summary.get("total_verified_bytes")) + int_value(agg_summary.get("total_verified_bytes"))
    conservative_bytes = max(row_based_bytes, int(input_bytes * minimum_input_fraction))
    return round(conservative_bytes / 1_000_000_000, 6)


def readiness_checks(book_summary: dict[str, Any], agg_summary: dict[str, Any], agg_validator: dict[str, Any]) -> dict[str, bool]:
    book_expected = int_value(book_summary.get("expected_file_count"))
    agg_expected = int_value(agg_summary.get("expected_file_count"))
    return {
        "bookdepth_summary_passed": book_summary.get("status") == "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED",
        "aggtrades_summary_passed": agg_summary.get("status") == "PASS_81_FULL_MATCHING_AGGTRADES_DOWNLOAD_VERIFIED",
        "aggtrades_validator_passed": agg_validator.get("status")
        == "PASS_ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_DOWNLOAD_VALIDATED",
        "bookdepth_expected_file_count": book_expected == EXPECTED_MATCHING_FILE_COUNT,
        "aggtrades_expected_file_count": agg_expected == EXPECTED_MATCHING_FILE_COUNT,
        "bookdepth_checksums_complete": int_value(book_summary.get("checksum_verified_count")) == book_expected
        and int_value(book_summary.get("checksum_missing_count")) == 0
        and int_value(book_summary.get("failed_count")) == 0,
        "aggtrades_checksums_complete": int_value(agg_summary.get("checksum_verified_count")) == agg_expected
        and int_value(agg_summary.get("checksum_missing_count")) == 0
        and int_value(agg_summary.get("failed_count")) == 0,
        "coverage_files_exist": BOOKDEPTH_COVERAGE_CSV.exists() and AGGTRADES_COVERAGE_CSV.exists(),
        "file_status_files_exist": BOOKDEPTH_FILE_STATUS_CSV.exists() and AGGTRADES_FILE_STATUS_CSV.exists(),
        "bookdepth_raw_root_outside_repo": not path_is_inside(DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT),
        "aggtrades_raw_root_outside_repo": not path_is_inside(DEFAULT_AGGTRADES_RAW_ROOT, REPO_ROOT),
    }


def manifest_row(pair: dict[str, Any], status: str, row_count: int = 0, error_message: str = "") -> dict[str, Any]:
    return {
        "symbol": pair["symbol"],
        "file_date": pair["file_date"],
        "year_month": pair["year_month"],
        "output_mode": pair.get("output_mode", selected_output_mode()),
        "bookdepth_zip_path": pair["bookdepth_zip_path"],
        "aggtrades_zip_path": pair["aggtrades_zip_path"],
        "partition_path": pair["partition_path"],
        "sidecar_path": pair["sidecar_path"],
        "partition_exists": Path(str(pair["partition_path"])).exists(),
        "row_count": row_count,
        "status": status,
        "error_message": error_message,
    }


def write_partition_manifest(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "symbol",
        "file_date",
        "year_month",
        "output_mode",
        "bookdepth_zip_path",
        "aggtrades_zip_path",
        "partition_path",
        "sidecar_path",
        "partition_exists",
        "row_count",
        "status",
        "error_message",
    ]
    with PARTITION_MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_pairs(
    pairs: list[dict[str, Any]],
    full_build: bool,
    parquet_engine_available: bool,
    output_mode: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest_rows: list[dict[str, Any]] = []
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    row_count_total = 0
    parquet_size_bytes_total = 0
    category_total: Counter[str] = Counter()
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS
    limit = len(pairs) if full_build else max(0, int_value(os.environ.get(SMOKE_LIMIT_ENV), 1))

    if not parquet_engine_available:
        for index, pair in enumerate(pairs):
            status = "SMOKE_SKIPPED_PARQUET_ENGINE_MISSING" if index < max(limit, 1) else "PLANNED_FULL_BUILD"
            manifest_rows.append(manifest_row(pair, status))
        return manifest_rows, {
            "processed_partition_count": 0,
            "skipped_verified_partition_count": 0,
            "failed_partition_count": 0,
            "row_count_total": 0,
            "parquet_size_bytes_total": 0,
            "parquet_size_mb_total": 0.0,
            "absorption_category_counts": {},
            "smoke_result": "not_created_parquet_engine_missing",
        }

    for index, pair in enumerate(pairs):
        if index >= limit:
            manifest_rows.append(manifest_row(pair, "PLANNED_FULL_BUILD"))
            continue
        partition_path = Path(str(pair["partition_path"]))
        sidecar_path = Path(str(pair["sidecar_path"]))
        if sidecar_is_valid(partition_path, sidecar_path, output_mode):
            sidecar = load_json(sidecar_path)
            row_count = int_value(sidecar.get("row_count"))
            skipped_count += 1
            row_count_total += row_count
            parquet_size_bytes_total += int_value(sidecar.get("parquet_size_bytes"))
            category_total.update(sidecar.get("absorption_category_counts", {}))
            manifest_rows.append(manifest_row(pair, "SKIPPED_VERIFIED_PARTITION", row_count))
        else:
            try:
                rows = build_feature_rows(pair)
                metadata = write_parquet_partition(rows, partition_path, sidecar_path, output_mode)
                processed_count += 1
                row_count_total += int(metadata["row_count"])
                parquet_size_bytes_total += int(metadata.get("parquet_size_bytes", 0))
                category_total.update(metadata.get("absorption_category_counts", {}))
                manifest_rows.append(manifest_row(pair, "WRITTEN_VERIFIED_PARTITION", int(metadata["row_count"])))
            except Exception as exc:  # noqa: BLE001
                failed_count += 1
                manifest_rows.append(manifest_row(pair, "FAILED_PARTITION", 0, f"{type(exc).__name__}: {exc}"))
        if time.monotonic() >= next_progress:
            print(
                "progress "
                f"processed={processed_count} skipped={skipped_count} failed={failed_count} "
                f"planned_index={index + 1}/{len(pairs)} rows={row_count_total}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    smoke_result = "created" if processed_count + skipped_count > 0 and not full_build else "not_applicable"
    return manifest_rows, {
        "processed_partition_count": processed_count,
        "skipped_verified_partition_count": skipped_count,
        "failed_partition_count": failed_count,
        "row_count_total": row_count_total,
        "parquet_size_bytes_total": parquet_size_bytes_total,
        "parquet_size_mb_total": round(parquet_size_bytes_total / 1_000_000, 6),
        "absorption_category_counts": dict(category_total),
        "smoke_result": smoke_result,
    }


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 full absorption dataset builder v1",
        "",
        f"status: {summary['status']}",
        f"mode: {summary['mode']}",
        f"output_mode: {summary.get('output_mode', '')}",
        f"output_root: {summary['output_root']}",
        f"estimated_rows: {summary['estimated_rows']}",
        f"estimated_standard_parquet_gb: {summary.get('estimated_standard_parquet_gb', '')}",
        f"estimated_lean_parquet_gb: {summary.get('estimated_lean_parquet_gb', '')}",
        f"selected_estimated_parquet_gb: {summary['estimated_parquet_gb']}",
        f"free_disk_gb: {summary['free_disk_gb']}",
        f"required_free_disk_selected_mode_gb: {summary.get('required_free_disk_selected_mode_gb', '')}",
        f"actual_smoke_parquet_size_mb: {summary.get('actual_smoke_parquet_size_mb', '')}",
        f"schema_column_count: {summary.get('schema_column_count', '')}",
        f"smoke_result: {summary['smoke_result']}",
        f"full_build_requested: {str(summary['full_build_requested']).lower()}",
        f"lean_mode_requested: {str(summary.get('lean_mode_requested', False)).lower()}",
        f"parquet_engine_available: {str(summary['parquet_engine_available']).lower()}",
        f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}",
        "",
        "## Checks",
    ]
    for key, value in summary.get("readiness_checks", {}).items():
        lines.append(f"- {key}: {str(value).lower()}")
    if summary.get("exact_blocker"):
        lines.extend(["", f"exact_blocker: {summary['exact_blocker']}"])
    BUILD_SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_summary() -> dict[str, Any]:
    root = output_root()
    output_mode = selected_output_mode()
    assert_output_root_safe(root)
    root.mkdir(parents=True, exist_ok=True)

    book_summary = load_json(BOOKDEPTH_SUMMARY_JSON)
    agg_summary = load_json(AGGTRADES_SUMMARY_JSON)
    agg_validator = load_json(AGGTRADES_VALIDATOR_JSON)
    checks = readiness_checks(book_summary, agg_summary, agg_validator)
    pairs = build_input_pairs()
    symbols = sorted({str(pair["symbol"]) for pair in pairs})
    sample_limit = max(1, int_value(os.environ.get(ESTIMATE_SAMPLE_ENV), 10))
    estimate = estimate_from_samples(pairs, sample_limit)
    estimated_rows = int(estimate["estimated_output_rows"])
    estimated_standard_gb = estimate_parquet_size_gb(
        estimated_rows,
        book_summary,
        agg_summary,
        STANDARD_COMPRESSED_BYTES_PER_ROW,
        0.10,
    )
    estimated_lean_gb = estimate_parquet_size_gb(
        estimated_rows,
        book_summary,
        agg_summary,
        LEAN_COMPRESSED_BYTES_PER_ROW,
        0.03,
    )
    estimated_gb = estimated_lean_gb if output_mode == LEAN_OUTPUT_MODE else estimated_standard_gb
    free_bytes = free_disk_bytes(root)
    free_gb = round(free_bytes / 1_000_000_000, 6)
    required_free_gb = round(estimated_gb * DISK_FREE_MULTIPLIER, 6)
    pa, pq, engine_error = parquet_modules()
    parquet_engine_available = pa is not None and pq is not None
    full_build = os.environ.get(FULL_BUILD_ENV, "").strip().upper() == "YES"

    checks.update(
        {
            "input_pair_count_matches_expected": len(pairs) == EXPECTED_MATCHING_FILE_COUNT,
            "symbols_represented_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
            "output_root_outside_repo": not path_is_inside(root, REPO_ROOT),
            "free_disk_sufficient_for_estimate": free_gb >= required_free_gb,
        }
    )

    failed_checks = [key for key, value in checks.items() if not value]
    exact_blocker = ""
    if failed_checks:
        if failed_checks == ["free_disk_sufficient_for_estimate"]:
            exact_blocker = f"full build would require {required_free_gb} GB free; current free disk is {free_gb} GB"
        else:
            exact_blocker = "one or more readiness checks failed: " + ", ".join(failed_checks)
    elif full_build and not parquet_engine_available:
        exact_blocker = f"parquet engine unavailable: {engine_error}"
    elif full_build and free_gb < required_free_gb:
        exact_blocker = f"free disk {free_gb} GB is below required {required_free_gb} GB"

    if exact_blocker and full_build:
        manifest_rows = [manifest_row(pair, "BLOCKED_FULL_BUILD") for pair in pairs]
        process_summary = {
            "processed_partition_count": 0,
        "skipped_verified_partition_count": 0,
        "failed_partition_count": 0,
        "row_count_total": 0,
        "parquet_size_bytes_total": 0,
        "parquet_size_mb_total": 0.0,
        "absorption_category_counts": {},
        "smoke_result": "not_applicable",
    }
    elif exact_blocker and not parquet_engine_available:
        manifest_rows, process_summary = process_pairs(
            pairs,
            full_build=False,
            parquet_engine_available=False,
            output_mode=output_mode,
        )
    else:
        manifest_rows, process_summary = process_pairs(
            pairs,
            full_build=full_build,
            parquet_engine_available=parquet_engine_available,
            output_mode=output_mode,
        )

    write_partition_manifest(manifest_rows)
    successful_rows = [
        row
        for row in manifest_rows
        if row["status"] in {"WRITTEN_VERIFIED_PARTITION", "SKIPPED_VERIFIED_PARTITION"}
    ]
    if full_build:
        status = (
            "PASS_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_BUILT"
            if len(successful_rows) == len(pairs) and process_summary["failed_partition_count"] == 0 and not exact_blocker
            else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_BUILD"
        )
        mode = "FULL_BUILD"
    else:
        mode = "ESTIMATE_SMOKE"
        if parquet_engine_available and successful_rows:
            status = "PASS_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_SMOKE_BUILT"
        elif parquet_engine_available:
            status = "ESTIMATE_ONLY_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_NO_SMOKE_ROWS"
        else:
            status = "ESTIMATE_ONLY_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_PARQUET_ENGINE_MISSING"

    replacement_checks_all_true = (
        all(checks.values())
        and ((not full_build and (parquet_engine_available is False or bool(successful_rows))) or status.startswith("PASS_"))
    )

    summary = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "mode": mode,
        "output_mode": output_mode,
        "task_name": "ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_BUILDER_V1",
        "output_root": str(root),
        "partitions_root": str(partitions_root_for_mode(root, output_mode)),
        "full_build_requested": full_build,
        "full_build_env_var": FULL_BUILD_ENV,
        "lean_mode_requested": output_mode == LEAN_OUTPUT_MODE,
        "lean_mode_env_var": LEAN_MODE_ENV,
        "output_root_env_var": OUTPUT_ROOT_ENV,
        "parquet_engine_available": parquet_engine_available,
        "parquet_engine_error": engine_error,
        "expected_pair_count": EXPECTED_MATCHING_FILE_COUNT,
        "matched_pair_count": len(pairs),
        "symbol_count": len(symbols),
        "symbols": symbols,
        "coverage_start": "2023-01-01",
        "coverage_end": "2026-06-15",
        "estimated_rows": estimated_rows,
        "estimated_parquet_gb": estimated_gb,
        "estimated_standard_parquet_gb": estimated_standard_gb,
        "estimated_lean_parquet_gb": estimated_lean_gb,
        "free_disk_gb": free_gb,
        "required_free_gb": required_free_gb,
        "required_free_disk_selected_mode_gb": required_free_gb,
        "required_free_standard_gb": round(estimated_standard_gb * DISK_FREE_MULTIPLIER, 6),
        "required_free_lean_gb": round(estimated_lean_gb * DISK_FREE_MULTIPLIER, 6),
        "disk_free_multiplier": DISK_FREE_MULTIPLIER,
        "schema_column_count": len(schema_for_mode(output_mode)),
        "estimate": estimate,
        "processed_partition_count": process_summary["processed_partition_count"],
        "skipped_verified_partition_count": process_summary["skipped_verified_partition_count"],
        "failed_partition_count": process_summary["failed_partition_count"],
        "row_count_total": process_summary["row_count_total"],
        "actual_smoke_parquet_size_mb": process_summary["parquet_size_mb_total"] if not full_build else "",
        "smoke_result": process_summary["smoke_result"],
        "absorption_category_counts": process_summary["absorption_category_counts"],
        "partition_manifest_csv": str(PARTITION_MANIFEST_CSV),
        "readiness_checks": checks,
        "exact_blocker": exact_blocker,
        "replacement_checks_all_true": replacement_checks_all_true,
        "full_build_command": (
            "$env:ORDERBOOK_81_FULL_ABSORPTION_BUILD='YES'; "
            ".\\run_orderbook_um_81_full_absorption_dataset_builder_v1.ps1"
        ),
        "lean_full_build_command": (
            "$env:ORDERBOOK_81_FULL_ABSORPTION_LEAN_MODE='YES'; "
            "$env:ORDERBOOK_81_FULL_ABSORPTION_BUILD='YES'; "
            ".\\run_orderbook_um_81_full_absorption_dataset_builder_v1.ps1"
        ),
        "safety_scope": (
            "research dataset construction only; no trading recommendation, execution, account, or private endpoint logic"
        ),
        "next_module": "ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_VALIDATOR_V1",
    }
    BUILD_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    return summary


def main() -> int:
    try:
        summary = build_summary()
    except Exception as exc:  # noqa: BLE001
        summary = {
            "status": "BLOCKED_ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_BUILDER",
            "created_at_utc": utc_now_text(),
            "exact_blocker": f"{type(exc).__name__}: {exc}",
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_81_FULL_ABSORPTION_DATASET_BLOCKER_REVIEW",
        }
        BUILD_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_summary_md(summary)
    print(f"status: {summary['status']}")
    print(f"build_summary_json: {BUILD_SUMMARY_JSON}")
    print(f"build_summary_md: {BUILD_SUMMARY_MD}")
    print(f"partition_manifest_csv: {PARTITION_MANIFEST_CSV}")
    print(f"output_root: {summary.get('output_root', output_root())}")
    print(f"estimated_rows: {summary.get('estimated_rows', '')}")
    print(f"estimated_parquet_gb: {summary.get('estimated_parquet_gb', '')}")
    print(f"estimated_standard_parquet_gb: {summary.get('estimated_standard_parquet_gb', '')}")
    print(f"estimated_lean_parquet_gb: {summary.get('estimated_lean_parquet_gb', '')}")
    print(f"free_disk_gb: {summary.get('free_disk_gb', '')}")
    print(f"required_free_disk_selected_mode_gb: {summary.get('required_free_disk_selected_mode_gb', '')}")
    print(f"output_mode: {summary.get('output_mode', '')}")
    print(f"smoke_result: {summary.get('smoke_result', '')}")
    print(f"replacement_checks_all_true: {str(summary.get('replacement_checks_all_true', False)).lower()}")
    return 0 if not str(summary["status"]).startswith("BLOCKED_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
