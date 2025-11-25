#!/usr/bin/env python
"""
Normaliza los datos de valor tasado de vivienda de MIVAU.

INPUT:
  data_raw/mivau/valor_tasado_municipios_25000.XLS
  - 83 pestañas (T1A2005 a T3A2025) con datos trimestrales
  - Cada pestaña contiene tabla con cabeceras en filas 14-16
  - Columnas: Provincia, Municipio, Valor tasado (3 cols), Número tasaciones (3 cols)

OUTPUT:
  data/curated/mivau_valor_tasado_normalizado.csv
  - Columnas: municipio, provincia, periodo, valor_tasado_total_medio, numero_tasaciones_total
  - Un registro por municipio-periodo
  - Periodo formato: YYYY-QX (ej: 2020-Q1)

AUTOR: Script generado automáticamente
FECHA: 2025-11-25
"""
import pandas as pd
import numpy as np
from pathlib import Path
import re

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "data_raw" / "mivau" / "valor_tasado_municipios_25000.XLS"
OUTPUT_FILE = PROJECT_ROOT / "data" / "curated" / "mivau_valor_tasado_normalizado.csv"

print("=" * 70)
print("NORMALIZACIÓN MIVAU - VALOR TASADO DE VIVIENDA")
print("=" * 70)

# Verificar que existe el archivo de entrada
if not INPUT_FILE.exists():
    print(f"\n❌ ERROR: Archivo no encontrado: {INPUT_FILE}")
    exit(1)

print(f"\n📂 Archivo de entrada: {INPUT_FILE}")
print(f"📂 Archivo de salida: {OUTPUT_FILE}")

# Leer todas las pestañas
print("\n1️⃣ Leyendo pestañas del archivo Excel...")
xl = pd.ExcelFile(INPUT_FILE)
print(f"   Total pestañas encontradas: {len(xl.sheet_names)}")

# Lista para acumular todos los datos normalizados
all_data = []

# Procesar cada pestaña
print("\n2️⃣ Procesando pestañas...")
for i, sheet_name in enumerate(xl.sheet_names, 1):
    # Extraer periodo de nombre de pestaña: T1A2005 -> 2005-Q1
    # Nota: algunos nombres tienen espacios al final (ej: "T1A2007 ")
    match = re.match(r'T(\d)A(\d{4})', sheet_name.strip())
    if not match:
        print(f"   ⚠️  Saltando pestaña con formato desconocido: {sheet_name}")
        continue
    
    trimestre = match.group(1)
    año = match.group(2)
    periodo = f"{año}-Q{trimestre}"
    
    # Leer pestaña sin headers (los extraeremos manualmente)
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name=sheet_name, header=None)
    except Exception as e:
        print(f"   ❌ Error leyendo {sheet_name}: {e}")
        continue
    
    # Buscar la fila con "Provincia" y "Municipio" (normalmente fila 14 o 16)
    header_row_idx = None
    for idx, row in df.iterrows():
        if pd.notna(row[1]) and pd.notna(row[2]):
            row_str = str(row[1]) + str(row[2])
            if 'Provincia' in row_str and 'Municipi' in row_str:
                header_row_idx = idx
                break
    
    if header_row_idx is None:
        print(f"   ⚠️  No se encontró header en {sheet_name}, saltando...")
        continue
    
    # Verificar si es formato antiguo (6 columnas) o nuevo (10 columnas)
    num_cols = len(df.columns)
    
    if num_cols == 6:
        # Formato antiguo (2005-2009): columnas simplificadas
        # 1=Provincia, 2=Municipio, 3=Valor Total, 5=Tasaciones Total
        data_start_idx = header_row_idx + 2  # Solo 1 fila de subheader
        df_data = df.iloc[data_start_idx:].copy()
        
        if len(df_data.columns) < 6:
            print(f"   ⚠️  {sheet_name.strip()} tiene columnas insuficientes, saltando...")
            continue
        
        df_data = df_data[[1, 2, 3, 5]].copy()
        df_data.columns = ['provincia', 'municipio', 'valor_tasado_total_medio', 'numero_tasaciones_total']
        
    elif num_cols == 10:
        # Formato nuevo (2010+): columnas detalladas
        # 1=Provincia, 2=Municipio, 5=Valor Total, 9=Tasaciones Total
        data_start_idx = header_row_idx + 3  # 2 filas de subheaders
        df_data = df.iloc[data_start_idx:].copy()
        
        df_data = df_data[[1, 2, 5, 9]].copy()
        df_data.columns = ['provincia', 'municipio', 'valor_tasado_total_medio', 'numero_tasaciones_total']
    else:
        print(f"   ⚠️  {sheet_name.strip()} tiene formato desconocido ({num_cols} columnas), saltando...")
        continue
    
    # Limpiar: eliminar filas completamente vacías
    df_data = df_data.dropna(how='all')
    
    # Rellenar provincia hacia abajo (forward fill) - solo aparece en primera fila de cada provincia
    df_data['provincia'] = df_data['provincia'].ffill()
    
    # Eliminar filas sin municipio
    df_data = df_data.dropna(subset=['municipio'])
    
    # Agregar columna de periodo
    df_data['periodo'] = periodo
    
    # Convertir valores numéricos (pueden estar como string o tener "n.r" = no registrado)
    df_data['valor_tasado_total_medio'] = pd.to_numeric(
        df_data['valor_tasado_total_medio'], 
        errors='coerce'
    )
    df_data['numero_tasaciones_total'] = pd.to_numeric(
        df_data['numero_tasaciones_total'], 
        errors='coerce'
    )
    
    # Reordenar columnas
    df_data = df_data[['municipio', 'provincia', 'periodo', 
                       'valor_tasado_total_medio', 'numero_tasaciones_total']]
    
    # Agregar a lista
    all_data.append(df_data)
    
    if i % 10 == 0:
        print(f"   Procesadas {i}/{len(xl.sheet_names)} pestañas...")

print(f"   ✅ {len(all_data)} pestañas procesadas correctamente")

# Concatenar todos los datos
print("\n3️⃣ Consolidando datos...")
df_final = pd.concat(all_data, ignore_index=True)

print(f"   Total registros: {len(df_final):,}")
print(f"   Municipios únicos: {df_final['municipio'].nunique()}")
print(f"   Provincias únicas: {df_final['provincia'].nunique()}")
print(f"   Periodos únicos: {df_final['periodo'].nunique()}")

# Estadísticas
print("\n4️⃣ Estadísticas de los datos:")
print(f"   Rango temporal: {df_final['periodo'].min()} - {df_final['periodo'].max()}")
print(f"   Valores nulos en valor_tasado: {df_final['valor_tasado_total_medio'].isna().sum():,} ({df_final['valor_tasado_total_medio'].isna().sum()/len(df_final)*100:.1f}%)")
print(f"   Valores nulos en numero_tasaciones: {df_final['numero_tasaciones_total'].isna().sum():,} ({df_final['numero_tasaciones_total'].isna().sum()/len(df_final)*100:.1f}%)")

# Mostrar resumen estadístico
print("\n   Resumen valor tasado (€/m²):")
print(df_final['valor_tasado_total_medio'].describe().to_string())

# Guardar resultado
print("\n5️⃣ Guardando archivo normalizado...")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
print(f"   ✅ Archivo guardado: {OUTPUT_FILE}")

# Mostrar muestra de datos
print("\n6️⃣ Muestra de datos normalizados (primeras 10 filas):")
print(df_final.head(10).to_string(index=False))

print("\n" + "=" * 70)
print("✅ NORMALIZACIÓN COMPLETADA")
print("=" * 70)
