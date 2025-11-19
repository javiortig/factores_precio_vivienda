#!/usr/bin/env python
"""
Descarga Padrón municipal iterando por las 52 provincias españolas.

Fuente: https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225
Cada provincia tiene su propia tabla con todos sus municipios.

Estrategia:
1. Mapear código provincia → tabla INE
2. Para cada provincia, descargar CSV desde endpoint de descarga
3. Consolidar todos los CSVs en un único archivo
"""
import os
import sys
from pathlib import Path
import pandas as pd
import requests
import time
from io import StringIO

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes, read_csv_auto_from_bytes

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
except AttributeError:
    pass

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data_raw" / "ine"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_RAW = OUT_DIR / "padron_all_raw.csv"
OUT_AGG = OUT_DIR / "padron_all.csv"

# Mapeo provincia → código de tabla INE
# Verificados manualmente desde: https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225
# Códigos confirmados:
# - Albacete (02): 33582 ✓
# - Madrid (28): 33847 ✓
# Los demás se intentan calcular o necesitan verificación manual
PROVINCIAS_TABLAS = {
    "01": {"nombre": "Álava/Araba", "tabla": "33589"},  # ✓ Funcionó
    "02": {"nombre": "Albacete", "tabla": "33582"},  # ✓ Confirmado
    "03": {"nombre": "Alicante/Alacant", "tabla": None},  # Buscar
    "04": {"nombre": "Almería", "tabla": "33584"},  # ✓ Funcionó
    "05": {"nombre": "Ávila", "tabla": None},
    "06": {"nombre": "Badajoz", "tabla": None},
    "07": {"nombre": "Balears, Illes", "tabla": "33587"},  # ✓ Funcionó
    "08": {"nombre": "Barcelona", "tabla": "33588"},  # ✓ Funcionó
    "09": {"nombre": "Burgos", "tabla": "33590"},  # ✓ Funcionó
    "10": {"nombre": "Cáceres", "tabla": "33591"},  # ✓ Funcionó
    "11": {"nombre": "Cádiz", "tabla": None},
    "12": {"nombre": "Castellón/Castelló", "tabla": None},
    "13": {"nombre": "Ciudad Real", "tabla": None},
    "14": {"nombre": "Córdoba", "tabla": None},
    "15": {"nombre": "Coruña, A", "tabla": None},
    "16": {"nombre": "Cuenca", "tabla": "33597"},  # ✓ Funcionó
    "17": {"nombre": "Girona", "tabla": None},
    "18": {"nombre": "Granada", "tabla": None},
    "19": {"nombre": "Guadalajara", "tabla": None},
    "20": {"nombre": "Gipuzkoa", "tabla": None},
    "21": {"nombre": "Huelva", "tabla": None},
    "22": {"nombre": "Huesca", "tabla": None},
    "23": {"nombre": "Jaén", "tabla": None},
    "24": {"nombre": "León", "tabla": None},
    "25": {"nombre": "Lleida", "tabla": None},
    "26": {"nombre": "Rioja, La", "tabla": None},
    "27": {"nombre": "Lugo", "tabla": None},
    "28": {"nombre": "Madrid", "tabla": "33847"},  # ✓ Confirmado
    "29": {"nombre": "Málaga", "tabla": None},
    "30": {"nombre": "Murcia", "tabla": None},
    "31": {"nombre": "Navarra", "tabla": None},
    "32": {"nombre": "Ourense", "tabla": None},
    "33": {"nombre": "Asturias", "tabla": None},
    "34": {"nombre": "Palencia", "tabla": None},
    "35": {"nombre": "Palmas, Las", "tabla": None},
    "36": {"nombre": "Pontevedra", "tabla": None},
    "37": {"nombre": "Salamanca", "tabla": None},
    "38": {"nombre": "Santa Cruz de Tenerife", "tabla": None},
    "39": {"nombre": "Cantabria", "tabla": None},
    "40": {"nombre": "Segovia", "tabla": None},
    "41": {"nombre": "Sevilla", "tabla": None},
    "42": {"nombre": "Soria", "tabla": None},
    "43": {"nombre": "Tarragona", "tabla": None},
    "44": {"nombre": "Teruel", "tabla": None},
    "45": {"nombre": "Toledo", "tabla": "33626"},  # ✓ Funcionó
    "46": {"nombre": "Valencia/València", "tabla": "33627"},  # ✓ Funcionó
    "47": {"nombre": "Valladolid", "tabla": "33628"},  # ✓ Funcionó
    "48": {"nombre": "Bizkaia", "tabla": "33629"},  # ✓ Funcionó
    "49": {"nombre": "Zamora", "tabla": None},
    "50": {"nombre": "Zaragoza", "tabla": None},
    "51": {"nombre": "Ceuta", "tabla": None},
    "52": {"nombre": "Melilla", "tabla": None},
}


