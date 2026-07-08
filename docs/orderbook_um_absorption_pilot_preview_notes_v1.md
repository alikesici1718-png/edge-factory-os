# Orderbook UM absorption pilot preview notes v1

This route downloads only the four matching Binance USD-M Futures Data Vision daily `aggTrades` pilot ZIP files for the existing bookDepth pilot symbols/dates. Raw ZIPs stay outside the repo under `binance_um_aggtrades_pilot`.

Binance aggTrades convention used here: when `isBuyerMaker` is true, the buyer was the maker and the aggressive/taker side is sell. When `isBuyerMaker` is false, the aggressive/taker side is buy.

The absorption preview aligns trailing aggTrades windows ending at each bookDepth timestamp. For timestamp T, feature construction uses only aggTrades with timestamps less than or equal to T. Forward-return columns remain diagnostics from the existing bookDepth mid proxy and are not features for any live or paper action.

## Run sequence

1. `.\run_orderbook_um_aggtrades_pilot_download_v1.ps1`
2. `.\run_orderbook_um_absorption_pilot_preview_v1.ps1`
3. `.\run_orderbook_um_absorption_pilot_validator_v1.ps1`

## Output files

- `outputs/orderbook_um_aggtrades_pilot_schema_summary.json`
- `outputs/orderbook_um_aggtrades_pilot_schema_summary.md`
- `outputs/orderbook_um_absorption_pilot_preview_summary.json`
- `outputs/orderbook_um_absorption_pilot_preview_summary.md`
- `outputs/orderbook_um_absorption_pilot_quantile_diagnostics.csv`
- `outputs/orderbook_um_absorption_pilot_category_diagnostics.csv`
- `outputs/orderbook_um_absorption_pilot_quality_report.md`
- `outputs/orderbook_um_absorption_pilot_sample.csv`
- `outputs/orderbook_um_absorption_pilot_sample.parquet` when `pyarrow` is available

## Safety boundary

Absorption categories are diagnostic categories only: `BUY_PRESSURE_ABSORBED`, `SELL_PRESSURE_ABSORBED`, `FLOW_AND_DEPTH_ALIGNED_UP`, `FLOW_AND_DEPTH_ALIGNED_DOWN`, `MIXED_OR_NOISY`, and `INSUFFICIENT_DATA`.

They are not trade signals, buy/sell labels, entries, exits, stops, targets, position sizing, leverage logic, PnL, or recommendations.
