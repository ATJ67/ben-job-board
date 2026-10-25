"""Reed.co.uk search within 20 miles of Bristol. Usage: reed.py out.json section:slug ..."""
import json, re, sys, time
sys.path.insert(0, '.')
from collect import get
out = sys.argv[1]; seen = {}
for arg in sys.argv[2:]:
    sec, slug = arg.split(':', 1)
    for page in (1, 2, 3):
        code, h = get(f"https://www.reed.co.uk/jobs/{slug}-jobs-in-bristol?proximity=20&pageno={page}")
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
        if not m: break
        jobs = json.loads(m.group(1))["props"]["pageProps"].get("searchResults", {}).get("jobs", [])
        for j in jobs:
            d = j["jobDetail"]
            v = seen.setdefault(d["jobId"], {"id": d["jobId"], "title": d["jobTitle"], "company": d["ouName"],
                "loc": d["displayLocationName"], "county": d.get("countyLocation"), "posted": d["dateCreated"][:10],
                "expires": d["expiryDate"][:10], "from": d.get("salaryFrom"), "to": d.get("salaryTo"),
                "mode": d.get("workingOption"), "agencyType": d.get("ouType"), "snippet": d["jobDescriptionSnippet"],
                "url": "https://www.reed.co.uk" + j["url"], "secs": []})
            if sec not in v["secs"]: v["secs"].append(sec)
        time.sleep(1)
        if len(jobs) < 25: break
json.dump(list(seen.values()), open(out, 'w'), indent=1)
print(len(seen))
