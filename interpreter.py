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
    self.variables[var_name]=0
    return 0
