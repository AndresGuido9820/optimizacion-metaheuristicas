# Teoría — Algoritmos Evolutivos, PSO y Evolución Diferencial

## 1. Algoritmos Evolutivos (EA)

Inspirados en la selección natural darwiniana (Holland, 1975), los EA operan sobre una **población** de soluciones candidatas y aplican iterativamente tres operadores: selección, cruce y mutación.

### 1.1 Selección por torneo

Se eligen $k$ individuos al azar de la población y se preserva el mejor. Con $k=3$, se tiene un buen balance entre presión selectiva (favorece a los mejores) y diversidad (no elimina completamente a los peores).

### 1.2 Cruce BLX-α (cxBlend)

Propuesto por Eshelman y Schaffer (1993). Dados dos padres $\mathbf{x}$ e $\mathbf{y}$, genera un hijo $\mathbf{c}$ con:

$$c_i = x_i + U(-\alpha, 1+\alpha)(y_i - x_i), \quad \alpha = 0.5$$

El rango $[-\alpha, 1+\alpha]$ permite **extrapolación**: el hijo puede quedar fuera del segmento entre los dos padres, favoreciendo la exploración. Con $\alpha=0.5$, el hijo puede estar hasta un 50% fuera del intervalo $[x_i, y_i]$.

### 1.3 Mutación gaussiana

Se agrega ruido $\mathcal{N}(0, \sigma^2)$ con $\sigma=0.5$ y probabilidad $p_\text{indpb}=0.2$ por componente. Genera perturbaciones locales alrededor del individuo actual.

### 1.4 Por qué EA falla en Rosenbrock pero no en Rastrigin

- **Rastrigin:** La multimodalidad premia la exploración amplia. cxBlend con $\alpha=0.5$ y mutación gaussiana son exactamente lo que se necesita para saltar entre mínimos locales.
- **Rosenbrock:** El valle estrecho requiere refinamiento fino y movimientos a lo largo del fondo del valle. cxBlend puede generar hijos fuera del valle (la combinación de dos padres dentro del valle pero en posiciones distintas puede producir un hijo fuera del valle estrecho). La mutación con $\sigma=0.5$ es demasiado grande para el refinamiento necesario.

---

## 2. Optimización por Enjambre de Partículas (PSO)

Propuesto por Kennedy y Eberhart (1995), el PSO modela una bandada de pájaros buscando alimento. Cada partícula $i$ mantiene una posición $\mathbf{x}_i$, una velocidad $\mathbf{v}_i$, su mejor posición personal $\mathbf{p}_i$ y la mejor posición global del enjambre $\mathbf{g}$.

### 2.1 Ecuación de actualización

$$\mathbf{v}_i \leftarrow w\mathbf{v}_i + c_1 r_1 (\mathbf{p}_i - \mathbf{x}_i) + c_2 r_2 (\mathbf{g} - \mathbf{x}_i)$$

$$\mathbf{x}_i \leftarrow \mathbf{x}_i + \mathbf{v}_i$$

Donde $r_1, r_2 \sim U(0,1)$ son aleatorios en cada paso. Los tres términos de la velocidad son:

| Término | Nombre | Efecto |
|---------|--------|--------|
| $w\mathbf{v}_i$ | Inercia | Mantiene la dirección actual |
| $c_1 r_1 (\mathbf{p}_i - \mathbf{x}_i)$ | Componente cognitivo | Atrae hacia la mejor posición personal |
| $c_2 r_2 (\mathbf{g} - \mathbf{x}_i)$ | Componente social | Atrae hacia la mejor posición global |

### 2.2 Factor de constricción de Clerc-Kennedy

El peso inercial $w = 0.729$ con $c_1 = c_2 = 2.05$ es el **factor de constricción** propuesto por Clerc y Kennedy (2002):

$$w = \frac{2}{\left|2 - \phi - \sqrt{\phi^2 - 4\phi}\right|}, \quad \phi = c_1 + c_2 = 4.1$$

Este valor garantiza **convergencia teórica** del enjambre, evitando que las partículas diverjan o se muevan caóticamente. Sin él, con $c_1 + c_2 > 4$, el enjambre puede volverse inestable.

---

## 3. Evolución Diferencial (DE)

Propuesta por Storn y Price (1997), la DE es una metaheurística para espacios continuos especialmente eficiente en funciones de valle estrecho.

### 3.1 Estrategia best1bin

Para cada individuo objetivo $\mathbf{x}_i$, se generan tres individuos aleatorios distintos $r_1, r_2, r_3$ y se construye un **vector mutante**:

$$\mathbf{v}_i = \mathbf{x}_{r_1} + F(\mathbf{x}_{r_2} - \mathbf{x}_{r_3})$$

Luego se aplica **cruce binomial** con probabilidad $CR = 0.7$ para generar el **trial vector** $\mathbf{u}_i$ (cada componente se toma de $\mathbf{v}_i$ con probabilidad $CR$, o de $\mathbf{x}_i$ en caso contrario). Finalmente se aplica **selección greedy**:

$$\mathbf{x}_i \leftarrow \begin{cases} \mathbf{u}_i & \text{si } f(\mathbf{u}_i) \leq f(\mathbf{x}_i) \\ \mathbf{x}_i & \text{en caso contrario} \end{cases}$$

### 3.2 Escala adaptativa: por qué DE domina en Rosenbrock

El vector de mutación $F(\mathbf{x}_{r_2} - \mathbf{x}_{r_3})$ tiene una propiedad clave: cuando la población converge cerca del óptimo, la diferencia $\mathbf{x}_{r_2} - \mathbf{x}_{r_3}$ se vuelve pequeña automáticamente, produciendo perturbaciones finas sin ajuste manual del tamaño de paso. Esto es exactamente lo que el valle estrecho de Rosenbrock requiere:

- **Al inicio:** puntos dispersos → diferencias grandes → exploración amplia
- **Al final:** puntos concentrados → diferencias pequeñas → refinamiento fino

PSO y EA usan perturbaciones de magnitud fija ($\sigma=0.5$ para EA), lo que los hace ineficientes para el refinamiento.

### 3.3 Parámetros utilizados

- $F \in [0.5, 1.0]$ adaptativo (scipy `differential_evolution`)
- $CR = 0.7$, `popsize=15`, `maxiter=1000`, `tol=1e-7`
- Estrategia `best1bin`

---

## 4. Comparativa conceptual

| Característica | EA | PSO | DE |
|---|---|---|---|
| Tipo de perturbación | Cruce + mutación fija | Velocidad + inercia | Diferencia entre individuos |
| Comunicación | Implícita (cruce) | Global (mejor g) | Implícita (diferencias) |
| Escala adaptativa | No | Parcial | Sí (automática) |
| Mejor en Rosenbrock | No | 2D sí, 3D no | Sí (2D y 3D) |
| Mejor en Rastrigin | Sí | Sí | Sí |

---

## 5. Referencias

- Holland, J. H. (1975). *Adaptation in natural and artificial systems*. University of Michigan Press.
- Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. *ICNN*, 4, 1942–1948.
- Clerc, M., & Kennedy, J. (2002). The particle swarm — Explosion, stability, and convergence. *IEEE TEC*, *6*(1), 58–73.
- Storn, R., & Price, K. (1997). Differential evolution. *Journal of Global Optimization*, *11*(4), 341–359.
- Eshelman, L. J., & Schaffer, J. D. (1993). Real-coded genetic algorithms and interval-schemata. *FOGA*, *2*, 187–202.
- Fortin, F.-A. et al. (2012). DEAP: Evolutionary algorithms made easy. *JMLR*, *13*, 2171–2175.
