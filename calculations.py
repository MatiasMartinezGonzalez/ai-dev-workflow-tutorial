import pandas as pd


def total_sales(df: pd.DataFrame) -> float:
    return df["total_amount"].sum()


def total_orders(df: pd.DataFrame) -> int:
    return len(df)
