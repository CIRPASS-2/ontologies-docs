"""Source fidelity, migrated constraints, focus coverage and inference controls."""
import hashlib
import json
from pathlib import Path
import zipfile

import pytest
from rdflib import Graph, URIRef, RDF, RDFS, OWL, Namespace, Literal
from rdflib.namespace import SH
from rdflib.compare import isomorphic
from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics
from pyshacl import validate
from migration import implement_core as m
from scripts import validate_public as v

ROOT=Path(__file__).resolve().parents[1]
EX=Namespace('https://example.org/textile-soc/')
CASES=json.loads((ROOT/'tests/abox_corpus/expectations/migration-shacl-expectations.json').read_text('utf8'))['scenarios']


@pytest.fixture(scope='module')
def ontology():
    graph=Graph()
    for name in ('textile-core','textile-connector','textile-associated-materials','textile-soc'):
        graph+=m.parse(ROOT/f'ontology/{name}.ttl')
    for path in (ROOT/'mireot').glob('*.ttl'):graph+=m.parse(path)
    return graph


@pytest.fixture(scope='module')
def shapes():
    return m.parse(ROOT/'shacl/textile-soc-shapes.ttl')


def test_preservation_and_adopted_source_bytes():
    inv=json.loads((ROOT/'migration/historical/inventory.json').read_text('utf8'))
    archive=ROOT/'migration/historical'/inv['archive']
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==inv['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        for name,checksum in inv['files'].items():
            assert hashlib.sha256(z.read(name)).hexdigest()==checksum,name
            if (m.HISTORY/name).exists():assert (m.HISTORY/name).read_bytes()==z.read(name)
    for line in (ROOT/'dependencies/current-core/SHA256SUMS').read_text().splitlines():
        expected,name=line.split('  ',1)
        assert hashlib.sha256((ROOT/'dependencies/current-core'/name).read_bytes()).hexdigest()==expected
        assert (ROOT/'dependencies/current-core'/name).read_bytes()==(m.SOURCE/name).read_bytes()


@pytest.mark.parametrize('subset', ['soc','con','dpp','event','actor','mat'])
def test_bounded_extraction_faithfully_copies_source_axioms(subset):
    scopes=json.loads((ROOT/'migration/extraction-scopes.json').read_text('utf8'))
    record=scopes[subset]
    graph=m.parse(ROOT/f'mireot/{subset}-textile-mireot.ttl')
    graph.remove((URIRef(f'https://w3id.org/eudpp/textile-{subset}-mireot'),None,None))
    expected=m.extract(m.parse(m.SOURCE/record['source']),[m.E[name] for name in record['roots']])
    assert isomorphic(graph,expected)


def test_no_legacy_or_unrelated_core_in_active_closure():
    cat={entry.attrib['name']:entry.attrib['uri'] for entry in v.ET.parse(ROOT/'catalog-v001.xml').getroot()}
    closure=v.current_import_closure(ROOT,cat)
    assert len(closure)==20
    model=Graph()
    for name in closure:model+=m.parse(ROOT/name)
    v.reject_legacy_soc(model,'test closure')
    for iri in ('EnvironmentalFootprint','CarbonFootprint','ResourceConsumption','RecycledMaterialsUse'):
        assert not list(model.triples((m.E[iri],None,None)))
    assert not any(isinstance(x,URIRef) and str(x)=='https://w3id.org/eudpp/IDENT' for triple in model for x in triple)
    assert not list(model.triples((m.E.hasSubstanceIdentifier,None,None)))


def test_historical_catalogue_targets_exact_preserved_bytes():
    inventory=json.loads((ROOT/'migration/historical/inventory.json').read_text('utf8'))['files']
    for entry in v.ET.parse(m.HISTORY/'catalog-v001.xml').getroot():
        iri,rel=entry.attrib['name'],entry.attrib['uri']
        if iri.endswith(('/1.1.2','/1.1.3')) or iri=='https://w3id.org/eudpp/soc':
            assert hashlib.sha256((m.HISTORY/rel).read_bytes()).hexdigest()==inventory[rel]


@pytest.mark.parametrize('entry', ['textile-ontology/1.1.2','textile-soc/1.1.2','textile-soc-mireot/1.1.3'])
def test_historical_complete_import_closure_is_isolated(entry):
    catalogue=m.HISTORY/'catalog-v001.xml'
    closure=v.catalogue_import_closure(catalogue,'https://w3id.org/eudpp/'+entry)
    inventory=json.loads((ROOT/'migration/historical/inventory.json').read_text('utf8'))['files']
    assert closure
    if entry.startswith('textile-ontology/'):assert len(closure)==19
    for path in closure:
        rel=path.relative_to(m.HISTORY).as_posix()
        assert hashlib.sha256(path.read_bytes()).hexdigest()==inventory[rel]
        assert path.name!='con-textile-mireot.ttl'
        assert not any(str(x).endswith('/2.0.0') for x in m.parse(path).objects(None,OWL.versionIRI))
    with pytest.raises(ValueError,match='Unmapped import'):
        v.catalogue_import_closure(ROOT/'catalog-v001.xml','https://w3id.org/eudpp/'+entry)


def test_e10_concentration_transfer_and_unknown_identifier_are_lossless():
    graph=m.parse(ROOT/'examples/example-10-textile-soc-v2.0.0.ttl')
    assert str(graph.value(EX.concentrationInformation,m.E.numericalValue))=='0.0008'
    assert str(graph.value(EX.thresholdMassFraction,m.C.numericValue))=='0.001'
    assert graph.value(EX.reportedSubstance,m.T.substanceIdentifier)==Literal('illustrative-substance-id')
    assert not any(graph.objects(EX.reportedSubstance,m.E.casNumber))
    assert not any(graph.objects(EX.reportedSubstance,m.E.ecNumber))
    assert not any(graph.objects(EX.reportedSubstance,m.E.echaNumber))
    assert graph.value(EX.concentrationInformation,m.T.refersToProductPartForConcentration)==EX.outerFabricMaterialGroup
    assert graph.value(EX.concentrationInformation,m.T.hasConcentrationReferenceBasis)==m.T.MaterialGroupMassBasis
    assert graph.value(EX.presence,m.E.hasRecyclingInstruction)==EX.recyclingInformation
    assert graph.value(EX.recyclingInformation,m.T.instructionContent)
    rows=json.loads((ROOT/'migration/node-correspondence.json').read_text('utf8'))
    assert rows==[dict(fixture='examples/example-10-textile-soc-v1.1.2.ttl',old_value_node=str(EX.reportedMassFraction),new_concentration_node=str(EX.concentrationInformation))]


@pytest.mark.parametrize('complete',[False,True])
def test_positive_soc_coverage_conforms(ontology,shapes,complete):
    data=m.parse(ROOT/'tests/abox_corpus/fixtures/valid/V09-soc-migration-coverage.ttl')
    selected=Graph()+shapes
    if complete:selected+=m.parse(ROOT/'shacl/profiles/textile-soc-complete-report.ttl')
    ok,_,report=validate(ontology+data,shacl_graph=selected,inference='rdfs',advanced=True,do_owl_imports=False)
    assert ok,report


@pytest.mark.parametrize('case',CASES,ids=lambda row:row['scenario_id'])
def test_migration_discriminating_results(case,ontology,shapes):
    selected=Graph()+shapes
    if case['complete_report']:selected+=m.parse(ROOT/'shacl/profiles/textile-soc-complete-report.ttl')
    data=m.parse(ROOT/case['fixture_path'])
    v.reject_legacy_soc(data,case['scenario_id'])
    ok,results,report=validate(ontology+data,shacl_graph=selected,inference='rdfs',advanced=True,do_owl_imports=False)
    assert bool(ok)==case['expected_conforms'],report
    v.match_shacl_results(results,selected,case)


def test_every_soc_shape_has_positive_focus_and_discriminating_negative(ontology,shapes):
    model=ontology+m.parse(ROOT/'tests/abox_corpus/fixtures/valid/V09-soc-migration-coverage.ttl')
    DeductiveClosure(RDFS_Semantics).expand(model)
    negative_shapes={URIRef(row['source_shape']) for case in CASES for row in case['expected_results']}
    selected=shapes+m.parse(ROOT/'shacl/profiles/textile-soc-complete-report.ttl')
    for shape in selected.subjects(RDF.type,SH.NodeShape):
        focus=set(selected.objects(shape,SH.targetNode))
        for cls in selected.objects(shape,SH.targetClass):focus.update(model.subjects(RDF.type,cls))
        for prop in selected.objects(shape,SH.targetObjectsOf):focus.update(model.objects(None,prop))
        for prop in selected.objects(shape,SH.targetSubjectsOf):focus.update(model.subjects(prop,None))
        for target in selected.objects(shape,SH.target):
            query=selected.value(target,SH.select)
            if query:focus.update(row[0] for row in model.query(str(query)))
        assert focus, f'No intended positive focus nodes: {shape}'
        constraint_shapes={shape}|set(selected.objects(shape,SH.property))
        assert negative_shapes & constraint_shapes, f'No discriminating negative for {shape}'


def test_owl_entailments_and_non_entailments():
    model=v.ontology_graph(ROOT)
    for path in (ROOT/'mireot').glob('*.ttl'):model+=m.parse(path)
    model+=m.parse(ROOT/'tests/abox_corpus/fixtures/valid/V09-soc-migration-coverage.ttl')
    model.add((EX.genericMaterialGroup,RDF.type,m.T.TextileMaterialGroup))
    model.add((EX.nonTextileComponent,RDF.type,m.A.NonTextileComponent))
    DeductiveClosure(OWLRL_Semantics).expand(model)
    assert (EX.reportedSubstance,RDF.type,m.E.SubstanceOfConcern) in model
    assert (EX.genericChemical,RDF.type,m.E.SubstanceOfConcern) not in model
    assert (EX.outerFabricMaterialGroup,RDF.type,m.E.Product) not in model
    for part in (EX.genericMaterialGroup,EX.nonTextileComponent):
        assert (part,RDF.type,m.E.Product) not in model
        assert (part,RDF.type,m.E.MaterialOfComposition) not in model
    assert (EX.execution,RDF.type,m.E.ProductEvent) not in model
    assert (EX.nonExemptionThreshold,RDF.type,m.E.ConcentrationOfSubstanceOfConcern) not in model
    assert (EX.thresholdMassFraction,RDF.type,m.E.ConcentrationOfSubstanceOfConcern) not in model
    assert (EX.thresholdMassFraction,RDF.type,m.C.QuantitativeValue) in model
    assert (EX.otherPresence,m.E.hasApplicableQualification,EX.typeDQualification) not in model
    assert (EX.otherPresence,m.E.hasApplicableQualification,EX.typeAQualification) in model
    assert (m.UNITS.one,OWL.sameAs,m.E.massFractionUnit) not in model
    # Local OWL existential commitments remain; concentration is not a universal
    # existential on partial presence declarations.
    graph=m.parse(ROOT/'ontology/textile-soc.ttl')
    restrictions=list(graph.objects(m.T.TextileSubstanceOfConcernPresenceContext,RDFS.subClassOf))
    props={graph.value(r,OWL.onProperty) for r in restrictions}
    assert {m.E.isSubstancePresenceOf,m.E.concernsSubstance,m.E.hasApplicableQualification}<=props
    assert m.E.hasConcentration not in props


def test_current_range_axiom_exposes_wrong_maximum_carrier():
    graph=m.parse(ROOT/'mireot/soc-textile-mireot.ttl')
    graph.add((EX.maximum,RDF.type,m.E.MaximumConcentration))
    graph.add((EX.maximum,m.E.maximumNumericalValue,Literal('0.1',datatype=m.XSD.decimal)))
    DeductiveClosure(OWLRL_Semantics).expand(graph)
    assert (EX.maximum,RDF.type,m.E.ConcentrationRange) in graph
    assert (m.E.MaximumConcentration,OWL.disjointWith,m.E.ConcentrationRange) in graph


def test_legacy_data_is_rejected_before_inference():
    graph=Graph();graph.add((EX.presence,m.OLD.hasSubstance,EX.reportedSubstance))
    with pytest.raises(ValueError,match='Legacy SOC identity'):v.reject_legacy_soc(graph,'negative fixture')


def test_existing_creators_are_preserved_with_owner_approved_additions():
    for name in v.CURRENT_MODULES:
        before=m.parse(m.HISTORY/'ontology'/name)
        after=m.parse(ROOT/'ontology'/name)
        ontology=next(after.subjects(RDF.type,OWL.Ontology))
        additions={(ontology,m.Literal(person,lang='en')) for person in ('Ivo Ladenius','Andreas Schneider','Jan Merckx','Piero de Sabbata')}
        assert set(after.subject_objects(m.DC.creator))==set(before.subject_objects(m.DC.creator))|additions,name


def test_product_event_has_no_obsolete_minimum_product_restriction():
    graph=m.parse(ROOT/'mireot/event-textile-mireot.ttl')
    assert set(graph.objects(m.E.ProductEvent,RDFS.subClassOf))=={m.E.ESPREvent}


def test_shared_quantitative_profile_accepts_only_authorised_threshold_extension(ontology,shapes):
    data=m.parse(ROOT/'tests/abox_corpus/fixtures/valid/V09-soc-migration-coverage.ttl')
    selected=shapes+m.parse(ROOT/'shacl/textile-quantitative-shapes.ttl')
    ok,_,report=validate(ontology+data,shacl_graph=selected,inference='rdfs',advanced=True,do_owl_imports=False)
    assert ok,report
    data.add((EX.UnauthorisedValue,RDFS.subClassOf,m.C.QuantitativeValue))
    ok,results,_=validate(ontology+data,shacl_graph=selected,inference='rdfs',advanced=True,do_owl_imports=False)
    assert not ok
    assert URIRef('https://w3id.org/eudpp/textile-shacl#NoQuantitativeValueSubclassShape') in set(results.objects(None,SH.sourceShape))


@pytest.mark.parametrize('fault',['shared','external_identity','conflicting_metadata'])
def test_concentration_wrapper_conflicts_require_an_explicit_decision(fault):
    old=Graph()
    old.add((EX.concentration,m.OLD.hasQuantitativeValue,EX.value))
    old.add((EX.value,RDF.type,m.OLD.ExactQuantitativeValue))
    old.add((EX.value,m.OLD.numericValue,Literal('0.0008',datatype=m.XSD.decimal)))
    if fault=='shared':old.add((EX.anotherConcentration,m.OLD.hasQuantitativeValue,EX.value))
    if fault=='external_identity':old.add((EX.value,OWL.sameAs,EX.externalValue))
    if fault=='conflicting_metadata':
        old.add((EX.concentration,RDFS.label,Literal('concentration label')))
        old.add((EX.value,RDFS.label,Literal('different value label')))
    projected=Graph()
    for triple in old:projected.add(tuple(m.mapped(term) for term in triple))
    with pytest.raises(m.MigrationConflict):m.flatten_concentration_wrapper(old,projected,EX.concentration,EX.value)


def test_concentration_wrapper_transfers_citation_and_provenance_without_identity_merge():
    old=Graph()
    old.add((EX.concentration,m.OLD.hasQuantitativeValue,EX.value))
    old.add((EX.value,RDF.type,m.OLD.ExactQuantitativeValue))
    old.add((EX.value,m.OLD.numericValue,Literal('0.0008',datatype=m.XSD.decimal)))
    old.add((EX.value,m.DC.source,EX.originalLaboratoryReference))
    projected=Graph()
    for triple in old:projected.add(tuple(m.mapped(term) for term in triple))
    m.flatten_concentration_wrapper(old,projected,EX.concentration,EX.value)
    assert projected.value(EX.concentration,m.E.numericalValue)==Literal('0.0008',datatype=m.XSD.decimal)
    assert projected.value(EX.concentration,m.DC.source)==EX.originalLaboratoryReference
    assert not list(projected.triples((EX.value,None,None)))
    assert not list(projected.triples((None,OWL.sameAs,None)))
