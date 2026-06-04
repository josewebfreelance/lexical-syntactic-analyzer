"""
ir_generator.py
---------------
Generador de LLVM IR usando llvmlite.
"""

import llvmlite.ir as ir
import llvmlite.binding as llvm
from Language_v4Visitor import Language_v4Visitor
from Language_v4Parser import Language_v4Parser

class IRGenerator(Language_v4Visitor):
    def __init__(self):
        self.module = ir.Module(name="program")
        self.module.triple = llvm.get_default_triple()
        self.builder = None
        self.func = None
        
        # Mapa de variables: name -> alloca_ptr
        self.variables = {}
        # Mapa de funciones: name -> ir.Function
        self.functions = {}
        # Structs se modelan como campos aplanados: p.x, p.y, etc.
        self.struct_defs = {}
        self.struct_vars = {}

        # Stack para break/continue en ciclos: [(continue_block, end_block)]
        self.loop_stack = []
        # Stack para break en switch/case
        self.switch_stack = []

        # Tipos base
        self.i32 = ir.IntType(32)
        self.f64 = ir.DoubleType()
        self.i1 = ir.IntType(1)
        self.void = ir.VoidType()
        self.char_ptr = ir.IntType(8).as_pointer()
        
        # Declarar printf
        printf_ty = ir.FunctionType(self.i32, [self.char_ptr], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")
        
        # Formatos comunes
        self.fmt_int = self._create_global_string("%d\n\0", "fmt_int")
        self.fmt_float = self._create_global_string("%f\n\0", "fmt_float")
        self.fmt_str = self._create_global_string("%s\n\0", "fmt_str")

    def _create_global_string(self, text, name):
        text_bytes = bytearray(text.encode("utf8"))
        c_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(text_bytes)), text_bytes)
        global_var = ir.GlobalVariable(self.module, c_str.type, name=name)
        global_var.linkage = 'internal'
        global_var.global_constant = True
        global_var.initializer = c_str
        return global_var

    def get_output(self) -> str:
        return str(self.module)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_llvm_type(self, type_str):
        if type_str == 'int': return self.i32
        if type_str == 'float': return self.f64
        if type_str == 'bool': return self.i1
        if type_str == 'string': return self.char_ptr
        if type_str == 'void': return self.void
        if type_str.endswith('[]'):
            base = self._get_llvm_type(type_str.replace('[]', ''))
            return base.as_pointer()
        return self.void

    def _default_value(self, ty):
        if ty == self.i32:
            return ir.Constant(self.i32, 0)
        if ty == self.f64:
            return ir.Constant(self.f64, 0.0)
        if ty == self.i1:
            return ir.Constant(self.i1, 0)
        if ty == self.char_ptr:
            return ir.Constant(self.char_ptr, None)
        return ir.Constant(ty, None)

    def _coerce(self, val, target_ty):
        if val.type == target_ty:
            return val
        if val.type == self.i32 and target_ty == self.f64:
            return self.builder.sitofp(val, self.f64)
        if val.type == self.f64 and target_ty == self.i32:
            return self.builder.fptosi(val, self.i32)
        if val.type == self.i1 and target_ty == self.i32:
            return self.builder.zext(val, self.i32)
        if val.type == self.i32 and target_ty == self.i1:
            return self.builder.icmp_unsigned('!=', val, ir.Constant(self.i32, 0))
        return val

    def _numeric_pair(self, left, right):
        if left.type == self.f64 or right.type == self.f64:
            return self._coerce(left, self.f64), self._coerce(right, self.f64)
        return left, right

    def _to_bool(self, val):
        if val.type == self.i1:
            return val
        if val.type == self.f64:
            return self.builder.fcmp_ordered('!=', val, ir.Constant(self.f64, 0.0))
        return self.builder.icmp_signed('!=', val, ir.Constant(val.type, 0))

    def _field_key(self, ctx):
        ids = ctx.ID()
        return f"{ids[0].getText()}.{ids[1].getText()}"

    # ── Visitors ─────────────────────────────────────────────────────────────

    def visitProgram(self, ctx: Language_v4Parser.ProgramContext):
        # Crear main si no hay funciones? O el programa es el main.
        # En esta gramática, program tiene un bloque de instrucciones.
        # Vamos a envolver el cuerpo del program en una función @main.
        
        func_ty = ir.FunctionType(self.i32, [])
        self.func = ir.Function(self.module, func_ty, name="main")
        entry_block = self.func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        
        self.visitChildren(ctx)
        
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(self.i32, 0))
        return None

    def visitVariable(self, ctx: Language_v4Parser.VariableContext):
        name = ctx.ID().getText()
        ty = self._get_llvm_type(ctx.varType().getText())
        
        # Alloca en el bloque actual (idealmente al inicio de la función)
        ptr = self.builder.alloca(ty, name=name)
        self.variables[name] = ptr
        
        if ctx.expr():
            val = self.visit(ctx.expr())
            val = self._coerce(val, ty)
            self.builder.store(val, ptr)
        return None

    def visitAssignment(self, ctx: Language_v4Parser.AssignmentContext):
        name = ctx.ID().getText()
        ptr = self.variables.get(name)
        
        if len(ctx.expr()) == 2:
            idx = self.visit(ctx.expr(0))
            val = self.visit(ctx.expr(1))
            arr_ptr = self.builder.load(ptr)
            element_ptr = self.builder.gep(arr_ptr, [idx])
            self.builder.store(val, element_ptr)
            return val
        else:
            val = self.visit(ctx.expr(0))
            val = self._coerce(val, ptr.type.pointee)
            self.builder.store(val, ptr)
            return val

    def visitFunction(self, ctx: Language_v4Parser.FunctionContext):
        name = ctx.ID().getText()
        ret_ty = self._get_llvm_type(ctx.varType().getText())
        
        arg_types = []
        arg_names = []
        if ctx.argsFunction():
            for t, n in zip(ctx.argsFunction().varType(), ctx.argsFunction().ID()):
                arg_types.append(self._get_llvm_type(t.getText()))
                arg_names.append(n.getText())
        
        func_ty = ir.FunctionType(ret_ty, arg_types)
        func = ir.Function(self.module, func_ty, name=name)
        self.functions[name] = func
        
        # Guardar contexto actual
        old_builder = self.builder
        old_func = self.func
        old_vars = self.variables.copy()
        
        self.func = func
        entry_block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        
        # Allocar argumentos
        for i, arg in enumerate(func.args):
            arg.name = arg_names[i]
            ptr = self.builder.alloca(arg.type, name=arg.name)
            self.builder.store(arg, ptr)
            self.variables[arg.name] = ptr
            
        self.visit(ctx.block())
        
        # Retorno default si no hay
        if not self.builder.block.is_terminated:
            if ret_ty == self.void:
                self.builder.ret_void()
            else:
                self.builder.ret(ir.Constant(ret_ty, 0))
        
        # Restaurar contexto
        self.builder = old_builder
        self.func = old_func
        self.variables = old_vars
        return None

    def visitReturnStmt(self, ctx: Language_v4Parser.ReturnStmtContext):
        if ctx.expr():
            val = self.visit(ctx.expr())
            self.builder.ret(val)
        else:
            self.builder.ret_void()
        return None

    def visitConditional(self, ctx: Language_v4Parser.ConditionalContext):
        cond = self.visit(ctx.condition())
        
        then_block = self.func.append_basic_block(name="then")
        else_block = self.func.append_basic_block(name="else")
        merge_block = self.func.append_basic_block(name="ifcont")
        
        self.builder.cbranch(cond, then_block, else_block)
        
        # Then
        self.builder.position_at_end(then_block)
        self.visit(ctx.block(0))
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)
            
        # Else
        self.builder.position_at_end(else_block)
        if ctx.block(1):
            self.visit(ctx.block(1))
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)
            
        self.builder.position_at_end(merge_block)
        return None

    def visitWhileStmt(self, ctx: Language_v4Parser.WhileStmtContext):
        cond_block = self.func.append_basic_block(name="while_cond")
        body_block = self.func.append_basic_block(name="while_body")
        end_block = self.func.append_basic_block(name="while_end")
        
        self.builder.branch(cond_block)
        self.builder.position_at_end(cond_block)
        
        cond = self.visit(ctx.condition())
        self.builder.cbranch(cond, body_block, end_block)
        
        self.loop_stack.append((cond_block, end_block))
        
        self.builder.position_at_end(body_block)
        self.visit(ctx.block())
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)
            
        self.loop_stack.pop()
        self.builder.position_at_end(end_block)
        return None

    def visitForStmt(self, ctx: Language_v4Parser.ForStmtContext):
        # Scope para la variable de control si se declara en el for
        # Nota: La tabla de símbolos ya maneja esto, pero aquí en IR 
        # necesitamos ser cuidadosos con el builder.
        
        cond_block = self.func.append_basic_block(name="for_cond")
        body_block = self.func.append_basic_block(name="for_body")
        step_block = self.func.append_basic_block(name="for_step")
        end_block = self.func.append_basic_block(name="for_end")
        
        # 1. Init
        if ctx.variable(): self.visit(ctx.variable())
        elif ctx.assignment(): self.visit(ctx.assignment(0))
        
        self.builder.branch(cond_block)
        
        # 2. Condición
        self.builder.position_at_end(cond_block)
        cond = None
        if ctx.condition():
            cond = self.visit(ctx.condition())
        elif ctx.expr():
            cond = self.visit(ctx.expr())
            
        if cond:
            self.builder.cbranch(cond, body_block, end_block)
        else:
            self.builder.branch(body_block)
            
        # 3. Body
        self.loop_stack.append((step_block, end_block))
        self.builder.position_at_end(body_block)
        self.visit(ctx.statement())
        if not self.builder.block.is_terminated:
            self.builder.branch(step_block)
        self.loop_stack.pop()
        
        # 4. Step
        self.builder.position_at_end(step_block)
        has_var_init = ctx.variable() is not None
        assignments = ctx.assignment()
        step = None
        if has_var_init: step = assignments[0] if assignments else None
        else: step = assignments[1] if len(assignments) >= 2 else None
        
        if step: self.visit(step)
        self.builder.branch(cond_block)
        
        self.builder.position_at_end(end_block)
        return None

    def visitBreakStmt(self, ctx: Language_v4Parser.BreakStmtContext):
        if self.loop_stack:
            _, end_block = self.loop_stack[-1]
            self.builder.branch(end_block)
        elif self.switch_stack:
            self.builder.branch(self.switch_stack[-1])
        return None

    def visitContinueStmt(self, ctx: Language_v4Parser.ContinueStmtContext):
        if self.loop_stack:
            cond_block, _ = self.loop_stack[-1]
            self.builder.branch(cond_block)
        return None

    def visitPrintStmt(self, ctx: Language_v4Parser.PrintStmtContext):
        val = self.visit(ctx.expr())
        
        if val.type == self.i32:
            fmt_ptr = self.builder.bitcast(self.fmt_int, self.char_ptr)
            self.builder.call(self.printf, [fmt_ptr, val])
        elif val.type == self.f64:
            fmt_ptr = self.builder.bitcast(self.fmt_float, self.char_ptr)
            self.builder.call(self.printf, [fmt_ptr, val])
        elif val.type == self.char_ptr:
            fmt_ptr = self.builder.bitcast(self.fmt_str, self.char_ptr)
            self.builder.call(self.printf, [fmt_ptr, val])
        return None

    # ── Expresiones ──────────────────────────────────────────────────────────

    def visitMulDivMod(self, ctx: Language_v4Parser.MulDivModContext):
        lt = self.visit(ctx.left)
        rt = self.visit(ctx.right)
        lt, rt = self._numeric_pair(lt, rt)
        op = ctx.op.text
        if lt.type == self.f64:
            if op == '*': return self.builder.fmul(lt, rt)
            if op == '/': return self.builder.fdiv(lt, rt)
        else:
            if op == '*': return self.builder.mul(lt, rt)
            if op == '/': return self.builder.sdiv(lt, rt)
            if op == '%': return self.builder.srem(lt, rt)
        return None

    def visitAddSub(self, ctx: Language_v4Parser.AddSubContext):
        lt = self.visit(ctx.left)
        rt = self.visit(ctx.right)
        lt, rt = self._numeric_pair(lt, rt)
        op = ctx.op.text
        if lt.type == self.f64:
            if op == '+': return self.builder.fadd(lt, rt)
            if op == '-': return self.builder.fsub(lt, rt)
        else:
            if op == '+': return self.builder.add(lt, rt)
            if op == '-': return self.builder.sub(lt, rt)
        return None

    def visitComparison(self, ctx: Language_v4Parser.ComparisonContext):
        lt = self.visit(ctx.expr(0))
        rt = self.visit(ctx.expr(1))
        lt, rt = self._numeric_pair(lt, rt)
        op = ctx.op.text
        if lt.type == self.f64:
            return self.builder.fcmp_ordered(op, lt, rt)
        return self.builder.icmp_signed(op, lt, rt)

    def visitAndOr(self, ctx: Language_v4Parser.AndOrContext):
        left = self._to_bool(self.visit(ctx.condition(0)))
        right = self._to_bool(self.visit(ctx.condition(1)))
        if ctx.op.text == '&&':
            return self.builder.and_(left, right)
        return self.builder.or_(left, right)

    def visitParensCond(self, ctx: Language_v4Parser.ParensCondContext):
        return self.visit(ctx.condition())

    def visitParens(self, ctx: Language_v4Parser.ParensContext):
        return self.visit(ctx.expr())

    def visitCastExpr(self, ctx: Language_v4Parser.CastExprContext):
        val = self.visit(ctx.expr())
        return self._coerce(val, self._get_llvm_type(ctx.varType().getText()))

    def visitTernaryCompare(self, ctx: Language_v4Parser.TernaryCompareContext):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        left, right = self._numeric_pair(left, right)
        if left.type == self.f64:
            cond = self.builder.fcmp_ordered(ctx.op.text, left, right)
        else:
            cond = self.builder.icmp_signed(ctx.op.text, left, right)
        true_val = self.visit(ctx.expr(2))
        false_val = self.visit(ctx.expr(3))
        false_val = self._coerce(false_val, true_val.type)
        return self.builder.select(cond, true_val, false_val)

    def visitTernaryParensCond(self, ctx: Language_v4Parser.TernaryParensCondContext):
        cond = self._to_bool(self.visit(ctx.condition()))
        true_val = self.visit(ctx.expr(0))
        false_val = self.visit(ctx.expr(1))
        false_val = self._coerce(false_val, true_val.type)
        return self.builder.select(cond, true_val, false_val)

    def visitTernarySimple(self, ctx: Language_v4Parser.TernarySimpleContext):
        cond = self._to_bool(self.visit(ctx.expr(0)))
        true_val = self.visit(ctx.expr(1))
        false_val = self.visit(ctx.expr(2))
        false_val = self._coerce(false_val, true_val.type)
        return self.builder.select(cond, true_val, false_val)

    def visitId(self, ctx: Language_v4Parser.IdContext):
        ptr = self.variables.get(ctx.ID().getText())
        return self.builder.load(ptr)

    def visitInt(self, ctx: Language_v4Parser.IntContext):
        return ir.Constant(self.i32, int(ctx.NUMBER().getText()))

    def visitFloatExpr(self, ctx: Language_v4Parser.FloatExprContext):
        return ir.Constant(self.f64, float(ctx.FLOAT().getText()))

    def visitStringExpr(self, ctx: Language_v4Parser.StringExprContext):
        text = ctx.STRING().getText()[1:-1] + "\0"
        return self._create_global_string(text, f"str_{id(ctx)}").bitcast(self.char_ptr)

    def visitBoolExpr(self, ctx: Language_v4Parser.BoolExprContext):
        val = 1 if ctx.BOOL().getText() == 'true' else 0
        return ir.Constant(self.i1, val)

    def visitFunctionCall(self, ctx: Language_v4Parser.FunctionCallContext):
        name = ctx.ID().getText()
        func = self.functions.get(name) or self.module.globals.get(name)
        
        args = []
        if ctx.args():
            args = [self.visit(e) for e in ctx.args().expr()]
            
        return self.builder.call(func, args)
        
    def visitArrayAccess(self, ctx: Language_v4Parser.ArrayAccessContext):
        ptr = self.variables.get(ctx.ID().getText())
        idx = self.visit(ctx.expr())
        arr_ptr = self.builder.load(ptr)
        element_ptr = self.builder.gep(arr_ptr, [idx])
        return self.builder.load(element_ptr)

    def visitArrayLit(self, ctx: Language_v4Parser.ArrayLitContext):
        values = [self.visit(e) for e in ctx.expr()]
        elem_ty = values[0].type if values else self.i32
        arr_ty = ir.ArrayType(elem_ty, len(values))
        arr_ptr = self.builder.alloca(arr_ty, name="arraylit")
        for i, val in enumerate(values):
            element_ptr = self.builder.gep(
                arr_ptr,
                [ir.Constant(self.i32, 0), ir.Constant(self.i32, i)]
            )
            self.builder.store(self._coerce(val, elem_ty), element_ptr)
        return self.builder.gep(
            arr_ptr,
            [ir.Constant(self.i32, 0), ir.Constant(self.i32, 0)]
        )

    def visitArrayNew(self, ctx: Language_v4Parser.ArrayNewContext):
        size = self.visit(ctx.expr())
        base_ty = self._get_llvm_type(ctx.getChild(0).getText())
        return self.builder.alloca(base_ty, size=size, name="arraynew")

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
        self.struct_vars[var_name] = struct_name
        for field_name, field_type in self.struct_defs.get(struct_name, {}).items():
            ty = self._get_llvm_type(field_type)
            ptr = self.builder.alloca(ty, name=f"{var_name}.{field_name}")
            self.variables[f"{var_name}.{field_name}"] = ptr
            self.builder.store(self._default_value(ty), ptr)
        return None

    def visitFieldAssign(self, ctx: Language_v4Parser.FieldAssignContext):
        key = self._field_key(ctx)
        val = self.visit(ctx.expr())
        ptr = self.variables.get(key)
        if ptr is None:
            ptr = self.builder.alloca(val.type, name=key)
            self.variables[key] = ptr
        val = self._coerce(val, ptr.type.pointee)
        self.builder.store(val, ptr)
        return val

    def visitStructFieldAccess(self, ctx: Language_v4Parser.StructFieldAccessContext):
        return self.visit(ctx.fieldAccess())

    def visitFieldAccess(self, ctx: Language_v4Parser.FieldAccessContext):
        ptr = self.variables.get(self._field_key(ctx))
        return self.builder.load(ptr)

    def visitSwitchStmt(self, ctx: Language_v4Parser.SwitchStmtContext):
        switch_val = self.visit(ctx.expr())
        end_block = self.func.append_basic_block(name="switch_end")
        default_block = self.func.append_basic_block(name="switch_default") if ctx.defaultClause() else end_block
        case_blocks = [self.func.append_basic_block(name="switch_case") for _ in ctx.caseClause()]
        switch_inst = self.builder.switch(switch_val, default_block)

        for case_ctx, case_block in zip(ctx.caseClause(), case_blocks):
            case_val = self.visit(case_ctx.expr())
            case_val = self._coerce(case_val, switch_val.type)
            switch_inst.add_case(case_val, case_block)

        self.switch_stack.append(end_block)
        for case_ctx, case_block in zip(ctx.caseClause(), case_blocks):
            self.builder.position_at_end(case_block)
            self.visitCaseClause(case_ctx)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)

        if ctx.defaultClause():
            self.builder.position_at_end(default_block)
            self.visit(ctx.defaultClause())
            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)
        self.switch_stack.pop()

        self.builder.position_at_end(end_block)
        return None

    def visitCaseClause(self, ctx: Language_v4Parser.CaseClauseContext):
        for statement in ctx.statement():
            self.visit(statement)
            if self.builder.block.is_terminated:
                return None
        if ctx.breakStmt():
            self.visit(ctx.breakStmt())
        return None

    def visitDefaultClause(self, ctx: Language_v4Parser.DefaultClauseContext):
        for statement in ctx.statement():
            self.visit(statement)
            if self.builder.block.is_terminated:
                return None
        return None
