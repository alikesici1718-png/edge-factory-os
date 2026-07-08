# Safe Disk Cleanup Notes V1

This module audits `C:\Users\alike\OneDrive\Desktop\edge_lab_new` and separates strict safe-delete candidates from report-only disk consumers.

## Scope

- Default mode is dry-run.
- Actual deletion is allowed only when `EDGE_FACTORY_CLEANUP_DELETE_SAFE=YES`.
- Deletion is restricted to strict whitelist junk/cache/temp candidates.
- Source code, `.git`, docs, configs, reports, raw market data, and verified market data are protected.
- `C:\edge_factory_external_data` and `C:\edge_factory_external_data\binance_um_81_full_bookdepth_raw` are protected.

## Strict Delete Whitelist

Folders:

- `__pycache__`
- `.pytest_cache`
- `.mypy_cache`
- `.ruff_cache`
- `.ipynb_checkpoints`
- project-context `.cache`
- `htmlcov`
- empty directories outside git worktrees

Files:

- `*.pyc`
- `*.pyo`
- `*.tmp`
- `*.temp`
- `*.part`
- `.DS_Store`
- `Thumbs.db`
- `.coverage`

Anything outside this whitelist is not deleted by the delete module.

## Report-Only Items

The audit reports these for manual review only:

- `node_modules`
- `.next`
- `dist`
- `build`
- large ZIP, CSV, parquet, JSON, and JSONL outputs
- old external data folders under OneDrive
- duplicate-looking data folders
- pilot data folders
- logs larger than 100 MB
- recent ambiguous files or folders

Large report-only items require separate manual approval before deletion.

## Run Audit

```powershell
.\run_safe_disk_cleanup_audit_v1.ps1
```

Review:

- `outputs\safe_disk_cleanup_audit_summary.md`
- `outputs\safe_disk_cleanup_delete_whitelist_candidates.csv`
- `outputs\safe_disk_cleanup_report_only_large_items.csv`
- `outputs\safe_disk_cleanup_protected_items.md`

## Dry-Run Delete

```powershell
.\run_safe_disk_cleanup_delete_v1.ps1
```

This reads the whitelist candidates and writes skipped dry-run rows without deleting anything.

## Actual Strict Whitelist Deletion

After reviewing the audit outputs:

```powershell
$env:EDGE_FACTORY_CLEANUP_DELETE_SAFE="YES"
.\run_safe_disk_cleanup_delete_v1.ps1
```

The delete module rechecks each path before deletion:

- under `C:\Users\alike\OneDrive\Desktop\edge_lab_new`
- not inside `.git`
- not raw or external market data
- still matching the strict whitelist
- directories are cache folders or empty directories only

Report-only large items are never deleted by this module.
