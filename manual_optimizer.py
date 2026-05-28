import llvmlite.binding as llvm
import time

AVAILABLE_PASSES = {
    "mem2reg":     "Promueve variables de memoria (alloca/load/store) a registros SSA",
    "instcombine": "Combina instrucciones redundantes en formas más simples",
    "simplifycfg": "Simplifica el grafo de flujo de control eliminando bloques muertos",
    "dce":         "Elimina instrucciones cuyo resultado nunca se usa (Dead Code Elimination)",
    "inline":      "Sustituye llamadas a funciones pequeñas por su cuerpo (Function Inlining)",
    "loop-unroll": "Expande ciclos de iteración conocida eliminando su overhead de control",
}


def apply_manual_passes(ir_string: str, selected_passes: list) -> dict:
    """
    Aplica solo los passes seleccionados al IR.
    selected_passes: lista de strings, e.g. ["mem2reg", "dce"]
    Retorna dict con before_ir, after_ir, diff y metrics.
    """
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    start = time.perf_counter()

    mod = llvm.parse_assembly(ir_string)
    mod.verify()

    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = 0

    pm = llvm.create_module_pass_manager()

    if any(p in selected_passes for p in ["mem2reg", "instcombine", "simplifycfg", "dce"]):
        pmb.opt_level = 1
        pmb.populate(pm)

    if "inline" in selected_passes:
        pmb.inlining_threshold = 200

    if "loop-unroll" in selected_passes:
        pmb.opt_level = max(pmb.opt_level, 2)
        pmb.loop_vectorize = False
        pmb.slp_vectorize = False

    pm.run(mod)

    after_ir = str(mod)
    elapsed = (time.perf_counter() - start) * 1000

    diff = _compute_diff(ir_string, after_ir)

    return {
        "before_ir": ir_string,
        "after_ir": after_ir,
        "diff": diff,
        "metrics": {
            "passes_applied": selected_passes,
            "instructions_before": _count_instr(ir_string),
            "instructions_after": _count_instr(after_ir),
            "time_ms": round(elapsed, 2)
        }
    }


def _count_instr(ir_str: str) -> int:
    return sum(
        1 for l in ir_str.splitlines()
        if l.strip() and not l.strip().startswith(
            (';', 'define', 'declare', '@', '}', '{', ' }', ' {')
        ) and not l.strip().endswith(':')
    )


def _compute_diff(before: str, after: str) -> list:
    """
    Retorna lista de dicts: {type: 'added'|'removed'|'unchanged', line: str}
    Orden: líneas del IR original primero, líneas nuevas al final.
    """
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    before_set = set(before_lines)
    after_set = set(after_lines)

    diff = []
    for line in before_lines:
        if line not in after_set:
            diff.append({"type": "removed", "line": line})
        else:
            diff.append({"type": "unchanged", "line": line})
    for line in after_lines:
        if line not in before_set:
            diff.append({"type": "added", "line": line})

    return diff


def get_available_passes() -> dict:
    return AVAILABLE_PASSES