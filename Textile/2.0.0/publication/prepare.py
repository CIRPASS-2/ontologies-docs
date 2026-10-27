"""Assemble only approved committed assets; edit only Textile portal regions."""
import argparse, hashlib, json, re, subprocess
from html import escape
from urllib.parse import quote
from pathlib import Path
from rdflib import Graph, RDF, OWL, SKOS, URIRef
from rdflib.namespace import DCTERMS

ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'Textile/2.0.0'
SHA='a2bc2642627bf9223b1e39dc54a4e45c233e9232'
BASE='5c76af4448093cdc9e57d2bb3bfdf1416b8876eb'
PUBLIC='https://cirpass-2.github.io/ontologies-docs/'
MODULES=('assessment','associated-materials','connector','context','core','durability','indicator','process','recyclability','repairability','soc','structure')

def git(*args,cwd=ROOT):
    return subprocess.check_output(['git',*args],cwd=cwd)

def baseline(name):return git('show',BASE+':'+name).decode('utf8')

def portal_regions(text,name):
    if name=='index.html':
        patterns=[r'<tr><td><a href="Textile/[^\"]+">Textile(?: 2\.0\.0)?</a>.*?</tr>',
                  r'<section id="textile">.*?</section>',
                  r'<tr class="group"><th colspan="2">Textile(?: 2\.0\.0)?</th></tr>.*?(?=    </tbody>)']
    else:
        patterns=[r'<tr class="group"><td colspan="7">Textile(?: 2\.0\.0)?(?: sectoral ontology)?</td></tr>.*?(?=</tbody>)']
    regions=[]
    for pattern in patterns:
        matches=list(re.finditer(pattern,text,re.S));assert len(matches)==1,(name,pattern,len(matches))
        regions.append((matches[0].start(),matches[0].end()))
    return regions

def outside_regions(text,name):
    for start,end in reversed(portal_regions(text,name)):text=text[:start]+'<!-- Textile region -->'+text[end:]
    return text

def metadata(module):
    graph=Graph().parse(DEST/f'package/ontology/textile-{module}.ttl')
    ontology=URIRef('https://w3id.org/eudpp/textile-'+module)
    title=str(graph.value(ontology,DCTERMS.title))
    cats=[{s for s in graph.subjects(RDF.type,t) if isinstance(s,URIRef)} for t in (OWL.Class,OWL.ObjectProperty,OWL.DatatypeProperty)]
    individuals=set(graph.subjects(RDF.type,OWL.NamedIndividual))|set(graph.subjects(RDF.type,SKOS.Concept))
    individuals-=set().union(*cats)
    return title,[len(group) for group in cats]+[len(individuals)]

def current_rows(columns):
    if columns==7:
        rows=['<tr><td><a href="Textile/2.0.0/index.html"><strong>Textile Ontology 2.0.0</strong></a><div class="desc">Network landing page: twelve documented modules plus the umbrella ontology; source PR #19.</div></td><td>2.0.0 candidate</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td>Module graphs below</td></tr>']
        for module in MODULES:
            title,counts=metadata(module)
            rows.append('<tr><td><a href="Textile/2.0.0/'+module+'/index-en.html">'+escape(title)+'</a></td><td>2.0.0 candidate</td>'+''.join('<td class="n">'+str(n)+'</td>' for n in counts)+'<td><a href="Textile/2.0.0/'+module+'/webvowl/index.html">WebVOWL</a></td></tr>')
    elif columns==2:
        rows=['      <tr><td><a href="Textile/2.0.0/index.html">Textile Ontology 2.0.0</a></td><td>Network landing page and source package aligned to the October 2026 CORE baseline.</td></tr>']
        rows+=['      <tr><td><a href="Textile/2.0.0/'+module+'/index-en.html">Textile '+escape(module.replace('-',' '))+'</a></td><td>2.0.0 candidate; <a href="Textile/2.0.0/'+module+'/webvowl/index.html">WebVOWL</a>.</td></tr>' for module in MODULES]
    return '\n'.join(rows)

NOTICE='''Textile 2.0.0 aligns to the owner-adopted October 2026 CORE baseline, including SOC 2.2.0 in <code>https://w3id.org/eudpp#</code>. Its seven package-specific MIREOT resources (SOC, CON, P_DPP, EVENT, ACTOR, MAT and unchanged SI) are bounded subsets, distinct from the independently published CORE pages. Persistent Textile IRI resolution under <code>w3id.org/eudpp</code> is pending separate CIRPASS-2 and namespace-maintainer coordination; this documentation does not deploy redirects or content negotiation.'''

