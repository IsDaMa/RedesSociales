# 🏀 SISTEMA INTEGRAL DE AUTOMATIZACIÓN DE REDES SOCIALES (GOOGLE GEMINI)

Infraestructura completa y 100% gratuita ($0) para automatizar la comunicación y redes sociales de un club de baloncesto en **X (Twitter), Facebook, Instagram, WhatsApp y TikTok** utilizando **Supabase, Google Gemini AI y GitHub Actions**.

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
│   └── schema.sql               # Script SQL para crear las tablas en Supabase
├── prompts/                     # Prompts maestros optimizados para Gemini
│   ├── agente_1_calendario_prepartido.md
│   ├── agente_2_cronica_postpartido.md
│   ├── agente_3_guionista_tiktok_reels.md
│   └── agente_4_jugador_jornada_mvp.md
├── script_agentes.py            # Motor de automatización en Python con Gemini SDK
├── requirements.txt             # Dependencias del proyecto (google-genai, supabase)
├── .env.example                 # Plantilla de variables de entorno
└── README.md
```

---

## 🚀 GUÍA DE INSTALACIÓN PASO A PASO ($0 REAL)

### Paso 1: Configurar la Base de Datos Gratuita en Supabase
1. Entra en [Supabase](https://supabase.com/) y crea una cuenta gratuita.
2. Crea un nuevo proyecto llamado `ClubBaloncesto`.
3. Ve a **SQL Editor** en el menú lateral izquierdo.
4. Abre el archivo [`database/schema.sql`](./database/schema.sql), copia todo el contenido, pégalo en el editor y pulsa **Run**.
5. Ve a **Project Settings (Engranaje) > API** y copia:
   - `Project URL`
   - `anon public API Key`

### Paso 2: Obtener tu Clave Gratuita de Google Gemini
1. Entra en [Google AI Studio](https://aistudio.google.com/).
2. Inicia sesión con cualquier cuenta de Google.
3. Haz clic en **Get API Key** y luego en **Create API Key**.
4. Copia tu clave (`AIzaSy...`). *(El nivel gratuito permite hasta 15 solicitudes por minuto y 1,500 al día, más que de sobra para todo un club)*.

### Paso 3: Configurar Secretos en GitHub (Para la nube)
1. Sube este proyecto a tu repositorio de GitHub (público o privado).
2. En GitHub, ve a **Settings > Secrets and variables > Actions**.
3. Añade tres **Repository Secrets**:
   - `SUPABASE_URL`: Tu URL de Supabase.
   - `SUPABASE_KEY`: Tu clave anon pública de Supabase.
   - `GEMINI_API_KEY`: Tu clave obtenida en Google AI Studio.

---

## 🛠️ FUNCIONAMIENTO Y OPERATIVA DIARIA

### 1. Publicación de Calendarios Pre-partido:
- Rellenas los próximos partidos en la tabla `partidos` de Supabase (rival, fecha, hora, lugar).
- Cada lunes (o cuando pulses "Run workflow" en GitHub), Gemini redacta los textos para X, Facebook/Instagram y WhatsApp, y los guarda en la columna `contenido_prepartido`.

### 2. Publicación de Resultados y Crónicas:
- Cuando termine la jornada, añade una fila en la tabla `resultados` con los puntos y la nota rápida que envió el entrenador por WhatsApp.
- Gemini genera automáticamente:
  - Copy para Instagram/Facebook y X.
  - El guion de diseño del **Carrusel de 4 Diapositivas**.
  - El guion de 30 segundos para **TikTok / Reels** con tabla cronometrada.
- Todo queda guardado en Supabase listo para copiar y publicar.

---

## 💻 PRUEBA LOCAL EN TU EQUIPO

Si quieres probar la generación en tu propio ordenador:

```powershell
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Copiar .env.example a .env y colocar tus claves reales
cp .env.example .env

# 3. Ejecutar el script
python script_agentes.py
```

