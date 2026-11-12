import json,re
from gen import Gen
APP=json.load(open('../app/app.json'));M=APP['MESSAGES']
g=Gen(['sector_recon.xsd'])
NEW={
 'CapacityModelMessage':('Capacity Model','path','Capacity model data per timetable: identifiers, lead RU, coordinating IM, train and traffic type, capacity product type.'),
 'CapacityProductMessage':('Capacity Product','path','Response to a capacity product search: the matching TCRs, capacity bands, catalogue paths or paths.'),
 'CapacityProductSearchMessage':('Capacity Product Search','path','Search for capacity products; answered by the Capacity Product message.'),
 'ObjectInfoMessage':('Object Info','path','Request, update or report the content of a business object.'),
 'PathCoordinationMessage':('Path Coordination','path','Coordination and data synchronisation between RUs and between IMs.'),
 'PathSectionNotificationMessage':('Path Section Notification','path','Notification on the usage of path sections during the planning and operational phases.'),
 'UpdateLinkMessage':('Update Link','path','Indicates and updates the relation between the train and path business objects.'),
 'TCRMessage':('TCR','tcr','Temporary capacity restrictions exchanged between IMs / allocation bodies and RUs / applicants.'),
 'TCRCanceledMessage':('TCR Cancelled','tcr','Cancels a planned temporary capacity restriction; its status becomes "Canceled".'),
 'TCRResponseMessage':('TCR Response','tcr','Response to a TCR message: import status and report, with warnings.'),
 'PassengerTrainCompositionMessage':('Passenger Train Composition','prep','Composition of a passenger train, sent by an RU to another RU, the IM or the station manager.'),
 'TrainCompositionHermesCompatibleMessage':('Train Composition (Hermes-compatible)','prep','Train composition from RU to IM in the Hermes-compatible structure.'),
 'RollingStockRestrictionMessage':('Rolling Stock Restriction','prep','Restrictions and defects of passenger rolling stock, within the passenger train composition process.'),
 'RunningStatusReportMessage':('Running Status Report','run','Precise train localisation with raw GNSS data, sent by the RU to the IM.'),
 'TrainForecastedDelayCauseMessage':('Train Forecasted Delay Cause','run','Cause of a forecasted delay that has not yet occurred during the train journey.'),
 'WagonInterchangeNoticeMessage':('Wagon Interchange Notice','frt','Asks the neighbouring RU / service provider to accept responsibility for a wagon.'),
 'WagonInterchangeSubNoticeMessage':('Wagon Interchange Sub-Notice','frt','Informs the IM that responsibility is handed over to the next RU / service provider.'),
 'WagonReceivedAtInterchangeMessage':('Wagon Received at Interchange','frt','Answer to the interchange notice: confirms acceptance of responsibility for the wagon.'),
 'WagonRefusedAtInterchangeMessage':('Wagon Refused at Interchange','frt','Answer to the interchange notice: responsibility for the wagon is refused.'),
 'WagonPerformanceMessage':('Wagon Performance','frt','Wagon performance data delivered by the user RU to the wagon keeper.'),
}
ALIAS={'ChangeOfTrackMessage':'ChangeofTrackMessage'}
msgs={}
for n in sorted(g.el):
    if not (n.endswith('Message') or n.endswith('Messages')): continue
    t,tot,cod,dep=g.message(n)
    old=M.get(ALIAS.get(n,n))
    if old: title,cat,content=old['title'],old['cat'],old['content']; only=False
    else: title,cat,content=NEW[n]; only=True
    m={'title':title,'cat':cat,'content':content,'total':tot,'coded':cod,'depth':dep,'tree':t}
    if only: m['only']=True
    msgs[n]=m
