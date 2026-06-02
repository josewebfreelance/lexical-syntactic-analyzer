"""
tac_generator.py
----------------
Generador de Código de Tres Direcciones (TAC).
"""

from Language_v4Visitor import Language_v4Visitor
from Language_v4Parser import Language_v4Parser

class TACGenerator(Language_v4Visitor):
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0
        self.loop_stack = [] # [(start_label, end_label)]
        self.switch_stack = [] # [end_label]

    def new_temp(self) -> str:
        name = f"t{self.temp_count}"
        self.temp_count += 1
        return name

    def new_label(self) -> str:
        name = f"L{self.label_count}"
        self.label_count += 1
        return name

    def emit(self, instr: str):
        self.instructions.append(instr)

    def get_output(self) -> str:
        return "\n".join(self.instructions)

    # ── Nodos ────────────────────────────────────────────────────────────────

    def visitProgram(self, ctx: Language_v4Parser.ProgramContext):
        self.visitChildren(ctx)
        return None

    def visitVariable(self, ctx: Language_v4Parser.VariableContext):
        name = ctx.ID().getText()
        if ctx.expr():
            res = self.visit(ctx.expr())
            self.emit(f"{name} = {res}")
        return None

    def visitAssignment(self, ctx: Language_v4Parser.AssignmentContext):
        name = ctx.ID().getText()
        if len(ctx.expr()) == 2:
            idx = self.visit(ctx.expr(0))
            val = self.visit(ctx.expr(1))
            self.emit(f"{name}[{idx}] = {val}")
        else:
            val = self.visit(ctx.expr(0))
            self.emit(f"{name} = {val}")
        return None

    def visitFunction(self, ctx: Language_v4Parser.FunctionContext):
        name = ctx.ID().getText()
        self.emit(f"begin_func {name}")
        self.visit(ctx.block())
        self.emit(f"end_func {name}")
        return None

    def visitReturnStmt(self, ctx: Language_v4Parser.ReturnStmtContext):
        if ctx.expr():
            res = self.visit(ctx.expr())
            self.emit(f"return {res}")
        else:
            self.emit("return")
        return None

    def visitConditional(self, ctx: Language_v4Parser.ConditionalContext):
        l_else = self.new_label()
        l_end = self.new_label()
        
        cond = self.visit(ctx.condition())
        self.emit(f"ifFalse {cond} goto {l_else}")
        self.visit(ctx.block(0))
        self.emit(f"goto {l_end}")
        self.emit(f"{l_else}:")
        if ctx.block(1):
            self.visit(ctx.block(1))
        self.emit(f"{l_end}:")
        return None

    def visitWhileStmt(self, ctx: Language_v4Parser.WhileStmtContext):
        l_start = self.new_label()
        l_end = self.new_label()
        
        self.loop_stack.append((l_start, l_end))
        self.emit(f"{l_start}:")
        cond = self.visit(ctx.condition())
        self.emit(f"ifFalse {cond} goto {l_end}")
        self.visit(ctx.block())
        self.emit(f"goto {l_start}")
        self.emit(f"{l_end}:")
        self.loop_stack.pop()
        return None

    def visitForStmt(self, ctx: Language_v4Parser.ForStmtContext):
        l_start = self.new_label()
        l_step = self.new_label()
        l_end = self.new_label()
        
        # Init
        if ctx.variable(): self.visit(ctx.variable())
        elif ctx.assignment(): self.visit(ctx.assignment(0))
        
        self.loop_stack.append((l_step, l_end))
        self.emit(f"{l_start}:")
        
        cond = None
        if ctx.condition():
            cond = self.visit(ctx.condition())
        elif ctx.expr():
            cond = self.visit(ctx.expr())
            
        if cond:
            self.emit(f"ifFalse {cond} goto {l_end}")
        
        self.visit(ctx.statement())
        
        self.emit(f"{l_step}:")
        # Step
        has_var_init = ctx.variable() is not None
        assignments = ctx.assignment()
        step = None
        if has_var_init: step = assignments[0] if assignments else None
        else: step = assignments[1] if len(assignments) >= 2 else None
        if step: self.visit(step)
        
        self.emit(f"goto {l_start}")
        self.emit(f"{l_end}:")
        self.loop_stack.pop()
        return None

    def visitBreakStmt(self, ctx: Language_v4Parser.BreakStmtContext):
        if self.loop_stack:
            _, l_end = self.loop_stack[-1]
            self.emit(f"goto {l_end}")
        elif self.switch_stack:
            self.emit(f"goto {self.switch_stack[-1]}")
        return None

    def visitContinueStmt(self, ctx: Language_v4Parser.ContinueStmtContext):
        if self.loop_stack:
            l_step, _ = self.loop_stack[-1]
            self.emit(f"goto {l_step}")
        return None

    def visitPrintStmt(self, ctx: Language_v4Parser.PrintStmtContext):
        val = self.visit(ctx.expr())
        self.emit(f"print {val}")
        return None

    # ── Expresiones ──────────────────────────────────────────────────────────

    def visitMulDivMod(self, ctx: Language_v4Parser.MulDivModContext):
        lt = self.visit(ctx.left)
        rt = self.visit(ctx.right)
        res = self.new_temp()
        self.emit(f"{res} = {lt} {ctx.op.text} {rt}")
        return res

    def visitAddSub(self, ctx: Language_v4Parser.AddSubContext):
        lt = self.visit(ctx.left)
        rt = self.visit(ctx.right)
        res = self.new_temp()
        self.emit(f"{res} = {lt} {ctx.op.text} {rt}")
        return res

    def visitComparison(self, ctx: Language_v4Parser.ComparisonContext):
        lt = self.visit(ctx.expr(0))
        rt = self.visit(ctx.expr(1))
        res = self.new_temp()
        self.emit(f"{res} = {lt} {ctx.op.text} {rt}")
        return res

    def visitAndOr(self, ctx: Language_v4Parser.AndOrContext):
        lt = self.visit(ctx.condition(0))
        rt = self.visit(ctx.condition(1))
        res = self.new_temp()
        self.emit(f"{res} = {lt} {ctx.op.text} {rt}")
        return res

    def visitParens(self, ctx: Language_v4Parser.ParensContext):
        return self.visit(ctx.expr())

    def visitParensCond(self, ctx: Language_v4Parser.ParensCondContext):
        return self.visit(ctx.condition())

    def visitFunctionCall(self, ctx: Language_v4Parser.FunctionCallContext):
        args_ctx = ctx.args()
        arg_names = []
        if args_ctx:
            for e in args_ctx.expr():
                arg_names.append(self.visit(e))
        
        for arg in arg_names:
            self.emit(f"param {arg}")
        
        res = self.new_temp()
        self.emit(f"{res} = call {ctx.ID().getText()}, {len(arg_names)}")
        return res

    def visitArrayAccess(self, ctx: Language_v4Parser.ArrayAccessContext):
        idx = self.visit(ctx.expr())
        res = self.new_temp()
        self.emit(f"{res} = {ctx.ID().getText()}[{idx}]")
        return res

    def visitArrayLit(self, ctx: Language_v4Parser.ArrayLitContext):
        res = self.new_temp()
        elems = [self.visit(e) for e in ctx.expr()]
        self.emit(f"{res} = [{', '.join(elems)}]")
        return res

    def visitArrayNew(self, ctx: Language_v4Parser.ArrayNewContext):
        size = self.visit(ctx.expr())
        res = self.new_temp()
        base = ctx.getChild(0).getText()
        self.emit(f"{res} = new {base}[{size}]")
        return res

    def visitId(self, ctx: Language_v4Parser.IdContext):
        return ctx.ID().getText()

    def visitInt(self, ctx: Language_v4Parser.IntContext):
        return ctx.NUMBER().getText()

    def visitFloatExpr(self, ctx: Language_v4Parser.FloatExprContext):
        return ctx.FLOAT().getText()

    def visitStringExpr(self, ctx: Language_v4Parser.StringExprContext):
        return ctx.STRING().getText()

    def visitBoolExpr(self, ctx: Language_v4Parser.BoolExprContext):
        return ctx.BOOL().getText()

    # ── Language v4 ─────────────────────────────────────────────────────────

    def visitCastExpr(self, ctx: Language_v4Parser.CastExprContext):
        val = self.visit(ctx.expr())
        res = self.new_temp()
        self.emit(f"{res} = cast {val} to {ctx.varType().getText()}")
        return res

    def visitTernaryCompare(self, ctx: Language_v4Parser.TernaryCompareContext):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        cond = self.new_temp()
        self.emit(f"{cond} = {left} {ctx.op.text} {right}")
        return self._emit_ternary(cond, ctx.expr(2), ctx.expr(3))

    def visitTernaryParensCond(self, ctx: Language_v4Parser.TernaryParensCondContext):
        cond = self.visit(ctx.condition())
        return self._emit_ternary(cond, ctx.expr(0), ctx.expr(1))

    def visitTernarySimple(self, ctx: Language_v4Parser.TernarySimpleContext):
        cond = self.visit(ctx.expr(0))
        return self._emit_ternary(cond, ctx.expr(1), ctx.expr(2))

    def _emit_ternary(self, cond, true_expr, false_expr):
        l_false = self.new_label()
        l_end = self.new_label()
        res = self.new_temp()
        self.emit(f"ifFalse {cond} goto {l_false}")
        self.emit(f"{res} = {self.visit(true_expr)}")
        self.emit(f"goto {l_end}")
        self.emit(f"{l_false}:")
        self.emit(f"{res} = {self.visit(false_expr)}")
        self.emit(f"{l_end}:")
        return res

    def visitStructDecl(self, ctx: Language_v4Parser.StructDeclContext):
        fields = []
        for i, var_type in enumerate(ctx.varType()):
            fields.append(f"{var_type.getText()} {ctx.ID(i + 1).getText()}")
        self.emit(f"struct {ctx.ID(0).getText()} {{ {', '.join(fields)} }}")
        return None

    def visitStructVar(self, ctx: Language_v4Parser.StructVarContext):
        self.emit(f"{ctx.ID(1).getText()} = new_struct {ctx.ID(0).getText()}")
        if ctx.expr():
            self.emit(f"{ctx.ID(1).getText()} = {self.visit(ctx.expr())}")
        return None

    def visitFieldAssign(self, ctx: Language_v4Parser.FieldAssignContext):
        val = self.visit(ctx.expr())
        self.emit(f"{ctx.ID(0).getText()}.{ctx.ID(1).getText()} = {val}")
        return None

    def visitStructFieldAccess(self, ctx: Language_v4Parser.StructFieldAccessContext):
        return self.visit(ctx.fieldAccess())

    def visitFieldAccess(self, ctx: Language_v4Parser.FieldAccessContext):
        res = self.new_temp()
        self.emit(f"{res} = {ctx.ID(0).getText()}.{ctx.ID(1).getText()}")
        return res

    def visitSwitchStmt(self, ctx: Language_v4Parser.SwitchStmtContext):
        switch_val = self.visit(ctx.expr())
        l_end = self.new_label()
        default_label = self.new_label() if ctx.defaultClause() else l_end
        case_labels = [self.new_label() for _ in ctx.caseClause()]

        for case_ctx, case_label in zip(ctx.caseClause(), case_labels):
            case_val = self.visit(case_ctx.expr())
            self.emit(f"if {switch_val} == {case_val} goto {case_label}")
        self.emit(f"goto {default_label}")

        self.switch_stack.append(l_end)
        for case_ctx, case_label in zip(ctx.caseClause(), case_labels):
            self.emit(f"{case_label}:")
            self.visitCaseClause(case_ctx)
            self.emit(f"goto {l_end}")

        if ctx.defaultClause():
            self.emit(f"{default_label}:")
            self.visit(ctx.defaultClause())
        self.switch_stack.pop()

        self.emit(f"{l_end}:")
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