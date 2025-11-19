#!/usr/bin/env python
"""
Investigación de la API del INE para obtener Padrón completo.

Vamos a probar diferentes endpoints y parámetros de la API del INE
para encontrar la forma de obtener TODOS los municipios.
"""
import requests
import json
from pprint import pprint

print("=" * 70)
print("INVESTIGACIÓN API INE - PADRÓN")
print("=" * 70)

# URLs base conocidas
TEMPUS_BASE = "https://servicios.ine.es/wstempus"
JAXI_BASE = "https://www.ine.es/jaxiT3"

# Tabla del Padrón: 33775
TABLA_PADRON = "33775"

print("\n1️⃣ Probando endpoint Tempus (nacional)...")
url1 = f"{TEMPUS_BASE}/js/es/DATOS_TABLA/{TABLA_PADRON}"
try:
    r = requests.get(url1, timeout=30)
    print(f"   URL: {url1}")
    print(f"   Status: {r.status_code}")
    if r.ok:
        data = r.json()
        print(f"   Items: {len(data)}")
        if data:
            # Analizar primer item
            item = data[0]
            print(f"   Claves primer item: {list(item.keys())}")
            if "MetaData" in item:
                meta = {d.get("T3_Variable", d.get("Nombre")): d.get("Codigo") 
                        for d in item["MetaData"]}
                print(f"   Dimensiones: {list(meta.keys())}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2️⃣ Probando endpoint Tempus con parámetros...")
# Intentar diferentes parámetros
parametros = [
    {"tip": "A"},     # Anual
    {"tip": "AM"},    # Anual con metadatos
    {"nult": "1000"}, # Últimos N resultados
    {"det": "1"},     # Detalle
]

for params in parametros:
    url = f"{TEMPUS_BASE}/js/es/DATOS_TABLA/{TABLA_PADRON}"
    try:
        r = requests.get(url, params=params, timeout=30)
        print(f"   Params: {params}")
        print(f"   Status: {r.status_code}")
        if r.ok:
            data = r.json()
            print(f"   Items: {len(data)}")
            
            # Contar municipios únicos
            municipios = set()
            for item in data:
                meta = {d.get("T3_Variable", ""): d.get("Codigo", "") 
                        for d in item.get("MetaData", [])}
                if "Municipios" in meta and meta["Municipios"]:
                    municipios.add(meta["Municipios"][:2])  # Código provincia
            
            print(f"   Provincias únicas: {sorted(municipios)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n3️⃣ Probando endpoint SERIE...")
url3 = f"{TEMPUS_BASE}/js/es/SERIES_TABLA/{TABLA_PADRON}"
try:
    r = requests.get(url3, timeout=30)
    print(f"   URL: {url3}")
    print(f"   Status: {r.status_code}")
    if r.ok:
        data = r.json()
        print(f"   Tipo: {type(data)}")
        print(f"   Claves: {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
        if isinstance(data, dict):
            print(f"   Contenido (primeras 5 claves):")
            for key in list(data.keys())[:5]:
                print(f"      {key}: {type(data[key])}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n4️⃣ Probando endpoint VALORES...")
url4 = f"{TEMPUS_BASE}/js/es/VALORES_VARIABLE/Municipios"
try:
    r = requests.get(url4, timeout=30)
    print(f"   URL: {url4}")
    print(f"   Status: {r.status_code}")
    if r.ok:
        data = r.json()
        print(f"   Tipo: {type(data)}")
        if isinstance(data, list):
            print(f"   Total municipios: {len(data)}")
            print(f"   Primeros 5:")
            for item in data[:5]:
                print(f"      {item}")
        elif isinstance(data, dict):
            print(f"   Claves: {list(data.keys())}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n5️⃣ Probando endpoint TABLAS (metadatos)...")
url5 = f"{TEMPUS_BASE}/js/es/TABLA/{TABLA_PADRON}"
try:
    r = requests.get(url5, timeout=30)
    print(f"   URL: {url5}")
    print(f"   Status: {r.status_code}")
    if r.ok:
        data = r.json()
        print(f"   Tipo: {type(data)}")
        if isinstance(data, dict):
            print(f"   Claves: {list(data.keys())}")
            if "Variables" in data:
                print(f"   Variables disponibles:")
                for var in data["Variables"]:
                    print(f"      {var}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n6️⃣ Buscando documentación de la API...")
endpoints_doc = [
    f"{TEMPUS_BASE}/js/es/DATOS_TABLA/{TABLA_PADRON}?help=1",
    f"{TEMPUS_BASE}/api/help",
    f"{TEMPUS_BASE}/swagger",
]

for url in endpoints_doc:
    try:
        r = requests.get(url, timeout=10)
        if r.ok:
            print(f"   ✅ Encontrado: {url}")
            print(f"   Content-Type: {r.headers.get('content-type')}")
    except:
        pass

print("\n" + "=" * 70)
print("Análisis completado. Revisando resultados...")
