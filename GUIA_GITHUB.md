# 🚀 GUÍA RÁPIDA: SUBIR A GITHUB (Para principiantes)

## ¿POR QUÉ SUBIR A GITHUB?

✅ **Backup en la nube** → No pierdes nada si tu PC se rompe  
✅ **Acceso desde cualquier lugar** → Puedes trabajar desde otro ordenador  
✅ **Gratis** → GitHub es gratis para proyectos privados  
✅ **Portafolio** → Puedes mostrar tu trabajo a empresas  
✅ **Colaboración** → Puedes trabajar con otros desarrolladores  

---

## PASO 1: CREAR CUENTA EN GITHUB (5 minutos)

1. Ve a: **https://github.com/signup**
2. Introduce tu email
3. Crea una contraseña segura
4. Elige un nombre de usuario (por ejemplo: `tu-nombre-dev`)
5. Verifica que no eres un robot
6. Verifica tu email (revisa tu bandeja de entrada)

**¡LISTO!** Ya tienes cuenta en GitHub.

---

## PASO 2: CREAR REPOSITORIO EN GITHUB (2 minutos)

1. Una vez dentro de GitHub, clic en el **+** (arriba derecha)
2. Clic en **"New repository"**
3. Rellena:
   - **Repository name:** `ARCHIRAPID_PROYECT25`
   - **Description:** `Sistema MVP de gestión de fincas y arquitectos - Proyecto certificado 10/10`
   - **Privado o Público:**
     - ✅ **Private** (recomendado si no quieres que otros vean tu código)
     - ⭕ **Public** (si quieres compartirlo o usarlo como portafolio)
   - **NO marques** "Add a README file" (ya lo tienes)
4. Clic en **"Create repository"**

**¡LISTO!** Repositorio creado.

---

## PASO 3: CONECTAR TU PROYECTO CON GITHUB (3 minutos)

Copia los comandos que GitHub te muestra. Deberían ser similares a estos:

### En PowerShell (dentro de tu proyecto):

```powershell
cd D:\ARCHIRAPID_PROYECT25

# 1. Añadir GitHub como "remoto"
git remote add origin https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25.git

# 2. Verificar que se añadió correctamente
git remote -v

# 3. Subir tu código a GitHub
git push -u origin master

# 4. Subir también los tags (backups)
git push --tags
```

**IMPORTANTE:** Cambia `TU_USUARIO` por tu nombre de usuario real de GitHub.

---

## PASO 4: AUTENTICACIÓN (Primera vez)

Cuando hagas `git push`, GitHub te pedirá autenticación:

### Opción A: GitHub Desktop (MÁS FÁCIL)
1. Descarga: https://desktop.github.com/
2. Instala
3. Inicia sesión con tu cuenta
4. Ya no te pedirá contraseña nunca más

### Opción B: Personal Access Token (Para terminal)
1. Ve a: https://github.com/settings/tokens
2. Clic en **"Generate new token (classic)"**
3. Dale un nombre: `ARCHIRAPID_TOKEN`
4. Selecciona permisos: ✅ **repo** (marca todo en repo)
5. Clic en **"Generate token"**
6. **COPIA EL TOKEN** (solo lo verás una vez!)
7. Cuando Git te pida contraseña, pega el token

**Guarda el token** en un lugar seguro (puedes usar Notepad).

---

## PASO 5: VERIFICAR QUE SE SUBIÓ (1 minuto)

1. Ve a: `https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25`
2. Deberías ver:
   - ✅ Todos tus archivos (`app.py`, `src/`, `archirapid_extract/`, etc.)
   - ✅ Tu README.md
   - ✅ Commits (historial de cambios)
   - ✅ Tags (en la pestaña "Tags")

**¡ENHORABUENA!** Tu proyecto está en la nube.

---

## 🔄 WORKFLOW DIARIO (Cuando hagas cambios)

### Después de trabajar y probar que todo funciona:

```powershell
# 1. Ver qué archivos cambiaron
git status

# 2. Añadir todos los cambios
git add .

# 3. Guardar cambios con mensaje descriptivo
git commit -m "Arreglado filtro de búsqueda en mapa"

# 4. Subir a GitHub
git push
```

**¡LISTO!** Tus cambios están en GitHub.

---

## 📥 CLONAR EN OTRO ORDENADOR (Futuro)

Si necesitas trabajar desde otro PC:

```powershell
# 1. Instalar Git (si no lo tienes)
# Descarga: https://git-scm.com/download/win

# 2. Abrir PowerShell
cd D:\

# 3. Clonar el proyecto
git clone https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25.git

# 4. Entrar al proyecto
cd ARCHIRAPID_PROYECT25

# 5. Recrear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 6. Probar que funciona
.\venv\Scripts\streamlit.exe run app.py
```

**¡LISTO!** Trabajando desde otro PC.

---

## 🆘 PROBLEMAS COMUNES

### ❌ "remote origin already exists"
**Solución:**
```powershell
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25.git
```

### ❌ "Authentication failed"
**Solución:** Usa un Personal Access Token (ver Paso 4, Opción B)

### ❌ "fatal: refusing to merge unrelated histories"
**Solución:**
```powershell
git pull origin master --allow-unrelated-histories
```

### ❌ "Repository not found"
**Solución:** Verifica que el nombre del repositorio sea exactamente igual:
```powershell
git remote -v
# Debe mostrar: https://github.com/TU_USUARIO/ARCHIRAPID_PROYECT25.git
```

---

## 📊 RESUMEN DE COMANDOS IMPORTANTES

```powershell
# Ver estado
git status

# Guardar cambios localmente
git add .
git commit -m "mensaje"

# Subir a GitHub
git push

# Bajar cambios de GitHub
git pull

# Ver historial
git log --oneline

# Ver tags (backups)
git tag

# Crear tag
git tag -a v1.1 -m "Nueva versión"

# Subir tags
git push --tags

# Volver a un punto anterior
git checkout nombre-del-tag
```

---

## ✅ VENTAJAS DE USAR GITHUB

1. **Backup automático** → Cada `git push` guarda en la nube
2. **Historial completo** → Puedes ver qué cambiaste y cuándo
3. **Portafolio profesional** → Las empresas revisan GitHub al contratar
4. **Colaboración** → Otros pueden ayudarte (issues, pull requests)
5. **Integración** → Se conecta con VS Code, Streamlit Cloud, etc.
6. **Gratis ilimitado** → Para proyectos privados y públicos

---

## 🎯 SIGUIENTE PASO (OPCIONAL: Desplegar online)

Puedes hacer que tu aplicación sea accesible desde Internet (gratis):

### Streamlit Community Cloud:
1. Ve a: https://share.streamlit.io/
2. Conecta tu GitHub
3. Selecciona tu repositorio: `ARCHIRAPID_PROYECT25`
4. Archivo principal: `app.py`
5. Clic en "Deploy"

**En 5 minutos** tendrás tu app online con una URL tipo:
`https://tu-usuario-archirapid-proyect25.streamlit.app`

---

## 📞 RECURSOS ÚTILES

- **Documentación Git en español:** https://git-scm.com/book/es/v2
- **GitHub Guides:** https://guides.github.com/
- **VS Code + Git tutorial:** https://code.visualstudio.com/docs/sourcecontrol/overview
- **Foro GitHub Community:** https://github.community/

---

**¿QUIERES SUBIR A GITHUB AHORA?**  
Dime y te ayudo paso a paso en tiempo real. 🚀
