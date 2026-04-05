# Compilador Front-End e Intérprete con ANTLR y Python

Este proyecto ha evolucionado de forma completa para convertirse en un **compilador iterativo multifase** (lexico, sintáctico y semántico) con un **intérprete incorporado** para un lenguaje fuertemente tipado similar a C, desarrollado con ANTLR4 y Python. Valida la gramática, realiza chequeos semánticos rigurosos de tipos y finalmente ejecuta el código mediante un sistema de evaluación de árbol por *Visitors*.

## Características Nuevas y Mejoras

- **Análisis Semántico y Tipado Fuerte:** Inferencia de tipos y chequeos para asegurar que no existan asignaciones incorrectas, evitando llamadas de función con parámetros inválidos.
- **Tipos Base:** Soporte para verificaciones con `int`, `float`, `string`, `bool` y `void`.
- **Estructuras de Control de Flujo:** 
  - Condicionales `if-else`.
  - Bucles recursivos e iterativos `while` y `for`.
- **Funciones y Scope Local:** Declaración de funciones con parámetros, control de sentencias `return`, y validación recursiva manejando una "pila de frames".
- **Operaciones Completas:** Soporte para combinaciones booleanas (`&&`, `||`), comparaciones (`==`, `!=`, `<`, etc) y operaciones matemáticas.
- **Palabras Reservadas (Tokens Explícitos):** El analizador léxico (`Language.g4`) procesa de manera estricta y limpia todas las palabras reservadas (`program`, `int`, `if`, `while`, etc) mediante *Tokens Léxicos Explícitos*.

## Requisitos

- Python 3.10+
- Java (necesario para usar la herramienta/jar de ANTLR)

## Instalación y Preparación

1. Crear un entorno virtual e instalar dependencias (recomendado):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Generar archivos del parser y visitantes de AST (Necesario cada vez que modifiques `Language.g4`):
   ```bash
   java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor -no-listener Language.g4
   ```

## Ejecución e Iteración

El punto de acceso del análisis es `main.py`, que actúa como invocador del **Pipeline** principal de compilación y control manual de fases. 

```bash
python3 main.py <archivo_texto>

# Ejemplo:
python3 main.py test.txt
```

### Proceso Interno del Pipeline

El `pipeline.py` de este motor orquesta 3 instancias críticas sucesivas (y se detiene inmediatamente informando al usuario en caso de falla):

1. **Fase Léxica y Sintáctica:** El Scanner y Parser levantan el árbol y capturan errores de estructura usando Custom Listeners.
2. **Fase Semántica (`semantic_visitor.py`):** Un recorrido de solo-lectura sobre el árbol usando una **Tabla de Símbolos (`symbol_table.py`)**. Inspecciona duplicados, llamadas huérfanas, incompatibilidad de tipos y tipos de retorno mal implementados.
3. **Fase Ejecución (`interpreter.py`):** Suponiendo la superación de las pruebas anteriores (cero errores semánticos), el programa arranca en código limpio, manejando llamadas a funciones dentro de una pila propia de llamadas para la recursividad.

## Archivos del Núcleo de Análisis

- `Language.g4`: Gramática ANTLR4 centralizada.
- `pipeline.py`: Responsable de unificar el proceso y mostrar los errores visualmente.
- `semantic_visitor.py`: Control de consistencia del código sin ejecución en vivo.
- `interpreter.py`: Motor de iteración de lógica matemática, estado de ciclo de vida (`while`/`for`) e impresión.
- `symbol_table.py`: Memoria y registro para inferencia de dependencias durante análisis semántico.
