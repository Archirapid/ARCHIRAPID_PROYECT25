# IA Manager - Gestión de IA real con Ollama y Llama

import ollama
import json
from typing import Dict, Any, Optional

def feedback_ia(configuracion: Dict[str, Any]) -> str:
    """
    Genera feedback inteligente usando IA real (Llama via Ollama).
    Analiza configuración de diseño y sugiere mejoras basadas en normativa española.

    Args:
        configuracion: Dict con datos del diseño (m2, habitaciones, plantas, etc.)

    Returns:
        str: Feedback inteligente o mensaje de error
    """
    try:
        # Preparar prompt para IA
        prompt = f"""
        Analiza este diseño de vivienda en finca española y proporciona feedback inteligente:

        Configuración del diseño:
        - Superficie construida: {configuracion.get('superficie_construida', 'N/A')} m²
        - Número de habitaciones: {configuracion.get('habitaciones', 'N/A')}
        - Número de plantas: {configuracion.get('plantas', 'N/A')}
        - Retranqueo: {configuracion.get('retranqueo', 'N/A')} m
        - Tipo de finca: {configuracion.get('tipo_finca', 'N/A')}
        - Superficie de parcela: {configuracion.get('superficie_parcela', 'N/A')} m²

        Basándote en la normativa urbanística española (LOE, CTE, etc.):
        1. Evalúa la viabilidad del diseño
        2. Sugiere mejoras para optimizar espacio y cumplimiento normativo
        3. Identifica posibles problemas de edificabilidad
        4. Recomienda ajustes para mayor eficiencia energética

        Proporciona un análisis conciso pero completo.
        """

        # Llamar a Ollama con modelo llama3
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}]
        )

        return response['message']['content']

    except Exception as e:
        # Fallback: devolver mensaje de error
        return f"Error al generar feedback IA: {str(e)}. Verifica que Ollama esté instalado y el modelo 'llama3' descargado."

def evaluar_ia_simulada(configuracion: Dict[str, Any]) -> str:
    """
    Fallback: Evaluación simulada cuando IA real no está disponible.
    """
    return """
    📊 **Evaluación Simulada (IA no disponible)**

    ✅ **Aspectos Positivos:**
    - Diseño básico viable
    - Distribución funcional

    ⚠️ **Recomendaciones:**
    - Verificar normativa local
    - Considerar eficiencia energética
    - Consultar con arquitecto profesional

    💡 **Nota:** Para feedback inteligente real, instala Ollama y modelo llama3.
    """

def feedback_ia_con_fallback(configuracion: Dict[str, Any]) -> str:
    """
    Función principal: Intenta IA real, fallback a simulada.
    """
    try:
        # Intentar IA real
        feedback = feedback_ia(configuracion)
        if "Error al generar" not in feedback:
            return f"🤖 **Feedback IA Real (Llama3):**\n\n{feedback}"
        else:
            # Fallback
            return evaluar_ia_simulada(configuracion)
    except:
        # Fallback seguro
        return evaluar_ia_simulada(configuracion)