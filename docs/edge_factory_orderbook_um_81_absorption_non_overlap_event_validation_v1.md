# Orderbook UM 81 absorption non-overlap event validation v1

This tool validates the previously surviving absorption candidates after removing overlapping observations. It streams the verified raw bookDepth and aggTrades ZIPs symbol-day by symbol-day, computes the same lean research features through the existing price-linkage reader, and writes only compact aggregate diagnostics.

Scope:

- all 81 symbols
- latest 90 available days
- previous disjoint 90 available days before the latest window
- cooldowns of 300, 600, and 900 seconds
- fixed candidates only: SELL_PRESSURE_ABSORBED at 300s, FLOW_AND_DEPTH_ALIGNED_DOWN at 300s, 60s, and 30s

The cooldown rule is applied independently per symbol and candidate. The first event is kept, then later events inside the cooldown window are suppressed. The null comparison uses all valid bookDepth timestamps at the same horizon with the same per-symbol cooldown logic where feasible.

Outputs:

- outputs/orderbook_um_81_absorption_non_overlap_event_validation_summary.json
- outputs/orderbook_um_81_absorption_non_overlap_event_validation_summary.md
- outputs/orderbook_um_81_absorption_non_overlap_event_validation_candidate_cooldown.csv
- outputs/orderbook_um_81_absorption_non_overlap_event_validation_symbol_stability.csv
- outputs/orderbook_um_81_absorption_non_overlap_event_validation_null_comparison.csv
- outputs/orderbook_um_81_absorption_non_overlap_event_validation_validator_report.json
- outputs/orderbook_um_81_absorption_non_overlap_event_validation_validator_report.md

Safety boundaries:

- No downloads.
- No full parquet dataset.
- No row-level dataset.
- No strategy, backtest, signal, PnL, entry, exit, stop, target, leverage, order execution, private endpoint, or trading recommendation logic.
- Raw ZIPs stay outside the repo and are read only.

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_absorption_non_overlap_event_validation_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_absorption_non_overlap_event_validation_validator_v1.ps1
```
