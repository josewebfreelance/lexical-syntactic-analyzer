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

OUTPUT_DIR = "output"


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

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        final_path = os.path.join(OUTPUT_DIR, "output_linux")
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
                "clang no encontrado.\n\n"
                "OPCIONES:\n"
                "1. Instalar clang: sudo apt install clang\n"
                "2. Usar el intérprete integrado del pipeline\n"
                "3. Usar el IR de LLVM directamente (output.ll)"
            ),
            "time_ms": 0
        }


def _compile_windows(ir_path: str, tmpdir: str) -> dict:
    """
    Cross-compila el IR de LLVM a un ejecutable Windows (.exe) usando clang
    con el target x86_64-w64-mingw32 y el linker de mingw-w64.
    Requiere: sudo apt install clang mingw-w64
    """
    start = time.perf_counter()

    obj_path = os.path.join(tmpdir, "program_win.o")
    out_path = os.path.join(tmpdir, "program_win.exe")
    final_path = os.path.join(OUTPUT_DIR, "output_windows.exe")

    # Paso 1: compilar IR a objeto Windows con clang cross-target
    try:
        proc1 = subprocess.run(
            [
                "clang",
                "-target", "x86_64-w64-mingw32",
                "-O2",
                "-c",
                "-o", obj_path,
                ir_path,
            ],
            capture_output=True, text=True
        )
    except FileNotFoundError:
        return {
            "success": False,
            "error": (
                "clang no encontrado.\n"
                "Instala con: sudo apt install clang"
            ),
            "time_ms": 0
        }

    if proc1.returncode != 0:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {"success": False, "error": proc1.stderr, "time_ms": elapsed}

    # Paso 2: enlazar con x86_64-w64-mingw32-gcc para generar el .exe
    try:
        proc2 = subprocess.run(
            [
                "x86_64-w64-mingw32-gcc",
                "-mconsole",
                "-Wl,-e,mainCRTStartup",
                "-o", out_path,
                obj_path,
            ],
            capture_output=True, text=True
        )
    except FileNotFoundError:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return {
            "success": False,
            "error": (
                "x86_64-w64-mingw32-gcc no encontrado.\n"
                "Instala con: sudo apt install mingw-w64"
            ),
            "time_ms": elapsed
        }

    elapsed = round((time.perf_counter() - start) * 1000, 2)

    if proc2.returncode != 0:
        return {"success": False, "error": proc2.stderr, "time_ms": elapsed}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    shutil.copy(out_path, final_path)

    return {
        "success": True,
        "binary_path": final_path,
        "size_bytes": os.path.getsize(final_path),
        "time_ms": elapsed
    }
