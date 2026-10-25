import json,sys,re
d=json.load(open('pool.json'))
by={c['source'][0]+str(c['id']):c for c in d.values()}
for i in sys.argv[2:]:
  c=by.get(i)
  if not c: print("MISSING",i); continue
  desc=c.get('desc','')
  print(f"### {i} | {c['title']} | {c['company']} | {c['loc']} | {c['posted']} | {c.get('from','')}-{c.get('to','')} | {c.get('mode','')} | crit={c.get('criteria')}")
  print(desc[:int(sys.argv[1])])
  ex=set(m.group(0) for m in re.finditer(r'[^.]{0,80}(£\s?\d[\d,]*k?|salary|based|location|field|hybrid|office|territory|commission|OTE|days? in)[^.]{0,80}',desc,re.I))
  print("  >>", " || ".join(list(ex)[:6])[:900]); print()
