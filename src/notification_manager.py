# Notification Manager - Sistema completo de notificaciones

import os
import uuid
import json
import yagmail
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
from src.db import get_conn

# Configuración de email
SMTP_USER = os.getenv('SMTP_USER', 'noreply@archirapid.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Tipos de notificaciones
NOTIFICATION_TYPES = {
    'new_proposal': {'icon': '📨', 'title': 'Nueva Propuesta', 'priority': 'normal'},
    'proposal_accepted': {'icon': '✅', 'title': 'Propuesta Aceptada', 'priority': 'high'},
    'proposal_rejected': {'icon': '❌', 'title': 'Propuesta Rechazada', 'priority': 'normal'},
    'payment_received': {'icon': '💰', 'title': 'Pago Recibido', 'priority': 'high'},
    'subscription_expiring': {'icon': '⏰', 'title': 'Suscripción Expirando', 'priority': 'urgent'},
    'subscription_renewed': {'icon': '🔄', 'title': 'Suscripción Renovada', 'priority': 'normal'},
    'new_message': {'icon': '💬', 'title': 'Nuevo Mensaje', 'priority': 'normal'},
    'system_alert': {'icon': '⚠️', 'title': 'Alerta del Sistema', 'priority': 'urgent'}
}

class NotificationManager:
    def __init__(self):
        self.yag = None
        if SMTP_USER and SMTP_PASSWORD:
            try:
                self.yag = yagmail.SMTP(SMTP_USER, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT)
            except Exception as e:
                print(f"Error inicializando email: {e}")

    def send_email(self, to: str, subject: str, html_content: str) -> bool:
        """Enviar email de notificación"""
        if not self.yag:
            print("Email no configurado")
            return False

        try:
            self.yag.send(to=to, subject=subject, contents=html_content)
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

    def create_notification(self, user_id: str, user_type: str, notification_type: str,
                          title: str, message: str, data: Optional[Dict] = None) -> str:
        """Crear nueva notificación en BD"""
        from src.db import ensure_tables

        notification_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        with get_conn() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO notifications (id, user_id, user_type, type, title, message, data, read, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (notification_id, user_id, user_type, notification_type, title, message,
                  json.dumps(data) if data else None, False, created_at))

        return notification_id

    def get_user_notifications(self, user_id: str, user_type: str, limit: int = 50) -> List[Dict]:
        """Obtener notificaciones de un usuario"""
        with get_conn() as conn:
            df = pd.read_sql_query('''
                SELECT * FROM notifications
                WHERE user_id = ? AND user_type = ?
                ORDER BY created_at DESC LIMIT ?
            ''', conn, params=(user_id, user_type, limit))

        notifications = []
        for _, row in df.iterrows():
            notifications.append({
                'id': row['id'],
                'type': row['type'],
                'title': row['title'],
                'message': row['message'],
                'data': json.loads(row['data']) if row['data'] else None,
                'read': bool(row['read']),
                'created_at': row['created_at']
            })

        return notifications

    def mark_as_read(self, notification_id: str):
        """Marcar notificación como leída"""
        with get_conn() as conn:
            c = conn.cursor()
            c.execute('UPDATE notifications SET read = 1 WHERE id = ?', (notification_id,))

    def get_unread_count(self, user_id: str, user_type: str) -> int:
        """Contar notificaciones no leídas"""
        with get_conn() as conn:
            df = pd.read_sql_query('''
                SELECT COUNT(*) as count FROM notifications
                WHERE user_id = ? AND user_type = ? AND read = 0
            ''', conn, params=(user_id, user_type))

        return df.iloc[0]['count'] if df.shape[0] > 0 else 0

    def send_notification(self, user_id: str, user_type: str, notification_type: str,
                         title: str, message: str, email: Optional[str] = None,
                         data: Optional[Dict] = None) -> str:
        """Enviar notificación completa (BD + email si aplica)"""
        # Crear en BD
        notification_id = self.create_notification(user_id, user_type, notification_type, title, message, data)

        # Enviar email si se proporciona dirección y es alta prioridad
        if email and NOTIFICATION_TYPES[notification_type]['priority'] in ['high', 'urgent']:
            html_content = self._generate_email_html(notification_type, title, message)
            self.send_email(email, f"ARCHIRAPID - {title}", html_content)

        return notification_id

    def _generate_email_html(self, notification_type: str, title: str, message: str) -> str:
        """Generar HTML para email de notificación"""
        icon = NOTIFICATION_TYPES[notification_type]['icon']

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                .header {{ text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 20px; }}
                .content {{ margin: 20px 0; line-height: 1.6; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{icon} {title}</h1>
                    <p>ARCHIRAPID - Plataforma de Arquitectura</p>
                </div>
                <div class="content">
                    <p>{message}</p>
                    <p><a href="http://localhost:8504" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver en la App</a></p>
                </div>
                <div class="footer">
                    <p>Este es un email automático, por favor no responder.</p>
                    <p>&copy; 2025 ARCHIRAPID. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

# Instancia global
notification_manager = NotificationManager()

# Funciones de conveniencia
def send_notification(user_id: str, user_type: str, notification_type: str,
                     title: str, message: str, email: Optional[str] = None,
                     data: Optional[Dict] = None) -> str:
    """Función de conveniencia para enviar notificaciones"""
    return notification_manager.send_notification(user_id, user_type, notification_type, title, message, email, data)

def get_user_notifications(user_id: str, user_type: str, limit: int = 50) -> List[Dict]:
    """Función de conveniencia para obtener notificaciones"""
    return notification_manager.get_user_notifications(user_id, user_type, limit)

def get_unread_count(user_id: str, user_type: str) -> int:
    """Función de conveniencia para contar no leídas"""
    return notification_manager.get_unread_count(user_id, user_type)

def show_notifications_ui(user_id: str, user_type: str):
    """UI para mostrar notificaciones en Streamlit"""
    st.header("🔔 Notificaciones")

    # Contador de no leídas
    unread_count = get_unread_count(user_id, user_type)
    if unread_count > 0:
        st.info(f"Tienes {unread_count} notificaciones sin leer")

    # Obtener notificaciones
    notifications = get_user_notifications(user_id, user_type)

    if not notifications:
        st.info("No tienes notificaciones")
        return

    # Mostrar notificaciones
    for notification in notifications:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                icon = NOTIFICATION_TYPES.get(notification['type'], {}).get('icon', '📢')
                if not notification['read']:
                    st.markdown(f"**{icon}**")
                else:
                    st.markdown(f"{icon}")

            with col2:
                if not notification['read']:
                    st.markdown(f"**{notification['title']}**")
                else:
                    st.markdown(notification['title'])
                st.caption(notification['message'])

                # Timestamp
                created_at = datetime.fromisoformat(notification['created_at'])
                time_ago = _get_time_ago(created_at)
                st.caption(f"Hace {time_ago}")

            with col3:
                if not notification['read']:
                    if st.button("Marcar como leída", key=f"read_{notification['id']}"):
                        notification_manager.mark_as_read(notification['id'])
                        st.rerun()

            st.divider()

def _get_time_ago(dt: datetime) -> str:
    """Calcular tiempo transcurrido"""
    now = datetime.now()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} días"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} horas"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutos"
    else:
        return "ahora"

# Funciones para eventos específicos
def notify_new_proposal(proposal_data: Dict):
    """Notificar nueva propuesta"""
    # Notificar al propietario de la finca
    plot_owner_email = proposal_data.get('plot_owner_id')  # Es el email
    architect_name = proposal_data.get('architect_name', 'Arquitecto')

    if plot_owner_email:
        send_notification(
            user_id=plot_owner_email,  # Usar email como ID temporal
            user_type='client',
            notification_type='new_proposal',
            title='Nueva Propuesta Recibida',
            message=f"El arquitecto {architect_name} ha enviado una propuesta para tu finca.",
            email=plot_owner_email,  # Enviar email también
            data={'proposal_id': proposal_data.get('id')}
        )

def notify_proposal_accepted(proposal_data: Dict):
    """Notificar propuesta aceptada"""
    architect_id = proposal_data.get('architect_id')
    client_name = proposal_data.get('client_name', 'Cliente')

    if architect_id:
        send_notification(
            user_id=architect_id,
            user_type='architect',
            notification_type='proposal_accepted',
            title='¡Propuesta Aceptada!',
            message=f"Tu propuesta ha sido aceptada por {client_name}.",
            data={'proposal_id': proposal_data.get('id')}
        )

def notify_subscription_expiring(architect_id: str, days_left: int):
    """Notificar suscripción expirando"""
    from app import get_architect_by_id
    architect = get_architect_by_id(architect_id)

    if architect:
        send_notification(
            user_id=architect_id,
            user_type='architect',
            notification_type='subscription_expiring',
            title='Suscripción Expirando',
            message=f"Tu suscripción expira en {days_left} días. Renueva para continuar enviando propuestas.",
            email=architect.get('email')
        )

def notify_payment_received(payment_data: Dict):
    """Notificar pago recibido"""
    user_id = payment_data.get('user_id')
    user_type = payment_data.get('user_type')
    amount = payment_data.get('amount')

    send_notification(
        user_id=user_id,
        user_type=user_type,
        notification_type='payment_received',
        title='Pago Recibido',
        message=f"Se ha recibido un pago de €{amount:.2f}.",
        data=payment_data
    )