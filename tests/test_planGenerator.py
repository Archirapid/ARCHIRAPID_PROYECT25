# tests/test_planGenerator.py
"""
Tests unitarios para el módulo planGenerator
Simula respuestas de la API local para testing
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path
import sys

# Añadir el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.planGenerator import generar_plano_local, generar_plano

class TestPlanGenerator(unittest.TestCase):
    """Tests para el generador de planos"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.test_prompt = "Blueprint-style architectural floor plan test"
        self.test_negative = "blurry, people, trees"
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpieza después de tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('services.planGenerator.requests.post')
    def test_generar_plano_local_success(self, mock_post):
        """Test generación local exitosa"""
        # Mock respuesta exitosa de Automatic1111
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "images": ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="]  # PNG 1x1 pixel en base64
        }
        mock_post.return_value = mock_response

        result = generar_plano_local(self.test_prompt, self.test_negative)

        self.assertIsNotNone(result)
        self.assertTrue(result.endswith('.png'))
        self.assertTrue(os.path.exists(result))

    @patch('services.planGenerator.requests.post')
    def test_generar_plano_local_no_images(self, mock_post):
        """Test cuando la API no devuelve imágenes"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"images": []}
        mock_post.return_value = mock_response

        result = generar_plano_local(self.test_prompt)

        self.assertIsNone(result)

    @patch('services.planGenerator.requests.post')
    def test_generar_plano_local_connection_error(self, mock_post):
        """Test error de conexión"""
        mock_post.side_effect = Exception("Connection failed")

        result = generar_plano_local(self.test_prompt)

        self.assertIsNone(result)

    @patch('services.planGenerator.USE_LOCAL_IMAGE_GEN', True)
    @patch('services.planGenerator.generar_plano_local')
    def test_generar_plano_local_success_flow(self, mock_local):
        """Test flujo completo con generación local exitosa"""
        mock_local.return_value = "/tmp/test_plano.png"

        prompt_data = {
            "estilo": "moderno",
            "habitaciones": 3,
            "banos": 2,
            "m2": 100
        }

        result = generar_plano(prompt_data)

        self.assertTrue(result["success"])
        self.assertEqual(result["file"], "/tmp/test_plano.png")
        self.assertEqual(result["backend"], "local")

    @patch('services.planGenerator.USE_LOCAL_IMAGE_GEN', True)
    @patch('services.planGenerator.generar_plano_local')
    @patch('services.planGenerator.generar_plano_openai')
    def test_generar_plano_fallback_to_openai(self, mock_openai, mock_local):
        """Test fallback a OpenAI cuando local falla"""
        mock_local.return_value = None
        mock_openai.return_value = {"success": True, "file": "/tmp/openai_plano.png", "backend": "openai"}

        prompt_data = {"estilo": "clasico", "habitaciones": 2}

        result = generar_plano(prompt_data)

        self.assertTrue(result["success"])
        self.assertEqual(result["backend"], "openai")

    @patch('services.planGenerator.USE_LOCAL_IMAGE_GEN', True)
    @patch('services.planGenerator.generar_plano_local')
    @patch('services.planGenerator.generar_plano_openai')
    def test_generar_plano_all_fail(self, mock_openai, mock_local):
        """Test cuando ambos métodos fallan"""
        mock_local.return_value = None
        mock_openai.return_value = {"success": False, "error": "OpenAI failed"}

        prompt_data = {"estilo": "minimalista"}

        result = generar_plano(prompt_data)

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch('services.planGenerator.requests.post')
    def test_generar_plano_local_with_init_image(self, mock_post):
        """Test generación local con imagen de inicialización"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "images": ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="]
        }
        mock_post.return_value = mock_response

        # Imagen dummy en base64 (1x1 pixel PNG)
        init_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        result = generar_plano_local(
            self.test_prompt,
            init_image_b64=init_image_b64,
            width=512,
            height=512
        )

        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))

if __name__ == '__main__':
    unittest.main()