CATORDER=['path','tcr','prep','run','frt','ref','svc']
CATS={'path':'Path Management & Capacity','tcr':'Temporary Capacity Restrictions (TCR)','prep':'Train Preparation & Composition','run':'Train Running & Monitoring','frt':'Wagons & Consignment','ref':'Reference Data / Datasets','svc':'Messaging Service'}
SEC={'MESSAGES':msgs,'ORDER':list(msgs),'CATS':CATS,'CATORDER':CATORDER}
assert all(m['cat'] in CATS for m in msgs.values())
print(len(msgs),sum(m['total'] for m in msgs.values()),sum(m['coded'] for m in msgs.values()),sum(1 for m in msgs.values() if m.get('only')))
js=json.dumps(SEC,ensure_ascii=False,separators=(',',':')).replace('</','<\\/').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
print(len(js))

L=open('../app/orig.html',encoding='utf-8').read().split('\n')
assert L[158].startswith('<script>const APP=') and L[158].endswith(';')
L[158]=L[158]+'\nconst APP_SECTOR='+js+';'
h='\n'.join(L)
def rep(a,b,cnt=1):
    global h
    assert h.count(a)==cnt,(a[:60],h.count(a)); h=h.replace(a,b)
# --- data binding
rep("const MESSAGES=APP.MESSAGES, ORDER=APP.ORDER, CATS=APP.CATS, CATORDER=APP.CATORDER;",
"""/* ---------- SCHEMAS (switchable) ---------- */
const SCHEMAS={
  tel:{data:APP, label:"TEL TSI \\u00B7 official", sub:"Freight, passenger and ticket-data messages \\u2014 pick one to explore its full data-element tree.",
       code:"Freight & passenger messages \\u00B7 UIC ticket data (ASN.1) \\u00B7 from the official XML / ASN.1 schemas", alias:{ChangeOfTrackMessage:"ChangeofTrackMessage"}},
  sector:{data:APP_SECTOR, label:"RU/IM sector \\u00B7 XSD 3.5.2.1", sub:"RU/IM sector messages, including those not in the TSI schema \\u2014 pick one to explore its full data-element tree.",
       code:"taf_cat_complete_sector_3.5.2.1.xsd \\u00B7 Sector Handbook 3.9, Annex 6.2 (June 2026) \\u00B7 rebuilt from the published schema documentation", alias:{ChangeofTrackMessage:"ChangeOfTrackMessage"}}
};
let SCHEMA="tel", MESSAGES, ORDER, CATS, CATORDER;
function bindSchema(k){ SCHEMA=SCHEMAS[k]?k:"tel"; const d=SCHEMAS[SCHEMA].data; MESSAGES=d.MESSAGES; ORDER=d.ORDER; CATS=d.CATS; CATORDER=d.CATORDER; }
(function(){ let k="tel"; try{ k=localStorage.getItem("tel-explorer-schema")||"tel"; }catch(e){} bindSchema(k); })();""")
rep("""const INDEX=[];
ORDER.forEach((mk,mi)=>{ (function walk(n,path,names){""","""let INDEX=[];
function buildIndex(){ INDEX=[];
ORDER.forEach((mk,mi)=>{ (function walk(n,path,names){""")
rep("""})(MESSAGES[mk].tree,[],[MESSAGES[mk].title]); });
""","""})(MESSAGES[mk].tree,[],[MESSAGES[mk].title]); });
}
""")
# --- home
rep("""  let html="";
  CATORDER.forEach(cat=>{
    const keys=ORDER.filter(k=>MESSAGES[k].cat===cat);""","""  const S=SCHEMAS[SCHEMA];
  document.getElementById('h-sub').textContent=S.sub; document.getElementById('h-code').textContent=S.code;
  document.querySelectorAll('.schsw button').forEach(b=>{const on=b.getAttribute('data-schema')===SCHEMA; b.classList.toggle('on',on); b.setAttribute('aria-pressed',on?'true':'false');});
  let html="";
  CATORDER.forEach(cat=>{
    const keys=ORDER.filter(k=>MESSAGES[k].cat===cat);""")
