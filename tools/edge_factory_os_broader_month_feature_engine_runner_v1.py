from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_broader_month_feature_engine_runner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "broader_month_feature_engine_contract_latest.json"
)

CANONICAL_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_canonical_month_window_guard_v1"
    / "canonical_month_window_guard_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"broader_month_feature_engine_runner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "broader_month_feature_engine_runner_latest.json"
LATEST_MD = OUT_ROOT / "broader_month_feature_engine_runner_latest.md"

COST_BPS_TOTAL = 75.0


def load_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def fnum(v: Any, default=None):
    try:
        if v is None:
            return default
        x = float(v)
        return x if math.isfinite(x) else default
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def all_auth_false(action_guard: Dict[str, Any]) -> bool:
    auth = action_guard.get("authorization")
    if not isinstance(auth, dict):
        return False
    return all(v is False for v in auth.values())


def strict_12_stats(values_by_month: Dict[str, Any], canonical_months: List[str]) -> Dict[str, Any]:
    monthly_values: Dict[str, Optional[float]] = {}
    vals: List[float] = []

    for m in canonical_months:
        v = fnum(values_by_month.get(m), None)
        monthly_values[m] = v
        if v is not None:
            vals.append(v)

    active = len(vals)
    positive = sum(1 for x in vals if x > 0)
    negative = sum(1 for x in vals if x < 0)
    flat = sum(1 for x in vals if x == 0)
    total = float(sum(vals)) if vals else 0.0
    mean = total / active if active else None
    positive_rate = positive / active if active else None

    return {
        "canonical_policy_month_count": len(canonical_months),
        "active_month_count": active,
        "positive_month_count": positive,
        "negative_month_count": negative,
        "flat_month_count": flat,
        "positive_month_rate": positive_rate,
        "total": total,
        "mean": mean,
        "monthly_values": monthly_values,
        "strict_12_of_12_pass": (
            len(canonical_months) == 12
            and active == 12
            and positive == 12
            and negative == 0
            and positive_rate == 1.0
        ),
    }


def add_rolling_features(month_df, canonical_months: List[str]):
    import pandas as pd

    month_df = month_df.copy()
    month_df["month"] = month_df["month"].astype(str)
    month_df = month_df.sort_values("month").reset_index(drop=True)

    numeric_cols: List[str] = []
    for c in month_df.columns:
        if c == "month" or c.startswith("label_"):
            continue
        s = pd.to_numeric(month_df[c], errors="coerce")
        if s.notna().any():
            numeric_cols.append(c)

    new_cols = {}
    for col in numeric_cols:
        s = pd.to_numeric(month_df[col], errors="coerce")
        new_cols[f"{col}_mom_change"] = s.diff()
        new_cols[f"{col}_rolling3_mean"] = s.rolling(3, min_periods=2).mean()
        new_cols[f"{col}_rolling3_std"] = s.rolling(3, min_periods=2).std()
        new_cols[f"{col}_rolling6_mean"] = s.rolling(6, min_periods=3).mean()
        new_cols[f"{col}_rolling6_std"] = s.rolling(6, min_periods=3).std()

    extra = pd.DataFrame(new_cols)
    out = pd.concat([month_df, extra], axis=1).copy()
    out["is_canonical_policy_month"] = out["month"].isin(canonical_months)
    return out


