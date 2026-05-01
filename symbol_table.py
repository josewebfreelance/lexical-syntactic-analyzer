class SymbolTable:
    def __init__(self):
        # Pila de scopes: índice 0 = scope global, el último = scope actual
        self.scopes = [{}]
        # Registro de funciones: name -> {return_type, params: [(type_str, name)]}
        self.functions = {}
        # Módulos importados
        self.imported_modules = set()

    # ── Manejo de scopes ─────────────────────────────────────────────────────

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    # ── Variables ────────────────────────────────────────────────────────────

    def declare(self, name, data_type, is_array=False, array_size=None, line=0, col=0):
        """
        Declara variable en el scope actual.
        is_array: bool
        array_size: int o None (si es dinámico o literal)
        """
        if name in self.scopes[-1]:
            return False
        
        element_type = data_type.replace('[]', '') if is_array else data_type
        
        self.scopes[-1][name] = {
            "type": data_type, # e.g., 'int' o 'int[]'
            "element_type": element_type,
            "is_array": is_array,
            "array_size": array_size,
            "value": None
        }
        return True

    def lookup(self, name):
        """Busca variable desde el scope más interno hacia fuera. Retorna entry o None."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def get_type(self, name):
        """Retorna el tipo de una variable o None si no existe."""
        entry = self.lookup(name)
        return entry["type"] if entry else None

    def update(self, name, value):
        """Actualiza el valor de una variable en cualquier scope. Retorna True si encontró."""
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]["value"] = value
                return True
        return False

    # ── Funciones ────────────────────────────────────────────────────────────

    def declare_function(self, name, return_type, params):
        """
        Registra una función.
        params: lista de tuplas (type_str, var_name)
        """
        self.functions[name] = {"return_type": return_type, "params": params}

    def lookup_function(self, name):
        """Retorna el descriptor de función o None si no existe."""
        return self.functions.get(name)

    # ── Imports ──────────────────────────────────────────────────────────────

    def add_import(self, module_name):
        self.imported_modules.add(module_name)
        if module_name == 'math':
            # Pre-cargar funciones de math
            self.declare_function("abs", "int", [("int", "n")])
            self.declare_function("pow", "float", [("float", "base"), ("float", "exp")])
            self.declare_function("sqrt", "float", [("float", "n")])
