import os
import json
import uuid
import hmac
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)

# Configuración de Seguridad y Sesión
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "cbe-super-secret-key-2026-basket-club")
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Máximo 16 MB por subida
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Credenciales de Acceso Administrador (configurables en .env)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "basketclub2026")

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar Google Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
MODEL_NAME = "gemini-3.1-flash-lite"

# ==============================================================================
# MIDDLEWARE Y SEGURIDAD
# ==============================================================================
@app.after_request
def aplicar_cabeceras_seguridad(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autorizado. Inicia sesión.'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==============================================================================
# PROMPT DEL SUPERVISOR INTELIGENTE
# ==============================================================================
PROMPT_SUPERVISOR_GENERAL = """Eres el Director de Comunicación y Contenidos de élite para un Club de Baloncesto.
Tu función es recibir un borrador, notas de entrenador, datos de partido o un anuncio en bruto del club, supervisarlo, optimizarlo y devolver el contenido adaptado a 6 plataformas específicas:
1. X (Twitter): Menos de 270 caracteres, dinámico, hashtags.
2. Instagram: Texto completo con saltos de línea, emojis, mención a patrocinadores o afición, llamada a comentar y hashtags.
3. Facebook: Tono comunitario, espaciado por párrafos, llamada a compartir.
4. WhatsApp: Optimizado para lectura en móvil. Usa *negritas* con asteriscos para datos clave y viñetas de emojis.
5. Página Web: Titular de prensa y artículo periodístico de 2-3 párrafos.
6. TikTok: Texto gancho para pantalla (0-3s), copy corto, audio sugerido y guion técnico en 4 tramos (0-3s, 3-15s, 15-25s, 25-30s).

DEBES RESPONDER EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO (sin bloques de código markdown ni texto adicional fuera del JSON), con esta estructura exacta:
{
  "x": "Texto adaptado a X...",
  "instagram": "Texto para Instagram...",
  "facebook": "Texto para Facebook...",
  "whatsapp": "Texto para WhatsApp con *negritas*...",
  "web": {
    "titulo": "Titular de prensa para la web del club",
    "cuerpo": "Artículo completo para la web del club..."
  },
  "tiktok": {
    "copy": "Texto breve para la descripción...",
    "audio": "Vibra musical (BPM / Trap / Épico)",
    "hook": "Texto gancho en pantalla...",
    "guion": [
      {"tiempo": "0-3s", "visual": "...", "locucion": "..."},
      {"tiempo": "3-15s", "visual": "...", "locucion": "..."},
      {"tiempo": "15-25s", "visual": "...", "locucion": "..."},
      {"tiempo": "25-30s", "visual": "...", "locucion": "..."}
    ]
  }
}
"""

# ==============================================================================
# RUTAS DE AUTENTICACIÓN Y NAVEGACIÓN
# ==============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        user = request.form.get('username', '').strip()
        pwd = request.form.get('password', '').strip()

        # Comparación segura para evitar ataques de temporización (timing attacks)
        val_user = hmac.compare_digest(user.encode('utf-8'), ADMIN_USERNAME.encode('utf-8'))
        val_pwd = hmac.compare_digest(pwd.encode('utf-8'), ADMIN_PASSWORD.encode('utf-8'))

        if val_user and val_pwd:
            session['logged_in'] = True
            session['user'] = user
            return redirect(url_for('index'))
        else:
            error = "Usuario o contraseña incorrectos."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('user', 'Admin'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

# ==============================================================================
# RUTAS API (PROTEGIDAS)
# ==============================================================================
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'foto' not in request.files:
        return jsonify({'error': 'No se envió ninguna imagen'}), 400
    file = request.files['foto']
    if file.filename == '':
        return jsonify({'error': 'Archivo no seleccionado'}), 400
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex[:12]}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        return jsonify({'url': f"/uploads/{unique_name}", 'filename': unique_name})
    return jsonify({'error': 'Formato de imagen no permitido (Usa JPG, PNG o WEBP)'}), 400

@app.route('/api/supervisar', methods=['POST'])
@login_required
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
        return jsonify({'error': f"Error al generar con Gemini: {str(e)}"}), 500

if __name__ == '__main__':
    print("🏀 SERVIDOR SEGURO Y CONTROLADO ACTIVO 🏀")
    print("👉 Abre tu navegador en: http://localhost:5000")
    print(f"🔑 Credenciales por defecto -> Usuario: {ADMIN_USERNAME} | Contraseña: {ADMIN_PASSWORD}")
    app.run(host='0.0.0.0', port=5000, debug=True)
