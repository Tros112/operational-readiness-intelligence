# Reproduce the fixed ORI prototype

Day 11 documentation, October 20, 2026. All operational data and requirements are synthetic. The reference is pinned to **October 7, 2026**, seed **20261007**, six units, 300 people, eight qualification types and 600 administrative cases. [Requirements](../requirements.txt), [configuration](../config/project.yml), [source dictionary](data_dictionary.md), [export dictionary](export_dictionary.md) and [limitations](limitations.md) define this release.

## Choose the task before running commands

| Task | Procedure |
| --- | --- |
| Continue the accepted Windows report | Keep the existing Day 3 checkout, .venv, data, database, PBIX and every accepted page. Day 11 requires no regeneration, reload, report refresh or repeated acceptance screenshots. |
| Check inputs immediately before an actual refresh | Run the three read-only preflights below. Keep the files stable until refresh finishes. |
| Reproduce from code and configuration | Use a **new checkout and environment**. The guarded Windows block below creates a sibling ORI-reproduction folder and refuses an existing destination. It writes generated outputs only in that new checkout. |
| Reproduce the complete Desktop presentation | The Python pipeline and the Power BI report are separate steps. Git contains M/DAX/build instructions, not a PBIX. Build from [the report index](../powerbi/build_instructions.md), or use a separate comparison copy of the user's accepted PBIX and point that copy at the new outputs. |

The full fresh-checkout execution and demo rehearsal belong to **Day 12** and have not been performed as Day 11 evidence. These instructions are source/argument checked; the Windows block has not been executed by the assistant. Keep the accepted checkout and report intact.

## Prerequisites and fixed configuration

- Git; Python **3.11+**; Python's SQLite engine **3.37+** for STRICT tables. A SQLite command-line program, PostgreSQL server and database driver are unnecessary for the recorded SQLite/CSV strategy.
- The Windows example uses the `py -3.11` launcher. If your installation differs, use its explicit Python 3.11+ executable for environment creation; subsequent commands use the new environment's interpreter directly.
- Install only the pinned [requirements](../requirements.txt): PyYAML 6.0.3, pandas 2.2.3 and NumPy 2.3.5. sqlite3 and unittest are standard-library modules. Use the project interpreter directly; activating a shell environment is optional.
- Clone/package installation needs network access. Generation, validation, SQL, CSV export and tests then run locally with the installed dependencies.
- Keep config/project.yml unchanged when reproducing this reference. The Power Query shape/date checks and published expected values are pinned to the same snapshot. Changing the configuration requires a separately reconciled snapshot, not an automatic date refresh.

From the project root, the environment check is `python src/check_environment.py`. It prints JSON, tests the schema in memory and returns 0 for passed. Its optional PostgreSQL inventory is informational for the SQLite strategy. It does not create the populated database. Do not redirect its output over the historical docs/environment_inventory.json merely to run it.

## Dependency order and expected gates

Paths below are relative to the new project root; invoke scripts with its own Python interpreter. Each ordinary step must exit 0. The deliberately dirty validation is the one expected exit 1.

| Order | Script / arguments | Expected result or output |
| --- | --- | --- |
| 1 | `src/check_environment.py` | status passed; Python/packages/configuration/schema usable |
| 2 | `src/generate_data.py` | data/raw/clean: six CSVs, generation_manifest.json; counts 6/300/8/265/48/600 |
| 3 | `src/inject_defects.py` | Separate data/raw/dirty and defect metadata; clean source preserved |
| 4 | `src/validate_data.py` | data/processed/validation_clean: passed, load_allowed true, 1,227 accepted / 0 rejected |
| 5 | `src/validate_data.py --input-dir data/raw/dirty --output-dir data/rejected/day03_dirty` | **Exit 1**, blocked, load_allowed false; 1,229 input = 1,210 accepted + 19 rejected. The accepted dirty subset is diagnostic, not authorized input. |
| 6 | `src/load_data.py` | Loads only the passed clean bundle into data/processed/readiness.sqlite3; six-table counts agree, FK/integrity checks pass; load_report.json |
| 7 | `src/export_metrics.py` | Original dashboard bundle: 6 unit, 48 qualification and 193 current-certificate rows; passed export_manifest.json |
| 8 | `src/export_process_metrics.py` | Separate process bundle: 600 case rows, six SQL unit-reference rows; passed process_export_manifest.json |
| 9 | `src/export_qualification_scenario.py` | Separate scenario bundle: 144 pair/horizon rows, 18 SQL unit/horizon-reference rows; passed scenario_export_manifest.json |
| 10 | `-m unittest discover -s tests -v` | **72 tests / OK**. Run after generation and all exports: several integration fixtures read the repository's reference files. |
| 11 | `src/check_powerbi_input.py` | Passed, three files checked, zero writes |
| 12 | `src/check_process_input.py` | Passed, two files checked, zero writes |
| 13 | `src/check_scenario_input.py` | Passed, two files checked, zero writes |

