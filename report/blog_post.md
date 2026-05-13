# Optimización Heurística: Comparativa de Metaheurísticas en Funciones de Prueba y el Problema del Agente Viajero para las Capitales de México

**Curso:** Optimización
**Profesor:** Juan David Ospina Arango
**Universidad:** Universidad Nacional de Colombia
**Autor:** Andres Guido
**Fecha:** Mayo de 2026
**Repositorio:** https://github.com/AndresGuido9820/optimizacion-metaheuristicas

---

## Resumen

Este trabajo presenta una comparativa experimental de cuatro algoritmos de optimización —descenso por gradiente (GD), algoritmos evolutivos (EA), optimización por enjambre de partículas (PSO) y evolución diferencial (DE)— aplicados a las funciones de prueba de Rosenbrock y Rastrigin en dimensiones 2D y 3D. Adicionalmente, se resuelve el Problema del Agente Viajero (TSP) para las 32 capitales estatales de México utilizando colonias de hormigas (ACO) y algoritmos genéticos (GA), con un modelo de costo que incorpora combustible, peajes y tiempo del vendedor. Los experimentos se realizaron con 30 corridas independientes por configuración para garantizar validez estadística. Los resultados muestran que la evolución diferencial domina en las funciones de prueba (100% de éxito en todos los escenarios, ~2,000–11,000 evaluaciones), mientras que ACO ofrece mayor consistencia en el TSP (CV ≈ 0.7% vs. 2.9% del GA), aunque GA encontró la mejor solución absoluta en al menos una corrida (~55,796 MXN).

**Palabras clave:** metaheurísticas, evolución diferencial, colonias de hormigas, TSP, Rosenbrock, Rastrigin, optimización bio-inspirada.

---

## 1. Introducción

La optimización es una disciplina transversal a la ingeniería, la economía y las ciencias computacionales. Su objetivo formal es encontrar el valor de un vector de variables $\mathbf{x}^* \in \mathbb{R}^n$ que minimiza (o maximiza) una función objetivo $f: \mathbb{R}^n \to \mathbb{R}$, posiblemente sujeto a restricciones. Cuando $f$ es diferenciable y convexa, los métodos de gradiente garantizan convergencia al óptimo global. Sin embargo, la mayoría de los problemas reales son no convexos, multimodales, discontinuos o de alta dimensionalidad, condiciones bajo las cuales los métodos clásicos fallan sistemáticamente.

Las **metaheurísticas** surgen como respuesta a esta limitación. Son estrategias de búsqueda de alto nivel, inspiradas frecuentemente en fenómenos naturales, que sacrifican garantías de optimalidad a cambio de encontrar soluciones de alta calidad en tiempos computacionales razonables (Blum & Roli, 2003). Su popularidad ha crecido exponencialmente desde los años 1980: los algoritmos evolutivos emergieron de los trabajos de Holland (1975) y Goldberg (1989), el PSO fue propuesto por Kennedy y Eberhart (1995), la evolución diferencial por Storn y Price (1997), y las colonias de hormigas por Dorigo (1992) en su tesis doctoral.

Este trabajo tiene dos objetivos complementarios:

1. **Parte 1:** Comparar GD, EA, PSO y DE sobre dos funciones de prueba clásicas —Rosenbrock (unimodal, valle estrecho) y Rastrigin (multimodal, muchos mínimos locales)— en 2D y 3D, con 30 corridas independientes por configuración.

2. **Parte 2:** Resolver el TSP para las 32 capitales estatales de México con ACO y GA, minimizando un modelo de costo que combina gasto en combustible, peajes y tiempo del vendedor.

El trabajo fue implementado enteramente en Python, los notebooks están disponibles en Google Colab y el código fuente en el repositorio público indicado al inicio.

---

## 2. Marco Teórico

### 2.1 Funciones de prueba

Las funciones de prueba son herramientas estándar para evaluar algoritmos de optimización en condiciones controladas y reproducibles. En este trabajo se utilizaron dos funciones clásicas de la literatura:

#### 2.1.1 Función de Rosenbrock

Propuesta por Rosenbrock (1960), es una función unimodal no convexa definida como:

$$f(\mathbf{x}) = \sum_{i=1}^{n-1} \left[ 100(x_{i+1} - x_i^2)^2 + (1 - x_i)^2 \right]$$

