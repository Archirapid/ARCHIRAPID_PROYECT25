# 🚀 ARCHIRAPID Deployment Guide# 🚀 Guía de Deployment ARCHIRAPID

**Version:** 1.0-stable-observability  

**Last Updated:** 2025-11-15  ## ✅ Estado Actual del Sistema

**Target Environment:** Production Windows Server / Azure App Service

### Local (100% Funcional)

---- ✅ Pipeline completo operativo

- ✅ Tiempo de ejecución: ~12 segundos

## 📋 Table of Contents- ✅ Tesseract OCR: 5.5.0 instalado

- ✅ Todas las dependencias verificadas

1. [Pre-Deployment Checklist](#pre-deployment-checklist)

2. [Environment Setup](#environment-setup)### GitHub

3. [Database Configuration](#database-configuration)- 📦 Repositorio: https://github.com/Archirapid/ARCHIRAPID_PROYECT25

4. [Application Deployment](#application-deployment)- 🏷️ Tag actual: **v1.3-DXF-EXPORT**

5. [Health Monitoring Setup](#health-monitoring-setup)- 📝 Último commit: `4f2dced` - DXF export integrado + Tesseract Linux

6. [Security Hardening](#security-hardening)- ✅ **CÓDIGO SUBIDO EXITOSAMENTE** (13 Nov 2025)

7. [Post-Deployment Validation](#post-deployment-validation)

8. [Rollback Procedures](#rollback-procedures)## 🌐 Deployment en Streamlit Cloud

9. [Troubleshooting](#troubleshooting)

### Paso 1: Acceder a Streamlit Cloud

---1. Ve a: **https://share.streamlit.io/**

2. Inicia sesión con tu cuenta de GitHub

## 🎯 Pre-Deployment Checklist3. Verás tu app: **ARCHIRAPID_PROYECT25**



### Infrastructure Requirements### Paso 2: Actualizar la App

- [ ] **OS:** Windows Server 2019+ or Linux (Ubuntu 20.04+)1. Haz clic en los **3 puntos** (⋮) junto a tu app

- [ ] **Python:** 3.10 or higher2. Selecciona **"Reboot app"**

- [ ] **RAM:** Minimum 4GB, recommended 8GB3. Streamlit Cloud descargará los últimos cambios de GitHub

- [ ] **Disk:** 20GB+ free space (10GB for app, 10GB for logs/backups)4. La app se reiniciará automáticamente (~2-3 minutos)

- [ ] **Network:** Port 8501 (Streamlit default) or custom port configured

### Paso 3: Verificar Deployment

### Software Dependencies- La URL de tu app será algo como:

- [ ] **PostgreSQL:** 13+ installed and running  ```

- [ ] **Git:** For version control (optional but recommended)  https://archirapid-archirapid-proyect25-app-XXXXX.streamlit.app

- [ ] **FFmpeg:** For video processing (required by `moviepy`)  ```

- [ ] **Poppler:** For PDF processing (required by `pdf2image`)- Copia esta URL y podrás acceder desde **cualquier dispositivo** (PC, móvil, tablet)

- [ ] **Ghostscript:** For PDF manipulation

## 📱 Acceso desde Cualquier Lugar

### Security Preparation

- [ ] Database credentials secured (use environment variables)### Desde tu PC

- [ ] Firewall rules configured (allow only necessary ports)- Abre el navegador

- [ ] SSL/TLS certificates ready (if using HTTPS)- Ve a la URL de Streamlit Cloud

- [ ] Backup strategy defined and tested- ✅ Todo funciona sin instalar nada



---### Desde tu Móvil/Tablet

- Abre el navegador (Chrome, Safari, etc.)

## 🛠️ Environment Setup- Ve a la misma URL

- ✅ La app es responsive y funciona en móvil

### 1. Clone Repository

```powershell### Compartir con Clientes

# PowerShell- Envía la URL por email/WhatsApp

cd D:\- Los clientes pueden ver la app sin registro

git clone https://github.com/Archirapid/ARCHIRAPID_PROYECT25.git- ✅ No necesitan instalar nada

cd ARCHIRAPID_PROYECT25

## ⚙️ Características en Streamlit Cloud

# Checkout stable release

git checkout v1.0-stable-observability### ✅ Lo que FUNCIONA en Cloud:

```1. **Mapa interactivo** con parcelas

2. **Gestión de proyectos** y arquitectos

### 2. Create Virtual Environment3. **Subida y descarga** de PDFs

```powershell4. **Base de datos** SQLite

# Create venv5. **Visualización** de datos

python -m venv venv6. **Pipeline OCR** completo (con packages.txt)



# Activate venv### 🔧 Instalación Automática:

.\venv\Scripts\Activate.ps1Streamlit Cloud instalará automáticamente:

- Python 3.10

# Verify Python version- Todas las librerías en `requirements.txt`

python --version  # Should be 3.10+- Tesseract OCR (via `packages.txt`)

```- Dependencias del sistema



### 3. Install System Dependencies## 📋 Archivos Clave para Cloud



#### Windows### `requirements.txt`

```powershell```

# Install Chocolatey (if not already installed)streamlit>=1.23.1

Set-ExecutionPolicy Bypass -Scope Process -Forcefolium>=0.14.0

[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072streamlit-folium>=0.12.0

iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))PyMuPDF>=1.23.0

opencv-python-headless>=4.8.0

# Install dependenciespytesseract>=0.3.10

choco install ffmpeg poppler ghostscript -yshapely>=2.0.0

matplotlib>=3.7.0

# Verify installations```

ffmpeg -version

pdfinfo -v### `packages.txt` (NUEVO)

gs -version```

```tesseract-ocr

tesseract-ocr-spa

#### Linux (Ubuntu)```

```bashEste archivo indica a Streamlit Cloud que instale Tesseract OCR.

sudo apt update

sudo apt install -y ffmpeg poppler-utils ghostscript## 🐛 Troubleshooting

```

### Si la app no arranca:

### 4. Install Python Packages1. Ve a **Manage app** → **Logs**

```powershell2. Busca errores en rojo

# Upgrade pip3. Verifica que `packages.txt` esté en el repositorio

python -m pip install --upgrade pip setuptools wheel

### Si Tesseract falla en Cloud:

# Install requirements- Verifica que `packages.txt` existe

pip install -r requirements.txt- Comprueba los logs de instalación

- Streamlit Cloud instalará Tesseract 4.x (compatible)

# Verify critical packages

python -c "import streamlit; print(f'Streamlit: {streamlit.__version__}')"### Si el pipeline es lento:

python -c "import psycopg2; print('PostgreSQL driver: OK')"- Streamlit Cloud usa máquinas compartidas

python -c "import magic; print('python-magic-bin: OK')"- El pipeline puede tardar 20-30 segundos (vs 12s local)

```- Es normal, la infraestructura es más limitada



---## 🔒 Seguridad y Límites



## 🗄️ Database Configuration### Streamlit Cloud (Plan Gratuito):

- ✅ **Recursos**: 1 GB RAM, CPU compartida

### 1. Create Production Database- ✅ **Uptime**: La app "duerme" tras 7 días sin uso

```sql- ✅ **Despertado**: Automático al visitar la URL

-- Connect to PostgreSQL as admin- ✅ **Privacidad**: Puedes hacer la app privada en configuración

psql -U postgres

### Recomendaciones:

-- Create database- Mantén archivos pequeños (<100 MB)

CREATE DATABASE archirapid_prod;- No subas datos sensibles al repositorio público

- Usa `.gitignore` para excluir backups

-- Create user with strong password

CREATE USER archirapid_user WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';## 📊 Monitoreo



-- Grant privileges### Ver estadísticas de uso:

GRANT ALL PRIVILEGES ON DATABASE archirapid_prod TO archirapid_user;1. Streamlit Cloud → Dashboard

2. Ver métricas de visitas

-- Connect to new database3. Revisar logs de errores

\c archirapid_prod

### Logs en tiempo real:

-- Grant schema privileges```

GRANT ALL ON SCHEMA public TO archirapid_user;Manage app → Logs → View app logs

``````



### 2. Configure Environment Variables## 🎯 Próximos Pasos

Create `.env` file in project root (NEVER commit this file):

### Mejoras Futuras:

```ini1. **Autenticación** de usuarios (para gating de DXF/PDF)

# Database Configuration2. **Pago integrado** (Stripe/PayPal) para descargas premium

DB_HOST=localhost3. **Base de datos** PostgreSQL en cloud

DB_PORT=54324. **Storage** externo (AWS S3, Google Cloud)

DB_NAME=archirapid_prod5. **API REST** para integraciones con BIM/CAD

DB_USER=archirapid_user6. **Export** a DWG/IFC para gemelos digitales

DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE

## 🎉 NUEVAS FUNCIONALIDADES (v1.3-DXF-EXPORT)

# Application Settings

STREAMLIT_SERVER_PORT=8501### ✅ Export DXF Integrado:

STREAMLIT_SERVER_ADDRESS=0.0.0.0- Descarga directa desde la app después del análisis

STREAMLIT_SERVER_HEADLESS=true- Formato compatible con AutoCAD, Revit, ArchiCAD

STREAMLIT_BROWSER_GATHER_USAGE_STATS=false- Escala configurable (default: 0.1)

- Layers organizados: PARCELA_CATASTRAL

# File Upload Settings- Metadatos incluidos: Ref. catastral, superficie

MAX_IMAGE_SIZE_MB=5

MAX_PDF_SIZE_MB=10### 🔧 Cómo Usar:

1. Sube PDF catastral en "Ver detalles"

# Logging2. Click "Analizar Documento"

LOG_LEVEL=INFO3. Espera resultados (10-30 segundos)

LOG_RETENTION_DAYS=304. Scroll hasta "📥 Descargar DXF"

```5. Click "Descargar DXF para CAD/BIM"

6. Archivo descarga como: `ARCHIRAPID_{referencia_catastral}.dxf`

### 3. Initialize Database Schema

```powershell---

# Run migrations (if using Alembic)

# Or manually create schema from app.py initialization**Versión del sistema**: v1.3-DXF-EXPORT  

**Última actualización**: 2025-11-13  

# Test database connection**Estado**: ✅ CÓDIGO EN GITHUB - LISTO PARA DEPLOY CLOUD

python -c "from src.database import get_db_connection; conn = get_db_connection(); print('DB Connection: OK'); conn.close()"
```

---

## 📦 Application Deployment

### Method 1: Direct Streamlit (Development/Testing)
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run app
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Method 2: Windows Service (Production)

#### Create Service Wrapper Script (`run_service.ps1`)
```powershell
# run_service.ps1
$ErrorActionPreference = "Stop"
$VENV_PYTHON = "D:\ARCHIRAPID_PROYECT25\venv\Scripts\python.exe"
$APP_PATH = "D:\ARCHIRAPID_PROYECT25\app.py"

# Log startup
Add-Content -Path "D:\ARCHIRAPID_PROYECT25\logs\service.log" -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Service starting..."

# Run Streamlit
& $VENV_PYTHON -m streamlit run $APP_PATH --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

#### Install NSSM (Non-Sucking Service Manager)
```powershell
choco install nssm -y

# Create Windows Service
nssm install ARCHIRAPID "D:\ARCHIRAPID_PROYECT25\venv\Scripts\python.exe" "-m streamlit run D:\ARCHIRAPID_PROYECT25\app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"

# Configure service
nssm set ARCHIRAPID AppDirectory "D:\ARCHIRAPID_PROYECT25"
nssm set ARCHIRAPID DisplayName "ARCHIRAPID Application"
nssm set ARCHIRAPID Description "ARCHIRAPID Streamlit Application"
nssm set ARCHIRAPID Start SERVICE_AUTO_START

# Start service
nssm start ARCHIRAPID

# Check status
nssm status ARCHIRAPID
```

### Method 3: Azure App Service

#### Prepare `startup.sh` (for Linux App Service)
```bash
#!/bin/bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true --server.enableCORS false
```

#### Azure CLI Deployment
```bash
# Login to Azure
az login

# Create resource group
az group create --name archirapid-rg --location westeurope

# Create App Service plan
az appservice plan create --name archirapid-plan --resource-group archirapid-rg --sku B2 --is-linux

# Create web app
az webapp create --resource-group archirapid-rg --plan archirapid-plan --name archirapid-app --runtime "PYTHON:3.10"

# Configure startup command
az webapp config set --resource-group archirapid-rg --name archirapid-app --startup-file "startup.sh"

# Deploy code
az webapp up --resource-group archirapid-rg --name archirapid-app --runtime "PYTHON:3.10"
```

---

## 🏥 Health Monitoring Setup

### 1. Configure Health Check Endpoint
The `health.py` script provides system diagnostics:

```powershell
# Manual health check
python health.py

# Expected output (JSON):
{
  "status": "healthy",
  "timestamp": "2025-11-15T21:15:00",
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 67.8,
    "disk_free_gb": 125.4
  },
  "database": {
    "connected": true,
    "response_time_ms": 12
  },
  "logs": {
    "recent_errors": 0,
    "recent_warnings": 2
  }
}
```

### 2. Setup Automated Monitoring (Windows Task Scheduler)

#### Create Monitoring Script (`monitor_health.ps1`)
```powershell
# monitor_health.ps1
$HEALTH_SCRIPT = "D:\ARCHIRAPID_PROYECT25\health.py"
$PYTHON_EXE = "D:\ARCHIRAPID_PROYECT25\venv\Scripts\python.exe"
$LOG_FILE = "D:\ARCHIRAPID_PROYECT25\logs\health_monitor.log"

$result = & $PYTHON_EXE $HEALTH_SCRIPT | ConvertFrom-Json

if ($result.status -ne "healthy") {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $message = "$timestamp - ALERT: System unhealthy - $($result | ConvertTo-Json -Compress)"
    Add-Content -Path $LOG_FILE -Value $message
    
    # Send email alert (configure SMTP settings)
    # Send-MailMessage -To "admin@archirapid.com" -Subject "ARCHIRAPID Health Alert" -Body $message
}
```

#### Schedule Task
```powershell
# Create scheduled task to run every 5 minutes
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File D:\ARCHIRAPID_PROYECT25\monitor_health.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "ARCHIRAPID_Health_Monitor" -Action $action -Trigger $trigger -Principal $principal -Description "Monitors ARCHIRAPID application health"
```

### 3. In-App Diagnostics Panel
The sidebar diagnostics panel is enabled by default in `app.py` (lines ~990-1050):
- System metrics (CPU, RAM, Disk)
- Database status
- Recent log events
- File validation statistics

Access via Streamlit sidebar under **"🔧 Sistema"** expander.

---

## 🔒 Security Hardening

### 1. File Upload Security
Already implemented in `app.py`:
- **MIME type validation** (python-magic-bin)
- **Size limits** (5MB images, 10MB PDFs)
- **Allowed extensions** (png, jpg, jpeg, pdf, dxf)

Verify configuration in `src/utils.py`:
```python
# Default limits (can override via .env)
MAX_IMAGE_SIZE_MB = int(os.getenv('MAX_IMAGE_SIZE_MB', 5))
MAX_PDF_SIZE_MB = int(os.getenv('MAX_PDF_SIZE_MB', 10))
```

### 2. Database Security
```sql
-- Revoke unnecessary privileges
REVOKE ALL ON DATABASE archirapid_prod FROM PUBLIC;

-- Enable row-level security (RLS) for sensitive tables
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Create policy (example: users can only see their own data)
CREATE POLICY client_isolation ON clients
    USING (user_id = current_user);
```

### 3. Network Security
```powershell
# Windows Firewall - Allow only specific port
New-NetFirewallRule -DisplayName "ARCHIRAPID App" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow

# Deny all other inbound traffic
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block
```

### 4. Application Security Headers
Add to `.streamlit/config.toml`:
```toml
[server]
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 10

[browser]
gatherUsageStats = false
```

### 5. Logging Security
Already implemented:
- **Email/NIF masking** in logs (src/logger.py)
- **No sensitive data** in JSON logs
- **Correlation IDs** for audit trails

Verify with:
```powershell
# Check recent logs for sensitive data
Get-Content logs\payment_flow.log -Tail 50 | Select-String -Pattern "@|[0-9]{8}[A-Z]"
# Should return 0 matches (data is masked)
```

---

## ✅ Post-Deployment Validation

### 1. Smoke Tests
```powershell
# Test 1: App starts
Start-Process "http://localhost:8501"

# Test 2: Database connection
python -c "from src.database import get_db_connection; conn = get_db_connection(); print('✅ DB Connection OK'); conn.close()"

# Test 3: Health endpoint
python health.py | ConvertFrom-Json | Select-Object status
# Expected: "healthy"
```

### 2. Functional Tests
```powershell
# Run full test suite
pytest tests/ -v --cov=src --cov-report=html

# Expected: 44 passed in ~18s
# Coverage: payment_flow 86%, overall 70%+
```

### 3. Load Testing (Optional)
```powershell
# Install Locust
pip install locust

# Create locustfile.py
@task
def test_home_page(self):
    self.client.get("/")

# Run load test
locust -f locustfile.py --host=http://localhost:8501 --users 50 --spawn-rate 5
```

### 4. Monitoring Validation
```powershell
# Check logs directory
Get-ChildItem logs\ | Format-Table Name, Length, LastWriteTime

# Verify log rotation
Get-Content logs\payment_flow.log | Measure-Object -Line
# Should be < 10000 lines if rotation is working

# Test health script
python health.py | ConvertFrom-Json | Format-List
```

---

## 🔄 Rollback Procedures

### Emergency Rollback (Immediate)
```powershell
# Stop application
nssm stop ARCHIRAPID

# Restore last stable backup
Copy-Item "backups\full_backup_20251115_211208\*" -Destination "." -Recurse -Force

# Restart application
nssm start ARCHIRAPID

# Verify status
nssm status ARCHIRAPID
```

### Git-Based Rollback
```powershell
# View available tags
git tag -l

# Rollback to previous stable version
git checkout v0.9-stable-20251115

# Reinstall dependencies (in case requirements changed)
pip install -r requirements.txt --force-reinstall

# Restart app
nssm restart ARCHIRAPID
```

### Database Rollback
```sql
-- If database changes were made, restore from backup
psql -U postgres -d archirapid_prod < backups/db_backup_20251115.sql
```

---

## 🐛 Troubleshooting

### Issue: App Won't Start

#### Symptom
```
ModuleNotFoundError: No module named 'streamlit'
```

#### Solution
```powershell
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt --upgrade
```

---

### Issue: Database Connection Fails

#### Symptom
```
psycopg2.OperationalError: could not connect to server
```

#### Solutions
```powershell
# 1. Verify PostgreSQL is running
Get-Service -Name postgresql*

# 2. Test connection manually
psql -U archirapid_user -d archirapid_prod -h localhost

# 3. Check firewall (if remote DB)
Test-NetConnection -ComputerName db.server.com -Port 5432

# 4. Verify credentials in .env
Get-Content .env | Select-String "DB_"
```

---

### Issue: High Memory Usage

#### Symptom
```
System memory > 90%
```

#### Diagnostics
```powershell
# Run health check
python health.py | ConvertFrom-Json | Select-Object -ExpandProperty system

# Check Streamlit processes
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Format-Table ProcessName, WS -AutoSize
```

#### Solutions
1. **Restart app** (clears memory leaks)
2. **Increase server RAM** (minimum 8GB recommended)
3. **Enable log rotation** (prevent huge log files)
4. **Optimize queries** (add indexes to frequently queried columns)

---

### Issue: File Upload Fails

#### Symptom
```
ValidationError: File type not allowed
```

#### Diagnostics
```powershell
# Check MIME detection
python -c "import magic; print(magic.from_file('path/to/file', mime=True))"

# Verify python-magic-bin is installed
pip show python-magic-bin
```

#### Solutions
```powershell
# Reinstall python-magic-bin
pip uninstall python-magic-bin -y
pip install python-magic-bin

# If still fails, check file extension whitelist in app.py
Get-Content app.py | Select-String "allowed_extensions"
```

---

### Issue: Slow PDF Processing

#### Symptom
PDF extraction takes > 60 seconds

#### Diagnostics
```powershell
# Check Poppler installation
pdfinfo -v

# Check Ghostscript
gs -version
```

#### Solutions
1. **Optimize PDFs** before upload (reduce resolution)
2. **Increase timeout** in `archirapid_extract/extract_pdf.py`
3. **Use faster OCR engine** (Tesseract Fast mode)

---

## 📞 Support & Maintenance

### Log Locations
- **Application:** `logs/payment_flow.log`
- **Errors:** `logs/error.log`
- **System:** `logs/system.log`

### Backup Schedule
- **Daily:** Full app backup (automated via Task Scheduler)
- **Weekly:** Database dump
- **Monthly:** Archive old backups (retention: 3 months)

### Version History
- `v1.0-stable-observability` (2025-11-15): Production release with health monitoring
- `v0.9-stable-20251115` (2025-11-15): Pre-release with payment flow fixes

### Contact
For critical issues: admin@archirapid.com  
Documentation: [GitHub Wiki](https://github.com/Archirapid/ARCHIRAPID_PROYECT25/wiki)

---

## 📚 Additional Resources

- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/security.html)
- [Python Magic Documentation](https://github.com/ahupp/python-magic)
- [NSSM Documentation](https://nssm.cc/usage)

---

**End of Deployment Guide**  
Last Reviewed: 2025-11-15  
Next Review: 2025-12-15
