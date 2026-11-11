# Calculation, caches and external data

Use this reference when a task depends on formula results or choosing an execution engine. The dated evidence and limitations are in [research-2026-09.md](research-2026-09.md).

## Separate the capabilities

| Capability | What must be demonstrated |
| --- | --- |
| Formula text | The expression survives at the intended cell |
| Cached value | A previously saved result is present; this does not establish freshness |
| Calculation | The engine recomputes the formula with the intended inputs and semantics |
| Cache writeback | The saved output retains formulas and contains the new typed results |
| External-data refresh | Source queries/connections actually ran and supplied current data |
| Document preservation | Required workbook objects and relationships survive the chosen writer |

openpyxl and XlsxWriter do not calculate formulas. Value readers expose stored values, which may be absent or stale. A recalculate-on-open flag only requests future work from another application. Even unchanged formula text may lose its cached result during a save.

## Installed Excel

Local xlwings drives Excel on Windows/macOS. Excel performs calculation and saving, but platform-specific workbook features, add-ins and data connections must still be available. xlwings Server is a service model, not a Linux installation of Excel or an independent calculation engine.

Use a dedicated copy and an owned application instance for file automation. Do not close a user's existing session. On macOS, Excel does not safely arbitrate the same file across multiple instances, so use a unique copy and avoid concurrent writers. Opening a workbook must not silently enable macros or refresh external links beyond the requested scope.

For a trusted ordinary `.xlsx` file with no required refresh, the calculation step must be explicit:

```python
from pathlib import Path
from shutil import copy2
import xlwings as xw

source = Path("model.xlsx").resolve()
output = Path("model.updated.xlsx").resolve()
if output == source or output.exists():
    raise FileExistsError("Choose a new output path")
copy2(source, output)

with xw.App(visible=False, add_book=False) as app:
    wb = app.books.open(str(output), update_links=False)
    try:
        wb.sheets["Inputs"].range("B2").value = 1_250_000
        app.calculate()
        wb.save()
    finally:
        wb.close()
```

This is a mutation/calculation example, not a complete verification routine. Reopen the output and verify formulas, caches and business results. When a full dependency rebuild is needed, use the target platform's supported Excel API; `app.calculate()` is not a claim that every external connection refreshed. If refresh is part of the task, wait for its actual completion before calculating and saving.

## Microsoft 365: distinguish Graph from Office Scripts

- **Microsoft Graph workbook calculation:** the reviewed `workbookApplication: calculate` endpoint permits delegated work/school `Files.ReadWrite`. Personal accounts and application permissions are not supported. File access through another Graph API does not imply this endpoint supports app-only access. Verify workbook/storage support. When using a session for saved changes, set `persistChanges=true`; non-persistent sessions discard their changes. Calls without a session also persist changes, so omitting the session is not a read-only mode.
- **Office Scripts:** has its own platform and subscription rules. Personal/Family subscriptions have a documented preview; do not copy Graph's account restriction to this product. Power Automate integration requires a business Microsoft 365 license.
- **Size/runtime limits:** Office Scripts on Excel for the web limits requests/responses to 5 MB and a range to five million cells. Power Automate synchronous operations have a 120-second timeout. Batch bounded ranges and verify the current limits for the chosen surface.
- **Refresh limitation:** in Power Automate, Office Scripts cannot refresh most data. `refreshAllDataConnections()` only refreshes Power BI sources, and pivot refresh methods can return successfully without doing anything. Calculation therefore does not prove that Power Query or pivot inputs are current.

Use these routes when the workbook location, account and task support them. A local-file request alone does not authorize uploading it to Microsoft 365.

## Headless engines

**LibreOffice/UNO:** use an explicit hard recalculation (`calculateAll()` through UNO or the application's Recalculate Hard action), then save/export. Test on the actual workbook class, including formulas, dynamic arrays, charts, names, VBA expectations and links. New XLSX fixes are not a parity guarantee.

**Commercial engines:** Aspose.Cells and Spire.XLS are candidates when their supported features match the workbook. Check current licensing, evaluation restrictions, platform support and known issues before adoption. Do not infer complete feature preservation from a vendor's fidelity claim or its ability to calculate a formula.

**formualizer:** a Rust-backed engine with Python bindings, still classified Beta at the review. There are distinct write paths:

- `recalculate_file(...)` uses the existing workbook/Umya write path.
- `recalculate_xlsx_file(..., output=...)` and `recalculate_xlsx_bytes(...)` are the newer, explicitly invoked **cache-only** APIs. Upstream describes them as preserving formula text and unrelated package members, with unsupported metadata/results rejected instead of publishing partial output. This is an upstream claim to verify on the pinned release and workbook, not proof of Excel-equivalent results.

For cache-only work, evaluate the second path rather than assuming the two APIs have identical preservation behavior. Always specify a separate output, inspect the returned summary/errors, and compare formulas, caches and relevant package members. Do not fall back to a general writer after a preservation rejection without reassessing what that writer can lose.

**formulas:** a pure-Python evaluator with modern function support. A stable package classification and a function name appearing in its coverage list do not establish Excel parity. Test compound reference operations and real formulas; the research reference includes a reported silent wrong-result case.

For either evaluator, pin the version and compare representative results to Excel or independently known answers before adopting it. Include blanks versus zero, error propagation, lookup match modes, dates, dynamic arrays/spill blockers, names, external references and circular/volatile formulas when the workbook uses them. Function counts are not a correctness benchmark.

Record Excel version/build, workbook Compatibility Version, 1900/1904 date system, calculation/iteration settings and relevant locale assumptions for parity tests. Compatibility Version 2 changes Unicode behavior in several text functions; it is the default for **new** Current Channel workbooks from April 2026, not a forced conversion of all existing workbooks.
