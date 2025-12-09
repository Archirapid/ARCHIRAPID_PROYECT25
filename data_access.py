#!/usr/bin/env python3
"""
Integración Frontend-Backend para ARCHIRAPID
Cliente API que conecta Streamlit con FastAPI backend
"""

import requests
import json
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
from datetime import datetime
import time

# ==========================================
# CONFIGURACIÓN DE API
# ==========================================

class APIClient:
    """Cliente para conectar con el backend FastAPI"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30  # Timeout de 30 segundos

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Realiza petición HTTP con manejo de errores"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

        except requests.exceptions.ConnectionError:
            st.error("❌ No se puede conectar con el backend. Asegúrate de que el servidor esté ejecutándose.")
            return {"error": "connection_error"}

        except requests.exceptions.Timeout:
            st.error("⏰ Timeout: El servidor tardó demasiado en responder.")
            return {"error": "timeout"}

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 404:
                st.error("❌ Endpoint no encontrado.")
            elif status_code == 422:
                st.error("❌ Datos inválidos enviados al servidor.")
            elif status_code >= 500:
                st.error("🔧 Error interno del servidor.")
            else:
                st.error(f"❌ Error HTTP {status_code}")
            return {"error": "http_error", "status_code": status_code}

        except json.JSONDecodeError:
            st.error("❌ Respuesta inválida del servidor.")
            return {"error": "json_decode_error"}

        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            return {"error": "unexpected_error"}

# Instancia global del cliente API
api_client = APIClient()

# ==========================================
# FUNCIONES DE FINCAS (FINCAS API)
# ==========================================

def crear_finca(finca_data: Dict) -> Optional[Dict]:
    """
    Crea una nueva finca via API
    Retorna la finca creada o None si error
    """
    with st.spinner("Creando finca..."):
        response = api_client._make_request(
            "POST",
            "/fincas/",
            json=finca_data
        )

    if "error" in response:
        return None

    st.success("✅ Finca creada exitosamente")
    return response

def obtener_fincas() -> List[Dict]:
    """
    Obtiene lista de todas las fincas
    """
    response = api_client._make_request("GET", "/fincas/")

    if "error" in response:
        return []

    return response if isinstance(response, list) else []

def obtener_finca(finca_id: str) -> Optional[Dict]:
    """
    Obtiene una finca específica por ID
    """
    response = api_client._make_request("GET", f"/fincas/{finca_id}")

    if "error" in response:
        return None

    return response

def actualizar_finca(finca_id: str, finca_data: Dict) -> Optional[Dict]:
    """
    Actualiza una finca existente
    """
    with st.spinner("Actualizando finca..."):
        response = api_client._make_request(
            "PUT",
            f"/fincas/{finca_id}",
            json=finca_data
        )

    if "error" in response:
        return None

    st.success("✅ Finca actualizada exitosamente")
    return response

def eliminar_finca(finca_id: str) -> bool:
    """
    Elimina una finca
    """
    with st.spinner("Eliminando finca..."):
        response = api_client._make_request("DELETE", f"/fincas/{finca_id}")

    if "error" in response:
        return False

    st.success("✅ Finca eliminada exitosamente")
    return True

# ==========================================
# FUNCIONES DE PROYECTOS (PROYECTOS API)
# ==========================================

def crear_proyecto(proyecto_data: Dict) -> Optional[Dict]:
    """
    Crea un nuevo proyecto via API
    """
    with st.spinner("Creando proyecto..."):
        response = api_client._make_request(
            "POST",
            "/proyectos/",
            json=proyecto_data
        )

    if "error" in response:
        return None

    st.success("✅ Proyecto creado exitosamente")
    return response

def obtener_proyectos(filtros: Optional[Dict] = None) -> List[Dict]:
    """
    Obtiene lista de proyectos con filtros opcionales
    """
    params = filtros or {}
    response = api_client._make_request("GET", "/proyectos/", params=params)

    if "error" in response:
        return []

    return response if isinstance(response, list) else []

def obtener_proyecto(proyecto_id: str) -> Optional[Dict]:
    """
    Obtiene un proyecto específico por ID
    """
    response = api_client._make_request("GET", f"/proyectos/{proyecto_id}")

    if "error" in response:
        return None

    return response

def actualizar_proyecto(proyecto_id: str, proyecto_data: Dict) -> Optional[Dict]:
    """
    Actualiza un proyecto existente
    """
    with st.spinner("Actualizando proyecto..."):
        response = api_client._make_request(
            "PUT",
            f"/proyectos/{proyecto_id}",
            json=proyecto_data
        )

    if "error" in response:
        return None

    st.success("✅ Proyecto actualizado exitosamente")
    return response

def eliminar_proyecto(proyecto_id: str) -> bool:
    """
    Elimina un proyecto
    """
    with st.spinner("Eliminando proyecto..."):
        response = api_client._make_request("DELETE", f"/proyectos/{proyecto_id}")

    if "error" in response:
        return False

    st.success("✅ Proyecto eliminado exitosamente")
    return True

# ==========================================
# FUNCIONES DE EXPORTACIÓN (EXPORT API)
# ==========================================

def exportar_proyecto(proyecto_data: Dict, opciones: List[str]) -> Optional[Dict]:
    """
    Exporta un proyecto con opciones específicas
    """
    export_data = {
        "proyecto": proyecto_data,
        "opciones": opciones,
        "timestamp": datetime.now().isoformat()
    }

    with st.spinner("Generando exportación profesional..."):
        response = api_client._make_request(
            "POST",
            "/exportar/",
            json=export_data
        )

    if "error" in response:
        return None

    st.success("✅ Exportación generada exitosamente")
    return response

def descargar_exportacion(export_id: str) -> Optional[bytes]:
    """
    Descarga archivo de exportación
    """
    with st.spinner("Descargando archivo..."):
        response = api_client._make_request("GET", f"/exportar/{export_id}/download")

    if "error" in response:
        return None

    # En una implementación real, esto retornaría los bytes del archivo
    return b"mock_file_content"

# ==========================================
# FUNCIONES DE COMPATIBILIDAD (LEGACY)
# ==========================================

def load_fincas() -> List[Dict]:
    """Compatibilidad: carga fincas desde API"""
    return obtener_fincas()

def save_finca(finca: Dict) -> bool:
    """Compatibilidad: guarda finca via API"""
    if finca.get("id"):
        return actualizar_finca(finca["id"], finca) is not None
    else:
        return crear_finca(finca) is not None

def load_proyectos() -> List[Dict]:
    """Compatibilidad: carga proyectos desde API"""
    return obtener_proyectos()

def save_proyecto(proyecto: Dict) -> bool:
    """Compatibilidad: guarda proyecto via API"""
    if proyecto.get("id"):
        return actualizar_proyecto(proyecto["id"], proyecto) is not None
    else:
        return crear_proyecto(proyecto) is not None

# ==========================================
# FUNCIONES DE ESTADO Y MONITOREO
# ==========================================

def verificar_conexion_backend() -> bool:
    """
    Verifica si el backend está disponible
    """
    try:
        response = api_client._make_request("GET", "/health")
        return "error" not in response
    except:
        return False

def obtener_estadisticas() -> Dict:
    """
    Obtiene estadísticas del sistema
    """
    response = api_client._make_request("GET", "/estadisticas")

    if "error" in response:
        return {
            "fincas_count": 0,
            "proyectos_count": 0,
            "exportaciones_count": 0
        }

    return response

# ==========================================
# FUNCIONES DE UI INTEGRATION
# ==========================================

def mostrar_estado_conexion():
    """Muestra el estado de conexión con el backend en la UI"""
    if verificar_conexion_backend():
        st.success("🟢 Backend conectado")
    else:
        st.error("🔴 Backend desconectado - Modo demo activado")

        with st.expander("🔧 Solución de problemas"):
            st.markdown("""
            **Para conectar con el backend:**

            1. **Ejecuta el backend FastAPI:**
               ```bash
               cd backend
               python main.py
               ```

            2. **O ejecuta con uvicorn:**
               ```bash
               uvicorn backend.main:app --reload
               ```

            3. **Verifica que esté corriendo en:** `http://localhost:8000`

            4. **Documentación API:** `http://localhost:8000/docs`
            """)

def cache_con_api(func):
    """
    Decorador para cachear respuestas de API
    """
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"

        # Cache simple en session_state
        if "api_cache" not in st.session_state:
            st.session_state.api_cache = {}

        if cache_key in st.session_state.api_cache:
            cached_time, cached_data = st.session_state.api_cache[cache_key]
            # Cache válido por 5 minutos
            if (datetime.now() - cached_time).seconds < 300:
                return cached_data

        # Llamada real a API
        result = func(*args, **kwargs)

        # Guardar en cache
        st.session_state.api_cache[cache_key] = (datetime.now(), result)

        return result

    return wrapper

# Aplicar cache a funciones de lectura
obtener_fincas = cache_con_api(obtener_fincas)
obtener_proyectos = cache_con_api(obtener_proyectos)
obtener_estadisticas = cache_con_api(obtener_estadisticas)

# ==========================================
# FUNCIONES DE DEMO (FALLBACK)
# ==========================================

def demo_fincas() -> List[Dict]:
    """Datos demo de fincas para cuando el backend no está disponible"""
    return [
        {
            "id": "demo_1",
            "direccion": "Calle Demo 123, Madrid",
            "superficie_m2": 500,
            "precio_estimado": 150000,
            "retranqueos": {"front": 5, "side": 3, "back": 5},
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "demo_2",
            "direccion": "Avenida Demo 456, Barcelona",
            "superficie_m2": 800,
            "precio_estimado": 250000,
            "retranqueos": {"front": 6, "side": 4, "back": 6},
            "created_at": datetime.now().isoformat()
        }
    ]

def demo_proyectos() -> List[Dict]:
    """Datos demo de proyectos para cuando el backend no está disponible"""
    return [
        {
            "id": "demo_proj_1",
            "finca_id": "demo_1",
            "titulo": "Casa Moderna Demo",
            "descripcion": "Proyecto demo generado automáticamente",
            "plan_json": {
                "program": {"rooms": [], "total_m2": 120},
                "site": {"area": 500}
            },
            "estado": "borrador",
            "created_at": datetime.now().isoformat()
        }
    ]

# ==========================================
# FUNCIONES DE AUTO-DETECCIÓN DE MODO
# ==========================================

def usar_api_real() -> bool:
    """Determina si usar API real o modo demo"""
    return verificar_conexion_backend()

def obtener_fincas_con_fallback() -> List[Dict]:
    """Obtiene fincas con fallback a demo si API no disponible"""
    if usar_api_real():
        return obtener_fincas()
    else:
        st.info("📱 Usando datos demo - Backend no disponible")
        return demo_fincas()

def obtener_proyectos_con_fallback(filtros: Optional[Dict] = None) -> List[Dict]:
    """Obtiene proyectos con fallback a demo si API no disponible"""
    if usar_api_real():
        return obtener_proyectos(filtros)
    else:
        st.info("📱 Usando datos demo - Backend no disponible")
        return demo_proyectos()

# ==========================================
# INICIALIZACIÓN
# ==========================================

def inicializar_conexion():
    """Inicializa la conexión y configura el estado"""
    if "api_initialized" not in st.session_state:
        st.session_state.api_initialized = True

        # Mostrar estado de conexión
        mostrar_estado_conexion()

        # Configurar modo de operación
        st.session_state.usar_api_real = usar_api_real()

        if st.session_state.usar_api_real:
            st.session_state.modo_operacion = "API Real"
        else:
            st.session_state.modo_operacion = "Modo Demo"

# Ejecutar inicialización automática (solo en contexto Streamlit)
try:
    inicializar_conexion()
except:
    pass  # Silenciar errores si no hay contexto Streamlit