"""
Optimización heurística — EA, PSO, Evolución Diferencial
Funciones: Rosenbrock, Rastrigin, Schwefel, Griewank (2D y 3D)
           Goldstein-Price, Camel 6-hump (solo 2D)
30 corridas por método/función/dimensión
Uso: python scripts/heuristicos.py
Salida: resultados_heuristicos.json
"""

import numpy as np
import json
import time
from scipy.optimize import differential_evolution
from deap import base, creator, tools, algorithms
import pyswarms as ps
import warnings
warnings.filterwarnings("ignore")

# ── Constantes ──────────────────────────────────────────────────────────────
N_RUNS   = 30
A        = 10   # parametro de Rastrigin

# Dominios por funcion: usados tanto para GD como para heuristicos
BOUNDS_ND = {   # funciones validas en 2D y 3D (dominio simetrico [lo,hi]^n)
    'Rosenbrock':  (-5.0,   5.0),
    'Rastrigin':   (-5.0,   5.0),
    'Schwefel':    (-500.0, 500.0),
    'Griewank':    (-600.0, 600.0),
}
BOUNDS_2D = {   # funciones exclusivamente 2D (caja simetrica por defecto)
    'Goldstein-Price': (-2.0, 2.0),
    'Camel 6-hump':    (-3.0, 3.0),
}

# Camel 6-hump tiene dominios distintos por variable: x1 in [-3,3], x2 in [-2,2].
BOUNDS_PERDIM = {
    'Camel 6-hump': [(-3.0, 3.0), (-2.0, 2.0)],
}


def get_bounds(fname, ndim):
    """Lista de pares (lo, hi) de longitud ndim para la funcion dada."""
    if fname in BOUNDS_PERDIM:
        return list(BOUNDS_PERDIM[fname])
    lo, hi = BOUNDS_ND.get(fname, BOUNDS_2D.get(fname))
    return [(lo, hi)] * ndim


# Valor minimo global conocido de cada funcion (para medir la tasa de exito
# como distancia al optimo |f - f_opt| < TOL, no como umbral absoluto).
F_OPT = {
    'Rosenbrock':       0.0,
    'Rastrigin':        0.0,
    'Schwefel':         0.0,       # con la constante 418.9829*n el minimo es ~0
    'Griewank':         0.0,
    'Goldstein-Price':  3.0,
    'Camel 6-hump':    -1.0316284535,
}

# Tolerancia de exito por funcion (distancia al optimo global). Valores fijados
# a priori segun la escala y dificultad de cada paisaje, no ajustados a posteriori.
TOL = {
    'Rosenbrock':      1e-4,   # valle suave: se exige convergencia fina
    'Rastrigin':       1e-1,   # multimodal: basta caer en el pozo global
    'Schwefel':        1.0,    # tolerancia amplia por la gran escala del dominio
    'Griewank':        1e-2,
    'Goldstein-Price': 1e-2,
    'Camel 6-hump':    1e-2,
}

# EA
EA_POP   = 100
EA_GENS  = 500
EA_CXPB  = 0.7
EA_MUTPB = 0.2

# PSO
PSO_N     = 50
PSO_ITERS = 500
PSO_OPTS  = {'c1': 2.05, 'c2': 2.05, 'w': 0.729}

# DE
DE_CONF = dict(strategy='best1bin', maxiter=1000, popsize=15,
               tol=1e-7, mutation=(0.5, 1.0), recombination=0.7)


# ── Funciones de prueba ──────────────────────────────────────────────────────
def rosenbrock(x):
    x = np.asarray(x, dtype=float)
    return float(np.sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1.0 - x[:-1])**2))

def rastrigin(x):
    x = np.asarray(x, dtype=float)
    return float(A * len(x) + np.sum(x**2 - A * np.cos(2 * np.pi * x)))

def schwefel(x):
    x = np.asarray(x, dtype=float)
    return float(418.9829 * len(x) - np.sum(x * np.sin(np.sqrt(np.abs(x)))))

def griewank(x):
    x = np.asarray(x, dtype=float)
    suma = np.sum(x**2) / 4000
    prod = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
    return float(1 + suma - prod)

def goldstein_price(x):
    x = np.asarray(x, dtype=float)
    x1, x2 = float(x[0]), float(x[1])
    a = (1 + (x1 + x2 + 1)**2
         * (19 - 14*x1 + 3*x1**2 - 14*x2 + 6*x1*x2 + 3*x2**2))
    b = (30 + (2*x1 - 3*x2)**2
         * (18 - 32*x1 + 12*x1**2 + 48*x2 - 36*x1*x2 + 27*x2**2))
    return float(a * b)

def camel_6hump(x):
    x = np.asarray(x, dtype=float)
    x1, x2 = float(x[0]), float(x[1])
    return float(
        (4 - 2.1*x1**2 + x1**4 / 3) * x1**2
        + x1 * x2
        + (-4 + 4*x2**2) * x2**2
    )

# Funciones nD (validas en 2D y 3D) y funciones solo 2D
FUNCIONES_ND = {
    'Rosenbrock':  rosenbrock,
    'Rastrigin':   rastrigin,
    'Schwefel':    schwefel,
    'Griewank':    griewank,
}
FUNCIONES_2D = {
    'Goldstein-Price': goldstein_price,
    'Camel 6-hump':    camel_6hump,
}
FUNCIONES = {**FUNCIONES_ND, **FUNCIONES_2D}


