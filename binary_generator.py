"""
binary_generator.py
-------------------
Fase 8: Compila el IR optimizado a binarios nativos para Linux y/o Windows.
Requiere en el sistema: clang, llvm-as, lli y opcionalmente mingw-w64.
Instalación: sudo apt install clang llvm mingw-w64
"""

import os
import tempfile

def generate_binary(ir_string: str, target_linux: bool, target_windows: bool) -> dict:
    """
    Compila el IR a ejecutables nativos según las plataformas seleccionadas.
    Retorna dict con resultados para cada plataforma.
    """
    results = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        ir_path = os.path.join(tmpdir, "program.ll")
        with open(ir_path, "w") as f:
            f.write(ir_string)
        
        if target_linux:
            results["linux"] = _compile_linux(ir_path, tmpdir)
        if target_windows:
            results["windows"] = _compile_windows(ir_path, tmpdir)
            
    return results

def _compile_linux(ir_path: str, tmpdir: str) -> dict:
    # Por ahora retorna un stub, se implementará en el siguiente commit
    return {"success": False, "error": "Not implemented yet", "time_ms": 0}

def _compile_windows(ir_path: str, tmpdir: str) -> dict:
    # Por ahora retorna un stub, se implementará en un commit posterior
    return {"success": False, "error": "Not implemented yet", "time_ms": 0}