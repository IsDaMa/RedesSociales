# ================================================================
# SCRIPT DE INICIO RÁPIDO PARA CLUB DE BALONCESTO (CB SOCIAL HUB)
# ================================================================

Write-Host ""
Write-Host "==========================================================" -ForegroundColor DarkYellow
Write-Host "🏀 INICIANDO SERVIDOR WEB CB SOCIAL HUB (START.PS1) 🏀" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor DarkYellow
Write-Host ""

# 1. Comprobar Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python no está instalado o no se encuentra en el PATH." -ForegroundColor Red
    Exit 1
}

# 2. Detener instancias previas en el puerto 5000 para evitar conflictos
$portConnection = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($portConnection) {
    Write-Host "⚠️ Puerto 5000 ocupado. Liberando puerto..." -ForegroundColor DarkGray
    python stop.py | Out-Null
    Start-Sleep -Seconds 1
}

# 3. Iniciar el servidor start.py en segundo plano en la carpeta del proyecto
Write-Host "🚀 Arrancando servidor seguro en segundo plano..." -ForegroundColor Cyan
$directorioProyecto = $PSScriptRoot
if (-not $directorioProyecto) { $directorioProyecto = (Get-Location).Path }

Start-Process -FilePath "python" -ArgumentList "start.py" -WorkingDirectory $directorioProyecto -WindowStyle Minimized

# 4. Esperar a que el servidor esté listo
Write-Host "⏳ Esperando confirmación de inicio..." -ForegroundColor Gray
$intentos = 0
$servidorListo = $false

while ($intentos -lt 10) {
    Start-Sleep -Milliseconds 700
    try {
        $test = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -UseBasicParsing -TimeoutSec 2
        if ($test.StatusCode -eq 200) {
            $servidorListo = $true
            break
        }
    } catch {
        $intentos++
    }
}

if ($servidorListo) {
    Write-Host ""
    Write-Host "🎉 ¡SERVIDOR INICIADO CORRECTAMENTE!" -ForegroundColor Green
    Write-Host "👉 URL Local: " -NoNewline; Write-Host "http://localhost:5000" -ForegroundColor White
    Write-Host "🔑 Usuario: " -NoNewline; Write-Host "admin" -ForegroundColor White
    Write-Host "🔑 Contraseña: " -NoNewline; Write-Host "basketclub2026" -ForegroundColor White
    Write-Host ""
    Write-Host "Abriendo en tu navegador predeterminado..." -ForegroundColor Yellow
    Start-Process "http://localhost:5000"
} else {
    Write-Host "⚠️ El servidor está arrancando. Abre manualmente: http://localhost:5000" -ForegroundColor Yellow
}
