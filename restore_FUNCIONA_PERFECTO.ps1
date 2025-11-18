#!/usr/bin/env pwsh
# Restore pre-configured backup FUNCIONA_PERFECTO

param(
    [string]$BackupDirectory = "D:\ARCHIRAPID_BACKUPS"
)

$backupName = "FUNCIONA_PERFECTO"
Write-Host "Restaurando backup: $backupName desde $BackupDirectory" -ForegroundColor Yellow
.
# Call the restore script; it accepts the backup folder name parameter
.
Write-Host "Llamando a restore_backup.ps1" -ForegroundColor Yellow
& "$PSScriptRoot\restore_backup.ps1" $backupName
