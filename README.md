# Analizador Léxico y Sintáctico con ANTLR y Python

Este proyecto es un analizador léxico, sintáctico e intérprete para un lenguaje similar a C, desarrollado con ANTLR4 y Python. Valida la gramática, analiza expresiones y sirve como base para un compilador completo.

## Características

- **Declaración de Variables:** Ej. `int x;`
- **Operaciones Aritméticas:** Suma, resta, multiplicación y división.
- **Símbolos de Agrupación:** Paréntesis para la precedencia de expresiones.
- **Estructuras Condicionales:** Bloques `if-else` con condiciones booleanas.
- **Operadores Lógicos:** `>`, `<`, `==`, `!=`
- **Declaración del Programa:** Envuelto en un bloque `program { ... }`.

## Requisitos

- Python 3
- Java (necesario para generar el Parser de ANTLR)

- Instalar paquetes de antlr4
- `antlr4-tools` y `antlr4-python3-runtime`
  
## Ejecución de los Ejemplos

1. Instalar dependencias (si no se han gestionado aún):

   ```bash
   pip install -r requirements.txt
   ```

2. Uso de entorno virtual (recomendado)
   ```bash
   source .venv/bin/activate
   ```

3. Generar archivos del parser:
   ```bash
   java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor Language.g4
   ```
  
4. Ejecutar el Intérprete:
Ejecuta el script `main.py` incluido y pasa tu archivo de código como argumento.

   ```bash
   python3 main.py input.txt
   ```

   **Ejemplo de salida:**

   ```
   Execution Finished.
   Variables state:
   x = 10
   y = 20
   w = 25.0
   z = 50
   ```

## Estructura del Proyecto

- `Language.g4`: La gramática de ANTLR que define las reglas léxicas y sintácticas.
- `interpreter.py`: El "Visitor" de Python personalizado que recorre el AST (Árbol de Sintaxis Abstracta) y ejecuta las operaciones.
- `main.py`: El script para inicializar el Lexer/Parser de ANTLR e invocar al Intérprete.
- `input.txt`: Un programa de ejemplo escrito en el lenguaje diseñado.
