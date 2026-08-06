import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "extract"))  # noqa: E402
from extract_crm import clean_dataframe  # noqa: E402


def test_clean_dataframe_removes_duplicates_by_id():
    """Debe eliminar filas con el mismo id_column, quedándose con la primera."""
    df = pd.DataFrame({
        "account_id": ["ACC-0001", "ACC-0001", "ACC-0002"],
        "account_name": ["Keokuk Spirits", "Keokuk Spirits ", "John's Grocery"],
    })

    resultado = clean_dataframe(df, id_column="account_id")

    assert len(resultado) == 2
    assert set(resultado["account_id"]) == {"ACC-0001", "ACC-0002"}


def test_clean_dataframe_strips_whitespace():
    """Debe quitar espacios en blanco al inicio/final de columnas de texto."""
    df = pd.DataFrame({
        "account_id": ["ACC-0001"],
        "account_name": ["  Keokuk Spirits  "],
    })

    resultado = clean_dataframe(df, id_column="account_id")

    assert resultado.iloc[0]["account_name"] == "Keokuk Spirits"


def test_clean_dataframe_keeps_unique_rows_untouched():
    """No debe eliminar filas cuando no hay duplicados."""
    df = pd.DataFrame({
        "account_id": ["ACC-0001", "ACC-0002", "ACC-0003"],
        "account_name": ["A", "B", "C"],
    })

    resultado = clean_dataframe(df, id_column="account_id")

    assert len(resultado) == 3