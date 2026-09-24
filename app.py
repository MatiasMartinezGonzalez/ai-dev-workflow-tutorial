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
