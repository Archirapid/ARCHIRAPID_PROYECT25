# UI Manager - Funciones de interfaz de usuario para ARCHIRAPID

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
import json
import os

def show_analysis_modal_fullpage(plot_id: str):
    """Modal a página completa con análisis catastral detallado"""
    # Implementación aquí (copiada de app.py)
    pass

def show_analysis_modal(plot_id: str):
    """Modal profesional con tabs para análisis catastral completo"""
    from pathlib import Path
    
    cache_all = st.session_state.get('analysis_cache', {})
    cache = cache_all.get(plot_id)
    
    if not cache:
        st.error("❌ No hay datos de análisis disponibles.")
        return
    
    # CRÍTICO: Obtener datos REALES de la finca desde BD (no confiar solo en OCR)
    from app import get_plot_by_id  # Temporal, cambiar a import desde db
    plot_data = get_plot_by_id(plot_id)
    if not plot_data:
        st.error("❌ No se encontró la finca en la base de datos.")
        return
    
    edata = cache.get('edata') or {}
    vdata = cache.get('vdata') or {}
    output_dir = Path(cache.get('output_dir', 'archirapid_extract/catastro_output'))
    overlay_img = output_dir / "contours_visualization.png"
    clean_img = output_dir / "contours_clean.png"
    
    user_has_paid = st.session_state.get('payment_completed', False)
    
    # USAR DATOS REALES DE LA BD (no del OCR que puede estar equivocado)
    plot_type = plot_data.get('type', 'rural').lower()
    is_buildable = plot_type in ['urban', 'industrial']
    
    tab_names = ["📊 Métricas", "🗺️ Plano", "📥 DXF"]
    if user_has_paid and is_buildable:
        tab_names.append("🏗️ Diseñador IA")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        # Destacar estado edificable con banner visual
        if is_buildable:
            st.success(f"### ✅ FINCA EDIFICABLE - Tipo: {plot_data.get('type', 'N/A').upper()}")
        else:
            st.error(f"### ❌ NO EDIFICABLE - Tipo: {plot_data.get('type', 'N/A').upper()}")
        
        st.markdown("---")
        st.markdown("### 📋 Información Registrada (Base de Datos)")
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            st.metric("📍 Tipo de Finca", plot_data.get('type', 'N/A').upper())
        with bc2:
            st.metric("📏 Superficie Registrada", f"{plot_data.get('m2', 0):,.0f} m²")
        with bc3:
            st.metric("💰 Precio", f"€{plot_data.get('price', 0):,.0f}")
        
        st.markdown("---")
        st.markdown("### 🔍 Datos del Análisis Catastral (OCR)")
        mc1, mc2 = st.columns(2)
        with mc1:
            st.metric("Ref. Catastral", edata.get("cadastral_ref") or "N/A")
            st.metric("Superficie Detectada", f"{edata.get('surface_m2', 0):,.0f} m²")
        with mc2:
            st.metric("Máx. Edificable (estimado)", f"{edata.get('max_buildable_m2', 0):,.1f} m²")
            perc = edata.get('edificability_percent') or 0
            st.metric("% Edificabilidad", f"{perc*100:.1f}%")
        
        # Info sobre validación de datos
        ocr_type = vdata.get('classification', {}).get('terrain_type', '') if vdata else ''
        if ocr_type and ocr_type.lower() not in ['', 'desconocido', plot_type]:
            st.info(f"ℹ️ **Nota:** El OCR detectó '{ocr_type}' en el PDF, pero prevalecen los datos registrados ('{plot_type.upper()}'). La clasificación definitiva la determina el registro oficial.")
    
    with tabs[1]:
        if clean_img.exists():
            st.image(str(clean_img), width='stretch')
    
    with tabs[2]:
        try:
            from archirapid_extract.export_dxf import create_dxf_from_cadastral_output
            dxf_bytes = create_dxf_from_cadastral_output(output_dir=str(output_dir), scale_factor=0.1)
            if dxf_bytes:
                ref = edata.get("cadastral_ref") or "parcela"
                st.download_button("⬇️ Descargar DXF", dxf_bytes, f"ARCHIRAPID_{ref}.dxf", "application/dxf", width='stretch', key="download_dxf_analysis")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if user_has_paid and is_buildable and len(tabs) > 3:
        with tabs[3]:
            st.caption("🎯 Diseño paramétrico 3D")
            c1, c2, c3 = st.columns(3)
            with c1:
                beds = st.selectbox("Dormitorios", [1,2,3,4], 1, key=f"beds_{plot_id}")
            with c2:
                floors = st.selectbox("Plantas", [1,2,3], 0, key=f"floors_{plot_id}")
            with c3:
                setback = st.slider("Retranqueo (m)", 1.0, 8.0, 3.0, 0.5, key=f"set_{plot_id}")
            
            if st.button("🚀 Generar Diseño", key=f"gen_{plot_id}", type="primary", width='stretch'):
                st.session_state['design_requested'] = {'bedrooms': beds, 'floors': floors, 'setback': setback, 'plot_id': plot_id}
                st.rerun()
            
            design_key = f"design_result_{plot_id}"
            if st.session_state.get(design_key):
                res = st.session_state[design_key]
                if res.get('success'):
                    plan_path = "archirapid_extract/design_output/design_plan.png"
                    if os.path.exists(plan_path):
                        st.image(plan_path, width='stretch')
                    model_path = "archirapid_extract/design_output/design_model.glb"
                    if os.path.exists(model_path):
                        with open(model_path, 'rb') as f:
                            glb = f.read()
                        import base64 as b64
                        st.components.v1.html(f'<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script><model-viewer src="data:model/gltf-binary;base64,{b64.b64encode(glb).decode()}" camera-controls auto-rotate style="width:100%;height:400px;"></model-viewer>', 420)
    elif is_buildable and not user_has_paid:
        st.info("💡 Reserva o compra para acceder al Diseñador IA")


