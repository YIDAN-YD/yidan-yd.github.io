"""Import pinned ICTV taxonomy using stdlib; XLSX files stay local, untracked."""
import json,collections,pathlib,urllib.request,zipfile,xml.etree.ElementTree as E
root=pathlib.Path(__file__).resolve().parent.parent
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
urls={'msl':'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2025_MSL41.v1.xlsx','vmr':'https://ictv.global/sites/default/files/VMR/VMR_MSL41.v1.20260729.xlsx'}
def read(kind):
 path=root/'sources'/f'{kind}.xlsx'
 if not path.exists():urllib.request.urlretrieve(urls[kind],path)
 with zipfile.ZipFile(path) as z:
  strings=[''.join(t.text or '' for t in e.findall('.//s:t',ns)) for e in E.fromstring(z.read('xl/sharedStrings.xml'))]
  rows=[]
  for row in E.fromstring(z.read('xl/worksheets/sheet2.xml')).findall('.//s:sheetData/s:row',ns):
   d={}
   for c in row:
    v=c.find('s:v',ns);value=v.text if v is not None else ''
    if c.get('t')=='s':value=strings[int(value)] if value else ''
    elif c.get('t')=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//s:t',ns))
    d[''.join(x for x in c.get('r') if x.isalpha())]=value
   rows.append(d)
  return rows
msl,vmr=read('msl'),read('vmr');by_id=collections.defaultdict(list)
for r in vmr[1:]:
 if r.get('S'):by_id[r['S']].append(r)
rows=[]
for r in msl[1:]:
 if not r.get('P'):continue
 a=by_id[r['Q']];e=next((x for x in a if x.get('T')=='E'),a[0] if a else {})
 rows.append(dict(id=r['Q'],species=r['P'],family=r.get('L',''),genus=r.get('N',''),realm=r.get('B',''),kingdom=r.get('D',''),phylum=r.get('F',''),class_name=r.get('H',''),order=r.get('J',''),genome=r.get('R',''),name=e.get('U',''),abbr=e.get('V',''),host=e.get('AA',''),aliases=list(dict.fromkeys(v.strip() for x in a for v in [x.get('U',''),x.get('V','')] if v.strip() and v.strip()!=e.get('U','').strip()))))
assert len(rows)==17554 and len({r['id'] for r in rows})==17554
meta=dict(date='2026-11-20',msl='MSL41.v1 (2025 taxonomy, ratified 2026)',vmr='MSL41.v1.20260729',species=len(rows),families=len({r['family'] for r in rows if r['family']}),realms=len({r['realm'] for r in rows if r['realm']}),matched=sum(bool(r['name']) for r in rows),genomes=dict(collections.Counter(r['genome'] for r in rows)))
for name,data in [('taxonomy',rows),('meta',meta)]: (root/'dist'/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print(meta)
