# Teoría — TSP, Colonias de Hormigas y Algoritmos Genéticos

## 1. Problema del Agente Viajero (TSP)

El TSP es uno de los problemas de optimización combinatoria más estudiados. Dado un conjunto de $n$ ciudades con costos $d_{ij}$ entre pares, se busca la permutación $\pi^*$ que minimiza el costo del recorrido cerrado:

$$\min_{\pi} \; C(\pi) = \sum_{i=0}^{n-1} d\!\left(\pi_i,\, \pi_{(i+1) \bmod n}\right)$$

### 1.1 Complejidad

El espacio de búsqueda tiene $(n-1)!/2$ tours posibles (se fija la ciudad de inicio y se considera simetría). Para $n = 96$ departamentos de Francia:

$$(95)!/2 \approx 4.7 \times 10^{148} \text{ tours posibles}$$

La enumeración exacta es completamente inviable. El TSP es NP-difícil: no se conoce algoritmo polinomial garantizado. El problema de Francia (n=96) es considerablemente más difícil que el de México (n=32): el espacio de búsqueda crece en $\sim 10^{115}$ órdenes de magnitud.

### 1.2 Modelo de costo para Francia

El costo incorpora tres componentes económicos reales del recorrido:

$$C(\pi) = \sum_{i=0}^{95} d(\pi_i, \pi_{(i+1) \bmod 96}) \cdot \left( c_\text{km} + \frac{c_\text{hora}}{v} \right)$$

**Vehículo de referencia:** Renault Clio 1.0 TCe (consumo estándar en carretera: 5.5 L/100 km).

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Combustible | $\approx 0.096$ EUR/km | SP95 a 1.75 EUR/L (precio medio Francia 2024) |
| Peajes | $0.08$ EUR/km | Promedio red de autopistas concesionadas (ASFA, 2024) |
| $c_\text{km}$ total | $\approx 0.176$ EUR/km | Suma combustible + peajes |
| $v$ | $90$ km/h | Velocidad media en carretera francesa (mezcla autopistas y RN) |
| $c_\text{hora}$ | $25$ EUR/h | Valor hora del vendedor (referencia SMIC neto 2024) |
| Factor total | $\approx 0.454$ EUR/km | $c_\text{km} + c_\text{hora}/v$ |

### 1.3 Los 96 departamentos de la Francia metropolitana

Francia metropolitana comprende **96 departamentos**: los numerados 01–95 más 2A (Corse-du-Sud) y 2B (Haute-Corse), que forman la isla de Córcega. Cada departamento tiene una **prefectura** (capital administrativa) que actúa como nodo del TSP.

La extensión geográfica es de aproximadamente 1 200 km norte-sur (Dunkerque a Ajaccio) y 900 km este-oeste (Brest a Estrasburgo), generando distancias haversine de hasta $\sim$1 600 km entre pares de prefecturas.

### 1.4 Distancia haversine

Las distancias entre prefecturas se calculan sobre la esfera terrestre usando la fórmula de Haversine:

$$d = 2R \arctan2\!\left(\sqrt{a},\, \sqrt{1-a}\right)$$

$$a = \sin^2\!\frac{\Delta\phi}{2} + \cos\phi_1 \cos\phi_2 \sin^2\!\frac{\Delta\lambda}{2}$$

con $R = 6{,}371$ km, $\phi$ = latitud y $\lambda$ = longitud en radianes. El error respecto a la elipsoide WGS84 es menor al 0.5% para distancias < 2 000 km.

**Factor de sinuosidad para Francia:**

| Tipo de vía | Factor empírico |
|-------------|:---------------:|
| Autopistas (A) | ~1.10–1.15 |
| Rutas nacionales (RN) | ~1.20–1.30 |
| Rutas departamentales (D) | ~1.30–1.50 |
| Promedio nacional | ~1.18 |

El factor de corrección escala linealmente el costo total pero **no cambia la ruta óptima** si es uniforme.

---

## 2. Colonias de Hormigas (ACO)

### 2.1 Fundamentos teóricos

El ACO fue introducido por Dorigo (1992) como modelo computacional del comportamiento de forrajeo de hormigas reales. Cada hormiga construye una solución completa guiada por la **regla de transición probabilística**:

$$p_{ij}^k = \frac{[\tau_{ij}]^\alpha [\eta_{ij}]^\beta}{\displaystyle\sum_{l \notin \text{visitadas}} [\tau_{il}]^\alpha [\eta_{il}]^\beta}$$

