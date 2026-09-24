import pandas as pd


def total_sales(df: pd.DataFrame) -> float:
    return df["total_amount"].sum()


def total_orders(df: pd.DataFrame) -> int:
    return len(df)


def sales_by_month(df: pd.DataFrame) -> pd.Series:
    return df.groupby(df["date"].dt.to_period("M"))["total_amount"].sum()
