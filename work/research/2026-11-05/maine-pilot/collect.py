import asyncio,json,hashlib,datetime,pathlib,sys
from bc_web.search import Searcher, SearchQuery
from bc_web import Retriever
from bc_web.settings import BcWebSettings
p=pathlib.Path(__file__).parent
async def main():
 s=Searcher(BcWebSettings(search_throttle_retries=0))
 searches=[('exa','Peru Maine November 3 2026 Article 2 data center moratorium election results town warrant'),('serpapi','Peru Maine November 3 2026 Article 2 moratorium election results warrant'),('exa','Wells Maine November 3 2026 Article 5 data center moratorium election results'),('serpapi','Wells Maine November 3 2026 Article 5 data center moratorium results'),('exa','Wiscasset Maine November 3 2026 Question 2 data center election results town ballot'),('serpapi','Wiscasset Maine November 3 2026 question 2 data center election results town ballot')]
 records=[]
 for i,(backend,q) in enumerate(searches,1):
  try:
   x=await s.search(SearchQuery(query=q,backend=backend,max_results=10))
   (p/f'search-{i}.private.json').write_text(x.model_dump_json(indent=2))
   records.append({'n':i,'backend':backend,'query':q,'ok':True,'cost_usd':x.cost_usd,'hits':len(x.hits)})
   print(i,backend,'cost',x.cost_usd,[(h.title,h.url) for h in x.hits],flush=True)
  except Exception as e:
   records.append({'n':i,'backend':backend,'query':q,'ok':False,'error_type':type(e).__name__,'cost_usd':None})
   print(i,backend,'failed',type(e).__name__,flush=True)
  (p/'search-log.private.json').write_text(json.dumps(records,indent=2))
 await s.close()
asyncio.run(main())
