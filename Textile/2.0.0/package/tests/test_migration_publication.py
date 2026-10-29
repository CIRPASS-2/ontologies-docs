"""Changed documentation downloads preserve the canonical semantic graph."""
from pathlib import Path
import json
import pytest
from rdflib import Graph, RDF, OWL
from rdflib.compare import isomorphic

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('module',['assessment','associated-materials','connector','context','core','durability','indicator','process','recyclability','repairability','soc','structure'])
def test_widoco_downloads_match_canonical_graph(module):
    path=ROOT/f'ontology/textile-{module}.ttl'
    folder=ROOT/'docs/widoco'/module
    assert path.read_bytes()==(folder/'ontology.ttl').read_bytes()
    source=Graph().parse(path,format='turtle')
    for name,format_ in [('ontology.owl','xml'),('ontology.nt','nt'),('ontology.jsonld','json-ld')]:
        graph=Graph().parse(folder/name,format=format_)
        assert isomorphic(source,graph),(module,name)
    html=(folder/'index-en.html').read_text('utf8')
    assert str(next(source.objects(None,OWL.versionIRI))) in html
    for creator in ('Elio Hbeich','BOUGACHA Racem','Ivo Ladenius','Andreas Schneider','Jan Merckx','Piero de Sabbata'):
        assert creator in html
    assert 'https://w3id.org/eudpp/soc#' not in html
    editorial=ROOT/f'widoco/sections/{module}/description-en.html'
    assert editorial.read_bytes()==(folder/'sections/description-en.html').read_bytes()


def test_diagrams_and_landing_page_show_migrated_candidate():
    for name in ['textile-soc','textile-associated-materials','textile-recyclability','textile-ontology-network-overview']:
        svg=(ROOT/f'diagrams/{name}.svg').read_text('utf8')
        assert 'https://w3id.org/eudpp/soc#' not in svg
        assert (ROOT/f'diagrams/{name}.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    landing=(ROOT/'docs/widoco/index.html').read_text('utf8')
    assert '2.0.0' in landing and '/1.1.2' not in landing
