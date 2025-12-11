#!/usr/bin/env python3
"""
Panel Cliente Integrado ARCHIRAPID
IA Avanzada + Precios en Vivo + Exportación Profesional
"""

import streamlit as st
import json
import os
from datetime import datetime
import time
import requests

# ==========================================
# COMPONENTES LOCALES
# ==========================================

def render_header():
    """Header con logo de ARCHIRAPID"""
    col1, col2 = st.columns([1, 3])

    with col1:
        # Logo de ARCHIRAPID
        logo_path = "assets/branding/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        else:
            st.title("🏗️ ARCHIRAPID")

    with col2:
        st.markdown("### IA Avanzada + Precios en Vivo + Exportación Profesional")
        st.markdown("*Diseña tu casa ideal con inteligencia artificial*")

    st.markdown("---")

def render_footer():
    """Footer con información de contacto"""
    st.divider()
    st.caption("© 2025 ARCHIRAPID — MVP demostrativo")
    st.caption("📧 moskovia@me.com | 📱 +34 623 172 704 | 📍 Madrid (Spain)")

# ==========================================
# IMPORTS DEL SISTEMA INTEGRADO
# ==========================================

from design_ops import parametric_engine, calculate_live_price
from export_ops import generate_professional_export, get_export_options
from data_access import (
    obtener_fincas_con_fallback, obtener_proyectos_con_fallback,
    crear_proyecto, actualizar_proyecto, exportar_proyecto,
    mostrar_estado_conexion, inicializar_conexion
)

# ==========================================
# FUNCIONES DE DIAGNÓSTICO
# ==========================================

def check_backend():
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        return r.status_code == 200 and r.json().get("status") == "ok"
    except Exception:
        return False

# ==========================================
# CONFIGURACIÓN DE LA APP
# ==========================================

st.set_page_config(
    page_title="ARCHIRAPID - IA + Precios en Vivo",
    layout="wide",
    page_icon="🏗️"
)

# ==========================================
# INICIALIZACIÓN DEL SISTEMA
# ==========================================

inicializar_conexion()

# ==========================================
# HEADER PRINCIPAL
# ==========================================

def render_app_header():
    """Header de la aplicación"""
    render_header()

# ==========================================
# PANEL PRINCIPAL DEL CLIENTE
# ==========================================

def main():
    # Mostrar header siempre
    render_app_header()

    # Indicador global de backend
    BACKEND_URL = "http://localhost:8000"
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        is_backend_ok = r.status_code == 200 and r.json().get("status") == "ok"
    except Exception:
        is_backend_ok = False

    status_label = "🟢 Backend conectado - Modo Producción" if is_backend_ok else "🔴 Backend no disponible - Usando demo"
    st.markdown(f"**{status_label}**")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Actualizar", help="Actualizar estado del backend"):
            st.rerun()

    # Sidebar con navegación
    with st.sidebar:
        st.markdown("### 🎯 Mi Panel")

        # Navegación principal
        opciones = [
            "🏠 Inicio",
            "🏡 Ficha de Finca",
            "🏠 Mapa Inmobiliario",
            "👥 Registro Arquitectos",
            "🎨 Diseñar con IA",
            "💰 Precios en Vivo",
            "📦 Exportar Proyecto",
            "📊 Mis Proyectos",
            "🏢 Intranet Arquitectos",
            "🧠 Gemelo Digital"
        ]

        seleccion = st.radio("Navegación:", opciones, key="navegacion_radio")
        
        # Actualizar session_state
        st.session_state.seleccion = seleccion

        # Sección de acceso (no bloqueante)
        st.markdown("### 🔐 Acceso")
        email = st.text_input(
            "Tu email (opcional para explorar, requerido para guardar/exportar)",
            value=st.session_state.get("email", ""),
            key="user_email"
        )
        if email:
            st.session_state["email"] = email
            st.success(f"✅ Acceso completo: {email}")
        else:
            st.info("💡 Puedes explorar libremente. Para guardar/exportar, introduce tu email.")

        # Información del sistema
        with st.expander("ℹ️ Estado del Sistema"):
            mostrar_estado_conexion()

            if st.session_state.get("proyecto_actual"):
                st.markdown(f"**Proyecto:** {st.session_state.proyecto_actual.get('titulo', 'N/A')}")
                st.markdown(f"**Versión:** {st.session_state.proyecto_actual.get('version', 0)}")

    # Contenido principal - SIEMPRE accesible
    if seleccion == "🏠 Inicio":
        render_inicio()
    elif seleccion == "🏡 Ficha de Finca":
        render_ficha_finca()
    elif seleccion == "🏠 Mapa Inmobiliario":
        render_mapa_inmobiliario()
    elif seleccion == "👥 Registro Arquitectos":
        render_registro_arquitectos()
    elif seleccion == "🎨 Diseñar con IA":
        render_diseno_ia()
    elif seleccion == "💰 Precios en Vivo":
        render_precios_vivo()
    elif seleccion == "📦 Exportar Proyecto":
        render_exportacion()
    elif seleccion == "📊 Mis Proyectos":
        render_mis_proyectos()
    elif seleccion == "🏢 Intranet Arquitectos":
        render_intranet_arquitectos()
    elif seleccion == "🧠 Gemelo Digital":
        render_gemelo_digital()
        render_precios_vivo()
    elif seleccion == "📦 Exportar Proyecto":
        render_exportacion()
    elif seleccion == "📊 Mis Proyectos":
        render_mis_proyectos(email)

