"""
interpreter_visitor.py  (clase: Interpreter)
---------------------------------------------
Visitor de EJECUCIÓN. Solo se llama cuando el SemanticVisitor terminó con 0 errores.
Usa un call stack de frames para soportar recursividad real:
  - self.global_env  : variables globales {name: value}
  - self.functions   : funciones registradas {name: FunctionContext}
  - self.call_stack  : pila de frames locales [{name: value}, ...]

La búsqueda de variables sigue el orden:
  frame_actual → global_env → NameError
"""

from LanguageVisitor import LanguageVisitor
from LanguageParser import LanguageParser


# ── Excepción especial para return ────────────────────────────────────────────

class ReturnException(Exception):
    """Usado para cortar la ejecución de un bloque de función al encontrar return."""
    def __init__(self, value):
        self.value = value


# ── Intérprete ────────────────────────────────────────────────────────────────

class Interpreter(LanguageVisitor):

    def __init__(self):
        self.global_env: dict = {}         # Variables globales
        self.functions: dict = {}          # Funciones registradas
        self.call_stack: list[dict] = []   # Stack de frames locales

    # ── Manejo de variables con scopes ───────────────────────────────────────

    def _declare_var(self, name: str, value):
        """Declara (o sobreescribe si ya existe) una variable en el scope actual."""
        if self.call_stack:
            self.call_stack[-1][name] = value
        else:
            self.global_env[name] = value

    def _lookup_var(self, name: str):
        """Busca una variable: frame actual → global. Lanza NameError si no existe."""
        if self.call_stack and name in self.call_stack[-1]:
            return self.call_stack[-1][name]
        if name in self.global_env:
            return self.global_env[name]
        raise NameError(
            f"[Error Runtime] Variable '{name}' no definida en el scope actual.")

    def _set_var(self, name: str, value):
        """Actualiza el valor de una variable existente (frame actual o global)."""
        if self.call_stack and name in self.call_stack[-1]:
            self.call_stack[-1][name] = value
            return
        if name in self.global_env:
            self.global_env[name] = value
            return
        raise NameError(
            f"[Error Runtime] Variable '{name}' no declarada. Usa una declaración primero.")

    # ── Nodos de estructura ───────────────────────────────────────────────────

    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.visitChildren(ctx)

    def visitDeclaration(self, ctx: LanguageParser.DeclarationContext):
        return self.visitChildren(ctx)

    def visitStatement(self, ctx: LanguageParser.StatementContext):
        return self.visitChildren(ctx)

    def visitBlock(self, ctx: LanguageParser.BlockContext):
        """Ejecuta instrucciones del bloque en orden. No crea un frame nuevo
        (el frame de función ya está activo; las variables locales comparten frame)."""
        return self.visitChildren(ctx)

    # ── Declaración y asignación ──────────────────────────────────────────────

    def visitVariable(self, ctx: LanguageParser.VariableContext):
        """int x; o int x = expr; — declara y asigna en el scope actual."""
        var_name = ctx.ID().getText()
        if ctx.expr():
            value = self.visit(ctx.expr())
        else:
            # Valor por defecto según el tipo declarado (int x; → x = 0)
            defaults = {'int': 0, 'float': 0.0, 'string': '', 'bool': False}
            value = defaults.get(ctx.type_().getText(), None)
        self._declare_var(var_name, value)
        return value

    def visitAssignment(self, ctx: LanguageParser.AssignmentContext):
        """x = expr; — actualiza variable ya declarada."""
        var_name = ctx.ID().getText()
        value = self.visit(ctx.expr())
        self._set_var(var_name, value)
        return value

    # ── Funciones ─────────────────────────────────────────────────────────────

    def visitFunction(self, ctx: LanguageParser.FunctionContext):
        """Registra la función en el directorio. No la ejecuta."""
        func_name = ctx.ID().getText()
        self.functions[func_name] = ctx
        return None

    def visitFunctionCall(self, ctx: LanguageParser.FunctionCallContext):
        """
        Llama una función:
        1. Evalúa argumentos en el scope ACTUAL (antes de cambiar de frame).
        2. Crea un nuevo frame con los parámetros.
        3. Ejecuta el bloque de la función.
        4. Captura ReturnException y retorna su valor.
        5. Limpia el frame al terminar (finally).
        """
        func_name = ctx.ID().getText()
        func_ctx = self.functions.get(func_name)
        if func_ctx is None:
            raise NameError(f"[Error Runtime] Función '{func_name}' no definida.")

        # 1 — Evaluar argumentos en el scope actual
        args_ctx = ctx.args()
        arg_values = []
        if args_ctx:
            for arg_expr in args_ctx.expr():
                arg_values.append(self.visit(arg_expr))

        # 2 — Obtener nombres de parámetros
        params = []
        if func_ctx.argsFunction():
            params = [n.getText() for n in func_ctx.argsFunction().ID()]

        # 3 — Nuevo frame con los argumentos ligados a los parámetros
        frame = {pname: val for pname, val in zip(params, arg_values)}
        self.call_stack.append(frame)

        result = None
        try:
            # 4 — Ejecutar el bloque de la función
            self.visit(func_ctx.block())
        except ReturnException as ret:
            result = ret.value
        finally:
            # 5 — Siempre limpiar el frame, incluso si hubo excepción
            self.call_stack.pop()

        return result

    def visitReturnStmt(self, ctx: LanguageParser.ReturnStmtContext):
        """Evalúa la expresión y lanza ReturnException para cortar la ejecución."""
        value = self.visit(ctx.expr()) if ctx.expr() else None
        raise ReturnException(value)

    # ── Control de flujo ─────────────────────────────────────────────────────

    def visitConditional(self, ctx: LanguageParser.ConditionalContext):
        """if (cond) block [else block]"""
        if self.visit(ctx.condition()):
            return self.visit(ctx.block(0))
        elif ctx.block(1) is not None:
            return self.visit(ctx.block(1))
        return None

    def visitWhileStmt(self, ctx: LanguageParser.WhileStmtContext):
        """while (cond) block — re-evalúa la condición en cada iteración."""
        while self.visit(ctx.condition()):
            try:
                self.visit(ctx.block())
            except ReturnException:
                raise  # Propagar return fuera del while hacia la función
        return None

    def visitForStmt(self, ctx: LanguageParser.ForStmtContext):
        """
        for (init; cond; step) statement
        Nota: 'cond' en la gramática actual es un expr (no condition).
        """
        # Init
        if ctx.variable():
            self.visit(ctx.variable())
        else:
            assignments = ctx.assignment()
            if assignments and len(assignments) > 0:
                # Si hay variable de init, todos los assignment son step;
                # si no hay variable, el primer assignment es el init
                self.visit(assignments[0])

        has_var_init = ctx.variable() is not None
        assignments = list(ctx.assignment()) if ctx.assignment() else []

        # Determinar cuál es el step
        if has_var_init:
            step = assignments[0] if assignments else None
        else:
            step = assignments[1] if len(assignments) >= 2 else None

        # Loop
        while True:
            if ctx.expr():
                if not self.visit(ctx.expr()):
                    break
            try:
                self.visit(ctx.statement())
            except ReturnException:
                raise
            if step:
                self.visit(step)

        return None

    def visitPrintStmt(self, ctx: LanguageParser.PrintStmtContext):
        """Imprime el valor de la expresión."""
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

    # ── Expresiones aritméticas ───────────────────────────────────────────────

    def visitMulDiv(self, ctx: LanguageParser.MulDivContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.text
        if op == '*':
            return left * right
        if right == 0:
            raise ZeroDivisionError("[Error Runtime] División por cero.")
        # Mantener int si ambos son int y es divisible; float si no
        if isinstance(left, int) and isinstance(right, int) and left % right == 0:
            return left // right
        return left / right

    def visitAddSub(self, ctx: LanguageParser.AddSubContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        return (left + right) if ctx.op.text == '+' else (left - right)

    def visitParens(self, ctx: LanguageParser.ParensContext):
        return self.visit(ctx.expr())

    # ── Literales ─────────────────────────────────────────────────────────────

    def visitInt(self, ctx: LanguageParser.IntContext):
        return int(ctx.NUMBER().getText())

    def visitFloatExpr(self, ctx: LanguageParser.FloatExprContext):
        return float(ctx.FLOAT().getText())

    def visitStringExpr(self, ctx: LanguageParser.StringExprContext):
        # Eliminar las comillas dobles: "hello" → hello
        raw = ctx.STRING().getText()
        return raw[1:-1]

    def visitBoolExpr(self, ctx: LanguageParser.BoolExprContext):
        return ctx.BOOL().getText() == 'true'

    # ── Identificadores y argumentos ─────────────────────────────────────────

    def visitId(self, ctx: LanguageParser.IdContext):
        return self._lookup_var(ctx.ID().getText())

    def visitArgs(self, ctx: LanguageParser.ArgsContext):
        return [self.visit(e) for e in ctx.expr()]
