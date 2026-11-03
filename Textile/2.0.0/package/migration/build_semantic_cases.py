"""Generate reviewed positive coverage and single-defect migration fixtures."""
import json
from rdflib import Graph, Namespace, Literal, RDF, XSD
from rdflib.namespace import SH
from migration.implement_core import ROOT,E,T,A,C,UNITS,parse,save
S=Namespace('https://w3id.org/eudpp/textile-shacl#')
EX=Namespace('https://example.org/textile-soc/')
V=Namespace('https://example.org/textile-abox/valid/')
P=ROOT/'tests/abox_corpus/fixtures'
base=parse(ROOT/'examples/example-10-textile-soc-v2.0.0.ttl')
base+=parse(P/'valid/V08-soc-quantities-thresholds.ttl')
for node,cls in [(EX.maximumConcentration,E.MaximumConcentration),(EX.rangeConcentration,E.ConcentrationRange)]:
    base.add((node,RDF.type,T.TextileConcentrationInformation));base.add((node,RDF.type,cls))
    base.add((node,E.hasMeasurementUnit,E.massFractionUnit))
base.add((EX.maximumConcentration,E.numericalValue,Literal('0.002',datatype=XSD.decimal)))
base.add((EX.rangeConcentration,E.minimumNumericalValue,Literal('0.0006',datatype=XSD.decimal)))
base.add((EX.rangeConcentration,E.maximumNumericalValue,Literal('0.0009',datatype=XSD.decimal)))
base.add((EX.typeDQualification,RDF.type,T.TextileTypeDQualification))
base.add((EX.typeDQualification,E.qualifiesSubstance,EX.reportedSubstance))
base.add((EX.typeDQualification,E.hasSoCCriterion,E.CriterionD))
base.add((EX.typeDQualification,T.appliesToProduct,EX.jacket))
base.add((EX.typeDQualification,T.hasRegulatoryBasis,EX.reference))
base.add((EX.reference,RDF.type,T.TextileProductGroupSoCReference))
base.add((EX.reference,T.referenceIdentifier,Literal('Illustrative reference; no legal determination')))
base.add((EX.reference,T.referenceVersion,Literal('example-v1')))
base.add((EX.reference,T.referenceDate,Literal('2026-10-15',datatype=XSD.date)))
base.add((EX.reference,T.productGroupApplicability,Literal('Illustrative textile product group')))
base.add((EX.presence,E.hasApplicableQualification,EX.typeDQualification))
base.add((EX.otherPresence,RDF.type,T.TextileSubstanceOfConcernPresenceContext))
base.add((EX.otherPresence,E.isSubstancePresenceOf,EX.otherProduct))
base.add((EX.otherPresence,E.concernsSubstance,EX.reportedSubstance))
base.add((EX.otherPresence,E.hasApplicableQualification,EX.typeAQualification))
base.add((EX.otherPresence,E.hasConcentration,EX.maximumConcentration))
# Neither generic chemical use nor a material grouping asserts a positive SoC.
PR=Namespace('https://w3id.org/eudpp/textile-process#')
base.add((EX.genericChemical,RDF.type,A.TextileChemicalSubstance))
base.add((EX.execution,RDF.type,PR.TextileProcessExecution))
base.add((EX.execution,PR.concernsProduct,EX.jacket))
base.add((EX.execution,PR.usesChemicalSubstance,EX.genericChemical))
save(base,P/'valid/V09-soc-migration-coverage.ttl')
scenarios=[]


def result(focus,shape,component='SPARQLConstraintComponent',path=None):
    return {'focus_node':str(focus),'source_shape':str(S[shape]),'constraint_component':str(SH[component]),
            'result_path':None if path is None else str(path),'severity':str(SH.Violation),
            'source_constraint_message_sha256':None}


def case(name,changes,expected,complete=False,conforms=False):
    graph=Graph()+base
    for action,triple in changes:
        if action=='remove':graph.remove(triple)
        else:graph.add(triple)
    folder='valid' if conforms else 'invalid'
    rel=f'tests/abox_corpus/fixtures/{folder}/{name}.ttl'
    save(graph,ROOT/rel)
    constraint_names={
      'M11':'ConcentrationRangeOrder','M12':'ThresholdRangeOrder','M13':'ThresholdNotConcentration',
      'M14':'MaximumRangeDisjoint','M15':'PresenceQualificationIdentity','M16':'CriterionDContext',
      'M17':'ProductLocationNotGroup','M18':'LocationPartMembership','M19':'DenominatorPartMembership',
      'M20':'QualificationSourceRequired','M21':'ReferenceIdentityRequired','M29':'EvaluationIntervalOutcome',
      'M30':'EvaluationIntervalOutcome','M32':'EvaluationBasisCompatibility',
      'M36':'ExactThresholdValueShapeNotConcentration','M38':'EvaluationIntervalOutcome'}
    for row in expected:
        if row['constraint_component']==str(SH.SPARQLConstraintComponent) and name[:3] in constraint_names:
            row['source_constraint']=str(S[constraint_names[name[:3]]])
    scenarios.append({'scenario_id':name,'fixture_path':rel,'complete_report':complete,
                      'expected_conforms':conforms,'expected_results':expected,'allowed_additional_results':False,
                      'result_count_min':len(expected),'result_count_max':len(expected)})


