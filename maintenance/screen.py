import json,re,sys
d=json.load(open('pool.json'))
F=re.compile(r'\bfood|cheese|dairy|\bdrinks?\b|beverage|\bwines?\b|\bbeers?\b|brewer|spirits|coffee|fmcg|grocer|catering|bakery|\bmeat\b|fresh produce|confection|snack|chilled|frozen|foodservice|\bdeli\b|ingredient|on-trade|off-trade|wholesal|cider|ice cream|nutrition',re.I)
BUY=re.compile(r'buyer|buying|purchas|procure|category|sourcing|trader',re.I)
mode=sys.argv[1]
rows=[]
for k,c in d.items():
  if c.get('closed') or c.get('live') not in (None,'Live'): continue
  txt=c['title']+' '+c['company']+' '+c.get('desc','')
  n=len(F.findall(txt)); isbuy=bool(BUY.search(c['title']))
  if mode=='food' and (isbuy or n<3): continue
  if mode=='buyer' and not isbuy: continue
  if mode=='other' and (isbuy or n>=3): continue
  rows.append((c['company'],n,c))
for co,n,c in sorted(rows,key=lambda r:r[0]):
  print(f"[{n}] {c['title']} | {c['company']} | {c['loc']} | {c['posted']} | {c.get('from','')}-{c.get('to','')} | {c.get('mode','')} | {c['source']}:{c['id']}")
  if len(sys.argv)>2: print("     ",c.get('desc','')[:int(sys.argv[2])])
