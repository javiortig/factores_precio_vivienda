# src/etl/sources/fetch_ine_adrh_all.py
from __future__ import annotations
from pathlib import Path
import requests, pandas as pd, sys, time, unicodedata

# Añadir src al path para imports absolutos
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes, read_csv_auto_from_bytes

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
except AttributeError:
    pass

# Tabla correcta para MUNICIPIOS (ADRH): 31277
API_JSON = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/31277?tip=AM"
CSV_SC   = "https://www.ine.es/jaxiT3/files/t/csv_bdsc/31277.csv"  # ; separado
CSV_TSV  = "https://www.ine.es/jaxiT3/files/t/csv_bd/31277.csv"    # \t separado

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data_raw" / "ine"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_RAW = OUT_DIR / "adrh_all_raw.csv"
OUT     = OUT_DIR / "adrh_all.csv"

def norm_txt(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).strip().lower()

def fetch_json(url: str):
    for _ in range(2):
        r = requests.get(url, timeout=180)
        if r.ok:
            return r.json()
        time.sleep(1)
    r.raise_for_status()
    return []

def json_to_df(rows: list[dict]) -> pd.DataFrame:
    recs = []
    for it in rows:
        # Usar T3_Variable como clave, extraer nombre y código
        meta = {}
        for d in it.get("MetaData", []):
            var_name = d.get("T3_Variable", "")
            meta[var_name] = {
                "nombre": d.get("Nombre", ""),
                "codigo": d.get("Codigo", "")
            }
        
        # Obtener municipio e indicador
        muni_nombre = meta.get("Municipios", {}).get("nombre", "")
        muni_codigo = meta.get("Municipios", {}).get("codigo", "")
        indic_nombre = meta.get("Indicadores de renta media y mediana", {}).get("nombre", "")
        
        # Usar código como identificador principal (más robusto)
        municipio = muni_codigo or muni_nombre
        
        for d in it.get("Data", []):
            recs.append({
                "municipio": municipio,
                "indicador": indic_nombre,
                "periodo": d.get("Fecha"),
                "valor": d.get("Valor"),
            })
    return pd.DataFrame.from_records(recs)

def read_csv_auto(url: str) -> pd.DataFrame:
    try:
        return pd.read_csv(url, sep=";", dtype=str, encoding="utf-8")
    except Exception:
        return pd.read_csv(url, sep="\t", dtype=str, encoding="utf-8")

def main():
    print(f"⬇️ ADRH (municipios) - Iterando por provincias...")
    
    # Lista de códigos de provincia (01-52)
    provincias = [f"{i:02d}" for i in range(1, 53)]
    
    all_recs = []
    provincias_ok = 0
    provincias_fail = 0
    
    for prov in provincias:
        # URL con filtro de provincia usando operación de filtro
        # No existe un parámetro directo, así que iteramos tabla completa
        # y filtramos localmente (más lento pero funcional)
        pass
    
    # Como la API no permite filtrar por provincia, usamos CSV completo
    print(f"   Intentando CSV completo (más lento pero completo)...")
    
    try:
        # Intentar con CSV semicolon
        df = pd.read_csv(CSV_SC, sep=";", dtype=str, encoding="ISO-8859-1", on_bad_lines="skip")
        print(f"   ✅ CSV descargado: {len(df):,} filas")
    except Exception as e:
        print(f"   ⚠️  CSV semicolon falló ({e}), pruebo TSV...")
        try:
            df = pd.read_csv(CSV_TSV, sep="\t", dtype=str, encoding="ISO-8859-1", on_bad_lines="skip")
            print(f"   ✅ CSV descargado: {len(df):,} filas")
        except Exception as e2:
            print(f"   ❌ Ambos CSVs fallaron")
            raise RuntimeError(f"No se pudo descargar ADRH: {e2}")
    
    # Mostrar columnas para debug
    print(f"   Columnas: {list(df.columns[:10])}")
    
    # Normalizar nombres de columnas
    cols_norm = {norm_txt(c): c for c in df.columns}
    
    # Buscar columnas clave
    c_muni = None
    c_ind = None
    c_per = None
    c_val = None
    
    for k, v in cols_norm.items():
        if "municipio" in k:
            c_muni = v
        elif "indicador" in k or "renta" in k:
            c_ind = v
        elif "periodo" in k or "año" in k or "ano" in k:
            c_per = v
        elif k in ("total", "valor", "value"):
            c_val = v
    
    if not all([c_muni, c_per, c_val]):
        print(f"   ❌ No encuentro columnas clave.")
        print(f"      Municipio: {c_muni}, Indicador: {c_ind}, Periodo: {c_per}, Valor: {c_val}")
        raise RuntimeError(f"Columnas no encontradas en CSV")
    
    # Renombrar
    rename_map = {c_muni: "municipio", c_per: "periodo", c_val: "valor"}
    if c_ind:
        rename_map[c_ind] = "indicador"
    
    df = df.rename(columns=rename_map)
    
    # Si no hay columna indicador, crear una genérica
    if "indicador" not in df.columns:
        df["indicador"] = "Renta media"
    
    # Limpiar
    df["valor"] = pd.to_numeric(df["valor"].str.replace(",", "."), errors="coerce")
    df = df.dropna(subset=["valor", "municipio"])
    
    # Guardar RAW
    df[["municipio", "indicador", "periodo", "valor"]].to_csv(OUT_RAW, index=False)
    print(f"🧾 RAW ADRH: {OUT_RAW} ({len(df):,} filas, {df['municipio'].nunique()} municipios)")
    
    # Versión simplificada
    out = df[["municipio", "periodo", "valor"]].copy()
    out.to_csv(OUT, index=False)
    print(f"✅ ADRH: {OUT} ({len(out):,} filas)")

if __name__ == "__main__":
    main()
