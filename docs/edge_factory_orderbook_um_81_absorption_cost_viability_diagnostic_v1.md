# Orderbook UM 81 absorption cost viability diagnostic v1

This diagnostic uses the compact non-overlap absorption validation outputs to stress the fixed surviving candidates against simple cost assumptions. It does not reopen raw ZIPs and does not create row-level or parquet data.

Inputs:

- outputs/orderbook_um_81_absorption_non_overlap_event_validation_summary.json
- outputs/orderbook_um_81_absorption_non_overlap_event_validation_candidate_cooldown.csv

Cost grid:

- 0 bps
- 0.5 bps
- 1 bps
- 2 bps
- 3 bps
- 5 bps
- 10 bps

Method:

- Use the observed latest+holdout effect direction from the non-overlap validation.
- Convert signed gross effect versus null into observed-direction gross edge.
- Apply cost as `cost_bps / 10000`.
- Report net effect after cost, break-even cost, stability rates, and classifications.

Outputs:

- outputs/orderbook_um_81_absorption_cost_viability_summary.json
- outputs/orderbook_um_81_absorption_cost_viability_summary.md
- outputs/orderbook_um_81_absorption_cost_viability_candidate_cost_grid.csv
- outputs/orderbook_um_81_absorption_cost_viability_stability.csv
- outputs/orderbook_um_81_absorption_cost_viability_validator_report.json
- outputs/orderbook_um_81_absorption_cost_viability_validator_report.md

Safety boundaries:

- No downloads.
- No full parquet dataset.
- No row-level dataset.
- No strategy, backtest, signal, PnL curve, orders, private endpoint, or recommendations.

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_absorption_cost_viability_diagnostic_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_absorption_cost_viability_validator_v1.ps1
```
