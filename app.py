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

def render_header():
    """Header principal con estado del sistema"""
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.title("🏗️ ARCHIRAPID")
        st.markdown("*IA Avanzada + Precios en Vivo + Exportación Profesional*")

    with col2:
        if st.session_state.get("usar_api_real", False):
            st.success("🟢 API Real")
        else:
            st.warning("🟡 Modo Demo")

    with col3:
        if st.button("🔄 Actualizar", help="Actualizar datos del sistema"):
            st.rerun()

# ==========================================
# PANEL PRINCIPAL DEL CLIENTE
# ==========================================

def main():
    render_header()

    # Sidebar con navegación
    with st.sidebar:
        st.title("🎯 Mi Panel")

        # Autenticación suave
        email = st.text_input("📧 Tu email", key="user_email")
        if not email:
            st.info("✨ Introduce tu email para acceder a todas las funciones")
            return

        # Navegación principal
        opciones = [
            "🏠 Inicio",
            "🎨 Diseñar con IA",
            "💰 Precios en Vivo",
            "📦 Exportar Proyecto",
            "📊 Mis Proyectos"
        ]

        seleccion = st.radio("Navegación:", opciones)

        # Información del sistema
        with st.expander("ℹ️ Estado del Sistema"):
            mostrar_estado_conexion()

            if st.session_state.get("proyecto_actual"):
                st.markdown(f"**Proyecto:** {st.session_state.proyecto_actual.get('titulo', 'N/A')}")
                st.markdown(f"**Versión:** {st.session_state.proyecto_actual.get('version', 0)}")

    # Contenido principal
    if seleccion == "🏠 Inicio":
        render_inicio(email)
    elif seleccion == "🎨 Diseñar con IA":
        render_diseno_ia(email)
    elif seleccion == "💰 Precios en Vivo":
        render_precios_vivo()
    elif seleccion == "📦 Exportar Proyecto":
        render_exportacion()
    elif seleccion == "📊 Mis Proyectos":
        render_mis_proyectos(email)

# ==========================================
# PANTALLA DE INICIO
# ==========================================

def render_inicio(email: str):
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

    # Selector de finca
    fincas = obtener_fincas_con_fallback()

    if not fincas:
        st.warning("No hay fincas disponibles. El sistema está en modo demo.")
        return

    finca_seleccionada = st.selectbox(
        "🏡 Selecciona tu finca:",
        options=fincas,
        format_func=lambda x: f"{x.get('direccion', 'Sin dirección')} - {x.get('superficie_m2', 0)}m²",
        key="finca_selector"
    )

    if finca_seleccionada:
        st.session_state.finca_actual = finca_seleccionada

        # Mostrar información de la finca
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Datos de la Finca")
            st.metric("Superficie", f"{finca_seleccionada.get('superficie_m2', 0)} m²")
            st.metric("Máx. Construible", f"{int(finca_seleccionada.get('superficie_m2', 0) * 0.33)} m²")

            precio = finca_seleccionada.get('precio_venta', 0)
            if precio:
                st.metric("Valor Estimado", f"€{precio:,.0f}")

        with col2:
            st.subheader("🎯 Acciones Rápidas")

            if st.button("🎨 Comenzar Diseño con IA", type="primary", use_container_width=True):
                st.session_state.pantalla_actual = "diseno_ia"
                st.rerun()

            if st.button("📊 Ver Proyectos Existentes", use_container_width=True):
                proyectos = obtener_proyectos_con_fallback({"finca_id": finca_seleccionada["id"]})
                if proyectos:
                    st.session_state.proyectos_finca = proyectos
                    st.session_state.pantalla_actual = "proyectos_finca"
                    st.rerun()
                else:
                    st.info("No hay proyectos para esta finca aún.")

# ==========================================
# DISEÑO CON IA AVANZADA
# ==========================================

def render_diseno_ia(email: str):
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

# ==========================================
# PRECIOS EN VIVO (CONFIGURADOR DE COCHES)
# ==========================================

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

# ==========================================
# EXPORTACIÓN PROFESIONAL
# ==========================================

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

def render_mis_proyectos(email: str):
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
# EJECUCIÓN PRINCIPAL
# ==========================================

if __name__ == "__main__":
    main()
