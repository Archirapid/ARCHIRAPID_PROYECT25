#!/usr/bin/env pwsh
# Script de restauración ARCHIRAPID MVP
# Uso: .\restore_backup.ps1 "ARCHIRAPID_MATRICULA_HONOR_20251111_143000"

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupName
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESTAURAR BACKUP ARCHIRAPID MVP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backupDir = "D:\ARCHIRAPID_BACKUPS"
$backupZip = "$backupDir\$BackupName.zip"
$backupExtracted = "$backupDir\$BackupName"
$targetDir = "D:\ARCHIRAPID_PROYECT25"

# 1. Verificar que existe el backup
if (-not (Test-Path $backupZip)) {
    Write-Host "❌ ERROR: Backup no encontrado: $backupZip" -ForegroundColor Red
    Write-Host ""
    Write-Host "Backups disponibles:" -ForegroundColor Yellow
    Get-ChildItem "$backupDir\*.zip" | ForEach-Object { 
        Write-Host "  - $($_.BaseName)" -ForegroundColor White 
    }
    exit 1
}

# 2. Confirmar restauración
Write-Host "⚠️  ADVERTENCIA: Esta operación sobrescribirá los archivos actuales en:" -ForegroundColor Yellow
Write-Host "   $targetDir" -ForegroundColor White
Write-Host ""
$confirm = Read-Host "¿Desea continuar? (S/N)"
if ($confirm -notmatch "^[Ss]$") {
    Write-Host "❌ Restauración cancelada" -ForegroundColor Red
    exit 0
}

# 3. Crear backup de seguridad del estado actual
Write-Host ""
Write-Host "📦 Creando backup del estado actual antes de restaurar..." -ForegroundColor Yellow
$preRestoreBackup = "D:\ARCHIRAPID_PROYECT25_PRE_RESTORE_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
if (Test-Path $targetDir) {
    Copy-Item -Path $targetDir -Destination $preRestoreBackup -Recurse -Force
    Write-Host "✅ Backup previo creado en: $preRestoreBackup" -ForegroundColor Green
}

# 4. Descomprimir backup
Write-Host "📂 Descomprimiendo backup..." -ForegroundColor Yellow
if (Test-Path $backupExtracted) {
    Remove-Item $backupExtracted -Recurse -Force
}
Expand-Archive -Path $backupZip -DestinationPath "$backupDir\temp_extract" -Force
$actualBackupPath = Get-ChildItem "$backupDir\temp_extract" | Select-Object -First 1
Write-Host "✅ Backup descomprimido" -ForegroundColor Green

# 5. Restaurar archivos
Write-Host "🔄 Restaurando archivos..." -ForegroundColor Yellow

# Archivos críticos a restaurar
$filesToRestore = @(
    "app.py",
    "requirements.txt",
    "archirapid_extract",
    "src",
    "assets",
    "*.md",
    "*.json"
)

foreach ($item in $filesToRestore) {
    $sourcePath = "$($actualBackupPath.FullName)\$item"
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination "$targetDir\" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ Restaurado: $item" -ForegroundColor Green
    }
}

# 6. Restaurar base de datos (si existe)
if (Test-Path "$($actualBackupPath.FullName)\data_BACKUP.db") {
    Copy-Item "$($actualBackupPath.FullName)\data_BACKUP.db" -Destination "$targetDir\data.db" -Force
    Write-Host "  ✅ Restaurado: data.db" -ForegroundColor Green
}

# 7. Limpiar extracción temporal
Remove-Item "$backupDir\temp_extract" -Recurse -Force

# 8. Verificar requirements.txt y sugerir reinstalación
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ RESTAURACIÓN COMPLETADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 PASOS SIGUIENTES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Verificar entorno virtual (venv):" -ForegroundColor White
Write-Host "   cd $targetDir" -ForegroundColor DarkGray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor DarkGray
Write-Host ""
Write-Host "2. Reinstalar dependencias (si es necesario):" -ForegroundColor White
Write-Host "   pip install -r requirements.txt" -ForegroundColor DarkGray
Write-Host ""
Write-Host "3. Verificar base de datos:" -ForegroundColor White
Write-Host "   python archirapid_extract\check_db.py" -ForegroundColor DarkGray
Write-Host ""
Write-Host "4. Ejecutar aplicación:" -ForegroundColor White
Write-Host "   streamlit run app.py" -ForegroundColor DarkGray
Write-Host ""
Write-Host "📍 Backup previo guardado en:" -ForegroundColor Yellow
Write-Host "   $preRestoreBackup" -ForegroundColor White
Write-Host ""
Write-Host "📄 Info del backup restaurado:" -ForegroundColor Yellow
if (Test-Path "$($actualBackupPath.FullName)\BACKUP_INFO.txt") {
    Get-Content "$($actualBackupPath.FullName)\BACKUP_INFO.txt" | Write-Host
}
Write-Host ""
