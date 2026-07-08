# Sell pressure absorbed capacity-aware refinement v1

This diagnostic tests the locked candidate `SELL_PRESSURE_ABSORBED@300s` with a fixed 600 second cooldown over the latest 90-day window and the previous disjoint holdout 90-day window only.

It uses the existing execution-delay capacity diagnostic reader path and evaluates only the requested capacity-aware subsets:

- HIGH only
- HIGH + MEDIUM
- exclude THIN
- top 10, top 20, and top 40 symbols by around-event notional
- minimum around-event notional thresholds of 5k, 10k, 25k, 50k, and 100k

Locked settings:

- category: SELL_PRESSURE_ABSORBED
- horizon: 300 seconds
- cooldown: 600 seconds
- delays: 0, 1, 3, 5, 10 seconds
- costs: 0, 1, 2, 3, 5 bps

Outputs:

- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_summary.json
- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_summary.md
- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_subset_summary.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_delay_cost_grid.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_symbol_selection.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_capacity_by_symbol_window.csv
- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_validator_report.json
- outputs/orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_validator_report.md

Safety boundaries:

- No downloads.
- No full-history scan in this task.
- No full parquet dataset.
- No row-level dataset.
- No new feature discovery.
- No strategy, backtest, signal, PnL curve, entries, exits, stops, targets, leverage, orders, private endpoints, live trading, paper trading, or recommendations.

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_validator_v1.ps1
```
