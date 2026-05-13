# Optimización Metaheurística: Funciones de Prueba y TSP

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-orange?logo=jupyter)](https://jupyter.org/)
[![Validacion](https://github.com/AndresGuido9820/optimizacion-metaheuristicas/actions/workflows/validacion.yml/badge.svg)](https://github.com/AndresGuido9820/optimizacion-metaheuristicas/actions/workflows/validacion.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb)

**Curso:** Optimización · **Profesor:** Juan David Ospina Arango
**Universidad Nacional de Colombia** · 2026
**Autores:** Andrés F. Guido Montoya · Juan José Martínez · Andrés Lemus

[Reporte completo](https://docs.google.com/document/d/1eQcFLAz5GOUN9K0MFBEfZ_peTL8IftK03j1gI9b6te0/edit?usp=sharing) · [Notebook 01](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb) · [Notebook 02](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/02_heuristicos_comparativa.ipynb) · [Notebook 03](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/03_tsp_mexico.ipynb)

</div>

---

## Resumen

Comparativa experimental de cuatro algoritmos de optimización —**GD**, **EA**, **PSO** y **DE**— sobre las funciones de Rosenbrock y Rastrigin en 2D y 3D, con 30 corridas independientes por configuración. En la Parte 2 se resuelve el **TSP** para las 32 capitales estatales de México con **ACO** y **GA**, minimizando un modelo de costo económico real (combustible + peajes + tiempo del vendedor).

**Hallazgo principal:** DE alcanza 100% de tasa de éxito en todos los escenarios con hasta 24× menos evaluaciones que PSO y EA. ACO ofrece mayor consistencia en TSP (CV = 0.72% vs. 2.91% del GA), aunque GA encontró la mejor solución absoluta (55,796 MXN).

**Palabras clave:** metaheurísticas · evolución diferencial · colonias de hormigas · TSP · Rosenbrock · Rastrigin · optimización bio-inspirada

---

## Notebooks

| # | Contenido | Métodos | Colab |
|---|-----------|---------|-------|
| 01 | Funciones de prueba y Descenso por Gradiente | GD + Armijo backtracking | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb) |
| 02 | Heurísticos — comparativa estadística | EA · PSO · DE | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/02_heuristicos_comparativa.ipynb) |
| 03 | TSP — 32 capitales de México | ACO · GA | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/03_tsp_mexico.ipynb) |

---

## Resultados

### Parte 1 — Funciones de prueba (30 corridas · dominio $[-5,5]^n$)

**Rosenbrock** — $f(\mathbf{x}) = \sum_{i=1}^{n-1}\left[100(x_{i+1}-x_i^2)^2 + (1-x_i)^2\right]$, $\mathbf{x}^*=(1,\ldots,1)$, umbral $f^*<10^{-4}$

| Método | 2D — Éxito | 2D — Evals | 3D — Éxito | 3D — Evals |
|--------|:----------:|:----------:|:----------:|:----------:|
| GD     | ~80%       | ~2,000     | ~50%       | ~3,500     |
| EA     | 0%         | 55,100     | 0%         | 55,100     |
| PSO    | 100%       | 25,000     | 10%        | 25,000     |
| **DE** | **100%**   | **~2,100** | **100%**   | **~11,000**|

**Rastrigin** — $f(\mathbf{x}) = 10n + \sum_{i=1}^{n}\left[x_i^2 - 10\cos(2\pi x_i)\right]$, $\mathbf{x}^*=\mathbf{0}$, umbral $f^*<1.0$

| Método | 2D — Éxito | 3D — Éxito | Evals promedio |
|--------|:----------:|:----------:|:--------------:|
| GD     | ~20%       | ~10%       | ~1,500–2,000   |
| EA     | 100%       | 100%       | 55,100         |
| PSO    | 100%       | 100%       | 25,000         |
| **DE** | **100%**   | **100%**   | **~2,300–5,800**|

### Parte 2 — TSP: 32 capitales de México (30 corridas)

Costo: $C = d_\text{km} \cdot (4.5 + 150/80) = 6.375$ MXN/km · Distancias haversine sobre coordenadas INEGI

| Método | Media (MXN) | Std (MXN) | Mejor (MXN) | Peor (MXN) | CV (%) | Tiempo (s) |
|--------|:-----------:|:---------:|:-----------:|:----------:|:------:|:----------:|
| **ACO**| **56,957**  | **410**   | 56,195      | 57,715     | **0.72** | 274.6    |
| GA     | 58,744      | 1,710     | **55,796**  | 64,473     | 2.91   | 111.5      |

> ACO: mayor consistencia (CV=0.72%) · GA: mejor solución absoluta en al menos 1 de 30 corridas

---

## Metodología

```
Diseño experimental
├── 30 corridas independientes por configuración (semillas 0–29)
├── Métricas: media, std, mejor, peor, tasa de éxito, n° evaluaciones
├── Dominio funciones de prueba: [-5, 5]^n
└── Validez estadística: TCL con N=30 permite prueba t de Student

Parte 1 — Funciones continuas
├── GD:  gradiente numérico (diferencias centrales h=1e-5) + Armijo (c=1e-4, β=0.5)
├── EA:  DEAP · cxBlend(α=0.5) · mutGaussian(σ=0.5) · torneo k=3 · 100 ind. · 500 gen.
├── PSO: pyswarms · w=0.729 (Clerc-Kennedy) · c1=c2=2.05 · 50 partículas · 500 iter.
└── DE:  scipy best1bin · F∈[0.5,1.0] adaptativo · CR=0.7 · popsize=15 · maxiter=1000

Parte 2 — TSP combinatorio
├── Distancias: haversine · matriz 32×32 · suma total de pares ≈ 427,770 km
├── ACO: 50 hormigas · 300 iter. · α=1 · β=3 · ρ=0.1 · depósito proporcional Q/C
└── GA:  DEAP · OX crossover (Davis, 1985) · shuffle mutation · 200 ind. · 500 gen. · torneo k=5
```

---

## Documentación

| Archivo | Descripción |
|---------|-------------|
| [blog_post.md](report/blog_post.md) | Reporte completo con introducción, resultados y discusión |
| [teoria_01_funciones_gradiente.md](report/teoria_01_funciones_gradiente.md) | Rosenbrock, Rastrigin, GD y búsqueda en línea de Armijo |
| [teoria_02_heuristicos.md](report/teoria_02_heuristicos.md) | EA (cxBlend), PSO (factor Clerc-Kennedy), DE (escala adaptativa) |
| [teoria_03_tsp_mexico.md](report/teoria_03_tsp_mexico.md) | TSP, haversine, ACO (feromona), GA (OX crossover) |
| [casos_de_uso.md](report/casos_de_uso.md) | Ejemplos de código reutilizables, guía de selección de algoritmo, análisis de complejidad |
| [discusion.md](report/discusion.md) | Temas de discusión abierta, limitaciones y trabajo futuro |
| [ai_prompts_log.md](report/ai_prompts_log.md) | Registro de uso de IA en el desarrollo |

---

## Estructura del repositorio

```
optimizacion-metaheuristicas/
│
├── notebooks/
│   ├── 01_funciones_gradiente.ipynb
│   ├── 02_heuristicos_comparativa.ipynb
│   ├── 03_tsp_mexico.ipynb
│   └── outputs/                    ← JSON de resultados y GIFs de convergencia
│
├── report/
│   ├── blog_post.md
│   ├── teoria_01_funciones_gradiente.md
│   ├── teoria_02_heuristicos.md
│   ├── teoria_03_tsp_mexico.md
│   ├── casos_de_uso.md
│   ├── discusion.md
│   └── ai_prompts_log.md
│
├── scripts/
│   └── heuristicos.py              ← Script de validación Parte 1
│
├── requirements.txt
└── LICENSE
```

---

## Reproducibilidad

**Google Colab** — clic en **▶ Abrir** en la tabla de notebooks. La primera celda instala dependencias. Ejecutar con `Ctrl+F9`.

**Local:**
```bash
git clone https://github.com/AndresGuido9820/optimizacion-metaheuristicas.git
cd optimizacion-metaheuristicas
pip install -r requirements.txt
jupyter notebook notebooks/
```

Los experimentos usan semillas fijas (0–29). `notebooks/outputs/resultados_tsp.json` contiene los resultados pre-computados de las 60 corridas del TSP para reproducir tablas y figuras sin re-ejecutar (~6 min en CPU).

---

## Citar este trabajo

```bibtex
@misc{guido2026metaheuristicas,
  author      = {Guido Montoya, Andrés Felipe and Martínez, Juan José and Lemus, Andrés},
  title       = {Optimización Metaheurística: Comparativa sobre Funciones de Prueba y TSP},
  year        = {2026},
  institution = {Universidad Nacional de Colombia},
  url         = {https://github.com/AndresGuido9820/optimizacion-metaheuristicas},
  note        = {Curso: Optimización, Prof. Juan David Ospina Arango}
}
```

---

## Referencias

- Storn, R., & Price, K. (1997). Differential evolution. *Journal of Global Optimization*, 11(4), 341–359.
- Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. *ICNN*, 4, 1942–1948.
- Clerc, M., & Kennedy, J. (2002). The particle swarm — Explosion, stability, and convergence. *IEEE TEC*, 6(1), 58–73.
- Dorigo, M. (1992). *Optimization, learning and natural algorithms* [Tesis doctoral]. Politecnico di Milano.
- Davis, L. (1985). Applying adaptive algorithms to epistatic domains. *IJCAI*, 162–164.
- Wolpert, D. H., & Macready, W. G. (1997). No free lunch theorems for optimization. *IEEE TEC*, 1(1), 67–82.
- Rosenbrock, H. H. (1960). An automatic method for finding the greatest or least value of a function. *The Computer Journal*, 3(3), 175–184.

---

<div align="center">
Universidad Nacional de Colombia · Facultad de Minas · 2026
</div>
