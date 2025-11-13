@echo off
echo.
echo ========================================
echo   ABRIR GITHUB - CREAR TOKEN
echo ========================================
echo.
echo 1. Se abrira GitHub en tu navegador
echo 2. Inicia sesion si no lo estas
echo 3. Sigue las instrucciones en pantalla
echo.
pause
start https://github.com/settings/tokens/new?description=ARCHIRAPID_LOCAL^&scopes=repo,workflow
echo.
echo ========================================
echo   INSTRUCCIONES:
echo ========================================
echo.
echo 1. Nombre del token: ARCHIRAPID_LOCAL
echo 2. Expiration: 90 days (o mas)
echo 3. Permisos: repo, workflow (ya preseleccionados)
echo 4. Click "Generate token"
echo 5. COPIAR EL TOKEN (solo se muestra 1 vez)
echo 6. Volver a VS Code
echo.
echo Presiona cualquier tecla cuando tengas el token copiado...
pause
