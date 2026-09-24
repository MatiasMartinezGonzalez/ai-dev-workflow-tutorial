# E-Commerce Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit sales dashboard (KPIs, trend chart, category/region breakdowns, and a Top 5 Products table) reading `data/sales-data.csv`, with a tested calculations module, and deploy it to Streamlit Community Cloud.

**Architecture:** `calculations.py` holds pure aggregation functions (no I/O), unit-tested with pytest. `charts.py` builds Plotly figures from those results. `app.py` loads and validates the CSV, then wires calculations into charts and Streamlit UI calls. `app.py`'s page logic lives in a `main()` function guarded by `if __name__ == "__main__":` so `load_data()` stays importable and testable without triggering Streamlit calls at import time — everything else about `app.py` behaves exactly as `streamlit run app.py` expects, since Streamlit runs the script as `__main__`.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly, pytest. Plain `venv/` virtual environment with `requirements.txt` (no uv, no conda).

**Spec:** [docs/superpowers/specs/2026-09-23-sales-dashboard-design.md](../specs/2026-09-23-sales-dashboard-design.md)

## Global Constraints

- Python 3.11+ (PRD Technical Approach)
- Plain virtual environment in `venv/`, dependencies in `requirements.txt`; no `uv`, no `conda`
- `calculations.py` has zero Streamlit or file-I/O imports — pure functions only, each unit-tested with pytest
- `charts.py` and `app.py`'s Streamlit rendering are not unit-tested — verified by manually running `streamlit run app.py`
- Work on the current branch (`feature/sales-dashboard`); do not create a git worktree
- Every commit message includes its milestone ID (e.g. `TASK-3: ...`)
- TASK-7 (deployment) is executed by the human partner from `main` after merge — this plan stops at handoff and does not run deployment commands
- The Top 5 Products table (`top_products` in `calculations.py`) is an intentional addition beyond the PRD's Phase 1 scope, labeled "Extra feature, personal brainstorming" in `TASKS.md` (TASK-5) and the design doc — keep that labeling intact in code comments/docstrings where it appears

## Review Focus

- CSV file missing at the configured path → must surface as a clear `st.error()` + `st.stop()`, not an unhandled traceback (PRD Risk: data quality issues, high impact). Pinned in Task 2.
- CSV present but missing one or more required columns (e.g. a stray edit drops `region`) → must surface as a clear `st.error()`, not a `KeyError` deep inside a later groupby call. Pinned in Task 2.
- Rows with missing/NaN values in `total_amount` → KPI sums must not silently become `NaN` on the executive-facing dashboard without at least matching pandas's default (skip missing values) behavior. Pinned in Task 3.
- Fewer distinct products in the data than the requested top-N (e.g. a smaller dataset with only 3 products) → `top_products` must return all available rows rather than erroring or padding with blank rows. Pinned in Task 9.
- A category or region value not on the PRD's known list of 5/4 (e.g. future data adds a 6th category) → `sales_by_category`/`sales_by_region` must include every distinct value actually present in the data, not a hardcoded list. Pinned in Task 7.

---

## Task 1: Project scaffold and dependencies (Milestone: TASK-1)

**Files:**
- Create: `requirements.txt`
- Create: `app.py`

**Interfaces:**
- Produces: `app.py` with a `main()` function that Streamlit runs when the file is executed directly (`if __name__ == "__main__": main()`). No functions here are consumed by later tasks' tests — later tasks add to `main()` directly.

- [ ] **Step 1: Create the virtual environment**

Run: `python -m venv venv` (use `python3` instead of `python` on macOS)

- [ ] **Step 2: Create `requirements.txt`**

```
streamlit
pandas
plotly
pytest
```

- [ ] **Step 3: Activate the virtual environment and install dependencies**

Run (Windows): `venv\Scripts\activate` then `pip install -r requirements.txt`
Run (macOS/Linux): `source venv/bin/activate` then `pip install -r requirements.txt`
Expected: streamlit, pandas, plotly, pytest and their dependencies install without errors.

- [ ] **Step 4: Create the placeholder `app.py`**

