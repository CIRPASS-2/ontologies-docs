"""Regressions for the independent audit's targeted corrections."""
import csv
import json
import zipfile
import pytest
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import SH, SKOS
from owlrl import DeductiveClosure, OWLRL_Semantics, RDFS_Semantics
from pyshacl import validate
from migration import implement_core as m
from migration.audit_counterexamples import mutate
from scripts import validate_public as v

EX=Namespace('https://example.org/textile-soc/')
S=Namespace('https://w3id.org/eudpp/textile-shacl#')
PROV=Namespace('http://www.w3.org/ns/prov#')


@pytest.fixture(scope='module')
def model():
    graph=v.ontology_graph(m.ROOT)
    for p in (m.ROOT/'mireot').glob('*.ttl'):graph+=m.parse(p)
    return graph


@pytest.fixture(scope='module')
def shapes():
    graph=Graph()
    for p in (m.ROOT/'shacl').glob('*.ttl'):graph+=m.parse(p)
    return graph


def base():return m.parse(m.ROOT/'tests/abox_corpus/fixtures/valid/V09-soc-migration-coverage.ttl')


def check(model,shapes,data,expected,carriers=()):
    ok,results,report=validate(model+data,shacl_graph=shapes,inference='rdfs',advanced=True,do_owl_imports=False)
    assert bool(ok)==expected,report
    actual=set(results.objects(None,SH.sourceConstraint))|set(results.objects(None,SH.sourceShape))
    assert set(carriers)<=actual,report
    return results


@pytest.mark.parametrize('case,expected,carriers',[
    ('CE6',False,[S.EvaluationOwnership]),('CE7',True,[]),('CE8',True,[])])
def test_claude_counterexamples(case,expected,carriers,model,shapes):
    check(model,shapes,mutate(base(),case),expected,carriers)


@pytest.mark.parametrize('relation',['forward','inverse','non_textile'])
@pytest.mark.parametrize('wrong_product',[False,True])
def test_location_and_denominator_membership_is_product_specific(relation,wrong_product,model,shapes):
    data=base();part=EX.outerFabricMaterialGroup
    data.remove((EX.jacket,m.T.hasPart,part))
    product=EX.otherProduct if wrong_product else EX.jacket
    if relation=='forward':data.add((product,m.T.hasPart,part))
    elif relation=='inverse':data.add((part,m.T.isPartOfProduct,product))
    else:
        # A denominator at component level can refer to a non-textile component;
        # material reporting retains its separate material-group constraint.
        part=EX.zipper
        data.set((EX.locationInformation,m.T.refersToProductPartForLocation,part))
        data.set((EX.concentrationInformation,m.T.refersToProductPartForConcentration,part))
        data.add((part,RDF.type,m.A.NonTextileComponent))
        data.add((product,m.A.hasNonTextileComponent,part))
        data.add((EX.componentLevel,RDF.type,m.T.ReportingLevel))
        data.add((EX.componentMassBasis,RDF.type,m.T.ConcentrationReferenceBasis))
        data.set((EX.concentrationInformation,m.T.hasConcentrationReportingLevel,EX.componentLevel))
        data.set((EX.concentrationInformation,m.T.hasConcentrationReferenceBasis,EX.componentMassBasis))
    carriers=[S.LocationPartMembership,S.DenominatorPartMembership] if wrong_product else []
    check(model,shapes,data,not wrong_product,carriers)


@pytest.mark.parametrize('semantics',[RDFS_Semantics,OWLRL_Semantics])
def test_inverse_and_component_inference_preserves_structural_types(semantics,model):
    graph=model+mutate(base(),'CE7')
    graph.add((EX.jacket,m.A.hasNonTextileComponent,EX.zipper))
    DeductiveClosure(semantics).expand(graph)
    if semantics==OWLRL_Semantics:assert (EX.jacket,m.T.hasPart,EX.outerFabricMaterialGroup) in graph
    assert (EX.zipper,RDF.type,m.A.TextileProductPart) in graph
    for node in (EX.zipper,EX.outerFabricMaterialGroup):assert (node,RDF.type,m.E.Product) not in graph
    assert (EX.zipper,RDF.type,m.E.MaterialOfComposition) not in graph
    assert (EX.recyclingInformation,RDF.type,m.E.DigitalInstruction) in graph


