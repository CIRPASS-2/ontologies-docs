"""Creator-only graph regression against the accepted correction candidate."""
import json
import re
from rdflib import Graph, Literal, URIRef
from migration import implement_core as m
from migration.update_creators import semantic_digest


def test_all_thirteen_graphs_preserve_every_non_creator_triple():
    report=json.loads((m.ROOT/'migration/creator-update-results.json').read_text('utf8'))
    assert len(report['modules'])==13 and report['added_creator_triples']==52
    assert report['excluded_documentation_annotations']==[]
    revision=json.loads((m.ROOT/'migration/version-identity-results.json').read_text('utf8'))
    revisions={row['file']:row for row in revision['modules']}
    for row in report['modules']:
        path=m.ROOT/row['file'];graph=m.parse(path);ontology=URIRef(row['ontology_iri'])
        assert set(graph.objects(ontology,m.DC.creator))=={Literal(name,lang='en') for name in row['creators_after']}
        assert set(row['creators_before'])=={'Elio Hbeich','BOUGACHA Racem'}
        # Retain the original frozen creator proof by reversing only the exact
        # subsequent owner-approved header changes (independently checked below).
        change=revisions[row['file']]
        for triple in Graph().parse(data='\n'.join(change['added']),format='turtle'):
            assert triple in graph
            graph.remove(triple)
        for triple in Graph().parse(data='\n'.join(change['removed']),format='turtle'):graph.add(triple)
        graph.remove((ontology,m.DC.creator,None))
        assert semantic_digest(graph)==row['non_creator_graph_sha256'],row['file']
        block=re.search(r'(?m)^    dcterms:creator [\s\S]*?;',path.read_text('utf8')).group()
        creators=re.findall(r'"([^"]+)"@en',block)
        assert len(creators)==len(set(creators))==6
