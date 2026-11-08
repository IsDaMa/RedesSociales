# 🏀 SISTEMA INTEGRAL DE AUTOMATIZACIÓN DE REDES SOCIALES (GOOGLE GEMINI)

Infraestructura completa y 100% gratuita ($0) para automatizar la comunicación y redes sociales de un club de baloncesto en **X (Twitter), Facebook, Instagram, WhatsApp, TikTok y Página Web** utilizando **Supabase, Google Gemini AI y GitHub Actions**.

---

## 📁 ESTRUCTURA DEL PROYECTO

```text
RedesSociales/
├── .agents/skills/              # Habilidades y subagentes de Antigravity / Gemini CLI
│   ├── generador-calendarios/   # Agente 1: Pre-Partido
│   ├── cronica-postpartido/     # Agente 2: Post-Partido + Carrusel
│   ├── guionista-tiktok-reels/  # Agente 3: TikTok / Reels (30s)
│   └── jugador-jornada-mvp/     # Agente 4: MVP y Valores de Cantera
├── .github/workflows/
│   └── automatizacion_club.yml  # Automatización periódica en la nube (GitHub Actions)
├── database/
│   ├── schema.sql               # Tablas Supabase (equipos, partidos, resultados, auditoria)
│   └── auditoria_local.db       # Base de datos SQLite local de registro de actividad
├── prompts/                     # Prompts maestros optimizados para Gemini
│   ├── agente_1_calendario_prepartido.md
│   ├── agente_2_cronica_postpartido.md
│   ├── agente_3_guionista_tiktok_reels.md
│   └── agente_4_jugador_jornada_mvp.md
├── templates/
│   ├── login.html               # Pantalla de acceso seguro controlado
│   └── index.html               # Panel responsive multiplataforma con visor de auditoría
├── start.py                     # Servidor seguro y controlado (Flask + Gemini + Auditoría)
├── start.ps1                    # Script de inicio rápido para Windows
├── stop.py                      # Script de parada limpia en Python
├── stop.ps1                     # Script de parada rápida para Windows
├── script_agentes.py            # Motor de automatización en lote con Gemini SDK
├── requirements.txt             # Dependencias del proyecto
├── .env.example                 # Plantilla de variables de entorno
└── README.md
```

---

## 🚀 CÓMO ARRANCAR Y DETENER EL PANEL WEB

### 1. Iniciar el servidor:
- **En PowerShell:** Ejecuta `./start.ps1` (o haz doble clic en `start.ps1`).
- **En Python directo:** `python start.py`
- *Se abrirá automáticamente tu navegador en `http://localhost:5000`*.

### 2. Detener el servidor:
- **En PowerShell:** Ejecuta `./stop.ps1`.
- **En Python directo:** `python stop.py`

### 🔑 Credenciales por Defecto:
- **Usuario:** `admin`
- **Contraseña:** `basketclub2026`
*(Modificables en tu archivo local `.env`)*

---

## 🛡️ TABLA DE AUDITORÍA Y CONTROL DE ACTIVIDAD

El sistema incorpora un registro que guarda de forma inmutable **quién se ha conectado y qué operación ha realizado**:
- **Fecha y Hora exacta (UTC)**
- **Usuario conectado**
- **Operación:** `LOGIN`, `LOGIN_FALLIDO`, `LOGOUT`, `SUPERVISION_IA`, `SUBIDA_FOTO`, `PUBLICACION`, `MODIFICACION`, `BORRADO`.
- **Detalles:** Información de la acción (modo, texto analizado, nombre de archivo).
- **Dirección IP** del dispositivo.

### Visualización:
Desde el propio panel web, pulsa en el botón superior **🛡️ Auditoría** para ver la tabla en tiempo real con las últimas 50 operaciones.

### Para activar la tabla en Supabase:
Pega esto en el **SQL Editor** de Supabase y dale a **Run**:

```sql
CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalles TEXT,
    ip VARCHAR(50),
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE IF EXISTS auditoria DISABLE ROW LEVEL SECURITY;
```
*(El sistema además guarda una copia local en SQLite `database/auditoria_local.db` para que el registro nunca falle aunque no haya conexión a internet).*
