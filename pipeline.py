"""
pipeline.py
-----------
Orquesta las 6 fases del compilador v3:
1. Léxico
2. Sintáctico
3. Semántico
4. TAC (Generación de Código Intermedio)
5. LLVM IR (Generación de Código)
6. Ejecución (Intérprete + Ejecución de IR)
"""

import time
import io
import sys
import subprocess
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from Language_v3Lexer import Language_v3Lexer
from Language_v3Parser import Language_v3Parser
from semantic_visitor import SemanticVisitor
from interpreter import Interpreter
from tac_generator import TACGenerator
from ir_generator import IRGenerator


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


def run_pipeline(source_code: str, is_file=True):
    start_total = time.perf_counter()
    results = {
        "phases": [],
        "tac_output": "",
        "ir_output": "",
        "console_output": "",
        "ir_exec_output": "",
        "success": True
    }

    def add_phase(name, status, duration, errors=None):
        results["phases"].append({
            "name": name,
            "status": status,
            "time_ms": round(duration * 1000, 2),
            "errors": errors or []
        })

    # 1. Preparación ──────────────────────────────────────────────────────────
    if is_file:
        input_stream = FileStream(source_code, encoding='utf-8')
    else:
        input_stream = InputStream(source_code)

    # 2. FASE LÉXICA ──────────────────────────────────────────────────────────
    start = time.perf_counter()
    lexer = Language_v3Lexer(input_stream)
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
    parser = Language_v3Parser(token_stream)
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

    # 8. EJECUCIÓN LLVM (lli) ───────────────────────────────────────────────────
    try:
        as_proc = subprocess.run(["llvm-as", "output.ll", "-o", "output.bc"], capture_output=True, text=True)
        if as_proc.returncode != 0:
            results["ir_exec_output"] = f"Error en llvm-as:\n{as_proc.stderr}"
        else:
            lli_proc = subprocess.run(["lli", "output.bc"], capture_output=True, text=True)
            results["ir_exec_output"] = lli_proc.stdout + lli_proc.stderr
    except FileNotFoundError:
        results["ir_exec_output"] = "Error: 'lli' o 'llvm-as' no encontrado en el sistema."
    except Exception as e:
        results["ir_exec_output"] = f"Error al ejecutar IR: {e}"

    return results
