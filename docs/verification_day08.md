# Day 8 qualification/expiration preparation

Started **October 13, 2026**, under the user's explicit instruction, early relative to October 14. The October 7 synthetic snapshot, fictional readiness proxies, six operational sources, SQLite/CSV strategy, audience, and release dates are unchanged. The Day 7 prototype gate remains passed; MVP/polish remain open.

**Status: prepared and statically reviewed; Windows/Desktop runtime pending.** The local execution environment is unavailable. No native command/file-system execution, current local dataset/hash check, Python/SQL/PowerShell run, M/DAX compilation, or actual PBIX operation is claimed. Read the immutable public baseline **9fdd5a39c7f4065c446303f20e5e1da74b37572f** through the connected GitHub interface. Root AGENTS is the only instruction file in that tree.

## Prepared files and model

| Asset | Purpose | Runtime boundary |
| --- | --- | --- |
| powerbi/qualification_detail.pq | Approved 48-row/13-column pair import; counts/capping/gaps/ratio/fragility, date and unique grain gates | Not executed in M |
| powerbi/qualification_filter.pq | Eight unique qualification ID/name rows derived from approved pairs | Not loaded or linked in Desktop |
| powerbi/expiration_detail.pq | Approved 193-row/14-column current inventory; validity/days/inclusive flags, grain and identity checks | Not executed in M |
| powerbi/qualification_measures.dax | Sixteen scoped ORI Q measures, including distinct people per window and blank undefined values | Not executed in DAX |
| docs/day08_windows_handoff.md | Existing-folder import, four-relationship model, page, checks, and truthful project résumé wording | User build/evidence pending |
| docs/day08_reconciliation.md | Prior known references and a read-only selected-CSV PowerShell reference | PowerShell not executed |
| docs/qualification_check.json | Machine-readable static results, previous evidence, and pending runtime state | Preparation status, not page acceptance |

Reuse six-row unit_summary as the one-side unit lookup. The eight-row qualification_filter is another one side. Both filter qualification_detail and expiration_detail through four active 1:* Single relationships; no fact-to-fact link/merge or connection to the older learning tables is added. Source rows retain their grains. Original executive/learning measures stay intact; new qualification-specific formulas use pair detail, while inventory formulas use certificate detail.

The M gates validate integers before Int64 conversion, keep all 48 demands, check capped counts/gap/ratio/fragility, retain both inventory availability states, and verify exclusive current validity with inclusive cumulative flags. A distinct projection builds lookup rows; it does not silently deduplicate fact data. Python preflight still supplies SHA-256 immediately before import/refresh, with stable files between steps. M does not hash, and the filesystem procedure is not atomic.

## Static/reference verification performed

- Read governing files, source milestone, metric/export dictionaries, SQL, existing checker/import source, prior analytical audits/tests, and current report status at the pinned baseline.
- Confirmed exact 13/14-column schemas and grains, sixteen unique measure names, and valid DAX source-column references. Coverage divides summed capped slots by summed demand; window people use DISTINCTCOUNT with KEEPFILTERS, not summed category people totals.
- JSON parsing, whitespace, and relative file links pass. Git blob hashes for eighteen read source files match the pinned tree; prepared UTF-8 contents are hashed for publication checks. These checks use the orchestration JavaScript environment, not a native filesystem or M/DAX engine.
- Seven **JavaScript teaching-reference cases** pass: capped weighted coverage, unmet-versus-fragile, surplus, undefined demand, inclusive 30/60/90 boundaries, unavailable inventory, and distinct/empty selections. These are mathematical reference checks, not M/DAX/PowerShell tests, and are not findings in the live reference.
- Prior SQL evidence supplies global 88/95 = 92.63%, seven missing slots/seven gap pairs, inventory 193 certificates/145 people, and cumulative certificate/people values 45/41, 68/62, 98/84. B/Q03 and C/Q06 distinguish met fragility from an existing gap. Existing test code and its recorded prior passes establish exactly six D/Q04 inventory rows at days 7/10/14/20/25/30; each window includes all six people.
- The prior audit does not report global fragile-pair totals. The prepared Windows CSV reference derives those and new multi-selection results rather than inventing values.
- Reviewed primary Microsoft relationship, distinct-count/filter, and M-type documentation. This establishes documented semantics, not execution in the user's report.

Existing **49 Python tests** previously passed on Linux and screenshot-verified Windows. Python/SQL/test definitions are unchanged; those tests do not compile the new M/DAX. No new runtime pass, live export reconciliation, or local hash-preservation claim is added for this unavailable session.

## Publication and remaining checks

Prepared code/text publication is within the user's standing scope. Build a normal commit from fresh public main and verify the parent, complete tree, changed path set, and blob contents through GitHub before reporting delivery. Preserve every other remote path and excluded image/generated/binary/private-history asset. No native fetch or branch alignment is possible/claimed here; existing native private archives are not accessed or pushed.

First user review: passed input checker, imported 48/13 and 193/14 facts plus 8/2 lookup, correct types/date/classification, and four active Single relationships. Then inspect page measures and shared slicer scopes against the read-only reference, selected B/C/D cases, multiple qualifications/units, boundary counts, clear/empty behavior, and report save/reopen including earlier pages. Exact Desktop definitions and actual PBIX internals remain uninspected until evidence establishes them.

Keep distinct-person/overlapping-window and unmet/fragile ownership explanations specific. Carried zero-holder join/person-certificate grain review is not marked mastered by generated code or reference checks. Workshop/event attendance, employer feedback, and actual hours remain unreported. Stop at Day 8 acceptance; process metrics/view are Day 9 and the no-renewal gap is Day 10.