rep("""        <div class="c-title">${esc(m.title)}</div>""","""        <div class="c-title">${esc(m.title)}${m.only?'<span class="tag-only" title="Not part of the official TEL TSI schema">sector only</span>':''}</div>""")
rep("""    <div class="sub">Freight, passenger and ticket-data messages — pick one to explore its full data-element tree.</div>
    <div class="code">Freight &amp; passenger messages · UIC ticket data (ASN.1) · from the official XML / ASN.1 schemas</div>""",
"""    <div class="sub" id="h-sub"></div>
    <div class="code" id="h-code"></div>
    <div class="schsw" role="group" aria-label="Schema"><span class="schsw-l">Schema</span><button type="button" data-schema="tel">TEL TSI · official</button><button type="button" data-schema="sector">RU/IM sector · XSD 3.5.2.1</button></div>""")
rep("""    <select id="switcher" title="Jump to message"></select>""","""    <div class="schsw schsw-sm" role="group" aria-label="Schema"><button type="button" data-schema="tel" title="TEL TSI · official schemas">TEL TSI</button><button type="button" data-schema="sector" title="RU/IM sector schema · XSD 3.5.2.1">Sector 3.5.2.1</button></div>
    <select id="switcher" title="Jump to message"></select>""")
# --- explorer meta + hash
rep("""document.getElementById('exp-code').textContent=key+'  \\u00B7  '+m.total""","""document.getElementById('exp-code').textContent=(SCHEMA==='sector'?'Sector 3.5.2.1':'TEL TSI')+'  \\u00B7  '+key+'  \\u00B7  '+m.total""")
rep("""renderTree(); renderDetail(); try{location.hash=key;}catch(e){}""","""renderTree(); renderDetail(); try{location.hash=(SCHEMA==='tel'?'':SCHEMA+':')+key;}catch(e){}""")
rep("""try{location.hash='';}catch(e){} window.scrollTo(0,0); }""","""try{location.hash='';}catch(e){} window.scrollTo(0,0); }
function setSchema(k){
  if(!SCHEMAS[k]||k===SCHEMA) return;
  const was=current; bindSchema(k); try{localStorage.setItem("tel-explorer-schema",k);}catch(e){}
  buildIndex(); buildHome();
  const key=was?(MESSAGES[was]?was:SCHEMAS[k].alias[was]):null;   // same message in the other schema, if it exists there
  if(key&&MESSAGES[key]) openMessage(key); else goHome();
}
document.addEventListener('click',e=>{const b=e.target.closest('.schsw [data-schema]'); if(b) setSchema(b.getAttribute('data-schema'));});""")
rep("""buildHome();
(function(){ let h=""; try{h=decodeURIComponent((location.hash||"").replace(/^#/,""));}catch(e){} if(h&&MESSAGES[h]) openMessage(h); else goHome(); })();""",
"""(function(){ let h=""; try{h=decodeURIComponent((location.hash||"").replace(/^#/,""));}catch(e){}
  const i=h.indexOf(":"); if(i>0&&SCHEMAS[h.slice(0,i)]){ bindSchema(h.slice(0,i)); h=h.slice(i+1); }
  else if(h&&!MESSAGES[h]&&APP.MESSAGES[h]) bindSchema("tel");   // plain deep links keep pointing at the official schema
  buildIndex(); buildHome();
  if(h&&MESSAGES[h]) openMessage(h); else goHome(); })();""")
