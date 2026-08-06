import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "extract"))

import pandas as pd  # noqa: E402
from google.cloud import bigquery  # noqa: E402
from extract_crm import extract_entity  # noqa: E402
from extract_catalogue import download_parquet_as_dataframe, clean_catalogue, CATALOGUE_BLOB_NAME  # noqa: E402
PROJECT_ID = "alchemialabs-tech-assessment"
DATASET_ID = "raw"


def load_dataframe_to_bq(df: pd.DataFrame, table_name: str) -> None:
    """
    Sube un DataFrame de pandas como tabla en BigQuery,
    reemplazando la tabla completa si ya existe (WRITE_TRUNCATE).
    """
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    print(f"  Tabla '{table_id}' cargada: {len(df)} filas")


if __name__ == "__main__":
    accounts = extract_entity("crm/crm_accounts", "account_id")
    contacts = extract_entity("crm/crm_contacts", "contact_id")
    opportunities = extract_entity("crm/crm_opportunities", "opportunity_id")

    catalogue = download_parquet_as_dataframe(CATALOGUE_BLOB_NAME)
    catalogue = clean_catalogue(catalogue)

    print("\n--- Cargando a BigQuery ---")
    load_dataframe_to_bq(accounts, "crm_accounts")
    load_dataframe_to_bq(contacts, "crm_contacts")
    load_dataframe_to_bq(opportunities, "crm_opportunities")
    load_dataframe_to_bq(catalogue, "product_catalogue")

    print("\nCarga completa.")