```python
import streamlit as st


def main():
    st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
    st.title("ShopSmart Sales Dashboard")
    st.write("Dashboard coming soon.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run the app to verify it launches**

Run: `streamlit run app.py`
Expected: A browser tab opens showing the title "ShopSmart Sales Dashboard" and the text "Dashboard coming soon.", with no errors in the terminal. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt app.py
git commit -m "TASK-1: scaffold project and add dependencies"
```

---

## Task 2: Data loading and validation (Milestone: TASK-2)

**Files:**
- Modify: `app.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: nothing from earlier tasks (this task introduces `load_data`).
- Produces: `load_data(path: str) -> pandas.DataFrame`, defined at module level in `app.py`, raising `FileNotFoundError` (unchanged, from `pandas.read_csv`) or `ValueError` (with a message naming the missing columns) on invalid input. Later tasks' `main()` code calls `load_data(DATA_PATH)` inside a `try`/`except` and pass the returned DataFrame to `calculations.py` functions.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_app.py`:

```python
import pandas as pd
import pytest

from app import load_data, EXPECTED_COLUMNS


def test_load_data_reads_csv_and_parses_dates(tmp_path):
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price,total_amount\n"
        "2024-01-03,ORD-1,Widget,Electronics,North,2,10.0,20.0\n"
    )

    df = load_data(str(csv_path))

    assert len(df) == 1
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_data_raises_file_not_found_for_missing_path(tmp_path):
    missing_path = tmp_path / "does-not-exist.csv"

    with pytest.raises(FileNotFoundError):
        load_data(str(missing_path))


def test_load_data_raises_value_error_for_missing_columns(tmp_path):
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text(
        "date,order_id,product,category,quantity,unit_price,total_amount\n"
        "2024-01-03,ORD-1,Widget,Electronics,2,10.0,20.0\n"
    )

    with pytest.raises(ValueError, match="region"):
        load_data(str(csv_path))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_app.py -v`
