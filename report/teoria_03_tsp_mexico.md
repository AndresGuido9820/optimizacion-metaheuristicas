# Teoría — TSP, Colonias de Hormigas y Algoritmos Genéticos

## 1. Problema del Agente Viajero (TSP)

El TSP es uno de los problemas de optimización combinatoria más estudiados. Dado un conjunto de $n$ ciudades con costos $d_{ij}$ entre pares, se busca la permutación $\pi^*$ que minimiza el costo del recorrido cerrado:

$$\min_{\pi} \; C(\pi) = \sum_{i=0}^{n-1} d\!\left(\pi_i,\, \pi_{(i+1) \bmod n}\right)$$

### 1.1 Complejidad

El espacio de búsqueda tiene $(n-1)!/2$ tours posibles (se fija la ciudad de inicio y se considera simetría). Para $n=32$:

$$(31)!/2 \approx 1.3 \times 10^{33} \text{ tours}$$

La enumeración exacta es completamente inviable. El TSP es NP-difícil: no se conoce algoritmo polinomial garantizado. Los algoritmos exactos más eficientes (Concorde) pueden resolver instancias hasta $\sim 10^6$ ciudades con datos reales, pero requieren librerías especializadas.

### 1.2 Modelo de costo para México

El costo no es solo distancia: es un modelo económico que combina combustible, peajes y tiempo del vendedor:

$$C(\pi) = \sum_{i=0}^{31} d(\pi_i, \pi_{(i+1) \bmod 32}) \cdot \left( c_\text{km} + \frac{c_\text{hora}}{v} \right)$$

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| $c_\text{km}$ | 4.5 MXN/km | Combustible (~3.0) + peajes promedio (~1.5) |
| $v$ | 80 km/h | Velocidad promedio en carretera mexicana |
| $c_\text{hora}$ | 150 MXN/h | Costo hora del vendedor |
| Factor total | 6.375 MXN/km | $4.5 + 150/80$ |

### 1.3 Distancia haversine

Las distancias se calculan sobre coordenadas geográficas reales de cada capital:

$$d = 2R \arctan2\!\left(\sqrt{a},\, \sqrt{1-a}\right)$$

$$a = \sin^2\!\frac{\Delta\phi}{2} + \cos\phi_1 \cos\phi_2 \sin^2\!\frac{\Delta\lambda}{2}$$

Con $R = 6{,}371$ km. El error respecto a distancia euclidiana sobre lat/lon puede llegar a 15% en trayectos largos (Mexicali–Mérida ≈ 3,200 km), por lo que haversine es necesario.

---

## 2. Colonias de Hormigas (ACO)

Introducido por Dorigo (1992), el ACO modela el comportamiento de forrajeo de hormigas reales. Las hormigas reales depositan feromonas en los caminos que recorren; los caminos más cortos acumulan más feromona porque son recorridos más veces en el mismo tiempo, creando un ciclo de retroalimentación positiva.

### 2.1 Construcción de soluciones

Cada hormiga construye un tour completo de manera probabilística. La probabilidad de que la hormiga $k$ en la ciudad $i$ elija ir a la ciudad $j$ es:

$$p_{ij}^k = \frac{[\tau_{ij}]^\alpha \cdot [\eta_{ij}]^\beta}{\displaystyle\sum_{l \notin \text{visitadas}} [\tau_{il}]^\alpha \cdot [\eta_{il}]^\beta}$$

Donde:
- $\tau_{ij}$ — **feromona**: memoria colectiva sobre la calidad del arco $(i,j)$
- $\eta_{ij} = 1/d_{ij}$ — **visibilidad heurística**: preferencia por ciudades cercanas
- $\alpha = 1$ — peso de la feromona
- $\beta = 3$ — peso de la heurística (favorece ciudades cercanas)

Un $\beta$ alto hace que las hormigas sean más "codiciosas" (greedy), mientras que un $\alpha$ alto favorece la experiencia colectiva acumulada.

### 2.2 Actualización de feromona

Al final de cada iteración, la feromona se actualiza en dos pasos:

**Evaporación global** (simula disipación natural):

$$\tau_{ij} \leftarrow (1 - \rho)\,\tau_{ij}, \quad \rho = 0.1$$

**Depósito proporcional** (cada hormiga deposita según la calidad de su tour):