# --- css
rep("""</style></head><body>""",""".schsw{display:inline-flex;align-items:center;gap:0;margin-top:14px;border:1px solid rgba(255,255,255,.45);border-radius:9px;overflow:hidden;background:rgba(255,255,255,.08)}
.schsw-l{font-size:11px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;padding:0 12px;opacity:.8}
.schsw button{font:inherit;font-size:13px;font-weight:600;color:#fff;background:transparent;border:none;border-left:1px solid rgba(255,255,255,.3);padding:8px 14px;cursor:pointer;white-space:nowrap}
.schsw button:first-of-type{border-left:none}.schsw .schsw-l+button{border-left:1px solid rgba(255,255,255,.3)}
.schsw button:hover{background:rgba(255,255,255,.16)}
.schsw button.on{background:#fff;color:var(--navy)}
.schsw button:focus-visible{outline:2px solid #fff;outline-offset:-3px}
.schsw-sm{margin-top:0;flex:0 0 auto;margin-left:auto}.schsw-sm+#switcher{margin-left:0}.schsw-sm button{font-size:12px;padding:6px 10px}
.tag-only{display:inline-block;margin-left:8px;font-size:10px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;padding:2px 7px;border-radius:10px;background:#fdf2d8;color:#8a6300;border:1px solid #f2dca0;vertical-align:middle;white-space:nowrap}
@media(max-width:820px){.exp-bar{flex-wrap:wrap;row-gap:8px}.exp-meta{flex:1 1 50%;min-width:0}.schsw{display:flex;width:100%}.schsw button{flex:1 1 0;padding:9px 6px;font-size:12.5px}.schsw-l{display:none}.schsw-sm{width:auto;display:inline-flex}.schsw-sm button{flex:0 0 auto;padding:6px 8px;font-size:11.5px}}
</style></head><body>""")

# ======================= COMPARE MODE =======================
import diff as _diff
D=_diff.build(msgs)
CMP={'MESSAGES':D,'ORDER':list(D),'CATS':CATS,'CATORDER':CATORDER}
jsc=json.dumps(CMP,ensure_ascii=False,separators=(',',':')).replace('</','<\\/').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
print('compare',len(D),len(jsc),sum(m['da'] for m in D.values()),sum(m['dr'] for m in D.values()),sum(m['dc'] for m in D.values()))
rep("\nconst APP_SECTOR=","\nconst APP_COMPARE="+jsc+";\nconst APP_SECTOR=")
rep("""};
let SCHEMA="tel", MESSAGES, ORDER, CATS, CATORDER;""",""",
  compare:{data:APP_COMPARE, label:"Compare", sub:"Official TEL TSI schema against the RU/IM sector schema 3.5.2.1, message by message \\u2014 pick one to see what differs.",
       code:"Structure, occurrence, types, constraints and code-list values are compared \\u00B7 documentation text is not \\u00B7 passenger retail and ticket data have no sector counterpart", alias:{ChangeofTrackMessage:"ChangeOfTrackMessage"}}
};
let SCHEMA="tel", MESSAGES, ORDER, CATS, CATORDER;
const isCmp=()=>SCHEMA==="compare";
function diffTag(n){ return n.st==='a'?'<span class="dtag d-a" title="Only in the sector schema">+ sector</span>':n.st==='r'?'<span class="dtag d-r" title="Only in the official schema">\\u2212 official</span>':n.st==='c'?'<span class="dtag d-c" title="Defined differently in the two schemas">\\u2260 changed</span>':''; }
function diffSummary(m){ if(!(m.da+m.dr+m.dc)) return '<span class="c-stat dsum-same">identical</span>';
  return (m.da?`<span class="c-stat dsum-a"><b>+${m.da}</b> sector only</span>`:'')+(m.dr?`<span class="c-stat dsum-r"><b>\\u2212${m.dr}</b> official only</span>`:'')+(m.dc?`<span class="c-stat dsum-c"><b>\\u2260${m.dc}</b> changed</span>`:''); }""")
