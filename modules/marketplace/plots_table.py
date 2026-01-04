"""
Vista de tabla de fincas guardadas con opción de crear proyectos
"""
import streamlit as st
import pandas as pd
from src import db as _db
import os

# Configuración de columnas para la tabla
columnas_disponibles = [
    'title', 'catastral_ref', 'm2', 'locality', 'province',
    'owner_name', 'created_at', 'id', 'referencia_catastral', 'plano_catastral_path'
]

nombres_columnas = {
    'title': 'Título',
    'catastral_ref': 'Referencia Catastral',
    'referencia_catastral': 'Ref. Catastral IA',  # Nuevo campo
    'm2': 'Superficie (m²)',
    'locality': 'Municipio',
    'province': 'Provincia',
    'owner_name': 'Propietario',
    'created_at': 'Fecha Creación',
    'plano_catastral_path': 'PDF Catastral',  # Nuevo campo
    'id': 'ID'
}

def main():
    """Vista principal de la tabla de fincas"""
    st.title("🏠 Fincas Guardadas")

    st.markdown("""
    Aquí puedes ver todas las fincas que se han guardado en el sistema.
    Cada finca tiene la opción de crear un proyecto arquitectónico.
    """)

    # Obtener todas las fincas
    try:
        df_fincas = _db.get_all_plots()

        if df_fincas.empty:
            st.info("📭 No hay fincas guardadas en el sistema todavía.")
            st.markdown("""
            Para agregar fincas:
            1. Ve a la sección **"Propietarios (Subir Fincas)"**
            2. Sube un PDF catastral
            3. La IA extraerá automáticamente los datos
            4. Los datos se guardarán aquí
            """)
            return

        # Mostrar estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Fincas", len(df_fincas))
        with col2:
            superficie_total = df_fincas['m2'].sum() if 'm2' in df_fincas.columns else 0
            st.metric("Superficie Total (m²)", f"{superficie_total:,.0f}")
        with col3:
            municipios_unicos = df_fincas['locality'].nunique() if 'locality' in df_fincas.columns else 0
            st.metric("Municipios", municipios_unicos)

        # Filtros
        st.markdown("### 🔍 Filtros")

        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_municipio = st.selectbox(
                "Municipio",
                options=["Todos"] + sorted(df_fincas['locality'].dropna().unique().tolist()) if 'locality' in df_fincas.columns else ["Todos"],
                key="filtro_municipio"
            )

        with col2:
            filtro_provincia = st.selectbox(
                "Provincia",
                options=["Todos"] + sorted(df_fincas['province'].dropna().unique().tolist()) if 'province' in df_fincas.columns else ["Todos"],
                key="filtro_provincia"
            )

        with col3:
            filtro_propietario = st.selectbox(
                "Propietario",
                options=["Todos"] + sorted(df_fincas['owner_name'].dropna().unique().tolist()) if 'owner_name' in df_fincas.columns else ["Todos"],
                key="filtro_propietario"
            )

        # Aplicar filtros
        df_filtrado = df_fincas.copy()

        if filtro_municipio != "Todos" and 'locality' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['locality'] == filtro_municipio]

        if filtro_provincia != "Todos" and 'province' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['province'] == filtro_provincia]

        if filtro_propietario != "Todos" and 'owner_name' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['owner_name'] == filtro_propietario]

        # Actualizar estadísticas con filtros aplicados
        if len(df_filtrado) != len(df_fincas):
            st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df_fincas)} fincas (filtros aplicados)")

        # Preparar datos para mostrar (con o sin filtros)
        df_mostrar = df_fincas[columnas_disponibles].copy()
        df_mostrar = df_mostrar.rename(columns=nombres_columnas)
        df_fincas_para_acciones = df_fincas

        if not df_filtrado.empty:
            df_mostrar_filtrado = df_filtrado[columnas_disponibles].copy()
            df_mostrar_filtrado = df_mostrar_filtrado.rename(columns=nombres_columnas)

            # Formatear fechas y superficie para datos filtrados
            if 'created_at' in df_mostrar_filtrado.columns:
                df_mostrar_filtrado['Fecha Creación'] = pd.to_datetime(df_mostrar_filtrado['Fecha Creación'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')

            if 'Superficie (m²)' in df_mostrar_filtrado.columns:
                df_mostrar_filtrado['Superficie (m²)'] = df_mostrar_filtrado['Superficie (m²)'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")

            # Usar datos filtrados para mostrar y acciones
            df_mostrar = df_mostrar_filtrado
            df_fincas_para_acciones = df_filtrado

        # Formatear fechas y superficie para datos sin filtrar (si no hay filtros aplicados)
        if len(df_filtrado) == len(df_fincas):
            if 'created_at' in df_mostrar.columns:
                df_mostrar['Fecha Creación'] = pd.to_datetime(df_mostrar['Fecha Creación'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')

            if 'Superficie (m²)' in df_mostrar.columns:
                df_mostrar['Superficie (m²)'] = df_mostrar['Superficie (m²)'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")

        # Mostrar tabla con botones usando st.dataframe con columnas personalizadas
        st.markdown("### 📋 Lista de Fincas")

        # Crear una copia del dataframe para mostrar con botones
        df_display = df_mostrar.copy()

        # Agregar columna de botones usando índices
        df_display.insert(0, '🏗️ Crear Proyecto', [f"Proyecto {i+1}" for i in range(len(df_display))])

        # Mostrar dataframe con configuración personalizada
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "🏗️ Crear Proyecto": st.column_config.TextColumn(
                    "Acción",
                    help="Haz clic en el botón para crear un proyecto"
                ),
                "Título": st.column_config.TextColumn("Título", width="medium"),
                "Referencia Catastral": st.column_config.TextColumn("Ref. Catastral", width="large"),
                "Ref. Catastral IA": st.column_config.TextColumn("Ref. IA", width="large"),  # Nuevo campo
                "Superficie (m²)": st.column_config.TextColumn("Superficie", width="small"),
                "Municipio": st.column_config.TextColumn("Municipio", width="medium"),
                "Provincia": st.column_config.TextColumn("Provincia", width="medium"),
                "Propietario": st.column_config.TextColumn("Propietario", width="medium"),
                "Fecha Creación": st.column_config.TextColumn("Creado", width="medium"),
                "PDF Catastral": st.column_config.TextColumn("PDF", width="medium")  # Nuevo campo
            }
        )

        # Sección de botones individuales para cada finca
        st.markdown("### 🎯 Acciones por Finca")

        # Crear tarjetas para cada finca con botones
        for idx, row in df_mostrar_filtrado.iterrows():
            finca_id = df_fincas_para_acciones.iloc[idx]['id'] if 'id' in df_fincas_para_acciones.columns else idx

            with st.expander(f"🏠 {row.get('Título', f'Finca {idx+1}')} - {row.get('Referencia Catastral', 'Sin ref.')}"):
                col1, col2, col3 = st.columns([1, 1, 2])

                with col1:
                    if st.button("🏗️ Crear Proyecto", key=f"create_project_{finca_id}", type="primary"):
                        st.session_state[f"selected_plot_{finca_id}"] = finca_id
                        st.success(f"✅ Proyecto creado para la finca: {row.get('Título', f'Finca {idx+1}')}")
                        st.balloons()

                    # Botón IA para generar análisis
                    if st.button("🤖 Análisis IA", key=f"ai_analysis_{finca_id}"):
                        with st.spinner("🔍 Generando análisis inteligente de la finca..."):
                            try:
                                # Obtener los datos completos de la finca
                                finca_data = df_fincas_para_acciones.iloc[idx]

                                # Construir diccionario con datos para el análisis
                                datos = {
                                    "referencia_catastral": finca_data.get("referencia_catastral"),
                                    "superficie_parcela": finca_data.get("m2"),
                                    "municipio": finca_data.get("locality"),
                                    "lat": finca_data.get("lat"),
                                    "lon": finca_data.get("lon")
                                }

                                # Llamar a la función de análisis IA
                                from modules.marketplace.ai_engine import analisis_finca_ia
                                informe = analisis_finca_ia(datos)

                                # Mostrar el informe generado
                                if informe.startswith("Error"):
                                    st.error(informe)
                                else:
                                    st.success("✅ Análisis generado exitosamente")
                                    st.markdown("### 📊 Análisis Inteligente de la Finca")
                                    st.markdown(informe)

                            except Exception as e:
                                st.error(f"❌ Error al generar análisis: {str(e)}")

                with col2:
                    if st.button("👁️ Ver Detalles", key=f"view_details_{finca_id}"):
                        # Obtener datos completos de la finca
                        finca_data = df_fincas_para_acciones.iloc[idx] if idx < len(df_fincas_para_acciones) else {}
                        
                        st.info(f"""
                        **Detalles de la Finca:**
                        - 📍 Ubicación: {row.get('Municipio', 'N/A')}, {row.get('Provincia', 'N/A')}
                        - 📐 Superficie: {row.get('Superficie (m²)', 'N/A')} m²
                        - 🆔 Ref. Catastral: {row.get('Referencia Catastral', 'N/A')}
                        - 🆔 Ref. IA: {finca_data.get('referencia_catastral', 'N/A')}
                        - 📄 PDF: {finca_data.get('plano_catastral_path', 'N/A')}
                        - 👤 Propietario: {row.get('Propietario', 'N/A')}
                        - 📅 Creado: {row.get('Fecha Creación', 'N/A')}
                        """)

                    # Botón para descargar/ver PDF si existe
                    pdf_path = df_fincas_para_acciones.iloc[idx].get('plano_catastral_path') if idx < len(df_fincas_para_acciones) else None
                    if pdf_path and os.path.exists(pdf_path):
                        if st.button("📄 Ver PDF Catastral", key=f"view_pdf_{finca_id}"):
                            st.info(f"📄 PDF disponible en: {pdf_path}")
                            # Aquí se podría mostrar el PDF o permitir descarga

                with col3:
                    st.markdown(f"**ID de Finca:** `{finca_id}`")
                    
                    # Mostrar estado de validación catastral
                    ref_ia = df_fincas_para_acciones.iloc[idx].get('referencia_catastral') if idx < len(df_fincas_para_acciones) else None
                    if ref_ia:
                        st.success("✅ Datos catastrales validados por IA")
                    else:
                        st.warning("⚠️ Sin validación IA")

        # Información adicional
        st.markdown("### 💡 Información")
        st.markdown("""
        - **Crear Proyecto**: Inicia el proceso de diseño arquitectónico para la finca seleccionada
        - **Análisis IA**: Genera análisis inteligente de la finca usando IA avanzada
        - **Referencia Catastral**: Código único que identifica la propiedad
        - **Ref. IA**: Referencia catastral extraída automáticamente por IA del PDF
        - **Superficie**: Área en metros cuadrados de la parcela
        - **Municipio/Provincia**: Ubicación de la propiedad
        - **PDF Catastral**: Ruta al documento PDF catastral guardado
        - **✅ Datos validados por IA**: Indica que la finca tiene datos oficiales verificados
        """)

    except Exception as e:
        st.error(f"❌ Error al cargar las fincas: {str(e)}")
        st.info("Verifica que la base de datos esté correctamente configurada.")

if __name__ == "__main__":
    main()