def build_month_table_from_panel(panel_path: Path, canonical_months: List[str]):
    import pandas as pd

    df = pd.read_parquet(panel_path)

    required = [
        "time",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "entry_vol_quote",
        "entry_range_bps",
        "coin_ret3_bps",
        "coin_ret6_bps",
        "mkt_ret3_bps",
        "mkt_ret6_bps",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"panel_missing_required_columns:{missing}")

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    df = df.dropna(subset=["time", "symbol", "close"])
    df = df.sort_values(["symbol", "time"]).reset_index(drop=True)
    df["month"] = df["time"].dt.to_period("M").astype(str)

    for hold in [3, 6, 12, 24]:
        future_col = f"future_close_{hold}h"
        gross_col = f"gross_long_{hold}h_bps"
        long_col = f"label_long_net_{hold}h_bps"
        short_col = f"label_short_net_{hold}h_bps"

        df[future_col] = df.groupby("symbol")["close"].shift(-hold)
        df[gross_col] = ((df[future_col] / df["close"]) - 1.0) * 10000.0
        df[long_col] = df[gross_col] - COST_BPS_TOTAL
        df[short_col] = (-df[gross_col]) - COST_BPS_TOTAL

    bars = df.groupby("time").agg(
        symbol_count=("symbol", "nunique"),

        mean_coin_ret3_bps=("coin_ret3_bps", "mean"),
        median_coin_ret3_bps=("coin_ret3_bps", "median"),
        std_coin_ret3_bps=("coin_ret3_bps", "std"),
        q10_coin_ret3_bps=("coin_ret3_bps", lambda x: x.quantile(0.10)),
        q25_coin_ret3_bps=("coin_ret3_bps", lambda x: x.quantile(0.25)),
        q75_coin_ret3_bps=("coin_ret3_bps", lambda x: x.quantile(0.75)),
        q90_coin_ret3_bps=("coin_ret3_bps", lambda x: x.quantile(0.90)),

        mean_coin_ret6_bps=("coin_ret6_bps", "mean"),
        median_coin_ret6_bps=("coin_ret6_bps", "median"),
        std_coin_ret6_bps=("coin_ret6_bps", "std"),
        q10_coin_ret6_bps=("coin_ret6_bps", lambda x: x.quantile(0.10)),
        q90_coin_ret6_bps=("coin_ret6_bps", lambda x: x.quantile(0.90)),

        mean_mkt_ret3_bps=("mkt_ret3_bps", "mean"),
        mean_mkt_ret6_bps=("mkt_ret6_bps", "mean"),

        mean_entry_range_bps=("entry_range_bps", "mean"),
        median_entry_range_bps=("entry_range_bps", "median"),
        std_entry_range_bps=("entry_range_bps", "std"),
        q90_entry_range_bps=("entry_range_bps", lambda x: x.quantile(0.90)),

        mean_entry_vol_quote=("entry_vol_quote", "mean"),
        median_entry_vol_quote=("entry_vol_quote", "median"),
        std_entry_vol_quote=("entry_vol_quote", "std"),
        q25_entry_vol_quote=("entry_vol_quote", lambda x: x.quantile(0.25)),
        q75_entry_vol_quote=("entry_vol_quote", lambda x: x.quantile(0.75)),
    ).reset_index()

    tmp = df[["time", "coin_ret3_bps", "coin_ret6_bps", "entry_range_bps", "entry_vol_quote"]].copy()
    tmp["ret3_pos"] = tmp["coin_ret3_bps"] > 0
    tmp["ret3_neg"] = tmp["coin_ret3_bps"] < 0
    tmp["ret6_pos"] = tmp["coin_ret6_bps"] > 0
    tmp["ret6_neg"] = tmp["coin_ret6_bps"] < 0

    for thr in [100, 150, 200, 250, 350, 500]:
        tmp[f"impulse_{thr}_share"] = tmp["coin_ret3_bps"] >= thr
        tmp[f"drop_{thr}_share"] = tmp["coin_ret3_bps"] <= -thr
        tmp[f"range_{thr}_share"] = tmp["entry_range_bps"] >= thr

    liq_q25 = float(tmp["entry_vol_quote"].quantile(0.25))
    liq_q75 = float(tmp["entry_vol_quote"].quantile(0.75))
    tmp["low_liq_share"] = tmp["entry_vol_quote"] <= liq_q25
    tmp["high_liq_share"] = tmp["entry_vol_quote"] >= liq_q75

    share_aggs = {
        "breadth_ret3_pos": ("ret3_pos", "mean"),
        "breadth_ret3_neg": ("ret3_neg", "mean"),
        "breadth_ret6_pos": ("ret6_pos", "mean"),
        "breadth_ret6_neg": ("ret6_neg", "mean"),
        "low_liq_share": ("low_liq_share", "mean"),
        "high_liq_share": ("high_liq_share", "mean"),
    }

    for thr in [100, 150, 200, 250, 350, 500]:
        share_aggs[f"impulse_{thr}_share"] = (f"impulse_{thr}_share", "mean")
        share_aggs[f"drop_{thr}_share"] = (f"drop_{thr}_share", "mean")
        share_aggs[f"range_{thr}_share"] = (f"range_{thr}_share", "mean")

    shares = tmp.groupby("time").agg(**share_aggs).reset_index()
    bars = bars.merge(shares, on="time", how="left")
    bars["month"] = bars["time"].dt.to_period("M").astype(str)

    month_aggs = {
        "bar_count": ("time", "count"),
        "avg_symbol_count": ("symbol_count", "mean"),
    }

    for c in bars.columns:
        if c in {"time", "month", "symbol_count"}:
            continue
        month_aggs[f"avg_{c}"] = (c, "mean")
        month_aggs[f"std_{c}"] = (c, "std")

    month_features = bars.groupby("month").agg(**month_aggs).reset_index()

    label_cols = []
    for hold in [3, 6, 12, 24]:
        for side in ["long", "short"]:
            label_cols.append(f"label_{side}_net_{hold}h_bps")

    label_aggs = {}
    for c in label_cols:
        label_aggs[f"label_avg_{c}"] = (c, "mean")
        label_aggs[f"label_median_{c}"] = (c, "median")

    month_labels = df.groupby("month").agg(**label_aggs).reset_index()
    month_table = month_features.merge(month_labels, on="month", how="left")

    avg_label_cols = [c for c in month_table.columns if c.startswith("label_avg_")]
    month_table["label_best_broad_avg_net_bps"] = month_table[avg_label_cols].max(axis=1)
    month_table["label_worst_broad_avg_net_bps"] = month_table[avg_label_cols].min(axis=1)

    def best_template(row):
        vals = row[avg_label_cols]
        if vals.isna().all():
            return None
        return vals.idxmax()

    month_table["label_best_broad_template"] = month_table.apply(best_template, axis=1)
    month_table = add_rolling_features(month_table, canonical_months)

    panel_summary = {
        "panel_rows": int(len(df)),
        "panel_symbol_count": int(df["symbol"].nunique()),
        "panel_start": str(df["time"].min()),
        "panel_end": str(df["time"].max()),
        "raw_month_count": int(df["month"].nunique()),
        "liq_q25": liq_q25,
        "liq_q75": liq_q75,
    }

    return month_table, panel_summary


