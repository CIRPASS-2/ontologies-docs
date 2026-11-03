"""Record publication-blocker checks after full successful regression runs."""
import collections
import hashlib
import json
import subprocess
from xml.etree import ElementTree as ET
from rdflib import Graph
from rdflib.compare import isomorphic
from migration.finalize_audit_records import inventory_since
from migration.refresh_publication import integrity
from scripts import validate_public as v

ROOT=v.ROOT
BASELINE='1866acd9f998976481dcfaba3b531c016822b87f'


def write(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def record():
    tree=ET.parse(ROOT/'migration/validation-pytest.xml')
    suites=list(tree.getroot().iter('testsuite'))
    counts={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    assert counts==dict(tests=180,failures=0,errors=0,skipped=0),counts
    for suite in suites:suite.attrib.pop('hostname',None)
    (ROOT/'migration/validation-pytest.xml').write_bytes(ET.tostring(tree.getroot(),encoding='utf8',xml_declaration=True)+b'\n')
    protected=('ontology','mireot','dependencies','migration/core-sources','migration/historical',
               'shacl','examples','traceability','widoco/sections','diagrams')
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASELINE,'--',*protected],text=True,cwd=ROOT).splitlines()
    # The three Graphwise reference-only files are verified as committed blobs;
    # their pre-existing working-tree line endings are outside the release contract.
    names=[name for name in names if name not in v.PRESERVED_REFERENCE_MATERIAL]
    hashes={}
    for name in names:
        old=subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)
        current=(ROOT/name).read_bytes()
        assert current==old,name
        hashes[name]=hashlib.sha256(current).hexdigest()
    graphs=0;exports=0
    for source in sorted((ROOT/'ontology').glob('*.ttl')):
        old=subprocess.check_output(['git','show',BASELINE+':ontology/'+source.name],cwd=ROOT)
        graph=Graph().parse(source)
        assert isomorphic(graph,Graph().parse(data=old,format='turtle'))
        graphs+=1
        if source.stem=='textile-ontology':continue
        folder=ROOT/'docs/widoco'/source.stem.removeprefix('textile-')
        for name,fmt in [('ontology.ttl','turtle'),('ontology.owl','xml'),('ontology.nt','nt'),('ontology.jsonld','json-ld')]:
            path=folder/name
            assert path.read_bytes()==subprocess.check_output(['git','show',BASELINE+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
            assert isomorphic(graph,Graph().parse(path,format=fmt)),str(path)
            exports+=1
    changes=subprocess.check_output(['git','diff','--name-only',BASELINE,'--','docs/widoco'],text=True,cwd=ROOT).splitlines()
    assert sorted(changes)==['docs/widoco/connector/sections/crossref-en.html','docs/widoco/context/sections/crossref-en.html'],changes
    before=json.loads((ROOT/'migration/widoco-links-before.json').read_text('utf8'))
    after=json.loads((ROOT/'migration/widoco-links-after.json').read_text('utf8'))
    assert collections.Counter(row['url'] for row in before['errors'])==dict(sourceLocator=20,sourceType=20,typicallyQualifiesProcess=9)
    assert not after['errors']
    keys=('examples_conformant','shacl_scenarios','reasoning_scenarios','rdfs_negative_control')
    modes={}
    for name in ('partial','complete'):
        result=json.loads((ROOT/f'blocker-{name}-result.json').read_text('utf8'))
        modes[name]={key:result[key] for key in keys}
        assert list(modes[name].values())==[11,16,6,'passed']
    result=dict(baseline_commit=BASELINE,candidate='2.0.0',pytest=counts,public_validation_modes=modes,
                canonical_graphs_verified=graphs,canonical_rdf_differences=0,metadata_exclusions=0,
                widoco_exports_isomorphic=exports,widoco_exports_byte_unchanged=exports,
                protected_file_sha256=hashes,protected_files_verified=len(names),
                broken_links_before=len(before['errors']),broken_links_after=0,
                local_only=True,redirects_modified=False)
    write('migration/publication-blocker-results.json',result)
    report=json.loads((ROOT/'migration/validation-results.json').read_text('utf8'))
    report['pytest']=counts;report['public_validation_modes']=modes
    report['publication_blockers']={key:value for key,value in result.items() if key!='protected_file_sha256'}
    write('migration/validation-results.json',report)
    inv=json.loads((ROOT/'migration/change-inventory.json').read_text('utf8'))
    inv['publication_blocker_baseline']=BASELINE
    entries=inventory_since(BASELINE)
    inv['entries_since_publication_blocker_baseline']=entries
    inv['summary_since_publication_blocker_baseline']=dict(sorted(collections.Counter(row['status'] for row in entries).items()))
    write('migration/change-inventory.json',inv)
    integrity()
    report['results']=v.structural_checks(ROOT)
    report['results'].update(modes['complete'])
    write('migration/validation-results.json',report)
    integrity()
    v.structural_checks(ROOT)
    print(json.dumps({k:value for k,value in result.items() if k!='protected_file_sha256'},indent=2))


if __name__=='__main__':record()
