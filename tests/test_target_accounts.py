import pytest
from google.cloud import bigquery

PROJECT_ID = "alchemialabs-tech-assessment"
TABLE_ID = f"{PROJECT_ID}.analytics.target_accounts_iowa_gin"


@pytest.fixture(scope="module")
def client():
    return bigquery.Client(project=PROJECT_ID)


@pytest.fixture(scope="module")
def target_accounts(client):
    query = f"SELECT * FROM `{TABLE_ID}`"
    return client.query(query).result().to_dataframe()


def test_returns_exactly_25_accounts(target_accounts):
    assert len(target_accounts) == 25


def test_no_duplicate_store_numbers(target_accounts):
    assert target_accounts["store_number"].is_unique


def test_no_nulls_in_key_fields(target_accounts):
    campos_clave = ["store_number", "store_name", "total_sale_dollars"]
    for campo in campos_clave:
        assert target_accounts[campo].notna().all(), f"Se encontraron nulos en '{campo}'"


def test_no_overlap_with_existing_crm_accounts(client):
    query = f"""
        SELECT COUNT(*) AS coincidencias
        FROM `{TABLE_ID}` t
        WHERE t.store_number IN (
            SELECT CAST(store_number AS STRING)
            FROM `{PROJECT_ID}.raw.crm_accounts`
            WHERE store_number IS NOT NULL
        )
    """
    resultado = client.query(query).result().to_dataframe()
    assert resultado.iloc[0]["coincidencias"] == 0


def test_ranked_descending_by_sale_dollars(target_accounts):
    valores = target_accounts["total_sale_dollars"].tolist()
    assert valores == sorted(valores, reverse=True)