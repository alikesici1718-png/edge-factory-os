# Sell pressure absorbed full-history validation v1

This scanner validates the locked candidate `SELL_PRESSURE_ABSORBED@300s` with a fixed 600 second cooldown over the verified full history from 2023-01-01 through 2026-06-15 for all 81 symbols.

Locked settings:

- category: SELL_PRESSURE_ABSORBED
- horizon: 300 seconds
- cooldown: 600 seconds
- observed price direction: negative price effect from the prior validation chain

The scanner streams verified bookDepth and aggTrades ZIPs symbol-day by symbol-day, computes the existing lean absorption features through the existing reader, and writes only compact aggregate diagnostics.

Outputs:

- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_summary.json
- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_summary.md
- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_period_stability.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_symbol_stability.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_cost_grid.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_null_comparison.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_validator_report.json
- outputs/orderbook_um_81_sell_pressure_absorbed_full_history_validation_validator_report.md

Safety boundaries:

- No downloads.
- No full parquet dataset.
- No row-level dataset.
- No new filters.
- No strategy, backtest, signal, PnL curve, entries, exits, stops, targets, leverage, orders, private endpoints, or recommendations.

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_sell_pressure_absorbed_full_history_validation_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_sell_pressure_absorbed_full_history_validation_validator_v1.ps1
```