case('M01-missing-product',[('remove',(EX.presence,E.isSubstancePresenceOf,None))],[result(EX.presence,'PresenceProduct','MinCountConstraintComponent',E.isSubstancePresenceOf)])
case('M02-missing-substance',[('remove',(EX.presence,E.concernsSubstance,None))],[result(EX.presence,'PresenceSubstance','MinCountConstraintComponent',E.concernsSubstance)])
case('M03-missing-qualification',[('remove',(EX.presence,E.hasApplicableQualification,None))],[result(EX.presence,'PresenceQualification','MinCountConstraintComponent',E.hasApplicableQualification)])
partial_changes=[('remove',(EX.presence,E.hasConcentration,None)),('remove',(EX.presence,T.hasThresholdEvaluation,None))]
case('M04-missing-concentration-complete',partial_changes,[result(EX.presence,'CompletePresenceConcentration','MinCountConstraintComponent',E.hasConcentration)],complete=True)
case('M04-partial-without-concentration',partial_changes,[],conforms=True)
case('M05-missing-exact-scalar',[('remove',(EX.concentrationInformation,E.numericalValue,None))],[result(EX.concentrationInformation,'ExactConcentrationScalar','MinCountConstraintComponent',E.numericalValue)])
case('M06-missing-maximum-scalar',[('remove',(EX.maximumConcentration,E.numericalValue,None))],[result(EX.maximumConcentration,'MaximumConcentrationScalar','MinCountConstraintComponent',E.numericalValue)])
case('M07-missing-range-endpoint',[('remove',(EX.rangeConcentration,E.minimumNumericalValue,None))],[result(EX.rangeConcentration,'ConcentrationMinimum','MinCountConstraintComponent',E.minimumNumericalValue)])
case('M08-missing-unit',[('remove',(EX.concentrationInformation,E.hasMeasurementUnit,None))],[result(EX.concentrationInformation,'ConcentrationUnit','MinCountConstraintComponent',E.hasMeasurementUnit)])
for name,unit in [('M09-unknown-unit',EX.arbitraryUnit),('M10-temperature-unit',UNITS.degreeCelsius)]:
    expected=[result(EX.concentrationInformation,'ConcentrationUnit','InConstraintComponent',E.hasMeasurementUnit),result(EX.thresholdEvaluation,'TextileThresholdEvaluationShape')]
    expected[-1]['source_constraint']=str(S.EvaluationUnitCompatibility)
    case(name,[('remove',(EX.concentrationInformation,E.hasMeasurementUnit,None)),('add',(EX.concentrationInformation,E.hasMeasurementUnit,unit))],expected)
