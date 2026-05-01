"""
ir_generator.py
---------------
Generador de LLVM IR usando llvmlite.
"""

import llvmlite.ir as ir
from Language_v3Visitor import Language_v3Visitor
from Language_v3Parser import Language_v3Parser

class IRGenerator(Language_v3Visitor):
    def __init__(self):
        self.module = ir.Module(name="program")
        self.builder = None
        self.func = None
        
        # Mapa de variables: name -> alloca_ptr
        self.variables = {}
        # Mapa de funciones: name -> ir.Function
        self.functions = {}
        
        # Stack para break/continue: [(cond_block, end_block)]
        self.loop_stack = []
        
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

    # ── Visitors ─────────────────────────────────────────────────────────────

    def visitProgram(self, ctx: Language_v3Parser.ProgramContext):
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

    def visitVariable(self, ctx: Language_v3Parser.VariableContext):
        name = ctx.ID().getText()
        ty = self._get_llvm_type(ctx.varType().getText())
        
        # Alloca en el bloque actual (idealmente al inicio de la función)
        ptr = self.builder.alloca(ty, name=name)
        self.variables[name] = ptr
        
        if ctx.expr():
            val = self.visit(ctx.expr())
            self.builder.store(val, ptr)
        return None

    def visitAssignment(self, ctx: Language_v3Parser.AssignmentContext):
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
            self.builder.store(val, ptr)
            return val

    def visitFunction(self, ctx: Language_v3Parser.FunctionContext):
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

    def visitReturnStmt(self, ctx: Language_v3Parser.ReturnStmtContext):
        if ctx.expr():
            val = self.visit(ctx.expr())
            self.builder.ret(val)
        else:
            self.builder.ret_void()
        return None

    def visitConditional(self, ctx: Language_v3Parser.ConditionalContext):
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

    def visitWhileStmt(self, ctx: Language_v3Parser.WhileStmtContext):
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

    def visitForStmt(self, ctx: Language_v3Parser.ForStmtContext):
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

    def visitBreakStmt(self, ctx: Language_v3Parser.BreakStmtContext):
        if self.loop_stack:
            _, end_block = self.loop_stack[-1]
            self.builder.branch(end_block)
        return None

    def visitContinueStmt(self, ctx: Language_v3Parser.ContinueStmtContext):
        if self.loop_stack:
            cond_block, _ = self.loop_stack[-1]
            self.builder.branch(cond_block)
        return None

    def visitPrintStmt(self, ctx: Language_v3Parser.PrintStmtContext):
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

    def visitMulDivMod(self, ctx: Language_v3Parser.MulDivModContext):
        lt = self.visit(ctx.left)
        rt = self.visit(ctx.right)
        op = ctx.op.text
        if op == '*': return self.builder.mul(lt, rt)
        if op == '/': return self.builder.sdiv(lt, rt)
        if op == '%': return self.builder.srem(lt, rt)
        return None

    def visitAddSub(self, ctx: Language_v3Parser.AddSubContext):
        lt = self.visit(ctx.left)
        rt = self.visit(ctx.right)
        op = ctx.op.text
        if op == '+': return self.builder.add(lt, rt)
        if op == '-': return self.builder.sub(lt, rt)
        return None

    def visitComparison(self, ctx: Language_v3Parser.ComparisonContext):
        lt = self.visit(ctx.expr(0))
        rt = self.visit(ctx.expr(1))
        op = ctx.op.text
        # Simplificando para i32
        return self.builder.icmp_signed(op, lt, rt)

    def visitId(self, ctx: Language_v3Parser.IdContext):
        ptr = self.variables.get(ctx.ID().getText())
        return self.builder.load(ptr)

    def visitInt(self, ctx: Language_v3Parser.IntContext):
        return ir.Constant(self.i32, int(ctx.NUMBER().getText()))

    def visitFloatExpr(self, ctx: Language_v3Parser.FloatExprContext):
        return ir.Constant(self.f64, float(ctx.FLOAT().getText()))

    def visitStringExpr(self, ctx: Language_v3Parser.StringExprContext):
        text = ctx.STRING().getText()[1:-1] + "\0"
        return self._create_global_string(text, f"str_{id(ctx)}").bitcast(self.char_ptr)

    def visitBoolExpr(self, ctx: Language_v3Parser.BoolExprContext):
        val = 1 if ctx.BOOL().getText() == 'true' else 0
        return ir.Constant(self.i1, val)

    def visitFunctionCall(self, ctx: Language_v3Parser.FunctionCallContext):
        name = ctx.ID().getText()
        func = self.functions.get(name) or self.module.globals.get(name)
        
        args = []
        if ctx.args():
            args = [self.visit(e) for e in ctx.args().expr()]
            
        return self.builder.call(func, args)
        
    def visitArrayAccess(self, ctx: Language_v3Parser.ArrayAccessContext):
        ptr = self.variables.get(ctx.ID().getText())
        idx = self.visit(ctx.expr())
        arr_ptr = self.builder.load(ptr)
        element_ptr = self.builder.gep(arr_ptr, [idx])
        return self.builder.load(element_ptr)
