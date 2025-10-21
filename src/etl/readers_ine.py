from __future__ import annotations
import pandas as pd, requests

def download_ipv_ccaa_csv(url: str, out_csv_path) -> None:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(out_csv_path, "wb") as f: f.write(r.content)
    print(f"✅ Descargado IPV CCAA a {out_csv_path}")

def normalize_ipv_ccaa(csv_path: str) -> pd.DataFrame:
    # El CSV de INE JAXI suele venir con separador ';'
    df = pd.read_csv(csv_path, sep=';')
    # Campos típicos: 'Periodo', 'Comunidades y Ciudades Autónomas', 'Índice', 'Tipo de vivienda', 'Valor'
    # Nos quedamos con el índice general
    if "Periodo" not in df.columns or "Valor" not in df.columns:
        raise ValueError("Estructura inesperada en CSV del INE (falta 'Periodo' o 'Valor').")
    df["date"] = pd.PeriodIndex(df["Periodo"].astype(str).str.replace("T", "Q"), freq="Q")
    out = df.rename(columns={"Comunidades y Ciudades Autónomas":"scope","Valor":"index_value"})
    return out[["scope","date","index_value"]].dropna().reset_index(drop=True)
