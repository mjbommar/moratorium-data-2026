import asyncio,json,pathlib
from bc_web.search import Searcher,SearchQuery
from bc_web.settings import BcWebSettings
p=pathlib.Path(__file__).parent
async def main():
 s=Searcher(BcWebSettings(search_throttle_retries=0))
 for i,b,q in [(7,'exa','site:wiscasset.gov November 3 2026 town warrant question 2 data center moratorium'),(8,'serpapi','site:townofperumaine.org "2026" "election" results November moratorium')]:
  try:
   x=await s.search(SearchQuery(query=q,backend=b,max_results=10)); (p/f'search-{i}.private.json').write_text(x.model_dump_json(indent=2)); z={'n':i,'backend':b,'query':q,'ok':True,'cost_usd':x.cost_usd,'hits':len(x.hits)}; print(i,[(h.title,h.url) for h in x.hits],flush=True)
  except Exception as e: z={'n':i,'backend':b,'query':q,'ok':False,'cost_usd':None,'error_type':type(e).__name__}; print(z,flush=True)
  a=json.loads((p/'search-log.private.json').read_text()); a.append(z); (p/'search-log.private.json').write_text(json.dumps(a,indent=2))
 await s.close()
asyncio.run(main())
