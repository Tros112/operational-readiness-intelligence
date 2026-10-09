# Data directories

The clean reference remains in `raw/clean/`: six CSVs and `generation_manifest.json`. Day 3 adds a separately damaged `raw/dirty/` copy plus `defect_manifest.json`, and explicit validation bundles. All operational inputs, defects, and findings are synthetic.

- `raw/`: keep clean reference CSVs separate from the intentionally dirty input set.
- `processed/validation_clean/`: passed clean report, six accepted CSVs, and empty rejection/issue CSVs.
- `processed/readiness.sqlite3`: Day 4 persistent six-table snapshot, loaded only from a verified passed bundle.
- `processed/load_report.json`: counts, hashes, integrity/FK results, and logical snapshot digest; separate second/dirty audit files support the assistant's verification.
- `rejected/day03_dirty/`: failed report, rejected raw rows/reasons, issue rows, and six diagnostic accepted CSVs. The entire dirty batch is blocked; these accepted subsets must not be loaded or reported as trusted readiness inputs.

Generate/rebuild with `python src/generate_data.py` from the project root. Run `python src/inject_defects.py` to create the separate dirty demonstration. `python src/validate_data.py` validates clean input by default; use `--input-dir data/raw/dirty --output-dir data/rejected/day03_dirty` for the intentional failure. After clean validation, `python src/load_data.py` creates/replaces the persistent snapshot atomically. Source/accepted hashes and values must still match. Repeating a successful load retains the same logical contents; a blocked or failed load preserves good contents. See `docs/day04_windows_handoff.md` for the existing Windows folder. Generated data/audits/database remain local and ignored by Git. Never silently fill a critical identifier, date, or outcome. Analytical exports remain pending.
