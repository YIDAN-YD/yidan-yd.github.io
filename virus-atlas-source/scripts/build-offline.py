from pathlib import Path
import json,re
root=Path(__file__).resolve().parent.parent
dist=root/'dist'
html=re.sub(r'\?v=[0-9.]+','',(dist/'index.html').read_text())
for name in ['atlas-extras.css','styles.css','taxonomy-tree.css','research-tracker.css','research-observatory.css']:
 html=html.replace('<link rel="stylesheet" href="'+name+'">','<style>'+ (dist/name).read_text()+'</style>')
for name in ['atlas-extras.js','taxonomy-tree.js','research-tracker.js','research-observatory.js','app.js']:
 html=re.sub(r'<script[^>]*src="'+re.escape(name)+r'"[^>]*></script>','',html)
names=['profiles','taxonomy','meta','literature','research','news','progress','care','gaps']
data=[json.loads((dist/(name+'.json')).read_text()) for name in names]
extras=[json.loads((dist/(name+'.json')).read_text()) for name in ['viralzone-links','host-context','paper-briefs','receptor-evidence']]
js='window.ATLAS_EXTRAS='+json.dumps(extras,ensure_ascii=False)+';window.ATLAS_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n'+'\n'.join((dist/name).read_text() for name in ['atlas-extras.js','taxonomy-tree.js','research-tracker.js','research-observatory.js','app.js'])
html=html.replace('</body>','<script>'+js.replace('</script','<\\/script')+'</script></body>')
out=root.parent/'病毒图谱-离线版.html';out.write_text(html);print(out)
