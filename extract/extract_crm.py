import pandas as pd
from google.cloud import storage
from io import BytesIO

PROJECT_ID = "alchemialabs-tech-assessment"
BUCKET_NAME = "alchemialabs-tech-assessment"


def get_latest_file(prefix: str) -> str:
    """
    Busca en el bucket todos los archivos que empiezan con 'prefix'
    y devuelve el nombre del más reciente, asumiendo que las fechas
    en el nombre siguen el formato YYYY-MM-DD (orden alfabético = orden cronológico).
    """
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=prefix))
    nombres = [b.name for b in blobs]

    if not nombres:
        raise FileNotFoundError(f"No se encontraron archivos con prefijo '{prefix}'")

    return max(nombres)


def download_csv_as_dataframe(blob_name: str) -> pd.DataFrame:
    """
    Descarga un archivo CSV del bucket y lo carga como DataFrame de pandas,
    forzando encoding UTF-8 para evitar el problema de mojibake (Â£).
    """
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    contenido = blob.download_as_bytes()
    df = pd.read_csv(BytesIO(contenido), encoding="utf-8")

    return df


def clean_dataframe(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """
    Limpieza genérica para cualquier entidad del CRM:
    - Quita espacios en blanco al inicio/final de columnas de texto
    - Elimina duplicados según la columna ID indicada, quedándose con el primer registro
    """
    columnas_texto = df.select_dtypes(include=["object", "string"]).columns
    for col in columnas_texto:
        df[col] = df[col].str.strip()

    filas_antes = len(df)
    df = df.drop_duplicates(subset=id_column, keep="first")
    filas_despues = len(df)

    print(f"  Duplicados eliminados: {filas_antes - filas_despues}")

    return df


def extract_entity(prefix: str, id_column: str) -> pd.DataFrame:
    """
    Orquesta el proceso completo para una entidad del CRM:
    encuentra el archivo más reciente, lo descarga, y lo limpia.
    """
    latest = get_latest_file(prefix)
    print(f"\n{prefix} -> archivo más reciente: {latest}")

    df = download_csv_as_dataframe(latest)
    print(f"  Filas descargadas: {len(df)}")

    df_limpio = clean_dataframe(df, id_column)
    print(f"  Filas después de limpieza: {len(df_limpio)}")

    return df_limpio


if __name__ == "__main__":
    accounts = extract_entity("crm/crm_accounts", "account_id")
    contacts = extract_entity("crm/crm_contacts", "contact_id")
    opportunities = extract_entity("crm/crm_opportunities", "opportunity_id")

    print("\n--- Resumen final ---")
    print(f"Accounts: {len(accounts)} filas")
    print(f"Contacts: {len(contacts)} filas")
    print(f"Opportunities: {len(opportunities)} filas")