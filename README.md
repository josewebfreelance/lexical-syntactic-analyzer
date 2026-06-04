# Compilador Front-End e Intérprete con ANTLR y Python

Este proyecto es un **compilador multifase** (léxico, sintáctico, semántico, **generación de código intermedio** y ejecución) con un **intérprete incorporado** para un lenguaje fuertemente tipado similar a C, desarrollado con ANTLR4 y Python. Valida la gramática, realiza chequeos semánticos rigurosos de tipos, genera código intermedio en **TAC** y **LLVM IR**, y finalmente ejecuta el código mediante un sistema de evaluación de árbol por *Visitors*.

---

## Características

### Fase 1–2: Análisis Léxico, Sintáctico y Semántico

- **Análisis Semántico y Tipado Fuerte:** Inferencia de tipos y chequeos para asegurar que no existan asignaciones incorrectas.
- **Tipos Base:** Soporte para `int`, `float`, `string`, `bool` y `void`.
- **Arreglos:** Declaración, inicialización y acceso por índice (`int[] nums = [1, 2, 3];`).
- **Módulos / Imports:** Soporte para `import math;` que habilita funciones como `abs`, `pow` y `sqrt`.
- **Operadores:** Soporte para aritmética completa, incluyendo el operador módulo `%`.
- **Estructuras de Control de Flujo:**
  - Condicionales `if-else`.
  - Bucles `while` y `for`.
  - Instrucciones `break` y `continue`.
- **Funciones y Scope Local:** Declaración de funciones con múltiples `return`, parámetros y validación recursiva manejando una pila de frames.

### Fase 3: Generación de Código Intermedio

- **TAC (Código de Tres Direcciones):** Generador que produce instrucciones atómicas con temporales (`t0`, `t1`, …) y etiquetas de salto (`L0`, `L1`, …).
- **LLVM IR:** Generador que utiliza `llvmlite` para producir código `.ll` funcional. El código generado es verificable con `llvm-as` y ejecutable con `lli`.

### Fase 4: Optimización

- **Optimizador Automático (O3):** Aplica optimizaciones de LLVM usando PassManager para reducir el tamaño del código y mejorar el rendimiento.
- **Optimizador Manual:** Permite seleccionar passes individuales (mem2reg, instcombine, dce, inline, etc.) para control granular de las optimizaciones.

### Fase 5: Generación de Binarios

- **Binarios Nativos Linux:** Compila el IR optimizado a ejecutables nativos para Linux usando clang.
- **Cross-compilación Windows:** Temporalmente deshabilitada debido a problemas de compatibilidad con mingw-w64 en WSL/Ubuntu.
- **Interfaz Web Interactiva (`ui_compiler.py`):** Una aplicación web completa (Flask) que permite escribir código, compilar y visualizar el progreso por fases, tiempos, errores, TAC, IR y salida de ejecución en paneles dedicados.

---

## Arquitectura del Pipeline

```
ui_compiler.py (Flask)
  └─→ pipeline.run_pipeline(code)
         │
         ├─ 1. Léxico         → LexerErrorListener    [Error Léxico]
         ├─ 2. Sintáctico     → ParserErrorListener   [Error Sintáctico]
         │       ↓ (solo si 0 errores)
         ├─ 3. Semántico      → SemanticVisitor       [Error Semántico]
         │       ↓ (solo si 0 errores)
         ├─ 4. TAC            → TACGenerator          → Viewer TAC
         ├─ 5. LLVM IR        → IRGenerator           → Viewer IR
         │       ↓
         ├─ 6. Ejecución      → Interpreter / lli     → Consola UI
         │       ↓
         ├─ 7. Optimización    → Optimizer (O3)        → IR Optimizado
         │       ↓
         └─ 8. Binarios       → Binary Generator       → Ejecutables (Linux/Windows)
```

---

## Requisitos

- Python 3.10+
- Java (requerido para ejecutar el generador de ANTLR)
- LLVM (opcional, para ejecutar el código `.ll` con `lli`)

## Instalación y Preparación

1. Crear un entorno virtual e instalar dependencias:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Instalar ANTLR4 (si aún no está instalado):
   ```bash
   sudo apt-get install antlr4
   ```

3. Generar archivos del parser (necesario si modificas `Language_v4.g4`):
   
   Si estás dentro del venv y usas `antlr4-tools`, especifica la versión:
   ```bash
   export ANTLR4_TOOLS_ANTLR_VERSION=4.13.2
   antlr4 -Dlanguage=Python3 -visitor -no-listener Language_v4.g4
   ```
   
   Alternativamente, fuera del venv usa el binario del sistema:
   ```bash
   deactivate
   /usr/bin/antlr4 -Dlanguage=Python3 -visitor -no-listener Language_v4.g4
   source .venv/bin/activate
   ```

