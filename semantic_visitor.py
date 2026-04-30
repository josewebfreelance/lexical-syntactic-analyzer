"""
semantic_visitor.py
-------------------
Visitor de VALIDACIÓN de tipos para Fase 3 (v3).
Soporta arreglos, módulo, break/continue e imports.
"""

from Language_v3Visitor import Language_v3Visitor
from Language_v3Parser import Language_v3Parser
from symbol_table import SymbolTable


class SemanticVisitor(Language_v3Visitor):

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function_return_type = None
        self.loop_depth = 0 # Para validar break/continue

    def _err(self, line, col, msg):
        self.errors.append(f"[Error Semántico] Línea {line}, Columna {col}: {msg}")

    def _infer(self, ctx):
        if isinstance(ctx, Language_v3Parser.IntContext):
            return 'int'

        if isinstance(ctx, Language_v3Parser.FloatExprContext):
            return 'float'

        if isinstance(ctx, Language_v3Parser.StringExprContext):
            return 'string'

        if isinstance(ctx, Language_v3Parser.BoolExprContext):
            return 'bool'

        if isinstance(ctx, Language_v3Parser.IdContext):
            name = ctx.ID().getText()
            sym = self.symbol_table.lookup(name)
            if sym is None:
                tok = ctx.ID().getSymbol()
                self._err(tok.line, tok.column, f"Variable '{name}' no declarada.")
                return None
            return sym['type']

        if isinstance(ctx, Language_v3Parser.ParensContext):
            return self._infer(ctx.expr())

        if isinstance(ctx, Language_v3Parser.MulDivModContext):
            return self._infer_binary(ctx)

        if isinstance(ctx, Language_v3Parser.AddSubContext):
            lt = self._infer(ctx.left)
            rt = self._infer(ctx.right)
            op = ctx.op.text

            if op == '+' and lt == 'string' and rt == 'string':
                return 'string'

            if lt == 'string' or rt == 'string':
                self._err(ctx.op.line, ctx.op.column,
                          f"Operación '{op}' no válida con tipo 'string'.")
                return None

            return self._check_numeric_compat(lt, rt, ctx.op)

        if isinstance(ctx, Language_v3Parser.FunctionCallContext):
            return self._check_call(ctx)

        if isinstance(ctx, Language_v3Parser.ArrayAccessContext):
            name = ctx.ID().getText()
            sym = self.symbol_table.lookup(name)
            if sym is None:
                tok = ctx.ID().getSymbol()
                self._err(tok.line, tok.column, f"Arreglo '{name}' no declarado.")
                return None
            if not sym.get('is_array'):
                tok = ctx.ID().getSymbol()
                self._err(tok.line, tok.column, f"La variable '{name}' no es un arreglo.")
                return None
            idx_type = self._infer(ctx.expr())
            if idx_type != 'int':
                self._err(ctx.expr().start.line, ctx.expr().start.column, 
                          f"El índice del arreglo debe ser 'int', se encontró '{idx_type}'.")
            return sym['element_type']

        if isinstance(ctx, Language_v3Parser.ArrayLitContext):
            exprs = ctx.expr()
            if not exprs:
                return 'void[]' # Arreglo vacío, tipo indeterminado hasta asignación
            first_type = self._infer(exprs[0])
            for i in range(1, len(exprs)):
                t = self._infer(exprs[i])
                if t != first_type:
                    self._err(exprs[i].start.line, exprs[i].start.column,
                              f"Inconsistencia de tipos en literal de arreglo: se esperaba '{first_type}' pero se encontró '{t}'.")
            return f"{first_type}[]"

        if isinstance(ctx, Language_v3Parser.ArrayNewContext):
            idx_type = self._infer(ctx.expr())
            if idx_type != 'int':
                self._err(ctx.expr().start.line, ctx.expr().start.column, 
                          f"El tamaño del arreglo debe ser 'int', se encontró '{idx_type}'.")
            # El tipo base está en los tokens hijos (INT_R, FLOAT_R, etc.)
            base_type = ctx.getChild(0).getText()
            return f"{base_type}[]"

        return None

    def _infer_binary(self, ctx):
        lt = self._infer(ctx.left)
        rt = self._infer(ctx.right)

        if lt == 'string' or rt == 'string':
            self._err(ctx.op.line, ctx.op.column,
                      f"Operación '{ctx.op.text}' no válida con tipo 'string'.")
            return None

        return self._check_numeric_compat(lt, rt, ctx.op)

    def _check_numeric_compat(self, lt, rt, op_token):
        if lt is None or rt is None:
            return lt or rt

        if lt != rt:
            self._err(op_token.line, op_token.column,
                      f"Incompatibilidad de tipos en '{op_token.text}': '{lt}' y '{rt}'.")
            return None

        return lt