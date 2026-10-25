import json,sys,re,html,time
sys.path.insert(0,'.')
from collect import get, TITLE_BAD
kws=sys.argv[2:]
out=sys.argv[1]
seen={}
for kw in kws:
  for start in (0,25):
    q=f"keywords={kw.replace(' ','%20')}&location=Bristol%2C%20England%2C%20United%20Kingdom&distance=25&start={start}&f_TPR=r2592000"
    code,h=get(f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?{q}")
    time.sleep(1.2); n=0
    for card in h.split("<li>"):
      t=re.search(r'base-search-card__title">\s*(.*?)\s*</h3>',card,re.S); u=re.search(r'href="(https://[a-z.]*linkedin\.com/jobs/view/[^"?]+)',card)
      if not(t and u): continue
      n+=1
      c=re.search(r'base-search-card__subtitle">.*?>\s*(.*?)\s*</a>',card,re.S); l=re.search(r'job-search-card__location">\s*(.*?)\s*</span>',card,re.S); dt=re.search(r'datetime="([\d-]+)"',card)
      jid=re.search(r"(\d+)$",u.group(1)).group(1)
      seen.setdefault(jid,{"title":html.unescape(t.group(1).strip()),"company":html.unescape(re.sub("<[^>]+>","",c.group(1)).strip()) if c else "","location":html.unescape(l.group(1).strip()) if l else "","posted":dt.group(1) if dt else "","id":jid,"kw":kw})
    if n<20: break
json.dump(list(seen.values()),open(out,'w'),indent=1)
for v in sorted(seen.values(),key=lambda v:v['company']): print(v['title'],'|',v['company'],'|',v['location'],'|',v['posted'],'|',v['id'])
