"""Build the crawlable root viewer and self-contained offline edition."""
from pathlib import Path
from html import escape
from datetime import datetime
from zoneinfo import ZoneInfo
import json,base64,hashlib,gzip
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1];out=r/'output';assets=r/'assets'
config=json.loads((r/'config/site.config.json').read_text());summary=json.loads((out/'model_summary.json').read_text());records=json.loads((out/'viewer_records.json').read_text());site=config['url']
meta=json.loads((r/'sources/terrain_export_metadata.json').read_text());e=meta['extent'];dem=np.asarray(Image.open(r/'sources/terrain_dem.tif'));ox,oy=summary['origin_utm']
xs=np.linspace(e['xmin'],e['xmax'],dem.shape[1],endpoint=False)+(e['xmax']-e['xmin'])/dem.shape[1]/2-ox;ys=np.linspace(e['ymin'],e['ymax'],dem.shape[0],endpoint=False)+(e['ymax']-e['ymin'])/dem.shape[0]/2-oy
xi=list(range(0,len(xs),3));yi=list(range(0,len(ys),3));xi.append(len(xs)-1);yi.append(len(ys)-1)
grid={'x':[round(float(xs[i]),2) for i in xi],'y':[round(float(ys[i]),2) for i in yi],'heights':np.round(dem[::-1][np.ix_(yi,xi)],2).tolist()}
model=(out/'UW_Seattle.glb').read_bytes();from web_model_package import web_payload
web,compressed=web_payload(r,model)
encoded=base64.b64encode(compressed).decode();preview=base64.b64encode((out/'campus_aerial.png').read_bytes()).decode()
preview_width,preview_height=Image.open(out/'campus_aerial.png').size
order=[b['facility_id'] for b in records if b['landmark']]
from curation import LANDMARKS,HIGHLIGHT_ORDER
order=[id for id in HIGHLIGHT_ORDER if id in order or id=='DRUMHELLER']
from terrain_contact import grade_pads
b=summary['bounds'];data={**web,'groundPads':grade_pads(out),'overviewCenter':summary['overview_center'],'groundGrid':grid,'modelByteLength':len(model),'modelTransferBytes':len(compressed),'modelGlobal':'__UW_MODEL_BASE64__','downloadUrl':'output/UW_Seattle.glb','compression':'gzip','offlineModelScript':'assets/model-local.js','layers':json.loads((out/'layer_map.json').read_text()),'palette':json.loads((out/'palette.json').read_text()),'records':records,'preview':'output/campus_aerial.png','seo':{'en':{k:config[k] for k in ['title','description','imageAlt']},'zh':config['zh']},'landmarkOrder':order,'districtBounds':{**summary['district_bounds'],'core':[-250,-280,360,330],'east':[390,-810,970,30],'overview':[-740,-840,850,760]},'siteCenter':[(b[0]+b[2])/2,(b[1]+b[3])/2],'places':json.loads((out/'places.json').read_text())}
fountain=next(p for p in data['places']if p['name']=='Drumheller Fountain')
from shapely.geometry import shape
fb=shape(fountain['hitArea']).bounds;fz=fountain['position'][2]-1
data['tourPlaces']=[{'facility_id':'DRUMHELLER','code':'place:drumheller','outdoor':True,'name':fountain['name'],'name_zh':fountain['name_zh'],'bounds':[fb[0]-8,fb[1]-8,fz,fb[2]+8,fb[3]+8,fz+20]}]
neighbors=json.loads((out/'neighboring_areas.json').read_text());data['neighbors']=json.loads((out/'neighboring_records.json').read_text());data['neighborPads']=neighbors['pads'];data['neighborBounds']=neighbors['bounds'];data['waterFrame']=summary['water_frame']
date=datetime.now(ZoneInfo('America/Chicago')).date().isoformat()
schema={'@context':'https://schema.org','@graph':[{'@type':'WebSite','@id':site+'#website','url':site,'name':'UW Campus 3D Model','inLanguage':['en','zh-CN'],'sameAs':config['repository'],'image':site+'assets/brand/w-map.png'},{'@type':'WebPage','@id':site+'#webpage','url':site,'name':config['title'],'description':config['description'],'inLanguage':['en','zh-CN'],'isPartOf':{'@id':site+'#website'},'mainEntity':{'@id':site+'#model'},'dateModified':date,'primaryImageOfPage':{'@type':'ImageObject','url':site+'output/campus_aerial.png','width':preview_width,'height':preview_height}},{'@type':'3DModel','@id':site+'#model','name':'University of Washington Seattle exterior campus model','description':f"Independent public-source exterior model with {len(records)} building layers, a separate environment layer, university GIS tree positions and sampled USGS terrain. Exterior heights and geometry are approximate, not a measured as-built survey.",'contentUrl':site+'output/UW_Seattle.glb','encodingFormat':'model/gltf-binary','contentSize':str(len(model))+' bytes','sha256':hashlib.sha256(model).hexdigest(),'thumbnailUrl':site+'output/campus_aerial.png','contentLocation':{'@type':'Place','name':'University of Washington Seattle campus','address':{'@type':'PostalAddress','addressLocality':'Seattle','addressRegion':'WA','addressCountry':'US'}},'isBasedOn':['https://map.uw.edu/?id=2099','https://facilities.uw.edu/services/space/gis-maps','https://www.openstreetmap.org/','https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer']}]}
def jsjson(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
from model_downloads import downloads,links
data['downloads']=downloads(r)

for item in schema['@graph']:
 if item['@type']=='3DModel':
  glb=data['downloads'][2];item['contentUrl']=site+glb['url'];item['encodingFormat']='application/x-xz'if glb['name'].endswith('.xz')else'model/gltf-binary';item['contentSize']=str((r/glb['url']).stat().st_size)+' bytes';item['sha256']=hashlib.sha256((r/glb['url']).read_bytes()).hexdigest()

template=(r/'scripts/viewer.template.html').read_text();bundle=(r/'tmp/viewer.bundle.js').read_text()
rows=''.join(f'<div class="row"><span class="building-name" data-building-name="{escape(b["code"])}">{escape(b["name"])}</span><span class="building-meta">{escape(b["name_zh"])} · {b["code"]}</span></div>' for b in records)
for token,value in {'__SITE_URL__':site,'__SEO_TITLE__':escape(config['title'],quote=True),'__SEO_DESCRIPTION__':escape(config['description'],quote=True),'__IMAGE_ALT__':escape(config['imageAlt'],quote=True),'__STRUCTURED_DATA__':jsjson(schema),'__INITIAL_BUILDINGS__':rows,'__INITIAL_COUNT__':str(len(records)),'__PREVIEW_WIDTH__':str(preview_width),'__PREVIEW_HEIGHT__':str(preview_height)}.items():template=template.replace(token,value)
license=((r/'docs/THIRD_PARTY_NOTICES.md').read_text()+'\n'+(assets/'fonts/OFL.txt').read_text()).replace('--','- -');template=template.replace('</head>','<!--\n'+license+'\n-->\n</head>')
def edition(payload,font,preview,icons,logo,script,robots,rhino):
    html=template.replace('__MODEL_DOWNLOADS__',links(payload,robots.startswith('noindex')))
    for token,value in {'__CAMPUS_DATA__':jsjson(payload),'__TITLE_FONT_URL__':font,'__PREVIEW_IMAGE__':preview,'__FAVICON__':icons['32'],'__FAVICON_16__':icons['16'],'__APPLE_ICON__':icons['apple'],'__LOGO__':logo,'__VIEWER_SCRIPT__':script,'__ROBOTS__':robots,'__RHINO_URL__':rhino}.items():html=html.replace(token,value)
    assert not any(t in html for t in ['__CAMPUS_DATA__','__TITLE_FONT_URL__','__PREVIEW_IMAGE__','__FAVICON__','__APPLE_ICON__','__LOGO__','__VIEWER_SCRIPT__','__ROBOTS__','__RHINO_URL__']);return html
(assets/'viewer.bundle.js').write_text(bundle);(assets/'model-local.js').write_text('// Generated GLB model data, not credentials.\nwindow.__UW_MODEL_BASE64__=\"'+'\\\n'.join(encoded[i:i+32]for i in range(0,len(encoded),32))+'\";\n')
html=edition(data,'assets/fonts/Manrope.ttf','output/campus_aerial.png',{'32':'assets/favicon-32.png','16':'assets/favicon-16.png','apple':'assets/apple-touch-icon.png'},'assets/brand/w-map-192.png','<script defer src="assets/viewer.bundle.js?v='+hashlib.sha256(bundle.encode()).hexdigest()[:12]+'"></script>','index, follow, max-image-preview:large','output/UW_Seattle_Layered.3dm');(r/'index.html').write_text(html)
def png(path):return 'data:image/png;base64,'+base64.b64encode((assets/path).read_bytes()).decode()
offline=edition({**data,'downloads':[{**i,'url':i['name']}for i in data['downloads']],'model':encoded,'preview':'data:image/png;base64,'+preview},'data:font/ttf;base64,'+base64.b64encode((assets/'fonts/Manrope.ttf').read_bytes()).decode(),'data:image/png;base64,'+preview,{'32':png('favicon-32.png'),'16':png('favicon-16.png'),'apple':png('apple-touch-icon.png')},png('brand/w-map-192.png'),'<script>'+bundle.replace('</script',r'<\/script')+'</script>','noindex, follow','UW_Seattle_Layered.3dm');(out/'UW_Campus_Offline.html').write_text(offline)
(r/'CNAME').write_text(config['domain']+'\n');(r/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+site+'sitemap.xml\n');(r/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+site+'</loc><lastmod>'+date+'</lastmod></url></urlset>\n')
print('Viewer:',len(html.encode()),'bytes; offline:',len(offline.encode()),'bytes; buildings:',len(records))
