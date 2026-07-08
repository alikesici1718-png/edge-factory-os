# Orderbook UM 81 full matching aggTrades download notes v1

Task: ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_DOWNLOAD_V1

Scope:

- Public Binance Data Vision USD-M Futures daily aggTrades ZIP archives only.
- Existing verified 81-symbol bookDepth universe only.
- Download only aggTrades rows that match verified same-day bookDepth coverage.
- Older extra aggTrades history outside verified bookDepth coverage is deliberately excluded.
- Raw ZIP files remain outside the git repository.
- The external data root defaults to `C:\edge_factory_external_data` unless `EDGE_FACTORY_DATA_ROOT` is set.
- The full matching raw target directory is `binance_um_81_full_matching_aggtrades_raw` under the external data root.
- The logs and checksum directory is `binance_um_81_full_matching_aggtrades_logs` under the external data root.

Matching manifest inputs:

- `outputs/orderbook_um_81_aggtrades_availability_manifest.csv`
- `outputs/orderbook_um_81_aggtrades_coverage_summary.json`
- `outputs/orderbook_um_81_aggtrades_vs_bookdepth_coverage_gaps.csv`
- `outputs/orderbook_um_81_full_bookdepth_symbol_coverage.csv`
- `outputs/orderbook_um_81_full_bookdepth_download_summary.json`

Manifest filter rules:

- `symbol` must be in the verified 81-symbol bookDepth universe.
- `data_type` must be `aggTrades`.
- `frequency` must be `daily`.
- `bookdepth_available_same_day` must be `true`.
- `aggtrades_available_same_day` must be `true`.
- `file_date` must be inside that symbol's verified bookDepth coverage.
- `status` must be `AVAILABLE`.

Expected matching slice:

- Expected matching file count: `99,404`.
- Estimated matching size: about `214.747592 GB`.
- The broader aggTrades availability set is about `384.339696 GB` and must not be downloaded for this task.

Safety boundaries:

- No API keys.
- No private or account endpoints.
- No order execution.
- No paper trading or live trading.
- No strategy, backtest, signal generator, recommendation, entry, exit, stop, leverage, PnL, target, or position sizing logic.
- No raw ZIP extraction into the git repository.

Execution:

1. Run `run_orderbook_um_81_full_matching_aggtrades_manifest_validator_v1.ps1`.
2. Review `outputs/orderbook_um_81_full_matching_aggtrades_manifest_validation.json`.
3. Confirm expected matching file count and disk space.
4. Set `AGGTRADES_81_FULL_MATCHING_DOWNLOAD=YES`.
5. Run `run_orderbook_um_81_full_matching_aggtrades_downloader_v1.ps1`.
6. Run `run_orderbook_um_81_full_matching_aggtrades_download_validator_v1.ps1`.

Parallel downloader:

- The downloader uses a bounded `ThreadPoolExecutor` queue for independent daily aggTrades ZIP files.
- `AGGTRADES_DOWNLOAD_WORKERS` controls worker count.
- Default workers: `8`.
- Allowed worker range: `1` to `32`; non-numeric values are rejected, and out-of-range numeric values are clamped with a warning.
- Recommended worker values for this archive are `12` or `16` on a stable connection.
- Timeout and retry controls:
  - `AGGTRADES_DOWNLOAD_CONNECT_TIMEOUT`, default `20`.
  - `AGGTRADES_DOWNLOAD_READ_TIMEOUT`, default `120`.
  - `AGGTRADES_DOWNLOAD_MAX_RETRIES`, default `5`.

Recommended 16-worker run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$env:EDGE_FACTORY_DATA_ROOT="C:\edge_factory_external_data"
$env:AGGTRADES_81_FULL_MATCHING_DOWNLOAD="YES"
$env:AGGTRADES_DOWNLOAD_WORKERS="16"
.\run_orderbook_um_81_full_matching_aggtrades_downloader_v1.ps1
```

If the download is too aggressive for the network or disk, lower workers to `8`:

```powershell
$env:AGGTRADES_DOWNLOAD_WORKERS="8"
.\run_orderbook_um_81_full_matching_aggtrades_downloader_v1.ps1
```

Resume behavior:

- The downloader is restartable.
- Existing ZIP files are skipped only after checksum verification.
- Each ZIP downloads to a `.part` file first.
- The `.part` file is checksum-verified before it is renamed to the final `.zip`.
- If checksum verification fails, the `.part` file is deleted and the file is retried within the configured retry limit.
- Re-running the downloader skips final ZIP files only when their checksum verifies.
- Files with missing checksum URLs are marked `NO_CHECKSUM_AVAILABLE` or equivalent and are not counted as checksum verified.
- Repeated checksum mismatch fails closed and writes a failure summary.

Expected repo outputs:

- `outputs/orderbook_um_81_full_matching_aggtrades_manifest_validation.json`
- `outputs/orderbook_um_81_full_matching_aggtrades_manifest_validation.md`
- `outputs/orderbook_um_81_full_matching_aggtrades_download_manifest.csv`
- `outputs/orderbook_um_81_full_matching_aggtrades_download_manifest.jsonl`
- `outputs/orderbook_um_81_full_matching_aggtrades_download_summary.json`
- `outputs/orderbook_um_81_full_matching_aggtrades_download_summary.md`
- `outputs/orderbook_um_81_full_matching_aggtrades_file_status.csv`
- `outputs/orderbook_um_81_full_matching_aggtrades_symbol_coverage.csv`
- `outputs/orderbook_um_81_full_matching_aggtrades_download_validator_report.json`
- `outputs/orderbook_um_81_full_matching_aggtrades_download_validator_report.md`

Blocked routes:

- If `AGGTRADES_81_FULL_MATCHING_DOWNLOAD` is not `YES`, the downloader does not start and writes `outputs/orderbook_um_81_full_matching_aggtrades_BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED.md`.
- If the target disk does not have enough free space for the remaining matching download with the safety multiplier, the process reports `BLOCKED_INSUFFICIENT_DISK_FOR_FULL_MATCHING_AGGTRADES`.
