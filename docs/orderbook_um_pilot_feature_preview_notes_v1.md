# Orderbook UM pilot feature preview notes v1

This module reads only the already downloaded Binance USD-M Futures Data Vision `bookDepth` pilot ZIP files from the external data root. It does not download full history, does not use API keys, and does not use private/account/order endpoints.

The observed pilot schema is `timestamp`, `percentage`, `depth`, and `notional`. That schema supports percentage-depth diagnostics and price proxies derived from notional divided by depth. It does not expose exact top-of-book price levels or level-1 queue quantities.

## Run sequence

1. `.\run_orderbook_um_pilot_feature_preview_v1.ps1`
2. `.\run_orderbook_um_pilot_feature_validator_v1.ps1`

## Output files

- `outputs/orderbook_um_pilot_feature_preview_summary.json`
- `outputs/orderbook_um_pilot_feature_preview_summary.md`
- `outputs/orderbook_um_pilot_feature_quantile_diagnostics.csv`
- `outputs/orderbook_um_pilot_feature_quality_report.md`
- `outputs/orderbook_um_pilot_feature_sample.csv`
- `outputs/orderbook_um_pilot_feature_sample.parquet` when `pyarrow` is available

## Safety boundary

The generated forward-return columns are diagnostics from the pilot mid-price proxy only. They are not trade labels, entries, exits, stops, targets, position sizing, leverage logic, PnL, signals, or recommendations.

The next safe step after a passing validator is to add aggTrades pilot data for absorption diagnostics, not to run a full historical bookDepth download.