def test_42_copied_external_definitions_have_exact_source_attribution():
    graph=m.parse(m.ROOT/'ontology/textile-soc.ttl');old=m.parse(m.HISTORY/'dependencies/soc.ttl')
    expected={}
    for s in set(graph.subjects()):
        if isinstance(s,URIRef) and str(s).startswith(str(m.T)):
            source=m.OLD[str(s).split('#')[-1]]
            matches={(p,o) for p in (SKOS.definition,RDFS.comment) for o in graph.objects(s,p) if (source,p,o) in old}
            if matches:expected[s]=(source,matches)
    records=json.loads((m.ROOT/'migration/legacy-soc-attribution.json').read_text('utf8'))
    assert len(expected)==len(records)==42
    assert {row['resource_iri'] for row in records}==set(map(str,expected))
    for row in records:
        subject=URIRef(row['resource_iri']);source,matches=expected[subject]
        assert row['source_resource']==str(source)
        assert {(a['predicate'],a['text']) for a in row['copied_annotations']}=={(str(p),str(o)) for p,o in matches}
        assert (subject,m.DC.source,URIRef(v.LEGACY_SOC)) in graph
        assert (subject,m.DC.source,m.PROJECT) in graph
        assert (subject,PROV.wasDerivedFrom,source) in graph
        assert (subject,m.C.sourceType,m.C.adaptedDefinition) in graph
        assert (subject,m.C.sourceType,m.C.projectDecision) not in graph
    _,evidence,_,_=v.derive(v.ontology_graph(m.ROOT))
    copied=[e for e in evidence if e['source_document_id']=='HISTORICAL-SOC-0.1.2']
    assert len(copied)==42
    assert {e['locator_status'] for e in copied}=={'PRESENT_NOT_REVERIFIED'}


def test_inherited_unresolved_source_relationships_are_unchanged():
    with zipfile.ZipFile(next((m.ROOT/'migration/historical').glob('*.zip'))) as archive:
        original=list(csv.DictReader(archive.read('traceability/textile-resource-evidence.csv').decode('utf8').splitlines()))
    _,current,_,_=v.derive(v.ontology_graph(m.ROOT))
    unresolved=lambda rows:sorted([r for r in rows if r['locator_status']=='UNRESOLVED'],key=lambda r:r['evidence_id'])
    assert len(unresolved(current))==2
    assert unresolved(current)==unresolved(original)


@pytest.mark.parametrize('name',['casNumber','iupacName','hasQualification','hasPresenceContext','unknownResource',
    'ProductMassBasis','ProductPartMassBasis','ProductLevel','ComponentLevel','SparePartLevel'])
def test_unknown_legacy_mapping_requires_review(name):
    with pytest.raises(ValueError,match='manual review'):m.mapped(m.OLD[name])


def test_literal_text_is_never_rewritten():
    text=Literal('soc:casNumber https://w3id.org/eudpp/soc#hasQualification',lang='en')
    assert m.mapped(text)==text


def test_every_permitted_mapping_has_a_declared_destination(model):
    for name,destination in m.MAP.items():assert (destination,None,None) in model,name


def test_legacy_positive_presence_is_targeted_by_textile_shapes():
    assert m.mapped(m.OLD.SubstanceOfConcernPresenceContext)==m.T.TextileSubstanceOfConcernPresenceContext


@pytest.mark.parametrize('kind',[m.OLD.SubstancePresenceContext,m.OLD.SubstanceOfConcernPresenceContext])
def test_incomplete_legacy_presence_cannot_bypass_validation(kind):
    data=Graph();data.add((EX.legacyStylePresence,RDF.type,kind))
    data.add((EX.legacyStylePresence,m.OLD.hasConcentrationInformation,EX.maximumConcentration))
    with pytest.raises(m.MigrationConflict,match='manual review'):m.project_supported_legacy_data(data)


def test_mapping_inventory_covers_all_96_resources_and_contexts():
    old=m.parse(m.HISTORY/'mireot/soc-textile-mireot.ttl')
    expected={str(s) for s in old.subjects() if isinstance(s,URIRef) and str(s).startswith(str(m.OLD))}
    with (m.ROOT/'migration/semantic-mapping.csv').open(encoding='utf8') as f:rows=list(csv.DictReader(f))
    assert len(expected)==96
    assert {r['old_iri'] for r in rows}==expected
    for name in ('ExactQuantitativeValue','MaximumQuantitativeValue','RangeQuantitativeValue','numericValue','hasUnit'):
        assert len({r['new_iri'] for r in rows if r['old_iri']==str(m.OLD[name])})==2


@pytest.mark.parametrize('fault,carrier',[
    ('qualification-substance',S.QualificationSubstance),('qualification-criteria',S.QualificationCriteria),
    ('product-is-part',S.PresenceProductNotPart),('evaluation-applicability',S.EvaluationApplicability),
    ('threshold-unit',S.ExactThresholdValueShapeUnit),('threshold-exclusion',S.ExactThresholdValueShapeExcluded0),
    ('svhc-criterion',S.isQualifiedBySVHCListCriterion),('d-list-criterion',S.isQualifiedByProductGroupListCriterion)])
