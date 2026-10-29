"""Public traceability integrity and source-attribution negative controls."""
import copy, importlib.util, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('textile_public',ROOT/'scripts/validate_public.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

@pytest.fixture(scope='module')
def tables():
 return (v.read_csv(ROOT/'traceability/textile-resource-traceability.csv',v.RESOURCE_FIELDS),v.read_csv(ROOT/'traceability/textile-resource-evidence.csv',v.EVIDENCE_FIELDS),v.read_csv(ROOT/'traceability/source-documents.csv',v.SOURCE_FIELDS))

def test_public_tables_match_graph_projection(tables):
 assert tables==tuple(v.derive(v.ontology_graph(ROOT))[:3])
 v.validate_links(*tables)

@pytest.mark.parametrize('fault',['duplicate_resource','orphan_resource','orphan_source','count','jrc_flag','id'])
def test_corrupt_relationship_is_rejected(tables,fault):
 r,e,s=copy.deepcopy(tables)
 if fault=='duplicate_resource':r.append(copy.deepcopy(r[0]))
 elif fault=='orphan_resource':e[0]['resource_iri']='https://example.org/missing'
 elif fault=='orphan_source':e[0]['source_document_id']='MISSING'
 elif fault=='count':r[0]['evidence_count']=str(int(r[0]['evidence_count'])+1)
 elif fault=='jrc_flag':r[0]['has_jrc_evidence']='FALSE' if r[0]['has_jrc_evidence']=='TRUE' else 'TRUE'
 elif fault=='id':e[0]['evidence_id']='EVID-0000000000000000'
 with pytest.raises(ValueError):v.validate_links(r,e,s)

def test_two_studies_cannot_exchange_pages(tables):
 _,e,_=tables
 rows=[x for x in e if x['resource_iri'].endswith('#DigitalTextileEndOfLifeInstruction')]
 assert {(x['source_document_id'],x['source_section'],x['source_page']) for x in rows}=={
 ('JRC-TEXTILE-2025-12','13.3.8','359'),('JRC-TEXTILE-2025-12','6.3.3','86'),('JRC-DPP-2026-05','7.3','49')}
 changed=copy.deepcopy(rows[0]);changed['source_page']='999'
 assert v.evidence_id(changed)!=rows[0]['evidence_id']

def test_compound_location_is_not_flattened():
 raw='JRC Section 12.1, printed page 219; Section 12.3.6, printed pages 238-239'
 section,page,compound=v.scalar_parts(raw)
 assert compound and section==page==''
 assigned,missing=v.split_locations(raw,[v.J25])
 assert assigned[v.J25]==[raw] and missing==[]

def test_external_source_is_not_automatically_jrc(tables):
 r,e,_=tables
 row=next(x for x in r if x['provenance_category']=='externalReuse')
 assert row['has_jrc_evidence']=='FALSE'
 assert all(x['source_document_id']=='TEXTILE-MAT-MIREOT' for x in e if x['resource_iri']==row['resource_iri'])

def test_ontology_headers_and_external_subjects_are_excluded(tables):
 r,_,_=tables;g=v.ontology_graph(ROOT)
 assert not any((v.URIRef(x['resource_iri']),v.RDF.type,v.OWL.Ontology) in g for x in r)
 assert all(x['resource_iri'].startswith('https://w3id.org/eudpp/textile-') for x in r)


def test_textile_ontology_headers_cannot_self_define_and_context_metadata_is_stable():
 context=v.URIRef('https://w3id.org/eudpp/textile-context')
 expected_imports={
  v.URIRef('https://w3id.org/eudpp/textile-connector'),
  v.URIRef('https://w3id.org/eudpp/textile-dpp-mireot'),
  v.URIRef('https://w3id.org/eudpp/textile-durability'),
  v.URIRef('https://w3id.org/eudpp/textile-process'),
 }
 for name in v.CURRENT_MODULES:
  graph=v.parse(ROOT/'ontology'/name)
  headers=set(graph.subjects(v.RDF.type,v.OWL.Ontology))
  assert headers, name
  offenders=[str(header) for header in headers if (header,v.RDFS.isDefinedBy,header) in graph]
  assert not offenders, (name,offenders)
 context_graph=v.parse(ROOT/'ontology/textile-context.ttl')
 assert (context,v.RDF.type,v.OWL.Ontology) in context_graph
 assert set(context_graph.objects(context,v.OWL.versionIRI))=={
  v.URIRef('https://w3id.org/eudpp/textile-context/2.0.0')
 }
 assert {str(value) for value in context_graph.objects(context,v.OWL.versionInfo)}=={'Version 2.0.0 candidate'}
 assert set(context_graph.objects(context,v.OWL.priorVersion))=={v.URIRef('https://w3id.org/eudpp/textile-context/1.1.2')}
 assert set(context_graph.objects(context,v.OWL.imports))==expected_imports

def test_missing_external_locator_stays_unresolved(tables):
 _,e,_=tables
 rows=[x for x in e if not x['source_locator']]
 assert rows and all(x['locator_status']=='UNRESOLVED' for x in rows)
 assert not any(x['locator_status']=='VERIFIED' for x in e)


def test_reversed_documentary_range_is_rejected():
 with pytest.raises(ValueError,match='Reversed recorded range'):
  v.check_recorded_ranges('JRC Section 12.1, printed pages 220-219, lines 100-110')
 with pytest.raises(ValueError,match='Reversed recorded range'):
  v.check_recorded_ranges('JRC Section 12.1, printed page 219, lines 110-100')


def test_seven_supplements_leave_only_two_unresolved(tables):
 _,e,_=tables
 assert len([x for x in e if x['source_document_id']!='HISTORICAL-SOC-0.1.2'])==904
 assert len([x for x in e if x['source_document_id']=='HISTORICAL-SOC-0.1.2'])==42
 assert {x['resource_iri'].split('#')[-1] for x in e if x['locator_status']=='UNRESOLVED'}=={'fibreCompositionLocation','nonTextileComponentLocation'}
 assert sum(x['verification_basis'].startswith('public_locator_checked_') for x in e)==7


def test_reference_and_unrelated_files_do_not_enter_package(tmp_path):
 (tmp_path/'ontology/graphwise-ontology').mkdir(parents=True)
 (tmp_path/'ontology/graphwise-ontology/ontology.ttl').write_text('deliberately not RDF')
 (tmp_path/'ref-data').mkdir()
 (tmp_path/'ref-data/arbitrary.ttl').write_text('deliberately not RDF')
 assert not any('graphwise-ontology' in p or p.startswith('ref-data/') for p in v.package_files(tmp_path))
 (tmp_path/'ontology/unapproved.ttl').write_text('unexpected current file')
 assert 'ontology/unapproved.ttl' in v.package_files(tmp_path)


def test_current_graph_does_not_read_preserved_reference(tmp_path):
 import shutil
 shutil.copytree(ROOT/'ontology',tmp_path/'ontology')
 (tmp_path/'ontology/graphwise-ontology/ontology.ttl').write_text('deliberately invalid RDF')
 assert len(v.ontology_graph(tmp_path))==len(v.ontology_graph(ROOT))


def test_catalogue_cannot_redirect_current_import_to_reference():
 cat={x.attrib['name']:x.attrib['uri'] for x in v.ET.parse(ROOT/'catalog-v001.xml').getroot()}
 imported=next(v.parse(ROOT/'ontology/textile-ontology.ttl').objects(None,v.OWL.imports))
 cat[str(imported)]='ontology/graphwise-ontology/ontology.ttl'
 with pytest.raises(ValueError,match='outside approved current closure'):
  v.current_import_closure(ROOT,cat)


def test_manifest_cannot_include_reference_in_integrity_contract(tmp_path,monkeypatch):
 import shutil
 shutil.copy(ROOT/'PUBLICATION_MANIFEST.txt',tmp_path/'PUBLICATION_MANIFEST.txt')
 for rel in v.PRESERVED_REFERENCE_MATERIAL:
  p=tmp_path/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('reference')
 expected=v.package_files(ROOT)
 monkeypatch.setattr(v,'package_files',lambda root:expected)
 assert v.manifest_sections(tmp_path)['CURRENT_PACKAGE']==expected
 text=(tmp_path/'PUBLICATION_MANIFEST.txt').read_text()
 text=text.replace('[CURRENT_PACKAGE]','[CURRENT_PACKAGE]\nontology/graphwise-ontology/ontology.ttl')
 (tmp_path/'PUBLICATION_MANIFEST.txt').write_text(text)
 with pytest.raises(ValueError,match='current package files'):
  v.manifest_sections(tmp_path)


def test_resolution_cannot_change_source_identity(tmp_path,tables):
 resolutions=v.read_csv(ROOT/'traceability/evidence-locator-resolutions.csv',v.RESOLUTION_FIELDS)
 evidence=[]
 for row in resolutions:
  original=dict(zip(v.EVIDENCE_FIELDS,['']*len(v.EVIDENCE_FIELDS)))
  original.update(evidence_id=row['previous_evidence_id'],resource_iri=row['resource_iri'],source_document_id=row['source_document_id'],locator_status='UNRESOLVED')
  evidence.append(original)
 (tmp_path/'traceability').mkdir()
 (tmp_path/'traceability/evidence-locator-resolutions.csv').write_bytes(v.csv_bytes(v.RESOLUTION_FIELDS,resolutions))
 assert len(v.apply_locator_resolutions(copy.deepcopy(evidence),tmp_path))==7
 resolutions[0]['source_document_id']='JRC-TEXTILE-2025-12'
 (tmp_path/'traceability/evidence-locator-resolutions.csv').write_bytes(v.csv_bytes(v.RESOLUTION_FIELDS,resolutions))
 with pytest.raises(ValueError,match='changes source relationship'):
  v.apply_locator_resolutions(evidence,tmp_path)


@pytest.mark.parametrize('relative_path', [
 'mireot/actor-textile-mireot.ttl',
 'mireot/dpp-textile-mireot.ttl',
 'mireot/event-textile-mireot.ttl',
 'mireot/mat-textile-mireot.ttl',
 'mireot/si-textile-mireot.ttl',
 'mireot/soc-textile-mireot.ttl',
 'mireot/con-textile-mireot.ttl',
 'dependencies/current-core/soc.owl',
])
def test_review_dependencies_are_packaged_and_checksum_covered(relative_path):
 assert (ROOT/relative_path).is_file()
 assert relative_path in v.manifest_sections(ROOT)['CURRENT_PACKAGE']
 checksums = dict(line.split('  ', 1)[::-1]
                  for line in (ROOT/'SHA256SUMS').read_text('utf8').splitlines())
 assert checksums[relative_path] == v.hashlib.sha256((ROOT/relative_path).read_bytes()).hexdigest()


def test_review_current_properties_have_single_declaration_owner():
 property_types = {v.RDF.Property, v.OWL.ObjectProperty, v.OWL.DatatypeProperty,
                   v.OWL.AnnotationProperty, v.OWL.FunctionalProperty,
                   v.OWL.InverseFunctionalProperty, v.OWL.TransitiveProperty,
                   v.OWL.SymmetricProperty, v.OWL.AsymmetricProperty,
                   v.OWL.ReflexiveProperty, v.OWL.IrreflexiveProperty}
 owners = {}
 for path in sorted((ROOT/'ontology').glob('*.ttl')):
  graph = v.parse(path)
  declared = {s for s, kind in graph.subject_objects(v.RDF.type)
              if isinstance(s, v.URIRef) and kind in property_types}
  for subject in declared:
   owners.setdefault(subject, []).append(path.name)
 duplicates = {str(subject): files for subject, files in owners.items() if len(files) > 1}
 assert not duplicates, duplicates


def test_review_fibre_component_keeps_core_material_specialization():
 graph = v.parse(ROOT/'ontology/textile-core.ttl')
 assert (v.URIRef('https://w3id.org/eudpp/textile-core#FibreCompositionComponent'),
         v.RDFS.subClassOf,
         v.URIRef('https://w3id.org/eudpp#MaterialOfComposition')) in graph


def test_review_object_properties_do_not_use_subclass_axioms():
 graph = v.ontology_graph(ROOT)
 defects = [(str(subject), str(parent))
            for subject in graph.subjects(v.RDF.type, v.OWL.ObjectProperty)
            for parent in graph.objects(subject, v.RDFS.subClassOf)]
 assert not defects, defects
