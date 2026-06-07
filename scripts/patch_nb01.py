"""
Parche para notebook 01: agrega las 4 funciones faltantes y el experimento n=100/500/1000.

Cambios:
  - Inserta funciones Schwefel, Griewank, Goldstein-Price y Camel 6-hump.
  - Actualiza CONFIGS para incluir las 6 funciones.
  - Inserta la seccion de histogramas (n=100/500/1000) antes de las conclusiones.
"""

import json
from pathlib import Path

NB_PATH = Path("notebooks/01_funciones_gradiente.ipynb")


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
# Celda: descripcion de las 4 funciones nuevas (markdown)
# ---------------------------------------------------------------------------
NEW_FUNCTIONS_MD = """\
### 1.2 Funciones adicionales

La tarea requiere seis funciones en total. Se agregan las cuatro restantes:

| Funcion | Dominio | Minimo global | Dimensiones |
|---|---|---|---|
| **Schwefel** | $[-500, 500]^n$ | $f(420.97,\\ldots) = 0$ | 2D y 3D |
| **Griewank** | $[-600, 600]^n$ | $f(0,\\ldots,0) = 0$ | 2D y 3D |
| **Goldstein-Price** | $[-2, 2]^2$ | $f(0,-1) = 3$ | Solo 2D |
| **Camel 6-hump** | $x_1\\in[-3,3],\\, x_2\\in[-2,2]$ | $f(\\pm0.0898, \\mp0.7126)\\approx -1.0316$ | Solo 2D |

> Goldstein-Price y Camel son funciones **exclusivamente bidimensionales**.
> Schwefel y Griewank se extienden a 3D de forma natural.\
"""

# ---------------------------------------------------------------------------
# Celda: implementacion de las 4 funciones nuevas (codigo)
# ---------------------------------------------------------------------------
NEW_FUNCTIONS_CODE = """\
# ---------------------------------------------------------------------------
# Funciones adicionales requeridas por la tarea
# Cada funcion incluye su formula, dominio y minimo global conocido.
# ---------------------------------------------------------------------------

def schwefel(x):
    \"\"\"
    Funcion de Schwefel.
    Dominio: x_i en [-500, 500].
    Minimo global: f(420.9687, ...) = 0.
    Nota: el minimo esta lejos del centro del dominio, lo que engana facilmente al GD.
    \"\"\"
    x = np.asarray(x, dtype=float)
    n = len(x)
    return float(418.9829 * n - np.sum(x * np.sin(np.sqrt(np.abs(x)))))


def grad_schwefel(x):
    \"\"\"Gradiente de Schwefel por diferencias finitas centradas.\"\"\"
    return gradiente_numerico(schwefel, x)


def griewank(x):
    \"\"\"
    Funcion de Griewank.
    Dominio: x_i en [-600, 600].
    Minimo global: f(0, ..., 0) = 0.
    Nota: tiene muchos minimos locales uniformemente distribuidos.
    \"\"\"
    x = np.asarray(x, dtype=float)
    suma = np.sum(x**2) / 4000
    prod = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
    return float(1 + suma - prod)


def grad_griewank(x):
    \"\"\"Gradiente de Griewank por diferencias finitas centradas.\"\"\"
    return gradiente_numerico(griewank, x)


def goldstein_price(x):
    \"\"\"
    Funcion de Goldstein-Price (solo 2D).
    Dominio: x_i en [-2, 2].
    Minimo global: f(0, -1) = 3.
    Nota: paisaje muy irregular, multiple minimos locales.
    \"\"\"
    x = np.asarray(x, dtype=float)
    x1, x2 = float(x[0]), float(x[1])
    a = (1 + (x1 + x2 + 1)**2
         * (19 - 14*x1 + 3*x1**2 - 14*x2 + 6*x1*x2 + 3*x2**2))
    b = (30 + (2*x1 - 3*x2)**2
         * (18 - 32*x1 + 12*x1**2 + 48*x2 - 36*x1*x2 + 27*x2**2))
    return float(a * b)


def grad_goldstein_price(x):
    \"\"\"Gradiente de Goldstein-Price por diferencias finitas centradas.\"\"\"
    return gradiente_numerico(goldstein_price, x)


def camel_6hump(x):
    \"\"\"
    Funcion de las seis jorobas de camello (Six-Hump Camel), solo 2D.
    Dominio: x1 en [-3, 3], x2 en [-2, 2].
    Minimos globales: f(0.0898, -0.7126) = f(-0.0898, 0.7126) ~ -1.0316.
    Nota: dos minimos globales simetricos, seis jorobas locales.
    \"\"\"
    x = np.asarray(x, dtype=float)
    x1, x2 = float(x[0]), float(x[1])
    return float(
        (4 - 2.1*x1**2 + x1**4 / 3) * x1**2
        + x1 * x2
        + (-4 + 4*x2**2) * x2**2
    )


def grad_camel_6hump(x):
    \"\"\"Gradiente de Camel 6-hump por diferencias finitas centradas.\"\"\"
    return gradiente_numerico(camel_6hump, x)


# ---------------------------------------------------------------------------
# Verificacion en los minimos conocidos
# ---------------------------------------------------------------------------
print("Verificacion de nuevas funciones en sus minimos globales:")
print(f"  Schwefel       [420.97, 420.97] -> f = {schwefel([420.9687, 420.9687]):.4f}  (esperado ~ 0)")
print(f"  Griewank       [0, 0]           -> f = {griewank([0.0, 0.0]):.4f}             (esperado = 0)")
print(f"  Goldstein      [0, -1]          -> f = {goldstein_price([0.0, -1.0]):.4f}     (esperado = 3)")
print(f"  Camel 6-hump   [0.0898,-0.7126] -> f = {camel_6hump([0.0898, -0.7126]):.4f}  (esperado ~ -1.0316)")\
"""

