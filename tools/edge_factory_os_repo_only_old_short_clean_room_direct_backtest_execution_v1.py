from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "old_short_clean_room_direct_backtest_execution_v1.json"
THRESHOLD_CONTRACT_PATH = REPO_ROOT / "artifacts" / "old_short_clean_room" / "old_short_clean_room_runner_fixture_threshold_contract_v1.json"
SOURCE_REVIEW_PATH = REPO_ROOT / "artifacts" / "old_short" / "old_short_proxy_backtest_data_coverage_source_review_v1.json"

STATUS = "PASS_REPO_CODE_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_EXECUTED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_EXECUTION"
ROUTE_KEY = "old_short_clean_room_v1"
FAMILY_KEY = "old_short"
FAMILIES = ("blowoff_short", "mean_reversion_short")
SIDE = "short"
ENTRY_DELAY_MINUTES = 2
HOLD_MINUTES = 120
NOTIONAL_USDT = 50.0
ROUND_TRIP_COST_BPS = 20.0
VALID_SUBFAMILIES = set(FAMILIES)
REQUIRED_LABELS = {
    "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
    "NOT_ORIGINAL_THRESHOLD",
    "NOT_PNL_OPTIMIZED",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
}
REQUIRED_CANDLE_COLUMNS = {"ts", "open", "high", "low", "close", "volCcyQuote", "time"}
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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return sha256_text(canonical_json(clone))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


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


def range_bps(high: float, low: float, close: float) -> float | None:
    if close <= 0:
        return None
    return (high - low) / close * 10000.0


