import sys
from antlr4 import *
from LanguageLexer import LanguageLexer
from LanguageParser import LanguageParser
from interpreter import Interpreter

def main():
    # Nombre del archivo de prueba
    input_file = "input.txt"
    
    try:
        # Cargar el archivo
        input_stream = FileStream(input_file, encoding='utf-8')
        
        # Análisis Léxico
        lexer = LanguageLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        
        # Análisis Sintáctico
        parser = LanguageParser(token_stream)
        tree = parser.program()
        
        #Verificar errores de sintaxis antes de comtinuar
        if parser.getNumberOfSyntaxErrors()>0:
            print("\n[!] Error. Se encontrarron errores de sintaxis en el programa.")
            return

        # Ejecutar el Intérprete mediante el Visitor
        print("--- Iniciando Ejecución ---")
        visitor = Interpreter()
        visitor.visit(tree)
        
        # Mostrar el estado final de las variables (Requisito de validación)
        print("\n--- Ejecución Exitosa ---")
        print("Variables finales:")
        for var, val in visitor.variables.items():
            print(f"  {var} = {val}")

    except Exception as e:
        print(f"\n[!] Error durante la ejecución: {e}")

if __name__ == '__main__':
    main()
