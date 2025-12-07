# disenador_vivienda.py - Flujo para diseñadores de vivienda personalizada
import streamlit as st
import json
from .data_access import list_fincas, get_finca, save_proyecto
from .catastro_api import fetch_by_ref_catastral
from .gemelo_editor import editor_tabiques
from .gemelo_digital_vis import create_gemelo_3d as visualizacion_3d
from .validacion import validar_plan_local as validar_proyecto
from .documentacion import generar_memoria_constructiva as generar_memoria
from .pago_simulado import verificar_pago as procesar_pago

def main():
    st.title("🎨 Diseñador de Vivienda Personalizada")
    st.markdown("Crea diseños únicos adaptados a fincas específicas")

    # Paso 1: Seleccionar finca
    st.header("🏡 Paso 1: Seleccionar Finca")

    fincas = list_fincas()
    if not fincas:
        st.warning("No hay fincas disponibles. Ve a la sección de Propietario para subir una finca.")
        return

    finca_options = {f"{f['direccion']} (Ref: {f['ref_catastral']})": f for f in fincas}
    selected_finca_name = st.selectbox("Selecciona una finca:",
                                     list(finca_options.keys()),
                                     key="disenador_finca_select")

    if not selected_finca_name:
        st.info("👆 Selecciona una finca para comenzar el diseño")
        return

    finca = finca_options[selected_finca_name]

    # Mostrar información de la finca
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Información de la Finca")
        st.write(f"**Dirección:** {finca['direccion']}")
        st.write(f"**Referencia Catastral:** {finca['ref_catastral']}")
        st.write(f"**Superficie:** {finca.get('superficie', 'N/A')} m²")

    with col2:
        st.subheader("📊 Datos Catastrales")
        if st.button("🔄 Actualizar datos catastrales", key="disenador_catastro_update"):
            with st.spinner("Consultando Catastro..."):
                catastro_data = fetch_by_ref_catastral(finca['ref_catastral'])
                if catastro_data:
                    st.success("✅ Datos actualizados")
                    # Aquí se actualizarían los datos en la finca
                else:
                    st.error("❌ Error al consultar Catastro")

    # Paso 2: Parámetros de diseño
    st.header("⚙️ Paso 2: Parámetros de Diseño")

    col1, col2, col3 = st.columns(3)
    with col1:
        habitaciones = st.slider("Habitaciones", 1, 6, 3, key="disenador_habitaciones")
        banos = st.slider("Baños", 1, 4, 2, key="disenador_banos")

    with col2:
        plantas = st.slider("Plantas", 1, 3, 2, key="disenador_plantas")
        garaje = st.checkbox("Incluir garaje", key="disenador_garaje")

    with col3:
        estilo = st.selectbox("Estilo arquitectónico",
                            ["Moderno", "Tradicional", "Mediterráneo", "Industrial", "Minimalista"],
                            key="disenador_estilo")
        presupuesto = st.selectbox("Rango presupuestario",
                                 ["Económico", "Medio", "Premium", "Lujo"],
                                 key="disenador_presupuesto")

    # Paso 3: Editor interactivo
    st.header("🎯 Paso 3: Editor Interactivo")

    if st.button("🚀 Generar Diseño Base", key="disenador_generar"):
        with st.spinner("Generando diseño personalizado..."):
            # Aquí iría la lógica de IA para generar el diseño base
            # Por ahora simulamos
            st.success("✅ Diseño base generado")

            # Crear proyecto
            proyecto = {
                "id": f"diseno_{finca['id']}_{hash(str(st.session_state)) % 10000}",
                "finca_id": finca['id'],
                "tipo": "diseno_personalizado",
                "titulo": f"Diseño personalizado para {finca['direccion']}",
                "descripcion": f"Diseño {estilo.lower()} con {habitaciones} hab, {banos} baños, {plantas} plantas",
                "parametros": {
                    "habitaciones": habitaciones,
                    "banos": banos,
                    "plantas": plantas,
                    "garaje": garaje,
                    "estilo": estilo,
                    "presupuesto": presupuesto
                },
                "estado": "diseno",
                "creado_por": "disenador",  # En producción vendría del login
                "fecha_creacion": "2024-01-01"
            }

            save_proyecto(proyecto)
            st.session_state['proyecto_actual'] = proyecto

    # Si hay un proyecto activo, mostrar editor
    if 'proyecto_actual' in st.session_state:
        proyecto = st.session_state['proyecto_actual']

        # Crear un plan básico si no existe
        if 'plan_json' not in proyecto:
            proyecto['plan_json'] = {
                "habitaciones": [
                    {"nombre": "Dormitorio principal", "m2": 15},
                    {"nombre": "Dormitorio secundario", "m2": 12},
                    {"nombre": "Salón", "m2": 25},
                    {"nombre": "Cocina", "m2": 10}
                ],
                "total_m2": 62
            }

        # Editor interactivo
        plan_actualizado, validacion = editor_tabiques(proyecto['plan_json'], finca['superficie'])
        if plan_actualizado != proyecto['plan_json']:
            proyecto['plan_json'] = plan_actualizado
            st.session_state['proyecto_actual'] = proyecto
            st.success("✅ Cambios guardados")

        # Visualización 3D
        st.header("🏗️ Visualización 3D")
        visualizacion_3d(proyecto)

        # Validación
        st.header("✅ Validación")
        if st.button("🔍 Validar Proyecto", key="disenador_validar"):
            errores = validar_proyecto(proyecto)
            if errores:
                st.error("❌ Errores encontrados:")
                for error in errores:
                    st.write(f"- {error}")
            else:
                st.success("✅ Proyecto válido")

        # Documentación
        st.header("📄 Documentación")
        if st.button("📋 Generar Memoria", key="disenador_memoria"):
            memoria = generar_memoria(proyecto)
            st.download_button("⬇️ Descargar Memoria",
                             memoria,
                             "memoria.pdf",
                             key="disenador_download_memoria")

        # Pago
        st.header("💳 Pago y Finalización")
        if st.button("💰 Procesar Pago", key="disenador_pago"):
            exito = procesar_pago(proyecto, 1500)  # Precio simulado
            if exito:
                st.success("✅ Pago procesado exitosamente")
                st.balloons()
            else:
                st.error("❌ Error en el pago")

if __name__ == "__main__":
    main()