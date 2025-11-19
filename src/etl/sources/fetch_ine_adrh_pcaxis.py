# src/etl/sources/fetch_ine_adrh_pcaxis.py
"""
Descarga ADRH completo en formato PC-Axis (.px) y convierte a CSV.

El formato PC-Axis es el único que el INE proporciona con datos completos
de todos los municipios de España. Las APIs REST y CSVs están pre-filtrados.

Requiere: pip install pyaxis
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
except AttributeError:
    pass

# URL del archivo PC-Axis completo de ADRH
# Fuente: https://www.ine.es/jaxiT3/Tabla.htm?t=31277
PX_URL = "https://www.ine.es/jaxiT3/files/t/px/31277.px"

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data_raw" / "ine"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PX = OUT_DIR / "adrh_all.px"
OUT_CSV = OUT_DIR / "adrh_all_raw.csv"
OUT_AGG = OUT_DIR / "adrh_all.csv"


def main():
    print(f"⬇️ ADRH completo (formato PC-Axis)")
    
    # 1. Descargar archivo .px
    print(f"   Descargando {PX_URL}...")
    try:
        px_bytes = download_bytes(PX_URL, timeout=300, retries=3)
        OUT_PX.write_bytes(px_bytes)
        print(f"   ✅ Descargado: {OUT_PX} ({len(px_bytes):,} bytes)")
    except Exception as e:
        print(f"   ❌ Error descargando: {e}")
        raise
    
    # 2. Convertir .px a DataFrame
    print(f"   Convirtiendo PC-Axis a CSV...")
    try:
        import pyaxis
        px = pyaxis.parse(str(OUT_PX), encoding='ISO-8859-15')
        df = px['DATA']
        print(f"   ✅ Convertido: {len(df):,} filas")
    except ImportError:
        print(f"\n   ❌ ERROR: pyaxis no está instalado")
        print(f"   ℹ️  Instala con: pip install pyaxis")
        print(f"   ℹ️  El archivo .px se descargó correctamente en: {OUT_PX}")
        print(f"   ℹ️  Puedes convertirlo manualmente después de instalar pyaxis")
        return
    except Exception as e:
        print(f"   ❌ Error convirtiendo: {e}")
        raise
    
    # 3. Procesar y guardar
    print(f"   Procesando datos...")
    
    # Normalizar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Identificar columnas relevantes
    # El formato varía, pero generalmente: municipios, indicadores, periodo, valor
    col_municipio = next((c for c in df.columns if 'municipio' in c), None)
    col_indicador = next((c for c in df.columns if 'indicador' in c or 'renta' in c), None)
    col_periodo = next((c for c in df.columns if 'periodo' in c or 'año' in c), None)
    col_valor = next((c for c in df.columns if c in ['valor', 'total', 'data']), None)
    
    if not col_municipio:
        print(f"   ⚠️  No se encontró columna de municipio. Columnas: {list(df.columns)}")
        # Guardar tal cual para inspección manual
        df.to_csv(OUT_CSV, index=False)
        print(f"   ℹ️  Datos guardados sin procesar: {OUT_CSV}")
        return
    
    # Renombrar columnas
    rename_map = {col_municipio: 'municipio'}
    if col_indicador:
        rename_map[col_indicador] = 'indicador'
    if col_periodo:
        rename_map[col_periodo] = 'periodo'
    if col_valor:
        rename_map[col_valor] = 'valor'
    
    df = df.rename(columns=rename_map)
    
    # Agregar columna indicador si no existe
    if 'indicador' not in df.columns:
        df['indicador'] = 'Renta media'
    
    # Limpiar y convertir valor
    if 'valor' in df.columns:
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        df = df.dropna(subset=['valor'])
    
    # Guardar RAW
    cols_out = ['municipio', 'indicador', 'periodo', 'valor']
    cols_out = [c for c in cols_out if c in df.columns]
    df[cols_out].to_csv(OUT_CSV, index=False)
    
    n_munis = df['municipio'].nunique() if 'municipio' in df.columns else 0
    print(f"🧾 RAW: {OUT_CSV} ({len(df):,} filas, {n_munis} municipios)")
    
    # Guardar agregado (si tiene las columnas necesarias)
    if all(c in df.columns for c in ['municipio', 'periodo', 'valor']):
        agg = df[['municipio', 'periodo', 'valor']].copy()
        agg.to_csv(OUT_AGG, index=False)
        print(f"✅ Agregado: {OUT_AGG} ({len(agg):,} filas)")
    else:
        print(f"   ⚠️  No se pudo crear agregado (faltan columnas)")


if __name__ == "__main__":
    main()
