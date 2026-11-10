import os
import json
import uuid
import hmac
import sqlite3
from datetime import datetime, timezone
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
app.config['DB_PATH'] = os.path.join(os.path.dirname(__file__), 'database', 'auditoria_local.db')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Máximo 16 MB por subida
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Credenciales de Administrador (limpiando posibles espacios accidentales)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin").strip()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "basketclub2026").strip()

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['DB_PATH']), exist_ok=True)

# Inicializar Supabase si está disponible
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").replace("/rest/v1/", "").replace("/rest/v1", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
client_supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        client_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Aviso: Supabase no disponible en inicio ({e})")

# Inicializar Google Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client_gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
MODEL_NAME = "gemini-3.1-flash-lite"

# ==============================================================================
# BASE DE DATOS LOCAL DE AUDITORÍA (Garantiza registro inmediato 100% fiable)
# ==============================================================================
def init_local_audit_db():
    conn = sqlite3.connect(app.config['DB_PATH'])
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            accion TEXT NOT NULL,
            detalles TEXT,
            ip TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_local_audit_db()

def registrar_auditoria(usuario: str, accion: str, detalles: str, ip: str = None):
    """Registra cualquier acción en la base de datos local y en Supabase (si existe la tabla)."""
    if not ip:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
    
    fecha_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1. Registro Local (SQLite - siempre disponible sin fallos de red)
    try:
        conn = sqlite3.connect(app.config['DB_PATH'])
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO auditoria (usuario, accion, detalles, ip, fecha) VALUES (?, ?, ?, ?, ?)",
            (usuario, accion, detalles, ip, fecha_iso)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al registrar auditoría local: {e}")

    # 2. Registro Remoto en Supabase (si está configurada la tabla)
    if client_supabase:
        try:
            client_supabase.table("auditoria").insert({
                "usuario": usuario,
                "accion": accion,
                "detalles": detalles,
                "ip": ip
            }).execute()
        except Exception:
            # Si la tabla auditoria no ha sido creada aún en Supabase, no interrumpe el flujo
            pass

