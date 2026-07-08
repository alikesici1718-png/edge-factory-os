# Orderbook UM 81 aggTrades availability and size notes v1

Task: ORDERBOOK_UM_81_SYMBOL_AGGTRADES_AVAILABILITY_SIZE_AUDIT_V1

Scope:

- Public Binance Data Vision USD-M Futures daily aggTrades listings only.
- Existing verified 81-symbol bookDepth universe only.
- Manifest, coverage, and size audit only.
- No raw aggTrades ZIP download.
- Raw market data remains outside the git repository.

Inputs:

- `outputs/orderbook_um_bookdepth_availability_manifest.csv`
- `outputs/orderbook_um_bookdepth_coverage_summary.json`
- `outputs/orderbook_um_81_full_bookdepth_download_summary.json`
- `outputs/orderbook_um_81_full_bookdepth_symbol_coverage.csv`

Outputs:

- `outputs/orderbook_um_81_aggtrades_availability_manifest.csv`
- `outputs/orderbook_um_81_aggtrades_availability_manifest.jsonl`
- `outputs/orderbook_um_81_aggtrades_coverage_summary.json`
- `outputs/orderbook_um_81_aggtrades_coverage_summary.md`
- `outputs/orderbook_um_81_aggtrades_vs_bookdepth_coverage_gaps.csv`
- `outputs/orderbook_um_81_aggtrades_manifest_validator_report.json`
- `outputs/orderbook_um_81_aggtrades_manifest_validator_report.md`

Run:

```powershell
.\run_orderbook_um_81_aggtrades_availability_size_audit_v1.ps1
.\run_orderbook_um_81_aggtrades_manifest_validator_v1.ps1
```

Safety boundaries:

- No API keys.
- No private or account endpoints.
- No live trading.
- No paper trading.
- No order execution.
- No candidate generation for trading.
- No strategy, backtest, signal, entry, exit, stop, target, position sizing, leverage, PnL, buy or sell labels, or recommendations.

Next action options:

- A) full 81-symbol aggTrades download if size is acceptable.
- B) recent-window aggTrades download if full size is too large.
- C) stop due to missing or unsupported coverage.
