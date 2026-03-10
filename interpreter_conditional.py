from LanguageVisitor import LanguageVisitor
from LanguageParser import LanguageParser

class Interpreter(LanguageVisitor):
    def __init__(self):
        # Tabla de Símbolos: Diccionario para persistir las variables
        self.variables = {}

    # program: 'program' '{' (declaration | statement)* '}' ;
    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.visitChildren(ctx)





# conditional: 'if' '(' condition ')' block ('else' block)? ;
    def visitConditional(self, ctx: LanguageParser.ConditionalContext):
        condition_result = self.visit(ctx.condition())
        if condition_result:
            return self.visit(ctx.block(0))
        elif ctx.block(1):  # Si existe el bloque else
            return self.visit(ctx.block(1))
        return None

    # condition: left=expr op=('>' | '<' | '==' | '!=' | '>=' | '<=') right=expr ;
    def visitCondition(self, ctx: LanguageParser.ConditionContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.text

        if op == '>':  return left > right
        if op == '<':  return left < right
        if op == '==': return left == right
        if op == '!=': return left != right
        if op == '>=': return left >= right
        if op == '<=': return left <= right
        return False