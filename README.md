# Optimización Metaheurística: Funciones de Prueba y TSP

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-orange?logo=jupyter)](https://jupyter.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb)

**Curso:** Optimización · **Profesor:** Juan David Ospina Arango
**Universidad Nacional de Colombia** · 2026
**Autores:** Andrés F. Guido Montoya · Juan José Martínez · Andrés Lemus

[Reporte completo](https://docs.google.com/document/d/1eQcFLAz5GOUN9K0MFBEfZ_peTL8IftK03j1gI9b6te0/edit?usp=sharing) · [Notebook 01](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb) · [Notebook 02](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/02_heuristicos_comparativa.ipynb) · [Notebook 03](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/03_tsp_mexico.ipynb)

</div>

---

## Resumen

Comparativa experimental de cuatro algoritmos de optimización —**Descenso por Gradiente (GD)**, **Algoritmos Evolutivos (EA)**, **Optimización por Enjambre de Partículas (PSO)** y **Evolución Diferencial (DE)**— sobre las funciones de prueba de Rosenbrock y Rastrigin en 2D y 3D, con 30 corridas independientes por configuración. Adicionalmente, se resuelve el **Problema del Agente Viajero (TSP)** para las 32 capitales estatales de México con **Colonias de Hormigas (ACO)** y **Algoritmos Genéticos (GA)**, minimizando un modelo de costo económico real (combustible + peajes + tiempo).

**Hallazgo principal:** DE alcanza 100% de tasa de éxito en todos los escenarios con hasta 24× menos evaluaciones que PSO y EA. ACO ofrece mayor consistencia en TSP (CV = 0.72% vs. 2.91% del GA), aunque GA encontró la mejor solución absoluta (55,796 MXN).

---

## Contenido

| # | Notebook | Métodos | Colab |
|---|----------|---------|-------|
| 01 | Funciones de prueba y Descenso por Gradiente | GD (Armijo backtracking) | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb) |
| 02 | Métodos heurísticos — comparativa | EA · PSO · DE | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/02_heuristicos_comparativa.ipynb) |
| 03 | TSP — 32 capitales de México | ACO · GA | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/03_tsp_mexico.ipynb) |

---

## Resultados

### Parte 1 — Funciones de prueba (30 corridas por configuración)

**Rosenbrock** $f(\mathbf{x}) = \sum_{i=1}^{n-1}\left[100(x_{i+1}-x_i^2)^2 + (1-x_i)^2\right]$, óptimo en $\mathbf{x}^*=(1,\ldots,1)$

| Método | 2D — Éxito | 2D — Evals | 3D — Éxito | 3D — Evals |
|--------|:----------:|:----------:|:----------:|:----------:|
| GD     | ~80%       | ~2,000     | ~50%       | ~3,500     |
| EA     | 0%         | 55,100     | 0%         | 55,100     |
| PSO    | 100%       | 25,000     | 10%        | 25,000     |
| **DE** | **100%**   | **~2,100** | **100%**   | **~11,000**|

**Rastrigin** $f(\mathbf{x}) = 10n + \sum_{i=1}^{n}\left[x_i^2 - 10\cos(2\pi x_i)\right]$, óptimo en $\mathbf{x}^*=\mathbf{0}$

| Método | 2D — Éxito | 3D — Éxito | Evals promedio |
|--------|:----------:|:----------:|:--------------:|
| GD     | ~20%       | ~10%       | ~1,500–2,000   |
| EA     | 100%       | 100%       | 55,100         |
| PSO    | 100%       | 100%       | 25,000         |
| **DE** | **100%**   | **100%**   | **~2,300–5,800** |

> Criterio de éxito: $f^* < 10^{-4}$ (Rosenbrock) · $f^* < 1.0$ (Rastrigin)

### Parte 2 — TSP: 32 capitales de México (30 corridas)

Modelo de costo: $C = d_\text{km} \cdot (4.5 + 150/80)$ MXN/km = **6.375 MXN/km** · Distancias haversine

| Método | Media (MXN) | Std (MXN) | Mejor (MXN) | Peor (MXN) | CV (%) | Tiempo (s) |
|--------|:-----------:|:---------:|:-----------:|:----------:|:------:|:----------:|
| **ACO**| **56,957**  | **410**   | 56,195      | 57,715     | **0.72** | 274.6    |
| GA     | 58,744      | 1,710     | **55,796**  | 64,473     | 2.91   | 111.5      |