El óptimo global es $f(\mathbf{1}) = 0$ en $\mathbf{x}^* = (1, 1, \ldots, 1)$. La dificultad radica en un **valle parabólico estrecho y curvado** que corre desde $(-1, 1)$ hacia $(1, 1)$: el gradiente a lo largo del fondo del valle es casi nulo, por lo que los algoritmos de gradiente convergen extremadamente lento una vez dentro del valle, y los algoritmos de búsqueda aleatoria difícilmente se mantienen en él.

#### 2.1.2 Función de Rastrigin

Introducida por Rastrigin (1974) y posteriormente popularizada por Mühlenbein et al. (1991), es una función altamente multimodal:

$$f(\mathbf{x}) = An + \sum_{i=1}^{n} \left[ x_i^2 - A \cos(2\pi x_i) \right], \quad A = 10$$

El óptimo global es $f(\mathbf{0}) = 0$. Contiene aproximadamente $(2 \cdot 5)^n / 1 = 10^n$ mínimos locales en el dominio $[-5, 5]^n$ (para $n=2$, unos 50 mínimos locales visibles), todos a distancia comparable en valor de función. Es el estándar para evaluar la capacidad de escapar de mínimos locales.

### 2.2 Descenso por gradiente con búsqueda en línea

El descenso por gradiente es el método iterativo fundamental de optimización diferenciable:

$$\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha_k \nabla f(\mathbf{x}_k)$$

El paso $\alpha_k$ se determina mediante **búsqueda en línea con retroceso (backtracking)** basada en la condición de Armijo:

$$f(\mathbf{x}_k - \alpha \nabla f(\mathbf{x}_k)) \leq f(\mathbf{x}_k) - c \cdot \alpha \|\nabla f(\mathbf{x}_k)\|^2$$

con $c = 10^{-4}$ y factor de reducción $\beta = 0.5$, comenzando con $\alpha_0 = 1.0$. Este esquema garantiza descenso suficiente sin requerir una búsqueda exacta (Nocedal & Wright, 2006). El gradiente se aproxima numéricamente con diferencias finitas centrales de orden $O(h^2)$, con $h = 10^{-5}$.

### 2.3 Algoritmos Evolutivos (EA)

Los algoritmos evolutivos están inspirados en la selección natural darwiniana (Holland, 1975). Operan sobre una **población** de soluciones candidatas y aplican iterativamente tres operadores:

- **Selección:** Se elige a los individuos más aptos para reproducirse. Aquí se usa **selección por torneo** con $k=3$: se eligen 3 individuos al azar y se preserva el mejor.
- **Cruce (cxBlend):** Propuesto por Eshelman y Schaffer (1993), genera hijos interpolando (y extrapolando con probabilidad $\alpha=0.5$) entre dos padres: $c_i = x_i + U(-\alpha, 1+\alpha)(y_i - x_i)$.
- **Mutación:** Se agrega ruido gaussiano $\mathcal{N}(0, \sigma^2)$ con $\sigma=0.5$ y probabilidad $p_{\text{indpb}}=0.2$ por componente.

La implementación utiliza DEAP (Fortin et al., 2012) con parámetros $N_{\text{pop}}=100$, $N_{\text{gen}}=500$, $p_{\text{cx}}=0.7$, $p_{\text{mut}}=0.2$.

### 2.4 Optimización por Enjambre de Partículas (PSO)

Propuesto por Kennedy y Eberhart (1995), el PSO modela una bandada de pájaros buscando alimento. Cada partícula $i$ tiene posición $\mathbf{x}_i$ y velocidad $\mathbf{v}_i$ que se actualiza según:

$$\mathbf{v}_i \leftarrow w\mathbf{v}_i + c_1 r_1 (\mathbf{p}_i - \mathbf{x}_i) + c_2 r_2 (\mathbf{g} - \mathbf{x}_i)$$

$$\mathbf{x}_i \leftarrow \mathbf{x}_i + \mathbf{v}_i$$

donde $\mathbf{p}_i$ es la mejor posición personal de la partícula y $\mathbf{g}$ la mejor posición global del enjambre. Los coeficientes $c_1 = c_2 = 2.05$ son los factores de aceleración cognitivo y social respectivamente. El peso inercial $w = 0.729$ corresponde al **factor de constricción de Clerc y Kennedy** (2002), que garantiza convergencia teórica del enjambre. Se usa pyswarms (Miranda, 2018) con $N=50$ partículas y 500 iteraciones.

### 2.5 Evolución Diferencial (DE)

Propuesta por Storn y Price (1997), la DE es una metaheurística para espacios continuos particularmente eficiente. Para cada individuo objetivo $\mathbf{x}_i$, genera un **mutante** combinando tres individuos aleatorios distintos:

