"""
optimizer.py
------------
Fase 7: Optimización automática del IR mediante llvmlite PassManager (O3).
"""
import llvmlite.binding as llvm
import os
import shutil
import subprocess
import tempfile
import time


def optimize_ir(ir_string: str) -> dict:
    """
    Recibe el IR sin optimizar como string.
    Retorna un dict con:
      - optimized_ir: str
      - metrics: dict con instruction_count_before, instruction_count_after,
                 reduction_pct, transformations_applied: list[str], time_ms: float
    """
    start = time.perf_counter()
    count_before = _count_instructions(ir_string)
    optimized_str = None
    opt_error = None

    if shutil.which("opt"):
        optimized_str, opt_error = _run_opt_o3(ir_string)

    if optimized_str is None:
        try:
            mod = llvm.parse_assembly(ir_string)
            mod.verify()
            pmb = llvm.PassManagerBuilder()
            pmb.opt_level = 3
            pmb.inlining_threshold = 275
            pm = llvm.ModulePassManager()
            pmb.populate(pm)
            pm.run(mod)
            optimized_str = str(mod)
        except Exception as exc:
            optimized_str = ir_string
            opt_error = opt_error or str(exc)

    count_after = _count_instructions(optimized_str)
    elapsed = (time.perf_counter() - start) * 1000

    reduction = 0.0
    if count_before > 0:
        reduction = round((1 - count_after / count_before) * 100, 2)

    transformations = _detect_transformations(ir_string, optimized_str)
    if opt_error and optimized_str == ir_string:
        transformations = [f"Optimización no disponible: {opt_error}"]

    return {
        "optimized_ir": optimized_str,
        "metrics": {
            "instruction_count_before": count_before,
            "instruction_count_after": count_after,
            "reduction_pct": reduction,
            "transformations_applied": transformations,
            "time_ms": round(elapsed, 2)
        }
    }


def _run_opt_o3(ir_string: str) -> tuple[str | None, str | None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, "input.ll")
        out_path = os.path.join(tmpdir, "output.opt.ll")
        with open(in_path, "w", encoding="utf-8") as f:
            f.write(ir_string)
        proc = subprocess.run(
            ["opt", "-S", "-O3", in_path, "-o", out_path],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return None, proc.stderr.strip() or proc.stdout.strip()
        with open(out_path, encoding="utf-8") as f:
            return f.read(), None


def _count_instructions(ir_str: str) -> int:
    """Cuenta líneas que son instrucciones LLVM (no labels, comentarios ni declaraciones)."""
    count = 0
    for line in ir_str.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(';') \
           and not stripped.startswith('define') \
           and not stripped.startswith('declare') \
           and not stripped.startswith('@') \
           and not stripped.startswith('}') \
           and not stripped.startswith('{') \
           and not stripped.endswith(':'):
            count += 1
    return count


def _detect_transformations(before: str, after: str) -> list:
    """Identifica cuáles optimizaciones tuvieron efecto observable."""
    transformations = []
    before_lines = set(before.splitlines())
    after_lines = set(after.splitlines())

    if before_lines != after_lines:
        transformations.append("PassManager O3 ejecutado sobre el módulo LLVM")
        if 'alloca' in before and 'alloca' not in after:
            transformations.append("mem2reg: Variables promovidas de memoria a registros")
        if before.count('br ') > after.count('br '):
            transformations.append("simplifycfg: Bloques básicos simplificados/eliminados")
        if _count_instructions(before) > _count_instructions(after):
            transformations.append("dce: Instrucciones muertas eliminadas")
            transformations.append("instcombine: Instrucciones combinadas/simplificadas")
        if 'call ' in before and before.count('call ') > after.count('call '):
            transformations.append("inline: Llamadas a funciones inlineadas")
        if before.count('br ') > after.count('br ') or before.count('switch ') > after.count('switch '):
            transformations.append("control-flow: saltos/switch simplificados")

    if not transformations:
        transformations.append(
            "PassManager O3 ejecutado; sin cambios observables para este programa"
        )

    return transformations