The loader verifies source/report/accepted values before a transactional load. Each exporter independently verifies the approved source against a read-only SQLite snapshot. A failed exporter disables its own successful manifest; leftover CSVs alone never authorize refresh. Resolve the reported cause before rerunning the affected step.

## Windows: guarded fresh-checkout run

Run this only when starting the fresh reproduction, from the **existing project root**. It creates a sibling folder named ORI-reproduction. If that path already exists, choose another unused destination deliberately; do not delete, reset or reuse the accepted checkout to get past the guard. The final location returns to the accepted root.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $oriAcceptedRoot = (Get-Location).Path
    if (-not (Test-Path '.\config\project.yml' -PathType Leaf)) {
        throw 'Start in the existing ORI project root.'
    }
    $oriReproRoot = Join-Path (Split-Path $oriAcceptedRoot -Parent) 'ORI-reproduction'
    if (Test-Path $oriReproRoot) {
        throw "Destination already exists: $oriReproRoot. Select a new unused destination."
    }
    git clone https://github.com/Tros112/operational-readiness-intelligence.git $oriReproRoot
    if ($LASTEXITCODE -ne 0) { throw 'Clone failed.' }
    try {
        Set-Location $oriReproRoot
        $oriSourceCommit = git rev-parse HEAD
        if ($LASTEXITCODE -ne 0) { throw 'Cannot record source commit.' }
        py -3.11 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed.' }
        $oriPython = Join-Path $oriReproRoot '.venv\Scripts\python.exe'
        function Invoke-OriPython {
            param([string[]]$OriArgv, [int]$OriExpectedExit = 0)
            & $oriPython @OriArgv
            $oriActualExit = $LASTEXITCODE
            if ($oriActualExit -ne $OriExpectedExit) {
                throw "Expected exit $OriExpectedExit, got ${oriActualExit}: $($OriArgv -join ' ')"
            }
        }
        Invoke-OriPython -OriArgv @('-m', 'pip', 'install', '-r', 'requirements.txt')
        Invoke-OriPython -OriArgv @('src/check_environment.py')
        Invoke-OriPython -OriArgv @('src/generate_data.py')
        Invoke-OriPython -OriArgv @('src/inject_defects.py')
        Invoke-OriPython -OriArgv @('src/validate_data.py')
        Invoke-OriPython -OriArgv @('src/validate_data.py', '--input-dir', 'data/raw/dirty', '--output-dir', 'data/rejected/day03_dirty') -OriExpectedExit 1
        Invoke-OriPython -OriArgv @('src/load_data.py')
        Invoke-OriPython -OriArgv @('src/export_metrics.py')
        Invoke-OriPython -OriArgv @('src/export_process_metrics.py')
        Invoke-OriPython -OriArgv @('src/export_qualification_scenario.py')
        Invoke-OriPython -OriArgv @('-m', 'unittest', 'discover', '-s', 'tests', '-v')
        Invoke-OriPython -OriArgv @('src/check_powerbi_input.py')
        Invoke-OriPython -OriArgv @('src/check_process_input.py')
        Invoke-OriPython -OriArgv @('src/check_scenario_input.py')
        "Fresh-checkout pipeline finished: $oriReproRoot"
        "Source commit: $oriSourceCommit"
        'Desktop reproduction and the demo rehearsal are separate checks.'
    }
    finally {
        Set-Location $oriAcceptedRoot
    }
}
```

The wrapper checks the exact expected native exit code; it does not suppress all validation errors. Dirty validation returning 2 or returning 0 unexpectedly stops the run. No dirty bundle is passed to the loader.

## Linux/macOS equivalent

From the existing project root, this subshell uses the same sibling isolation and run order. It requires python3 meeting the version/SQLite requirements. The accepted checkout remains the caller's current directory.

```bash
(
    set -eu
    test -f config/project.yml
    ori_repro_root="$(dirname "$PWD")/ORI-reproduction"
    if test -e "$ori_repro_root"; then
        printf '%s\n' 'Choose an unused reproduction destination.' >&2
        exit 1
    fi
    git clone https://github.com/Tros112/operational-readiness-intelligence.git "$ori_repro_root"
    cd "$ori_repro_root"
    ori_source_commit=$(git rev-parse HEAD)
    python3 -m venv .venv
    ori_python="$PWD/.venv/bin/python"
    "$ori_python" -m pip install -r requirements.txt
    "$ori_python" src/check_environment.py
    "$ori_python" src/generate_data.py
    "$ori_python" src/inject_defects.py
    "$ori_python" src/validate_data.py
    if "$ori_python" src/validate_data.py --input-dir data/raw/dirty --output-dir data/rejected/day03_dirty; then
        printf '%s\n' 'Dirty validation unexpectedly passed.' >&2
        exit 1
    else
        ori_dirty_exit=$?
        test "$ori_dirty_exit" -eq 1
    fi
    "$ori_python" src/load_data.py
    "$ori_python" src/export_metrics.py
    "$ori_python" src/export_process_metrics.py
    "$ori_python" src/export_qualification_scenario.py
    "$ori_python" -m unittest discover -s tests -v
    "$ori_python" src/check_powerbi_input.py
    "$ori_python" src/check_process_input.py
    "$ori_python" src/check_scenario_input.py
    printf 'Fresh-checkout pipeline finished: %s\nSource commit: %s\n' "$ori_repro_root" "$ori_source_commit"
)
```

The block is syntax checked on Linux; clone/install/full execution remains Day 12 evidence. It does not establish Power BI Desktop reproduction.

## Existing checkout: preflight before an actual refresh

```powershell
& {
    $ErrorActionPreference = 'Stop'
    foreach ($oriScript in @('src/check_powerbi_input.py', 'src/check_process_input.py', 'src/check_scenario_input.py')) {
        & .\.venv\Scripts\python.exe $oriScript
        if ($LASTEXITCODE -ne 0) { throw "Input gate blocked: $oriScript" }
    }
}
```

All three must report passed with 3/2/2 files and zero writes. Python supplies CSV SHA-256 checks; M does not hash. A failed Desktop refresh can leave cached visuals, so a visible old report is not proof of a successful refresh.

## Power BI and reproducibility evidence

Use the [build index](../powerbi/build_instructions.md) and accepted Day 6, 8, 9 and 10 handoffs. The operational report uses the original three exports, process_case_detail and qualification_scenario; process_unit_summary and scenario_unit_summary are SQL references only. Derived lookup queries add no operational source. Preserve the learning pages and the ten accepted active Single links. Scenario default is one 30-day horizon; numerical/date guards reject absent/multiple horizons.

A comparison PBIX must have its own saved path before any ProjectRoot changes. The five file-backed M queries are unit_summary, qualification_detail, expiration_detail, process_case_detail and qualification_scenario; lookup queries derive from them. Build/refresh/reopen and page checks require Windows/user evidence. Git alone does not supply the private PBIX, cached dataset or offline demo.

For Day 12, record the source commit, Python/SQLite/package versions, native exits, clean/dirty totals, six DB counts, seven export CSV row counts, three preflight summaries and the full 72-test result. Reconcile the report against [current references](day10_reconciliation.md) and [process references](day09_reconciliation.md), then record the actual two-minute/five-minute rehearsals and offline backup. Do not infer those results from this runbook.

Repeat exports should preserve CSV bytes for the unchanged verified snapshot. Compare actual files with their own passed manifests. Generator metadata records software versions; validation/load metadata can include absolute paths. A new checkout's audit files need not be byte-identical to another machine's files. Loader repeatability is exact logical records/counts; unchanged database bytes are separately expected for read-only exports/preflights, not promised for a reload. [Boundary checks](day11_boundary_checks.md) document the focused metric tests.
