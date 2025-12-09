@echo off
cd /d D:\ARCHIRAPID_PROYECT25
call venv\Scripts\activate.bat
streamlit run app.py --server.port 8503
pause