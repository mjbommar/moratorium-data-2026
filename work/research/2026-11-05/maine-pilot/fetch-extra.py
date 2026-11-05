import asyncio,json,pathlib,hashlib
from bc_web import Retriever
from bc_web.models import FetchRequest
p=pathlib.Path(__file__).parent
urls=[('peru-ordinance','https://townofperumaine.org/wp-content/uploads/2026/09/Temporary-Moratorium-of-the-Development-and-Permitting-of-Data-Centers.pdf'),('wiscasset-guide','https://www.wiscasset.gov/DocumentCenter/View/1735/Special-Town-Meeting-Voter-Guide---November-3-2026'),('peru-news','https://www.sunjournal.com/2026/11/03/peru-backs-food-sovereignty-data-center-ballot-questions/')]
async def main():
 async with Retriever() as r:
  for name,url in urls:
   try:
    x=await r.fetch(FetchRequest(url=url,mode='http',timeout_ms=25000)); data=x.raw if x.raw is not None else x.html.encode(); suf='pdf' if data.startswith(b'%PDF') else 'html'; (p/f'{name}.private.{suf}').write_bytes(data); (p/f'{name}.private.json').write_text(json.dumps(x.to_json_dict(include_html=False),indent=2,default=str)); z={'name':name,'url':url,'status':x.status,'ok':x.ok,'engine':x.engine,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'artifact':f'{name}.private.{suf}','error':x.error,'final_url':x.final_url}
   except Exception as e: z={'name':name,'url':url,'error_type':type(e).__name__}
   a=json.loads((p/'fetch-log.private.json').read_text()); a.append(z); (p/'fetch-log.private.json').write_text(json.dumps(a,indent=2)); print(z,flush=True)
asyncio.run(main())
