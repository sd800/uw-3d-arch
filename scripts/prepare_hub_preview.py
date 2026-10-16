"""Prepare a canvas-only capture of the historical navigation-hub core view.

Run after package_viewer.py. Serve the project and capture tmp/hub-preview.html
at a 1440 x 975 CSS-pixel viewport, reloading after setting that size. Wait for
the loading overlay to disappear, then use Save view for a lossless PNG export.
No camera or model data is changed.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'index.html').read_text().replace('<head>','<head><base href="../">',1)
style='''<style>
.header,.sidebar,.map-controls,.cut-panel,.legend,.statusbar,.orientation,.scale,.labels{display:none!important}
.app,.workspace,#viewport,#canvas-host{position:absolute!important;inset:0!important;width:100vw!important;height:100vh!important;min-height:0!important;margin:0!important;padding:0!important;display:block!important}
/* Export only the canvas, without including any interface pixels. */
.header,.header .header-right{display:contents!important}
.header>*,.header-right>*{display:none!important}
#download-image{display:block!important;position:fixed;right:8px;top:8px;z-index:100}
</style>'''
(r/'tmp').mkdir(exist_ok=True)
(r/'tmp/hub-preview.html').write_text(s.replace('</head>',style+'</head>'))
print('Capture tmp/hub-preview.html at 1440 x 975; keep the initial core camera.')
