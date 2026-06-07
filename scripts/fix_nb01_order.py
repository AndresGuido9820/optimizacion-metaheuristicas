"""
Correccion de orden en notebook 01:
Las 3 celdas de histogramas quedaron al inicio (indices 0-2) en lugar de
antes de las Conclusiones. Este script las mueve al lugar correcto.
"""

import json
from pathlib import Path

NB_PATH = Path("notebooks/01_funciones_gradiente.ipynb")

with open(NB_PATH) as fh:
    nb = json.load(fh)

cells = nb["cells"]

# Extraer las 3 celdas desplazadas del inicio
hist_md   = cells.pop(0)
hist_exp  = cells.pop(0)
hist_plot = cells.pop(0)

# Verificar que son las correctas
assert "estadistico" in "".join(hist_md["source"]).lower(), "No es la celda de histogramas"
print(f"Extraidas 3 celdas de histogramas del inicio.")
print(f"Notebook ahora tiene {len(cells)} celdas.")

# Buscar la celda de Conclusiones (buscamos la que empiece con '## 5.' o '## Concl')
for i, c in enumerate(cells):
    src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
    if c["cell_type"] == "markdown" and src.strip().startswith("## 5."):
        # Insertar las 3 celdas antes de ella en orden correcto
        cells.insert(i, hist_plot)
        cells.insert(i, hist_exp)
        cells.insert(i, hist_md)
        print(f"Celdas de histogramas insertadas antes de celda {i}: {src[:60]!r}")
        break

nb["cells"] = cells

with open(NB_PATH, "w") as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)

print(f"\nNotebook 01 corregido: {len(nb['cells'])} celdas totales.")
