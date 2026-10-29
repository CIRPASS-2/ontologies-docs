"""Build named, independently testable Textile SoC validation constraints."""
from rdflib import Graph, URIRef, BNode, Literal, Namespace, RDF, XSD
from rdflib.namespace import SH, OWL, RDFS
from rdflib.collection import Collection
from migration.implement_core import ROOT, E, T, A, C, SI, UNITS, save

S=Namespace('https://w3id.org/eudpp/textile-shacl#')
g=Graph()
PREFIX='''PREFIX e: <https://w3id.org/eudpp#>
PREFIX t: <https://w3id.org/eudpp/textile-soc#>
PREFIX a: <https://w3id.org/eudpp/textile-associated-materials#>
PREFIX c: <https://w3id.org/eudpp/textile-connector#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
'''


def shape(name, cls=None, objects=None):
    s=S[name];g.add((s,RDF.type,SH.NodeShape))
    if cls:g.add((s,SH.targetClass,cls))
    if objects:g.add((s,SH.targetObjectsOf,objects))
    return s


def prop(s, name, path, minimum=None, maximum=1, datatype=None, cls=None, allowed=None):
    p=S[name];g.add((s,SH.property,p));g.add((p,RDF.type,SH.PropertyShape));g.add((p,SH.path,path))
    if minimum is not None:g.add((p,SH.minCount,Literal(minimum)))
    if maximum is not None:g.add((p,SH.maxCount,Literal(maximum)))
    if datatype:g.add((p,SH.datatype,datatype))
    if datatype==XSD.decimal:
        g.add((p,SH.minInclusive,Literal('0',datatype=XSD.decimal)))
        g.add((p,SH.maxInclusive,Literal('1',datatype=XSD.decimal)))
    if cls:g.add((p,SH['class'],cls))
    if allowed is not None:
        node=BNode();Collection(g,node,allowed);g.add((p,SH['in'],node))
    return p


def query(s,name,message,body):
    constraint=S[name];g.add((s,SH.sparql,constraint));g.add((constraint,RDF.type,SH.SPARQLConstraint))
    g.add((constraint,SH.message,Literal(message,lang='en')))
    g.add((constraint,SH.select,Literal(PREFIX+'SELECT DISTINCT $this WHERE { '+body+' }')))


presence=shape('TextilePresenceShape',T.TextileSubstanceOfConcernPresenceContext)
prop(presence,'PresenceProduct',E.isSubstancePresenceOf,1,cls=E.Product)
prop(presence,'PresenceSubstance',E.concernsSubstance,1,cls=E.Substance)
prop(presence,'PresenceQualification',E.hasApplicableQualification,1,maximum=None,cls=E.SoCQualificationAssertion)
query(presence,'PresenceQualificationIdentity','The applicable qualification must qualify the same substance.',
      '$this e:concernsSubstance ?s; e:hasApplicableQualification ?q. ?q e:qualifiesSubstance ?other. FILTER (?s != ?other)')
query(presence,'CriterionDContext','Criterion D requires an explicit qualification scope matching the owning product.',
      '$this e:isSubstancePresenceOf ?product; e:hasApplicableQualification ?q. ?q e:hasSoCCriterion e:CriterionD. FILTER NOT EXISTS { ?q t:appliesToProduct ?product }')
query(presence,'PresenceProductNotPart','A material group or structural part must not be used as the owning product.',
      '$this e:isSubstancePresenceOf ?product. ?product a a:TextileProductPart.')

qualification=shape('TextileQualificationShape',objects=E.hasApplicableQualification)
prop(qualification,'QualificationSubstance',E.qualifiesSubstance,1,cls=E.Substance)
prop(qualification,'QualificationCriteria',E.hasSoCCriterion,1,maximum=None,allowed=[E.CriterionA,E.CriterionB,E.CriterionC,E.CriterionD])
prop(qualification,'QualificationSourceText',T.qualificationSource,maximum=None,datatype=XSD.string)
prop(qualification,'QualificationBasis',T.hasRegulatoryBasis,maximum=None,cls=T.ExternalRegulatoryReference)
query(qualification,'QualificationSourceRequired','A qualification needs preserved source text or a structured regulatory basis.',
      'FILTER NOT EXISTS { $this t:qualificationSource ?text. FILTER(STRLEN(STR(?text)) > 0) } FILTER NOT EXISTS { $this t:hasRegulatoryBasis ?reference }')
for relation,criterion in [('isQualifiedBySVHCList','CriterionA'),('isQualifiedByProductGroupList','CriterionD')]:
    query(qualification,relation+'Criterion','A criterion-specific regulatory basis requires its matching criterion.',
          '$this t:'+relation+' ?basis. FILTER NOT EXISTS { $this e:hasSoCCriterion e:'+criterion+' }')

