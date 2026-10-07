# Data directories

No operational dataset exists on Day 1. All later inputs and findings must be synthetic.

- `raw/`: keep clean reference CSVs separate from the intentionally dirty input set.
- `processed/`: accepted records, the SQLite database, SQL dashboard exports, and reconciliation evidence.
- `rejected/`: rejected input and validation reports with visible reasons/counts.

Do not overwrite the clean reference to inject defects. Never silently replace a missing critical identifier or certificate date. Generated outputs will be reproducible from the fixed seed/configuration; pipeline code and run order are pending the scheduled milestones.
