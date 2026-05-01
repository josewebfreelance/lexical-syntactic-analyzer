"""
ui_compiler.py
--------------
Interfaz Web para el Compilador Language v3.
Usa Flask para el servidor y pipeline.py para la lógica.
"""

from flask import Flask, render_template, request, jsonify
from pipeline import run_pipeline
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    code = data.get('code', '')
    
    if not code.strip():
        return jsonify({
            "success": False,
            "message": "El código está vacío."
        })

    try:
        results = run_pipeline(code, is_file=False)
        return jsonify(results)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error interno: {str(e)}"
        })

if __name__ == '__main__':
    # Asegurarse de que el directorio de templates existe
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Iniciando servidor en http://localhost:5000")
    app.run(debug=True, port=5000)
