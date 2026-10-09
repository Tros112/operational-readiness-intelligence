# Explain validation in your own words

Day 3. Everything here is simulated. Review this beside `src/validate_data.py`, `src/inject_defects.py`, and the actual validation reports. Generated explanations are not evidence of independent ownership.

## What the code does

1. `read_sources()` reads the six exact schemas as strings. It preserves blank cells and IDs, counts logical CSV records, records input hashes, and marks unreadable or malformed files as errors. It does not infer a missing input count as zero.
2. `check_local_fields()` checks required values, flags/counts, real calendar dates, date ordering, and case outcome state. A syntactically valid expired certificate passes: validation asks whether the record is usable, while SQL later asks whether it is eligible at D.
3. `validate_records()` groups declared keys and rejects every collision. It checks foreign keys in parent-before-child order using only accepted parents, then checks the full unit/qualification requirement grid. It never chooses a duplicate version or fills a missing requirement.
4. `validate_directory()` counts each rejected record once even if it has several issues. It sets `load_allowed` to false if any record, batch, or file failed.
5. `write_result()` exports accepted records and quarantined raw cells/reasons, records output hashes, and finalizes the report after exports succeed. The CLI first invalidates any previous success report, including before reading configuration.
6. `build_dirty()` makes sixteen documented edits to a separate clean-data copy. It records exact targets and expected codes without putting a timestamp into the manifest. The validator runs independently afterward; matching the manifest proves the intended failures were found.

## Three important distinctions

**Rows versus issues:** one person with an invalid availability flag and a broken unit reference has two issues but is one rejected person. That person's certificate is a second rejected record when its parent is unusable. Counts reconcile by records, not by error-message count.

**Duplicate counting versus conflict resolution:** `COUNT(DISTINCT person_id)` can prevent duplicate rows from inflating a count. It cannot decide which conflicting unit, availability, or certificate date is correct. Rejecting both versions and blocking the batch makes that uncertainty visible.

**Diagnostic acceptance versus release approval:** the dirty run has 1,210 individually accepted rows, but `load_allowed` is false. Dropping bad requirement rows could shrink the denominator and make coverage look better. The missing-pair check and batch gate prevent using that incomplete subset as trusted readiness evidence.

## Walk through the arithmetic

Clean sources have 1,227 rows. Two duplicate appends raise dirty input to 1,229. The sixteen edits affect eighteen rejected records because each of the two duplicate groups rejects two versions. One dependent certificate also fails, giving nineteen rejected records. **1,229 = 1,210 + 19**.

Do not recalculate the simulated staffing findings from this damaged subset. The original clean snapshot still has 254 available / 250 required and Unit C's local gap of 10; those source bytes were preserved.

## Ownership checks

Explain without reading the answers:

- Why reject both rows with the same person/qualification key rather than keep the first?
- Why can the dirty run reconcile perfectly while loading remains blocked?
- Why does an expired certificate pass validation, but February 30 fails?
- Why must an open case's correction outcome remain blank rather than become zero?

These explanations remain pending. The earlier aggregate-versus-local staffing explanation is already confirmed. No professional deployment, production pipeline, or predictive-validity claim follows from these tests.