def rank_feature(month_df, feature: str, label: str, canonical_months: List[str]) -> List[Dict[str, Any]]:
    clean = month_df[month_df["month"].astype(str).isin(canonical_months)].copy()

    if feature not in clean.columns or label not in clean.columns:
        return []

    clean = clean[["month", feature, label]].dropna().copy()
    if len(clean) < 8:
        return []

    tests: List[Dict[str, Any]] = []

    for q in [0.20, 0.25, 0.33, 0.50, 0.67, 0.75, 0.80]:
        try:
            threshold = float(clean[feature].quantile(q))
        except Exception:
            continue

        for direction in [">=", "<="]:
            if direction == ">=":
                selected = clean[clean[feature] >= threshold]
                excluded = clean[clean[feature] < threshold]
            else:
                selected = clean[clean[feature] <= threshold]
                excluded = clean[clean[feature] > threshold]

            if len(selected) < 3 or len(excluded) < 2:
                continue

            sv = [fnum(x, 0.0) for x in selected[label].tolist()]
            ev = [fnum(x, 0.0) for x in excluded[label].tolist()]

            sp = sum(1 for x in sv if x > 0)
            sn = sum(1 for x in sv if x < 0)
            sr = sp / len(sv) if sv else None
            sm = sum(sv) / len(sv) if sv else None

            ep = sum(1 for x in ev if x > 0)
            er = ep / len(ev) if ev else None
            em = sum(ev) / len(ev) if ev else None

            separation = 0.0
            if sm is not None and em is not None:
                separation += abs(sm - em)
            if sr is not None and er is not None:
                separation += abs(sr - er) * 100.0

            strict_subset_pass = (
                len(sv) == 12
                and sp == 12
                and sn == 0
                and sr == 1.0
            )

            score = separation
            score += 500 if strict_subset_pass else 0
            score += sp * 20
            score -= sn * 25
            score -= 100 if len(sv) < 6 else 0

            tests.append({
                "feature": feature,
                "label": label,
                "threshold": threshold,
                "direction": direction,
                "selected_month_count": int(len(selected)),
                "excluded_month_count": int(len(excluded)),
                "selected_months": selected["month"].astype(str).tolist(),
                "excluded_months": excluded["month"].astype(str).tolist(),
                "selected_positive_month_count": int(sp),
                "selected_negative_month_count": int(sn),
                "selected_positive_month_rate": sr,
                "selected_mean_label": sm,
                "excluded_positive_month_count": int(ep),
                "excluded_positive_month_rate": er,
                "excluded_mean_label": em,
                "separation_score": separation,
                "diagnostic_score": score,
                "strict_12_of_12_subset_pass": strict_subset_pass,
            })

    tests.sort(key=lambda x: x["diagnostic_score"], reverse=True)
    return tests


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(CONTRACT_LATEST)
    canonical_guard = load_json(CANONICAL_GUARD_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)

    if not isinstance(contract, dict):
        critical.append("broader_month_feature_engine_contract_latest_missing")
        contract = {}

    if not isinstance(canonical_guard, dict):
        critical.append("canonical_month_window_guard_latest_missing")
        canonical_guard = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_month_policy_latest_missing")
        strict_policy = {}

    if not isinstance(action_guard, dict):
        critical.append("action_prerequisite_guard_latest_missing")
        action_guard = {}

    if contract.get("research_key") != "BROADER_MONTH_FEATURE_ENGINE_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if canonical_guard.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical_guard.get('guard_status')}")

    canonical_months = safe_get(canonical_guard, ["month_window", "canonical_policy_months"], [])
    if not isinstance(canonical_months, list) or len(canonical_months) != 12:
        critical.append(f"canonical_months_not_12:{canonical_months}")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    if not all_auth_false(action_guard):
        critical.append("action_authorization_not_all_false")

    for p in [
        ["required_runner_behavior", "candidate_generation_allowed_now"],
        ["required_runner_behavior", "candidate_contract_allowed_now"],
        ["required_runner_behavior", "family_release_allowed_now"],
        ["required_runner_behavior", "runtime_change_allowed_now"],
        ["required_runner_behavior", "capital_change_allowed_now"],
    ]:
        if safe_get(contract, p) is not False:
            critical.append(f"contract_action_flag_not_false:{'.'.join(p)}")

    panel_path = safe_get(contract, ["input_artifacts", "source_panel_path"])
    source_month_table_path = safe_get(contract, ["input_artifacts", "source_month_feature_table_csv"])

    panel = Path(str(panel_path)) if panel_path else None
    source_month_table = Path(str(source_month_table_path)) if source_month_table_path else None

    if panel is None or not panel.exists():
        if source_month_table is None or not source_month_table.exists():
            critical.append(f"no_panel_or_source_month_table_found:panel={panel_path};month_table={source_month_table_path}")
        else:
            attention.append("panel_missing_using_source_month_feature_table_only")

    if critical:
        runner_status = "BROADER_MONTH_FEATURE_ENGINE_RUNNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CONTRACT_OR_GUARD_INPUTS"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,
            "critical": critical,
            "attention": attention,
            "info": info,
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
        }

        dump_json(RUN_DIR / "broader_month_feature_engine_runner_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS BROADER MONTH FEATURE ENGINE RUNNER v1")
        print("=" * 100)
        print(f"runner_status: {runner_status}")
        print(f"severity: {severity}")
        print(f"reason: {reason}")
        print(f"latest_json: {LATEST_JSON}")
        print("=" * 100)
        return 2

    import pandas as pd

    if panel is not None and panel.exists():
        month_table, panel_summary = build_month_table_from_panel(panel, canonical_months)
    else:
        month_table = pd.read_csv(source_month_table)
        month_table["month"] = month_table["month"].astype(str)
        month_table = add_rolling_features(month_table, canonical_months)
        panel_summary = {
            "panel_rows": None,
            "panel_symbol_count": None,
            "panel_start": None,
            "panel_end": None,
            "raw_month_count": int(month_table["month"].nunique()),
            "source": "source_month_feature_table_only",
        }

    canonical_table = month_table[month_table["month"].astype(str).isin(canonical_months)].copy()

    label_cols = [
        c for c in canonical_table.columns
        if c.startswith("label_") and c != "label_best_broad_template"
    ]

    preferred_labels = [
        "label_best_broad_avg_net_bps",
        "label_avg_label_long_net_6h_bps",
        "label_avg_label_long_net_12h_bps",
        "label_avg_label_short_net_6h_bps",
        "label_avg_label_short_net_12h_bps",
    ]

    labels_to_rank = [c for c in preferred_labels if c in label_cols]
    if not labels_to_rank:
        labels_to_rank = label_cols[:8]

    feature_cols: List[str] = []
    for c in canonical_table.columns:
        if c == "month" or c.startswith("label_") or c == "is_canonical_policy_month":
            continue
        s = pd.to_numeric(canonical_table[c], errors="coerce")
        if s.notna().any():
            feature_cols.append(c)

    rankings: List[Dict[str, Any]] = []

    for feature in feature_cols:
        for label in labels_to_rank:
            try:
                rankings.extend(rank_feature(canonical_table, feature, label, canonical_months)[:3])
            except Exception as exc:
                attention.append(f"rank_feature_failed:{feature}:{label}:{exc}")

    rankings.sort(
        key=lambda x: (
            1 if x.get("strict_12_of_12_subset_pass") else 0,
            x.get("diagnostic_score") or 0.0,
        ),
        reverse=True,
    )

    strict_subset_passes = [r for r in rankings if r.get("strict_12_of_12_subset_pass") is True]

    canonical_label_baselines = {}
    for label in labels_to_rank:
        values = {}
        for _, row in canonical_table.iterrows():
            values[str(row["month"])] = fnum(row[label], None)
        canonical_label_baselines[label] = strict_12_stats(values, canonical_months)

    expanded_table_path = RUN_DIR / "broader_month_feature_engine_expanded_month_table.csv"
    scoreboard_json_path = RUN_DIR / "broader_month_feature_engine_feature_scoreboard.json"
    scoreboard_csv_path = RUN_DIR / "broader_month_feature_engine_feature_scoreboard.csv"

    month_table.to_csv(expanded_table_path, index=False)
    dump_json(scoreboard_json_path, {"rankings": rankings[:1000]})

    flat_rows = []
    for r in rankings:
        flat_rows.append({
            "diagnostic_score": r.get("diagnostic_score"),
            "strict_12_of_12_subset_pass": r.get("strict_12_of_12_subset_pass"),
            "feature": r.get("feature"),
            "label": r.get("label"),
            "threshold": r.get("threshold"),
            "direction": r.get("direction"),
            "selected_month_count": r.get("selected_month_count"),
            "selected_positive_month_count": r.get("selected_positive_month_count"),
            "selected_negative_month_count": r.get("selected_negative_month_count"),
            "selected_positive_month_rate": r.get("selected_positive_month_rate"),
            "selected_mean_label": r.get("selected_mean_label"),
            "excluded_mean_label": r.get("excluded_mean_label"),
            "separation_score": r.get("separation_score"),
            "selected_months": ",".join(r.get("selected_months") or []),
        })

    pd.DataFrame(flat_rows).to_csv(scoreboard_csv_path, index=False)

    runner_status = "BROADER_MONTH_FEATURE_ENGINE_RUNNER_COMPLETE"
    severity = "ATTENTION"
    allowed_scope = "READ_ONLY_RESEARCH"
    next_action = "EVALUATE_BROADER_MONTH_FEATURE_ENGINE_RESULTS"
    reason = (
        f"canonical_month_count={len(canonical_months)}; "
        f"expanded_feature_count={len(feature_cols)}; "
        f"ranking_count={len(rankings)}; "
        f"strict_subset_pass_count={len(strict_subset_passes)}"
    )

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "runner_status": runner_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "contract_source": str(CONTRACT_LATEST),
        "canonical_guard_source": str(CANONICAL_GUARD_LATEST),
        "strict_policy_source": str(STRICT_POLICY_LATEST),
        "action_guard_source": str(ACTION_GUARD_LATEST),

        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "research_key": contract.get("research_key"),

        "canonical_month_window": {
            "canonical_policy_month_count": len(canonical_months),
            "canonical_policy_months": canonical_months,
            "raw_calendar_month_count": safe_get(canonical_guard, ["month_window", "raw_calendar_month_count"]),
            "boundary_partial_months": safe_get(canonical_guard, ["month_window", "boundary_partial_months"]),
        },

        "strict_policy": {
            "policy_key": strict_policy.get("policy_key"),
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"]),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"]),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"]),
        },

        "panel_summary": panel_summary,

        "expanded_feature_summary": {
            "raw_month_count": int(month_table["month"].nunique()),
            "canonical_month_count": int(canonical_table["month"].nunique()),
            "expanded_feature_count": len(feature_cols),
            "label_count": len(labels_to_rank),
            "ranking_count": len(rankings),
            "strict_12_subset_pass_count": len(strict_subset_passes),
        },

        "canonical_label_baselines": canonical_label_baselines,
        "top_rankings": rankings[:40],
        "strict_12_subset_passes": strict_subset_passes[:20],

        "outputs": {
            "expanded_month_table_csv": str(expanded_table_path),
            "feature_family_scoreboard_json": str(scoreboard_json_path),
            "feature_family_scoreboard_csv": str(scoreboard_csv_path),
        },

        "findings": [
            {
                "finding_id": "BMFE_RUNNER_F1_CANONICAL_MONTH_WINDOW_CONSUMED",
                "severity": "CONTROL",
                "claim": "Runner consumed canonical 12-month window and did not use raw 13 calendar buckets for release logic.",
                "evidence": {
                    "canonical_months": canonical_months,
                    "raw_calendar_month_count": safe_get(canonical_guard, ["month_window", "raw_calendar_month_count"]),
                    "boundary_partial_months": safe_get(canonical_guard, ["month_window", "boundary_partial_months"]),
                },
            },
            {
                "finding_id": "BMFE_RUNNER_F2_EXPANDED_FEATURE_TABLE_CREATED",
                "severity": "INFO",
                "claim": "Expanded canonical-month feature table and feature-family scoreboard were created.",
                "evidence": {
                    "expanded_month_table": str(expanded_table_path),
                    "feature_scoreboard_json": str(scoreboard_json_path),
                    "feature_scoreboard_csv": str(scoreboard_csv_path),
                    "expanded_feature_count": len(feature_cols),
                    "ranking_count": len(rankings),
                },
            },
            {
                "finding_id": "BMFE_RUNNER_F3_ACTIONS_STILL_BLOCKED",
                "severity": "CONTROL",
                "claim": "All candidate/family/runtime/capital/live/real-order actions remain blocked.",
                "evidence": {
                    "authorization": action_guard.get("authorization"),
                },
            },
        ],

        "release_gate_feed": {
            "BROADER_MONTH_FEATURE_ENGINE_RUNNER_RAN": True,
            "CANONICAL_MONTH_WINDOW_CONSUMED": True,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12",
            "EXPANDED_MONTH_FEATURE_TABLE_CREATED": True,
            "FEATURE_FAMILY_SCOREBOARD_CREATED": True,
            "STRICT_12_OF_12_SUBSET_SIGNAL_FOUND": bool(strict_subset_passes),
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "ACTIVE_PAPER_ALLOWED": False,
            "LIVE_ALLOWED": False,
            "REAL_ORDERS_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_RUNNER": False,
            "status": runner_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "active_paper_recommended": False,
            "live_or_real_order_recommended": False,
            "next_module": "edge_factory_os_broader_month_feature_engine_evaluator_v1.py",
            "why_no_action": [
                "runner_is_diagnostic_only",
                "action_prerequisite_guard_blocks_all_actions",
                "feature_family_scoreboard_is_not_candidate_generation",
                "strict_12_of_12_requires evaluator and full prerequisite chain",
                "no_runtime_or_capital_action_allowed",
            ],
        },

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
            "execution_performed": True,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "broader_month_feature_engine_runner_v1_state.json"
    out_md = RUN_DIR / "broader_month_feature_engine_runner_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS BROADER MONTH FEATURE ENGINE RUNNER v1

runner_status: {runner_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_id: {contract.get("contract_id")}  
research_key: {contract.get("research_key")}

## Canonical Month Window

{json.dumps(result["canonical_month_window"], indent=2, default=str)}

## Strict Policy

{json.dumps(result["strict_policy"], indent=2, default=str)}

## Expanded Feature Summary

{json.dumps(result["expanded_feature_summary"], indent=2, default=str)}

## Top Rankings

{json.dumps(rankings[:20], indent=2, default=str)[:20000]}

## Canonical Label Baselines

{json.dumps(canonical_label_baselines, indent=2, default=str)[:12000]}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Decision

{json.dumps(result["decision"], indent=2, default=str)}

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
execution_performed: True

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS BROADER MONTH FEATURE ENGINE RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {runner_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("EXPANDED FEATURE SUMMARY")
    print("-" * 100)
    print(json.dumps(result["expanded_feature_summary"], indent=2, default=str))
    print()
    print("TOP RANKINGS")
    print("-" * 100)
    for row in rankings[:10]:
        print(row)
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
    print()
    print("DECISION")
    print("-" * 100)
    print(json.dumps(result["decision"], indent=2, default=str))
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
    print("execution_performed: True")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