reference=shape('TextileRegulatoryReferenceShape',objects=T.hasRegulatoryBasis)
prop(reference,'ReferenceIdentifier',T.referenceIdentifier,datatype=XSD.string)
prop(reference,'ReferenceVersion',T.referenceVersion,datatype=XSD.string)
prop(reference,'ReferenceDate',T.referenceDate,datatype=XSD.date)
prop(reference,'ReferenceApplicability',T.productGroupApplicability,datatype=XSD.string)
query(reference,'ReferenceIdentityRequired','A structured regulatory reference needs its original identifier or source text.',
      'FILTER NOT EXISTS { $this t:referenceIdentifier ?id } FILTER NOT EXISTS { $this <http://purl.org/dc/terms/source> ?source }')

location=shape('TextileLocationShape',objects=T.hasLocationInformation)
prop(location,'LocationType',T.hasTextileLocationType,1,cls=T.TextileSoCLocationTypeConcept)
prop(location,'LocationPart',T.refersToProductPartForLocation,cls=A.TextileProductPart)
prop(location,'LocationDescriptor',T.locationDescriptor,datatype=XSD.string)

scope=shape('TextileScopeShape',T.TextileSubstanceOfConcernPresenceContext)
membership='(t:hasPart|^t:isPartOfProduct|a:hasNonTextileComponent)+'
query(scope,'LocationPartMembership','A location part must belong to the owning product structure.',
      '$this e:isSubstancePresenceOf ?product; t:hasLocationInformation ?loc. ?loc t:refersToProductPartForLocation ?part. FILTER NOT EXISTS { ?product '+membership+' ?part }')
query(scope,'DenominatorPartMembership','A concentration denominator part must belong to the owning product structure.',
      '$this e:isSubstancePresenceOf ?product; e:hasConcentration ?conc. ?conc t:refersToProductPartForConcentration ?part. FILTER NOT EXISTS { ?product '+membership+' ?part }')
query(scope,'ProductLocationNotGroup','CORE product-location objects must be products, not structural material groups.',
      '$this e:isLocatedInProduct ?part. ?part a a:TextileProductPart.')

concentration=shape('TextileConcentrationShape',E.ConcentrationOfSubstanceOfConcern,objects=E.hasConcentration)
prop(concentration,'ConcentrationUnit',E.hasMeasurementUnit,1,allowed=[E.massFractionUnit,UNITS.one])
prop(concentration,'ConcentrationBasis',T.hasConcentrationReferenceBasis,cls=T.ConcentrationReferenceBasis)
prop(concentration,'ConcentrationLevel',T.hasConcentrationReportingLevel,cls=T.ReportingLevel)
prop(concentration,'ConcentrationPart',T.refersToProductPartForConcentration,cls=A.TextileProductPart)
prop(concentration,'ConcentrationMethod',T.analyticalMethod,datatype=XSD.string)
query(concentration,'ConcentrationMaterialScope','Material reporting requires a material-group denominator and reference basis.',
      '$this t:hasConcentrationReportingLevel t:MaterialLevel. FILTER NOT EXISTS { $this t:hasConcentrationReferenceBasis t:MaterialGroupMassBasis; t:refersToProductPartForConcentration ?part. ?part a t:MaterialGroup }')

exact=shape('ExactConcentrationShape')
target=BNode();g.add((exact,SH.target,target));g.add((target,RDF.type,SH.SPARQLTarget))
g.add((target,SH.select,Literal(PREFIX+'''SELECT ?this WHERE { ?this a e:ConcentrationOfSubstanceOfConcern.
 FILTER NOT EXISTS { ?this a e:MaximumConcentration } FILTER NOT EXISTS { ?this a e:ConcentrationRange } }''')))
prop(exact,'ExactConcentrationScalar',E.numericalValue,1,datatype=XSD.decimal)
prop(exact,'ExactNoMinimum',E.minimumNumericalValue,maximum=0)
prop(exact,'ExactNoMaximum',E.maximumNumericalValue,maximum=0)
maximum=shape('MaximumConcentrationShape',E.MaximumConcentration)
prop(maximum,'MaximumConcentrationScalar',E.numericalValue,1,datatype=XSD.decimal)
prop(maximum,'MaximumNoMinimum',E.minimumNumericalValue,maximum=0)
prop(maximum,'MaximumNoMaximum',E.maximumNumericalValue,maximum=0)
query(maximum,'MaximumRangeDisjoint','Maximum concentration must not also be a concentration range.', '$this a e:ConcentrationRange.')
range_=shape('ConcentrationRangeShape',E.ConcentrationRange)
prop(range_,'ConcentrationMinimum',E.minimumNumericalValue,1,datatype=XSD.decimal)
prop(range_,'ConcentrationMaximum',E.maximumNumericalValue,1,datatype=XSD.decimal)
prop(range_,'RangeNoScalar',E.numericalValue,maximum=0)
query(range_,'ConcentrationRangeOrder','The lower concentration bound must not exceed the upper bound.',
      '$this e:minimumNumericalValue ?lower; e:maximumNumericalValue ?upper. FILTER (?lower > ?upper)')

