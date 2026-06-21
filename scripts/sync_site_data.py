"""
Sincroniza las regiones de datos de docs/index.html con los resultados reales.

Regenera, a partir de resultados_heuristicos.json:
  - El cuerpo (<tbody>) de la tabla comparativa de heuristicos (30 filas).
  - El arreglo JS `pbData` con las tasas de exito por funcion/dim.

No toca el diseno ni el resto del HTML. Idempotente: correrlo de nuevo
produce el mismo resultado si los JSON no cambian.

Uso: python scripts/sync_site_data.py
"""

import json
import os

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML  = os.path.join(ROOT, 'docs', 'index.html')
JSONF = os.path.join(ROOT, 'resultados_heuristicos.json')

BADGE = {  # color del badge de metodo
    'EA':  ('bg-primary',   'text-on-primary'),
    'PSO': ('bg-tertiary',  'text-on-tertiary'),
    'DE':  ('bg-secondary', 'text-on-secondary'),
}


def fmt_f(v):
    return '0.00e+00' if v == 0 else '%.2e' % v


def fmt_int(v):
    return format(int(round(v)), ',').replace(',', ' ')


def exito_badge(pct):
    if pct == 100:
        return 'bg-secondary-container text-on-secondary-container'
    if pct == 0:
        return 'bg-error-container text-on-error-container'
    return 'bg-tertiary-container text-on-tertiary-container'


def fila(r, idx):
    bg = ('hover:bg-surface-container' if idx % 2 == 0
          else 'bg-surface-container-low hover:bg-surface-container')
    bcls, tcls = BADGE[r['metodo']]
    pct = int(round(r['tasa_exito'] * 100))
    # f* en negrita/verde solo cuando el exito es total
    fcls = ('text-right font-bold text-secondary text-xs' if pct == 100
            else 'text-right text-on-surface-variant text-xs')
    # evals en negrita/verde para DE (consistentemente el mas eficiente)
    ecls = ('text-right font-bold text-secondary text-xs' if r['metodo'] == 'DE'
            else 'text-right text-on-surface-variant text-xs')
    return (
        '            <tr class="%s transition-colors">\n'
        '              <td class="px-3 py-2"><span class="%s %s text-label-caps font-label-caps px-2 py-0.5 uppercase tracking-wider text-xs">%s</span></td>\n'
        '              <td class="px-3 py-2 text-on-surface text-xs">%s</td><td class="px-3 py-2 text-on-surface-variant text-xs">%dD</td>\n'
        '              <td class="%s">%s</td><td class="%s">%s</td>\n'
        '              <td class="px-3 py-2 text-center text-xs"><span class="%s px-2 py-0.5 text-label-caps font-label-caps uppercase tracking-wider">%d%%</span></td>\n'
        '              <td class="%s">%s</td>\n'
        '            </tr>\n'
    ) % (bg, bcls, tcls, r['metodo'], r['funcion'], r['ndim'],
         fcls, fmt_f(r['f_media']), fcls, fmt_f(r['f_mejor']),
         exito_badge(pct), pct, ecls, fmt_int(r['evals_media']))


def build_tbody(data):
    return ''.join(fila(r, i) for i, r in enumerate(data))


def build_pbdata(data):
    # agrupa por (funcion, dim) -> {metodo: pct}
    grupos = {}
    orden  = []
    for r in data:
        k = (r['funcion'], r['ndim'])
        if k not in grupos:
            grupos[k] = {}
            orden.append(k)
        grupos[k][r['metodo']] = int(round(r['tasa_exito'] * 100))
    lineas = []
    for (fn, dim) in orden:
        g = grupos[(fn, dim)]
        lineas.append("  { label:'%s %dD', ea:%d, pso:%d, de:%d },"
                      % (fn, dim, g.get('EA', 0), g.get('PSO', 0), g.get('DE', 0)))
    return 'const pbData = [\n' + '\n'.join(lineas) + '\n];'


def replace_between(text, start_marker, end_marker, new_inner, keep_markers=True):
    i = text.index(start_marker)
    j = text.index(end_marker, i + len(start_marker))
    if keep_markers:
        return text[:i + len(start_marker)] + new_inner + text[j:]
    return text[:i] + new_inner + text[j + len(end_marker):]


def main():
    with open(JSONF, encoding='utf-8') as fp:
        data = json.load(fp)
    with open(HTML, encoding='utf-8') as fp:
        html = fp.read()

    # 1) tbody de la tabla de heuristicos (primer tbody del documento)
    tbody_open = '<tbody class="divide-y divide-outline-variant">\n'
    html = replace_between(html, tbody_open, '          </tbody>',
                           build_tbody(data))

    # 2) arreglo pbData del grafico de tasas de exito
    html = replace_between(html, 'const pbData = [', '];',
                           build_pbdata(data)[len('const pbData = ['):-len('];')])

    with open(HTML, 'w', encoding='utf-8') as fp:
        fp.write(html)
    print('index.html sincronizado: %d filas, pbData actualizado.' % len(data))


if __name__ == '__main__':
    main()
