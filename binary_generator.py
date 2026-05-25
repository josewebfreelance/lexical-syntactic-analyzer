"""
binary_generator.py
-------------------
Fase 8: Compila el IR optimizado a binarios nativos para Linux y/o Windows.
Requiere en el sistema: clang, llvm-as, lli y opcionalmente mingw-w64.
Instalación: sudo apt install clang llvm mingw-w64
"""
import subprocess
import time
import os
import tempfile
import shutil

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
    out_path = os.path.join(tmpdir, "program_linux")
    start = time.perf_counter()
    try:
        obj_path = os.path.join(tmpdir, "program_linux.o")
        proc = subprocess.run(
            ["clang", "-O2", "-o", obj_path, "-c", ir_path],
            capture_output=True, text=True
        )
        if proc.returncode != 0:
            return {"success": False, "error": proc.stderr, "time_ms": 0}

        proc2 = subprocess.run(
            ["clang", "-O2", "-o", out_path, obj_path],
            capture_output=True, text=True
        )
        elapsed = round((time.perf_counter() - start) * 1000, 2)

        if proc2.returncode != 0:
            return {"success": False, "error": proc2.stderr, "time_ms": elapsed}

        final_path = "output_linux"
        shutil.copy(out_path, final_path)

        return {
            "success": True,
            "binary_path": final_path,
            "size_bytes": os.path.getsize(final_path),
            "time_ms": elapsed
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "clang no encontrado.\nInstala con: sudo apt install clang",
            "time_ms": 0
        }

def _compile_windows(ir_path: str, tmpdir: str) -> dict:
    out_path = os.path.join(tmpdir, "program.exe")
    start = time.perf_counter()
    try:
        proc = subprocess.run([
            "clang", "-O2",
            "--target=x86_64-w64-mingw32",
            "-o", out_path,
            ir_path,
            "-lmingw32"
        ], capture_output=True, text=True)

        elapsed = round((time.perf_counter() - start) * 1000, 2)

        if proc.returncode != 0:
            proc2 = subprocess.run([
                "x86_64-w64-mingw32-gcc", "-O2", "-o", out_path, ir_path
            ], capture_output=True, text=True)
            elapsed = round((time.perf_counter() - start) * 1000, 2)

            if proc2.returncode != 0:
                return {
                    "success": False,
                    "error": (
                        f"clang: {proc.stderr}\n"
                        f"mingw-gcc: {proc2.stderr}\n\n"
                        "Instala con: sudo apt install clang mingw-w64"
                    ),
                    "time_ms": elapsed
                }

        final_path = "output_windows.exe"
        shutil.copy(out_path, final_path)

        return {
            "success": True,
            "binary_path": final_path,
            "size_bytes": os.path.getsize(final_path),
            "time_ms": elapsed
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": (
                "Herramientas de cross-compilación no encontradas.\n"
                "Instala con: sudo apt install clang mingw-w64"
            ),
            "time_ms": 0
        }