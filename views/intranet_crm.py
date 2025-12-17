import streamlit as st
import pandas as pd
from src import db

st.set_page_config(page_title='Intranet CRM')

# Requiere acceso desde la Intranet (header.py pone st.session_state['page']='Intranet' tras login admin)
if st.session_state.get('page') != 'Intranet':
    st.error('Acceso denegado. Debe acceder como administrador desde el botón ACCESO.')
    st.stop()

st.title('Intranet - CRM y Finanzas')

# Ingresos por comisiones de ventas de proyectos
try:
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute('SELECT IFNULL(SUM(comision_archirapid),0) FROM ventas_proyectos')
    total_comisiones = cur.fetchone()[0] or 0.0

    # Ingresos recurrentes: sumar precio_mensual de planes de arquitectos activos (simulado)
    cur.execute('SELECT IFNULL(SUM(p.precio_mensual),0) FROM arquitectos a LEFT JOIN planes p ON a.plan_id = p.id')
    total_suscripciones = cur.fetchone()[0] or 0.0

    # Obtener todas las filas de ventas_proyectos
    df = pd.read_sql_query('SELECT * FROM ventas_proyectos ORDER BY fecha DESC', conn)
finally:
    conn.close()

st.markdown('## Flujo de Dinero — Resumen')
col1, col2 = st.columns(2)
with col1:
    st.metric('Ingresos Totales por Proyectos Vendidos (Comisiones)', f"€ {total_comisiones:,.2f}")
with col2:
    st.metric('Ingresos Recurrentes (Planes Arquitectos) — (mensual)', f"€ {total_suscripciones:,.2f}")

st.markdown('---')
st.subheader('Registro de Ventas de Proyectos')
if df is not None and not df.empty:
    # Mostrar tabla
    st.dataframe(df)
else:
    st.info('No hay ventas registradas aún.')
