# 🚀 Guía de Deployment ARCHIRAPID

## ✅ Estado Actual del Sistema

### Local (100% Funcional)
- ✅ Pipeline completo operativo
- ✅ Tiempo de ejecución: ~12 segundos
- ✅ Tesseract OCR: 5.5.0 instalado
- ✅ Todas las dependencias verificadas

### GitHub
- 📦 Repositorio: https://github.com/Archirapid/ARCHIRAPID_PROYECT25
- 🏷️ Tag actual: **v1.3-DXF-EXPORT**
- 📝 Último commit: `4f2dced` - DXF export integrado + Tesseract Linux
- ✅ **CÓDIGO SUBIDO EXITOSAMENTE** (13 Nov 2025)

## 🌐 Deployment en Streamlit Cloud

### Paso 1: Acceder a Streamlit Cloud
1. Ve a: **https://share.streamlit.io/**
2. Inicia sesión con tu cuenta de GitHub
3. Verás tu app: **ARCHIRAPID_PROYECT25**

### Paso 2: Actualizar la App
1. Haz clic en los **3 puntos** (⋮) junto a tu app
2. Selecciona **"Reboot app"**
3. Streamlit Cloud descargará los últimos cambios de GitHub
4. La app se reiniciará automáticamente (~2-3 minutos)

### Paso 3: Verificar Deployment
- La URL de tu app será algo como:
  ```
  https://archirapid-archirapid-proyect25-app-XXXXX.streamlit.app
  ```
- Copia esta URL y podrás acceder desde **cualquier dispositivo** (PC, móvil, tablet)

## 📱 Acceso desde Cualquier Lugar

### Desde tu PC
- Abre el navegador
- Ve a la URL de Streamlit Cloud
- ✅ Todo funciona sin instalar nada

### Desde tu Móvil/Tablet
- Abre el navegador (Chrome, Safari, etc.)
- Ve a la misma URL
- ✅ La app es responsive y funciona en móvil

### Compartir con Clientes
- Envía la URL por email/WhatsApp
- Los clientes pueden ver la app sin registro
- ✅ No necesitan instalar nada

## ⚙️ Características en Streamlit Cloud

### ✅ Lo que FUNCIONA en Cloud:
1. **Mapa interactivo** con parcelas
2. **Gestión de proyectos** y arquitectos
3. **Subida y descarga** de PDFs
4. **Base de datos** SQLite
5. **Visualización** de datos
6. **Pipeline OCR** completo (con packages.txt)

### 🔧 Instalación Automática:
Streamlit Cloud instalará automáticamente:
- Python 3.10
- Todas las librerías en `requirements.txt`
- Tesseract OCR (via `packages.txt`)
- Dependencias del sistema

## 📋 Archivos Clave para Cloud

### `requirements.txt`
```
streamlit>=1.23.1
folium>=0.14.0
streamlit-folium>=0.12.0
PyMuPDF>=1.23.0
opencv-python-headless>=4.8.0
pytesseract>=0.3.10
shapely>=2.0.0
matplotlib>=3.7.0
```

### `packages.txt` (NUEVO)
```
tesseract-ocr
tesseract-ocr-spa
```
Este archivo indica a Streamlit Cloud que instale Tesseract OCR.

## 🐛 Troubleshooting

### Si la app no arranca:
1. Ve a **Manage app** → **Logs**
2. Busca errores en rojo
3. Verifica que `packages.txt` esté en el repositorio

### Si Tesseract falla en Cloud:
- Verifica que `packages.txt` existe
- Comprueba los logs de instalación
- Streamlit Cloud instalará Tesseract 4.x (compatible)

### Si el pipeline es lento:
- Streamlit Cloud usa máquinas compartidas
- El pipeline puede tardar 20-30 segundos (vs 12s local)
- Es normal, la infraestructura es más limitada

## 🔒 Seguridad y Límites

### Streamlit Cloud (Plan Gratuito):
- ✅ **Recursos**: 1 GB RAM, CPU compartida
- ✅ **Uptime**: La app "duerme" tras 7 días sin uso
- ✅ **Despertado**: Automático al visitar la URL
- ✅ **Privacidad**: Puedes hacer la app privada en configuración

### Recomendaciones:
- Mantén archivos pequeños (<100 MB)
- No subas datos sensibles al repositorio público
- Usa `.gitignore` para excluir backups

## 📊 Monitoreo

### Ver estadísticas de uso:
1. Streamlit Cloud → Dashboard
2. Ver métricas de visitas
3. Revisar logs de errores

### Logs en tiempo real:
```
Manage app → Logs → View app logs
```

## 🎯 Próximos Pasos

### Mejoras Futuras:
1. **Autenticación** de usuarios (para gating de DXF/PDF)
2. **Pago integrado** (Stripe/PayPal) para descargas premium
3. **Base de datos** PostgreSQL en cloud
4. **Storage** externo (AWS S3, Google Cloud)
5. **API REST** para integraciones con BIM/CAD
6. **Export** a DWG/IFC para gemelos digitales

## 🎉 NUEVAS FUNCIONALIDADES (v1.3-DXF-EXPORT)

### ✅ Export DXF Integrado:
- Descarga directa desde la app después del análisis
- Formato compatible con AutoCAD, Revit, ArchiCAD
- Escala configurable (default: 0.1)
- Layers organizados: PARCELA_CATASTRAL
- Metadatos incluidos: Ref. catastral, superficie

### 🔧 Cómo Usar:
1. Sube PDF catastral en "Ver detalles"
2. Click "Analizar Documento"
3. Espera resultados (10-30 segundos)
4. Scroll hasta "📥 Descargar DXF"
5. Click "Descargar DXF para CAD/BIM"
6. Archivo descarga como: `ARCHIRAPID_{referencia_catastral}.dxf`

---

**Versión del sistema**: v1.3-DXF-EXPORT  
**Última actualización**: 2025-11-13  
**Estado**: ✅ CÓDIGO EN GITHUB - LISTO PARA DEPLOY CLOUD
