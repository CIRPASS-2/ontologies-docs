"""Owner-approved creator additions; preserve every other source byte/triple."""
import hashlib
import json
import re
import subprocess
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL
from rdflib.compare import isomorphic, to_canonical_graph, graph_diff, to_isomorphic
from migration import implement_core as m
from scripts import validate_public as v

BASELINE='f527fc577bec246a25d9332df018be6a64ec9070'
ADDITIONS=('Ivo Ladenius','Andreas Schneider','Jan Merckx','Piero de Sabbata')


def semantic_digest(graph):
    text='\n'.join(sorted(' '.join(term.n3() for term in row) for row in to_canonical_graph(graph)))
    return hashlib.sha256(text.encode('utf8')).hexdigest()


def record_comparison():
    rows=[]
    for name in v.CURRENT_MODULES:
        relative='ontology/'+name;path=m.ROOT/relative
        original=subprocess.run(['git','show',BASELINE+':'+relative],cwd=m.ROOT,capture_output=True,check=True).stdout
        before=Graph().parse(data=original,format='turtle');after=m.parse(path)
        ontology=next(before.subjects(RDF.type,OWL.Ontology))
        prior=set(before.objects(ontology,m.DC.creator));current=set(after.objects(ontology,m.DC.creator))
        expected={Literal(name,lang='en') for name in ADDITIONS}
        assert current==prior|expected,(relative,current)
        projected=Graph()+after
        for creator in expected-prior:projected.remove((ontology,m.DC.creator,creator))
        assert isomorphic(before,projected),'Non-creator RDF difference: '+relative
        stripped=Graph()+before;stripped.remove((ontology,m.DC.creator,None))
        rows.append({'file':relative,'ontology_iri':str(ontology),'creators_before':sorted(map(str,prior)),
                     'creators_after':sorted(map(str,current)), 'added_triples':len(expected-prior),
                     'other_rdf_difference':False,'non_creator_graph_sha256':semantic_digest(stripped)})
    record={'baseline_commit':BASELINE,'candidate':'2.0.0','representation':'English language-tagged literal (@en)',
            'intended_additions':list(ADDITIONS),'modules':rows,'added_creator_triples':sum(r['added_triples'] for r in rows),
            'non_creator_rdf_difference':'none; isomorphic after removing only the intended additions',
            'excluded_documentation_annotations':[]}
    (m.ROOT/'migration/creator-update-results.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8',newline='\n')


def update():
    for name in v.CURRENT_MODULES:
        path=m.ROOT/'ontology'/name;graph=m.parse(path)
        ontology=next(graph.subjects(RDF.type,OWL.Ontology))
        missing=[name for name in ADDITIONS if Literal(name,lang='en') not in set(graph.objects(ontology,m.DC.creator))]
        if not missing:continue
        text=path.read_bytes().decode('utf8')
        matches=list(re.finditer(r'(?m)^    dcterms:creator [\s\S]*?;',text))
        assert len(matches)==1,path
        match=matches[0]
        block=match.group()[:-1].rstrip()+',\n'+',\n'.join('        "'+name+'"@en' for name in missing)+' ;'
        path.write_bytes((text[:match.start()]+block+text[match.end():]).encode('utf8'))
    record_comparison()


