"""
Regenera las figuras de comparacion de heuristicos del sitio a partir de los
resultados reales (resultados_heuristicos.json):
  - docs/assets/figures/comparison_bars.png : tasa de exito por funcion/dim y metodo
  - docs/assets/figures/evals_comparison.png: evaluaciones promedio (escala log)

Uso: python scripts/figuras_comparativa.py
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONF = os.path.join(ROOT, 'resultados_heuristicos.json')
DIR   = os.path.join(ROOT, 'docs', 'assets', 'figures')

COL = {'EA': '#6750A4', 'PSO': '#7D5260', 'DE': '#386A20'}


def main():
    with open(JSONF, encoding='utf-8') as fp:
        data = json.load(fp)

    # agrupa por (funcion, dim) preservando orden de aparicion
    labels, ex, ev = [], {'EA': [], 'PSO': [], 'DE': []}, {'EA': [], 'PSO': [], 'DE': []}
    seen = []
    for r in data:
        k = '%s %dD' % (r['funcion'], r['ndim'])
        if k not in seen:
            seen.append(k)
    for k in seen:
        labels.append(k)
        for r in data:
            if '%s %dD' % (r['funcion'], r['ndim']) == k:
                ex[r['metodo']].append(r['tasa_exito'] * 100)
                ev[r['metodo']].append(r['evals_media'])

    x = np.arange(len(labels))
    w = 0.26

    # ── Figura 1: tasa de exito ───────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for i, m in enumerate(('EA', 'PSO', 'DE')):
        ax.bar(x + (i - 1) * w, ex[m], w, label=m, color=COL[m])
    ax.set_ylabel('Tasa de éxito (%)')
    ax.set_title('Tasa de éxito por función/dimensión y método (30 corridas)')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=35, ha='right', fontsize=8)
    ax.set_ylim(0, 105); ax.legend(); ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(DIR, 'comparison_bars.png'), dpi=120, bbox_inches='tight')
    plt.close(fig)

    # ── Figura 2: evaluaciones (escala log) ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for i, m in enumerate(('EA', 'PSO', 'DE')):
        ax.bar(x + (i - 1) * w, ev[m], w, label=m, color=COL[m])
    ax.set_ylabel('Evaluaciones de $f$ (escala log)')
    ax.set_yscale('log')
    ax.set_title('Número de evaluaciones de la función objetivo por método')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=35, ha='right', fontsize=8)
    ax.legend(); ax.grid(axis='y', alpha=0.3, which='both')
    fig.tight_layout()
    fig.savefig(os.path.join(DIR, 'evals_comparison.png'), dpi=120, bbox_inches='tight')
    plt.close(fig)

    print('Regeneradas: comparison_bars.png, evals_comparison.png')


if __name__ == '__main__':
    main()
