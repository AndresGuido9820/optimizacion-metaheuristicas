"""
Parche para notebook 03: reemplaza las 32 capitales de Mexico por las 96
prefecturas de los departamentos de la Francia metropolitana.

Cambios:
  - Titulo del notebook actualizado a Francia.
  - Datos de ciudades: 96 prefecturas (departamentos 01-95 + 2A + 2B).
  - Modelo de costo: EUR/km en lugar de MXN/km (combustible + peajes + tiempo).
  - Todas las referencias a 'Mexico' y 'MXN' se actualizan.
  - El archivo se guarda como 03_tsp_france.ipynb.
"""

import json
from pathlib import Path

NB_IN  = Path("notebooks/03_tsp_mexico.ipynb")
NB_OUT = Path("notebooks/03_tsp_france.ipynb")


def md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


# ---------------------------------------------------------------------------
# Nuevo titulo y descripcion del notebook
# ---------------------------------------------------------------------------
NEW_TITLE_MD = """\
# TSP — 96 Departamentos de la Francia Metropolitana: ACO y Algoritmo Genetico

Este notebook resuelve el **Problema del Viajero (TSP)** para las 96 prefecturas
de los departamentos de la Francia metropolitana (Francia continental + Corsega).

Se utilizan dos metaheuristicas:
- **ACO** (Ant Colony Optimization): colonias de hormigas.
- **GA** (Genetic Algorithm): algoritmo genetico con operadores de orden.

El costo de desplazamiento entre ciudades incluye:
- Combustible: consumo del vehiculo x precio de la gasolina en Francia.
- Peajes: costo promedio por km en autopistas francesas.
- Tiempo del vendedor: valor hora definido como parametro.\
"""

# ---------------------------------------------------------------------------
# Nueva celda de configuracion global y modelo de costo
# ---------------------------------------------------------------------------
NEW_CONFIG_CODE = """\
# ---------------------------------------------------------------------------
# Imports y configuracion global
# ---------------------------------------------------------------------------
import numpy as np
import random
import time
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
from IPython.display import Image, display

from deap import base, creator, tools, algorithms

Path('outputs').mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Modelo de costo del viajero
# Vehiculo de referencia: Renault Clio 1.0 TCe (5.5 L/100 km en carretera)
# Precio gasolina SP95 en Francia (2024): ~1.75 EUR/L
# ---------------------------------------------------------------------------
CONSUMO_L100KM = 5.5          # litros cada 100 km
PRECIO_GASOLINA = 1.75        # EUR por litro
COSTO_COMBUSTIBLE_KM = (CONSUMO_L100KM / 100) * PRECIO_GASOLINA  # EUR/km ~ 0.096

PEAJES_KM  = 0.08             # EUR/km promedio autopistas francesas
VEL_KMH    = 90.0             # km/h velocidad media en carretera francesa
COSTO_HORA = 25.0             # EUR/h valor hora del vendedor (SMIC ~ 11.65 EUR/h neto)

# Costo total por km = combustible + peajes
COSTO_KM = COSTO_COMBUSTIBLE_KM + PEAJES_KM

print(f"Modelo de costo:")
print(f"  Combustible : {COSTO_COMBUSTIBLE_KM:.4f} EUR/km")
print(f"  Peajes      : {PEAJES_KM:.4f} EUR/km")
print(f"  Total viaje : {COSTO_KM:.4f} EUR/km")
print(f"  Tiempo      : {COSTO_HORA:.2f} EUR/h  a  {VEL_KMH:.0f} km/h = {COSTO_HORA/VEL_KMH:.4f} EUR/km")
print(f"  Factor total: {COSTO_KM + COSTO_HORA/VEL_KMH:.4f} EUR/km")

# ---------------------------------------------------------------------------
# Hiperparametros ACO (Ant Colony Optimization)
# ---------------------------------------------------------------------------
ACO_N_ANTS = 50
ACO_ITERS  = 300
ACO_ALPHA  = 1.0   # importancia de la feromona
ACO_BETA   = 3.0   # importancia de la heuristica (1/distancia)
ACO_RHO    = 0.1   # tasa de evaporacion de feromona
ACO_Q      = 100.0 # constante de deposito de feromona

# ---------------------------------------------------------------------------
# Hiperparametros GA (Algoritmo Genetico)
# ---------------------------------------------------------------------------
GA_POP   = 200
GA_GENS  = 500
GA_CXPB  = 0.8    # probabilidad de cruce
GA_MUTPB = 0.2    # probabilidad de mutacion

N_RUNS    = 30    # corridas independientes para la comparativa estadistica
SEED_DEMO = 7     # semilla para corridas de demostracion\
"""

