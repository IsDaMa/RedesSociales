# ================================================================
# SCRIPT DE PARADA - CB SOCIAL HUB
# ================================================================

Write-Host ""
Write-Host "==========================================================" -ForegroundColor DarkRed
Write-Host ">>> DETENIENDO SERVIDOR WEB CB SOCIAL HUB (STOP.PS1) <<<" -ForegroundColor Red
Write-Host "==========================================================" -ForegroundColor DarkRed
Write-Host ""

$directorio = $PSScriptRoot
if (-not $directorio) {
    $directorio = (Get-Location).Path
}
Set-Location $directorio

# 1. Ejecutar stop.py
if (Get-Command python -ErrorAction SilentlyContinue) {
    python stop.py
}

# 2. Asegurar que el puerto 5000 queda libre
$conns = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($conns) {
    foreach ($c in $conns) {
        $p = $c.OwningProcess
        if ($p -gt 0) {
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            Write-Host "[OK] Proceso PID $p detenido." -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "[OK] Servidor detenido. Puerto 5000 liberado." -ForegroundColor Green
Write-Host ""
