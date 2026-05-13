# Casos de Uso y Ejemplos Ilustrativos

Los algoritmos implementados en este repositorio son directamente reutilizables en problemas reales de ingeniería, logística y ciencia de datos. Esta guía presenta cuatro casos de uso con fragmentos de código adaptables.

---

## Caso 1 — Calibración de modelos con múltiples mínimos locales

**Problema:** Ajustar los parámetros $(\theta_1, \theta_2, \theta_3)$ de un modelo no lineal donde la función de pérdida tiene múltiples mínimos locales (similar a Rastrigin).

**¿Por qué DE?** Cuando la función de pérdida tiene múltiples mínimos locales (redes neuronales pequeñas, modelos ODE, ajuste de curvas), DE escapa de ellos gracias a su operador de mutación diferencial. GD quedaría atrapado en el mínimo más cercano al punto inicial.

```python
from scipy.optimize import differential_evolution
import numpy as np

def loss(params):
    theta1, theta2, theta3 = params
    # Reemplazar con la función de pérdida real del modelo
    return your_model_loss(theta1, theta2, theta3)

bounds = [(-5, 5), (-5, 5), (-5, 5)]
result = differential_evolution(
    loss, bounds,
    strategy='best1bin', maxiter=1000,
    popsize=15, mutation=(0.5, 1.0), recombination=0.7,
    seed=42, tol=1e-7
)
print(f"Parámetros óptimos: {result.x}")
print(f"Pérdida mínima:     {result.fun:.6e}")
```

**Ejemplo de resultado esperado:**
```
Parámetros óptimos: [ 1.000e+00  1.000e+00  1.000e+00]
Pérdida mínima:     2.341e-09
```

---

## Caso 2 — Optimización de rutas logísticas (TSP generalizado)

**Problema:** Un equipo de ventas debe visitar $n$ sucursales minimizando el costo total de combustible + tiempo del vendedor. Aplicación directa del modelo TSP implementado en el Notebook 03.

```python
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Coordenadas de las sucursales (lat, lon)
SUCURSALES = [
    ("Bogotá",       4.7110,  -74.0721),
    ("Medellín",     6.2442,  -75.5812),
    ("Cali",         3.4516,  -76.5320),
    ("Barranquilla", 10.9685, -74.7813),
    # ... más sucursales
]

COSTO_KM   = 4.5     # MXN/km  (ajustar a COP, USD, etc.)
VEL_KMH    = 80.0
COSTO_HORA = 150.0   # MXN/hora del vendedor

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def build_dist_matrix(locations):
    n = len(locations)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_km(locations[i][1], locations[i][2],
                             locations[j][1], locations[j][2])
            D[i, j] = D[j, i] = d
    return D

def tour_cost(route, D):
    n = len(route)
    km = sum(D[route[i], route[(i + 1) % n]] for i in range(n))
    return km * COSTO_KM + (km / VEL_KMH) * COSTO_HORA
```

**Extensiones directas del código:**
- Cambiar `SUCURSALES` → aplicable a cualquier país o región
- Modificar `COSTO_KM` y `COSTO_HORA` → adaptar a costos locales o moneda
- Agregar ventanas de tiempo → TSP con restricciones (TSPTW)
- Usar distancias de API de mapas → mayor precisión que haversine

---

## Caso 3 — Búsqueda de hiperparámetros con EA (caja negra)

**Problema:** Optimizar hiperparámetros de un modelo de ML (learning rate, regularización, tamaño de capas) sin gradiente disponible, usando EA como optimizador de caja negra.

```python
from deap import base, creator, tools, algorithms
import numpy as np
import random

# Espacio de búsqueda: [learning_rate, lambda_reg, n_units]
BOUNDS = [(1e-5, 1e-1), (1e-6, 1e-2), (16.0, 256.0)]

def evaluate_hyperparams(individual):
    lr, lam, n_units = individual
    n_units = int(np.clip(n_units, 16, 256))
    # Reemplazar con entrenamiento y validación real del modelo
    val_loss = train_and_evaluate(lr=lr, lambda_reg=lam, n_units=n_units)
    return (val_loss,)  # DEAP requiere tupla

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

tb = base.Toolbox()
tb.register("attr", lambda: [np.random.uniform(*BOUNDS[i]) for i in range(3)])
tb.register("individual", tools.initIterate, creator.Individual, tb.attr)
tb.register("population", tools.initRepeat, list, tb.individual)
tb.register("evaluate", evaluate_hyperparams)
tb.register("mate",   tools.cxBlend, alpha=0.5)
tb.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.3)
tb.register("select", tools.selTournament, tournsize=3)

pop = tb.population(n=50)
hof = tools.HallOfFame(1)
algorithms.eaSimple(pop, tb, cxpb=0.7, mutpb=0.2, ngen=100,
                    halloffame=hof, verbose=False)

best = hof[0]
print(f"Mejor lr={best[0]:.2e}, lambda={best[1]:.2e}, n_units={int(best[2])}")
```

**Ventaja sobre Grid Search:** Con 50 individuos × 100 generaciones = 5,000 evaluaciones totales vs. $10^3$ combinaciones en un Grid Search 10×10×10.

---

## Caso 4 — PSO para diseño de ingeniería con restricciones