# ==========================================
# PANTALLA DE INICIO
# ==========================================

def render_inicio():
    st.header("🏠 Bienvenido a ARCHIRAPID")

    st.markdown("""
    ### 🚀 Tu casa ideal en minutos con IA

    **ARCHIRAPID** combina inteligencia artificial avanzada con precios en tiempo real
    para crear diseños arquitectónicos profesionales al instante.

    #### ✨ Lo que puedes hacer:
    - 🎨 **Diseñar con IA**: Describe tu casa ideal y la IA la crea
    - 💰 **Precios en Vivo**: Ve cómo cambian los precios en tiempo real
    - 📦 **Exportación Profesional**: Obtén planos CAD, memorias técnicas y presupuestos
    - 🔄 **Iteración Continua**: Modifica y perfecciona tu diseño paso a paso
    """)

    # Mostrar mapa con fincas disponibles
    render_mapa_inmobiliario()

    # Lista lateral con fincas para explorar
    st.markdown("---")
    st.subheader("🏡 Fincas Disponibles")

    fincas = obtener_fincas_con_fallback()

    if not fincas:
        st.warning("No hay fincas disponibles. El sistema está en modo demo.")
        return

    # Mostrar lista de fincas con botones de acción
    for finca in fincas:
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{finca.get('direccion', 'Sin dirección')}**")
                st.caption(f"Superficie: {finca.get('superficie_m2', 0)} m²")

            with col2:
                if st.button("Más detalles", key=f"detalles_{finca['id']}", use_container_width=True):
                    st.session_state.finca_actual = finca
                    st.session_state.seleccion = "🏡 Ficha de Finca"
                    st.rerun()

        st.markdown("---")

    render_footer()

def render_ficha_finca():
    st.header("🏡 Ficha de Finca")

    if "finca_actual" not in st.session_state:
        st.warning("No hay finca seleccionada. Ve a Inicio y selecciona una finca.")
        return

    finca = st.session_state.finca_actual

    # Título con dirección
    st.subheader(f"📍 {finca.get('direccion', 'Finca sin dirección')}")

    # Mostrar información técnica de la finca
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Datos Técnicos")
        st.metric("Superficie Total", f"{finca.get('superficie_m2', 0)} m²")
        st.metric("Máx. Construible", f"{int(finca.get('superficie_m2', 0) * 0.33)} m²")
        st.metric("Plantas Máximas", "2 plantas")

        # Validación de reglas
        superficie = finca.get('superficie_m2', 0)
        max_construible = int(superficie * 0.33)

        if max_construible > 0:
            st.success(f"✅ Reglas cumplidas: Máx. {max_construible}m² construibles (33% de {superficie}m²)")
        else:
            st.error("❌ Error en cálculo de superficie construible")

    with col2:
        st.markdown("### 🎯 Acciones Rápidas")

        # Botón para diseñar con IA
        if st.button("🎨 Diseñar con IA sobre esta finca", type="primary", use_container_width=True):
            st.session_state.pantalla_actual = "diseno_ia"
            st.rerun()

        # Botón para ver proyectos existentes
        if st.button("📊 Ver Proyectos Existentes", use_container_width=True):
            proyectos = obtener_proyectos_con_fallback({"finca_id": finca["id"]})
            if proyectos:
                st.session_state.proyectos_finca = proyectos
                st.session_state.pantalla_actual = "proyectos_finca"
                st.rerun()
            else:
                st.info("No hay proyectos para esta finca aún. ¡Sé el primero en diseñar!")

        # Botón para exportar (placeholder)
        if st.button("📦 Exportar Proyecto", use_container_width=True):
            st.info("Selecciona un proyecto existente para exportar, o crea uno nuevo con IA.")

        # Botón para contactar (placeholder)
        if st.button("📞 Contactar Propietario", use_container_width=True):
            st.info("Funcionalidad de contacto próximamente disponible.")

    # Información adicional
    st.markdown("---")
    st.markdown("### 📋 Información Adicional")
    st.info(f"**Estado:** {finca.get('estado', 'No especificado')}")
    st.info("**Nota:** Esta finca está disponible para diseño arquitectónico con IA. Los diseños cumplen con las normativas locales de edificabilidad.")

    render_footer()

