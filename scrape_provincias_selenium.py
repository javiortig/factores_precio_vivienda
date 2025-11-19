#!/usr/bin/env python
"""
Extrae TODOS los códigos de tabla del Padrón provincial usando Selenium.

Navega por https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225
y extrae el código de tabla de cada provincia inspeccionando los enlaces de descarga.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import re

# URL de la página con todas las provincias
URL = "https://www.ine.es/dynt3/inebase/index.htm?padre=6225&capsel=6225"

def extraer_codigos_provincias():
    """Extrae códigos de tabla para las 52 provincias."""
    
    print("🚀 Iniciando navegador Chrome...")
    
    # Configurar opciones de Chrome
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Descomentar para modo sin interfaz
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print(f"📥 Cargando página: {URL}")
        driver.get(URL)
        
        # Esperar a que cargue la página y el contenido dinámico
        print("⏳ Esperando a que cargue el contenido...")
        wait = WebDriverWait(driver, 20)
        
        # Esperar a que aparezca el contenido principal
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        time.sleep(5)  # Tiempo adicional para JavaScript
        
        # Guardar screenshot para debug
        driver.save_screenshot('debug_pagina.png')
        print("📸 Screenshot guardada: debug_pagina.png")
        
        # Guardar HTML para inspección
        with open('debug_pagina.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("📄 HTML guardado: debug_pagina.html")
        
        print("🔍 Buscando provincias en el árbol de navegación...")
        
        # Verificar si hay iframes
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"   iframes encontrados: {len(iframes)}")
        
        # Buscar todos los elementos <a>
        todos_enlaces = driver.find_elements(By.TAG_NAME, 'a')
        print(f"   Total enlaces <a>: {len(todos_enlaces)}")
        
        # Filtrar los que tienen dlgExport
        enlaces_descarga = [a for a in todos_enlaces if 'dlgExport' in (a.get_attribute('href') or '')]
        
        print(f"✅ Encontrados {len(enlaces_descarga)} enlaces de descarga")
        
        provincias = {}
        codigos_provincia = list(range(1, 53))  # 01-52
        
        for idx, enlace in enumerate(enlaces_descarga):
            try:
                href = enlace.get_attribute('href')
                
                # Extraer código de tabla
                match = re.search(r't=(\d+)', href)
                if not match:
                    continue
                
                codigo_tabla = match.group(1)
                
                # Encontrar el nombre de la provincia
                # El enlace está dentro de un <li>, buscar hacia arriba para encontrar el nombre
                parent_li = enlace.find_element(By.XPATH, './ancestor::li[1]')
                
                # Buscar el texto de la provincia (suele estar en un <a> anterior o <span>)
                try:
                    # Intentar encontrar el enlace de la provincia (no el de descarga)
                    nombre_elem = parent_li.find_element(By.XPATH, './/a[not(contains(@class, "thickbox"))]')
                    nombre = nombre_elem.text.strip()
                except:
                    # Si no hay enlace, buscar cualquier texto
                    nombre = parent_li.text.split('\n')[0].strip()
                
                # Limpiar nombre (quitar números al final si existen)
                nombre = re.sub(r'\s+\d+$', '', nombre)
                
                if nombre and codigo_tabla:
                    # Intentar determinar el código de provincia (01-52)
                    # Basándonos en el orden de aparición
                    codigo_prov = f"{idx + 1:02d}" if idx < 52 else None
                    
                    print(f"  [{codigo_prov}] {nombre}: {codigo_tabla}")
                    
                    provincias[codigo_tabla] = {
                        "codigo": codigo_prov,
                        "nombre": nombre,
                        "tabla": codigo_tabla
                    }
                    
            except Exception as e:
                print(f"  ⚠️ Error procesando enlace {idx}: {e}")
                continue
        
        print(f"\n✅ Total provincias extraídas: {len(provincias)}")
        
        # Guardar resultados
        output = {
            "provincias": provincias,
            "total": len(provincias),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open('provincias_codigos_extraidos.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Guardado en: provincias_codigos_extraidos.json")
        
        return provincias
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
        
    finally:
        print("🔚 Cerrando navegador...")
        driver.quit()


def mapear_a_codigo_provincia(provincias_extraidas):
    """
    Mapea los códigos de tabla extraídos a códigos de provincia oficiales (01-52).
    """
    # Nombres de provincias en orden oficial INE
    provincias_orden_ine = [
        "Álava", "Albacete", "Alicante", "Almería", "Ávila", "Badajoz", "Balears",
        "Barcelona", "Burgos", "Cáceres", "Cádiz", "Castellón", "Ciudad Real",
        "Córdoba", "Coruña", "Cuenca", "Girona", "Granada", "Guadalajara",
        "Gipuzkoa", "Huelva", "Huesca", "Jaén", "León", "Lleida", "Rioja",
        "Lugo", "Madrid", "Málaga", "Murcia", "Navarra", "Ourense", "Asturias",
        "Palencia", "Palmas", "Pontevedra", "Salamanca", "Santa Cruz", "Cantabria",
        "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo",
        "Valencia", "Valladolid", "Bizkaia", "Zamora", "Zaragoza", "Ceuta", "Melilla"
    ]
    
    mapeo = {}
    
    for codigo_tabla, info in provincias_extraidas.items():
        nombre = info["nombre"].lower()
        
        # Buscar coincidencia con el orden oficial
        for idx, prov_oficial in enumerate(provincias_orden_ine):
            if prov_oficial.lower() in nombre or nombre in prov_oficial.lower():
                codigo_prov = f"{idx + 1:02d}"
                mapeo[codigo_prov] = {
                    "nombre": prov_oficial,
                    "tabla": codigo_tabla
                }
                break
    
    return mapeo


if __name__ == "__main__":
    print("=" * 70)
    print("EXTRACCIÓN DE CÓDIGOS DE TABLA - PADRÓN PROVINCIAL")
    print("=" * 70)
    
    provincias = extraer_codigos_provincias()
    
    print("\n" + "=" * 70)
    print("MAPEO A CÓDIGOS OFICIALES")
    print("=" * 70)
    
    mapeo = mapear_a_codigo_provincia(provincias)
    
    print(f"\nProvincias mapeadas: {len(mapeo)}/52")
    
    # Mostrar resultado en formato para copiar/pegar
    print("\n📋 CÓDIGOS PARA fetch_ine_padron_provincias.py:")
    print("=" * 70)
    
    for codigo_prov in sorted(mapeo.keys()):
        info = mapeo[codigo_prov]
        print(f'    "{codigo_prov}": {{"nombre": "{info["nombre"]}", "tabla": "{info["tabla"]}"}},')
    
    # Guardar mapeo final
    with open('provincias_mapeo_final.json', 'w', encoding='utf-8') as f:
        json.dump(mapeo, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Mapeo final guardado en: provincias_mapeo_final.json")
