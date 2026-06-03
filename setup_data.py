import sys
sys.path.insert(0, '.')
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

from database import SessionLocal
from models.seleccion import Seleccion
from models.jugador import Jugador

# ─── Configuración API ────────────────────────────────────────────────────────

API_KEY = os.getenv("API_FOOTBALL_KEY")
BALLDONTLIE_URL = "https://api.balldontlie.io/fifa/worldcup/v1"
HEADERS = {"Authorization": API_KEY}

# ─── Mapeos ───────────────────────────────────────────────────────────────────

FLAG_MAP = {
    "Algeria": "dz", "Argentina": "ar", "Australia": "au", "Austria": "at",
    "Belgium": "be", "Bosnia & Herzegovina": "ba", "Brazil": "br", "Cabo Verde": "cv",
    "Canada": "ca", "Colombia": "co", "Côte d'Ivoire": "ci", "Croatia": "hr",
    "Curaçao": "cw", "Czechia": "cz", "DR Congo": "cd", "Ecuador": "ec",
    "Egypt": "eg", "England": "gb-eng", "France": "fr", "Germany": "de",
    "Ghana": "gh", "Haiti": "ht", "Iran": "ir", "Iraq": "iq",
    "Japan": "jp", "Jordan": "jo", "Mexico": "mx", "Morocco": "ma",
    "Netherlands": "nl", "New Zealand": "nz", "Norway": "no", "Panama": "pa",
    "Paraguay": "py", "Portugal": "pt", "Qatar": "qa", "Saudi Arabia": "sa",
    "Scotland": "gb-sct", "Senegal": "sn", "South Africa": "za", "South Korea": "kr",
    "Spain": "es", "Sweden": "se", "Switzerland": "ch", "Tunisia": "tn",
    "Türkiye": "tr", "Uruguay": "uy", "USA": "us", "Uzbekistan": "uz",
}

GRUPOS = {
    "A": ["USA", "Panama", "Morocco", "Algeria"],
    "B": ["Mexico", "Ecuador", "Uzbekistan", "Haiti"],
    "C": ["Argentina", "Chile", "Peru", "Australia"],
    "D": ["France", "Belgium", "Croatia", "Egypt"],
    "E": ["Spain", "Switzerland", "Türkiye", "Côte d'Ivoire"],
    "F": ["Brazil", "Colombia", "Paraguay", "Saudi Arabia"],
    "G": ["England", "Germany", "DR Congo", "Iraq"],
    "H": ["Netherlands", "Senegal", "Japan", "Canada"],
    "I": ["Portugal", "Uruguay", "Czechia", "Curaçao"],
    "J": ["South Korea", "Norway", "Ghana", "Bosnia & Herzegovina"],
    "K": ["Morocco", "Iran", "New Zealand", "Tunisia"],
    "L": ["Qatar", "Austria", "Jordan", "South Africa"],
}

SELECCION_GRUPO = {equipo: grupo for grupo, equipos in GRUPOS.items() for equipo in equipos}

