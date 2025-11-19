#!/usr/bin/env python
"""
Descarga Padrón municipal (tabla 33775) de TODOS los municipios españoles.

❌ PROBLEMA IDENTIFICADO:
   - CSV endpoints (csv_bd, csv_bdsc): Solo devuelven 1 provincia
   - API Tempus JSON: Solo devuelve A Coruña (provincia 15), sin importar parámetros URL
   - No existe API pública que permita iterar por provincias

💡 SOLUCIÓN TEMPORAL:
   Usar los datos consolidados del INE que ya tenemos en formato agregado,
   O descargar manualmente el archivo PC-Axis completo (.px) desde la web.

Fuentes:
- Tabla interactiva: https://www.ine.es/jaxiT3/Tabla.htm?t=33775
- API Tempus (FILTRADA): https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775
"""
import os
import sys
from pathlib import Path
import pandas as pd
import requests

# Añadir src/ al path para imports absolutos
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

OUT_DIR = Path(__file__).resolve().parents[3] / "data_raw" / "ine"
OUT_RAW = OUT_DIR / "padron_all_raw.csv"
OUT_AGG = OUT_DIR / "padron_all.csv"


def main():
    print("⬇️ Padrón Municipal - Tabla 33775")
    print("=" * 70)
    
    print("\n❌ LIMITACIÓN DEL INE:")
    print("   La API Tempus JSON solo devuelve 1 provincia (A Coruña)")
    print("   Total de items con municipio: 29,070")
    print("   Municipios únicos: 95 (solo provincia 15)")
    print("   Provincias esperadas: 52")
    print("   Municipios esperados: ~8,132")
    
    print("\n📋 OPCIONES:")
    print("\n   1️⃣ DESCARGA MANUAL (Recomendado)")
    print("      a) Ir a: https://www.ine.es/jaxiT3/Tabla.htm?t=33775")
    print("      b) Clic en 'Seleccionar valores'")
    print("      c) Municipios → 'Seleccionar todos' (8,132)")
    print("      d) Descargar formato 'PC-Axis' (.px)")
    print("      e) Guardar como: data_raw/ine/padron_manual.px")
    print("      f) Instalar: pip install pyaxis")
    print("      g) Parsear con: pyaxis.parse('padron_manual.px')")
    
    print("\n   2️⃣ USAR DATOS YA DESCARGADOS")
    print("      Si ya tenemos padron_all.csv de descarga previa,")
    print("      verificar que contenga las 52 provincias.")
    
    print("\n   3️⃣ SCRAPING (No recomendado)")
    print("      Hacer 52 peticiones a la tabla interactiva filtrando")
    print("      por provincia, pero puede violar ToS del INE.")
    
    print("\n💡 MIENTRAS TANTO:")
    print("   Crearemos un archivo placeholder con los datos de A Coruña")
    print("   que ya tenemos, para no bloquear el resto del pipeline.")
    
    # Verificar si ya existe el archivo
    if OUT_AGG.exists():
        df_existing = pd.read_csv(OUT_AGG)
        n_municipios = df_existing['municipio_codigo'].nunique() if 'municipio_codigo' in df_existing.columns else 0
        n_provincias = df_existing['municipio_codigo'].str[:2].nunique() if 'municipio_codigo' in df_existing.columns else 0
        
        print(f"\n✅ Ya existe: {OUT_AGG}")
        print(f"   Municipios: {n_municipios}")
        print(f"   Provincias: {n_provincias}")
        
        if n_provincias >= 50:  # Consideramos completo si tiene al menos 50 provincias
            print("   ✅ Dataset parece completo (≥50 provincias)")
            return
        else:
            print(f"   ⚠️ Dataset incompleto (solo {n_provincias} provincias)")
    
    # Descargar datos de A Coruña como placeholder
    print("\n📥 Descargando datos parciales (A Coruña) como placeholder...")
    
    url = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775?tip=AM"
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    data = r.json()
    
    print(f"   Items recibidos: {len(data):,}")
    
    # Procesar JSON
    recs = []
    for item in data:
        meta = {d["T3_Variable"]: {
            "nombre": d.get("Nombre", ""),
            "codigo": d.get("Codigo", "")
        } for d in item.get("MetaData", [])}
        
        if "Municipios" not in meta:
            continue
        
        municipio_codigo = meta["Municipios"]["codigo"]
        municipio_nombre = meta["Municipios"]["nombre"]
        
        for d in item.get("Data", []):
            recs.append({
                "municipio_codigo": municipio_codigo,
                "municipio": municipio_nombre,
                "sexo": meta.get("Sexo", {}).get("nombre", ""),
                "edad": meta.get("Totales de edad", {}).get("nombre", ""),
                "periodo": d.get("Fecha", ""),
                "valor": d.get("Valor", ""),
            })
    
    df = pd.DataFrame.from_records(recs)
    print(f"   Registros procesados: {len(df):,}")
    
    # Guardar RAW
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_RAW, index=False, encoding="utf-8")
    print(f"   📄 RAW guardado: {OUT_RAW} ({len(df):,} filas)")
    
    # Agregar por municipio×periodo (población total)
    df_agg = (df
              .groupby(["municipio_codigo", "municipio", "periodo"], as_index=False)
              .agg({"valor": "sum"}))
    
    df_agg.to_csv(OUT_AGG, index=False, encoding="utf-8")
    print(f"   📊 AGREGADO guardado: {OUT_AGG} ({len(df_agg):,} filas)")
    
    n_munis = df_agg['municipio_codigo'].nunique()
    n_provs = df_agg['municipio_codigo'].str[:2].nunique()
    
    print(f"\n⚠️ RECORDATORIO:")
    print(f"   Este archivo solo tiene {n_munis} municipios de {n_provs} provincia(s)")
    print(f"   Para el análisis completo, se requiere descarga manual.")
    print(f"   Ver instrucciones arriba (Opción 1️⃣)")


if __name__ == "__main__":
    main()
