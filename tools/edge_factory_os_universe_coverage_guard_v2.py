from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_universe_coverage_guard_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"universe_coverage_guard_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "universe_coverage_guard_v2_latest.json"
LATEST_MD = OUT_ROOT / "universe_coverage_guard_v2_latest.md"

MIN_EXPECTED_SYMBOLS = 250
MIN_EXPECTED_ROWS = 1_000_000
MIN_EXPECTED_DAYS = 350

PREFERRED_PANEL_DIR_MARKERS = [
    "edge_factory_feature_panels",
    "market_panic_rebound_long_v1",
    "post_impulse_drift_long_v1",
]

BAD_PANEL_MARKERS = [
    "family_promotion_sandbox",
    "session_top_exact_validator",
    "ret60_rule_artifact",
    "candidate_family_watchlist",
    "coin_subset_validation",
]


def load_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk(x)


def find_key_any(obj: Any, names: List[str]) -> Any:
    wanted = {n.lower() for n in names}
    for d in walk(obj):
        for k, v in d.items():
            if str(k).lower() in wanted:
                return v
    return None


def to_int(v: Any, default: int = 0) -> int:
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            return int(v)
        if isinstance(v, str):
            m = re.search(r"-?\d+", v.replace(",", ""))
            return int(m.group(0)) if m else default
    except Exception:
        return default
    return default


def parse_dt(v: Any) -> Optional[datetime]:
    if not isinstance(v, str):
        return None

    s = v.strip()
    if not s:
        return None

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    candidates = [s, s.replace(" ", "T"), s[:10]]

    for c in candidates:
        try:
            dt = datetime.fromisoformat(c)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

    return None


def infer_panel_metadata_from_parquet(panel_path: Optional[str]) -> Dict[str, Any]:
    meta = {
        "parquet_read_attempted": False,
        "parquet_read_ok": False,
        "parquet_error": None,
        "inferred_row_count": None,
        "inferred_symbol_count": None,
        "inferred_start": None,
        "inferred_end": None,
        "inferred_day_span": None,
        "inferred_columns": [],
    }

    if not panel_path:
        return meta

    path = Path(panel_path)

    if not path.exists() or path.suffix.lower() != ".parquet":
        return meta

    meta["parquet_read_attempted"] = True

    try:
        import pandas as pd

        # Only metadata / selected columns if possible.
        df_head = pd.read_parquet(path)
        meta["parquet_read_ok"] = True
        meta["inferred_row_count"] = int(len(df_head))
        meta["inferred_columns"] = list(map(str, df_head.columns))[:100]

        symbol_col = None
        for c in df_head.columns:
            lc = str(c).lower()
            if lc in {"symbol", "coin", "inst_id", "instid", "ticker"}:
                symbol_col = c
                break

        time_col = None
        for c in df_head.columns:
            lc = str(c).lower()
            if lc in {"timestamp", "time", "dt", "datetime", "bar_time", "ts"}:
                time_col = c
                break

        if symbol_col is not None:
            meta["inferred_symbol_count"] = int(df_head[symbol_col].nunique())

        if time_col is not None:
            ts = pd.to_datetime(df_head[time_col], errors="coerce", utc=True)
            if ts.notna().any():
                start = ts.min()
                end = ts.max()
                meta["inferred_start"] = str(start)
                meta["inferred_end"] = str(end)
                meta["inferred_day_span"] = float((end - start).total_seconds() / 86400.0)

    except Exception as e:
        meta["parquet_error"] = repr(e)

    return meta


