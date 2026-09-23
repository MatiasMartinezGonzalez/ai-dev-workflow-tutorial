# Design: E-Commerce Sales Dashboard

Source: [prd/ecommerce-analytics.md](../../../prd/ecommerce-analytics.md)
Milestones tracked in: [TASKS.md](../../../TASKS.md)

## Overview

A single-page Streamlit dashboard reading `data/sales-data.csv`, showing two KPI
cards, a monthly sales trend line chart, category and region bar charts, and a
Top 5 Products table. Built on the current feature branch
(`feature/sales-dashboard`), no git worktree.

## Architecture

```
data/sales-data.csv          (existing, unchanged)
calculations.py              (pure functions, no I/O — unit tested)
charts.py                    (Plotly figure builders, take calculation results in)
app.py                       (Streamlit page: load CSV, call calculations, call charts, render)
tests/test_calculations.py   (pytest suite for calculations.py)
requirements.txt             (streamlit, pandas, plotly, pytest)
venv/                        (gitignored)
```

Data flows one direction: `app.py` loads the CSV, passes the DataFrame to
`calculations.py` functions, passes the results to `charts.py` builders, then
renders the returned Plotly figures and metric values with `st.metric` /
`st.plotly_chart` / `st.dataframe`.

`calculations.py` has no Streamlit or file-I/O imports, so its tests build
small in-memory DataFrames and assert on plain numbers — no app startup, no
fixture files.

## `calculations.py`

Six pure functions, each taking the loaded sales DataFrame and returning a
plain value. Sorting for the ranked outputs happens here, not in `charts.py`,
so tests can assert order directly.

| Function | Returns | Backs |
|---|---|---|
| `total_sales(df)` | `float` — sum of `total_amount` | FR-1 (Total Sales KPI) |
| `total_orders(df)` | `int` — row count | FR-1 (Total Orders KPI) |
| `sales_by_month(df)` | Series indexed by month, summed `total_amount` | FR-2 (trend chart) |
| `sales_by_category(df)` | Series indexed by category, summed, sorted descending | FR-3 (category chart) |
| `sales_by_region(df)` | Series indexed by region, summed, sorted descending | FR-4 (region chart) |
| `top_products(df, n=5)` | DataFrame: top *n* products by total revenue, with units sold | **Extra feature, personal brainstorming (beyond PRD scope)** |

## `charts.py`

Three builder functions, each taking a calculation result and returning a
Plotly `Figure`:

- `trend_chart(monthly_series)` — line chart, month on X, sales on Y, hover tooltip with exact value
- `category_chart(category_series)` — bar chart, already sorted by the calculation layer, hover tooltip with exact value
- `region_chart(region_series)` — same, for region

The Top 5 Products table is rendered directly from `top_products()`'s
DataFrame via `st.dataframe` in `app.py` — no chart-builder function needed.

## `app.py` — page structure

1. `st.set_page_config(...)` + title ("ShopSmart Sales Dashboard")
2. Load CSV, validate the 8 expected columns are present
   - On `FileNotFoundError` or a column mismatch: `st.error("...")` with a
     specific message, then `st.stop()` — the rest of the script never runs
     against bad data
3. Two-column `st.metric()` row: Total Sales (currency-formatted
   `$X,XXX,XXX`), Total Orders (comma-formatted count)
4. `st.plotly_chart(trend_chart(...))`, full width
5. Two-column `st.plotly_chart()` row: category, then region
6. `st.dataframe(top_products(...))` — Top 5 Products table (**extra feature,
   personal brainstorming**)

Currency/comma formatting happens in `app.py` at render time, not in
`calculations.py`, which returns raw numbers to stay simple to test.

## Testing strategy

- `tests/test_calculations.py`: one test per function in `calculations.py`
  (six total), each building a small in-memory DataFrame (3-5 rows spanning
  multiple categories/regions/months) and asserting exact expected output,
  including sort order for `sales_by_category`, `sales_by_region`, and
  `top_products`.
- No tests for `charts.py` or `app.py` — Plotly figure construction and
  Streamlit layout are UI glue verified by manually running
  `streamlit run app.py`, not unit tests.

## Error handling

CSV loading and column validation live in `app.py`. A missing file or a
mismatched column set produces a specific `st.error()` message and
`st.stop()`, rather than a raw traceback — matching NFR-2 (no training
required) and the PRD's "no errors" acceptance criterion.

## Milestone mapping

| Milestone | Design elements it covers |
|---|---|
| TASK-1 | `venv/`, `requirements.txt` (streamlit, pandas, plotly, pytest), folder scaffold, placeholder `app.py` |
| TASK-2 | CSV loading + column validation + `st.error`/`st.stop()` in `app.py` |
| TASK-3 | `total_sales`, `total_orders` in `calculations.py` (+ tests); KPI cards in `app.py` |
| TASK-4 | `sales_by_month` (+ test); `trend_chart` in `charts.py`; rendered in `app.py` |
| TASK-5 | `sales_by_category`, `sales_by_region`, `top_products` (+ tests); `category_chart`, `region_chart` in `charts.py`; Top 5 Products table in `app.py` |
| TASK-6 | Manual verification against PRD acceptance criteria; layout/label polish |
| TASK-7 | Deployment to Streamlit Community Cloud — yours to execute from `main` after merge |

## Non-goals

Explicitly out of scope per the PRD's Phase 2 list: authentication, real-time
database integration, export functionality, email alerts, filtering/date-range
selection, transaction-level drill-down, mobile-responsive design.

The Top 5 Products table is the one deliberate exception beyond Phase 1
scope — added at the developer's request as a simple, business-relevant
enhancement (addresses the PRD's own stated pain points: marketing lacking
data to optimize campaigns, inventory decisions made with outdated
information) and labeled **"Extra feature, personal brainstorming"** in both
this document and `TASKS.md` (TASK-5) to keep it clearly distinguished from
the PRD's baseline requirements.
