import json,re,sys
d=json.load(open('reed.json'))
BAD=re.compile(r'telesales|\bsdr\b|\bbdr\b|door|commission only|recruitment consultant|resourcer|apprentice|graduate|intern\b|store|shop|retail sales|sales assistant|advisor|adviser|customer service|engineer|driver|warehouse|chef|director|head of|internal sales|inside sales|lettings|estate agent|mortgage|insurance|holiday|telemarket|appointment|canvass|coordinator|co-ordinator|administrator|support|analyst|accountant|ledger',re.I)
SALES=re.compile(r'sales|account manager|account executive|business development|territory|key account|national account|customer development|trade|account director|\bbdm\b|\bkam\b|area manager',re.I)
BUY=re.compile(r'buyer|buying|purchas|procure|category (manager|exec|controller)|sourcing',re.I)
F=re.compile(r'\bfood|cheese|dairy|drink|beverage|wine|beer|brew|spirit|coffee|fmcg|grocery|catering|bakery|meat|fresh produce|confection|snack|chilled|frozen|foodservice|\bdeli\b|ingredient',re.I)
mode=sys.argv[1]
for c in sorted(d,key=lambda c:c['company']):
  t=c['title']
  if BAD.search(t): continue
  food=bool(F.search(t+' '+c['snippet']+' '+c['company']))
  if mode=='foodsales' and not(food and SALES.search(t)): continue
  if mode=='buyer' and not BUY.search(t): continue
  if mode=='other' and not(SALES.search(t) and not food): continue
  print(t,'|',c['company'],'|',c['loc'],'|',c['posted'],'|',c['from'],c['to'],'|',c['mode'],'|',c['id'],'|',c['snippet'][:110] if mode!='other' else '')
