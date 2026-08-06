import pandas as pd
from google.cloud import storage
from io import BytesIO

PROJECT_ID = "alchemialabs-tech-assessment"
BUCKET_NAME = "alchemialabs-tech-assessment"
CATALOGUE_BLOB_NAME = "product_catalogue.parquet"


def download_parquet_as_dataframe(blob_name: str) -> pd.DataFrame:
    """
    Descarga un archivo Parquet del bucket y lo carga como DataFrame de pandas.
    A diferencia del CSV, Parquet no necesita especificar encoding: 
    el esquema y tipos de dato ya vienen definidos dentro del propio archivo.
    """
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    contenido = blob.download_as_bytes()
    df = pd.read_parquet(BytesIO(contenido))

    return df


def clean_catalogue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza del catálogo de productos:
    - Quita espacios en blanco al inicio/final de columnas de texto real (no fechas)
    - Verifica que no haya sku_id duplicados (no se esperan, pero se valida por seguridad)
    """
    for col in df.columns:
        primer_valor = df[col].dropna().iloc[0] if df[col].notna().any() else None
        if isinstance(primer_valor, str):
            df[col] = df[col].str.strip()

    duplicados = df["sku_id"].duplicated().sum()
    if duplicados > 0:
        print(f"  ADVERTENCIA: se encontraron {duplicados} sku_id duplicados")
    else:
        print("  Sin duplicados en sku_id")

    return df


if __name__ == "__main__":
    df = download_parquet_as_dataframe(CATALOGUE_BLOB_NAME)
    print(f"Filas descargadas: {len(df)}")

    df_limpio = clean_catalogue(df)
    print(df_limpio)