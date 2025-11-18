# src/etl/sources/fetch_euribor_bde.py
from pathlib import Path
import sys

# Añadir src al path para imports absolutos
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except AttributeError:
    pass

RAW = Path("data_raw/macro"); RAW.mkdir(parents=True, exist_ok=True)
OUT = RAW / "ti_1_7.csv"

URL = "https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv"

def main():
    print(f"⬇️ Descargando Euríbor (BdE) -> {OUT}")
    b = download_bytes(URL, timeout=60)
    if not b or len(b) < 1000:
        raise RuntimeError("Respuesta demasiado pequeña: ¿cambió el recurso del BdE?")
    OUT.write_bytes(b)
    print(f"✅ Guardado: {OUT}")

if __name__ == "__main__":
    main()
