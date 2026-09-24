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


from calculations import sales_by_month


def test_sales_by_month_groups_and_sums_by_calendar_month():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-05", "2024-01-20", "2024-02-10"]),
        "total_amount": [100.0, 50.0, 200.0],
    })

    result = sales_by_month(df)

    assert result[pd.Period("2024-01", freq="M")] == pytest.approx(150.0)
    assert result[pd.Period("2024-02", freq="M")] == pytest.approx(200.0)
