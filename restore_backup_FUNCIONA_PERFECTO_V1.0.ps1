#!/usr/bin/env pwsh
# Script de restauración para FUNCIONA_PERFECTO_V1.0

param(
    [switch]$Test
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESTAURAR BACKUP FUNCIONA_PERFECTO_V1.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backupDir = "D:\ARCHIRAPID_BACKUPS"
$backupName = "FUNCIONA_PERFECTO_V1.0"
$backupZip = "$backupDir\$backupName.zip"
$backupExtracted = "$backupDir\$backupName"
$targetDir = "D:\ARCHIRAPID_PROYECT25"

if (-not (Test-Path $backupZip)) {
    Write-Host "❌ ERROR: Backup no encontrado: $backupZip" -ForegroundColor Red
    exit 1
}

if (-not $Test) {
    Write-Host "⚠️  ADVERTENCIA: Esta operación sobrescribirá los archivos actuales en:" -ForegroundColor Yellow
    Write-Host "   $targetDir" -ForegroundColor White
    Write-Host ""
    $confirm = Read-Host "¿Desea continuar? (S/N)"
    if ($confirm -notmatch "^[Ss]$") {
        Write-Host "❌ Restauración cancelada" -ForegroundColor Red
        exit 0
    }
} else {
    Write-Host "🔬 Ejecutando RESTAURACIÓN EN MODO TEST (no se sobrescribirá)" -ForegroundColor Yellow
}

Write-Host "📦 Creando backup del estado actual antes de restaurar..." -ForegroundColor Yellow
if ($Test) {
    $preRestoreBackup = "$env:TEMP\ARCHIRAPID_PRE_RESTORE_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
} else {
    $preRestoreBackup = "D:\ARCHIRAPID_PROYECT25_PRE_RESTORE_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
}
if (Test-Path $targetDir) {
    Copy-Item -Path $targetDir -Destination $preRestoreBackup -Recurse -Force
    Write-Host "✅ Backup previo creado en: $preRestoreBackup" -ForegroundColor Green
}

Write-Host "📂 Descomprimiendo backup..." -ForegroundColor Yellow
Expand-Archive -Path $backupZip -DestinationPath "$backupDir\temp_extract" -Force
$actualBackupPath = Get-ChildItem "$backupDir\temp_extract" | Select-Object -First 1

Write-Host "🔄 Restaurando archivos..." -ForegroundColor Yellow

$filesToRestore = @("app.py", "requirements.txt", "archirapid_extract", "src", "assets", "*.md", "*.json")

foreach ($item in $filesToRestore) {
    $sourcePath = "$($actualBackupPath.FullName)\$item"
    if (Test-Path $sourcePath) {
        if ($Test) {
            Write-Host "  (test) ✅ Encontrado: $item" -ForegroundColor Green
        } else {
            Copy-Item -Path $sourcePath -Destination "$targetDir\" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✅ Restaurado: $item" -ForegroundColor Green
        }
    }
}

if (Test-Path "$($actualBackupPath.FullName)\data_BACKUP.db") {
    if ($Test) {
        Write-Host "  (test) ✅ Encontrado: data_BACKUP.db" -ForegroundColor Green
    } else {
        Copy-Item "$($actualBackupPath.FullName)\data_BACKUP.db" -Destination "$targetDir\data.db" -Force
        Write-Host "  ✅ Restaurado: data.db" -ForegroundColor Green
    }
}

Remove-Item "$backupDir\temp_extract" -Recurse -Force

Write-Host "\n========================================" -ForegroundColor Cyan
Write-Host "  ✅ RESTAURACIÓN FUNCIONA_PERFECTO_V1.0 COMPLETADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path "$($actualBackupPath.FullName)\BACKUP_INFO.txt") {
    Get-Content "$($actualBackupPath.FullName)\BACKUP_INFO.txt" | Write-Host
}
