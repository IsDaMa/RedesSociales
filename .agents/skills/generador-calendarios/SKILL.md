---
name: generador-calendarios
description: >-
  Genera publicaciones pre-partido optimizadas para redes sociales (X, Instagram/Facebook y WhatsApp) para un club de baloncesto a partir de los datos del encuentro.
---

# Generador de Calendarios y Convocatorias Pre-Partido

Este agente convierte datos de partidos de baloncesto (categoría, rival, fecha, hora, pabellón) en publicaciones de alto impacto para los canales oficiales del club.

## Reglas de Ejecución

1. **Revisión de Integridad de Datos**:
   - Verificar si falta algún dato (hora, pabellón o rival).
   - **Prohibido alucinar o inventar**: Si un campo no está definido, marcar siempre como `Por confirmar`.
2. **Generación Multicanal**:
   - **X (Twitter)**: Conteo estricto < 280 caracteres. Directo, dinámico, con hashtags.
   - **Instagram / Facebook**: Estructura de bloques espaciados, llamada a la afición ("Llenemos la grada") y mención a patrocinadores.
   - **WhatsApp**: Formato optimizado para móvil con negritas (`*texto*`) y viñetas con emojis.

## Formato de Salida

Siempre devolver las publicaciones con la siguiente estructura:

```markdown
### 🐦 X (Twitter) [< 280 caracteres]
[Texto optimizado para X]

---

### 📸 Instagram / Facebook
[Texto estructurado con saltos de línea, llamada a la acción y patrocinadores]

---

### 💬 WhatsApp (Grupos de Familias y Jugadores)
[Texto con formato *negrita* y viñetas limpias para móvil]
```

