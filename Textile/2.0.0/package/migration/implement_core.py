"""Deterministic bounded extraction and Textile/data migration from preserved inputs."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import shutil
import zipfile
from xml.etree import ElementTree as ET
from rdflib import Graph, URIRef, BNode, Literal, Namespace, RDF, RDFS, OWL, XSD
from rdflib.namespace import DCTERMS as DC, SKOS
from rdflib.collection import Collection

ROOT = Path(__file__).resolve().parents[1]
E = Namespace('https://w3id.org/eudpp#')
T = Namespace('https://w3id.org/eudpp/textile-soc#')
A = Namespace('https://w3id.org/eudpp/textile-associated-materials#')
C = Namespace('https://w3id.org/eudpp/textile-connector#')
OLD = Namespace('https://w3id.org/eudpp/soc#')
SI = Namespace('https://si-digital-framework.org/SI#')
UNITS = Namespace('https://si-digital-framework.org/SI/units/')
PROJECT = URIRef('https://w3id.org/eudpp/textile-ontology')
HISTORY = ROOT/'migration/historical/1.1.2'
SOURCE = ROOT/'migration/core-sources'
MAP = {
 'Substance': E.Substance, 'SubstanceOfConcern': E.SubstanceOfConcern,
 'SubstancePresenceContext': T.TextileSubstanceOfConcernPresenceContext,
 'SubstanceOfConcernPresenceContext': T.TextileSubstanceOfConcernPresenceContext,
 'RegulatoryQualification': E.SoCQualificationAssertion,
 'SubstanceOfConcernQualification': E.SoCQualificationAssertion,
 'SoCTypeAQualification': E.SoCQualificationAssertion,
 'SoCTypeDQualification': E.SoCQualificationAssertion,
 'hasProduct': E.isSubstancePresenceOf, 'hasSubstance': E.concernsSubstance,
 'hasApplicableQualification': E.hasApplicableQualification,
 'qualifiesSubstance': E.qualifiesSubstance,
 'ConcentrationInformation': E.ConcentrationOfSubstanceOfConcern,
 'hasConcentrationInformation': E.hasConcentration,
 'InstructionInformation': E.SubstanceManagementInstruction,
 'ProductPart': A.TextileProductPart, 'ProductComponent': A.TextileProductPart,
 'RegulatoryThreshold': E.ThresholdOfSubstanceOfConcern,
 'QuantitativeValue': C.QuantitativeValue,
 'ExactQuantitativeValue': T.ExactThresholdValue,
 'MaximumQuantitativeValue': T.MaximumThresholdValue,
 'RangeQuantitativeValue': T.RangeThresholdValue,
 'numericValue': C.numericValue, 'hasUnit': C.hasMeasurementUnit,
 'Unit': SI.MeasurementUnit,
}
# Deliberately enumerated retained legacy terms. Identity properties and new
# legacy resources require review; constructing a local IRI is not a mapping.
RETAINED = '''MaterialGroup LocationInformation ConcentrationReferenceBasis ReportingLevel
ProductGroupSpecificSoCList ExternalRegulatoryReference SVHCCandidateList isQualifiedBySVHCList Situation
NonExemptionThreshold TrackingThreshold AlertConcentrationThreshold ThresholdEvaluation ThresholdEvaluationResult
BelowThreshold AtThreshold AboveThreshold IndeterminateThresholdResult
MaterialGroupMassBasis MaterialLevel RecyclingInstructionType
SafeUseInstructionType InstructionType hasInstructionType instructionContent hasLocationInformation
locationDescriptor refersToProductPartForLocation hasPart isPartOfProduct refersToProductPartForConcentration
hasConcentrationReferenceBasis hasConcentrationReportingLevel analyticalMethod hasRegulatoryBasis
isQualifiedByProductGroupList qualificationSource hasApplicableRegulatoryThreshold hasThresholdEvaluation
evaluatesConcentrationInformation evaluatesAgainstThreshold hasThresholdEvaluationResult evaluationNote
thresholdNote hasThresholdQuantitativeValue substanceIdentifier maximumValue lowerBound upperBound'''.split()
MAP.update({name:T[name] for name in RETAINED})


def parse(path):
    return Graph().parse(path, format='xml' if str(path).endswith('.owl') else 'turtle')


def save(graph, path):
    for prefix, ns in [('dpp',E),('txtsoc',T),('txtam',A),('txtcon',C),('dcterms',DC),('si',SI),('units',UNITS)]:
        graph.bind(prefix, ns, replace=True)
    Path(path).write_text(graph.serialize(format='turtle').rstrip('\r\n')+'\n',encoding='utf8',newline='\n')


def mapped(term):
    if isinstance(term, URIRef) and str(term).startswith(str(OLD)):
        name = str(term)[len(str(OLD)):]
        if name in MAP:return MAP[name]
        # These edges are consumed by the contextual converter, not published.
        if name=='hasQuantitativeValue':return T.hasQuantitativeValue
        if name=='hasInstructionInformation':return T.hasTextileHandlingInformation
        raise ValueError('Unmapped legacy SOC resource requires manual review: '+str(term))
    return term


def extract(source, roots):
    """Copy complete selected subjects plus anonymous axioms and named support."""
    out = Graph()
    pending = list(roots)
    seen = set()
    semantic = {RDFS.subClassOf, RDFS.subPropertyOf, RDFS.domain, RDFS.range,
                OWL.inverseOf, OWL.disjointWith, OWL.onClass, OWL.onProperty,
                OWL.allValuesFrom, OWL.someValuesFrom, OWL.hasValue,
                SKOS.inScheme, SKOS.topConceptOf, SKOS.hasTopConcept}
    while pending:
        subject = pending.pop()
        if subject in seen:
            continue
        seen.add(subject)
        for triple in source.triples((subject,None,None)):
            out.add(triple)
            _, predicate, obj = triple
            if isinstance(obj,BNode) or (predicate in semantic and (obj,None,None) in source):
                pending.append(obj)
    return out


def stage1():
    archive = next((ROOT/'migration/historical').glob('*.zip'))
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if name.startswith('ontology/graphwise-ontology/'):continue
            if name.startswith(('ontology/','mireot/','dependencies/')) or name=='catalog-v001.xml':
                target = HISTORY/name
                if target.exists():
                    assert target.read_bytes()==z.read(name), name
                else:
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(z.read(name))
    current = ROOT/'dependencies/current-core'
    current.mkdir(exist_ok=True)
    for source in SOURCE.iterdir():
        shutil.copyfile(source,current/source.name)
    scopes = {
     'soc': ('soc.owl', '''Substance SubstanceOfConcern SubstancePresence SoCQualificationAssertion
         CriterionA CriterionB CriterionC CriterionD SoCCriterionScheme MaximumConcentration ConcentrationRange
         minimumNumericalValue maximumNumericalValue
         concernsSubstance hasApplicableQualification qualifiesSubstance hasQualificationAssertion hasSoCCriterion
         casNumber ecNumber echaNumber casName iupacName internationalName otherName tradeName usualName abbreviation
         qualificationNote qualificationValidFrom qualificationValidUntil substanceLocationDescription
         SubstanceManagementInstruction hasSafeUseInstruction hasRecyclingInstruction hasReuseInstruction
         hasDisassemblyInstruction hasPreparationForReuseInstruction hasEndOfLifeManagementInstruction massFractionUnit sourceStatus'''.split()),
     'con': ('connector.owl', 'hasSubstancePresence isSubstancePresenceOf isLocatedInProduct hasConcentration SubstanceManagementInstruction'.split()),
     'dpp': ('p_dpp.owl', sorted({str(s).split('#')[-1] for s in parse(HISTORY/'mireot/dpp-textile-mireot.ttl').subjects()
              if isinstance(s,URIRef) and str(s).startswith(str(E))}
              - {'EnvironmentalFootprint','ResourceConsumption','RecycledMaterialsUse','CarbonFootprint'}
              | {'ConcentrationOfSubstanceOfConcern','ThresholdOfSubstanceOfConcern','numericalValue','hasMeasurementUnit'})),
     'event': ('event.owl', 'ESPREvent ProductEvent RefurbishmentEvent RemanufacturingEvent RepairEvent UpgradingEvent'.split()),
     'actor': ('actor.owl', ['Actor']),
     'mat': ('mat.owl', ['MaterialOfComposition','MaterialType','hasMaterialType']),
    }
    records = {}
    for subset,(filename,names) in scopes.items():
        source = parse(SOURCE/filename)
        roots = [E[name] for name in names]
        assert all((root,None,None) in source for root in roots), (filename,names)
        graph = extract(source,roots)
        iri = URIRef(f'https://w3id.org/eudpp/textile-{subset}-mireot')
        source_iri = next(source.subjects(RDF.type,OWL.Ontology))
        for predicate,value in [(RDF.type,OWL.Ontology),(RDFS.label,Literal(f'Textile {subset.upper()} bounded MIREOT',lang='en')),
                                (DC.source,source_iri),(DC.modified,Literal('2026-10-27',datatype=XSD.date)),
                                (DC.references,Literal(f'Owner-designated CORE {source.value(source_iri,OWL.versionInfo)}; unchanged source in dependencies/current-core/{filename}.',lang='en')),
                                (OWL.versionIRI,URIRef(str(iri)+'/2.0.0')),(OWL.versionInfo,Literal('Version 2.0.0 candidate'))]:
            graph.add((iri,predicate,value))
        save(graph,ROOT/f'mireot/{subset}-textile-mireot.ttl')
        records[subset] = {'source':filename,'source_iri':str(source_iri),'roots':names,'copied_triples':len(graph)-7}
    (ROOT/'migration/extraction-scopes.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8',newline='\n')
    # Old source bytes remain in the preserved archive and extracted package.
    for filename in ('actor.owl','mat.owl','p_dpp.owl','event.ttl','soc.ttl'):
        path=ROOT/'dependencies'/filename
        if path.exists():path.unlink()
    print('Stage 1: historical identities preserved; six bounded CORE extractions written.')


def minimum(graph, cls, prop, target):
    restriction = BNode()
    for triple in [(cls,RDFS.subClassOf,restriction),(restriction,RDF.type,OWL.Restriction),
                   (restriction,OWL.onProperty,prop),(restriction,OWL.someValuesFrom,target)]:graph.add(triple)


def owned(graph, subject, kind, label):
    graph.add((subject,RDF.type,kind))
    graph.add((subject,RDFS.label,Literal(label,lang='en')))
    graph.add((subject,RDFS.isDefinedBy,URIRef(str(subject).split('#')[0])))
    graph.add((subject,DC.source,PROJECT))
    graph.add((subject,C.sourceType,C.projectDecision))
    graph.add((subject,C.sourceLocator,Literal('docs/decisions/TXT-DEC-010.md',lang='en')))


def stage2():
    graph = parse(HISTORY/'ontology/textile-soc.ttl')
    graph = Graph() + Graph().parse(data=graph.serialize(format='nt'),format='nt')
    migrated = Graph()
    for triple in graph:migrated.add(tuple(mapped(t) for t in triple))
    graph=migrated
    graph.remove((T.hasTextileHandlingInformation,RDFS.subPropertyOf,None))
    graph.remove((T.hasTextileProductGroupReference,RDFS.subPropertyOf,None))
    legacy=parse(HISTORY/'mireot/soc-textile-mireot.ttl')
    keep='''MaterialGroup LocationInformation ConcentrationReferenceBasis ReportingLevel
       ProductGroupSpecificSoCList ExternalRegulatoryReference SVHCCandidateList isQualifiedBySVHCList Situation NonExemptionThreshold TrackingThreshold
       AlertConcentrationThreshold ThresholdEvaluation ThresholdEvaluationResult
       BelowThreshold AtThreshold AboveThreshold IndeterminateThresholdResult
       ProductMassBasis ProductPartMassBasis MaterialGroupMassBasis ProductLevel ComponentLevel MaterialLevel SparePartLevel
       RecyclingInstructionType SafeUseInstructionType InstructionType hasInstructionType instructionContent
       hasLocationInformation locationDescriptor refersToProductPartForLocation
       hasPart isPartOfProduct refersToProductPartForConcentration hasConcentrationReferenceBasis
       hasConcentrationReportingLevel analyticalMethod hasRegulatoryBasis isQualifiedByProductGroupList qualificationSource
       hasApplicableRegulatoryThreshold hasThresholdEvaluation evaluatesConcentrationInformation evaluatesAgainstThreshold
       hasThresholdEvaluationResult evaluationNote thresholdNote hasThresholdQuantitativeValue
       substanceIdentifier'''.split()
    # Migrate only supported declarations. New properties/classes are Textile-owned;
    # do not copy legacy global restrictions or unused inverse declarations.
    for name in keep:
        subject=OLD[name]
        if (subject,None,None) not in legacy:continue
        new=mapped(subject)
        for _,predicate,obj in legacy.triples((subject,None,None)):
            if isinstance(obj,BNode) or predicate==OWL.inverseOf:continue
            graph.add((new,predicate,mapped(obj)))
        owned(graph,new,next(legacy.objects(subject,RDF.type)),name)
    graph.set((T.MaterialGroup,RDFS.subClassOf,A.TextileProductPart))
    graph.set((T.ProductGroupSpecificSoCList,RDFS.subClassOf,T.ExternalRegulatoryReference))
    graph.add((T.hasTextileProductGroupReference,RDFS.subPropertyOf,T.hasRegulatoryBasis))
    graph.set((T.hasRegulatoryBasis,RDFS.domain,E.SoCQualificationAssertion))
    graph.set((T.qualificationSource,RDFS.domain,E.SoCQualificationAssertion))
    graph.set((T.hasPart,RDFS.range,A.TextileProductPart))
    graph.set((T.refersToProductPartForLocation,RDFS.range,A.TextileProductPart))
    graph.set((T.refersToProductPartForConcentration,RDFS.range,A.TextileProductPart))
    graph.set((T.hasThresholdQuantitativeValue,RDFS.range,C.QuantitativeValue))
    graph.set((T.TextileSubstanceOfConcernPresenceContext,C.sourceLocator,
               Literal('Regulation (EU) 2024/1781, Article 2(27) and Article 7(5); CORE SOC 2.2.0 SubstancePresence.',lang='en')))
    graph.add((T.TextileTypeDQualification,RDFS.subClassOf,E.SoCQualificationAssertion))
    restriction=BNode()
    for triple in [(T.TextileTypeDQualification,RDFS.subClassOf,restriction),(restriction,RDF.type,OWL.Restriction),
                   (restriction,OWL.onProperty,E.hasSoCCriterion),(restriction,OWL.hasValue,E.CriterionD)]:graph.add(triple)
    # Explicit scope for context-sensitive qualification; no propagation to another product.
    for name,domain,range_ in [('appliesToProduct',E.SoCQualificationAssertion,E.Product),
                               ('referenceVersion',T.ExternalRegulatoryReference,XSD.string),
                               ('referenceIdentifier',T.ExternalRegulatoryReference,XSD.string),
                               ('referenceDate',T.ExternalRegulatoryReference,XSD.date),
                               ('productGroupApplicability',T.ExternalRegulatoryReference,XSD.string)]:
        owned(graph,T[name],OWL.ObjectProperty if name=='appliesToProduct' else OWL.DatatypeProperty,name)
        graph.add((T[name],RDFS.domain,domain));graph.add((T[name],RDFS.range,range_))
    for name in ('ExactThresholdValue','MaximumThresholdValue','RangeThresholdValue'):
        owned(graph,T[name],OWL.Class,name)
        graph.add((T[name],RDFS.subClassOf,C.QuantitativeValue))
        graph.add((T[name],OWL.disjointWith,E.ConcentrationOfSubstanceOfConcern))
    for name,domain in [('maximumValue',T.MaximumThresholdValue),('lowerBound',T.RangeThresholdValue),('upperBound',T.RangeThresholdValue)]:
        owned(graph,T[name],OWL.DatatypeProperty,name)
        graph.add((T[name],RDFS.domain,domain));graph.add((T[name],RDFS.range,XSD.decimal))
    for cls in (T.NonExemptionThreshold,T.TextileTrackingThreshold,T.TextileRecyclingAlertThreshold):
        graph.add((cls,OWL.disjointWith,E.ConcentrationOfSubstanceOfConcern))
        minimum(graph,cls,T.hasThresholdQuantitativeValue,C.QuantitativeValue)
    for name in ('AboveThreshold','AtThreshold','IndeterminateThresholdResult'):
        owned(graph,T[name],OWL.NamedIndividual,name)
        graph.add((T[name],RDF.type,T.ThresholdEvaluationResult))
    for name,range_ in [('hasThresholdReferenceBasis',T.ConcentrationReferenceBasis),
                         ('hasThresholdReportingLevel',T.ReportingLevel),
                         ('refersToProductPartForThreshold',A.TextileProductPart)]:
        owned(graph,T[name],OWL.ObjectProperty,name)
        graph.add((T[name],RDFS.domain,E.ThresholdOfSubstanceOfConcern));graph.add((T[name],RDFS.range,range_))
    for cls,requirements in {
       T.TextileSubstanceOfConcernPresenceContext:[(E.isSubstancePresenceOf,E.Product),(E.concernsSubstance,E.SubstanceOfConcern),(E.hasApplicableQualification,E.SoCQualificationAssertion)],
       T.ThresholdEvaluation:[(T.evaluatesConcentrationInformation,E.ConcentrationOfSubstanceOfConcern),(T.evaluatesAgainstThreshold,E.ThresholdOfSubstanceOfConcern),(T.hasThresholdEvaluationResult,T.ThresholdEvaluationResult)],
       T.ExactThresholdValue:[(C.numericValue,XSD.decimal),(C.hasMeasurementUnit,SI.MeasurementUnit)],
       T.MaximumThresholdValue:[(T.maximumValue,XSD.decimal),(C.hasMeasurementUnit,SI.MeasurementUnit)],
       T.RangeThresholdValue:[(T.lowerBound,XSD.decimal),(T.upperBound,XSD.decimal),(C.hasMeasurementUnit,SI.MeasurementUnit)],
       T.TextileConcentrationInformation:[(E.hasMeasurementUnit,SI.MeasurementUnit)],
    }.items():
        for prop,target in requirements:minimum(graph,cls,prop,target)
    # The former quantitative-wrapper existential becomes a scalar-or-range
    # expression existential on the concentration itself, without an exact class.
    scalar=BNode();lower=BNode();upper=BNode()
    for restriction,prop in [(scalar,E.numericalValue),(lower,E.minimumNumericalValue),(upper,E.maximumNumericalValue)]:
        graph.add((restriction,RDF.type,OWL.Restriction));graph.add((restriction,OWL.onProperty,prop));graph.add((restriction,OWL.someValuesFrom,XSD.decimal))
    range_class=BNode();range_list=BNode();Collection(graph,range_list,[lower,upper]);graph.add((range_class,OWL.intersectionOf,range_list))
    expression=BNode();expressions=BNode();Collection(graph,expressions,[scalar,range_class]);graph.add((expression,OWL.unionOf,expressions))
    graph.add((T.TextileConcentrationInformation,RDFS.subClassOf,expression))
    graph.add((URIRef('https://w3id.org/eudpp/textile-soc'),OWL.imports,URIRef('https://w3id.org/eudpp/textile-con-mireot')))
    save(graph,ROOT/'ontology/textile-soc.ttl')
    am=Graph()
    for triple in parse(HISTORY/'ontology/textile-associated-materials.ttl'):am.add(tuple(mapped(t) for t in triple))
    owned(am,A.TextileProductPart,OWL.Class,'Textile product part')
    for subject,predicate,value in list(am):
        if isinstance(value,Literal) and 'txtsoc:Substance' in str(value):
            am.remove((subject,predicate,value));am.add((subject,predicate,Literal(str(value).replace('txtsoc:Substance','dpp:Substance'),lang=value.language,datatype=value.datatype)))
    am.set((A.NonTextileComponent,RDFS.subClassOf,A.TextileProductPart))
    am.set((A.NonTextileComponent,C.modellingNote,Literal('A structural product part; neither Product nor MaterialOfComposition is universally entailed.',lang='en')))
    save(am,ROOT/'ontology/textile-associated-materials.ttl')
    rec=parse(HISTORY/'ontology/textile-recyclability.ttl')
    rec.remove((None,DC.relation,E.RecycledMaterialsUse))
    for subject,predicate,obj in list(rec):
        if isinstance(obj,Literal) and 'RecycledMaterialsUse' in str(obj):
            rec.remove((subject,predicate,obj))
            rec.add((subject,predicate,Literal('Recycled content is represented by Textile-owned declarations, independently of recyclability.',lang=obj.language)))
    save(rec,ROOT/'ontology/textile-recyclability.ttl')
    changed=['textile-soc','textile-associated-materials','textile-recyclability','textile-ontology']
    for name in changed:
        path=ROOT/f'ontology/{name}.ttl';g=parse(path);iri=URIRef('https://w3id.org/eudpp/'+name)
        g.set((iri,OWL.versionIRI,URIRef(str(iri)+'/2.0.0')))
        g.set((iri,OWL.versionInfo,Literal('Version 2.0.0 candidate')))
        g.set((iri,DC.modified,Literal('2026-10-27',datatype=XSD.date)))
        for value in list(g.objects(iri,DC.bibliographicCitation)):
            g.remove((iri,DC.bibliographicCitation,value));g.add((iri,DC.bibliographicCitation,Literal(str(value).replace('1.1.2','2.0.0 candidate'),lang=value.language)))
        save(g,path)
    migrate_data()
    catalog()
    (ROOT/'VERSION').write_text('2.0.0\n',encoding='utf8',newline='\n')
    print('Stage 2: Textile extensions, data correspondence and catalogue written.')


class MigrationConflict(ValueError):
    """A wrapper cannot be projected safely without an explicit decision."""


def project_supported_legacy_data(old):
    """Project the bounded positive-report input; refuse incomplete contexts.

    This is not a general SOC/IDENT converter. Wrapper edges are temporary and
    must subsequently be consumed by flatten_concentration_wrapper.
    """
    presences=set(old.subjects(RDF.type,OLD.SubstancePresenceContext))|set(old.subjects(RDF.type,OLD.SubstanceOfConcernPresenceContext))
    for presence in presences:
        if not all(any(old.objects(presence,p)) for p in (OLD.hasProduct,OLD.hasSubstance,OLD.hasApplicableQualification)):
            raise MigrationConflict('Incomplete legacy presence requires manual review: '+str(presence))
    graph=Graph()
    for triple in old:graph.add(tuple(mapped(term) for term in triple))
    return graph


def flatten_concentration_wrapper(old, graph, concentration, wrapper):
    incoming=list(old.subject_predicates(wrapper))
    if incoming!=[(concentration,OLD.hasQuantitativeValue)]:
        raise MigrationConflict(f'Shared or externally referenced concentration value node: {wrapper}; incoming={incoming}')
    roles={OLD.ExactQuantitativeValue,OLD.MaximumQuantitativeValue,OLD.RangeQuantitativeValue}
    actual_types=set(old.objects(wrapper,RDF.type))
    if len(actual_types & roles)!=1 or actual_types-roles-{OWL.NamedIndividual}:
        raise MigrationConflict(f'Ambiguous concentration value types at {wrapper}: {actual_types}')
    # Citations/provenance are transferable. Identity links and other external
    # relationships are not silently moved from a value to a concentration.
    allowed_links={RDF.type,OLD.hasUnit,DC.source,DC.provenance,DC.references,C.sourceType}
    for predicate,value in old.predicate_objects(wrapper):
        if isinstance(value,(URIRef,BNode)) and predicate not in allowed_links:
            raise MigrationConflict(f'External identity/reference on {wrapper}: {predicate} {value}')
    graph.remove((concentration,T.hasQuantitativeValue,wrapper))
    for predicate,value in list(graph.predicate_objects(wrapper)):
        graph.remove((wrapper,predicate,value))
        if predicate==RDF.type:
            if value==T.MaximumThresholdValue:graph.add((concentration,RDF.type,E.MaximumConcentration))
            elif value==T.RangeThresholdValue:graph.add((concentration,RDF.type,E.ConcentrationRange))
            elif value!=T.ExactThresholdValue:graph.add((concentration,predicate,value))
        else:
            newpred={C.numericValue:E.numericalValue,C.hasMeasurementUnit:E.hasMeasurementUnit,T.maximumValue:E.numericalValue,T.lowerBound:E.minimumNumericalValue,T.upperBound:E.maximumNumericalValue}.get(predicate,predicate)
            existing=set(graph.objects(concentration,newpred))
            if existing and existing!={value}:
                raise MigrationConflict(f'Conflicting concentration metadata from {wrapper} at {concentration}: {newpred}')
            graph.add((concentration,newpred,value))


def migrate_data():
    correspondence=[]
    paths=[Path('examples/example-10-textile-soc-v1.1.2.ttl'),Path('tests/abox_corpus/fixtures/valid/V08-soc-quantities-thresholds.ttl'),Path('tests/abox_corpus/fixtures/invalid/I08-soc-quantities-thresholds.ttl')]
    with zipfile.ZipFile(next((ROOT/'migration/historical').glob('*.zip'))) as archive:
        for rel in paths:
            old=Graph().parse(data=archive.read(rel.as_posix()),format='turtle')
            g=project_supported_legacy_data(old)
            for qualification in old.subjects(RDF.type,OLD.SoCTypeAQualification):g.add((qualification,E.hasSoCCriterion,E.CriterionA))
            type_d=set(old.subjects(RDF.type,OLD.SoCTypeDQualification))|set(old.subjects(RDF.type,T.TextileTypeDQualification))
            for qualification in type_d:
                g.add((qualification,E.hasSoCCriterion,E.CriterionD))
                for presence in old.subjects(OLD.hasApplicableQualification,qualification):
                    for product in old.objects(presence,OLD.hasProduct):g.add((qualification,T.appliesToProduct,product))
            for concentration,wrapper in old.subject_objects(OLD.hasQuantitativeValue):
                flatten_concentration_wrapper(old,g,concentration,wrapper)
                correspondence.append({'fixture':rel.as_posix(),'old_value_node':str(wrapper),'new_concentration_node':str(concentration)})
            # E10's anonymous dimensionless unit is quantity-specifically mapped to
            # CORE's decimal mass ratio convention. No numerical rescaling/sameAs.
            for owner in list(g.subjects(E.hasMeasurementUnit,URIRef('https://example.org/textile-soc/dimensionlessUnit'))):
                g.set((owner,E.hasMeasurementUnit,E.massFractionUnit))
            for owner in list(g.subjects(C.hasMeasurementUnit,URIRef('https://example.org/textile-soc/dimensionlessUnit'))):
                g.set((owner,C.hasMeasurementUnit,E.massFractionUnit))
            for presence,instruction in g.subject_objects(T.hasTextileHandlingInformation):
                for kind,edge in [('RecyclingInstructionType',E.hasRecyclingInstruction),('SafeUseInstructionType',E.hasSafeUseInstruction),('ReuseInstructionType',E.hasReuseInstruction),('DisassemblyInstructionType',E.hasDisassemblyInstruction),('PreparationForReuseInstructionType',E.hasPreparationForReuseInstruction),('EndOfLifeManagementInstructionType',E.hasEndOfLifeManagementInstruction)]:
                    if (instruction,T.hasInstructionType,T[kind]) in g:g.add((presence,edge,instruction))
            target=rel
            if rel.as_posix().startswith('examples/'):
                target=Path(rel.as_posix().replace('-v1.1.2.ttl','-v2.0.0.ttl'))
                if (ROOT/rel).exists():(ROOT/rel).unlink()
            save(g,ROOT/target)
    (ROOT/'migration/node-correspondence.json').write_text(json.dumps(correspondence,indent=2)+'\n',encoding='utf8',newline='\n')
    rows=[]
    used=set(MAP)
    with zipfile.ZipFile(next((ROOT/'migration/historical').glob('*.zip'))) as archive:
        old_paths=['ontology/textile-soc.ttl','ontology/textile-associated-materials.ttl',*(p.as_posix() for p in paths)]
        for path in old_paths:
            old_graph=Graph().parse(data=archive.read(path),format='turtle')
            used.update(str(x)[len(str(OLD)):] for triple in old_graph for x in triple if isinstance(x,URIRef) and str(x).startswith(str(OLD)))
    for name in sorted(used):
        new=str(mapped(OLD[name]));treatment='CORE reuse' if new.startswith(str(E)) else 'Textile retained extension / quantity-specific SI alignment'
        if name=='hasQuantitativeValue':new='';treatment='Concentration wrapper edge eliminated; transfer fields using node-correspondence.json'
        if name=='SoCTypeAQualification':treatment='CORE assertion with explicit CriterionA in migrated data'
        if name=='SoCTypeDQualification':treatment='CORE assertion with explicit CriterionD and preserved applicable product scope'
        rows.append({'old_iri':str(OLD[name]),'new_iri':new,'treatment':treatment})
    for old,new in [('numericValue',E.numericalValue),('maximumValue',E.numericalValue),('lowerBound',E.minimumNumericalValue),('upperBound',E.maximumNumericalValue),('hasUnit',E.hasMeasurementUnit)]:
        rows.append({'old_iri':str(OLD[old]),'new_iri':str(new),'treatment':'Concentration wrapper context only; threshold expressions retain shared/local Textile carriers'})
    with (ROOT/'migration/semantic-mapping.csv').open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['old_iri','new_iri','treatment'],lineterminator='\n');writer.writeheader();writer.writerows(rows)


def catalog():
    ns='urn:oasis:names:tc:entity:xmlns:xml:catalog';ET.register_namespace('',ns)
    # Historical versions require their own catalogue for the entire load.
    # A top-level alias here would resolve their versionless imports as current.
    mappings={}
    for file in (ROOT/'dependencies/current-core').glob('*.owl'):
        for iri in parse(file).subjects(RDF.type,OWL.Ontology):mappings[str(iri)]=file.relative_to(ROOT).as_posix()
    for area in ('ontology','mireot','shacl'):
        files=(ROOT/area).rglob('*.ttl') if area=='shacl' else (ROOT/area).glob('*.ttl')
        for file in files:
            g=parse(file)
            for iri in g.subjects(RDF.type,OWL.Ontology):
                mappings[str(iri)]=file.relative_to(ROOT).as_posix()
                for version in g.objects(iri,OWL.versionIRI):
                    if not str(version).endswith(('/1.1.2','/1.1.3')):
                        mappings[str(version)]=file.relative_to(ROOT).as_posix()
    new=ET.Element('{'+ns+'}catalog',prefer='public')
    for iri,path in sorted(mappings.items()):ET.SubElement(new,'{'+ns+'}uri',name=iri,uri=path)
    ET.indent(new,space='  ')
    (ROOT/'catalog-v001.xml').write_bytes(ET.tostring(new,encoding='UTF-8',xml_declaration=True)+b'\n')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['1','2'])
    stage1() if parser.parse_args().stage=='1' else stage2()
