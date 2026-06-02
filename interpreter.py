"""
interpreter.py
--------------
Visitor de EJECUCIÓN para Fase 3 (v3).
Soporta arreglos, módulo, break/continue e imports.
"""

import math
from Language_v4Visitor import Language_v4Visitor
from Language_v4Parser import Language_v4Parser


# ── Excepciones de control de flujo ──────────────────────────────────────────

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass


# ── Intérprete ────────────────────────────────────────────────────────────────

class Interpreter(Language_v4Visitor):

    def __init__(self):
        self.global_env: dict = {
            "abs": lambda n: abs(n),
            "pow": lambda b, e: math.pow(b, e),
            "sqrt": lambda n: math.sqrt(n)
        }
        self.functions: dict = {}
        self.struct_defs: dict = {}
        self.call_stack: list[dict] = []

    # ── Manejo de variables ──────────────────────────────────────────────────

    def _declare_var(self, name: str, value):
        if self.call_stack:
            self.call_stack[-1][name] = value
        else:
            self.global_env[name] = value

    def _lookup_var(self, name: str):
        if self.call_stack and name in self.call_stack[-1]:
            return self.call_stack[-1][name]
        if name in self.global_env:
            return self.global_env[name]
        raise NameError(f"Variable '{name}' no definida.")

    def _set_var(self, name: str, value):
        if self.call_stack and name in self.call_stack[-1]:
            self.call_stack[-1][name] = value
            return
        if name in self.global_env:
            self.global_env[name] = value
            return
        raise NameError(f"Variable '{name}' no declarada.")

    # ── Nodos de estructura ───────────────────────────────────────────────────

    def visitProgram(self, ctx: Language_v4Parser.ProgramContext):
        return self.visitChildren(ctx)

    def visitImportStmt(self, ctx: Language_v4Parser.ImportStmtContext):
        return None # Ya se manejó en el semántico (registro de funciones)

    def visitDeclaration(self, ctx: Language_v4Parser.DeclarationContext):
        return self.visitChildren(ctx)

    def visitStatement(self, ctx: Language_v4Parser.StatementContext):
        return self.visitChildren(ctx)

    def visitBlock(self, ctx: Language_v4Parser.BlockContext):
        return self.visitChildren(ctx)

    # ── Declaración y asignación ──────────────────────────────────────────────

    def visitVariable(self, ctx: Language_v4Parser.VariableContext):
        var_name = ctx.ID().getText()
        if ctx.expr():
            value = self.visit(ctx.expr())
        else:
            type_str = ctx.varType().getText()
            if type_str.endswith('[]'):
                value = []
            else:
                defaults = {'int': 0, 'float': 0.0, 'string': '', 'bool': False}
                value = defaults.get(type_str, None)
        self._declare_var(var_name, value)
        return value

    def visitAssignment(self, ctx: Language_v4Parser.AssignmentContext):
        var_name = ctx.ID().getText()
        
        # Asignación a índice: ID '[' expr ']' '=' expr
        if len(ctx.expr()) == 2:
            idx = self.visit(ctx.expr(0))
            val = self.visit(ctx.expr(1))
            arr = self._lookup_var(var_name)
            if not isinstance(arr, list):
                raise TypeError(f"'{var_name}' no es un arreglo.")
            arr[idx] = val
            return val
        else:
            value = self.visit(ctx.expr(0))
            self._set_var(var_name, value)
            return value

    # ── Funciones ─────────────────────────────────────────────────────────────

    def visitFunction(self, ctx: Language_v4Parser.FunctionContext):
        func_name = ctx.ID().getText()
        self.functions[func_name] = ctx
        return None

    def visitFunctionCall(self, ctx: Language_v4Parser.FunctionCallContext):
        func_name = ctx.ID().getText()
        
        # Caso funciones built-in
        if func_name in self.global_env and callable(self.global_env[func_name]):
            args_ctx = ctx.args()
            arg_values = [self.visit(e) for e in args_ctx.expr()] if args_ctx else []
            return self.global_env[func_name](*arg_values)

        func_ctx = self.functions.get(func_name)
        if func_ctx is None:
            raise NameError(f"Función '{func_name}' no definida.")

        args_ctx = ctx.args()
        arg_values = [self.visit(e) for e in args_ctx.expr()] if args_ctx else []

        params = []
        if func_ctx.argsFunction():
            params = [n.getText() for n in func_ctx.argsFunction().ID()]

        frame = {pname: val for pname, val in zip(params, arg_values)}
        self.call_stack.append(frame)

        result = None
        try:
            self.visit(func_ctx.block())
        except ReturnException as ret:
            result = ret.value
        finally:
            self.call_stack.pop()

        return result

    def visitReturnStmt(self, ctx: Language_v4Parser.ReturnStmtContext):
        value = self.visit(ctx.expr()) if ctx.expr() else None
        raise ReturnException(value)

    # ── Control de flujo ─────────────────────────────────────────────────────

    def visitConditional(self, ctx: Language_v4Parser.ConditionalContext):
        if self.visit(ctx.condition()):
            return self.visit(ctx.block(0))
        elif ctx.block(1) is not None:
            return self.visit(ctx.block(1))
        return None

    def visitWhileStmt(self, ctx: Language_v4Parser.WhileStmtContext):
        while self.visit(ctx.condition()):
            try:
                self.visit(ctx.block())
            except BreakException:
                break
            except ContinueException:
                continue
        return None

    def visitForStmt(self, ctx: Language_v4Parser.ForStmtContext):
        # Init
        if ctx.variable():
            self.visit(ctx.variable())
        elif ctx.assignment():
            self.visit(ctx.assignment(0))

        has_var_init = ctx.variable() is not None
        assignments = list(ctx.assignment()) if ctx.assignment() else []
        if has_var_init:
            step = assignments[0] if assignments else None
        else:
            step = assignments[1] if len(assignments) >= 2 else None

        while True:
            # Evaluar condición si existe (puede ser ctx.condition() o ctx.expr())
            cond_val = True
            if ctx.condition():
                cond_val = self.visit(ctx.condition())
            elif ctx.expr():
                cond_val = self.visit(ctx.expr())
            
            if not cond_val:
                break
            try:
                self.visit(ctx.statement())
            except BreakException:
                break
            except ContinueException:
                pass # Sigue al step
            
            if step:
                self.visit(step)
        return None

    def visitBreakStmt(self, ctx: Language_v4Parser.BreakStmtContext):
        raise BreakException()

    def visitContinueStmt(self, ctx: Language_v4Parser.ContinueStmtContext):
        raise ContinueException()

    def visitPrintStmt(self, ctx: Language_v4Parser.PrintStmtContext):
        value = self.visit(ctx.expr())
        print(value)
        return value

    # ── Condiciones ───────────────────────────────────────────────────────────

    def visitAndOr(self, ctx: Language_v4Parser.AndOrContext):
        left = self.visit(ctx.condition(0))
        right = self.visit(ctx.condition(1))
        op = ctx.op.text
        if op == '&&':
            return bool(left) and bool(right)
        return bool(left) or bool(right)

    def visitComparison(self, ctx: Language_v4Parser.ComparisonContext):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        op = ctx.op.text
        ops = {
            '>':  left > right,
            '<':  left < right,
            '==': left == right,
            '!=': left != right,
            '>=': left >= right,
            '<=': left <= right,
        }
        return ops.get(op, False)

    def visitParensCond(self, ctx: Language_v4Parser.ParensCondContext):
        return self.visit(ctx.condition())

    # ── Expresiones ──────────────────────────────────────────────────────────

    def visitMulDivMod(self, ctx: Language_v4Parser.MulDivModContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.text
        if op == '*': return left * right
        if right == 0: raise ZeroDivisionError("División por cero.")
        if op == '/':
            if isinstance(left, int) and isinstance(right, int) and left % right == 0:
                return left // right
            return left / right
        if op == '%': return left % right
        return None

    def visitAddSub(self, ctx: Language_v4Parser.AddSubContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        return (left + right) if ctx.op.text == '+' else (left - right)

    def visitParens(self, ctx: Language_v4Parser.ParensContext):
        return self.visit(ctx.expr())

    def visitArrayAccess(self, ctx: Language_v4Parser.ArrayAccessContext):
        arr = self._lookup_var(ctx.ID().getText())
        idx = self.visit(ctx.expr())
        return arr[idx]

    def visitArrayLit(self, ctx: Language_v4Parser.ArrayLitContext):
        return [self.visit(e) for e in ctx.expr()]

    def visitArrayNew(self, ctx: Language_v4Parser.ArrayNewContext):
        size = self.visit(ctx.expr())
        base_type = ctx.getChild(0).getText()
        defaults = {'int': 0, 'float': 0.0, 'string': '', 'bool': False}
        return [defaults.get(base_type, None)] * size

# ── convierte un valor a un tipo ─────────────────────────────────────────────────────

    def visitCastExpr(self, ctx: Language_v4Parser.CastExprContext):
        value = self.visit(ctx.expr())
        target_type = ctx.varType().getText().replace('[]', '')
        casts = {
            'int': int,
            'float': float,
            'string': str,
            'bool': bool,
        }
        return casts.get(target_type, lambda v: v)(value)

    def visitTernaryCompare(self, ctx: Language_v4Parser.TernaryCompareContext):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        op = ctx.op.text
        cond = {
            '>': left > right,
            '<': left < right,
            '==': left == right,
            '!=': left != right,
            '>=': left >= right,
            '<=': left <= right,
        }.get(op, False)
        return self.visit(ctx.expr(2)) if cond else self.visit(ctx.expr(3))

    def visitTernaryParensCond(self, ctx: Language_v4Parser.TernaryParensCondContext):
        return self.visit(ctx.expr(0)) if self.visit(ctx.condition()) else self.visit(ctx.expr(1))

    def visitTernarySimple(self, ctx: Language_v4Parser.TernarySimpleContext):
        return self.visit(ctx.expr(1)) if self.visit(ctx.expr(0)) else self.visit(ctx.expr(2))



    def visitId(self, ctx: Language_v4Parser.IdContext):
        return self._lookup_var(ctx.ID().getText())

    def visitInt(self, ctx: Language_v4Parser.IntContext):
        return int(ctx.NUMBER().getText())

    def visitFloatExpr(self, ctx: Language_v4Parser.FloatExprContext):
        return float(ctx.FLOAT().getText())

    def visitStringExpr(self, ctx: Language_v4Parser.StringExprContext):
        raw = ctx.STRING().getText()
        return raw[1:-1]

    def visitBoolExpr(self, ctx: Language_v4Parser.BoolExprContext):
        return ctx.BOOL().getText() == 'true'

    def visitArgs(self, ctx: Language_v4Parser.ArgsContext):
        return [self.visit(e) for e in ctx.expr()]


# ── Structs y switch ─────────────────────────────────────────────────────

    def _default_value_for_type(self, type_name: str):
        return {'int': 0, 'float': 0.0, 'string': '', 'bool': False}.get(type_name, None)

    def visitStructDecl(self, ctx: Language_v4Parser.StructDeclContext):
        struct_name = ctx.ID(0).getText()
        fields = {}
        for i, var_type in enumerate(ctx.varType()):
            fields[ctx.ID(i + 1).getText()] = var_type.getText()
        self.struct_defs[struct_name] = fields
        return None

    def visitStructVar(self, ctx: Language_v4Parser.StructVarContext):
        struct_name = ctx.ID(0).getText()
        var_name = ctx.ID(1).getText()
        fields = self.struct_defs.get(struct_name, {})
        value = {
            field_name: self._default_value_for_type(field_type)
            for field_name, field_type in fields.items()
        }
        self._declare_var(var_name, value)
        return value

    def visitFieldAssign(self, ctx: Language_v4Parser.FieldAssignContext):
        var_name = ctx.ID(0).getText()
        field_name = ctx.ID(1).getText()
        struct_value = self._lookup_var(var_name)
        value = self.visit(ctx.expr())
        struct_value[field_name] = value
        return value

    def visitStructFieldAccess(self, ctx: Language_v4Parser.StructFieldAccessContext):
        return self.visit(ctx.fieldAccess())

    def visitFieldAccess(self, ctx: Language_v4Parser.FieldAccessContext):
        var_name = ctx.ID(0).getText()
        field_name = ctx.ID(1).getText()
        return self._lookup_var(var_name)[field_name]

    def visitSwitchStmt(self, ctx: Language_v4Parser.SwitchStmtContext):
        switch_value = self.visit(ctx.expr())
        matched = False

        try:
            for case_ctx in ctx.caseClause():
                if matched or self.visit(case_ctx.expr()) == switch_value:
                    matched = True
                    self.visitCaseClause(case_ctx)

            if not matched and ctx.defaultClause():
                self.visit(ctx.defaultClause())
        except BreakException:
            return None
        return None

    def visitCaseClause(self, ctx: Language_v4Parser.CaseClauseContext):
        for statement in ctx.statement():
            self.visit(statement)
        if ctx.breakStmt():
            self.visit(ctx.breakStmt())
        return None

    def visitDefaultClause(self, ctx: Language_v4Parser.DefaultClauseContext):
        for statement in ctx.statement():
            self.visit(statement)
        return None        