# home stats + cards
rep("""  document.getElementById('h-stats').innerHTML =
     `<div class="stat"><b>${ORDER.length}</b><span>MESSAGES</span></div>`
   + `<div class="stat"><b>${totalEl}</b><span>DATA ELEMENTS</span></div>`
   + `<div class="stat"><b>${totalCo}</b><span>CODED FIELDS</span></div>`;""","""  if(isCmp()){ let a=0,r=0,c=0,same=0; ORDER.forEach(k=>{const m=MESSAGES[k]; a+=m.da; r+=m.dr; c+=m.dc; if(!(m.da+m.dr+m.dc))same++;});
    document.getElementById('h-stats').innerHTML =
       `<div class="stat"><b>${ORDER.length}</b><span>MESSAGES IN BOTH</span></div>`
     + `<div class="stat"><b>${same}</b><span>IDENTICAL</span></div>`
     + `<div class="stat"><b>+${a}</b><span>SECTOR-ONLY ELEMENTS</span></div>`
     + `<div class="stat"><b>\\u2212${r}</b><span>OFFICIAL-ONLY ELEMENTS</span></div>`
     + `<div class="stat"><b>\\u2260${c}</b><span>CHANGED ELEMENTS</span></div>`;
  } else
  document.getElementById('h-stats').innerHTML =
     `<div class="stat"><b>${ORDER.length}</b><span>MESSAGES</span></div>`
   + `<div class="stat"><b>${totalEl}</b><span>DATA ELEMENTS</span></div>`
   + `<div class="stat"><b>${totalCo}</b><span>CODED FIELDS</span></div>`;""")
rep("""        <div class="c-foot">
          <span class="c-stat"><b>${m.total}</b> elements</span>
          <span class="c-stat"><b>${m.coded}</b> coded</span>
          <span class="c-stat"><b>${m.depth}</b> levels</span>
          <span class="c-go">Explore \\u2192</span>
        </div></button>`;
    });
    html+=`</div>`;
  });""","""        <div class="c-foot">`+(isCmp()?diffSummary(m):`
          <span class="c-stat"><b>${m.total}</b> elements</span>
          <span class="c-stat"><b>${m.coded}</b> coded</span>
          <span class="c-stat"><b>${m.depth}</b> levels</span>`)+`
          <span class="c-go">${isCmp()?'Compare':'Explore'} \\u2192</span>
        </div></button>`;
    });
    html+=`</div>`;
  });
  if(isCmp()){ const SM=APP_SECTOR.MESSAGES, only=APP_SECTOR.ORDER.filter(k=>SM[k].only);
    html+=`<div class="cat-h">Sector only \\u00B7 no counterpart in the official schema <span class="cnt">${only.length}</span></div><div class="grid">`
      + only.map(k=>`<button class="card" data-open-sector="${k}"><div class="c-title">${esc(SM[k].title)}<span class="tag-only">sector only</span></div><div class="c-code">${esc(k)}</div><div class="c-desc">${esc(SM[k].content)}</div>
          <div class="c-foot"><span class="c-stat"><b>${SM[k].total}</b> elements</span><span class="c-go">Open in sector schema \\u2192</span></div></button>`).join("")+`</div>`; }""")
# explorer state + rows
rep("""let UID=0, TREE=null, byId={}, expanded=new Set(), selected=0, query="", mandOnly=false, enumFilter="", current=null;""",
    """let UID=0, TREE=null, byId={}, expanded=new Set(), selected=0, query="", mandOnly=false, diffOnly=false, enumFilter="", current=null;""")
rep("""  let h=`<div class="row ${n.__id===selected?'sel':''}" style="padding-left:${8+depth*17}px" data-sel="${n.__id}">`+caret+badge(n.card)+`<span class="nm">${hl(n.name)}</span>`+typ+ec+ch+`</div>`;
  if(kids.length&&open) for(const c of kids){ if(mandOnly&&!hasMand(c))continue;""","""  let h=`<div class="row ${n.__id===selected?'sel':''}${n.st?' row-'+n.st:''}" style="padding-left:${8+depth*17}px" data-sel="${n.__id}">`+caret+badge(n.card)+`<span class="nm">${hl(n.name)}</span>`+typ+ec+ch+diffTag(n)+`</div>`;
  if(kids.length&&open) for(const c of kids){ if(mandOnly&&!hasMand(c))continue; if(diffOnly&&!c.d)continue;""")
# detail
rep("""  if(n.inChoice)chips+=`<span class="chip chip-c">within choice</span>`;""","""  if(n.inChoice)chips+=`<span class="chip chip-c">within choice</span>`;
  if(n.st)chips+=`<span class="chip chip-d chip-d${n.st}">${n.st==='a'?'Only in sector schema':n.st==='r'?'Only in official schema':'Differs between schemas'}</span>`;""")