# ---------------------------------------------------------------------------
# Celda: CONFIGS actualizado con las 6 funciones
# ---------------------------------------------------------------------------
NEW_CONFIGS_CODE = """\
# ---------------------------------------------------------------------------
# Lista canonica de funciones usada en todo el notebook.
# Se distingue entre funciones validas en nD y las que son solo 2D.
# ---------------------------------------------------------------------------

# Funciones validas en 2D y 3D
CONFIGS_ND = [
    ('Rosenbrock', rosenbrock,       grad_rosenbrock),
    ('Rastrigin',  rastrigin,        grad_rastrigin),
    ('Schwefel',   schwefel,         grad_schwefel),
    ('Griewank',   griewank,         grad_griewank),
]

# Funciones exclusivamente 2D por definicion matematica
CONFIGS_2D_ONLY = [
    ('Goldstein-Price', goldstein_price,  grad_goldstein_price),
    ('Camel 6-hump',    camel_6hump,      grad_camel_6hump),
]

# CONFIGS: todas las funciones (para visualizacion y GD en 2D)
CONFIGS = CONFIGS_ND + CONFIGS_2D_ONLY


def make_grid(f, bounds=BOUNDS_2D, n=GRID_N):
    \"\"\"Evalua f en un grid 2D para visualizacion.\"\"\"
    x  = np.linspace(*bounds, n)
    X, Y = np.meshgrid(x, x)
    XY = np.stack([X, Y], axis=-1)
    Z  = np.apply_along_axis(f, 2, XY)
    return X, Y, Z


# Pre-calcular grids una sola vez (todos son 2D)
grids = {nombre: make_grid(f) for nombre, f, _ in CONFIGS}
print("Funciones registradas:", [c[0] for c in CONFIGS])
print("Grids calculados:", list(grids.keys()))\
"""

# ---------------------------------------------------------------------------
# Celda: descripcion de la seccion de histogramas (markdown)
# ---------------------------------------------------------------------------
HIST_MD = """\
### 3.4 Analisis estadistico: n = 100, 500 y 1000 condiciones iniciales

Para evaluar la robustez del descenso por gradiente se repite el proceso con
**n condiciones iniciales aleatorias** (n = 100, 500 y 1000).

Se registran dos metricas por corrida:
- **f\\*** — valor de la funcion objetivo al converger.
- **Evaluaciones** — numero de evaluaciones de la funcion objetivo hasta la convergencia.

Los histogramas permiten ver si el GD encuentra el minimo global de forma
consistente o queda atrapado en minimos locales segun la funcion.\
"""

# ---------------------------------------------------------------------------
# Celda: experimento estadistico (codigo)
# ---------------------------------------------------------------------------
HIST_EXP_CODE = """\
# ---------------------------------------------------------------------------
# Experimento estadistico: n repeticiones con condicion inicial aleatoria.
# Se usa CONFIGS_ND porque Goldstein y Camel tienen dominios diferentes.
# ---------------------------------------------------------------------------

N_REPS_LIST = [100, 500, 1000]

# resultados_stat[nombre][ndim][n_reps] = {'f_vals': [...], 'evals': [...]}
resultados_stat = {}

for nombre, f, gf in CONFIGS_ND:
    resultados_stat[nombre] = {}
    for ndim in [2, 3]:
        resultados_stat[nombre][ndim] = {}
        for n_reps in N_REPS_LIST:
            np.random.seed(SEED)
            f_vals, evals_list = [], []
            for _ in range(n_reps):
                x0  = np.random.uniform(*BOUNDS_OPT, ndim)
                res = descenso_gradiente(f, gf, x0)
                f_vals.append(res['f_final'])
                evals_list.append(res['n_evals'])
            resultados_stat[nombre][ndim][n_reps] = {
                'f_vals': f_vals,
                'evals':  evals_list,
            }
        print(f"  {nombre} {ndim}D: listo")

print("\\nExperimento estadistico completo.")\
"""