> ACO: mayor consistencia · GA: mejor solución absoluta en al menos una corrida

---

## Casos de uso y aplicaciones prácticas

Los algoritmos implementados en este repositorio tienen aplicaciones directas en problemas reales de ingeniería, logística y ciencia de datos. A continuación se presentan ejemplos ilustrativos con fragmentos de código reutilizables.

### Caso 1 — Calibración de modelos con múltiples mínimos locales

> **Problema:** Ajustar los parámetros $(\theta_1, \theta_2, \theta_3)$ de un modelo no lineal donde la función de pérdida tiene múltiples mínimos locales (similar a Rastrigin).

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

**¿Por qué DE?** Cuando la función de pérdida tiene múltiples mínimos locales (redes neuronales pequeñas, modelos ODE, ajuste de curvas), DE escapa de ellos gracias a su operador de mutación diferencial. GD quedaría atrapado en el mínimo más cercano al punto inicial.

---

### Caso 2 — Optimización de rutas logísticas (TSP generalizado)

> **Problema:** Un equipo de ventas debe visitar $n$ sucursales minimizando el costo total de combustible + tiempo del vendedor. Aplicación directa del modelo TSP implementado en este repositorio.

```python
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Coordenadas de las sucursales (lat, lon)
SUCURSALES = [
    ("Bogotá",     4.7110, -74.0721),
    ("Medellín",   6.2442, -75.5812),
    ("Cali",       3.4516, -76.5320),
    ("Barranquilla", 10.9685, -74.7813),
    # ... más sucursales
]

COSTO_KM    = 4.5   # COP/km
VEL_KMH     = 80.0
COSTO_HORA  = 50000 # COP/hora vendedor

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def tour_cost(route, D):
    n = len(route)
    km = sum(D[route[i], route[(i+1) % n]] for i in range(n))
    return km * COSTO_KM + (km / VEL_KMH) * COSTO_HORA
```

**Extensiones directas del código:**
- Cambiar coordenadas → aplicable a cualquier país/región
- Modificar `COSTO_KM` y `COSTO_HORA` → adaptar a costos locales
- Agregar ventanas de tiempo → TSP con restricciones (TSPTW)

---

### Caso 3 — Búsqueda de hiperparámetros con EA

> **Problema:** Optimizar hiperparámetros de un modelo de ML (learning rate, regularización, tamaño de capas) sin gradiente, usando EA como caja negra.

```python
from deap import base, creator, tools, algorithms
import numpy as np

# Espacio de búsqueda: [lr, lambda_reg, n_units]
BOUNDS = [(1e-5, 1e-1), (1e-6, 1e-2), (16, 256)]

def evaluate_hyperparams(individual):
    lr, lam, n_units = individual
    n_units = int(n_units)
    # Entrenar modelo con estos hiperparámetros
    val_loss = train_and_evaluate(lr=lr, lambda_reg=lam, n_units=n_units)
    return (val_loss,)  # DEAP requiere tupla

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

tb = base.Toolbox()
tb.register("attr", lambda: [
    np.random.uniform(*BOUNDS[i]) for i in range(3)
])
tb.register("individual", tools.initIterate, creator.Individual, tb.attr)
tb.register("population", tools.initRepeat, list, tb.individual)
tb.register("evaluate", evaluate_hyperparams)
tb.register("mate",   tools.cxBlend, alpha=0.5)
tb.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.3)
tb.register("select", tools.selTournament, tournsize=3)
```

---

### Caso 4 — PSO para diseño de ingeniería

> **Problema:** Minimizar el peso de una viga estructural sujeta a restricciones de resistencia y deflexión, donde el espacio de diseño tiene restricciones no lineales.

```python
import pyswarms as ps
import numpy as np

# Variables: [altura (m), ancho (m), longitud (m)]
# Restricciones: σ_max < 250 MPa, δ_max < L/300
def objective(X):
    costs = np.zeros(X.shape[0])
    for i, params in enumerate(X):
        h, b, L = params
        rho = 7850  # kg/m³ acero
        peso = rho * b * h * L
        # Penalización por violación de restricciones
        sigma = calcular_tension(h, b, L)
        delta = calcular_deflexion(h, b, L)
        penalty = 1e6 * max(0, sigma - 250e6)**2
        penalty += 1e6 * max(0, delta - L/300)**2
        costs[i] = peso + penalty
    return costs

bounds = (np.array([0.1, 0.05, 2.0]),   # mínimos
          np.array([1.0, 0.5,  10.0]))   # máximos

optimizer = ps.single.GlobalBestPSO(
    n_particles=50, dimensions=3,
    options={'c1': 2.05, 'c2': 2.05, 'w': 0.729},
    bounds=bounds
)
cost, pos = optimizer.optimize(objective, iters=500)
```

