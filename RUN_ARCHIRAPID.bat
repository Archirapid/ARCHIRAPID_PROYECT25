@echo off
cd /d C:\ARCHIRAPID_PROYECT25

echo ================================
echo Lanzando backend (FastAPI/Uvicorn)...
start cmd /k "uvicorn main:app --reload --port 8000"

echo Lanzando frontend (Streamlit)...
start cmd /k "streamlit run app.py"

echo Esperando 5 segundos para validacion...
timeout /t 5 >nul

echo Validando servicios...
powershell -ExecutionPolicy Bypass -File validate_services.ps1

echo ================================
echo ARCHIRAPID arrancado correctamente.
pause