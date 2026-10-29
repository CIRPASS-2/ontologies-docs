"""Publish equivalent RDF downloads from the canonical module graph.

WIDOCO's independent serializers can add declaration triples differently.
Keep its generated HTML/WebVOWL, but use canonical source RDF for downloads.
"""
from pathlib import Path
import sys
from rdflib import Graph
from rdflib.compare import to_canonical_graph

ROOT=Path(__file__).resolve().parents[1]


def sync(module):
    path=ROOT/f'ontology/textile-{module}.ttl'
    source=Graph().parse(path,format='turtle')
    canonical=Graph()
    for prefix,namespace in source.namespaces():canonical.bind(prefix,namespace)
    for triple in sorted(to_canonical_graph(source),key=lambda row:tuple(t.n3() for t in row)):
        canonical.add(triple)
    folder=ROOT/'docs/widoco'/module
    (folder/'ontology.ttl').write_bytes(path.read_bytes())
    canonical.serialize(folder/'ontology.owl',format='xml')
    (folder/'ontology.nt').write_text(''.join(sorted(canonical.serialize(format='nt').splitlines(keepends=True))),encoding='utf8',newline='\n')
    canonical.serialize(folder/'ontology.jsonld',format='json-ld')
    print('Canonical RDF downloads synchronised:',module)


if __name__=='__main__':
    for module in sys.argv[1:]:sync(module)
