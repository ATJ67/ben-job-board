"""Fetch descriptions for sales/buyer-titled candidates from reed.json + candidates.json (+food2.json). Writes pool.json."""
import json, re, sys, time
sys.path.insert(0, '.')
from collect import get, text, li_detail
BAD = re.compile(r'telesales|\bsdr\b|\bbdr\b|door|commission only|recruitment consultant|resourcer|apprentice|graduate|placement|intern\b|store|shop|retail sales|sales assistant|associate|advisor|adviser|customer service|engineer|driver|warehouse|chef|director|head of|lettings|estate agent|mortgage|telemarket|appointment|canvass|coordinator|co-ordinator|administrator|admin|support|analyst|accountant|ledger|scout|kitchen sales|sales designer|team member|promotional|sales consultant|quantity surveyor|stores officer|paralegal', re.I)
SALES = re.compile(r'sales|account manager|account executive|business development|territory|key account|national account|customer development|trade (development|client|account)|\bbdm\b|\bkam\b|area (sales|business) manager|business manager|account lead|client manager|relationship manager', re.I)
BUY = re.compile(r'buyer|buying|purchas|procure|category (manager|exec|controller|buyer)|sourcing|commercial manager|trader', re.I)
pool = {}
for c in json.load(open('reed.json')):
    if BAD.search(c['title']) or not (SALES.search(c['title']) or BUY.search(c['title'])): continue
    pool[c['url']] = dict(c, source='reed')
li = json.load(open('candidates.json'))['candidates'] + [dict(v, url="https://uk.linkedin.com/jobs/view/" + v['id']) for v in json.load(open('food2.json'))]
for c in li:
    if BAD.search(c['title']) or not (SALES.search(c['title']) or BUY.search(c['title'])): continue
    jid = re.search(r'(\d+)/?$', c['url']).group(1)
    pool.setdefault("li:" + jid, {"id": jid, "title": c['title'], "company": c['company'], "loc": c['location'],
        "posted": c['posted'], "url": "https://uk.linkedin.com/jobs/view/" + jid, "source": "linkedin"})
print(len(pool), flush=True)
try: done = json.load(open('pool.json'))
except Exception: done = {}
from concurrent.futures import ThreadPoolExecutor
def reed_one(kc):
    k, c = kc
    code, h = get(c['url'])
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    try:
        jd = json.loads(m.group(1))["props"]["pageProps"]["consolidatedJobDetails"]
        c['desc'] = text(jd["jobDetails"].get("description", ""))[:3500]
        c['live'] = jd.get("gaTags", {}).get("jobLiveStatus")
        c['recType'] = jd.get("gaTags", {}).get("jobRecruiterType")
    except Exception:
        c['desc'] = ''
    time.sleep(1.5); return k, c
todo = [(k, c) for k, c in pool.items() if c['source'] == 'reed' and not (k in done and done[k].get('desc'))]
with ThreadPoolExecutor(1) as ex:
    for k, c in ex.map(reed_one, todo): done[k] = c
json.dump(done, open('pool.json', 'w'), indent=1); print('reed done', len(done), flush=True)
for k, c in pool.items():
    if k in done and done[k].get('desc'): continue
    if c['source'] == 'reed':
        code, h = get(c['url'])
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
        try:
            jd = json.loads(m.group(1))["props"]["pageProps"]["consolidatedJobDetails"]
            c['desc'] = text(jd["jobDetails"].get("description", ""))[:3500]
            c['live'] = jd.get("gaTags", {}).get("jobLiveStatus")
            c['recType'] = jd.get("gaTags", {}).get("jobRecruiterType")
        except Exception:
            c['desc'] = ''
        time.sleep(0.8)
    else:
        d = li_detail(c['id'])
        c['desc'] = d.get('description', ''); c['closed'] = d.get('closed'); c['criteria'] = d.get('criteria')
        time.sleep(2.5)
    done[k] = c
    if len(done) % 20 == 0:
        json.dump(done, open('pool.json', 'w'), indent=1); print(len(done), flush=True)
json.dump(done, open('pool.json', 'w'), indent=1)
print("done", len(done))
