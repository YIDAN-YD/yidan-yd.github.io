import re,json,pathlib,requests,concurrent.futures,xml.etree.ElementTree as E,email.utils,datetime,urllib.parse,time
root=pathlib.Path(__file__).resolve().parent.parent
papers=json.loads((root/'dist/literature.json').read_text());profiles=json.loads((root/'dist/profiles.json').read_text())
hosts=['who.int','cdc.gov','nih.gov','ecdc.europa.eu','reuters.com']
sites='(site:who.int OR site:cdc.gov OR site:nih.gov/news-events OR site:ecdc.europa.eu OR site:reuters.com)'
def job(p):
 aliases=papers['profiles'].get(p['id'],{}).get('aliases',[p['en']])[:2]
 q='('+' OR '.join('"'+a.replace('"','')+'"' for a in aliases)+') when:90d'
 d={'query':q,'checked':'2026-11-20','items':[],'status':'ok','source':'Google News RSS · selected sources'}
 try:
  r=requests.get('https://news.google.com/rss/search',params={'q':q,'hl':'en-US','gl':'US','ceid':'US:en'},timeout=20);r.raise_for_status()
  for x in E.fromstring(r.content).findall('.//item'):
   se=x.find('source');su=se.get('url','') if se is not None else '';host=urllib.parse.urlparse(su).hostname or ''
   if not any(host==h or host.endswith('.'+h) for h in hosts):continue
   title=x.findtext('title') or '';norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
   names=aliases+(['COVID','COVID-19'] if p['id']=='sars-cov-2' else [])
   if not any(norm(a) in norm(title) for a in names):continue
   date=email.utils.parsedate_to_datetime(x.findtext('pubDate')).isoformat()
   if date[:10]>'2026-11-20' or date[:10]<'2026-08-22':continue
   d['items'].append({'title':x.findtext('title'),'url':x.findtext('link'),'source':x.findtext('source'),'sourceUrl':su,'date':date,'kind':'news','linkType':'Google News indexed link'})
  d['items']=sorted({x['title']:x for x in d['items']}.values(),key=lambda x:x['date'],reverse=True)[:8]
 except Exception as e:d.update(status='error',error=type(e).__name__)
 return p['id'],d
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=dict(ex.map(job,profiles))
(root/'dist/news.json').write_text(json.dumps({'checked':'2026-11-20','scope':'Selected-source news index; titles/links only, not verified scientific findings','profiles':rows},ensure_ascii=False,separators=(',',':')))
print('News profiles:',len(rows),'items:',sum(len(v['items']) for v in rows.values()),'errors:',[k for k,v in rows.items() if v['status']=='error'])
