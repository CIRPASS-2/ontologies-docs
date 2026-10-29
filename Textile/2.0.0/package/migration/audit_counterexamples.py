"""Reproduce Claude CE6/7/8 using accepted and corrected full RDF/SHACL.

Git is used only to read the accepted audit input, never to change the worktree.
The independent regression tests use current files without needing Git.
"""
import json
import subprocess
from rdflib import Graph, Namespace, URIRef, RDF, RDFS
from rdflib.namespace import SH, SKOS
from pyshacl import validate
from migration import implement_core as m

ACCEPTED='5bac1a2cba2332b3e5ad7d45d305fbb786ee59f2'
EX=Namespace('https://example.org/textile-soc/')


def mutate(graph,case):
    if case=='CE6':
        graph.remove((EX.presence,m.T.hasThresholdEvaluation,EX.thresholdEvaluation))
        graph.add((EX.otherPresence,m.T.hasThresholdEvaluation,EX.thresholdEvaluation))
    elif case=='CE7':
        graph.remove((EX.jacket,m.T.hasPart,EX.outerFabricMaterialGroup))
        graph.add((EX.outerFabricMaterialGroup,m.T.isPartOfProduct,EX.jacket))
    elif case=='CE8':
        graph.add((EX.zipper,RDF.type,m.A.NonTextileComponent))
        graph.add((EX.jacket,m.A.hasNonTextileComponent,EX.zipper))
        graph.set((EX.locationInformation,m.T.refersToProductPartForLocation,EX.zipper))
        graph.set((EX.locationInformation,m.T.hasTextileLocationType,m.T.nonTextileComponentLocation))
    else:raise ValueError(case)
    return graph


def accepted_graph(path):
    data=subprocess.run(['git','show',ACCEPTED+':'+path.relative_to(m.ROOT).as_posix()],cwd=m.ROOT,check=True,capture_output=True).stdout
    return Graph().parse(data=data,format='turtle')


def reproduce():
    result={}
    for label,loader in [('accepted',accepted_graph),('corrected',m.parse)]:
        ontology=Graph();shapes=Graph()
        for folder in ('ontology','mireot'):
            for path in (m.ROOT/folder).glob('*.ttl'):ontology+=loader(path)
        for path in (m.ROOT/'shacl').glob('*.ttl'):shapes+=loader(path)
        base=loader(m.ROOT/'tests/abox_corpus/fixtures/valid/V09-soc-migration-coverage.ttl')
        rows={}
        for case in ('CE6','CE7','CE8'):
            data=mutate(Graph()+base,case)
            ok,report,_=validate(ontology+data,shacl_graph=shapes,inference='rdfs',advanced=True,do_owl_imports=False)
            rows[case]={'conforms':bool(ok),'results':sorted([{'focus_node':str(report.value(r,SH.focusNode)),
                'source_shape':str(report.value(r,SH.sourceShape)),
                'source_constraint':str(report.value(r,SH.sourceConstraint))} for r in report.subjects(RDF.type,SH.ValidationResult)],key=lambda x:json.dumps(x,sort_keys=True))}
            print(label,case,ok,flush=True)
        result[label]=rows
    assert [result['accepted'][c]['conforms'] for c in ('CE6','CE7','CE8')]==[True,False,False]
    assert [result['corrected'][c]['conforms'] for c in ('CE6','CE7','CE8')]==[False,True,True]
    (m.ROOT/'migration/audit-counterexample-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')


def verify_accepted_attribution():
    before=accepted_graph(m.ROOT/'ontology/textile-soc.ttl')
    old=m.parse(m.HISTORY/'dependencies/soc.ttl')
    matches=[]
    for subject in sorted(set(before.subjects())):
        if not isinstance(subject,URIRef) or not str(subject).startswith(str(m.T)):continue
        source=m.OLD[str(subject).split('#')[-1]]
        statements=[{'predicate':str(p),'text':str(o),'language':o.language} for p in (SKOS.definition,RDFS.comment) for o in before.objects(subject,p) if (source,p,o) in old]
        if statements:
            assert set(before.objects(subject,m.DC.source))=={m.PROJECT}
            assert set(before.objects(subject,m.C.sourceType))=={m.C.projectDecision}
            matches.append({'resource_iri':str(subject),'source_resource':str(source),'matching_statements':statements,'before_source':str(m.PROJECT),'before_category':'projectDecision'})
    current=json.loads((m.ROOT/'migration/legacy-soc-attribution.json').read_text('utf8'))
    assert len(matches)==42
    assert {row['resource_iri'] for row in matches}=={row['resource_iri'] for row in current}
    (m.ROOT/'migration/attribution-baseline-evidence.json').write_text(json.dumps({'accepted_commit':ACCEPTED,'resources':matches},indent=2)+'\n',encoding='utf8',newline='\n')


if __name__=='__main__':
    verify_accepted_attribution()
    reproduce()