rep("""  if(n.doc)h+=`<p class="doc">${esc(n.doc)}</p>`;
  if(n.simple){""","""  if(n.doc)h+=`<p class="doc">${esc(n.doc)}</p>`;
  if(isCmp()){
    if(n.st==='a')h+=`<p class="dnote dnote-a">This element exists only in the RU/IM sector schema 3.5.2.1.</p>`;
    if(n.st==='r')h+=`<p class="dnote dnote-r">This element exists only in the official TEL TSI schema. The details below are the official definition.</p>`;
    if(n.ch&&n.ch.length)h+=`<div class="d-sec">Differences <span class="cnt">${n.ch.length}</span></div><table class="facets dtable"><tr><th></th><th>Official</th><th>Sector 3.5.2.1</th></tr>`+n.ch.map(r=>`<tr><td>${esc(r[0])}</td><td class="mono">${esc(r[1])}</td><td class="mono">${esc(r[2])}</td></tr>`).join("")+`</table>`;
    const ev=(t,l,c)=>l&&l.length?`<div class="d-sec">${t} <span class="cnt">${l.length}</span></div><div class="enumlist ${c}">`+l.map(e=>`<div class="enumrow"><span class="ev">${esc(e[0])}</span>${e[1]?`<span class="el">${esc(e[1])}</span>`:""}</div>`).join("")+`</div>`:"";
    h+=ev("Allowed values only in sector schema",n.ea,"el-a")+ev("Allowed values only in official schema",n.er,"el-r");
    if(!n.st&&n.d)h+=`<p class="dnote">This element is the same in both schemas; differences are further down its tree.</p>`;
    if(!n.d)h+=`<p class="dnote">Same in both schemas, including everything below it.</p>`;
  }
  if(n.simple){""")
# open message
rep("""  expanded=new Set([TREE.__id]); selected=TREE.__id; query=""; mandOnly=false; enumFilter="";""","""  expanded=new Set([TREE.__id]); selected=TREE.__id; query=""; mandOnly=false; enumFilter="";
  diffOnly=isCmp()&&!!TREE.d;
  if(diffOnly) Object.values(byId).forEach(n=>{ if(n.d&&!n.st&&(n.children||[]).length) expanded.add(n.__id); if(n.st==='c'&&(n.children||[]).some(c=>c.d)) expanded.add(n.__id); });
  document.getElementById('diffOnly').checked=diffOnly; document.getElementById('explorer').classList.toggle('cmp',isCmp());""")
rep("""document.getElementById('exp-code').textContent=(SCHEMA==='sector'?'Sector 3.5.2.1':'TEL TSI')+'  \\u00B7  '+key+'  \\u00B7  '+m.total+' elements  \\u00B7  '+m.coded+' coded  \\u00B7  depth '+m.depth;""",
"""document.getElementById('exp-code').textContent=isCmp()
    ? 'Official vs sector 3.5.2.1  \\u00B7  '+key+'  \\u00B7  '+((m.da+m.dr+m.dc)?('+'+m.da+' sector only  \\u00B7  \\u2212'+m.dr+' official only  \\u00B7  \\u2260'+m.dc+' changed'):'identical in both schemas')
    : (SCHEMA==='sector'?'Sector 3.5.2.1':'TEL TSI')+'  \\u00B7  '+key+'  \\u00B7  '+m.total+' elements  \\u00B7  '+m.coded+' coded  \\u00B7  depth '+m.depth;""")
