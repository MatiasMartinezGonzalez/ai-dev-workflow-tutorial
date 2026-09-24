import pandas as pd
import streamlit as st

from calculations import (
    total_sales,
    total_orders,
    sales_by_month,
    sales_by_category,
    sales_by_region,
    top_products,
)
from charts import trend_chart, category_chart, region_chart

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
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        raise ValueError("CSV contains invalid values in the 'date' column")
    if not pd.api.types.is_numeric_dtype(df["total_amount"]):
        raise ValueError("CSV contains non-numeric values in the 'total_amount' column")
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

    col1, col2 = st.columns(2)
    col1.metric("Total Sales", f"${total_sales(data):,.0f}")
    col2.metric("Total Orders", f"{total_orders(data):,}")

    st.divider()
    st.plotly_chart(trend_chart(sales_by_month(data)), use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)
    col3.plotly_chart(category_chart(sales_by_category(data)), use_container_width=True)
    col4.plotly_chart(region_chart(sales_by_region(data)), use_container_width=True)

    st.subheader("Top 5 Products")
    st.caption("Extra feature, personal brainstorming — beyond the PRD's Phase 1 scope.")
    st.dataframe(
        top_products(data),
        use_container_width=True,
        hide_index=True,
        column_config={
            "product": st.column_config.TextColumn("Product"),
            "total_revenue": st.column_config.NumberColumn("Total Revenue", format="$%.2f"),
            "units_sold": st.column_config.NumberColumn("Units Sold", format="%d"),
        },
    )


if __name__ == "__main__":
    main()
