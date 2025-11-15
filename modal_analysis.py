# Archivo temporal con la función modal
# Copiar este contenido en app.py después de get_image_base64() y antes de init_db()
import os
import streamlit as st

@st.dialog("📊 Análisis Catastral Completo", width="medium")
def show_analysis_modal(plot_id):
    """
    Modal con tabs para mostrar análisis catastral:
    - Métricas
    - Plano Vectorizado  
    - Exportar DXF
    - Diseñador IA (solo si usuario ha pagado)
    """
    from pathlib import Path
    
    # Obtener datos del caché
    cache_all = st.session_state.get('analysis_cache', {})
    cache = cache_all.get(plot_id)
    
    if not cache:
        st.error("❌ No hay datos de análisis disponibles. Ejecuta el análisis primero.")
        return
    
    edata = cache.get('edata') or {}
    vdata = cache.get('vdata') or {}
    output_dir = Path(cache.get('output_dir', 'archirapid_extract/catastro_output'))
    overlay_img = output_dir / "contours_visualization.png"
    clean_img = output_dir / "contours_clean.png"
    
    # Verificar si usuario ha pagado (reserva o compra de finca)
    user_has_paid = st.session_state.get('payment_completed', False)
    is_buildable = vdata.get('is_buildable', False)
    
    # Crear tabs dinámicamente
    tab_names = ["📊 Métricas", "🗺️ Plano Vectorizado", "📥 Exportar DXF"]
    if user_has_paid and is_buildable:
        tab_names.append("🏗️ Diseñador IA")
    
    tabs = st.tabs(tab_names)
    
    # TAB 1: MÉTRICAS
    with tabs[0]:
        st.markdown("### 📊 Métricas Catastrales")
        
        mc1, mc2 = st.columns(2)
        with mc1:
            st.metric("Referencia Catastral", edata.get("cadastral_ref") or edata.get("cadastral_reference", "N/A"))
            st.metric("Superficie Parcela", f"{edata.get('surface_m2', 0):,.0f} m²")
        with mc2:
            st.metric("Máx. Edificable", f"{edata.get('max_buildable_m2', 0):,.2f} m²")
            perc = edata.get('edificability_percent') or edata.get('edificability_ratio') or 0
            st.metric("% Edificabilidad", f"{perc*100:.1f}%")
        
        if vdata:
            if is_buildable:
                st.success("✅ FINCA EDIFICABLE")
            else:
                st.error("❌ NO EDIFICABLE (según criterios automáticos)")
            
            with st.expander("📋 Informe de Validación"):
                st.write({k: v for k, v in vdata.items() if k not in ['issues']})
                issues = vdata.get('issues', [])
                if issues:
                    st.markdown("**Observaciones:**")
                    for iss in issues:
                        st.markdown(f"- {iss}")
                else:
                    st.markdown("✓ Sin observaciones críticas")
    
    # TAB 2: PLANO VECTORIZADO
    with tabs[1]:
        st.markdown("### 🗺️ Plano Vectorizado")
        
        if overlay_img.exists() or clean_img.exists():
            sub_t1, sub_t2 = st.tabs(["Plano Limpio", "Overlay PDF"])
            with sub_t1:
                if clean_img.exists():
                    st.image(str(clean_img), caption="Contorno procesado limpio", width='stretch')
                else:
                    st.info("No disponible")
            with sub_t2:
                if overlay_img.exists():
                    st.image(str(overlay_img), caption="Contorno sobre documento original", width='stretch')
                else:
                    st.info("No disponible")
        else:
            st.warning("No se encontraron imágenes de plano vectorizado")
    
    # TAB 3: EXPORTAR DXF
    with tabs[2]:
        st.markdown("### 📥 Exportar DXF")
        
        try:
            from archirapid_extract.export_dxf import create_dxf_from_cadastral_output
            dxf_bytes = create_dxf_from_cadastral_output(output_dir=str(output_dir), scale_factor=0.1)
            
            if dxf_bytes:
                ref = edata.get("cadastral_ref") or edata.get("cadastral_reference") or "parcela"
                st.success("✅ Archivo DXF generado correctamente")
                st.download_button(
                    "⬇️ Descargar DXF (AutoCAD)",
                    data=dxf_bytes,
                    file_name=f"ARCHIRAPID_{ref}.dxf",
                    mime="application/dxf",
                    help="Archivo compatible con AutoCAD / Revit / CAD genérico",
                    width='stretch'
                )
                st.caption("📐 Compatible con AutoCAD, Revit, FreeCAD y otros programas CAD")
            else:
                st.warning("⚠️ DXF no generado (faltan datos GeoJSON)")
        except Exception as e:
            st.error(f"❌ Error exportando DXF: {e}")
    
    # TAB 4: DISEÑADOR IA (solo si pagado + edificable)
    if user_has_paid and is_buildable and len(tabs) > 3:
        with tabs[3]:
            st.markdown("### 🏗️ Diseñador Paramétrico IA")
            st.caption("🎯 Genera plano 2D, modelo 3D interactivo y presupuesto basado en geometría catastral")
            
            dcol1, dcol2, dcol3 = st.columns(3)
            with dcol1:
                num_bedrooms = st.selectbox("Dormitorios", [1,2,3,4], index=1, key=f"design_bedrooms_{plot_id}")
            with dcol2:
                num_floors = st.selectbox("Plantas", [1,2,3], index=0, key=f"design_floors_{plot_id}")
            with dcol3:
                setback_m = st.slider("Retranqueo (m)", min_value=1.0, max_value=8.0, value=3.0, step=0.5, key=f"design_setback_{plot_id}")
            
            if st.button("🚀 Generar Diseño 3D", key=f"btn_generate_design_{plot_id}", type="primary", width='stretch'):
                st.session_state['design_requested'] = {
                    'bedrooms': num_bedrooms,
                    'floors': num_floors,
                    'setback': setback_m,
                    'plot_id': plot_id
                }
                st.rerun()
            
            # Mostrar resultado del diseño si existe
            design_key = f"design_result_{plot_id}"
            if st.session_state.get(design_key):
                design_res = st.session_state[design_key]
                if design_res.get('success'):
                    st.success("✅ Diseño generado correctamente")
                    plan_path = os.path.join("archirapid_extract", "design_output", "design_plan.png")
                    if os.path.exists(plan_path):
                        st.image(plan_path, caption="Plano preliminar", width='stretch')
                    
                    budget = design_res.get("metadata", {}).get("budget", {})
                    if budget:
                        st.markdown("#### 💰 Presupuesto Estimado")
                        bc1, bc2, bc3 = st.columns(3)
                        with bc1:
                            st.metric("Sup. Construida", f"{budget.get('superficie_construida_m2',0):.1f} m²")
                        with bc2:
                            st.metric("Coste/m²", f"{budget.get('coste_por_m2_eur',0):.0f} €")
                        with bc3:
                            st.metric("Total Estimado", f"{budget.get('total_estimado_eur',0):,.0f} €")
                        st.caption("💡 Estimación orientativa. No incluye licencias ni impuestos adicionales.")
                    
                    # VISOR 3D INTERACTIVO
                    model_path = os.path.join("archirapid_extract", "design_output", "design_model.glb")
                    if os.path.exists(model_path):
                        with open(model_path, 'rb') as mf:
                            glb_bytes = mf.read()
                        import base64 as _b64
                        glb_b64 = _b64.b64encode(glb_bytes).decode()
                        st.markdown("#### 🏢 Modelo 3D Interactivo")
                        viewer_html = f"""
                        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                        <model-viewer src="data:model/gltf-binary;base64,{glb_b64}" camera-controls auto-rotate style="width:100%;height:450px;background:#f0f0f0;border-radius:12px;"></model-viewer>
                        <p style='text-align:center;font-size:12px;color:#666;margin-top:8px;'>🖱️ Rotar: arrastrar · Zoom: rueda · 📱 Móvil: multitouch</p>
                        """
                        st.components.v1.html(viewer_html, height=480)
                        dl1, dl2 = st.columns([2,1])
                        with dl1:
                            st.download_button("⬇️ Descargar GLB", data=glb_bytes, file_name="ARCHIRAPID_modelo.glb", mime="model/gltf-binary", width='stretch')
                        with dl2:
                            st.info(f"{len(glb_bytes)/1024:.1f} KB")
                    else:
                        st.warning("Modelo 3D no encontrado")
                else:
                    st.error(f"❌ Fallo generando diseño: {design_res.get('error','desconocido')}")
    
    # Mensaje si NO ha pagado pero la finca es edificable
    elif is_buildable and not user_has_paid:
        st.info("💡 **Diseñador IA disponible:** Reserva o compra esta finca para acceder al diseñador paramétrico 3D")