threshold=shape('TextileRegulatoryThresholdShape',E.ThresholdOfSubstanceOfConcern,objects=T.evaluatesAgainstThreshold)
p=prop(threshold,'ThresholdExpression',T.hasThresholdQuantitativeValue,1,cls=C.QuantitativeValue)
head=BNode();branches=[]
for cls in (T.ExactThresholdValue,T.MaximumThresholdValue,T.RangeThresholdValue):
    branch=BNode();g.add((branch,SH['class'],cls));branches.append(branch)
Collection(g,head,branches);g.add((p,SH.xone,head))
query(threshold,'ThresholdNotConcentration','A regulatory threshold must not be typed as a concentration.', '$this a e:ConcentrationOfSubstanceOfConcern.')
for name,cls,fields,forbidden in [
 ('ExactThresholdValueShape',T.ExactThresholdValue,[(C.numericValue,'ExactThresholdScalar')],[T.maximumValue,T.lowerBound,T.upperBound]),
 ('MaximumThresholdValueShape',T.MaximumThresholdValue,[(T.maximumValue,'MaximumThresholdScalar')],[C.numericValue,T.lowerBound,T.upperBound]),
 ('RangeThresholdValueShape',T.RangeThresholdValue,[(T.lowerBound,'ThresholdMinimum'),(T.upperBound,'ThresholdMaximum')],[C.numericValue,T.maximumValue])]:
    s=shape(name,cls)
    prop(s,name+'Unit',C.hasMeasurementUnit,1,allowed=[E.massFractionUnit,UNITS.one])
    for field,label in fields:prop(s,label,field,1,datatype=XSD.decimal)
    for i,field in enumerate(forbidden):prop(s,name+'Excluded'+str(i),field,maximum=0)
    query(s,name+'NotConcentration','A threshold expression must not be typed as a concentration.', '$this a e:ConcentrationOfSubstanceOfConcern.')
query(S.RangeThresholdValueShape,'ThresholdRangeOrder','The lower threshold bound must not exceed the upper bound.',
      '$this t:lowerBound ?lower; t:upperBound ?upper. FILTER (?lower > ?upper)')

evaluation=shape('TextileThresholdEvaluationShape',T.ThresholdEvaluation)
prop(evaluation,'EvaluationConcentration',T.evaluatesConcentrationInformation,1,cls=E.ConcentrationOfSubstanceOfConcern)
prop(evaluation,'EvaluationThreshold',T.evaluatesAgainstThreshold,1,cls=E.ThresholdOfSubstanceOfConcern)
prop(evaluation,'EvaluationResult',T.hasThresholdEvaluationResult,1,
     allowed=[T.BelowThreshold,T.AtThreshold,T.AboveThreshold,T.IndeterminateThresholdResult])
query(evaluation,'EvaluationApplicability','The evaluated threshold must be applicable to the concentration.',
      '$this t:evaluatesConcentrationInformation ?c; t:evaluatesAgainstThreshold ?threshold. FILTER NOT EXISTS { ?c t:hasApplicableRegulatoryThreshold ?threshold }')
query(evaluation,'EvaluationOwnership','An evaluation attached to a presence must evaluate a concentration of that presence.',
      '?presence t:hasThresholdEvaluation $this. $this t:evaluatesConcentrationInformation ?c. FILTER NOT EXISTS { ?presence e:hasConcentration ?c }')
query(evaluation,'EvaluationScopeRequired','Numerical evaluation requires a declared concentration reference basis and reporting level.',
      '$this t:evaluatesConcentrationInformation ?c. FILTER NOT EXISTS { ?c t:hasConcentrationReferenceBasis ?basis; t:hasConcentrationReportingLevel ?level }')
