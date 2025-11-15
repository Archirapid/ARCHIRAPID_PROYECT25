# SPRINT 2 - CAMBIOS PENDIENTES

## ✅ Completado
- Backup pre-Sprint2 creado
- Migración BD: Agregadas columnas `project_id` a `proposals`, creadas tablas `commissions` y `payments`
- Debug code eliminado (pendiente aplicar cambios si tool se habilita)

## 🔨 Cambios necesarios en app.py

### 1. Modificar función `insert_proposal` (línea 228)

**ANTES:**
```python
def insert_proposal(data):
    """Insertar nueva propuesta con detalles económicos"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO proposals (
        id, architect_id, plot_id, proposal_text, estimated_budget, deadline_days, 
        sketch_image_path, status, created_at, responded_at,
        delivery_format, delivery_price, supervision_fee, visa_fee, total_cliente, commission
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        data['id'], data['architect_id'], data['plot_id'], data['proposal_text'], 
        data['estimated_budget'], data['deadline_days'], data.get('sketch_image_path'), 
        data['status'], data['created_at'], data.get('responded_at'),
        data.get('delivery_format', 'PDF'), data.get('delivery_price', 1200),
        data.get('supervision_fee', 0), data.get('visa_fee', 0),
        data.get('total_cliente', 0), data.get('commission', 0)
    ))
```

**DESPUÉS:**
```python
def insert_proposal(data):
    """Insertar nueva propuesta con detalles económicos"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO proposals (
        id, architect_id, plot_id, proposal_text, estimated_budget, deadline_days, 
        sketch_image_path, status, created_at, responded_at,
        delivery_format, delivery_price, supervision_fee, visa_fee, total_cliente, commission,
        project_id
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        data['id'], data['architect_id'], data['plot_id'], data['proposal_text'], 
        data['estimated_budget'], data['deadline_days'], data.get('sketch_image_path'), 
        data['status'], data['created_at'], data.get('responded_at'),
        data.get('delivery_format', 'PDF'), data.get('delivery_price', 1200),
        data.get('supervision_fee', 0), data.get('visa_fee', 0),
        data.get('total_cliente', 0), data.get('commission', 0),
        data.get('project_id')  # NUEVO
    ))
```

### 2. Modificar `show_proposal_modal` (línea ~730)

**ANTES:**
```python
            proposal_data = {
                'id': proposal_id,
                'architect_id': architect_id,
                'plot_id': plot_id,
                'proposal_text': proposal_text,
                'estimated_budget': estimated_budget,
                'deadline_days': deadline_days,
                'sketch_image_path': sketch_path,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'responded_at': None,
                'delivery_format': delivery_format,
                'delivery_price': delivery_price,
                'supervision_fee': supervision_fee,
                'visa_fee': visa_fee,
                'total_cliente': total_cliente,
                'commission': commission
            }
```

**DESPUÉS:**
```python
            proposal_data = {
                'id': proposal_id,
                'architect_id': architect_id,
                'plot_id': plot_id,
                'proposal_text': proposal_text,
                'estimated_budget': estimated_budget,
                'deadline_days': deadline_days,
                'sketch_image_path': sketch_path,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'responded_at': None,
                'delivery_format': delivery_format,
                'delivery_price': delivery_price,
                'supervision_fee': supervision_fee,
                'visa_fee': visa_fee,
                'total_cliente': total_cliente,
                'commission': commission,
                'project_id': selected_project['id'] if selected_project else None  # NUEVO
            }
```

### 3. Eliminar debug code (líneas 2148-2152)

**ELIMINAR:**
```python
        # DEBUG TEMPORAL
        st.sidebar.write(f"🔍 DEBUG arch_id: {arch_id[:8]}...")
        st.sidebar.write(f"🔍 Subscription: {subscription is not None}")
        if subscription:
            st.sidebar.write(f"✅ Plan: {subscription.get('plan_type')}")
```

## 📋 Próximos pasos

### 4. Panel Cliente - Vista Propuestas Recibidas
- Crear función `get_client_proposals(client_email)` que haga JOIN entre proposals, plots, architects, projects
- Agregar tab "📨 Propuestas Recibidas" en panel cliente
- Mostrar cards con: foto proyecto, nombre arquitecto, presupuesto, detalles técnicos

### 5. Botones Aceptar/Rechazar
- En cada card de propuesta, botones "✅ Aceptar" y "❌ Rechazar"
- Al hacer clic, actualizar `proposals.status` y `proposals.responded_at`

### 6. Modal Pago Cliente
- Si status='accepted', mostrar `payment_modal` con `amount=total_cliente`
- Guardar pago en tabla `payments`

### 7. Sistema Comisiones
- Tras pago cliente exitoso, insertar en `commissions`:
  ```python
  {
      'id': uuid4(),
      'proposal_id': proposal_id,
      'architect_id': architect_id,
      'client_id': client_id,
      'amount': commission,
      'paid': False,
      'created_at': now()
  }
  ```

## 🎯 Estado actual
- ✅ BD migrada
- ⏸️ Esperando aplicar cambios en app.py (tools deshabilitados)
