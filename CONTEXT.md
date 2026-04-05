# CONTEXT.md — Registro de Cambios del Compilador
## Proyecto: Analizador Léxico → Front-End de Compilación Completo

---

## ¿Qué se pedía?

Evolucionar un analizador léxico-sintáctico básico en ANTLR4 a un compilador front-end completo con:
1. Regeneración limpia usando `-visitor -no-listener`
2. Error Listeners con formato estándar por tipo (Léxico / Sintáctico / Semántico)
3. Separación clara: `SemanticVisitor` valida tipos → solo si pasa, `Interpreter` ejecuta

---

## Cambios realizados y justificación

### 1. `Language.g4` — Gramática

**Cambio:**
```antlr
-- ANTES:
whileStmt: 'while' PARS (expr | condition) PARE statement;

-- DESPUÉS:
whileStmt: 'while' PARS condition PARE block;
```

**¿Por qué?**

| Problema anterior | Solución |
|---|---|
| `(expr \| condition)` crea ambigüedad en el parser. ANTLR tiene que hacer lookahead extra y en algunos casos produce "no viable alternative" | Se elimina `expr` como opción; un while siempre requiere una condición lógica (`x > 0`, `a == b`, etc.) |
| El body era `statement`, lo que permitía `while (x > 0) x = x - 1;` sin llaves | Se cambia a `block`, obligando `{ }`. Esto hace el AST más predecible: `ctx.block()` siempre existe |

**Pendiente:** Regenerar los archivos del parser con:
```bash
antlr4 -Dlanguage=Python3 -visitor -no-listener Language.g4
```

---

### 2. `symbol_table.py` — Tabla de Símbolos

**Cambios agregados:**
- `get_type(name)` — retorna el tipo de una variable sin tener que navegar el dict
- `declare_function(name, return_type, params)` — registra la firma completa de una función
- `lookup_function(name)` — busca un descriptor de función

**¿Por qué?**

El `SemanticVisitor` necesita:
1. Saber el tipo de una variable para validar asignaciones → `get_type()`
2. Registrar funciones para validar llamadas y tipos de retorno → `declare_function()`
3. Recuperar esa firma en llamadas e invocaciones recursivas → `lookup_function()`

La tabla anterior solo gestionaba variables; ahora soporta **funciones** como ciudadanos de primera clase.

---

### 3. `semantic_visitor.py` — NUEVO ARCHIVO

**¿Qué hace?**

Visitor que recorre el AST completo y **acumula errores sin ejecutar nada**. El pipeline solo invoca al intérprete si `semantic.errors` está vacío.

**Diseño clave: `_infer(ctx)`**

Función central que infiere el tipo de cualquier nodo de expresión:

```
_infer(IntContext)       → 'int'
_infer(FloatExprContext) → 'float'
_infer(StringExprContext)→ 'string'
_infer(BoolExprContext)  → 'bool'
_infer(IdContext)        → lookup en SymbolTable
_infer(MulDivContext)    → valida que ambos operandos sean del mismo tipo
_infer(AddSubContext)    → igual, pero permite 'string' + 'string'
_infer(FunctionCallContext) → retorna el return_type de la función
```

**Reglas de compatibilidad implementadas:**

| Declaración | Tipos asignables |
|---|---|
| `int` | solo `int` |
| `float` | solo `float` (sin promoción implícita int→float) |
| `string` | solo `string` |
| `bool` | solo `bool` |
| `void` | funciones que no retornan valor |

**Recursividad semántica:** La función se registra con `declare_function()` **antes** de validar su cuerpo. Así, una función puede llamarse a sí misma dentro de su body y el semántico lo ve como válido.

**Scopes:** `visitBlock()` hace `push_scope() / pop_scope()` en cada bloque. `visitFunction()` crea un scope para los parámetros y luego el block crea otro para las variables locales.

**Returns:** `visitReturnStmt()` compara el tipo de la expresión retornada contra `self.current_function_return_type`, que se establece al entrar a `visitFunction()`.

---

### 4. `interpreter.py` — REESCRITO COMPLETAMENTE

**Problema del código anterior:**
- Solo tenía un dict plano `self.variables = {}`
- `visitAssignment` no podía distinguir entre variables globales y locales
- No había soporte para: `float`, `string`, `bool`, `while`, `for`, `print`, funciones, `return`

**Solución: Call Stack de frames**

```python
self.global_env  = {}   # variables del scope global
self.functions   = {}   # funciones registradas {nombre: FunctionContext}
self.call_stack  = []   # stack de frames locales [{param: valor}, ...]
```

**Búsqueda de variables:**
```
_lookup_var(name):
  1. Busca en call_stack[-1]  (frame actual de la función)
  2. Busca en global_env      (variables globales)
  3. NameError                (el semántico ya garantizó que debería existir)
```

**¿Por qué un call stack?**