PLAYERS_DATA = [
    {
        "country": "Argentina",
        "players": [
            {"id_api": 1001, "nombre": "Lionel Messi", "posicion": "Delantero", "numero_camiseta": 10, "edad": 38},
            {"id_api": 1002, "nombre": "Emiliano Martínez", "posicion": "Portero", "numero_camiseta": 23, "edad": 32},
            {"id_api": 1003, "nombre": "Julián Álvarez", "posicion": "Delantero", "numero_camiseta": 9, "edad": 25},
            {"id_api": 1004, "nombre": "Rodrigo De Paul", "posicion": "Mediocampista", "numero_camiseta": 7, "edad": 31},
            {"id_api": 1005, "nombre": "Alexis Mac Allister", "posicion": "Mediocampista", "numero_camiseta": 20, "edad": 26},
            {"id_api": 1006, "nombre": "Enzo Fernández", "posicion": "Mediocampista", "numero_camiseta": 24, "edad": 24},
            {"id_api": 1007, "nombre": "Lautaro Martínez", "posicion": "Delantero", "numero_camiseta": 22, "edad": 27},
            {"id_api": 1008, "nombre": "Cristian Romero", "posicion": "Defensa", "numero_camiseta": 13, "edad": 27},
            {"id_api": 1009, "nombre": "Nicolás Otamendi", "posicion": "Defensa", "numero_camiseta": 19, "edad": 37},
            {"id_api": 1010, "nombre": "Nahuel Molina", "posicion": "Defensa", "numero_camiseta": 26, "edad": 27},
            {"id_api": 1011, "nombre": "Marcos Acuña", "posicion": "Defensa", "numero_camiseta": 8, "edad": 33},
            {"id_api": 1012, "nombre": "Leandro Paredes", "posicion": "Mediocampista", "numero_camiseta": 5, "edad": 31},
            {"id_api": 1013, "nombre": "Ángel Di María", "posicion": "Delantero", "numero_camiseta": 11, "edad": 37},
            {"id_api": 1014, "nombre": "Franco Armani", "posicion": "Portero", "numero_camiseta": 1, "edad": 38},
            {"id_api": 1015, "nombre": "Nicolás González", "posicion": "Delantero", "numero_camiseta": 21, "edad": 27},
        ]
    },
    {
        "country": "Colombia",
        "players": [
            {"id_api": 2001, "nombre": "James Rodríguez", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 34},
            {"id_api": 2002, "nombre": "Luis Díaz", "posicion": "Delantero", "numero_camiseta": 7, "edad": 27},
            {"id_api": 2003, "nombre": "Camilo Vargas", "posicion": "Portero", "numero_camiseta": 1, "edad": 33},
            {"id_api": 2004, "nombre": "Jhon Córdoba", "posicion": "Delantero", "numero_camiseta": 19, "edad": 31},
            {"id_api": 2005, "nombre": "Rafael Santos Borré", "posicion": "Delantero", "numero_camiseta": 9, "edad": 29},
            {"id_api": 2006, "nombre": "Richard Ríos", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 24},
            {"id_api": 2007, "nombre": "Jhon Arias", "posicion": "Defensa", "numero_camiseta": 22, "edad": 27},
            {"id_api": 2008, "nombre": "Daniel Muñoz", "posicion": "Defensa", "numero_camiseta": 18, "edad": 28},
            {"id_api": 2009, "nombre": "Dávinson Sánchez", "posicion": "Defensa", "numero_camiseta": 4, "edad": 28},
            {"id_api": 2010, "nombre": "Jefferson Lerma", "posicion": "Mediocampista", "numero_camiseta": 6, "edad": 30},
            {"id_api": 2011, "nombre": "Cucho Hernández", "posicion": "Delantero", "numero_camiseta": 11, "edad": 26},
            {"id_api": 2012, "nombre": "Juan Guillermo Cuadrado", "posicion": "Defensa", "numero_camiseta": 23, "edad": 36},
            {"id_api": 2013, "nombre": "Wilmar Barrios", "posicion": "Mediocampista", "numero_camiseta": 5, "edad": 31},
            {"id_api": 2014, "nombre": "Carlos Cuesta", "posicion": "Defensa", "numero_camiseta": 3, "edad": 26},
            {"id_api": 2015, "nombre": "Cristian Mosquera", "posicion": "Defensa", "numero_camiseta": 2, "edad": 22},
        ]
    },
    {
        "country": "Brazil",
        "players": [
            {"id_api": 3001, "nombre": "Vinicius Jr", "posicion": "Delantero", "numero_camiseta": 7, "edad": 25},
            {"id_api": 3002, "nombre": "Rodrygo", "posicion": "Delantero", "numero_camiseta": 10, "edad": 24},
            {"id_api": 3003, "nombre": "Alisson Becker", "posicion": "Portero", "numero_camiseta": 1, "edad": 32},
            {"id_api": 3004, "nombre": "Marquinhos", "posicion": "Defensa", "numero_camiseta": 4, "edad": 31},
            {"id_api": 3005, "nombre": "Casemiro", "posicion": "Mediocampista", "numero_camiseta": 5, "edad": 33},
            {"id_api": 3006, "nombre": "Bruno Guimarães", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 27},
            {"id_api": 3007, "nombre": "Endrick", "posicion": "Delantero", "numero_camiseta": 9, "edad": 19},
            {"id_api": 3008, "nombre": "Raphinha", "posicion": "Delantero", "numero_camiseta": 11, "edad": 28},
            {"id_api": 3009, "nombre": "Gabriel Martinelli", "posicion": "Delantero", "numero_camiseta": 17, "edad": 24},
            {"id_api": 3010, "nombre": "Éder Militão", "posicion": "Defensa", "numero_camiseta": 3, "edad": 27},
            {"id_api": 3011, "nombre": "Danilo", "posicion": "Defensa", "numero_camiseta": 2, "edad": 33},
            {"id_api": 3012, "nombre": "Ederson", "posicion": "Portero", "numero_camiseta": 23, "edad": 31},
            {"id_api": 3013, "nombre": "Richarlison", "posicion": "Delantero", "numero_camiseta": 19, "edad": 28},
            {"id_api": 3014, "nombre": "Lucas Paquetá", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 28},
            {"id_api": 3015, "nombre": "Savinho", "posicion": "Delantero", "numero_camiseta": 16, "edad": 21},
        ]
    },
    {
        "country": "France",
        "players": [
            {"id_api": 4001, "nombre": "Kylian Mbappé", "posicion": "Delantero", "numero_camiseta": 10, "edad": 26},
            {"id_api": 4002, "nombre": "Antoine Griezmann", "posicion": "Delantero", "numero_camiseta": 7, "edad": 34},
            {"id_api": 4003, "nombre": "Mike Maignan", "posicion": "Portero", "numero_camiseta": 16, "edad": 29},
            {"id_api": 4004, "nombre": "Raphaël Varane", "posicion": "Defensa", "numero_camiseta": 4, "edad": 32},
            {"id_api": 4005, "nombre": "Aurélien Tchouaméni", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 25},
            {"id_api": 4006, "nombre": "Eduardo Camavinga", "posicion": "Mediocampista", "numero_camiseta": 14, "edad": 22},
            {"id_api": 4007, "nombre": "Ousmane Dembélé", "posicion": "Delantero", "numero_camiseta": 11, "edad": 28},
            {"id_api": 4008, "nombre": "William Saliba", "posicion": "Defensa", "numero_camiseta": 17, "edad": 24},
            {"id_api": 4009, "nombre": "Theo Hernández", "posicion": "Defensa", "numero_camiseta": 22, "edad": 27},
            {"id_api": 4010, "nombre": "Benjamin Pavard", "posicion": "Defensa", "numero_camiseta": 5, "edad": 29},
            {"id_api": 4011, "nombre": "Marcus Thuram", "posicion": "Delantero", "numero_camiseta": 9, "edad": 27},
            {"id_api": 4012, "nombre": "Adrien Rabiot", "posicion": "Mediocampista", "numero_camiseta": 25, "edad": 30},
            {"id_api": 4013, "nombre": "Kingsley Coman", "posicion": "Delantero", "numero_camiseta": 20, "edad": 29},
            {"id_api": 4014, "nombre": "Alphanso Davies", "posicion": "Defensa", "numero_camiseta": 3, "edad": 24},
            {"id_api": 4015, "nombre": "Mattéo Guendouzi", "posicion": "Mediocampista", "numero_camiseta": 6, "edad": 26},
        ]
    },
    {
        "country": "Spain",
        "players": [
            {"id_api": 5001, "nombre": "Lamine Yamal", "posicion": "Delantero", "numero_camiseta": 19, "edad": 18},
            {"id_api": 5002, "nombre": "Pedri", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 23},
            {"id_api": 5003, "nombre": "Álvaro Morata", "posicion": "Delantero", "numero_camiseta": 7, "edad": 32},
            {"id_api": 5004, "nombre": "Unai Simón", "posicion": "Portero", "numero_camiseta": 23, "edad": 28},
            {"id_api": 5005, "nombre": "Rodri", "posicion": "Mediocampista", "numero_camiseta": 16, "edad": 29},
            {"id_api": 5006, "nombre": "Dani Carvajal", "posicion": "Defensa", "numero_camiseta": 2, "edad": 33},
            {"id_api": 5007, "nombre": "Aymeric Laporte", "posicion": "Defensa", "numero_camiseta": 14, "edad": 31},
            {"id_api": 5008, "nombre": "Ferran Torres", "posicion": "Delantero", "numero_camiseta": 11, "edad": 25},
            {"id_api": 5009, "nombre": "Dani Olmo", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 27},
            {"id_api": 5010, "nombre": "Nico Williams", "posicion": "Delantero", "numero_camiseta": 17, "edad": 23},
            {"id_api": 5011, "nombre": "Alejandro Grimaldo", "posicion": "Defensa", "numero_camiseta": 3, "edad": 29},
            {"id_api": 5012, "nombre": "Robin Le Normand", "posicion": "Defensa", "numero_camiseta": 4, "edad": 28},
            {"id_api": 5013, "nombre": "Fabián Ruiz", "posicion": "Mediocampista", "numero_camiseta": 26, "edad": 28},
            {"id_api": 5014, "nombre": "Mikel Oyarzabal", "posicion": "Delantero", "numero_camiseta": 9, "edad": 28},
            {"id_api": 5015, "nombre": "Gavi", "posicion": "Mediocampista", "numero_camiseta": 6, "edad": 21},
        ]
    },
    {
        "country": "England",
        "players": [
            {"id_api": 6001, "nombre": "Jude Bellingham", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 22},
            {"id_api": 6002, "nombre": "Harry Kane", "posicion": "Delantero", "numero_camiseta": 9, "edad": 32},
            {"id_api": 6003, "nombre": "Bukayo Saka", "posicion": "Delantero", "numero_camiseta": 7, "edad": 24},
            {"id_api": 6004, "nombre": "Jordan Pickford", "posicion": "Portero", "numero_camiseta": 1, "edad": 31},
            {"id_api": 6005, "nombre": "Phil Foden", "posicion": "Mediocampista", "numero_camiseta": 11, "edad": 25},
            {"id_api": 6006, "nombre": "Declan Rice", "posicion": "Mediocampista", "numero_camiseta": 4, "edad": 26},
            {"id_api": 6007, "nombre": "Trent Alexander-Arnold", "posicion": "Defensa", "numero_camiseta": 2, "edad": 27},
            {"id_api": 6008, "nombre": "Harry Maguire", "posicion": "Defensa", "numero_camiseta": 6, "edad": 32},
            {"id_api": 6009, "nombre": "Marcus Rashford", "posicion": "Delantero", "numero_camiseta": 14, "edad": 28},
            {"id_api": 6010, "nombre": "Kyle Walker", "posicion": "Defensa", "numero_camiseta": 5, "edad": 35},
            {"id_api": 6011, "nombre": "Cole Palmer", "posicion": "Mediocampista", "numero_camiseta": 20, "edad": 23},
            {"id_api": 6012, "nombre": "John Stones", "posicion": "Defensa", "numero_camiseta": 5, "edad": 31},
            {"id_api": 6013, "nombre": "Kobbie Mainoo", "posicion": "Mediocampista", "numero_camiseta": 26, "edad": 20},
            {"id_api": 6014, "nombre": "Ezri Konsa", "posicion": "Defensa", "numero_camiseta": 17, "edad": 27},
            {"id_api": 6015, "nombre": "Ollie Watkins", "posicion": "Delantero", "numero_camiseta": 21, "edad": 30},
        ]
    },
    {
        "country": "Germany",
        "players": [
            {"id_api": 7001, "nombre": "Florian Wirtz", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 22},
            {"id_api": 7002, "nombre": "Manuel Neuer", "posicion": "Portero", "numero_camiseta": 1, "edad": 39},
            {"id_api": 7003, "nombre": "Jamal Musiala", "posicion": "Mediocampista", "numero_camiseta": 14, "edad": 22},
            {"id_api": 7004, "nombre": "Kai Havertz", "posicion": "Delantero", "numero_camiseta": 7, "edad": 26},
            {"id_api": 7005, "nombre": "Joshua Kimmich", "posicion": "Mediocampista", "numero_camiseta": 6, "edad": 30},
            {"id_api": 7006, "nombre": "Antonio Rüdiger", "posicion": "Defensa", "numero_camiseta": 2, "edad": 32},
            {"id_api": 7007, "nombre": "Leroy Sané", "posicion": "Delantero", "numero_camiseta": 19, "edad": 29},
            {"id_api": 7008, "nombre": "Thomas Müller", "posicion": "Delantero", "numero_camiseta": 13, "edad": 36},
            {"id_api": 7009, "nombre": "Leon Goretzka", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 30},
            {"id_api": 7010, "nombre": "Niklas Süle", "posicion": "Defensa", "numero_camiseta": 4, "edad": 30},
            {"id_api": 7011, "nombre": "Serge Gnabry", "posicion": "Delantero", "numero_camiseta": 10, "edad": 30},
            {"id_api": 7012, "nombre": "İlkay Gündoğan", "posicion": "Mediocampista", "numero_camiseta": 21, "edad": 34},
            {"id_api": 7013, "nombre": "David Raum", "posicion": "Defensa", "numero_camiseta": 3, "edad": 26},
            {"id_api": 7014, "nombre": "Nico Schlotterbeck", "posicion": "Defensa", "numero_camiseta": 5, "edad": 25},
            {"id_api": 7015, "nombre": "Chris Führich", "posicion": "Delantero", "numero_camiseta": 11, "edad": 27},
        ]
    },
    {
        "country": "Portugal",
        "players": [
            {"id_api": 8001, "nombre": "Cristiano Ronaldo", "posicion": "Delantero", "numero_camiseta": 7, "edad": 41},
            {"id_api": 8002, "nombre": "Bruno Fernandes", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 31},
            {"id_api": 8003, "nombre": "Bernardo Silva", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 31},
            {"id_api": 8004, "nombre": "Rúben Dias", "posicion": "Defensa", "numero_camiseta": 4, "edad": 28},
            {"id_api": 8005, "nombre": "João Cancelo", "posicion": "Defensa", "numero_camiseta": 20, "edad": 31},
            {"id_api": 8006, "nombre": "Diogo Jota", "posicion": "Delantero", "numero_camiseta": 11, "edad": 29},
            {"id_api": 8007, "nombre": "Gonçalo Ramos", "posicion": "Delantero", "numero_camiseta": 9, "edad": 24},
            {"id_api": 8008, "nombre": "Vitinha", "posicion": "Mediocampista", "numero_camiseta": 16, "edad": 25},
            {"id_api": 8009, "nombre": "Rúben Neves", "posicion": "Mediocampista", "numero_camiseta": 15, "edad": 28},
            {"id_api": 8010, "nombre": "João Félix", "posicion": "Delantero", "numero_camiseta": 21, "edad": 26},
            {"id_api": 8011, "nombre": "Pepe", "posicion": "Defensa", "numero_camiseta": 3, "edad": 42},
            {"id_api": 8012, "nombre": "Diogo Costa", "posicion": "Portero", "numero_camiseta": 1, "edad": 26},
            {"id_api": 8013, "nombre": "Nuno Mendes", "posicion": "Defensa", "numero_camiseta": 19, "edad": 23},
            {"id_api": 8014, "nombre": "Otávio", "posicion": "Mediocampista", "numero_camiseta": 23, "edad": 30},
            {"id_api": 8015, "nombre": "Rafael Leão", "posicion": "Delantero", "numero_camiseta": 17, "edad": 26},
        ]
    },
    {
        "country": "Netherlands",
        "players": [
            {"id_api": 9001, "nombre": "Virgil van Dijk", "posicion": "Defensa", "numero_camiseta": 4, "edad": 34},
            {"id_api": 9002, "nombre": "Memphis Depay", "posicion": "Delantero", "numero_camiseta": 10, "edad": 31},
            {"id_api": 9003, "nombre": "Frenkie de Jong", "posicion": "Mediocampista", "numero_camiseta": 21, "edad": 28},
            {"id_api": 9004, "nombre": "Cody Gakpo", "posicion": "Delantero", "numero_camiseta": 11, "edad": 26},
            {"id_api": 9005, "nombre": "Tijjani Reijnders", "posicion": "Mediocampista", "numero_camiseta": 14, "edad": 27},
            {"id_api": 9006, "nombre": "Bart Verbruggen", "posicion": "Portero", "numero_camiseta": 1, "edad": 23},
            {"id_api": 9007, "nombre": "Denzel Dumfries", "posicion": "Defensa", "numero_camiseta": 22, "edad": 29},
            {"id_api": 9008, "nombre": "Xavi Simons", "posicion": "Mediocampista", "numero_camiseta": 7, "edad": 23},
            {"id_api": 9009, "nombre": "Wout Weghorst", "posicion": "Delantero", "numero_camiseta": 9, "edad": 33},
            {"id_api": 9010, "nombre": "Nathan Aké", "posicion": "Defensa", "numero_camiseta": 5, "edad": 30},
        ]
    },
    {
        "country": "Uruguay",
        "players": [
            {"id_api": 10001, "nombre": "Darwin Núñez", "posicion": "Delantero", "numero_camiseta": 11, "edad": 26},
            {"id_api": 10002, "nombre": "Federico Valverde", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 27},
            {"id_api": 10003, "nombre": "Luis Suárez", "posicion": "Delantero", "numero_camiseta": 9, "edad": 38},
            {"id_api": 10004, "nombre": "Rodrigo Bentancur", "posicion": "Mediocampista", "numero_camiseta": 30, "edad": 28},
            {"id_api": 10005, "nombre": "José María Giménez", "posicion": "Defensa", "numero_camiseta": 2, "edad": 30},
            {"id_api": 10006, "nombre": "Fernando Muslera", "posicion": "Portero", "numero_camiseta": 1, "edad": 38},
            {"id_api": 10007, "nombre": "Facundo Pellistri", "posicion": "Delantero", "numero_camiseta": 22, "edad": 23},
            {"id_api": 10008, "nombre": "Nahitan Nández", "posicion": "Mediocampista", "numero_camiseta": 15, "edad": 29},
            {"id_api": 10009, "nombre": "Ronald Araújo", "posicion": "Defensa", "numero_camiseta": 4, "edad": 26},
            {"id_api": 10010, "nombre": "Mathías Olivera", "posicion": "Defensa", "numero_camiseta": 16, "edad": 27},
        ]
    },
    {
        "country": "Mexico",
        "players": [
            {"id_api": 11001, "nombre": "Hirving Lozano", "posicion": "Delantero", "numero_camiseta": 22, "edad": 30},
            {"id_api": 11002, "nombre": "Raúl Jiménez", "posicion": "Delantero", "numero_camiseta": 9, "edad": 34},
            {"id_api": 11003, "nombre": "Guillermo Ochoa", "posicion": "Portero", "numero_camiseta": 13, "edad": 39},
            {"id_api": 11004, "nombre": "Edson Álvarez", "posicion": "Mediocampista", "numero_camiseta": 18, "edad": 27},
            {"id_api": 11005, "nombre": "Santiago Giménez", "posicion": "Delantero", "numero_camiseta": 11, "edad": 24},
            {"id_api": 11006, "nombre": "Alexis Vega", "posicion": "Delantero", "numero_camiseta": 23, "edad": 28},
            {"id_api": 11007, "nombre": "Carlos Antuna", "posicion": "Delantero", "numero_camiseta": 17, "edad": 26},
            {"id_api": 11008, "nombre": "César Montes", "posicion": "Defensa", "numero_camiseta": 3, "edad": 28},
            {"id_api": 11009, "nombre": "Jesús Gallardo", "posicion": "Defensa", "numero_camiseta": 23, "edad": 30},
            {"id_api": 11010, "nombre": "Héctor Herrera", "posicion": "Mediocampista", "numero_camiseta": 16, "edad": 34},
        ]
    },
    {
        "country": "USA",
        "players": [
            {"id_api": 12001, "nombre": "Christian Pulisic", "posicion": "Delantero", "numero_camiseta": 10, "edad": 27},
            {"id_api": 12002, "nombre": "Weston McKennie", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 27},
            {"id_api": 12003, "nombre": "Tyler Adams", "posicion": "Mediocampista", "numero_camiseta": 4, "edad": 26},
            {"id_api": 12004, "nombre": "Matt Turner", "posicion": "Portero", "numero_camiseta": 1, "edad": 31},
            {"id_api": 12005, "nombre": "Sergiño Dest", "posicion": "Defensa", "numero_camiseta": 2, "edad": 25},
            {"id_api": 12006, "nombre": "Gio Reyna", "posicion": "Mediocampista", "numero_camiseta": 7, "edad": 23},
            {"id_api": 12007, "nombre": "Yunus Musah", "posicion": "Mediocampista", "numero_camiseta": 6, "edad": 23},
            {"id_api": 12008, "nombre": "Tim Weah", "posicion": "Delantero", "numero_camiseta": 21, "edad": 25},
            {"id_api": 12009, "nombre": "Joe Scally", "posicion": "Defensa", "numero_camiseta": 15, "edad": 22},
            {"id_api": 12010, "nombre": "Ricardo Pepi", "posicion": "Delantero", "numero_camiseta": 9, "edad": 23},
        ]
    },
    {
        "country": "Morocco",
        "players": [
            {"id_api": 13001, "nombre": "Achraf Hakimi", "posicion": "Defensa", "numero_camiseta": 2, "edad": 27},
            {"id_api": 13002, "nombre": "Hakim Ziyech", "posicion": "Mediocampista", "numero_camiseta": 7, "edad": 33},
            {"id_api": 13003, "nombre": "Yassine Bounou", "posicion": "Portero", "numero_camiseta": 1, "edad": 34},
            {"id_api": 13004, "nombre": "Sofyan Amrabat", "posicion": "Mediocampista", "numero_camiseta": 4, "edad": 28},
            {"id_api": 13005, "nombre": "Noussair Mazraoui", "posicion": "Defensa", "numero_camiseta": 23, "edad": 28},
            {"id_api": 13006, "nombre": "Sofiane Boufal", "posicion": "Delantero", "numero_camiseta": 11, "edad": 31},
            {"id_api": 13007, "nombre": "Youssef En-Nesyri", "posicion": "Delantero", "numero_camiseta": 19, "edad": 28},
            {"id_api": 13008, "nombre": "Romain Saiss", "posicion": "Defensa", "numero_camiseta": 5, "edad": 35},
        ]
    },
    {
        "country": "Japan",
        "players": [
            {"id_api": 14001, "nombre": "Takehiro Tomiyasu", "posicion": "Defensa", "numero_camiseta": 5, "edad": 27},
            {"id_api": 14002, "nombre": "Takumi Minamino", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 30},
            {"id_api": 14003, "nombre": "Hiroki Sakai", "posicion": "Defensa", "numero_camiseta": 5, "edad": 34},
            {"id_api": 14004, "nombre": "Junya Ito", "posicion": "Delantero", "numero_camiseta": 14, "edad": 32},
            {"id_api": 14005, "nombre": "Shuichi Gonda", "posicion": "Portero", "numero_camiseta": 1, "edad": 32},
            {"id_api": 14006, "nombre": "Kaoru Mitoma", "posicion": "Delantero", "numero_camiseta": 11, "edad": 28},
            {"id_api": 14007, "nombre": "Wataru Endo", "posicion": "Mediocampista", "numero_camiseta": 7, "edad": 32},
            {"id_api": 14008, "nombre": "Ritsu Doan", "posicion": "Delantero", "numero_camiseta": 8, "edad": 27},
        ]
    },
    {
        "country": "Senegal",
        "players": [
            {"id_api": 15001, "nombre": "Sadio Mané", "posicion": "Delantero", "numero_camiseta": 10, "edad": 33},
            {"id_api": 15002, "nombre": "Edouard Mendy", "posicion": "Portero", "numero_camiseta": 1, "edad": 33},
            {"id_api": 15003, "nombre": "Kalidou Koulibaly", "posicion": "Defensa", "numero_camiseta": 3, "edad": 34},
            {"id_api": 15004, "nombre": "Ismaïla Sarr", "posicion": "Delantero", "numero_camiseta": 23, "edad": 27},
            {"id_api": 15005, "nombre": "Idrissa Gueye", "posicion": "Mediocampista", "numero_camiseta": 5, "edad": 35},
            {"id_api": 15006, "nombre": "Cheikhou Kouyaté", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 35},
            {"id_api": 15007, "nombre": "Boulaye Dia", "posicion": "Delantero", "numero_camiseta": 19, "edad": 28},
            {"id_api": 15008, "nombre": "Nampalys Mendy", "posicion": "Mediocampista", "numero_camiseta": 6, "edad": 33},
        ]
    },
    {
        "country": "Croatia",
        "players": [
            {"id_api": 16001, "nombre": "Luka Modrić", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 40},
            {"id_api": 16002, "nombre": "Ivan Perišić", "posicion": "Delantero", "numero_camiseta": 4, "edad": 36},
            {"id_api": 16003, "nombre": "Dominik Livaković", "posicion": "Portero", "numero_camiseta": 1, "edad": 30},
            {"id_api": 16004, "nombre": "Mateo Kovačić", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 31},
            {"id_api": 16005, "nombre": "Josip Šutalo", "posicion": "Defensa", "numero_camiseta": 6, "edad": 24},
            {"id_api": 16006, "nombre": "Andrej Kramarić", "posicion": "Delantero", "numero_camiseta": 9, "edad": 34},
            {"id_api": 16007, "nombre": "Marcelo Brozović", "posicion": "Mediocampista", "numero_camiseta": 11, "edad": 32},
            {"id_api": 16008, "nombre": "Joško Gvardiol", "posicion": "Defensa", "numero_camiseta": 3, "edad": 23},
        ]
    },
    {
        "country": "Switzerland",
        "players": [
            {"id_api": 17001, "nombre": "Granit Xhaka", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 33},
            {"id_api": 17002, "nombre": "Xherdan Shaqiri", "posicion": "Mediocampista", "numero_camiseta": 23, "edad": 33},
            {"id_api": 17003, "nombre": "Yann Sommer", "posicion": "Portero", "numero_camiseta": 1, "edad": 36},
            {"id_api": 17004, "nombre": "Breel Embolo", "posicion": "Delantero", "numero_camiseta": 7, "edad": 28},
            {"id_api": 17005, "nombre": "Manuel Akanji", "posicion": "Defensa", "numero_camiseta": 5, "edad": 30},
            {"id_api": 17006, "nombre": "Noah Okafor", "posicion": "Delantero", "numero_camiseta": 11, "edad": 25},
        ]
    },
    {
        "country": "Ecuador",
        "players": [
            {"id_api": 18001, "nombre": "Enner Valencia", "posicion": "Delantero", "numero_camiseta": 13, "edad": 35},
            {"id_api": 18002, "nombre": "Moisés Caicedo", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 23},
            {"id_api": 18003, "nombre": "Hernán Galíndez", "posicion": "Portero", "numero_camiseta": 1, "edad": 36},
            {"id_api": 18004, "nombre": "Jeremy Sarmiento", "posicion": "Mediocampista", "numero_camiseta": 11, "edad": 23},
            {"id_api": 18005, "nombre": "Piero Hincapié", "posicion": "Defensa", "numero_camiseta": 4, "edad": 23},
            {"id_api": 18006, "nombre": "Byron Castillo", "posicion": "Defensa", "numero_camiseta": 23, "edad": 27},
        ]
    },
    {
        "country": "Canada",
        "players": [
            {"id_api": 19001, "nombre": "Alphonso Davies", "posicion": "Defensa", "numero_camiseta": 3, "edad": 25},
            {"id_api": 19002, "nombre": "Jonathan David", "posicion": "Delantero", "numero_camiseta": 9, "edad": 25},
            {"id_api": 19003, "nombre": "Milan Borjan", "posicion": "Portero", "numero_camiseta": 18, "edad": 37},
            {"id_api": 19004, "nombre": "Tajon Buchanan", "posicion": "Delantero", "numero_camiseta": 11, "edad": 26},
            {"id_api": 19005, "nombre": "Stephen Eustáquio", "posicion": "Mediocampista", "numero_camiseta": 7, "edad": 28},
            {"id_api": 19006, "nombre": "Cyle Larin", "posicion": "Delantero", "numero_camiseta": 17, "edad": 30},
        ]
    },
    {
        "country": "South Korea",
        "players": [
            {"id_api": 20001, "nombre": "Son Heung-min", "posicion": "Delantero", "numero_camiseta": 7, "edad": 33},
            {"id_api": 20002, "nombre": "Lee Kang-in", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 24},
            {"id_api": 20003, "nombre": "Kim Min-jae", "posicion": "Defensa", "numero_camiseta": 3, "edad": 29},
            {"id_api": 20004, "nombre": "Cho Gue-sung", "posicion": "Delantero", "numero_camiseta": 9, "edad": 27},
            {"id_api": 20005, "nombre": "Kim Seung-gyu", "posicion": "Portero", "numero_camiseta": 1, "edad": 34},
            {"id_api": 20006, "nombre": "Hwang Hee-chan", "posicion": "Delantero", "numero_camiseta": 11, "edad": 29},
        ]
    },
    {
        "country": "Australia",
        "players": [
            {"id_api": 21001, "nombre": "Mathew Ryan", "posicion": "Portero", "numero_camiseta": 1, "edad": 33},
            {"id_api": 21002, "nombre": "Mathew Leckie", "posicion": "Delantero", "numero_camiseta": 7, "edad": 34},
            {"id_api": 21003, "nombre": "Aaron Mooy", "posicion": "Mediocampista", "numero_camiseta": 13, "edad": 35},
            {"id_api": 21004, "nombre": "Martin Boyle", "posicion": "Delantero", "numero_camiseta": 11, "edad": 31},
            {"id_api": 21005, "nombre": "Harry Souttar", "posicion": "Defensa", "numero_camiseta": 6, "edad": 26},
        ]
    },
    {
        "country": "Norway",
        "players": [
            {"id_api": 22001, "nombre": "Erling Haaland", "posicion": "Delantero", "numero_camiseta": 9, "edad": 25},
            {"id_api": 22002, "nombre": "Martin Ødegaard", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 27},
            {"id_api": 22003, "nombre": "Ørjan Nyland", "posicion": "Portero", "numero_camiseta": 1, "edad": 34},
            {"id_api": 22004, "nombre": "Alexander Sørloth", "posicion": "Delantero", "numero_camiseta": 19, "edad": 29},
            {"id_api": 22005, "nombre": "Sander Berge", "posicion": "Mediocampista", "numero_camiseta": 6, "edad": 27},
        ]
    },
    {
        "country": "Belgium",
        "players": [
            {"id_api": 23001, "nombre": "Kevin De Bruyne", "posicion": "Mediocampista", "numero_camiseta": 7, "edad": 34},
            {"id_api": 23002, "nombre": "Romelu Lukaku", "posicion": "Delantero", "numero_camiseta": 9, "edad": 32},
            {"id_api": 23003, "nombre": "Thibaut Courtois", "posicion": "Portero", "numero_camiseta": 1, "edad": 33},
            {"id_api": 23004, "nombre": "Jan Vertonghen", "posicion": "Defensa", "numero_camiseta": 5, "edad": 38},
            {"id_api": 23005, "nombre": "Youri Tielemans", "posicion": "Mediocampista", "numero_camiseta": 8, "edad": 28},
        ]
    },
    {
        "country": "Türkiye",
        "players": [
            {"id_api": 24001, "nombre": "Hakan Çalhanoğlu", "posicion": "Mediocampista", "numero_camiseta": 10, "edad": 31},
            {"id_api": 24002, "nombre": "Arda Güler", "posicion": "Mediocampista", "numero_camiseta": 17, "edad": 20},
            {"id_api": 24003, "nombre": "Mert Günok", "posicion": "Portero", "numero_camiseta": 1, "edad": 36},
            {"id_api": 24004, "nombre": "Zeki Çelik", "posicion": "Defensa", "numero_camiseta": 2, "edad": 28},
            {"id_api": 24005, "nombre": "Burak Yılmaz", "posicion": "Delantero", "numero_camiseta": 17, "edad": 39},
        ]
    },
]


