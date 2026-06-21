"""
Experimento estadistico del descenso por gradiente (Parte 1, punto 1).

Optimiza las funciones validas en nD (Rosenbrock, Rastrigin, Schwefel, Griewank)
en 2D y 3D con condicion inicial aleatoria, repitiendo n = 100, 500 y 1000 veces.
Genera los histogramas del valor final f* y del numero de evaluaciones de la
funcion objetivo, y guarda las estadisticas en JSON para el reporte.

El gradiente se aproxima por diferencias centrales (h=1e-5); se contabilizan
TODAS las evaluaciones de f, incluidas las del gradiente y las del backtracking,
para que "numero de evaluaciones" sea una metrica comparable con los heuristicos.

Uso:   python scripts/histogramas_gd.py
Salida: docs/assets/figures/hist_*  y  notebooks/outputs/resultados_gd_stats.json
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from heuristicos import (rosenbrock, rastrigin, schwefel, griewank,
                         BOUNDS_ND, F_OPT)

# ── Configuracion ─────────────────────────────────────────────────────────────
SEED        = 42
N_REPS_LIST = [100, 500, 1000]
GD_ALPHA0   = 1.0
GD_RHO      = 0.5
GD_C_ARMIJO = 1e-4
GD_TOL      = 1e-6
GD_MAX_ITER = 2_000
H_GRAD      = 1e-5

FUNCIONES = {
    'Rosenbrock': rosenbrock,
    'Rastrigin':  rastrigin,
    'Schwefel':   schwefel,
    'Griewank':   griewank,
}

# Rutas de salida (relativas a la raiz del repo)
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_FIG  = os.path.join(ROOT, 'docs', 'assets', 'figures')
DIR_OUT  = os.path.join(ROOT, 'notebooks', 'outputs')
os.makedirs(DIR_FIG, exist_ok=True)
os.makedirs(DIR_OUT, exist_ok=True)


# ── Descenso por gradiente (gradiente numerico, conteo honesto de evals) ──────
def num_grad(f, x, h=H_GRAD):
    """Gradiente por diferencias centrales. Devuelve (g, n_evals_usadas)."""
    g  = np.empty_like(x)
    ne = 0
    for i in range(x.size):
        xp = x.copy(); xp[i] += h
        xm = x.copy(); xm[i] -= h
        g[i] = (f(xp) - f(xm)) / (2.0 * h)
        ne  += 2
    return g, ne


def descenso_gradiente(f, x0, lo, hi):
    """GD proyectado al dominio [lo,hi] con backtracking (Armijo).

    Se recorta cada iterado al dominio (descenso por gradiente proyectado): sin
    esto, el GD se escapa de la caja en funciones como Schwefel y reporta valores
    por debajo del optimo global, fuera del dominio de definicion del problema.
    Cuenta toda evaluacion de f.
    """
    x  = np.clip(np.array(x0, dtype=float), lo, hi)
    fx = f(x)
    n_evals = 1

    it = 0
    for it in range(GD_MAX_ITER):
        g, ne = num_grad(f, x)
        n_evals += ne
        gnorm = np.linalg.norm(g)
        if gnorm < GD_TOL:                  # 1) gradiente ~ 0
            break
        direccion = -g
        gx_dir    = -gnorm ** 2
        alpha     = GD_ALPHA0
        mejorado  = False
        while alpha >= 1e-14:               # backtracking (Armijo)
            x_new  = np.clip(x + alpha * direccion, lo, hi)   # proyeccion al dominio
            fx_new = f(x_new)
            n_evals += 1
            if fx_new <= fx + GD_C_ARMIJO * alpha * gx_dir:
                mejorado = True
                break
            alpha *= GD_RHO
        if not mejorado:                    # 2) la busqueda de linea no avanza
            break
        if fx - fx_new < 1e-10 * (1.0 + abs(fx)):   # 3) estancamiento
            x, fx = x_new, fx_new
            break
        x, fx = x_new, fx_new

    return {'f_final': float(fx), 'n_evals': n_evals, 'n_iter': it + 1}


# ── Experimento ───────────────────────────────────────────────────────────────
def correr():
    stats = {}
    for nombre, f in FUNCIONES.items():
        lo, hi = BOUNDS_ND[nombre]
        stats[nombre] = {}
        for ndim in (2, 3):
            stats[nombre][str(ndim)] = {}
            for n_reps in N_REPS_LIST:
                rng = np.random.default_rng(SEED)
                f_vals, evals = [], []
                for _ in range(n_reps):
                    x0  = rng.uniform(lo, hi, ndim)
                    res = descenso_gradiente(f, x0, lo, hi)
                    f_vals.append(res['f_final'])
                    evals.append(res['n_evals'])
                f_arr = np.array(f_vals)
                stats[nombre][str(ndim)][str(n_reps)] = {
                    'f_vals':     f_vals,
                    'evals':      evals,
                    'f_media':    float(f_arr.mean()),
                    'f_std':      float(f_arr.std()),
                    'f_mejor':    float(f_arr.min()),
                    'evals_media': float(np.mean(evals)),
                }
                print('%-12s %dD n=%4d | media=%.3e mejor=%.3e evals_prom=%d'
                      % (nombre, ndim, n_reps, f_arr.mean(), f_arr.min(),
                         int(np.mean(evals))))
    return stats


# ── Histogramas ───────────────────────────────────────────────────────────────
COLORES = {100: '#1f77b4', 500: '#2ca02c', 1000: '#d62728'}


def figura_histograma(stats, ndim, magnitud):
    """magnitud in {'f','evals'}: histogramas (filas=funcion, col=n_reps)."""
    funcs   = list(FUNCIONES.keys())
    n_cols  = len(N_REPS_LIST)
    fig, axes = plt.subplots(len(funcs), n_cols,
                             figsize=(4.2 * n_cols, 3.0 * len(funcs)),
                             constrained_layout=True)
    titulo = ('Histograma del valor final $f^*$' if magnitud == 'f'
              else 'Histograma del nº de evaluaciones de $f$')
    fig.suptitle('%s — Descenso por gradiente (%dD)' % (titulo, ndim),
                 fontsize=14)

    for row, nombre in enumerate(funcs):
        for col, n_reps in enumerate(N_REPS_LIST):
            ax   = axes[row][col]
            d    = stats[nombre][str(ndim)][str(n_reps)]
            data = d['f_vals'] if magnitud == 'f' else d['evals']
            ax.hist(data, bins=30, color=COLORES[n_reps],
                    alpha=0.8, edgecolor='white', linewidth=0.3)
            if col == 0:
                ax.set_ylabel('%s\nfrecuencia' % nombre, fontsize=9)
            if row == 0:
                ax.set_title('n = %d' % n_reps, fontsize=11)
            if row == len(funcs) - 1:
                ax.set_xlabel('$f^*$' if magnitud == 'f' else 'nº evals',
                              fontsize=9)
            ax.tick_params(labelsize=7)
    return fig


def guardar_figuras(stats):
    for ndim in (2, 3):
        for magnitud, slug in (('f', 'fstar'), ('evals', 'evals')):
            fig  = figura_histograma(stats, ndim, magnitud)
            base = 'hist_gd_%s_%dd.png' % (slug, ndim)
            for d in (DIR_FIG, DIR_OUT):
                fig.savefig(os.path.join(d, base), dpi=120, bbox_inches='tight')
            plt.close(fig)
            print('Guardado:', base)


if __name__ == '__main__':
    print('Corriendo GD: 4 funciones x 2 dims x {100,500,1000} repeticiones...\n')
    stats = correr()
    guardar_figuras(stats)
    # Guardar estadisticas (sin los vectores crudos, para mantener el JSON liviano)
    resumen = {}
    for fn, dd in stats.items():
        resumen[fn] = {}
        for nd, nn in dd.items():
            resumen[fn][nd] = {n: {k: v for k, v in r.items()
                                   if k not in ('f_vals', 'evals')}
                               for n, r in nn.items()}
    with open(os.path.join(DIR_OUT, 'resultados_gd_stats.json'), 'w') as fp:
        json.dump(resumen, fp, indent=2)
    print('\nEstadisticas en notebooks/outputs/resultados_gd_stats.json')
