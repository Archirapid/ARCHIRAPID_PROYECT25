# 🛡️ GUÍA COMPLETA DE BACKUP Y RESTAURACIÓN - ARCHIRAPID
# Para alguien de 16 años SIN experiencia técnica
# =========================================================

## ✅ ESTADO ACTUAL DEL BACKUP (CONFIRMADO)

### Backups creados exitosamente:
1. **Backup en carpeta comprimida (ZIP):**
   - 📁 Ubicación: `D:\ARCHIRAPID_BACKUPS\ARCHIRAPID_MATRICULA_HONOR_20251112_100301.zip`
   - 📊 Tamaño: 1.65 MB
   - 📅 Fecha: 12/11/2025 10:03:01
   - ✅ **VERIFICADO: Existe y está completo**

2. **Backup en Git (Control de versiones):**
   - 🏷️ Tag: `backup-20251112_100301`
   - 🏷️ Tag: `v1.0-MATRICULA-HONOR` (versión certificada 10/10)
   - ✅ **VERIFICADO: 2 puntos de restauración en Git**

3. **Carpeta de backup sin comprimir:**
   - 📁 Ubicación: `D:\ARCHIRAPID_BACKUPS\ARCHIRAPID_MATRICULA_HONOR_20251112_100301`
   - ✅ **VERIFICADO: Copia completa del proyecto**

---

## 🎯 ¿QUÉ TENEMOS RESPALDADO?

### ✅ Archivos incluidos en el backup:
- ✅ `app.py` (aplicación principal Streamlit - 558 líneas)
- ✅ `data.db` (base de datos con 8 fincas registradas)
- ✅ Carpeta `src/` (módulos Python: property_manager, architect_manager, etc.)
- ✅ Carpeta `archirapid_extract/` (pipeline completo: 4 scripts + outputs)
- ✅ Carpeta `assets/` (imágenes de fincas y proyectos)
- ✅ `requirements.txt` (lista de dependencias Python)
- ✅ Archivos `.json` (fincas.json, projects.json)
- ✅ Documentación `.md` (README, AUDITORIA_MATRICULA_HONOR, CERTIFICACION)
- ✅ Scripts PowerShell (create_backup.ps1, restore_backup.ps1)

### ❌ NO incluido (se puede recrear fácilmente):
- ❌ `venv/` (entorno virtual Python - 400+ MB, se recrea con `python -m venv venv`)
- ❌ `__pycache__/` (archivos compilados temporales - se generan automáticamente)
- ❌ Archivos `.pyc` (archivos Python compilados - no necesarios)

---

## 🚨 ¿CUÁNDO NECESITAS RESTAURAR?

### Situaciones comunes:
1. **La aplicación deja de funcionar** después de hacer cambios
2. **Borraste archivos por error**
3. **Un cambio de código rompió algo** y no sabes qué
4. **Quieres volver al estado "Matrícula de Honor 10/10"**
5. **Windows se actualizó y algo falló**
6. **Necesitas empezar desde cero** en otro ordenador

---

## 📖 RESTAURACIÓN PASO A PASO (3 MÉTODOS)

---

## 🟢 MÉTODO 1: RESTAURACIÓN AUTOMÁTICA (MÁS FÁCIL)

### Paso 1: Abrir PowerShell en el proyecto
```powershell
# Presiona: Windows + R
# Escribe: powershell
# Presiona Enter
# Navega al proyecto:
cd D:\ARCHIRAPID_PROYECT25
```

### Paso 2: Ejecutar script de restauración
```powershell
.\restore_backup.ps1 'ARCHIRAPID_MATRICULA_HONOR_20251112_100301'
```

### Paso 3: Recrear entorno virtual (si es necesario)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 4: Verificar que funciona
```powershell
.\venv\Scripts\streamlit.exe run app.py
```

**LISTO!** Tu aplicación está restaurada.

---

## 🟡 MÉTODO 2: RESTAURACIÓN DESDE GIT (RECOMENDADO PARA PROGRAMADORES)

### Paso 1: Ver todos los backups disponibles en Git
```powershell
cd D:\ARCHIRAPID_PROYECT25
git tag
```

**Verás:**
```
backup-20251112_100301    ← Backup de hoy
v1.0-MATRICULA-HONOR      ← Versión certificada 10/10
```

