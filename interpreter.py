from LanguageVisitor import LanguageVisitor
from LanguageParser import LanguageParser

class Interpreter(LanguageVisitor):
    def __init__(self):
        # Tabla de Símbolos: Diccionario para persistir las variables
        self.variables = {}

    # program: 'program' '{' (declaration | statement)* '}' ;
    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.visitChildren(ctx)

    #declaration:'int' ID ',';
    def visitDeclaration(self, ctx: languageParser.DeclationContect):
        var_name = CTX.ID().getText()
        #Inicializamos la variable en nuestratabla de simbolos
        self.variables[var_name] = 0
        return 0

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


   def visitAssignment(self, ctx: LanguageParser.AssignmentContext):
        var_name = ctx.ID().getText()
        if var_name not in self.variables:
            raise NameError(f"Error Semántico: Variable '{var_name}' no declarada.")

        value = self.visit(ctx.expr())
        self.variables[var_name] = value
        return value

    def visitBlock(self, ctx: LanguageParser.BlockContext):
        return self.visitChildren(ctx)
