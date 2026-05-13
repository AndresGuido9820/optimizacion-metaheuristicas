# Trabajo 01 — Optimización Heurística

**Curso:** Optimización
**Profesor:** Juan David Ospina Arango
**Entrega:** 24 de marzo de 2026

---

## Contenido

### Parte 1 — Optimización numérica
Minimización de las funciones de prueba **Rosenbrock** y **Rastrigin** en 2D y 3D usando:
- Descenso por gradiente (con condición inicial aleatoria)
- Algoritmos evolutivos (EA)
- Optimización por enjambre de partículas (PSO)
- Evolución diferencial (DE)

Incluye animaciones GIF del proceso de optimización para cada método.

### Parte 2 — TSP: Capitales de México
Recorrido óptimo por las 32 capitales estatales de México minimizando el costo total de viaje (combustible + peajes + tiempo del vendedor), usando:
- Colonias de hormigas (ACO)
- Algoritmos genéticos (GA)

Incluye animación GIF del recorrido sobre el mapa de México.

---

## Estructura

```
part1/        # Funciones de prueba, GD, EA, PSO, DE, experimentos
part2/        # Capitales, modelo de costos, ACO, GA, comparativa
animations/   # GIFs de convergencia y mapa
report/       # Entrada de blog + registro de prompts de IA
```

## Dependencias

```bash
pip install numpy scipy matplotlib pillow deap pyswarms geopandas contextily pandas
```

## Reporte

Publicado en: [enlace al blog]

## Repositorio

https://github.com/AndresGuido9820/tarea01-optimizacion-heuristica
