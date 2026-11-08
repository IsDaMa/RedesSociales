# ================================================================
# SCRIPT DE PARADA PARA CLUB DE BALONCESTO (CB SOCIAL HUB)
# ================================================================

Write-Host ""
Write-Host "==========================================================" -ForegroundColor DarkRed
Write-Host "🛑 DETENIENDO SERVIDOR WEB CB SOCIAL HUB (STOP.PS1) 🛑" -ForegroundColor Red
Write-Host "==========================================================" -ForegroundColor DarkRed
Write-Host ""

$directorioProyecto = $PSScriptRoot
if (-not $directorioProyecto) { $directorioProyecto = (Get-Location).Path }
Set-Location $directorioProyecto

# 1. Intentar con stop.py
if (Get-Command python -ErrorAction SilentlyContinue) {
    python stop.py
}

# 2. Asegurar liberación del puerto 5000
$connections = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($connections) {
    foreach ($conn in $connections) {
        $pidToKill = $conn.OwningProcess
        if ($pidToKill -gt 0) {
            Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Proceso PID $pidToKill detenido forzosamente." -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "🎉 Servidor detenido. Puerto 5000 libre." -ForegroundColor Green
Write-Host ""