def show_3d_rv_viewer(design_id: str):
    """Vista 3D interactiva con Three.js y placeholder para tours VR"""
    st.header("🏠 Vista 3D Interactiva y Realidad Virtual")
    
    # Placeholder para tours VR
    st.subheader("🌐 Tour Virtual (RV)")
    st.info("🚧 **Placeholder:** Integración con plataforma de tours VR en desarrollo. Próximamente disponible.")
    st.markdown("""
    <iframe width="100%" height="400" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allowfullscreen></iframe>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Vista 3D con Three.js
    st.subheader("🔍 Modelo 3D Interactivo")
    st.caption("Vista preliminar del terreno y diseño básico con Three.js")
    
    # HTML con Three.js básico
    three_js_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body { margin: 0; }
            canvas { display: block; }
        </style>
    </head>
    <body>
        <script>
            // Escena básica Three.js
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer();
            renderer.setSize(window.innerWidth, 400);
            document.body.appendChild(renderer.domElement);
            
            // Terreno (plano verde)
            const geometry = new THREE.PlaneGeometry(10, 10);
            const material = new THREE.MeshBasicMaterial({color: 0x00ff00, side: THREE.DoubleSide});
            const plane = new THREE.Mesh(geometry, material);
            plane.rotation.x = Math.PI / 2;
            scene.add(plane);
            
            // Casa básica (cubo)
            const cubeGeometry = new THREE.BoxGeometry(2, 2, 2);
            const cubeMaterial = new THREE.MeshBasicMaterial({color: 0xff0000});
            const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
            cube.position.y = 1;
            scene.add(cube);
            
            camera.position.z = 5;
            
            function animate() {
                requestAnimationFrame(animate);
                cube.rotation.x += 0.01;
                cube.rotation.y += 0.01;
                renderer.render(scene, camera);
            }
            animate();
            
            // Ajustar tamaño al contenedor
            window.addEventListener('resize', function() {
                camera.aspect = window.innerWidth / 400;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, 400);
            });
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(three_js_html, height=420)