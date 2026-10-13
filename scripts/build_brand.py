"""Generate an editable purple/gold W-and-map project icon."""
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];a=r/'assets';(a/'brand').mkdir(exist_ok=True)
purple='#4b2e83';gold='#e8e3d3';scale=4
# Original project monogram; not an official university signature lockup.
pts=[(60,68),(158,68),(158,101),(140,101),(181,239),(226,98),(212,98),(212,68),(301,68),(301,98),(287,98),(332,239),(374,101),(356,101),(356,68),(452,68),(452,101),(429,101),(355,319),(301,319),(256,179),(211,319),(157,319),(83,101),(60,101)]
path='M'+' '.join(f'{x},{y}' for x,y in pts)+'Z'
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><title>UW campus model: W and map</title><rect width="512" height="512" rx="72" fill="{purple}"/><path d="{path}" fill="{gold}"/><rect x="120" y="365" width="272" height="101" rx="4" fill="{gold}"/><path d="M150 390H215V417H258M150 439H213M238 389V405M280 441L292 428L316 425" fill="none" stroke="{purple}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/><path d="M334 385C320 385 311 395 311 407C311 420 334 441 334 441S357 420 357 407C357 395 348 385 334 385Z" fill="{purple}"/><circle cx="334" cy="406" r="8" fill="{gold}"/></svg>'''
(a/'brand/w-map.svg').write_text(svg+'\n');im=Image.new('RGBA',(2048,2048),(0,0,0,0));d=ImageDraw.Draw(im);d.rounded_rectangle((0,0,2047,2047),radius=72*scale,fill=purple);d.polygon([(x*scale,y*scale) for x,y in pts],fill=gold);d.rounded_rectangle((120*scale,365*scale,392*scale,466*scale),radius=4*scale,fill=gold)
for points in [[(150,390),(215,390),(215,417),(258,417)],[(150,439),(213,439)],[(238,389),(238,405)],[(280,441),(292,428),(316,425)]]:d.line([(x*scale,y*scale) for x,y in points],fill=purple,width=7*scale,joint='curve')
d.polygon([(311*scale,407*scale),(357*scale,407*scale),(334*scale,441*scale)],fill=purple);d.ellipse((311*scale,385*scale,357*scale,427*scale),fill=purple);d.ellipse((326*scale,398*scale,342*scale,414*scale),fill=gold)
for size,file in [(1024,'brand/w-map.png'),(192,'brand/w-map-192.png'),(180,'apple-touch-icon.png'),(32,'favicon-32.png'),(16,'favicon-16.png')]:im.resize((size,size),Image.Resampling.LANCZOS).save(a/file)
im.resize((256,256),Image.Resampling.LANCZOS).save(r/'favicon.ico',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
(a/'brand/README.md').write_text('''# Campus model icon

Original W-and-map project monogram in UW-inspired purple (#4b2e83) and pale gold (#e8e3d3). The upright map contains a route and location pin. This is an independent project icon, not an official UW signature. Edit `w-map.svg` or regenerate all sizes with `scripts/build_brand.py`.

Palette reference: https://www.washington.edu/brand/brand-elements/colors/
''')
print('W-and-map SVG, PNG sizes and favicon generated.')
