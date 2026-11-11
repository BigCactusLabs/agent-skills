---
name: working-with-excel-workbooks
description: Read, create, edit, recalculate, repair, and verify Excel files (.xlsx/.xlsm/.xlsb/.xls), with guidance on tool selection, template fidelity, formula caches, and large pandas/Polars pipelines. Use connected Excel session tools for explicitly live workbook tasks.
---

# Working with Excel Workbooks

A successful `save()` does not prove that formulas, objects or business logic survived. Choose tools by the job and required fidelity. Honor the user's tool and active session; a file task does not authorize cloud upload or export of a live workbook.

## Choose the backend

| Job | Default | Limit |
| --- | --- | --- |
| Read values | Polars calamine/fastexcel or pandas `read_excel(engine="calamine")` | Stored values, not recalculation or document preservation |
| Compute | Polars or established pandas code | Use Parquet/Arrow between steps |
| Create `.xlsx` | XlsxWriter or Polars `write_excel` | Cannot edit templates or calculate formulas |
| Read formulas / edit supported OOXML structures | openpyxl, `data_only=False` | Unsupported objects and cached results can be lost |
| Preserve rich workbooks | Excel through xlwings or session tools | Local xlwings needs installed Excel on Windows/macOS |
| Edit or calculate headlessly | Validated LibreOffice/UNO or a suitable commercial engine | Test the actual workbook; no universal fidelity guarantee |

Reader support does not imply writer support. Preserve the required format; renaming an extension is not conversion.

For current results, cache-only updates, external refresh, Microsoft 365 or formula evaluators, read [calculation.md](references/calculation.md). Use [research-2026-09.md](references/research-2026-09.md) only for dated versions, sources, experimental tools and known failures.

## Edit and verify

1. **Inspect a copy** unless an in-place edit is requested. Inventory sheets/hidden state, names, merges, tables, formulas, validation, conditional formatting, charts, links, protection and VBA. Check for Power Query/Data Model, slicers, pivot caches, embedded objects and signatures. OOXML ZIP parts/relationships can reveal features a reader ignores.
2. **Define the patch:** target ranges, intended values/formulas, allowed structural changes and business invariants. Preserve unrelated content. Row/column insertion or deletion needs an audit of dependent formulas, names, tables, charts and validations.
3. **Use supported edits.** Ordinary charts/tables/formulas do not prohibit openpyxl; required unsupported objects prohibit an unvalidated round-trip. Use Excel, a demonstrated compatible backend, or report the limit. pandas append/overlay is also a document rewrite. Reuse template styles; file-writing formula APIs require English function names and commas. Check modern/dynamic-array serialization in the target Excel version.
4. **Recalculate if results matter.** openpyxl and XlsxWriter do not calculate. Recalculate-on-open flags are not current results, and calculation is not external-data refresh. Follow the calculation reference; disclose unavailable verification.
5. **Reopen the saved output.** Check values and formula text at their coordinates, not just formula counts. Compare required structure and objects; for rich files, inspect meaningful package-part/relationship differences. Check caches against expected results and reconcile relevant totals, balances, keys, dates and row counts. Render/open critical sheets when layout matters; autofit is approximate.

For openpyxl edits:

- Keep `data_only=False`; saving a `data_only=True` load loses formulas. Use a separate load to read caches. Even a formula-preserving save can clear caches.
- Use `keep_vba=True` for `.xlsm` and retain the extension; this does not guarantee controls or signatures survive. Use `rich_text=True` and preserve external links when required.

Read-only extraction needs the correct sheet/table, headers, types and cache-freshness assessment, not a save/recalculation cycle.

## Read and transform

- Pin pandas `engine=`; check installed/stable behavior rather than treating development-doc changes as shipped.
- Calamine is a full-read default. For a few rows from a huge file, consider lazy openpyxl reads. Polars `read_excel` is eager; `.lazy()` afterward does not stream ingestion.
- Bound sheets/columns. Use `schema_overrides` or `infer_schema_length` for Polars typing; sheets needing different options require separate calls. Preserve identifiers/leading zeros and distinguish stored text from number display formats.
- Set handling for blanks, literal `NA`, null/NaN, errors and date systems. For pandas-to-Polars migration, remove index assumptions, prefer expressions to row loops, and sort where output order matters.

## Write new reports

- Keep literal text literal: XlsxWriter `write_string()` or `strings_to_formulas=False`; write intended formulas explicitly. Preserve text identifiers.
- `constant_memory=True` requires sequential **row-major** writes; flushed rows cannot be patched. Tables are unavailable and merges are limited. Do not blindly enable it for dataframe exports: Polars `write_excel` produces tables. Choose normal mode or a compatible row-streaming design without silently dropping requested features.
- `in_memory=True` overrides constant-memory mode. Budget temporary disk and RAM.
- XlsxWriter caches formula results as zero unless supplied. Supply only known results or recalculate before delivering current values.

## Repair and report

Preserve original and broken files. Use the repair log, last writer and a minimal reproducer to locate damage; switch backend if unsupported round-tripping caused it. Windows Excel's `Workbooks.Open(..., CorruptLoad=xlRepairFile)` or `xlExtractData` can recover a copy, but extraction may discard features. Verify recovered data/objects and open in Excel before calling it repaired.

Report output path, backend/version, changed ranges, calculation/refresh status, checks/results and unresolved fidelity limits. Use [TESTS.md](TESTS.md) for skill-maintenance scenarios.
