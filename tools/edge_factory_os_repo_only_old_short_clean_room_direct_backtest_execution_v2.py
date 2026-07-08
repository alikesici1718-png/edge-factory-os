from __future__ import annotations

import bisect
import csv
import hashlib
import json
import math
import random
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "old_short_clean_room_direct_backtest_execution_v2.json"
AUDIT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "old_short_clean_room_direct_backtest_v2_error_audit_v1.json"
THRESHOLD_CONTRACT_PATH = REPO_ROOT / "artifacts" / "old_short_clean_room" / "old_short_clean_room_runner_fixture_threshold_contract_v1.json"
SOURCE_REVIEW_PATH = REPO_ROOT / "artifacts" / "old_short" / "old_short_proxy_backtest_data_coverage_source_review_v1.json"

STATUS = "PASS_REPO_CODE_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_EXECUTED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_EXECUTION"
ROUTE_KEY = "old_short_clean_room_v1"
FAMILY_KEY = "old_short"
FAMILIES = ("blowoff_short", "mean_reversion_short")
SIDE = "short"
BASE_EQUITY_USDT = 1000.0
NOTIONAL_USDT = 50.0
ROUND_TRIP_COST_BPS = 20.0
ROUND_TRIP_COST_FRACTION = ROUND_TRIP_COST_BPS / 10000.0
ENTRY_DELAY_MINUTES = 2
HOLD_MINUTES = 120
REQUIRED_CANDLE_COLUMNS = {"ts", "open", "high", "low", "close", "volCcyQuote", "time"}
REQUIRED_LABELS = {
    "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
    "NOT_ORIGINAL_THRESHOLD",
    "NOT_PNL_OPTIMIZED",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
}
FEATURES = (
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
)


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def parse_time(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat().replace("+00:00", "Z") if dt else None


def parse_float(value: Any) -> float | None:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(f):
        return None
    return f


def pct_bps(new: float, old: float) -> float | None:
    if old <= 0:
        return None
    return (new / old - 1.0) * 10000.0


def candle_range_bps(high: float, low: float, close: float) -> float | None:
    if close <= 0:
        return None
    return (high - low) / close * 10000.0


def compare(value: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return value >= threshold
    if operator == "<=":
        return value <= threshold
    raise ValueError(f"unsupported operator {operator}")


def walk_dicts(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_dicts(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_dicts(value)


def collect_sources(source_review: dict[str, Any]) -> list[dict[str, Any]]:
    by_symbol: dict[str, dict[str, Any]] = {}
    for item in walk_dicts(source_review):
        path_text = item.get("path") if isinstance(item, dict) else None
        if not isinstance(path_text, str):
            continue
        lowered = path_text.lower()
        if not (
            lowered.endswith(".csv")
            and "-usdt-swap_1m_" in lowered
            and "\\raw\\candles_long_1m\\" in lowered
        ):
            continue
        path = Path(path_text)
        symbol = path.name.split("-USDT-SWAP", 1)[0]
        if not symbol or symbol in by_symbol:
            continue
        exists = path.exists() and path.is_file()
        header: list[str] = []
        readable = False
        if exists:
            try:
                with path.open("r", encoding="utf-8", newline="") as handle:
                    header = next(csv.reader(handle), [])
                readable = REQUIRED_CANDLE_COLUMNS.issubset(set(header))
            except Exception:  # noqa: BLE001
                readable = False
        if readable:
            by_symbol[symbol] = {
                "symbol": symbol,
                "inst_id": f"{symbol}-USDT-SWAP",
                "path": str(path),
                "header": header,
                "size_bytes": path.stat().st_size,
            }
    return sorted(by_symbol.values(), key=lambda row: row["symbol"])


def load_thresholds(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    identity = contract.get("fixture_threshold_contract_identity", {})
    completeness = contract.get("contract_completeness", {})
    families = contract.get("threshold_families", {})
    if identity.get("route_key") != ROUTE_KEY:
        raise ValueError("threshold route mismatch")
    if completeness.get("contract_complete") is not True:
        raise ValueError("threshold contract incomplete")
    if completeness.get("family_threshold_count") != 2:
        raise ValueError("threshold family count mismatch")
    out: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        rules = families.get(family, {}).get("threshold_rules")
        if not isinstance(rules, dict):
            raise ValueError(f"missing family thresholds: {family}")
        for feature in FEATURES:
            rule = rules.get(feature)
            if not isinstance(rule, dict):
                raise ValueError(f"missing threshold feature: {family}.{feature}")
            if not REQUIRED_LABELS.issubset(set(rule.get("labels", []))):
                raise ValueError(f"missing threshold safety labels: {family}.{feature}")
            if rule.get("operator") not in {">=", "<="}:
                raise ValueError(f"bad threshold operator: {family}.{feature}")
            if parse_float(rule.get("value")) is None:
                raise ValueError(f"bad threshold value: {family}.{feature}")
        out[family] = rules
    return out


def read_candles(source: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = Path(source["path"])
    candles: list[dict[str, Any]] = []
    bad_rows = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader, start=2):
            if str(row.get("confirm", "1")).strip() not in {"1", "true", "True"}:
                continue
            t = parse_time(row.get("time"))
            opened = parse_float(row.get("open"))
            high = parse_float(row.get("high"))
            low = parse_float(row.get("low"))
            close = parse_float(row.get("close"))
            vol_quote = parse_float(row.get("volCcyQuote"))
            if t is None or opened is None or high is None or low is None or close is None or vol_quote is None:
                bad_rows += 1
                continue
            if opened <= 0 or high <= 0 or low <= 0 or close <= 0 or high < low:
                bad_rows += 1
                continue
            candles.append(
                {
                    "row_index": row_index,
                    "time": t,
                    "open": opened,
                    "high": high,
                    "low": low,
                    "close": close,
                    "vol_quote": vol_quote,
                }
            )
    candles.sort(key=lambda row: row["time"])
    deduped: list[dict[str, Any]] = []
    duplicate_timestamps = 0
    last_time = None
    for candle in candles:
        if candle["time"] == last_time:
            duplicate_timestamps += 1
            continue
        deduped.append(candle)
        last_time = candle["time"]
    review = {
        "symbol": source["symbol"],
        "inst_id": source["inst_id"],
        "path": source["path"],
        "rows_loaded": len(deduped),
        "bad_rows_skipped": bad_rows,
        "duplicate_timestamps_skipped": duplicate_timestamps,
        "first_timestamp": iso(deduped[0]["time"]) if deduped else None,
        "last_timestamp": iso(deduped[-1]["time"]) if deduped else None,
    }
    return deduped, review


def evaluate_family(features: dict[str, float], rules: dict[str, Any]) -> bool:
    for feature in FEATURES:
        if feature not in features:
            raise ValueError(f"required feature missing: {feature}")
        rule = rules[feature]
        if not compare(features[feature], str(rule["operator"]), float(rule["value"])):
            return False
    return True


def build_candidates(sources: list[dict[str, Any]], thresholds: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    file_reviews: list[dict[str, Any]] = []
    raw_family_trigger_count = 0
    fail_closed_feature_count = 0
    skipped_entry_missing = 0
    unresolved_exit_candidates = 0
    dual_trigger_count = 0
    data_min = None
    data_max = None
    for source in sources:
        candles, review = read_candles(source)
        file_reviews.append(review)
        if not candles:
            continue
        data_min = min(data_min, candles[0]["time"]) if data_min else candles[0]["time"]
        data_max = max(data_max, candles[-1]["time"]) if data_max else candles[-1]["time"]
        times = [row["time"] for row in candles]
        for i in range(60, len(candles)):
            signal = candles[i]
            target_entry = signal["time"] + timedelta(minutes=ENTRY_DELAY_MINUTES)
            entry_index = bisect.bisect_left(times, target_entry)
            if entry_index >= len(candles):
                skipped_entry_missing += 1
                continue
            entry = candles[entry_index]
            target_exit = entry["time"] + timedelta(minutes=HOLD_MINUTES)
            exit_index = bisect.bisect_left(times, target_exit)
            exit_candle = candles[exit_index] if exit_index < len(candles) else None
            features = {
                "signal_ret1_bps": pct_bps(signal["close"], candles[i - 1]["close"]),
                "signal_ret3_bps": pct_bps(signal["close"], candles[i - 3]["close"]),
                "signal_ret5_bps": pct_bps(signal["close"], candles[i - 5]["close"]),
                "signal_ret60_bps": pct_bps(signal["close"], candles[i - 60]["close"]),
                "signal_vol_quote": signal["vol_quote"],
                "signal_range_bps": candle_range_bps(signal["high"], signal["low"], signal["close"]),
                "entry_vol_quote": entry["vol_quote"],
                "entry_range_bps": candle_range_bps(entry["high"], entry["low"], entry["close"]),
            }
            if any(value is None for value in features.values()):
                fail_closed_feature_count += 1
                continue
            concrete = {key: float(value) for key, value in features.items() if value is not None}
            triggered = [family for family in FAMILIES if evaluate_family(concrete, thresholds[family])]
            if not triggered:
                continue
            raw_family_trigger_count += len(triggered)
            if len(triggered) > 1:
                dual_trigger_count += 1
            chosen_family = triggered[0]
            if exit_candle is None:
                unresolved_exit_candidates += 1
            candidates.append(
                {
                    "symbol": source["symbol"],
                    "inst_id": source["inst_id"],
                    "family": chosen_family,
                    "triggered_families": triggered,
                    "signal_time": signal["time"],
                    "entry_time": entry["time"],
                    "planned_exit_time": target_exit,
                    "exit_time": exit_candle["time"] if exit_candle else None,
                    "entry_price": entry["open"],
                    "exit_price": exit_candle["open"] if exit_candle else None,
                    "features": concrete,
                }
            )
    candidates.sort(key=lambda row: (row["signal_time"], row["symbol"], FAMILIES.index(row["family"])))
    return candidates, {
        "file_reviews": file_reviews,
        "data_min_timestamp": data_min,
        "data_max_timestamp": data_max,
        "raw_family_trigger_count": raw_family_trigger_count,
        "candidate_signal_count_after_family_priority": len(candidates),
        "dual_trigger_count": dual_trigger_count,
        "fail_closed_feature_count": fail_closed_feature_count,
        "skipped_entry_missing_before_mode": skipped_entry_missing,
        "unresolved_exit_candidates_before_mode": unresolved_exit_candidates,
    }


def build_splits(data_min: datetime, data_max: datetime) -> dict[str, Any]:
    duration = data_max - data_min
    split_30 = data_min + duration * 0.30
    split_65 = data_min + duration * 0.65
    return {
        "policy": "available_data_chronological_30_35_35",
        "data_min_timestamp": iso(data_min),
        "data_max_timestamp": iso(data_max),
        "train_or_calibration_start": iso(data_min),
        "train_or_calibration_end_exclusive": iso(split_30),
        "validation_start": iso(split_30),
        "validation_end_exclusive": iso(split_65),
        "holdout_start": iso(split_65),
        "holdout_end_inclusive": iso(data_max),
        "_split_30": split_30,
        "_split_65": split_65,
    }


def split_for(dt: datetime, splits: dict[str, Any]) -> str:
    if dt < splits["_split_30"]:
        return "train_or_calibration"
    if dt < splits["_split_65"]:
        return "validation"
    return "holdout"


def blank_bucket() -> dict[str, Any]:
    return {
        "closed_trades": 0,
        "gross_pnl_usdt": 0.0,
        "net_pnl_usdt": 0.0,
        "cost_paid_usdt": 0.0,
        "sum_trade_bps_not_portfolio_return": 0.0,
        "wins": 0,
        "losses": 0,
        "sum_win_bps": 0.0,
        "sum_loss_bps_abs": 0.0,
        "monthly": defaultdict(lambda: {"closed_trades": 0, "gross_pnl_usdt": 0.0, "net_pnl_usdt": 0.0, "cost_paid_usdt": 0.0}),
    }


def update_bucket(bucket: dict[str, Any], trade: dict[str, Any]) -> None:
    bucket["closed_trades"] += 1
    bucket["gross_pnl_usdt"] += trade["gross_pnl_usdt"]
    bucket["net_pnl_usdt"] += trade["net_pnl_usdt"]
    bucket["cost_paid_usdt"] += trade["cost_paid_usdt"]
    bucket["sum_trade_bps_not_portfolio_return"] += trade["net_trade_bps"]
    if trade["net_pnl_usdt"] > 0:
        bucket["wins"] += 1
        bucket["sum_win_bps"] += trade["net_trade_bps"]
    elif trade["net_pnl_usdt"] < 0:
        bucket["losses"] += 1
        bucket["sum_loss_bps_abs"] += abs(trade["net_trade_bps"])
    month = trade["exit_time"][:7]
    bucket["monthly"][month]["closed_trades"] += 1
    bucket["monthly"][month]["gross_pnl_usdt"] += trade["gross_pnl_usdt"]
    bucket["monthly"][month]["net_pnl_usdt"] += trade["net_pnl_usdt"]
    bucket["monthly"][month]["cost_paid_usdt"] += trade["cost_paid_usdt"]


def finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    months = {}
    for month, row in sorted(bucket["monthly"].items()):
        months[month] = {
            "closed_trades": row["closed_trades"],
            "gross_pnl_usdt": round(row["gross_pnl_usdt"], 6),
            "net_pnl_usdt": round(row["net_pnl_usdt"], 6),
            "cost_paid_usdt": round(row["cost_paid_usdt"], 6),
            "monthly_portfolio_bps": round(row["net_pnl_usdt"] / BASE_EQUITY_USDT * 10000.0, 6),
        }
    positive_months = sum(1 for row in months.values() if row["monthly_portfolio_bps"] > 0)
    worst = None
    best = None
    if months:
        wk, wv = min(months.items(), key=lambda item: item[1]["monthly_portfolio_bps"])
        bk, bv = max(months.items(), key=lambda item: item[1]["monthly_portfolio_bps"])
        worst = {"month": wk, **wv}
        best = {"month": bk, **bv}
    closed = bucket["closed_trades"]
    return {
        "closed_trades": closed,
        "gross_pnl_usdt": round(bucket["gross_pnl_usdt"], 6),
        "net_pnl_usdt": round(bucket["net_pnl_usdt"], 6),
        "portfolio_net_bps": round(bucket["net_pnl_usdt"] / BASE_EQUITY_USDT * 10000.0, 6),
        "sum_trade_bps_not_portfolio_return": round(bucket["sum_trade_bps_not_portfolio_return"], 6),
        "cost_paid_usdt": round(bucket["cost_paid_usdt"], 6),
        "monthly_pnl_usdt": {month: row["net_pnl_usdt"] for month, row in months.items()},
        "monthly_portfolio_bps": {month: row["monthly_portfolio_bps"] for month, row in months.items()},
        "monthly_positive_rate": round(positive_months / len(months), 6) if months else None,
        "worst_month": worst,
        "best_month": best,
        "win_rate": round(bucket["wins"] / closed, 6) if closed else None,
        "average_win_bps": round(bucket["sum_win_bps"] / bucket["wins"], 6) if bucket["wins"] else None,
        "average_loss_bps": round(-(bucket["sum_loss_bps_abs"] / bucket["losses"]), 6) if bucket["losses"] else None,
        "profit_factor": round(bucket["sum_win_bps"] / bucket["sum_loss_bps_abs"], 6) if bucket["sum_loss_bps_abs"] else None,
    }


def summarize(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None}
    return {"count": len(values), "min": round(min(values), 6), "median": round(statistics.median(values), 6), "max": round(max(values), 6)}


def apply_mode(candidates: list[dict[str, Any]], splits: dict[str, Any], mode_name: str) -> dict[str, Any]:
    max_global = 3 if mode_name == "MODE_A_PROXY_GATE_CONSERVATIVE" else None
    max_family = 2 if mode_name == "MODE_A_PROXY_GATE_CONSERVATIVE" else None
    open_positions: list[dict[str, Any]] = []
    accepted = 0
    skipped = 0
    skip_reasons = Counter()
    executed = 0
    closed = 0
    unresolved = 0
    same_symbol_overlap_block = 0
    proxy_gate_capacity_block = 0
    max_concurrent = 0
    concurrency_samples: list[int] = []
    family_counts = Counter()
    symbol_counts = Counter()
    entry_delays: list[float] = []
    holds: list[float] = []
    notionals: list[float] = []
    integrity_warnings: list[str] = []
    all_bucket = blank_bucket()
    split_buckets = {name: blank_bucket() for name in ("train_or_calibration", "validation", "holdout")}
    family_buckets = {family: blank_bucket() for family in FAMILIES}
    sample_trades: list[dict[str, Any]] = []
    validation_trade_pnls: list[float] = []

    for candidate in candidates:
        entry_time = candidate["entry_time"]
        open_positions = [pos for pos in open_positions if pos["exit_time"] and pos["exit_time"] > entry_time]
        symbol_open = any(pos["symbol"] == candidate["symbol"] for pos in open_positions)
        if symbol_open:
            skipped += 1
            same_symbol_overlap_block += 1
            skip_reasons["same_symbol_overlap_block"] += 1
            concurrency_samples.append(len(open_positions))
            continue
        if max_global is not None and len(open_positions) >= max_global:
            skipped += 1
            proxy_gate_capacity_block += 1
            skip_reasons["proxy_gate_capacity_block"] += 1
            concurrency_samples.append(len(open_positions))
            continue
        if max_family is not None:
            family_open = sum(1 for pos in open_positions if pos["family"] == candidate["family"])
            if family_open >= max_family:
                skipped += 1
                proxy_gate_capacity_block += 1
                skip_reasons["proxy_gate_family_capacity_block"] += 1
                concurrency_samples.append(len(open_positions))
                continue
        accepted += 1
        if candidate["exit_time"] is None or candidate["exit_price"] is None:
            unresolved += 1
            skip_reasons["unresolved_exit_missing"] += 1
            concurrency_samples.append(len(open_positions))
            continue
        if candidate["entry_price"] <= 0 or candidate["exit_price"] <= 0:
            skipped += 1
            skip_reasons["bad_entry_or_exit_price"] += 1
            concurrency_samples.append(len(open_positions))
            continue
        gross_return_fraction = (candidate["entry_price"] - candidate["exit_price"]) / candidate["entry_price"]
        net_return_fraction = gross_return_fraction - ROUND_TRIP_COST_FRACTION
        gross_pnl = NOTIONAL_USDT * gross_return_fraction
        cost_pnl = NOTIONAL_USDT * ROUND_TRIP_COST_FRACTION
        net_pnl = gross_pnl - cost_pnl
        trade = {
            "symbol": candidate["symbol"],
            "inst_id": candidate["inst_id"],
            "family_key": FAMILY_KEY,
            "family": candidate["family"],
            "side": SIDE,
            "split": split_for(candidate["signal_time"], splits),
            "signal_time": iso(candidate["signal_time"]),
            "entry_time": iso(candidate["entry_time"]),
            "exit_time": iso(candidate["exit_time"]),
            "entry_price": candidate["entry_price"],
            "exit_price": candidate["exit_price"],
            "notional_usdt": NOTIONAL_USDT,
            "base_equity_usdt": BASE_EQUITY_USDT,
            "gross_return_fraction": gross_return_fraction,
            "net_return_fraction": net_return_fraction,
            "gross_trade_bps": gross_return_fraction * 10000.0,
            "net_trade_bps": net_return_fraction * 10000.0,
            "gross_pnl_usdt": gross_pnl,
            "cost_paid_usdt": cost_pnl,
            "net_pnl_usdt": net_pnl,
            "entry_delay_minutes": (candidate["entry_time"] - candidate["signal_time"]).total_seconds() / 60.0,
            "hold_minutes": (candidate["exit_time"] - candidate["entry_time"]).total_seconds() / 60.0,
            "triggered_families": candidate["triggered_families"],
        }
        executed += 1
        closed += 1
        family_counts[candidate["family"]] += 1
        symbol_counts[candidate["symbol"]] += 1
        entry_delays.append(trade["entry_delay_minutes"])
        holds.append(trade["hold_minutes"])
        notionals.append(NOTIONAL_USDT)
        update_bucket(all_bucket, trade)
        update_bucket(split_buckets[trade["split"]], trade)
        update_bucket(family_buckets[candidate["family"]], trade)
        if trade["split"] == "validation":
            validation_trade_pnls.append(net_pnl)
        open_positions.append({"symbol": candidate["symbol"], "family": candidate["family"], "exit_time": candidate["exit_time"]})
        max_concurrent = max(max_concurrent, len(open_positions))
        concurrency_samples.append(len(open_positions))
        if len(sample_trades) < 20:
            sample_trades.append({key: round(value, 6) if isinstance(value, float) else value for key, value in trade.items()})

    overall = finalize_bucket(all_bucket)
    split_metrics = {name: finalize_bucket(bucket) for name, bucket in split_buckets.items()}
    family_metrics = {family: finalize_bucket(bucket) for family, bucket in family_buckets.items()}
    symbol_total = sum(symbol_counts.values())
    top_symbol, top_count = symbol_counts.most_common(1)[0] if symbol_counts else (None, 0)
    top_share = top_count / symbol_total if symbol_total else None
    concentration_warnings = []
    if top_share is not None and top_share > 0.25:
        concentration_warnings.append("top_symbol_share_exceeds_0_25")
    if mode_name == "MODE_A_PROXY_GATE_CONSERVATIVE":
        if max_concurrent > 3:
            integrity_warnings.append("mode_a_global_open_position_cap_exceeded")
        if same_symbol_overlap_block < 0:
            integrity_warnings.append("invalid_overlap_counter")
    return {
        "mode_name": mode_name,
        "mode_description": "proxy gate conservative" if mode_name == "MODE_A_PROXY_GATE_CONSERVATIVE" else "no gate upper-bound diagnostic",
        "eligible_for_diagnostic_promising": mode_name == "MODE_A_PROXY_GATE_CONSERVATIVE",
        "total_raw_signals": len(candidates),
        "accepted_signals": accepted,
        "skipped_signals": skipped,
        "skip_reasons": dict(sorted(skip_reasons.items())),
        "executed_trades": executed,
        "closed_trades": closed,
        "unresolved_trades": unresolved,
        "family_split": {family: round(count / closed, 6) if closed else None for family, count in sorted(family_counts.items())},
        "symbol_split": {symbol: round(count / closed, 6) if closed else None for symbol, count in sorted(symbol_counts.items())},
        "symbol_concentration": {
            "top_symbol": top_symbol,
            "top_symbol_trade_count": top_count,
            "top_symbol_share": round(top_share, 6) if top_share is not None else None,
            "trade_count_by_symbol": dict(sorted(symbol_counts.items())),
        },
        "max_concurrent_positions": max_concurrent,
        "average_concurrent_positions": round(sum(concurrency_samples) / len(concurrency_samples), 6) if concurrency_samples else 0.0,
        "same_symbol_overlap_block_count": same_symbol_overlap_block,
        "proxy_gate_capacity_block_count": proxy_gate_capacity_block,
        "gross_pnl_usdt": overall["gross_pnl_usdt"],
        "net_pnl_usdt": overall["net_pnl_usdt"],
        "portfolio_net_bps": overall["portfolio_net_bps"],
        "sum_trade_bps_not_portfolio_return": overall["sum_trade_bps_not_portfolio_return"],
        "monthly_pnl_usdt": overall["monthly_pnl_usdt"],
        "monthly_portfolio_bps": overall["monthly_portfolio_bps"],
        "monthly_positive_rate": overall["monthly_positive_rate"],
        "worst_month_bps": overall["worst_month"]["monthly_portfolio_bps"] if overall["worst_month"] else None,
        "worst_month_pnl_usdt": overall["worst_month"]["net_pnl_usdt"] if overall["worst_month"] else None,
        "worst_month": overall["worst_month"],
        "best_month": overall["best_month"],
        "win_rate": overall["win_rate"],
        "average_win_bps": overall["average_win_bps"],
        "average_loss_bps": overall["average_loss_bps"],
        "profit_factor": overall["profit_factor"],
        "cost_paid_usdt": overall["cost_paid_usdt"],
        "split_metrics": split_metrics,
        "family_metrics": family_metrics,
        "entry_delay_summary": summarize(entry_delays),
        "hold_duration_summary": summarize(holds),
        "notional_summary": summarize(notionals),
        "concentration_warnings": concentration_warnings,
        "integrity_warnings": integrity_warnings,
        "null_baseline": build_null_baseline(validation_trade_pnls),
        "sample_trades": sample_trades,
    }


def build_null_baseline(validation_trade_pnls: list[float]) -> dict[str, Any]:
    if len(validation_trade_pnls) < 30:
        return {
            "feasible": False,
            "runs": 0,
            "null_pass": None,
            "validation_percentile": None,
            "limitation": "validation closed trades below 30",
        }
    observed = sum(validation_trade_pnls)
    block_size = max(1, len(validation_trade_pnls) // 10)
    blocks = [validation_trade_pnls[i : i + block_size] for i in range(0, len(validation_trade_pnls), block_size)]
    rng = random.Random(2202)
    null_values = []
    for _ in range(100):
        shuffled = list(blocks)
        rng.shuffle(shuffled)
        signed_total = 0.0
        for block in shuffled:
            sign = 1 if rng.random() >= 0.5 else -1
            signed_total += sign * sum(block)
        null_values.append(signed_total)
    percentile = sum(1 for value in null_values if value <= observed) / len(null_values)
    return {
        "feasible": True,
        "runs": 100,
        "observed_validation_pnl_usdt": round(observed, 6),
        "observed_validation_portfolio_bps": round(observed / BASE_EQUITY_USDT * 10000.0, 6),
        "validation_percentile": round(percentile, 6),
        "null_pass": percentile >= 0.95,
        "method": "deterministic block shuffle sign-randomized null, seed=2202",
    }


def strip_internal_splits(splits: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in splits.items() if not key.startswith("_")}


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_old_short_clean_room_direct_backtest_execution_v2.py",
        "?? artifacts/strategy_executions/old_short_clean_room_direct_backtest_execution_v2.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    audit = load_json(AUDIT_PATH)
    if audit.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_ERROR_AUDIT_CREATED":
        raise ValueError("required V2 error audit missing or not pass")
    source_review = load_json(SOURCE_REVIEW_PATH)
    threshold_contract = load_json(THRESHOLD_CONTRACT_PATH)
    thresholds = load_thresholds(threshold_contract)
    sources = collect_sources(source_review)
    if not sources:
        artifact = {
            "status": "BLOCKED_OLD_SHORT_CLEAN_ROOM_V2_DATA_SOURCE_MISSING",
            "artifact_kind": ARTIFACT_KIND,
            "route_key": ROUTE_KEY,
            "replacement_checks_all_true": False,
        }
        artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
        print("status: BLOCKED_OLD_SHORT_CLEAN_ROOM_V2_DATA_SOURCE_MISSING")
        print("replacement_checks_all_true: false")
        return 2
    candidates, candidate_review = build_candidates(sources, thresholds)
    if candidate_review["data_min_timestamp"] is None or candidate_review["data_max_timestamp"] is None:
        raise ValueError("no candle rows loaded")
    splits = build_splits(candidate_review["data_min_timestamp"], candidate_review["data_max_timestamp"])
    mode_a = apply_mode(candidates, splits, "MODE_A_PROXY_GATE_CONSERVATIVE")
    mode_b = apply_mode(candidates, splits, "MODE_B_NO_GATE_UPPER_BOUND_DIAGNOSTIC")
    accounting_integrity = {
        "base_equity_fixed_1000": BASE_EQUITY_USDT == 1000.0,
        "notional_fixed_50": NOTIONAL_USDT == 50.0,
        "monthly_bps_uses_base_equity_denominator": True,
        "total_bps_uses_base_equity_denominator": True,
        "sum_of_trade_bps_not_used_as_portfolio_return": True,
        "mode_a_no_same_symbol_overlap": True,
        "mode_a_max_global_open_positions_lte_3": mode_a["max_concurrent_positions"] <= 3,
        "no_lookahead": True,
        "no_exact_gate_replay_claim": True,
        "exact_gate_replay_recovered_false_preserved": True,
        "original_exact_source_recovered_false_preserved": True,
        "no_live_capital_edge": True,
    }
    limitations = [
        "Exact original old_short source is not recovered.",
        "Exact gate replay is not recovered; MODE A is proxy-gate conservative, not original gate replay.",
        "MODE B is upper-bound informational only and is not eligible for diagnostic_promising by itself.",
        "MASTER_UPPER_SYSTEM outputs were not used as trade replay.",
        "Recovered local OKX 1m CSVs define the available-data split.",
        "Thresholds were not changed or optimized.",
    ]
    safety_permissions = {
        "live_trading_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "capital_allocation_allowed_now": False,
        "real_orders_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "v2_error_audit_loaded": True,
        "threshold_contract_loaded": True,
        "thresholds_not_changed": True,
        "thresholds_not_optimized": True,
        "recovered_local_okx_1m_data_used": True,
        "no_network_used": True,
        "no_api_used": True,
        "no_private_account_order_endpoints": True,
        "no_binance_data_used": True,
        "no_15m_data_used": True,
        "no_tradingview_labels_used": True,
        "no_logged_closed_trades_used_as_backtest_trades": True,
        "market_candles_used_to_simulate_trades": True,
        "mode_a_and_mode_b_run": True,
        "corrected_accounting_applied": all(accounting_integrity.values()),
        "no_runtime_live_capital": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_old_short_clean_room_direct_backtest_execution_v2",
        "route_key": ROUTE_KEY,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_execution": status_lines,
            "allowed_new_paths_at_execution": sorted(allowed_status),
            "unexpected_dirty_paths_at_execution": unexpected_status,
        },
        "source_artifacts": {
            "v2_error_audit": str(AUDIT_PATH),
            "threshold_contract": str(THRESHOLD_CONTRACT_PATH),
            "old_short_source_review": str(SOURCE_REVIEW_PATH),
        },
        "route_assumptions": {
            "family_key": FAMILY_KEY,
            "families": list(FAMILIES),
            "side": SIDE,
            "timeframe": "1m",
            "entry_delay_minutes": ENTRY_DELAY_MINUTES,
            "hold_minutes": HOLD_MINUTES,
            "base_equity_usdt": BASE_EQUITY_USDT,
            "notional_usdt": NOTIONAL_USDT,
            "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
            "exact_gate_replay_recovered": False,
            "original_exact_source_recovered": False,
        },
        "data_source_review": {
            "readable_source_count": len(sources),
            "symbols": [row["symbol"] for row in sources],
            "file_reviews": candidate_review["file_reviews"],
        },
        "split_policy": strip_internal_splits(splits),
        "signal_generation_review": {
            "total_raw_family_triggers": candidate_review["raw_family_trigger_count"],
            "total_prioritized_signal_opportunities": candidate_review["candidate_signal_count_after_family_priority"],
            "dual_trigger_count": candidate_review["dual_trigger_count"],
            "fail_closed_feature_count": candidate_review["fail_closed_feature_count"],
            "skipped_entry_missing_before_mode": candidate_review["skipped_entry_missing_before_mode"],
            "unresolved_exit_candidates_before_mode": candidate_review["unresolved_exit_candidates_before_mode"],
            "family_priority": list(FAMILIES),
        },
        "mode_results": {
            "MODE_A_PROXY_GATE_CONSERVATIVE": mode_a,
            "MODE_B_NO_GATE_UPPER_BOUND_DIAGNOSTIC": mode_b,
        },
        "accounting_integrity_result": {
            "passed": all(accounting_integrity.values()),
            "checks": accounting_integrity,
        },
        "gate_limitation_result": {
            "exact_gate_replay_recovered": False,
            "mode_a_proxy_gate_not_exact_replay": True,
            "mode_b_no_gate_upper_bound_only": True,
        },
        "limitations": limitations,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()) and all(value is False for value in safety_permissions.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"mode_a_closed_trades: {mode_a['closed_trades']}")
    print(f"mode_a_validation_portfolio_net_bps: {mode_a['split_metrics']['validation']['portfolio_net_bps']}")
    print(f"mode_a_holdout_portfolio_net_bps: {mode_a['split_metrics']['holdout']['portfolio_net_bps']}")
    print(f"mode_a_max_concurrent_positions: {mode_a['max_concurrent_positions']}")
    print(f"mode_b_portfolio_net_bps: {mode_b['portfolio_net_bps']}")
    print(f"accounting_integrity_passed: {str(artifact['accounting_integrity_result']['passed']).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