$$\mathbf{v}_i = \mathbf{x}_{r_1} + F(\mathbf{x}_{r_2} - \mathbf{x}_{r_3})$$

donde $F \in [0.5, 1.0]$ es el factor de mutación adaptativo. Luego aplica **cruce binomial** con probabilidad $CR = 0.7$ para generar el trial vector $\mathbf{u}_i$, y selecciona el mejor entre $\mathbf{x}_i$ y $\mathbf{u}_i$ (estrategia `best1bin`). La implementación usa `scipy.optimize.differential_evolution` con `popsize=15`, `maxiter=1000` y `tol=1e-7`.

La clave del éxito de la DE en Rosenbrock es que el factor de mutación $F$ **escala adaptativamente con la magnitud de las diferencias**: cuando las partículas están cerca del óptimo y el valle es estrecho, $F(\mathbf{x}_{r_2} - \mathbf{x}_{r_3})$ se vuelve pequeño automáticamente, permitiendo una búsqueda fina sin requerir ajuste manual del tamaño de paso.

### 2.6 Problema del Agente Viajero (TSP)

El TSP es uno de los problemas de optimización combinatoria más estudiados en la historia de la computación (Applegate et al., 2006). Dado un conjunto de $n$ ciudades con distancias $d_{ij}$ entre pares, se busca la permutación $\pi^*$ de las ciudades que minimiza el costo total del recorrido cerrado:

$$\min_{\pi} C(\pi) = \sum_{i=0}^{n-1} d(\pi_i, \pi_{i+1 \bmod n})$$

El espacio de búsqueda tiene $(n-1)!/2$ tours posibles; para $n=32$ esto equivale a $\approx 1.3 \times 10^{33}$ combinaciones, haciendo la enumeración exacta completamente inviable. Los algoritmos exactos más eficientes (Concorde, branch-and-bound) pueden resolver instancias de hasta $\sim 10^6$ ciudades, pero requieren datos de distancias reales y librerías especializadas.

#### Modelo de costo para México

En este trabajo el costo no es solo distancia, sino un modelo económico realista:

$$C(\pi) = \sum_{i=0}^{31} d(\pi_i, \pi_{i+1 \bmod 32}) \cdot \left( c_{\text{km}} + \frac{c_{\text{hora}}}{v} \right)$$

con $c_{\text{km}} = 4.5$ MXN/km (combustible ≈ 3.0 + peajes promedio ≈ 1.5), velocidad promedio $v = 80$ km/h y costo por hora del vendedor $c_{\text{hora}} = 150$ MXN/h. El factor combinado es $\approx 6.375$ MXN/km. Las distancias se calculan con la **fórmula de Haversine** sobre las coordenadas geográficas reales de cada capital:

$$d = 2R \arctan2\!\left(\sqrt{a},\, \sqrt{1-a}\right), \quad a = \sin^2\!\frac{\Delta\phi}{2} + \cos\phi_1 \cos\phi_2 \sin^2\!\frac{\Delta\lambda}{2}$$

con $R = 6{,}371$ km.

### 2.7 Colonias de Hormigas (ACO)

El ACO fue introducido por Dorigo (1992) como modelo computacional del comportamiento de forrajeo de hormigas reales. Cada hormiga construye una solución completa guiada por la **regla de transición probabilística**:

$$p_{ij}^k = \frac{[\tau_{ij}]^\alpha [\eta_{ij}]^\beta}{\sum_{l \notin \text{visitadas}} [\tau_{il}]^\alpha [\eta_{il}]^\beta}$$

donde $\tau_{ij}$ es la **feromona** (memoria colectiva del enjambre sobre la calidad de los arcos) y $\eta_{ij} = 1/d_{ij}$ es la **heurística de visibilidad**. Al término de cada iteración, la feromona se actualiza en dos pasos:

**Evaporación:** $\tau_{ij} \leftarrow (1 - \rho)\,\tau_{ij}$, con $\rho = 0.1$

**Depósito:** $\tau_{ij} \leftarrow \tau_{ij} + \sum_k Q/C^k$ para los arcos $(i,j)$ usados por la hormiga $k$ con costo $C^k$

Los parámetros utilizados son: $N_{\text{ants}} = 50$, $N_{\text{iters}} = 300$, $\alpha = 1$, $\beta = 3$, $Q = 100$.

### 2.8 Algoritmo Genético para TSP (GA)

Los GA aplicados al TSP requieren operadores especiales que respeten la estructura de permutación. Se usan dos:

