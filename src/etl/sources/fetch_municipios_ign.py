from pathlib import Path
import zipfile, sys, re

# Añadir src al path para imports absolutos
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.etl.sources._fetch_utils import download_bytes

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
except AttributeError:
    pass

def try_extract_zip_bytes(b: bytes, out_dir: Path):
    # Try to open the bytes as a zipfile
    try:
        import io
        with zipfile.ZipFile(io.BytesIO(b)) as zf:
            zf.extractall(out_dir)
        return True
    except zipfile.BadZipFile:
        return False

def find_zip_in_html(text: str) -> str | None:
    # search for href="...zip" patterns
    m = re.search(r'href\s*=\s*"([^"]+\.zip)"', text, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    m2 = re.search(r"(https?://[^\s<>]+\.zip)", text, flags=re.IGNORECASE)
    if m2:
        return m2.group(1)
    return None

def main():
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "data_raw" / "geo"
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_urls = [
        "https://centrodedescargas.cnig.es/CentroDescargas/downloadFile.do?file=/RCM/RECINTOS_MUNICIPALES_INSP/recintos_municipales_inspire_peninbal_etrs89.zip",
        "https://centrodedescargas.cnig.es/CentroDescargas/downloadFile.do?file=/RCM/RECINTOS_MUNICIPALES_INSP/RECINTOS_MUNICIPALES_INSP.zip",
        "https://ftpgeodesia.ign.es/RCM/recintos_municipales_inspire_peninbal_etrs89.zip",
        "ftp://ftpgeodesia.ign.es/RCM/recintos_municipales_inspire_peninbal_etrs89.zip",
    ]

    for url in candidate_urls:
        try:
            print(f"⬇️ Intentando {url}")
            b = download_bytes(url, timeout=60)
            # If bytes look like a zip, extract
            if try_extract_zip_bytes(b, out_dir):
                print(f"✅ Extraído correctamente desde {url}")
                return
            # If not a zip, maybe it's an HTML page pointing to a true ZIP
            text = b.decode("utf-8", errors="ignore")
            zip_link = find_zip_in_html(text)
            if zip_link:
                print(f"ℹ️ Encontrado link a ZIP en HTML: {zip_link}")
                try:
                    b2 = download_bytes(zip_link, timeout=60)
                    if try_extract_zip_bytes(b2, out_dir):
                        print(f"✅ Extraído correctamente desde {zip_link}")
                        return
                except Exception as e:
                    print(f"⚠️ Error descargando zip encontrado: {e}")
            else:
                print("⚠️ Respuesta no es ZIP y no encontré link a ZIP en HTML")
        except Exception as e:
            print(f"⚠️ Error con {url}: {e}")

    print("❌ No se pudo obtener el shapefile de municipios desde ninguna fuente automática.")
    print("Prueba a descargarlo manualmente desde https://centrodedescargas.cnig.es/CentroDescargas/resultados-busqueda y extraer en data_raw/geo/")

if __name__ == "__main__":
    main()
