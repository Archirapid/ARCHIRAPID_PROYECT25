import streamlit as st
from typing import Tuple

# Intentar obtener fincas desde la DB; si falla, usar lista vacía
try:
    from src import db
    _plots_df = db.get_all_plots()
    # Puede devolver un pandas.DataFrame o una lista
    if hasattr(_plots_df, 'to_dict'):
        plots = _plots_df.to_dict(orient='records')
    else:
        try:
            plots = list(_plots_df)
        except Exception:
            plots = []
except Exception:
    plots = []

st.set_page_config(page_title='Diseñador IA - AI Configurator', layout='wide')
st.title('Diseña tu Casa con IA (AI Configurator)')

st.markdown('### Seleccione la finca (límite de superficie y edificabilidad)')
plot_options = [f"{p.get('title','Sin título')} ({p.get('surface_m2') or p.get('m2','N/A')} m²)" for p in plots]
sel_index = 0
if plot_options:
    sel_index = st.selectbox('Finca', options=list(range(len(plot_options))), format_func=lambda i: plot_options[i])
    selected_plot = plots[sel_index]
    finca_m2 = float(selected_plot.get('surface_m2') or selected_plot.get('m2') or 0)
else:
    st.info('No hay fincas disponibles en la base de datos. Trabaja con una finca de ejemplo.')
    finca_m2 = st.number_input('Superficie de finca de ejemplo (m²)', value=300.0)
    selected_plot = None

st.markdown('---')

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader('Malla de Diseño 2D (simulada)')
    mesh_text = st.text_area('Malla de Diseño 2D', value='[Área de trabajo simulada]\n- Añade notas de diseño aquí...\n', height=300)

    st.markdown('### Parámetros de Configuración')
    num_habitaciones = st.number_input('Nº de Habitaciones', min_value=1, max_value=20, value=3)
    estilo = st.selectbox('Estilo de Casa', options=['Moderno', 'Clásico', 'Mediterráneo', 'Industrial', 'Minimalista'])
    piscina = st.checkbox('¿Quiere Piscina?')

    st.markdown('\n')
    if st.button('Generar / Evaluar Diseño'):
        # Forzar cálculo inmediato en el mismo flujo
        pass

with col_right:
    st.subheader('Resultados en Vivo')

    # Helper local para cálculo y validación
    def calcular_coste_y_validar(finca_m2: float, num_habitaciones: int, estilo: str, piscina: bool) -> Tuple[float, str, float, float]:
        """Calcula coste estimado y valida la regla del 33%.\n\n        Retorna (coste_estimado, mensaje_validacion, m2_construidos_estimado, max_built_area)
        """
        # Heurística simple: m2 por habitación + zona común + piscina
        m2_por_habitacion = 20
        zona_comun = 30  # salón, cocina, etc.
        piscina_area = 30 if piscina else 0
        m2_construidos_estimado = num_habitaciones * m2_por_habitacion + zona_comun + piscina_area

        coste_estimado = 1500.0 * m2_construidos_estimado

        max_built_area = finca_m2 * 0.33
        if m2_construidos_estimado > max_built_area:
            mensaje = f"⚠️ ¡Advertencia Urbanística! Supera el 33% de edificabilidad permitida ({int(max_built_area)} m²). Diseño: {int(m2_construidos_estimado)} m²."
        else:
            mensaje = '✅ Diseño cumple normativa MVP.'

        return coste_estimado, mensaje, m2_construidos_estimado, max_built_area

    coste, mensaje, m2_est, max_built = calcular_coste_y_validar(finca_m2, num_habitaciones, estilo, piscina)

    st.markdown('**Coste de Ejecución Estimado:**')
    st.success(f"€ {coste:,.0f} (estimado para ~{int(m2_est)} m²)")

    st.markdown('**Estatus IA / Validación:**')
    if '⚠️' in mensaje:
        st.warning(mensaje)
    else:
        st.info(mensaje)

    st.markdown('---')
    st.caption(f"Superficie finca: {int(finca_m2)} m² — Máx. construible (33%): {int(max_built)} m²")

st.markdown('\n---\n')
st.write('Puedes usar este prototipo para iterar parámetros y validar restricciones urbanísticas básicas.')

# Opcional: finalizar diseño y generar paquete de entrega
try:
    from export_ops import generar_paquete_descarga
    from src import db
    can_export = True
except Exception:
    can_export = False

if can_export:
    st.markdown('---')
    st.subheader('Finalizar diseño y obtener paquete')
    buyer_email = st.text_input('Email para recibir el paquete (ej: cliente@ejemplo.com)', key='ai_buy_email')
    if st.button('Finalizar y Descargar Paquete'):
        if not buyer_email or '@' not in buyer_email:
            st.error('Introduce un email válido')
        else:
            # Registrar venta simulada (proyecto_id puede ser NULL)
            precio_base = coste
            try:
                comision = db.registrar_venta_proyecto(None, buyer_email, 'Paquete IA', precio_base)
            except Exception:
                comision = 0.0

            try:
                title = f"Diseño_IA_{int(st.time())}"
            except Exception:
                title = 'Diseño_IA'
            paquete = generar_paquete_descarga(title)
            st.download_button('Descargar paquete ZIP del diseño', data=paquete, file_name=f"{title}.zip", mime='application/zip')
            st.success(f'Paquete generado. Comisión Archirapid: €{comision:.2f}')