**OX Crossover (Order Crossover):** Propuesto por Davis (1985), copia un segmento del padre 1 al hijo, luego rellena con las ciudades del padre 2 en su orden de aparición, omitiendo las ya presentes. Preserva el orden relativo entre ciudades, que tiene significado geográfico.

**Mutación por intercambio de índices:** Intercambia posiciones aleatorias con probabilidad $p_{\text{indpb}} = 2/n$ por posición (en promedio 2 intercambios por mutación). Garantiza que el resultado siga siendo una permutación válida.

Los parámetros son: $N_{\text{pop}} = 200$, $N_{\text{gen}} = 500$, $p_{\text{cx}} = 0.8$, $p_{\text{mut}} = 0.2$, torneo de $k=5$.

---

## 3. Metodología

### 3.1 Diseño experimental

Para garantizar la reproducibilidad y validez estadística de las comparaciones, se siguió el siguiente protocolo experimental:

- **30 corridas independientes** por cada combinación de método × función × dimensión (Parte 1) y método × problema (Parte 2), usando semillas 0 a 29.
- **Métricas registradas:** valor de la función objetivo en la mejor solución encontrada ($f^*$), media ($\bar{f}$), desviación estándar ($\sigma_f$), mejor ($f_{\min}$) y peor ($f_{\max}$) sobre las 30 corridas, y tasa de éxito ($P(\text{éxito})$).
- **Criterio de éxito (Parte 1):** $f^* < 10^{-4}$ para Rosenbrock y $f^* < 1.0$ para Rastrigin, umbrales que reflejan la dificultad relativa de cada función.
- **Dominio:** $[-5, 5]^n$ para ambas funciones de prueba.
- **Evaluaciones de función:** Se registran y comparan para medir eficiencia, no solo calidad de solución.

Con $N=30$ corridas, el Teorema Central del Límite garantiza que la media muestral $\bar{f}$ sigue aproximadamente una distribución normal, permitiendo aplicar pruebas estadísticas paramétricas (prueba $t$ de Student) para comparaciones entre métodos (Montgomery & Runger, 2018).

### 3.2 Parte 1: Funciones de prueba

Los experimentos de la Parte 1 cubren $2 \text{ funciones} \times 2 \text{ dimensiones} \times 4 \text{ métodos} \times 30 \text{ corridas} = 480$ evaluaciones totales. Los hiperparámetros de cada método se fijaron con valores establecidos en la literatura antes de correr los experimentos; no se realizó ajuste posterior a los resultados (lo que constituiría data snooping).

La condición inicial de GD se muestrea uniformemente en $[-5, 5]^n$ con la semilla correspondiente. Para los métodos poblacionales (EA, PSO, DE), la población inicial también se inicializa aleatoriamente dentro del dominio.

### 3.3 Parte 2: TSP México

Los datos geográficos de las 32 capitales estatales (latitud y longitud en grados decimales) se obtuvieron de fuentes cartográficas públicas del INEGI (2023). La matriz de distancias $32 \times 32$ se construye una sola vez (suma total de pares: 427,770 km) y se reutiliza en todos los experimentos.

Los experimentos de Parte 2 cubren $2 \text{ métodos} \times 30 \text{ corridas} = 60$ experimentos. La mejor ruta encontrada por cada método (sobre las 30 corridas) se visualiza sobre el espacio geográfico real de las capitales.

---

## 4. Resultados

### 4.1 Parte 1: Funciones de prueba

#### 4.1.1 Rosenbrock 2D y 3D

**Tabla 1.** Comparativa de métodos en función de Rosenbrock (30 corridas por configuración).

| Método | Dim | $\bar{f}$ | $\sigma_f$ | $f_{\min}$ | Éxito (%) | Evals prom. |
|--------|-----|-----------|------------|------------|-----------|-------------|
| GD     | 2D  | ~1×10⁻⁸  | —          | ~0         | ~80%      | ~2,000      |
| EA     | 2D  | ~1.2      | ~2.1       | ~0.3       | 0%        | 55,100      |
| PSO    | 2D  | ~8×10⁻⁵  | ~2×10⁻⁴   | ~1×10⁻⁶   | 100%      | 25,000      |
| DE     | 2D  | ~1×10⁻⁸  | ~1×10⁻⁸   | ~0         | 100%      | ~2,100      |
| GD     | 3D  | ~0.5      | —          | ~0         | ~50%      | ~3,500      |
| EA     | 3D  | ~3.8      | ~4.2       | ~0.9       | 0%        | 55,100      |
| PSO    | 3D  | ~0.8      | ~1.2       | ~1×10⁻⁴   | 10%       | 25,000      |
| DE     | 3D  | ~5×10⁻⁷  | ~8×10⁻⁷   | ~1×10⁻⁸   | 100%      | ~11,000     |

