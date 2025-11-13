# 🔧 SOLUCIÓN: Git Credential Manager Bloqueado

## ❌ Problema
La ventana de autenticación de Git se queda bloqueada y no responde.

## ✅ Solución Profesional (Personal Access Token)

### Paso 1: Crear Token en GitHub
1. Abre tu navegador y ve a: https://github.com/settings/tokens
2. Click en **"Generate new token (classic)"**
3. Nombre: `ARCHIRAPID_LOCAL`
4. Selecciona permisos:
   - ✅ **repo** (todos los sub-items)
   - ✅ **workflow**
5. Click **"Generate token"**
6. **COPIA EL TOKEN** (ej: `ghp_xxxxxxxxxxxxxxxxxxxx`)
   - Solo se muestra UNA VEZ
   - Guárdalo en un lugar seguro

### Paso 2: Configurar Git (en PowerShell)

```powershell
# Cambiar a autenticación básica
git config --global credential.helper store

# Verificar configuración
git config --global --list | Select-String credential
```

### Paso 3: Hacer Push con Token

```powershell
# Hacer push (te pedirá credenciales UNA VEZ)
git push origin main

# Cuando te pida:
# Username for 'https://github.com': Archirapid
# Password for 'https://Archirapid@github.com': [PEGA TU TOKEN AQUÍ]
```

### Paso 4: Verificar que funcionó

```powershell
# Ver archivos pendientes
git status

# Debería mostrar: "Your branch is up to date with 'origin/main'"
```

---

## 🚨 Si Sigue Sin Funcionar - Plan B

### Deshabilitar Git Credential Manager completamente:

```powershell
# Deshabilitar credential manager
git config --global --unset credential.helper

# Configurar store básico
git config --global credential.helper store

# Reintentar push
git push origin main
```

---

## 📋 Estado Actual del Repositorio

```
✅ Commit local creado: "feat: DXF export integrated..."
✅ Tag creado: v1.3-DXF-EXPORT
❌ Push pendiente: NO subido a GitHub aún
```

### Archivos que se subirán:
- ✅ `app.py` (integración DXF)
- ✅ `requirements.txt` (ezdxf añadido)
- ✅ `archirapid_extract/export_dxf.py` (nuevo módulo)
- ✅ `RESTORE_POINT_DXF.md` (documentación)
- ✅ `.gitignore` (excluir *.dxf)

---

## 🎯 Siguiente Paso Después del Push

Una vez que `git push origin main` funcione:

1. **Ir a tu repo en GitHub**: https://github.com/Archirapid/ARCHIRAPID_PROYECT25
2. **Verificar** que aparezca el tag `v1.3-DXF-EXPORT`
3. **Continuar** con el despliegue en Streamlit Cloud

---

## 💡 Notas Importantes

- El token es como una contraseña de un solo uso
- Una vez guardado con `credential.helper store`, queda en:
  - Windows: `%USERPROFILE%\.git-credentials`
  - Es un archivo de texto plano, mantén seguro tu PC
- **NUNCA** compartas el token en capturas o código

---

## 🆘 Si Nada Funciona

```powershell
# Última opción: usar SSH en lugar de HTTPS
# (Requiere generar claves SSH)
# Ver: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```
