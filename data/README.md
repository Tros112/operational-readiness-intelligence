# Data directories

The clean reference remains in `raw/clean/`: six CSVs and `generation_manifest.json`. Day 3 adds a separately damaged `raw/dirty/` copy plus `defect_manifest.json`, and explicit validation bundles. All operational inputs, defects, and findings are synthetic.

- `raw/`: keep clean reference CSVs separate from the intentionally dirty input set.
- `processed/validation_clean/`: passed clean report, six accepted CSVs, and empty rejection/issue CSVs. Database/marts remain pending.
- `rejected/day03_dirty/`: failed report, rejected raw rows/reasons, issue rows, and six diagnostic accepted CSVs. The entire dirty batch is blocked; these accepted subsets must not be loaded or reported as trusted readiness inputs.

Generate/rebuild with `python src/generate_data.py` from the project root. Run `python src/inject_defects.py` to create the separate dirty demonstration. `python src/validate_data.py` validates clean input by default; use `--input-dir data/raw/dirty --output-dir data/rejected/day03_dirty` for the intentional failure. See `docs/validation_rules.md` and `docs/day03_windows_handoff.md`. Never silently fill a critical identifier, date, or outcome. No persistent database or analytical exports exist yet.