# ─── PASO 1: Importar selecciones desde API ───────────────────────────────────

def importar_selecciones():
    print("\n📡 PASO 1: Importando selecciones desde API...")
    response = requests.get(
        f"{BALLDONTLIE_URL}/teams",
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
                activo=True
            )
            db.add(seleccion)
            total += 1
            print(f"  ✅ {team['name']}")
        else:
            print(f"  ⏩ Ya existe: {team['name']}")
    db.commit()
    db.close()
    print(f"  → {total} selecciones nuevas importadas.")


# ─── PASO 2: Seed de jugadores ────────────────────────────────────────────────

def seed_jugadores():
    print("\n🌍 PASO 2: Cargando jugadores...")
    db = SessionLocal()
    total = 0
    for team_data in PLAYERS_DATA:
        seleccion = db.query(Seleccion).filter(Seleccion.pais == team_data["country"]).first()
        if not seleccion:
            print(f"  ⚠️ No se encontró: {team_data['country']}")
            continue
        for p in team_data["players"]:
            if not db.query(Jugador).filter(Jugador.id_api == p["id_api"]).first():
                db.add(Jugador(
                    id_api=p["id_api"],
                    nombre=p["nombre"],
                    seleccion_id=seleccion.id,
                    posicion=p["posicion"],
                    numero_camiseta=p["numero_camiseta"],
                    edad=p["edad"],
                    activo=True
                ))
                total += 1
        db.commit()
        print(f"  ✅ {team_data['country']}")
    db.close()
    print(f"  → {total} jugadores nuevos cargados.")