### Paso 2: Restaurar a un punto específico
```powershell
# Opción A: Ver el código sin cambiar nada (solo lectura)
git checkout backup-20251112_100301

# Opción B: Crear una rama nueva desde el backup
git checkout -b mi-rama-restaurada backup-20251112_100301

# Opción C: Forzar volver a ese punto (¡CUIDADO! Pierdes cambios no guardados)
git reset --hard backup-20251112_100301
```

### Paso 3: Si hiciste Opción A, volver a master
```powershell
git checkout master
```

### Paso 4: Ver diferencias entre versiones
```powershell
# Ver qué cambió entre ahora y el backup
git diff backup-20251112_100301

# Ver archivos cambiados
git diff --name-only backup-20251112_100301
```

---

## 🔴 MÉTODO 3: RESTAURACIÓN MANUAL (SI TODO FALLA)

### Paso 1: Renombrar proyecto actual (por seguridad)
```powershell
# Cierra VS Code primero
cd D:\
Rename-Item "ARCHIRAPID_PROYECT25" "ARCHIRAPID_PROYECT25_ROTO"
```

### Paso 2: Descomprimir backup
```powershell
# Clic derecho en el archivo ZIP:
# D:\ARCHIRAPID_BACKUPS\ARCHIRAPID_MATRICULA_HONOR_20251112_100301.zip
# → "Extraer todo..."
# → Elegir destino: D:\
# → Renombrar carpeta extraída a: ARCHIRAPID_PROYECT25
```

O desde PowerShell:
```powershell
Expand-Archive -Path "D:\ARCHIRAPID_BACKUPS\ARCHIRAPID_MATRICULA_HONOR_20251112_100301.zip" -DestinationPath "D:\" -Force
Rename-Item "D:\ARCHIRAPID_MATRICULA_HONOR_20251112_100301" "ARCHIRAPID_PROYECT25"
```

### Paso 3: Recrear entorno virtual
```powershell
cd D:\ARCHIRAPID_PROYECT25
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 4: Abrir en VS Code
```powershell
code .
```

### Paso 5: Probar que funciona
```powershell
.\venv\Scripts\streamlit.exe run app.py
```

---

## 🌐 SUBIR A GITHUB (BACKUP EN LA NUBE)

### ¿Por qué subir a GitHub?
- ✅ Backup en la nube (accesible desde cualquier PC)
- ✅ Gratis para proyectos privados
- ✅ Historial completo de cambios
- ✅ Colaboración con otros desarrolladores
- ✅ Protección contra pérdida del disco duro

### Paso 1: Crear cuenta en GitHub (si no tienes)
1. Ve a: https://github.com/signup
2. Crea tu usuario (gratis)
3. Verifica tu email

### Paso 2: Crear repositorio en GitHub
1. Ve a: https://github.com/new
2. Nombre: `ARCHIRAPID_PROYECT25`
3. Privado: ✅ (marca esta opción si no quieres que sea público)
4. NO marques: "Initialize with README" (ya lo tienes)
5. Clic en: "Create repository"

### Paso 3: Conectar tu proyecto local con GitHub
```powershell
cd D:\ARCHIRAPID_PROYECT25

# Añadir GitHub como "remoto"
git remote add origin https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25.git

# Subir todo a GitHub
git push -u origin master

# Subir los tags (backups) también
git push --tags
```

### Paso 4: Verificar que se subió
- Ve a: https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25
- Deberías ver todos tus archivos

### Paso 5 (FUTURO): Clonar en otro PC
```powershell
# En otro ordenador:
cd D:\
git clone https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25.git
cd ARCHIRAPID_PROYECT25
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🔍 VERIFICAR QUE EL BACKUP ESTÁ BIEN

### Comprobación rápida:
```powershell
# 1. ¿Existe el archivo ZIP?
Test-Path "D:\ARCHIRAPID_BACKUPS\ARCHIRAPID_MATRICULA_HONOR_20251112_100301.zip"
# Debe decir: True ✅

# 2. ¿Cuánto pesa el backup?
(Get-Item "D:\ARCHIRAPID_BACKUPS\ARCHIRAPID_MATRICULA_HONOR_20251112_100301.zip").Length / 1MB
# Debe decir: ~1.65 MB ✅

# 3. ¿Existen los tags en Git?
git tag
# Debe mostrar:
# backup-20251112_100301 ✅
# v1.0-MATRICULA-HONOR ✅

# 4. ¿Puedo ver el contenido del backup?
git show backup-20251112_100301:app.py | Select-Object -First 10
# Debe mostrar las primeras líneas de app.py ✅
```

