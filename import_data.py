import requests
import os
import time
from dotenv import load_dotenv
from database import SessionLocal
from models.seleccion import Seleccion
from models.jugador import Jugador

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://api.balldontlie.io/fifa/worldcup/v1"
HEADERS = {"Authorization": API_KEY}


def importar_selecciones():
    print("📡 Obteniendo selecciones del Mundial 2026...")
    response = requests.get(
        f"{BASE_URL}/teams",
        headers=HEADERS,
        params={"seasons[]": 2026}
    )
    data = response.json()

    if not data.get("data"):
        print("❌ Error:", data)
        return

    db = SessionLocal()
    total = 0

    for team in data["data"]:
        existente = db.query(Seleccion).filter(Seleccion.id_api == team["id"]).first()
        if not existente:
            seleccion = Seleccion(
                id_api=team["id"],
                nombre=team["name"],
                pais=team["name"],
                logo_url=team.get("logo_url"),
                activo=True
            )
            db.add(seleccion)
            total += 1
            print(f"  ✅ {team['name']}")
        else:
            print(f"  ⏩ Ya existe: {team['name']}")

    db.commit()
    db.close()
    print(f"\n✅ {total} selecciones importadas.")


def importar_jugadores():
    print("\n📡 Obteniendo jugadores del Mundial 2026...")
    db = SessionLocal()
    total = 0
    cursor = None

    while True:
        params = {"seasons[]": 2026, "per_page": 100}
        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            f"{BASE_URL}/players",
            headers=HEADERS,
            params=params
        )

        print(f"  Status: {response.status_code}")

        if response.status_code == 429:
            print("  ⏳ Rate limit, esperando 10 segundos...")
            time.sleep(10)
            continue

        if response.status_code != 200:
            print(f"  ❌ Error: {response.text[:200]}")
            break

        data = response.json()
        jugadores = data.get("data", [])

        if not jugadores:
            print("  ✅ Sin más jugadores")
            break

        for player in jugadores:
            seleccion = db.query(Seleccion).filter(
                Seleccion.pais == player.get("country_name")
            ).first()

            if not seleccion:
                continue

            existente = db.query(Jugador).filter(
                Jugador.id_api == player["id"]
            ).first()

            if not existente:
                jugador = Jugador(
                    id_api=player["id"],
                    nombre=player.get("name", ""),
                    seleccion_id=seleccion.id,
                    posicion=player.get("position"),
                    numero_camiseta=player.get("jersey_number"),
                    edad=player.get("age"),
                    foto_url=None,
                    activo=True
                )
                db.add(jugador)
                total += 1

        db.commit()
        print(f"  📦 {total} jugadores hasta ahora...")

        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

        time.sleep(1)

    db.close()
    print(f"\n✅ Total jugadores importados: {total}")


if __name__ == "__main__":
    importar_selecciones()
    importar_jugadores()