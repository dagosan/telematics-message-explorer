import re,sys
from lxml import etree
txt=open('annex62_layout.txt',encoding='utf-8').read().replace('\f','\n')
lines=txt.split('\n')
hdr=re.compile(r'^(element|complexType|simpleType|attribute) (\S+)\s*$')
starts=[(i,m.group(1),m.group(2)) for i,l in enumerate(lines) if (m:=hdr.match(l))]
print('components',len(starts))
comps=[];bad=[]
for k,(i,kind,name) in enumerate(starts):
    end=starts[k+1][0] if k+1<len(starts) else len(lines)
    blk=lines[i+1:end]
    # find source line
    si=next((j for j,l in enumerate(blk) if re.match(r'^\s*source\s+<xs:',l)),None)
    if si is None: bad.append((kind,name,'nosource')); continue
    src=[re.sub(r'^\s*source\s+','',blk[si])]+blk[si+1:]
    src=[l for l in src if not l.startswith('XML Schema documentation generated')]
    s=' '.join(l.strip() for l in src if l.strip())
    comps.append((kind,name,s))
top=[c for c in comps if '/' not in c[1]]
print('top',len(top),'bad',bad[:5],len(bad))
XS='http://www.w3.org/2001/XMLSchema'
out=[];fail=[]
for kind,name,s in top:
    try:
        el=etree.fromstring('<r xmlns:xs="%s" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:doc="urn:doc" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:tap="http://www.era.europa.eu/schemes/TAPTSI/1.4">%s</r>'%(XS,s))
        assert len(el)==1 and el[0].get('name')==name,(len(el),el[0].get('name'))
        out.append(s)
    except Exception as e: fail.append((kind,name,str(e)[:150]))
print('parsed',len(out),'fail',len(fail))
for f in fail[:30]: print(f)
open('sector_recon.xsd','w',encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<xs:schema xmlns:xs="%s" xmlns="http://www.era.europa.eu/schemes/TAFTSI/3.5" targetNamespace="http://www.era.europa.eu/schemes/TAFTSI/3.5" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:doc="urn:doc" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:tap="http://www.era.europa.eu/schemes/TAPTSI/1.4" elementFormDefault="qualified" attributeFormDefault="unqualified">\n'%XS+'\n'.join(out)+'\n</xs:schema>\n')
