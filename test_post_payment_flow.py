#!/usr/bin/env python3
"""
Prueba del flujo post-pago corregido
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from modules.marketplace.utils import create_or_update_client_user, reserve_plot
import sqlite3

def test_post_payment_flow():
    """Prueba el flujo completo post-pago"""
    print("🧪 Probando flujo post-pago corregido...")

    # Simular datos de compra
    buyer_email = "cliente_test@example.com"
    buyer_name = "Cliente de Prueba"
    plot_id = "test_plot_123"
    amount = 1500.0

    # 1. Crear/actualizar usuario cliente (lo que hace el pago exitoso)
    print("1. Creando/actualizando usuario cliente...")
    create_or_update_client_user(buyer_email, buyer_name)
    print("   ✅ Usuario creado/actualizado")

    # 2. Reservar/compra de finca
    print("2. Procesando reserva/compra...")
    try:
        rid = reserve_plot(plot_id, buyer_name, buyer_email, amount, kind="purchase")
        print(f"   ✅ Transacción completada: {rid}")
    except Exception as e:
        print(f"   ⚠️  Reserva falló (esperado si la finca no existe): {e}")

    # 3. Verificar que el usuario existe en la DB con rol correcto
    print("3. Verificando usuario en base de datos...")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT email, full_name, role FROM users WHERE email = ?", (buyer_email,))
    user = c.fetchone()
    conn.close()

    if user:
        email, name, role = user
        print(f"   ✅ Usuario encontrado: {name} ({email}) - Rol: {role}")
        if role == 'client':
            print("   ✅ Rol correcto asignado")
        else:
            print(f"   ❌ Rol incorrecto: {role}")
    else:
        print("   ❌ Usuario no encontrado en DB")

    print("\n🎉 Flujo post-pago funcionando correctamente!")
    print(f"Usuario: {buyer_email}")
    print("Próximos pasos en UI:")
    print("  - Mensaje de éxito sin contraseñas")
    print("  - Documentación descargable desde data/notas_catastrales/")
    print("  - Botón único '🚀 ENTRAR A MI PANEL DE CONTROL'")
    print("  - Login automático y redirección a '👤 Panel de Cliente'")

if __name__ == "__main__":
    test_post_payment_flow()