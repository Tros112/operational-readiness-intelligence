# Data directories

The clean reference remains in `raw/clean/`: six CSVs and `generation_manifest.json`. Day 3 adds a separately damaged `raw/dirty/` copy plus `defect_manifest.json`, and explicit validation bundles. All operational inputs, defects, and findings are synthetic.

- `raw/`: keep clean reference CSVs separate from the intentionally dirty input set.
- `processed/validation_clean/`: passed clean report, six accepted CSVs, and empty rejection/issue CSVs.
- `processed/readiness.sqlite3`: Day 4 persistent six-table snapshot, loaded only from a verified passed bundle.
- `processed/load_report.json`: counts, hashes, integrity/FK results, and logical snapshot digest; separate second/dirty audit files support the assistant's verification.
- `processed/dashboard/`: Day 5 SQL-generated `unit_summary.csv` (6 rows), `qualification_detail.csv` (48), and `expiration_detail.csv` (193). Grains/date/classification and exact fields are in `docs/export_dictionary.md`.
- `processed/dashboard/export_manifest.json`: passed/exports_ready gate, source/database reconciliation, CSV/SQL hashes, row counts, and grains. A failed rerun invalidates this gate; old CSVs alone must not drive a refresh.
- `rejected/day03_dirty/`: failed report, rejected raw rows/reasons, issue rows, and six diagnostic accepted CSVs. The entire dirty batch is blocked; these accepted subsets must not be loaded or reported as trusted readiness inputs.
- `rejected/day05_export_attempt/`: separate blocked dirty-export demonstration, no dashboard CSVs; preserves the clean export's successful manifest.

Generate/rebuild with `python src/generate_data.py` from the project root. Run `python src/inject_defects.py` to create the separate dirty demonstration. `python src/validate_data.py` validates clean input by default; use `--input-dir data/raw/dirty --output-dir data/rejected/day03_dirty` for the intentional failure. After clean validation, `python src/load_data.py` creates/replaces the persistent snapshot atomically. Source/accepted hashes and values must still match. Repeating a successful load retains the same logical contents; a blocked or failed load preserves good contents.

`python src/export_metrics.py` reads and verifies that saved database in one transaction without changing it; two successful runs produce identical CSVs. An existing working Day 4 folder needs only this export, not regeneration/reload. Follow `docs/day05_windows_handoff.md`. Generated data/audits/database remain local and ignored by Git. Never silently fill a critical identifier, date, or outcome. Current staffing/qualification/expiration exports are implemented; process and projected no-renewal metrics remain later milestones.
