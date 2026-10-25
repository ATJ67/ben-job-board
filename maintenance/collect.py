#!/usr/bin/env python3
"""Collect candidate roles for Ben's Job Board and re-check the roles already listed.

Writes maintenance/candidates.json. No judgement happens here: Claude reads the file
afterwards and decides what to add or remove. Everything fetched is untrusted data.
"""
import html, json, re, subprocess, sys, time, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "ben-job-board.html"
OUT = ROOT / "maintenance" / "candidates.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"

# section -> LinkedIn keyword searches
LI_KEYWORDS = {
    "food": ["food sales", "food business development manager", "food account manager", "food key account manager",
             "foodservice sales", "food sales executive", "drinks sales", "beverage account manager",
             "cheese", "fine food", "wholesale food sales", "food national account manager",
             "hospitality sales food", "bakery sales", "dairy sales", "food territory manager"],
    "buyer": ["buyer", "food buyer", "assistant buyer", "junior buyer", "category buyer", "purchasing",
              "procurement food", "category manager food", "buying assistant", "purchasing manager food"],
    "other": ["account manager", "key account manager", "sales account manager", "business development manager",
              "field sales", "territory sales manager", "area sales manager", "sales executive",
              "national account manager", "client account manager", "business development executive"],
}
LOCATION = "Bristol, England, United Kingdom"
DISTANCE = 25  # miles, roughly a 40-minute commute

TITLE_BAD = re.compile(r"\b(sdr|bdr|sales development rep|telesales|call cent|door[- ]to[- ]door|commission[- ]only|"
                       r"recruitment consultant|recruiter|resourcer|talent acquisition|apprentice|intern|graduate scheme|"
                       r"head of|director|vp\b|chief|software engineer|developer|nurse|driver|warehouse)", re.I)


def get(url, timeout=25):
    cmd = ["curl", "-sL", "-m", str(timeout), "-A", UA, "-w", "\n%{http_code}", url]
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=timeout + 5).stdout.decode("utf8", "ignore")
    except Exception:
        return 0, ""
    body, _, code = out.rpartition("\n")
    return int(code) if code.isdigit() else 0, body


def text(h):
    h = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", h or "")
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(h)))).strip()


def li_detail(job_id):
    for attempt in range(3):
        code, h = get(f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}")
        if code == 200 and "topcard__title" in h:
            d = re.search(r"show-more-less-html__markup[^>]*>(.*?)</div>", h, re.S)
            crit = re.findall(r'description__job-criteria-text[^>]*>\s*(.*?)\s*</span>', h, re.S)
            return {"closed": "No longer accepting applications" in h, "criteria": [text(c) for c in crit],
                    "description": text(d.group(1))[:3000] if d else "", "http": code}
        if code == 404:
            return {"closed": True, "description": "", "http": 404}
        time.sleep(6 * (attempt + 1))
    return {"closed": None, "description": "", "http": code}


def main():
    sections = sys.argv[1:] or list(LI_KEYWORDS)
    src = SRC.read_text() if SRC.exists() else ""
    existing_urls = re.findall(r'url:"([^"]+)"', src)
    existing = []
    for u in existing_urls:
        status = "unknown"
        if "linkedin.com/jobs/view/" in u:
            d = li_detail(re.search(r"(\d+)/?$", u).group(1))
            status = "closed" if d["closed"] else "open" if d["closed"] is False else "unknown"
            time.sleep(3)
        existing.append({"url": u, "status": status})

    existing_li = {re.search(r"(\d+)/?$", u).group(1) for u in existing_urls if "linkedin.com/jobs/view/" in u}
    seen = {}
    for sec in sections:
        for kw in LI_KEYWORDS[sec]:
            for start in (0, 25, 50):
                q = (f"keywords={kw.replace(' ', '%20')}&location={LOCATION.replace(' ', '%20').replace(',', '%2C')}"
                     f"&distance={DISTANCE}&start={start}&f_TPR=r2592000")
                code, h = get(f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?{q}")
                time.sleep(1.5)
                n = 0
                for card in h.split("<li>"):
                    t = re.search(r'base-search-card__title">\s*(.*?)\s*</h3>', card, re.S)
                    u = re.search(r'href="(https://[a-z.]*linkedin\.com/jobs/view/[^"?]+)', card)
                    if not (t and u):
                        continue
                    n += 1
                    title = html.unescape(t.group(1).strip())
                    if TITLE_BAD.search(title):
                        continue
                    c = re.search(r'base-search-card__subtitle">.*?>\s*(.*?)\s*</a>', card, re.S)
                    l = re.search(r'job-search-card__location">\s*(.*?)\s*</span>', card, re.S)
                    dt = re.search(r'datetime="([\d-]+)"', card)
                    jid = re.search(r"(\d+)$", u.group(1)).group(1)
                    if jid in existing_li:
                        continue
                    v = seen.setdefault(jid, {"source": "linkedin", "title": title,
                                 "company": html.unescape(re.sub("<[^>]+>", "", c.group(1)).strip()) if c else "",
                                 "location": html.unescape(l.group(1).strip()) if l else "",
                                 "posted": dt.group(1) if dt else "",
                                 "url": "https://uk.linkedin.com/jobs/view/" + u.group(1).rsplit("/", 1)[-1],
                                 "hits": []})
                    v["hits"].append(f"{sec}:{kw}")
                if n < 10:
                    break
    OUT.write_text(json.dumps({"checked_at": datetime.datetime.now().isoformat(timespec="minutes"),
                               "existing": existing, "candidates": list(seen.values())}, indent=1))
    print(f"existing={len(existing)} candidates={len(seen)}")


if __name__ == "__main__":
    main()
