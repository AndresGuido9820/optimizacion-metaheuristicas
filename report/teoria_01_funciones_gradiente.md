# Teoría — Funciones de Prueba y Descenso por Gradiente

## 1. Funciones de prueba

Las funciones de prueba son herramientas estándar para evaluar algoritmos de optimización en condiciones controladas y reproducibles. Permiten comparar métodos en paisajes conocidos antes de aplicarlos a problemas reales.

### 1.1 Función de Rosenbrock

Propuesta por Rosenbrock (1960), es una función **unimodal no convexa**:

$$f(\mathbf{x}) = \sum_{i=1}^{n-1} \left[ 100(x_{i+1} - x_i^2)^2 + (1 - x_i)^2 \right]$$

- **Óptimo global:** $f(\mathbf{1}) = 0$ en $\mathbf{x}^* = (1, 1, \ldots, 1)$
- **Dominio habitual:** $[-5, 5]^n$

La dificultad radica en un **valle parabólico estrecho y curvado**: el gradiente a lo largo del fondo del valle es casi nulo, por lo que los algoritmos convergen muy lento una vez dentro. El primer término penaliza la desviación de $x_{i+1} = x_i^2$ (fuerza al punto hacia la parábola), y el segundo penaliza alejarse de $x_i = 1$ (empuja hacia el óptimo a lo largo del valle).

En 2D el valle corre desde $(-1, 1)$ hacia $(1, 1)$. En 3D la estructura se vuelve más difícil: hay que navegar simultáneamente dos valles acoplados.

### 1.2 Función de Rastrigin

Introducida por Rastrigin (1974), es una función **altamente multimodal**:

$$f(\mathbf{x}) = An + \sum_{i=1}^{n} \left[ x_i^2 - A \cos(2\pi x_i) \right], \quad A = 10$$

- **Óptimo global:** $f(\mathbf{0}) = 0$
- **Número de mínimos locales:** $\approx 10^n$ en $[-5, 5]^n$

La función combina una parábola base ($x_i^2$) con una perturbación coseno que crea un reticulado regular de mínimos locales, todos a distancia comparable en valor de función. En 2D hay aproximadamente 50 mínimos locales visibles. Es el estándar para evaluar la capacidad de un método para **escapar de mínimos locales**.

---

### 1.3 Función de Schwefel

Propuesta por Schwefel (1981):

$$f(\mathbf{x}) = 418.9829\,n - \sum_{i=1}^{n} x_i \sin\!\left(\sqrt{|x_i|}\right)$$

- **Dominio:** $[-500, 500]^n$
- **Óptimo global:** $f(420.9687, \ldots) \approx 0$
- **Gradiente:** se aproxima numéricamente (no tiene forma analítica simple)

La característica que hace difícil esta función es que el **mínimo global está lejos del centro del dominio** (en $x \approx 420.97$), y los mínimos locales secundarios tienen valores de función muy similares. El descenso por gradiente iniciado cerca del origen convergerá a un mínimo local subóptimo en la mayoría de los casos.

---

### 1.4 Función de Griewank

Propuesta por Griewank (1981):

$$f(\mathbf{x}) = 1 + \frac{1}{4000}\sum_{i=1}^{n} x_i^2 - \prod_{i=1}^{n} \cos\!\left(\frac{x_i}{\sqrt{i}}\right)$$

- **Dominio:** $[-600, 600]^n$
- **Óptimo global:** $f(\mathbf{0}) = 0$

La función combina una parábola de baja curvatura (término $\sum x_i^2 / 4000$) con un término producto de cosenos que genera mínimos locales uniformemente distribuidos. Cerca del origen, la curvatura de la parábola domina y la función se comporta casi cuadráticamente; lejos del origen, los mínimos locales se vuelven más pronunciados.

---

### 1.5 Función de Goldstein-Price (solo 2D)

Definida para $\mathbf{x} \in [-2, 2]^2$:

$$f(\mathbf{x}) = \left[1 + (x_1+x_2+1)^2(19 - 14x_1 + 3x_1^2 - 14x_2 + 6x_1x_2 + 3x_2^2)\right]$$
$$\times\left[30 + (2x_1-3x_2)^2(18 - 32x_1 + 12x_1^2 + 48x_2 - 36x_1x_2 + 27x_2^2)\right]$$

- **Dominio:** $[-2, 2]^2$ (solo 2D por definición)
- **Óptimo global:** $f(0, -1) = 3$

