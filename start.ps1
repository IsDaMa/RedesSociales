# ================================================================
# SCRIPT DE INICIO RAPIDO - CB SOCIAL HUB
# ================================================================

Write-Host ""
Write-Host "==========================================================" -ForegroundColor DarkYellow
Write-Host ">>> INICIANDO SERVIDOR WEB CB SOCIAL HUB (START.PS1) <<<" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor DarkYellow
Write-Host ""

# 1. Comprobar que Python este disponible
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python no esta instalado o no se encuentra en el PATH." -ForegroundColor Red
    Exit 1
}

# 2. Directorio del proyecto
$directorio = $PSScriptRoot
if (-not $directorio) {
    $directorio = (Get-Location).Path
}
Set-Location $directorio

# 3. Liberar puerto 5000 si estuviera ocupado
$conn = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($conn) {
    Write-Host "[INFO] Liberando puerto 5000..." -ForegroundColor DarkGray
    python stop.py | Out-Null
    Start-Sleep -Seconds 1
}

# 4. Arrancar start.py en segundo plano
Write-Host "[INFO] Arrancando servidor seguro en segundo plano..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "start.py" -WorkingDirectory $directorio -WindowStyle Minimized

# 5. Esperar confirmacion de arranque
Write-Host "[INFO] Esperando conexion..." -ForegroundColor Gray
$intentos = 0
$listo = $false

while ($intentos -lt 12) {
    Start-Sleep -Milliseconds 600
    try {
        $req = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -UseBasicParsing -TimeoutSec 2
        if ($req.StatusCode -eq 200) {
            $listo = $true
            break
        }
    }
    catch {
        $intentos++
    }
}

Write-Host ""
if ($listo) {
    Write-Host "[EXITO] Servidor iniciado correctamente." -ForegroundColor Green
    Write-Host "URL Local:   http://localhost:5000" -ForegroundColor White
    Write-Host "Usuario:     admin" -ForegroundColor White
    Write-Host "Password:    basketclub2026" -ForegroundColor White
    Write-Host ""
    Write-Host "Abriendo en tu navegador..." -ForegroundColor Yellow
    Start-Process "http://localhost:5000"
}
else {
    Write-Host "[AVISO] El servidor se esta iniciando. Abre: http://localhost:5000" -ForegroundColor Yellow
}

Write-Host ""