Expected: FAIL with `ImportError` or `ModuleNotFoundError` (`load_data`/`EXPECTED_COLUMNS` don't exist yet).

- [ ] **Step 3: Implement `load_data` and wire it into `main()`**

Replace the contents of `app.py`:

```python
import pandas as pd
import streamlit as st

DATA_PATH = "data/sales-data.csv"
EXPECTED_COLUMNS = {
    "date",
    "order_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
    "total_amount",
}


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing expected columns: {sorted(missing)}")
    return df


def main():
    st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
    st.title("ShopSmart Sales Dashboard")

    try:
        data = load_data(DATA_PATH)
    except FileNotFoundError:
        st.error(f"Could not find the data file at `{DATA_PATH}`.")
        st.stop()
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.write(f"Loaded {len(data)} transactions.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_app.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Manually verify against the real data file**

Run: `streamlit run app.py`
Expected: Page shows "Loaded 482 transactions." with no errors. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 6: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "TASK-2: load and validate sales data CSV"
```

---

## Task 3: KPI calculations — total sales and total orders (Milestone: TASK-3)

**Files:**
- Create: `calculations.py`
- Test: `tests/test_calculations.py`

**Interfaces:**
- Consumes: nothing (first task to create `calculations.py`).
- Produces: `total_sales(df: pandas.DataFrame) -> float` and `total_orders(df: pandas.DataFrame) -> int`. Task 4 imports both from `calculations`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_calculations.py`:

```python
import pandas as pd
import pytest

from calculations import total_sales, total_orders


def test_total_sales_sums_total_amount_column():
    df = pd.DataFrame({"total_amount": [100.0, 250.5, 49.99]})

    assert total_sales(df) == pytest.approx(400.49)


def test_total_sales_ignores_missing_values():
    df = pd.DataFrame({"total_amount": [100.0, None, 50.0]})

    assert total_sales(df) == pytest.approx(150.0)


def test_total_orders_counts_rows():
    df = pd.DataFrame({"total_amount": [10.0, 20.0, 30.0]})

    assert total_orders(df) == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'calculations'`

- [ ] **Step 3: Implement the minimal functions**

Create `calculations.py`:

```python
import pandas as pd


def total_sales(df: pd.DataFrame) -> float:
    return df["total_amount"].sum()


def total_orders(df: pd.DataFrame) -> int:
    return len(df)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-3: add total sales and total orders calculations"
```

---

## Task 4: Render KPI cards (Milestone: TASK-3)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `total_sales(df) -> float`, `total_orders(df) -> int` from `calculations.py` (Task 3).

- [ ] **Step 1: Add KPI cards to `main()`**

In `app.py`, add the import and replace the `st.write(f"Loaded {len(data)} transactions.")` line:

```python
from calculations import total_sales, total_orders
```

```python
    col1, col2 = st.columns(2)
    col1.metric("Total Sales", f"${total_sales(data):,.0f}")
    col2.metric("Total Orders", f"{total_orders(data):,}")
```

- [ ] **Step 2: Manually verify**

Run: `streamlit run app.py`
Expected: Two metric cards showing "Total Sales" as approximately `$116,500` and "Total Orders" as `482`, matching the PRD's Expected Output table. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-3: render Total Sales and Total Orders KPI cards"
```

---

## Task 5: Monthly sales calculation (Milestone: TASK-4)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `sales_by_month(df: pandas.DataFrame) -> pandas.Series`, indexed by `pandas.Period` (monthly), values are summed `total_amount`. Task 6 consumes this and passes it to `charts.trend_chart`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_calculations.py`:

```python
from calculations import sales_by_month


def test_sales_by_month_groups_and_sums_by_calendar_month():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-05", "2024-01-20", "2024-02-10"]),
        "total_amount": [100.0, 50.0, 200.0],
    })

    result = sales_by_month(df)

    assert result[pd.Period("2024-01", freq="M")] == pytest.approx(150.0)
    assert result[pd.Period("2024-02", freq="M")] == pytest.approx(200.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_calculations.py -k sales_by_month -v`
Expected: FAIL with `ImportError: cannot import name 'sales_by_month'`

- [ ] **Step 3: Implement the function**

Add to `calculations.py`:

```python
def sales_by_month(df: pd.DataFrame) -> pd.Series:
    return df.groupby(df["date"].dt.to_period("M"))["total_amount"].sum()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_calculations.py -k sales_by_month -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-4: add monthly sales calculation"
```

---

## Task 6: Sales trend chart (Milestone: TASK-4)

**Files:**
- Create: `charts.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_by_month(df) -> pandas.Series` from `calculations.py` (Task 5).
- Produces: `trend_chart(monthly_series: pandas.Series) -> plotly.graph_objects.Figure`. Rendered directly in `app.py`; no later task consumes this function's return value.

- [ ] **Step 1: Create `charts.py` with the trend chart builder**

```python
import plotly.express as px


def trend_chart(monthly_series):
    df = monthly_series.reset_index()
    df.columns = ["month", "total_amount"]
    df["month"] = df["month"].astype(str)

    fig = px.line(
        df,
        x="month",
        y="total_amount",
        markers=True,
        labels={"month": "Month", "total_amount": "Sales ($)"},
        title="Sales Trend Over Time",
    )
    fig.update_traces(hovertemplate="%{x}: $%{y:,.2f}<extra></extra>")
    return fig
```

- [ ] **Step 2: Render the chart in `app.py`**

Add the imports and append after the KPI cards block:

```python
from calculations import total_sales, total_orders, sales_by_month
from charts import trend_chart
```

```python
    st.plotly_chart(trend_chart(sales_by_month(data)), use_container_width=True)
```

- [ ] **Step 3: Manually verify**

Run: `streamlit run app.py`
Expected: A line chart below the KPI cards showing 12 monthly points, with hover tooltips showing exact dollar values. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 4: Commit**

```bash
git add charts.py app.py
git commit -m "TASK-4: add sales trend chart"
```

---

## Task 7: Category and region calculations (Milestone: TASK-5)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `sales_by_category(df) -> pandas.Series` and `sales_by_region(df) -> pandas.Series`, both indexed by the group label and sorted descending by summed `total_amount`. Task 10 consumes both and passes them to `charts.category_chart`/`charts.region_chart`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_calculations.py`:

```python
from calculations import sales_by_category, sales_by_region


def test_sales_by_category_sorted_descending():
    df = pd.DataFrame({
        "category": ["Electronics", "Audio", "Electronics", "Audio"],
        "total_amount": [100.0, 300.0, 50.0, 20.0],
    })

    result = sales_by_category(df)

    assert list(result.index) == ["Audio", "Electronics"]
    assert result["Audio"] == pytest.approx(320.0)
    assert result["Electronics"] == pytest.approx(150.0)


def test_sales_by_category_includes_every_distinct_category():
    df = pd.DataFrame({
        "category": ["Electronics", "Audio", "Wearables"],
        "total_amount": [100.0, 50.0, 10.0],
    })

    result = sales_by_category(df)

    assert set(result.index) == {"Electronics", "Audio", "Wearables"}


def test_sales_by_region_sorted_descending():
    df = pd.DataFrame({
        "region": ["North", "South", "North", "South"],
        "total_amount": [40.0, 100.0, 10.0, 5.0],
    })

    result = sales_by_region(df)

    assert list(result.index) == ["South", "North"]
    assert result["South"] == pytest.approx(105.0)
    assert result["North"] == pytest.approx(50.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_calculations.py -k "sales_by_category or sales_by_region" -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement the functions**

Add to `calculations.py`:

```python
def sales_by_category(df: pd.DataFrame) -> pd.Series:
    return df.groupby("category")["total_amount"].sum().sort_values(ascending=False)


def sales_by_region(df: pd.DataFrame) -> pd.Series:
    return df.groupby("region")["total_amount"].sum().sort_values(ascending=False)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -k "sales_by_category or sales_by_region" -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-5: add category and region sales calculations"
```

---

## Task 8: Top products calculation (Milestone: TASK-5, extra feature)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `top_products(df: pandas.DataFrame, n: int = 5) -> pandas.DataFrame` with columns `product`, `total_revenue`, `units_sold`, sorted descending by `total_revenue`, at most `n` rows. Task 10 renders this DataFrame directly with `st.dataframe`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_calculations.py`:

```python
from calculations import top_products


def test_top_products_returns_top_n_sorted_by_revenue():
    df = pd.DataFrame({
        "product": ["A", "A", "B", "C"],
        "quantity": [1, 2, 5, 1],
        "total_amount": [10.0, 10.0, 100.0, 5.0],
    })

    result = top_products(df, n=2)

    assert list(result["product"]) == ["B", "A"]
    b_row = result[result["product"] == "B"].iloc[0]
    assert b_row["total_revenue"] == pytest.approx(100.0)
    assert b_row["units_sold"] == 5


def test_top_products_returns_all_when_fewer_than_n():
    df = pd.DataFrame({
        "product": ["A", "B"],
        "quantity": [1, 2],
        "total_amount": [10.0, 20.0],
    })

    result = top_products(df, n=5)

    assert len(result) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_calculations.py -k top_products -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement the function**

Add to `calculations.py`:

```python
def top_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Extra feature, personal brainstorming: top products by revenue (beyond PRD scope)."""
    grouped = df.groupby("product").agg(
        total_revenue=("total_amount", "sum"),
        units_sold=("quantity", "sum"),
    )
    return (
        grouped.sort_values("total_revenue", ascending=False)
        .head(n)
        .reset_index()
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -k top_products -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-5: add top products calculation (extra feature, personal brainstorming)"
```

---

## Task 9: Category and region charts, plus Top 5 Products table (Milestone: TASK-5)

**Files:**
- Modify: `charts.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_by_category(df)`, `sales_by_region(df)` from Task 7; `top_products(df)` from Task 8.
- Produces: `category_chart(category_series) -> plotly.graph_objects.Figure`, `region_chart(region_series) -> plotly.graph_objects.Figure`. Rendered directly in `app.py`; no later task consumes these.

- [ ] **Step 1: Add chart builders to `charts.py`**

```python
def category_chart(category_series):
    df = category_series.reset_index()
    df.columns = ["category", "total_amount"]

    fig = px.bar(
        df,
        x="category",
        y="total_amount",
        labels={"category": "Category", "total_amount": "Sales ($)"},
        title="Sales by Category",
    )
    fig.update_traces(hovertemplate="%{x}: $%{y:,.2f}<extra></extra>")
    return fig


def region_chart(region_series):
    df = region_series.reset_index()
    df.columns = ["region", "total_amount"]

    fig = px.bar(
        df,
        x="region",
        y="total_amount",
        labels={"region": "Region", "total_amount": "Sales ($)"},
        title="Sales by Region",
    )
    fig.update_traces(hovertemplate="%{x}: $%{y:,.2f}<extra></extra>")
    return fig
```

- [ ] **Step 2: Render the charts and table in `app.py`**

Update the imports:

```python
from calculations import (
    total_sales,
    total_orders,
    sales_by_month,
    sales_by_category,
    sales_by_region,
    top_products,
)
from charts import trend_chart, category_chart, region_chart
```

Append after the trend chart:

```python
    col3, col4 = st.columns(2)
    col3.plotly_chart(category_chart(sales_by_category(data)), use_container_width=True)
    col4.plotly_chart(region_chart(sales_by_region(data)), use_container_width=True)

    st.subheader("Top 5 Products")
    st.caption("Extra feature, personal brainstorming — beyond the PRD's Phase 1 scope.")
    st.dataframe(top_products(data), use_container_width=True)
```

- [ ] **Step 3: Manually verify**

Run: `streamlit run app.py`
Expected: Category bar chart (5 bars, sorted highest to lowest, Electronics on top), region bar chart (4 bars, sorted highest to lowest), and a Top 5 Products table below with columns `product`, `total_revenue`, `units_sold`, each with working hover tooltips on the charts. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 4: Commit**

```bash
git add charts.py app.py
git commit -m "TASK-5: add category and region charts and top products table"
```

---

## Task 10: Testing and refinement (Milestone: TASK-6)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: the full `main()` built by Tasks 1–9. No new functions produced.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: All tests pass (calculations tests + `app.py` load_data tests), no failures or warnings.

- [ ] **Step 2: Add visual separation between sections**

In `app.py`, insert `st.divider()` between the KPI row and the trend chart, and between the trend chart and the category/region row:

```python
    st.divider()
    st.plotly_chart(trend_chart(sales_by_month(data)), use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)
```

(These replace the corresponding lines added in Tasks 6 and 9 — same code, with a `st.divider()` line added directly above each.)

- [ ] **Step 3: Manually verify against the PRD's acceptance criteria**

Run: `streamlit run app.py` and confirm each of the following (PRD "Acceptance Criteria" section):
- Total Sales and Total Orders displayed prominently, matching ~$116,500 and 482
- Trend chart shows 12 months of data with working tooltips
- Category chart shows all 5 categories, sorted highest to lowest, Electronics on top
- Region chart shows all 4 regions, sorted highest to lowest
- No errors or warnings appear in the terminal or in the browser
- Overall layout looks clean and presentation-ready (consistent spacing via the dividers added above)

Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "TASK-6: polish layout and verify against PRD acceptance criteria"
```

---

## Task 11: Deployment to Streamlit Community Cloud (Milestone: TASK-7) — HUMAN-EXECUTED

**This task is not implemented by the agent.** It requires the human partner's GitHub and Streamlit Cloud accounts and a go/no-go call on making the dashboard publicly visible. Stop here and hand off.

For the human partner, after this branch is reviewed and merged to `main`:

1. Push `main` to GitHub (if not already pushed).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in, and click "New app".
3. Select this repository, the `main` branch, and `app.py` as the entry point.
4. Click Deploy and wait for Streamlit Cloud to install `requirements.txt` and start the app.
5. Verify the public URL loads correctly and matches what was verified locally in Task 10.
6. Update `TASKS.md`: move TASK-7 to Done, and fill in its `Commit:` line.

---

## Self-Review Notes

- **Spec coverage:** Every design-doc element maps to a task — architecture/file layout (Task 1), data loading/validation (Task 2), KPI calculations and rendering (Tasks 3–4), trend chart (Tasks 5–6), category/region/top-products calculations and rendering (Tasks 7–9), testing/refinement (Task 10), deployment (Task 11, human-executed).
- **Type consistency:** `sales_by_month`/`sales_by_category`/`sales_by_region` all return `pandas.Series` consumed by matching `charts.py` functions with matching `reset_index()` + rename pattern; `top_products` returns a `pandas.DataFrame` consumed directly by `st.dataframe` with no chart wrapper, consistent with the design doc.
- **Review Focus:** all five items are pinned by tests in the task that owns the relevant code (Task 2: missing file / missing columns; Task 3: NaN in `total_amount`; Task 7: all distinct categories included; Task 8: fewer products than `n`).
