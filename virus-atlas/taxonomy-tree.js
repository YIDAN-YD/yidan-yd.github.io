/* ICTV rank navigation: areas encode species counts, never evolutionary distance. */
(function () {
  'use strict';
  const RANKS=[['realm','域','Realm'],['kingdom','界','Kingdom'],['phylum','门','Phylum'],['class_name','纲','Class'],['order','目','Order'],['family','科','Family'],['genus','属','Genus']];
  const COLORS=['#0d8279','#3faaa0','#6dbaa6','#91cdb7','#366d7a','#668eaa','#a4bbc9','#76a391','#b3c68d','#517e73','#acb4b8'];
  const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=n=>n.toLocaleString('en-US');
  function buildTree(records){
    const root={key:'root',name:'全部已分类物种',en:'All indexed species',rank:-1,parent:null,count:0,children:new Map()};
    const nodes=[root];
    for(const row of records){let n=root;n.count++;
      for(let rank=0;rank<RANKS.length;rank++){
        const name=row[RANKS[rank][0]]||'',key=n.key+'\u001f'+rank+':'+name;
        if(!n.children.has(name)){const child={key,name:name||'未分配'+RANKS[rank][1],en:name||'Unassigned '+RANKS[rank][2].toLowerCase(),unassigned:!name,rank,parent:n,count:0,children:new Map()};n.children.set(name,child);nodes.push(child);}
        n=n.children.get(name);n.count++;
      }
      const leaf={key:row.id,name:row.species,en:row.species,rank:7,parent:n,count:1,record:row,children:new Map()};n.children.set(row.id,leaf);nodes.push(leaf);
    }
    return {root,nodes};
  }
  function collectLeaves(node,out=[]){if(node.record)out.push(node);else for(const child of node.children.values())collectLeaves(child,out);return out;}
  function point(r,a){return [260+r*Math.cos(a),260+r*Math.sin(a)];}
  function arc(a,b){const gap=Math.min(.011,(b-a)*.08),start=a+gap,end=b-gap;const p=point(201,start),q=point(201,end),r=point(127,end),s=point(127,start),large=end-start>Math.PI?1:0;return `M${p} A201 201 0 ${large} 1 ${q} L${r} A127 127 0 ${large} 0 ${s} Z`;}
  window.initTaxonomyMap=function(records,callbacks={}){
    const mount=document.getElementById('taxonomy-map');if(!mount)return;
    const {root,nodes}=buildTree(records),byKey=new Map(nodes.map(n=>[n.key,n]));let current=root,mode='children',query='',page=0,searchResults=[];
    const searchNodes=nodes.slice(1).filter(n=>!n.unassigned).map(n=>({n,text:(n.name+' '+(n.record?[n.record.name,n.record.abbr,...(n.record.aliases||[])].join(' '):'')).toLowerCase()}));
    mount.innerHTML=`<div class="map-heading"><div><div class="eyebrow">EXPLORE THE VIRAL WORLD</div><h2>点击分类，探索病毒世界</h2><p>域 → 界 → 门 → 纲 → 目 → 科 → 属 → 物种<span class="en">Realm → Kingdom → Phylum → Class → Order → Family → Genus → Species</span></p></div><span class="map-release">ICTV MSL41 · ${fmt(records.length)} species</span></div><div class="map-shell"><div class="map-controls"><label class="map-search"><span aria-hidden="true">⌕</span><input type="search" aria-label="在分类图搜索名称" placeholder="搜索分类、病毒名称或缩写 / Search names"></label><button type="button" class="map-reset">重置 / Reset</button></div><div class="map-crumb" aria-label="分类路径 / Taxonomic path"></div><div class="map-layout"><div class="map-visual"><div class="map-svg"></div><p class="map-legend">扇区面积表示物种数量；这是分类导航图，不是系统发育树。<span class="en">Sector area represents species counts. This is a taxonomic navigator, not a phylogenetic tree.</span></p></div><div class="map-browser"><div class="map-browser-heading"><div><span class="map-kicker"></span><h3 class="map-current"></h3></div><div class="map-modes"><button type="button" data-map-mode="children">下级分类</button><button type="button" data-map-mode="species">物种列表</button></div></div><div class="map-results-summary" aria-live="polite"></div><div class="map-list"></div><div class="map-pagination"><button type="button" data-map-page="-1">上一页 / Previous</button><span></span><button type="button" data-map-page="1">下一页 / Next</button></div></div></div><div class="map-footnote">覆盖本次 ICTV 正式发布的分类单元，包括类病毒；未分类序列与尚未发现的病毒不在其中。520 个物种尚未分配至域，保留在“未分配域”分支。<span class="en">This release includes related entities such as viroids, not every detected sequence or undiscovered virus. The 520 species without an assigned realm remain in the unassigned branch.</span></div></div>`;
    const $=s=>mount.querySelector(s);const search=$('.map-search input');
    function navigate(n){if(n.record){if(typeof callbacks.openTaxon==='function')callbacks.openTaxon(n.record.id);return;}current=n;query='';search.value='';mode='children';page=0;render();}
    function children(){return [...current.children.values()].sort((a,b)=>b.count-a.count||a.name.localeCompare(b.name));}
    function ring(){
      let visible=children(),tail=[];if(visible.length>16){tail=visible.slice(15);visible=visible.slice(0,15);visible.push({key:'other',name:'其他分类',en:'Other taxa',count:tail.reduce((a,n)=>a+n.count,0),aggregate:true});}
      let angle=-Math.PI/2;const paths=[];
      visible.forEach((n,i)=>{const end=angle+2*Math.PI*n.count/current.count,mid=(angle+end)/2,p=point(165,mid),pct=100*n.count/current.count;
        // A single full-circle ring is split into two arcs for valid SVG geometry.
        const d=visible.length===1?arc(angle,angle+Math.PI)+' '+arc(angle+Math.PI,end):arc(angle,end);
        paths.push(`<g class="map-sector" role="button" tabindex="0" data-map-key="${e(encodeURIComponent(n.key))}" aria-label="${e(n.name)}, ${fmt(n.count)} species"><title>${e(n.name)} · ${fmt(n.count)} species · ${pct.toFixed(1)}%</title><path d="${d}" fill="${COLORS[i%COLORS.length]}"></path>${pct>=4.5?`<text x="${p[0]}" y="${p[1]+5}" text-anchor="middle">${pct.toFixed(pct>=10?0:1)}%</text>`:''}</g>`);angle=end;});
      let title=current===root?'病毒分类图谱':current.name;let lines=title.length>21?[title.slice(0,21),title.slice(21,42)]:[title];
      $('.map-svg').innerHTML=`<svg viewBox="0 0 520 520" role="group" aria-label="${e(title)}下级分类物种分布"><circle cx="260" cy="260" r="220" fill="none" stroke="#dce8e7" stroke-dasharray="3 8"/><circle cx="260" cy="260" r="117" fill="#eff7f4"/>${paths.join('')}<text class="map-center-kicker" x="260" y="206" text-anchor="middle">${current===root?'ICTV CLASSIFICATION':(RANKS[current.rank]?.[2]||'Species').toUpperCase()}</text>${lines.map((line,i)=>`<text class="map-center-title" x="260" y="${234+i*23}" text-anchor="middle">${e(line)}</text>`).join('')}<text class="map-center-count" x="260" y="${lines.length===1?286:302}" text-anchor="middle">${fmt(current.count)}</text><text class="map-center-unit" x="260" y="${lines.length===1?311:327}" text-anchor="middle">物种 / species</text></svg>`;
      $('.map-svg').querySelectorAll('.map-sector').forEach(el=>{const go=()=>{if(el.dataset.mapKey==='other'){mode='children';page=1;renderList();$('.map-browser').scrollIntoView({block:'nearest',behavior:'smooth'});}else navigate(byKey.get(decodeURIComponent(el.dataset.mapKey)));};el.addEventListener('click',go);el.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();go()}});});
    }
    function renderList(){let list=query?searchResults:mode==='species'?collectLeaves(current).sort((a,b)=>a.name.localeCompare(b.name)):children();const limit=8,pages=Math.max(1,Math.ceil(list.length/limit));page=Math.min(page,pages-1);const nextRank=RANKS[current.rank+1];$('.map-kicker').textContent=query?'GLOBAL SEARCH / 全库搜索':mode==='species'?'SPECIES / 物种':`${nextRank?.[2]||'Species'} / ${nextRank?.[1]||'物种'}`;$('.map-current').textContent=query?'匹配分类与病毒':current===root?'10 个域 + 未分配分支':current.name;$('.map-results-summary').textContent=`${fmt(list.length)} 项结果 / results · ${query?'全分类库':fmt(current.count)+' 个物种 / species'}`;
      $('.map-list').innerHTML=list.slice(page*limit,page*limit+limit).map(n=>{const color=COLORS[Math.max(0,children().indexOf(n))%COLORS.length];return `<button type="button" class="map-node ${n.record?'map-leaf':''}" data-map-key="${e(encodeURIComponent(n.key))}"><span class="map-node-dot" style="background:${color}"></span><span class="map-node-main"><b>${e(n.name)}</b><small>${n.record?e(n.record.name||n.record.abbr||'ICTV species'):(RANKS[n.rank]?.[1]||'物种')+' / '+(RANKS[n.rank]?.[2]||'Species')+(n.unassigned?' · Unassigned':'')}</small></span><span class="map-node-end">${n.record?'查看 / Open':fmt(n.count)}<small>${n.record?e(n.record.genome):'species'}</small></span></button>`;}).join('')||'<div class="map-empty">没有匹配项。请尝试英文名或缩写。<br>No matches. Try a scientific name or abbreviation.</div>';
      $('.map-list').querySelectorAll('[data-map-key]').forEach(b=>b.onclick=()=>navigate(byKey.get(decodeURIComponent(b.dataset.mapKey))));$('.map-pagination span').textContent=`${page+1} / ${fmt(pages)}`;$('.map-pagination [data-map-page="-1"]').disabled=page===0;$('.map-pagination [data-map-page="1"]').disabled=page>=pages-1;
      mount.querySelectorAll('[data-map-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mapMode===mode&&!query);b.setAttribute('aria-pressed',String(b.dataset.mapMode===mode&&!query));});
    }
    function render(){const path=[];let n=current;while(n){path.unshift(n);n=n.parent;}
      $('.map-crumb').innerHTML=path.map((n,i)=>`<button type="button" data-map-key="${e(encodeURIComponent(n.key))}" ${i===path.length-1?'aria-current="location"':''}>${n===root?'全部 / All':e(n.name)}</button>${i<path.length-1?'<span aria-hidden="true">/</span>':''}`).join('');$('.map-crumb').querySelectorAll('button').forEach(b=>b.onclick=()=>navigate(byKey.get(decodeURIComponent(b.dataset.mapKey))));ring();renderList();}
    $('.map-reset').onclick=()=>navigate(root);mount.querySelectorAll('[data-map-mode]').forEach(b=>b.onclick=()=>{query='';search.value='';mode=b.dataset.mapMode;page=0;renderList()});mount.querySelectorAll('[data-map-page]').forEach(b=>b.onclick=()=>{page+=Number(b.dataset.mapPage);renderList()});let timer;search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{query=search.value.trim().toLowerCase();searchResults=query?searchNodes.filter(x=>x.text.includes(query)).map(x=>x.n):[];page=0;renderList()},120)});render();
    return {root,nodes,navigateRoot:()=>navigate(root)};
  };
  // Exposed for lightweight data-integrity verification without a browser.
  window.VirusTaxonomyTree={buildTree,collectLeaves};
})();
