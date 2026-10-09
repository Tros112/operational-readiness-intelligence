# Day 5 verification

Implemented October 9, 2026, Phase 1, at the user's request, ahead of the scheduled October 11 milestone. The metric date remains **2026-10-07**. Day 5 Linux implementation and its completion check pass; Windows reproduction and the user's SQL explanation remain pending. All operational results below are **simulated**; readiness is a fictional proxy, not an official Navy rule.

## Concrete output and checks

`src/export_metrics.py` executes `sql/unit_summary.sql`, `sql/qualification_detail.sql`, and `sql/expiration_detail.sql`. The existing six-table database is opened read-only. One read transaction holds the same snapshot while all records are compared with the passed validation bundle and all three queries are executed. Source/export hashes, eligibility, unique output grains, and cross-query sums are checked before CSV replacement.

| Local generated output | Grain | Rows |
| --- | --- | ---: |
| `data/processed/dashboard/unit_summary.csv` | Unit / analysis date | 6 |
| `data/processed/dashboard/qualification_detail.csv` | Unit / qualification / analysis date | 48 |
| `data/processed/dashboard/expiration_detail.csv` | Currently valid person / qualification / analysis date | 193 |

Every row has `data_classification = synthetic_only` and the fixed analysis date. All 48 requirements survive the joins. The clean reference has no zero-holder pair; the memory-only zero-holder fixture separately proves that those rows survive and show their full gap. This distinction prevents claiming a nonexistent pattern was observed in the generated reference.

**Tests:** Python 3.12.14 / SQLite 3.53.1 on Linux: **42 tests, OK, exit 0**, 10.731 seconds. Ten Day 5 tests cover independent Python calculations for every SQL metric against the source CSVs, duplicate-certificate counting, zero-holder requirements, unavailable inventory, validity and inclusive horizon boundaries, undefined denominators, repeat exports, blocked input, database mismatch/missing files, protected outputs, and an interrupted CSV replacement. Existing 32 generation/validation/load checks still pass. Details: `tests/test_export_metrics.py`; machine evidence: `docs/analytics_check.json`.

Two successful live exports return exit 0 and identical hashes for all three CSVs. The saved Day 4 database's physical SHA-256 remains `16d3119d57fd7ba6195fa372b9f970819a6397010162cab11119c2ce7014fe46`; all six clean CSVs and their generator manifest retain the Day 4 hashes. No live regeneration or reload was needed. The logical snapshot remains `fc5ee84198bee07dcc0e90bcf4fcf1f242fd640eb08116ff3bdc6f55b8bf8a66`. Physical database hashes are local preservation evidence, not a required Windows/Linux byte match.

The live dirty-bundle attempt uses a separate output directory: `data/rejected/day05_export_attempt/`. It returns **blocked / exit 1 / exports_ready false**, creates no CSVs, and leaves the database unchanged. Tests also prove that a failed rerun invalidates a previous passed export manifest while retaining old CSVs. Missing databases return exit 2 without creating a database.

## Simulated calculations reconciled

Global staffing is **254 / 250 = 101.6%**; summed unit staffing gaps are **10**, entirely in Unit C. Global qualification coverage is **88 / 95 = 92.63%**, with **7 missing holder slots across 7 requirement pairs**. These are separate measures; the qualification denominator counts slots, not unique personnel or simultaneous assignment capacity.

Unit C is the hand check: **40 / 50 = 80% staffing**, gap **10**. Its Q01–Q08 available valid holder counts are **5, 4, 7, 4, 3, 1, 4, 3**, against two required per pair. Capping each pair gives **15 / 16 = 93.75%** qualification coverage. Q06 has one holder and a gap of one. It is unmet, so it is not marked fragile under the contract. `docs/sql_walkthrough.md` traces the calculation.

Unit B/Q03 has one valid available holder for one required: fragile and single-holder dependency are both 1. Unit D/Q04 currently has six available holders for two required and is not fragile. Those six certificates expire after **7, 10, 14, 20, 25, and 30 days**; the November 6 endpoint is included. Unit D has **11** certificates in the total 30-day inventory; the six planted Q04 certificates are only part of that total. No projected no-renewal gap was implemented today.

The currently valid inventory has **193 certificates held by 145 distinct people**, including **21 certificates held by unavailable people**. Current available-holder coverage excludes those 21 certificates; expiration inventory includes them.

| Cumulative window from October 7 | Expiring certificates | Distinct affected people |
| --- | ---: | ---: |
| 30 days, through November 6 | 45 | 41 |
| 60 days, through December 6 | 68 | 62 |
| 90 days, through January 5, 2027 | 98 | 84 |

The windows overlap. Do not add them. Distinct affected people must be recomputed when filtering qualifications; adding qualification-level people counts can count a person more than once.

## Remaining evidence and limits

Windows Day 4 checks and report availability were already confirmed; do not repeat setup or create a daily project folder. Day 5 Windows export/test results and independent explanation of the joins are still pending. Follow `docs/day05_windows_handoff.md` using the existing `.venv` and project root. No additional dependency is needed.

CSV replacement is not a multi-file filesystem transaction. Only refresh/report from a manifest with `status = passed`, `exports_ready = true`, the expected date, and matching CSV hashes. A failed or interrupted run must be repaired and successfully rerun before refresh. A Power BI refresh guard remains part of its later build, not a feature claimed here.

No actual Windows environment or PBIX was operated by the assistant. Power BI/SQL reconciliation, the executive-page build, process metrics, and the no-renewal scenario remain later milestones. No release gate, employer feedback, professional implementation experience, or predictive validity is inferred. Delivery is code/tests/text only; local datasets, databases, images, `.venv`, and Power BI binaries are excluded.

**Next exact action:** update the same Windows checkout, run the exporter twice, confirm the manifest/counts/repeat and database preservation, run the 42-test suite, then explain why requirements use a LEFT JOIN and why certificate joins must not multiply staffing. Stop at that Day 5 check; Day 6 requires the next instruction.