def extract_candidate(path: Path, obj: Any) -> Optional[Dict[str, Any]]:
    text = json.dumps(obj, default=str).lower()
    ptext = str(path).lower()

    if not (
        "symbol_count" in text
        or "feature_panel" in text
        or "panel_path" in text
        or "failed_file_count" in text
        or "row_count" in text
        or "parquet" in text
    ):
        return None

    symbol_count = to_int(find_key_any(obj, [
        "symbol_count",
        "unique_symbol_count",
        "trade_symbol_count",
    ]), 0)

    row_count = to_int(find_key_any(obj, [
        "row_count",
        "rows",
        "total_rows",
        "panel_row_count",
    ]), 0)

    failed_file_count = to_int(find_key_any(obj, [
        "failed_file_count",
        "failed_files",
        "error_file_count",
    ]), 0)

    start_raw = find_key_any(obj, [
        "start",
        "start_time",
        "start_ts",
        "min_time",
        "min_timestamp",
        "data_start",
        "start_utc",
        "min_ts",
    ])

    end_raw = find_key_any(obj, [
        "end",
        "end_time",
        "end_ts",
        "max_time",
        "max_timestamp",
        "data_end",
        "end_utc",
        "max_ts",
    ])

    start_dt = parse_dt(start_raw)
    end_dt = parse_dt(end_raw)

    day_span = None
    if start_dt and end_dt:
        day_span = (end_dt - start_dt).total_seconds() / 86400.0

    panel_path_raw = find_key_any(obj, [
        "panel_path",
        "feature_panel_path",
        "output_panel_path",
        "parquet_path",
        "path",
    ])

    panel_path_exists = None
    if isinstance(panel_path_raw, str) and panel_path_raw:
        try:
            panel_path_exists = Path(panel_path_raw).exists()
        except Exception:
            panel_path_exists = None

    parquet_meta = infer_panel_metadata_from_parquet(panel_path_raw if isinstance(panel_path_raw, str) else None)

    if parquet_meta.get("inferred_symbol_count"):
        symbol_count = max(symbol_count, int(parquet_meta["inferred_symbol_count"]))

    if parquet_meta.get("inferred_row_count"):
        row_count = max(row_count, int(parquet_meta["inferred_row_count"]))

    if day_span is None and parquet_meta.get("inferred_day_span") is not None:
        day_span = float(parquet_meta["inferred_day_span"])
        start_raw = parquet_meta.get("inferred_start")
        end_raw = parquet_meta.get("inferred_end")

    if symbol_count <= 0 and row_count <= 0:
        return None

    preferred_score = 0

    for marker in PREFERRED_PANEL_DIR_MARKERS:
        if marker in ptext or (isinstance(panel_path_raw, str) and marker in panel_path_raw.lower()):
            preferred_score += 300

    bad_score = 0
    for marker in BAD_PANEL_MARKERS:
        if marker in ptext or (isinstance(panel_path_raw, str) and marker in panel_path_raw.lower()):
            bad_score += 250

    score = 0
    score += preferred_score
    score -= bad_score
    score += min(symbol_count, 500) * 3
    score += min(int(row_count / 1000), 3000)
    score += 200 if failed_file_count == 0 else -500
    score += 300 if day_span is not None and day_span >= MIN_EXPECTED_DAYS else 0
    score += 200 if panel_path_exists is True else 0
    score += 200 if isinstance(panel_path_raw, str) and panel_path_raw.lower().endswith(".parquet") else 0

    return {
        "manifest_path": str(path),
        "score": score,
        "preferred_score": preferred_score,
        "bad_score": bad_score,
        "symbol_count": symbol_count,
        "row_count": row_count,
        "failed_file_count": failed_file_count,
        "start_raw": start_raw,
        "end_raw": end_raw,
        "day_span": day_span,
        "panel_path": panel_path_raw,
        "panel_path_exists": panel_path_exists,
        "parquet_meta": parquet_meta,
    }


