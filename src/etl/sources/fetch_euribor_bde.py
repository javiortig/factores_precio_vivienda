# src/etl/sources/fetch_euribor_bde.py
from pathlib import Path
import requests

RAW = Path("data_raw/macro"); RAW.mkdir(parents=True, exist_ok=True)
OUT = RAW / "ti_1_7.csv"

URL = "https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv"

def main():
    print(f"⬇️ Descargando Euríbor (BdE) -> {OUT}")
    r = requests.get(URL, timeout=90)
    r.raise_for_status()
    if not r.content or len(r.content) < 1000:
        raise RuntimeError("Respuesta demasiado pequeña: ¿cambió el recurso del BdE?")
    OUT.write_bytes(r.content)
    print(f"✅ Guardado: {OUT}")

if __name__ == "__main__":
    main()