# ---------------------------------------------------------------------------
# Nueva celda de descripcion de datos (markdown)
# ---------------------------------------------------------------------------
NEW_DATA_MD = """\
## 1. Datos y Modelo de Costo

### 1.1 Los 96 departamentos de la Francia metropolitana

Francia metropolitana se divide en **96 departamentos** (numerados 01-95 mas
2A y 2B para Corsega). Cada departamento tiene una **prefectura** (capital
administrativa) que es el nodo del TSP.

El mapa cubre desde Dunkerque (norte) hasta Ajaccio (sur, Corsega), una
extension de aproximadamente 1 200 km de norte a sur.\
"""

# ---------------------------------------------------------------------------
# Nueva celda de datos: 96 prefecturas francesas
# ---------------------------------------------------------------------------
NEW_DATA_CODE = """\
# ---------------------------------------------------------------------------
# Las 96 prefecturas de los departamentos de la Francia metropolitana.
# Formato: (departamento, prefectura, latitud, longitud)
# Fuente: coordenadas oficiales de las prefecturas (WGS84).
# ---------------------------------------------------------------------------

PREFECTURAS = [
    ("Ain",                    "Bourg-en-Bresse",        46.2050,   5.2275),
    ("Aisne",                  "Laon",                   49.5647,   3.6253),
    ("Allier",                 "Moulins",                46.5647,   3.3333),
    ("Alpes-de-Hte-Provence",  "Digne-les-Bains",        44.0922,   6.2361),
    ("Hautes-Alpes",           "Gap",                    44.5594,   6.0786),
    ("Alpes-Maritimes",        "Nice",                   43.7102,   7.2620),
    ("Ardeche",                "Privas",                 44.7353,   4.5989),
    ("Ardennes",               "Charleville-Mezieres",   49.7736,   4.7183),
    ("Ariege",                 "Foix",                   42.9667,   1.6039),
    ("Aube",                   "Troyes",                 48.2973,   4.0744),
    ("Aude",                   "Carcassonne",            43.2130,   2.3491),
    ("Aveyron",                "Rodez",                  44.3500,   2.5753),
    ("Bouches-du-Rhone",       "Marseille",              43.2965,   5.3698),
    ("Calvados",               "Caen",                   49.1829,  -0.3707),
    ("Cantal",                 "Aurillac",               44.9264,   2.4406),
    ("Charente",               "Angouleme",              45.6494,   0.1564),
    ("Charente-Maritime",      "La Rochelle",            46.1603,  -1.1511),
    ("Cher",                   "Bourges",                47.0814,   2.3986),
    ("Correze",                "Tulle",                  45.2670,   1.7761),
    ("Corse-du-Sud",           "Ajaccio",                41.9192,   8.7386),
    ("Haute-Corse",            "Bastia",                 42.6976,   9.4500),
    ("Cote-d-Or",              "Dijon",                  47.3220,   5.0415),
    ("Cotes-d-Armor",          "Saint-Brieuc",           48.5147,  -2.7653),
    ("Creuse",                 "Gueret",                 46.1672,   1.8675),
    ("Dordogne",               "Perigueux",              45.1847,   0.7214),
    ("Doubs",                  "Besancon",               47.2378,   6.0242),
    ("Drome",                  "Valence",                44.9333,   4.8917),
    ("Eure",                   "Evreux",                 49.0272,   1.1508),
    ("Eure-et-Loir",           "Chartres",               48.4469,   1.4875),
    ("Finistere",              "Quimper",                48.0000,  -4.1000),
    ("Gard",                   "Nimes",                  43.8367,   4.3600),
    ("Haute-Garonne",          "Toulouse",               43.6047,   1.4442),
    ("Gers",                   "Auch",                   43.6461,   0.5853),
    ("Gironde",                "Bordeaux",               44.8378,  -0.5792),
    ("Herault",                "Montpellier",            43.6119,   3.8772),
    ("Ille-et-Vilaine",        "Rennes",                 48.1173,  -1.6778),
    ("Indre",                  "Chateauroux",            46.8108,   1.6917),
    ("Indre-et-Loire",         "Tours",                  47.3941,   0.6848),
    ("Isere",                  "Grenoble",               45.1885,   5.7245),
    ("Jura",                   "Lons-le-Saunier",        46.6744,   5.5536),
    ("Landes",                 "Mont-de-Marsan",         43.8897,  -0.5000),
    ("Loir-et-Cher",           "Blois",                  47.5861,   1.3361),
    ("Loire",                  "Saint-Etienne",          45.4347,   4.3900),
    ("Haute-Loire",            "Le Puy-en-Velay",        45.0436,   3.8853),
    ("Loire-Atlantique",       "Nantes",                 47.2184,  -1.5536),
    ("Loiret",                 "Orleans",                47.9025,   1.9090),
    ("Lot",                    "Cahors",                 44.4497,   1.4411),
    ("Lot-et-Garonne",         "Agen",                   44.2008,   0.6167),
    ("Lozere",                 "Mende",                  44.5194,   3.5011),
    ("Maine-et-Loire",         "Angers",                 47.4736,  -0.5542),
    ("Manche",                 "Saint-Lo",               49.1175,  -1.0906),
    ("Marne",                  "Chalons-en-Champagne",   48.9575,   4.3681),
    ("Haute-Marne",            "Chaumont",               48.1117,   5.1389),
    ("Mayenne",                "Laval",                  48.0731,  -0.7683),
    ("Meurthe-et-Moselle",     "Nancy",                  48.6921,   6.1844),
    ("Meuse",                  "Bar-le-Duc",             48.7728,   5.1606),
    ("Morbihan",               "Vannes",                 47.6578,  -2.7603),
    ("Moselle",                "Metz",                   49.1196,   6.1757),
    ("Nievre",                 "Nevers",                 46.9897,   3.1581),
    ("Nord",                   "Lille",                  50.6292,   3.0573),
    ("Oise",                   "Beauvais",               49.4294,   2.0808),
    ("Orne",                   "Alencon",                48.4311,   0.0919),
    ("Pas-de-Calais",          "Arras",                  50.2917,   2.7783),
    ("Puy-de-Dome",            "Clermont-Ferrand",       45.7772,   3.0870),
    ("Pyrenees-Atlantiques",   "Pau",                    43.2951,  -0.3708),
    ("Hautes-Pyrenees",        "Tarbes",                 43.2328,   0.0781),
    ("Pyrenees-Orientales",    "Perpignan",              42.6887,   2.8948),
    ("Bas-Rhin",               "Strasbourg",             48.5734,   7.7521),
    ("Haut-Rhin",              "Colmar",                 48.0800,   7.3589),
    ("Rhone",                  "Lyon",                   45.7640,   4.8357),
    ("Haute-Saone",            "Vesoul",                 47.6219,   6.1561),
    ("Saone-et-Loire",         "Macon",                  46.3058,   4.8319),
    ("Sarthe",                 "Le Mans",                48.0014,   0.1997),
    ("Savoie",                 "Chambery",               45.5646,   5.9178),
    ("Haute-Savoie",           "Annecy",                 45.8992,   6.1294),
    ("Paris",                  "Paris",                  48.8566,   2.3522),
    ("Seine-Maritime",         "Rouen",                  49.4431,   1.0993),
    ("Seine-et-Marne",         "Melun",                  48.5406,   2.6589),
    ("Yvelines",               "Versailles",             48.8014,   2.1301),
    ("Deux-Sevres",            "Niort",                  46.3244,  -0.4594),
    ("Somme",                  "Amiens",                 49.8942,   2.2958),
    ("Tarn",                   "Albi",                   43.9293,   2.1488),
    ("Tarn-et-Garonne",        "Montauban",              44.0181,   1.3556),
    ("Var",                    "Toulon",                 43.1242,   5.9280),
    ("Vaucluse",               "Avignon",                43.9493,   4.8058),
    ("Vendee",                 "La Roche-sur-Yon",       46.6703,  -1.4267),
    ("Vienne",                 "Poitiers",               46.5803,   0.3400),
    ("Haute-Vienne",           "Limoges",                45.8336,   1.2611),
    ("Vosges",                 "Epinal",                 48.1736,   6.4497),
    ("Yonne",                  "Auxerre",                47.7981,   3.5681),
    ("Territoire de Belfort",  "Belfort",                47.6386,   6.8644),
    ("Essonne",                "Evry-Courcouronnes",     48.6312,   2.4275),
    ("Hauts-de-Seine",         "Nanterre",               48.8924,   2.2069),
    ("Seine-Saint-Denis",      "Bobigny",                48.9100,   2.4406),
    ("Val-de-Marne",           "Creteil",                48.7882,   2.4558),
    ("Val-d-Oise",             "Cergy",                  49.0360,   2.0631),
]

N_CITIES = len(PREFECTURAS)
NOMBRES  = [p[1] for p in PREFECTURAS]
DEPTS    = [p[0] for p in PREFECTURAS]
LATS     = np.array([p[2] for p in PREFECTURAS])
LONS     = np.array([p[3] for p in PREFECTURAS])

print(f"{N_CITIES} prefecturas cargadas")
print(f"Latitud  : [{LATS.min():.2f}, {LATS.max():.2f}]")
print(f"Longitud : [{LONS.min():.2f}, {LONS.max():.2f}]")\
"""

