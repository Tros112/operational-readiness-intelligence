# Explain the Day 4 loader

All examples are synthetic. Review this beside `src/load_data.py`, `sql/schema.sql`, and `docs/verification_day04.md`. Ownership is confirmed only when you explain the choices independently.

## Before SQLite is opened

`prepare_bundle()` requires a completed, passed Day 3 report with load_allowed true, no rejected records or errors, and the same configured analysis date. It hashes the original and accepted CSVs, checks their declared row counts, and reruns the existing validation rules on the records read into memory. The accepted values must match the passed source. Stale source bytes, changed exports, malformed metadata, or a dirty diagnostic bundle block the load.

The configured snapshot must still contain six units, 300 people, eight qualification types, 600 cases, and the configured parent IDs. Certificate count comes from the passed accepted file rather than an invented fixed target. The validator already requires the full unit/qualification requirement grid.

Hashes detect changes since validation; they are not a signature or proof of real-world source truth. This is a fictional local pipeline. The independent checks and source/export equality prevent treating an edited export hash alone as authorization.

The records used for insertion are the same in-memory records that passed these checks. The loader does not reread an export after hashing it. Protected paths prevent database/audit outputs inside `.git`, `.venv`, raw inputs, or the validation bundle. Database outputs require a database extension, so a PBIX path cannot be a loader target.

## One transaction for one snapshot

The loader enables SQLite foreign keys **on its connection before BEGIN**, then starts `BEGIN IMMEDIATE`. An existing database must have the compatible six-table schema; an unrelated database is refused. Schema statements execute individually inside the transaction. Python's `executescript()` can commit a pending transaction, so it is deliberately not used for the persistent load.

Deletes run child-first to satisfy foreign keys; inserts run parent-first. Every value uses an SQL placeholder. Known numeric fields become integers. Only optional blank case completion/outcome fields become SQL NULL. Unknown correction outcomes remain unknown; a known zero stays zero. Expired and future-start certificates remain stored records, with metric eligibility left to Day 5 SQL.

Before commit, the loader compares every stored row with its verified input, checks all six counts, runs foreign_key_check and integrity_check, and counts open cases retaining NULL outcomes. Any failure rolls back the transaction. A test causes a real duplicate-key violation after deletes and partial inserts and proves the previous complete snapshot survives.

This is a **full snapshot replacement**, not an append or historical change log. Repeating the load produces the same final records without duplicates. `logical_data_sha256` hashes ordered table contents; it can stay the same even if SQLite's physical file bytes change during a successful reload. The dirty preflight check is stronger in another respect: it never opens the database, so those database bytes remain unchanged.

## Audit and failure behavior

Exit 0 means loaded/verified. Exit 1 means blocked preflight. Exit 2 means configuration, I/O, SQLite, or audit error. The CLI invalidates an earlier success audit before processing, so a failed rerun cannot retain stale loaded status. The load audit is not a dashboard-input approval mechanism.

The database transaction and final JSON write are separate filesystem operations. If the database commits but the final audit write fails, the console preserves database_updated true and reports audit_report_error/exit 2. Do not describe that situation as a database rollback.

## Ownership check

The transaction explanation was independently supplied October 9 at 04:38 PDT. The user identified the risk of mixing old/new data after an error and described how an incomplete personnel transfer could distort staffing coverage, gaps, or accounted personnel. This is a hypothetical illustration, not an implemented transfer history or observed project finding. The Day 3 duplicate-authority explanation is also confirmed; other future SQL/metric explanations remain separate ownership checks.

Clarification supplied as guidance: child-first deletion and parent-first insertion satisfy foreign-key order. The single transaction makes the six-table replacement complete together or roll back together. Foreign keys can pass while tables still describe different snapshots; valid relationships alone do not establish snapshot consistency. This clarification is assistant guidance, not an additional independently demonstrated user explanation.

Primary technical references: [Python 3.11 sqlite3](https://docs.python.org/3.11/library/sqlite3.html) and [SQLite transactions](https://www.sqlite.org/lang_transaction.html). The implementation checks are described in `docs/verification_day04.md`; they do not establish professional deployment experience.