donde $\tau_{ij}$ es la **feromona** (memoria colectiva del enjambre sobre la calidad de los arcos) y $\eta_{ij} = 1/d_{ij}$ es la **heurística de visibilidad**. Al término de cada iteración, la feromona se actualiza en dos pasos:

**Evaporación:** $\tau_{ij} \leftarrow (1 - \rho)\,\tau_{ij}$, con $\rho = 0.1$

**Depósito:** $\tau_{ij} \leftarrow \tau_{ij} + \sum_k Q/C^k$ para los arcos $(i,j)$ usados por la hormiga $k$ con costo $C^k$

### 2.2 Parámetros utilizados

| Parámetro | Valor | Efecto |
|-----------|-------|--------|
| $N_\text{ants}$ | 50 | Número de hormigas por iteración |
| $N_\text{iters}$ | 300 | Iteraciones totales |
| $\alpha$ | 1.0 | Peso de la feromona |
| $\beta$ | 3.0 | Peso de la heurística (favorece arcos cortos) |
| $\rho$ | 0.1 | Tasa de evaporación (memoria larga) |
| $Q$ | 100 | Constante de depósito |

> **Nota sobre escala (n=96):** Con 96 ciudades, la matriz de feromona tiene $96^2 = 9{,}216$ celdas. La construcción de una ruta completa requiere 95 decisiones probabilísticas. La complejidad por iteración es $O(N_\text{ants} \cdot n^2)$, lo que hace a ACO más lento que GA para el mismo número de iteraciones.

---

## 3. Algoritmo Genético para TSP (GA)

### 3.1 Fundamentos teóricos

Los GA aplicados al TSP requieren operadores especiales que respeten la estructura de permutación.

**OX Crossover (Order Crossover)** — propuesto por Davis (1985): copia un segmento aleatorio del padre 1 al hijo, luego rellena con las ciudades del padre 2 en su orden de aparición, omitiendo las ya copiadas. Preserva el orden relativo entre ciudades.

Ejemplo con $n=6$ ciudades:
```
Padre 1:  [1, 2, 3 | 4, 5, 6]     <- segmento [4,5,6] copiado
Padre 2:  [4, 5, 2 | 1, 3, 6]
Relleno (P2 sin {4,5,6}): 2, 1, 3
Hijo A:   [2, 1, 3, 4, 5, 6]      <- permutación válida
```

**Mutación por intercambio de índices (shuffle):** Intercambia posiciones aleatorias en la ruta, garantizando que el resultado siga siendo una permutación válida.

### 3.2 Parámetros utilizados

| Parámetro | Valor |
|-----------|-------|
| $N_\text{pop}$ | 200 individuos |
| $N_\text{gen}$ | 500 generaciones |
| $p_\text{cx}$ | 0.8 — probabilidad de cruce |
| $p_\text{mut}$ | 0.2 — probabilidad de mutación |
| Selección | Torneo de tamaño $k=5$ |

---

## 4. Comparativa conceptual: ACO vs GA

| Característica | ACO | GA |
|---|---|---|
| Memoria | Explícita: matriz de feromona $\tau \in \mathbb{R}^{96\times96}$ | Implícita: genes en la población |
| Costo de memoria | $O(n^2)$ — crece cuadráticamente | $O(N_\text{pop} \cdot n)$ — lineal en $n$ |
| Construcción de solución | Incremental (ciudad a ciudad) | Recombinación de soluciones completas |
| Convergencia | Suave, monotónica | Errática, con saltos abruptos |
| Riesgo de estancamiento | Alto si $\rho$ es pequeño | Bajo por diversidad genética |
| Velocidad (por iteración) | Lenta con $n=96$ ($O(n^2)$ por ruta) | Más rápida (OX crossover es $O(n)$) |

Para $n=96$, la mayor complejidad de ACO por iteración sugiere que GA puede explorar más soluciones en el mismo tiempo de cómputo, lo que podría darle ventaja en encontrar buenas soluciones absolutas.

---

## 5. Referencias

Davis, L. (1985). Applying adaptive algorithms to epistatic domains. En *Proceedings of the 9th International Joint Conference on Artificial Intelligence* (pp. 162–164). IJCAI.

Dorigo, M. (1992). *Optimization, learning and natural algorithms* [Tesis doctoral]. Politecnico di Milano.

Dorigo, M., & Gambardella, L. M. (1997). Ant colony system: A cooperative learning approach to the traveling salesman problem. *IEEE TEC*, *1*(1), 53–66.

Dorigo, M., & Stützle, T. (2004). *Ant Colony Optimization*. MIT Press.
