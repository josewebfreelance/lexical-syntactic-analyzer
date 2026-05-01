"""
interpreter.py
--------------
Visitor de EJECUCIÓN.
"""

# >>> ADDED
import math

from LanguageVisitor import LanguageVisitor
from LanguageParser import LanguageParser


# ── Excepción especial para return ────────────────────────────────────────────

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


# >>> ADDED
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass


# ── Intérprete ────────────────────────────────────────────────────────────────

class Interpreter(LanguageVisitor):

    def __init__(self):
        self.global_env: dict = {}
        self.functions: dict = {}
        self.call_stack: list[dict] = []

        # >>> ADDED
        self.global_env.update({
            "abs": lambda n: abs(n),
            "pow": lambda b, e: math.pow(b, e),
            "sqrt": lambda n: math.sqrt(n)
        })

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
        raise NameError(f"[Error Runtime] Variable '{name}' no definida en el scope actual.")

    def _set_var(self, name: str, value):
        if self.call_stack and name in self.call_stack[-1]:
            self.call_stack[-1][name] = value
            return
        if name in self.global_env:
            self.global_env[name] = value
            return
        raise NameError(f"[Error Runtime] Variable '{name}' no declarada.")

    # ── Nodos de estructura ───────────────────────────────────────────────────

    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.visitChildren(ctx)

    def visitDeclaration(self, ctx: LanguageParser.DeclarationContext):
        return self.visitChildren(ctx)

    def visitStatement(self, ctx: LanguageParser.StatementContext):
        return self.visitChildren(ctx)

    def visitBlock(self, ctx: LanguageParser.BlockContext):
        return self.visitChildren(ctx)

    # ── Declaración y asignación ──────────────────────────────────────────────

    def visitVariable(self, ctx: LanguageParser.VariableContext):
        var_name = ctx.ID().getText()
        if ctx.expr():
            value = self.visit(ctx.expr())
        else:
            defaults = {'int': 0, 'float': 0.0, 'string': '', 'bool': False}
            value = defaults.get(ctx.type_().getText(), None)
        self._declare_var(var_name, value)
        return value

    def visitAssignment(self, ctx: LanguageParser.AssignmentContext):
        var_name = ctx.ID().getText()

        # >>> ADDED (soporte array assignment)
        if len(ctx.expr()) == 2:
            idx = self.visit(ctx.expr(0))
            val = self.visit(ctx.expr(1))
            arr = self._lookup_var(var_name)
            if not isinstance(arr, list):
                raise TypeError(f"'{var_name}' no es un arreglo.")
            arr[idx] = val
            return val

        value = self.visit(ctx.expr())
        self._set_var(var_name, value)
        return value

    # ── Funciones ─────────────────────────────────────────────────────────────

    def visitFunction(self, ctx: LanguageParser.FunctionContext):
        func_name = ctx.ID().getText()
        self.functions[func_name] = ctx
        return None

    def visitFunctionCall(self, ctx: LanguageParser.FunctionCallContext):
        func_name = ctx.ID().getText()

        # >>> ADDED (built-ins)
        if func_name in self.global_env and callable(self.global_env[func_name]):
            args_ctx = ctx.args()
            arg_values = []
            if args_ctx:
                for arg_expr in args_ctx.expr():
                    arg_values.append(self.visit(arg_expr))
            return self.global_env[func_name](*arg_values)

        func_ctx = self.functions.get(func_name)
        if func_ctx is None:
            raise NameError(f"[Error Runtime] Función '{func_name}' no definida.")

        args_ctx = ctx.args()
        arg_values = []
        if args_ctx:
            for arg_expr in args_ctx.expr():
                arg_values.append(self.visit(arg_expr))

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

    def visitReturnStmt(self, ctx: LanguageParser.ReturnStmtContext):
        value = self.visit(ctx.expr()) if ctx.expr() else None
        raise ReturnException(value)

    # ── Control de flujo ─────────────────────────────────────────────────────

    def visitConditional(self, ctx: LanguageParser.ConditionalContext):
        if self.visit(ctx.condition()):
            return self.visit(ctx.block(0))
        elif ctx.block(1) is not None:
            return self.visit(ctx.block(1))
        return None

    def visitWhileStmt(self, ctx: LanguageParser.WhileStmtContext):
        while self.visit(ctx.condition()):
            try:
                self.visit(ctx.block())
            except BreakException:
                break
            except ContinueException:
                continue
            except ReturnException:
                raise
        return None

    def visitForStmt(self, ctx: LanguageParser.ForStmtContext):
        if ctx.variable():
            self.visit(ctx.variable())
        else:
            assignments = ctx.assignment()
            if assignments and len(assignments) > 0:
                self.visit(assignments[0])

        has_var_init = ctx.variable() is not None
        assignments = list(ctx.assignment()) if ctx.assignment() else []

        if has_var_init:
            step = assignments[0] if assignments else None
        else:
            step = assignments[1] if len(assignments) >= 2 else None

        while True:
            if ctx.expr():
                if not self.visit(ctx.expr()):
                    break
            try:
                self.visit(ctx.statement())
            except BreakException:
                break
            except ContinueException:
                pass
            except ReturnException:
                raise
            if step:
                self.visit(step)

        return None

    # >>> ADDED
    def visitBreakStmt(self, ctx: LanguageParser.BreakStmtContext):
        raise BreakException()

    def visitContinueStmt(self, ctx: LanguageParser.ContinueStmtContext):
        raise ContinueException()

    def visitPrintStmt(self, ctx: LanguageParser.PrintStmtContext):
        value = self.visit(ctx.expr())
        print(value)
        return value

    # ── Condiciones ───────────────────────────────────────────────────────────

    def visitAndOr(self, ctx: LanguageParser.AndOrContext):
        left = self.visit(ctx.condition(0))
        right = self.visit(ctx.condition(1))
        op = ctx.op.text
        if op == '&&':
            return bool(left) and bool(right)
        return bool(left) or bool(right)

    def visitComparison(self, ctx: LanguageParser.ComparisonContext):
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

    def visitParensCond(self, ctx: LanguageParser.ParensCondContext):
        return self.visit(ctx.condition())

    # ── Expresiones ──────────────────────────────────────────────────────────

    def visitMulDiv(self, ctx: LanguageParser.MulDivContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.text
        if op == '*':
            return left * right
        if right == 0:
            raise ZeroDivisionError("[Error Runtime] División por cero.")
        if isinstance(left, int) and isinstance(right, int) and left % right == 0:
            return left // right
        return left / right

    def visitAddSub(self, ctx: LanguageParser.AddSubContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        return (left + right) if ctx.op.text == '+' else (left - right)

    def visitParens(self, ctx: LanguageParser.ParensContext):
        return self.visit(ctx.expr())

    # >>> ADDED (arrays)
    def visitArrayAccess(self, ctx: LanguageParser.ArrayAccessContext):
        arr = self._lookup_var(ctx.ID().getText())
        idx = self.visit(ctx.expr())
        return arr[idx]

    def visitArrayLit(self, ctx: LanguageParser.ArrayLitContext):
        return [self.visit(e) for e in ctx.expr()]

    def visitArrayNew(self, ctx: LanguageParser.ArrayNewContext):
        size = self.visit(ctx.expr())
        base_type = ctx.getChild(0).getText()
        defaults = {'int': 0, 'float': 0.0, 'string': '', 'bool': False}
        return [defaults.get(base_type, None)] * size

    def visitId(self, ctx: LanguageParser.IdContext):
        return self._lookup_var(ctx.ID().getText())

    def visitInt(self, ctx: LanguageParser.IntContext):
        return int(ctx.NUMBER().getText())

    def visitFloatExpr(self, ctx: LanguageParser.FloatExprContext):
        return float(ctx.FLOAT().getText())

    def visitStringExpr(self, ctx: LanguageParser.StringExprContext):
        raw = ctx.STRING().getText()
        return raw[1:-1]

    def visitBoolExpr(self, ctx: LanguageParser.BoolExprContext):
        return ctx.BOOL().getText() == 'true'

    def visitArgs(self, ctx: LanguageParser.ArgsContext):
        return [self.visit(e) for e in ctx.expr()]

