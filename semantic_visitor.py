   # ── Declaraciones ────────────────────────────────────────────────────────

    def visitVariable(self, ctx: LanguageParser.VariableContext):
        type_str = ctx.type_().getText()
        var_name = ctx.ID().getText()
        tok = ctx.ID().getSymbol()

        # Solo validar tipo si hay inicializador (int x = expr;)
        if ctx.expr():
            expr_type = self._infer(ctx.expr())
            if expr_type is not None and expr_type != type_str:
                self._err(tok.line, tok.column,
                          f"Incompatibilidad de tipos. No se puede asignar "
                          f"'{expr_type}' a '{type_str}'.")

        ok = self.symbol_table.declare(var_name, type_str, tok.line, tok.column)
        if not ok:
            self._err(tok.line, tok.column,
                      f"Variable '{var_name}' ya declarada en este ámbito.")
        return None

    def visitAssignment(self, ctx: LanguageParser.AssignmentContext):
        var_name = ctx.ID().getText()
        tok = ctx.ID().getSymbol()

        entry = self.symbol_table.lookup(var_name)
        if entry is None:
            self._err(tok.line, tok.column,
                      f"Variable '{var_name}' no declarada.")
            return None

        expr_type = self._infer(ctx.expr())
        if expr_type is not None and expr_type != entry['type']:
            self._err(tok.line, tok.column,
                      f"Incompatibilidad de tipos. No se puede asignar "
                      f"'{expr_type}' a '{entry['type']}'.")
        return None

    def visitFunction(self, ctx: LanguageParser.FunctionContext):
        return_type = ctx.type_().getText()
        func_name = ctx.ID().getText()
        tok = ctx.ID().getSymbol()

        # Recopilar parámetros
        params = []
        if ctx.argsFunction():
            af = ctx.argsFunction()
            types = [t.getText() for t in af.type_()]
            names = [n.getText() for n in af.ID()]
            params = list(zip(types, names))

        # Registrar función ANTES de procesar el cuerpo (permite recursividad)
        self.symbol_table.declare_function(func_name, return_type, params)

        # Nuevo scope para los parámetros
        self.symbol_table.push_scope()
        for ptype, pname in params:
            self.symbol_table.declare(pname, ptype)

        # Entrar al scope de la función y validar cuerpo
        prev_return_type = self.current_function_return_type
        self.current_function_return_type = return_type

        self.visit(ctx.block())   # visitBlock() hace push/pop del body scope

        self.current_function_return_type = prev_return_type
        self.symbol_table.pop_scope()
        return None

    # ── Bloques y control de flujo ────────────────────────────────────────────

    def visitBlock(self, ctx: LanguageParser.BlockContext):
        self.symbol_table.push_scope()
        self.visitChildren(ctx)
        self.symbol_table.pop_scope()
        return None

    def visitConditional(self, ctx: LanguageParser.ConditionalContext):
        self.visit(ctx.condition())
        for block in ctx.block():
            self.visit(block)
        return None

    def visitWhileStmt(self, ctx: LanguageParser.WhileStmtContext):
        self.visit(ctx.condition())
        self.visit(ctx.block())
        return None

    def visitForStmt(self, ctx: LanguageParser.ForStmtContext):
        # Abrimos un scope para que la variable del init sea local al for
        self.symbol_table.push_scope()
        self.visitChildren(ctx)
        self.symbol_table.pop_scope()
        return None

    def visitReturnStmt(self, ctx: LanguageParser.ReturnStmtContext):
        if self.current_function_return_type is None:
            return None  # return fuera de función (la gramática lo previene)

        if ctx.expr():
            expr_type = self._infer(ctx.expr())
            if self.current_function_return_type == 'void':
                self._err(ctx.start.line, ctx.start.column,
                          "Una función 'void' no puede retornar un valor.")
            elif expr_type is not None and expr_type != self.current_function_return_type:
                self._err(ctx.start.line, ctx.start.column,
                          f"Tipo de retorno incorrecto. Se esperaba "
                          f"'{self.current_function_return_type}' "
                          f"pero se retornó '{expr_type}'.")
        else:
            if self.current_function_return_type != 'void':
                self._err(ctx.start.line, ctx.start.column,
                          f"La función debe retornar un valor de tipo "
                          f"'{self.current_function_return_type}'.")
        return None

    def visitPrintStmt(self, ctx: LanguageParser.PrintStmtContext):
        self._infer(ctx.expr())  # Solo valida que la expresión sea válida
        return None

    # ── Condiciones ───────────────────────────────────────────────────────────

    def visitComparison(self, ctx: LanguageParser.ComparisonContext):
        lt = self._infer(ctx.expr(0))
        rt = self._infer(ctx.expr(1))
        if lt is not None and rt is not None and lt != rt:
            self._err(ctx.op.line, ctx.op.column,
                      f"Incompatibilidad de tipos en comparación "
                      f"'{ctx.op.text}': '{lt}' y '{rt}'.")
        return None

    def visitAndOr(self, ctx: LanguageParser.AndOrContext):
        self.visit(ctx.condition(0))
        self.visit(ctx.condition(1))
        return None

    def visitParensCond(self, ctx: LanguageParser.ParensCondContext):
        return self.visit(ctx.condition())

    # ── Expresiones (delegamos a _infer que ya valida) ─────────────────────

    def visitMulDiv(self, ctx: LanguageParser.MulDivContext):
        self._infer(ctx)
        return None

    def visitAddSub(self, ctx: LanguageParser.AddSubContext):
        self._infer(ctx)
        return None

    def visitParens(self, ctx: LanguageParser.ParensContext):
        self._infer(ctx)
        return None

    def visitFunctionCall(self, ctx: LanguageParser.FunctionCallContext):
        self._infer(ctx)
        return None

    def visitId(self, ctx: LanguageParser.IdContext):
        self._infer(ctx)
        return None

    def visitInt(self, ctx: LanguageParser.IntContext):
        return None

    def visitFloatExpr(self, ctx: LanguageParser.FloatExprContext):
        return None

    def visitStringExpr(self, ctx: LanguageParser.StringExprContext):
        return None

    def visitBoolExpr(self, ctx: LanguageParser.BoolExprContext):
        return None

    def visitArgs(self, ctx: LanguageParser.ArgsContext):
        return self.visitChildren(ctx)
