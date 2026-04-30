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

    def _check_call(self, ctx):
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

    def visitProgram(self, ctx: Language_v3Parser.ProgramContext):
        return self.visitChildren(ctx)

    def visitImportStmt(self, ctx: Language_v3Parser.ImportStmtContext):
        module_name = ctx.ID().getText()
        self.symbol_table.add_import(module_name)
        return None

    def visitDeclaration(self, ctx: Language_v3Parser.DeclarationContext):
        return self.visitChildren(ctx)

    def visitStatement(self, ctx: Language_v3Parser.StatementContext):
        return self.visitChildren(ctx)

    def visitVarType(self, ctx: Language_v3Parser.VarTypeContext):
        return None

    def visitVariable(self, ctx: Language_v3Parser.VariableContext):
        type_str = ctx.varType().getText()
        var_name = ctx.ID().getText()
        tok = ctx.ID().getSymbol()
        
        is_array = type_str.endswith('[]')
        
        # Solo validar tipo si hay inicializador
        if ctx.expr():
            expr_type = self._infer(ctx.expr())
            if expr_type is not None:
                # Caso especial: arreglo vacío [] compatible con cualquier T[]
                if expr_type == 'void[]' and is_array:
                    pass
                elif expr_type != type_str:
                    self._err(tok.line, tok.column,
                              f"Incompatibilidad de tipos. No se puede asignar "
                              f"'{expr_type}' a '{type_str}'.")

        ok = self.symbol_table.declare(var_name, type_str, is_array=is_array, line=tok.line, col=tok.column)
        if not ok:
            self._err(tok.line, tok.column,
                      f"Variable '{var_name}' ya declarada en este ámbito.")
        return None

    def visitAssignment(self, ctx: Language_v3Parser.AssignmentContext):
        var_name = ctx.ID().getText()
        tok = ctx.ID().getSymbol()

        entry = self.symbol_table.lookup(var_name)
        if entry is None:
            self._err(tok.line, tok.column,
                      f"Variable '{var_name}' no declarada.")
            return None

        expr_type = self._infer(ctx.expr())
        
        # Si es asignación a índice: ID '[' expr ']' '=' expr
        if len(ctx.expr()) == 2:
            if not entry.get('is_array'):
                self._err(tok.line, tok.column, f"La variable '{var_name}' no es un arreglo.")
            else:
                idx_type = self._infer(ctx.expr(0))
                val_type = self._infer(ctx.expr(1))
                if idx_type != 'int':
                    self._err(ctx.expr(0).start.line, ctx.expr(0).start.column, "El índice debe ser int.")
                if val_type != entry['element_type']:
                    self._err(tok.line, tok.column, 
                              f"No se puede asignar '{val_type}' a un elemento de tipo '{entry['element_type']}'.")
        else:
            if expr_type is not None:
                if expr_type == 'void[]' and entry.get('is_array'):
                    pass
                elif expr_type != entry['type']:
                    self._err(tok.line, tok.column,
                              f"Incompatibilidad de tipos. No se puede asignar "
                              f"'{expr_type}' a '{entry['type']}'.")
        return None

    def visitFunction(self, ctx: Language_v3Parser.FunctionContext):
        return_type = ctx.varType().getText()
        func_name = ctx.ID().getText()
        tok = ctx.ID().getSymbol()

        params = []
        if ctx.argsFunction():
            af = ctx.argsFunction()
            types = [t.getText() for t in af.varType()]
            names = [n.getText() for n in af.ID()]
            params = list(zip(types, names))

        self.symbol_table.declare_function(func_name, return_type, params)

        self.symbol_table.push_scope()
        for ptype, pname in params:
            self.symbol_table.declare(pname, ptype, is_array=ptype.endswith('[]'))

        prev_return_type = self.current_function_return_type
        self.current_function_return_type = return_type

        self.visit(ctx.block())

        self.current_function_return_type = prev_return_type
        self.symbol_table.pop_scope()
        return None
