"""
ARCHIRAPID - Payment Simulator
Sistema de simulación de pagos para MVP (no requiere pasarela real)
Versión 2.0 con Modal Dialog para mejor UX
"""
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io
import uuid


@st.dialog("💳 Checkout - Pago Seguro", width="medium")
def payment_modal(amount, concept, buyer_name="", buyer_email=""):
    """
    Modal de pago con formulario amplio y profesional
    
    Args:
        amount: Importe en euros
        concept: Descripción del pago
        buyer_name: Nombre del comprador (prellenado)
        buyer_email: Email del comprador (prellenado)
        
    Returns:
        dict con payment_data en session_state si confirma
    """
    
    st.markdown("### � Resumen de tu Pedido")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info(f"**{concept}**")
    with col2:
        st.metric("💰 Total", f"{amount:,.2f} €", label_visibility="visible")
    
    st.markdown("---")
    
    # Formulario comprador
    st.markdown("### 👤 Datos de Facturación")
    
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("Nombre completo*", value=buyer_name, key="modal_name")
    with col_b:
        email = st.text_input("Email*", value=buyer_email, key="modal_email")
    
    col_c, col_d = st.columns(2)
    with col_c:
        phone = st.text_input("Teléfono*", placeholder="+34 600 000 000", key="modal_phone")
    with col_d:
        nif = st.text_input("NIF/NIE", placeholder="12345678X", key="modal_nif")
    
    st.markdown("---")
    st.markdown("### 💳 Método de Pago")
    
    payment_method = st.radio(
        "Selecciona método:",
        ["💳 Tarjeta de Crédito/Débito", "🏦 Transferencia Bancaria"],
        horizontal=True,
        key="modal_payment_method"
    )
    
    if "Tarjeta" in payment_method:
        st.caption("⚠️ **Modo Simulación MVP** - Introduce cualquier dato válido (no se procesará cargo real)")
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            card_number = st.text_input(
                "Número de tarjeta", 
                value="4111 1111 1111 1111",
                help="Simulación MVP - puedes modificar",
                key="modal_card",
                placeholder="1234 5678 9012 3456"
            )
        with col2:
            expiry = st.text_input(
                "Caducidad (MM/AA)", 
                value="12/28", 
                key="modal_exp",
                help="Formato: MM/AA",
                placeholder="12/28"
            )
        with col3:
            cvv = st.text_input(
                "CVV", 
                value="123", 
                type="password", 
                key="modal_cvv",
                placeholder="123"
            )
    else:
        st.info("📋 **Instrucciones de transferencia:**\n\n"
                "IBAN: ES12 1234 5678 9012 3456 7890\n\n"
                "Beneficiario: ARCHIRAPID SL\n\n"
                "Concepto: Indicar tu email")
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        if st.button("✅ CONFIRMAR PAGO", width='stretch', type="primary", key="modal_confirm"):
            if not name or not email or not phone:
                st.error("❌ Completa todos los campos obligatorios (*)")
            else:
                # Simular procesamiento
                with st.spinner("Procesando pago seguro..."):
                    import time
                    time.sleep(1.5)
                
                payment_data = {
                    'payment_id': uuid.uuid4().hex,
                    'amount': amount,
                    'concept': concept,
                    'buyer_name': name,
                    'buyer_email': email,
                    'buyer_phone': phone,
                    'buyer_nif': nif,
                    'card_last4': '1111' if "Tarjeta" in payment_method else 'N/A',
                    'status': 'COMPLETED',
                    'timestamp': datetime.utcnow().isoformat(),
                    'method': payment_method
                }
                
                # Guardar en session_state para acceder desde fuera del modal
                st.session_state['last_payment'] = payment_data
                st.session_state['payment_completed'] = True
                st.rerun()
    
    with col_btn2:
        if st.button("❌ Cancelar", width='stretch', key="modal_cancel"):
            st.session_state['payment_completed'] = False
            st.rerun()
    
    with col_btn3:
        st.caption("🔒 Pago seguro")


def show_payment_success(payment_data, download_receipt=True):
    """
    Muestra confirmación de pago exitoso (fuera del modal)
    
    Args:
        payment_data: dict con datos del pago
        download_receipt: si True, muestra botón descarga recibo
    """
    st.success("✅ ¡Pago procesado correctamente!")
    st.balloons()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Nº Transacción:**\n`{payment_data['payment_id'][:16].upper()}`")
    with col2:
        st.info(f"**Importe:**\n**{payment_data['amount']:,.2f} €**")
    with col3:
        st.info(f"**Estado:**\n✅ **COMPLETADO**")
    
    st.markdown("---")
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown("### 📧 Confirmación Enviada")
        st.write(f"Hemos enviado un email de confirmación a:")
        st.code(payment_data['buyer_email'])
        st.caption("(Simulación MVP - Email no enviado realmente)")
    
    with col_b:
        if download_receipt:
            st.markdown("### 📄 Tu Recibo")
            pdf_bytes = generate_receipt_pdf(payment_data)
            
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_bytes,
                file_name=f"recibo_{payment_data['payment_id'][:8]}.pdf",
                mime="application/pdf",
                width='stretch'
            )


def generate_receipt_pdf(payment_data):
    """
    Genera recibo PDF del pago
    
    Args:
        payment_data: dict con datos del pago
        
    Returns:
        bytes del PDF generado
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Encabezado
    c.setFont("Helvetica-Bold", 24)
    c.drawString(2*cm, height - 3*cm, "ARCHIRAPID")
    
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, height - 3.8*cm, "Recibo de Pago - Simulación MVP")
    
    # Línea separadora
    c.line(2*cm, height - 4.2*cm, width - 2*cm, height - 4.2*cm)
    
    # Datos del pago
    y = height - 5.5*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, f"Nº Transacción: {payment_data['payment_id'][:16].upper()}")
    
    y -= 0.8*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, f"Fecha: {datetime.fromisoformat(payment_data['timestamp']).strftime('%d/%m/%Y %H:%M')}")
    
    y -= 0.6*cm
    c.drawString(2*cm, y, f"Estado: ✓ {payment_data['status']}")
    
    # Datos del comprador
    y -= 1.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Datos del Comprador:")
    
    y -= 0.8*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, f"Nombre: {payment_data['buyer_name']}")
    
    y -= 0.6*cm
    c.drawString(2*cm, y, f"Email: {payment_data['buyer_email']}")
    
    y -= 0.6*cm
    c.drawString(2*cm, y, f"Teléfono: {payment_data.get('buyer_phone', 'N/A')}")
    
    if payment_data.get('buyer_nif'):
        y -= 0.6*cm
        c.drawString(2*cm, y, f"NIF/NIE: {payment_data['buyer_nif']}")
    
    # Detalle del pago
    y -= 1.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Detalle del Pago:")
    
    y -= 0.8*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, f"Concepto: {payment_data['concept']}")
    
    y -= 0.6*cm
    c.drawString(2*cm, y, f"Método: {payment_data['method']}")
    
    # Total destacado
    y -= 2*cm
    c.setFillColorRGB(0, 0.5, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, f"TOTAL PAGADO: {payment_data['amount']:,.2f} €")
    
    # Pie de página
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 8)
    c.drawString(2*cm, 2.5*cm, "ARCHIRAPID - Tu Proyecto, Tu Finca, Tu Futuro")
    c.drawString(2*cm, 2*cm, "www.archirapid.com | info@archirapid.com")
    c.drawString(2*cm, 1.5*cm, "⚠️ Este es un recibo simulado para demostración MVP - No tiene validez fiscal")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.getvalue()
