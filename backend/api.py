# backend/api.py
"""
API endpoints para ARCHIRAPID
Endpoints REST para integración con frontend
"""

print("Starting Flask app")

from flask import Flask, request, jsonify
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Agregar el directorio raíz al path para imports absolutos
_backend_dir = Path(__file__).parent
_project_root = _backend_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Imports para planos ASCII
import math
sys.path.insert(0, str(_project_root))
# from modules.marketplace.ascii_generator import ascii_square  # mover al endpoint

# Import de ai_engine_groq se hace en el endpoint para evitar problemas con streamlit

app = Flask(__name__)
print("App created")
logger = logging.getLogger(__name__)

@app.route('/api/generar-plano-ascii', methods=['POST'])
def api_generar_plano_ascii():
    """
    Endpoint para generar planos ASCII
    Espera JSON: {"area_m2": float, "tipologia": str, "use_ai": bool}
    """
    print("Endpoint called")
    try:
        data = request.get_json()
        print(f"Data received: {data}")
        if not data or "area_m2" not in data:
            return jsonify({"success": False, "error": "Falta area_m2"}), 400

        area_m2 = data["area_m2"]
        tipologia = data.get("tipologia", "casa")
        use_ai = data.get("use_ai", True)

        if area_m2 <= 0:
            return jsonify({"success": False, "error": "Área debe ser positiva"}), 400

        print(f"Generating for {area_m2} m2, use_ai={use_ai}")
        if use_ai:
            print("Using AI")
            from modules.marketplace import ai_engine_groq as ai
            from modules.marketplace.ascii_generator import ascii_square
            lado = math.sqrt(area_m2)
            prompt = f"Genera plano ASCII para {area_m2} m², tipología {tipologia}: PLANO BASICO ({area_m2} m²) NORTE +----+ {lado:.1f}m | {tipologia.upper()} | +----+ {lado:.1f}m."
            plano = ai.generate_ascii_plan(prompt)
            if "Error:" in plano:
                plano = ascii_square(area_m2)
        else:
            print("Using algorithm")
            from modules.marketplace.ascii_generator import ascii_square
            plano = ascii_square(area_m2)
        print(f"Plano generated: {plano[:50]}...")
        return jsonify({"success": True, "plano": plano, "area_m2": area_m2, "tipologia": tipologia, "metodo": "AI" if use_ai else "Algoritmo"}), 200

    except Exception as e:
        print(f"Error in endpoint: {e}")
        logger.error(f"Error en endpoint /api/generar-plano-ascii: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    try:
        print("Health check called")
        return jsonify({"status": "healthy", "service": "planGenerator"}), 200
    except Exception as e:
        print(f"Error in health: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    print("Running app.run")
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"Error running app: {e}")
        import traceback
        traceback.print_exc()