rep("""document.getElementById("mandOnly").addEventListener("change",e=>{mandOnly=e.target.checked;renderTree();});""","""document.getElementById("mandOnly").addEventListener("change",e=>{mandOnly=e.target.checked;renderTree();});
document.getElementById("diffOnly").addEventListener("change",e=>{diffOnly=e.target.checked;renderTree();});
document.getElementById('home-grid').addEventListener('click',e=>{const b=e.target.closest('[data-open-sector]'); if(b){ const k=b.getAttribute('data-open-sector'); setSchema('sector'); openMessage(k); }});""")
# markup
rep("""<button type="button" data-schema="sector">RU/IM sector · XSD 3.5.2.1</button></div>""","""<button type="button" data-schema="sector">RU/IM sector · XSD 3.5.2.1</button><button type="button" data-schema="compare">Compare the two</button></div>""")
rep("""<button type="button" data-schema="sector" title="RU/IM sector schema · XSD 3.5.2.1">Sector 3.5.2.1</button></div>""","""<button type="button" data-schema="sector" title="RU/IM sector schema · XSD 3.5.2.1">Sector 3.5.2.1</button><button type="button" data-schema="compare" title="Compare official and sector schema">Compare</button></div>""")
rep("""    <label class="chk"><input type="checkbox" id="mandOnly"> Mandatory only</label>""","""    <label class="chk"><input type="checkbox" id="mandOnly"> Mandatory only</label>
    <label class="chk cmp-only"><input type="checkbox" id="diffOnly"> Differences only</label>""")
rep("""      <span><span class="enumchip">▤</span> coded</span>""","""      <span><span class="enumchip">▤</span> coded</span>
      <span class="cmp-only"><span class="dtag d-a">+ sector</span></span>
      <span class="cmp-only"><span class="dtag d-r">− official</span></span>
      <span class="cmp-only"><span class="dtag d-c">≠ changed</span></span>""")
rep("""</style></head><body>""",""".cmp-only{display:none!important}#explorer.cmp .cmp-only{display:inline-flex!important}
.dtag{display:inline-block;margin-left:8px;font-size:10.5px;font-weight:700;padding:1px 7px;border-radius:10px;white-space:nowrap;border:1px solid}
.d-a{background:#e3f4e8;color:#17663a;border-color:#a9d8b8}.d-r{background:#fbe6e6;color:#a12a2a;border-color:#eab4b4}.d-c{background:#fdf2d8;color:#8a6300;border-color:#f2dca0}
.row-a{background:#f1faf3}.row-r{background:#fdf3f3}.row-r .nm{text-decoration:line-through;text-decoration-color:#c98a8a}.row-c{background:#fffaeb}
.chip-da{background:#e3f4e8;color:#17663a;border-color:#a9d8b8}.chip-dr{background:#fbe6e6;color:#a12a2a;border-color:#eab4b4}.chip-dc{background:#fdf2d8;color:#8a6300;border-color:#f2dca0}
.dnote{font-size:13px;color:var(--muted);margin:10px 0}.dnote-a{color:#17663a}.dnote-r{color:#a12a2a}
.dtable th{text-align:left;font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--muted);padding:5px 8px;border-bottom:1px solid var(--border)}
.dtable td:first-child{width:30%}
.el-a{border-color:#a9d8b8}.el-r{border-color:#eab4b4}
.c-foot .dsum-a b{color:#17663a}.c-foot .dsum-r b{color:#a12a2a}.c-foot .dsum-c b{color:#8a6300}.dsum-same{color:var(--muted)}
.cat-h .cnt{vertical-align:middle}
</style></head><body>""")

