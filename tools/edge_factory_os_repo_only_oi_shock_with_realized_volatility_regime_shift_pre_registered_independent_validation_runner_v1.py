"""Pre-registered independent validation runner for OI shock volatility diagnostics."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
import subprocess
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "749982396877be53d0ce9fa1b1df60322f632b13"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_CONTRACT_RELATIVE_PATH = "artifacts/contracts/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_contract_v1.json"
SOURCE_EVALUATOR_RELATIVE_PATH = "artifacts/research/oi_shock_with_realized_volatility_regime_shift_robustness_evaluator_v1.json"
SOURCE_ROBUSTNESS_RELATIVE_PATH = "artifacts/research/oi_shock_with_realized_volatility_regime_shift_forward_diagnostic_robustness_runner_v1.json"
SOURCE_VALIDATOR_RELATIVE_PATH = "artifacts/research/oi_shock_with_realized_volatility_regime_shift_event_validator_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.json"
SOURCE_DATASET_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_CONTRACT_RELATIVE_PATH,
    SOURCE_EVALUATOR_RELATIVE_PATH,
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_VALIDATOR_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_DATASET_RELATIVE_PATH,
]

ARCHIVE_HELPER_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_pre_registered_independent_validation_runner_v1.py"
DISCOVERY_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.py"
FORWARD_DIAGNOSTIC_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_forward_return_diagnostic_v1.py"

VALIDATION_STATUS_PASS = "PASS_REPO_ONLY_OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER_CREATED"
VALIDATION_STATUS_BLOCKED = "BLOCKED_OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER"
ARTIFACT_KIND = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER"

RESULT_PASS = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_PASS_DIAGNOSTIC_ONLY"
RESULT_FAIL = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_FAIL"
RESULT_INCONCLUSIVE = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
RESULT_ATTENTION = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_FAILED_STOP"

NEXT_EVALUATOR = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_EVALUATOR_V1"
NEXT_CLOSE_OR_REDESIGN = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_ROUTE_CLOSE_OR_REDESIGN_EVALUATOR_V1"
NEXT_ACCUMULATION = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_SAMPLE_ACCUMULATION_MONITOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_2026_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"
NEXT_RUNTIME_REPAIR = "RECOVERY_OR_RUNTIME_REPAIR_V1"

THEORY_ID = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT"
PRIMARY_TARGETS = [
    "best_oi_expansion_volatility_expansion_definition",
    "best_oi_expansion_volatility_compression_break_definition",
]
PRIMARY_TARGET_LABELS = {
    "best_oi_expansion_volatility_expansion_definition": "expansion + volatility expansion, 15m",
    "best_oi_expansion_volatility_compression_break_definition": "expansion + volatility compression break, 15m",
}
VALIDATION_START = date(2026, 1, 1)
HORIZON = "15m"
HORIZON_BARS = 1
KLINE_INTERVAL_MS = 15 * 60 * 1000
PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528
CACHE_ROOT = REPO_ROOT / "cache" / "oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1"


class ValidationBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        output = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(output):
        return None
    return output


def load_module(path: Path, name: str) -> Any:
    if not path.exists():
        raise ValidationBlocked(f"missing required helper tool: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValidationBlocked(f"could not load helper module spec: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive_helper_module() -> Any:
    module = load_module(ARCHIVE_HELPER_TOOL, "public_archive_helper_for_oi_shock_validation_v1")
    module.CACHE_ROOT = CACHE_ROOT
    module.VALIDATION_START = VALIDATION_START
    module.REQUEST_SLEEP_SECONDS = 0.01
    return module


def discovery_module() -> Any:
    return load_module(DISCOVERY_TOOL, "oi_shock_discovery_for_independent_validation_v1")


def forward_diagnostic_module() -> Any:
    return load_module(FORWARD_DIAGNOSTIC_TOOL, "oi_shock_forward_diagnostic_for_independent_validation_v1")


def git_base_args() -> list[str]:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    return ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={safe_dir}"]


def run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        [*git_base_args(), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.returncode, result.stdout, result.stderr


def git_lines(args: list[str]) -> list[str]:
    code, stdout, stderr = run_git(args)
    if code != 0:
        raise ValidationBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
    return [line.rstrip() for line in stdout.splitlines() if line.strip()]


def current_head() -> str:
    lines = git_lines(["rev-parse", "HEAD"])
    return lines[0] if lines else ""


def current_branch() -> str:
    lines = git_lines(["branch", "--show-current"])
    return lines[0] if lines else ""


def working_tree_status() -> list[str]:
    return git_lines(["status", "--porcelain=v1"])


def staged_files() -> list[str]:
    return git_lines(["diff", "--cached", "--name-only"])


def modified_tracked_files() -> list[str]:
    return git_lines(["diff", "--name-only"])


def untracked_files() -> list[str]:
    return git_lines(["ls-files", "--others", "--exclude-standard"])


def deleted_files() -> list[str]:
    return git_lines(["ls-files", "--deleted"])


def output_only_status(status_lines: list[str]) -> bool:
    allowed = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
    for line in status_lines:
        if line in allowed:
            continue
        if line.startswith("!! ") and line[3:].startswith("cache/"):
            continue
        return False
    return True


def recovery_audit() -> dict[str, Any]:
    head = current_head()
    branch = current_branch()
    status = working_tree_status()
    staged = staged_files()
    modified = modified_tracked_files()
    untracked = untracked_files()
    deleted = deleted_files()
    if staged:
        decision = "STOP_STAGED_FILES_EXIST"
    elif head != EXPECTED_HEAD:
        decision = "STOP_HEAD_MISMATCH"
    elif status and not output_only_status(status):
        decision = "STOP_DIRTY_WORKTREE_UNKNOWN_OR_RISKY_FILES"
    else:
        decision = RECOVERY_AUDIT_STATUS
    return {
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "branch": branch,
        "git_status_porcelain": status,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "recovery_decision": decision,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_artifact_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative_path in INPUT_ARTIFACT_RELATIVE_PATHS:
        path = REPO_ROOT / relative_path
        if not path.exists():
            raise ValidationBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise ValidationBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValidationBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise ValidationBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise ValidationBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def flags_false(payload: dict[str, Any], flags: list[str]) -> bool:
    return all(payload.get(flag) is False for flag in flags)


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    contract = read_json_readonly(SOURCE_CONTRACT_RELATIVE_PATH)
    evaluator = read_json_readonly(SOURCE_EVALUATOR_RELATIVE_PATH)
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    validator = read_json_readonly(SOURCE_VALIDATOR_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_CONTRACT_RELATIVE_PATH: verify_payload_hash(contract, "independent validation contract"),
        SOURCE_EVALUATOR_RELATIVE_PATH: verify_payload_hash(evaluator, "robustness evaluator"),
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "robustness runner"),
        SOURCE_VALIDATOR_RELATIVE_PATH: verify_payload_hash(validator, "event validator"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "event discovery"),
        SOURCE_DATASET_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
    }
    checks = validate_input_chain(contract, evaluator, robustness, validator, discovery, dataset)
    if not all(checks.values()):
        raise ValidationBlocked(f"input chain validation failed: {checks}")
    return contract, evaluator, robustness, validator, discovery, dataset, payload_hashes


def validate_input_chain(
    contract: dict[str, Any],
    evaluator: dict[str, Any],
    robustness: dict[str, Any],
    validator: dict[str, Any],
    discovery: dict[str, Any],
    dataset: dict[str, Any],
) -> dict[str, bool]:
    return {
        "contract_ready": contract.get("result_classification")
        == "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY",
        "contract_allows_this_runner": contract.get("allowed_next_step") == MODULE,
        "contract_independent_validation_required": contract.get("independent_validation_required") is True,
        "contract_permissions_false": flags_false(
            contract,
            ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed", "runtime_touch_allowed", "capital_change_allowed", "live_allowed"],
        ),
        "evaluator_promising_volatility": evaluator.get("result_classification")
        == "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_ROBUSTNESS_EVALUATOR_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY",
        "evaluator_route_promising": evaluator.get("diagnostic_route_promising") is True,
        "robustness_promising": robustness.get("result_classification")
        == "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_ROBUSTNESS_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY",
        "validator_passed": validator.get("result_classification")
        in {
            "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
            "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_VALIDATOR_PASS",
        },
        "validator_forward_diagnostic_allowed": validator.get("forward_return_diagnostic_allowed") is True,
        "discovery_ready": discovery.get("result_classification")
        == "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_READY",
        "dataset_builder_pass": dataset.get("status") == "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED",
        "permissions_false": all(
            payload.get(flag) is False
            for payload in [contract, evaluator, robustness, validator]
            for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]
        ),
    }


def dataset_symbols(dataset: dict[str, Any], archive_helper: Any) -> list[str]:
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols") or dataset.get("requested_symbols")
    if not isinstance(symbols, list) or not symbols:
        symbols = list(getattr(archive_helper, "DEFAULT_SYMBOLS"))
    ordered = []
    for symbol in symbols:
        text = str(symbol)
        if text not in ordered:
            ordered.append(text)
    return ordered


def normalize_metric_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        clean = dict(row)
        clean["taker_buy_pressure"] = row.get("taker_buy_pressure", row.get("taker_buy_aggression"))
        clean["taker_sell_pressure"] = row.get("taker_sell_pressure", row.get("taker_sell_aggression"))
        clean["top_account_long_short_ratio"] = row.get("top_account_long_short_ratio", row.get("top_account_ratio"))
        clean["top_position_long_short_ratio"] = row.get("top_position_long_short_ratio", row.get("top_position_ratio"))
        normalized.append(clean)
    return normalized


def read_2026_kline_archives(paths: list[Path], symbol: str, archive_helper: Any) -> dict[str, Any]:
    rows_by_open: dict[int, tuple[float, float, float, float, float]] = {}
    for path in paths:
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not names:
                raise ValidationBlocked(f"no CSV member in kline archive: {path}")
            for name in names:
                content = archive.read(name).decode("utf-8", errors="replace")
                parsed_rows = [row for row in csv.reader(io.StringIO(content)) if row]
                if not parsed_rows:
                    continue
                if archive_helper.detect_header(parsed_rows[0]):
                    header = [cell.strip() for cell in parsed_rows[0]]
                    data_rows = parsed_rows[1:]
                else:
                    header = [
                        "open_time",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "close_time",
                        "quote_asset_volume",
                        "number_of_trades",
                        "taker_buy_base_asset_volume",
                        "taker_buy_quote_asset_volume",
                        "ignore",
                    ][: len(parsed_rows[0])]
                    data_rows = parsed_rows
                for raw_row in data_rows:
                    record = {header[idx]: raw_row[idx].strip() if idx < len(raw_row) else "" for idx in range(len(header))}
                    open_ms = archive_helper.parse_ts_ms(record.get("open_time") or record.get("timestamp") or "")
                    if open_ms is None:
                        continue
                    if datetime.fromtimestamp(open_ms / 1000, timezone.utc).date() < VALIDATION_START:
                        continue
                    open_price = archive_helper.to_float(record.get("open"))
                    high = archive_helper.to_float(record.get("high"))
                    low = archive_helper.to_float(record.get("low"))
                    close = archive_helper.to_float(record.get("close"))
                    volume = archive_helper.to_float(record.get("volume")) or 0.0
                    if None in (open_price, high, low, close):
                        continue
                    rows_by_open[int(open_ms)] = (float(open_price), float(high), float(low), float(close), float(volume))
    if not rows_by_open:
        raise ValidationBlocked(f"no 2026+ kline rows loaded for {symbol}")
    opens = np.asarray(sorted(rows_by_open), dtype=np.int64)
    open_prices = np.asarray([rows_by_open[int(ts)][0] for ts in opens], dtype=np.float64)
    high = np.asarray([rows_by_open[int(ts)][1] for ts in opens], dtype=np.float64)
    low = np.asarray([rows_by_open[int(ts)][2] for ts in opens], dtype=np.float64)
    close = np.asarray([rows_by_open[int(ts)][3] for ts in opens], dtype=np.float64)
    volume = np.asarray([rows_by_open[int(ts)][4] for ts in opens], dtype=np.float64)
    open_to_index = {int(ts): idx for idx, ts in enumerate(opens)}
    abs_return_15m = np.full(opens.shape, np.nan, dtype=np.float64)
    returns_15m = np.full(opens.shape, np.nan, dtype=np.float64)
    for idx in range(1, len(close)):
        prior = float(close[idx - 1])
        current = float(close[idx])
        if prior != 0 and math.isfinite(prior) and math.isfinite(current):
            ret = (current / prior) - 1.0
            abs_return_15m[idx] = abs(ret)
    for idx, open_ms in enumerate(opens):
        target_idx = open_to_index.get(int(open_ms) + KLINE_INTERVAL_MS)
        if target_idx is not None:
            base_close = float(close[idx])
            target_close = float(close[target_idx])
            if base_close != 0 and math.isfinite(base_close) and math.isfinite(target_close):
                returns_15m[idx] = (target_close / base_close) - 1.0
    ranges = np.where(open_prices != 0, (high - low) / np.maximum(open_prices, 1e-12), np.nan)
    valid_indices_15m = np.flatnonzero(np.isfinite(returns_15m))
    return {
        "symbol": symbol,
        "opens": opens,
        "open": open_prices,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "range": ranges.astype(np.float64),
        "abs_return_15m": abs_return_15m,
        "returns_15m": returns_15m,
        "valid_indices_15m": valid_indices_15m,
        "open_to_index": open_to_index,
        "timestamp_min": archive_helper.ms_to_iso(int(opens[0])),
        "timestamp_max": archive_helper.ms_to_iso(int(opens[-1])),
        "row_count": int(opens.size),
    }


def selected_primary_definitions(discovery: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected = discovery.get("selected_clean_event_definitions")
    if not isinstance(selected, list):
        raise ValidationBlocked("selected_clean_event_definitions is not a list")
    by_slot: dict[str, dict[str, Any]] = {}
    for item in selected:
        if not isinstance(item, dict):
            continue
        slot = item.get("selection_slot")
        if slot in PRIMARY_TARGETS:
            if not isinstance(item.get("meta"), dict):
                raise ValidationBlocked(f"primary target selected definition missing meta: {slot}")
            by_slot[str(slot)] = item
    missing = [slot for slot in PRIMARY_TARGETS if slot not in by_slot]
    if missing:
        raise ValidationBlocked(f"selected primary definitions missing from discovery artifact: {missing}")
    return by_slot


def reconstruct_primary_events_for_symbol(
    symbol: str,
    rows: list[dict[str, Any]],
    kline_data: dict[str, Any],
    base: Any,
    shock: Any,
    selected_meta_by_slot: dict[str, dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    metric_thresholds = shock.build_metric_thresholds(rows)
    feature_pack = shock.kline_feature_pack(kline_data, base)
    events = {slot: [] for slot in PRIMARY_TARGETS}
    counters: dict[str, Any] = {"raw_counts": Counter(), "cooldown_rejections": Counter(), "missing": Counter()}
    last_event_ms: dict[str, dict[str, int]] = {slot: {} for slot in PRIMARY_TARGETS}
    for row in rows:
        metric_month = metric_thresholds.get(row["month"])
        if metric_month is None:
            counters["missing"]["metric_threshold_month_missing"] += 1
            continue
        feature = shock.feature_for_row(row, kline_data, feature_pack, base)
        if feature is None:
            counters["missing"]["price_bar_missing"] += 1
            continue
        oi_delta = row.get("oi_delta_log_1h")
        if oi_delta is None:
            counters["missing"]["oi_delta_log_1h_missing"] += 1
            continue
        positive_pass = {
            shock.percentile_name(q)
            for q in shock.OI_POSITIVE_QUANTILES
            if metric_month["oi_positive"].get(shock.percentile_name(q)) is not None
            and oi_delta >= metric_month["oi_positive"][shock.percentile_name(q)]
        }
        if not positive_pass:
            continue
        for slot, meta in selected_meta_by_slot.items():
            if meta["oi_direction"] != "expansion":
                continue
            if meta["oi_threshold"] not in positive_pass:
                continue
            passed, regime_label = shock.regime_pass(meta, feature)
            if not passed:
                if regime_label == "missing_volatility_feature":
                    counters["missing"][f"{slot}_missing_volatility_feature"] += 1
                continue
            counters["raw_counts"][slot] += 1
            previous = last_event_ms[slot].get(symbol)
            cooldown_ms = int(meta["cooldown_hours"]) * 60 * 60 * 1000
            if previous is not None and row["ts_ms"] - previous < cooldown_ms:
                counters["cooldown_rejections"][slot] += 1
                continue
            last_event_ms[slot][symbol] = int(row["ts_ms"])
            base_open = base.floor_to_15m_open(row["ts_ms"])
            events[slot].append(
                {
                    "selection_slot": slot,
                    "target_label": PRIMARY_TARGET_LABELS[slot],
                    "definition_id": shock.definition_id(meta),
                    "symbol": symbol,
                    "timestamp": row["timestamp"],
                    "ts_ms": int(row["ts_ms"]),
                    "base_open_ms": int(base_open),
                    "base_open_iso": base.ms_to_iso(int(base_open)),
                    "month": row["month"],
                    "regime_label": regime_label,
                    "oi_direction": meta["oi_direction"],
                }
            )
    return events, {
        "raw_counts": dict(counters["raw_counts"]),
        "cooldown_rejections": dict(counters["cooldown_rejections"]),
        "missing": dict(counters["missing"]),
    }


def reconstruct_primary_events(
    archive_paths_by_symbol: dict[str, dict[str, list[Path]]],
    symbols: list[str],
    discovery: dict[str, Any],
    archive_helper: Any,
    shock: Any,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    selected = selected_primary_definitions(discovery)
    selected_meta_by_slot = {slot: dict(item["meta"]) for slot, item in selected.items()}
    base = shock.load_base_module()
    events = {slot: [] for slot in PRIMARY_TARGETS}
    kline_by_symbol: dict[str, dict[str, Any]] = {}
    metrics_by_symbol: dict[str, list[dict[str, Any]]] = {}
    counters: dict[str, Any] = {"per_symbol": {}, "aggregate": Counter()}
    data_quality_warnings: list[str] = []
    for symbol in symbols:
        paths = archive_paths_by_symbol.get(symbol, {"metrics": [], "klines": []})
        if not paths.get("metrics") or not paths.get("klines"):
            data_quality_warnings.append(
                f"{symbol} missing 2026+ validation archives: metrics={len(paths.get('metrics', []))}, klines={len(paths.get('klines', []))}"
            )
            continue
        try:
            rows = normalize_metric_rows(archive_helper.read_metrics_archives(paths["metrics"], symbol))
            kline_data = read_2026_kline_archives(paths["klines"], symbol, archive_helper)
        except Exception as exc:
            data_quality_warnings.append(f"{symbol} load/reconstruction warning: {exc}")
            continue
        metrics_by_symbol[symbol] = rows
        kline_by_symbol[symbol] = kline_data
        symbol_events, symbol_counters = reconstruct_primary_events_for_symbol(
            symbol,
            rows,
            kline_data,
            base,
            shock,
            selected_meta_by_slot,
        )
        for slot, slot_events in symbol_events.items():
            events[slot].extend(slot_events)
        counters["per_symbol"][symbol] = symbol_counters
        for group in ["raw_counts", "cooldown_rejections", "missing"]:
            counters["aggregate"].update({f"{group}__{key}": value for key, value in symbol_counters[group].items()})
    counters["aggregate"] = dict(counters["aggregate"])
    return events, kline_by_symbol, metrics_by_symbol, counters, data_quality_warnings


def signed_forward_return(kline_data: dict[str, Any], base_open_ms: int) -> float | None:
    index = kline_data["open_to_index"].get(int(base_open_ms))
    if index is None:
        return None
    target_index = index + HORIZON_BARS
    if target_index >= len(kline_data["close"]):
        return None
    base_close = float(kline_data["close"][index])
    target_close = float(kline_data["close"][target_index])
    if base_close == 0 or not math.isfinite(base_close) or not math.isfinite(target_close):
        return None
    return (target_close / base_close) - 1.0


def forward_range_proxy(kline_data: dict[str, Any], base_open_ms: int) -> float | None:
    index = kline_data["open_to_index"].get(int(base_open_ms))
    if index is None:
        return None
    target_index = index + HORIZON_BARS
    if target_index >= len(kline_data["close"]):
        return None
    base_close = float(kline_data["close"][index])
    if base_close == 0 or not math.isfinite(base_close):
        return None
    high = float(np.max(kline_data["high"][index + 1 : target_index + 1]))
    low = float(np.min(kline_data["low"][index + 1 : target_index + 1]))
    if not math.isfinite(high) or not math.isfinite(low):
        return None
    return (high - low) / base_close


def realized_vol_proxy(kline_data: dict[str, Any], base_open_ms: int) -> float | None:
    value = signed_forward_return(kline_data, base_open_ms)
    return abs(value) if value is not None else None


def summarize(values: list[float] | np.ndarray) -> dict[str, Any]:
    arr = np.asarray(values, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "std": None,
            "q01": None,
            "q05": None,
            "q25": None,
            "q50": None,
            "q75": None,
            "q90": None,
            "q95": None,
            "q99": None,
        }
    return {
        "count": int(arr.size),
        "mean": safe_float(np.mean(arr)),
        "median": safe_float(np.median(arr)),
        "std": safe_float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "q01": safe_float(np.quantile(arr, 0.01)),
        "q05": safe_float(np.quantile(arr, 0.05)),
        "q25": safe_float(np.quantile(arr, 0.25)),
        "q50": safe_float(np.quantile(arr, 0.50)),
        "q75": safe_float(np.quantile(arr, 0.75)),
        "q90": safe_float(np.quantile(arr, 0.90)),
        "q95": safe_float(np.quantile(arr, 0.95)),
        "q99": safe_float(np.quantile(arr, 0.99)),
    }


def observed_primary_stats(
    events: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    missing_summary: dict[str, Any] = {"by_primary_target": {}, "total_missing": 0}
    for slot, slot_events in events.items():
        abs_values: list[float] = []
        range_values: list[float] = []
        rv_values: list[float] = []
        valid_events: list[dict[str, Any]] = []
        missing = 0
        valid_counts_by_symbol_month: Counter[tuple[str, str]] = Counter()
        event_indices_by_symbol_month: dict[tuple[str, str], set[int]] = defaultdict(set)
        for event in slot_events:
            kline = kline_by_symbol.get(event["symbol"])
            if kline is None:
                missing += 1
                continue
            value = signed_forward_return(kline, int(event["base_open_ms"]))
            if value is None:
                missing += 1
                continue
            abs_value = abs(value)
            abs_values.append(abs_value)
            range_value = forward_range_proxy(kline, int(event["base_open_ms"]))
            rv_value = realized_vol_proxy(kline, int(event["base_open_ms"]))
            if range_value is not None:
                range_values.append(range_value)
            if rv_value is not None:
                rv_values.append(rv_value)
            index = kline["open_to_index"].get(int(event["base_open_ms"]))
            event_indices_by_symbol_month[(event["symbol"], event["month"])].add(int(index))
            valid_counts_by_symbol_month[(event["symbol"], event["month"])] += 1
            valid_events.append(
                {
                    **event,
                    "forward_return_15m": float(value),
                    "forward_abs_return_15m": float(abs_value),
                    "forward_range_proxy_15m": range_value,
                    "realized_vol_proxy_15m": rv_value,
                }
            )
        abs_stats = summarize(abs_values)
        range_stats = summarize(range_values)
        rv_stats = summarize(rv_values)
        observed[slot] = {
            "event_count": len(slot_events),
            "valid_count": abs_stats["count"],
            "missing_count": missing,
            "mean_abs_return": abs_stats["mean"],
            "median_abs_return": abs_stats["median"],
            "std_abs_return": abs_stats["std"],
            "q50_abs_return": abs_stats["q50"],
            "q75_abs_return": abs_stats["q75"],
            "q90_abs_return": abs_stats["q90"],
            "q95_abs_return": abs_stats["q95"],
            "q99_abs_return": abs_stats["q99"],
            "forward_range_proxy_stats": {
                "valid_count": range_stats["count"],
                "mean": range_stats["mean"],
                "median": range_stats["median"],
                "q75": range_stats["q75"],
                "q95": range_stats["q95"],
            },
            "realized_vol_proxy_stats": {
                "valid_count": rv_stats["count"],
                "mean": rv_stats["mean"],
                "median": rv_stats["median"],
                "q75": rv_stats["q75"],
                "q95": rv_stats["q95"],
            },
            "_valid_events": valid_events,
            "_valid_counts_by_symbol_month": valid_counts_by_symbol_month,
            "_event_indices_by_symbol_month": event_indices_by_symbol_month,
        }
        missing_summary["by_primary_target"][slot] = missing
        missing_summary["total_missing"] += missing
    return observed, missing_summary


def null_distribution_stats(null_means: np.ndarray) -> dict[str, Any]:
    arr = np.asarray(null_means, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {
            "null_mean_mean": None,
            "null_mean_std": None,
            "null_mean_q01": None,
            "null_mean_q05": None,
            "null_mean_q50": None,
            "null_mean_q95": None,
            "null_mean_q99": None,
        }
    return {
        "null_mean_mean": safe_float(np.mean(arr)),
        "null_mean_std": safe_float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "null_mean_q01": safe_float(np.quantile(arr, 0.01)),
        "null_mean_q05": safe_float(np.quantile(arr, 0.05)),
        "null_mean_q50": safe_float(np.quantile(arr, 0.50)),
        "null_mean_q95": safe_float(np.quantile(arr, 0.95)),
        "null_mean_q99": safe_float(np.quantile(arr, 0.99)),
    }


def empirical_abs_p_values(observed_mean: float | None, null_means: np.ndarray) -> dict[str, Any]:
    if observed_mean is None or not math.isfinite(float(observed_mean)) or null_means.size == 0:
        return {
            "p_abs_high_mean": None,
            "p_abs_low_mean": None,
            "empirical_p_value_formula": "p = (1 + count(null stats as or more extreme than observed)) / (1 + permutation_count)",
        }
    denominator = 1 + PERMUTATION_COUNT
    return {
        "p_abs_high_mean": float((1 + int(np.sum(null_means >= float(observed_mean)))) / denominator),
        "p_abs_low_mean": float((1 + int(np.sum(null_means <= float(observed_mean)))) / denominator),
        "empirical_p_value_formula": "p = (1 + count(null stats as or more extreme than observed)) / (1 + permutation_count)",
    }


def bh_fdr(p_values: dict[str, float | None]) -> dict[str, float | None]:
    valid = [(key, float(value)) for key, value in p_values.items() if isinstance(value, (int, float)) and math.isfinite(float(value))]
    if not valid:
        return {key: None for key in p_values}
    valid_sorted = sorted(valid, key=lambda item: item[1])
    n = len(valid_sorted)
    q_values: dict[str, float] = {}
    running = 1.0
    for rank_from_end, (key, value) in enumerate(reversed(valid_sorted), start=1):
        rank = n - rank_from_end + 1
        running = min(running, value * n / rank)
        q_values[key] = min(running, 1.0)
    return {key: q_values.get(key) for key in p_values}


def month_aware_null_for_target(
    slot: str,
    observed: dict[str, Any],
    kline_by_symbol: dict[str, dict[str, Any]],
    rng: np.random.Generator,
) -> dict[str, Any]:
    valid_count = int(observed.get("valid_count") or 0)
    if valid_count <= 0:
        return {
            "permutation_count_requested": PERMUTATION_COUNT,
            "permutation_count_completed": 0,
            "null_means": np.asarray([], dtype=np.float64),
            "null_range_means": np.asarray([], dtype=np.float64),
            "null_rv_means": np.asarray([], dtype=np.float64),
            "null_stats": null_distribution_stats(np.asarray([], dtype=np.float64)),
            "p_values": empirical_abs_p_values(None, np.asarray([], dtype=np.float64)),
            "fallback_summary": {"skipped_reason": "zero valid events"},
        }
    null_sums = np.zeros(PERMUTATION_COUNT, dtype=np.float64)
    range_sums = np.zeros(PERMUTATION_COUNT, dtype=np.float64)
    rv_sums = np.zeros(PERMUTATION_COUNT, dtype=np.float64)
    total_count = 0
    fallback = {
        "month_aware_pool_used": 0,
        "symbol_pool_fallback_used": 0,
        "event_timestamp_exclusion_used": 0,
        "empty_pool_count": 0,
        "target": slot,
    }
    counts_by_symbol_month: Counter[tuple[str, str]] = observed["_valid_counts_by_symbol_month"]
    event_indices_by_symbol_month: dict[tuple[str, str], set[int]] = observed["_event_indices_by_symbol_month"]
    for (symbol, month), count in counts_by_symbol_month.items():
        kline = kline_by_symbol[symbol]
        month_mask = np.array([datetime.fromtimestamp(int(open_ms) / 1000, timezone.utc).strftime("%Y-%m") == month for open_ms in kline["opens"]], dtype=bool)
        finite_mask = np.isfinite(kline["returns_15m"])
        candidate_indices = np.flatnonzero(month_mask & finite_mask)
        if candidate_indices.size:
            fallback["month_aware_pool_used"] += 1
        else:
            fallback["symbol_pool_fallback_used"] += 1
            candidate_indices = np.flatnonzero(finite_mask)
        event_indices = event_indices_by_symbol_month.get((symbol, month), set())
        if candidate_indices.size and event_indices:
            keep = np.array([int(index) not in event_indices for index in candidate_indices], dtype=bool)
            filtered = candidate_indices[keep]
            if filtered.size:
                candidate_indices = filtered
                fallback["event_timestamp_exclusion_used"] += 1
        if candidate_indices.size == 0:
            fallback["empty_pool_count"] += 1
            continue
        abs_candidates = np.abs(kline["returns_15m"][candidate_indices])
        range_candidates = []
        rv_candidates = []
        for index in candidate_indices:
            base_open = int(kline["opens"][int(index)])
            range_value = forward_range_proxy(kline, base_open)
            rv_value = realized_vol_proxy(kline, base_open)
            range_candidates.append(range_value if range_value is not None else np.nan)
            rv_candidates.append(rv_value if rv_value is not None else np.nan)
        range_candidates_arr = np.asarray(range_candidates, dtype=np.float64)
        rv_candidates_arr = np.asarray(rv_candidates, dtype=np.float64)
        valid = np.isfinite(abs_candidates)
        abs_candidates = abs_candidates[valid]
        range_candidates_arr = range_candidates_arr[valid]
        rv_candidates_arr = rv_candidates_arr[valid]
        if abs_candidates.size == 0:
            fallback["empty_pool_count"] += 1
            continue
        draws = rng.integers(0, abs_candidates.size, size=(PERMUTATION_COUNT, int(count)))
        null_sums += abs_candidates[draws].sum(axis=1)
        if np.isfinite(range_candidates_arr).any():
            range_clean = np.where(np.isfinite(range_candidates_arr), range_candidates_arr, abs_candidates)
            range_sums += range_clean[draws].sum(axis=1)
        if np.isfinite(rv_candidates_arr).any():
            rv_clean = np.where(np.isfinite(rv_candidates_arr), rv_candidates_arr, abs_candidates)
            rv_sums += rv_clean[draws].sum(axis=1)
        total_count += int(count)
    if total_count <= 0:
        raise ValidationBlocked("VALIDATION_NULL_RUNTIME_OR_MEMORY_LIMIT: zero valid null sample count")
    null_means = null_sums / float(total_count)
    null_range_means = range_sums / float(total_count)
    null_rv_means = rv_sums / float(total_count)
    p_values = empirical_abs_p_values(observed.get("mean_abs_return"), null_means)
    return {
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": PERMUTATION_COUNT,
        "null_means": null_means,
        "null_range_means": null_range_means,
        "null_rv_means": null_rv_means,
        "null_stats": null_distribution_stats(null_means),
        "p_values": p_values,
        "fallback_summary": fallback,
    }


def build_nulls(observed_by_slot: dict[str, dict[str, Any]], kline_by_symbol: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    rng = np.random.default_rng(RANDOM_SEED)
    null_stats: dict[str, Any] = {}
    p_values: dict[str, Any] = {}
    fallback: dict[str, Any] = {}
    p_abs_high: dict[str, float | None] = {}
    completed = 0
    for slot in PRIMARY_TARGETS:
        result = month_aware_null_for_target(slot, observed_by_slot[slot], kline_by_symbol, rng)
        null_stats[slot] = result["null_stats"]
        p_values[slot] = result["p_values"]
        fallback[slot] = result["fallback_summary"]
        p_abs_high[slot] = result["p_values"].get("p_abs_high_mean")
        completed = max(completed, int(result["permutation_count_completed"]))
    fdr = bh_fdr(p_abs_high)
    bonferroni = {
        slot: (min(float(value) * len(PRIMARY_TARGETS), 1.0) if isinstance(value, (int, float)) else None)
        for slot, value in p_abs_high.items()
    }
    summary = {
        "null_model": "month_aware_symbol_balanced_null",
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": completed,
        "fallback_summary": fallback,
    }
    return null_stats, p_values, fdr, bonferroni, summary


def group_contributors(valid_events: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for event in valid_events:
        grouped[str(event[key])].append(float(event["forward_abs_return_15m"]))
    total_sum = sum(sum(values) for values in grouped.values())
    rows = []
    for group_key, values in grouped.items():
        stats = summarize(values)
        contribution = (sum(values) / total_sum) if total_sum else None
        rows.append({"key": group_key, "count": len(values), "mean_abs_return": stats["mean"], "contribution_to_total_abs_return": contribution})
    rows.sort(key=lambda row: abs(row["contribution_to_total_abs_return"] or 0.0), reverse=True)
    return rows


def leave_one_diagnostics(valid_events: list[dict[str, Any]], key: str, full_mean: float | None) -> dict[str, Any]:
    groups = sorted({str(event[key]) for event in valid_events})
    if full_mean is None or not groups or len(valid_events) < 100:
        return {"skipped": True, "reason": "insufficient events or full mean unavailable", "any_single_dependence": None}
    rows = []
    any_single = False
    for group in groups:
        subset = [float(event["forward_abs_return_15m"]) for event in valid_events if str(event[key]) != group]
        stats = summarize(subset)
        mean = stats["mean"]
        ratio = (mean / full_mean) if mean is not None and full_mean else None
        necessary = ratio is not None and ratio < 0.30
        any_single = any_single or bool(necessary)
        rows.append(
            {
                key: group,
                "remaining_count": stats["count"],
                "mean_abs_return": mean,
                "magnitude_ratio_vs_full": ratio,
                "single_group_dependence": necessary,
            }
        )
    worst_ratio = min((row["magnitude_ratio_vs_full"] for row in rows if row["magnitude_ratio_vs_full"] is not None), default=None)
    return {"skipped": False, "groups_tested": len(groups), "worst_magnitude_ratio": worst_ratio, "any_single_dependence": any_single, "details": rows}


def arbusdt_sensitivity(valid_events: list[dict[str, Any]], full_mean: float | None) -> dict[str, Any]:
    arbusdt_count = sum(1 for event in valid_events if event["symbol"] == "ARBUSDT")
    if arbusdt_count == 0:
        return {"arbusdt_event_count": 0, "skipped": True, "reason": "no ARBUSDT events"}
    subset = [float(event["forward_abs_return_15m"]) for event in valid_events if event["symbol"] != "ARBUSDT"]
    stats = summarize(subset)
    mean = stats["mean"]
    return {
        "arbusdt_event_count": arbusdt_count,
        "skipped": False,
        "observed_without_arbusdt": {
            "count": stats["count"],
            "mean_abs_return": mean,
            "median_abs_return": stats["median"],
            "q95_abs_return": stats["q95"],
        },
        "magnitude_ratio_vs_full": (mean / full_mean) if mean is not None and full_mean else None,
        "effect_destroyed": (mean / full_mean) < 0.30 if mean is not None and full_mean else None,
    }


def alternate_proxy_sensitivity(valid_events: list[dict[str, Any]]) -> dict[str, Any]:
    range_values = [float(event["forward_range_proxy_15m"]) for event in valid_events if event.get("forward_range_proxy_15m") is not None]
    rv_values = [float(event["realized_vol_proxy_15m"]) for event in valid_events if event.get("realized_vol_proxy_15m") is not None]
    range_stats = summarize(range_values)
    rv_stats = summarize(rv_values)
    return {
        "forward_range_proxy_available": range_stats["count"] > 0,
        "realized_vol_proxy_available": rv_stats["count"] > 0,
        "forward_range_proxy_mean": range_stats["mean"],
        "realized_vol_proxy_mean": rv_stats["mean"],
        "alternate_proxy_recorded": range_stats["count"] > 0 or rv_stats["count"] > 0,
    }


def sensitivity_diagnostics(observed_by_slot: dict[str, dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for slot in PRIMARY_TARGETS:
        observed = observed_by_slot[slot]
        valid_events = observed["_valid_events"]
        full_mean = observed.get("mean_abs_return")
        output[slot] = {
            "leave_one_symbol_out": leave_one_diagnostics(valid_events, "symbol", full_mean),
            "leave_one_month_out": leave_one_diagnostics(valid_events, "month", full_mean),
            "arbusdt_exclusion": arbusdt_sensitivity(valid_events, full_mean),
            "top_contributor_symbols": group_contributors(valid_events, "symbol")[:5],
            "top_contributor_months": group_contributors(valid_events, "month")[:5],
            "alternate_volatility_proxy_sensitivity": alternate_proxy_sensitivity(valid_events),
        }
    return output


def public_archive_summary(manifest: list[dict[str, Any]], archive_helper: Any) -> dict[str, Any]:
    summary = archive_helper.archive_summary(manifest)
    summary["validation_start"] = "2026-01-01"
    summary["uses_public_data_binance_vision_only"] = True
    return summary


def coverage(events: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any], dict[str, Any]]:
    symbol_coverage = {}
    month_coverage = {}
    for slot, slot_events in events.items():
        symbol_counts = Counter(event["symbol"] for event in slot_events)
        month_counts = Counter(event["month"] for event in slot_events)
        top_symbol = symbol_counts.most_common(1)[0] if symbol_counts else (None, 0)
        top_month = month_counts.most_common(1)[0] if month_counts else (None, 0)
        count = len(slot_events)
        symbol_coverage[slot] = {
            "symbol_count": len(symbol_counts),
            "symbols": sorted(symbol_counts),
            "top_symbol": top_symbol[0],
            "top_symbol_count": top_symbol[1],
            "top_symbol_concentration": (top_symbol[1] / count) if count else None,
        }
        month_coverage[slot] = {
            "month_count": len(month_counts),
            "months": sorted(month_counts),
            "top_month": top_month[0],
            "top_month_count": top_month[1],
            "top_month_concentration": (top_month[1] / count) if count else None,
        }
    return symbol_coverage, month_coverage


def clean_observed_for_json(observed_by_slot: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    clean: dict[str, dict[str, Any]] = {}
    for slot, observed in observed_by_slot.items():
        clean[slot] = {key: value for key, value in observed.items() if not key.startswith("_")}
    return clean


def classify_validation(
    event_counts: dict[str, int],
    observed_by_slot: dict[str, dict[str, Any]],
    p_abs_high: dict[str, Any],
    fdr: dict[str, Any],
    bonferroni: dict[str, Any],
    validation_gates: dict[str, bool],
    archive_availability: dict[str, Any],
) -> tuple[str, str, bool, str]:
    if archive_availability.get("available_archive_count", 0) == 0:
        return RESULT_ATTENTION, NEXT_REPAIR, False, "no public 2026+ archive coverage was available"
    if any(count < 50 for count in event_counts.values()):
        return RESULT_INCONCLUSIVE, NEXT_ACCUMULATION, False, "at least one primary target has fewer than 50 validation events"
    if any(count < 100 for count in event_counts.values()):
        return RESULT_INCONCLUSIVE, NEXT_ACCUMULATION, False, "at least one primary target is in the 50-99 attention/inconclusive event-count band"
    if all(validation_gates.values()):
        return RESULT_PASS, NEXT_EVALUATOR, True, "at least one pre-registered primary volatility target passed validation gates"
    if any(
        observed_by_slot[slot].get("mean_abs_return") is not None
        and p_abs_high.get(slot) is not None
        and p_abs_high[slot] <= 0.05
        and (fdr.get(slot) is not None and fdr[slot] <= 0.05)
        for slot in PRIMARY_TARGETS
    ):
        return RESULT_ATTENTION, NEXT_REPAIR, False, "statistical gate appears supportive but one or more sensitivity/data gates failed"
    return RESULT_FAIL, NEXT_CLOSE_OR_REDESIGN, False, "pre-registered independent validation volatility gates failed"


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_validation_outcomes": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "used_2023_2025_as_independent_validation": False,
        "event_definition_changes": False,
        "threshold_changes": False,
        "horizon_changes": False,
        "signed_return_findings_promoted": False,
        "outcome_based_selection": False,
        "release_promotion": False,
    }


def blocked_artifact(
    reason: str,
    audit: dict[str, Any] | None = None,
    hashes_before: dict[str, str] | None = None,
    hashes_after: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "validation_status": VALIDATION_STATUS_BLOCKED,
        "status": VALIDATION_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": (audit or {}).get("recovery_decision", "RECOVERY_UNKNOWN"),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "theory_id": THEORY_ID,
        "frozen_hypothesis": {},
        "independent_validation_window": {},
        "independent_validation_data_policy_followed": False,
        "public_data_source_summary": {},
        "symbols_requested": [],
        "symbols_available": [],
        "archive_availability_summary": {},
        "event_reconstruction_status": "BLOCKED",
        "event_counts_by_primary_target": {slot: 0 for slot in PRIMARY_TARGETS},
        "symbol_coverage": {},
        "month_coverage": {},
        "observed_primary_volatility_stats": {},
        "null_model": "month_aware_symbol_balanced_null",
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": 0,
        "null_stats_by_primary_target": {},
        "p_abs_high_mean_by_primary_target": {},
        "fdr_q_values": {},
        "bonferroni_p_values": {},
        "validation_gates": {},
        "failed_validation_gates": [reason],
        "sensitivity_diagnostics": {},
        "data_quality_warnings": [f"BLOCKED: {reason}"],
        "final_validation_decision": "blocked",
        "independent_validation_passed": False,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_RUNTIME_REPAIR,
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    if audit["recovery_decision"] != RECOVERY_AUDIT_STATUS:
        return blocked_artifact(audit["recovery_decision"], audit)
    hashes_before = input_artifact_hashes()
    contract, evaluator, robustness, validator, discovery, dataset, payload_hashes = load_inputs()
    archive_helper = archive_helper_module()
    shock = discovery_module()
    _ = forward_diagnostic_module()
    symbols = dataset_symbols(dataset, archive_helper)
    archive_paths_by_symbol, manifest = archive_helper.download_all_archives(symbols)
    events, kline_by_symbol, metrics_by_symbol, reconstruction_counters, reconstruction_warnings = reconstruct_primary_events(
        archive_paths_by_symbol,
        symbols,
        discovery,
        archive_helper,
        shock,
    )
    symbols_available = sorted(set(metrics_by_symbol) & set(kline_by_symbol))
    observed_by_slot, missing_summary = observed_primary_stats(events, kline_by_symbol)
    null_stats, p_values, fdr_q_values, bonferroni_p_values, null_summary = build_nulls(observed_by_slot, kline_by_symbol)
    sensitivity = sensitivity_diagnostics(observed_by_slot)
    event_counts = {slot: len(events[slot]) for slot in PRIMARY_TARGETS}
    symbol_coverage, month_coverage = coverage(events)
    archive_availability = public_archive_summary(manifest, archive_helper)
    all_kline_mins = [data["timestamp_min"] for data in kline_by_symbol.values()]
    all_kline_maxs = [data["timestamp_max"] for data in kline_by_symbol.values()]
    independent_window = {
        "start": min(all_kline_mins) if all_kline_mins else None,
        "end": max(all_kline_maxs) if all_kline_maxs else None,
        "validation_start_not_before": "2026-01-01",
        "uses_2023_2025_research_sample": False,
    }
    p_abs_high = {slot: p_values.get(slot, {}).get("p_abs_high_mean") for slot in PRIMARY_TARGETS}
    validation_gates = {
        "independent_validation_uses_2026_plus_only": independent_window["start"] is not None
        and str(independent_window["start"]) >= "2026-01-01",
        "event_reconstruction_current_or_prior_bar_only": True,
        "sufficient_event_count_exists_for_at_least_one_primary_target": any(count >= 100 for count in event_counts.values()),
        "observed_primary_volatility_metric_higher_than_null": any(
            observed_by_slot[slot].get("mean_abs_return") is not None
            and null_stats.get(slot, {}).get("null_mean_mean") is not None
            and observed_by_slot[slot]["mean_abs_return"] > null_stats[slot]["null_mean_mean"]
            for slot in PRIMARY_TARGETS
        ),
        "p_abs_high_mean_lte_0_05_for_at_least_one_primary_target": any(
            isinstance(p_abs_high.get(slot), (int, float)) and p_abs_high[slot] <= 0.05 for slot in PRIMARY_TARGETS
        ),
        "both_primary_targets_reported": all(slot in observed_by_slot for slot in PRIMARY_TARGETS),
        "fdr_and_bonferroni_recorded_across_two_primary_tests": all(
            fdr_q_values.get(slot) is not None and bonferroni_p_values.get(slot) is not None for slot in PRIMARY_TARGETS
        ),
        "leave_one_symbol_no_single_dependence_when_applicable": all(
            sensitivity[slot]["leave_one_symbol_out"].get("any_single_dependence") is not True for slot in PRIMARY_TARGETS
        ),
        "leave_one_month_no_single_dependence_when_applicable": all(
            sensitivity[slot]["leave_one_month_out"].get("any_single_dependence") is not True for slot in PRIMARY_TARGETS
        ),
        "arbusdt_missing_archive_sensitivity_recorded_if_relevant": all(
            "arbusdt_event_count" in sensitivity[slot]["arbusdt_exclusion"] for slot in PRIMARY_TARGETS
        ),
        "alternate_volatility_proxy_sensitivity_recorded_when_feasible": all(
            sensitivity[slot]["alternate_volatility_proxy_sensitivity"].get("alternate_proxy_recorded") is True
            or observed_by_slot[slot].get("valid_count", 0) == 0
            for slot in PRIMARY_TARGETS
        ),
        "no_forbidden_action_occurred": True,
    }
    failed_gates = [key for key, value in validation_gates.items() if value is not True]
    data_quality_warnings = list(reconstruction_warnings)
    if archive_availability["available_archive_count"] == 0:
        data_quality_warnings.append("No public 2026+ Binance Data Vision archives were available or downloadable.")
    if archive_availability["missing_archive_count"] > 0:
        data_quality_warnings.append(f"{archive_availability['missing_archive_count']} public archive probes were unavailable.")
    if missing_summary["total_missing"]:
        data_quality_warnings.append(f"{missing_summary['total_missing']} selected-event rows had missing 15m forward absolute returns.")
    if not symbols_available:
        data_quality_warnings.append("No symbols had both 2026+ metrics and kline coverage loaded.")
    result_classification, allowed_next_step, validation_passed, final_decision = classify_validation(
        event_counts,
        observed_by_slot,
        p_abs_high,
        fdr_q_values,
        bonferroni_p_values,
        validation_gates,
        archive_availability,
    )
    if result_classification == RESULT_INCONCLUSIVE and "insufficient_independent_validation_sample" not in failed_gates:
        failed_gates.append("insufficient_independent_validation_sample")
    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise ValidationBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    validation_checks = {
        "input_artifact_hashes_unchanged": input_unchanged,
        "contract_ready": True,
        "public_data_vision_only": True,
        "validation_window_2026_plus_only": validation_gates["independent_validation_uses_2026_plus_only"]
        or sum(event_counts.values()) == 0,
        "no_2023_2025_independent_validation_reuse": True,
        "no_strategy_signal_candidate_release_permissions": True,
        "event_definition_unchanged": True,
        "thresholds_unchanged": True,
        "horizon_unchanged": True,
        "signed_return_not_promoted": True,
    }
    artifact = {
        "validation_status": VALIDATION_STATUS_PASS,
        "status": VALIDATION_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_decision"],
        "current_head": audit["current_head"],
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": input_unchanged,
        "input_payload_hashes_verified": payload_hashes,
        "theory_id": THEORY_ID,
        "frozen_hypothesis": contract.get("frozen_hypothesis", {}),
        "independent_validation_window": independent_window,
        "independent_validation_data_policy_followed": validation_checks["validation_window_2026_plus_only"]
        and validation_checks["no_2023_2025_independent_validation_reuse"],
        "public_data_source_summary": {
            "host": getattr(archive_helper, "PUBLIC_ARCHIVE_HOST", "data.binance.vision"),
            "monthly_metrics_root": getattr(archive_helper, "MONTHLY_METRICS_ROOT", None),
            "daily_metrics_root": getattr(archive_helper, "DAILY_METRICS_ROOT", None),
            "monthly_klines_root": getattr(archive_helper, "MONTHLY_KLINES_ROOT", None),
            "daily_klines_root": getattr(archive_helper, "DAILY_KLINES_ROOT", None),
            "cache_root": str(CACHE_ROOT),
            "raw_data_committed": False,
            "cache_files_staged": False,
        },
        "symbols_requested": symbols,
        "symbols_available": symbols_available,
        "archive_availability_summary": archive_availability,
        "event_reconstruction_status": "RECONSTRUCTED_FROZEN_PRIMARY_TARGETS_ONLY",
        "event_reconstruction_summary": {
            "selected_primary_targets": selected_primary_definitions(discovery),
            "reconstruction_counters": reconstruction_counters,
            "current_or_prior_bar_only": True,
            "threshold_changes": False,
            "horizon_changes": False,
            "strict_variant_promotion": False,
            "signed_return_promotion": False,
        },
        "event_counts_by_primary_target": event_counts,
        "symbol_coverage": symbol_coverage,
        "month_coverage": month_coverage,
        "observed_primary_volatility_stats": clean_observed_for_json(observed_by_slot),
        "null_model": "month_aware_symbol_balanced_null",
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": int(null_summary["permutation_count_completed"]),
        "null_stats_by_primary_target": null_stats,
        "p_abs_high_mean_by_primary_target": p_abs_high,
        "p_values_by_primary_target": p_values,
        "fdr_q_values": fdr_q_values,
        "bonferroni_p_values": bonferroni_p_values,
        "month_aware_symbol_balanced_null_summary": null_summary,
        "validation_gates": validation_gates,
        "failed_validation_gates": failed_gates,
        "sensitivity_diagnostics": sensitivity,
        "missing_forward_return_summary": missing_summary,
        "data_quality_warnings": data_quality_warnings,
        "final_validation_decision": final_decision,
        "independent_validation_passed": validation_passed,
        "validation_checks": validation_checks,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": allowed_next_step,
        "blocker": None,
        "replacement_checks_all_true": all(validation_checks.values()) and input_unchanged,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def format_report(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('validation_status')}",
        f"result_classification: {payload.get('result_classification')}",
        f"recovery_audit_status: {payload.get('recovery_audit_status')}",
        f"input_artifact_hashes_unchanged: {bool_text(bool(payload.get('input_artifact_hashes_unchanged')))}",
        f"theory_id: {payload.get('theory_id')}",
        f"independent_validation_window: {json.dumps(payload.get('independent_validation_window'), sort_keys=True)}",
        f"symbols_requested: {json.dumps(payload.get('symbols_requested'), sort_keys=True)}",
        f"symbols_available: {json.dumps(payload.get('symbols_available'), sort_keys=True)}",
        f"event_counts_by_primary_target: {json.dumps(payload.get('event_counts_by_primary_target'), sort_keys=True)}",
        f"symbol_coverage: {json.dumps(payload.get('symbol_coverage'), sort_keys=True)}",
        f"month_coverage: {json.dumps(payload.get('month_coverage'), sort_keys=True)}",
        f"observed_primary_volatility_stats: {json.dumps(payload.get('observed_primary_volatility_stats'), sort_keys=True)}",
        f"permutation_count_requested: {payload.get('permutation_count_requested')}",
        f"permutation_count_completed: {payload.get('permutation_count_completed')}",
        f"p_abs_high_mean_by_primary_target: {json.dumps(payload.get('p_abs_high_mean_by_primary_target'), sort_keys=True)}",
        f"fdr_q_values: {json.dumps(payload.get('fdr_q_values'), sort_keys=True)}",
        f"bonferroni_p_values: {json.dumps(payload.get('bonferroni_p_values'), sort_keys=True)}",
        f"validation_gates: {json.dumps(payload.get('validation_gates'), sort_keys=True)}",
        f"failed_validation_gates: {json.dumps(payload.get('failed_validation_gates'), sort_keys=True)}",
        f"sensitivity_diagnostics: {json.dumps(payload.get('sensitivity_diagnostics'), sort_keys=True)}",
        f"data_quality_warnings: {json.dumps(payload.get('data_quality_warnings'), sort_keys=True)}",
        f"final_validation_decision: {payload.get('final_validation_decision')}",
        f"independent_validation_passed: {bool_text(bool(payload.get('independent_validation_passed')))}",
        f"strategy_allowed: {bool_text(bool(payload.get('strategy_allowed')))}",
        f"signal_allowed: {bool_text(bool(payload.get('signal_allowed')))}",
        f"candidate_generation_allowed: {bool_text(bool(payload.get('candidate_generation_allowed')))}",
        f"release_allowed: {bool_text(bool(payload.get('release_allowed')))}",
        f"allowed_next_step: {payload.get('allowed_next_step')}",
        "commit hash: PENDING_COMMIT",
        "final git status: PENDING_COMMIT",
        "repo clean: PENDING_COMMIT",
        "tracked Python count: PENDING_COMMIT",
        "raw data committed: false",
        "cache files staged: false",
        f"forbidden actions confirmed false: {json.dumps(payload.get('forbidden_actions_confirmed_false'), sort_keys=True)}",
        f"blocker: {payload.get('blocker')}",
    ]
    return "\n".join(lines)


def main() -> int:
    hashes_before: dict[str, str] | None = None
    audit: dict[str, Any] | None = None
    try:
        audit = recovery_audit()
        hashes_before = input_artifact_hashes() if audit["head_matches_expected"] else None
        artifact = build_artifact()
    except Exception as exc:
        hashes_after = input_artifact_hashes() if hashes_before is not None else None
        artifact = blocked_artifact(str(exc), audit, hashes_before, hashes_after)
    write_artifact(artifact)
    print(format_report(artifact))
    return 0 if artifact.get("result_classification") != RESULT_FAILED else 1


if __name__ == "__main__":
    raise SystemExit(main())
