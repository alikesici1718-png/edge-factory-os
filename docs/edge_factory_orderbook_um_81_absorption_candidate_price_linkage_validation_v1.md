# Edge factory orderbook UM 81 absorption candidate price linkage validation v1

This validation checks whether the five surviving absorption candidates from latest-90d and holdout-90d discovery also show linkage to actual forward aggTrades price returns.

It reuses the existing streaming absorption feature and category logic. It does not rediscover candidates, optimize thresholds, add features, or write a row-level dataset.

## Fixed Candidates

1. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 300s`
2. `SELL_PRESSURE_ABSORBED @ 300s`
3. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 60s`
4. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 30s`
5. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 10s`

## Windows

- latest 90 available matched symbol-days
- previous disjoint 90 available matched symbol-days
- all 81 symbols

## Price Return Definition

Reference price is the last aggTrade price at or before the absorption event timestamp.

Future price is the first aggTrade price at or after event timestamp plus the candidate horizon.

Forward price return is `future_price / reference_price - 1`.

## Outputs

- `outputs/orderbook_um_81_absorption_candidate_price_linkage_summary.json`
- `outputs/orderbook_um_81_absorption_candidate_price_linkage_summary.md`
- `outputs/orderbook_um_81_absorption_candidate_price_linkage_candidate_comparison.csv`
- `outputs/orderbook_um_81_absorption_candidate_price_linkage_symbol_stability.csv`
- `outputs/orderbook_um_81_absorption_candidate_price_linkage_null_comparison.csv`
- `outputs/orderbook_um_81_absorption_candidate_price_linkage_validator_report.json`
- `outputs/orderbook_um_81_absorption_candidate_price_linkage_validator_report.md`

## Safety Boundaries

- No downloads.
- No full parquet dataset.
- No row-level dataset.
- No strategy.
- No backtest.
- No signal.
- No PnL.
- No entries, exits, stops, targets, leverage, or position sizing.
- No orders.
- No private endpoints.
- No recommendations.

## Commands

Run validation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validation_v1.ps1
```

Validate outputs:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validator_v1.ps1
```
