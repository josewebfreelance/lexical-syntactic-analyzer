from LanguageVisitor import LanguageVisitor
from LanguageParser import LanguageParser

class Interpreter(LanguageVisitor):
    def __init__(self):
        # Tabla de Símbolos: Diccionario para persistir las variables
        self.variables = {}

    # program: 'program' '{' (declaration | statement)* '}' ;
    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.visitChildren(ctx)

    # expr: left=expr op=('*'|'/') right=expr # MulDiv
    def visitMulDiv(self, ctx: LanguageParser.MulDivContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.text
        if op == '*':
            return left * right
        else:
            if right == 0:
                raise ZeroDivisionError("Error en tiempo de ejecución: División por cero.")
            return left / right

    # expr: left=expr op=('+'|'-') right=expr # AddSub
    def visitAddSub(self, ctx: LanguageParser.AddSubContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.text
        return (left + right) if op == '+' else (left - right)

    # expr: '(' expr ')' # Parens
    def visitParens(self, ctx: LanguageParser.ParensContext):
        return self.visit(ctx.expr())

    # expr: ID # Id
    def visitId(self, ctx: LanguageParser.IdContext):
        var_name = ctx.ID().getText()
        if var_name in self.variables:
            return self.variables[var_name]
        raise NameError(f"Error: Variable '{var_name}' no definida.")

    # expr: NUMBER # Int
    def visitInt(self, ctx: LanguageParser.IntContext):
        return int(ctx.NUMBER().getText())
