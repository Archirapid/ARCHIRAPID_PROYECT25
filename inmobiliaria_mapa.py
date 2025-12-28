#!/usr/bin/env python3
"""
Mapa Inmobiliario ARCHIRAPID
Gestión visual de fincas con integración backend
"""

import streamlit as st
import folium
from streamlit_folium import folium_static
import json
from datetime import datetime
import pandas as pd

# ==========================================
# IMPORTS DEL SISTEMA INTEGRADO
# ==========================================

from data_access import (
    obtener_fincas_con_fallback, crear_finca, actualizar_finca,
    eliminar_finca, mostrar_estado_conexion
)

# ==========================================
# CONFIGURACIÓN DE LA APP
# ==========================================

st.set_page_config(
    page_title="🏠 Mapa Inmobiliario ARCHIRAPID",
    layout="wide",
    page_icon="🏠"
)

# ==========================================
# FUNCIONES DEL MAPA
# ==========================================

def crear_mapa_interactivo(fincas: list) -> folium.Map:
    """
    Crea un mapa interactivo con las fincas
    """
    # Centro de España por defecto
    mapa = folium.Map(
        location=[40.4168, -3.7038],  # Madrid
        zoom_start=6,
        tiles='OpenStreetMap'
    )

    # Añadir fincas al mapa
    for finca in fincas:
        # Coordenadas (usar coordenadas reales si existen, sino aleatorias cercanas a Madrid)
        lat = finca.get('lat', 40.4168 + (hash(finca['id']) % 100 - 50) * 0.01)
        lng = finca.get('lng', -3.7038 + (hash(finca['id']) % 100 - 50) * 0.01)

        # Color según estado
        color = 'green' if finca.get('estado') == 'disponible' else 'orange'

        # Popup con información
        popup_html = f"""
        <div style="width: 200px;">
            <h4>{finca.get('titulo', 'Finca sin título')}</h4>
            <p><strong>Dirección:</strong> {finca.get('direccion', 'N/A')}</p>
            <p><strong>Superficie:</strong> {finca.get('superficie_m2', 0)} m²</p>
            <p><strong>Precio:</strong> €{finca.get('precio_venta', 0):,.0f}</p>
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

        # Añadir marcador con icono
        icon_type = 'home' if finca.get('tipo') == 'vivienda' else 'building'
        folium.Marker(
            location=[lat, lng],
            popup=popup_html,
            icon=folium.Icon(color=color, icon=icon_type, prefix='fa')
        ).add_to(mapa)

    return mapa

def mostrar_estadisticas_fincas(fincas: list):
    """
    Muestra estadísticas generales de las fincas
    """
    if not fincas:
        st.warning("No hay fincas para mostrar estadísticas")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_fincas = len(fincas)
        st.metric("Total Fincas", total_fincas)

    with col2:
        superficie_total = sum(f.get('superficie_m2', 0) for f in fincas)
        st.metric("Superficie Total", f"{superficie_total:,.0f} m²")

    with col3:
        precio_total = sum(f.get('precio_venta', 0) for f in fincas)
        precio_promedio = precio_total / len(fincas) if fincas else 0
        st.metric("Precio Promedio", f"€{precio_promedio:,.0f}")

    with col4:
        disponibles = len([f for f in fincas if f.get('estado') == 'disponible'])
        st.metric("Disponibles", disponibles)

def filtrar_fincas(fincas: list, filtros: dict) -> list:
    """
    Aplica filtros a la lista de fincas
    """
    fincas_filtradas = fincas.copy()

    # Filtro por precio mínimo
    if filtros.get('precio_min'):
        fincas_filtradas = [f for f in fincas_filtradas
                           if f.get('precio_venta', 0) >= filtros['precio_min']]

    # Filtro por precio máximo
    if filtros.get('precio_max'):
        fincas_filtradas = [f for f in fincas_filtradas
                           if f.get('precio_venta', 0) <= filtros['precio_max']]

    # Filtro por superficie mínima
    if filtros.get('superficie_min'):
        fincas_filtradas = [f for f in fincas_filtradas
                           if f.get('superficie_m2', 0) >= filtros['superficie_min']]

    # Filtro por estado
    if filtros.get('estado') and filtros['estado'] != 'todos':
        fincas_filtradas = [f for f in fincas_filtradas
                           if f.get('estado') == filtros['estado']]

    # Filtro por tipo
    if filtros.get('tipo') and filtros['tipo'] != 'todos':
        fincas_filtradas = [f for f in fincas_filtradas
                           if f.get('tipo') == filtros['tipo']]

    return fincas_filtradas

# ==========================================
# FORMULARIO DE NUEVA FINCA
# ==========================================

def mostrar_formulario_nueva_finca():
    """
    Muestra formulario para crear una nueva finca
    """
    st.subheader("➕ Nueva Finca")

    with st.form("nueva_finca_form"):
        col1, col2 = st.columns(2)

        with col1:
            titulo = st.text_input("Título de la finca", placeholder="Ej: Solar en zona residencial")
            direccion = st.text_input("Dirección completa", placeholder="Calle, número, ciudad")
            superficie = st.number_input("Superficie (m²)", min_value=50, max_value=10000, value=500)
            precio = st.number_input("Precio de venta (€)", min_value=10000, step=5000)

        with col2:
            tipo = st.selectbox("Tipo de finca",
                              ["solar", "vivienda", "local_comercial", "industrial"])
            estado = st.selectbox("Estado",
                                ["disponible", "reservado", "vendido"])
            lat = st.number_input("Latitud", value=40.4168, format="%.6f")
            lng = st.number_input("Longitud", value=-3.7038, format="%.6f")

        # Campos adicionales
        descripcion = st.text_area("Descripción detallada",
                                 placeholder="Describe la finca, sus características, entorno...")

        # Metadatos adicionales
        with st.expander("📊 Datos técnicos adicionales"):
            col1, col2 = st.columns(2)
            with col1:
                pendiente = st.number_input("Pendiente del terreno (%)", min_value=0, max_value=100)
                orientacion = st.selectbox("Orientación principal", ["norte", "sur", "este", "oeste"])
            with col2:
                acceso = st.selectbox("Tipo de acceso", ["carretera", "camino", "pista"])
                servicios = st.multiselect("Servicios disponibles",
                                         ["agua", "electricidad", "gas", "telefonia"])

        # Botón de envío
        submitted = st.form_submit_button("💾 Crear Finca", type="primary", use_container_width=True)

        if submitted:
            # Crear objeto finca
            nueva_finca = {
                "titulo": titulo,
                "direccion": direccion,
                "superficie_m2": superficie,
                "precio_venta": precio,
                "tipo": tipo,
                "estado": estado,
                "lat": lat,
                "lng": lng,
                "descripcion": descripcion,
                "datos_tecnicos": {
                    "pendiente": pendiente,
                    "orientacion": orientacion,
                    "acceso": acceso,
                    "servicios": servicios
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Intentar crear via API
            resultado = crear_finca(nueva_finca)

            if resultado:
                st.success("✅ Finca creada exitosamente")
                st.balloons()
                return True  # Indicar que se creó correctamente
            else:
                st.error("❌ Error al crear la finca")
                return False

    return False

# ==========================================
# LISTADO DE FINCAS
# ==========================================

def mostrar_listado_fincas(fincas: list):
    """
    Muestra listado detallado de fincas
    """
    st.subheader("📋 Listado de Fincas")

    if not fincas:
        st.info("No hay fincas que mostrar con los filtros actuales")
        return

    # Mostrar como tabla
    df_fincas = pd.DataFrame([{
        'Título': f.get('titulo', 'N/A'),
        'Dirección': f.get('direccion', 'N/A'),
        'Superficie': f"{f.get('superficie_m2', 0)} m²",
        'Precio': f"€{f.get('precio_venta', 0):,.0f}",
        'Tipo': f.get('tipo', 'N/A'),
        'Estado': f.get('estado', 'N/A')
    } for f in fincas])

    st.dataframe(df_fincas, use_container_width=True)

    # Acciones por finca
    st.markdown("### 🔧 Acciones")

    for finca in fincas:
        with st.expander(f"🏠 {finca.get('titulo', 'Finca')} - {finca.get('direccion', 'Sin dirección')}"):

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("👁️ Ver detalles", key=f"ver_{finca['id']}"):
                    st.session_state.finca_seleccionada = finca
                    st.session_state.mostrar_detalle_finca = True

            with col2:
                if st.button("🎨 Diseñar casa", key=f"disenar_{finca['id']}"):
                    # Redirigir al panel principal con esta finca seleccionada
                    st.session_state.finca_actual = finca
                    st.switch_page("app.py")

            with col3:
                if st.button("✏️ Editar", key=f"editar_{finca['id']}"):
                    st.session_state.finca_editar = finca
                    st.session_state.mostrar_editor_finca = True

            with col4:
                if st.button("🗑️ Eliminar", key=f"eliminar_{finca['id']}", type="secondary"):
                    if st.session_state.get(f"confirmar_eliminar_{finca['id']}", False):
                        if eliminar_finca(finca['id']):
                            st.success("Finca eliminada")
                            st.rerun()
                        else:
                            st.error("Error al eliminar finca")
                    else:
                        st.session_state[f"confirmar_eliminar_{finca['id']}"] = True
                        st.warning("¿Estás seguro? Haz clic de nuevo para confirmar")

# ==========================================
# DETALLE DE FINCA
# ==========================================

def mostrar_detalle_finca(finca: dict):
    """
    Muestra detalle completo de una finca
    """
    st.subheader(f"🏠 {finca.get('titulo', 'Finca')}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**📍 Dirección:** {finca.get('direccion', 'No especificada')}")
        st.markdown(f"**🏷️ Tipo:** {finca.get('tipo', 'No especificado').title()}")
        st.markdown(f"**📊 Estado:** {finca.get('estado', 'No especificado').title()}")

        if finca.get('descripcion'):
            st.markdown("**📝 Descripción:**")
            st.write(finca['descripcion'])

    with col2:
        st.metric("Superficie", f"{finca.get('superficie_m2', 0):,} m²")
        st.metric("Precio", f"€{finca.get('precio_venta', 0):,.0f}")

        precio_m2 = finca.get('precio_venta', 0) / max(finca.get('superficie_m2', 1), 1)
        st.metric("Precio/m²", f"€{precio_m2:,.0f}")

        # Calcular edificabilidad máxima
        edificabilidad_max = int(finca.get('superficie_m2', 0) * 0.33)
        st.metric("Edificable máx.", f"{edificabilidad_max:,} m²")

    # Datos técnicos
    if finca.get('datos_tecnicos'):
        st.markdown("### 📊 Datos Técnicos")
        datos_tec = finca['datos_tecnicos']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Pendiente", f"{datos_tec.get('pendiente', 0)}%")

        with col2:
            st.metric("Orientación", datos_tec.get('orientacion', 'N/A').title())

        with col3:
            st.metric("Acceso", datos_tec.get('acceso', 'N/A').title())

        with col4:
            servicios = datos_tec.get('servicios', [])
            st.metric("Servicios", len(servicios))

        if servicios:
            st.markdown("**Servicios disponibles:**")
            st.write(", ".join(servicios).title())

    # Mapa individual de la finca
    if finca.get('lat') and finca.get('lng'):
        st.markdown("### 🗺️ Ubicación")
        mapa_finca = folium.Map(
            location=[finca['lat'], finca['lng']],
            zoom_start=15
        )

        folium.Marker(
            location=[finca['lat'], finca['lng']],
            popup=f"<strong>{finca.get('titulo', 'Finca')}</strong><br>{finca.get('direccion', 'N/A')}",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(mapa_finca)

        folium_static(mapa_finca, width=700, height=400)

    # Acciones
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎨 Comenzar Diseño", type="primary", use_container_width=True):
            st.session_state.finca_actual = finca
            st.switch_page("app.py")

    with col2:
        if st.button("✏️ Editar Finca", use_container_width=True):
            st.session_state.finca_editar = finca
            st.session_state.mostrar_editor_finca = True

    with col3:
        if st.button("⬅️ Volver al listado", use_container_width=True):
            st.session_state.mostrar_detalle_finca = False
            st.rerun()

# ==========================================
# EDITOR DE FINCA
# ==========================================

def mostrar_editor_finca(finca: dict):
    """
    Muestra editor para modificar una finca
    """
    st.subheader(f"✏️ Editando: {finca.get('titulo', 'Finca')}")

    with st.form("editar_finca_form"):
        col1, col2 = st.columns(2)

        with col1:
            titulo = st.text_input("Título", value=finca.get('titulo', ''))
            direccion = st.text_input("Dirección", value=finca.get('direccion', ''))
            superficie = st.number_input("Superficie (m²)",
                                       value=finca.get('superficie_m2', 0),
                                       min_value=50, max_value=10000)
            precio = st.number_input("Precio (€)",
                                   value=finca.get('precio_venta', 0),
                                   min_value=10000, step=5000)

        with col2:
            tipo = st.selectbox("Tipo",
                              ["solar", "vivienda", "local_comercial", "industrial"],
                              index=["solar", "vivienda", "local_comercial", "industrial"].index(finca.get('tipo', 'solar')))
            estado = st.selectbox("Estado",
                                ["disponible", "reservado", "vendido"],
                                index=["disponible", "reservado", "vendido"].index(finca.get('estado', 'disponible')))
            lat = st.number_input("Latitud", value=finca.get('lat', 40.4168), format="%.6f")
            lng = st.number_input("Longitud", value=finca.get('lng', -3.7038), format="%.6f")

        descripcion = st.text_area("Descripción", value=finca.get('descripcion', ''))

        # Datos técnicos
        if finca.get('datos_tecnicos'):
            with st.expander("📊 Datos Técnicos"):
                datos_tec = finca['datos_tecnicos']
                col1, col2 = st.columns(2)
                with col1:
                    pendiente = st.number_input("Pendiente (%)", value=datos_tec.get('pendiente', 0))
                    orientacion = st.selectbox("Orientación",
                                             ["norte", "sur", "este", "oeste"],
                                             index=["norte", "sur", "este", "oeste"].index(datos_tec.get('orientacion', 'norte')))
                with col2:
                    acceso = st.selectbox("Acceso",
                                        ["carretera", "camino", "pista"],
                                        index=["carretera", "camino", "pista"].index(datos_tec.get('acceso', 'carretera')))
                    servicios = st.multiselect("Servicios",
                                             ["agua", "electricidad", "gas", "telefonia"],
                                             default=datos_tec.get('servicios', []))

        submitted = st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True)

        if submitted:
            finca_actualizada = finca.copy()
            finca_actualizada.update({
                "titulo": titulo,
                "direccion": direccion,
                "superficie_m2": superficie,
                "precio_venta": precio,
                "tipo": tipo,
                "estado": estado,
                "lat": lat,
                "lng": lng,
                "descripcion": descripcion,
                "datos_tecnicos": {
                    "pendiente": pendiente,
                    "orientacion": orientacion,
                    "acceso": acceso,
                    "servicios": servicios
                },
                "updated_at": datetime.now().isoformat()
            })

            if actualizar_finca(finca['id'], finca_actualizada):
                st.success("✅ Finca actualizada exitosamente")
                st.session_state.mostrar_editor_finca = False
                st.rerun()
            else:
                st.error("❌ Error al actualizar la finca")

# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================

def main():
    st.title("🏠 Mapa Inmobiliario ARCHIRAPID")
    st.markdown("*Gestión visual y completa de fincas inmobiliarias*")

    # Mostrar estado de conexión
    mostrar_estado_conexion()

    # Obtener fincas
    fincas = obtener_fincas_con_fallback()

    # Sidebar con filtros
    with st.sidebar:
        st.header("🔍 Filtros")

        # Filtros de búsqueda
        filtros = {}

        precio_min = st.number_input("Precio mínimo (€)", min_value=0, value=0, step=10000)
        if precio_min > 0:
            filtros['precio_min'] = precio_min

        precio_max = st.number_input("Precio máximo (€)", min_value=0, value=0, step=10000)
        if precio_max > 0:
            filtros['precio_max'] = precio_max

        superficie_min = st.number_input("Superficie mínima (m²)", min_value=0, value=0, step=50)
        if superficie_min > 0:
            filtros['superficie_min'] = superficie_min

        estado_filtro = st.selectbox("Estado", ["todos", "disponible", "reservado", "vendido"])
        if estado_filtro != "todos":
            filtros['estado'] = estado_filtro

        tipo_filtro = st.selectbox("Tipo", ["todos", "solar", "vivienda", "local_comercial", "industrial"])
        if tipo_filtro != "todos":
            filtros['tipo'] = tipo_filtro

        # Aplicar filtros
        fincas_filtradas = filtrar_fincas(fincas, filtros)

        st.markdown(f"**Mostrando {len(fincas_filtradas)} de {len(fincas)} fincas**")

    # Contenido principal
    tab1, tab2, tab3 = st.tabs(["🗺️ Mapa", "📋 Listado", "➕ Nueva Finca"])

    with tab1:
        st.subheader("🗺️ Mapa Interactivo")

        if fincas_filtradas:
            mapa = crear_mapa_interactivo(fincas_filtradas)
            folium_static(mapa, width=800, height=600)

            # Estadísticas
            mostrar_estadisticas_fincas(fincas_filtradas)
        else:
            st.info("No hay fincas para mostrar en el mapa")

    with tab2:
        mostrar_listado_fincas(fincas_filtradas)

    with tab3:
        if mostrar_formulario_nueva_finca():
            st.rerun()  # Recargar si se creó una finca

    # Mostrar detalle de finca si está seleccionada
    if st.session_state.get("mostrar_detalle_finca") and st.session_state.get("finca_seleccionada"):
        st.markdown("---")
        mostrar_detalle_finca(st.session_state.finca_seleccionada)

    # Mostrar editor de finca si está activado
    if st.session_state.get("mostrar_editor_finca") and st.session_state.get("finca_editar"):
        st.markdown("---")
        mostrar_editor_finca(st.session_state.finca_editar)

if __name__ == "__main__":
    main()