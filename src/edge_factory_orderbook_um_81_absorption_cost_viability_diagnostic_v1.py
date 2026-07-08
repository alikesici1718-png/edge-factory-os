#!/usr/bin/env python
"""Cost viability diagnostic for fixed non-overlap absorption candidates."""

from __future__ import annotations

import csv
import json
import math
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

NON_OVERLAP_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_absorption_non_overlap_event_validation_summary.json"
NON_OVERLAP_CANDIDATE_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_non_overlap_event_validation_candidate_cooldown.csv"

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_absorption_cost_viability_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_absorption_cost_viability_summary.md"
CANDIDATE_COST_GRID_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_cost_viability_candidate_cost_grid.csv"
STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_cost_viability_stability.csv"

COST_GRID_BPS = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
WINDOW_PREFIXES = ["latest", "holdout"]
MIN_EVENT_COUNT = 100
MIN_STABILITY_RATE = 0.5

EXPECTED_CANDIDATES = [
    ("SELL_PRESSURE_ABSORBED", 300),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 300),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 60),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", 30),
]
EXPECTED_COOLDOWNS = [300, 600, 900]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def float_or_none(value: Any) -> float | None:
    try:
        if value in {None, ""}:
            return None
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    if math.isnan(result):
        return None
    return result


def rounded(value: float | None, places: int = 12) -> float | str:
    if value is None or math.isnan(value):
        return ""
    return round(value, places)


def sign_of(value: float | None, tolerance: float = 1e-12) -> int:
    if value is None or abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1


def sign_text(direction: int) -> str:
    if direction < 0:
        return "NEGATIVE_PRICE_EFFECT"
    if direction > 0:
        return "POSITIVE_PRICE_EFFECT"
    return "UNAVAILABLE"


def candidate_label(category: str, horizon: int) -> str:
    return f"{category}@{horizon}s"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"not a JSON object: {path}")
    return payload


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def stable_enough(metrics: dict[str, Any]) -> bool:
    rates = [
        float_or_none(metrics.get("symbol_stability_rate")),
        float_or_none(metrics.get("week_stability_rate")),
        float_or_none(metrics.get("month_stability_rate")),
    ]
    return all(value is not None and value >= MIN_STABILITY_RATE for value in rates)


def window_metrics(row: dict[str, str], prefix: str) -> dict[str, Any]:
    return {
        "event_count": int_value(row.get(f"{prefix}_event_count")),
        "gross_mean_forward_price_return": float_or_none(row.get(f"{prefix}_mean_forward_price_return")),
        "gross_median_forward_price_return": float_or_none(row.get(f"{prefix}_median_forward_price_return")),
        "gross_effect_vs_null_signed": float_or_none(row.get(f"{prefix}_price_effect_vs_null")),
        "price_effect_size_vs_null": float_or_none(row.get(f"{prefix}_price_effect_size_vs_null")),
        "directional_diagnostic_rate": float_or_none(row.get(f"{prefix}_directional_diagnostic_rate")),
        "symbol_stability_rate": float_or_none(row.get(f"{prefix}_symbol_stability_rate")),
        "week_stability_rate": float_or_none(row.get(f"{prefix}_week_stability_rate")),
        "month_stability_rate": float_or_none(row.get(f"{prefix}_month_stability_rate")),
    }


def observed_direction(latest_effect: float | None, holdout_effect: float | None) -> int:
    latest_sign = sign_of(latest_effect)
    holdout_sign = sign_of(holdout_effect)
    if latest_sign and latest_sign == holdout_sign:
        return latest_sign
    combined = (latest_effect or 0.0) + (holdout_effect or 0.0)
    return sign_of(combined)


def classify_cost_row(
    gross_edge: float | None,
    net_edge: float | None,
    event_count: int,
    stable: bool,
    paired_net_positive: bool,
) -> str:
    if gross_edge is None or gross_edge <= 0 or event_count < MIN_EVENT_COUNT or not stable:
        return "FAILS_COST"
    if net_edge is not None and net_edge > 0 and paired_net_positive:
        return "SURVIVES_COST"
    return "FILTER_ONLY"


