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
