# Edge factory orderbook UM 81 streaming absorption discovery 90d v1

This scanner reads verified raw Binance UM bookDepth and aggTrades ZIP files symbol-day by symbol-day, computes lean absorption and liquidity proxy diagnostics in memory, and writes compact aggregate research outputs only.

Default scope is the latest 90 available matched bookDepth plus aggTrades days per symbol across the 81-symbol universe. Setting `ORDERBOOK_81_STREAMING_ABSORPTION_DISCOVERY=YES` is reserved for all-available-history discovery.

## Inputs

- bookDepth raw ZIP root: `C:\edge_factory_external_data\binance_um_81_full_bookdepth_raw`
- aggTrades raw ZIP root: `C:\edge_factory_external_data\binance_um_81_full_matching_aggtrades_raw`
- verified bookDepth file status: `outputs/orderbook_um_81_full_bookdepth_file_status.csv`
- verified aggTrades file status: `outputs/orderbook_um_81_full_matching_aggtrades_file_status.csv`

## Outputs

- `outputs/orderbook_um_81_streaming_absorption_discovery_90d_summary.json`
- `outputs/orderbook_um_81_streaming_absorption_discovery_90d_summary.md`
- `outputs/orderbook_um_81_streaming_absorption_discovery_90d_category_horizon.csv`
- `outputs/orderbook_um_81_streaming_absorption_discovery_90d_symbol_stability.csv`
- `outputs/orderbook_um_81_streaming_absorption_discovery_90d_null_comparison.csv`
- `outputs/orderbook_um_81_streaming_absorption_discovery_90d_candidates.csv`

## Diagnostics

- horizons: 10s, 30s, 60s, 300s
- categories: `BUY_PRESSURE_ABSORBED`, `SELL_PRESSURE_ABSORBED`, `FLOW_AND_DEPTH_ALIGNED_UP`, `FLOW_AND_DEPTH_ALIGNED_DOWN`, `MIXED_OR_NOISY`, `INSUFFICIENT_DATA`
- forward proxy return: future rolling depth-imbalance proxy minus current rolling depth-imbalance proxy
- directional diagnostic rate: share of nonzero category-direction observations matching nonzero forward proxy direction
- null comparison: category result compared with the same-horizon all-category baseline
- stability: symbol, month, and week consistency for compact research ranking
- volatility split: high and low groups based on median day-level depth-imbalance delta standard deviation

## Safety boundaries

- No downloads.
- No full dataset materialization.
- No row-level parquet.
- No live trading.
- No orders.
- No private endpoints.
- No entries, exits, stops, targets, position sizing, leverage, or PnL.
- No trading recommendations.
- Raw ZIPs stay outside the repository.
- Raw extracted CSV files are not written inside the repository.

## Commands

Run latest 90-day discovery:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_streaming_absorption_discovery_90d_v1.ps1
```

Validate compact outputs:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_streaming_absorption_discovery_90d_validator_v1.ps1
```

Run all-available-history discovery only when explicitly intended:

```powershell
$env:ORDERBOOK_81_STREAMING_ABSORPTION_DISCOVERY='YES'
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_streaming_absorption_discovery_90d_v1.ps1
```