La función tiene valores que varían entre 3 y $\sim 10^6$ en el dominio, con un paisaje muy irregular y múltiples mínimos locales en un espacio pequeño.

---

### 1.6 Función de las seis jorobas de camello (Camel 6-hump, solo 2D)

Definida para $x_1 \in [-3, 3],\; x_2 \in [-2, 2]$:

$$f(\mathbf{x}) = \left(4 - 2.1x_1^2 + \frac{x_1^4}{3}\right)x_1^2 + x_1 x_2 + (-4 + 4x_2^2)x_2^2$$

- **Dominio:** $x_1 \in [-3, 3],\; x_2 \in [-2, 2]$ (solo 2D por definición)
- **Mínimos globales:** $f(0.0898, -0.7126) = f(-0.0898, 0.7126) \approx -1.0316$

La función tiene exactamente 6 mínimos locales (las "jorobas"), dos de los cuales son globales y simétricamente ubicados respecto al origen. Es útil para evaluar si un algoritmo puede encontrar ambos mínimos globales.

---

### 1.7 Análisis estadístico: n = 100, 500 y 1 000 condiciones iniciales

Para el descenso por gradiente, el desempeño depende fuertemente de la condición inicial. La tasa de éxito y el número de evaluaciones varían según la función:

| Función | Comportamiento esperado con n repeticiones |
|---------|-------------------------------------------|
| Rosenbrock | Alta varianza: ~80% éxito en 2D, ~50% en 3D (depende del punto inicial respecto al valle) |
| Rastrigin | Baja tasa: ~20% en 2D, ~10% en 3D (muchos mínimos locales) |
| Schwefel | Muy baja tasa: el mínimo está lejos del centro del dominio |
| Griewank | Moderada: cerca del origen la función se comporta casi cuadrática, favoreciendo al GD |

Los **histogramas de f*** permiten ver la distribución bimodal típica: un pico cerca de 0 (éxito) y otro en los mínimos locales (fracaso). Los **histogramas de evaluaciones** revelan que convergencia exitosa requiere más iteraciones (el algoritmo navega el valle antes de terminar).

---

## 2. Descenso por gradiente con búsqueda en línea

El descenso por gradiente es el método iterativo fundamental de la optimización diferenciable:

$$\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha_k \nabla f(\mathbf{x}_k)$$

### 2.1 Búsqueda en línea con retroceso (Armijo)

El tamaño de paso $\alpha_k$ se determina con **backtracking** basado en la condición de Armijo:

$$f(\mathbf{x}_k - \alpha \nabla f(\mathbf{x}_k)) \leq f(\mathbf{x}_k) - c \cdot \alpha \|\nabla f(\mathbf{x}_k)\|^2$$

- Parámetros: $c = 10^{-4}$, factor de reducción $\beta = 0.5$, paso inicial $\alpha_0 = 1.0$
- El backtracking reduce $\alpha \leftarrow \beta \alpha$ hasta que se cumpla la condición

La condición de Armijo garantiza **descenso suficiente** en cada iteración sin requerir una búsqueda exacta, reduciendo el costo computacional por iteración (Nocedal & Wright, 2006).

### 2.2 Gradiente numérico

El gradiente se aproxima con **diferencias finitas centrales** de orden $O(h^2)$:

$$\frac{\partial f}{\partial x_i} \approx \frac{f(\mathbf{x} + h\mathbf{e}_i) - f(\mathbf{x} - h\mathbf{e}_i)}{2h}, \quad h = 10^{-5}$$

### 2.3 Limitaciones en funciones multimodales

GD es un método **local**: solo puede converger al mínimo más cercano al punto de inicio. En Rastrigin, donde hay $\approx 10^n$ mínimos locales, la probabilidad de converger al óptimo global desde un punto aleatorio es pequeña, especialmente en dimensiones altas. En Rosenbrock, el problema es diferente: GD converge al óptimo único pero puede hacerlo extremadamente lento si la condición inicial está lejos del fondo del valle.

---

## 3. Referencias

- Nocedal, J., & Wright, S. J. (2006). *Numerical optimization* (2.ª ed.). Springer.
- Rosenbrock, H. H. (1960). An automatic method for finding the greatest or least value of a function. *The Computer Journal*, *3*(3), 175–184.
- Rastrigin, L. A. (1974). *Systems of extremal control*. Nauka.
