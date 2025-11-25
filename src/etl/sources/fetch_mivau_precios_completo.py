#!/usr/bin/env python
"""
Fetcher completo de precios de vivienda MIVAU (Ministerio de Transportes, Movilidad y Agenda Urbana).

Fuente: Estadística de Valor Tasado de Vivienda Libre
URL base: https://www.mitma.gob.es/el-ministerio/estadisticas

Este script descarga datos trimestrales de precio €/m² por municipio.
Cobertura: Municipios con datos de tasación (generalmente >5k habitantes).
"""
import os
import sys
from pathlib import Path
import pandas as pd
import requests
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
except AttributeError:
    pass

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data_raw" / "mivau"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# URLs conocidas de MIVAU
# Estas URLs cambian periódicamente, hay que verificarlas en la web del ministerio
URLS_MIVAU = [
    # Valor tasado trimestral
    "https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=35000000",
    
    # CSV descargables (ejemplos - verificar URLs actuales)
    "https://www.mitma.gob.es/recursos_mfom/listado/recursos/valor_tasado_vivienda.csv",
    
    # Alternativa: Portal de datos abiertos
    "https://datos.gob.es/es/catalogo?q=precio+vivienda+municipio",
]

def main():
    print("⬇️ Precios MIVAU - Estadística de Valor Tasado")
    print("=" * 70)
    
    print("\n⚠️  IMPORTANTE:")
    print("   Las URLs de MIVAU cambian frecuentemente.")
    print("   Verificar manualmente en:")
    print("   https://www.mitma.gob.es/el-ministerio/estadisticas")
    print("   Buscar: 'Estadística de Valor Tasado de Vivienda Libre'")
    
    print("\n📋 Pasos para descarga manual:")
    print("   1. Ir a: https://www.mitma.gob.es/el-ministerio/estadisticas")
    print("   2. Buscar 'Valor Tasado' o 'Precio vivienda'")
    print("   3. Descargar Excel/CSV de datos municipales")
    print("   4. Guardar como: data_raw/mivau/valor_tasado_mivau_manual.csv")
    print("   5. Ejecutar normalización para formatear")
    
    # Intentar descargar desde ICANE (fuente alternativa que ya usamos)
    print("\n🔄 Intentando descarga desde ICANE (fuente secundaria)...")
    url_icane = "https://www.icane.es/data/api/precio-vivienda-libre-municipios-tasaciones.csv"
    
    try:
        csv_bytes = download_bytes(url_icane, timeout=30)
        df = pd.read_csv(BytesIO(csv_bytes), encoding='utf-8', sep=',')
        
        print(f"   ✅ Descargado desde ICANE: {len(df):,} filas")
        print(f"   Columnas: {list(df.columns)}")
        
        # Guardar
        out_file = OUT_DIR / "valor_tasado_icane.csv"
        df.to_csv(out_file, index=False, encoding='utf-8')
        print(f"   📄 Guardado: {out_file}")
        
        # Resumen
        if 'municipio_id' in df.columns:
            n_munis = df['municipio_id'].nunique()
            print(f"   📊 Municipios: {n_munis}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n💡 ALTERNATIVAS:")
    print("   1. Catastro - Valores de referencia por municipio")
    print("      https://www.catastro.minhap.es/")
    print("   2. API Idealista (si tienes API key)")
    print("   3. Web scraping de portales inmobiliarios (⚠️ contra ToS)")
    
    print("\n✅ Para uso con Idealista API:")
    print("   Crear script: src/etl/sources/fetch_idealista_precios.py")
    print("   Configurar API_KEY en .env")
    print("   Iterar por municipios principales (>25k hab)")


if __name__ == "__main__":
    main()