Para soportar recursividad real. Ejemplo con `factorial(5)`:
```
global_env: {x: 10, prefijo: "El resultado es: "}
call_stack: [
  {n: 5},        ← frame de factorial(5)
  {n: 4},        ← frame de factorial(4)  -- NUEVO PUSH
  {n: 3},        ← frame de factorial(3)  -- NUEVO PUSH
  ...
]
```
Cada llamada tiene su propio `n` sin pisar el de las llamadas anteriores.

**`ReturnException`:**
```python
class ReturnException(Exception):
    def __init__(self, value): self.value = value
```
Al ejecutar `return expr`, se lanza `ReturnException`. En `visitFunctionCall` se atrapa con `except ReturnException as ret` y se devuelve `ret.value`. El `finally` garantiza que el frame siempre se elimina del stack, incluso en recursión.

**Métodos implementados que faltaban:**

| Método | Descripción |
|---|---|
| `visitVariable` | Declara variable en `global_env` o en el frame actual |
| `visitFunction` | Registra la función para llamadas posteriores |
| `visitFunctionCall` | Push de frame → ejecuta body → pop de frame (con recursividad) |
| `visitReturnStmt` | Lanza `ReturnException(value)` |
| `visitWhileStmt` | Loop con `ctx.block()` (body del while) |
| `visitForStmt` | Loop con init/cond/step |
| `visitPrintStmt` | `print(value)` |
| `visitFloatExpr` | `float(ctx.FLOAT().getText())` |
| `visitStringExpr` | Elimina comillas: `"hello"` → `hello` |
| `visitBoolExpr` | `'true'` → `True`, `'false'` → `False` |
| `visitParensCond` | Delega a `ctx.condition()` |
| `visitAndOr` | `&&` y `\|\|` con cortocircuito |

---

### 5. `pipeline.py` — REESCRITO

**Antes:** Un solo `MyErrorListener` compartido para léxico y sintáctico, sin separación de fases. El semántico estaba comentado.

**Ahora:** 4 fases secuenciales con detención temprana:

```
Fase 1: LexerErrorListener   → errores de tokens inválidos
Fase 2: ParserErrorListener  → errores de estructura
  ↓ Si hay errores → DETENER y mostrar mensajes
Fase 3: SemanticVisitor      → validación de tipos
  ↓ Si hay errores → DETENER y mostrar mensajes
Fase 4: Interpreter          → ejecución del programa
```

**Formatos de error implementados:**
```
[Error Léxico]     Línea 5, Columna 10: Símbolo no reconocido '@'.
[Error Sintáctico] Línea 18, Columna 2: mismatched input '}' [...] (encontrado: '}').
[Error Semántico]  Línea 12, Columna 5: Incompatibilidad de tipos. No se puede asignar 'string' a 'int'.
```

**`removeErrorListeners()`**: Se llama en ambos (lexer y parser) para **silenciar la salida por defecto de ANTLR** que imprime en stderr con un formato diferente. Sin esto, los errores aparecerían dos veces: una con el formato de ANTLR y otra con nuestro formato personalizado.

---

### 6. `main.py` — SIMPLIFICADO

**Antes:** Contenía lógica de fases mezclada (carga de archivo, creación de lexer/parser, ejecución).

**Ahora:** Solo valida que se pasó un argumento y delega a `run_pipeline()`. Toda la responsabilidad de orquestar fases está en `pipeline.py`, que es el lugar correcto.

---

## Arquitectura final

```
main.py
  └─→ pipeline.run_pipeline(file)
         │
         ├─ 1. LexerErrorListener    [Error Léxico]
         ├─ 2. ParserErrorListener   [Error Sintáctico]
         │       ↓ (solo si 0 errores)
         ├─ 3. SemanticVisitor       [Error Semántico]
         │       ↓ (solo si 0 errores)
         └─ 4. Interpreter           (ejecución real)
                  │
                  ├─ global_env   {x: 10, prefijo: "..."}
                  ├─ functions    {factorial: FunctionContext}
                  └─ call_stack   [{n:5}, {n:4}, {n:3}, ...]
```

---

## Comando de regeneración pendiente

Ejecutar en la carpeta del proyecto **después de modificar la gramática**:

```bash
antlr4 -Dlanguage=Python3 -visitor -no-listener Language.g4
```

Esto regenera:
- `LanguageLexer.py`
- `LanguageParser.py` (con `WhileStmtContext.block()` en lugar de `WhileStmtContext.statement()`)
- `LanguageVisitor.py`

Y **no genera** `LanguageListener.py` (puede eliminarse el existente).

---

## Prueba rápida

```bash
python3 pipeline.py input_v2.txt
```

Salida esperada:
```
✔  Análisis léxico y sintáctico exitoso.
→  Iniciando validación semántica...
✔  Validación semántica exitosa. Sin errores de tipo.
→  Iniciando ejecución del programa...
──────────────────────────────────────────────────
El resultado es: 
3628800
El resultado es: 
40320
El resultado es: 
720
El resultado es: 
24
El resultado es: 
2
──────────────────────────────────────────────────
✔  Ejecución completada exitosamente.
```
