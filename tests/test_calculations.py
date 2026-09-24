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