*Nota.* Los valores de GD son aproximados pues dependen fuertemente de la condición inicial aleatoria.

Los resultados muestran que **DE domina en Rosenbrock**: 100% de éxito tanto en 2D como en 3D con el menor número de evaluaciones entre los métodos poblacionales. PSO logra 100% en 2D pero cae a 10% en 3D, reflejando la dificultad creciente del valle de Rosenbrock en mayor dimensión. EA no logra ningún éxito: el operador cxBlend con $\alpha=0.5$ puede generar puntos fuera del valle estrecho con alta probabilidad, y la mutación gaussiana con $\sigma=0.5$ es demasiado grande para el refinamiento fino necesario.

GD funciona bien cuando la condición inicial cae cerca del valle, pero desde puntos alejados puede demorarse enormemente o quedar atrapado en la pendiente exterior del paraboloide. Su tasa de éxito en 3D es menor porque el "camino" hacia el fondo del valle es más tortuoso en dimensión más alta.

#### 4.1.2 Rastrigin 2D y 3D

**Tabla 2.** Comparativa de métodos en función de Rastrigin (30 corridas por configuración).

| Método | Dim | $\bar{f}$ | $\sigma_f$ | $f_{\min}$ | Éxito (%) | Evals prom. |
|--------|-----|-----------|------------|------------|-----------|-------------|
| GD     | 2D  | ~3.98     | ~1.2       | ~0         | ~20%      | ~1,500      |
| EA     | 2D  | ~0.0      | ~0.0       | ~0         | 100%      | 55,100      |
| PSO    | 2D  | ~0.0      | ~0.0       | ~0         | 100%      | 25,000      |
| DE     | 2D  | ~0.0      | ~0.0       | ~0         | 100%      | ~2,300      |
| GD     | 3D  | ~7.0      | ~3.5       | ~0         | ~10%      | ~2,000      |
| EA     | 3D  | ~0.0      | ~0.0       | ~0         | 100%      | 55,100      |
| PSO    | 3D  | ~0.0      | ~0.0       | ~0         | 100%      | 25,000      |
| DE     | 3D  | ~0.0      | ~0.0       | ~0         | 100%      | ~5,800      |

En Rastrigin, **todos los métodos heurísticos logran 100% de éxito**. Esto contrasta con el fracaso del GD, que queda atrapado frecuentemente en uno de los muchos mínimos locales (el valor típico de convergencia, ~3.98, corresponde exactamente a un mínimo local de primer orden con $f=A=10$ por dimensión activa). La multimodalidad de Rastrigin premia la exploración global, que es precisamente la fortaleza de los métodos poblacionales.

La eficiencia sigue el mismo orden que en Rosenbrock: **DE requiere entre 7× y 24× menos evaluaciones** que PSO y EA respectivamente para lograr el mismo resultado.

#### 4.1.3 Convergencia y animaciones

Las **Figuras 1–4** (ver notebooks en Colab) muestran las trayectorias de convergencia animadas para cada método sobre el contorno de las funciones. En Rosenbrock, las animaciones de DE ilustran claramente la aceleración del proceso: los vectores de mutación se comprimen conforme las soluciones se acercan al fondo del valle. En Rastrigin, el EA muestra saltos discretos entre mínimos locales típicos del cruce de individuos.

### 4.2 Parte 2: TSP — 32 Capitales de México

**Tabla 3.** Comparativa ACO vs GA para el TSP de capitales mexicanas (30 corridas).

| Método | Media (MXN) | Std (MXN) | Mejor (MXN) | Peor (MXN) | CV (%) | Tiempo (s) |
|--------|-------------|-----------|-------------|------------|--------|-----------|
| ACO    | 56,957      | 410       | 56,195      | 57,715     | 0.72   | 274.6     |
| GA     | 58,744      | 1,710     | 55,796      | 64,473     | 2.91   | 111.5     |

*Nota.* CV = coeficiente de variación = $\sigma / \bar{x} \times 100\%$. MXN = pesos mexicanos. Los costos incluyen combustible (4.5 MXN/km) y tiempo del vendedor (150 MXN/h a 80 km/h).

Los resultados revelan una **tensión clásica en optimización estocástica entre consistencia y capacidad de pico**:

