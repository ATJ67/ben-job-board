#!/bin/zsh
# Builds index.html (the GitHub Pages page) from ben-job-board.html (the artifact-style source).
cd "${0:A:h}"
{
  printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex">\n'
  sed -n '1,/^<\/style>/p' ben-job-board.html
  printf '</head>\n<body>\n'
  sed -n '/^<\/style>/,$p' ben-job-board.html | sed 1d
  printf '</body>\n</html>\n'
} > index.html
# Sanity check: the data script must still parse.
python3 - <<'PY'
import re,sys,subprocess
h=open('index.html').read()
js=re.search(r'<script>([\s\S]*)</script>',h).group(1)
open('/tmp/bjb-check.js','w').write("const document={getElementById(){return{addEventListener(){},set innerHTML(v){},set textContent(v){},checked:false,value:''}},querySelectorAll(){return[]},addEventListener(){}};const localStorage={getItem(){return null},setItem(){}};"+js+"\nconsole.log('OK',ROLES.length)")
PY
if command -v node >/dev/null; then node /tmp/bjb-check.js || { echo "BUILD CHECK FAILED"; exit 1; }; fi
