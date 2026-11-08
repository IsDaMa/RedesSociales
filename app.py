import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
MODEL_NAME = "gemini-3.1-flash-lite"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

PROMPT_SUPERVISOR_GENERAL = """Eres el Director de Comunicación y Contenidos de élite para un Club de Baloncesto.
Tu función es recibir un borrador, notas de entrenador, datos de partido o un anuncio en bruto del club, supervisarlo, optimizarlo y devolver el contenido adaptado a 6 plataformas específicas.

REGLAS DE TONO:
- Emocionante, comunitario, orgullo de club, deportividad y cercanía.
- Sin clichés vacíos, con llamadas a la acción claras.

DEBES RESPONDER EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO (sin bloques de código markdown ni texto adicional fuera del JSON), con esta estructura exacta:
{
  "x": "Texto adaptado a X (Twitter). Máximo 270 caracteres, dinámico, con emojis (🏀, 📅, etc.) y 2 hashtags oficiales.",
  "instagram": "Texto completo para Instagram con saltos de línea, emojis, mención a patrocinadores o afición, llamada a comentar y bloque final de hashtags.",
  "facebook": "Texto para Facebook con tono comunitario, informativo, espaciado por párrafos y llamada a compartir/asistir.",
  "whatsapp": "Texto para WhatsApp optimizado para lectura en móvil. Usa *negritas* con asteriscos para datos clave y viñetas de emojis.",
  "web": {
    "titulo": "Titular de prensa atractivo para la web del club",
    "cuerpo": "Artículo completo para la web del club (2-3 párrafos con estilo periodístico deportivo)."
  },
  "tiktok": {
    "copy": "Texto breve para la descripción de TikTok con llamada a seguir y hashtags virales.",
    "audio": "Vibra musical sugerida (ej. Beat enérgico 130 BPM / Trap)",
    "hook": "Texto gancho que va en los primeros 3 segundos en pantalla",
    "guion": [
      {"tiempo": "0-3s", "visual": "Gancho visual potente", "locucion": "Frase de enganche"},
      {"tiempo": "3-15s", "visual": "Clips dinámicos", "locucion": "Desarrollo de la historia"},
      {"tiempo": "15-25s", "visual": "Momento cumbre o dato", "locucion": "Clímax de la acción"},
      {"tiempo": "25-30s", "visual": "Escudo y llamada a seguir", "locucion": "Llamada a la acción"}
    ]
  }
}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'foto' not in request.files:
        return jsonify({'error': 'No se envió ninguna imagen'}), 400
    file = request.files['foto']
    if file.filename == '':
        return jsonify({'error': 'Archivo no seleccionado'}), 400
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex[:10]}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        return jsonify({'url': f"/uploads/{unique_name}", 'filename': unique_name})
    return jsonify({'error': 'Formato no permitido'}), 400

@app.route('/api/supervisar', methods=['POST'])
def supervisar():
    data = request.json or {}
    texto_usuario = data.get('texto', '').strip()
    modo = data.get('modo', 'general')

    if not texto_usuario:
        return jsonify({'error': 'El texto base está vacío'}), 400

    contexto_modo = f"MODO SELECCIONADO: {modo.upper()}.\n"
    if modo == 'prepartido':
        contexto_modo += "Enfócate en convocar a la afición, fechas, horas, pabellón y rival. No inventes datos."
    elif modo == 'postpartido':
        contexto_modo += "Enfócate en el marcador, crónica de victoria épica o aprendizaje con orgullo, y carrusel."
    elif modo == 'mvp':
        contexto_modo += "Enfócate en el reconocimiento individual, destacando los valores de equipo y cantera."
    elif modo == 'noticia':
        contexto_modo += "Enfócate en anuncio institucional, evento, campus o comunicado formal pero cercano."

    prompt_final = f"{contexto_modo}\n\nTEXTO/NOTAS EN BRUTO A SUPERVISAR:\n{texto_usuario}"

    try:
        response = client_gemini.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_final,
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_SUPERVISOR_GENERAL,
                response_mime_type="application/json",
                temperature=0.7,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        resultado_json = json.loads(response.text)
        return jsonify({'success': True, 'data': resultado_json})
    except Exception as e:
        print(f"Error con Gemini: {e}")
        # En caso de error o formato no JSON puro, intentar fallback limpio
        return jsonify({'error': f"Error al generar con Gemini: {str(e)}"}), 500

if __name__ == '__main__':
    print("🏀 SERVIDOR DE PREVISUALIZACIÓN MULTIPLATAFORMA ACTIVO 🏀")
    print("👉 Abre tu navegador en: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
