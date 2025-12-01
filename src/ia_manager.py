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

        # Intentar con modelo más pequeño primero si el grande falla
        models_to_try = ['llama3.1:latest', 'qwen3:4b']
        
        for model in models_to_try:
            try:
                # Llamar a Ollama con modelo disponible
                response = ollama.chat(
                    model=model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response['message']['content']
            except Exception as model_error:
                print(f"Modelo {model} falló: {model_error}")
                continue
        
        # Si todos los modelos fallan, usar fallback
        raise Exception("No se pudo cargar ningún modelo de IA")

    except Exception as e:
        # Fallback: devolver mensaje de error
        error_msg = str(e)
        if "system memory" in error_msg.lower():
            return f"Error: Memoria insuficiente para IA real ({error_msg}). Se recomienda al menos 8GB RAM para modelos avanzados."
        else:
            return f"Error al generar feedback IA: {error_msg}. Usando evaluación simulada."

def evaluar_ia_simulada(configuracion: Dict[str, Any]) -> str:
    """
    Fallback: Evaluación simulada cuando IA real no está disponible.
    Proporciona análisis inteligente basado en reglas y mejores prácticas.
    """
    superficie = configuracion.get('superficie_construida', 0)
    habitaciones = configuracion.get('habitaciones', 0)
    plantas = configuracion.get('plantas', 1)
    retranqueo = configuracion.get('retranqueo', 3.0)
    tipo_finca = configuracion.get('tipo_finca', 'urbana')
    parcela = configuracion.get('superficie_parcela', 0)
    
    # Análisis inteligente simulado
    analisis = []
    recomendaciones = []
    
    # Análisis de superficie
    if superficie > 0:
        superficie_por_habitacion = superficie / max(habitaciones, 1)
        if superficie_por_habitacion < 25:
            analisis.append("⚠️ Superficie por habitación baja (<25m²/hab)")
            recomendaciones.append("Considerar aumentar superficie habitable")
        elif superficie_por_habitacion > 50:
            analisis.append("✅ Buena superficie por habitación")
    
    # Análisis de edificabilidad
    if parcela > 0 and superficie > 0:
        ratio_edificabilidad = superficie / parcela
        if tipo_finca == 'urbana':
            if ratio_edificabilidad > 0.6:
                analisis.append("⚠️ Alto ratio de edificabilidad (>60%)")
                recomendaciones.append("Verificar límites de edificabilidad local")
            elif ratio_edificabilidad < 0.2:
                analisis.append("ℹ️ Bajo aprovechamiento de parcela")
                recomendaciones.append("Posibilidad de ampliación")
        else:  # rural
            if ratio_edificabilidad > 0.1:
                analisis.append("⚠️ Ratio elevado para finca rústica")
    
    # Análisis de retranqueo
    if retranqueo < 3.0:
        analisis.append("⚠️ Retranqueo inferior a 3m")
        recomendaciones.append("Verificar normativa de retranqueo local")
    else:
        analisis.append("✅ Retranqueo adecuado")
    
    # Análisis de plantas
    if plantas > 2:
        analisis.append("⚠️ Más de 2 plantas pueden requerir ascensor")
        recomendaciones.append("Considerar accesibilidad y normativa")
    
    # Recomendaciones generales
    recomendaciones.extend([
        "Consultar PGOU municipal para normativa específica",
        "Considerar orientación solar para eficiencia energética",
        "Evaluar impacto ambiental y certificación energética",
        "Verificar servidumbres y restricciones de la parcela"
    ])
    
    return f"""
🤖 **Análisis Arquitectónico Inteligente (Simulado)**

**📊 Configuración Analizada:**
- Superficie: {superficie} m² | Habitaciones: {habitaciones} | Plantas: {plantas}
- Retranqueo: {retranqueo}m | Tipo: {tipo_finca.title()} | Parcela: {parcela} m²

**🔍 Aspectos Evaluados:**
""" + "\n".join(f"- {item}" for item in analisis) + f"""

**💡 Recomendaciones:**
""" + "\n".join(f"- {rec}" for rec in recomendaciones) + f"""

**⚠️ Limitación:** IA real no disponible (requiere ≥8GB RAM).
Para análisis con IA avanzada, actualiza hardware o usa servicio cloud.
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