def find_candidates() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for path in BASE_DIR.rglob("*.json"):
        ps = str(path).lower()

        if ".git" in ps or "__pycache__" in ps:
            continue

        try:
            size = path.stat().st_size
        except Exception:
            continue

        if size <= 0 or size > 100_000_000:
            continue

        obj = load_json(path)

        if obj is None:
            continue

        c = extract_candidate(path, obj)

        if c:
            candidates.append(c)

    candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
    return candidates


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    candidates = find_candidates()
    best = candidates[0] if candidates else None

    if not best:
        universe_status = "UNIVERSE_COVERAGE_GUARD_V2_NO_PANEL_FOUND"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIND_OR_BUILD_FULL_1Y_OKX_SWAP_PANEL"
        reason = "no candidate panel manifest found"
        hard_pass = False
        full_pass = False

    else:
        symbol_count = int(best.get("symbol_count") or 0)
        row_count = int(best.get("row_count") or 0)
        failed_file_count = int(best.get("failed_file_count") or 0)
        day_span = best.get("day_span")
        panel_path_exists = best.get("panel_path_exists")

        symbol_ok = symbol_count >= MIN_EXPECTED_SYMBOLS
        row_ok = row_count >= MIN_EXPECTED_ROWS
        failed_ok = failed_file_count == 0
        panel_ok = panel_path_exists is True
        day_ok = day_span is not None and day_span >= MIN_EXPECTED_DAYS

        if not symbol_ok:
            critical.append(f"symbol_count_below_min:{symbol_count}<{MIN_EXPECTED_SYMBOLS}")

        if not row_ok:
            critical.append(f"row_count_below_min:{row_count}<{MIN_EXPECTED_ROWS}")

        if not failed_ok:
            critical.append(f"failed_file_count_not_zero:{failed_file_count}")

        if not panel_ok:
            critical.append(f"panel_path_missing_or_not_exists:{best.get('panel_path')}")

        if not day_ok:
            attention.append(f"day_span_missing_or_below_min:{day_span}")

        hard_pass = symbol_ok and row_ok and failed_ok and panel_ok
        full_pass = hard_pass and day_ok

        if full_pass:
            universe_status = "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY"
            severity = "OK"
            allowed_scope = "READ_ONLY_OR_OFFLINE_RESEARCH"
            next_action = "ALLOW_RESEARCH_TO_USE_THIS_FULL_UNIVERSE_PANEL"
            reason = f"symbol_count={symbol_count}; row_count={row_count}; day_span={day_span}; failed_file_count=0"

        elif hard_pass:
            universe_status = "UNIVERSE_COVERAGE_GUARD_V2_PASS_WITH_DATE_ATTENTION"
            severity = "ATTENTION"
            allowed_scope = "READ_ONLY_OR_OFFLINE_RESEARCH"
            next_action = "ALLOW_ONLY_RESEARCH_WITH_DATE_SPAN_CAVEAT_OR_CONFIRM_RAW_INVENTORY"
            reason = f"symbol_count={symbol_count}; row_count={row_count}; failed_file_count=0; day_span={day_span}"

        else:
            universe_status = "UNIVERSE_COVERAGE_GUARD_V2_FAIL_BLOCK_FAMILY_GENERATION"
            severity = "CRITICAL"
            allowed_scope = "READ_ONLY_REVIEW"
            next_action = "REBUILD_OR_LOCATE_FULL_1Y_OKX_SWAP_PANEL"
            reason = "; ".join(critical)

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "universe_status": universe_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "rule": {
            "new_family_or_candidate_generation_must_use_full_available_1y_okx_swap_universe": True,
            "paper_ledger_only_family_generation_allowed": False,
            "single_symbol_or_small_sample_family_generation_allowed": False,
            "min_expected_symbols": MIN_EXPECTED_SYMBOLS,
            "min_expected_rows": MIN_EXPECTED_ROWS,
            "min_expected_days": MIN_EXPECTED_DAYS,
        },

        "best_universe_manifest": best,
        "candidate_count": len(candidates),
        "top_candidates": candidates[:20],

        "family_generation_allowed_by_universe_guard": bool(hard_pass),
        "candidate_generation_allowed_by_universe_guard": bool(hard_pass),
        "promotion_allowed_by_universe_guard": False,

        "release_gate_note": "This guard only approves universe/data coverage. It does not approve family promotion by itself.",

        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": False,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "universe_coverage_guard_v2_state.json"
    out_md = RUN_DIR / "universe_coverage_guard_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS UNIVERSE COVERAGE GUARD v2

universe_status: {universe_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Rule

new_family_or_candidate_generation_must_use_full_available_1y_okx_swap_universe: True  
paper_ledger_only_family_generation_allowed: False  
single_symbol_or_small_sample_family_generation_allowed: False  
min_expected_symbols: {MIN_EXPECTED_SYMBOLS}  
min_expected_rows: {MIN_EXPECTED_ROWS}  
min_expected_days: {MIN_EXPECTED_DAYS}

## Best Universe Manifest

{json.dumps(best, indent=2, default=str)}

candidate_count: {len(candidates)}

family_generation_allowed_by_universe_guard: {bool(hard_pass)}  
candidate_generation_allowed_by_universe_guard: {bool(hard_pass)}  
promotion_allowed_by_universe_guard: False

## Safety

read_only: True  
offline_only: True  
mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: False

critical: {critical}  
attention: {attention}  
info: {info}
"""
    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS UNIVERSE COVERAGE GUARD v2")
    print("=" * 100)
    print(f"universe_status: {universe_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("BEST UNIVERSE MANIFEST")
    print("-" * 100)
    print(json.dumps(best, indent=2, default=str))
    print()
    print("DECISION")
    print("-" * 100)
    print(f"family_generation_allowed_by_universe_guard: {bool(hard_pass)}")
    print(f"candidate_generation_allowed_by_universe_guard: {bool(hard_pass)}")
    print("promotion_allowed_by_universe_guard: False")
    print()
    print("RULE")
    print("-" * 100)
    print("paper_ledger_only_family_generation_allowed: False")
    print("single_symbol_or_small_sample_family_generation_allowed: False")
    print("new_family_or_candidate_generation_must_use_full_available_1y_okx_swap_universe: True")
    print()
    print("SAFETY")
    print("-" * 100)
    print("read_only: True")
    print("offline_only: True")
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
