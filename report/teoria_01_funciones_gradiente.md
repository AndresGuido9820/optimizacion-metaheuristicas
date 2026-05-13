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
