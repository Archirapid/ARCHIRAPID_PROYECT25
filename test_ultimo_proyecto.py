"""
Script de prueba para detectar el problema con architect_id
"""
import sqlite3

# Verificar último proyecto guardado
conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute("""
    SELECT title, architect_id, architect_name, created_at 
    FROM projects 
    ORDER BY created_at DESC 
    LIMIT 1
""")

ultimo = c.fetchone()
if ultimo:
    print("\n🔍 ÚLTIMO PROYECTO GUARDADO:")
    print(f"Título: {ultimo[0]}")
    print(f"architect_id: [{ultimo[1]}]")
    print(f"architect_name: {ultimo[2]}")
    print(f"created_at: {ultimo[3]}")
    
    if ultimo[1] is None:
        print("\n❌ CONFIRMADO: architect_id se guardó como NULL")
        print("\n💡 CONCLUSIÓN:")
        print("   El problema NO está en insert_project()")
        print("   El problema está en que el parámetro 'architect_id'")
        print("   que recibe show_create_project_modal() es None")
        print("\n🔧 POSIBLE CAUSA:")
        print("   Streamlit @st.dialog reinicia el scope de variables")
        print("   Los parámetros de función no se preservan entre reruns")
    else:
        print(f"\n✅ architect_id correcto: {ultimo[1]}")

conn.close()