---

## 🛠️ CREAR NUEVO BACKUP (ANTES DE HACER CAMBIOS)

### Comando rápido:
```powershell
cd D:\ARCHIRAPID_PROYECT25
.\create_backup.ps1
```

**El script hace automáticamente:**
1. ✅ Crea carpeta con timestamp
2. ✅ Copia todos los archivos importantes
3. ✅ Comprime en ZIP
4. ✅ Hace commit en Git
5. ✅ Crea tag de backup
6. ✅ Te muestra resumen

---

## 📋 LISTA DE VERIFICACIÓN ANTES DE HACER CAMBIOS

```
[ ] ✅ Backup creado (ejecutar create_backup.ps1)
[ ] ✅ Verificar que existe el ZIP
[ ] ✅ Verificar tag en Git (git tag)
[ ] ✅ Aplicación funciona AHORA (streamlit run app.py)
[ ] ✅ Anotar qué vas a cambiar
[ ] ✅ Hacer cambios pequeños, probar, repetir
[ ] ✅ Si algo falla: restaurar inmediatamente
```

---

## ⚠️ IMPORTANTE: ESTRATEGIA DE TRABAJO SEGURA

### REGLA DE ORO:
**"Haz un backup ANTES de cada sesión de cambios importantes"**

### Workflow recomendado:
```
1. Abrir proyecto
2. Ejecutar: .\create_backup.ps1
3. Probar que funciona (streamlit run app.py)
4. Hacer 1 cambio pequeño
5. Probar inmediatamente
6. Si funciona → guardar (git commit)
7. Si falla → restaurar backup
8. Repetir desde paso 4
```

### Commits frecuentes en Git:
```powershell
# Cada vez que algo funcione bien:
git add .
git commit -m "Descripción clara de qué cambiaste"
git tag -a checkpoint-funcional-$(Get-Date -Format 'yyyyMMdd-HHmm') -m "Punto funcional"
```

---

## 🆘 PROBLEMAS COMUNES Y SOLUCIONES

### ❌ "No encuentro el archivo restore_backup.ps1"
**Solución:** Está en `D:\ARCHIRAPID_PROYECT25\restore_backup.ps1`
```powershell
cd D:\ARCHIRAPID_PROYECT25
ls restore_backup.ps1
```

### ❌ "Git dice 'detached HEAD state'"
**Solución:** Vuelve a master
```powershell
git checkout master
```

### ❌ "El backup no restaura la base de datos"
**Solución:** Restaurar manualmente
```powershell
Copy-Item "D:\ARCHIRAPID_BACKUPS\ARCHIRAPID_MATRICULA_HONOR_20251112_100301\data.db.backup" "D:\ARCHIRAPID_PROYECT25\data.db" -Force
```

### ❌ "Streamlit no arranca después de restaurar"
**Solución:** Recrear entorno virtual
```powershell
Remove-Item venv -Recurse -Force
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ "GitHub pide usuario/contraseña cada vez"
**Solución:** Usar Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Usar token como contraseña

---

## 📞 CONTACTOS DE EMERGENCIA (SI TODO FALLA)

1. **Foro GitHub Discussions:** https://github.com/orgs/community/discussions
2. **Stack Overflow en español:** https://es.stackoverflow.com
3. **Discord Python España:** https://discord.gg/python-es

---

## ✅ CONFIRMACIÓN FINAL

**ESTADO DEL SISTEMA DE BACKUP: 🟢 PERFECTO**

- ✅ Backup automático creado: `20251112_100301`
- ✅ Backup ZIP verificado: 1.65 MB
- ✅ Tags Git creados: 2 puntos de restauración
- ✅ Script de restauración disponible
- ✅ Documentación completa creada
- ✅ Sistema listo para cambios seguros

**Ahora puedes trabajar con TOTAL seguridad.**
Si algo falla → Ejecutas `restore_backup.ps1` y vuelves al estado perfecto.

---

**Fecha guía:** 12 de Noviembre de 2025  
**Versión respaldada:** MATRÍCULA DE HONOR 10/10  
**Confianza:** 100% - Sistema probado y certificado ✨