def render_diseno_ia():
    st.header("🎨 Diseño Inteligente con IA")

    if "finca_actual" not in st.session_state:
        st.warning("Primero selecciona una finca en la pantalla de inicio")
        return

    finca = st.session_state.finca_actual

    # Chat con IA para diseño
    st.subheader("💬 Describe tu casa ideal")

    # Historial de conversación
    if "chat_historial" not in st.session_state:
        st.session_state.chat_historial = []

    # Área de chat
    chat_container = st.container()

    with chat_container:
        for mensaje in st.session_state.chat_historial[-10:]:  # Últimos 10 mensajes
            if mensaje["tipo"] == "usuario":
                st.markdown(f"**👤 Tú:** {mensaje['texto']}")
            else:
                st.markdown(f"**🤖 IA:** {mensaje['texto']}")

    # Input para nuevo mensaje
    col1, col2 = st.columns([4, 1])

    with col1:
        mensaje_usuario = st.text_input(
            "Describe qué quieres en tu casa:",
            placeholder="Ej: Quiero una casa moderna de 3 habitaciones con piscina y garaje...",
            key="mensaje_ia",
            label_visibility="collapsed"
        )

    with col2:
        if st.button("📤 Enviar", type="primary", use_container_width=True):
            if mensaje_usuario.strip():
                # Añadir mensaje del usuario
                st.session_state.chat_historial.append({
                    "tipo": "usuario",
                    "texto": mensaje_usuario,
                    "timestamp": datetime.now()
                })

                # Procesar con IA y generar respuesta
                respuesta_ia = procesar_mensaje_ia(mensaje_usuario, finca)

                st.session_state.chat_historial.append({
                    "tipo": "ia",
                    "texto": respuesta_ia,
                    "timestamp": datetime.now()
                })

                st.rerun()

    # Mostrar plan actual si existe
    if "plan_actual" in st.session_state:
        render_plan_actual()

    # Acciones del plan
    if st.session_state.get("plan_actual"):
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Modificar con IA", use_container_width=True):
                st.info("Describe los cambios que quieres hacer")

        with col2:
            if st.button("💰 Ver Precios en Vivo", type="primary", use_container_width=True):
                st.session_state.pantalla_actual = "precios_vivo"
                st.rerun()

        with col3:
            if st.button("📦 Exportar Profesional", type="primary", use_container_width=True):
                st.session_state.pantalla_actual = "exportacion"
                st.rerun()

def procesar_mensaje_ia(mensaje: str, finca: dict) -> str:
    """
    Procesa mensaje del usuario y actualiza el plan usando el motor paramétrico
    """
    # Lógica simplificada de procesamiento de IA
    # En producción, esto usaría un LLM avanzado

    mensaje_lower = mensaje.lower()

    # Inicializar plan si no existe
    if "plan_actual" not in st.session_state:
        st.session_state.plan_actual = parametric_engine({}, "validate", {"finca": finca})

    plan = st.session_state.plan_actual

    # Procesar diferentes tipos de solicitudes
    if "habitacion" in mensaje_lower or "dormitorio" in mensaje_lower:
        # Extraer número de habitaciones
        import re
        nums = re.findall(r'\d+', mensaje)
        if nums:
            num_hab = int(nums[0])
            for i in range(num_hab):
                plan = parametric_engine(plan, "add_room", {
                    "type": "bedroom",
                    "name": f"Dormitorio {i+1}"
                })
            respuesta = f"✅ Añadidas {num_hab} habitaciones al plano"

    elif "baño" in mensaje_lower or "bathroom" in mensaje_lower:
        nums = re.findall(r'\d+', mensaje)
        if nums:
            num_banos = int(nums[0])
            for i in range(num_banos):
                plan = parametric_engine(plan, "add_room", {
                    "type": "bathroom",
                    "name": f"Baño {i+1}"
                })
            respuesta = f"✅ Añadidos {num_banos} baños al plano"

    elif "piscina" in mensaje_lower or "pool" in mensaje_lower:
        plan = parametric_engine(plan, "add_system", {
            "system_type": "pool",
            "config": {"exists": True, "area": 50}
        })
        respuesta = "✅ Piscina añadida al diseño"

    elif "moderno" in mensaje_lower or "modern" in mensaje_lower:
        plan = parametric_engine(plan, "set_style", {"style": "modern"})
        respuesta = "✅ Estilo moderno aplicado al diseño"

    elif "clasico" in mensaje_lower or "classic" in mensaje_lower:
        plan = parametric_engine(plan, "set_style", {"style": "classic"})
        respuesta = "✅ Estilo clásico aplicado al diseño"

    elif "distribuir" in mensaje_lower or "layout" in mensaje_lower:
        plan = parametric_engine(plan, "auto_layout")
        respuesta = "✅ Distribución automática optimizada"

    else:
        respuesta = "🤔 Entiendo tu solicitud. Estoy procesando los cambios en el plano. ¿Puedes darme más detalles sobre qué tipo de espacio necesitas?"

    # Actualizar plan en sesión
    st.session_state.plan_actual = plan

    return respuesta

