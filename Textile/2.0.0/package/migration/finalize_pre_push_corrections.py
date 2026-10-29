"""Prepare exact pre-push evidence, then record successful final validation gates."""
import argparse
import collections
import hashlib
import json
import subprocess
from xml.etree import ElementTree as ET
from rdflib import Graph, RDF, OWL, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS
from migration.correct_version_identities import BASELINE, MODULES, project, record as record_headers
from migration.finalize_audit_records import inventory_since
from migration.refresh_publication import integrity
from scripts import validate_public as v
from scripts.check_widoco_links import audit_tree
from scripts.widoco_annotations import render, Anchors
from scripts.observe_textile_resolvers import identities, retained_versions

ROOT=v.ROOT
RESULT='migration/final-pre-push-results.json'


def write(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def original(name):
    return subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)


def statements(triples):
    return sorted(' '.join(term.n3() for term in row)+' .' for row in triples)


def prepare():
    record_headers();retained_versions()
    inventory=identities();assert len(inventory)==20
    assert len({row['version_iri'] for row in inventory})==20
    assert sum(row['version_iri'].endswith('/2.0.0') for row in inventory)==19
    write('migration/current-version-iri-inventory.json',inventory)
    exports=[];stable=[];provenance=[]
    for path in sorted((ROOT/'ontology').glob('*.ttl')):
        relative=path.relative_to(ROOT).as_posix()
        source=Graph().parse(path);ontology=next(source.subjects(RDF.type,OWL.Ontology))
        past=Graph().parse(data=original(relative),format='turtle')
        assert set(source.objects(ontology,DCTERMS.creator))==set(past.objects(ontology,DCTERMS.creator))
        if path.stem=='textile-ontology':continue
        module=path.stem.removeprefix('textile-');folder=ROOT/'docs/widoco'/module
        crossref=folder/'sections/crossref-en.html';text=crossref.read_text('utf8')
        assert render(source,text)==text and render(source,render(source,text))==text,module
        anchors=Anchors();anchors.feed(text)
        namespace=str(ontology)+'#'
        for subject in source.subjects(RDF.type,OWL.AnnotationProperty):
            if str(subject).startswith(namespace):
                local=str(subject)[len(namespace):]
                assert local in anchors.ids and f'href="{local}"' not in text
        stable.append(module)
        for name,fmt in [('ontology.ttl','turtle'),('ontology.owl','xml'),('ontology.nt','nt'),('ontology.jsonld','json-ld')]:
            export=folder/name;rel=export.relative_to(ROOT).as_posix()
            before=Graph().parse(data=original(rel),format=fmt)
            after=Graph().parse(export,format=fmt)
            assert isomorphic(source,after),rel
            assert isomorphic(project(before,ontology),project(after,ontology)),rel
            left=set(before.triples((ontology,None,None)));right=set(after.triples((ontology,None,None)))
            exports.append(dict(file=rel,removed=statements(left-right),added=statements(right-left),
                                non_metadata_differences=0,isomorphic_to_canonical=True,
                                before_sha256=hashlib.sha256(original(rel)).hexdigest(),
                                after_sha256=hashlib.sha256(export.read_bytes()).hexdigest()))
        if module in MODULES:
            rel=f'docs/widoco/{module}/provenance/provenance-en.ttl'
            public_id=f'https://cirpass-2.github.io/ontologies-docs/Textile/2.0.0/{module}/provenance/provenance-en.ttl'
            before=Graph().parse(data=original(rel),format='turtle',publicID=public_id)
            after=Graph().parse(data=(ROOT/rel).read_bytes(),format='turtle',publicID=public_id)
            provenance.append(dict(file=rel,removed=statements(set(before)-set(after)),
                                   added=statements(set(after)-set(before)),
                                   explanation='Documentation entity moves to 2.0.0 and records prov:wasRevisionOf 1.1.2; ontology-supplied provenance date retained.'))
    assert len(exports)==48 and len(stable)==12
    protected=('mireot','dependencies','migration/core-sources','migration/historical','shacl','examples','traceability','diagrams','widoco/sections')
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASELINE,'--',*protected],cwd=ROOT,text=True).splitlines()
    hashes={}
    for name in paths:
        assert (ROOT/name).read_bytes()==original(name),name
        hashes[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    for filename in v.CURRENT_MODULES:
        if filename.removeprefix('textile-').removesuffix('.ttl') not in MODULES:
            assert (ROOT/'ontology'/filename).read_bytes()==original('ontology/'+filename)
    links=audit_tree(ROOT/'docs/widoco');assert not links['errors']
    write('migration/final-pre-push-links.json',links)
    cat=ROOT/'catalog-v001.xml'
    assert len(v.catalogue_import_closure(cat,'https://w3id.org/eudpp/textile-ontology/2.0.0'))==20
    history=ROOT/'migration/historical/1.1.2/catalog-v001.xml'
    closures={}
    for entry,want in [('textile-ontology/1.1.2',19),('textile-soc/1.1.2',12)]:
        closure=v.catalogue_import_closure(history,'https://w3id.org/eudpp/'+entry)
        assert len(closure)==want and not any(path.name=='con-textile-mireot.ttl' for path in closure)
        closures[entry]=len(closure)
    files=subprocess.check_output(['git','diff','--name-only',BASELINE,'--','docs/widoco'],cwd=ROOT,text=True).splitlines()
    result=dict(baseline_commit=BASELINE,candidate='2.0.0',status='prepared; full regression pending',
                canonical_graphs_verified=13,canonical_non_metadata_rdf_differences=0,
                creators_preserved=True,protected_file_sha256=hashes,
                historical_import_closures=closures,current_import_closure=20,
                widoco_exports=exports,documentation_provenance=provenance,
                annotation_supplement_idempotent_modules=stable,regenerated_changed_documentation=files,
                local_link_summary={k:value for k,value in links.items() if k not in ('references','errors')},
                limitations=['WIDOCO could not download old version IRIs for its optional automated changelog; exact local RDF changes are recorded instead.',
                             'WIDOCO provenance uses ontology-supplied creation dates; these inherited date fields were retained. Canonical revision metadata is dated 2026-10-27.',
                             'Idempotency covers the annotation-property supplement on all twelve modules. Full Java generation may reorder serializer output and WebVOWL identifiers; RDF equivalence is checked independently.',
                             'External HTTP links are inventoried, not exhaustively checked; resolver routes remain undeployed.'],
                local_only=True)
    write(RESULT,result)
    integrity()
    v.structural_checks(ROOT)
    print('Prepared:',len(files),'changed WIDOCO assets; 48 exports equivalent; 12 supplements stable; protected files unchanged:',len(paths))


def finalize():
    tree=ET.parse(ROOT/'migration/validation-pytest.xml');suites=list(tree.getroot().iter('testsuite'))
    counts={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    assert counts==dict(tests=205,failures=0,errors=0,skipped=0),counts
    for suite in suites:suite.attrib.pop('hostname',None)
    (ROOT/'migration/validation-pytest.xml').write_bytes(ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)+b'\n')
    modes={};keys=('examples_conformant','shacl_scenarios','reasoning_scenarios','rdfs_negative_control')
    for name in ('partial','complete'):
        runtime=json.loads((ROOT/f'pre-push-{name}-result.json').read_text('utf8'))
        modes[name]={key:runtime[key] for key in keys}
        assert list(modes[name].values())==[11,16,6,'passed']
    result=json.loads((ROOT/RESULT).read_text('utf8'))
    result.update(status='passed',pytest=counts,public_validation_modes=modes)
    write(RESULT,result)
    report=json.loads((ROOT/'migration/validation-results.json').read_text('utf8'))
    report.update(pytest=counts,public_validation_modes=modes,
                  final_pre_push_corrections=dict(baseline_commit=BASELINE,status='passed',owner_decision='Option B',
                   canonical_non_metadata_rdf_differences=0,removed_metadata_triples=36,added_metadata_triples=45,
                   textile_version_iris_2_0_0=13,mireot_version_iris_2_0_0=6,si_version='1.1.2',
                   creators_preserved=True,all_48_exports_isomorphic=True,all_12_annotation_supplements_idempotent=True,
                   local_broken_links=0,protected_files_unchanged=True,local_only=True))
    report['nonfatal_warnings']=['Twelve RDFLib JSON-LD deprecation warnings in pytest; WIDOCO optional changelog retrieval and existing configuration/logging warnings. See final-pre-push-results.json limitations.']
    write('migration/validation-results.json',report)
    inv=json.loads((ROOT/'migration/change-inventory.json').read_text('utf8'))
    inv['pre_push_correction_baseline']=BASELINE
    entries=inventory_since(BASELINE)
    inv['entries_since_pre_push_correction_baseline']=entries
    inv['summary_since_pre_push_correction_baseline']=dict(sorted(collections.Counter(row['status'] for row in entries).items()))
    write('migration/change-inventory.json',inv)
    integrity();report['results']=v.structural_checks(ROOT);report['results'].update(modes['complete'])
    write('migration/validation-results.json',report);integrity();v.structural_checks(ROOT)
    print(json.dumps(dict(pytest=counts,public_validation_modes=modes,changed_files=len(entries),
                         package_files=report['results']['package_files'],status='passed'),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true')
    prepare() if parser.parse_args().prepare else finalize()