# ─── PASO 3: Fix logos y grupos ───────────────────────────────────────────────

def fix_selecciones():
    print("\n🔧 PASO 3: Actualizando logos y grupos...")
    db = SessionLocal()
    actualizadas = 0
    for s in db.query(Seleccion).all():
        iso = FLAG_MAP.get(s.nombre)
        if iso:
            s.logo_url = f"https://flagcdn.com/w80/{iso}.png"
            actualizadas += 1
        grupo = SELECCION_GRUPO.get(s.nombre)
        if grupo:
            s.grupo = grupo
    db.commit()
    db.close()
    print(f"  → {actualizadas} selecciones actualizadas.")


# ─── PASO 4: Fix fotos jugadores ─────────────────────────────────────────────

def buscar_foto(nombre, intentos=3):
    for i in range(intentos):
        try:
            r = requests.get(
                "https://www.thesportsdb.com/api/v1/json/3/searchplayers.php",
                params={"p": nombre},
                timeout=10
            )
            if not r.text or not r.text.strip() or r.text.strip() == "null":
                time.sleep(5)
                continue
            try:
                data = r.json()
            except Exception:
                time.sleep(5)
                continue
            if data.get("player") and data["player"][0].get("strThumb"):
                return data["player"][0]["strThumb"]
            return None
        except Exception:
            time.sleep(3)
    return None

