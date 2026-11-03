"""Discriminating controls for the SHACL result contract matcher."""
import copy
import importlib.util
from pathlib import Path

import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF
from rdflib.namespace import SH, XSD

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('textile_validator', ROOT/'scripts/validate_public.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
EX = Namespace('https://example.org/contract/')


def sample():
    shapes = Graph()
    prop = BNode()
    shapes.add((EX.Shape, SH.property, prop))
    shapes.add((prop, SH.path, EX.value))
    shapes.add((prop, SH.datatype, XSD.decimal))
    report = Graph()
    result = BNode()
    for predicate, value in ((RDF.type, SH.ValidationResult),
                             (SH.focusNode, EX.focus), (SH.sourceShape, prop),
                             (SH.sourceConstraintComponent, SH.DatatypeConstraintComponent),
                             (SH.resultPath, EX.value), (SH.resultSeverity, SH.Violation),
                             (SH.resultMessage, Literal('Expected decimal'))):
        report.add((result, predicate, value))
    expected = dict(focus_node=str(EX.focus), source_shape=str(EX.Shape),
                    constraint_component=str(SH.DatatypeConstraintComponent),
                    result_path=str(EX.value), severity=str(SH.Violation),
                    source_constraint_message_sha256=v.hashlib.sha256(b'Expected decimal').hexdigest())
    contract = dict(scenario_id='matcher-control', expected_results=[expected],
                    result_count_min=1, result_count_max=2, allowed_additional_results=False)
    return shapes, report, contract, result, prop


def test_anonymous_property_shape_resolves_to_owning_shape():
    shapes, report, contract, _, _ = sample()
    v.match_shacl_results(report, shapes, contract)


@pytest.mark.parametrize('field', ['focus_node', 'source_shape', 'constraint_component',
                                  'result_path', 'severity', 'source_constraint_message_sha256'])
def test_same_count_with_wrong_constraint_identity_is_rejected(field):
    shapes, report, contract, _, _ = sample()
    contract['expected_results'][0][field] = str(EX.wrong)
    with pytest.raises(ValueError, match='Missing expected SHACL result'):
        v.match_shacl_results(report, shapes, contract)


def test_unrelated_anonymous_shape_with_same_path_is_rejected():
    shapes, report, contract, result, _ = sample()
    other = BNode()
    shapes.add((EX.OtherShape, SH.property, other))
    shapes.add((other, SH.path, EX.value))
    report.set((result, SH.sourceShape, other))
    with pytest.raises(ValueError, match='Missing expected SHACL result'):
        v.match_shacl_results(report, shapes, contract)


def test_duplicate_result_cannot_satisfy_one_expected_result():
    shapes, report, contract, result, _ = sample()
    duplicate = BNode()
    for predicate, value in list(report.predicate_objects(result)):
        report.add((duplicate, predicate, value))
    with pytest.raises(ValueError, match='Unexpected additional SHACL results'):
        v.match_shacl_results(report, shapes, contract)


def test_one_actual_result_cannot_satisfy_duplicate_expectations():
    shapes, report, contract, _, _ = sample()
    contract['expected_results'].append(copy.deepcopy(contract['expected_results'][0]))
    with pytest.raises(ValueError, match='Missing expected SHACL result'):
        v.match_shacl_results(report, shapes, contract)


def test_anonymous_source_path_must_match_reported_path():
    shapes, report, contract, _, prop = sample()
    shapes.set((prop, SH.path, EX.unrelated))
    with pytest.raises(ValueError, match='unexpected result path'):
        v.match_shacl_results(report, shapes, contract)


def test_specific_source_constraint_identity_is_checked():
    shapes, report, contract, result, _ = sample()
    report.add((result, SH.sourceConstraint, EX.ExpectedConstraint))
    contract['expected_results'][0]['source_constraint'] = str(EX.ExpectedConstraint)
    v.match_shacl_results(report, shapes, contract)
    contract['expected_results'][0]['source_constraint'] = str(EX.UnrelatedConstraint)
    with pytest.raises(ValueError, match='Missing expected SHACL result'):
        v.match_shacl_results(report, shapes, contract)
