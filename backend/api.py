# backend/api.py
"""
API endpoints para ARCHIRAPID
Endpoints REST para integración con frontend
"""

from flask import Flask, request, jsonify
import logging
from backend.services.planGenerator import generar_plano

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/api/generar-plano', methods=['POST'])
def api_generar_plano():
    """
    Endpoint para generar planos arquitectónicos
    Espera JSON con datos del proyecto
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se proporcionaron datos"}), 400

        logger.info(f"Recibida petición de generación: {data}")

        # Llamar al generador
        result = generar_plano(data)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Error en endpoint /api/generar-plano: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Endpoint para verificar estado del backend y servicios de IA"""
    try:
        # Verificar si Stable Diffusion está disponible
        sd_available = False
        try:
            import requests
            response = requests.get("http://127.0.0.1:7860/sdapi/v1/options", timeout=3)
            sd_available = response.status_code == 200
        except:
            pass

        return jsonify({
            "status": "operational",
            "services": {
                "stable_diffusion": "available" if sd_available else "unavailable",
                "backend_api": "operational"
            },
            "version": "1.0-fase4"
        }), 200

    except Exception as e:
        logger.error(f"Error en endpoint /api/status: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)