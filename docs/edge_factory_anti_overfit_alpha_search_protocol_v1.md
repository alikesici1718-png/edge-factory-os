# Anti-overfit alpha search protocol v1

This protocol searches fixed, capacity-aware absorption candidates against verified Binance UM bookDepth and aggTrades data only.

Default execution is smoke-only. Full search requires:

```powershell
$env:EDGE_FACTORY_RUN_ANTI_OVERFIT_ALPHA_SEARCH="YES"; powershell -NoProfile -ExecutionPolicy Bypass -File .\run_edge_factory_anti_overfit_alpha_search_protocol_v1.ps1
```

## Fixed Inputs

- bookDepth root: `C:\edge_factory_external_data\binance_um_81_full_bookdepth_raw`
- aggTrades root: `C:\edge_factory_external_data\binance_um_81_full_matching_aggtrades_raw`
- coverage: 2023-01-01 through 2026-06-15
- universe: 81 symbols
- baseline comparison: `SELL_PRESSURE_ABSORBED@300s`, cooldown 600s, full-history break-even 3.724399 bps, capacity-limited

## Frozen Grid

- categories: `BUY_PRESSURE_ABSORBED`, `SELL_PRESSURE_ABSORBED`, `FLOW_AND_DEPTH_ALIGNED_UP`, `FLOW_AND_DEPTH_ALIGNED_DOWN`
- horizons: 30s, 60s, 120s, 300s, 600s
- cooldowns: 300s, 600s, 900s, 1200s
- delays: 0s, 1s, 3s, 5s, 10s
- costs bps: 0, 1, 2, 3, 5, 7.5, 10
- capacity subsets: all, exclude THIN, HIGH only, HIGH+MEDIUM, top 10/20/40 by discovery notional, min around-event notional 5k/10k/25k/50k/100k

Grid count: 960 base candidates and 33,600 fixed execution-stress cells.

## Walk-forward

Each fold uses discovery 180d, validation 90d, test 90d, step 90d. Discovery ranks the frozen grid. At most 20 candidates promote to validation and at most 5 promote to test. Direction is inferred only in discovery, then locked. Test windows are evaluated only after validation promotion.

## Hard Pass Gates

- kept events >= 5000 per fold
- same locked sign in discovery, validation, and test
- break-even >= 3 bps
- survives 3 bps cost at 3s delay
- survives 2 bps cost at 5s delay
- symbol stability >= 0.65
- month stability >= 0.70
- week stability >= 0.65
- single symbol <= 25% kept events
- single week <= 15% kept events
- not THIN-only unless small-cap-only
- null comparison same sign and nonzero

## Outputs

All outputs use the prefix `outputs/edge_factory_anti_overfit_alpha_search_*`:

- summary json/md
- fixed_grid json
- fold_plan csv
- trial_log csv
- ranked_candidates csv
- rejected_candidates csv
- promoted_candidates csv
- walk_forward_results csv
- multiple_testing_report json
- validator json/md

This is research diagnostics only. It performs no downloads, creates no row-level dataset, uses no private endpoints, creates no orders, and emits no trading recommendations.
