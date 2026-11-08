import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").replace("/rest/v1/", "").replace("/rest/v1", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def crear_partido_de_prueba():
    print("🏀 Creando datos de prueba en Supabase...")

    # 1. Crear o comprobar equipo de prueba
    res_equipo = supabase.table("equipos").select("*").eq("nombre", "Senior Masculino A").execute()
    
    if not res_equipo.data:
        res_nuevo_equipo = supabase.table("equipos").insert({
            "nombre": "Senior Masculino A",
            "categoria": "Primera Nacional"
        }).execute()
        equipo_id = res_nuevo_equipo.data[0]['id']
        print(f"✅ Creado equipo de prueba con ID: {equipo_id}")
    else:
        equipo_id = res_equipo.data[0]['id']
        print(f"ℹ️ Usando equipo existente con ID: {equipo_id}")

    # 2. Fecha del próximo sábado a las 18:30h UTC
    fecha_partido = datetime.now(timezone.utc) + timedelta(days=5)
    fecha_iso = fecha_partido.strftime("%Y-%m-%d 18:30:00+00")

    # 3. Crear partido no publicado
    res_partido = supabase.table("partidos").insert({
        "equipo_id": equipo_id,
        "rival": "CB Los Leones",
        "fecha_hora": fecha_iso,
        "lugar": "Pabellón Municipal Esperanza",
        "es_local": True,
        "publicado_calendario": False
    }).execute()

    partido_id = res_partido.data[0]['id']
    print(f"🎉 ¡Partido de prueba creado con éxito en Supabase! (ID Partido: {partido_id})")
    print("👉 Este partido está pendiente de redactar (publicado_calendario = False).")

if __name__ == "__main__":
    crear_partido_de_prueba()
