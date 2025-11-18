import pandas as pd, os, sys
from pathlib import Path

# Añadir src al path para imports absolutos
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes, read_csv_auto_from_bytes

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except AttributeError:
    pass

os.makedirs("data_raw/mivau", exist_ok=True)
# CSV consolidado público con valor tasado municipal (municipios >=25k habitantes)
urls = [
    "https://www.icane.es/data/api/precio-vivienda-libre-municipios-tasaciones.csv",
]

df = None
for url in urls:
    try:
        print(f"⬇️ Intentando {url}")
        b = download_bytes(url, timeout=30)
        df = read_csv_auto_from_bytes(b)
        print(f"ℹ️ Leído {len(df):,} filas desde {url}")
        break
    except Exception as e:
        print(f"⚠️ Error leyendo {url}: {e}")

if df is None:
    raise RuntimeError("No se pudo descargar ni parsear el CSV de MIVAU. Revisar URL/Conexión.")

# Renombra a un esquema fijo si las columnas existen
cols = {c.strip().lower(): c for c in df.columns}
renames = {}
mapping = {
    "codigo_municipio": "municipio_id",
    "municipio": "municipio",
    "periodo": "date",
    "valor_tasado_vivienda_libre": "price_eur_m2",
    "numero_tasaciones": "tasaciones",
}
for k, v in mapping.items():
    if k in cols:
        renames[cols[k]] = v

if renames:
    df = df.rename(columns=renames)

out_path = "data_raw/mivau/valor_tasado_seed.csv"
df.to_csv(out_path, index=False)
print(f"✅ Guardado -> {out_path}")
