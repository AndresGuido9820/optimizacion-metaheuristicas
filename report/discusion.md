# Discusión, Limitaciones y Trabajo Futuro

---

## Temas de discusión abierta

Preguntas científicas que surgen de los resultados experimentales y que pueden extenderse en trabajos futuros o proyectos de investigación.

---

### 1. ¿Es DE siempre superior? El Teorema de No Free Lunch

DE dominó en este estudio (100% de éxito, mínimas evaluaciones), pero el **Teorema de No Free Lunch** (Wolpert & Macready, 1997) establece que ningún algoritmo es universalmente mejor que otro en el promedio sobre todos los problemas posibles. En clases de problemas donde DE fallaría:

- **Espacios discretos o combinatorios:** DE opera sobre vectores reales; su adaptación a permutaciones requiere codificación especial y pierde su ventaja de escala adaptativa.
- **Funciones separables de alta dimensión:** En problemas donde cada variable es independiente, los métodos coordenada a coordenada (coordinate descent) son más eficientes que la diferenciación vectorial de DE.
- **Restricciones duras:** DE no tiene mecanismo nativo para manejar restricciones; requiere funciones de penalización que pueden distorsionar el paisaje de fitness.
- **Evaluaciones extremadamente costosas ($\leq 100$):** Con presupuestos muy limitados, la **Optimización Bayesiana** (Gaussian Process + acquisition function) supera a DE al modelar la función objetivo explícitamente.

---

### 2. Feromona vs. genes: dos modelos de memoria colectiva

ACO usa **memoria explícita** (matriz de feromona $\tau \in \mathbb{R}^{n \times n}$, costo $O(n^2)$); GA usa **memoria implícita** (genes distribuidos en la población). Esto genera una tensión fundamental:

| Característica | ACO | GA |
|---|---|---|
| Costo de memoria | $O(n^2)$ — crece cuadráticamente | $O(N_\text{pop} \cdot n)$ — lineal en $n$ |
| Velocidad de convergencia | Suave, monotónica | Errática, con saltos abruptos |
| Capacidad de pico | Menor (CV=0.72%) | Mayor (encontró la mejor absoluta) |
| Riesgo de estancamiento | Alto si $\rho$ es pequeño | Bajo por diversidad genética |

Para $n=32$ capitales, $O(n^2) = 1024$ celdas de feromona es trivial. Para $n=1000$ ciudades, la matriz ocupa ~8 MB y el cómputo de probabilidades de transición domina el tiempo de ejecución.

---

### 3. El efecto de la dimensionalidad en PSO

PSO logró 100% de éxito en Rosenbrock 2D pero cayó a 10% en 3D. La razón es estructural: el **valle estrecho de Rosenbrock en 3D** requiere navegar simultáneamente dos parábolas acopladas. La velocidad de PSO tiene componentes de tamaño $\|\mathbf{p}_i - \mathbf{x}_i\|$ y $\|\mathbf{g} - \mathbf{x}_i\|$, que son independientes de la forma local del valle. DE, en cambio, usa diferencias entre individuos que se adaptan automáticamente a la geometría local.

**Pregunta abierta:** ¿Mejora PSO con una topología de vecindad local (lbest) en lugar de global (gbest) en Rosenbrock 3D? La topología lbest reduce la velocidad de convergencia pero mantiene más diversidad.

---

### 4. Representación y factibilidad en problemas combinatorios

El OX crossover es necesario porque el cruce estándar produce tours inválidos. Contraejemplo con $n=6$ ciudades:

```
Padre 1:  [1, 2, 3 | 4, 5, 6]
Padre 2:  [4, 5, 2 | 1, 3, 6]

Cruce 1 punto (inválido):
  Hijo A: [1, 2, 3 | 1, 3, 6]  ← ciudades 1 y 3 repetidas, falta 4 y 5
  Hijo B: [4, 5, 2 | 4, 5, 6]  ← ciudades 4 y 5 repetidas, falta 1 y 3

OX crossover (válido), segmento [1,3] de Padre 1:
  Segmento copiado: [_, 2, 3, 4, _, _]
  Relleno con P2 en orden (omitiendo {2,3,4}): 5, 1, 6
  Hijo A: [5, 2, 3, 4, 1, 6]  ← permutación válida
```

Esta propiedad es fundamental: en optimización combinatoria, **la factibilidad de la solución debe ser mantenida por los operadores**, no recuperada mediante penalización posterior.

---

### 5. Distancia haversine vs. red vial real

Las distancias haversine subestiman el recorrido real. Para México:

| Tipo de vía | Factor de sinuosidad empírico |
|-------------|:-----------------------------:|
| Autopistas de cuota | ~1.10–1.15 |
| Carreteras federales | ~1.20–1.30 |
| Carreteras secundarias | ~1.30–1.50 |
| Promedio nacional | ~1.25 |

**Impacto en el modelo:** Si todos los arcos se multiplican por el mismo factor $k=1.25$, el costo total escala linealmente ($C_\text{real} \approx 1.25 \cdot C_\text{haversine}$) pero **la ruta óptima no cambia** (el factor cancela al comparar tours). Sin embargo, si el factor varía por tramo (e.g., Baja California tiene carreteras largas con poca sinuosidad vs. Oaxaca con carreteras montañosas), la ruta óptima sí cambiaría.

---

