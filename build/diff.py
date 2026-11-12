"""Merged official-vs-sector trees for the Explorer's Compare mode."""
import json,difflib,copy
from gen import Gen
FACET_L={'pattern':'pattern','minLength':'min length','maxLength':'max length','length':'length','totalDigits':'total digits','fractionDigits':'fraction digits','minInclusive':'min (incl.)','maxInclusive':'max (incl.)','minExclusive':'min (excl.)','maxExclusive':'max (excl.)','whiteSpace':'white space'}
def mark(n,st):
    n=copy.deepcopy(n)
    def w(x):
        x['st']=st; x['d']=1
        for c in x.get('children',[]): w(c)
    w(n); return n
def merge(o,s):
    """o: official node, s: sector node (same element). returns merged node (sector view + diff marks)."""
    n={k:v for k,v in s.items() if k!='children'}
    ch=[]
    if o['name']!=s['name']: ch.append(['name',o['name'],s['name']])
    if o['cardRaw']!=s['cardRaw']: ch.append(['occurrence',o['cardRaw'],s['cardRaw']])
    if (o.get('type') or '')!=(s.get('type') or ''): ch.append(['type',o.get('type') or '—',s.get('type') or '—'])
    if bool(o.get('inChoice'))!=bool(s.get('inChoice')): ch.append(['within choice','yes' if o.get('inChoice') else 'no','yes' if s.get('inChoice') else 'no'])
    so,ss=o.get('simple') or {},s.get('simple') or {}
    if (so.get('base') or '')!=(ss.get('base') or ''): ch.append(['base type',so.get('base') or '—',ss.get('base') or '—'])
    fo,fs=so.get('facets') or {},ss.get('facets') or {}
    for k in list(FACET_L)+[k for k in set(fo)|set(fs) if k not in FACET_L]:
        if fo.get(k)!=fs.get(k) and (k in fo or k in fs): ch.append([FACET_L.get(k,k),fo.get(k,'—'),fs.get(k,'—')])
    eo,es=so.get('enums') or [],ss.get('enums') or []
    vo={e[0] for e in eo}; vs={e[0] for e in es}
    ea=[e for e in es if e[0] not in vo]; er=[e for e in eo if e[0] not in vs]
    if ch: n['ch']=ch
    if ea: n['ea']=ea
    if er: n['er']=er
    if ch or ea or er: n['st']='c'
    co,cs=o.get('children',[]),s.get('children',[])
    kids=[]
    sm=difflib.SequenceMatcher(None,[c['name'] for c in co],[c['name'] for c in cs],autojunk=False)
    # name-based pairing that tolerates re-ordering: first LCS, then leftover same-name pairs
    pend_r=[];pend_a=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal':
            for a,b in zip(co[i1:i2],cs[j1:j2]): kids.append(('m',a,b))
        else:
            for a in co[i1:i2]: kids.append(('r',a,None))
            for b in cs[j1:j2]: kids.append(('a',None,b))
    # re-pair moved elements (removed here, added elsewhere under the same parent)
    rem={}; 
    for idx,(t,a,b) in enumerate(kids):
        if t=='r': rem.setdefault(a['name'],[]).append(idx)
    drop=set()
    for idx,(t,a,b) in enumerate(kids):
        if t=='a' and rem.get(b['name']):
            ridx=rem[b['name']].pop(0); kids[idx]=('mv',kids[ridx][1],b); drop.add(ridx)
    out=[]
    for idx,(t,a,b) in enumerate(kids):
        if idx in drop: continue
        if t=='m': out.append(merge(a,b))
        elif t=='mv':
            m=merge(a,b); m.setdefault('ch',[]).append(['position','—','moved within parent']); m['st']='c'; out.append(m)
        elif t=='r': out.append(mark(a,'r'))
        else: out.append(mark(b,'a'))
    if out: n['children']=out
    if n.get('st') or any(c.get('d') for c in out): n['d']=1
    return n
def stats(t):
    r={'total':0,'coded':0,'depth':0,'da':0,'dr':0,'dc':0}
    def w(n,d):
        r['total']+=1; r['depth']=max(r['depth'],d)
        if (n.get('simple') or {}).get('enums'): r['coded']+=1
        st=n.get('st')
        if st=='a': r['da']+=1
        elif st=='r': r['dr']+=1
        elif st=='c': r['dc']+=1
        for c in n.get('children',[]): w(c,d+1)
    w(t,1); return r
def build(sector_msgs):
    go=Gen(['taf_cat_complete.xsd','taf_cat_codelists.xsd','TAP_TSI_codelist.xsd']); gs=Gen(['sector_recon.xsd'])
    ALIAS={'ChangeOfTrackMessage':'ChangeofTrackMessage'}
    msgs={}
    for k,m in sector_msgs.items():
        ok=ALIAS.get(k,k)
        if ok not in go.el: continue
        t=merge(go.message(ok)[0],gs.message(k)[0])
        e={'title':m['title'],'cat':m['cat'],'content':m['content'],'tree':t}; e.update(stats(t)); msgs[k]=e
    return msgs
if __name__=='__main__':
    from build import msgs as SM
