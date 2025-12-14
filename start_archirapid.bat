@echo off

echo ================================
echo Lanzando backend (FastAPI/Uvicorn)...
cd /d C:\ARCHIRAPID_PROYECT25\backend
start cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Lanzando frontend (Streamlit)...
cd /d C:\ARCHIRAPID_PROYECT25
start cmd /k "streamlit run app.py"

echo Esperando 5 segundos para validacion...
timeout /t 5 >nul

echo Validando servicios...
powershell -ExecutionPolicy Bypass -File C:\ARCHIRAPID_PROYECT25\validate_services.ps1

echo ================================
echo ARCHIRAPID arrancado correctamente.
pause

