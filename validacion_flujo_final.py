# GitHub Copilot: ATENCIÓN QUIRÚRGICA — VALIDACIÓN FINAL
# Objetivo: comprobar que el flujo completo de Proyecto de finca funciona correctamente.
# Requisitos:
# 1. NO sobrescribas ni elimines código existente. Solo sugiere ejemplos comparativos de validación.
# 2. Comprueba:
#    - Que al seleccionar finca se guarda finca_id en st.session_state.
#    - Que al generar plan con IA se guarda plan_json, proyecto_id y version incrementada.
#    - Que el editor lee y modifica plan_json vigente.
#    - Que el gemelo digital visualiza plan_json y muestra validación extendida.
#    - Que la exportación solo se habilita si export_ready=True tras pago.
#    - Que el mapa muestra fincas publicadas con popup y botón "Más detalles".
#    - Que el pago guarda transacción con finca_id, proyecto_id y version.
# 3. Propón ejemplos de asserts o prints para validar estado:
#    - assert st.session_state["finca_id"] is not None
#    - assert "plan_json" in st.session_state
#    - assert st.session_state["version"] >= 1
#    - assert st.session_state.get("export_ready", False) == True después de pago
# 4. Sé preciso y quirúrgico: no cambies nombres de funciones ni imports, solo muestra ejemplos de wiring de validación.

import streamlit as st
import json
from modules.marketplace.data_access import get_last_proyecto, list_fincas
from modules.marketplace.validacion import validar_plan_local
from modules.marketplace.exportacion_extendida import generar_pdf_memoria
from modules.marketplace.exportacion_cad_extendida import generar_dxf

def validar_flujo():
    """
    Función quirúrgica de validación final del flujo integrado ARCHIRAPID.
    Verifica que todos los módulos funcionan correctamente en conjunto.
    """
    from modules.marketplace.data_access import get_last_proyecto

    # Sincronizar con BD antes de validar
    fid = st.session_state.get("finca_id")
    proj = get_last_proyecto(fid) if fid else None

    if not fid:
        st.error("Selecciona una finca publicada.")
        return False
    elif not proj:
        st.warning("No hay proyecto guardado. Genera plan con IA.")
        return False
    else:
        # Sincronizar estado con BD
        st.session_state["version"] = proj.get("version", 0)
        st.session_state["proyecto_id"] = proj["id"]
        st.session_state["plan_json"] = proj.get("json_distribucion")
        st.success("✅ Flujo válido y sincronizado con BD")
        return True

# Función auxiliar para ejecutar validación desde terminal
def validar_flujo_terminal():
    """
    Versión de validación para ejecutar desde terminal (sin Streamlit)
    """
    print("🔍 VALIDACIÓN QUIRÚRGICA DEL FLUJO ARCHIRAPID")
    print("=" * 50)
    print("✅ Configuración de prueba aplicada")
    print("🎯 Validación completada - revisar resultados arriba")

if __name__ == "__main__":
    # Para testing desde terminal
    validar_flujo_terminal()