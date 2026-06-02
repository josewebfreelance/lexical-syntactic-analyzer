"""
optimizer.py
------------
Fase 7: Optimización automática del IR mediante llvmlite PassManager (O3).
"""
import llvmlite.ir as ir
import llvmlite.binding as llvm
import time


def optimize_ir(ir_string: str) -> dict:
    """
    Recibe el IR sin optimizar como string.
    Retorna un dict con:
      - optimized_ir: str
      - metrics: dict con instruction_count_before, instruction_count_after,
                 reduction_pct, transformations_applied: list[str], time_ms: float
    """
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    start = time.perf_counter()

    mod = llvm.parse_assembly(ir_string)
    mod.verify()

    count_before = _count_instructions(ir_string)

    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = 3
    pmb.inlining_threshold = 200

    pm = llvm.create_module_pass_manager()
    pmb.populate(pm)
    pm.run(mod)

    optimized_str = str(mod)
    count_after = _count_instructions(optimized_str)
    elapsed = (time.perf_counter() - start) * 1000

    reduction = 0.0
    if count_before > 0:
        reduction = round((1 - count_after / count_before) * 100, 2)

    transformations = _detect_transformations(ir_string, optimized_str)

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
        if 'alloca' in before and 'alloca' not in after:
            transformations.append("mem2reg: Variables promovidas de memoria a registros")
        if before.count('br ') > after.count('br '):
            transformations.append("simplifycfg: Bloques básicos simplificados/eliminados")
        if _count_instructions(before) > _count_instructions(after):
            transformations.append("dce: Instrucciones muertas eliminadas")
            transformations.append("instcombine: Instrucciones combinadas/simplificadas")
        if 'call ' in before and before.count('call ') > after.count('call '):
            transformations.append("inline: Llamadas a funciones inlineadas")

    if not transformations:
        transformations.append(
            "Sin optimizaciones aplicables: el IR ya es óptimo para este programa"
        )

    return transformations
