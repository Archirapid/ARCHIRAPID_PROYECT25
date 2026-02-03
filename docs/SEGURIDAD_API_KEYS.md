# 🔐 Guía de Seguridad - Protección de API Keys

## ⚠️ IMPORTANTE: Nunca subas API Keys a Git

Este proyecto usa **Google Gemini** y **Groq AI** APIs. Las API keys son confidenciales y NUNCA deben subirse al repositorio.

## 📋 Configuración Inicial

### 1. Crear archivo .env

```bash
cp .env.example .env
```

### 2. Agregar tus API Keys

Edita el archivo `.env` con tus claves reales:

```bash
# Google Gemini AI API Key
GEMINI_API_KEY=AIzaSy...tu_clave_real_aqui

# Groq AI API Key  
GROQ_API_KEY=gsk_...tu_clave_real_aqui
```

### 3. Verificar protección

El archivo `.gitignore` ya está configurado para **NO** incluir:
- `.env`
- `.env.local`
- `.env.*.local`
- `*.env`

## 🔍 Cómo obtener las API Keys

### Google Gemini API Key
1. Visita: https://makersuite.google.com/app/apikey
2. Inicia sesión con tu cuenta Google
3. Crea o copia tu API key
4. Pégala en tu archivo `.env`

### Groq AI API Key
1. Visita: https://console.groq.com/keys
2. Crea una cuenta o inicia sesión
3. Genera una nueva API key
4. Pégala en tu archivo `.env`

## ✅ Verificación de Seguridad

Para verificar que tus claves NO están en git:

```bash
# Ver archivos ignorados
git status --ignored

# Verificar que .env está en .gitignore
git check-ignore .env
# Debería mostrar: .env

# Buscar API keys en el historial (NO debería encontrar nada)
git log --all --full-history -- "*.env"
```

## 🚨 Si accidentalmente subiste una API key

1. **Revoca inmediatamente la clave comprometida**
   - Gemini: https://makersuite.google.com/app/apikey
   - Groq: https://console.groq.com/keys

2. **Genera una nueva clave**

3. **Elimina la clave del historial de Git** (contacta al administrador)

## 📖 Uso en el código

Las API keys se cargan automáticamente desde el archivo `.env`:

```python
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Usar las API keys
gemini_key = os.getenv('GEMINI_API_KEY')
groq_key = os.getenv('GROQ_API_KEY')
```

## 🛡️ Mejores Prácticas

1. ✅ **SIEMPRE** usa archivo `.env` para claves secretas
2. ✅ **NUNCA** hardcodees API keys en el código
3. ✅ **VERIFICA** que `.env` está en `.gitignore`
4. ✅ **USA** `.env.example` como plantilla (sin valores reales)
5. ✅ **REVOCA** inmediatamente claves comprometidas
6. ✅ **ROTA** las claves periódicamente

## 📞 Soporte

Si tienes dudas sobre la configuración de seguridad:
- 📧 Email: moskovia@me.com
- 📱 Teléfono: +34 623 172 704

---

**Última actualización:** 2026-02-03  
**Versión:** DIA 3 DISEÑO IA - Protección completa de API keys