# ---------------------------------------------------------------------------
# Celda: graficas de histogramas (codigo)
# ---------------------------------------------------------------------------
HIST_PLOT_CODE = """\
# ---------------------------------------------------------------------------
# Histogramas de f* y de evaluaciones de la funcion objetivo.
# Una figura por dimension (2D / 3D).
# Filas = funciones, columnas = n_reps.
# ---------------------------------------------------------------------------

colores_n = {100: '#1f77b4', 500: '#2ca02c', 1000: '#d62728'}

for ndim in [2, 3]:
    n_funcs = len(CONFIGS_ND)
    n_cols  = len(N_REPS_LIST)

    # -- Histogramas de f* --------------------------------------------------
    fig, axes = plt.subplots(n_funcs, n_cols,
                             figsize=(5 * n_cols, 3.5 * n_funcs),
                             constrained_layout=True)
    fig.suptitle(f'Histogramas del valor final f* — GD ({ndim}D)', fontsize=13)

    for row, (nombre, _, __) in enumerate(CONFIGS_ND):
        for col, n_reps in enumerate(N_REPS_LIST):
            ax   = axes[row][col]
            data = resultados_stat[nombre][ndim][n_reps]['f_vals']
            ax.hist(data, bins=30, color=colores_n[n_reps],
                    edgecolor='white', alpha=0.85)
            mediana = float(np.median(data))
            ax.axvline(mediana, color='black', linestyle='--', lw=1.2,
                       label=f'Mediana: {mediana:.2e}')
            ax.set_title(f'{nombre}  n={n_reps}', fontsize=9)
            ax.set_xlabel('f* final', fontsize=8)
            ax.set_ylabel('Frecuencia', fontsize=8)
            ax.legend(fontsize=7)

    fname = f'outputs/histogramas_f_gd_{ndim}d.png'
    plt.savefig(fname, dpi=120, bbox_inches='tight')
    plt.show()
    print(f'Guardado: {fname}')

    # -- Histogramas de evaluaciones ----------------------------------------
    fig, axes = plt.subplots(n_funcs, n_cols,
                             figsize=(5 * n_cols, 3.5 * n_funcs),
                             constrained_layout=True)
    fig.suptitle(f'Histogramas de evaluaciones de f — GD ({ndim}D)', fontsize=13)

    for row, (nombre, _, __) in enumerate(CONFIGS_ND):
        for col, n_reps in enumerate(N_REPS_LIST):
            ax   = axes[row][col]
            data = resultados_stat[nombre][ndim][n_reps]['evals']
            ax.hist(data, bins=30, color=colores_n[n_reps],
                    edgecolor='white', alpha=0.85)
            mediana = float(np.median(data))
            ax.axvline(mediana, color='black', linestyle='--', lw=1.2,
                       label=f'Mediana: {mediana:.0f}')
            ax.set_title(f'{nombre}  n={n_reps}', fontsize=9)
            ax.set_xlabel('Evaluaciones de f', fontsize=8)
            ax.set_ylabel('Frecuencia', fontsize=8)
            ax.legend(fontsize=7)

    fname = f'outputs/histogramas_evals_gd_{ndim}d.png'
    plt.savefig(fname, dpi=120, bbox_inches='tight')
    plt.show()
    print(f'Guardado: {fname}')\
"""

# ---------------------------------------------------------------------------
# Aplicar todos los cambios al notebook
# ---------------------------------------------------------------------------
with open(NB_PATH) as fh:
    nb = json.load(fh)

cells = nb["cells"]

# 1. Insertar markdown + codigo de nuevas funciones despues de celda 4
#    (justo despues de la verificacion de Rosenbrock/Rastrigin)
cells.insert(5, code_cell(NEW_FUNCTIONS_CODE))
cells.insert(5, md_cell(NEW_FUNCTIONS_MD))

# 2. Reemplazar la celda que contiene "CONFIGS = ["
for i, c in enumerate(cells):
    if c["cell_type"] == "code" and "CONFIGS = [" in "".join(c["source"]):
        cells[i] = code_cell(NEW_CONFIGS_CODE)
        print(f"  CONFIGS actualizado en celda {i}")
        break

# 3. Insertar seccion de histogramas ANTES de las Conclusiones
for i, c in enumerate(cells):
    if c["cell_type"] == "markdown" and "Conclusiones" in "".join(c["source"]):
        cells.insert(i, code_cell(HIST_PLOT_CODE))
        cells.insert(i, code_cell(HIST_EXP_CODE))
        cells.insert(i, md_cell(HIST_MD))
        print(f"  Seccion histogramas insertada antes de celda {i}")
        break

nb["cells"] = cells

with open(NB_PATH, "w") as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)

print(f"\nNotebook 01 actualizado: {len(nb['cells'])} celdas totales.")
