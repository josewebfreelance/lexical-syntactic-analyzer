"""
Punto de entrada del compilador, se delega toda la lógica al pipeline.
"""

import sys
from pipeline import run_pipeline

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <archivo_fuente>")
        print("Ejemplo: python3 main.py test.txt")
        sys.exit(1)
    run_pipeline(sys.argv[1])
