"""Approved MAT bridge: class-wide inference, property inference and boundaries."""
import json
import hashlib
from rdflib import Graph, RDF, RDFS, SKOS, Namespace, OWL, Literal, URIRef
from rdflib.namespace import DCTERMS, XSD
from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics
from pyshacl import validate
import pytest
from migration import mat_alignment as m

EX = Namespace('https://example.org/eu-dpp-textile/')


@pytest.fixture(scope='module', params=[RDFS_Semantics, OWLRL_Semantics], ids=['RDFS', 'OWL-RL'])
def model(request):
    graph = m.closure() + Graph().parse(m.ROOT / 'examples/example-01-product-composition-v1.1.2.ttl')
    DeductiveClosure(request.param).expand(graph)
    return graph


def test_exact_approved_delta_and_no_other_canonical_changes():
    rows = m.canonical_differences()
    assert len(rows) == 13
    assert sum(len(row['added']) for row in rows) == 7
    assert sum(len(row['removed']) for row in rows) == 6


@pytest.mark.parametrize('fault', [
    'extra-class', 'extra-property', 'extra-subclass', 'remove-unrelated',
    'wrong-date', 'wrong-note', 'missing-mat-class', 'missing-mat-property',
    'creator-change', 'restore-closeMatch',
])
def test_exact_delta_rejects_unauthorized_changes(fault):
    module = 'connector' if fault == 'restore-closeMatch' else 'core'
    relative = f'ontology/textile-{module}.ttl'
    graph = Graph().parse(m.ROOT / relative)
    m.restore_frozen_graph(graph, relative)  # The unmodified candidate is accepted.
    if fault == 'extra-class':
        graph.add((EX.unauthorized, RDF.type, OWL.Class))
    elif fault == 'extra-property':
        graph.add((EX.unauthorized, RDF.type, OWL.ObjectProperty))
    elif fault == 'extra-subclass':
        graph.add((m.TXT.TextileProduct, RDFS.subClassOf, m.DPP.MaterialOfComposition))
    elif fault == 'remove-unrelated':
        graph.remove(next(graph.triples((None, RDF.type, SKOS.Concept))))
    elif fault == 'wrong-date':
        graph.set((URIRef('https://w3id.org/eudpp/textile-core'), DCTERMS.modified,
                   Literal('2026-11-03', datatype=XSD.date)))
    elif fault == 'wrong-note':
        graph.set((m.TXT.hasFibreCompositionComponent,
                   Namespace('https://w3id.org/eudpp/textile-connector#').modellingNote,
                   Literal('Unapproved wording', lang='en')))
    elif fault == 'missing-mat-class':
        graph.remove((m.TXT.FibreTypeConcept, RDFS.subClassOf, m.DPP.MaterialType))
    elif fault == 'missing-mat-property':
        graph.remove((m.TXT.hasFibreType, RDFS.subPropertyOf, m.DPP.hasMaterialType))
    elif fault == 'creator-change':
        graph.add((URIRef('https://w3id.org/eudpp/textile-core'), DCTERMS.creator,
                   Literal('Unapproved creator', lang='en')))
    else:
        graph.add((SKOS.closeMatch, RDF.type, OWL.AnnotationProperty))
    with pytest.raises(AssertionError, match='Unauthorized canonical RDF difference'):
        m.restore_frozen_graph(graph, relative)


def test_frozen_external_inputs_catalogue_and_history_are_unchanged():
    assert len(m.protected_hashes()) == 76


def test_all_fibre_concepts_are_mat_material_types(model):
    canonical = Graph().parse(m.ROOT / 'ontology/textile-core.ttl')
    concepts = set(canonical.subjects(RDF.type, m.TXT.FibreTypeConcept))
    assert len(concepts) == 22
    assert concepts <= set(model.subjects(RDF.type, m.DPP.MaterialType))


def test_fibre_type_assertions_entail_mat_classifications(model):
    edges = list(model.subject_objects(m.TXT.hasFibreType))
    assert len(edges) == 2
    assert all((s, m.DPP.hasMaterialType, o) in model for s, o in edges)


def test_skos_typing_is_preserved(model):
    assert set(model.subjects(RDF.type, m.TXT.FibreTypeConcept)) <= set(model.subjects(RDF.type, SKOS.Concept))


def test_composition_entries_remain_mat_materials(model):
    assert (m.TXT.FibreCompositionComponent, RDFS.subClassOf, m.DPP.MaterialOfComposition) in model
    for entry in ['composition-cotton-95', 'composition-elastane-5']:
        assert (EX[entry], RDF.type, m.DPP.MaterialOfComposition) in model


def test_owning_product_does_not_become_material_occurrence(model):
    assert (EX['tshirt-001'], RDF.type, m.TXT.TextileProduct) in model
    assert (EX['tshirt-001'], RDF.type, m.DPP.MaterialOfComposition) not in model


def test_product_to_entry_property_has_no_mat_type_alignment(model):
    assert (m.TXT.hasFibreCompositionComponent, RDFS.subPropertyOf, m.DPP.hasMaterialType) not in model
    assert not list(model.triples((EX['tshirt-001'], m.DPP.hasMaterialType, None)))


def test_historical_ontology_bytes_are_unchanged():
    inventory = json.loads((m.ROOT / 'migration/historical/inventory.json').read_text('utf8'))
    for name, digest in inventory['files'].items():
        if name.startswith('ontology/'):
            path = m.ROOT / 'migration/historical/1.1.2' / name
            if path.exists(): assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name


@pytest.mark.parametrize('complete', [False, True], ids=['default', 'complete-report'])
def test_public_example_shacl_results_are_preserved(complete):
    graph = m.closure()
    examples = sum((Graph().parse(p) for p in (m.ROOT / 'examples').glob('*.ttl')), Graph())
    shapes = sum((Graph().parse(p) for p in (m.ROOT / 'shacl').glob('*.ttl')), Graph())
    if complete:
        shapes += Graph().parse(m.ROOT / 'shacl/profiles/textile-soc-complete-report.ttl')
    from rdflib.namespace import SH
    for ontology in [m.without_alignment(graph), graph]:
        ok, report, _ = validate(ontology + examples, shacl_graph=shapes,
                                inference='rdfs', advanced=True, do_owl_imports=False)
        assert ok
        assert not list(report.subjects(RDF.type, SH.ValidationResult))
