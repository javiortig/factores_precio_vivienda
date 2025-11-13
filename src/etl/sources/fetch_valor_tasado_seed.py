import pandas as pd, os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

os.makedirs("data_raw/mivau", exist_ok=True)
# CSV consolidado público con valor tasado municipal (municipios >=25k habitantes)
url = "https://www.icane.es/data/api/precio-vivienda-libre-municipios-tasaciones.csv"
df = pd.read_csv(url, sep=";", dtype=str)
# Renombra a un esquema fijo
df = df.rename(columns={
    "codigo_municipio":"municipio_id",
    "municipio":"municipio",
    "periodo":"date",
    "valor_tasado_vivienda_libre":"price_eur_m2",
    "numero_tasaciones":"tasaciones"
})
df.to_csv("data_raw/mivau/valor_tasado_seed.csv", index=False)
print("✅ data_raw/mivau/valor_tasado_seed.csv")
