import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno locales si existen
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Faltan las variables SUPABASE_URL o SUPABASE_KEY.")
    sys.exit(1)

if not GEMINI_API_KEY:
    print("❌ ERROR: Falta la variable GEMINI_API_KEY. Consíguela gratis en https://aistudio.google.com")
    sys.exit(1)

# Inicializar cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurar cliente de Google Gemini
try:
    from google import genai
    from google.genai import types
    client_gemini = genai.Client(api_key=GEMINI_API_KEY)
    USE_MODERN_SDK = True
except ImportError:
    import google.generativeai as genai_legacy
    genai_legacy.configure(api_key=GEMINI_API_KEY)
    USE_MODERN_SDK = False

MODEL_NAME = "gemini-2.5-flash"

def llamar_gemini(system_prompt: str, user_content: str) -> str:
    """Invoca el modelo Gemini con instrucciones de sistema y contenido del usuario."""
    if USE_MODERN_SDK:
        response = client_gemini.models.generate_content(
            model=MODEL_NAME,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
        )
        return response.text
    else:
        model = genai_legacy.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt
        )
        response = model.generate_content(user_content)
        return response.text

# ==============================================================================
# 1. AGENTE 1: CALENDARIOS Y CONVOCATORIAS PRE-PARTIDO
# ==============================================================================
PROMPT_SISTEMA_AGENTE_1 = """Eres el Responsable de Comunicación y Redes Sociales del Club de Baloncesto.
Tu objetivo es transformar los datos de los próximos partidos en publicaciones atractivas y con alta legibilidad.

Formatos requeridos por canal:
- X (Twitter): Un único post corto, directo, con ganchos limpios y estricto uso de menos de 280 caracteres.
- Facebook/Instagram: Texto detallado, espaciado por bloques, llamada a la afición ("¡Llenemos el pabellón!") y mención a patrocinadores.
- WhatsApp (Familias y Jugadores): Formato limpio usando negritas de WhatsApp (*texto*) y emojis como viñetas para lectura rápida en pantallas móviles.

REGLAS DE TONO Y SEGURIDAD:
- Emocionante, comunitario, enfocado en el orgullo de club.
- Uso obligatorio de emojis de baloncesto (🏀, 📅, 📍, ⏱️).
- NUNCA inventes datos. Si falta la hora o el lugar, escribe 'Por confirmar'.
"""

def procesar_calendario_semanal():
    print("\n🔍 Comprobando partidos pendientes de publicar...")
    response = supabase.table("partidos").select("*, equipos(nombre, categoria)").eq("publicado_calendario", False).execute()
    partidos = response.data

    if not partidos:
        print("✅ No hay nuevos partidos para publicar esta semana.")
        return

    for partido in partidos:
        equipo_info = partido.get('equipos') or {}
        nombre_equipo = equipo_info.get('nombre', 'Equipo del Club')
        categoria = equipo_info.get('categoria', 'Baloncesto')

        info_partido = (
            f"Equipo: {nombre_equipo} ({categoria})\n"
            f"Rival: {partido['rival']}\n"
            f"Fecha y Hora: {partido['fecha_hora']}\n"
            f"Lugar / Pabellón: {partido['lugar']}\n"
            f"Condición: {'Local' if partido.get('es_local', True) else 'Visitante'}"
        )

        print(f"⚙️ Procesando partido ID {partido['id']}: {nombre_equipo} vs {partido['rival']}...")
        
        contenido_generado = llamar_gemini(
            system_prompt=PROMPT_SISTEMA_AGENTE_1,
            user_content=f"Genera las publicaciones pre-partido con estos datos:\n\n{info_partido}"
        )

        print(f"--- CONTENIDO PRE-PARTIDO GENERADO (ID {partido['id']}) ---")
        print(contenido_generado[:250] + "...\n")

        supabase.table("partidos").update({
            "publicado_calendario": True,
            "contenido_prepartido": contenido_generado
        }).eq("id", partido['id']).execute()

    print("🎉 Calendarios pre-partido procesados y guardados en Supabase.")

