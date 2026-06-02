"""
manual_optimizer.py
-------------------
Módulo de optimización manual: aplica passes individuales seleccionados por el usuario.
"""
import llvmlite.binding as llvm
import os
import shutil
import subprocess
import tempfile
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
    start = time.perf_counter()
    after_ir = None
    error = None

    if shutil.which("opt"):
        after_ir, error = _run_selected_passes(ir_string, selected_passes)

    if after_ir is None:
        try:
            mod = llvm.parse_assembly(ir_string)
            mod.verify()
            pmb = llvm.PassManagerBuilder()
            pmb.opt_level = 1 if selected_passes else 0
            if "inline" in selected_passes:
                pmb.inlining_threshold = 200
            pm = llvm.ModulePassManager()
            pmb.populate(pm)
            pm.run(mod)
            after_ir = str(mod)
        except Exception as exc:
            raise RuntimeError(error or str(exc)) from exc

    elapsed = (time.perf_counter() - start) * 1000

    diff = _compute_diff(ir_string, after_ir)

    return {
        "before_ir": ir_string,
        "after_ir": after_ir,
        "diff": diff,
        "metrics": {
            "passes_applied": selected_passes,
            "llvm_pass_pipeline": _build_pass_pipeline(selected_passes),
            "instructions_before": _count_instr(ir_string),
            "instructions_after": _count_instr(after_ir),
            "time_ms": round(elapsed, 2)
        }
    }


def _build_pass_pipeline(selected_passes: list) -> list[str]:
    mapping = {
        "mem2reg": "mem2reg",
        "instcombine": "instcombine",
        "simplifycfg": "simplifycfg",
        "dce": "dce",
        "inline": "module-inline",
        "loop-unroll": "loop-unroll<O3>",
    }
    return [mapping[p] for p in selected_passes if p in mapping]


def _run_selected_passes(ir_string: str, selected_passes: list) -> tuple[str | None, str | None]:
    pipeline = _build_pass_pipeline(selected_passes)
    if not pipeline:
        return ir_string, None
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, "input.ll")
        out_path = os.path.join(tmpdir, "output.manual.ll")
        with open(in_path, "w", encoding="utf-8") as f:
            f.write(ir_string)
        proc = subprocess.run(
            ["opt", "-S", f"-passes={','.join(pipeline)}", in_path, "-o", out_path],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return None, proc.stderr.strip() or proc.stdout.strip()
        with open(out_path, encoding="utf-8") as f:
            return f.read(), None


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