"""
pipeline.py
-----------
Orquesta las 8 fases del compilador v4:
1. Léxico
2. Sintáctico
3. Semántico
4. TAC (Generación de Código Intermedio)
5. LLVM IR (Generación de Código)
6. Ejecución (Intérprete + Ejecución de IR)
7. Optimización O3
8. Generación de Binarios
"""

import time
import io
import sys
import subprocess
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from Language_v4Lexer import Language_v4Lexer
from Language_v4Parser import Language_v4Parser
from semantic_visitor import SemanticVisitor
from interpreter import Interpreter
from tac_generator import TACGenerator
from ir_generator import IRGenerator
from optimizer import optimize_ir
from binary_generator import generate_binary


class LexerErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors: list[dict] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        symbol = offendingSymbol.text if offendingSymbol else '?'
        self.errors.append({
            "type": "Léxico",
            "line": line,
            "column": column,
            "msg": f"Símbolo no reconocido '{symbol}'."
        })


class ParserErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors: list[dict] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        found = offendingSymbol.text if offendingSymbol else '<EOF>'
        self.errors.append({
            "type": "Sintáctico",
            "line": line,
            "column": column,
            "msg": f"{msg} (encontrado: '{found}')"
        })


def run_pipeline(source_code: str, is_file=True, target_linux=False, target_windows=False):
    start_total = time.perf_counter()
    results = {
        "phases": [],
        "tac_output": "",
        "ir_output": "",
        "console_output": "",
        "ir_exec_output": "",
        "optimized_ir": "",
        "opt_metrics": {},
        "binary_result": {},
        "success": True
    }

    def add_phase(name, status, duration, errors=None):
        results["phases"].append({
            "name": name,
            "status": status,
            "time_ms": round(duration * 1000, 2),
            "errors": errors or []
        })

    def add_error(name, duration, exc):
        add_phase(name, "ERROR", duration, [{
            "type": name,
            "line": 0,
            "column": 0,
            "msg": str(exc)
        }])

    # 1. Preparación ──────────────────────────────────────────────────────────
    if is_file:
        input_stream = FileStream(source_code, encoding='utf-8')
    else:
        input_stream = InputStream(source_code)

    # 2. FASE LÉXICA ──────────────────────────────────────────────────────────
    start = time.perf_counter()
    lexer = Language_v4Lexer(input_stream)
    lexer_errors = LexerErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_errors)
    
    token_stream = CommonTokenStream(lexer)
    token_stream.fill() 
    
    lexer_duration = time.perf_counter() - start
    if lexer_errors.errors:
        add_phase("Léxico", "ERROR", lexer_duration, lexer_errors.errors)
        results["success"] = False
        return results
    add_phase("Léxico", "OK", lexer_duration)

    # 3. FASE SINTÁCTICA ───────────────────────────────────────────────────────
    start = time.perf_counter()
    parser = Language_v4Parser(token_stream)
    parser_errors = ParserErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(parser_errors)
    
    tree = parser.program()
    
    parser_duration = time.perf_counter() - start
    if parser_errors.errors:
        add_phase("Sintáctico", "ERROR", parser_duration, parser_errors.errors)
        results["success"] = False
        return results
    add_phase("Sintáctico", "OK", parser_duration)

    # 4. FASE SEMÁNTICA ────────────────────────────────────────────────────────
    start = time.perf_counter()
    semantic = SemanticVisitor()
    semantic.visit(tree)
    
    sem_duration = time.perf_counter() - start
    if semantic.errors:
        formatted_errors = []
        for err in semantic.errors:
            parts = err.split(": ")
            header = parts[0].replace("[Error Semántico] ", "")
            msg = parts[1]
            line_col = header.split(", ")
            l = int(line_col[0].replace("Línea ", ""))
            c = int(line_col[1].replace("Columna ", ""))
            formatted_errors.append({"type": "Semántico", "line": l, "column": c, "msg": msg})
        
        add_phase("Semántico", "ERROR", sem_duration, formatted_errors)
        results["success"] = False
        return results
    add_phase("Semántico", "OK", sem_duration)

    # 5. FASE TAC ──────────────────────────────────────────────────────────────
    start = time.perf_counter()
    tac_gen = TACGenerator()
    tac_gen.visit(tree)
    results["tac_output"] = tac_gen.get_output()
    tac_duration = time.perf_counter() - start
    
    with open("output.tac", "w") as f:
        f.write(results["tac_output"])
        
    add_phase("TAC", "OK", tac_duration)

    # 6. FASE LLVM IR ──────────────────────────────────────────────────────────
    start = time.perf_counter()
    ir_gen = IRGenerator()
    ir_gen.visit(tree)
    results["ir_output"] = ir_gen.get_output()
    ir_duration = time.perf_counter() - start
    
    with open("output.ll", "w") as f:
        f.write(results["ir_output"])
        
    add_phase("LLVM IR", "OK", ir_duration)

    # 7. FASE EJECUCIÓN (Intérprete) ────────────────────────────────────────────
    start = time.perf_counter()
    output_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output_capture
    
    try:
        interpreter = Interpreter()
        interpreter.visit(tree)
        exec_status = "OK"
    except Exception as e:
        print(f"\n[Error Runtime] {e}")
        exec_status = "ERROR"
    finally:
        sys.stdout = old_stdout
        results["console_output"] = output_capture.getvalue()
    
    exec_duration = time.perf_counter() - start
    add_phase("Ejecución (Int)", exec_status, exec_duration)

    results["ir_exec_output"] = execute_ir(results["ir_output"])

    # 7. FASE OPTIMIZACIÓN O3 ─────────────────────────────────────────────────────
    start = time.perf_counter()
    try:
        opt_result = optimize_ir(results["ir_output"])
        results["optimized_ir"] = opt_result["optimized_ir"]
        results["opt_metrics"] = opt_result["metrics"]

        with open("output.opt.ll", "w") as f:
            f.write(results["optimized_ir"])

        opt_duration = time.perf_counter() - start
        add_phase("Optimización O3", "OK", opt_duration)
    except Exception as e:
        opt_duration = time.perf_counter() - start
        add_error("Optimización O3", opt_duration, e)
        results["success"] = False
        return results

    # 8. FASE GENERACIÓN BINARIO ──────────────────────────────────────────────────
    start = time.perf_counter()
    if target_linux or target_windows:
        bin_result = generate_binary(results["optimized_ir"], target_linux, target_windows)
        results["binary_result"] = bin_result
        bin_duration = time.perf_counter() - start
        status = "OK" if all(r.get("success") for r in bin_result.values()) else "ERROR"
        errors = []
        for platform, platform_result in bin_result.items():
            if not platform_result.get("success"):
                errors.append({
                    "type": "Binario",
                    "line": 0,
                    "column": 0,
                    "msg": f"{platform}: {platform_result.get('error', 'Error desconocido')}"
                })
        add_phase("Generación Binario", status, bin_duration, errors)
        if status == "ERROR":
            results["success"] = False
    else:
        results["binary_result"] = {}
        add_phase("Generación Binario", "OK", time.perf_counter() - start)

    return results


def execute_ir(ir_string: str) -> str:
    with open("output.exec.ll", "w") as f:
        f.write(ir_string)
    try:
        as_proc = subprocess.run(
            ["llvm-as", "output.exec.ll", "-o", "output.bc"],
            capture_output=True,
            text=True,
        )
        if as_proc.returncode != 0:
            return f"Error en llvm-as:\n{as_proc.stderr}"
        lli_proc = subprocess.run(["lli", "output.bc"], capture_output=True, text=True)
        return lli_proc.stdout + lli_proc.stderr
    except FileNotFoundError:
        return "Error: 'lli' o 'llvm-as' no encontrado en el sistema."
    except Exception as e:
        return f"Error al ejecutar IR: {e}"