# Excel tooling review — 2026-09-26

Scope: refresh tool selection, preservation and calculation guidance with frontier-search at medium effort. High confidence in the documented API distinctions below; conditional confidence in alternative engines until a representative workbook passes comparison tests. Release metadata is an observation date, not a mandatory upgrade list.

## Changes that affect decisions

### Microsoft automation has separate restrictions

[Graph calculation permissions](https://learn.microsoft.com/en-us/graph/api/workbookapplication-calculate?view=graph-rest-1.0) exclude application permissions and personal accounts. [Office Scripts platform requirements](https://learn.microsoft.com/en-us/office/dev/scripts/testing/platform-limits) instead document a Personal/Family preview and business licensing for Power Automate. The previous combined restriction was wrong. The same platform page documents the web payload/range limits and Power Automate timeout used in the calculation reference.

[Power Automate troubleshooting](https://learn.microsoft.com/en-us/office/dev/scripts/testing/power-automate-troubleshooting) explicitly warns that most refresh methods do nothing in flows; data-connection refresh supports Power BI sources. Treat data freshness and formula calculation as separate acceptance checks. [Graph session documentation](https://learn.microsoft.com/en-us/graph/api/workbook-createsession?view=graph-rest-1.0) also distinguishes persisted, temporary and sessionless changes.

### formualizer has a new cache-only path, with remaining correctness limits

[Version 0.9.2 release notes](https://github.com/PSU3D0/formualizer/releases/tag/v0.9.2) introduce separate cache-only XLSX APIs with package-preserving writeback and rejection of unsupported metadata/results. The [0.9.3 Python package documentation](https://pypi.org/project/formualizer/0.9.3/) distinguishes `recalculate_xlsx_file`/`recalculate_xlsx_bytes` from the existing `recalculate_file` and Umya export path. This is useful when only formula caches need updating; it is not a reason to route arbitrary rich-document edits through that engine.

Counter-case: [0.9.3 release notes](https://github.com/PSU3D0/formualizer/releases/tag/v0.9.3) describe fixes to stale dependencies, spill handling and statistics. [Maintainer issue 464](https://github.com/PSU3D0/formualizer/issues/464), still open when checked, records residual statistical precision and Z.TEST convention problems. New function counts and active commits do not establish Excel parity. Test the pinned release against actual formulas and independently known results.

### Stable evaluators still need semantic checks

The [formulas changelog](https://formulas.readthedocs.io/en/stable/change.html) documents modern functions including LET, LAMBDA, XLOOKUP and dynamic-array operations. Do not reduce suitability to a percentage of supported functions. [Issue 182](https://github.com/vinci1it2000/formulas/issues/182) reports a silent wrong result in 1.3.4 for `SUM(INDEX(A1:E1,,2):D1)` with values 1–5: reported 12 versus the expected 9. This is an upstream report, not a reproduction performed during this review. It supplies a useful compound-reference regression case.

### Reader defaults and memory modes need precise wording

[pandas 3.0.6 read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html) still selects openpyxl for ordinary `.xlsx` reads. The [3.1 development notes](https://pandas.pydata.org/pandas-docs/dev/whatsnew/v3.1.0.html) announce a future calamine default and deprecate xlrd/pyxlsb readers; these are development changes, not stable-release behavior. Pin an engine. The older [calamine introduction](https://pandas.pydata.org/pandas-docs/dev/whatsnew/v2.2.0.html) also identifies the counter-case: lazy readers can win for a few rows from large files. No speed ratios were adopted here.

[Polars read_excel](https://docs.pola.rs/api/python/stable/reference/api/polars.read_excel.html) supports schema overrides and inference controls. Its [write_excel API](https://docs.pola.rs/api/python/stable/reference/api/polars.DataFrame.write_excel.html) writes tables. [XlsxWriter memory guidance](https://xlsxwriter.readthedocs.io/working_with_memory.html) requires row-major writes in constant-memory mode and excludes tables. Inference: do not enable that mode blindly on a dataframe writer. The [Workbook API](https://xlsxwriter.readthedocs.io/workbook.html) documents `in_memory` overriding constant-memory mode and automatic string-to-formula conversion.

### Preservation is feature-specific

[openpyxl's tutorial](https://openpyxl.readthedocs.io/en/stable/tutorial.html) documents `data_only`, VBA, rich text, links and loss of unsupported shapes. Its [table documentation](https://openpyxl.readthedocs.io/en/stable/worksheet_tables.html) demonstrates supported tables. The correct boundary is required feature support, not a blanket ban whenever a workbook contains formulas or tables. A sparse release history is not proof of abandonment.

[xlwings App documentation](https://docs.xlwings.org/en/latest/api/app.html) provides explicit calculation and warns about simultaneous writers on macOS; [installation guidance](https://docs.xlwings.org/en/latest/installation.html) gives platform requirements. The example now calls calculation before saving. [Excel Compatibility Versions](https://support.microsoft.com/en-us/excel/compatibility-versions) applies Version 2 by default to **new** Current Channel workbooks, not all existing workbooks.

[LibreOffice 26.8 was released on August 26](https://blog.documentfoundation.org/blog/2026/08/26/libreoffice-26-8/); it is no longer a beta in this snapshot. Its XLSX fixes do not establish full fidelity. [Hard recalculation](https://help.libreoffice.org/latest/en-US/text/scalc/01/recalculate_hard.html) remains a separate operation to invoke and verify.

## Maintenance snapshot

PyPI JSON metadata was fetched directly with the requested user agent. These are latest package versions observed on 2026-09-26, not versions installed or benchmarked in the user's projects.

| Package | Version | Release date | Primary metadata |
| --- | --- | --- | --- |
| pandas | 3.0.6 | 2026-09-17 | [PyPI](https://pypi.org/pypi/pandas/json) |
| Polars | 1.44.2 | 2026-09-09 | [PyPI](https://pypi.org/pypi/polars/json) |
| python-calamine | 0.8.2 | 2026-07-13 | [PyPI](https://pypi.org/pypi/python-calamine/json) |
| fastexcel | 0.21.0 | 2026-08-19 | [PyPI](https://pypi.org/pypi/fastexcel/json) |
| XlsxWriter | 3.2.9 | 2025-09-16 | [PyPI](https://pypi.org/pypi/XlsxWriter/json) |
| openpyxl | 3.1.5 | 2024-06-28 | [PyPI](https://pypi.org/pypi/openpyxl/json) |
| xlwings | 0.37.4 | 2026-09-16 | [PyPI](https://pypi.org/pypi/xlwings/json) |
| formualizer | 0.9.3, Beta classifier | 2026-09-11 | [PyPI](https://pypi.org/pypi/formualizer/json) |
| formulas | 1.3.4, Stable classifier | 2026-03-11 | [PyPI](https://pypi.org/pypi/formulas/json) |
| IronCalc | 0.8.3, Alpha classifier | 2026-07-31 | [PyPI](https://pypi.org/pypi/ironcalc/json) |
| Aspose.Cells Python via .NET | 26.9.0 | 2026-09-14 | [PyPI](https://pypi.org/pypi/aspose-cells-python/json) |
| Spire.XLS | 16.8.2 | 2026-08-25 | [PyPI](https://pypi.org/pypi/spire-xls/json) |

GitHub repository metadata checked with `gh` showed these projects unarchived, with latest pushes in the stated month: [pandas](https://github.com/pandas-dev/pandas), [Polars](https://github.com/pola-rs/polars), [python-calamine](https://github.com/dimastbk/python-calamine), [fastexcel](https://github.com/ToucanToco/fastexcel), [xlwings](https://github.com/xlwings/xlwings), [formualizer](https://github.com/PSU3D0/formualizer) and [IronCalc](https://github.com/ironcalc/IronCalc) in September 2026; [XlsxWriter](https://github.com/jmcnamara/XlsxWriter) and [formulas](https://github.com/vinci1it2000/formulas) in August. Push dates measure activity, not correctness or a new release. Current formualizer and formulas issues supplied the failure checks above.

Access-limited: openpyxl's [Heptapod commit view](https://foss.heptapod.net/openpyxl/openpyxl/-/commits/branch/3.1) failed in the browser fetch; a direct retry returned the page shell without usable commit dates. Its PyPI release and documentation were checked, but current commit/issue activity and archived status were not established. Do not infer them from the 2024 release date.

## Agent-oriented candidates

The old `PSU3D0/spreadsheet-mcp` repository redirects to [agent-spreadsheet](https://github.com/PSU3D0/agent-spreadsheet). Its current README describes a Formualizer-backed CLI/MCP/SDK, `.xlsx`/`.xlsm` writes and discovery/read workflows for `.xls`/`.xlsb`. [IronCalc](https://github.com/ironcalc/IronCalc) describes itself as a work in progress with XLSX import/export. Both repositories were active and unarchived; neither was tested for full workbook fidelity in this review.

Keep these as evaluation candidates, not preferred backends solely because they expose MCP. An agent protocol adds no calculation or preservation capability beyond its underlying engine. The old star-count comparison was removed because it was neither stable nor a useful correctness signal.

## Evidence coverage and limits

- **T1:** Microsoft and library docs establish API behavior; package metadata establishes release observations.
- **T2:** repository status, releases and issue reports test maintenance and counter-cases. Commercial pricing, incidents and feature parity were not evaluated; those engines remain conditional candidates.
- **T4:** XlsxWriter maintainer John McNamara's [first-hand autofit notes](https://github.com/jmcnamara/XlsxWriter/issues/936) and [constant-memory response](https://github.com/jmcnamara/XlsxWriter/issues/1125#issuecomment-2758968612) explain implementation limits. These older sources are useful design evidence, not recent performance tests. They overlap the library's T1/T2 channel and are not independent corroboration.
- **T3/T5:** no independent comparative fidelity benchmark or broad pre-consensus survey was established. Emerging tools were checked against their own artifacts; no performance ranking is claimed.

Post-draft checks re-examined the Graph/Office Scripts distinction, the two formualizer write paths and XlsxWriter memory restrictions. Session persistence was clarified after checking Microsoft's createSession documentation. Omitted: full Excel/LibreOffice/commercial parity testing and licensing comparison.

Local validation: the skill validator, relative links and Python example syntax passed. Seven synthetic checks with openpyxl 3.1.5 and XlsxWriter 3.2.9 confirmed formula/cache separation, literal text handling, cache loss on an openpyxl save, chart/table survival in a narrow conventional edit, formula loss after a data-only save, the row-major memory-mode requirement and table rejection in that mode. These small checks do not establish rich-workbook fidelity. The xlwings example was checked against its API documentation and parsed, but not executed in Excel. formualizer, formulas, Office Scripts and Graph were researched rather than run.

*Adapted: focused on execution boundaries and concrete failure cases instead of function counts or popularity.*
