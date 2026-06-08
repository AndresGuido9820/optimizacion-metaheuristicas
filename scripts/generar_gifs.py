"""
Genera dos GIFs de animación para el trabajo de optimización:
  1. gd_rosenbrock_2d.gif   — trayectoria del descenso por gradiente sobre contour 2D
  2. pso_rosenbrock_2d.gif  — partículas PSO moviéndose sobre contour 2D

Salida: docs/assets/figures/
Uso: python scripts/generar_gifs.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path

OUT_DIR = Path('docs/assets/figures')
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED       = 42
BOUNDS_VIZ = (-3.0, 3.0)
BOUNDS_OPT = (-5.0,  5.0)
GRID_N     = 300
GIF_FPS    = 20
GIF_FRAMES = 120

# ── Funciones ────────────────────────────────────────────────────────────────

def rosenbrock(x):
    x = np.asarray(x, dtype=float)
    return float(np.sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1.0 - x[:-1])**2))

def grad_rosenbrock(x):
    x = np.asarray(x, dtype=float)
    g = np.zeros_like(x)
    g[:-1] += -400.0 * x[:-1] * (x[1:] - x[:-1]**2) - 2.0 * (1.0 - x[:-1])
    g[1:]  +=  200.0 * (x[1:] - x[:-1]**2)
    return g


# ── Grid para visualización ──────────────────────────────────────────────────

def make_grid(f, bounds=BOUNDS_VIZ, n=GRID_N):
    xi = np.linspace(*bounds, n)
    X, Y = np.meshgrid(xi, xi)
    Z = np.apply_along_axis(f, 2, np.stack([X, Y], axis=-1))
    return X, Y, Z


# ── GIF 1: Descenso por Gradiente ────────────────────────────────────────────

def backtracking(f, x, d, fx, gx_d):
    alpha = 1.0
    while f(x + alpha * d) > fx + 1e-4 * alpha * gx_d:
        alpha *= 0.5
        if alpha < 1e-14:
            break
    return alpha

def descenso_gradiente(f, gf, x0, max_iter=5000, tol=1e-6):
    x    = np.array(x0, dtype=float)
    tray = [x.copy()]
    hist = [f(x)]
    for _ in range(max_iter):
        g = gf(x)
        if np.linalg.norm(g) < tol:
            break
        d     = -g
        alpha = backtracking(f, x, d, hist[-1], np.dot(g, d))
        x     = x + alpha * d
        tray.append(x.copy())
        hist.append(f(x))
    return np.array(tray), hist


def generar_gif_gd(out_path):
    np.random.seed(SEED)
    x0   = np.random.uniform(*BOUNDS_OPT, 2)
    tray, hist = descenso_gradiente(rosenbrock, grad_rosenbrock, x0)

    X, Y, Z = make_grid(rosenbrock)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.contourf(X, Y, np.log1p(Z), levels=60, cmap='viridis')
    ax.set_xlabel('$x_1$')
    ax.set_ylabel('$x_2$')
    ax.set_xlim(BOUNDS_VIZ)
    ax.set_ylim(BOUNDS_VIZ)
    ax.plot(1.0, 1.0, 'y*', ms=14, zorder=5, label='Optimo (1,1)')
    ax.legend(loc='upper right', fontsize=8)

    linea, = ax.plot([], [], 'w-', lw=1.5, alpha=0.85)
    punto, = ax.plot([], [], 'ro', ms=7)
    titulo = ax.set_title('')

    indices = np.linspace(0, len(tray) - 1, GIF_FRAMES, dtype=int)

    def actualizar(k):
        i = indices[k]
        linea.set_data(tray[:i+1, 0], tray[:i+1, 1])
        punto.set_data([tray[i, 0]], [tray[i, 1]])
        fi = hist[min(i, len(hist) - 1)]
        titulo.set_text('GD — Rosenbrock 2D | iter ' + str(i) + ' | f = ' + '{:.3e}'.format(fi))
        return linea, punto, titulo

    ani = animation.FuncAnimation(
        fig, actualizar, frames=GIF_FRAMES,
        init_func=lambda: (linea, punto, titulo), blit=True
    )
    ani.save(str(out_path), writer='pillow', fps=GIF_FPS)
    plt.close()
    print('[GD]  Guardado: ' + str(out_path) + '  (' + str(out_path.stat().st_size // 1024) + ' KB)')


# ── GIF 2: PSO — partículas sobre contour ────────────────────────────────────

PSO_N    = 30
PSO_ITER = 80
W        = 0.729
C1       = 2.05
C2       = 2.05


def pso_con_historial(f, lo, hi, ndim, n_part, n_iter, seed):
    """PSO simple que devuelve historial completo de posiciones y mejor global."""
    rng = np.random.default_rng(seed)

    pos = rng.uniform(lo, hi, (n_part, ndim))
    vel = rng.uniform(-(hi - lo), (hi - lo), (n_part, ndim))

    pbest_pos = pos.copy()
    pbest_val = np.array([f(p) for p in pos])

    gbest_idx = int(np.argmin(pbest_val))
    gbest_pos = pbest_pos[gbest_idx].copy()
    gbest_val = float(pbest_val[gbest_idx])

    hist_pos    = [pos.copy()]
    hist_gbest  = [gbest_val]
    hist_gpos   = [gbest_pos.copy()]

    for _ in range(n_iter):
        r1 = rng.random((n_part, ndim))
        r2 = rng.random((n_part, ndim))
        vel = (W * vel
               + C1 * r1 * (pbest_pos - pos)
               + C2 * r2 * (gbest_pos - pos))
        pos = np.clip(pos + vel, lo, hi)

        vals = np.array([f(p) for p in pos])
        improved = vals < pbest_val
        pbest_pos[improved] = pos[improved].copy()
        pbest_val[improved] = vals[improved]

        idx = int(np.argmin(pbest_val))
        if pbest_val[idx] < gbest_val:
            gbest_pos = pbest_pos[idx].copy()
            gbest_val = float(pbest_val[idx])

        hist_pos.append(pos.copy())
        hist_gbest.append(gbest_val)
        hist_gpos.append(gbest_pos.copy())

    return hist_pos, hist_gbest, hist_gpos


def generar_gif_pso(out_path):
    hist_pos, hist_gbest, hist_gpos = pso_con_historial(
        rosenbrock, BOUNDS_OPT[0], BOUNDS_OPT[1], 2,
        PSO_N, PSO_ITER, SEED
    )

    X, Y, Z = make_grid(rosenbrock)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.subplots_adjust(wspace=0.35)

    # Panel izquierdo: partículas sobre contour
    ax_c = axes[0]
    ax_c.contourf(X, Y, np.log1p(Z), levels=60, cmap='viridis')
    ax_c.set_xlabel('$x_1$')
    ax_c.set_ylabel('$x_2$')
    ax_c.set_xlim(BOUNDS_VIZ)
    ax_c.set_ylim(BOUNDS_VIZ)
    ax_c.plot(1.0, 1.0, 'y*', ms=14, zorder=6, label='Optimo (1,1)')
    ax_c.legend(loc='upper right', fontsize=8)

    scatter  = ax_c.scatter([], [], s=35, c='white', alpha=0.85,
                             edgecolors='#ff4444', lw=0.8, zorder=5)
    gbest_pt, = ax_c.plot([], [], 'r*', ms=13, zorder=7, label='Mejor global')
    titulo_c  = ax_c.set_title('')

    # Panel derecho: curva de convergencia
    ax_f = axes[1]
    ax_f.set_xlim(0, PSO_ITER)
    fmax = max(hist_gbest)
    fmin = min(hist_gbest)
    ax_f.set_ylim(max(0, fmin * 0.5), fmax * 1.1 + 1)
    ax_f.set_yscale('symlog', linthresh=max(1e-10, abs(fmin) * 0.1 + 1e-30))
    ax_f.set_xlabel('Iteracion')
    ax_f.set_ylabel('Mejor f global (symlog)')
    ax_f.grid(True, alpha=0.3)
    linea_f, = ax_f.plot([], [], lw=2, color='#1f77b4')

    total_frames = len(hist_pos)
    frame_indices = np.linspace(0, total_frames - 1, GIF_FRAMES, dtype=int)

    def actualizar(k):
        i = frame_indices[k]
        pos = hist_pos[i]
        mask = ((pos[:, 0] >= BOUNDS_VIZ[0]) & (pos[:, 0] <= BOUNDS_VIZ[1]) &
                (pos[:, 1] >= BOUNDS_VIZ[0]) & (pos[:, 1] <= BOUNDS_VIZ[1]))
        scatter.set_offsets(pos[mask])
        gp = hist_gpos[i]
        if BOUNDS_VIZ[0] <= gp[0] <= BOUNDS_VIZ[1] and BOUNDS_VIZ[0] <= gp[1] <= BOUNDS_VIZ[1]:
            gbest_pt.set_data([gp[0]], [gp[1]])
        gv = hist_gbest[i]
        titulo_c.set_text('PSO — Rosenbrock 2D | iter ' + str(i) + '/' + str(PSO_ITER) + ' | f* = ' + '{:.3e}'.format(gv))
        linea_f.set_data(range(i + 1), hist_gbest[:i + 1])
        return scatter, gbest_pt, titulo_c, linea_f

    ani = animation.FuncAnimation(
        fig, actualizar, frames=GIF_FRAMES,
        init_func=lambda: (scatter, gbest_pt, titulo_c, linea_f), blit=True
    )
    ani.save(str(out_path), writer='pillow', fps=GIF_FPS)
    plt.close()
    print('[PSO] Guardado: ' + str(out_path) + '  (' + str(out_path.stat().st_size // 1024) + ' KB)')


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    generar_gif_gd(OUT_DIR / 'gd_rosenbrock_2d.gif')
    generar_gif_pso(OUT_DIR / 'pso_rosenbrock_2d.gif')
    print('\nGIFs generados en ' + str(OUT_DIR))
