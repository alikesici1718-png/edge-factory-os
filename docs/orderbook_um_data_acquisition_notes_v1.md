# Binance USD-M orderbook data acquisition notes v1

This route is a public-data-only availability audit, manifest validator, and small pilot downloader for Binance USD-M Futures Data Vision `bookDepth` archives over the existing Binance/OKX 81-symbol overlap universe.

It is not allowed to create trading logic, private/account/API-key access, buy signal or sell signal outputs, leverage handling, position size logic, entry rules, take profit rules, stop loss rules, live trading, paper trading, or any capital/runtime launcher.

## Files

- `src/edge_factory_orderbook_um_availability_audit_v1.py`
- `src/edge_factory_orderbook_um_manifest_validator_v1.py`
- `src/edge_factory_orderbook_um_pilot_downloader_v1.py`
- `run_orderbook_um_availability_audit_v1.ps1`
- `run_orderbook_um_manifest_validator_v1.ps1`
- `run_orderbook_um_pilot_download_v1.ps1`

## Data root

Default external data root:

`C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data`

Override with `EDGE_FACTORY_DATA_ROOT`. The runners and Python modules refuse to continue if that path resolves inside the git repo.

Expected external subdirectories:

- `binance_um_orderbook_raw`
- `binance_um_orderbook_manifest`
- `binance_um_orderbook_pilot`
- `binance_um_orderbook_logs`

## Safe execution order

1. `.\run_orderbook_um_availability_audit_v1.ps1`
2. `.\run_orderbook_um_manifest_validator_v1.ps1`
3. `.\run_orderbook_um_pilot_download_v1.ps1`

The default downloader mode is pilot-only. It downloads BTCUSDT earliest/latest daily `bookDepth`, ETHUSDT latest, and SOLUSDT latest when those files exist in the manifest.

## Full download lock

Full historical download remains blocked unless every lock is present:

- `ORDERBOOK_FULL_DOWNLOAD=YES`
- `I_ACKNOWLEDGE_ORDERBOOK_DOWNLOAD_SIZE=YES`
- the manifest validator passes
- free disk is at least estimated total size times 1.25
- the external data root is outside the repo
- `outputs/ALLOW_ORDERBOOK_FULL_DOWNLOAD.txt` contains exactly `ALLOW_FULL_ORDERBOOK_DOWNLOAD`

If any lock is missing, the downloader stops with `BLOCKED_FULL_DOWNLOAD_LOCKED`.
