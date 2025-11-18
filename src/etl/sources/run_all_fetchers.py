#!/usr/bin/env python
"""
Ejecuta todos los fetchers de fuentes de datos para el data lake.
Uso: python src/etl/sources/run_all_fetchers.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="ignore")  # type: ignore

FETCHERS = [
    "fetch_municipios_ign.py",
    "fetch_valor_tasado_seed.py",
    "fetch_ine_padron_all.py",
    "fetch_ine_adrh_all.py",
    "fetch_sepe_paro_all.py",
    "fetch_euribor_bde.py",
]

def run_fetcher(script_path: Path):
    """Ejecuta un fetcher y captura errores."""
    print(f"\n{'='*70}")
    print(f"▶️  Ejecutando: {script_path.name}")
    print(f"{'='*70}")
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            code = compile(f.read(), script_path, "exec")
            exec(code, {"__name__": "__main__", "__file__": str(script_path)})
        print(f"✅ {script_path.name} completado.")
        return True
    except Exception as e:
        print(f"❌ {script_path.name} falló: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    root = Path(__file__).resolve().parent
    results = {}
    
    print("🚀 Iniciando descarga de todas las fuentes de datos...")
    print(f"📂 Directorio de trabajo: {root}")
    
    for fname in FETCHERS:
        fpath = root / fname
        if not fpath.exists():
            print(f"⚠️ No encontrado: {fname}")
            results[fname] = False
            continue
        results[fname] = run_fetcher(fpath)
    
    # Resumen
    print(f"\n{'='*70}")
    print("📊 RESUMEN DE EJECUCIÓN")
    print(f"{'='*70}")
    success = sum(1 for v in results.values() if v)
    total = len(results)
    for fname, ok in results.items():
        status = "✅" if ok else "❌"
        print(f"{status} {fname}")
    
    print(f"\n{success}/{total} fetchers completados exitosamente.")
    
    if success < total:
        print("\n⚠️ Algunos fetchers fallaron. Revisa los errores arriba.")
        sys.exit(1)
    else:
        print("\n🎉 Todas las fuentes descargadas correctamente!")
        sys.exit(0)

if __name__ == "__main__":
    main()