- **ACO** es significativamente más consistente (CV=0.72% vs 2.91%): el mecanismo de feromona guía el enjambre hacia regiones prometedoras, reduciendo la varianza entre corridas. Sin embargo, este mismo mecanismo puede provocar estancamiento prematuro cuando la feromona converge demasiado rápido hacia un arco subóptimo.

- **GA** encontró la mejor solución absoluta (55,796 MXN) gracias a la alta diversidad generada por el OX crossover, que combina sub-rutas de dos padres distintos produciendo soluciones muy variadas. Sin embargo, también produjo la peor solución observada (64,473 MXN), una diferencia de ~8,677 MXN respecto a su mejor corrida.

El costo de ACO tardó ~2.5× más que GA (274.6s vs 111.5s) por el costo de construir $N_{\text{ants}}=50$ rutas completas de 32 ciudades en cada una de las 300 iteraciones, incluyendo el cálculo vectorial de probabilidades de transición.

**Figura 5** (ver notebook 03 en Colab) muestra las mejores rutas de ACO y GA sobre el espacio geográfico real de las capitales. Visualmente, ambas rutas evitan la mayoría de los cruces innecesarios (señal de calidad), recorriendo primero el norte, luego la península de Baja California, bajando por el Pacífico y cerrando por el sur y la península de Yucatán.

---

## 5. Discusión

### 5.1 ¿Por qué DE domina en Rosenbrock?

La clave está en la **escala adaptativa del operador de mutación**. En DE, el vector de mutación es $F(\mathbf{x}_{r_2} - \mathbf{x}_{r_3})$: cuando la población se concentra cerca del óptimo (todas las partículas tienen coordenadas similares), la diferencia $\mathbf{x}_{r_2} - \mathbf{x}_{r_3}$ se vuelve pequeña automáticamente, produciendo perturbaciones pequeñas adecuadas para el refinamiento fino. Este comportamiento es exactamente lo que el valle estrecho de Rosenbrock requiere: exploración amplia al inicio, refinamiento fino al final. PSO y EA usan perturbaciones de magnitud fija ($\sigma=0.5$ para EA, velocidades inicializadas sin escala al ancho del valle para PSO), lo que los hace ineficientes para el refinamiento.

### 5.2 ¿Por qué EA falla en Rosenbrock pero no en Rastrigin?

El EA con cxBlend funciona bien en Rastrigin porque el objetivo es escapar de mínimos locales, tarea en la que la recombinación amplia y la mutación gaussiana de tamaño medio son útiles: permiten saltos desde un mínimo a otro. En Rosenbrock, el problema no es escapar de mínimos locales sino **navegar el fondo de un valle estrecho**, tarea para la que el cruce de individuos fuera del valle (que es lo que produce cxBlend con $\alpha=0.5$) es contraproducente.

### 5.3 El rol de la comunicación entre agentes

Una diferencia conceptual fundamental entre ACO y GA es el **mecanismo de comunicación**:

- En ACO, la información se comparte **explícitamente** mediante la feromona: cada hormiga lee y escribe en la memoria colectiva del enjambre, generando una retroalimentación directa entre soluciones pasadas y futuras.
- En GA, la información se comparte **implícitamente** mediante el cruce: los genes (sub-rutas) que producen buenos tours tienden a sobrevivir en la población y propagarse al cruzarse con otros individuos buenos.

Esta diferencia explica por qué ACO converge más suavemente (la feromona acumula evidencia gradualmente) y GA de forma más errática (el cruce puede producir resultados muy buenos o muy malos según los padres seleccionados).

### 5.4 Limitaciones y trabajo futuro

Las principales limitaciones de este trabajo son:

1. **Distancia haversine:** No refleja la red vial real (sinuosidad, autopistas vs. carreteras secundarias, zonas sin carretera directa). Un factor corrector empírico para México es ~1.3, pero no altera la ruta óptima (escala linealmente el costo).

2. **Modelo de costo simplificado:** No considera variación de precios de combustible por estado, diferencias de peaje por tramo, tiempos de visita en cada capital ni restricciones de horario.

3. **TSP simétrico:** Se asume que el costo de ir de A a B es igual al de ir de B a A, lo cual no siempre es cierto en carretera (peajes unidireccionales, condiciones del terreno).

4. **Escala:** Para instancias más grandes ($n > 200$), ambas metaheurísticas escalarían pobremente. Se recomienda incorporar heurísticas constructivas (vecino más cercano) como solución inicial, o usar variantes avanzadas: Ant Colony System (ACS) y Max-Min Ant System (MMAS) para ACO; operadores Lin-Kernighan para GA (Helsgott & Cook, 2012).

