import asyncio,json,pathlib,hashlib,sys
from bc_web import Retriever
from bc_web.models import FetchRequest
p=pathlib.Path(__file__).parent
urls=[('wells-warrant','https://wellstown.org/DocumentCenter/View/8514/November-3-2026-Special-Town-Meeting-Warrant?bidId=',None),('wells-results','https://www.wellstown.org/DocumentCenter/View/8559/November-3-2026-Official-Election-Results?bidId=',None),('wells-ordinance','https://www.wellstown.org/AgendaCenter/ViewFile/Item/6565?fileID=16871',None),('peru-town','https://townofperumaine.org/temporary-moratorium-of-the-development-and-permitting-of-data-centers-to-be-on-the-november-2026-ballot/',None),('peru-elections','https://townofperumaine.org/category/elections/',None),('wiscasset-results','https://www.wiscasset.gov/m/newsflash/Home/Detail/211','pydoll'),('wiscasset-ballotpedia','https://ballotpedia.org/Wiscasset,_Maine,_Question_2,_Data_Center_Moratorium_Measure_(November_2026)',None),('peru-ballotpedia','https://ballotpedia.org/Peru,_Maine,_Article_2,_Moratorium_on_Data_Center_Development_and_Permitting_Measure_(November_2026)',None)]
async def main():
 log=[]
 async with Retriever() as r:
  for name,url,eng in urls:
   try:
    kw={'url':url,'timeout_ms':25000}
    if eng: kw.update(engine=eng,mode='browser')
    else: kw.update(mode='http')
    x=await r.fetch(FetchRequest(**kw))
    data=x.raw if x.raw is not None else x.html.encode()
    suffix='pdf' if data.startswith(b'%PDF') else 'html'
    (p/f'{name}.private.{suffix}').write_bytes(data)
    (p/f'{name}.private.json').write_text(json.dumps(x.to_json_dict(include_html=False),indent=2,default=str))
    z={'name':name,'url':url,'status':x.status,'ok':x.ok,'engine':x.engine,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'artifact':f'{name}.private.{suffix}','error':x.error,'final_url':x.final_url}
   except Exception as e: z={'name':name,'url':url,'error_type':type(e).__name__}
   log.append(z); (p/'fetch-log.private.json').write_text(json.dumps(log,indent=2)); print(z,flush=True)
asyncio.run(main())
