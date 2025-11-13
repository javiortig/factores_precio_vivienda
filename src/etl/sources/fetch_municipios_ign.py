from pathlib import Path
import requests, zipfile, urllib.request, sys, io

sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

def download_http(url, out_path):
    print(f"⬇️ HTTP -> {url}")
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

def download_ftp(url, out_path):
    print(f"⬇️ FTP -> {url}")
    with urllib.request.urlopen(url) as response, open(out_path, "wb") as out_file:
        out_file.write(response.read())
    return out_path

def main():
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "data_raw" / "geo"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_zip = out_dir / "recintos_municipales.zip"

    urls = [
        # Portal HTTP (a veces HTML)
        "https://centrodedescargas.cnig.es/CentroDescargas/downloadFile.do?file=/RCM/RECINTOS_MUNICIPALES_INSP/recintos_municipales_inspire_peninbal_etrs89.zip",
        # Mirror FTP (sin SSL)
        "ftp://ftpgeodesia.ign.es/RCM/recintos_municipales_inspire_peninbal_etrs89.zip",
    ]

    for url in urls:
        try:
            if url.startswith("ftp://"):
                path = download_ftp(url, out_zip)
            else:
                path = download_http(url, out_zip)

            with zipfile.ZipFile(path, "r") as zf:
                zf.extractall(out_dir)
            print(f"✅ Extraído correctamente desde {url}")
            return
        except zipfile.BadZipFile:
            print(f"⚠️ {url} no es un ZIP válido, probando siguiente fuente…")
        except Exception as e:
            print(f"⚠️ Error con {url}: {e}")

    print("❌ No se pudo obtener el shapefile de municipios desde ninguna fuente.")
    print ("Prueba a descargarlo manualmente desde https://centrodedescargas.cnig.es/CentroDescargas/resultados-busqueda")

if __name__ == "__main__":
    main()
