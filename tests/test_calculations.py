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