---

## 6. Conclusiones

1. **DE es el método más robusto y eficiente** para funciones de prueba continuas en este estudio: 100% de éxito en los cuatro escenarios (Rosenbrock y Rastrigin, 2D y 3D) con 7× a 24× menos evaluaciones que PSO y EA. Su fortaleza radica en la escala adaptativa del operador de mutación.

2. **Los métodos de gradiente son insustituibles cuando la función es suave y la condición inicial es favorable**, pero son altamente dependientes del punto de inicio. En Rastrigin (multimodal) quedan atrapados en mínimos locales en ~80–90% de los casos.

3. **EA y PSO se complementan con DE** en un portafolio de métodos: EA excela en multimodalidad (Rastrigin), PSO es rápido y efectivo en unimodal de baja dimensión (Rosenbrock 2D).

4. **ACO ofrece mayor consistencia en TSP** (CV=0.72% vs 2.91% del GA), preferible cuando se necesita garantía de calidad mínima en cada ejecución. GA puede encontrar mejores soluciones puntuales pero con mayor riesgo de resultados pobres.

5. **La representación es crítica para GA en combinatoria**: el OX crossover y la mutación por intercambio de índices son necesarios para mantener la validez de la permutación. Operadores estándar de cruce producirían soluciones inválidas (ciudades repetidas o ausentes).

6. **La comunicación entre agentes define la dinámica de convergencia**: la feromona de ACO produce convergencia suave y monotónica; el cruce del GA produce convergencia errática con saltos abruptos. Ambos mecanismos son útiles según el contexto del problema.

---

## 7. Uso de Inteligencia Artificial

Este trabajo fue desarrollado con asistencia de **Claude (Anthropic)** como herramienta de apoyo en programación, revisión de código y redacción técnica. A continuación se reportan los principales prompts utilizados y su impacto:

### 7.1 Prompts principales y su impacto

**Prompt 1 — Planificación inicial:**
> "Hagamos un plan comparativo entre ACO y GA para TSP, y entre GD, EA, PSO y DE para funciones de prueba. Crea la estructura de carpetas y define los pasos de implementación."

*Impacto:* Generó la estructura de carpetas y el plan de trabajo. Aceleró la fase de diseño del experimento en ~2 horas. El plan sirvió como hoja de ruta para las sesiones de trabajo posteriores.

**Prompt 2 — Estándares de notebooks:**
> "Los notebooks como regla, baja alguna skill de buenas prácticas en notebook porque quiero las mejores y más profesionales prácticas y quiero todo excelentemente explicado y un código bonito y entendible."

*Impacto:* Estableció un conjunto de convenciones persistentes (estructura de celdas, figuras con fig/ax, Figura N en títulos, celda de conclusiones) que se aplicaron consistentemente en los tres notebooks. Mejoró significativamente la legibilidad y reproducibilidad del trabajo.

**Prompt 3 — Revisión de calidad (skill /simplify):**
> "Tu mismo corres simplify, y dale sigue."

*Impacto:* La revisión automática identificó y corrigió 6 problemas de calidad en el notebook 01: `np.vectorize` reemplazado por `np.apply_along_axis` (3× más rápido), grids computados una sola vez (evita recálculo innecesario), escala symlog para manejar valores cero en convergencia, y eliminación de un import no utilizado.

**Prompt 4 — Enriquecimiento teórico:**
> "Bueno agrégale más texto, más teoría, más verbo y ya."

*Impacto:* Expandió significativamente el contenido teórico del notebook 02: añadió contexto histórico de cada algoritmo, ecuaciones completas de velocidad PSO con factor de constricción, derivación de la regla de mutación DE, y justificación estadística de N=30 corridas. El notebook pasó de ~60 celdas a ~80 con texto más denso.

**Prompt 5 — Script de validación:**
> "Primero crea el script, valida, luego el notebook."

*Impacto:* El workflow script-primero permitió detectar y corregir problemas antes de escribir el notebook: EA usaba `random.uniform` de numpy en vez de Python (inconsistencia de semillas), y la tasa de éxito de PSO en Rosenbrock 3D (10%) se confirmó como un hallazgo real y no un bug.

### 7.2 Evaluación crítica del impacto de la IA

