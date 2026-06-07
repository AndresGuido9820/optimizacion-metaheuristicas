# Registro de Prompts de IA — Trabajo 01

**Herramienta utilizada:** Claude (Anthropic)
**Propósito:** Apoyo en implementación, depuración y análisis de los algoritmos.

---

## Prompt 1 — Depuración de ACO

> "Mi ACO converge muy rápido en las primeras iteraciones pero después se estanca. ¿El problema puede ser la tasa de evaporación o el depósito de feromona?"

**Impacto:** Identificó que rho=0.3 era demasiado alto y estaba colapsando la diversidad del enjambre. Se ajustó a rho=0.1 y el estancamiento desapareció.

---

## Prompt 2 — OX Crossover en DEAP

> "Cómo implemento el Order Crossover (OX) de Davis en DEAP para que respete la estructura de permutación del TSP?"

**Impacto:** Confirmó el uso de `tools.cxOrdered` de DEAP como implementación directa del OX crossover. Evitó implementar el operador desde cero.

---

## Prompt 3 — Factor de constricción en PSO

> "¿Por qué usar w=0.729 en PSO? ¿Qué garantiza ese valor específico?"

**Impacto:** Explicó que w=0.729 es el factor de constricción de Clerc-Kennedy (2002) que garantiza convergencia teórica del enjambre. Se usó este valor en lugar de w arbitrario.

---

## Prompt 4 — DE en valle estrecho

> "La evolución diferencial converge bien en Rosenbrock 2D pero en 3D le cuesta más. ¿Por qué y cómo se comporta el vector de mutación cerca del óptimo?"

**Impacto:** Explicó el mecanismo de escala adaptativa: cuando la población converge, F*(x_r2 - x_r3) se vuelve pequeño automáticamente. Esto clarificó por qué DE maneja bien el valle sin ajuste manual de step size.

---

## Prompt 5 — Haversine vs distancia euclidiana

> "Para el TSP de las capitales, ¿qué tan grande es el error si uso distancia euclidiana sobre lat/lon en vez de haversine?"

**Impacto:** Cuantificó el error: hasta 15% en distancias largas (Mexicali–Mérida ~3,200 km). Se decidió usar haversine para todas las distancias.

---

## Prompt 6 — Tasa de éxito EA en Rosenbrock

> "Mi EA tiene 0% de éxito en Rosenbrock pero 100% en Rastrigin. ¿Es un bug o tiene sentido teórico?"

**Impacto:** Confirmó que es un resultado teóricamente esperado: cxBlend con alpha=0.5 genera hijos fuera del valle estrecho de Rosenbrock, mientras que para Rastrigin la exploración amplia es exactamente lo que se necesita.

---

## Prompt 7 — Comparación estadística ACO vs GA

> "Tengo 30 corridas de ACO con media=56,957 y std=410, y GA con media=58,744 y std=1,710. ¿Cómo interpreto que GA encontró la mejor solución absoluta (55,796) pero ACO tiene menor varianza?"

**Impacto:** Introdujo el concepto de tensión entre consistencia (CV=0.72% ACO) y capacidad de pico (GA encontró mejor absoluto). Se usó el coeficiente de variación como métrica principal en la discusión.

---

---

## Prompt 8 — Completar funciones faltantes y TSP Francia

> "Sí, revisa por fa [el contenido de los notebooks]. [...] Sí, pero hazlo de manera ordenada, un código fácil de entender, descripción entre celdas y así."

**Impacto:** Identificó que los notebooks originales solo implementaban Rosenbrock y Rastrigin, faltaban Schwefel, Griewank, Goldstein-Price y Camel 6-hump, el experimento n=100/500/1000 con histogramas, y que el TSP usaba México en lugar de Francia (que era lo pedido en la tarea). Se reorganizaron los tres notebooks con las correcciones y se actualizó todo el reporte.

---

## Prompt 9 — Limpieza y consistencia del repositorio

> "Okey y cambia entonces el reporte, con los resultados reales, cambia si es necesario el README, y mira todo los detalles, revisa que las carpetas y archivos estén organizadas, no haya código inútil, etc."

**Impacto:** Se eliminaron archivos obsoletos (notebooks y scripts de parche), se renombró `teoria_03_tsp_mexico.md` a `teoria_03_tsp_france.md`, se actualizaron README, blog_post, teoría de funciones y discusión para reflejar las 6 funciones y el TSP de Francia. El repositorio quedó consistente entre código, notebooks y documentación.

---

*Nota: Los prompts son paráfrasis representativas. Los valores numéricos reportados provienen de las corridas experimentales reales.*
