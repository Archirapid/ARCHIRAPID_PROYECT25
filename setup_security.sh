#!/bin/bash

# Script de configuración inicial de ARCHIRAPID
# Protege API keys y configura el entorno

echo "🔐 ARCHIRAPID - Configuración de Seguridad"
echo "=========================================="
echo ""

# 1. Verificar que .env no existe o está en .gitignore
if [ -f ".env" ]; then
    echo "⚠️  Archivo .env encontrado"
    
    # Verificar que está en .gitignore
    if git check-ignore .env > /dev/null 2>&1; then
        echo "✅ .env está protegido en .gitignore"
    else
        echo "❌ ERROR: .env NO está en .gitignore"
        echo "   Agregando .env al .gitignore..."
        echo ".env" >> .gitignore
        echo "✅ Protección añadida"
    fi
else
    echo "📝 Creando archivo .env desde plantilla..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Archivo .env creado"
        echo "⚠️  IMPORTANTE: Edita .env y agrega tus API keys reales"
    else
        echo "❌ ERROR: No se encuentra .env.example"
    fi
fi

echo ""
echo "🔍 Verificación de seguridad..."

# 2. Verificar que .env está en .gitignore
if grep -q "^\.env$" .gitignore; then
    echo "✅ .env está en .gitignore"
else
    if grep -q "\.env" .gitignore; then
        echo "✅ .env está protegido con patrón en .gitignore"
    else
        echo "⚠️  Agregando .env al .gitignore..."
        echo ".env" >> .gitignore
        echo "✅ Protección añadida"
    fi
fi

# 3. Verificar que .env no está en el historial de git
echo ""
echo "🔍 Verificando historial de git..."
if git log --all --full-history -- "*.env" 2>/dev/null | grep -q "commit"; then
    echo "❌ ADVERTENCIA: Se encontraron archivos .env en el historial"
    echo "   Contacta al administrador para limpiar el historial"
else
    echo "✅ No se encontraron .env en el historial"
fi

# 4. Verificar que no hay API keys hardcodeadas
echo ""
echo "🔍 Buscando API keys hardcodeadas en el código..."
if grep -r "AIzaSy\|gsk_" --include="*.py" . 2>/dev/null | grep -v ".env" | grep -v "#" > /dev/null; then
    echo "⚠️  ADVERTENCIA: Se encontraron posibles API keys en el código"
    echo "   Revisa los archivos y usa variables de entorno"
else
    echo "✅ No se encontraron API keys hardcodeadas"
fi

echo ""
echo "📦 Instalando dependencias..."
pip install python-dotenv >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ python-dotenv instalado"
else
    echo "⚠️  No se pudo instalar python-dotenv automáticamente"
    echo "   Ejecuta: pip install python-dotenv"
fi

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📖 Próximos pasos:"
echo "1. Edita el archivo .env con tus API keys reales"
echo "2. Nunca compartas o subas el archivo .env"
echo "3. Lee docs/SEGURIDAD_API_KEYS.md para más información"
echo ""
echo "🚀 Para iniciar la aplicación:"
echo "   streamlit run app.py"
echo ""