# ---------------------------------------------------------------------------
# Nueva celda de distancia y funcion objetivo
# ---------------------------------------------------------------------------
NEW_COST_CODE = """\
# ---------------------------------------------------------------------------
# Distancia haversine y funcion objetivo del TSP
# ---------------------------------------------------------------------------

def haversine_km(lat1, lon1, lat2, lon2):
    \"\"\"Distancia en km entre dos puntos en grados decimales (formula haversine).\"\"\"
    R    = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a    = (sin(dlat / 2)**2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2)
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def build_dist_matrix():
    \"\"\"Matriz simetrica N x N de distancias haversine en km entre prefecturas.\"\"\"
    D = np.zeros((N_CITIES, N_CITIES))
    for i in range(N_CITIES):
        for j in range(i + 1, N_CITIES):
            d       = haversine_km(LATS[i], LONS[i], LATS[j], LONS[j])
            D[i, j] = d
            D[j, i] = d
    return D


def tour_cost(route, D):
    \"\"\"
    Costo total en EUR de una ruta completa (con regreso al origen).

    costo = distancia * (combustible + peajes) + tiempo * valor_hora
    \"\"\"
    km_total     = sum(D[route[i], route[(i + 1) % N_CITIES]] for i in range(N_CITIES))
    costo_viaje  = km_total * COSTO_KM
    costo_tiempo = (km_total / VEL_KMH) * COSTO_HORA
    return costo_viaje + costo_tiempo


D = build_dist_matrix()

idx_max = int(D.argmax())
print(f"Matriz {D.shape} construida.")
print(f"Par mas lejano: {NOMBRES[idx_max // N_CITIES]} — {NOMBRES[idx_max % N_CITIES]}  ({D.max():,.0f} km)")
print(f"Factor costo total: {COSTO_KM + COSTO_HORA / VEL_KMH:.4f} EUR/km")\
"""

