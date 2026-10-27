"""Targeted corrections over the accepted candidate; never rebuild history or CORE.

Safe to rerun: source matches, attribution inventory and mapping are deterministic.
"""
import csv
import hashlib
import json
from rdflib import URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import SKOS
from migration import implement_core as m


def provenance_and_metadata():
    old=m.parse(m.HISTORY/'dependencies/soc.ttl')
    graph=m.parse(m.ROOT/'ontology/textile-soc.ttl')
    rows=[]
    for subject in sorted(set(graph.subjects())):
        if not isinstance(subject,URIRef) or not str(subject).startswith(str(m.T)):continue
        source=m.OLD[str(subject).split('#')[-1]]
        matches=[(p,o) for p in (SKOS.definition,RDFS.comment) for o in graph.objects(subject,p) if (source,p,o) in old]
        if matches:
            graph.add((subject,m.DC.source,URIRef('https://w3id.org/eudpp/soc')))
            graph.remove((subject,m.DC.isVersionOf,source))
            graph.add((subject,URIRef('http://www.w3.org/ns/prov#wasDerivedFrom'),source))
            graph.set((subject,m.C.sourceType,m.C.adaptedDefinition))
            graph.set((subject,m.C.sourceLocator,Literal('Historical SOC 0.1.2, '+str(source)+'; local adaptation: docs/decisions/TXT-DEC-010.md',lang='en')))
            graph.set((subject,m.C.modellingNote,Literal('Definition/comment adapted from historical SOC 0.1.2. Local namespace, scope and CORE alignment are Textile decisions documented in docs/decisions/TXT-DEC-010.md; no equivalence to the historical resource is asserted.',lang='en')))
            rows.append(dict(resource_iri=str(subject),source_resource=str(source),source_file='migration/historical/1.1.2/dependencies/soc.ttl',
                             copied_annotations=[dict(predicate=str(p),text=str(o),language=o.language,datatype=str(o.datatype) if o.datatype else None,text_sha256=hashlib.sha256(str(o).encode()).hexdigest()) for p,o in sorted(matches,key=lambda x:(str(x[0]),str(x[1]))) ]))
        labels=list(graph.objects(subject,RDFS.label))
        if len([x for x in labels if x.language=='en'])>1:
            # Remove only the mechanical local-name label when a descriptive
            # historical English label is also present.
            mechanical=Literal(str(subject).split('#')[-1],lang='en')
            if mechanical in labels:graph.remove((subject,RDFS.label,mechanical))
    assert len(rows)==42
    graph.add((m.T.isPartOfProduct,OWL.inverseOf,m.T.hasPart))
    # No broad qualification domain for the two criterion-specific properties.
    graph.set((m.T.isQualifiedByProductGroupList,RDFS.domain,m.T.TextileTypeDQualification))
    # Criterion A has no dedicated Textile class: keep the common CORE domain
    # and enforce its criterion through the SHACL applicability constraint.
    definitions={
      'MaterialGroupMassBasis':'A concentration reference basis using the mass of the identified material reporting group as denominator.',
      'appliesToProduct':'Identifies the product to which a qualification assertion applies in this Textile reporting profile.',
      'ExactThresholdValue':'A Textile threshold expression represented by one exact decimal mass-ratio value.',
      'MaximumThresholdValue':'A Textile threshold expression represented by an upper bound on a decimal mass ratio.',
      'RangeThresholdValue':'A Textile threshold expression represented by lower and upper decimal mass-ratio bounds.',
      'referenceIdentifier':'An identifier recorded for an external regulatory reference.',
      'referenceVersion':'A version recorded for an external regulatory reference.',
      'referenceDate':'A date recorded for an external regulatory reference.',
      'productGroupApplicability':'Text describing the product groups to which an external regulatory reference applies.',
      'maximumValue':'The upper bound of a Textile maximum threshold expression.',
      'lowerBound':'The lower bound of a Textile range threshold expression.',
      'upperBound':'The upper bound of a Textile range threshold expression.',
      'hasThresholdReferenceBasis':'Records the reference basis applicable to a regulatory threshold comparison.',
      'hasThresholdReportingLevel':'Records the reporting level applicable to a regulatory threshold comparison.',
      'refersToProductPartForThreshold':'Identifies the structural product part to which a regulatory threshold comparison applies.',
      'AtThreshold':'An evaluation result in which exact concentration and exact threshold values are equal.',
      'AboveThreshold':'An evaluation result in which the complete concentration interval lies above the threshold interval.',
      'IndeterminateThresholdResult':'An evaluation result in which the recorded intervals overlap without establishing an exact equality or a strictly lower or higher relation.'}
    for name,text in definitions.items():graph.set((m.T[name],SKOS.definition,Literal(text,lang='en')))
    graph.set((m.T.appliesToProduct,RDFS.label,Literal('qualification applies to product',lang='en')))
    graph.set((m.T.appliesToProduct,m.C.modellingNote,Literal('Qualification applicability in the Textile SoC profile. This differs from dpp:appliesToProduct, whose domain is DigitalProductPassport. Always use the txtsoc prefix for qualification scope.',lang='en')))
    m.save(graph,m.ROOT/'ontology/textile-soc.ttl')
    (m.ROOT/'migration/legacy-soc-attribution.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8',newline='\n')