MIREOT_LINKS='Package-specific MIREOT Turtle: '+', '.join('<a href="Textile/2.0.0/package/mireot/'+filename+'-textile-mireot.ttl">'+label+'</a>' for filename,label in [('actor','ACTOR'),('con','CON'),('dpp','P_DPP'),('event','EVENT'),('mat','MAT'),('soc','SOC'),('si','SI')])

def update_portals():
    name='index.html';original=baseline(name);regions=portal_regions(original,name)
    old_section=original[regions[1][0]:regions[1][1]]
    old_table=re.search(r'<table class="data numbered" id="tab-textile">.*?</table>',old_section,re.S).group()
    legacy_table=old_table.replace('id="tab-textile"','id="tab-textile-1-1-2"').replace('Modules of the textile ontology.','Historical Textile 1.1.2 modules (preserved).')
    replacements=[
        '<tr><td><a href="Textile/2.0.0/index.html">Textile 2.0.0</a></td><td>Bounded October 2026 CORE MIREOT alignment.</td><td>'+NOTICE+' <a href="Textile/2.0.0/package/docs/DEPENDENCIES.md">Package dependency sources and attribution</a>. <a href="Textile/textile-ontology/index-en.html">Historical Textile 1.1.2</a> remains available.</td></tr>',
        '''<section id="textile">
    <h3>Textile</h3>
    <p><a href="Textile/2.0.0/index.html"><strong>Textile Ontology 2.0.0</strong></a> documents the validated source candidate in <a href="https://github.com/CIRPASS-2/ontologie-textiles/pull/19">source PR #19</a>. It retains twelve sector modules and an umbrella ontology, with distinct 2.0.0 version identities for all thirteen graphs.</p>
    <p>'''+NOTICE+'''</p>
    <p><a href="Textile/2.0.0/package/catalog-v001.xml">Current package catalogue</a> &middot; <a href="Textile/2.0.0/package/mireot/">Package-specific MIREOT Turtle files</a> &middot; <a href="Textile/2.0.0/package/docs/CORE_2026_MIGRATION.md">Migration guidance</a> &middot; <a href="Textile/2.0.0/package/LICENSE.md">Textile licence and source notices</a> &middot; <a href="Textile/2.0.0/package/docs/TEXTILE_IRI_RESOLVER_COORDINATION_2.0.0.md">Resolver coordination</a></p>
    <table class="data numbered" id="tab-textile">
      <caption>Textile Ontology 2.0.0 module documentation.</caption>
      <thead><tr><th>Module</th><th>Version</th><th>Scope</th></tr></thead><tbody>
'''+ '\n'.join('<tr><td><a href="Textile/2.0.0/'+module+'/index-en.html">'+escape(module.replace('-',' ').title())+'</a></td><td>2.0.0 candidate</td><td>Textile '+escape(module.replace('-',' '))+' module.</td></tr>' for module in MODULES)+'''
      </tbody></table>
    <h4>Historical Textile 1.1.2</h4>
    <p>The previous documentation and its complete-vocabulary reading view remain unchanged. <a href="Textile/textile-ontology/index-en.html">Open the historical umbrella page</a>. Reproducible historical ontology loading uses the separate <a href="Textile/2.0.0/package/migration/historical/1.1.2/catalog-v001.xml">preserved historical catalogue</a>; the legacy draft SOC namespace in those pages does not describe the current 2.0.0 model.</p>
'''+legacy_table+'''
    <p><a href="Textile/textile-ontology-complete/index-en.html">Historical Textile 1.1.2 complete vocabulary</a> remains a reading view, not a new 2.0.0 merged ontology.</p>
  </section>''',
        '<tr class="group"><th colspan="2">Textile 2.0.0</th></tr>\n'+current_rows(2)+'\n'+original[regions[2][0]:regions[2][1]].replace('>Textile</th>','>Historical Textile 1.1.2</th>',1)
    ]
    text=original
    for (start,end),replacement in reversed(list(zip(regions,replacements))):text=text[:start]+replacement+text[end:]
    assert outside_regions(original,name)==outside_regions(text,name)
    text=text.replace('<a href="Textile/2.0.0/package/mireot/">Package-specific MIREOT Turtle files</a>',MIREOT_LINKS).replace('<a href="Textile/2.0.0/package/mireot/">Package-specific MIREOT files</a>',MIREOT_LINKS)
    (ROOT/name).write_bytes(text.encode('utf8'))
    name='ontologies.html';original=baseline(name);start,end=portal_regions(original,name)[0]
    old=original[start:end]
    new='<tr class="group"><td colspan="7">Textile 2.0.0</td></tr>\n<tr><td colspan="7"><p>'+NOTICE+'</p><p><a href="Textile/2.0.0/package/docs/DEPENDENCIES.md">Package dependencies and source notices</a> &middot; <a href="Textile/2.0.0/package/mireot/">Package-specific MIREOT files</a> &middot; <a href="Textile/2.0.0/package/LICENSE.md">Textile licensing</a>. The original catalogue dated above is retained below, including all historical Textile 1.1.2 links.</p></td></tr>\n'+current_rows(7)+'\n'+old.replace('>Textile sectoral ontology</td>','>Historical Textile 1.1.2</td>',1)
    text=original[:start]+new+original[end:]
    assert outside_regions(original,name)==outside_regions(text,name)
    text=text.replace('<a href="Textile/2.0.0/package/mireot/">Package-specific MIREOT Turtle files</a>',MIREOT_LINKS).replace('<a href="Textile/2.0.0/package/mireot/">Package-specific MIREOT files</a>',MIREOT_LINKS)
    (ROOT/name).write_bytes(text.encode('utf8'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);args=parser.parse_args()
    source=args.source.resolve();assert git('rev-parse','HEAD').decode().strip()==BASE
    assert git('branch','--show-current').decode().strip()=='docs/textile-2.0.0'
    tree=git('ls-tree','-r','--name-only',SHA,cwd=source).decode().splitlines()
    manifest=git('show',SHA+':PUBLICATION_MANIFEST.txt',cwd=source).decode('utf8')
    sections={};section=None
    for line in manifest.splitlines():
        if not line or line.startswith('#'):continue
        if line.startswith('['):section=line[1:-1];sections[section]=[]
        else:sections[section].append(line)
    mappings=[]
    for path in tree:
        if path.startswith('docs/widoco/'):mappings.append((path,'Textile/2.0.0/'+path[len('docs/widoco/'):],'widoco'))
        if path.startswith('diagrams/'):mappings.append((path,'Textile/2.0.0/'+path,'diagrams'))
    for section in ('CURRENT_PACKAGE','PRESERVED_REFERENCE_MATERIAL'):
        for path in sections[section]:mappings.append((path,'Textile/2.0.0/package/'+path,section))
    needed=sorted({row[0] for row in mappings});assert 'migration/PUBLICATION_PLAN_2.0.0.md' not in needed
    batch=''.join(SHA+':'+path+'\n' for path in needed).encode()
    raw=subprocess.run(['git','cat-file','--batch'],cwd=source,input=batch,capture_output=True,check=True).stdout
    blobs={};position=0
    for path in needed:
        end=raw.index(b'\n',position);header=raw[position:end].split();assert header[1]==b'blob'
        size=int(header[2]);blobs[path]=raw[end+1:end+1+size];position=end+size+2
    rows=[]
    for src,dst,category in sorted(mappings,key=lambda row:row[1]):
        path=ROOT/dst;data=blobs[src];assert path.resolve().is_relative_to(DEST.resolve())
        if path.exists():assert path.read_bytes()==data,'Refuse to overwrite different asset: '+dst
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        rows.append(dict(source=src,destination=dst,category=category,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),expected_url=PUBLIC+quote(dst,safe='/')))
    contract=blobs['SHA256SUMS'].decode().splitlines()
    assert contract==[hashlib.sha256(blobs[path]).hexdigest()+'  '+path for path in sections['CURRENT_PACKAGE'] if path!='SHA256SUMS']
    assert len({row['destination'] for row in rows})==len(rows)
    (DEST/'.gitattributes').write_text('# Preserve committed source bytes, including historical references.\n* -text\n',encoding='utf8',newline='\n')
    counts={category:sum(row['category']==category for row in rows) for category in ('widoco','diagrams','CURRENT_PACKAGE','PRESERVED_REFERENCE_MATERIAL')}
    inventory=dict(source_repository='https://github.com/CIRPASS-2/ontologie-textiles',source_commit=SHA,source_pr='https://github.com/CIRPASS-2/ontologie-textiles/pull/19',documentation_baseline=BASE,pages_source=dict(branch='main',path='/',build_type='legacy'),expected_base_url=PUBLIC+'Textile/2.0.0/',counts=counts,transfer_files=len(rows),transfer_bytes=sum(row['bytes'] for row in rows),package_files=counts['CURRENT_PACKAGE']+counts['PRESERVED_REFERENCE_MATERIAL'],package_bytes=sum(row['bytes'] for row in rows if row['category'] in ('CURRENT_PACKAGE','PRESERVED_REFERENCE_MATERIAL')),files=rows)
    (DEST/'publication/transfer-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf8',newline='\n')
    update_portals()
    print(json.dumps({key:value for key,value in inventory.items() if key!='files'},indent=2))

if __name__=='__main__':main()