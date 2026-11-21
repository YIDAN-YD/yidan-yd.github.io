"""Receive short-lived Sites service access over hidden stdin; never persist it."""
import json,sys,termios,urllib.request,urllib.error,ssl,certifi
old=termios.tcgetattr(sys.stdin);new=old.copy();new[3]&=~(termios.ECHO|termios.ICANON);termios.tcsetattr(sys.stdin,termios.TCSANOW,new)
print('Ready for hidden Site access JSON',flush=True)
try: cfg=json.loads(sys.stdin.readline())
finally: termios.tcsetattr(sys.stdin,termios.TCSANOW,old)
base=cfg['url'].rstrip('/')
assert base=='https://virus-atlas-bilingual-20261120.wangyidan-yd.chatgpt.site'
def call(path,data=None):
 headers={'OAI-Sites-Authorization':'Bearer '+cfg['token'],'Accept':'application/json'}
 if data is not None:
  headers['Content-Type']='application/json'
  headers['X-Atlas-Update-Key']=cfg['token']
 req=urllib.request.Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
 with urllib.request.urlopen(req,timeout=90,context=ssl.create_default_context(cafile=certifi.where())) as r:return json.load(r)
try:
 config=call('/update-instructions.json');print('Instructions revision:',config['version'],flush=True)
 result=call('/api/refresh-daily',{'id':'sars-cov-2'});print('Write:',json.dumps(result),flush=True)
 status=call('/api/daily-status');print('Readback profiles:',len(status.get('updates',[])),flush=True)
 papers=call('/api/papers?id=sars-cov-2');print('Papers delivery:',papers.get('delivery'),'count:',len(papers.get('items',[])),flush=True)
 if cfg.get('brief'):
  b=call('/api/store-briefs',{'papers':[cfg['brief']]});print('Brief write:',b,flush=True)
  b=call('/api/paper-brief?pmid='+cfg['brief']['pmid']);print('Brief readback:',b.get('status'),b.get('basis'),flush=True)
except urllib.error.HTTPError as e: print('HTTP failure:',e.code,e.read(1500).decode(errors='replace'));sys.exit(1)
except Exception as e: print('Failed:',type(e).__name__);sys.exit(1)