def render_plan_actual():
    """Muestra el plan actual en formato visual"""
    plan = st.session_state.plan_actual

    st.subheader("📋 Plan Actual")

    col1, col2, col3 = st.columns(3)

    with col1:
        rooms = plan.get("program", {}).get("rooms", [])
        st.metric("Habitaciones", len([r for r in rooms if r.get("type") == "bedroom"]))
        st.metric("Baños", len([r for r in rooms if r.get("type") == "bathroom"]))

    with col2:
        total_m2 = plan.get("program", {}).get("total_m2", 0)
        st.metric("Superficie Total", f"{total_m2} m²")

    with col3:
        precio = calculate_live_price(plan)
        st.metric("Presupuesto Estimado", f"€{precio['breakdown']['total']:,.0f}")

    # Mostrar distribución
    with st.expander("📊 Ver distribución detallada"):
        st.json(plan)

    render_footer()

def render_precios_vivo():
    st.header("💰 Precios en Vivo")

    if "plan_actual" not in st.session_state:
        st.warning("Primero crea un diseño en la sección 'Diseñar con IA'")
        return

    plan = st.session_state.plan_actual

    st.markdown("""
    ### 🎛️ Configurador Interactivo

    Modifica las características de tu casa y ve cómo cambian los precios **en tiempo real**,
    igual que configurar un coche.
    """)

    # Controles interactivos en columnas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Características de la Vivienda")

        # Sistema eléctrico inteligente
        electrico_smart = st.checkbox(
            "⚡ Sistema Eléctrico Inteligente (+€35/m²)",
            value=plan.get("systems", {}).get("electrical", {}).get("smart_home", False)
        )

        # Iluminación LED
        iluminacion_led = st.checkbox(
            "💡 Iluminación LED Premium (+€25/m²)",
            value=plan.get("systems", {}).get("lighting", {}).get("led_lighting", False)
        )

        # Domótica completa
        domotica = st.checkbox(
            "🏠 Domótica Completa (+€35/m²)",
            value=plan.get("systems", {}).get("smart_home", {}).get("enabled", False)
        )

        # Materiales premium
        materiales_premium = st.selectbox(
            "🛠️ Calidad de Materiales",
            ["Estándar", "Premium (+15%)", "Lujo (+30%)"],
            index=0
        )

    with col2:
        st.subheader("🌟 Acabados y Equipamiento")

        # Piscina
        piscina = st.checkbox(
            "🏊 Piscina (+€300/m²)",
            value=plan.get("site", {}).get("pool", {}).get("exists", False)
        )

        # Cocina premium
        cocina_premium = st.checkbox(
            "👨‍🍳 Cocina Premium (+€15,000)",
            value=False  # Por defecto no marcado
        )

        # Baños premium
        banos_premium = st.checkbox(
            "🛁 Baños Premium (+€8,000 c/u)",
            value=False
        )

        # Garaje
        garaje = st.checkbox(
            "🚗 Garaje (+€25/m²)",
            value=False
        )

    # Aplicar cambios al plan en tiempo real
    plan_actualizado = plan.copy()

    # Aplicar sistemas
    if electrico_smart:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "electrical",
            "config": {"smart_home": True}
        })

    if iluminacion_led:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "lighting",
            "config": {"led_lighting": True}
        })

    if domotica:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "smart_home",
            "config": {"enabled": True}
        })

    # Aplicar piscina
    if piscina:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "pool",
            "config": {"exists": True, "area": 50}
        })

    # Calcular precios con los cambios
    pricing = calculate_live_price(plan_actualizado)

    # Mostrar precios en tiempo real
    st.markdown("---")
    st.subheader("💎 Precio Total en Tiempo Real")

    # Métrica principal
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Precio Base",
            f"€{pricing['breakdown']['subtotal_construction']:,.0f}",
            help="Construcción básica"
        )

    with col2:
        st.metric(
            "Sistemas",
            f"€{pricing['breakdown']['systems']:,.0f}",
            help="Instalaciones avanzadas"
        )

    with col3:
        st.metric(
            "Acabados",
            f"€{pricing['breakdown']['finishes']:,.0f}",
            help="Materiales y mobiliario"
        )

    with col4:
        st.metric(
            "TOTAL",
            f"€{pricing['breakdown']['total']:,.0f}",
            delta=f"€{pricing['per_m2']:,.0f}/m²",
            help="Precio final completo"
        )

    # Desglose detallado
    with st.expander("📊 Desglose Completo del Presupuesto"):
        st.markdown("#### 🏗️ Construcción")
        st.write(f"- Base: €{pricing['breakdown']['base_construction']:,.0f}")
        st.write(f"- Multiplicador calidad: {pricing['breakdown']['construction_multiplier']:.2f}x")
        st.write(f"- **Subtotal construcción: €{pricing['breakdown']['subtotal_construction']:,.0f}**")

        st.markdown("#### ⚡ Sistemas e Instalaciones")
        st.write(f"- Sistemas avanzados: €{pricing['breakdown']['systems']:,.0f}")
        st.write(f"- Materiales: €{pricing['breakdown']['materials']:,.0f}")
        st.write(f"- Acabados: €{pricing['breakdown']['finishes']:,.0f}")

        st.markdown("#### 💼 Honorarios y Licencias")
        st.write(f"- Honorarios profesionales: €{pricing['breakdown']['professional_fees']:,.0f}")
        st.write(f"- Impuestos y licencias: €{pricing['breakdown']['taxes_licenses']:,.0f}")

        st.markdown(f"#### 📅 Cronograma: {pricing['estimated_duration_months']} meses")

    # Opciones de financiación
    with st.expander("💳 Opciones de Financiación"):
        for opcion in pricing["financing_options"]:
            st.markdown(f"**{opcion['type']}:** €{opcion['monthly_payment']:.0f}/meso")
            st.caption(f"Total a pagar: €{opcion['final_amount']:,.0f}")

    # Guardar cambios
    if st.button("💾 Guardar Configuración", type="primary"):
        st.session_state.plan_actual = plan_actualizado
        st.success("✅ Configuración guardada exitosamente")

    # Continuar al siguiente paso
    if st.button("📦 Continuar a Exportación Profesional", type="primary"):
        st.session_state.pantalla_actual = "exportacion"
        st.rerun()

    render_footer()