def record_exports():
    """Owner-approved documentation normalization, separate from source RDF."""
    rows=[]
    for name in v.CURRENT_MODULES:
        if name=='textile-ontology.ttl':continue
        module=name.removeprefix('textile-').removesuffix('.ttl')
        source=m.parse(m.ROOT/'ontology'/name)
        ontology=next(source.subjects(RDF.type,OWL.Ontology))
        original_source=Graph()+source
        for person in ADDITIONS:original_source.remove((ontology,m.DC.creator,Literal(person,lang='en')))
        for filename,format_ in [('ontology.ttl','turtle'),('ontology.owl','xml'),('ontology.nt','nt'),('ontology.jsonld','json-ld')]:
            relative=f'docs/widoco/{module}/{filename}';path=m.ROOT/relative
            old_bytes=subprocess.run(['git','show',BASELINE+':'+relative],cwd=m.ROOT,capture_output=True,check=True).stdout
            before=Graph().parse(data=old_bytes,format=format_)
            after=Graph().parse(path,format=format_)
            assert isomorphic(source,after),'Export differs from canonical source: '+relative
            projected=Graph()+after
            for person in ADDITIONS:projected.remove((ontology,m.DC.creator,Literal(person,lang='en')))
            _,removed,added=graph_diff(to_isomorphic(before),to_isomorphic(projected))
            declarations={OWL.Class,OWL.ObjectProperty,OWL.DatatypeProperty,OWL.AnnotationProperty,OWL.NamedIndividual,RDF.List,RDFS.Datatype}
            serialize=lambda graph:sorted(' '.join(term.n3() for term in row)+' .' for row in graph)
            removed_declarations=Graph();other_removed=Graph()
            for triple in removed:
                (removed_declarations if triple[1]==RDF.type and triple[2] in declarations else other_removed).add(triple)
            rows.append({'file':relative,'before_sha256':hashlib.sha256(old_bytes).hexdigest(),
                'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'before_export_matches_canonical_source':isomorphic(before,original_source),
                'after_export_matches_canonical_source':True,
                'non_creator_difference':not isomorphic(before,projected),
                'removed_serializer_declarations':serialize(removed_declarations),
                'removed_other_export_triples':serialize(other_removed),
                'added_export_triples_excluding_creators':serialize(added)})
    changed=[r for r in rows if r['non_creator_difference']]
    result={'baseline_commit':BASELINE,'owner_authorization':'Include documented export normalization; canonical source graphs remain strictly creator-only.',
        'canonical_semantic_changes':0,'exports_checked':len(rows),'normalized_exports':len(changed),
        'normalized_modules':sorted({r['file'].split('/')[2] for r in changed}),
        'diff_convention':'Exact canonical RDF triple differences after removing only four added creator statements. Blank-node labels are local to each comparison. List reordering/re-serialization can appear as additional anonymous triple differences; these are not changes to canonical ontology axioms.',
        'exports':rows}
    (m.ROOT/'migration/creator-export-differences.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Exports checked:',len(rows),'non-creator export normalizations:',len(changed))


def record_documentation_provenance():
    """Check the directly required creator annotations in WIDOCO provenance."""
    prov=Namespace('http://www.w3.org/ns/prov#');foaf=Namespace('http://xmlns.com/foaf/0.1/')
    rows=[]
    for name in v.CURRENT_MODULES:
        if name=='textile-ontology.ttl':continue
        module=name.removeprefix('textile-').removesuffix('.ttl')
        relative=f'docs/widoco/{module}/provenance/provenance-en.ttl'
        old_bytes=subprocess.run(['git','show',BASELINE+':'+relative],cwd=m.ROOT,capture_output=True,check=True).stdout
        base=f'https://example.org/widoco/{module}/provenance/'
        before=Graph().parse(data=old_bytes,publicID=base,format='turtle')
        after=Graph().parse(data=(m.ROOT/relative).read_bytes(),publicID=base,format='turtle')
        assert set(map(str,before.objects(None,foaf.name)))=={'Elio Hbeich','BOUGACHA Racem'}
        assert set(map(str,after.objects(None,foaf.name)))=={'Elio Hbeich','BOUGACHA Racem',*ADDITIONS}
        projected=[]
        for graph in (before,after):
            clean=Graph()+graph
            for agent in set(graph.subjects(foaf.name,None)):
                assert set(graph.predicates(agent,None))=={RDF.type,foaf.name}
                assert set(graph.objects(agent,RDF.type))=={prov.Agent}
                assert set(graph.predicates(None,agent))=={prov.wasAttributedTo}
                clean.remove((agent,None,None));clean.remove((None,prov.wasAttributedTo,agent))
            projected.append(clean)
        assert isomorphic(*projected),'Non-creator documentation provenance change: '+relative
        _,removed,added=graph_diff(to_isomorphic(before),to_isomorphic(after))
        serialize=lambda graph:sorted(' '.join(term.n3() for term in row)+' .' for row in graph)
        rows.append({'file':relative,'comparison_base_for_relative_agent_iris':base,
            'directly_required_creator_annotations_only':True,
            'removed_documentation_triples':serialize(removed),'added_documentation_triples':serialize(added)})
    path=m.ROOT/'migration/creator-export-differences.json';report=json.loads(path.read_text('utf8'))
    report['documentation_provenance']=rows
    report['documentation_provenance_note']='Creator-derived prov:wasAttributedTo links, prov:Agent declarations and foaf:name values change, including generated agent renumbering. After excluding only those required creator annotations, each documentation provenance graph is isomorphic to its baseline. No canonical ontology annotations were excluded.'
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Documentation provenance checked:',len(rows),'graphs; other differences: 0')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--check-exports',action='store_true')
    if parser.parse_args().check_exports:
        record_exports();record_documentation_provenance()
    else:update()