query(evaluation,'EvaluationUnitCompatibility','Threshold comparison requires the same approved decimal mass-ratio unit.',
      '$this t:evaluatesConcentrationInformation ?c; t:evaluatesAgainstThreshold/t:hasThresholdQuantitativeValue ?v. ?c e:hasMeasurementUnit ?cu. ?v c:hasMeasurementUnit ?tu. FILTER (?cu != ?tu && !(?cu IN (e:massFractionUnit,<https://si-digital-framework.org/SI/units/one>) && ?tu IN (e:massFractionUnit,<https://si-digital-framework.org/SI/units/one>)))')
for suffix,concprop,thresholdprop in [('Basis',T.hasConcentrationReferenceBasis,T.hasThresholdReferenceBasis),('Level',T.hasConcentrationReportingLevel,T.hasThresholdReportingLevel),('Part',T.refersToProductPartForConcentration,T.refersToProductPartForThreshold)]:
    query(evaluation,'Evaluation'+suffix+'Compatibility','Comparison scope must match the concentration scope.',
          f'$this t:evaluatesConcentrationInformation ?c; t:evaluatesAgainstThreshold ?threshold. ?threshold <{thresholdprop}> ?scope. FILTER NOT EXISTS {{ ?c <{concprop}> ?scope }}')
# Conservative interval semantics: an upper-bound-only maximum is [0, max]
# for the mass-fraction profile; overlapping intervals remain indeterminate.
intervals='''$this t:evaluatesConcentrationInformation ?c; t:evaluatesAgainstThreshold/t:hasThresholdQuantitativeValue ?v; t:hasThresholdEvaluationResult ?result.
 {
 { ?c e:numericalValue ?cs. FILTER NOT EXISTS { ?c a e:MaximumConcentration } BIND(?cs AS ?cl) BIND(?cs AS ?cu) }
 UNION { ?c a e:MaximumConcentration; e:numericalValue ?cm. BIND(0 AS ?cl) BIND(?cm AS ?cu) }
 UNION { ?c e:minimumNumericalValue ?cl; e:maximumNumericalValue ?cu. }
 }
 {
 { ?v a t:ExactThresholdValue; c:numericValue ?ts. BIND(?ts AS ?tl) BIND(?ts AS ?tu) }
 UNION { ?v a t:MaximumThresholdValue; t:maximumValue ?tm. BIND(0 AS ?tl) BIND(?tm AS ?tu) }
 UNION { ?v a t:RangeThresholdValue; t:lowerBound ?tl; t:upperBound ?tu. }
 }
 FILTER ((?result=t:BelowThreshold && !(?cu < ?tl)) ||
         (?result=t:AboveThreshold && !(?cl > ?tu)) ||
         (?result=t:AtThreshold && !(?cl=?cu && ?tl=?tu && ?cl=?tl)) ||
         (?result=t:IndeterminateThresholdResult && (?cu < ?tl || ?cl > ?tu || (?cl=?cu && ?tl=?tu && ?cl=?tl))))'''
query(evaluation,'EvaluationIntervalOutcome','A threshold result must follow conservative interval comparison; overlap is indeterminate.',intervals)

instruction=shape('TextileHandlingInformationShape',T.TextileSoCHandlingInformation,objects=T.hasTextileHandlingInformation)
prop(instruction,'InstructionText',T.instructionContent,1,datatype=XSD.string)

iri=URIRef('https://w3id.org/eudpp/textile-shacl/soc')
g.add((iri,RDF.type,OWL.Ontology));g.add((iri,RDFS.comment,Literal('Structural partial-report profile. Concentration is required only by the separately selected complete-report profile.',lang='en')))
g.add((iri,OWL.versionIRI,URIRef(str(iri)+'/2.0.0')));g.add((iri,OWL.versionInfo,Literal('Version 2.0.0 candidate')))
save(g,ROOT/'shacl/textile-soc-shapes.ttl')
complete=Graph();s=S.CompleteTextilePresenceShape
complete.add((s,RDF.type,SH.NodeShape));complete.add((s,SH.targetClass,T.TextileSubstanceOfConcernPresenceContext))
p=S.CompletePresenceConcentration;complete.add((s,SH.property,p));complete.add((p,RDF.type,SH.PropertyShape));complete.add((p,SH.path,E.hasConcentration));complete.add((p,SH.minCount,Literal(1)))
iri=URIRef('https://w3id.org/eudpp/textile-shacl/soc/complete-report')
complete.add((iri,RDF.type,OWL.Ontology));complete.add((iri,OWL.versionIRI,URIRef(str(iri)+'/2.0.0')))
folder=ROOT/'shacl/profiles';folder.mkdir(exist_ok=True)
save(complete,folder/'textile-soc-complete-report.ttl')
print('SoC structural shapes and separately selectable complete-report profile written.')
