# Causal trailing trade-count full-history validation v1

Task: `ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATION_V1`

This scanner validates the locked research candidate across the full verified history using resumable month chunks:

- candidate: `SELL_PRESSURE_ABSORBED@300s`
- cooldown: `600s`
- causal filter: `TRAILING_TRADE_COUNT_60S_GE_100`
- coverage: `2023-01-01` to `2026-06-15`
- symbols: all 81 verified Binance UM symbols

The locked filter uses only aggTrades count in `[event_ms - 60s, event_ms)`. It does not use future-window selection, post-event notional, post-event trade count, or around-event capacity helpers.

The scanner writes compact research diagnostics only. Each completed month is written before the next month starts, and reruns skip already completed contiguous chunks:

- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_summary.json`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_summary.md`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_period_stability.csv`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_symbol_stability.csv`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_delay_cost_grid.csv`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_null_comparison.csv`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_chunk_progress.csv`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_completed_chunks_manifest.json`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_partial_aggregate_summaries.json`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_chunks/*_chunk_summary.json`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_validator_report.json`
- `orderbook_um_81_causal_trailing_trade_count_full_history_validation_validator_report.md`

Chunk controls:

- `ORDERBOOK_FULL_HISTORY_CHUNK_PERIOD`: `month` by default; `quarter` is accepted.
- `ORDERBOOK_FULL_HISTORY_CHUNK_LIMIT`: optional number of new chunks to process, useful for smoke runs.
- `ORDERBOOK_FULL_HISTORY_CHUNK_WORKERS`: default `1`, capped at `4`; effective execution remains sequential for exact cross-chunk cooldown carry-forward.

Smoke:

```powershell
$env:ORDERBOOK_FULL_HISTORY_CHUNK_PERIOD='month'
$env:ORDERBOOK_FULL_HISTORY_CHUNK_LIMIT='1'
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_validator_v1.ps1
```

Resume/full run after approval:

```powershell
$env:ORDERBOOK_FULL_HISTORY_CHUNK_PERIOD='month'
Remove-Item Env:ORDERBOOK_FULL_HISTORY_CHUNK_LIMIT -ErrorAction SilentlyContinue
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.ps1
```

This is research validation only. It does not download data, modify raw ZIPs, create a parquet dataset, create row-level output, create strategy logic, run a backtest, create signals, create a PnL curve, place orders, use private endpoints, or make recommendations.

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_validator_v1.ps1
```
