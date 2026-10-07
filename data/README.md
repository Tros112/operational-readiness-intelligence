# Data directories

Day 2 clean reference exists in `raw/clean/`: six CSVs and `generation_manifest.json`. All operational inputs and findings are synthetic. No accepted/rejected pipeline output exists yet.

- `raw/`: keep clean reference CSVs separate from the intentionally dirty input set.
- `processed/`: accepted records, the SQLite database, SQL dashboard exports, and reconciliation evidence.
- `rejected/`: rejected input and validation reports with visible reasons/counts.

Generate/rebuild with `python src/generate_data.py` from the project root. Repeatability is verified for the same configuration, code, and pinned dependency versions. Do not overwrite the clean reference to inject defects: Day 3 creates `raw/dirty/` separately. Never silently replace a missing critical identifier or certificate date. Validation, loading, and dashboard export steps remain scheduled work.