---

### Guía de selección de algoritmo

| Tipo de problema | Función objetivo | Restricciones | Algoritmo recomendado | Razón |
|-----------------|-----------------|--------------|----------------------|-------|
| Unimodal, valle estrecho | Rosenbrock-like | No | **DE** | Escala adaptativa del operador de mutación |
| Multimodal densa | Rastrigin-like | No | **DE / PSO** | Alta exploración global |
| Combinatorio (permutaciones) | TSP, scheduling | Permutación válida | **ACO / GA-OX** | Operadores que respetan la estructura |
| Diferenciable, convexa | Cuadrática, lineal | Suaves | **GD** | Convergencia garantizada y rápida |
| Caja negra con ruido | Simulaciones | Cualquiera | **DE / EA** | No requiere gradiente, robusto a ruido |
| Alta dimensión (>50D) | Cualquiera | No | **DE** | Mejor escalabilidad que PSO y EA |
| Tiempo de evaluación muy alto | Cualquiera | Cualquiera | **PSO** | Menos evaluaciones por iteración que EA |

---

### Análisis de complejidad computacional

| Algoritmo | Evaluaciones por iteración | Complejidad total | Memoria |
|-----------|:--------------------------:|:-----------------:|:-------:|
| GD        | $O(n)$ (gradiente numérico) | $O(n \cdot T)$ | $O(n)$ |
| EA        | $N_\text{pop}$ | $O(N_\text{pop} \cdot G \cdot n)$ | $O(N_\text{pop} \cdot n)$ |
| PSO       | $N_\text{particles}$ | $O(N_p \cdot T \cdot n)$ | $O(N_p \cdot n)$ |
| DE        | $N_\text{pop}$ | $O(N_\text{pop} \cdot G \cdot n)$ | $O(N_\text{pop} \cdot n)$ |
| ACO (TSP) | $N_\text{ants} \cdot n^2$ | $O(N_a \cdot I \cdot n^2)$ | $O(n^2)$ |
| GA (TSP)  | $N_\text{pop}$ | $O(N_\text{pop} \cdot G \cdot n)$ | $O(N_\text{pop} \cdot n)$ |

> $n$ = dimensión del problema, $T/G/I$ = iteraciones/generaciones, $N$ = tamaño de población

---

### Sensibilidad a hiperparámetros

Los hiperparámetros utilizados provienen directamente de la literatura. La siguiente tabla resume la sensibilidad de cada método:

| Parámetro | Algoritmo | Valor usado | Rango típico | Efecto de aumentar |
|-----------|-----------|:-----------:|:------------:|-------------------|
| $\rho$ (evaporación) | ACO | 0.1 | 0.05–0.3 | Más exploración, menos explotación |
| $\beta$ (heurística) | ACO | 3 | 1–5 | Más greedy (prioriza vecinos cercanos) |
| $F$ (mutación) | DE | 0.5–1.0 | 0.4–1.2 | Mayor diversidad, convergencia más lenta |
| $CR$ (cruce) | DE | 0.7 | 0.5–0.9 | Más componentes del mutante en trial vector |
| $w$ (inercia) | PSO | 0.729 | 0.4–0.9 | Mayor exploración (más inercia) |
| $\sigma$ (mutación) | EA | 0.5 | 0.1–1.0 | Mayor perturbación por mutación |
| $\alpha$ (blend) | EA | 0.5 | 0.0–1.0 | Mayor extrapolación fuera del segmento |

---

## Metodología

```
Diseño experimental
├── 30 corridas independientes por configuración (semillas 0–29)
├── Métricas: media, std, mejor, peor, tasa de éxito, evaluaciones
├── Dominio funciones de prueba: [-5, 5]^n
└── Validez estadística: TCL con N=30 permite prueba t de Student

Parte 1 — Funciones continuas
├── GD: gradiente numérico (diferencias centrales h=1e-5) + Armijo (c=1e-4, β=0.5)
├── EA: DEAP · cxBlend(α=0.5) · mutGaussian(σ=0.5) · torneo k=3 · 100 ind. · 500 gen.
├── PSO: pyswarms · w=0.729 (Clerc-Kennedy) · c1=c2=2.05 · 50 partículas · 500 iter.
└── DE: scipy best1bin · F∈[0.5,1.0] adaptativo · CR=0.7 · popsize=15 · maxiter=1000

Parte 2 — TSP combinatorio
├── Distancias: haversine sobre coordenadas INEGI (32×32 matriz)
├── ACO: 50 hormigas · 300 iter. · α=1 · β=3 · ρ=0.1 · depósito proporcional Q/C
└── GA: DEAP · OX crossover (Davis 1985) · shuffle mutation · 200 ind. · 500 gen. · torneo k=5
```