# ======================= VERSION + CHANGE LOG =======================
VERSION="1.3"
CHANGELOG=[
 ["1.3","12 November 2026",["Version number in the header, with this change log."]],
 ["1.2","12 November 2026",["Compare mode: official TEL TSI schema against the RU/IM sector schema 3.5.2.1, for the 26 messages present in both.",
   "Merged tree with elements tagged as sector only, official only or changed, and a “Differences only” filter.",
   "Side-by-side table of differing occurrence, type, constraints and code-list values in the detail panel.",
   "Difference counts per message on the home page; sector-only messages listed separately."]],
 ["1.1","12 November 2026",["Schema switch between the official TEL TSI schemas and the RU/IM sector schema.",
   "RU/IM sector schema XSD 3.5.2.1 added (46 messages), rebuilt from Annex 6.2 of the Sector Handbook 3.9; 20 messages marked “sector only”.",
   "New category for Temporary Capacity Restrictions (TCR).",
   "Links can carry the schema (for example #sector:PathRequestMessage); the chosen schema is remembered."]],
 ["1.0","Before November 2026",["Message and data explorer for the official schemas: 52 freight, passenger and ticket-data messages.",
   "Element tree with occurrence, types, constraints and code lists; search across all messages; “Mandatory only” filter.",
   "Earlier history is not recorded in this log."]],
]
import html as _html
cl=''.join('<section class="cl-v"><h3>Version %s <span>%s</span></h3><ul>%s</ul></section>'%(v,d,''.join('<li>%s</li>'%_html.escape(i) for i in items)) for v,d,items in CHANGELOG)
rep("""    <h1>Telematics TSI — Message & Data Explorer</h1>""","""    <button type="button" class="verbtn" id="verBtn" title="Open the change log" aria-haspopup="dialog">v"""+VERSION+""" <span>· change log</span></button>
    <h1>Telematics TSI — Message & Data Explorer</h1>""")
rep("""<section id="explorer">""","""<dialog id="chlog" aria-labelledby="chlog-t"><div class="cl-head"><h2 id="chlog-t">Change log</h2><button type="button" class="cl-x" id="chlogClose" aria-label="Close">×</button></div><div class="cl-body">"""+cl+"""</div></dialog>
<section id="explorer">""")
rep("""document.getElementById("diffOnly").addEventListener("change",""","""(function(){ const d=document.getElementById('chlog');
  document.getElementById('verBtn').addEventListener('click',()=>{ if(d.showModal) d.showModal(); else d.setAttribute('open',''); });
  document.getElementById('chlogClose').addEventListener('click',()=>{ if(d.close) d.close(); else d.removeAttribute('open'); });
  d.addEventListener('click',e=>{ if(e.target===d&&d.close) d.close(); }); })();
document.getElementById("diffOnly").addEventListener("change",""")
rep("""<meta name="theme-color" content="#253ebe">""","""<meta name="theme-color" content="#253ebe">
<meta name="version" content=\""""+VERSION+"""\">""")
rep("""</style></head><body>""",""".verbtn{position:absolute;top:16px;right:20px;z-index:2;font:inherit;font-size:12px;font-weight:700;color:#fff;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.4);border-radius:20px;padding:5px 12px;cursor:pointer}
.verbtn span{font-weight:400;opacity:.85}.verbtn:hover{background:rgba(255,255,255,.24)}.verbtn:focus-visible{outline:2px solid #fff;outline-offset:2px}
#chlog{border:none;border-radius:14px;padding:0;width:min(640px,calc(100vw - 32px));max-height:min(80vh,720px);color:var(--ink);background:#fff;box-shadow:0 20px 60px rgba(0,0,0,.35)}
#chlog[open]{display:flex;flex-direction:column}
#chlog::backdrop{background:rgba(10,20,60,.5)}
.cl-head{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid var(--border);flex:0 0 auto}
.cl-head h2{margin:0;font-size:18px;color:var(--navy)}
.cl-x{font:inherit;font-size:24px;line-height:1;background:none;border:none;color:var(--muted);cursor:pointer;padding:2px 8px;border-radius:6px}.cl-x:hover{background:var(--light)}
.cl-body{padding:6px 20px 20px;overflow:auto}
.cl-v h3{font-size:14px;color:var(--navy);margin:16px 0 6px}.cl-v h3 span{font-weight:400;color:var(--muted);margin-left:8px;font-size:12.5px}
.cl-v ul{margin:0;padding-left:20px;font-size:13.5px;line-height:1.55}.cl-v li{margin:3px 0}
@media(max-width:820px){.verbtn{top:calc(env(safe-area-inset-top) + 8px);right:12px;font-size:11px;padding:4px 10px}.verbtn span{display:none}}
</style></head><body>""")
open('../app/Telematics_TSI_Message_Explorer.html','w',encoding='utf-8').write(h)
print('written',len(h))
