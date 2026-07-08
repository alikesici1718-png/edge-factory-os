#!/usr/bin/env python3
"""BTC/ETH Binance Options implied-move availability diagnostic.

This module checks whether public Binance Data Vision option archives can
support provisional ATM straddle breakeven calculations at already-discovered
BTC/ETH volatility diagnostic event timestamps. It does not compute realized
moves, PnL, p-values, nulls, backtests, strategies, signals, or candidates.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
import re
import statistics
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


MODULE = "BTC_ETH_OPTIONS_IMPLIED_MOVE_AVAILABILITY_DIAGNOSTIC_V1"
EXPECTED_HEAD = "fb15238310b080a130c7120e6d7a63523fed5dc9"
REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_btc_eth_options_implied_move_availability_diagnostic_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/btc_eth_options_implied_move_availability_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

RESULT_READY = "BTC_ETH_OPTIONS_IMPLIED_MOVE_AVAILABILITY_READY"
RESULT_INSUFFICIENT = "BTC_ETH_OPTIONS_IMPLIED_MOVE_AVAILABILITY_INSUFFICIENT_OPTIONS_COVERAGE"
RESULT_DATA_QUALITY = "BTC_ETH_OPTIONS_IMPLIED_MOVE_AVAILABILITY_DATA_QUALITY_ATTENTION"
RESULT_DATA_UNAVAILABLE = "BTC_ETH_OPTIONS_IMPLIED_MOVE_AVAILABILITY_DATA_UNAVAILABLE"
RESULT_FAILED = "BTC_ETH_OPTIONS_IMPLIED_MOVE_AVAILABILITY_FAILED_STOP"
NEXT_READY = "BTC_ETH_REALIZED_MOVE_VS_IMPLIED_MOVE_DIAGNOSTIC_V1"
NEXT_INSUFFICIENT = "BTC_ETH_OPTIONS_DATA_ACCUMULATION_OR_ALTERNATIVE_SOURCE_REVIEW_V1"
NEXT_UNAVAILABLE = "OPTIONS_DATA_AVAILABILITY_ALTERNATIVE_SOURCE_REVIEW_V1"
NEXT_RECOVERY = "BTC_ETH_OPTIONS_IMPLIED_MOVE_AVAILABILITY_RECOVERY_REVIEW_V1"

INPUT_RELATIVE_PATHS = [
    "artifacts/research/volatility_diagnostic_independent_sample_accumulation_monitor_summary_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_event_validator_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_robustness_evaluator_v1.json",
    "artifacts/contracts/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_contract_v1.json",
    "artifacts/research/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_event_validator_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_volatility_robustness_evaluator_v1.json",
    "artifacts/contracts/long_short_ratio_extreme_normalization_pre_registered_independent_validation_contract_v1.json",
    "artifacts/research/long_short_ratio_extreme_normalization_pre_registered_independent_validation_runner_v1.json",
    "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json",
    "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json",
]

OI_SHOCK_DISCOVERY_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.py"
)
OI_SHOCK_RESEARCH_RECON_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_forward_return_diagnostic_v1.py"
)
OI_SHOCK_INDEPENDENT_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.py"
)
LSR_DISCOVERY_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_event_discovery_v1.py"
)
LSR_RESEARCH_RECON_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_forward_return_diagnostic_v1.py"
)
LSR_INDEPENDENT_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_pre_registered_independent_validation_runner_v1.py"
)

S3_LIST_ENDPOINT = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
DATA_VISION_BASE = "https://data.binance.vision"
OPTION_PRODUCT_PREFIX = "data/option/daily/EOHSummary"
CACHE_ROOT = REPO_ROOT / "cache" / "btc_eth_options_implied_move_availability_diagnostic_v1"

UNDERLYING_MAPPING = {"BTCUSDT": "BTCUSDT", "ETHUSDT": "ETHUSDT"}
UNDERLYING_FAMILY = {"BTCUSDT": "BTC", "ETHUSDT": "ETH"}
BTC_ETH_SYMBOLS = ["BTCUSDT", "ETHUSDT"]
OI_TARGET_SLOTS = {
    "best_oi_expansion_volatility_expansion_definition": "expansion + volatility expansion",
    "best_oi_expansion_volatility_compression_break_definition": "expansion + volatility compression break",
}
LSR_TARGET_SLOT = "optional_account_position_divergence_resolution_candidate"
LSR_TARGET_LABEL = "account/position divergence resolution"
OPTION_SYMBOL_RE = re.compile(r"^(BTC|ETH)-(\d{6})-([0-9.]+)-([CP])$")

FORBIDDEN_ACTIONS_CONFIRMED_FALSE = {
    "strategy": False,
    "signal": False,
    "backtest": False,
    "pnl": False,
    "trade_simulation": False,
    "options_trade_simulation": False,
    "realized_vs_implied_outcome_test": False,
    "optimization_against_realized_move": False,
    "candidate_generation": False,
    "edge_claim": False,
    "runtime_live_capital_order_private_api_account_api_key": False,
    "altcoins_used": False,
    "combined_event_used_as_options_route": False,
    "event_definitions_changed": False,
    "expiry_or_strike_chosen_from_future_move": False,
}


class DiagnosticBlocked(RuntimeError):
    """Raised for hard stop conditions."""


class OptionsDataUnavailable(RuntimeError):
    """Raised when public option archive discovery cannot access usable data."""


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True, stderr=subprocess.STDOUT).strip()


def git_lines(args: list[str]) -> list[str]:
    output = run_git(args)
    return [line for line in output.splitlines() if line.strip()]


def recovery_audit() -> dict[str, Any]:
    current_head = run_git(["rev-parse", "HEAD"])
    branch = run_git(["branch", "--show-current"])
    try:
        core_longpaths = run_git(["config", "--local", "--get", "core.longpaths"])
    except subprocess.CalledProcessError:
        core_longpaths = "<unset>"
    porcelain = git_lines(["status", "--porcelain"])
    staged = git_lines(["diff", "--name-only", "--cached"])
    modified = git_lines(["diff", "--name-only"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    allowed = {
        MODULE_RELATIVE_PATH,
        MODULE_RELATIVE_PATH.replace("/", "\\"),
        ARTIFACT_RELATIVE_PATH,
        ARTIFACT_RELATIVE_PATH.replace("/", "\\"),
    }
    dirty_paths = set(modified + untracked + deleted)
    for line in porcelain:
        if len(line) >= 4:
            dirty_paths.add(line[3:])
    head_matches = current_head == EXPECTED_HEAD
    clean_or_output_only = (
        head_matches
        and not staged
        and all(path in allowed for path in dirty_paths)
        and all(line.startswith("?? ") and line[3:] in allowed for line in porcelain)
    )
    decision = "RECOVERY_AUDIT_CLEAN_CONTINUE" if clean_or_output_only else "RECOVERY_AUDIT_STOP"
    return {
        "current_head": current_head,
        "expected_head": EXPECTED_HEAD,
        "branch": branch,
        "core_longpaths_value": core_longpaths,
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "head_matches_expected": head_matches,
        "recovery_decision": decision,
        "recovery_audit_status": "PASS" if decision.endswith("CONTINUE") else "STOP",
    }


def print_recovery_audit(audit: dict[str, Any]) -> None:
    print(f"current HEAD: {audit['current_head']}")
    print(f"expected HEAD: {audit['expected_head']}")
    print(f"branch: {audit['branch']}")
    print(f"core.longpaths value: {audit['core_longpaths_value']}")
    print(f"git status porcelain: {audit['git_status_porcelain']}")
    print(f"staged files: {audit['staged_files']}")
    print(f"modified tracked files: {audit['modified_tracked_files']}")
    print(f"untracked files: {audit['untracked_files']}")
    print(f"deleted files: {audit['deleted_files']}")
    print(f"recovery decision: {audit['recovery_decision']}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel_path in INPUT_RELATIVE_PATHS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            raise DiagnosticBlocked(f"missing input artifact: {rel_path}")
        hashes[rel_path] = sha256_file(path)
    return hashes


def load_json(rel_path: str) -> dict[str, Any]:
    with (REPO_ROOT / rel_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise DiagnosticBlocked(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "nan"}:
        return None
    try:
        output = float(text)
    except ValueError:
        return None
    if not math.isfinite(output):
        return None
    return output


def median(values: list[float]) -> float | None:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(clean)) if clean else None


def quantile(values: list[float], q: float) -> float | None:
    clean = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    pos = (len(clean) - 1) * q
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return clean[int(pos)]
    return float(clean[low] * (high - pos) + clean[high] * (pos - low))


def utc_from_ms(ms_value: int) -> datetime:
    return datetime.fromtimestamp(ms_value / 1000, timezone.utc)


def ms_from_dt(dt_value: datetime) -> int:
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=timezone.utc)
    return int(dt_value.timestamp() * 1000)


def parse_iso_to_ms(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return ms_from_dt(parsed)


def s3_list(prefix: str, delimiter: str | None = None) -> dict[str, Any]:
    keys: list[str] = []
    prefixes: list[str] = []
    marker = ""
    while True:
        params = {"prefix": prefix, "max-keys": "1000"}
        if delimiter is not None:
            params["delimiter"] = delimiter
        if marker:
            params["marker"] = marker
        url = S3_LIST_ENDPOINT + "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            raise OptionsDataUnavailable(f"S3 listing unavailable for prefix {prefix}: {exc}") from exc
        root = ElementTree.fromstring(payload)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        keys.extend(
            item.text or "" for item in root.findall("s3:Contents/s3:Key", ns) if item.text
        )
        prefixes.extend(
            item.text or "" for item in root.findall("s3:CommonPrefixes/s3:Prefix", ns) if item.text
        )
        truncated = (root.findtext("s3:IsTruncated", default="false", namespaces=ns) or "false").lower() == "true"
        if not truncated:
            break
        next_marker = root.findtext("s3:NextMarker", namespaces=ns)
        marker = next_marker or (keys[-1] if keys else "")
        if not marker:
            break
    return {"keys": keys, "prefixes": sorted(set(prefixes))}


def download_public_file(key: str) -> Path | None:
    local = CACHE_ROOT / "raw_option_archives" / key
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists() and local.stat().st_size > 0:
        return local
    url = f"{DATA_VISION_BASE}/{key}"
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise OptionsDataUnavailable(f"public option archive download failed for {key}: {exc}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise OptionsDataUnavailable(f"public option archive download failed for {key}: {exc}") from exc
    local.write_bytes(data)
    return local


def option_key(underlying: str, day: date) -> str:
    value = day.isoformat()
    return f"{OPTION_PRODUCT_PREFIX}/{underlying}/{underlying}-EOHSummary-{value}.zip"


def option_date_from_key(key: str, underlying: str) -> str | None:
    match = re.search(rf"{re.escape(underlying)}-EOHSummary-(\d{{4}}-\d{{2}}-\d{{2}})\.zip$", key)
    return match.group(1) if match else None


def parse_option_symbol(symbol: str) -> dict[str, Any] | None:
    match = OPTION_SYMBOL_RE.match(str(symbol))
    if not match:
        return None
    family, expiry_text, strike_text, option_type = match.groups()
    expiry = datetime.strptime(expiry_text, "%y%m%d").replace(hour=8, minute=0, second=0, tzinfo=timezone.utc)
    strike = safe_float(strike_text)
    if strike is None:
        return None
    return {
        "family": family,
        "expiry": expiry,
        "expiry_date": expiry.date().isoformat(),
        "strike": float(strike),
        "type": option_type,
    }


def read_option_rows_for_date(underlying: str, day: date, available_dates: set[str]) -> list[dict[str, Any]]:
    day_text = day.isoformat()
    if day_text not in available_dates:
        return []
    key = option_key(underlying, day)
    path = download_public_file(key)
    if path is None:
        return []
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        for name in names:
            content = archive.read(name).decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(content))
            for row in reader:
                if row.get("underlying") != underlying:
                    continue
                parsed = parse_option_symbol(row.get("symbol", ""))
                if parsed is None:
                    continue
                hour_text = str(row.get("hour", "0")).zfill(2)[:2]
                try:
                    quote_time = datetime.strptime(f"{row.get('date')} {hour_text}", "%Y-%m-%d %H").replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
                enriched = dict(row)
                enriched.update(parsed)
                enriched["quote_time"] = quote_time
                enriched["quote_time_ms"] = ms_from_dt(quote_time)
                rows.append(enriched)
    return rows


def discover_options_data() -> dict[str, Any]:
    daily = s3_list("data/option/daily/", delimiter="/")
    eoh_underlyings = s3_list(f"{OPTION_PRODUCT_PREFIX}/", delimiter="/")
    bvol = s3_list("data/option/daily/BVOLIndex/", delimiter="/")
    by_underlying: dict[str, Any] = {}
    sample_headers: dict[str, Any] = {}
    for underlying in UNDERLYING_MAPPING.values():
        prefix = f"{OPTION_PRODUCT_PREFIX}/{underlying}/"
        listed = s3_list(prefix)
        zip_keys = sorted(key for key in listed["keys"] if key.endswith(".zip"))
        dates = [option_date_from_key(key, underlying) for key in zip_keys]
        dates = [value for value in dates if value is not None]
        by_underlying[underlying] = {
            "prefix": prefix,
            "zip_count": len(zip_keys),
            "available_date_min": min(dates) if dates else None,
            "available_date_max": max(dates) if dates else None,
            "available_dates": dates,
            "sample_keys": zip_keys[:5],
        }
        if zip_keys:
            sample_path = download_public_file(zip_keys[0])
            if sample_path is not None:
                with zipfile.ZipFile(sample_path) as archive:
                    names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
                    if names:
                        content = archive.read(names[0]).decode("utf-8", errors="replace")
                        reader = csv.reader(io.StringIO(content))
                        header = next(reader, [])
                        rows = []
                        for _ in range(2):
                            try:
                                rows.append(next(reader))
                            except StopIteration:
                                break
                        sample_headers[underlying] = {
                            "sample_key": zip_keys[0],
                            "csv_member": names[0],
                            "header": header,
                            "sample_rows": rows,
                        }
    return {
        "daily_prefixes": daily["prefixes"],
        "eoh_summary_underlying_prefixes": eoh_underlyings["prefixes"],
        "bvol_index_prefixes": bvol["prefixes"],
        "underlying_availability": by_underlying,
        "sample_headers": sample_headers,
        "products_discovered": {
            "EOHSummary": f"{OPTION_PRODUCT_PREFIX}/{{underlying}}/{{underlying}}-EOHSummary-YYYY-MM-DD.zip",
            "BVOLIndex": "data/option/daily/BVOLIndex/",
        },
    }


def load_inputs() -> dict[str, dict[str, Any]]:
    keys = [
        "monitor_summary",
        "oi_discovery",
        "oi_validator",
        "oi_robustness_evaluator",
        "oi_contract",
        "oi_independent",
        "lsr_discovery",
        "lsr_validator",
        "lsr_robustness_evaluator",
        "lsr_contract",
        "lsr_independent",
        "dataset",
        "kline",
    ]
    return {key: load_json(path) for key, path in zip(keys, INPUT_RELATIVE_PATHS)}


def assert_inputs(inputs: dict[str, dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    expected = {
        "monitor_summary": "VOLATILITY_DIAGNOSTIC_MONITOR_SUMMARY_READY",
        "oi_discovery": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_READY",
        "oi_validator": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
        "oi_robustness_evaluator": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_ROBUSTNESS_EVALUATOR_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY",
        "oi_contract": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY",
        "oi_independent": "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE",
        "lsr_discovery": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY",
        "lsr_validator": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
        "lsr_robustness_evaluator": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_PROMISING_DIAGNOSTIC_ONLY",
        "lsr_contract": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY",
        "lsr_independent": "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE",
    }
    for key, expected_class in expected.items():
        actual = inputs[key].get("result_classification")
        if actual != expected_class:
            blockers.append(f"{key}: {actual!r} != {expected_class!r}")
    for key, artifact in inputs.items():
        for flag in ("strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"):
            if flag in artifact and artifact.get(flag) is not False:
                blockers.append(f"{key}: {flag} not false")
    if inputs["monitor_summary"].get("options_availability_diagnostic_allowed_now") is not False:
        blockers.append("monitor_summary: options availability gate unexpectedly open")
    return blockers


def reference_price_from_kline(kline_data: dict[str, Any], event: dict[str, Any]) -> tuple[float | None, str | None]:
    opens = list(kline_data.get("opens", []))
    open_to_index = kline_data.get("open_to_index", {})
    event_ms = int(event.get("base_open_ms") or event.get("ts_ms"))
    index = open_to_index.get(event_ms)
    if index is None:
        candidates = [idx for idx, open_ms in enumerate(opens) if int(open_ms) <= event_ms]
        index = candidates[-1] if candidates else None
    if index is None:
        return None, None
    closes = kline_data["close"] if "close" in kline_data else kline_data.get("closes")
    if closes is None or index >= len(closes):
        return None, None
    value = float(closes[index])
    if not math.isfinite(value) or value <= 0:
        return None, None
    ref_open = int(opens[index]) if opens else event_ms
    return value, datetime.fromtimestamp(ref_open / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def event_record(
    route: str,
    sample_source: str,
    target_slot: str,
    target_label: str,
    event: dict[str, Any],
    reference_price: float | None,
    reference_time: str | None,
) -> dict[str, Any]:
    return {
        "route": route,
        "sample_source": sample_source,
        "target_slot": target_slot,
        "target_label": target_label,
        "symbol": event["symbol"],
        "underlying": UNDERLYING_MAPPING[event["symbol"]],
        "event_timestamp": event.get("timestamp"),
        "event_ts_ms": int(event["ts_ms"]),
        "reference_price": reference_price,
        "reference_price_time": reference_time,
        "event_definition_changed": False,
    }


def reconstruct_event_universe(inputs: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    warnings: list[str] = []
    events: list[dict[str, Any]] = []

    oi_shock = load_module(OI_SHOCK_DISCOVERY_TOOL, "options_availability_oi_shock_discovery")
    oi_research = load_module(OI_SHOCK_RESEARCH_RECON_TOOL, "options_availability_oi_shock_research_recon")
    oi_research_events, oi_research_klines, oi_research_reconstruction = oi_research.reconstruct_events(
        inputs["dataset"], inputs["kline"], inputs["oi_discovery"], oi_shock
    )
    for slot, label in OI_TARGET_SLOTS.items():
        for event in oi_research_events.get(slot, []):
            if event["symbol"] not in BTC_ETH_SYMBOLS:
                continue
            ref_price, ref_time = reference_price_from_kline(oi_research_klines[event["symbol"]], event)
            events.append(
                event_record(
                    COMPONENT_A_THEORY_ID,
                    "research_2023_2025",
                    slot,
                    label,
                    event,
                    ref_price,
                    ref_time,
                )
            )

    lsr_discovery = load_module(LSR_DISCOVERY_TOOL, "options_availability_lsr_discovery")
    lsr_research = load_module(LSR_RESEARCH_RECON_TOOL, "options_availability_lsr_research_recon")
    lsr_research_events, lsr_research_klines, lsr_research_reconstruction = lsr_research.reconstruct_events(
        inputs["dataset"], inputs["kline"], inputs["lsr_discovery"], lsr_discovery
    )
    for event in lsr_research_events.get(LSR_TARGET_SLOT, []):
        if event["symbol"] not in BTC_ETH_SYMBOLS:
            continue
        ref_price, ref_time = reference_price_from_kline(lsr_research_klines[event["symbol"]], event)
        events.append(
            event_record(
                COMPONENT_B_THEORY_ID,
                "research_2023_2025",
                LSR_TARGET_SLOT,
                LSR_TARGET_LABEL,
                event,
                ref_price,
                ref_time,
            )
        )

    oi_ind = load_module(OI_SHOCK_INDEPENDENT_TOOL, "options_availability_oi_shock_independent")
    oi_archive_helper = oi_ind.archive_helper_module()
    oi_archive_paths, oi_manifest = oi_archive_helper.download_all_archives(BTC_ETH_SYMBOLS)
    oi_ind_events, oi_ind_klines, _, oi_ind_counters, oi_ind_warnings = oi_ind.reconstruct_primary_events(
        oi_archive_paths,
        BTC_ETH_SYMBOLS,
        inputs["oi_discovery"],
        oi_archive_helper,
        oi_shock,
    )
    warnings.extend(f"oi_independent:{item}" for item in oi_ind_warnings)
    for slot, label in OI_TARGET_SLOTS.items():
        for event in oi_ind_events.get(slot, []):
            if event["symbol"] not in BTC_ETH_SYMBOLS:
                continue
            ref_price, ref_time = reference_price_from_kline(oi_ind_klines[event["symbol"]], event)
            events.append(
                event_record(
                    COMPONENT_A_THEORY_ID,
                    "independent_2026",
                    slot,
                    label,
                    event,
                    ref_price,
                    ref_time,
                )
            )

    lsr_ind = load_module(LSR_INDEPENDENT_TOOL, "options_availability_lsr_independent")
    lsr_archive_helper = lsr_ind.configure_archive_helper()
    lsr_module = lsr_ind.load_module(lsr_ind.DISCOVERY_TOOL, "options_availability_lsr_2026_discovery")
    lsr_meta = lsr_ind.selected_primary_meta(inputs["lsr_discovery"])
    lsr_archive_paths, lsr_manifest = lsr_archive_helper.download_all_archives(BTC_ETH_SYMBOLS)
    lsr_symbols_available = [
        symbol
        for symbol in BTC_ETH_SYMBOLS
        if lsr_archive_paths.get(symbol, {}).get("metrics") and lsr_archive_paths.get(symbol, {}).get("klines")
    ]
    lsr_ind_klines = {
        symbol: lsr_ind.read_2026_kline_archives(
            lsr_archive_paths.get(symbol, {}).get("klines", []), symbol, lsr_archive_helper
        )
        for symbol in lsr_symbols_available
    }
    lsr_ind_events, lsr_ind_reconstruction, lsr_ind_warnings = lsr_ind.reconstruct_primary_events(
        lsr_symbols_available,
        lsr_archive_paths,
        lsr_archive_helper,
        lsr_module,
        lsr_meta,
    )
    warnings.extend(f"lsr_independent:{item}" for item in lsr_ind_warnings)
    for event in lsr_ind_events:
        if event["symbol"] not in BTC_ETH_SYMBOLS:
            continue
        ref_price, ref_time = reference_price_from_kline(lsr_ind_klines[event["symbol"]], event)
        events.append(
            event_record(
                COMPONENT_B_THEORY_ID,
                "independent_2026",
                LSR_TARGET_SLOT,
                LSR_TARGET_LABEL,
                event,
                ref_price,
                ref_time,
            )
        )

    reconstruction = {
        "research_2023_2025": {
            "oi_shock": {
                "status": oi_research_reconstruction.get("status"),
                "actual_counts": oi_research_reconstruction.get("actual_counts"),
            },
            "long_short_ratio": {
                "status": lsr_research_reconstruction.get("status"),
                "actual_counts": lsr_research_reconstruction.get("actual_counts"),
            },
        },
        "independent_2026": {
            "oi_shock": {
                "counts_btc_eth": {slot: len([e for e in oi_ind_events.get(slot, []) if e["symbol"] in BTC_ETH_SYMBOLS]) for slot in OI_TARGET_SLOTS},
                "reconstruction_counters": oi_ind_counters,
            },
            "long_short_ratio": {
                "count_btc_eth": len([e for e in lsr_ind_events if e["symbol"] in BTC_ETH_SYMBOLS]),
                "reconstruction_status": lsr_ind_reconstruction,
            },
        },
        "reference_price_source": "public 15m kline close at or before event timestamp",
        "new_returns_computed": False,
    }
    return events, reconstruction, warnings


COMPONENT_A_THEORY_ID = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT"
COMPONENT_B_THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"


def rows_by_quote_time(rows: list[dict[str, Any]], event_ms: int) -> tuple[int | None, list[dict[str, Any]]]:
    quote_times = sorted({int(row["quote_time_ms"]) for row in rows if int(row["quote_time_ms"]) <= event_ms})
    if not quote_times:
        return None, []
    selected = quote_times[-1]
    return selected, [row for row in rows if int(row["quote_time_ms"]) == selected]


def classify_event_quality(
    breakeven_computable: bool,
    bid_ask_available: bool,
    quote_age_minutes: float | None,
    strike_distance_bps: float | None,
    expiry_suitable: bool,
) -> str:
    if not breakeven_computable:
        return "MISSING"
    if (
        bid_ask_available
        and quote_age_minutes is not None
        and quote_age_minutes <= 15
        and strike_distance_bps is not None
        and strike_distance_bps <= 100
        and expiry_suitable
    ):
        return "HIGH"
    if quote_age_minutes is not None and quote_age_minutes <= 60:
        return "MEDIUM"
    return "LOW"


def select_option_pair(event: dict[str, Any], option_rows: list[dict[str, Any]]) -> dict[str, Any]:
    underlying = event["underlying"]
    reference_price = event.get("reference_price")
    event_ms = int(event["event_ts_ms"])
    if reference_price is None or reference_price <= 0:
        return {"options_pair_found": False, "quality": "MISSING", "reason": "missing_underlying_reference_price"}
    quote_ms, rows = rows_by_quote_time(option_rows, event_ms)
    if quote_ms is None:
        return {"options_pair_found": False, "quality": "MISSING", "reason": "no_option_quote_at_or_before_event"}
    quote_dt = utc_from_ms(quote_ms)
    event_dt = utc_from_ms(event_ms)
    quote_age_minutes = (event_dt - quote_dt).total_seconds() / 60.0
    by_expiry: dict[datetime, dict[float, dict[str, dict[str, Any]]]] = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        if row.get("underlying") != underlying:
            continue
        expiry = row.get("expiry")
        strike = row.get("strike")
        option_type = row.get("type")
        if not isinstance(expiry, datetime) or strike is None or option_type not in {"C", "P"}:
            continue
        if expiry <= event_dt:
            continue
        by_expiry[expiry][float(strike)][option_type] = row
    if not by_expiry:
        return {
            "options_pair_found": False,
            "quality": "MISSING",
            "reason": "no_unexpired_options_at_quote_time",
            "quote_age_minutes": quote_age_minutes,
        }
    expiries = sorted(by_expiry)
    eligible_4h = [expiry for expiry in expiries if (expiry - event_dt).total_seconds() >= 4 * 3600]
    eligible_1h = [expiry for expiry in expiries if (expiry - event_dt).total_seconds() >= 1 * 3600]
    if eligible_4h:
        expiry_selected = eligible_4h[0]
        expiry_tier = "nearest_expiry_time_to_expiry_gte_4h"
    elif eligible_1h:
        expiry_selected = eligible_1h[0]
        expiry_tier = "nearest_expiry_time_to_expiry_gte_1h"
    else:
        return {
            "options_pair_found": False,
            "quality": "MISSING",
            "reason": "no_suitable_expiry_gte_1h",
            "quote_age_minutes": quote_age_minutes,
        }
    strike_pairs = {
        strike: pair for strike, pair in by_expiry[expiry_selected].items() if "C" in pair and "P" in pair
    }
    if not strike_pairs:
        return {
            "options_pair_found": False,
            "quality": "MISSING",
            "reason": "no_call_put_pair_for_selected_expiry",
            "expiry_selected": expiry_selected.isoformat(),
            "quote_age_minutes": quote_age_minutes,
        }
    strike = min(strike_pairs, key=lambda value: (abs(value - reference_price), value))
    pair = strike_pairs[strike]
    call = pair["C"]
    put = pair["P"]
    strike_distance_bps = abs(strike - reference_price) / reference_price * 10000.0
    time_to_expiry_minutes = (expiry_selected - event_dt).total_seconds() / 60.0

    call_bid = safe_float(call.get("best_bid_price"))
    call_ask = safe_float(call.get("best_ask_price"))
    put_bid = safe_float(put.get("best_bid_price"))
    put_ask = safe_float(put.get("best_ask_price"))
    call_mark = safe_float(call.get("mark_price")) or safe_float(call.get("close"))
    put_mark = safe_float(put.get("mark_price")) or safe_float(put.get("close"))
    bid_ask_available = (
        call_bid is not None
        and call_ask is not None
        and put_bid is not None
        and put_ask is not None
        and call_bid > 0
        and call_ask > 0
        and put_bid > 0
        and put_ask > 0
        and call_ask >= call_bid
        and put_ask >= put_bid
    )
    mark_available = call_mark is not None and put_mark is not None and call_mark > 0 and put_mark > 0
    call_mid = put_mid = straddle_mid_cost = breakeven_bps = None
    full_spread_bps = half_spread_bps = None
    price_source = None
    if bid_ask_available:
        call_mid = (call_bid + call_ask) / 2.0
        put_mid = (put_bid + put_ask) / 2.0
        straddle_mid_cost = call_mid + put_mid
        breakeven_bps = straddle_mid_cost / reference_price * 10000.0
        full_spread_bps = ((call_ask - call_bid) + (put_ask - put_bid)) / reference_price * 10000.0
        half_spread_bps = full_spread_bps / 2.0
        price_source = "bid_ask_mid"
    elif mark_available:
        call_mid = call_mark
        put_mid = put_mark
        straddle_mid_cost = call_mid + put_mid
        breakeven_bps = straddle_mid_cost / reference_price * 10000.0
        price_source = "mark_or_close_lower_quality"
    breakeven_computable = breakeven_bps is not None and math.isfinite(breakeven_bps)
    quality = classify_event_quality(
        breakeven_computable,
        bid_ask_available,
        quote_age_minutes,
        strike_distance_bps,
        expiry_selected in eligible_4h,
    )
    return {
        "options_pair_found": True,
        "atm_strike": strike,
        "atm_strike_distance_bps": strike_distance_bps,
        "expiry_selected": expiry_selected.isoformat(),
        "expiry_selection_tier": expiry_tier,
        "time_to_expiry_minutes": time_to_expiry_minutes,
        "quote_time": quote_dt.isoformat().replace("+00:00", "Z"),
        "quote_age_minutes": quote_age_minutes,
        "bid_ask_available": bid_ask_available,
        "mark_available": mark_available,
        "call_bid": call_bid,
        "call_ask": call_ask,
        "call_mid_or_mark": call_mid,
        "put_bid": put_bid,
        "put_ask": put_ask,
        "put_mid_or_mark": put_mid,
        "price_source": price_source,
        "straddle_mid_cost": straddle_mid_cost,
        "breakeven_bps": breakeven_bps,
        "mark_based_breakeven_bps": breakeven_bps if price_source == "mark_or_close_lower_quality" else None,
        "half_spread_bps": half_spread_bps,
        "full_spread_bps": full_spread_bps,
        "breakeven_bps_computable": breakeven_computable,
        "spread_bps": full_spread_bps,
        "quality": quality,
    }


def group_key(record: dict[str, Any]) -> str:
    return f"{record['route']}__{record['sample_source']}__{record['symbol']}"


def summarize_records(records: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[group_key(record)].append(record)
    counts_by_group: dict[str, Any] = {}
    breakeven_summary: dict[str, Any] = {}
    quality_summary: dict[str, Any] = {}
    for key, rows in sorted(groups.items()):
        breakevens = [row["breakeven_bps"] for row in rows if row.get("breakeven_bps_computable")]
        spreads = [row["full_spread_bps"] for row in rows if row.get("full_spread_bps") is not None]
        quote_ages = [row["quote_age_minutes"] for row in rows if row.get("quote_age_minutes") is not None]
        strike_distances = [row["atm_strike_distance_bps"] for row in rows if row.get("atm_strike_distance_bps") is not None]
        quality_counts = Counter(row.get("quality", "MISSING") for row in rows)
        counts_by_group[key] = {
            "event_count_btc_eth": len(rows),
            "events_with_options_pair": sum(1 for row in rows if row.get("options_pair_found")),
            "pair_coverage_rate": sum(1 for row in rows if row.get("options_pair_found")) / len(rows) if rows else None,
            "events_with_bid_ask": sum(1 for row in rows if row.get("bid_ask_available")),
            "bid_ask_coverage_rate": sum(1 for row in rows if row.get("bid_ask_available")) / len(rows) if rows else None,
            "events_with_computable_breakeven": len(breakevens),
        }
        breakeven_summary[key] = {
            "median_breakeven_bps": median(breakevens),
            "p25_breakeven_bps": quantile(breakevens, 0.25),
            "p75_breakeven_bps": quantile(breakevens, 0.75),
            "median_spread_bps": median(spreads),
            "median_quote_age_minutes": median(quote_ages),
            "median_strike_distance_bps": median(strike_distances),
        }
        quality_summary[key] = {
            "high_quality_count": quality_counts.get("HIGH", 0),
            "medium_quality_count": quality_counts.get("MEDIUM", 0),
            "low_quality_count": quality_counts.get("LOW", 0),
            "missing_count": quality_counts.get("MISSING", 0),
        }
    all_breakevens = [row["breakeven_bps"] for row in records if row.get("breakeven_bps_computable")]
    independent_high_quality = sum(
        1 for row in records if row.get("sample_source") == "independent_2026" and row.get("quality") == "HIGH"
    )
    aggregate = {
        "all_groups": {
            "event_count_btc_eth": len(records),
            "events_with_options_pair": sum(1 for row in records if row.get("options_pair_found")),
            "events_with_bid_ask": sum(1 for row in records if row.get("bid_ask_available")),
            "events_with_computable_breakeven": len(all_breakevens),
            "high_quality_independent_2026_count": independent_high_quality,
            "median_breakeven_bps": median(all_breakevens),
            "p25_breakeven_bps": quantile(all_breakevens, 0.25),
            "p75_breakeven_bps": quantile(all_breakevens, 0.75),
        },
        "by_source_sample_symbol": counts_by_group,
    }
    return aggregate, breakeven_summary, quality_summary


def build_event_coverage(
    events: list[dict[str, Any]],
    options_summary: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    rows_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
    records: list[dict[str, Any]] = []
    available_dates = {
        underlying: set(summary.get("available_dates", []))
        for underlying, summary in options_summary["underlying_availability"].items()
    }
    for index, event in enumerate(sorted(events, key=lambda item: (item["event_ts_ms"], item["route"], item["symbol"]))):
        underlying = event["underlying"]
        event_dt = utc_from_ms(int(event["event_ts_ms"]))
        candidate_days = [event_dt.date(), event_dt.date() - timedelta(days=1)]
        option_rows: list[dict[str, Any]] = []
        for day in candidate_days:
            cache_key = (underlying, day.isoformat())
            if cache_key not in rows_cache:
                rows_cache[cache_key] = read_option_rows_for_date(underlying, day, available_dates.get(underlying, set()))
            option_rows.extend(rows_cache[cache_key])
        selected = select_option_pair(event, option_rows)
        if selected.get("reason"):
            warnings.append(f"{underlying}:{event_dt.date()}:{selected['reason']}")
        records.append(
            {
                "event_index": index,
                **event,
                **selected,
                "realized_move_vs_breakeven_computed": False,
                "options_trade_simulation_performed": False,
            }
        )
    return records, sorted(set(warnings))


def classify_availability(records: list[dict[str, Any]], data_available: bool) -> tuple[str, str, bool]:
    if not data_available:
        return RESULT_DATA_UNAVAILABLE, NEXT_UNAVAILABLE, False
    computable = sum(1 for row in records if row.get("breakeven_bps_computable"))
    high_quality_independent = sum(
        1 for row in records if row.get("sample_source") == "independent_2026" and row.get("quality") == "HIGH"
    )
    if computable >= 100 or high_quality_independent >= 50:
        return RESULT_READY, NEXT_READY, True
    return RESULT_INSUFFICIENT, NEXT_INSUFFICIENT, False


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    print_recovery_audit(audit)
    if audit["recovery_decision"] != "RECOVERY_AUDIT_CLEAN_CONTINUE":
        raise DiagnosticBlocked(audit["recovery_decision"])
    hashes_before = input_hashes()
    inputs = load_inputs()
    blockers = assert_inputs(inputs)
    if blockers:
        raise DiagnosticBlocked("INPUT_CHAIN_BLOCKED:" + "; ".join(blockers))
    events, reconstruction_summary, reconstruction_warnings = reconstruct_event_universe(inputs)
    data_quality_warnings = list(reconstruction_warnings)
    try:
        options_summary = discover_options_data()
        data_available = all(
            options_summary["underlying_availability"].get(underlying, {}).get("zip_count", 0) > 0
            for underlying in UNDERLYING_MAPPING.values()
        )
    except OptionsDataUnavailable as exc:
        options_summary = {
            "discovery_error": str(exc),
            "products_discovered": {},
            "underlying_availability": {},
            "sample_headers": {},
        }
        data_available = False
        data_quality_warnings.append(str(exc))
    records, coverage_warnings = build_event_coverage(events, options_summary) if data_available else ([], [])
    data_quality_warnings.extend(coverage_warnings[:100])
    aggregate_counts, breakeven_summary, quality_summary = summarize_records(records)
    result_classification, allowed_next_step, realized_allowed_next = classify_availability(records, data_available)
    hashes_after = input_hashes()
    if hashes_before != hashes_after:
        raise DiagnosticBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    event_counts = Counter(
        f"{event['route']}__{event['sample_source']}__{event['symbol']}" for event in events
    )
    artifact = {
        "diagnostic_status": "READY" if result_classification == RESULT_READY else "PASS",
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_audit_status"],
        "current_head": audit["current_head"],
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "diagnostic_scope": {
            "scope": "BTC/ETH public Binance Data Vision options availability and provisional ATM straddle breakeven feasibility only",
            "underlyings": BTC_ETH_SYMBOLS,
            "sample_sources": ["research_2023_2025", "independent_2026"],
            "event_routes_used": [
                COMPONENT_A_THEORY_ID,
                COMPONENT_B_THEORY_ID,
            ],
            "combined_volatility_stress_event_used": False,
            "altcoins_used": False,
            "realized_vs_implied_test_performed": False,
        },
        "public_options_data_source_summary": {
            "source": "Binance Data Vision public option daily EOHSummary archives",
            "s3_listing_endpoint": S3_LIST_ENDPOINT,
            "download_base": DATA_VISION_BASE,
            "cache_root": str(CACHE_ROOT),
            "raw_option_cache_committed": False,
            "data_available": data_available,
        },
        "options_data_products_discovered": options_summary.get("products_discovered", {}),
        "options_schema_summary": {
            "sample_headers": options_summary.get("sample_headers", {}),
            "fields_needed": [
                "date",
                "hour",
                "symbol",
                "underlying",
                "type",
                "strike",
                "best_bid_price",
                "best_ask_price",
                "mark_price",
                "close",
            ],
            "call_put_strike_expiry_parse": "symbol format BTC-YYMMDD-STRIKE-C/P or ETH-YYMMDD-STRIKE-C/P",
        },
        "underlying_mapping": UNDERLYING_MAPPING,
        "event_sources_used": {
            "event_reconstruction_summary": reconstruction_summary,
            "routes": {
                COMPONENT_A_THEORY_ID: list(OI_TARGET_SLOTS.values()),
                COMPONENT_B_THEORY_ID: [LSR_TARGET_LABEL],
            },
        },
        "event_counts_by_source_sample_symbol": dict(sorted(event_counts.items())),
        "expiry_selection_policy": {
            "primary": "nearest expiry with time_to_expiry >= 4h",
            "fallback": "nearest expiry with time_to_expiry >= 1h",
            "outcome_optimized": False,
        },
        "atm_selection_policy": {
            "strike": "nearest strike to public kline reference price",
            "call_put_pair_required": True,
            "timestamp": "EOHSummary quote timestamp closest at or before event where possible",
            "outcome_optimized": False,
        },
        "breakeven_calculation_policy": {
            "bid_ask_mid": "call_mid=(bid+ask)/2, put_mid=(bid+ask)/2, breakeven=(call_mid+put_mid)/underlying_reference_price*10000",
            "mark_fallback": "mark/close based breakeven is lower-quality if bid/ask unavailable",
            "spread": "full_spread_bps=((call_ask-call_bid)+(put_ask-put_bid))/reference_price*10000",
            "realized_move_computed": False,
        },
        "event_level_coverage_summary": {
            "event_record_count": len(records),
            "records": records,
        },
        "aggregate_breakeven_summary": {
            "overall": aggregate_counts.get("all_groups", {}),
            "by_source_sample_symbol": breakeven_summary,
        },
        "aggregate_liquidity_quality_summary": {
            "coverage_counts": aggregate_counts,
            "quality_by_source_sample_symbol": quality_summary,
        },
        "data_quality_warnings": data_quality_warnings,
        "realized_vs_implied_diagnostic_allowed_next": realized_allowed_next,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": allowed_next_step,
        "blocker": None,
    }
    return artifact


def blocked_artifact(reason: str, result_classification: str = RESULT_FAILED) -> dict[str, Any]:
    audit = recovery_audit()
    try:
        before = input_hashes()
        after = input_hashes()
    except Exception:
        before = {}
        after = {}
    next_step = NEXT_UNAVAILABLE if result_classification == RESULT_DATA_UNAVAILABLE else NEXT_RECOVERY
    return {
        "diagnostic_status": "FAILED_STOP" if result_classification == RESULT_FAILED else "PASS",
        "result_classification": result_classification,
        "recovery_audit_status": audit.get("recovery_audit_status"),
        "current_head": audit.get("current_head"),
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit.get("head_matches_expected"),
        "input_artifact_hashes_before": before,
        "input_artifact_hashes_after": after,
        "input_artifact_hashes_unchanged": before == after and bool(before),
        "diagnostic_scope": {},
        "public_options_data_source_summary": {"data_available": False},
        "options_data_products_discovered": {},
        "options_schema_summary": {},
        "underlying_mapping": UNDERLYING_MAPPING,
        "event_sources_used": {},
        "event_counts_by_source_sample_symbol": {},
        "expiry_selection_policy": {},
        "atm_selection_policy": {},
        "breakeven_calculation_policy": {},
        "event_level_coverage_summary": {},
        "aggregate_breakeven_summary": {},
        "aggregate_liquidity_quality_summary": {},
        "data_quality_warnings": [reason],
        "realized_vs_implied_diagnostic_allowed_next": False,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": next_step,
        "blocker": reason,
    }


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")


def compact_report_value(value: Any, limit: int = 3000) -> str:
    text = json.dumps(value, sort_keys=True)
    return text if len(text) <= limit else text[:limit] + "...<truncated>"


def report_lines(artifact: dict[str, Any]) -> list[str]:
    return [
        f"status: {artifact.get('diagnostic_status')}",
        f"result_classification: {artifact.get('result_classification')}",
        f"recovery_audit_status: {artifact.get('recovery_audit_status')}",
        f"input_artifact_hashes_unchanged: {artifact.get('input_artifact_hashes_unchanged')}",
        "diagnostic_scope: " + compact_report_value(artifact.get("diagnostic_scope")),
        "public_options_data_source_summary: " + compact_report_value(artifact.get("public_options_data_source_summary")),
        "options_data_products_discovered: " + compact_report_value(artifact.get("options_data_products_discovered")),
        "options_schema_summary: " + compact_report_value(artifact.get("options_schema_summary")),
        "underlying_mapping: " + compact_report_value(artifact.get("underlying_mapping")),
        "event_sources_used: " + compact_report_value(artifact.get("event_sources_used"), 2000),
        "event_counts_by_source_sample_symbol: " + compact_report_value(artifact.get("event_counts_by_source_sample_symbol")),
        "event_level_coverage_summary: "
        + compact_report_value(
            {
                "event_record_count": artifact.get("event_level_coverage_summary", {}).get("event_record_count"),
                "first_10_records": artifact.get("event_level_coverage_summary", {}).get("records", [])[:10],
            },
            3000,
        ),
        "aggregate_breakeven_summary: " + compact_report_value(artifact.get("aggregate_breakeven_summary")),
        "aggregate_liquidity_quality_summary: " + compact_report_value(artifact.get("aggregate_liquidity_quality_summary")),
        "data_quality_warnings: " + compact_report_value(artifact.get("data_quality_warnings"), 2000),
        f"realized_vs_implied_diagnostic_allowed_next: {artifact.get('realized_vs_implied_diagnostic_allowed_next')}",
        f"allowed_next_step: {artifact.get('allowed_next_step')}",
        f"strategy_allowed: {artifact.get('strategy_allowed')}",
        f"signal_allowed: {artifact.get('signal_allowed')}",
        f"candidate_generation_allowed: {artifact.get('candidate_generation_allowed')}",
        f"release_allowed: {artifact.get('release_allowed')}",
        "commit hash: PENDING_COMMIT",
        "final git status: PENDING_COMMIT",
        "repo clean: PENDING_COMMIT",
        "tracked Python count: PENDING_COMMIT",
        "raw data committed: false",
        "cache files staged: false",
        "forbidden actions confirmed false: " + compact_report_value(artifact.get("forbidden_actions_confirmed_false")),
        f"blocker: {artifact.get('blocker')}",
    ]


def main() -> int:
    try:
        artifact = build_artifact()
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 0
    except OptionsDataUnavailable as exc:
        artifact = blocked_artifact(str(exc), RESULT_DATA_UNAVAILABLE)
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 0
    except Exception as exc:  # noqa: BLE001
        artifact = blocked_artifact(str(exc), RESULT_FAILED)
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