---

## Estructura del repositorio

```
optimizacion-metaheuristicas/
│
├── notebooks/
│   ├── 01_funciones_gradiente.ipynb     # GD sobre Rosenbrock / Rastrigin
│   ├── 02_heuristicos_comparativa.ipynb # EA, PSO, DE — comparativa estadística
│   ├── 03_tsp_mexico.ipynb              # ACO y GA — TSP 32 capitales
│   └── outputs/                         # JSON de resultados y GIFs de convergencia
│
├── report/
│   ├── blog_post.md                     # Reporte completo en Markdown
│   ├── ai_prompts_log.md                # Registro de uso de IA
│   ├── teoria_01_funciones_gradiente.md # Marco teórico notebook 01
│   ├── teoria_02_heuristicos.md         # Marco teórico notebook 02
│   └── teoria_03_tsp_mexico.md          # Marco teórico notebook 03
│
├── scripts/
│   └── heuristicos.py                   # Script de validación Parte 1
│
├── requirements.txt
└── LICENSE
```

---

## Reproducibilidad

### Google Colab (recomendado)

Haz clic en **▶ Abrir** en la tabla de contenido. La primera celda instala las dependencias automáticamente. Ejecuta con `Ctrl+F9`.

### Local

```bash
git clone https://github.com/AndresGuido9820/optimizacion-metaheuristicas.git
cd optimizacion-metaheuristicas
pip install -r requirements.txt
jupyter notebook notebooks/
```

Todos los experimentos usan semillas fijas (0–29). Los resultados en `notebooks/outputs/resultados_tsp.json` permiten reproducir tablas y figuras sin re-ejecutar los 60 experimentos del TSP (~6 min en CPU).

---

## Marco teórico

La documentación teórica completa de cada notebook está en `report/`:

| Archivo | Contenido |
|---------|-----------|
| [`teoria_01_funciones_gradiente.md`](report/teoria_01_funciones_gradiente.md) | Rosenbrock, Rastrigin, GD + búsqueda en línea Armijo |
| [`teoria_02_heuristicos.md`](report/teoria_02_heuristicos.md) | EA (cxBlend), PSO (factor Clerc-Kennedy), DE (escala adaptativa) |
| [`teoria_03_tsp_mexico.md`](report/teoria_03_tsp_mexico.md) | TSP, haversine, ACO (feromona), GA (OX crossover) |

---

## Temas de discusión abierta

Preguntas científicas que surgen de los resultados experimentales y pueden extenderse en trabajos futuros:

**1. ¿Es DE siempre superior?**
DE dominó en este estudio, pero el **Teorema de No Free Lunch** (Wolpert & Macready, 1997) garantiza que ningún algoritmo es universalmente mejor. ¿En qué clase de problemas fallaría DE? Considera: funciones separables de alta dimensión, espacios discretos, problemas con restricciones duras.

**2. Feromona vs. genes: ¿qué modelo de memoria es más eficiente?**
ACO usa memoria explícita (matriz de feromona $\tau \in \mathbb{R}^{n \times n}$, costo $O(n^2)$); GA usa memoria implícita (genes en la población). Para $n$ grande, ¿el costo de memoria de ACO se justifica con la mayor consistencia (CV=0.72%)?

**3. El efecto de la dimensionalidad en PSO**
PSO logró 100% de éxito en Rosenbrock 2D pero cayó a 10% en 3D. ¿Por qué la "maldición de la dimensionalidad" afecta más a PSO que a DE? Pista: la velocidad de PSO tiene componentes fijas de tamaño $O(\|\mathbf{p}_i - \mathbf{x}_i\|)$, mientras que la mutación de DE escala con la dispersión de la población.

**4. Representación y factibilidad en problemas combinatorios**
¿Por qué el OX crossover es necesario y no puede usarse cruce de un punto estándar en TSP? Diseña un contraejemplo con $n=6$ ciudades que muestre cómo el cruce estándar produce un tour inválido.

