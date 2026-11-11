# Pressure & Retrieval Tests

Use these scenarios to verify that an agent loads and follows `working-with-excel-workbooks`.
Scenarios 1–6 test safe mutation; 7–11 test tool selection; 12–18 cover the September 2026 corrections. These are behavioral evaluation prompts, not a claim that every scenario was executed.

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

## 8. Formula evaluation from Python

**Prompt:** Evaluate the formulas in a workbook in Python without any Excel or LibreOffice installed.

**Expected:** The agent distinguishes formula text / cached value / calculation, then routes to `formualizer` or `formulas` (pinned, regression-tested against the actual function set), rather than assuming a value reader (calamine/Polars/pandas) returns computed results.

## 9. pandas engine and migration

**Prompt:** Speed up a slow `pandas.read_excel` pipeline and consider moving it to Polars.

**Expected:** The agent checks installed/stable behavior, distinguishes the announced development-doc default change from a shipped switch, and pins `engine="calamine"` when selecting that reader. Migration audits null-vs-NaN, index assumptions and output order.

## 10. Headless recalculation without Excel

**Prompt:** On a Linux server with no Excel, recalculate a formula-heavy workbook and deliver verified results.

**Expected:** The agent does not claim openpyxl/XlsxWriter recalculate. It uses a *validated* LibreOffice/UNO workflow or a commercial engine (Aspose.Cells/Spire.XLS), or reports the fidelity limits — and does not treat "recalculate on open" as verified results. It notes xlwings needs installed Excel (xlwings Server is not headless recalc).

## 11. Internal interchange format

**Prompt:** Pass tabular data between two Python steps in a pipeline.

**Expected:** The agent uses Parquet/Arrow, not `.xlsx`, unless a human must inspect the intermediate at that point.

## 12. Personal Office Scripts versus app-only Graph

**Prompt:** I have Microsoft 365 Personal. Can I run Office Scripts? Can the same setup use app-only Graph workbook calculation?

**Expected:** The agent distinguishes the documented Personal/Family Office Scripts preview from Graph calculate, which supports neither personal accounts nor application permissions. Power Automate integration has separate business-license requirements. It does not upload a local workbook merely to try either route.

## 13. Successful calculation with stale query inputs

**Prompt:** My Power Automate script called refreshAllDataConnections and then calculate without an error. Confirm that the Power Query sales source and pivot report are current.

**Expected:** The agent does not confirm freshness. It checks actual source/refresh evidence and identifies the flow-specific data-connection and pivot refresh limits separately from calculation success.

## 14. Constant-memory table export

**Prompt:** Create a large styled report with Excel tables using Polars write_excel, and turn on XlsxWriter constant_memory to save RAM.

**Expected:** The agent identifies the incompatible table requirement. It chooses normal mode if feasible or a revised row-major export design, explains the effect on tables, and does not silently emit incomplete columns or remove requested features.

## 15. Cache-only preservation claim

**Prompt:** Only update formula caches in this rich XLSX without Excel. Use formualizer because it says it preserves package members.

**Expected:** The agent checks the installed version and distinguishes recalculate_xlsx_file from recalculate_file, writes to a separate output, verifies supported inputs and result errors, and checks formulas/caches/required package parts. It does not turn an upstream preservation claim into an Excel-parity guarantee or silently fall back after rejection.

## 16. Conventional workbook is not automatically high risk

**Prompt:** Change one label in a plain XLSX with an ordinary supported chart and table. No current calculation is required. openpyxl is available.

**Expected:** The agent inventories the workbook and can choose a narrow openpyxl edit, preserving formula text and checking the chart/table after saving. It reports cache limits; it does not insist that any chart or table requires Excel or a paid engine.

## 17. Partial read and typed identifiers

**Prompt:** Read the first ten rows from a very large workbook. Preserve identifiers such as 00123 and literal NA values.

**Expected:** The agent considers lazy read-only extraction instead of asserting that calamine always wins. It checks stored values versus formatting and explicit missing-value/type handling. It does not claim that converting a completed Polars Excel read to lazy mode makes ingestion stream.

## 18. Formula count and coverage are insufficient

**Prompt:** This evaluator lists INDEX and SUM, and the formula count is unchanged after saving. For A1:E1 containing 1,2,3,4,5, confirm SUM(INDEX(A1:E1,,2):D1) is correct.

**Expected:** The agent checks the actual result against 9 and compares formula coordinates/text, not just counts. It treats upstream issue reports as reports unless reproduced, and does not infer correctness from supported function names.
