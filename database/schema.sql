-- ================================================================
-- TABLAS DEL SISTEMA DE AUTOMATIZACIÓN PARA CLUB DE BALONCESTO
-- Ejecutar en: Supabase Dashboard > SQL Editor > New Query
-- ================================================================

-- 1. Tabla de Equipos del Club
CREATE TABLE IF NOT EXISTS equipos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL -- Ej: Senior Masc A, Junior Fem, Cadete, Infantil
);

-- 2. Tabla de Partidos (Calendario y Convocatorias)
CREATE TABLE IF NOT EXISTS partidos (
    id SERIAL PRIMARY KEY,
    equipo_id INT REFERENCES equipos(id) ON DELETE CASCADE,
    rival VARCHAR(100) NOT NULL,
    fecha_hora TIMESTAMP WITH TIME ZONE NOT NULL,
    lugar VARCHAR(150) NOT NULL, -- Ej: Pabellón Municipal Esperanza, Pabellón Norte
    es_local BOOLEAN DEFAULT TRUE,
    publicado_calendario BOOLEAN DEFAULT FALSE,
    contenido_prepartido TEXT -- Almacena los copies generados por Gemini
);

-- 3. Tabla de Resultados y Crónicas Post-Partido
CREATE TABLE IF NOT EXISTS resultados (
    id SERIAL PRIMARY KEY,
    partido_id INT REFERENCES partidos(id) ON DELETE CASCADE UNIQUE,
    puntos_club INT NOT NULL,
    puntos_rival INT NOT NULL,
    resumen_entrenador TEXT, -- Notas rápidas de WhatsApp dictadas por el entrenador
    url_imagen_1 TEXT, -- Enlaces a fotos del partido (Supabase Storage o Drive)
    url_imagen_2 TEXT,
    url_imagen_3 TEXT,
    url_imagen_4 TEXT,
    publicado_resultado BOOLEAN DEFAULT FALSE,
    contenido_postpartido TEXT, -- Copies multirred y guion de carrusel generados
    guion_tiktok TEXT -- Guion de vídeo vertical generado por el Agente 3
);

-- 4. Tabla de Noticias y Comunicados
CREATE TABLE IF NOT EXISTS noticias (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    publicado_noticia BOOLEAN DEFAULT FALSE
);

-- ================================================================
-- PERMISOS Y ACCESO (RLS) PARA SCRIPTS Y GITHUB ACTIONS
-- Permite que los scripts de automatización puedan leer y escribir
-- ================================================================
ALTER TABLE IF EXISTS equipos DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS partidos DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS resultados DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS noticias DISABLE ROW LEVEL SECURITY;


