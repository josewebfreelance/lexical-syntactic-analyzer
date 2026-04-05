"""
Visitor de VALIDACIÓN de tipos. Recorre el AST y acumula errores semánticos
SIN ejecutar ningún cálculo real. Solo si self.errors queda vacío el pipeline
debe llamar al InterpreterVisitor.

Formatos de error:
  [Error Semántico] Línea X, Columna Y: <descripción>.
"""

from LanguageVisitor import LanguageVisitor
from LanguageParser import LanguageParser
from symbol_table import SymbolTable


class SemanticVisitor(LanguageVisitor):

    def _init_(self):
        self.symbol_table = SymbolTable()
        self.errors: list[str] = []
        # Tipo de retorno esperado dentro de la función actual (None = scope global)
        self.current_function_return_type = None

    # ── Reporte de errores ────────────────────────────────────────────────────

    def _err(self, line: int, col: int, msg: str):
        self.errors.append(f"[Error Semántico] Línea {line}, Columna {col}: {msg}")

    # ── Inferencia de tipos ──────────────────────────────────────────────────
    # Retorna el tipo como str ('int', 'float', 'string', 'bool') o None si
    # no se puede determinar (ya se habrá anotado el error correspondiente).

    def _infer(self, ctx) -> str | None:
        if isinstance(ctx, LanguageParser.IntContext):
            return 'int'

        if isinstance(ctx, LanguageParser.FloatExprContext):
            return 'float'

        if isinstance(ctx, LanguageParser.StringExprContext):
            return 'string'

        if isinstance(ctx, LanguageParser.BoolExprContext):
            return 'bool'

        if isinstance(ctx, LanguageParser.IdContext):
            name = ctx.ID().getText()
            sym = self.symbol_table.lookup(name)
            if sym is None:
                tok = ctx.ID().getSymbol()
                self._err(tok.line, tok.column,
                          f"Variable '{name}' no declarada.")
                return None
            return sym['type']

        if isinstance(ctx, LanguageParser.ParensContext):
            return self._infer(ctx.expr())

        if isinstance(ctx, LanguageParser.MulDivContext):
            return self._infer_binary(ctx)

        if isinstance(ctx, LanguageParser.AddSubContext):
            lt = self._infer(ctx.left)
            rt = self._infer(ctx.right)
            op = ctx.op.text
            # Permitir concatenación de strings con '+'
            if op == '+' and lt == 'string' and rt == 'string':
                return 'string'
            if lt == 'string' or rt == 'string':
                self._err(ctx.op.line, ctx.op.column,
                          f"Operación '{op}' no válida con tipo 'string'. "
                          f"Solo se permite '+' entre dos operandos 'string'.")
                return None
            return self._check_numeric_compat(lt, rt, ctx.op)

        if isinstance(ctx, LanguageParser.FunctionCallContext):
            return self._check_call(ctx)

        return None  # Tipo desconocido — no generar error aquí

    def _infer_binary(self, ctx) -> str | None:
        """Valida una operación binaria aritmética (*, /)."""
        lt = self._infer(ctx.left)
        rt = self._infer(ctx.right)
        if lt == 'string' or rt == 'string':
            self._err(ctx.op.line, ctx.op.column,
                      f"Operación '{ctx.op.text}' no válida con tipo 'string'.")
            return None
        return self._check_numeric_compat(lt, rt, ctx.op)

    def _check_numeric_compat(self, lt, rt, op_token) -> str | None:
        """Verifica compatibilidad de tipos numéricos (sin promoción implícita)."""
        if lt is None or rt is None:
            return lt or rt  # Propagar tipo conocido si uno falló antes
        if lt != rt:
            self._err(op_token.line, op_token.column,
                      f"Incompatibilidad de tipos en '{op_token.text}': "
                      f"'{lt}' y '{rt}'. No hay promoción implícita de tipos.")
            return None
        return lt

    def _check_call(self, ctx) -> str | None:
        """Valida una llamada a función y retorna su tipo de retorno."""
        name = ctx.ID().getText()
        tok = ctx.ID().getSymbol()
        func = self.symbol_table.lookup_function(name)

        if func is None:
            self._err(tok.line, tok.column,
                      f"Función '{name}' no declarada.")
            return None

        params = func['params']
        args_ctx = ctx.args()
        call_args = args_ctx.expr() if args_ctx else []

        if len(call_args) != len(params):
            self._err(tok.line, tok.column,
                      f"Función '{name}' espera {len(params)} argumento(s), "
                      f"se pasaron {len(call_args)}.")
        else:
            for i, (arg_expr, (ptype, pname)) in enumerate(zip(call_args, params)):
                at = self._infer(arg_expr)
                if at is not None and at != ptype:
                    self._err(arg_expr.start.line, arg_expr.start.column,
                              f"Argumento {i + 1} de '{name}': "
                              f"se esperaba '{ptype}' pero se pasó '{at}'.")

        return func['return_type']

    # ── Visitors de estructura ────────────────────────────────────────────────

    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.visitChildren(ctx)

    def visitDeclaration(self, ctx: LanguageParser.DeclarationContext):
        return self.visitChildren(ctx)

    def visitStatement(self, ctx: LanguageParser.StatementContext):
        return self.visitChildren(ctx)

    def visitType(self, ctx: LanguageParser.TypeContext):
        return None

    def visitArgsFunction(self, ctx: LanguageParser.ArgsFunctionContext):
        return None  # Los parámetros se procesan en visitFunction