# ---------------------------------------------------------------------------
# Aplicar cambios al notebook
# ---------------------------------------------------------------------------
with open(NB_IN) as fh:
    nb = json.load(fh)

cells = nb["cells"]

# Actualizar el kernel/idioma si es necesario (no critico, lo dejamos)
# 1. Reemplazar celda 0 (titulo)
cells[0] = md_cell(NEW_TITLE_MD)

# 2. Reemplazar celda 2 (imports + config global)
cells[2] = code_cell(NEW_CONFIG_CODE)

# 3. Reemplazar celda 3 (markdown de datos)
cells[3] = md_cell(NEW_DATA_MD)

# 4. Reemplazar celda 4 (CAPITALES)
cells[4] = code_cell(NEW_DATA_CODE)

# 5. Reemplazar celda 5 (distancia y funcion objetivo)
cells[5] = code_cell(NEW_COST_CODE)

# 6. Reemplazar referencias a Mexico/MXN en celdas de markdown
for i, c in enumerate(cells):
    if c["cell_type"] == "markdown":
        src = "".join(c["source"])
        src = src.replace("México", "Francia")
        src = src.replace("Mexico", "Francia")
        src = src.replace("MXN", "EUR")
        src = src.replace("32 capital", "96 prefectura")
        src = src.replace("32 estado", "96 departamento")
        src = src.replace("mapa de México", "mapa de Francia")
        src = src.replace("mapa de Mexico", "mapa de Francia")
        cells[i]["source"] = src

# 7. Actualizar referencias en celdas de codigo (comentarios y strings)
for i, c in enumerate(cells):
    if c["cell_type"] == "code":
        src = "".join(c["source"])
        src = src.replace("CAPITALES", "PREFECTURAS")
        src = src.replace("capitales", "prefecturas")
        src = src.replace("MXN", "EUR")
        src = src.replace("Mexico", "Francia")
        src = src.replace("México", "Francia")
        src = src.replace("32", "96")
        cells[i]["source"] = src

nb["cells"] = cells

with open(NB_OUT, "w") as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)

print(f"\nNotebook 03 creado: {NB_OUT}  ({len(nb['cells'])} celdas)")
