"""
ui_compiler.py
--------------
Interfaz Web para el Compilador Language v4.
Usa Flask para el servidor y pipeline.py para la lógica.
"""

from flask import Flask, render_template, request, jsonify
from pipeline import execute_ir, run_pipeline
from manual_optimizer import apply_manual_passes, get_available_passes
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_passes', methods=['GET'])
def get_passes():
    return jsonify(get_available_passes())

@app.route('/optimize_manual', methods=['POST'])
def optimize_manual():
    data = request.json
    ir_string = data.get('ir', '')
    selected_passes = data.get('passes', [])
    if not ir_string:
        return jsonify({"success": False, "message": "IR vacío."})
    try:
        result = apply_manual_passes(ir_string, selected_passes)
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/compile_binary', methods=['POST'])
def compile_binary():
    data = request.json
    ir_string = data.get('ir', '')
    target_linux = data.get('linux', False)
    target_windows = data.get('windows', False)
    if not ir_string:
        return jsonify({"success": False, "message": "IR vacío."})
    try:
        from binary_generator import generate_binary
        result = generate_binary(ir_string, target_linux, target_windows)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/run_ir', methods=['POST'])
def run_ir():
    data = request.json
    ir_string = data.get('ir', '')
    if not ir_string:
        return jsonify({"success": False, "message": "IR vacío."})
    try:
        return jsonify({"success": True, "output": execute_ir(ir_string)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    code = data.get('code', '')
    target_linux = data.get('target_linux', False)
    target_windows = data.get('target_windows', False)

    if not code.strip():
        return jsonify({"success": False, "message": "El código está vacío."})

    try:
        results = run_pipeline(code, is_file=False,
                               target_linux=target_linux,
                               target_windows=target_windows)
        return jsonify(results)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"})

if __name__ == '__main__':
    # Asegurarse de que el directorio de templates existe
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Iniciando servidor en http://localhost:5000")
    app.run(debug=True, port=5000)
