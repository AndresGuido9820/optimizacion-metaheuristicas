"""
Renderiza el reporte tecnico (report/blog_post.md) a una pagina HTML autocontenida
publicable en GitHub Pages: docs/reporte.html.

- Protege las expresiones matematicas ($...$ y $$...$$) antes de convertir Markdown
  para que MathJax (mismo CDN que index.html) las renderice en el navegador.
- Reescribe las rutas de imagenes (../docs/assets/figures -> assets/figures) para
  que resuelvan desde docs/.

Uso: python scripts/build_report_html.py
"""
import os
import re
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, 'report', 'blog_post.md')
OUT  = os.path.join(ROOT, 'docs', 'reporte.html')

TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Reporte tecnico — Optimizacion Metaheuristica</title>
<script>
MathJax = {
  tex: { inlineMath: [['$','$']], displayMath: [['$$','$$']] },
  options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js" async></script>
<style>
  :root { --fg:#1b1c1e; --muted:#5b6168; --line:#d7dce3; --accent:#386A20; --bg:#ffffff; --soft:#f3f6f9; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         line-height:1.65; }
  .wrap { max-width: 920px; margin: 0 auto; padding: 32px 20px 80px; }
  .topbar { position:sticky; top:0; background:var(--bg); border-bottom:1px solid var(--line);
            padding:10px 20px; display:flex; gap:18px; align-items:center; font-size:14px; z-index:5; }
  .topbar a { color:var(--accent); text-decoration:none; font-weight:600; }
  .topbar a:hover { text-decoration:underline; }
  h1 { font-size:1.9rem; line-height:1.25; margin:1.2em 0 .5em; }
  h2 { font-size:1.45rem; margin:1.6em 0 .5em; padding-bottom:.2em; border-bottom:2px solid var(--line); }
  h3 { font-size:1.2rem; margin:1.3em 0 .4em; }
  h4 { font-size:1.05rem; margin:1.1em 0 .3em; color:var(--muted); }
  p, li { font-size:1rem; }
  a { color:var(--accent); }
  img { max-width:100%; height:auto; display:block; margin:1em auto; border:1px solid var(--line); border-radius:6px; }
  table { border-collapse:collapse; width:100%; margin:1em 0; font-size:.9rem; display:block; overflow-x:auto; }
  th, td { border:1px solid var(--line); padding:6px 10px; text-align:left; }
  thead th { background:var(--soft); }
  tbody tr:nth-child(even) { background:var(--soft); }
  code { background:var(--soft); padding:1px 5px; border-radius:4px; font-size:.88em; }
  pre { background:#1e293b; color:#e2e8f0; padding:14px 16px; border-radius:8px; overflow-x:auto; }
  pre code { background:transparent; color:inherit; padding:0; }
  blockquote { border-left:4px solid var(--accent); margin:1em 0; padding:.4em 1em; background:var(--soft); color:var(--muted); }
  hr { border:none; border-top:1px solid var(--line); margin:2em 0; }
</style>
</head>
<body>
<div class="topbar">
  <a href="index.html">&larr; Sitio del proyecto</a>
  <a href="https://github.com/AndresGuido9820/optimizacion-metaheuristicas" target="_blank">Repositorio</a>
</div>
<div class="wrap">
__BODY__
</div>
</body>
</html>
"""


def main():
    text = open(SRC, encoding='utf-8').read()
    # rutas de imagen relativas al reporte -> relativas a docs/
    text = text.replace('../docs/assets/figures/', 'assets/figures/')

    # proteger matematicas para que Markdown no las altere
    store = []

    def protect(m):
        store.append(m.group(0))
        return 'MJXMATH%dXJM' % (len(store) - 1)

    text = re.sub(r'\$\$.*?\$\$', protect, text, flags=re.S)
    text = re.sub(r'\$[^\$\n]+?\$', protect, text)

    body = markdown.markdown(
        text, extensions=['tables', 'fenced_code', 'sane_lists', 'toc'])

    for i, expr in enumerate(store):
        body = body.replace('MJXMATH%dXJM' % i, expr)

    html = TEMPLATE.replace('__BODY__', body)
    with open(OUT, 'w', encoding='utf-8') as fp:
        fp.write(html)
    print('Generado docs/reporte.html (%d expresiones math, %d KB)'
          % (len(store), len(html) // 1024))


if __name__ == '__main__':
    main()