def render_exportacion():
    st.header("📦 Exportación Profesional")

    if "plan_actual" not in st.session_state:
        st.warning("Primero crea un diseño en la sección 'Diseñar con IA'")
        return

    plan = st.session_state.plan_actual

    st.markdown("""
    ### 🎯 Exportación Profesional Completa

    Genera todos los documentos técnicos necesarios para construir tu casa:
    planos CAD, memorias técnicas, presupuestos detallados y más.
    """)

    # Opciones de exportación disponibles
    opciones_disponibles = get_export_options()

    st.subheader("📋 Selecciona qué documentos necesitas:")

    # Crear checkboxes para cada opción
    opciones_seleccionadas = []
    cols = st.columns(2)

    for i, opcion in enumerate(opciones_disponibles):
        col_idx = i % 2
        with cols[col_idx]:
            if st.checkbox(opcion, value=True):  # Por defecto todas seleccionadas
                opciones_seleccionadas.append(opcion)

    # Información del proyecto
    st.markdown("---")
    st.subheader("📊 Información del Proyecto")

    col1, col2 = st.columns(2)

    with col1:
        titulo = st.text_input(
            "Título del proyecto:",
            value=f"Proyecto ARCHIRAPID - {datetime.now().strftime('%d/%m/%Y')}"
        )

        descripcion = st.text_area(
            "Descripción:",
            value="Proyecto de vivienda unifamiliar diseñado con IA avanzada",
            height=100
        )

    with col2:
        autor = st.text_input("Autor:", value="Cliente ARCHIRAPID")
        version = st.text_input("Versión:", value="1.0")

        # Calcular tamaño estimado
        from export_ops import estimate_export_size
        tamano_estimado = estimate_export_size(opciones_seleccionadas)
        st.metric("Tamaño estimado", f"{tamano_estimado:.1f} MB")

    # Botón de exportación
    if st.button("🚀 Generar Exportación Profesional", type="primary", use_container_width=True):
        with st.spinner("🎨 Generando documentos profesionales... Esto puede tomar unos minutos"):

            # Preparar datos del proyecto
            proyecto_data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "autor": autor,
                "version": version,
                "plan_json": plan,
                "fecha_creacion": datetime.now().isoformat()
            }

            # Generar exportación
            try:
                export_result = exportar_proyecto(proyecto_data, opciones_seleccionadas)

                if export_result:
                    st.success("✅ ¡Exportación completada exitosamente!")

                    # Mostrar resumen
                    st.subheader("📁 Archivos Generados")

                    if "files_generated" in export_result:
                        for archivo in export_result["files_generated"]:
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write(f"📄 {archivo.get('description', archivo.get('filename', 'Archivo'))}")
                            with col2:
                                st.write(f"{archivo.get('type', 'N/A')}")
                            with col3:
                                st.write(f"{archivo.get('size_bytes', 0) / 1024:.1f} KB")

                    # Botón de descarga del bundle
                    if "bundle_file" in export_result:
                        st.download_button(
                            label="📥 Descargar Bundle Completo (ZIP)",
                            data=b"mock_zip_content",  # En producción sería el contenido real
                            file_name=export_result["bundle_file"].get("filename", "export.zip"),
                            mime="application/zip",
                            use_container_width=True
                        )

                    st.balloons()

                else:
                    st.error("❌ Error al generar la exportación")

            except Exception as e:
                st.error(f"❌ Error durante la exportación: {str(e)}")

    # Información adicional
    with st.expander("ℹ️ ¿Qué incluye cada documento?"):
        st.markdown("""
        #### 📄 Memoria Técnica PDF
        - Descripción completa del proyecto
        - Justificación técnica de las soluciones adoptadas
        - Cálculos estructurales y de instalaciones
        - Presupuesto detallado
        - Anexos con normativas aplicables

        #### 🏗️ Planos CAD/DWG
        - Planta baja, alzados y secciones
        - Planos de estructura, instalaciones y detalles
        - Formato compatible con AutoCAD y software similar

        #### 💰 Presupuesto Detallado
        - Desglose completo por partidas
        - Cronograma de pagos sugerido
        - Opciones de financiación
        - Comparativo de calidades

        #### 📊 Análisis Estructural
        - Cálculos de estructura portante
        - Análisis de cargas y solicitaciones
        - Certificados de cumplimiento normativo

        #### ⚡ Planos Eléctricos
        - Diagrama unifilar
        - Distribución de circuitos
        - Ubicación de puntos de luz y tomas

        #### 🚿 Planos de Fontanería
        - Distribución de agua fría y caliente
        - Sistema de evacuación
        - Ubicación de aparatos sanitarios

        #### 📋 Lista de Materiales
        - Catálogo completo de materiales
        - Cantidades y calidades
        - Referencias de proveedores

        #### 🪑 Plano de Muebles
        - Distribución del mobiliario
        - Especificaciones técnicas
        - Plano de implantación 2D
        """)

