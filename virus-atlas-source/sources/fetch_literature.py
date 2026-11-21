"""Reproducible metadata-only Europe PMC clinical literature snapshot.
No institutional credentials, cookies, abstracts or full text are stored.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,time,re,urllib.request,urllib.parse,datetime,requests
ROOT=Path(__file__).resolve().parent.parent
CHECKED='2026-11-20'
START='2024-01-01'
API='https://www.ebi.ac.uk/europepmc/webservices/rest/search'
ALIASES={
'sars-cov-2':['SARS-CoV-2','COVID-19'], 'influenza':['influenza'],
'rsv':['respiratory syncytial virus'], 'hmpv':['human metapneumovirus'], 'rhinovirus':['rhinovirus'],
'adenovirus':['human adenovirus','adenovirus infection'], 'measles':['measles'], 'mumps':['mumps'], 'rubella':['rubella'],
'vzv':['varicella','herpes zoster'], 'hsv':['herpes simplex'], 'ebv':['Epstein-Barr virus'], 'cmv':['cytomegalovirus'],
'hpv':['human papillomavirus'], 'b19':['parvovirus B19'], 'hav':['hepatitis A'], 'hbv':['hepatitis B'],
'hcv':['hepatitis C'], 'hdv':['hepatitis D','hepatitis delta'], 'hev':['hepatitis E'],
'hiv':['HIV','human immunodeficiency virus'], 'htlv1':['HTLV-1','human T-lymphotropic virus'],
'norovirus':['norovirus'], 'rotavirus':['rotavirus'], 'polio':['poliovirus','poliomyelitis'],
'eva71':['enterovirus A71','enterovirus 71','EV-A71'], 'dengue':['dengue'], 'zika':['Zika'],
'chikungunya':['chikungunya'], 'jev':['Japanese encephalitis'], 'rabies':['rabies'], 'ebola':['Ebola','Sudan virus','Bundibugyo virus'],
'marburg':['Marburg virus','Marburg disease'], 'nipah':['Nipah'], 'mpox':['mpox','monkeypox'],
'yellow-fever':['yellow fever'], 'west-nile':['West Nile'], 'hantavirus':['hantavirus','hantaviral','hemorrhagic fever with renal syndrome']}
TOPICS='(TITLE:epidemiolog* OR TITLE:clinical OR TITLE:vaccin* OR TITLE:treatment OR TITLE:therap* OR TITLE:diagnos* OR TITLE:surveillance OR TITLE:prevention OR TITLE:burden OR TITLE:outbreak OR TITLE:trial OR PUB_TYPE:review OR PUB_TYPE:"systematic review")'
EXCLUDE='NOT (TITLE:"gain of function" OR TITLE:"reverse genetics" OR TITLE:"host range" OR TITLE:engineer* OR TITLE:mutagenesis OR TITLE:pseudotyp* OR TITLE:"viral entry" OR TITLE:"spike mutation" OR TITLE:"receptor binding" OR TITLE:corrigendum OR TITLE:erratum OR TITLE:retraction OR TITLE:pandemic)'
def get(url,params=None):
 headers={'User-Agent':'VirusAtlasMetadata/2.0 (educational metadata retrieval)','Origin':'https://virus-atlas-bilingual-20261120.wangyidan-yd.chatgpt.site'}
 for retry in range(2):
  try:
   r=requests.get(url,params=params,headers=headers,timeout=35)
   r.raise_for_status()
   return r.json(),dict(r.headers)
  except Exception:
   if retry:raise
   time.sleep(2)
def query_for(aliases):
 # Titles provide a conservative association; content not mentioning the virus in its title is outside this snapshot.
 return '('+' OR '.join('TITLE:"'+x.replace('"','')+'"' for x in aliases)+') AND SRC:MED AND FIRST_PDATE:['+START+' TO '+CHECKED+'] AND '+TOPICS+' '+EXCLUDE+' sort_date:y'
def normalize(r):
 ji=r.get('journalInfo') or {};j=ji.get('journal') or {};pmid=r.get('id') if r.get('source')=='MED' else None
 return {'id':r.get('source','')+':'+str(r.get('id','')),'title':r.get('title',''),'authors':r.get('authorString',''),'journal':j.get('title') or ji.get('journalIssueId') or r.get('journalTitle',''),'year':str(r.get('pubYear') or ji.get('yearOfPublication') or ''),'date':r.get('firstPublicationDate',''),'doi':r.get('doi'),'pmid':pmid,'pmcid':r.get('pmcid'),'url':('https://pubmed.ncbi.nlm.nih.gov/'+str(pmid)+'/') if pmid else 'https://europepmc.org/article/'+r.get('source','MED')+'/'+str(r.get('id','')),'oa':r.get('isOpenAccess')=='Y','publicationTypes':(r.get('pubTypeList') or {}).get('pubType',[]),'source':'Europe PMC / PubMed','reviewStatus':'metadata-only; not individually critically appraised'}
def title_matches(title,aliases):
 if re.search(r"reverse.genetic|gain.of.function|host.range|pseudotyp|viral.entry|receptor.bind|mutagen|engineer|vector.construct|optimized.*protein|protein.*optimiz|replicon|infectious.clone|recombinant.*construct|virus.rescue|molecular.clon|cell.entry",title,re.I):return False
 title=title.lower().replace('–','-').replace('—','-').replace('‐','-')
 for alias in aliases:
  a=alias.lower().replace('–','-').replace('—','-')
  pattern=r'(?<![a-z0-9])'+re.escape(a).replace(r'\ ',r'\s+')+r'(?:es|s)?(?![a-z0-9])'
  if re.search(pattern,title):return True
 return False
def fetch_one(pair):
 ident,aliases=pair;q=query_for(aliases)
 if ident=='influenza':q=q.replace(' sort_date:y',' AND NOT (TITLE:avian OR TITLE:swine OR TITLE:poultry OR TITLE:chicken* OR TITLE:piglet* OR TITLE:mice OR TITLE:mouse OR TITLE:murine) sort_date:y')
 if ident=='hav':q=q.replace(' sort_date:y',' AND NOT (TITLE:autoimmune OR TITLE:"hepatitis B" OR TITLE:"hepatitis C" OR TITLE:"hepatitis D" OR TITLE:"hepatitis E") sort_date:y')
 try:
  d,h=get(API,{'query':q,'format':'json','resultType':'core','pageSize':100 if ident in ['hav','influenza'] else 30})
  items=[];seen=set()
  for r in d.get('resultList',{}).get('result',[]):
   n=normalize(r)
   if not n['title'] or not n['pmid'] or not title_matches(n['title'],aliases):continue
   if n['date'] and n['date']>CHECKED:continue
   key=n['doi'] or n['id']
   if key in seen:continue
   seen.add(key);items.append(n)
  items.sort(key=lambda x:(x['date'],x['id']),reverse=True)
  return ident,{'query':q,'aliases':aliases,'terms':aliases,'total':d.get('hitCount',0),'items':items[:8],'checked':CHECKED,'status':'ok' if items else 'no-matching-records','titleAssociationScreened':True,'searchUrl':'https://europepmc.org/search?query='+urllib.parse.quote(q),'cors':h.get('access-control-allow-origin') or h.get('Access-Control-Allow-Origin')}
 except Exception as e:return ident,{'query':q,'aliases':aliases,'terms':aliases,'total':None,'items':[],'checked':CHECKED,'status':'error','error':type(e).__name__+': '+str(e)[:200]}
def main():
 profiles={};audit={'checked':CHECKED,'window':[START,CHECKED],'protocol':'Title-associated PubMed records in Europe PMC. Clinical/public-health topic filter; metadata only; date-sorted; not exhaustive, and PubMed indexing alone is not a peer-review or quality guarantee.','requests':[],'crossrefVerification':[]}
 with ThreadPoolExecutor(max_workers=3) as pool:
  futures=[pool.submit(fetch_one,p) for p in ALIASES.items()]
  for f in as_completed(futures):
   ident,res=f.result();profiles[ident]=res;audit['requests'].append({'profile':ident,'status':res['status'],'query':res['query'],'total':res['total'],'selected':len(res['items']),'error':res.get('error')});print(ident,res['status'],len(res['items']),res['total'],flush=True)
   (ROOT/'dist/literature.json').write_text(json.dumps({'checked':CHECKED,'profiles':profiles},ensure_ascii=False,indent=2))
 # Independent bibliographic check; no abstracts, passwords or proxy URLs.
 for ident in ['sars-cov-2','rsv','hiv']:
  item=next((x for x in profiles.get(ident,{}).get('items',[]) if x.get('doi')),None)
  if not item:continue
  try:
   d,_=get('https://api.crossref.org/works/'+urllib.parse.quote(item['doi'],safe=''));m=d['message'];title=' '.join(m.get('title',[]));norm=lambda s:re.sub(r'[^a-z0-9]','',s.lower())
   audit['crossrefVerification'].append({'profile':ident,'doi':item['doi'],'europepmcTitle':item['title'],'crossrefTitle':title,'match':norm(title)==norm(item['title']),'crossrefUrl':'https://api.crossref.org/works/'+urllib.parse.quote(item['doi'],safe='')})
  except Exception as e:audit['crossrefVerification'].append({'profile':ident,'doi':item['doi'],'error':str(e)[:160]})
 out={'checked':CHECKED,'window':[START,CHECKED],'scope':{'zh':'按病毒名称与临床／公共卫生主题检索的近期论文元数据；每条最多8篇，按数据库首次发表日期降序。不是全部论文、系统综述或逐篇质量评价。','en':'Recent title-associated clinical/public-health publication metadata, up to eight records per profile, sorted by database first-publication date. Not an exhaustive search, systematic review or critical appraisal.'},'api':{'endpoint':API,'documentation':'https://europepmc.org/RestfulWebService','format':'json','resultType':'core','source':'MED','sort':'sort_date:y','dateField':'FIRST_PDATE','corsObserved':list(set(x.get('cors') for x in profiles.values() if x.get('cors')))},'profiles':{k:profiles[k] for k in ALIASES}}
 (ROOT/'dist/literature.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));(ROOT/'sources/literature-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
 print('DONE',sum(len(p['items']) for p in profiles.values()),'records',len(profiles),'profiles',flush=True)
if __name__=='__main__':main()