case('M11-inverted-concentration',[('remove',(EX.rangeConcentration,E.minimumNumericalValue,None)),('add',(EX.rangeConcentration,E.minimumNumericalValue,Literal('0.9',datatype=XSD.decimal)))],[result(EX.rangeConcentration,'ConcentrationRangeShape')])
case('M12-inverted-threshold',[('remove',(V.reportedRange,T.lowerBound,None)),('add',(V.reportedRange,T.lowerBound,Literal('0.95',datatype=XSD.decimal)))],[result(V.reportedRange,'RangeThresholdValueShape')])
case('M13-threshold-is-concentration',[('add',(EX.nonExemptionThreshold,RDF.type,E.ConcentrationOfSubstanceOfConcern))],[result(EX.nonExemptionThreshold,'TextileRegulatoryThresholdShape'),result(EX.nonExemptionThreshold,'ConcentrationUnit','MinCountConstraintComponent',E.hasMeasurementUnit),result(EX.nonExemptionThreshold,'ExactConcentrationScalar','MinCountConstraintComponent',E.numericalValue)])
case('M14-maximum-wrong-carrier',[('remove',(EX.maximumConcentration,E.numericalValue,None)),('add',(EX.maximumConcentration,E.maximumNumericalValue,Literal('0.002',datatype=XSD.decimal)))],[result(EX.maximumConcentration,'MaximumConcentrationScalar','MinCountConstraintComponent',E.numericalValue),result(EX.maximumConcentration,'MaximumNoMaximum','MaxCountConstraintComponent',E.maximumNumericalValue),result(EX.maximumConcentration,'MaximumConcentrationShape'),result(EX.maximumConcentration,'ConcentrationMinimum','MinCountConstraintComponent',E.minimumNumericalValue)])
case('M15-wrong-qualified-substance',[('remove',(EX.typeAQualification,E.qualifiesSubstance,None)),('add',(EX.typeAQualification,E.qualifiesSubstance,EX.genericChemical))],[result(EX.presence,'TextilePresenceShape'),result(EX.otherPresence,'TextilePresenceShape')])
case('M16-criterion-d-other-product',[('remove',(EX.typeDQualification,T.appliesToProduct,None)),('add',(EX.typeDQualification,T.appliesToProduct,EX.otherProduct))],[result(EX.presence,'TextilePresenceShape')])
case('M17-material-group-product-location',[('add',(EX.presence,E.isLocatedInProduct,EX.outerFabricMaterialGroup))],[result(EX.presence,'TextileScopeShape')])
case('M18-location-outside-structure',[('remove',(EX.locationInformation,T.refersToProductPartForLocation,None)),('add',(EX.locationInformation,T.refersToProductPartForLocation,EX.foreignGroup)),('add',(EX.foreignGroup,RDF.type,T.TextileMaterialGroup))],[result(EX.presence,'TextileScopeShape')])
case('M19-denominator-outside-structure',[('remove',(EX.concentrationInformation,T.refersToProductPartForConcentration,None)),('add',(EX.concentrationInformation,T.refersToProductPartForConcentration,EX.foreignGroup)),('add',(EX.foreignGroup,RDF.type,T.TextileMaterialGroup))],[result(EX.presence,'TextileScopeShape')])
case('M20-no-qualification-source',[('remove',(EX.typeAQualification,T.qualificationSource,None))],[result(EX.typeAQualification,'TextileQualificationShape')])
case('M21-no-structured-reference-identity',[('remove',(EX.reference,T.referenceIdentifier,None))],[result(EX.reference,'TextileRegulatoryReferenceShape')])
case('M22-no-location-type',[('remove',(EX.locationInformation,T.hasTextileLocationType,None))],[result(EX.locationInformation,'LocationType','MinCountConstraintComponent',T.hasTextileLocationType)])
case('M23-no-instruction-content',[('remove',(EX.recyclingInformation,T.instructionContent,None))],[result(EX.recyclingInformation,'InstructionText','MinCountConstraintComponent',T.instructionContent)])
case('M24-no-threshold-expression',[('remove',(V.trackingThreshold,T.hasThresholdQuantitativeValue,None))],[result(V.trackingThreshold,'ThresholdExpression','MinCountConstraintComponent',T.hasThresholdQuantitativeValue)])
case('M25-no-exact-threshold-scalar',[('remove',(EX.thresholdMassFraction,C.numericValue,None))],[result(EX.thresholdMassFraction,'ExactThresholdScalar','MinCountConstraintComponent',C.numericValue)])
case('M26-no-maximum-threshold-scalar',[('remove',(V.maximumAllowed,T.maximumValue,None))],[result(V.maximumAllowed,'MaximumThresholdScalar','MinCountConstraintComponent',T.maximumValue)])
case('M27-no-range-threshold-endpoint',[('remove',(V.reportedRange,T.lowerBound,None))],[result(V.reportedRange,'ThresholdMinimum','MinCountConstraintComponent',T.lowerBound)])
case('M28-no-evaluation-result',[('remove',(EX.thresholdEvaluation,T.hasThresholdEvaluationResult,None))],[result(EX.thresholdEvaluation,'EvaluationResult','MinCountConstraintComponent',T.hasThresholdEvaluationResult)])
case('M29-incorrect-threshold-outcome',[('remove',(EX.thresholdEvaluation,T.hasThresholdEvaluationResult,None)),('add',(EX.thresholdEvaluation,T.hasThresholdEvaluationResult,T.AboveThreshold))],[result(EX.thresholdEvaluation,'TextileThresholdEvaluationShape')])
case('M30-overlapping-intervals',[('add',(EX.concentrationInformation,RDF.type,E.ConcentrationRange)),('remove',(EX.concentrationInformation,E.numericalValue,None)),('add',(EX.concentrationInformation,E.minimumNumericalValue,Literal('0.0006',datatype=XSD.decimal))),('add',(EX.concentrationInformation,E.maximumNumericalValue,Literal('0.0015',datatype=XSD.decimal)))],[result(EX.thresholdEvaluation,'TextileThresholdEvaluationShape')])
case('M31-compatible-overlap-indeterminate',[('add',(EX.concentrationInformation,RDF.type,E.ConcentrationRange)),('remove',(EX.concentrationInformation,E.numericalValue,None)),('add',(EX.concentrationInformation,E.minimumNumericalValue,Literal('0.0006',datatype=XSD.decimal))),('add',(EX.concentrationInformation,E.maximumNumericalValue,Literal('0.0015',datatype=XSD.decimal))),('remove',(EX.thresholdEvaluation,T.hasThresholdEvaluationResult,None)),('add',(EX.thresholdEvaluation,T.hasThresholdEvaluationResult,T.IndeterminateThresholdResult))],[],conforms=True)
case('M32-threshold-denominator-mismatch',[('add',(EX.nonExemptionThreshold,T.hasThresholdReferenceBasis,T.ProductMassBasis))],[result(EX.thresholdEvaluation,'TextileThresholdEvaluationShape')])
case('M33-missing-evaluation-input',[('remove',(EX.thresholdEvaluation,T.evaluatesConcentrationInformation,None))],[result(EX.thresholdEvaluation,'EvaluationConcentration','MinCountConstraintComponent',T.evaluatesConcentrationInformation)])
case('M34-missing-evaluation-threshold',[('remove',(EX.thresholdEvaluation,T.evaluatesAgainstThreshold,None))],[result(EX.thresholdEvaluation,'EvaluationThreshold','MinCountConstraintComponent',T.evaluatesAgainstThreshold)])
case('M35-negative-concentration',[('remove',(EX.maximumConcentration,E.numericalValue,None)),('add',(EX.maximumConcentration,E.numericalValue,Literal('-0.1',datatype=XSD.decimal)))],[result(EX.maximumConcentration,'MaximumConcentrationScalar','MinInclusiveConstraintComponent',E.numericalValue)])
case('M36-threshold-expression-is-concentration',[('add',(EX.thresholdMassFraction,RDF.type,E.ConcentrationOfSubstanceOfConcern))],[result(EX.thresholdMassFraction,'ExactThresholdValueShape'),result(EX.thresholdMassFraction,'ConcentrationUnit','MinCountConstraintComponent',E.hasMeasurementUnit),result(EX.thresholdMassFraction,'ExactConcentrationScalar','MinCountConstraintComponent',E.numericalValue)])
case('M37-range-threshold-comparison',[('remove',(EX.thresholdEvaluation,T.evaluatesAgainstThreshold,None)),('add',(EX.thresholdEvaluation,T.evaluatesAgainstThreshold,V.trackingThreshold)),('add',(EX.concentrationInformation,T.hasApplicableRegulatoryThreshold,V.trackingThreshold))],[],conforms=True)
maxchanges=[('remove',(EX.thresholdEvaluation,T.evaluatesAgainstThreshold,None)),('add',(EX.thresholdEvaluation,T.evaluatesAgainstThreshold,V.recyclingAlertThreshold)),('add',(EX.concentrationInformation,T.hasApplicableRegulatoryThreshold,V.recyclingAlertThreshold))]
case('M38-maximum-threshold-overlap',maxchanges,[result(EX.thresholdEvaluation,'TextileThresholdEvaluationShape')])
case('M39-maximum-threshold-indeterminate',maxchanges+[('remove',(EX.thresholdEvaluation,T.hasThresholdEvaluationResult,None)),('add',(EX.thresholdEvaluation,T.hasThresholdEvaluationResult,T.IndeterminateThresholdResult))],[],conforms=True)
scope_expected=[result(EX.concentrationInformation,'TextileConcentrationShape'),result(EX.thresholdEvaluation,'TextileThresholdEvaluationShape')]
scope_expected[0]['source_constraint']=str(S.ConcentrationMaterialScope)
scope_expected[1]['source_constraint']=str(S.EvaluationScopeRequired)
case('M40-evaluation-missing-scope',[('remove',(EX.concentrationInformation,T.hasConcentrationReferenceBasis,None))],scope_expected)
doc={'schema_version':2,'validation_scope':'SoC structural profile only, plus complete-report where selected. Existing full-regression scenarios retain all shared profiles.','scenarios':scenarios}
(ROOT/'tests/abox_corpus/expectations/migration-shacl-expectations.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf8',newline='\n')
print(f'Positive focus coverage and {len(scenarios)} discriminating migration scenarios written.')
