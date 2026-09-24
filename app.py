import pandas as pd
import streamlit as st

from calculations import total_sales, total_orders, sales_by_month
from charts import trend_chart

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

    col1, col2 = st.columns(2)
    col1.metric("Total Sales", f"${total_sales(data):,.0f}")
    col2.metric("Total Orders", f"{total_orders(data):,}")

    st.plotly_chart(trend_chart(sales_by_month(data)), use_container_width=True)


if __name__ == "__main__":
    main()
