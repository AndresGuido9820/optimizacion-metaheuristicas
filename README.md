# Optimización Heurística — Metaheurísticas en Funciones de Prueba y TSP

**Curso:** Optimización
**Profesor:** Juan David Ospina Arango
**Universidad:** Universidad Nacional de Colombia
**Autores:** Andrés Felipe Guido Montoya · Juan José Martínez · Andrés Lemus
**Entrega:** 24 de marzo de 2026

---

## Descripción

Comparativa experimental de metaheurísticas aplicadas a dos problemas clásicos de optimización:

**Parte 1 — Funciones de prueba continuas**
Minimización de Rosenbrock y Rastrigin en 2D y 3D con 30 corridas independientes por configuración:
- Descenso por gradiente con búsqueda en línea (Armijo backtracking)
- Algoritmos evolutivos — EA (DEAP, cxBlend + mutGaussian)
- Optimización por enjambre de partículas — PSO (pyswarms, factor de constricción Clerc-Kennedy)
- Evolución diferencial — DE (scipy best1bin, F adaptativo)

**Parte 2 — TSP: 32 capitales estatales de México**
Minimización del costo de viaje (combustible + peajes + tiempo del vendedor) con distancias haversine:
- Colonias de hormigas — ACO (depósito proporcional, ρ=0.1)
- Algoritmos genéticos — GA (OX crossover, shuffle mutation, DEAP)

---

## Resultados principales

| Método | Rosenbrock 2D | Rastrigin 2D | Evals promedio |
|--------|:-------------:|:------------:|:--------------:|
| GD     | ~80% éxito    | ~20% éxito   | ~2,000         |
| EA     | 0% éxito      | 100% éxito   | 55,100         |
| PSO    | 100% éxito    | 100% éxito   | 25,000         |
| **DE** | **100% éxito**| **100% éxito**| **~2,100**    |

| Método | Media (MXN) | Std (MXN) | Mejor (MXN) | CV (%) |
|--------|:-----------:|:---------:|:-----------:|:------:|
| ACO    | 56,957      | 410       | 56,195      | 0.72   |
| GA     | 58,744      | 1,710     | 55,796      | 2.91   |

---

## Estructura del repositorio

```
notebooks/
  01_gradiente_EA.ipynb      # GD y EA sobre Rosenbrock / Rastrigin
  02_PSO_DE.ipynb            # PSO y DE sobre Rosenbrock / Rastrigin
  03_tsp_mexico.ipynb        # ACO y GA sobre las 32 capitales de México
  outputs/                   # Resultados JSON y GIFs de convergencia

report/
  blog_post.md               # Reporte completo en Markdown
  ai_prompts_log.md          # Registro de prompts de IA utilizados
  generar_reporte.py         # Genera el reporte Word (APA 7)

scripts/
  heuristicos.py             # Script de validación Parte 1 (local)
```

---

## Notebooks en Google Colab

| Notebook | Colab |
|----------|-------|
| 01 — GD y EA | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndresGuido9820/tarea01-optimizacion-heuristica/blob/main/notebooks/01_gradiente_EA.ipynb) |
| 02 — PSO y DE | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndresGuido9820/tarea01-optimizacion-heuristica/blob/main/notebooks/02_PSO_DE.ipynb) |
| 03 — TSP México | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndresGuido9820/tarea01-optimizacion-heuristica/blob/main/notebooks/03_tsp_mexico.ipynb) |

---

## Reporte

https://docs.google.com/document/d/1eQcFLAz5GOUN9K0MFBEfZ_peTL8IftK03j1gI9b6te0/edit?usp=sharing

---

## Dependencias

```bash
pip install numpy scipy matplotlib pillow deap pyswarms pandas
```

---

## Referencias clave

- Storn, R., & Price, K. (1997). Differential evolution. *Journal of Global Optimization*, 11(4), 341–359.
- Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. *ICNN*, 4, 1942–1948.
- Dorigo, M. (1992). *Optimization, learning and natural algorithms* [Tesis doctoral]. Politecnico di Milano.
- Holland, J. H. (1975). *Adaptation in natural and artificial systems*. University of Michigan Press.
- Rosenbrock, H. H. (1960). An automatic method for finding the greatest or least value of a function. *The Computer Journal*, 3(3), 175–184.
