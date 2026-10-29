"""Apply owner-approved Option B; compare only explicit ontology-header metadata."""
import hashlib
import json
import re
import subprocess
from rdflib import Graph, RDF, OWL, URIRef
from rdflib.namespace import DCTERMS
from rdflib.compare import isomorphic
from migration.update_creators import semantic_digest
from scripts import validate_public as v

ROOT=v.ROOT
BASELINE='ba6e12ef769d3849bde078ef4f1d32bdcf5e1af1'
REVISION_DATE='2026-10-27'
MODULES=('assessment','connector','context','core','durability','indicator','process','repairability','structure')
PREDICATES=(OWL.versionIRI,OWL.priorVersion,OWL.versionInfo,DCTERMS.modified,DCTERMS.bibliographicCitation)


def project(graph,ontology):
    graph=Graph()+graph
    for predicate in PREDICATES:graph.remove((ontology,predicate,None))
    return graph


def baseline_graph(relative):
    raw=subprocess.check_output(['git','show',BASELINE+':'+relative],cwd=ROOT)
    return Graph().parse(data=raw,format='turtle')


def record():
    rows=[]
    for filename in v.CURRENT_MODULES:
        relative='ontology/'+filename
        before=baseline_graph(relative);after=Graph().parse(ROOT/relative)
        ontology=next(before.subjects(RDF.type,OWL.Ontology))
        left={t for t in before if t[0]==ontology and t[1] in PREDICATES}
        right={t for t in after if t[0]==ontology and t[1] in PREDICATES}
        assert isomorphic(project(before,ontology),project(after,ontology)),relative
        assert set(before.objects(ontology,DCTERMS.creator))==set(after.objects(ontology,DCTERMS.creator))
        changed=filename.removeprefix('textile-').removesuffix('.ttl') in MODULES
        assert bool(left!=right)==changed,relative
        serialize=lambda triples:sorted(' '.join(term.n3() for term in t)+' .' for t in triples)
        rows.append(dict(file=relative,ontology_iri=str(ontology),
                         removed=serialize(left-right),added=serialize(right-left),
                         before_header=serialize(left),after_header=serialize(right),
                         version_iri=str(after.value(ontology,OWL.versionIRI)),
                         prior_version=str(after.value(ontology,OWL.priorVersion)) if after.value(ontology,OWL.priorVersion) else None,
                         non_metadata_graph_sha256=semantic_digest(project(before,ontology))))
    report=dict(baseline_commit=BASELINE,revision_date=REVISION_DATE,owner_decision='Option B',
                allowed_predicates=list(map(str,PREDICATES)),modules=rows,
                removed_triples=sum(len(row['removed']) for row in rows),
                added_triples=sum(len(row['added']) for row in rows),non_metadata_rdf_differences=0,
                creators_preserved=True,candidate='2.0.0')
    (ROOT/'migration/version-identity-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Exact ontology-header changes:',report['removed_triples'],'removed,',report['added_triples'],'added; no other RDF differences')


def update():
    for module in MODULES:
        path=ROOT/f'ontology/textile-{module}.ttl'
        text=path.read_bytes().decode('utf8')
        iri='https://w3id.org/eudpp/textile-'+module
        if f'owl:versionIRI <{iri}/2.0.0>' in text:continue
        text,count=re.subn(r'(    dcterms:modified ")[^"]+("\^\^xsd:date)',r'\g<1>'+REVISION_DATE+r'\2',text)
        assert count==1,path
        text,count=re.subn(r'(    dcterms:bibliographicCitation ")[^\n]+',lambda m:m[0].replace('Version 1.1.2','Version 2.0.0 candidate'),text)
        assert count==1,path
        text,count=re.subn(r'    owl:versionIRI <'+re.escape(iri)+r'/1\.1\.2>',
                          '    owl:priorVersion <'+iri+'/1.1.2> ;\n    owl:versionIRI <'+iri+'/2.0.0>',text)
        assert count==1,path
        text,count=re.subn(r'    owl:versionInfo "Version 1\.1\.2"','    owl:versionInfo "Version 2.0.0 candidate"',text)
        assert count==1,path
        path.write_bytes(text.encode('utf8'))
    record()


if __name__=='__main__':update()
