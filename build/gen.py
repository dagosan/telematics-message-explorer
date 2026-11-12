import json,sys,re
from lxml import etree
XS='{http://www.w3.org/2001/XMLSchema}'
def ln(e): return etree.QName(e).localname
def strip(t): return t.split(':')[-1] if t else t
class Gen:
    def __init__(self,files):
        self.el={};self.ty={};self.at={}
        for f in files:
            r=etree.parse(f).getroot()
            for ch in r:
                if not isinstance(ch.tag,str) or not ch.get('name'): continue
                k=ln(ch)
                if k=='element': self.el.setdefault(ch.get('name'),ch)
                elif k in('simpleType','complexType'): self.ty.setdefault(ch.get('name'),ch)
                elif k=='attribute': self.at.setdefault(ch.get('name'),ch)
    def doc(self,e):
        if e is None: return None
        d=e.find(XS+'annotation/'+XS+'documentation')
        if d is None: return None
        t=' '.join(''.join(d.itertext()).split())
        return t or None
    def simple_info(self,st):
        """st: simpleType element or restriction holder. returns dict base/facets/enums following base chain"""
        info={'base':None,'facets':{},'enums':[]}
        def walk(st):
            r=st.find(XS+'restriction')
            if r is None:
                u=st.find(XS+'union'); l=st.find(XS+'list')
                if info['base'] is None: info['base']='union' if u is not None else 'list'
                return
            b=r.get('base')
            if b and 'first' not in info: info['first']=strip(b)
            for f in r:
                if not isinstance(f.tag,str): continue
                k=ln(f)
                if k=='enumeration': info['enums'].append([f.get('value'),self.doc(f) or ''])
                elif k in('annotation','simpleType','attribute','attributeGroup'): pass
                else: info['facets'].setdefault(k,f.get('value'))
            if b:
                bn=strip(b)
                if b.startswith('xs:') or bn not in self.ty:
                    info['base']=bn
                else:
                    walk(self.ty[bn])
            else:
                inner=r.find(XS+'simpleType')
                if inner is not None: walk(inner)
        walk(st)
        out={}
        if info.get('first'): out['base']=info['first']
        elif info['base']: out['base']=info['base']
        if info['facets']: out['facets']=info['facets']
        if info['enums']: out['enums']=info['enums']
        return out
    def card(self,e,inchoice=False):
        mn=e.get('minOccurs','1'); mx=e.get('maxOccurs','1')
        c=('M' if mn!='0' else 'O')+('*' if (mx=='unbounded' or int(mx)>1) else '')
        return c, mn+'..'+('n' if mx=='unbounded' else mx)
    def attr_nodes(self,holder):
        out=[]
        for a in holder.findall(XS+'attribute'):
            d=a
            if a.get('ref'): d=self.at.get(strip(a.get('ref')),a)
            use=a.get('use','optional')
            n={'name':'@'+(d.get('name') or strip(a.get('ref'))),'card':'M' if use=='required' else 'O','cardRaw':use}
            doc=self.doc(a) or self.doc(d)
            if doc: n['doc']=doc
            t=d.get('type'); st=d.find(XS+'simpleType')
            n['type']=None; n['kind']='attr'
            if t:
                n['type']=strip(t)
                if not t.startswith('xs:') and strip(t) in self.ty:
                    si=self.simple_info(self.ty[strip(t)])
                    if si: n['simple']=si
            elif st is not None:
                si=self.simple_info(st)
                if si: n['simple']=si; n['type']=si.get('base')
            out.append(self.order(n))
        return out
    def order(self,n):
        o={}
        for k in('name','card','cardRaw','doc','type','kind','simple','inChoice','children'):
            if k in n: o[k]=n[k]
        return o
    def particle(self,p,inchoice,stack):
        out=[]
        for ch in p:
            if not isinstance(ch.tag,str): continue
            k=ln(ch)
            if k=='element': out.append(self.element(ch,inchoice,stack))
            elif k=='sequence': out+=self.particle(ch,inchoice,stack)
            elif k=='choice': out+=self.particle(ch,True,stack)
            elif k=='all': out+=self.particle(ch,inchoice,stack)
            elif k=='any': out.append({'name':'(any)','card':self.card(ch)[0],'cardRaw':self.card(ch)[1],'type':None,'kind':'complex'})
        return out
    def complex_children(self,ct,stack):
        kids=[]
        cc=ct.find(XS+'complexContent'); sc=ct.find(XS+'simpleContent')
        if cc is not None:
            ext=cc.find(XS+'extension'); 
            if ext is None: ext=cc.find(XS+'restriction')
            b=strip(ext.get('base'))
            if b in self.ty and ext.tag==XS+'extension': kids+=self.complex_children(self.ty[b],stack)
            kids+=self.particle(ext,False,stack); kids+=self.attr_nodes(ext)
        elif sc is not None:
            ext=sc.find(XS+'extension')
            if ext is None: ext=sc.find(XS+'restriction')
            kids+=self.attr_nodes(ext)
        else:
            kids+=self.particle(ct,False,stack); kids+=self.attr_nodes(ct)
        return kids
    def simple_content_base(self,ct):
        sc=ct.find(XS+'simpleContent')
        if sc is None: return None
        ext=sc.find(XS+'extension')
        if ext is None: ext=sc.find(XS+'restriction')
        return ext.get('base')
    def element(self,e,inchoice=False,stack=()):
        d=e
        if e.get('ref'):
            d=self.el[strip(e.get('ref'))]
        name=d.get('name')
        c,cr=self.card(e)
        n={'name':name,'card':c,'cardRaw':cr}
        doc=self.doc(e) or self.doc(d)
        if doc: n['doc']=doc
        if inchoice: n['inChoice']=True
        t=d.get('type'); ct=d.find(XS+'complexType'); st=d.find(XS+'simpleType')
        tname=None
        if t:
            tname=strip(t)
            if not t.startswith('xs:') and tname in self.ty:
                td=self.ty[tname]
                if ln(td)=='complexType': ct=td
                else: st=td
            else:
                n['type']=tname; n['kind']='builtin'; return self.order(n)
        if name in stack and ct is not None:
            n['type']=tname; n['kind']='complex'; return self.order(n)
        if ct is not None:
            scb=self.simple_content_base(ct)
            kids=self.complex_children(ct,stack+(name,))
            if scb:
                bn=strip(scb)
                n['type']=tname or bn
                if not scb.startswith('xs:') and bn in self.ty and ln(self.ty[bn])=='simpleType':
                    si=self.simple_info(self.ty[bn]); 
                    if si: n['simple']=si
                    n['kind']='codelist' if si.get('enums') else 'simple'
                else: n['kind']='builtin'
            else:
                n['type']=tname; n['kind']='complex'
            if kids: n['children']=kids
            return self.order(n)
        if st is not None:
            si=self.simple_info(st)
            n['type']=tname or si.get('base')
            if si: n['simple']=si
            n['kind']='codelist' if si.get('enums') else 'simple'
            return self.order(n)
        n['type']='(empty)'; n['kind']='builtin'
        return self.order(n)
    def message(self,name):
        e=self.el[name]
        t=self.element(e)
        tot=[0];cod=[0];dep=[0]
        def w(n,d):
            tot[0]+=1; dep[0]=max(dep[0],d)
            if n.get('simple',{}).get('enums'): cod[0]+=1
            for c in n.get('children',[]): w(c,d+1)
        w(t,1)
        return t,tot[0],cod[0],dep[0]