def compare(feature_value: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return feature_value >= threshold
    if operator == "<=":
        return feature_value <= threshold
    raise ValueError(f"unsupported operator: {operator}")


def walk_dicts(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_dicts(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_dicts(value)


def collect_recovered_sources(source_review: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for item in walk_dicts(source_review):
        path_text = item.get("path")
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
        if not symbol:
            continue
        if symbol in candidates:
            continue
        exists = path.exists() and path.is_file()
        header: list[str] = []
        readable = False
        read_error = None
        if exists:
            try:
                with path.open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.reader(handle)
                    header = next(reader, [])
                readable = REQUIRED_CANDLE_COLUMNS.issubset(set(header))
            except Exception as exc:  # noqa: BLE001 - artifact records the exact failure.
                read_error = f"{type(exc).__name__}: {exc}"
        candidates[symbol] = {
            "symbol": symbol,
            "inst_id": f"{symbol}-USDT-SWAP",
            "path": str(path),
            "exists": exists,
            "readable": readable,
            "header": header,
            "read_error": read_error,
            "size_bytes": path.stat().st_size if exists else None,
        }
    return sorted(candidates.values(), key=lambda row: row["symbol"])


def load_thresholds(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    completeness = contract.get("contract_completeness", {})
    identity = contract.get("fixture_threshold_contract_identity", {})
    families = contract.get("threshold_families", {})
    if identity.get("route_key") != ROUTE_KEY:
        raise ValueError("threshold contract route_key mismatch")
    if not completeness.get("contract_complete"):
        raise ValueError("threshold contract is incomplete")
    if completeness.get("family_threshold_count") != 2:
        raise ValueError("threshold contract family count mismatch")
    loaded: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        family_node = families.get(family)
        if not isinstance(family_node, dict):
            raise ValueError(f"threshold family missing: {family}")
        rules = family_node.get("threshold_rules")
        if not isinstance(rules, dict):
            raise ValueError(f"threshold rules missing: {family}")
        for feature in FEATURES:
            rule = rules.get(feature)
            if not isinstance(rule, dict):
                raise ValueError(f"threshold feature missing: {family}.{feature}")
            labels = set(rule.get("labels", []))
            if not REQUIRED_LABELS.issubset(labels):
                raise ValueError(f"threshold labels missing: {family}.{feature}")
            if rule.get("operator") not in {">=", "<="}:
                raise ValueError(f"unsupported threshold operator: {family}.{feature}")
            if parse_float(rule.get("value")) is None:
                raise ValueError(f"non-numeric threshold value: {family}.{feature}")
        loaded[family] = rules
    return loaded


def read_candles(source: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = Path(source["path"])
    candles: list[dict[str, Any]] = []
    bad_rows = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader, start=2):
            if str(row.get("confirm", "1")).strip() not in {"1", "true", "True"}:
                continue
            dt = parse_time(row.get("time", ""))
            opened = parse_float(row.get("open"))
            high = parse_float(row.get("high"))
            low = parse_float(row.get("low"))
            close = parse_float(row.get("close"))
            vol_quote = parse_float(row.get("volCcyQuote"))
            if dt is None or opened is None or high is None or low is None or close is None or vol_quote is None:
                bad_rows += 1
                continue
            if opened <= 0 or high <= 0 or low <= 0 or close <= 0 or high < low:
                bad_rows += 1
                continue
            candles.append(
                {
                    "row_index": row_index,
                    "time": dt,
                    "open": opened,
                    "high": high,
                    "low": low,
                    "close": close,
                    "vol_quote": vol_quote,
                }
            )
    candles.sort(key=lambda row: row["time"])
    duplicate_times = 0
    deduped: list[dict[str, Any]] = []
    last_time: datetime | None = None
    for candle in candles:
        if candle["time"] == last_time:
            duplicate_times += 1
            continue
        deduped.append(candle)
        last_time = candle["time"]
    review = {
        "symbol": source["symbol"],
        "inst_id": source["inst_id"],
        "path": source["path"],
        "rows_loaded": len(deduped),
        "bad_rows_skipped": bad_rows,
        "duplicate_timestamps_skipped": duplicate_times,
        "first_time_utc": deduped[0]["time"].isoformat().replace("+00:00", "Z") if deduped else None,
        "last_time_utc": deduped[-1]["time"].isoformat().replace("+00:00", "Z") if deduped else None,
    }
    return deduped, review


def split_for(dt: datetime) -> str:
    if dt < datetime(2024, 1, 1, tzinfo=timezone.utc):
        return "train"
    if dt < datetime(2025, 1, 1, tzinfo=timezone.utc):
        return "validation"
    return "holdout"


def blank_perf() -> dict[str, Any]:
    return {
        "closed_trades": 0,
        "gross_bps": 0.0,
        "net_bps": 0.0,
        "wins": 0,
        "losses": 0,
        "sum_win_bps": 0.0,
        "sum_loss_bps_abs": 0.0,
        "monthly": defaultdict(lambda: {"closed_trades": 0, "gross_bps": 0.0, "net_bps": 0.0}),
    }


def update_perf(perf: dict[str, Any], trade: dict[str, Any]) -> None:
    perf["closed_trades"] += 1
    perf["gross_bps"] += trade["gross_bps"]
    perf["net_bps"] += trade["net_bps"]
    if trade["net_bps"] > 0:
        perf["wins"] += 1
        perf["sum_win_bps"] += trade["net_bps"]
    elif trade["net_bps"] < 0:
        perf["losses"] += 1
        perf["sum_loss_bps_abs"] += abs(trade["net_bps"])
    month = trade["signal_time"][:7]
    perf["monthly"][month]["closed_trades"] += 1
    perf["monthly"][month]["gross_bps"] += trade["gross_bps"]
    perf["monthly"][month]["net_bps"] += trade["net_bps"]


def finalize_perf(perf: dict[str, Any]) -> dict[str, Any]:
    closed = perf["closed_trades"]
    months = dict(sorted(perf["monthly"].items()))
    positive_months = sum(1 for row in months.values() if row["net_bps"] > 0)
    worst_month = None
    best_month = None
    if months:
        worst_key, worst_value = min(months.items(), key=lambda item: item[1]["net_bps"])
        best_key, best_value = max(months.items(), key=lambda item: item[1]["net_bps"])
        worst_month = {"month": worst_key, **worst_value}
        best_month = {"month": best_key, **best_value}
    return {
        "closed_trades": closed,
        "gross_bps": round(perf["gross_bps"], 6),
        "net_bps": round(perf["net_bps"], 6),
        "win_rate": round(perf["wins"] / closed, 6) if closed else None,
        "average_win_bps": round(perf["sum_win_bps"] / perf["wins"], 6) if perf["wins"] else None,
        "average_loss_bps": round(-(perf["sum_loss_bps_abs"] / perf["losses"]), 6) if perf["losses"] else None,
        "profit_factor": round(perf["sum_win_bps"] / perf["sum_loss_bps_abs"], 6) if perf["sum_loss_bps_abs"] else None,
        "monthly": {k: {kk: round(vv, 6) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in months.items()},
        "monthly_positive_rate": round(positive_months / len(months), 6) if months else None,
        "worst_month": worst_month,
        "best_month": best_month,
    }


def evaluate_family(features: dict[str, float], rules: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for feature in FEATURES:
        if feature not in features:
            failures.append(f"required_feature_missing:{feature}")
            continue
        rule = rules[feature]
        threshold = float(rule["value"])
        operator = str(rule["operator"])
        if not compare(features[feature], operator, threshold):
            return False, []
    return not failures, failures


def run_backtest(sources: list[dict[str, Any]], thresholds: dict[str, dict[str, Any]]) -> dict[str, Any]:
    total_signals = 0
    executed_trades = 0
    skipped_signals = 0
    fail_closed_signals = 0
    unresolved_trades = 0
    data_bad_rows = 0
    skipped_no_required_window = 0
    file_reviews = []
    family_counts = Counter()
    symbol_counts = Counter()
    split_counts = Counter()
    entry_delays: list[float] = []
    hold_durations: list[float] = []
    notionals: list[float] = []
    sample_trades: list[dict[str, Any]] = []
    validation_net_bps: list[float] = []
    split_perf = {name: blank_perf() for name in ("train", "validation", "holdout")}
    all_perf = blank_perf()
    family_perf = {family: blank_perf() for family in FAMILIES}
    first_data_time = None
    last_data_time = None

    for source in sources:
        candles, review = read_candles(source)
        file_reviews.append(review)
        data_bad_rows += review["bad_rows_skipped"]
        if candles:
            first_data_time = min(first_data_time, candles[0]["time"]) if first_data_time else candles[0]["time"]
            last_data_time = max(last_data_time, candles[-1]["time"]) if last_data_time else candles[-1]["time"]
        if len(candles) <= 60 + ENTRY_DELAY_MINUTES + HOLD_MINUTES:
            skipped_no_required_window += max(len(candles), 0)
            continue
        for i in range(60, len(candles) - ENTRY_DELAY_MINUTES - HOLD_MINUTES):
            signal = candles[i]
            entry_index = i + ENTRY_DELAY_MINUTES
            exit_index = entry_index + HOLD_MINUTES
            entry = candles[entry_index]
            exit_candle = candles[exit_index]
            feature_values = {
                "signal_ret1_bps": pct_bps(signal["close"], candles[i - 1]["close"]),
                "signal_ret3_bps": pct_bps(signal["close"], candles[i - 3]["close"]),
                "signal_ret5_bps": pct_bps(signal["close"], candles[i - 5]["close"]),
                "signal_ret60_bps": pct_bps(signal["close"], candles[i - 60]["close"]),
                "signal_vol_quote": signal["vol_quote"],
                "signal_range_bps": range_bps(signal["high"], signal["low"], signal["close"]),
                "entry_vol_quote": entry["vol_quote"],
                "entry_range_bps": range_bps(entry["high"], entry["low"], entry["close"]),
            }
            if any(value is None for value in feature_values.values()):
                fail_closed_signals += len(FAMILIES)
                continue
            concrete_features = {k: float(v) for k, v in feature_values.items() if v is not None}
            for family in FAMILIES:
                passed, failures = evaluate_family(concrete_features, thresholds[family])
                if failures:
                    fail_closed_signals += 1
                    continue
                if not passed:
                    continue
                total_signals += 1
                entry_price = entry["open"]
                exit_price = exit_candle["open"]
                if entry_price <= 0 or exit_price <= 0:
                    skipped_signals += 1
                    fail_closed_signals += 1
                    continue
                gross_bps = (entry_price - exit_price) / entry_price * 10000.0
                net_bps = gross_bps - ROUND_TRIP_COST_BPS
                signal_time = signal["time"].isoformat().replace("+00:00", "Z")
                entry_time = entry["time"].isoformat().replace("+00:00", "Z")
                exit_time = exit_candle["time"].isoformat().replace("+00:00", "Z")
                trade = {
                    "symbol": source["symbol"],
                    "inst_id": source["inst_id"],
                    "family_key": FAMILY_KEY,
                    "family": family,
                    "side": SIDE,
                    "split": split_for(signal["time"]),
                    "signal_time": signal_time,
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                    "entry_delay_minutes": ENTRY_DELAY_MINUTES,
                    "hold_minutes": HOLD_MINUTES,
                    "entry_price_policy": "conservative_next_available_open_due_contract_ambiguity",
                    "exit_price_policy": "conservative_exit_open_due_contract_ambiguity",
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "gross_bps": gross_bps,
                    "net_bps": net_bps,
                    "notional": NOTIONAL_USDT,
                    "features": concrete_features,
                }
                executed_trades += 1
                family_counts[family] += 1
                symbol_counts[source["symbol"]] += 1
                split_counts[trade["split"]] += 1
                entry_delays.append(float(ENTRY_DELAY_MINUTES))
                hold_durations.append(float(HOLD_MINUTES))
                notionals.append(NOTIONAL_USDT)
                update_perf(all_perf, trade)
                update_perf(split_perf[trade["split"]], trade)
                update_perf(family_perf[family], trade)
                if trade["split"] == "validation":
                    validation_net_bps.append(net_bps)
                if len(sample_trades) < 20:
                    sample_trades.append({k: (round(v, 6) if isinstance(v, float) else v) for k, v in trade.items() if k != "features"})

    closed_trades = executed_trades
    symbol_total = sum(symbol_counts.values())
    top_symbol = symbol_counts.most_common(1)[0] if symbol_counts else (None, 0)
    concentration = {
        "top_symbol": top_symbol[0],
        "top_symbol_trade_count": top_symbol[1],
        "top_symbol_trade_share": round(top_symbol[1] / symbol_total, 6) if symbol_total else None,
        "trade_count_by_symbol": dict(sorted(symbol_counts.items())),
    }
    entry_delay_summary = summarize_numbers(entry_delays)
    hold_duration_summary = summarize_numbers(hold_durations)
    notional_summary = summarize_numbers(notionals)
    split_summary = {name: finalize_perf(perf) for name, perf in split_perf.items()}
    family_summary = {name: finalize_perf(perf) for name, perf in family_perf.items()}
    overall = finalize_perf(all_perf)

    null_baseline = build_null_baseline(validation_net_bps)
    first_iso = first_data_time.isoformat().replace("+00:00", "Z") if first_data_time else None
    last_iso = last_data_time.isoformat().replace("+00:00", "Z") if last_data_time else None
    return {
        "data_file_reviews": file_reviews,
        "data_source_summary": {
            "source_review_artifact": str(SOURCE_REVIEW_PATH),
            "symbols_loaded": len(file_reviews),
            "first_data_time_utc": first_iso,
            "last_data_time_utc": last_iso,
            "bad_rows_skipped": data_bad_rows,
            "usable_okx_1m_data_source_readable": bool(file_reviews),
            "source_scope": "recovered OKX 1m CSV paths recorded in old_short source-review artifact",
        },
        "execution_metrics": {
            "total_signals": total_signals,
            "executed_trades": executed_trades,
            "skipped_signals": skipped_signals,
            "fail_closed_signals": fail_closed_signals,
            "closed_trades": closed_trades,
            "unresolved_trades": unresolved_trades,
            "skipped_no_required_candle_window": skipped_no_required_window,
            "gross_bps": overall["gross_bps"],
            "net_bps": overall["net_bps"],
            "win_rate": overall["win_rate"],
            "average_win_bps": overall["average_win_bps"],
            "average_loss_bps": overall["average_loss_bps"],
            "profit_factor": overall["profit_factor"],
            "monthly_gross_net": overall["monthly"],
            "monthly_positive_rate": overall["monthly_positive_rate"],
            "worst_month": overall["worst_month"],
            "best_month": overall["best_month"],
            "family_split": {family: round(count / executed_trades, 6) if executed_trades else None for family, count in sorted(family_counts.items())},
            "trade_count_by_family": dict(sorted(family_counts.items())),
            "symbol_concentration": concentration,
            "entry_delay_summary": entry_delay_summary,
            "hold_duration_summary": hold_duration_summary,
            "notional_summary": notional_summary,
        },
        "split_metrics": split_summary,
        "family_metrics": family_summary,
        "split_trade_counts": dict(sorted(split_counts.items())),
        "sample_trades": sample_trades,
        "null_baseline": null_baseline,
    }


def summarize_numbers(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None}
    return {
        "count": len(values),
        "min": round(min(values), 6),
        "median": round(statistics.median(values), 6),
        "max": round(max(values), 6),
    }


def build_null_baseline(validation_net_bps: list[float]) -> dict[str, Any]:
    if len(validation_net_bps) < 30:
        return {
            "feasible": False,
            "runs": 0,
            "null_pass": None,
            "validation_percentile": None,
            "limitation": "validation trade count below 30, deterministic timestamp/block shuffle null not meaningful",
        }
    observed = sum(validation_net_bps)
    rng = random.Random(1701)
    null_totals: list[float] = []
    block_size = max(1, len(validation_net_bps) // 10)
    blocks = [validation_net_bps[i : i + block_size] for i in range(0, len(validation_net_bps), block_size)]
    for _ in range(100):
        shuffled = list(blocks)
        rng.shuffle(shuffled)
        signs = [1 if rng.random() >= 0.5 else -1 for _ in shuffled]
        null_totals.append(sum(sign * sum(block) for sign, block in zip(signs, shuffled)))
    less_equal = sum(1 for value in null_totals if value <= observed)
    percentile = less_equal / len(null_totals)
    return {
        "feasible": True,
        "runs": 100,
        "observed_validation_net_bps": round(observed, 6),
        "validation_percentile": round(percentile, 6),
        "null_pass": percentile >= 0.95,
        "method": "deterministic block shuffle with sign randomization, seed=1701",
    }


def main() -> int:
    repo_status = run_git(["status", "--short"])
    allowed_status_entries = {
        "?? tools/edge_factory_os_repo_only_old_short_clean_room_direct_backtest_execution_v1.py",
        "?? artifacts/strategy_executions/old_short_clean_room_direct_backtest_execution_v1.json",
    }
    repo_status_lines = [line for line in repo_status.splitlines() if line.strip()]
    unexpected_status_entries = [line for line in repo_status_lines if line not in allowed_status_entries]
    repo_clean = not unexpected_status_entries
    tracked_python_count = int(run_git(["ls-files", "*.py"], count_lines=True))
    head = run_git(["rev-parse", "HEAD"])

    threshold_contract = load_json(THRESHOLD_CONTRACT_PATH)
    source_review = load_json(SOURCE_REVIEW_PATH)
    thresholds = load_thresholds(threshold_contract)
    sources = collect_recovered_sources(source_review)
    readable_sources = [row for row in sources if row["readable"]]
    if not readable_sources:
        artifact = {
            "status": "BLOCKED_OLD_SHORT_CLEAN_ROOM_BACKTEST_DATA_SOURCE_MISSING",
            "artifact_kind": ARTIFACT_KIND,
            "route_key": ROUTE_KEY,
            "source_checkpoint": {"head": head, "tracked_python_count": tracked_python_count, "repo_clean_before_run": repo_clean},
            "data_source_review": {"candidate_source_count": len(sources), "readable_okx_1m_source_count": 0, "sources": sources[:20]},
            "replacement_checks_all_true": False,
            "next_module": "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_DATA_SOURCE_BLOCKER_REVIEW",
        }
        artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
        print("status: BLOCKED_OLD_SHORT_CLEAN_ROOM_BACKTEST_DATA_SOURCE_MISSING")
        print("replacement_checks_all_true: false")
        return 2

    results = run_backtest(readable_sources, thresholds)
    limitations = [
        "Original exact old_short source is not recovered.",
        "Exact replay is not claimed.",
        "Exact global gate replay is unavailable; this is a clean-room historical diagnostic with gate limitations recorded.",
        "Entry and exit price contract is ambiguous; conservative next available open is used and recorded.",
        "Costs use fallback 20 bps round-trip assumption because no more specific clean-room historical backtest cost was found in the reviewed contract.",
        "Recovered OKX 1m source coverage starts in 2025 for this artifact set, leaving train/validation splits absent or sparse under the requested standard split.",
    ]
    safety_permissions = {
        "live_trading_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "capital_allocation_allowed_now": False,
        "real_orders_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean,
        "threshold_contract_loaded": True,
        "threshold_contract_complete": True,
        "okx_1m_data_source_readable": True,
        "no_network_used": True,
        "no_api_used": True,
        "no_private_api_used": True,
        "no_account_or_order_endpoint_used": True,
        "no_binance_data_used": True,
        "no_tradingview_labels_used": True,
        "no_logged_closed_trades_used_as_backtest_trades": True,
        "market_candles_used_to_simulate_trades": True,
        "no_live_trading": True,
        "no_runtime_enablement": True,
        "no_monitor_start": True,
        "no_capital_allocation": True,
        "no_real_orders": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "exact_source_not_claimed": True,
        "exact_replay_not_claimed": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_old_short_clean_room_direct_backtest_execution_v1",
        "route_key": ROUTE_KEY,
        "source_checkpoint": {
            "head": head,
            "tracked_python_count": tracked_python_count,
            "repo_clean_before_run": repo_clean,
            "git_status_at_execution": repo_status_lines,
            "allowed_new_paths_at_execution": sorted(allowed_status_entries),
            "unexpected_dirty_paths_at_execution": unexpected_status_entries,
            "prompt_expected_head": "4b62f8afcb7af43840bdf5b88dbcf303ac35fcfb",
            "prompt_head_matches_actual": head == "4b62f8afcb7af43840bdf5b88dbcf303ac35fcfb",
        },
        "source_artifacts": {
            "threshold_contract": str(THRESHOLD_CONTRACT_PATH),
            "old_short_proxy_backtest_data_coverage_source_review": str(SOURCE_REVIEW_PATH),
        },
        "clean_room_route_assumptions": {
            "family_key": FAMILY_KEY,
            "families": list(FAMILIES),
            "side": SIDE,
            "timeframe": "1m",
            "entry_delay_minutes": ENTRY_DELAY_MINUTES,
            "hold_minutes": HOLD_MINUTES,
            "notional_usdt": NOTIONAL_USDT,
            "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
            "global_gate_required_if_gate_replay_available": True,
            "exact_gate_replay_available": False,
            "original_exact_source_recovered": False,
            "exact_replay_claimed": False,
        },
        "threshold_contract_review": {
            "contract_complete": True,
            "family_threshold_count": 2,
            "families": list(thresholds.keys()),
            "threshold_rule_summary": {
                family: {
                    feature: {"operator": rule["operator"], "value": rule["value"]}
                    for feature, rule in rules.items()
                    if feature in FEATURES
                }
                for family, rules in thresholds.items()
            },
        },
        "data_source_review": {
            "candidate_source_count": len(sources),
            "readable_okx_1m_source_count": len(readable_sources),
            "readable_symbols": [row["symbol"] for row in readable_sources],
        },
        "backtest_execution": results,
        "data_limitations": limitations,
        "gate_limitations": [
            "No exact global gate replay was available.",
            "No position-level gate allow was used; signals were evaluated as clean-room historical diagnostic trades.",
            "This diagnostic cannot prove no-position-without-gate behavior from historical gate decisions.",
        ],
        "null_baseline_result": results["null_baseline"],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()) and all(value is False for value in safety_permissions.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    metrics = results["execution_metrics"]
    split = results["split_metrics"]
    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"total_signals: {metrics['total_signals']}")
    print(f"executed_trades: {metrics['executed_trades']}")
    print(f"validation_net: {split['validation']['net_bps']}")
    print(f"holdout_net: {split['holdout']['net_bps']}")
    print(f"validation_monthly_positive_rate: {split['validation']['monthly_positive_rate']}")
    print(f"holdout_monthly_positive_rate: {split['holdout']['monthly_positive_rate']}")
    print(f"worst_month: {metrics['worst_month']}")
    print(f"null_baseline_result: {results['null_baseline']}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


def run_git(args: list[str], count_lines: bool = False) -> str:
    import subprocess

    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    output = completed.stdout.strip()
    if count_lines:
        return str(len([line for line in output.splitlines() if line.strip()]))
    return output


if __name__ == "__main__":
    sys.exit(main())
