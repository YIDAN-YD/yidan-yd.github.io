"""Fetch public PubMed-indexed abstracts for grounded, original editorial paraphrases.
Raw abstracts remain a temporary working cache, never included in deployed assets.
"""
import json, pathlib, requests, concurrent.futures, re, html
ROOT=pathlib.Path(__file__).resolve().parent.parent
API='https://www.ebi.ac.uk/europepmc/webservices/rest/search'
def clean(s):return html.unescape(re.sub('<[^>]+>',' ',s or '')).strip()
def batch(ids):
 q='SRC:MED AND ('+' OR '.join('EXT_ID:'+i for i in ids)+')'
 r=requests.get(API,params={'query':q,'format':'json','resultType':'core','pageSize':100},timeout=25);r.raise_for_status()
 return {str(x['id']):{'title':clean(x.get('title')),'abstract':clean(x.get('abstractText')),'types':(x.get('pubTypeList') or {}).get('pubType',[]),'doi':x.get('doi'),'source':'https://pubmed.ncbi.nlm.nih.gov/'+str(x['id'])+'/'} for x in r.json().get('resultList',{}).get('result',[])}
if __name__=='__main__':
 lit=json.loads((ROOT/'dist/literature.json').read_text());ids=list(dict.fromkeys(str(p['pmid']) for v in lit['profiles'].values() for p in v['items']));out={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  fs=[pool.submit(batch,ids[i:i+25]) for i in range(0,len(ids),25)]
  for f in concurrent.futures.as_completed(fs):
   try:out.update(f.result())
   except Exception as e:print(type(e).__name__,flush=True)
   pathlib.Path('/tmp/virus-atlas-brief-abstracts.json').write_text(json.dumps(out,ensure_ascii=False))
 print('fetched',len(out),'abstracts',sum(bool(x['abstract']) for x in out.values()),flush=True)
