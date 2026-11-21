"""Five-year clinical/public-health title metadata. No abstracts or credentials."""
from pathlib import Path
import json,datetime,concurrent.futures,re
from fetch_literature import get,API,ALIASES,TOPICS,EXCLUDE,normalize,title_matches
root=Path(__file__).resolve().parent.parent
end=datetime.date(2026,11,20);start=end.replace(year=end.year-5)
literature=json.loads((root/'dist/literature.json').read_text())
def job(pair):
 ident,profile=pair;rows=[]
 for i in range(5):
  a=start.replace(year=start.year+i);b=end if i==4 else start.replace(year=start.year+i+1)-datetime.timedelta(days=1)
  q=re.sub(r'FIRST_PDATE:\[[^\]]+\]',f'FIRST_PDATE:[{a} TO {b}]',profile['query']);row={'from':str(a),'to':str(b),'query':q,'total':None,'items':[],'status':'error'}
  try:
   d,_=get(API,{'query':q,'format':'json','pageSize':40,'resultType':'lite'})
   records=[dict(normalize(x),publicationTypes=(x.get('pubTypeList') or {}).get('pubType') or ([x['pubType']] if isinstance(x.get('pubType'),str) else x.get('pubType',[]))) for x in d.get('resultList',{}).get('result',[]) if x.get('source')=='MED' and title_matches(x.get('title',''),profile['aliases'])]
   records=[x for x in records if str(a)<=x['date']<=str(b)]
   records.sort(key=lambda x:x['date'],reverse=True)
   row.update(total=d.get('hitCount',0),status='ok',items=[{k:x[k] for k in ['id','title','journal','date','doi','pmid','url','publicationTypes']} for x in records[:12]])
  except Exception as e:row['error']=type(e).__name__
  rows.append(row)
 items={x['pmid']:x for r in rows for x in r['items']}
 result={'checked':str(end),'window':{'from':str(start),'to':str(end)},'bins':rows,'items':sorted(items.values(),key=lambda x:x['date'],reverse=True),'status':'ok' if all(r['status']=='ok' for r in rows) else 'partial','source':'Europe PMC / PubMed'}
 print(ident,len(items),result['status'],flush=True);return ident,result
if __name__=='__main__':
 output=root/'dist/progress.json'
 try: previous=json.loads(output.read_text()).get('profiles',{})
 except (OSError,ValueError): previous={}
 profiles={k:v for k,v in previous.items() if v.get('checked')==str(end) and v.get('status')=='ok' and len(v.get('bins',[]))==5}
 pending=[p for p in literature['profiles'].items() if p[0] not in profiles]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for future in concurrent.futures.as_completed([pool.submit(job,p) for p in pending]):
   key,value=future.result();profiles[key]=value
   temporary=output.with_suffix('.tmp')
   temporary.write_text(json.dumps({'checked':str(end),'profiles':profiles},ensure_ascii=False,separators=(',',':')))
   temporary.replace(output)
 print('DONE',len(profiles),sum(len(x['items']) for x in profiles.values()),flush=True)