**Problema:** Minimizar el peso de una viga estructural de acero sujeta a restricciones de tensión máxima y deflexión admisible.

```python
import pyswarms as ps
import numpy as np

# Variables de diseño: [altura h (m), ancho b (m), longitud L (m)]
def tension(h, b, L, F=10000):
    """Tensión máxima en la fibra extrema (Pa)."""
    I = b * h**3 / 12  # momento de inercia
    return F * L / (4 * I / h)

def deflexion(h, b, L, F=10000, E=200e9):
    """Deflexión máxima al centro (m)."""
    I = b * h**3 / 12
    return F * L**3 / (48 * E * I)

def objetivo(X):
    costs = np.zeros(X.shape[0])
    for i, (h, b, L) in enumerate(X):
        rho = 7850  # kg/m³ acero
        peso = rho * b * h * L
        # Penalización por violación de restricciones
        sigma = tension(h, b, L)
        delta = deflexion(h, b, L)
        pen = 1e8 * max(0, sigma - 250e6)**2   # σ ≤ 250 MPa
        pen += 1e8 * max(0, delta - L/300)**2  # δ ≤ L/300
        costs[i] = peso + pen
    return costs

bounds = (np.array([0.05, 0.02, 1.0]),   # mínimos [h, b, L]
          np.array([0.50, 0.30, 8.0]))    # máximos

optimizer = ps.single.GlobalBestPSO(
    n_particles=50, dimensions=3,
    options={'c1': 2.05, 'c2': 2.05, 'w': 0.729},
    bounds=bounds
)
costo, pos = optimizer.optimize(objetivo, iters=500, verbose=False)
h_opt, b_opt, L_opt = pos
print(f"Diseño óptimo: h={h_opt:.3f}m, b={b_opt:.3f}m, L={L_opt:.3f}m")
print(f"Peso mínimo:   {costo:.1f} kg")
```

---

## Guía de selección de algoritmo

| Tipo de problema | Función objetivo | Algoritmo recomendado | Razón principal |
|-----------------|-----------------|----------------------|----------------|
| Unimodal, valle estrecho | Rosenbrock-like | **DE** | Escala adaptativa del operador de mutación |
| Multimodal densa | Rastrigin-like | **DE / PSO** | Alta exploración global |
| Combinatorio (permutaciones) | TSP, scheduling | **ACO / GA-OX** | Operadores que respetan la estructura |
| Diferenciable y convexa | Cuadrática, lineal | **GD** | Convergencia garantizada y rápida |
| Caja negra con ruido | Simulaciones | **DE / EA** | No requiere gradiente, robusto a ruido |
| Alta dimensión (>50D) | Cualquiera | **DE** | Mejor escalabilidad que PSO y EA |
| Presupuesto de evaluaciones muy limitado | Cualquiera | **PSO** | Convergencia rápida con pocos individuos |

---

## Análisis de complejidad computacional

| Algoritmo | Evaluaciones/iter | Complejidad total | Memoria |
|-----------|:-----------------:|:-----------------:|:-------:|
| GD | $O(n)$ (gradiente numérico) | $O(n \cdot T)$ | $O(n)$ |
| EA | $N_\text{pop}$ | $O(N_p \cdot G \cdot n)$ | $O(N_p \cdot n)$ |
| PSO | $N_\text{particles}$ | $O(N_p \cdot T \cdot n)$ | $O(N_p \cdot n)$ |
| DE | $N_\text{pop}$ | $O(N_p \cdot G \cdot n)$ | $O(N_p \cdot n)$ |
| ACO (TSP) | $N_a \cdot n^2$ | $O(N_a \cdot I \cdot n^2)$ | $O(n^2)$ |
| GA (TSP) | $N_\text{pop}$ | $O(N_p \cdot G \cdot n)$ | $O(N_p \cdot n)$ |

> $n$ = dimensión del problema · $T/G/I$ = iteraciones/generaciones · $N$ = tamaño de población

---

## Sensibilidad a hiperparámetros

| Parámetro | Algoritmo | Valor usado | Rango típico | Efecto de aumentar |
|-----------|-----------|:-----------:|:------------:|-------------------|
| $\rho$ (evaporación) | ACO | 0.1 | 0.05–0.3 | Más exploración, menos explotación |
| $\beta$ (heurística) | ACO | 3 | 1–5 | Más greedy (prefiere vecinos cercanos) |
| $F$ (mutación) | DE | 0.5–1.0 | 0.4–1.2 | Mayor diversidad, convergencia más lenta |
| $CR$ (cruce) | DE | 0.7 | 0.5–0.9 | Más componentes del mutante en trial vector |
| $w$ (inercia) | PSO | 0.729 | 0.4–0.9 | Mayor exploración (más inercia) |
| $\sigma$ (mutación) | EA | 0.5 | 0.1–1.0 | Mayor perturbación por mutación |
| $\alpha$ (blend) | EA | 0.5 | 0.0–1.0 | Mayor extrapolación fuera del segmento |

> El valor $w=0.729$ no es arbitrario: es el factor de constricción de Clerc-Kennedy (2002) que garantiza convergencia teórica del enjambre para $c_1 + c_2 = 4.1$.
