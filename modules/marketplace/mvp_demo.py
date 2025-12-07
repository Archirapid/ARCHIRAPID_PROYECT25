# modules/marketplace/mvp_demo.py
"""
Demo completa del flujo MVP de ARCHIRAPID
Muestra el flujo end-to-end: inputs → IA → editor → 3D → documentación → pago → exportación
"""

import streamlit as st
import json
from modules.marketplace.ai_engine import get_ai_response
from modules.marketplace.gemelo_editor import editor_tabiques, evaluar_con_ia, aplicar_propuesta_ia
from modules.marketplace.gemelo_digital_vis import create_gemelo_3d
from modules.marketplace.documentacion import generar_memoria_constructiva, generar_presupuesto_estimado, generar_plano_cad
from modules.marketplace.pago_simulado import init_pago_state, render_paso_pago, verificar_pago


def plan_vivienda(superficie_finca, habitaciones, garage):
    """
    Función simplificada para demo - en producción usa la real
    """
    # Simular respuesta IA
    prompt = f"Genera un plan de vivienda JSON con {habitaciones} habitaciones, garage={garage}, superficie finca={superficie_finca}m²"
    response = get_ai_response(prompt)

    try:
        return json.loads(response)
    except:
        # Fallback si IA no devuelve JSON válido
        return {
            "habitaciones": [
                {"nombre": f"Dormitorio {i+1}", "m2": 12 + i*3} for i in range(habitaciones)
            ] + [{"nombre": "Salón-Comedor", "m2": 25}, {"nombre": "Cocina", "m2": 10}, {"nombre": "Baño", "m2": 6}],
            "garage": {"m2": 20} if garage else None,
            "total_m2": sum([12 + i*3 for i in range(habitaciones)]) + 25 + 10 + 6 + (20 if garage else 0)
        }


def main():
    st.title("🏠 ARCHIRAPID - MVP Completo Demo")
    st.markdown("**Flujo end-to-end: Diseño → Validación → Documentación → Pago → Exportación**")

    # Inicializar estado de pago
    init_pago_state()

    # --- PASO 1: Inputs del cliente ---
    st.header("📝 Paso 1: Parámetros del Proyecto")

    col1, col2, col3 = st.columns(3)
    with col1:
        superficie_finca = st.number_input("Superficie finca (m²)", 100, 20000, 500, step=100)
    with col2:
        habitaciones = st.slider("Habitaciones", 1, 10, 3)
    with col3:
        garage = st.checkbox("Garage")

    # --- PASO 2: Generar plan con IA ---
    st.header("🤖 Paso 2: Generación IA del Plan")

    if st.button("🚀 Generar Plan con IA", type="primary"):
        with st.spinner("Generando distribución óptima..."):
            plan_json = plan_vivienda(superficie_finca, habitaciones, garage)

        st.session_state.plan_json = plan_json
        st.success("✅ Plan generado exitosamente!")

        with st.expander("📊 Ver Plan JSON generado", expanded=True):
            st.json(plan_json)

    # Continuar solo si hay plan generado
    if "plan_json" not in st.session_state:
        st.info("👆 Genera un plan primero para continuar con el flujo.")
        return

    plan_json = st.session_state.plan_json

    # --- PASO 3: Editor de tabiques ---
    st.header("✏️ Paso 3: Editor Interactivo")

    plan_json, resultado_validacion = editor_tabiques(plan_json, superficie_finca)

    if resultado_validacion.get("valido"):
        st.success("✅ Plan válido según normativa local")
    else:
        st.error("❌ Plan requiere ajustes")
        st.write("Problemas:", resultado_validacion.get("problemas", []))

    # --- PASO 4: Validación IA y propuestas ---
    st.header("🧠 Paso 4: Validación IA y Optimización")

    if st.button("🔍 Analizar con IA y proponer mejoras"):
        with st.spinner("Analizando con IA..."):
            informe_ia = evaluar_con_ia(plan_json, superficie_finca)

        st.session_state.informe_ia = informe_ia

        with st.expander("📄 Informe de IA", expanded=True):
            st.markdown(informe_ia)

        if st.button("✅ Aplicar propuestas de IA"):
            plan_json = aplicar_propuesta_ia(informe_ia, plan_json)
            st.session_state.plan_json = plan_json
            st.success("🎯 Plan optimizado aplicado!")
            st.rerun()

    # --- PASO 5: Visualización 3D ---
    st.header("🏗️ Paso 5: Gemelo Digital 3D")

    try:
        fig = create_gemelo_3d(plan_json)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Vista 3D del proyecto con habitaciones y garage (si aplica)")
    except Exception as e:
        st.error(f"Error en visualización 3D: {e}")

    # --- PASO 6: Documentación ---
    st.header("📋 Paso 6: Documentación Técnica")

    col_doc1, col_doc2 = st.columns(2)

    with col_doc1:
        st.subheader("📄 Memoria Constructiva")
        memoria = generar_memoria_constructiva(plan_json, superficie_finca)
        st.code(memoria, language="text")

    with col_doc2:
        st.subheader("💰 Presupuesto Estimado")
        presupuesto = generar_presupuesto_estimado(plan_json)

        # Mostrar métricas clave
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Superficie Total", f"{presupuesto['superficie_total']:.1f} m²")
            st.metric("Coste/m²", f"€{presupuesto['coste_m2']:.0f}")
        with col_m2:
            st.metric("Subtotal Obra", f"€{presupuesto['subtotal_obra']:,.0f}")
            st.metric("Total Estimado", f"€{presupuesto['total_estimado']:,.0f}")

        with st.expander("Ver detalle completo"):
            st.json(presupuesto)

    # --- PASO 7: Pago Simulado ---
    st.header("💳 Paso 7: Pago y Exportación")

    render_paso_pago()

    # --- PASO 8: Exportación (habilitada tras pago) ---
    if verificar_pago():
        st.success("✅ Pago verificado - Exportación habilitada!")

        col_exp1, col_exp2, col_exp3 = st.columns(3)

        with col_exp1:
            st.subheader("📄 PDF")
            st.download_button(
                label="Descargar Memoria PDF",
                data=memoria.encode("utf-8"),
                file_name="memoria_constructiva.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col_exp2:
            st.subheader("🖼️ CAD (DXF)")
            if st.button("Generar Plano DXF", use_container_width=True):
                with st.spinner("Generando plano CAD con IA..."):
                    dxf_content = generar_plano_cad(plan_json)
                    st.session_state.dxf_content = dxf_content

                if "dxf_content" in st.session_state:
                    st.download_button(
                        label="💾 Descargar DXF",
                        data=st.session_state.dxf_content.encode("utf-8"),
                        file_name="planta_mvp.dxf",
                        mime="application/octet-stream",
                        use_container_width=True
                    )
                    st.success("✅ Plano DXF generado!")

        with col_exp3:
            st.subheader("📊 JSON")
            plan_json_str = json.dumps(plan_json, ensure_ascii=False, indent=2)
            st.download_button(
                label="Descargar JSON",
                data=plan_json_str.encode("utf-8"),
                file_name="plan_completo.json",
                mime="application/json",
                use_container_width=True
            )

        st.info("🎉 **MVP Completo!** El cliente puede descargar toda la documentación técnica.")

    else:
        st.warning("💳 Completa el pago simulado para habilitar las descargas.")

    # --- Información del sistema ---
    st.markdown("---")
    st.caption("**ARCHIRAPID MVP Demo** - Flujo completo end-to-end")
    st.caption("Tecnologías: Streamlit + IA (OpenRouter) + Plotly 3D + DXF generation")


if __name__ == "__main__":
    main()