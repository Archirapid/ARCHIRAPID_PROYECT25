# Subscription Manager - Gestión de suscripciones con Stripe

import os
import stripe
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import streamlit as st

# Configuración de Stripe
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_...')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
stripe.api_key = STRIPE_SECRET_KEY

# Planes de suscripción
SUBSCRIPTION_PLANS = {
    'starter': {
        'name': 'Starter',
        'price_monthly': 29.99,
        'price_yearly': 299.99,
        'monthly_proposals_limit': 50,
        'commission_rate': 0.15,
        'features': ['Hasta 50 propuestas/mes', 'Comisión 15%', 'Soporte básico']
    },
    'professional': {
        'name': 'Professional',
        'price_monthly': 79.99,
        'price_yearly': 799.99,
        'monthly_proposals_limit': 200,
        'commission_rate': 0.12,
        'features': ['Hasta 200 propuestas/mes', 'Comisión 12%', 'Soporte prioritario', 'Analytics avanzados']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price_monthly': 199.99,
        'price_yearly': 1999.99,
        'monthly_proposals_limit': 1000,
        'commission_rate': 0.10,
        'features': ['Hasta 1000 propuestas/mes', 'Comisión 10%', 'Soporte 24/7', 'API access', 'Consultoría dedicada']
    }
}

def create_stripe_customer(email: str, name: str) -> str:
    """Crear cliente en Stripe"""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
        )
        return customer.id
    except Exception as e:
        st.error(f"Error creando cliente Stripe: {e}")
        return None

def create_subscription_checkout_session(architect_id: str, plan_type: str, billing_cycle: str = 'monthly') -> Optional[str]:
    """Crear sesión de checkout para suscripción"""
    try:
        plan = SUBSCRIPTION_PLANS.get(plan_type)
        if not plan:
            st.error("Plan no encontrado")
            return None

        price = plan[f'price_{billing_cycle}']

        # Crear productos y precios en Stripe si no existen
        product_name = f"ARCHIRAPID {plan['name']} - {billing_cycle.capitalize()}"
        product = stripe.Product.create(name=product_name)

        price_obj = stripe.Price.create(
            product=product.id,
            unit_amount=int(price * 100),  # Centavos
            currency='eur',
            recurring={'interval': billing_cycle[:-2]},  # monthly -> month, yearly -> year
        )

        # Crear sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_obj.id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.getenv('APP_URL', 'http://localhost:8504')}/?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('APP_URL', 'http://localhost:8504')}/?canceled=true",
            metadata={
                'architect_id': architect_id,
                'plan_type': plan_type,
                'billing_cycle': billing_cycle
            }
        )

        return checkout_session.url

    except Exception as e:
        st.error(f"Error creando checkout: {e}")
        return None

def handle_stripe_webhook(payload: bytes, sig_header: str) -> bool:
    """Manejar webhooks de Stripe"""
    try:
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        if event.type == 'checkout.session.completed':
            session = event.data.object
            handle_subscription_created(session)

        elif event.type == 'invoice.payment_succeeded':
            invoice = event.data.object
            handle_subscription_renewed(invoice)

        elif event.type == 'invoice.payment_failed':
            invoice = event.data.object
            handle_subscription_payment_failed(invoice)

        return True

    except Exception as e:
        print(f"Webhook error: {e}")
        return False

def handle_subscription_created(session):
    """Manejar creación de suscripción"""
    try:
        architect_id = session.metadata.get('architect_id')
        plan_type = session.metadata.get('plan_type')
        billing_cycle = session.metadata.get('billing_cycle', 'monthly')

        # Obtener detalles de la suscripción
        subscription_id = session.subscription
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Calcular fechas
        start_date = datetime.fromtimestamp(subscription.current_period_start)
        end_date = datetime.fromtimestamp(subscription.current_period_end)

        # Insertar en BD
        from src.db import insert_subscription
        insert_subscription({
            'id': subscription_id,
            'architect_id': architect_id,
            'plan_type': plan_type,
            'price': SUBSCRIPTION_PLANS[plan_type][f'price_{billing_cycle}'],
            'monthly_proposals_limit': SUBSCRIPTION_PLANS[plan_type]['monthly_proposals_limit'],
            'commission_rate': SUBSCRIPTION_PLANS[plan_type]['commission_rate'],
            'status': 'active',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'created_at': datetime.now().isoformat()
        })

        print(f"Suscripción creada: {subscription_id} para {architect_id}")

    except Exception as e:
        print(f"Error manejando creación de suscripción: {e}")