# ==========================================
# MIS PROYECTOS
# ==========================================

def render_mis_proyectos():
    st.header("📊 Mis Proyectos")

    # Obtener proyectos
    proyectos = obtener_proyectos_con_fallback()

    if not proyectos:
        st.info("Aún no tienes proyectos. ¡Comienza diseñando con IA!")
        return

    # Mostrar proyectos en cards
    for proyecto in proyectos:
        with st.expander(f"🏗️ {proyecto.get('titulo', 'Proyecto sin título')}"):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Versión", proyecto.get("version", 1))
                st.metric("Superficie", f"{proyecto.get('total_m2', 0)} m²")

            with col2:
                presupuesto = proyecto.get("presupuesto", 0)
                st.metric("Presupuesto", f"€{presupuesto:,.0f}")

            with col3:
                estado = proyecto.get("estado", "borrador")
                if estado == "completado":
                    st.success("✅ Completado")
                elif estado == "en_progreso":
                    st.warning("🔄 En progreso")
                else:
                    st.info("📝 Borrador")

            # Acciones
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("👁️ Ver detalles", key=f"ver_{proyecto['id']}"):
                    st.session_state.proyecto_seleccionado = proyecto
                    st.session_state.pantalla_actual = "detalle_proyecto"

            with col2:
                if st.button("✏️ Continuar editando", key=f"editar_{proyecto['id']}"):
                    st.session_state.plan_actual = proyecto.get("plan_json", {})
                    st.session_state.pantalla_actual = "diseno_ia"

            with col3:
                if st.button("📦 Exportar", key=f"exportar_{proyecto['id']}"):
                    st.session_state.plan_actual = proyecto.get("plan_json", {})
                    st.session_state.pantalla_actual = "exportacion"

# ==========================================
# MAPA INMOBILIARIO
# ==========================================