# ── EA (DEAP) ────────────────────────────────────────────────────────────────
def _check_bounds(bounds):
    """Decorador DEAP que recorta cada hijo a la caja [lo,hi] por dimension.

    cxBlend y mutGaussian pueden generar valores fuera del dominio; sin este
    recorte los individuos divergen (p. ej. Schwefel -> f ~ -1e9, fuera de
    [-500,500]). El recorte garantiza que la busqueda permanece en el dominio.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            offspring = func(*args, **kwargs)
            for child in offspring:
                for i, (lo, hi) in enumerate(bounds):
                    if child[i] < lo:
                        child[i] = lo
                    elif child[i] > hi:
                        child[i] = hi
            return offspring
        return wrapper
    return decorator


def _init_ea_toolbox(f, ndim, bounds):
    import random
    from functools import partial
    for attr in ('FitnessMin', 'Individual'):
        if hasattr(creator, attr):
            delattr(creator, attr)
    creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMin)
    tb = base.Toolbox()
    # Inicializacion por dimension (respeta dominios distintos por variable)
    attr_gens = [partial(random.uniform, lo, hi) for (lo, hi) in bounds]
    tb.register('individual', tools.initCycle, creator.Individual, attr_gens, n=1)
    tb.register('population', tools.initRepeat, list, tb.individual)
    tb.register('evaluate',   lambda ind: (f(np.array(ind)),))
    tb.register('mate',       tools.cxBlend, alpha=0.5)
    tb.register('mutate',     tools.mutGaussian, mu=0, sigma=0.5, indpb=0.2)
    tb.register('select',     tools.selTournament, tournsize=3)
    # Recorte al dominio tras cruce y mutacion (corrige la divergencia del EA)
    tb.decorate('mate',   _check_bounds(bounds))
    tb.decorate('mutate', _check_bounds(bounds))
    return tb


def run_ea(fname, ndim, seed):
    import random
    np.random.seed(seed)
    random.seed(seed)
    f      = FUNCIONES[fname]
    bounds = get_bounds(fname, ndim)
    tb     = _init_ea_toolbox(f, ndim, bounds)
    hof    = tools.HallOfFame(1)
    algorithms.eaSimple(
        tb.population(n=EA_POP), tb,
        cxpb=EA_CXPB, mutpb=EA_MUTPB, ngen=EA_GENS,
        stats=None, halloffame=hof, verbose=False
    )
    return {'f_final': hof[0].fitness.values[0], 'n_evals': EA_POP * (EA_GENS + 1)}


# ── PSO (pyswarms) ───────────────────────────────────────────────────────────
def run_pso(fname, ndim, seed):
    np.random.seed(seed)
    f  = FUNCIONES[fname]
    bb = get_bounds(fname, ndim)

    def batch_f(X):
        return np.array([f(X[i]) for i in range(X.shape[0])])

    bounds = (np.array([lo for lo, _ in bb]), np.array([hi for _, hi in bb]))
    opt    = ps.single.GlobalBestPSO(n_particles=PSO_N, dimensions=ndim,
                                      options=PSO_OPTS, bounds=bounds)
    cost, _ = opt.optimize(batch_f, iters=PSO_ITERS, verbose=False)
    return {'f_final': float(cost), 'n_evals': PSO_N * PSO_ITERS}


# ── Evolución Diferencial (scipy) ────────────────────────────────────────────
def run_de(fname, ndim, seed):
    f      = FUNCIONES[fname]
    bounds = get_bounds(fname, ndim)
    result = differential_evolution(f, bounds, seed=seed, **DE_CONF)
    return {'f_final': float(result.fun), 'n_evals': int(result.nfev)}


# ── Experimentos ─────────────────────────────────────────────────────────────
METODOS = {'EA': run_ea, 'PSO': run_pso, 'DE': run_de}

def correr_experimentos():
    """
    Corre N_RUNS corridas de EA/PSO/DE sobre las 6 funciones de prueba.
    Funciones nD: 2D y 3D. Funciones 2D-only: solo 2D.
    """
    registros = []

    for fname, f in FUNCIONES.items():
        dims = [2, 3] if fname in FUNCIONES_ND else [2]
        for ndim in dims:
            for metodo, runner in METODOS.items():
                f_vals, evals = [], []
                t0 = time.time()
                for seed in range(N_RUNS):
                    res = runner(fname, ndim, seed)
                    f_vals.append(res['f_final'])
                    evals.append(res['n_evals'])

                tasa = np.mean(np.abs(np.array(f_vals) - F_OPT[fname]) < TOL[fname])
                print(
                    f'{metodo:4s} | {fname:18s} {ndim}D | '
                    f'media={np.mean(f_vals):.3e}  std={np.std(f_vals):.3e}  '
                    f'mejor={np.min(f_vals):.3e}  '
                    f'exito={tasa*100:.0f}%  '
                    f'evals={int(np.mean(evals))}  '
                    f't={time.time()-t0:.1f}s'
                )
                registros.append({
                    'metodo':       metodo,
                    'funcion':      fname,
                    'ndim':         ndim,
                    'f_media':      float(np.mean(f_vals)),
                    'f_std':        float(np.std(f_vals)),
                    'f_mejor':      float(np.min(f_vals)),
                    'f_peor':       float(np.max(f_vals)),
                    'tasa_exito':   float(tasa),
                    'evals_media':  float(np.mean(evals)),
                })

    return registros


if __name__ == '__main__':
    n_configs = (len(FUNCIONES_ND) * 2 + len(FUNCIONES_2D)) * len(METODOS)
    print(f'Corriendo {N_RUNS} corridas x {n_configs} configuraciones = '
          f'{N_RUNS * n_configs} experimentos\n')
    print('-' * 100)
    registros = correr_experimentos()
    print('-' * 100)

    with open('resultados_heuristicos.json', 'w') as fp:
        json.dump(registros, fp, indent=2)
    print('\nResultados guardados en resultados_heuristicos.json')
