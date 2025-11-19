#!/usr/bin/env python
"""
Investigación PARTE 2: Cómo obtener datos usando los códigos de municipio.
"""
import requests
import json

print("=" * 70)
print("PARTE 2: Obtener datos del Padrón usando códigos de municipio")
print("=" * 70)

# 1. Obtener TODOS los municipios
print("\n1️⃣ Descargando lista completa de municipios...")
url_municipios = "https://servicios.ine.es/wstempus/js/es/VALORES_VARIABLE/Municipios"
r = requests.get(url_municipios, timeout=30)
municipios = r.json()
print(f"   ✅ Municipios descargados: {len(municipios)}")

# Analizar estructura
print(f"\n   Estructura de un municipio:")
muni_ejemplo = municipios[0]
for key, val in muni_ejemplo.items():
    print(f"      {key}: {val} ({type(val).__name__})")

# 2. Probar obtener datos de UN municipio específico
print("\n2️⃣ Probando obtener datos de un municipio específico...")

# Usar Madrid (código 28079)
codigo_madrid = "28079"
municipio_madrid = next((m for m in municipios if m['Codigo'] == codigo_madrid), None)

if municipio_madrid:
    print(f"   Madrid: {municipio_madrid}")
    
    # Probar diferentes formas de filtrar
    urls_prueba = [
        f"https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775?Municipios={codigo_madrid}",
        f"https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775?cod={codigo_madrid}",
        f"https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775?codigo={codigo_madrid}",
        f"https://servicios.ine.es/wstempus/js/es/SERIE/{municipio_madrid['Id']}",
    ]
    
    for url in urls_prueba:
        try:
            r = requests.get(url, timeout=10)
            if r.ok:
                data = r.json()
                print(f"   ✅ {url}")
                print(f"      Items: {len(data) if isinstance(data, list) else 'dict'}")
        except Exception as e:
            print(f"   ❌ {url}: {e}")

# 3. Explorar el endpoint de ayuda
print("\n3️⃣ Consultando documentación de la API...")
url_help = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/33775?help=1"
r = requests.get(url_help, timeout=10)
if r.ok:
    help_data = r.json()
    print(f"   Contenido de help:")
    print(json.dumps(help_data, indent=2, ensure_ascii=False)[:1000])

# 4. Analizar la estructura de SERIES_TABLA
print("\n4️⃣ Analizando SERIES_TABLA...")
url_series = "https://servicios.ine.es/wstempus/js/es/SERIES_TABLA/33775"
r = requests.get(url_series, timeout=30)
if r.ok:
    series = r.json()
    print(f"   Total series: {len(series)}")
    if series:
        print(f"   Estructura primera serie:")
        serie_ejemplo = series[0]
        for key, val in serie_ejemplo.items():
            val_preview = str(val)[:100] if not isinstance(val, (dict, list)) else type(val).__name__
            print(f"      {key}: {val_preview}")
        
        # Buscar series de municipios
        series_municipios = [s for s in series if 'Municipio' in str(s.get('Nombre', ''))]
        print(f"\n   Series relacionadas con municipios: {len(series_municipios)}")
        if series_municipios:
            print(f"   Ejemplo:")
            print(f"      {series_municipios[0]}")

# 5. Probar endpoint DATOS_SERIE
print("\n5️⃣ Probando DATOS_SERIE con una serie específica...")
if series and len(series) > 0:
    codigo_serie = series[0].get('COD', series[0].get('Id', ''))
    if codigo_serie:
        url_datos_serie = f"https://servicios.ine.es/wstempus/js/es/DATOS_SERIE/{codigo_serie}"
        try:
            r = requests.get(url_datos_serie, timeout=10)
            if r.ok:
                datos = r.json()
                print(f"   ✅ Datos de serie {codigo_serie}:")
                print(f"      Tipo: {type(datos)}")
                if isinstance(datos, dict):
                    print(f"      Claves: {list(datos.keys())}")
                elif isinstance(datos, list):
                    print(f"      Items: {len(datos)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("SIGUIENTE PASO: Encontrar cómo iterar o solicitar datos masivos")
