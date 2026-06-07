"""
Parche para notebook 02: agrega las 4 funciones faltantes a los heuristicos.

Cambios:
  - Inserta funciones Schwefel, Griewank, Goldstein-Price y Camel 6-hump.
  - Actualiza CONFIGS para incluir las 6 funciones.
  - El resto del notebook (EA, PSO, DE, comparativa) ya itera sobre CONFIGS
    y se ejecuta automaticamente para todas las funciones.
"""

import json
from pathlib import Path

NB_PATH = Path("notebooks/02_heuristicos_comparativa.ipynb")


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
# Celda: descripcion de las funciones adicionales (markdown)
# ---------------------------------------------------------------------------
NEW_FUNCTIONS_MD = """\
### 1.2 Funciones adicionales

Ademas de Rosenbrock y Rastrigin, la tarea requiere cuatro funciones mas:

| Funcion | Dominio | Minimo global | Dimensiones |
|---|---|---|---|
| **Schwefel** | $[-500, 500]^n$ | $f(420.97,\\ldots) = 0$ | 2D y 3D |
| **Griewank** | $[-600, 600]^n$ | $f(0,\\ldots,0) = 0$ | 2D y 3D |
| **Goldstein-Price** | $[-2, 2]^2$ | $f(0,-1) = 3$ | Solo 2D |
| **Camel 6-hump** | $x_1\\in[-3,3],\\, x_2\\in[-2,2]$ | $f(\\pm0.0898, \\mp0.7126)\\approx -1.0316$ | Solo 2D |

> Los metodos heuristicos no requieren gradiente, por lo que todas las funciones
> se pueden optimizar directamente sin modificar los algoritmos.\
"""

# ---------------------------------------------------------------------------
# Celda: implementacion de las 4 funciones nuevas (codigo)
# ---------------------------------------------------------------------------
NEW_FUNCTIONS_CODE = """\
# ---------------------------------------------------------------------------
# Funciones adicionales (sin gradiente: los metodos heuristicos no lo usan)
# ---------------------------------------------------------------------------

def schwefel(x):
    \"\"\"
    Funcion de Schwefel.
    Dominio estandar: x_i en [-500, 500].
    Minimo global: f(420.9687, ...) = 0.
    \"\"\"
    x = np.asarray(x, dtype=float)
    n = len(x)
    return float(418.9829 * n - np.sum(x * np.sin(np.sqrt(np.abs(x)))))


def griewank(x):
    \"\"\"
    Funcion de Griewank.
    Dominio estandar: x_i en [-600, 600].
    Minimo global: f(0, ..., 0) = 0.
    \"\"\"
    x = np.asarray(x, dtype=float)
    suma = np.sum(x**2) / 4000
    prod = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
    return float(1 + suma - prod)


def goldstein_price(x):
    \"\"\"
    Funcion de Goldstein-Price (solo 2D).
    Dominio: x_i en [-2, 2].
    Minimo global: f(0, -1) = 3.
    \"\"\"
    x = np.asarray(x, dtype=float)
    x1, x2 = float(x[0]), float(x[1])
    a = (1 + (x1 + x2 + 1)**2
         * (19 - 14*x1 + 3*x1**2 - 14*x2 + 6*x1*x2 + 3*x2**2))
    b = (30 + (2*x1 - 3*x2)**2
         * (18 - 32*x1 + 12*x1**2 + 48*x2 - 36*x1*x2 + 27*x2**2))
    return float(a * b)


def camel_6hump(x):
    \"\"\"
    Funcion de las seis jorobas de camello (Six-Hump Camel), solo 2D.
    Dominio: x1 en [-3, 3], x2 en [-2, 2].
    Minimos globales: f(0.0898, -0.7126) = f(-0.0898, 0.7126) ~ -1.0316.
    \"\"\"
    x = np.asarray(x, dtype=float)
    x1, x2 = float(x[0]), float(x[1])
    return float(
        (4 - 2.1*x1**2 + x1**4 / 3) * x1**2
        + x1 * x2
        + (-4 + 4*x2**2) * x2**2
    )


# Verificacion rapida
print("Funciones adicionales cargadas:")
print(f"  Schwefel  [420.97, 420.97] -> {schwefel([420.9687, 420.9687]):.4f}  (esperado ~ 0)")
print(f"  Griewank  [0, 0]           -> {griewank([0.0, 0.0]):.4f}            (esperado = 0)")
print(f"  Goldstein [0, -1]          -> {goldstein_price([0.0, -1.0]):.4f}    (esperado = 3)")
print(f"  Camel 6H  [0.0898,-0.7126] -> {camel_6hump([0.0898, -0.7126]):.4f} (esperado ~ -1.0316)")\
"""

# ---------------------------------------------------------------------------
# Celda: CONFIGS actualizado con las 6 funciones
# ---------------------------------------------------------------------------
NEW_CONFIGS_CODE = """\
# ---------------------------------------------------------------------------
# Lista canonica de funciones usada en todo el notebook.
# CONFIGS_ND: funciones validas en 2D y 3D.
# CONFIGS_2D_ONLY: funciones exclusivamente bidimensionales.
# CONFIGS: todas juntas (para experimentos en 2D).
# ---------------------------------------------------------------------------

CONFIGS_ND = [
    ('Rosenbrock', rosenbrock),
    ('Rastrigin',  rastrigin),
    ('Schwefel',   schwefel),
    ('Griewank',   griewank),
]

CONFIGS_2D_ONLY = [
    ('Goldstein-Price', goldstein_price),
    ('Camel 6-hump',    camel_6hump),
]

CONFIGS = CONFIGS_ND + CONFIGS_2D_ONLY

# Umbrales de exito por funcion (para la tasa de exito en la comparativa)
THRESH = {
    'Rosenbrock':     1e-4,
    'Rastrigin':      1.0,
    'Schwefel':       10.0,
    'Griewank':       0.01,
    'Goldstein-Price': 3.5,
    'Camel 6-hump':   -1.0,
}

def make_grid(f, bounds=BOUNDS_VIZ, n=GRID_N):
    \"\"\"Evalua f en un grid 2D para visualizacion.\"\"\"
    x  = np.linspace(*bounds, n)
    X, Y = np.meshgrid(x, x)
    XY = np.stack([X, Y], axis=-1)
    Z  = np.apply_along_axis(f, 2, XY)
    return X, Y, Z

grids = {nombre: make_grid(f) for nombre, f in CONFIGS}
print("Funciones registradas:", [c[0] for c in CONFIGS])
print("Grids calculados:", list(grids.keys()))\
"""

# ---------------------------------------------------------------------------
# Aplicar todos los cambios al notebook
# ---------------------------------------------------------------------------
with open(NB_PATH) as fh:
    nb = json.load(fh)

cells = nb["cells"]

# 1. Insertar markdown + codigo de nuevas funciones despues de celda 4
#    (justo despues de la celda de rosenbrock/rastrigin/CONFIGS original)
cells.insert(5, code_cell(NEW_FUNCTIONS_CODE))
cells.insert(5, md_cell(NEW_FUNCTIONS_MD))

# 2. Reemplazar la celda que contiene "CONFIGS = ["
for i, c in enumerate(cells):
    if c["cell_type"] == "code" and "CONFIGS = [" in "".join(c["source"]):
        cells[i] = code_cell(NEW_CONFIGS_CODE)
        print(f"  CONFIGS actualizado en celda {i}")
        break

nb["cells"] = cells

with open(NB_PATH, "w") as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)

print(f"\nNotebook 02 actualizado: {len(nb['cells'])} celdas totales.")