def render_mapa_inmobiliario():
    st.header("🏠 Mapa Inmobiliario ARCHIRAPID")

    # Obtener fincas
    fincas = obtener_fincas_con_fallback()

    if not fincas:
        st.warning("No hay fincas disponibles para mostrar en el mapa.")
        return

    # Crear mapa interactivo
    import folium
    from streamlit_folium import st_folium

    # Centro de España por defecto
    mapa = folium.Map(
        location=[40.4168, -3.7038],  # Madrid
        zoom_start=6,
        tiles='OpenStreetMap'
    )

    # Añadir fincas al mapa
    for finca in fincas:
        # Coordenadas (usar reales si existen, sino cercanas a Madrid)
        lat = finca.get('ubicacion_geo', {}).get('lat', 40.4168 + (hash(finca['id']) % 100 - 50) * 0.01)
        lng = finca.get('ubicacion_geo', {}).get('lng', -3.7038 + (hash(finca['id']) % 100 - 50) * 0.01)

        # Color según estado
        color = 'green' if finca.get('estado') == 'disponible' else 'orange'

        # Popup con información
        popup_html = f"""
        <div style="width: 200px;">
            <h4>{finca.get('direccion', 'Finca sin dirección')}</h4>
            <p><strong>Superficie:</strong> {finca.get('superficie_m2', 0)} m²</p>
            <p><strong>Máx. Construible:</strong> {finca.get('max_construible_m2', 0)} m²</p>
            <p><strong>Estado:</strong> {finca.get('estado', 'N/A')}</p>
        </div>
        """

        folium.CircleMarker(
            location=[lat, lng],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(mapa)

    # Mostrar mapa
    st_folium(mapa, width=800, height=600)

    # Estadísticas
    st.markdown("---")
    st.subheader("📊 Estadísticas de Fincas")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Fincas", len(fincas))

    with col2:
        superficie_total = sum(f.get('superficie_m2', 0) for f in fincas)
        st.metric("Superficie Total", f"{superficie_total:,.0f} m²")

    with col3:
        superficie_promedio = superficie_total / len(fincas) if fincas else 0
        st.metric("Superficie Promedio", f"{superficie_promedio:,.0f} m²")

    with col4:
        disponibles = sum(1 for f in fincas if f.get('estado') == 'disponible')
        st.metric("Disponibles", disponibles)

# ==========================================
# REGISTRO DE ARQUITECTOS
# ==========================================

def render_registro_arquitectos():
    st.header("👥 Registro de Arquitectos y Clientes")

    tab1, tab2 = st.tabs(["👨‍💼 Registrar Arquitecto", "🏠 Registrar Cliente"])

    with tab1:
        st.subheader("Registro de Arquitecto")

        with st.form("registro_arquitecto"):
            nombre = st.text_input("Nombre completo")
            email_arq = st.text_input("Email profesional")
            especialidad = st.selectbox("Especialidad", ["Arquitectura Residencial", "Arquitectura Comercial", "Urbanismo", "Restauración", "Interiorismo"])
            experiencia = st.slider("Años de experiencia", 0, 50, 5)
            ubicacion = st.text_input("Ubicación")
            descripcion = st.text_area("Descripción profesional")

            if st.form_submit_button("📝 Registrar Arquitecto", type="primary"):
                # Simular registro
                arquitecto_data = {
                    "id": f"arq_{len(st.session_state.get('arquitectos', [])) + 1}",
                    "nombre": nombre,
                    "email": email_arq,
                    "especialidad": especialidad,
                    "experiencia": experiencia,
                    "ubicacion": ubicacion,
                    "descripcion": descripcion,
                    "fecha_registro": datetime.now().isoformat()
                }

                if "arquitectos" not in st.session_state:
                    st.session_state.arquitectos = []
                st.session_state.arquitectos.append(arquitecto_data)

                st.success(f"✅ Arquitecto {nombre} registrado exitosamente!")
                st.balloons()

    with tab2:
        st.subheader("Registro de Cliente")

        with st.form("registro_cliente"):
            nombre_cliente = st.text_input("Nombre completo")
            email_cliente = st.text_input("Email")
            tipo_cliente = st.selectbox("Tipo de cliente", ["Particular", "Empresa", "Inversor"])
            presupuesto = st.number_input("Presupuesto aproximado (€)", min_value=0, step=10000)
            ubicacion_deseada = st.text_input("Ubicación deseada")
            necesidades = st.text_area("Necesidades específicas")

            if st.form_submit_button("📝 Registrar Cliente", type="primary"):
                # Simular registro
                cliente_data = {
                    "id": f"cli_{len(st.session_state.get('clientes', [])) + 1}",
                    "nombre": nombre_cliente,
                    "email": email_cliente,
                    "tipo": tipo_cliente,
                    "presupuesto": presupuesto,
                    "ubicacion_deseada": ubicacion_deseada,
                    "necesidades": necesidades,
                    "fecha_registro": datetime.now().isoformat()
                }

                if "clientes" not in st.session_state:
                    st.session_state.clientes = []
                st.session_state.clientes.append(cliente_data)

                st.success(f"✅ Cliente {nombre_cliente} registrado exitosamente!")
                st.balloons()

    # Mostrar registros existentes
    st.markdown("---")
    st.subheader("📋 Registros Recientes")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👨‍💼 Arquitectos Registrados:**")
        arquitectos = st.session_state.get('arquitectos', [])
        if arquitectos:
            for arq in arquitectos[-3:]:  # Últimos 3
                st.markdown(f"- {arq['nombre']} ({arq['especialidad']})")
        else:
            st.info("No hay arquitectos registrados aún")

    with col2:
        st.markdown("**🏠 Clientes Registrados:**")
        clientes = st.session_state.get('clientes', [])
        if clientes:
            for cli in clientes[-3:]:  # Últimos 3
                st.markdown(f"- {cli['nombre']} ({cli['tipo']})")
        else:
            st.info("No hay clientes registrados aún")

# ==========================================
# INTRANET ARQUITECTOS
# ==========================================

def render_intranet_arquitectos():
    st.header("🏢 Intranet Arquitectos ARCHIRAPID")

    # Verificar si el usuario es arquitecto
    if not email or "@" not in email:
        st.warning("Debes iniciar sesión con un email válido para acceder a la intranet.")
        return

    st.markdown("### 🏗️ Panel de Control Arquitecto")

    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        proyectos_total = len(st.session_state.get('proyectos', []))
        st.metric("Mis Proyectos", proyectos_total)

    with col2:
        clientes_total = len(st.session_state.get('clientes', []))
        st.metric("Mis Clientes", clientes_total)

    with col3:
        # Simular proyectos activos
        proyectos_activos = sum(1 for p in st.session_state.get('proyectos', []) if p.get('estado') != 'completado')
        st.metric("Proyectos Activos", proyectos_activos)

    with col4:
        # Simular ingresos mensuales
        ingresos = sum(p.get('precio_estimado', 0) for p in st.session_state.get('proyectos', []) if p.get('estado') == 'completado')
        st.metric("Ingresos Totales", f"€{ingresos:,.0f}")

    # Herramientas del arquitecto
    st.markdown("---")
    st.subheader("🛠️ Herramientas Profesionales")

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "👥 Mis Clientes", "📋 Proyectos"])

    with tab1:
        st.markdown("### 📊 Dashboard de Rendimiento")

        # Gráfico simple de proyectos por estado
        import matplotlib.pyplot as plt

        proyectos = st.session_state.get('proyectos', [])
        estados = {}
        for p in proyectos:
            estado = p.get('estado', 'borrador')
            estados[estado] = estados.get(estado, 0) + 1

        if estados:
            fig, ax = plt.subplots()
            ax.bar(estados.keys(), estados.values())
            ax.set_ylabel('Número de Proyectos')
            ax.set_title('Proyectos por Estado')
            st.pyplot(fig)
        else:
            st.info("No hay proyectos para mostrar estadísticas")

    with tab2:
        st.markdown("### 👥 Gestión de Clientes")

        clientes = st.session_state.get('clientes', [])
        if clientes:
            for cliente in clientes:
                with st.expander(f"🏠 {cliente['nombre']} - {cliente['tipo']}"):
                    st.write(f"**Email:** {cliente['email']}")
                    st.write(f"**Presupuesto:** €{cliente['presupuesto']:,.0f}")
                    st.write(f"**Ubicación deseada:** {cliente['ubicacion_deseada']}")
                    st.write(f"**Necesidades:** {cliente['necesidades']}")

                    if st.button(f"📞 Contactar", key=f"contact_{cliente['id']}"):
                        st.info(f"Simulando contacto con {cliente['nombre']}...")
        else:
            st.info("No tienes clientes registrados aún")

    with tab3:
        st.markdown("### 📋 Gestión de Proyectos")

        proyectos = st.session_state.get('proyectos', [])
        if proyectos:
            for proyecto in proyectos:
                with st.expander(f"🏗️ {proyecto.get('titulo', 'Proyecto sin título')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Estado", proyecto.get('estado', 'borrador').title())
                        st.metric("Versión", proyecto.get('version', 1))
                    with col2:
                        precio = proyecto.get('precio_estimado', 0)
                        st.metric("Precio Estimado", f"€{precio:,.0f}")

                    if st.button(f"✏️ Editar Proyecto", key=f"edit_proy_{proyecto['id']}"):
                        st.session_state.plan_actual = proyecto.get("plan_json", {})
                        st.session_state.pantalla_actual = "diseno_ia"
                        st.rerun()
        else:
            st.info("No tienes proyectos aún")