def descargar_provincia_csv(codigo_tabla: str, provincia_nombre: str) -> pd.DataFrame:
    """
    Descarga el CSV de una provincia desde el endpoint de exportación del INE.
    
    URL patrón: https://www.ine.es/jaxiT3/dlgExport.htm?t={tabla}&L=0&nocab=1
    Formato: CSV separado por punto y coma (;)
    """
    # URL del diálogo de exportación
    url = f"https://www.ine.es/jaxiT3/dlgExport.htm?t={codigo_tabla}&L=0&nocab=1"
    
    # El enlace de descarga directa del CSV está en:
    # https://www.ine.es/jaxiT3/files/t/csv_bdsc/{codigo_tabla}.csv
    url_csv = f"https://www.ine.es/jaxiT3/files/t/csv_bdsc/{codigo_tabla}.csv"
    
    try:
        csv_bytes = download_bytes(url_csv, timeout=60, retries=3)
        df = read_csv_auto_from_bytes(csv_bytes)
        return df
    except Exception as e:
        print(f"      ❌ Error: {e}")
        raise


def normalizar_padron_df(df: pd.DataFrame, codigo_prov: str) -> pd.DataFrame:
    """
    Normaliza el DataFrame del Padrón a formato estándar:
    - municipio_codigo (5 dígitos INE)
    - municipio (nombre)
    - periodo (fecha ISO)
    - valor (población)
    """
    # Los CSVs del INE vienen con estructura variable
    # Típicamente: "Municipios", "Periodo", "Total"
    
    # Normalizar nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]
    
    # Detectar columnas clave
    col_municipio = None
    col_periodo = None
    col_valor = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'municipio' in col_lower:
            col_municipio = col
        elif 'periodo' in col_lower or 'año' in col_lower or any(str(year) in col for year in range(2000, 2030)):
            col_periodo = col
        elif 'total' in col_lower or 'valor' in col_lower or 'población' in col_lower:
            col_valor = col
    
    if not col_municipio:
        # Si no hay columna de municipio, intentar detectar por índice
        # Muchas veces la primera columna es el municipio
        col_municipio = df.columns[0]
    
    # Crear DataFrame normalizado
    resultado = []
    
    # Si el formato es wide (periodos como columnas)
    if col_periodo is None:
        # Buscar columnas que parezcan años
        cols_periodo = [c for c in df.columns if c.isdigit() or any(str(year) in str(c) for year in range(2000, 2030))]
        
        if cols_periodo:
            for _, row in df.iterrows():
                municipio = str(row[col_municipio]).strip()
                
                for periodo_col in cols_periodo:
                    valor = row[periodo_col]
                    
                    # Extraer año del nombre de columna
                    periodo = ''.join(c for c in str(periodo_col) if c.isdigit())
                    
                    if pd.notna(valor) and valor != '':
                        resultado.append({
                            'municipio': municipio,
                            'periodo': periodo,
                            'valor': valor
                        })
    else:
        # Formato long (una columna periodo)
        for _, row in df.iterrows():
            municipio = str(row[col_municipio]).strip()
            periodo = str(row[col_periodo]).strip() if col_periodo else ''
            valor = row[col_valor] if col_valor else ''
            
            if pd.notna(valor) and valor != '':
                resultado.append({
                    'municipio': municipio,
                    'periodo': periodo,
                    'valor': valor
                })
    
    df_norm = pd.DataFrame(resultado)
    
    # Añadir código de municipio (extraído del nombre si está en formato "99999 NombreMunicipio")
    # O generado a partir del código de provincia
    if 'municipio_codigo' not in df_norm.columns:
        def extraer_codigo(nombre):
            # Intentar extraer código del formato "99999 Nombre"
            partes = str(nombre).split()
            if partes and partes[0].isdigit() and len(partes[0]) == 5:
                return partes[0]
            return None
        
        df_norm['municipio_codigo'] = df_norm['municipio'].apply(extraer_codigo)
    
    # Limpiar nombres de municipio (quitar código si estaba incluido)
    df_norm['municipio'] = df_norm['municipio'].str.replace(r'^\d{5}\s+', '', regex=True)
    
    # Convertir valor a numérico
    df_norm['valor'] = pd.to_numeric(df_norm['valor'], errors='coerce')
    df_norm = df_norm.dropna(subset=['valor'])
    
    return df_norm


