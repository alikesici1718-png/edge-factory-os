# Orderbook UM 81 Full Absorption Dataset Notes V1

This module builds a research-only aligned dataset from the verified 81-symbol Binance UM bookDepth and matching aggTrades downloads.

## Scope

- Dataset construction only.
- Uses public Data Vision ZIP files already downloaded and checksum verified.
- Raw ZIPs stay outside the repo:
  - `C:\edge_factory_external_data\binance_um_81_full_bookdepth_raw`
  - `C:\edge_factory_external_data\binance_um_81_full_matching_aggtrades_raw`
- Dataset partitions are written outside the repo by default:
  - `C:\edge_factory_external_data\binance_um_81_full_absorption_dataset_v1`
- Override output root with `ABSORPTION_DATASET_OUTPUT_ROOT`.
- Enable compact lean output with `ORDERBOOK_81_FULL_ABSORPTION_LEAN_MODE=YES`.
- No account, private endpoint, order execution, recommendation, strategy, backtest, signal, PnL, entry, exit, stop, target, leverage, or position sizing logic is part of this module.

## Default Run

Default mode is estimate/smoke only:

```powershell
.\run_orderbook_um_81_full_absorption_dataset_builder_v1.ps1
```

The builder creates:

- `outputs/orderbook_um_81_full_absorption_dataset_build_summary.json`
- `outputs/orderbook_um_81_full_absorption_dataset_build_summary.md`
- `outputs/orderbook_um_81_full_absorption_dataset_partition_manifest.csv`

The builder estimates output rows and parquet size before any full build. It refuses full mode when disk is insufficient or when a parquet writer is unavailable.

## Lean Mode

Lean mode keeps only research-essential absorption and liquidity proxy fields and writes a smaller parquet schema:

- timestamp, symbol, file date, year month
- absorption category
- trade count
- total quantity and total notional
- aggressive buy and sell quantity/notional
- flow imbalance
- rolling flow pressure
- depth imbalance proxy
- rolling depth imbalance proxy
- flow-depth divergence proxy
- spread and microprice proxies when inferable
- data quality flags

Lean mode drops bulky raw bucket depth/notional intermediates and writes downcast numeric columns where safe. Category-like string fields use dictionary encoding when supported by the parquet engine. Smoke mode reports both standard and lean parquet estimates.

Run lean smoke:

```powershell
$env:ORDERBOOK_81_FULL_ABSORPTION_LEAN_MODE='YES'; .\run_orderbook_um_81_full_absorption_dataset_builder_v1.ps1
```

## Full Build

Full build requires explicit acknowledgement:

```powershell
$env:ORDERBOOK_81_FULL_ABSORPTION_BUILD='YES'; .\run_orderbook_um_81_full_absorption_dataset_builder_v1.ps1
```

Lean full build requires both lean mode and full build acknowledgement:

```powershell
$env:ORDERBOOK_81_FULL_ABSORPTION_LEAN_MODE='YES'; $env:ORDERBOOK_81_FULL_ABSORPTION_BUILD='YES'; .\run_orderbook_um_81_full_absorption_dataset_builder_v1.ps1
```

The full build streams one symbol-day pair at a time. It reads ZIP members directly and does not extract raw CSV files into the repo. Completed partition files are skipped when the parquet file and sidecar metadata verify.

## Partition Layout

Partitions are stored under:

```text
<output_root>\partitions\symbol=<SYMBOL>\year_month=<YYYY-MM>\<SYMBOL>-<YYYY-MM-DD>-absorption.parquet
```

Lean partitions are stored under:

```text
<output_root>\lean_partitions\symbol=<SYMBOL>\year_month=<YYYY-MM>\<SYMBOL>-<YYYY-MM-DD>-absorption-lean.parquet
```

Each parquet partition has a sidecar JSON file with row count, schema hash, checksum, duplicate count, and absorption category counts.

## Feature Families

The dataset derives research-only liquidity and flow proxy fields:

- timestamp, symbol, file date, year month
- bookDepth bid and ask depth by percentage bucket where the sign of `percentage` identifies side
- bookDepth bid and ask notional by percentage bucket
- depth imbalance proxy
- spread, mid, and microprice proxy columns, left null when not inferable from the percentage-depth schema
- aggressive buy and sell quantity/notional from aggTrades using `is_buyer_maker`
- trade count, total quantity, total notional
- buy/sell flow imbalance
- rolling flow pressure
- rolling depth imbalance
- flow-depth divergence proxy
- absorption category:
  - `BUY_PRESSURE_ABSORBED`
  - `SELL_PRESSURE_ABSORBED`
  - `FLOW_AND_DEPTH_ALIGNED_UP`
  - `FLOW_AND_DEPTH_ALIGNED_DOWN`
  - `MIXED_OR_NOISY`
  - `INSUFFICIENT_DATA`

The category is a descriptive research bucket, not a trading label.

## Validation

Run:

```powershell
.\run_orderbook_um_81_full_absorption_dataset_validator_v1.ps1
```

The validator checks output-root safety, partition presence, schema consistency, duplicate symbol/timestamp rows, nonzero row counts, category counts, and the absence of prohibited trading/private-endpoint behavior.