# ==========================================
# GEMELo DIGITAL
# ==========================================

def render_gemelo_digital():
    st.header("🧠 Gemelo Digital ARCHIRAPID")

    st.markdown("""
    ### 🚀 Tecnología de Vanguardia

    El **Gemelo Digital** de ARCHIRAPID es una representación virtual tridimensional
    de tu proyecto arquitectónico que te permite:

    - **Visualizar** la vivienda terminada antes de construir
    - **Interactuar** con el diseño en tiempo real
    - **Simular** iluminación, materiales y acabados
    - **Compartir** el proyecto con clientes de forma inmersiva
    """)

    # Estado del desarrollo
    st.info("🛠️ El Gemelo Digital está en desarrollo activo. Próximamente disponible.")

    # Preview conceptual
    st.subheader("🎯 Vista Previa Conceptual")

    # Simular una imagen 3D (placeholder)
    st.markdown("""
    ```
    [Vista 3D Interactiva - Próximamente]

         _____
       /     \\
      /  🏠   \\
     /_________\\
    |           |
    |   🪟 🪟    |
    |           |
    |   🚪      |
    |___________|
    ```
    """)

    # Características
    st.subheader("✨ Características del Gemelo Digital")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🎨 Personalización Visual:**
        - Cambiar colores de paredes
        - Probar diferentes materiales
        - Ajustar iluminación

        **📐 Medidas Precisas:**
        - Dimensiones exactas
        - Áreas calculadas
        - Volúmenes 3D
        """)

    with col2:
        st.markdown("""
        **🌅 Simulación Ambiental:**
        - Orientación solar
        - Sombras proyectadas
        - Eficiencia energética

        **📱 Acceso Multiplataforma:**
        - Web y móvil
        - VR compatible
        - Compartir con un link
        """)

    # Call to action
    st.markdown("---")
    if st.button("🚀 Solicitar Acceso Anticipado", type="primary"):
        st.success("✅ ¡Gracias! Te notificaremos cuando el Gemelo Digital esté disponible.")
        st.balloons()

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================

if __name__ == "__main__":
    main()