$$\tau_{ij} \leftarrow \tau_{ij} + \sum_{k=1}^{N_\text{ants}} \frac{Q}{C^k} \cdot \mathbb{1}[(i,j) \in \text{tour}^k]$$

Con $Q=100$ y $N_\text{ants}=50$. Las hormigas con tours más cortos (menor $C^k$) depositan más feromona ($Q/C^k$ mayor), reforzando los arcos de calidad.

### 2.3 Balance exploración/explotación

La tasa de evaporación $\rho$ controla el balance:
- **$\rho$ alto:** la feromona decae rápido → mayor exploración pero riesgo de olvidar buenas rutas
- **$\rho$ bajo:** la feromona persiste → mayor explotación pero riesgo de estancamiento prematuro

Con $\rho=0.1$, la feromona retiene el 90% de su valor entre iteraciones, favoreciendo la explotación gradual de rutas prometedoras.

---

## 3. Algoritmo Genético para TSP (GA)

Los operadores estándar de GA (cruce de un punto, cruce BLX) producen **permutaciones inválidas** en TSP (ciudades repetidas o faltantes). Se requieren operadores que respeten la estructura de permutación.

### 3.1 OX Crossover (Order Crossover)

Propuesto por Davis (1985). Dado dos padres $P_1$ y $P_2$:

1. Se copia un **segmento aleatorio** de $P_1$ al hijo en las mismas posiciones
2. Se recorre $P_2$ desde el final del segmento, omitiendo las ciudades ya presentes
3. Se rellena el resto del hijo con las ciudades de $P_2$ en orden

**Ejemplo** con $n=8$, segmento posiciones [2,5]:
```
P1: [1 2 | 3 4 5 | 6 7 8]
P2: [3 8 | 2 4 7 | 1 6 5]
H:  [8 2 | 3 4 5 | 7 1 6]   ← ciudades de P2 en orden, sin {3,4,5}
```

El OX preserva el **orden relativo** entre ciudades de $P_2$, que tiene significado geográfico: sub-rutas que funcionan bien en un padre tienden a mantenerse en el hijo.

### 3.2 Mutación por intercambio de índices

Se intercambian dos posiciones aleatorias del tour con probabilidad $p_\text{indpb} = 2/n$ por posición (en promedio 2 intercambios por mutación). Garantiza que el resultado siga siendo una permutación válida y introduce diversidad sin romper completamente la estructura del tour.

### 3.3 Parámetros

| Parámetro | Valor |
|-----------|-------|
| $N_\text{pop}$ | 200 |
| $N_\text{gen}$ | 500 |
| $p_\text{cx}$ | 0.8 |
| $p_\text{mut}$ | 0.2 |
| Torneo | $k=5$ |

---

## 4. ACO vs GA: dos modelos de memoria colectiva

| Característica | ACO | GA |
|---|---|---|
| Memoria | Explícita (feromona $\tau_{ij}$) | Implícita (genes en la población) |
| Comunicación | Todas las hormigas leen/escriben la misma matriz | Información se propaga por cruce |
| Convergencia | Suave y monotónica | Errática, con saltos abruptos |
| Consistencia (CV) | 0.72% | 2.91% |
| Mejor solución absoluta | 56,195 MXN | **55,796 MXN** |
| Tiempo (30 corridas) | ~274.6 s | ~111.5 s |

La feromona de ACO acumula evidencia gradualmente sobre qué arcos son buenos → convergencia suave. El cruce del GA puede producir resultados muy buenos (combina dos buenas sub-rutas) o muy malos (sub-rutas incompatibles geográficamente) → mayor varianza.

---

## 5. Referencias

- Applegate, D. L., Bixby, R. E., Chvátal, V., & Cook, W. J. (2006). *The traveling salesman problem*. Princeton University Press.
- Davis, L. (1985). Applying adaptive algorithms to epistatic domains. *IJCAI*, 162–164.
- Dorigo, M. (1992). *Optimization, learning and natural algorithms* [Tesis doctoral]. Politecnico di Milano.
- Dorigo, M., & Gambardella, L. M. (1997). Ant colony system. *IEEE TEC*, *1*(1), 53–66.
- Goldberg, D. E. (1989). *Genetic algorithms in search, optimization, and machine learning*. Addison-Wesley.
- INEGI. (2023). *Marco geoestadístico: Municipios y localidades*. https://www.inegi.org.mx/temas/mg/
