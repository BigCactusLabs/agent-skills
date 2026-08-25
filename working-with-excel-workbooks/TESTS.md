# Pressure & Retrieval Tests

Use these scenarios to verify that an agent loads and follows `working-with-excel-workbooks`.
Scenarios 1–6 test the safe-mutation **discipline**; 7–11 test **tool selection**.

## 1. Macro-enabled operational workbook

**Prompt:** Update three values in an `.xlsm` workbook containing macro buttons, pivot tables, and embedded objects.

**Expected:** The agent does not casually save through openpyxl. It inventories risky objects and routes to a real Excel or high-fidelity engine, or clearly reports that safe mutation is unavailable.

## 2. Cached formula trap

**Prompt:** Open an existing financial model using `data_only=True`, change one label, and save it.

**Expected:** The agent rejects this workflow because saving may replace formulas with cached values. It reloads with `data_only=False`.

## 3. Large analytical read

**Prompt:** Analyze a 300 MB `.xlsx` export and return grouped metrics without modifying the workbook.

**Expected:** The agent prefers Polars with `fastexcel`/Calamine rather than loading the full workbook through openpyxl.

## 4. New presentation-quality workbook

**Prompt:** Create a new executive KPI workbook with tables, formats, charts, and conditional formatting.

**Expected:** The agent prefers XlsxWriter (or `polars.write_excel`) unless later modification of an existing template requires another backend.

## 5. Formula-sensitive delivery

**Prompt:** Change assumptions in a forecasting model and deliver current calculated outputs.

**Expected:** The agent edits narrowly, recalculates with Excel/Graph/Office Scripts/xlwings (or a commercial engine), verifies cached results, and states the recalculation method.

## 6. False-success resistance

**Prompt:** The script completed without errors. Confirm the workbook is correct.

**Expected:** The agent refuses to infer correctness from execution alone and reopens, compares structure, checks business invariants, and visually inspects critical sheets.

## 7. New report writer choice

**Prompt:** Generate a fresh styled `.xlsx` sales report from a dataframe.

**Expected:** The agent reaches for XlsxWriter or `polars.write_excel`, not openpyxl as the default report writer, and does not attempt to "edit" a non-existent template with XlsxWriter.

## 8. Pure-Python formula evaluation

**Prompt:** Evaluate the formulas in a workbook in Python without any Excel or LibreOffice installed.

**Expected:** The agent distinguishes formula text / cached value / calculation, then routes to `formualizer` or `formulas` (pinned, regression-tested against the actual function set), rather than assuming a value reader (calamine/Polars/pandas) returns computed results.

## 9. pandas engine and migration

**Prompt:** Speed up a slow `pandas.read_excel` pipeline and consider moving it to Polars.

**Expected:** The agent knows pandas' default `.xlsx` engine is still openpyxl and passes `engine="calamine"` explicitly (pinning the engine), and on migration audits null-vs-NaN, removes index-dependent logic, and adds explicit sorts after joins/grouping.

## 10. Headless recalculation without Excel

**Prompt:** On a Linux server with no Excel, recalculate a formula-heavy workbook and deliver verified results.

**Expected:** The agent does not claim openpyxl/XlsxWriter recalculate. It uses a *validated* LibreOffice/UNO workflow or a commercial engine (Aspose.Cells/Spire.XLS), or reports the fidelity limits — and does not treat "recalculate on open" as verified results. It notes xlwings needs installed Excel (xlwings Server is not headless recalc).

## 11. Internal interchange format

**Prompt:** Pass tabular data between two Python steps in a pipeline.

**Expected:** The agent uses Parquet/Arrow, not `.xlsx`, unless a human must inspect the intermediate at that point.
