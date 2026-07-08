# Causal capacity filter repair v1

Task: `ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR_V1`

This diagnostic repairs the previously blocked capacity-aware refinement for the locked research candidate:

- candidate: `SELL_PRESSURE_ABSORBED@300s`
- cooldown: `600s`
- scope: latest 90d plus the disjoint holdout 90d
- symbols: all 81 verified Binance UM symbols

The previous `MIN_AROUND_EVENT_NOTIONAL_100000` result is invalidated and must not be used. It was based on around-event notional and included post-event trades through a future window ending after the event timestamp. That family is reported only as `NON_CAUSAL_DIAGNOSTIC`; it is not used for selection.

## Causal Filters

The repair tests only filters that can be known at or before the event timestamp:

- trailing aggTrades notional before the event: previous 60s, 300s, and 600s
- trailing aggTrades trade count before the event: previous 60s, 300s, and 600s
- event-time bookDepth notional proxy from the feature row at the event timestamp
- causal prior-7-day symbol liquidity ranking from aggTrades ZIP sizes before the window starts

Thresholds tested:

- trailing notional greater than or equal to 5k, 10k, 25k, 50k, and 100k
- trailing trade count greater than or equal to 5, 10, 25, 50, and 100
- event-time bookDepth notional greater than or equal to 5k, 10k, 25k, 50k, and 100k
- top 10, top 20, top 40, and exclude causal THIN by prior-7-day liquidity rank

## Guardrails

The repair does not use future information for capacity selection:

- no `event_ms + window` selection
- no post-event notional selection
- no post-event trade-count selection
- no post-event volatility selection
- no around-event filters except report-only invalidation rows marked `NON_CAUSAL_DIAGNOSTIC`

This is a research diagnostic only. It does not download data, alter raw ZIPs, create a parquet dataset, create row-level output, create strategy logic, run a backtest, create PnL, place orders, use private endpoints, or make recommendations.

## Outputs

The diagnostic writes compact outputs under `outputs/`:

- `orderbook_um_81_causal_capacity_filter_repair_summary.json`
- `orderbook_um_81_causal_capacity_filter_repair_summary.md`
- `orderbook_um_81_causal_capacity_filter_repair_subset_summary.csv`
- `orderbook_um_81_causal_capacity_filter_repair_delay_cost_grid.csv`
- `orderbook_um_81_causal_capacity_filter_repair_invalidated_non_causal_filters.json`
- `orderbook_um_81_causal_capacity_filter_repair_prior_liquidity_symbol_rank.csv`
- `orderbook_um_81_causal_capacity_filter_repair_validator_report.json`
- `orderbook_um_81_causal_capacity_filter_repair_validator_report.md`

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_causal_capacity_filter_repair_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_causal_capacity_filter_repair_validator_v1.ps1
```
