# 🏀 CB CÁRTAMA | SISTEMA DE REDES SOCIALES Y COMUNICACIÓN (IA GEMINI)

Plataforma oficial de gestión, redacción con IA y publicación supervisada de contenidos deportivos para el **Club Baloncesto Cártama** (Málaga).

* 🌐 **URL Oficial en Producción:** [https://redes.cbcartama.com](https://redes.cbcartama.com)
* 🌐 **Web del Club:** [https://www.cbcartama.com](https://www.cbcartama.com) | [https://www.cbcartama.es](https://www.cbcartama.es)
* 📍 **Sede:** Ciudad Deportiva de Cártama, Málaga
* 🎨 **Colores:** Verde (#15803d) y Amarillo/Dorado (#eab308)

---

## 📱 CANALES Y REDES SOCIALES CUBIERTAS

1. **🐦 X (Twitter):** Mensajes con gancho, emoticonos, límite controlado de 280 caracteres y hashtags `#CBCártama #BaloncestoMálaga`.
2. **📸 Instagram:** Copy emotivo para la afición, estructura para fotos y carruseles de 4 diapositivas.
3. **📘 Facebook:** Redacción completa orientada a familias, socios y patrocinadores locales.
4. **💬 WhatsApp:** Convocatorias y comunicados listos para compartir con 1 clic en grupos de padres y cantera.
5. **🎬 TikTok / Reels / Shorts:** Guion vertical dinámico de 30 segundos estructurado en tabla temporal (`0-3s`, `3-15s`, `15-25s`, `25-30s`).
6. **🌐 Web Oficial del Club:** Titular formal y cuerpo de noticia que se publica con 1 clic en la base de datos Supabase de `cbcartama.com`.

---

## 🛡️ PROTOCOLO DE SUPERVISIÓN Y SEGURIDAD

> **Regla de Oro:** Ningún contenido se publica en redes sociales sin aprobación humana previa.

1. **Previsualización Real:** El entrenador o coordinador ve en pantalla exactamente cómo lucirá el post en cada red.
2. **Publicación 1 a 1:** Cada red social se gestiona en su propia pestaña de forma totalmente independiente.
3. **Casilla de Confirmación Obligatoria:** Debajo de cada red existe el check `[ ] He revisado el texto y autorizo la publicación en [Red]`. El botón permanece bloqueado en gris hasta que se marca.
4. **Edición en Caliente:** Cualquier texto de la maqueta se puede corregir directamente pulsando sobre él antes de publicar.
5. **Auditoría Permanente:** Cada inicio de sesión, foto subida y publicación queda registrada con fecha, hora, usuario e IP (visible desde el botón *Auditoría* del panel).

---

## 🚀 ARQUITECTURA Y DESPLIEGUE EN LA NUBE ($0)

* **Servidor en la Nube:** Alojado en **Render.com** (Plan Free $0) conectado automáticamente al repositorio de GitHub `IsDaMa/RedesSociales`.
* **Dominio Corporativo:** Registro CNAME en **IONOS** apuntando `redes.cbcartama.com` hacia Render con certificado SSL automático (Let's Encrypt).
* **Motor de IA:** Google Gemini (`gemini-3.1-flash-lite`) con latencia ultra-rápida (<2s).
* **Publicación Automática:** Webhook en **Make.com** para publicar directamente en Facebook e Instagram sin tocar APIs complejas.

---

## 💻 EJECUCIÓN LOCAL (DESARROLLO O RESPALDO)

Si se desea ejecutar el servidor en un ordenador local:

### 1. Iniciar:
* **En PowerShell:** `.\start.ps1`
* **En Python:** `python start.py`
* *(Abre automáticamente `http://localhost:5000` o en la red local `http://192.168.x.x:5000`)*

### 2. Detener:
* **En PowerShell:** `.\stop.ps1`
* **En Python:** `python stop.py`

### 🔑 Credenciales por Defecto:
* **Usuario:** `admin` *(o `Admin`)*
* **Contraseña:** `basketclub2026`