**5. Distancia haversine vs. red vial real**
Las distancias haversine subestiman el recorrido real en ~30% en México (factor de sinuosidad empírico ≈ 1.3 para carreteras secundarias, ≈ 1.15 para autopistas). ¿Cambiaría la ruta óptima si se usaran distancias reales de la red vial del INEGI? Hipótesis: el orden relativo de ciudades cercanas cambiaría, pero la estructura global de la ruta (norte→pacífico→centro→sur→yucatán) se mantendría.

**6. Convergencia prematura en ACO**
Con $\rho=0.1$, la feromona retiene 90% de su valor entre iteraciones. Si la mejor solución encontrada en las primeras 50 iteraciones es subóptima, ¿el enjambre puede escapar de esa atracción? Analiza el efecto de aumentar $\rho$ a 0.3 sobre la media y el CV.

**7. Inicialización de la población**
Todos los métodos usan inicialización uniforme aleatoria. ¿Mejoraría el rendimiento en Rosenbrock una inicialización inteligente (e.g., a lo largo de la parábola $x_2 = x_1^2$)? ¿Constituiría esto sesgo en la comparativa?

**8. Pruebas estadísticas para comparación de métodos**
Con 30 corridas, ¿las diferencias observadas son estadísticamente significativas? Aplica la prueba de Wilcoxon rank-sum (no paramétrica) entre DE y PSO en Rosenbrock 3D. ¿Cuál es el p-value? ¿Se rechaza $H_0$: "no hay diferencia" con $\alpha=0.05$?

---

## Limitaciones y trabajo futuro

**Limitaciones del estudio:**
- Las distancias haversine aproximan la geodésica esférica; no reflejan la red vial real (sinuosidad, pendientes, zonas sin carretera directa).
- El modelo de costo es estático: no considera variación de precios de combustible por estado, peajes diferenciados por tramo, ni restricciones de horario.
- Los hiperparámetros se tomaron de la literatura sin sintonización bayesiana; resultados pueden mejorar con optimización de hiperparámetros.
- El TSP asume simetría ($d_{ij} = d_{ji}$); peajes unidireccionales y condiciones de terreno pueden romper este supuesto.
- Se evaluaron solo dimensiones 2D y 3D; el comportamiento en dimensiones altas ($n > 10$) requiere estudio separado.

**Extensiones propuestas:**
- Incorporar distancias reales de la API de Google Maps o del grafo vial del INEGI para el TSP México.
- Evaluar variantes avanzadas: **ACS** (Ant Colony System) y **MMAS** (Max-Min Ant System) para ACO; operadores **Lin-Kernighan** para GA.
- Extender a dimensiones $n \in \{5, 10, 20, 50\}$ para estudiar escalabilidad.
- Aplicar **Optimización Bayesiana** para sintonización automática de hiperparámetros.
- Incorporar pruebas estadísticas formales (Wilcoxon, Kruskal-Wallis) en la comparativa.
- Evaluar **CEC benchmark functions** (CEC 2017, CEC 2022) para comparación estandarizada con la literatura.

---

## Citar este trabajo

```bibtex
@misc{guido2026metaheuristicas,
  author       = {Guido Montoya, Andrés Felipe and Martínez, Juan José and Lemus, Andrés},
  title        = {Optimización Metaheurística: Comparativa sobre Funciones de Prueba y TSP},
  year         = {2026},
  institution  = {Universidad Nacional de Colombia},
  url          = {https://github.com/AndresGuido9820/optimizacion-metaheuristicas},
  note         = {Curso: Optimización, Prof. Juan David Ospina Arango}
}
```

---

## Referencias principales

- Storn, R., & Price, K. (1997). Differential evolution. *Journal of Global Optimization*, 11(4), 341–359.
- Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. *ICNN*, 4, 1942–1948.
- Clerc, M., & Kennedy, J. (2002). The particle swarm — Explosion, stability, and convergence. *IEEE TEC*, 6(1), 58–73.
- Dorigo, M. (1992). *Optimization, learning and natural algorithms* [Tesis doctoral]. Politecnico di Milano.
- Davis, L. (1985). Applying adaptive algorithms to epistatic domains. *IJCAI*, 162–164.
- Rosenbrock, H. H. (1960). An automatic method for finding the greatest or least value of a function. *The Computer Journal*, 3(3), 175–184.

---

<div align="center">
Universidad Nacional de Colombia · Facultad de Minas · 2026
</div>