def handle_subscription_renewed(invoice):
    """Manejar renovación de suscripción"""
    try:
        subscription_id = invoice.subscription
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Actualizar end_date en BD
        end_date = datetime.fromtimestamp(subscription.current_period_end)

        from src.db import update_subscription_end_date
        update_subscription_end_date(subscription_id, end_date.isoformat())

        print(f"Suscripción renovada: {subscription_id}")

    except Exception as e:
        print(f"Error manejando renovación: {e}")

def handle_subscription_payment_failed(invoice):
    """Manejar fallo de pago de suscripción"""
    try:
        subscription_id = invoice.subscription

        # Marcar como inactiva en BD
        from src.db import update_subscription_status
        update_subscription_status(subscription_id, 'past_due')

        print(f"Pago fallido para suscripción: {subscription_id}")

    except Exception as e:
        print(f"Error manejando pago fallido: {e}")

def cancel_subscription(subscription_id: str) -> bool:
    """Cancelar suscripción"""
    try:
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )

        # Actualizar BD
        from src.db import update_subscription_status
        update_subscription_status(subscription_id, 'canceling')

        return True

    except Exception as e:
        st.error(f"Error cancelando suscripción: {e}")
        return False

def get_subscription_plans() -> Dict:
    """Obtener planes disponibles"""
    return SUBSCRIPTION_PLANS

def show_subscription_management(architect_id: str):
    """UI para gestión de suscripciones"""
    st.header("🎯 Gestión de Suscripción")

    # Obtener suscripción actual
    from app import get_architect_subscription
    subscription = get_architect_subscription(architect_id)

    if subscription:
        st.subheader("📋 Tu Plan Actual")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Plan", subscription['plan_type'].title())
        with col2:
            st.metric("Estado", subscription['status'].title())
        with col3:
            end_date = datetime.fromisoformat(subscription['end_date'])
            days_left = (end_date - datetime.now()).days
            st.metric("Días Restantes", max(0, days_left))

        # Mostrar límites de uso
        from app import get_monthly_proposals_count
        proposals_sent = get_monthly_proposals_count(architect_id)
        remaining = subscription['monthly_proposals_limit'] - proposals_sent

        st.progress(min(1.0, proposals_sent / subscription['monthly_proposals_limit']))
        st.caption(f"Propuestas enviadas: {proposals_sent}/{subscription['monthly_proposals_limit']}")

        # Botón para cancelar
        if st.button("❌ Cancelar Suscripción", type="secondary"):
            if cancel_subscription(subscription['id']):
                st.success("Suscripción cancelada. Seguirás teniendo acceso hasta el final del período.")
                st.rerun()

    else:
        st.subheader("🚀 Elige tu Plan")

        # Mostrar planes disponibles
        plans = get_subscription_plans()
        cols = st.columns(len(plans))

        for i, (plan_key, plan) in enumerate(plans.items()):
            with cols[i]:
                with st.container():
                    st.markdown(f"### {plan['name']}")
                    st.markdown(f"**€{plan['price_monthly']:.2f}/mes** o **€{plan['price_yearly']:.2f}/año**")

                    st.markdown("**Incluye:**")
                    for feature in plan['features']:
                        st.markdown(f"✅ {feature}")

                    # Botones de selección
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Contratar Mensual", key=f"{plan_key}_monthly"):
                            checkout_url = create_subscription_checkout_session(architect_id, plan_key, 'monthly')
                            if checkout_url:
                                st.markdown(f"[Pagar con Stripe]({checkout_url})")

                    with col2:
                        if st.button(f"Contratar Anual", key=f"{plan_key}_yearly"):
                            checkout_url = create_subscription_checkout_session(architect_id, plan_key, 'yearly')
                            if checkout_url:
                                st.markdown(f"[Pagar con Stripe]({checkout_url})")