### 6. Convergencia prematura en ACO y el rol de la evaporación

Con $\rho=0.1$, después de $t$ iteraciones sin actualización, la feromona decae a $(0.9)^t \cdot \tau_0$. Para $t=50$, $(0.9)^{50} \approx 0.005$: la feromona inicial es prácticamente irrelevante. Si la mejor solución encontrada en las primeras 50 iteraciones es subóptima, el enjambre quedará atraído hacia esa región.

**Mecanismos de diversificación en variantes avanzadas:**
- **MMAS (Max-Min Ant System):** Limita la feromona al rango $[\tau_\text{min}, \tau_\text{max}]$, evitando colapso.
- **ACS (Ant Colony System):** Combina actualización local (reduce feromona en arcos usados) con actualización global (solo la mejor hormiga deposita), generando mayor exploración.

---

### 7. Inicialización de la población y sesgo experimental

Todos los métodos usan inicialización uniforme en $[-5, 5]^n$. Una inicialización inteligente podría mejorar el rendimiento pero introduce sesgo comparativo. Para un estudio justo:

> **Principio de comparación justa:** Si se aplica una técnica (inicialización inteligente, operadores especializados) a un método, debe aplicarse igualmente a todos los métodos comparados, o justificarse explícitamente por qué es específica del método.

---

### 8. Significancia estadística de la comparativa

Con $N=30$ corridas, el Teorema Central del Límite garantiza normalidad aproximada de la media. Para comparar dos métodos formalmente:

**Prueba de Wilcoxon rank-sum** (no paramétrica, robusta a no normalidad):

```python
from scipy.stats import mannwhitneyu
import numpy as np

# Costos de 30 corridas (cargados desde resultados_tsp.json)
aco_costs = [...]  # 30 valores
ga_costs  = [...]  # 30 valores

stat, p_value = mannwhitneyu(aco_costs, ga_costs, alternative='less')
print(f"Estadístico U: {stat:.1f}")
print(f"p-value:       {p_value:.4f}")
print(f"Conclusión:    {'ACO < GA significativo (α=0.05)' if p_value < 0.05 else 'Sin diferencia significativa'}")
```

La diferencia de medias (ACO: 56,957 vs GA: 58,744 MXN, Δ=1,787 MXN) combinada con std(GA)=1,710 sugiere que la prueba sería significativa, pero el resultado exacto depende de la distribución empírica de las 30 corridas.

---

## Limitaciones del estudio

1. **Distancias haversine** aproximan la geodésica esférica; no reflejan la red vial real (sinuosidad, pendientes, zonas sin carretera directa).

2. **Modelo de costo estático:** No considera variación de precios de combustible por estado, peajes diferenciados por tramo, tiempos de visita en cada capital ni restricciones de horario laboral.

3. **TSP simétrico:** Se asume $d_{ij} = d_{ji}$. Peajes unidireccionales y condiciones de terreno pueden romper este supuesto (TSP asimétrico, ATSP).

4. **Hiperparámetros de la literatura:** Los valores se tomaron de publicaciones originales sin sintonización bayesiana para este problema específico; los resultados pueden mejorar con optimización automática de hiperparámetros.

5. **Dimensionalidad limitada:** Se evaluaron solo 2D y 3D. El comportamiento en dimensiones altas ($n > 10$) requiere estudio separado; la "maldición de la dimensionalidad" afecta diferencialmente a cada método.

6. **Sin comparación estadística formal:** La comparativa es descriptiva (media, std, CV). No se aplicaron pruebas de hipótesis formales (Wilcoxon, Kruskal-Wallis) ni correcciones por comparaciones múltiples (Bonferroni).

---

## Trabajo futuro

| Extensión | Método afectado | Impacto esperado |
|-----------|----------------|-----------------|
| Distancias reales (API Google Maps / grafo INEGI) | ACO, GA | Rutas más realistas; posible cambio en ruta óptima |
| Variantes avanzadas: ACS, MMAS | ACO | Reducción de convergencia prematura |
| Operadores Lin-Kernighan | GA | Mejora de 5–15% en calidad de solución para TSP |
| Dimensiones $n \in \{5, 10, 20, 50\}$ | DE, PSO, EA | Caracterizar escalabilidad real |
| Optimización Bayesiana de hiperparámetros | Todos | Resultados más justos y posiblemente mejores |
| Pruebas estadísticas formales (CEC benchmarks) | Todos | Comparación estandarizada con literatura |
| TSP con ventanas de tiempo (TSPTW) | ACO, GA | Mayor realismo en planificación de rutas |
| Funciones de alta dimensión ($n=100$) | DE | Verificar escala adaptativa en espacios grandes |

---

## Referencias adicionales para profundización

- Wolpert, D. H., & Macready, W. G. (1997). No free lunch theorems for optimization. *IEEE TEC*, 1(1), 67–82.
- Dorigo, M., & Stützle, T. (2004). *Ant Colony Optimization*. MIT Press.
- Stützle, T., & Hoos, H. H. (2000). MAX-MIN Ant System. *Future Generation Computer Systems*, 16(9), 889–914.
- Lin, S., & Kernighan, B. W. (1973). An effective heuristic algorithm for the traveling salesman problem. *Operations Research*, 21(2), 498–516.
- Bergstra, J., & Bengio, Y. (2012). Random search for hyper-parameter optimization. *JMLR*, 13, 281–305.