def build_rows(
    source_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    cost_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    cooldown_rows: list[dict[str, Any]] = []

    for source_row in source_rows:
        category = str(source_row.get("category", ""))
        horizon = int_value(source_row.get("horizon_seconds"))
        cooldown = int_value(source_row.get("cooldown_seconds"))
        candidate = candidate_label(category, horizon)
        latest = window_metrics(source_row, "latest")
        holdout = window_metrics(source_row, "holdout")
        direction = observed_direction(latest["gross_effect_vs_null_signed"], holdout["gross_effect_vs_null_signed"])
        latest_gross_edge = (
            latest["gross_effect_vs_null_signed"] * direction if latest["gross_effect_vs_null_signed"] is not None and direction else None
        )
        holdout_gross_edge = (
            holdout["gross_effect_vs_null_signed"] * direction if holdout["gross_effect_vs_null_signed"] is not None and direction else None
        )
        latest_break_even = max(0.0, (latest_gross_edge or 0.0) * 10_000)
        holdout_break_even = max(0.0, (holdout_gross_edge or 0.0) * 10_000)
        min_break_even = min(latest_break_even, holdout_break_even)
        latest_stable = stable_enough(latest)
        holdout_stable = stable_enough(holdout)
        max_cost_survived_both = None

        for prefix, metrics, gross_edge, break_even, stable in [
            ("latest", latest, latest_gross_edge, latest_break_even, latest_stable),
            ("holdout", holdout, holdout_gross_edge, holdout_break_even, holdout_stable),
        ]:
            stability_rows.append(
                {
                    "candidate": candidate,
                    "category": category,
                    "horizon_seconds": horizon,
                    "cooldown_seconds": cooldown,
                    "window": prefix.upper() + "_90D",
                    "event_count": metrics["event_count"],
                    "observed_direction": sign_text(direction),
                    "break_even_cost_bps": rounded(break_even, 6),
                    "symbol_stability_rate": rounded(metrics["symbol_stability_rate"], 6),
                    "week_stability_rate": rounded(metrics["week_stability_rate"], 6),
                    "month_stability_rate": rounded(metrics["month_stability_rate"], 6),
                    "stable_all_periods": str(stable).lower(),
                    "directional_diagnostic_rate": rounded(metrics["directional_diagnostic_rate"], 6),
                }
            )

        for cost_bps in COST_GRID_BPS:
            cost_return = cost_bps / 10_000
            latest_net = latest_gross_edge - cost_return if latest_gross_edge is not None else None
            holdout_net = holdout_gross_edge - cost_return if holdout_gross_edge is not None else None
            both_positive = bool(
                latest_net is not None
                and latest_net > 0
                and holdout_net is not None
                and holdout_net > 0
                and latest_stable
                and holdout_stable
            )
            consistency = "CONSISTENT_POSITIVE" if both_positive else "NOT_POSITIVE_IN_BOTH_WINDOWS"
            if both_positive:
                max_cost_survived_both = cost_bps
            for prefix, metrics, gross_edge, net_edge, break_even, stable in [
                ("latest", latest, latest_gross_edge, latest_net, latest_break_even, latest_stable),
                ("holdout", holdout, holdout_gross_edge, holdout_net, holdout_break_even, holdout_stable),
            ]:
                cost_rows.append(
                    {
                        "candidate": candidate,
                        "category": category,
                        "horizon_seconds": horizon,
                        "cooldown_seconds": cooldown,
                        "window": prefix.upper() + "_90D",
                        "cost_bps": cost_bps,
                        "observed_direction": sign_text(direction),
                        "kept_event_count": metrics["event_count"],
                        "gross_mean_forward_price_return": rounded(metrics["gross_mean_forward_price_return"]),
                        "gross_median_forward_price_return": rounded(metrics["gross_median_forward_price_return"]),
                        "gross_effect_vs_null_signed": rounded(metrics["gross_effect_vs_null_signed"]),
                        "gross_edge_observed_direction": rounded(gross_edge),
                        "net_effect_after_cost": rounded(net_edge),
                        "net_effect_after_cost_bps": rounded(net_edge * 10_000 if net_edge is not None else None, 6),
                        "break_even_cost_bps": rounded(break_even, 6),
                        "directional_diagnostic_rate": rounded(metrics["directional_diagnostic_rate"], 6),
                        "symbol_stability_rate": rounded(metrics["symbol_stability_rate"], 6),
                        "week_stability_rate": rounded(metrics["week_stability_rate"], 6),
                        "month_stability_rate": rounded(metrics["month_stability_rate"], 6),
                        "latest_vs_holdout_consistency": consistency,
                        "classification": classify_cost_row(
                            gross_edge,
                            net_edge,
                            metrics["event_count"],
                            stable,
                            both_positive,
                        ),
                    }
                )

        cooldown_rows.append(
            {
                "candidate": candidate,
                "category": category,
                "horizon_seconds": horizon,
                "cooldown_seconds": cooldown,
                "observed_direction": sign_text(direction),
                "latest_event_count": latest["event_count"],
                "holdout_event_count": holdout["event_count"],
                "latest_break_even_cost_bps": rounded(latest_break_even, 6),
                "holdout_break_even_cost_bps": rounded(holdout_break_even, 6),
                "min_latest_holdout_break_even_cost_bps": rounded(min_break_even, 6),
                "max_cost_bps_survived_both_windows": "" if max_cost_survived_both is None else max_cost_survived_both,
                "latest_symbol_stability_rate": rounded(latest["symbol_stability_rate"], 6),
                "holdout_symbol_stability_rate": rounded(holdout["symbol_stability_rate"], 6),
                "latest_week_stability_rate": rounded(latest["week_stability_rate"], 6),
                "holdout_week_stability_rate": rounded(holdout["week_stability_rate"], 6),
                "latest_month_stability_rate": rounded(latest["month_stability_rate"], 6),
                "holdout_month_stability_rate": rounded(holdout["month_stability_rate"], 6),
            }
        )
    return cost_rows, stability_rows, cooldown_rows


def candidate_break_even_summary(cooldown_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in cooldown_rows:
        grouped[str(row["candidate"])].append(row)
    result: list[dict[str, Any]] = []
    for candidate in sorted(grouped):
        ranked = sorted(
            grouped[candidate],
            key=lambda row: float_or_none(row.get("min_latest_holdout_break_even_cost_bps")) or -1.0,
            reverse=True,
        )
        best = ranked[0]
        result.append(
            {
                "candidate": candidate,
                "best_cooldown_seconds": best["cooldown_seconds"],
                "best_min_latest_holdout_break_even_cost_bps": best["min_latest_holdout_break_even_cost_bps"],
                "best_max_cost_bps_survived_both_windows": best["max_cost_bps_survived_both_windows"],
                "cooldown_break_even_cost_bps": {
                    str(row["cooldown_seconds"]): row["min_latest_holdout_break_even_cost_bps"]
                    for row in ranked
                },
            }
        )
    return result


def strongest_candidate(cooldown_rows: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(
        cooldown_rows,
        key=lambda row: float_or_none(row.get("min_latest_holdout_break_even_cost_bps")) or -1.0,
        reverse=True,
    )
    return ranked[0] if ranked else {}


def sell_pressure_assessment(break_even_rows: list[dict[str, Any]]) -> dict[str, Any]:
    sell_rows = [row for row in break_even_rows if str(row.get("candidate")) == "SELL_PRESSURE_ABSORBED@300s"]
    if not sell_rows:
        return {"candidate": "SELL_PRESSURE_ABSORBED@300s", "assessment": "REJECTED"}
    best = sell_rows[0]
    best_survived_cost = float_or_none(best.get("best_max_cost_bps_survived_both_windows"))
    if best_survived_cost is not None and best_survived_cost >= 3.0:
        assessment = "STANDALONE_VIABLE_THROUGH_3_BPS_FILTER_ONLY_ABOVE"
    elif best_survived_cost is not None and best_survived_cost >= 1.0:
        assessment = "FILTER_ONLY"
    else:
        assessment = "REJECTED"
    return {
        "candidate": "SELL_PRESSURE_ABSORBED@300s",
        "assessment": assessment,
        "best_cooldown_seconds": best.get("best_cooldown_seconds", ""),
        "best_min_latest_holdout_break_even_cost_bps": best.get("best_min_latest_holdout_break_even_cost_bps", ""),
        "best_max_cost_bps_survived_both_windows": best.get("best_max_cost_bps_survived_both_windows", ""),
    }


def cost_grid_fieldnames() -> list[str]:
    return [
        "candidate",
        "category",
        "horizon_seconds",
        "cooldown_seconds",
        "window",
        "cost_bps",
        "observed_direction",
        "kept_event_count",
        "gross_mean_forward_price_return",
        "gross_median_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "net_effect_after_cost",
        "net_effect_after_cost_bps",
        "break_even_cost_bps",
        "directional_diagnostic_rate",
        "symbol_stability_rate",
        "week_stability_rate",
        "month_stability_rate",
        "latest_vs_holdout_consistency",
        "classification",
    ]


def stability_fieldnames() -> list[str]:
    return [
        "candidate",
        "category",
        "horizon_seconds",
        "cooldown_seconds",
        "window",
        "event_count",
        "observed_direction",
        "break_even_cost_bps",
        "symbol_stability_rate",
        "week_stability_rate",
        "month_stability_rate",
        "stable_all_periods",
        "directional_diagnostic_rate",
    ]


def output_sizes() -> dict[str, int]:
    paths = [SUMMARY_JSON, SUMMARY_MD, CANDIDATE_COST_GRID_CSV, STABILITY_CSV]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def write_summary_md(summary: dict[str, Any]) -> None:
    strongest = summary.get("strongest_latest_holdout_stable_candidate", {})
    sell = summary.get("sell_pressure_absorbed_300s_cost_viability", {})
    lines = [
        "# Orderbook UM 81 absorption cost viability diagnostic v1",
        "",
        f"status: {summary['status']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"source_non_overlap_status: {summary.get('source_non_overlap_status', '')}",
        f"cost_grid_bps: {', '.join(str(item) for item in summary['cost_grid_bps'])}",
        f"strongest_candidate: {strongest.get('candidate', '')} cooldown={strongest.get('cooldown_seconds', '')}s min_break_even_bps={strongest.get('min_latest_holdout_break_even_cost_bps', '')}",
        f"sell_pressure_absorbed_300s_assessment: {sell.get('assessment', '')}",
        f"row_level_dataset_created: {str(summary['row_level_dataset_created']).lower()}",
        f"parquet_dataset_created: {str(summary['parquet_dataset_created']).lower()}",
        "",
        "## Break-Even By Candidate",
        "| candidate | best cooldown | best min break-even bps | max tested cost survived both windows |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in summary.get("break_even_by_candidate", []):
        lines.append(
            "| "
            f"{row.get('candidate', '')} | {row.get('best_cooldown_seconds', '')} | "
            f"{row.get('best_min_latest_holdout_break_even_cost_bps', '')} | "
            f"{row.get('best_max_cost_bps_survived_both_windows', '')} |"
        )
    lines.extend(
        [
            "",
            "Cost is applied to the observed-direction gross effect versus the matched null baseline.",
            "This diagnostic does not create a trade rule, PnL curve, orders, private endpoint use, or recommendations.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_diagnostic() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    source_summary = load_json(NON_OVERLAP_SUMMARY_JSON)
    source_rows = read_csv_rows(NON_OVERLAP_CANDIDATE_CSV)
    cost_rows, stability_rows, cooldown_rows = build_rows(source_rows)
    break_even_rows = candidate_break_even_summary(cooldown_rows)
    strongest = strongest_candidate(cooldown_rows)
    sell_assessment = sell_pressure_assessment(break_even_rows)

    write_csv(CANDIDATE_COST_GRID_CSV, cost_grid_fieldnames(), cost_rows)
    write_csv(STABILITY_CSV, stability_fieldnames(), stability_rows)

    summary: dict[str, Any] = {
        "status": "PASS_ORDERBOOK_UM_81_ABSORPTION_COST_VIABILITY_DIAGNOSTIC",
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_ABSORPTION_COST_VIABILITY_DIAGNOSTIC_V1",
        "mode": "COMPACT_NON_OVERLAP_OUTPUT_COST_GRID",
        "source_non_overlap_status": source_summary.get("status", ""),
        "source_symbol_days_processed_total": source_summary.get("symbol_days_processed_total", 0),
        "cost_grid_bps": COST_GRID_BPS,
        "expected_candidates": [candidate_label(category, horizon) for category, horizon in EXPECTED_CANDIDATES],
        "cooldowns_seconds": EXPECTED_COOLDOWNS,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "candidate_cost_grid_row_count": len(cost_rows),
        "stability_row_count": len(stability_rows),
        "candidate_cooldown_summary": cooldown_rows,
        "break_even_by_candidate": break_even_rows,
        "strongest_latest_holdout_stable_candidate": strongest,
        "sell_pressure_absorbed_300s_cost_viability": sell_assessment,
        "classification_definitions": {
            "SURVIVES_COST": "net observed-direction effect is positive in both latest and holdout for the cost level, with stability rates at or above threshold",
            "FILTER_ONLY": "gross observed-direction effect is positive and stable, but cost stress is not cleared in both windows",
            "FAILS_COST": "gross observed-direction effect is unavailable/nonpositive, event support is too low, or stability is weak",
        },
        "cost_application": "net_effect_after_cost = gross_effect_in_observed_direction - cost_bps / 10000",
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "candidate_cost_grid_csv": str(CANDIDATE_COST_GRID_CSV),
            "stability_csv": str(STABILITY_CSV),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    summary["output_sizes_bytes"] = output_sizes()
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    try:
        summary = run_diagnostic()
    except Exception as exc:  # noqa: BLE001
        error_summary = {
            "status": "FAILED_ORDERBOOK_UM_81_ABSORPTION_COST_VIABILITY_DIAGNOSTIC",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "row_level_dataset_created": False,
            "parquet_dataset_created": False,
            "downloads_run": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Orderbook UM 81 absorption cost viability diagnostic v1\n\n"
            f"status: {error_summary['status']}\n"
            f"error: {error_summary['error']}\n",
            encoding="utf-8",
        )
        print(json.dumps(error_summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(summary.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