def test_important_constraint_carriers(fault,carrier,model,shapes):
    data=base()
    if fault=='qualification-substance':data.remove((EX.typeAQualification,m.E.qualifiesSubstance,None))
    elif fault=='qualification-criteria':data.remove((EX.typeAQualification,m.E.hasSoCCriterion,None))
    elif fault=='product-is-part':data.set((EX.presence,m.E.isSubstancePresenceOf,EX.outerFabricMaterialGroup))
    elif fault=='evaluation-applicability':data.remove((EX.concentrationInformation,m.T.hasApplicableRegulatoryThreshold,None))
    elif fault=='threshold-unit':data.set((EX.thresholdMassFraction,m.C.hasMeasurementUnit,URIRef(str(m.UNITS)+'degreeCelsius')))
    elif fault=='threshold-exclusion':data.add((EX.thresholdMassFraction,m.T.maximumValue,Literal('0.001',datatype=m.XSD.decimal)))
    elif fault=='svhc-criterion':
        data.add((EX.typeDQualification,m.T.isQualifiedBySVHCList,EX.svhc));data.add((EX.svhc,RDF.type,m.T.SVHCCandidateList));data.add((EX.svhc,m.T.referenceIdentifier,Literal('illustrative')))
    elif fault=='d-list-criterion':data.add((EX.typeAQualification,m.T.isQualifiedByProductGroupList,EX.reference))
    check(model,shapes,data,False,[carrier])


def test_e10_disclaimer_and_percentages_are_preserved():
    text=(m.ROOT/'examples/example-10-textile-soc-v2.0.0.ttl').read_text('utf8')
    assert 'not regulatory determinations' in text
    assert '0.0008 = 0.08 %' in text and '0.001 = 0.1 %' in text
    assert not list(m.parse(m.ROOT/'examples/example-10-textile-soc-v2.0.0.ttl').triples((EX.dimensionlessUnit,None,None)))


@pytest.mark.parametrize('node,shape',[(EX.thresholdMassFraction,'ExactThresholdValueShape'),
    (URIRef('https://example.org/textile-abox/valid/maximumThresholdValue'),'MaximumThresholdValueShape'),
    (URIRef('https://example.org/textile-abox/valid/rangeThresholdValue'),'RangeThresholdValueShape')])
def test_all_threshold_expression_unit_whitelists(node,shape,model,shapes):
    data=base()
    # Locate by class rather than depending on a fixture's incidental node name.
    cls={'ExactThresholdValueShape':m.T.ExactThresholdValue,'MaximumThresholdValueShape':m.T.MaximumThresholdValue,'RangeThresholdValueShape':m.T.RangeThresholdValue}[shape]
    node=next(data.subjects(RDF.type,cls))
    data.set((node,m.C.hasMeasurementUnit,URIRef(str(m.UNITS)+'degreeCelsius')))
    check(model,shapes,data,False,[S[shape+'Unit']])


@pytest.mark.parametrize('cls,shape,excluded',[
    (m.T.ExactThresholdValue,'ExactThresholdValueShape',m.T.maximumValue),
    (m.T.ExactThresholdValue,'ExactThresholdValueShape',m.T.lowerBound),
    (m.T.ExactThresholdValue,'ExactThresholdValueShape',m.T.upperBound),
    (m.T.MaximumThresholdValue,'MaximumThresholdValueShape',m.C.numericValue),
    (m.T.MaximumThresholdValue,'MaximumThresholdValueShape',m.T.lowerBound),
    (m.T.MaximumThresholdValue,'MaximumThresholdValueShape',m.T.upperBound),
    (m.T.RangeThresholdValue,'RangeThresholdValueShape',m.C.numericValue),
    (m.T.RangeThresholdValue,'RangeThresholdValueShape',m.T.maximumValue)])
def test_each_threshold_expression_exclusion(cls,shape,excluded,model,shapes):
    data=base();node=next(data.subjects(RDF.type,cls))
    data.add((node,excluded,Literal('0.001',datatype=m.XSD.decimal)))
    index={'ExactThresholdValueShape':[m.T.maximumValue,m.T.lowerBound,m.T.upperBound],
           'MaximumThresholdValueShape':[m.C.numericValue,m.T.lowerBound,m.T.upperBound],
           'RangeThresholdValueShape':[m.C.numericValue,m.T.maximumValue]}[shape].index(excluded)
    check(model,shapes,data,False,[S[shape+'Excluded'+str(index)]])


def test_criterion_specific_domain_decisions(model):
    graph=model+Graph()
    graph.add((EX.dQualification,m.T.isQualifiedByProductGroupList,EX.list))
    graph.add((EX.aQualification,m.T.isQualifiedBySVHCList,EX.svhc))
    DeductiveClosure(OWLRL_Semantics).expand(graph)
    assert (EX.dQualification,RDF.type,m.T.TextileTypeDQualification) in graph
    assert (EX.dQualification,m.E.hasSoCCriterion,m.E.CriterionD) in graph
    assert (EX.aQualification,RDF.type,m.E.SoCQualificationAssertion) in graph
    # Criterion A must be declared in data, never invented from a source link.
    assert (EX.aQualification,m.E.hasSoCCriterion,m.E.CriterionA) not in graph