# ==============================================================================
# SEGURIDAD Y MIDDLEWARE
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
# PROMPT DEL SUPERVISOR IA - CLUB BALONCESTO CÁRTAMA
# ==============================================================================
PROMPT_SUPERVISOR_GENERAL = """Eres el Director de Comunicación y Redes Sociales del CLUB BALONCESTO CÁRTAMA (CB CÁRTAMA), en Cártama (Málaga), jugando como locales en la Ciudad Deportiva de Cártama.
Los colores de identidad del club son el VERDE y el AMARILLO. Tu lema y valores son la cantera, la pasión deportiva, el compañerismo y el orgullo cartameño.

Tu función es recibir notas de entrenadores (incluso notas rápidas de WhatsApp), datos de partidos o comunicados del club, supervisarlos con criterio deportivo impecable, corregir ortografía y adaptar el contenido a las 6 plataformas oficiales del club:

1. X (Twitter): Menos de 270 caracteres, dinámico, emojis (🏀, 📅, 📍, ⏱️), mención a la Ciudad Deportiva de Cártama si es partido en casa, y hashtags: #CBCártama #BaloncestoCártama.
2. Instagram: Texto completo con saltos de línea elegantes, emojis, mención al orgullo de club, llamada a animar a la Ciudad Deportiva y bloque final de hashtags: #CBCártama #BaloncestoCártama #CanteraCártama #SomosVerdeYAmarillo.
3. Facebook: Tono comunitario, cercano a las familias y aficionados de Cártama, espaciado por párrafos, llamada a compartir y apoyar.
4. WhatsApp: Optimizado para lectura en pantallas móviles. Usa *negritas* con asteriscos (*fecha*, *hora*, *rival*) y viñetas de emojis.
5. Página Web (cbcartama.com / cbcartama.es): Titular de prensa oficial y crónica periodística de 2-3 párrafos con estilo deportivo riguroso.
6. TikTok: Texto gancho para pantalla (0-3s), copy breve, audio sugerido y guion técnico estructurado en 4 tramos (0-3s, 3-15s, 15-25s, 25-30s).

DEBES RESPONDER EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO (sin bloques de código markdown ni texto fuera del JSON):
{
  "x": "Texto adaptado a X...",
  "instagram": "Texto para Instagram...",
  "facebook": "Texto para Facebook...",
  "whatsapp": "Texto para WhatsApp con *negritas*...",
  "web": {
    "titulo": "Titular de prensa oficial para la web de CB Cártama",
    "cuerpo": "Artículo completo para la web de CB Cártama..."
  },
  "tiktok": {
    "copy": "Texto breve para la descripción...",
    "audio": "Vibra musical sugerida",
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
# RUTAS DE AUTENTICACIÓN
# ==============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        user = request.form.get('username', '').strip()
        pwd = request.form.get('password', '').strip()

        # Tolerante a mayúsculas/minúsculas en el usuario (los teclados de móvil suelen poner la primera letra en mayúscula)
        val_user = hmac.compare_digest(user.lower().encode('utf-8'), ADMIN_USERNAME.lower().encode('utf-8'))
        val_pwd = hmac.compare_digest(pwd.encode('utf-8'), ADMIN_PASSWORD.encode('utf-8'))

        if val_user and val_pwd:
            session['logged_in'] = True
            session['user'] = user.lower()
            registrar_auditoria(user, "LOGIN", "Inicio de sesión exitoso en el panel web")
            return redirect(url_for('index'))
        else:
            registrar_auditoria(user or "Desconocido", "LOGIN_FALLIDO", f"Intento de acceso fallido con usuario: {user}")
            error = "Usuario o contraseña incorrectos."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    user = session.get('user', 'Usuario')
    registrar_auditoria(user, "LOGOUT", "Cierre de sesión voluntario")
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
# RUTAS API PROTEGIDAS Y AUDITADAS
# ==============================================================================
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    user = session.get('user', 'Admin')
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
        
        # Construir URL pública absoluta válida para que Facebook / Instagram puedan descargarla
        base_url = request.host_url.rstrip('/')
        if request.headers.get('X-Forwarded-Proto') == 'https':
            base_url = base_url.replace('http://', 'https://')
        full_url = f"{base_url}/uploads/{unique_name}"

        registrar_auditoria(
            user, 
            "SUBIDA_FOTO", 
            f"Subida de imagen: {file.filename} -> Guardada como {unique_name}"
        )
        return jsonify({'url': full_url, 'filename': unique_name})
    return jsonify({'error': 'Formato de imagen no permitido (Usa JPG, PNG o WEBP)'}), 400

@app.route('/api/supervisar', methods=['POST'])
@login_required
def supervisar():
    user = session.get('user', 'Admin')
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
        
        # Registrar en auditoría
        resumen_texto = texto_usuario[:80] + "..." if len(texto_usuario) > 80 else texto_usuario
        registrar_auditoria(
            user, 
            "SUPERVISION_IA", 
            f"Modo: {modo.upper()} | Texto base: '{resumen_texto}' | Generados 6 canales con Gemini"
        )

        return jsonify({'success': True, 'data': resultado_json})
    except Exception as e:
        registrar_auditoria(user, "ERROR_IA", f"Fallo en generación: {str(e)}")
        return jsonify({'error': f"Error al generar con Gemini: {str(e)}"}), 500

@app.route('/api/auditoria', methods=['GET'])
@login_required
def obtener_auditoria():
    """Devuelve las últimas 50 operaciones registradas para el panel de control."""
    try:
        conn = sqlite3.connect(app.config['DB_PATH'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, accion, detalles, ip, fecha FROM auditoria ORDER BY id DESC LIMIT 50")
        filas = cursor.fetchall()
        logs = [dict(fila) for fila in filas]
        conn.close()
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/publicar_web', methods=['POST'])
@login_required
def publicar_web():
    """Publica una noticia o comunicado directamente en la base de datos de la Web (Supabase)."""
    user = session.get('user', 'Admin')
    data = request.json or {}
    titulo = data.get('titulo', '').strip()
    contenido = data.get('contenido', '').strip()

    if not titulo or not contenido:
        return jsonify({'error': 'Título y contenido requeridos'}), 400

    id_noticia = None
    if client_supabase:
        try:
            res = client_supabase.table("noticias").insert({
                "titulo": titulo,
                "contenido": contenido,
                "publicado_noticia": True
            }).execute()
            if res.data:
                id_noticia = res.data[0].get('id')
        except Exception as e:
            print(f"Error al publicar en Supabase: {e}")

    registrar_auditoria(user, "PUBLICACION_WEB", f"Noticia publicada en web: '{titulo}'")
    return jsonify({'success': True, 'id': id_noticia, 'message': 'Noticia publicada con éxito en la web del club.'})

@app.route('/api/publicar_red', methods=['POST'])
@login_required
def publicar_red():
    """Envía la publicación a un Webhook (ej. Make.com / Zapier) si está configurado en las variables de entorno."""
    user = session.get('user', 'Admin')
    data = request.json or {}
    red = data.get('red', '').lower()
    texto = data.get('texto', '').strip()
    url_imagen = data.get('url_imagen', '').strip()

    # Garantizar que la imagen sea una URL pública absoluta (Facebook/Instagram exigen https://)
    base_url = request.host_url.rstrip('/')
    if request.headers.get('X-Forwarded-Proto') == 'https':
        base_url = base_url.replace('http://', 'https://')

    if url_imagen.startswith('data:image'):
        # Es un cartel generado en vivo en el Canvas (Base64) -> Guardarlo como archivo físico público
        try:
            import base64
            header, encoded = url_imagen.split(',', 1)
            ext = 'jpg' if 'jpeg' in header.lower() else 'png'
            unique_name = f"cartel_{uuid.uuid4().hex[:10]}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(encoded))
            url_imagen = f"{base_url}/uploads/{unique_name}"
        except Exception as e:
            print(f"Aviso: error guardando canvas base64: {e}")
            url_imagen = "https://www.cbcartama.com/img/hero_bg.webp"
    elif url_imagen.startswith('/'):
        url_imagen = f"{base_url}{url_imagen}"
    elif not url_imagen or not url_imagen.startswith('http'):
        url_imagen = "https://www.cbcartama.com/img/hero_bg.webp"

    webhook_url = os.environ.get('WEBHOOK_PUBLICACION', '').strip()
    
    if not webhook_url:
        return jsonify({'has_webhook': False, 'message': 'No hay webhook configurado, usando método directo.'})

    import requests
    try:
        payload = {
            "club": "Club Baloncesto Cártama",
            "red": red,
            "texto": texto,
            "imagen": url_imagen,
            "usuario": user,
            "fecha": datetime.now().isoformat()
        }
        resp = requests.post(webhook_url, json=payload, timeout=12)
        if resp.status_code < 400:
            registrar_auditoria(user, f"PUBLICACION_AUTO_{red.upper()}", f"Publicado automáticamente en {red} vía Make.com")
            return jsonify({'has_webhook': True, 'success': True, 'message': f'Publicado con éxito en {red} vía Make.com'})
        else:
            return jsonify({'has_webhook': True, 'success': False, 'error': f'Error en el webhook (código {resp.status_code})'}), 500
    except Exception as e:
        return jsonify({'has_webhook': True, 'success': False, 'error': str(e)}), 500

@app.route('/api/registrar_accion', methods=['POST'])
@login_required
def registrar_accion_manual():
    """Permite registrar acciones como 'PUBLICACION', 'MODIFICACION' o 'BORRADO' desde la web."""
    user = session.get('user', 'Admin')
    data = request.json or {}
    accion = data.get('accion', 'OPERACION').upper()
    detalles = data.get('detalles', 'Acción realizada desde la interfaz web')
    
    registrar_auditoria(user, accion, detalles)
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🏀 SERVIDOR SEGURO Y CONTROLADO ACTIVO (START.PY) 🏀")
    print(f"👉 Abre tu navegador en: http://localhost:{port}")
    print(f"🔑 Credenciales -> Usuario: {ADMIN_USERNAME} | Contraseña: {ADMIN_PASSWORD}")
    app.run(host='0.0.0.0', port=port, debug=False)

