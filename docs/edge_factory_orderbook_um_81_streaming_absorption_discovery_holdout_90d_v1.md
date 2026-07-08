# Edge factory orderbook UM 81 streaming absorption discovery holdout 90d v1

This holdout run validates the five previously discovered latest-90d absorption candidates on the disjoint previous 90 available matched symbol-days for each of the 81 symbols.

It reuses the existing latest-90d streaming absorption discovery feature construction, horizons, categories, null comparison method, and stability metrics. It does not optimize thresholds, add features, or change category definitions.

## Fixed Candidates

1. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 300s`
2. `SELL_PRESSURE_ABSORBED @ 300s`
3. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 60s`
4. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 30s`
5. `FLOW_AND_DEPTH_ALIGNED_DOWN @ 10s`

## Window

- latest window skipped per symbol: 90 available matched days
- holdout window per symbol: the immediately preceding 90 available matched days
- symbols: all 81
- horizons: 10s, 30s, 60s, 300s

## Outputs

- `outputs/orderbook_um_81_streaming_absorption_discovery_holdout_90d_summary.json`
- `outputs/orderbook_um_81_streaming_absorption_discovery_holdout_90d_summary.md`
- `outputs/orderbook_um_81_streaming_absorption_discovery_holdout_90d_candidate_comparison.csv`
- `outputs/orderbook_um_81_streaming_absorption_discovery_holdout_90d_sign_audit.csv`
- `outputs/orderbook_um_81_streaming_absorption_discovery_holdout_90d_stability.csv`
- `outputs/orderbook_um_81_streaming_absorption_discovery_holdout_90d_validator_report.json`
- `outputs/orderbook_um_81_streaming_absorption_discovery_holdout_90d_validator_report.md`

## Sign Convention

The forward proxy return is `future rolling depth-imbalance proxy minus current rolling depth-imbalance proxy`.

Positive proxy means the rolling bid-vs-ask depth imbalance proxy increased. It is not a verified price-up movement.

`FLOW_AND_DEPTH_ALIGNED_DOWN` means contemporaneous rolling flow pressure is negative and rolling depth imbalance is negative. If this category has a positive forward proxy result, the name is ambiguous for forward interpretation because the forward proxy moved upward even though the current-state category name contains `DOWN`.

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

Run holdout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_streaming_absorption_discovery_holdout_90d_v1.ps1
```

Validate holdout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_streaming_absorption_discovery_holdout_90d_validator_v1.ps1
```
