# Sell pressure absorbed execution delay capacity diagnostic v1

This diagnostic validates the locked candidate `SELL_PRESSURE_ABSORBED@300s` with a fixed 600 second cooldown over the latest 90-day window and the previous disjoint holdout 90-day window only.

Locked settings:

- category: SELL_PRESSURE_ABSORBED
- horizon: 300 seconds
- cooldown: 600 seconds
- delays: 0, 1, 3, 5, 10, 30 seconds
- costs: 0, 0.5, 1, 2, 3, 5, 10 bps
- observed price direction: negative price effect from the prior validation chain

The scanner streams verified bookDepth and aggTrades ZIPs symbol-day by symbol-day, computes the existing lean absorption features through the existing reader, applies the fixed non-overlap cooldown, and writes only compact aggregate diagnostics.

Outputs:

- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_summary.json
- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_summary.md
- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_delay_cost_grid.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_capacity_by_symbol_window.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_stability.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_null_comparison.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_validator_report.json
- outputs/orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_validator_report.md

Safety boundaries:

- No downloads.
- No full-history scan in this task.
- No full parquet dataset.
- No row-level dataset.
- No new filters.
- No threshold optimization.
- No strategy, backtest, signal, PnL curve, entries, exits, stops, targets, leverage, orders, private endpoints, live trading, paper trading, or recommendations.

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_diagnostic_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_validator_v1.ps1
```
