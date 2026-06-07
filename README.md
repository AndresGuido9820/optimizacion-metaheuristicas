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

[Reporte completo](https://docs.google.com/document/d/1eQcFLAz5GOUN9K0MFBEfZ_peTL8IftK03j1gI9b6te0/edit?usp=sharing) · [Notebook 01](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb) · [Notebook 02](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/02_heuristicos_comparativa.ipynb) · [Notebook 03](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/03_tsp_france.ipynb)

</div>

---

## Resumen

Comparativa experimental de cuatro algoritmos de optimización —**GD**, **EA**, **PSO** y **DE**— sobre **seis funciones de prueba clásicas** (Rosenbrock, Rastrigin, Schwefel, Griewank, Goldstein-Price y Camel 6-hump) en 2D y 3D, con n = 100/500/1 000 condiciones iniciales para GD y 30 corridas independientes para los métodos heurísticos. En la Parte 2 se resuelve el **TSP** para las **96 prefecturas de los departamentos de la Francia metropolitana** con **ACO** y **GA**, minimizando un modelo de costo económico real (combustible + peajes + tiempo del vendedor) en EUR.

**Palabras clave:** metaheurísticas · evolución diferencial · colonias de hormigas · TSP · Rosenbrock · Rastrigin · Schwefel · Griewank · Goldstein-Price · Camel · optimización bio-inspirada

---

## Notebooks

| # | Contenido | Métodos | Colab |
|---|-----------|---------|-------|
| 01 | Seis funciones de prueba y Descenso por Gradiente | GD + Armijo backtracking · n=100/500/1 000 histogramas | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/01_funciones_gradiente.ipynb) |
| 02 | Heurísticos — comparativa estadística sobre 6 funciones | EA · PSO · DE · 30 corridas | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/02_heuristicos_comparativa.ipynb) |
| 03 | TSP — 96 prefecturas de la Francia metropolitana | ACO · GA · modelo de costo EUR | [▶ Abrir](https://colab.research.google.com/github/AndresGuido9820/optimizacion-metaheuristicas/blob/main/notebooks/03_tsp_france.ipynb) |

---

## Funciones de prueba

| Función | Fórmula | Dominio | Mínimo global | Dim |
|---------|---------|---------|---------------|-----|
| **Rosenbrock** | $\sum_{i} [100(x_{i+1}-x_i^2)^2+(1-x_i)^2]$ | $[-5,5]^n$ | $f(\mathbf{1})=0$ | 2D, 3D |
| **Rastrigin** | $10n+\sum_i[x_i^2-10\cos(2\pi x_i)]$ | $[-5,5]^n$ | $f(\mathbf{0})=0$ | 2D, 3D |
| **Schwefel** | $418.98\,n - \sum_i x_i\sin(\sqrt{|x_i|})$ | $[-500,500]^n$ | $f(420.97,\ldots)\approx 0$ | 2D, 3D |
| **Griewank** | $1+\frac{\sum x_i^2}{4000}-\prod\cos\!\frac{x_i}{\sqrt{i}}$ | $[-600,600]^n$ | $f(\mathbf{0})=0$ | 2D, 3D |
| **Goldstein-Price** | ver [Wikipedia](https://en.wikipedia.org/wiki/Test_functions_for_optimization) | $[-2,2]^2$ | $f(0,-1)=3$ | solo 2D |
| **Camel 6-hump** | $(4-2.1x_1^2+\frac{x_1^4}{3})x_1^2+x_1x_2+(-4+4x_2^2)x_2^2$ | $x_1\!\in\![-3,3],x_2\!\in\![-2,2]$ | $\approx -1.0316$ | solo 2D |

---

## Metodología

```
Diseño experimental
├── GD: n = 100, 500 y 1 000 condiciones iniciales aleatorias (histogramas de f* y evals)
├── Heurísticos: 30 corridas independientes por configuración (semillas 0–29)
├── Métricas: media, std, mejor, peor, tasa de éxito, n° evaluaciones
└── Validez estadística: TCL con N=30 permite prueba t de Student

Parte 1 — Funciones continuas
├── GD:  gradiente numérico (diferencias centrales h=1e-5) + Armijo (c=1e-4, β=0.5)
├── EA:  DEAP · cxBlend(α=0.5) · mutGaussian(σ=0.5) · torneo k=3 · 100 ind. · 500 gen.
├── PSO: pyswarms · w=0.729 (Clerc-Kennedy) · c1=c2=2.05 · 50 partículas · 500 iter.
└── DE:  scipy best1bin · F∈[0.5,1.0] adaptativo · CR=0.7 · popsize=15 · maxiter=1000

Parte 2 — TSP combinatorio (Francia · 96 prefecturas)
├── Distancias: haversine · matriz 96×96
├── Costo: combustible (Renault Clio, SP95 1.75 EUR/L) + peajes 0.08 EUR/km + 25 EUR/h
├── ACO: 50 hormigas · 300 iter. · α=1 · β=3 · ρ=0.1 · depósito proporcional Q/C
└── GA:  DEAP · OX crossover · shuffle mutation · 200 ind. · 500 gen. · torneo k=5
```

---

## Documentación

| Archivo | Descripción |
|---------|-------------|
| [blog_post.md](report/blog_post.md) | Reporte completo — introducción, marco teórico, resultados y discusión |
| [teoria_01_funciones_gradiente.md](report/teoria_01_funciones_gradiente.md) | Las seis funciones, GD y búsqueda en línea de Armijo |
| [teoria_02_heuristicos.md](report/teoria_02_heuristicos.md) | EA (cxBlend), PSO (factor Clerc-Kennedy), DE (escala adaptativa) |
| [teoria_03_tsp_france.md](report/teoria_03_tsp_france.md) | TSP, haversine, ACO (feromona), GA (OX crossover), modelo de costo Francia |
| [casos_de_uso.md](report/casos_de_uso.md) | Ejemplos de código reutilizables y guía de selección de algoritmo |
| [discusion.md](report/discusion.md) | Temas de discusión abierta, limitaciones y trabajo futuro |
| [ai_prompts_log.md](report/ai_prompts_log.md) | Registro de uso de IA en el desarrollo |

---

## Estructura del repositorio

```
optimizacion-metaheuristicas/
│
├── notebooks/
│   ├── 01_funciones_gradiente.ipynb    ← GD + 6 funciones + histogramas n=100/500/1000
│   ├── 02_heuristicos_comparativa.ipynb← EA / PSO / DE sobre 6 funciones
│   ├── 03_tsp_france.ipynb             ← ACO + GA sobre 96 prefecturas de Francia
│   └── outputs/                        ← JSON de resultados y GIFs de convergencia
│
├── report/
│   ├── blog_post.md                    ← Reporte completo (entrada de blog)
│   ├── teoria_01_funciones_gradiente.md
│   ├── teoria_02_heuristicos.md
│   ├── teoria_03_tsp_france.md
│   ├── casos_de_uso.md
│   ├── discusion.md
│   └── ai_prompts_log.md
│
├── scripts/
│   └── heuristicos.py                  ← Script de validación Parte 1 (línea de comandos)
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

Los experimentos usan semillas fijas (0–29). `notebooks/outputs/resultados_tsp.json` contiene los resultados pre-computados del TSP para reproducir tablas y figuras sin re-ejecutar.

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
- Schwefel, H.-P. (1981). *Numerical optimization of computer models*. Wiley.
- Griewank, A. (1981). Generalized descent for global optimization. *Journal of Optimization Theory and Applications*, 34(1), 11–39.
- Dixon, L. C. W., & Szegö, G. P. (1978). The global optimization problem: An introduction. *Towards Global Optimization*, 2, 1–15.

---

<div align="center">
Universidad Nacional de Colombia · Facultad de Minas · 2026
</div>
