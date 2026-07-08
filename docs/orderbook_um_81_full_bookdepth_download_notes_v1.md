# Orderbook UM 81 full bookDepth download notes v1

Task: ORDERBOOK_UM_81_SYMBOL_FULL_BOOKDEPTH_DOWNLOAD_V1

Scope:

- Public Binance Data Vision USD-M Futures daily bookDepth ZIP archives only.
- Existing 81-symbol universe only.
- Raw ZIP files remain outside the git repository.
- The external data root defaults to `C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data` unless `EDGE_FACTORY_DATA_ROOT` is set.
- The full raw target directory is `binance_um_81_full_bookdepth_raw` under the external data root.
- The logs and checksum directory is `binance_um_81_full_bookdepth_logs` under the external data root.

Safety boundaries:

- No API keys.
- No private or account endpoints.
- No order execution.
- No paper trading or live trading.
- No strategy, signal generator, recommendation, entry, exit, stop, leverage, PnL, or position sizing logic.
- No aggTrades download is part of this task.

Execution:

1. Run `run_orderbook_um_81_full_bookdepth_manifest_validator_v1.ps1`.
2. Review `outputs/orderbook_um_81_full_bookdepth_manifest_validation.json`.
3. Set `ORDERBOOK_81_FULL_BOOKDEPTH_DOWNLOAD=YES`.
4. Run `run_orderbook_um_81_full_bookdepth_downloader_v1.ps1`.
5. Run `run_orderbook_um_81_full_bookdepth_download_validator_v1.ps1`.

Parallel downloader:

- The downloader uses a bounded `ThreadPoolExecutor` queue for independent daily bookDepth ZIP files.
- `ORDERBOOK_DOWNLOAD_WORKERS` controls worker count.
- Default workers: `8`.
- Allowed worker range: `1` to `32`; non-numeric values are rejected, and out-of-range numeric values are clamped with a warning.
- Recommended worker values for this 99,404-file archive are `12` or `16` on a stable connection.
- Timeout and retry controls:
  - `ORDERBOOK_DOWNLOAD_CONNECT_TIMEOUT`, default `20`.
  - `ORDERBOOK_DOWNLOAD_READ_TIMEOUT`, default `120`.
  - `ORDERBOOK_DOWNLOAD_MAX_RETRIES`, default `5`.

Recommended 16-worker run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$env:EDGE_FACTORY_DATA_ROOT="C:\edge_factory_external_data"
$env:ORDERBOOK_81_FULL_BOOKDEPTH_DOWNLOAD="YES"
$env:ORDERBOOK_DOWNLOAD_WORKERS="16"
.\run_orderbook_um_81_full_bookdepth_downloader_v1.ps1
```

If the download is too aggressive for the network or disk, lower workers to `8`:

```powershell
$env:ORDERBOOK_DOWNLOAD_WORKERS="8"
.\run_orderbook_um_81_full_bookdepth_downloader_v1.ps1
```

OneDrive warning:

- The default external data root is under OneDrive on this machine.
- OneDrive is allowed, but large parallel downloads may sync slowly or add filesystem overhead.
- For the full archive, prefer `C:\edge_factory_external_data` when available.

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

- `outputs/orderbook_um_81_full_bookdepth_manifest_validation.json`
- `outputs/orderbook_um_81_full_bookdepth_manifest_validation.md`
- `outputs/orderbook_um_81_full_bookdepth_download_summary.json`
- `outputs/orderbook_um_81_full_bookdepth_download_summary.md`
- `outputs/orderbook_um_81_full_bookdepth_file_status.csv`
- `outputs/orderbook_um_81_full_bookdepth_symbol_coverage.csv`
- `outputs/orderbook_um_81_full_bookdepth_download_validator_report.json`
- `outputs/orderbook_um_81_full_bookdepth_download_validator_report.md`

If `ORDERBOOK_81_FULL_BOOKDEPTH_DOWNLOAD` is not `YES`, the downloader does not start and writes:

- `outputs/orderbook_um_81_full_bookdepth_BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED.md`
