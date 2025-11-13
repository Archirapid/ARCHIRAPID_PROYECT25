#!/usr/bin/env pwsh
# Script para subir el proyecto a GitHub - Usuario: ARCHIRAPID
# Uso: .\push_to_github.ps1

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SUBIR PROYECTO A GITHUB" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar que Git está configurado
Write-Host "[1/5] Verificando configuración Git..." -ForegroundColor Yellow
$gitUser = git config user.name
$gitEmail = git config user.email

if (-not $gitUser -or -not $gitEmail) {
    Write-Host "⚠️  Configurando Git por primera vez..." -ForegroundColor Yellow
    git config --global user.name "ARCHIRAPID"
    git config --global user.email "archirapid@example.com"
    Write-Host "✅ Git configurado" -ForegroundColor Green
} else {
    Write-Host "✅ Git ya configurado: $gitUser <$gitEmail>" -ForegroundColor Green
}

# Verificar remoto
Write-Host "`n[2/5] Verificando repositorio remoto..." -ForegroundColor Yellow
$remote = git remote -v | Select-String "origin"
if ($remote) {
    Write-Host "✅ Remoto configurado:" -ForegroundColor Green
    git remote -v | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "❌ No hay remoto configurado" -ForegroundColor Red
    exit 1
}

# Verificar estado
Write-Host "`n[3/5] Verificando estado del repositorio..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️  Hay cambios sin guardar:" -ForegroundColor Yellow
    git status --short
    Write-Host "`n¿Desea hacer commit de estos cambios? (S/N)" -ForegroundColor Yellow
    $commit = Read-Host
    if ($commit -match "^[Ss]$") {
        git add .
        $message = Read-Host "Mensaje del commit"
        git commit -m $message
        Write-Host "✅ Commit creado" -ForegroundColor Green
    }
} else {
    Write-Host "✅ No hay cambios pendientes" -ForegroundColor Green
}

# Subir a GitHub
Write-Host "`n[4/5] Subiendo código a GitHub..." -ForegroundColor Yellow
Write-Host "⚠️  Se te pedirá usuario y contraseña/token de GitHub" -ForegroundColor Yellow
Write-Host ""

try {
    git push -u origin master 2>&1 | Tee-Object -Variable pushOutput
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Código subido exitosamente a master" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al subir código" -ForegroundColor Red
        Write-Host "Posibles soluciones:" -ForegroundColor Yellow
        Write-Host "1. Verifica que creaste el repositorio en GitHub" -ForegroundColor White
        Write-Host "2. Usa un Personal Access Token como contraseña" -ForegroundColor White
        Write-Host "3. Ve a: https://github.com/settings/tokens" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

# Subir tags
Write-Host "`n[5/5] Subiendo tags (backups) a GitHub..." -ForegroundColor Yellow
try {
    git push --tags 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tags subidos exitosamente" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Error al subir tags (no crítico)" -ForegroundColor Yellow
}

# Resumen final
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✅ PROYECTO SUBIDO A GITHUB" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "🌐 URL: https://github.com/ARCHIRAPID/ARCHIRAPID_PROYECT25" -ForegroundColor Cyan
Write-Host "📊 Commits subidos: $(git rev-list --count origin/master 2>$null)" -ForegroundColor Cyan
Write-Host "🏷️  Tags subidos: $(git tag | Measure-Object -Line | Select-Object -ExpandProperty Lines)" -ForegroundColor Cyan

Write-Host "`n✅ Ahora puedes ver tu proyecto en:" -ForegroundColor Green
Write-Host "   https://github.com/ARCHIRAPID/ARCHIRAPID_PROYECT25`n" -ForegroundColor White

Write-Host "📚 Para futuros cambios, usa:" -ForegroundColor Yellow
Write-Host "   git add ." -ForegroundColor White
Write-Host "   git commit -m 'mensaje'" -ForegroundColor White
Write-Host "   git push`n" -ForegroundColor White
