# !pip install numpy matplotlib pillow deap

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
def display(*a, **kw): pass  # stub fuera de Jupyter
Image = lambda *a, **kw: None  # stub fuera de Jupyter

from deap import base, creator, tools, algorithms

Path('notebooks/outputs').mkdir(exist_ok=True)

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
SEED_DEMO = 7     # semilla para corridas de demostracion

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
    ("Cote-d-Or",              "Dijon",                  47.9620,   5.0415),
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
    ("Hautes-Pyrenees",        "Tarbes",                 43.2968,   0.0781),
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
    ("Deux-Sevres",            "Niort",                  46.9644,  -0.4594),
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
print(f"Longitud : [{LONS.min():.2f}, {LONS.max():.2f}]")

# ---------------------------------------------------------------------------
# Distancia haversine y funcion objetivo del TSP
# ---------------------------------------------------------------------------

def haversine_km(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos en grados decimales (formula haversine)."""
    R    = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a    = (sin(dlat / 2)**2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2)
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def build_dist_matrix():
    """Matriz simetrica N x N de distancias haversine en km entre prefecturas."""
    D = np.zeros((N_CITIES, N_CITIES))
    for i in range(N_CITIES):
        for j in range(i + 1, N_CITIES):
            d       = haversine_km(LATS[i], LONS[i], LATS[j], LONS[j])
            D[i, j] = d
            D[j, i] = d
    return D


def tour_cost(route, D):
    """
    Costo total en EUR de una ruta completa (con regreso al origen).

    costo = distancia * (combustible + peajes) + tiempo * valor_hora
    """
    km_total     = sum(D[route[i], route[(i + 1) % N_CITIES]] for i in range(N_CITIES))
    costo_viaje  = km_total * COSTO_KM
    costo_tiempo = (km_total / VEL_KMH) * COSTO_HORA
    return costo_viaje + costo_tiempo


D = build_dist_matrix()

idx_max = int(D.argmax())
print(f"Matriz {D.shape} construida.")
print(f"Par mas lejano: {NOMBRES[idx_max // N_CITIES]} — {NOMBRES[idx_max % N_CITIES]}  ({D.max():,.0f} km)")
print(f"Factor costo total: {COSTO_KM + COSTO_HORA / VEL_KMH:.4f} EUR/km")

# ── Implementación ACO ────────────────────────────────────────────────────────
def run_aco(D, seed, track_history=False):
    """ACO con depósito proporcional a la calidad de cada hormiga."""
    rng = np.random.default_rng(seed)

    with np.errstate(divide='ignore', invalid='ignore'):
        eta = np.where(D > 0, 1.0 / D, 0.0)

    tau        = np.ones((N_CITIES, N_CITIES))
    best_route = None
    best_cost  = np.inf
    history    = [] if track_history else None

    for _ in range(ACO_ITERS):
        all_routes, all_costs = [], []

        for _ in range(ACO_N_ANTS):
            start   = int(rng.integers(N_CITIES))
            route   = [start]
            visited = np.zeros(N_CITIES, dtype=bool)
            visited[start] = True

            for _ in range(N_CITIES - 1):
                current      = route[-1]
                probs        = (tau[current] ** ACO_ALPHA) * (eta[current] ** ACO_BETA)
                probs[visited] = 0.0
                total        = probs.sum()
                if total == 0:
                    probs = (~visited).astype(float)
                    total = probs.sum()
                nxt = int(rng.choice(N_CITIES, p=probs / total))
                route.append(nxt)
                visited[nxt] = True

            cost = tour_cost(route, D)
            all_routes.append(route)
            all_costs.append(cost)
            if cost < best_cost:
                best_cost, best_route = cost, route[:]

        # Evaporación + depósito
        tau *= (1.0 - ACO_RHO)
        for route, cost in zip(all_routes, all_costs):
            delta = ACO_Q / cost
            for i in range(N_CITIES):
                a, b         = route[i], route[(i+1) % N_CITIES]
                tau[a, b]   += delta
                tau[b, a]   += delta

        if track_history:
            history.append(best_cost)

    result = {'costo': best_cost, 'ruta': best_route}
    if track_history:
        result['history'] = history
    return result

# ── Corrida demo ACO ──────────────────────────────────────────────────────────
print('Ejecutando ACO (demo, seed={})...'.format(SEED_DEMO))
t0       = time.time()
aco_demo = run_aco(D, seed=SEED_DEMO, track_history=True)
print(f'  Costo final: {aco_demo["costo"]:,.0f} EUR   ({time.time()-t0:.1f}s)')
print(f'  Primeras 6 ciudades: {", ".join(NOMBRES[i] for i in aco_demo["ruta"][:6])} ...')

# ── GIF convergencia ACO ──────────────────────────────────────────────────────
def plot_route(ax, ruta, color, lw=1.2, alpha=0.8):
    """Dibuja la ruta sobre el plano lon/lat."""
    ruta_cerrada = ruta + [ruta[0]]
    lons_r = [LONS[i] for i in ruta_cerrada]
    lats_r = [LATS[i] for i in ruta_cerrada]
    ax.plot(lons_r, lats_r, '-', color=color, lw=lw, alpha=alpha)


hist_aco = aco_demo['history']
ruta_aco = aco_demo['ruta']
FRAMES   = 60
pasos    = np.linspace(0, len(hist_aco) - 1, FRAMES, dtype=int)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax_conv, ax_map = axes

# Panel convergencia
ax_conv.set_xlim(0, len(hist_aco))
ax_conv.set_ylim(min(hist_aco) * 0.97, hist_aco[0] * 1.02)
ax_conv.set_xlabel('Iteración')
ax_conv.set_ylabel('Mejor costo (EUR)')
ax_conv.set_title('Convergencia ACO')
ax_conv.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
    lambda x, _: f'{x:,.0f}'))
line_conv, = ax_conv.plot([], [], 'b-', lw=2)
pt_conv,   = ax_conv.plot([], [], 'ro', ms=5)

# Panel mapa
ax_map.scatter(LONS, LATS, s=30, color='steelblue', zorder=3)
ax_map.set_xlim(LONS.min() - 2, LONS.max() + 2)
ax_map.set_ylim(LATS.min() - 2, LATS.max() + 2)
ax_map.set_xlabel('Longitud')
ax_map.set_ylabel('Latitud')
ax_map.set_title('Mejor ruta ACO')
line_ruta, = ax_map.plot([], [], 'b-', lw=1, alpha=0.7)
costo_text = ax_map.text(0.02, 0.97, '', transform=ax_map.transAxes,
                          va='top', fontsize=9, color='navy')

plt.tight_layout()

def update(frame_idx):
    k = pasos[frame_idx]
    # Convergencia
    line_conv.set_data(range(k + 1), hist_aco[:k + 1])
    pt_conv.set_data([k], [hist_aco[k]])
    # Ruta (la mejor encontrada hasta la iteración k es la global hasta ese punto)
    mejor_hasta_k = hist_aco[k]
    ruta_cerrada  = ruta_aco + [ruta_aco[0]]
    lons_r = [LONS[i] for i in ruta_cerrada]
    lats_r = [LATS[i] for i in ruta_cerrada]
    line_ruta.set_data(lons_r, lats_r)
    costo_text.set_text(f'Iter {k}\n{mejor_hasta_k:,.0f} EUR')
    return line_conv, pt_conv, line_ruta, costo_text

ani_aco = FuncAnimation(fig, update, frames=FRAMES, interval=80, blit=True)
ani_aco.save('notebooks/outputs/aco_convergencia.gif', writer=PillowWriter(fps=20))
plt.close(fig)

print('GIF guardado en outputs/aco_convergencia.gif')
display(Image('notebooks/outputs/aco_convergencia.gif'))

# ── Implementación GA ─────────────────────────────────────────────────────────
def _init_ga_toolbox(D):
    """Configura DEAP para TSP: OX crossover + shuffle mutation."""
    for attr in ('FitnessMinTSP', 'RouteTSP'):
        if hasattr(creator, attr):
            delattr(creator, attr)
    creator.create('FitnessMinTSP', base.Fitness, weights=(-1.0,))
    creator.create('RouteTSP', list, fitness=creator.FitnessMinTSP)

    tb = base.Toolbox()
    tb.register('indices',    random.sample, range(N_CITIES), N_CITIES)
    tb.register('individual', tools.initIterate, creator.RouteTSP, tb.indices)
    tb.register('population', tools.initRepeat, list, tb.individual)
    tb.register('evaluate',   lambda ind: (tour_cost(list(ind), D),))
    tb.register('mate',       tools.cxOrdered)
    tb.register('mutate',     tools.mutShuffleIndexes, indpb=2.0 / N_CITIES)
    tb.register('select',     tools.selTournament, tournsize=5)
    return tb


def run_ga(D, seed, track_history=False):
    """GA para TSP. track_history=True registra mejor costo por generación."""
    np.random.seed(seed)
    random.seed(seed)

    tb  = _init_ga_toolbox(D)
    pop = tb.population(n=GA_POP)
    hof = tools.HallOfFame(1)

    history = [] if track_history else None

    if track_history:
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register('min', np.min)
        for _ in range(GA_GENS):
            pop, _ = algorithms.eaSimple(
                pop, tb, cxpb=GA_CXPB, mutpb=GA_MUTPB,
                ngen=1, stats=stats, halloffame=hof, verbose=False
            )
            history.append(float(hof[0].fitness.values[0]))
    else:
        pop, _ = algorithms.eaSimple(
            pop, tb, cxpb=GA_CXPB, mutpb=GA_MUTPB,
            ngen=GA_GENS, stats=None, halloffame=hof, verbose=False
        )

    result = {'costo': float(hof[0].fitness.values[0]), 'ruta': list(hof[0])}
    if track_history:
        result['history'] = history
    return result

# ── Corrida demo GA ───────────────────────────────────────────────────────────
print('Ejecutando GA (demo, seed={})...'.format(SEED_DEMO))
t0      = time.time()
ga_demo = run_ga(D, seed=SEED_DEMO, track_history=True)
print(f'  Costo final: {ga_demo["costo"]:,.0f} EUR   ({time.time()-t0:.1f}s)')
print(f'  Primeras 6 ciudades: {", ".join(NOMBRES[i] for i in ga_demo["ruta"][:6])} ...')

# ── GIF convergencia GA ───────────────────────────────────────────────────────
hist_ga = ga_demo['history']
ruta_ga = ga_demo['ruta']
pasos_ga = np.linspace(0, len(hist_ga) - 1, FRAMES, dtype=int)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax_conv2, ax_map2 = axes

ax_conv2.set_xlim(0, len(hist_ga))
ax_conv2.set_ylim(min(hist_ga) * 0.97, hist_ga[0] * 1.02)
ax_conv2.set_xlabel('Generación')
ax_conv2.set_ylabel('Mejor costo (EUR)')
ax_conv2.set_title('Convergencia GA')
ax_conv2.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
    lambda x, _: f'{x:,.0f}'))
line_conv2, = ax_conv2.plot([], [], 'g-', lw=2)
pt_conv2,   = ax_conv2.plot([], [], 'ro', ms=5)

ax_map2.scatter(LONS, LATS, s=30, color='steelblue', zorder=3)
ax_map2.set_xlim(LONS.min() - 2, LONS.max() + 2)
ax_map2.set_ylim(LATS.min() - 2, LATS.max() + 2)
ax_map2.set_xlabel('Longitud')
ax_map2.set_ylabel('Latitud')
ax_map2.set_title('Mejor ruta GA')
line_ruta2, = ax_map2.plot([], [], 'g-', lw=1, alpha=0.7)
costo_text2 = ax_map2.text(0.02, 0.97, '', transform=ax_map2.transAxes,
                            va='top', fontsize=9, color='darkgreen')

plt.tight_layout()

def update_ga(frame_idx):
    k = pasos_ga[frame_idx]
    line_conv2.set_data(range(k + 1), hist_ga[:k + 1])
    pt_conv2.set_data([k], [hist_ga[k]])
    ruta_cerrada = ruta_ga + [ruta_ga[0]]
    lons_r = [LONS[i] for i in ruta_cerrada]
    lats_r = [LATS[i] for i in ruta_cerrada]
    line_ruta2.set_data(lons_r, lats_r)
    costo_text2.set_text(f'Gen {k}\n{hist_ga[k]:,.0f} EUR')
    return line_conv2, pt_conv2, line_ruta2, costo_text2

ani_ga = FuncAnimation(fig, update_ga, frames=FRAMES, interval=80, blit=True)
ani_ga.save('notebooks/outputs/ga_convergencia.gif', writer=PillowWriter(fps=20))
plt.close(fig)

print('GIF guardado en outputs/ga_convergencia.gif')
display(Image('notebooks/outputs/ga_convergencia.gif'))

# ── 30 corridas ───────────────────────────────────────────────────────────────
import json

CACHE_FILE = Path('notebooks/outputs/resultados_tsp.json')

if CACHE_FILE.exists():
    with open(CACHE_FILE, encoding='utf-8') as fp:
        resultados = json.load(fp)
    print('Resultados cargados desde cache.')
else:
    resultados = []
    for nombre, runner in [('ACO', run_aco), ('GA', run_ga)]:
        costos, rutas = [], []
        t0 = time.time()
        for seed in range(N_RUNS):
            res = runner(D=D, seed=seed)
            costos.append(res['costo'])
            rutas.append(res['ruta'])
        mejor_idx = int(np.argmin(costos))
        print(f'{nombre}: media={np.mean(costos):,.0f}  std={np.std(costos):,.0f}  '
              f'mejor={np.min(costos):,.0f}  peor={np.max(costos):,.0f}  EUR  '
              f't={time.time()-t0:.1f}s')
        resultados.append({
            'metodo':      nombre,
            'costo_media': float(np.mean(costos)),
            'costo_std':   float(np.std(costos)),
            'costo_mejor': float(np.min(costos)),
            'costo_peor':  float(np.max(costos)),
            'mejor_ruta':  rutas[mejor_idx],
        })
    with open(CACHE_FILE, 'w', encoding='utf-8') as fp:
        json.dump(resultados, fp, indent=2, ensure_ascii=False)
    print('Guardado en', CACHE_FILE)

# ── Tabla comparativa ─────────────────────────────────────────────────────────
import pandas as pd

filas = []
for r in resultados:
    filas.append({
        'Método':          r['metodo'],
        'Media (EUR)':     r['costo_media'],
        'Std (EUR)':       r['costo_std'],
        'Mejor (EUR)':     r['costo_mejor'],
        'Peor (EUR)':      r['costo_peor'],
        'CV (%)':          r['costo_std'] / r['costo_media'] * 100,
    })

df = pd.DataFrame(filas).set_index('Método')
fmt = {
    'Media (EUR)': '{:,.0f}',
    'Std (EUR)':   '{:,.0f}',
    'Mejor (EUR)': '{:,.0f}',
    'Peor (EUR)':  '{:,.0f}',
    'CV (%)':      '{:.2f}',
}
# df.style (requiere jinja2) — omitido fuera de Jupyter
print(df.to_string())

# ── Figura 1. Convergencia ACO vs GA ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

# Normalizar ejes al mismo largo (GA=500 gens, ACO=300 iters → usar % de progreso)
pct_aco = np.linspace(0, 100, len(hist_aco))
pct_ga  = np.linspace(0, 100, len(hist_ga))

ax.plot(pct_aco, hist_aco, 'b-',  lw=2,   label=f'ACO  (final {aco_demo["costo"]:,.0f} EUR)')
ax.plot(pct_ga,  hist_ga,  'g--', lw=2,   label=f'GA   (final {ga_demo["costo"]:,.0f} EUR)')
ax.axhline(min(hist_aco), color='blue',  ls=':', lw=1, alpha=0.5)
ax.axhline(min(hist_ga),  color='green', ls=':', lw=1, alpha=0.5)

ax.set_xlabel('Progreso (%)')
ax.set_ylabel('Mejor costo (EUR)')
ax.set_title('Figura 1. Convergencia ACO vs GA — TSP 96 Capitales (seed=7)')
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.legend()
plt.tight_layout()
fig.savefig('notebooks/outputs/convergencia_aco_ga.png', dpi=120, bbox_inches='tight')
plt.show()

# ── Figura 2. Mejor ruta ACO y GA ────────────────────────────────────────────
ruta_aco_best = resultados[0]['mejor_ruta']
ruta_ga_best  = resultados[1]['mejor_ruta']
costo_aco_best = resultados[0]['costo_mejor']
costo_ga_best  = resultados[1]['costo_mejor']

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

for ax, ruta, costo, metodo, color in [
    (axes[0], ruta_aco_best, costo_aco_best, 'ACO', 'royalblue'),
    (axes[1], ruta_ga_best,  costo_ga_best,  'GA',  'seagreen'),
]:
    # Ruta cerrada
    rc   = ruta + [ruta[0]]
    lons_r = [LONS[i] for i in rc]
    lats_r = [LATS[i] for i in rc]
    ax.plot(lons_r, lats_r, '-', color=color, lw=1.5, alpha=0.7, zorder=1)

    # Ciudades
    ax.scatter(LONS, LATS, s=45, color='white', edgecolors=color,
               linewidths=1.2, zorder=2)

    # Etiquetas — solo las que caben sin solaparse (muestra todas, letra pequeña)
    for i, nombre in enumerate(NOMBRES):
        ax.annotate(nombre, (LONS[i], LATS[i]),
                    fontsize=5.5, ha='center', va='bottom',
                    xytext=(0, 4), textcoords='offset points')

    # Ciudad de inicio
    inicio = ruta[0]
    ax.scatter([LONS[inicio]], [LATS[inicio]], s=120, color='gold',
               edgecolors='black', linewidths=1.2, zorder=3)

    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title(f'Figura 2{"a" if metodo=="ACO" else "b"}. '
                 f'Mejor ruta {metodo}\n{costo:,.0f} EUR')
    ax.set_xlim(LONS.min() - 1.5, LONS.max() + 1.5)
    ax.set_ylim(LATS.min() - 1.5, LATS.max() + 1.5)

estrella = mpatches.Patch(color='gold', label='Ciudad de inicio')
fig.legend(handles=[estrella], loc='lower center', ncol=1)
plt.tight_layout()
fig.savefig('notebooks/outputs/mejor_ruta_comparativa.png', dpi=120, bbox_inches='tight')
plt.show()

# ── GIF: mejor ruta ACO construyéndose ciudad a ciudad ───────────────────────
ruta_anim = ruta_aco_best
n_frames  = N_CITIES + 5   # +5 frames finales para que se aprecie la ruta completa

fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(LONS, LATS, s=35, color='steelblue', zorder=2)
for i, nombre in enumerate(NOMBRES):
    ax.annotate(nombre, (LONS[i], LATS[i]),
                fontsize=5.5, ha='center', va='bottom',
                xytext=(0, 4), textcoords='offset points')
ax.set_xlim(LONS.min() - 1.5, LONS.max() + 1.5)
ax.set_ylim(LATS.min() - 1.5, LATS.max() + 1.5)
ax.set_xlabel('Longitud')
ax.set_ylabel('Latitud')
ax.set_title('Construcción de la mejor ruta ACO')
linea_mapa, = ax.plot([], [], 'b-', lw=1.5, alpha=0.8)
punto_actual, = ax.plot([], [], 'ro', ms=8, zorder=4)
n_text = ax.text(0.02, 0.97, '', transform=ax.transAxes, va='top', fontsize=9)
plt.tight_layout()

def update_ruta(frame):
    k = min(frame + 1, N_CITIES)
    segmento = ruta_anim[:k]
    if k == N_CITIES:
        segmento = ruta_anim + [ruta_anim[0]]   # cerrar el tour
    lons_s = [LONS[i] for i in segmento]
    lats_s = [LATS[i] for i in segmento]
    linea_mapa.set_data(lons_s, lats_s)
    if k < N_CITIES:
        punto_actual.set_data([LONS[ruta_anim[k-1]]], [LATS[ruta_anim[k-1]]])
    else:
        punto_actual.set_data([], [])
    n_text.set_text(f'Ciudad {k}/{N_CITIES}')
    return linea_mapa, punto_actual, n_text

ani_ruta = FuncAnimation(fig, update_ruta, frames=n_frames, interval=200, blit=True)
ani_ruta.save('notebooks/outputs/aco_ruta_construccion.gif', writer=PillowWriter(fps=5))
plt.close(fig)

print('GIF guardado en outputs/aco_ruta_construccion.gif')
display(Image('notebooks/outputs/aco_ruta_construccion.gif'))