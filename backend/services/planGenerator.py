# backend/services/planGenerator.py
import requests
import os
import json
import time
import logging
from pathlib import Path

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CONFIG: ajusta según tu entorno
USE_LOCAL_IMAGE_GEN = os.getenv("USE_LOCAL_IMAGE_GEN", "true").lower() == "true"
LOCAL_SD_API = os.getenv("LOCAL_SD_API", "http://127.0.0.1:7860")  # automatic1111 default
OUTPUT_DIR = Path("tmp")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generar_plano_local(prompt_text, negative_prompt="", width=1024, height=1024, steps=25, cfg_scale=7.0, controlnet=None, init_image_b64=None):
    """
    Llama a la API /sdapi/v1/txt2img del Automatic1111 WebUI.
    controlnet: dict con las keys adecuadas si quieres usar ControlNet.
    init_image_b64: base64 string si quieres usar init image.
    Devuelve ruta local del PNG generado.
    """
    logger.info(f"Intentando generación local con prompt: {prompt_text[:100]}...")
    
    payload = {
        "prompt": prompt_text,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "sampler_index": "Euler a",
        "enable_hr": False,
    }

    files = None
    if init_image_b64:
        import base64, tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(base64.b64decode(init_image_b64))
        tmp.flush()
        tmp.close()
        files = {"init_images": open(tmp.name, "rb")}
        payload["denoising_strength"] = 0.6
        logger.info("Usando imagen de inicialización para denoising")

    if controlnet:
        payload["alwayson_scripts"] = {"controlnet": {"args": [controlnet]}}
        logger.info("Aplicando ControlNet conditioning")

    try:
        url = f"{LOCAL_SD_API}/sdapi/v1/txt2img"
        logger.info(f"Llamando a API local: {url}")
        
        if files:
            r = requests.post(url, data={"options": json.dumps(payload)}, files=files)
        else:
            r = requests.post(url, json=payload)
        
        r.raise_for_status()
        resp = r.json()
        images = resp.get("images", [])
        
        if not images:
            logger.error("No se recibieron imágenes de la API local")
            return None
            
        import base64
        img_b64 = images[0]
        img_bytes = base64.b64decode(img_b64)
        filename = OUTPUT_DIR / f"plano_local_{int(time.time())}.png"
        with open(filename, "wb") as f:
            f.write(img_bytes)
        
        logger.info(f"Imagen generada exitosamente: {filename}")
        return str(filename)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con API local: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado en generación local: {e}")
        return None
    finally:
        if files:
            files["init_images"].close()

def generar_plano_openai(prompt_data):
    """
    Fallback a OpenAI DALL-E (código comentado como backup)
    """
    logger.info("Usando fallback OpenAI (no implementado en esta versión)")
    # Aquí iría el código de OpenAI comentado
    return {"success": False, "error": "OpenAI fallback not implemented"}

def generar_plano(prompt_data):
    """
    Función principal: intenta local primero, luego fallback.
    prompt_data: dict con keys como estilo, habitaciones, banos, m2, implantacion, etc.
    Retorna: {"success":bool, "file":path, "backend": "local"|"openai", "error":...}
    """
    logger.info(f"Generando plano con datos: {json.dumps(prompt_data, indent=2)}")
    
    # Construir prompt técnico
    prompt_text = f"""Blueprint-style architectural floor plan, technical drawing, clean black linework on white background. No shading, no textures, crisp lines, labelled rooms with area in m2. Show walls with realistic thickness, doors with swing arcs, windows, stairs if needed. Include linear dimensions for main walls and a scale bar. Use orthographic top-down view. Style: technical blueprint, vector-like, high-contrast, white background, black lines. No people, no vegetation. Output: a single-page floor plan with labels (e.g., "Salón 25.3 m2", "Dormitorio 1 12.0 m2").
Data: {json.dumps(prompt_data)}"""
    
    negative_prompt = "blurry, painterly, watercolor, people, trees, shadows, textures, color-saturation, artistic, comic"
    
    # Intentar generación local primero
    if USE_LOCAL_IMAGE_GEN:
        logger.info("Intentando generación con API local (Automatic1111)")
        local_file = generar_plano_local(
            prompt_text, 
            negative_prompt=negative_prompt, 
            width=1536, 
            height=1024, 
            steps=28, 
            cfg_scale=7.5
        )
        if local_file:
            logger.info("Generación local exitosa")
            return {"success": True, "file": local_file, "backend": "local"}
        else:
            logger.warning("Generación local falló, intentando fallback")
    
    # Fallback a OpenAI
    logger.info("Usando fallback OpenAI")
    openai_result = generar_plano_openai(prompt_data)
    if openai_result["success"]:
        return openai_result
    
    # Si todo falla
    error_msg = "No se pudo generar el plano: API local no disponible y OpenAI no configurado"
    logger.error(error_msg)
    return {"success": False, "error": error_msg}