def main():
    print("⬇️ Padrón Municipal - Descarga por provincias")
    print("=" * 70)
    print(f"   Total provincias: {len(PROVINCIAS_TABLAS)}")
    
    all_dfs = []
    provincias_ok = 0
    provincias_error = []
    provincias_pendientes = []
    
    for codigo_prov, info in PROVINCIAS_TABLAS.items():
        nombre = info["nombre"]
        tabla = info["tabla"]
        
        if tabla is None:
            provincias_pendientes.append((codigo_prov, nombre))
            continue
        
        print(f"\n📥 [{codigo_prov}] {nombre} (tabla {tabla})")
        
        try:
            df = descargar_provincia_csv(tabla, nombre)
            print(f"   ✅ Descargado: {len(df):,} filas, {len(df.columns)} columnas")
            
            # Normalizar
            df_norm = normalizar_padron_df(df, codigo_prov)
            print(f"   ✅ Normalizado: {len(df_norm):,} registros")
            
            if len(df_norm) > 0:
                all_dfs.append(df_norm)
                provincias_ok += 1
            else:
                print(f"   ⚠️  Sin datos normalizados")
                provincias_error.append((codigo_prov, nombre, "Sin datos tras normalizar"))
            
            # Rate limit: esperar 1 segundo entre peticiones
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            provincias_error.append((codigo_prov, nombre, str(e)))
            continue
    
    # Consolidar todos los DataFrames
    print("\n" + "=" * 70)
    print(f"📊 CONSOLIDACIÓN")
    print(f"   Provincias OK: {provincias_ok}/{len(PROVINCIAS_TABLAS)}")
    print(f"   Provincias pendientes: {len(provincias_pendientes)}")
    
    if provincias_error:
        print(f"\n   ⚠️  Provincias con errores ({len(provincias_error)}):")
        for cod, nom, err in provincias_error[:10]:  # Mostrar solo las primeras 10
            print(f"      [{cod}] {nom}: {err[:60]}")
        if len(provincias_error) > 10:
            print(f"      ... y {len(provincias_error) - 10} más")
    
    if provincias_pendientes:
        print(f"\n   📝 Provincias sin código de tabla ({len(provincias_pendientes)}):")
        print(f"      Requieren inspección manual de la página del INE")
        for cod, nom in provincias_pendientes[:5]:
            print(f"      [{cod}] {nom}")
        if len(provincias_pendientes) > 5:
            print(f"      ... y {len(provincias_pendientes) - 5} más")
    
    if not all_dfs:
        print("\n❌ No se pudo descargar ninguna provincia")
        return
    
    df_consolidado = pd.concat(all_dfs, ignore_index=True)
    print(f"\n   Total registros: {len(df_consolidado):,}")
    
    # Guardar RAW
    df_consolidado.to_csv(OUT_RAW, index=False, encoding='utf-8')
    print(f"   📄 RAW: {OUT_RAW}")
    
    # Agregar por municipio × periodo
    if all(c in df_consolidado.columns for c in ['municipio', 'periodo', 'valor']):
        cols_group = ['municipio_codigo', 'municipio', 'periodo'] if 'municipio_codigo' in df_consolidado.columns else ['municipio', 'periodo']
        
        df_agg = (df_consolidado
                  .groupby(cols_group, as_index=False)
                  .agg({'valor': 'sum'}))
        
        df_agg.to_csv(OUT_AGG, index=False, encoding='utf-8')
        
        n_munis = df_agg['municipio'].nunique()
        n_periodos = df_agg['periodo'].nunique()
        
        print(f"   📊 AGREGADO: {OUT_AGG}")
        print(f"      Municipios: {n_munis:,}")
        print(f"      Periodos: {n_periodos}")
        print(f"      Filas: {len(df_agg):,}")
    
    print("\n✅ COMPLETADO")


if __name__ == "__main__":
    main()