4. Limpiar archivos de versiones anteriores (Opcional):
   ```bash
   rm Language.g4 Language*.py Language*.tokens Language*.interp
   ```

5. (Opcional) Instalar LLVM para ejecutar el IR generado:
   ```bash
   sudo apt install llvm
   ```

6. (Opcional) Instalar herramientas de compilación para generar binarios nativos:
   ```bash
   sudo apt install clang
   ```

   Para cross-compilación a Windows (desde Linux/WSL):
   ```bash
   sudo apt install clang mingw-w64
   ```

---

## Ejecución

### Interfaz Web Interactiva (Recomendado)

Inicia el servidor Flask y abre el navegador en `http://localhost:5000`:

```bash
python3 ui_compiler.py
```

### Pipeline vía Terminal

También puedes ejecutar el pipeline directamente pasando un archivo:

```bash
python3 main.py test/input_v2.txt
```

---

## Sintaxis del Lenguaje

### Arreglos y Módulo
```c
int[] nums = [1, 2, 3];
int r = 10 % 3;
nums[0] = 42;
```

### Control de Flujo
```c
while (x > 0) {
    if (x == 5) { break; }
    x = x - 1;
}
```

### Imports
```c
import math;
float s = sqrt(16.0);
```

---

## Formato de Instrucciones TAC

| Tipo | Formato | Ejemplo |
|---|---|---|
| Funciones | `begin_func` / `end_func` | Delimitadores de función |
| Asignación | `t0 = 5` | Asignación con temporales |
| Salto | `ifFalse t0 goto L1` | Salto condicional |
| Llamada | `t3 = call factorial, 1` | Llamada con argumentos |
| Arreglo | `t1 = nums[t0]` | Lectura de índice |

---

## Archivos del Proyecto

### Generación de Código (Fase 3)

| Archivo | Descripción |
|---|---|
| `Language_v4.g4` | Gramática ANTLR4 versionada con todas las extensiones |
| `tac_generator.py` | Generador de Código de Tres Direcciones (TAC) |
| `ir_generator.py` | Generador de LLVM IR usando `llvmlite` |
| `optimizer.py` | Optimizador automático de LLVM IR (O3) |
| `manual_optimizer.py` | Optimizador manual con passes seleccionables |
| `binary_generator.py` | Generador de binarios nativos (Linux/Windows) |
| `ui_compiler.py` | Servidor Flask para la interfaz interactiva |
| `templates/index.html` | Frontend de la interfaz con 8 paneles |
| `pipeline.py` | Orquestador de las 8 fases con medición de tiempos |

### Núcleo

| Archivo | Descripción |
|---|---|
| `semantic_visitor.py` | Validación de tipos y reglas de control (break/continue) |
| `interpreter.py` | Motor de ejecución (Intérprete AST) |
| `symbol_table.py` | Gestión de scopes, variables, arreglos y funciones |

---

## Solución de Problemas

### Error: "Herramientas de cross-compilación no encontradas"

Al intentar generar binarios para Windows desde Linux/WSL, aparece este error:

```
Error de Compilación:
Herramientas de cross-compilación no encontradas.
Instala con: sudo apt install clang mingw-w64
```

**Soluciones:**

1. **Instalar herramientas de cross-compilación (para binarios Windows):**
   ```bash
   sudo apt update
   sudo apt install clang mingw-w64
   ```

2. **Generar solo binarios Linux (funciona en WSL):**
   - En la interfaz web, desmarca la opción "Windows" y marca solo "Linux"
   - Los binarios Linux generados funcionarán en tu entorno WSL

3. **Usar el IR de LLVM directamente:**
   - El pipeline genera automáticamente `output.ll` (IR de LLVM)
   - Puedes ejecutarlo con: `lli output.bc`
   - O compilarlo manualmente con herramientas que tengas instaladas

### Error: "clang no encontrado"

Si aparece este error al intentar generar binarios Linux:

**Soluciones:**

1. **Instalar clang:**
   ```bash
   sudo apt install clang
   ```

2. **Usar el intérprete integrado:**
   - El pipeline incluye un intérprete Python que ejecuta el código directamente
   - No requiere herramientas externas de compilación

3. **Usar el IR de LLVM:**
   - El archivo `output.ll` contiene el código intermedio de LLVM
   - Puede ser ejecutado con `lli` si tienes LLVM instalado

### Error: "llvmlite.binding.initialize() is deprecated"

Si aparece este error de versión de llvmlite:

**Solución:**
El código ha sido actualizado para manejar versiones modernas de llvmlite. Si persiste el error, actualiza llvmlite:
```bash
pip install --upgrade llvmlite
```

---