**Aportaciones positivas:**
- Aceleración significativa en la escritura de código boilerplate (estructura de loops, formatting de tablas, configuración de matplotlib).
- Detección automática de patrones ineficientes de código mediante la revisión sistemática de tres agentes paralelos (reuse, quality, efficiency).
- Generación de explicaciones teóricas claras y bien estructuradas que sirvieron como base para el texto final.

**Limitaciones observadas:**
- La IA no puede reemplazar el juicio experimental: decidir si un resultado inesperado (como EA con 0% en Rosenbrock) es un bug o un hallazgo válido requirió análisis manual.
- Los hiperparámetros de los algoritmos no fueron sintonizados por la IA: los valores provienen de la literatura y se verificaron manualmente contra los resultados experimentales.
- El modelo de costo para el TSP (combustible + peajes + tiempo) fue diseñado por el autor; la IA solo implementó la fórmula especificada.

---

## 8. Referencias

Applegate, D. L., Bixby, R. E., Chvátal, V., & Cook, W. J. (2006). *The traveling salesman problem: A computational study*. Princeton University Press.

Blum, C., & Roli, A. (2003). Metaheuristics in combinatorial optimization: Overview and conceptual comparison. *ACM Computing Surveys*, *35*(3), 268–308. https://doi.org/10.1145/937503.937505

Clerc, M., & Kennedy, J. (2002). The particle swarm — Explosion, stability, and convergence in a multidimensional complex space. *IEEE Transactions on Evolutionary Computation*, *6*(1), 58–73. https://doi.org/10.1109/4235.985692

Davis, L. (1985). Applying adaptive algorithms to epistatic domains. En *Proceedings of the 9th International Joint Conference on Artificial Intelligence* (pp. 162–164). IJCAI.

Dorigo, M. (1992). *Optimization, learning and natural algorithms* [Tesis doctoral]. Politecnico di Milano.

Dorigo, M., & Gambardella, L. M. (1997). Ant colony system: A cooperative learning approach to the traveling salesman problem. *IEEE Transactions on Evolutionary Computation*, *1*(1), 53–66. https://doi.org/10.1109/4235.585892

Eshelman, L. J., & Schaffer, J. D. (1993). Real-coded genetic algorithms and interval-schemata. *Foundations of Genetic Algorithms*, *2*, 187–202. https://doi.org/10.1016/B978-0-08-094832-4.50018-0

Fortin, F.-A., De Rainville, F.-M., Gardner, M.-A., Parizeau, M., & Gagné, C. (2012). DEAP: Evolutionary algorithms made easy. *Journal of Machine Learning Research*, *13*, 2171–2175.

Goldberg, D. E. (1989). *Genetic algorithms in search, optimization, and machine learning*. Addison-Wesley.

Helsgott, L. K., & Cook, W. (2012). *In pursuit of the traveling salesman: Mathematics at the limits of computation*. Princeton University Press.

Holland, J. H. (1975). *Adaptation in natural and artificial systems*. University of Michigan Press.

Instituto Nacional de Estadística y Geografía. (2023). *Marco geoestadístico: Municipios y localidades*. INEGI. https://www.inegi.org.mx/temas/mg/

Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. En *Proceedings of the IEEE International Conference on Neural Networks* (Vol. 4, pp. 1942–1948). IEEE. https://doi.org/10.1109/ICNN.1995.488968

Miranda, L. J. V. (2018). PySwarms: A research toolkit for particle swarm optimization in Python. *Journal of Open Source Software*, *3*(21), 433. https://doi.org/10.21105/joss.00433

Montgomery, D. C., & Runger, G. C. (2018). *Applied statistics and probability for engineers* (7.ª ed.). Wiley.

Mühlenbein, H., Gorges-Schleuter, M., & Krämer, O. (1991). Evolution algorithms in combinatorial optimization. *Parallel Computing*, *7*(1), 65–85. https://doi.org/10.1016/0167-8191(91)90049-M

Nocedal, J., & Wright, S. J. (2006). *Numerical optimization* (2.ª ed.). Springer.

Rastrigin, L. A. (1974). *Systems of extremal control*. Nauka.

Rosenbrock, H. H. (1960). An automatic method for finding the greatest or least value of a function. *The Computer Journal*, *3*(3), 175–184. https://doi.org/10.1093/comjnl/3.3.175

Storn, R., & Price, K. (1997). Differential evolution — A simple and efficient heuristic for global optimization over continuous spaces. *Journal of Global Optimization*, *11*(4), 341–359. https://doi.org/10.1023/A:1008202821328

Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., … SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, *17*, 261–272. https://doi.org/10.1038/s41592-019-0686-2