def fix_fotos():
    print("\n📸 PASO 4: Actualizando fotos de jugadores...")

    db = SessionLocal()
    jugadores_data = [(j.id, j.nombre) for j in db.query(Jugador).all()]
    db.close()

    actualizados = 0
    sin_foto = 0

    for i, (jugador_id, nombre) in enumerate(jugadores_data):
        foto = buscar_foto(nombre)
        nombre_encoded = nombre.replace(" ", "+")
        foto_final = foto if foto else f"https://ui-avatars.com/api/?name={nombre_encoded}&background=ffc107&color=000&size=200&bold=true"

        if foto:
            actualizados += 1
            print(f"  ✅ {nombre}")
        else:
            sin_foto += 1
            print(f"  ⚠️ Avatar: {nombre}")

        # Sesión nueva por cada jugador para evitar timeouts
        try:
            db = SessionLocal()
            j = db.query(Jugador).filter(Jugador.id == jugador_id).first()
            if j:
                j.foto_url = foto_final
                db.commit()
        except Exception as e:
            print(f"  ❌ Error guardando {nombre}: {e}")
            db.rollback()
        finally:
            db.close()

        time.sleep(1.5)

    print(f"  → {actualizados} fotos reales | {sin_foto} avatares.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  SETUP DE BASE DE DATOS — ÁLBUM MUNDIAL 2026")
    print("=" * 50)
    importar_selecciones()
    seed_jugadores()
    fix_selecciones()
    fix_fotos()
    print("\n" + "=" * 50)
    print("  ✅ BASE DE DATOS LISTA")
    print("=" * 50)