# ==============================================================================
# 2. AGENTE 2 & 3: CRÓNICAS POST-PARTIDO, CARRUSEL Y REELS
# ==============================================================================
PROMPT_SISTEMA_AGENTE_2 = """Eres el Director de Contenidos y Redactor Deportivo del Club de Baloncesto.
Recibirás el marcador final y un resumen informal del entrenador (con lenguaje coloquial o errores de tipeo).
Tu trabajo es procesarlo y estructurar el contenido de la victoria o derrota.

PRODUCCIÓN REQUERIDA:
1. Copy para Redes (Instagram/Facebook/X): Crónica épica si se gana, o de orgullo y aprendizaje si se pierde. (En X mantener menos de 280 caracteres).
2. Estructura de Carrusel de Instagram (4 Imágenes):
   - Imagen 1: Foto destacada con el Marcador Final gigante superpuesto.
   - Imagen 2: El quinteto ideal o la foto de equipo con la frase clave del partido.
   - Imagen 3: Foto de acción del partido con un dato estadístico o jugador destacado.
   - Imagen 4: Foto de la afición/banquillo con la fecha del próximo encuentro (Llamada a la acción).
"""

PROMPT_SISTEMA_AGENTE_3 = """Eres el Creador de Contenido Vertical del Club de Baloncesto.
Tu misión es transformar un resultado o noticia en un guion dinámico de 30 segundos de alta retención.

ESTRUCTURA DEL GUION (Formato Tabla Markdown):
| Tiempo | Lo que se ve (Visual) | Lo que se dice (Audio/Locución) | Ritmo/Música |
| 0-3s   | [Gancho visual impactante] | [Frase rompedora de retención] | Música enérgica/Corte rápido |
| 3-15s  | [Clips rápidos del partido] | [Desarrollo de la noticia/crónica] | Ritmo constante |
| 15-25s | [Mejor jugada o foto del resultado] | [Detalle clave o marcador] | Subidón de audio |
| 25-30s | [Pantalla final con logo del club] | [Llamada a la acción: "Síguenos"] | Efecto de sonido (Swish) |
"""

def procesar_resultados_postpartido():
    print("\n🔍 Comprobando resultados post-partido pendientes...")
    response = supabase.table("resultados").select("*, partidos(*, equipos(nombre, categoria))").eq("publicado_resultado", False).execute()
    resultados = response.data

    if not resultados:
        print("✅ No hay resultados pendientes de redactar.")
        return

    for res in resultados:
        partido = res.get('partidos') or {}
        equipo = partido.get('equipos') or {}
        
        info_resultado = (
            f"Equipo: {equipo.get('nombre', 'Club')} ({equipo.get('categoria', 'Baloncesto')})\n"
            f"Rival: {partido.get('rival', 'Rival')}\n"
            f"Marcador: Nuestro Club {res['puntos_club']} - {res['puntos_rival']} {partido.get('rival')}\n"
            f"Resultado: {'VICTORIA' if res['puntos_club'] > res['puntos_rival'] else 'DERROTA'}\n"
            f"Notas informales del entrenador:\n{res.get('resumen_entrenador', 'Gran esfuerzo colectivo.')}"
        )

        print(f"⚙️ Redactando crónica y carrusel para el partido ID {res['partido_id']}...")
        
        # Agente 2: Crónica y Carrusel
        cronica_y_carrusel = llamar_gemini(
            system_prompt=PROMPT_SISTEMA_AGENTE_2,
            user_content=f"Procesa este resultado y genera los copies y el carrusel:\n\n{info_resultado}"
        )

        # Agente 3: Guion TikTok / Reels
        guion_tiktok = llamar_gemini(
            system_prompt=PROMPT_SISTEMA_AGENTE_3,
            user_content=f"Genera el guion de vídeo vertical de 30 segundos para este partido:\n\n{info_resultado}"
        )

        supabase.table("resultados").update({
            "publicado_resultado": True,
            "contenido_postpartido": cronica_y_carrusel,
            "guion_tiktok": guion_tiktok
        }).eq("id", res['id']).execute()

    print("🎉 Crónicas, carruseles y guiones de Reels procesados y guardados en Supabase.")

if __name__ == "__main__":
    print("🏀 INICIANDO SISTEMA DE AUTOMATIZACIÓN CON GEMINI 🏀")
    procesar_calendario_semanal()
    procesar_resultados_postpartido()
    print("🏁 PROCESO COMPLETADO CON ÉXITO.")