def mapping_inventory():
    old=m.parse(m.HISTORY/'mireot/soc-textile-mireot.ttl')
    active=m.parse(m.ROOT/'ontology/textile-soc.ttl')
    subjects=sorted({s for s in old.subjects() if isinstance(s,URIRef) and str(s).startswith(str(m.OLD))})
    rows=[]
    for subject in subjects:
        name=str(subject).split('#')[-1]
        destination=m.MAP.get(name)
        if destination is not None:
            treatment='direct CORE reuse' if str(destination).startswith(str(m.E)) else 'Textile retained extension'
            if name in ('SoCTypeAQualification','SoCTypeDQualification','RegulatoryQualification','SubstanceOfConcernQualification','SubstancePresenceContext','SubstanceOfConcernPresenceContext'):
                treatment='context-dependent migration; no unconditional equivalence; positive SoC reports only; retain criterion and product applicability'
            if name=='isPartOfProduct':treatment='inverse relationship treatment; inverse of txtsoc:hasPart'
            if name in ('ExactQuantitativeValue','MaximumQuantitativeValue','RangeQuantitativeValue','QuantitativeValue','numericValue','maximumValue','lowerBound','upperBound','hasUnit'):
                treatment='context-dependent migration; threshold expression only'
            rows.append(dict(old_iri=str(subject),new_iri=str(destination),treatment=treatment))
        elif name=='hasQuantitativeValue':
            rows.append(dict(old_iri=str(subject),new_iri='',treatment='context-dependent migration; concentration wrapper eliminated after checked field transfer; no direct replacement'))
        else:
            inverse=any(old.objects(subject,OWL.inverseOf)) or any(old.subjects(OWL.inverseOf,subject))
            treatment=('retired or unused inverse relationship' if inverse else 'retired or unused term')+' in bounded Textile migration; no direct replacement; unsupported input requires manual review'
            rows.append(dict(old_iri=str(subject),new_iri='',treatment=treatment))
    for name,destination in [('ExactQuantitativeValue',m.E.ConcentrationOfSubstanceOfConcern),('MaximumQuantitativeValue',m.E.MaximumConcentration),('RangeQuantitativeValue',m.E.ConcentrationRange),('numericValue',m.E.numericalValue),('maximumValue',m.E.numericalValue),('lowerBound',m.E.minimumNumericalValue),('upperBound',m.E.maximumNumericalValue),('hasUnit',m.E.hasMeasurementUnit)]:
        rows.append(dict(old_iri=str(m.OLD[name]),new_iri=str(destination),treatment='context-dependent migration; concentration wrapper fields/types transferred onto concentration; no identity equivalence'))
    assert len(subjects)==96
    with (m.ROOT/'migration/semantic-mapping.csv').open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['old_iri','new_iri','treatment'],lineterminator='\n');writer.writeheader();writer.writerows(rows)


def bounded_con():
    path=m.ROOT/'migration/extraction-scopes.json'
    scopes=json.loads(path.read_text('utf8'));record=scopes['con']
    record['roots']='hasSubstancePresence isSubstancePresenceOf isLocatedInProduct hasConcentration SubstanceManagementInstruction'.split()
    graph=m.parse(m.ROOT/'mireot/con-textile-mireot.ttl')
    iri=URIRef('https://w3id.org/eudpp/textile-con-mireot');header=list(graph.triples((iri,None,None)))
    graph=m.extract(m.parse(m.SOURCE/record['source']),[m.E[n] for n in record['roots']])
    record['copied_triples']=len(graph)
    for triple in header:graph.add(triple)
    m.save(graph,m.ROOT/'mireot/con-textile-mireot.ttl')
    path.write_text(json.dumps(scopes,indent=2)+'\n',encoding='utf8',newline='\n')


if __name__=='__main__':
    provenance_and_metadata()
    mapping_inventory()
    bounded_con()
