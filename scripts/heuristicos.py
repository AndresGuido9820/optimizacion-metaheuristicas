"""
Optimización heurística — EA, PSO, Evolución Diferencial
Funciones: Rosenbrock y Rastrigin en 2D y 3D
30 corridas por método/función/dimensión
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
BOUNDS      = (-5.0, 5.0)
N_RUNS      = 30
A           = 10
THRESH      = {'Rosenbrock': 1e-4, 'Rastrigin': 1.0}

# EA
EA_POP      = 100
EA_GENS     = 500
EA_CXPB     = 0.7
EA_MUTPB    = 0.2

# PSO
PSO_N       = 50
PSO_ITERS   = 500
PSO_OPTS    = {'c1': 2.05, 'c2': 2.05, 'w': 0.729}

# DE
DE_CONF     = dict(strategy='best1bin', maxiter=1000, popsize=15,
                   tol=1e-7, mutation=(0.5, 1.0), recombination=0.7)


# ── Funciones de prueba ──────────────────────────────────────────────────────
def rosenbrock(x):
    x = np.asarray(x, dtype=float)
    return float(np.sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1.0 - x[:-1])**2))

def rastrigin(x):
    x = np.asarray(x, dtype=float)
    return float(A * len(x) + np.sum(x**2 - A * np.cos(2 * np.pi * x)))

FUNCIONES = {'Rosenbrock': rosenbrock, 'Rastrigin': rastrigin}


# ── EA (DEAP) ────────────────────────────────────────────────────────────────
def _init_ea_toolbox(f, ndim):
    # Limpiar creator para evitar conflictos entre corridas
    for attr in ('FitnessMin', 'Individual'):
        if hasattr(creator, attr):
            delattr(creator, attr)
    creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMin)

    tb = base.Toolbox()
    tb.register('attr', np.random.uniform, BOUNDS[0], BOUNDS[1])
    tb.register('individual', tools.initRepeat, creator.Individual, tb.attr, n=ndim)
    tb.register('population', tools.initRepeat, list, tb.individual)
    tb.register('evaluate', lambda ind: (f(np.array(ind)),))
    tb.register('mate',   tools.cxBlend, alpha=0.5)
    tb.register('mutate', tools.mutGaussian, mu=0, sigma=0.5, indpb=0.2)
    tb.register('select', tools.selTournament, tournsize=3)
    return tb

def run_ea(fname, ndim, seed):
    np.random.seed(seed)
    import random; random.seed(seed)
    f  = FUNCIONES[fname]
    tb = _init_ea_toolbox(f, ndim)
    pop, log = algorithms.eaSimple(
        tb.population(n=EA_POP), tb,
        cxpb=EA_CXPB, mutpb=EA_MUTPB, ngen=EA_GENS,
        stats=None, halloffame=tools.HallOfFame(1), verbose=False
    )
    hof = tools.HallOfFame(1)
    hof.update(pop)
    best = np.array(hof[0])
    return {'f_final': f(best), 'n_evals': EA_POP * (EA_GENS + 1)}


# ── PSO (pyswarms) ───────────────────────────────────────────────────────────
def run_pso(fname, ndim, seed):
    np.random.seed(seed)
    f = FUNCIONES[fname]

    def batch_f(X):
        return np.array([f(X[i]) for i in range(X.shape[0])])

    bounds = (np.full(ndim, BOUNDS[0]), np.full(ndim, BOUNDS[1]))
    opt    = ps.single.GlobalBestPSO(n_particles=PSO_N, dimensions=ndim,
                                      options=PSO_OPTS, bounds=bounds)
    cost, _ = opt.optimize(batch_f, iters=PSO_ITERS, verbose=False)
    return {'f_final': float(cost), 'n_evals': PSO_N * PSO_ITERS}


# ── Evolución Diferencial (scipy) ────────────────────────────────────────────
def run_de(fname, ndim, seed):
    f      = FUNCIONES[fname]
    result = differential_evolution(f, [BOUNDS] * ndim, seed=seed, **DE_CONF)
    return {'f_final': float(result.fun), 'n_evals': int(result.nfev)}


# ── Experimentos ─────────────────────────────────────────────────────────────
METODOS = {'EA': run_ea, 'PSO': run_pso, 'DE': run_de}

def correr_experimentos():
    registros = []
    total = len(FUNCIONES) * 2 * len(METODOS) * N_RUNS
    avance = 0

    for fname in FUNCIONES:
        for ndim in [2, 3]:
            for metodo, runner in METODOS.items():
                f_vals, evals = [], []
                t0 = time.time()
                for seed in range(N_RUNS):
                    res = runner(fname, ndim, seed)
                    f_vals.append(res['f_final'])
                    evals.append(res['n_evals'])
                    avance += 1

                tasa = np.mean(np.array(f_vals) < THRESH[fname])
                print(
                    f'{metodo:4s} | {fname:12s} {ndim}D | '
                    f'media={np.mean(f_vals):.3e}  std={np.std(f_vals):.3e}  '
                    f'mejor={np.min(f_vals):.3e}  '
                    f'exito={tasa*100:.0f}%  '
                    f'evals={int(np.mean(evals))}  '
                    f't={time.time()-t0:.1f}s'
                )
                registros.append({
                    'metodo': metodo, 'funcion': fname, 'ndim': ndim,
                    'f_media': float(np.mean(f_vals)),
                    'f_std':   float(np.std(f_vals)),
                    'f_mejor': float(np.min(f_vals)),
                    'f_peor':  float(np.max(f_vals)),
                    'tasa_exito': float(tasa),
                    'evals_media': float(np.mean(evals)),
                })

    return registros


if __name__ == '__main__':
    print(f'Corriendo {N_RUNS} corridas x 3 métodos x 2 funciones x 2 dims = '
          f'{N_RUNS * 3 * 2 * 2} experimentos\n')
    print('-' * 90)
    registros = correr_experimentos()
    print('-' * 90)

    with open('resultados_heuristicos.json', 'w') as fp:
        json.dump(registros, fp, indent=2)
    print('\nResultados guardados en resultados_heuristicos.json')
