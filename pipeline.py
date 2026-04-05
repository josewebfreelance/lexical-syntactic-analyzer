"""
pipeline.py
-----------
Orquesta las 4 fases del compilador en secuencia:

  1. Léxico     → LexerErrorListener   captura tokens inválidos
  2. Sintáctico → ParserErrorListener  captura violaciones de gramática
  3. Semántico  → SemanticVisitor      valida tipos sin ejecutar nada
  4. Ejecución  → Interpreter          corre el programa solo si no hay errores

Si alguna fase produce errores, se imprimen y el pipeline se detiene.
"""

import sys
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from LanguageLexer import LanguageLexer
from LanguageParser import LanguageParser
from semantic_visitor import SemanticVisitor
from interpreter import Interpreter

# Error Listeners con formato estándar ----------------------------------------

class LexerErrorListener(ErrorListener):
    """
    Captura errores del scanner (caracteres/tokens no reconocidos).
    Formato: [Error Léxico] Línea X, Columna Y: Símbolo no reconocido 'X'.
    """

    def __init__(self):
        super().__init__()
        self.errors: list[str] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # En el lexer, offendingSymbol puede ser None; usamos el carácter del msg
        symbol = offendingSymbol.text if offendingSymbol else '?'
        self.errors.append(
            f"[Error Léxico] Línea {line}, Columna {column}: "
            f"Símbolo no reconocido '{symbol}'."
        )


class ParserErrorListener(ErrorListener):
    """
    Captura violaciones de la gramática (estructura inválida).
    Formato: [Error Sintáctico] Línea X, Columna Y: Se esperaba ... pero se encontró '...'.
    """

    def __init__(self):
        super().__init__()
        self.errors: list[str] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        found = offendingSymbol.text if offendingSymbol else '<EOF>'
        self.errors.append(
            f"[Error Sintáctico] Línea {line}, Columna {column}: "
            f"{msg} (encontrado: '{found}')."
        )


# Pipeline principal --------------------------------------------------------

def _print_errors(errors: list[str]):
    for err in errors:
        print(err)


def run_pipeline(source_file: str):
    # 1. Carga del archivo ─────────────────────────────────────────────────
    try:
        input_stream = FileStream(source_file, encoding='utf-8')
    except FileNotFoundError:
        print(f"[!] Archivo no encontrado: '{source_file}'")
        return

    # 2. FASE LÉXICA ───────────────────────────────────────────────────────
    lexer = LanguageLexer(input_stream)
    lexer_errors = LexerErrorListener()
    lexer.removeErrorListeners()          # Quitar salida por defecto de ANTLR
    lexer.addErrorListener(lexer_errors)

    token_stream = CommonTokenStream(lexer)

    # 3. FASE SINTÁCTICA ───────────────────────────────────────────────────
    parser = LanguageParser(token_stream)
    parser_errors = ParserErrorListener()
    parser.removeErrorListeners()         # Quitar salida por defecto de ANTLR
    parser.addErrorListener(parser_errors)

    tree = parser.program()

    # Verificar errores léxicos y sintácticos antes de continuar
    all_early_errors = lexer_errors.errors + parser_errors.errors
    if all_early_errors:
        print("─" * 50)
        print("╔══ ERRORES ENCONTRADOS ══╗")
        _print_errors(all_early_errors)
        print("─" * 50)
        return

    print("✔  Análisis léxico y sintáctico exitoso.")

    # 4. FASE SEMÁNTICA ────────────────────────────────────────────────────
    print("→  Iniciando validación semántica...")
    semantic = SemanticVisitor()
    semantic.visit(tree)

    if semantic.errors:
        print("─" * 50)
        print("╔══ ERRORES SEMÁNTICOS ══╗")
        _print_errors(semantic.errors)
        print("─" * 50)
        print("✘  La ejecución fue detenida por errores semánticos.")
        return

    print("✔  Validación semántica exitosa. Sin errores de tipo.")

    # 5. FASE DE EJECUCIÓN ─────────────────────────────────────────────────
    print("→  Iniciando ejecución del programa...")
    print("─" * 50)

    try:
        interpreter = Interpreter()
        interpreter.visit(tree)
    except (NameError, ZeroDivisionError, TypeError) as e:
        print(f"\n[Error Runtime] {e}")
        return
    except Exception as e:
        print(f"\n[Error Inesperado] {e}")
        return

    print("─" * 50)
    print("✔  Ejecución completada exitosamente.")


# Punto de entrada ----------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 pipeline.py <archivo_fuente>")
        sys.exit(1)

    run_pipeline(sys.argv[1])