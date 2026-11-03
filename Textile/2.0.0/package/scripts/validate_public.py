"""Standalone offline checks for the Textile community candidate.

This module also defines the deterministic projection of public RDF annotations
into the three traceability tables. It never reads a workbook or Git history.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, io, json, re, sys
from pathlib import Path
from xml.etree import ElementTree as ET
from rdflib import Graph, URIRef, BNode, RDF, RDFS, OWL, SKOS, Namespace
from rdflib.namespace import SH

ROOT = Path(__file__).resolve().parents[1]
TXT = Namespace('https://w3id.org/eudpp/textile-connector#')
DCT = Namespace('http://purl.org/dc/terms/')
CATEGORIES = ('directExtraction','adaptedDefinition','adaptedRelation','modellingAbstraction','projectDecision','externalReuse')
RESOURCE_FIELDS = 'resource_iri resource_qname resource_type label module provenance_category evidence_count has_jrc_evidence modelling_decision_locator traceability_status notes'.split()
EVIDENCE_FIELDS = 'evidence_id resource_iri source_document_id source_section source_page source_locator evidence_kind locator_status verification_basis notes'.split()
SOURCE_FIELDS = 'source_document_id title publisher date scope source_type public_reference notes'.split()
J25 = 'https://susproc.jrc.ec.europa.eu/product-bureau/sites/default/files/2025-12/Textile-Prep-Study_3rd-Milestone_20251212.pdf'
J26 = 'https://susproc.jrc.ec.europa.eu/product-bureau/sites/default/files/2026-05/Textiles_DPP_20260513.pdf'
PROJECT = 'https://w3id.org/eudpp/textile-ontology'
LEGAL = 'http://data.europa.eu/eli/reg/2024/1781/oj'
MAT = 'https://w3id.org/eudpp/textile-mat-mireot'
EVENT = 'https://w3id.org/eudpp/textile-event-mireot'
LEGACY_SOC = 'https://w3id.org/eudpp/soc'
SOURCE_META = {
 LEGACY_SOC: ('HISTORICAL-SOC-0.1.2','EU DPP Core Ontology - Substances of Concern Module, Version 0.1.2 DRAFT','Elio Hbeich','2026-04-17','Preserved historical definitions adapted into Textile extensions','EXTERNAL_ONTOLOGY','CC BY 4.0. Exact snapshot: migration/historical/1.1.2/dependencies/soc.ttl. Source text comparison does not verify underlying legal or JRC references.'),
 J25: ('JRC-TEXTILE-2025-12','Textile Preparatory Study - 3rd Milestone','European Commission Joint Research Centre','2025-12-12','Broad textile technical and preparatory evidence','JRC',''),
 J26: ('JRC-DPP-2026-05','Textiles Digital Product Passport study','European Commission Joint Research Centre','2026-05-13','Narrower proposed apparel-DPP information content','JRC','Does not supersede the broad technical scope of the December 2025 study.'),
 LEGAL: ('EU-2024-1781','Regulation (EU) 2024/1781 (ESPR)','European Union','2024-06-28','Recorded regulatory references','LEGISLATION','Citation does not establish that every ontology field is legally mandatory.'),
 MAT: ('TEXTILE-MAT-MIREOT','Textile MAT MIREOT referencing EU DPP MAT 1.1.0','','','Bounded external material semantics','EXTERNAL_ONTOLOGY','Local graph: mireot/mat-textile-mireot.ttl; upstream: https://w3id.org/eudpp/MAT'),
 EVENT: ('TEXTILE-EVENT-MIREOT','Textile EVENT MIREOT referencing EU DPP EVENT 1.0.0','','','Bounded external product-event semantics','EXTERNAL_ONTOLOGY','Local graph: mireot/event-textile-mireot.ttl; upstream: https://w3id.org/eudpp/EVENT'),
}
# Public hygiene checks cover filesystem references, not workflow vocabulary.
LOCAL_PATH = re.compile(
 r'(?<![\w])(?:[A-Za-z]:[\\/]|file:/+|~[\\/])'
 r'|(?<![\w:/])/(?:home|Users|tmp|private|var/tmp)/'
 r'|\\\\[A-Za-z0-9_.-]+\\'
 r'|(?:\.\.[\\/]){2,}'
 r'|(?<![\w.])\.[A-Za-z_][\w.-]*[\\/]', re.I)
PRIVATE_PATH = re.compile(
 LOCAL_PATH.pattern + r'|(?:^|[\\/])(?:\.\.|private|internal)[\\/]', re.I)

# The current package owns these areas. Other repository content is out of scope.
PACKAGE_ROOT_FILES = ('CHANGELOG.md','LICENSE.md','PUBLICATION_MANIFEST.txt','README.md','SHA256SUMS','VERSION','catalog-v001.xml','requirements-validation.txt')
PACKAGE_AREAS = ('ontology','mireot','dependencies','shacl','examples','docs','diagrams','scripts','tests','traceability','LICENSES','migration','widoco')
# Owner-reviewed working plan remains untracked and outside the release contract.
NON_RELEASE_PLANNING_FILES = ('migration/PUBLICATION_PLAN_2.0.0.md',)
PRESERVED_REFERENCE_MATERIAL = ('ontology/graphwise-ontology/README.md','ontology/graphwise-ontology/SHACL textile product data.ttl','ontology/graphwise-ontology/ontology.ttl')
RESOLUTION_FIELDS = 'previous_evidence_id resource_iri source_document_id source_section source_page source_locator verification_basis notes'.split()
CURRENT_MODULES = ('textile-assessment.ttl', 'textile-associated-materials.ttl', 'textile-connector.ttl', 'textile-context.ttl', 'textile-core.ttl', 'textile-durability.ttl', 'textile-indicator.ttl', 'textile-ontology.ttl', 'textile-process.ttl', 'textile-recyclability.ttl', 'textile-repairability.ttl', 'textile-soc.ttl', 'textile-structure.ttl')

def package_files(root):
 paths=set(PACKAGE_ROOT_FILES)

 for area in PACKAGE_AREAS:
  for p in (root/area).rglob('*'):
   rel=p.relative_to(root).as_posix()
   if rel in NON_RELEASE_PLANNING_FILES:
    continue

   if not p.is_file():
    continue

   if rel.startswith('ontology/graphwise-ontology/'):
    continue
   if rel.startswith('migration/historical/1.1.2/ontology/graphwise-ontology/'):
    continue

   if '__pycache__' in p.parts or p.suffix == '.pyc':
    continue

   paths.add(rel)

 return sorted(paths)

def manifest_sections(root):
 sections={};section=None
 for line in (root/'PUBLICATION_MANIFEST.txt').read_text('utf8').splitlines():
  if not line or line.startswith('#'):continue
  if line.startswith('[') and line.endswith(']'):
   section=line[1:-1];require(section not in sections,'Duplicate manifest section');sections[section]=[]
  else:
   require(section is not None,'Missing manifest section')
   require(not Path(line).is_absolute() and '..' not in Path(line).parts and '\\' not in line,'Unsafe manifest path')
   sections[section].append(line)
 require(set(sections)=={'CURRENT_PACKAGE','PRESERVED_REFERENCE_MATERIAL'},'Manifest section mismatch')
 require(sections['CURRENT_PACKAGE']==package_files(root),'Publication manifest does not match current package files')
 require(sections['PRESERVED_REFERENCE_MATERIAL']==list(PRESERVED_REFERENCE_MATERIAL),'Preserved reference inventory mismatch')
 require(all((root/p).is_file() for p in PRESERVED_REFERENCE_MATERIAL),'Missing preserved reference material')
 require(not set(sections['CURRENT_PACKAGE']) & set(PRESERVED_REFERENCE_MATERIAL),'Reference material entered package contract')
 return sections

def apply_locator_resolutions(evidence,root):
 resolutions=read_csv(root/'traceability/evidence-locator-resolutions.csv',RESOLUTION_FIELDS)
 require(len(resolutions)==7,'Expected seven reviewed locator resolutions')
 by_id={e['evidence_id']:e for e in evidence};seen=set()
 for resolution in resolutions:
  old=resolution['previous_evidence_id'];require(old not in seen and old in by_id,'Unknown or duplicate resolution');seen.add(old)
  e=by_id[old]
  require(not e['source_locator'] and e['locator_status']=='UNRESOLVED','Resolution must target a missing locator')
  require(all(e[k]==resolution[k] for k in ('resource_iri','source_document_id')),'Resolution changes source relationship')
  require(resolution['source_locator'] and resolution['verification_basis'] and resolution['notes'],'Incomplete locator resolution')
  for k in ('source_section','source_page','source_locator','verification_basis','notes'):e[k]=resolution[k]
  e['locator_status']='PRESENT_NOT_REVERIFIED'
  e['evidence_id']=evidence_id(e)
 return evidence

def current_import_closure(root,cat):
 expected={'ontology/'+n for n in CURRENT_MODULES}|{p.relative_to(root).as_posix() for p in (root/'mireot').glob('*.ttl')}
 pending=['ontology/textile-ontology.ttl'];seen=set()
 while pending:
  rel=pending.pop()
  require(rel in expected,'Import outside approved current closure: '+rel)
  if rel in seen:continue
  seen.add(rel)
  for uri in parse(root/rel).objects(None,OWL.imports):
   require(str(uri) in cat,'Unmapped current import: '+str(uri));pending.append(cat[str(uri)])
 require(seen==expected,'Current import closure differs from the approved module/MIREOT set')
 return seen

def catalogue_import_closure(catalogue, entry_iri):
 """Resolve every import with one explicitly selected offline catalogue.

 Never fall back to the active catalogue or the network for missing entries.
 """
 base=catalogue.parent.resolve()
 cat={x.attrib['name']:x.attrib['uri'] for x in ET.parse(catalogue).getroot()}
 pending=[str(entry_iri)];seen=set()
 while pending:
  iri=pending.pop()
  require(iri in cat,'Unmapped import in selected catalogue: '+iri)
  path=(base/cat[iri]).resolve()
  require(path.is_relative_to(base),'Catalogue target escapes selected package')
  if path in seen:continue
  require(path.is_file(),'Missing selected catalogue target: '+cat[iri])
  seen.add(path)
  pending.extend(map(str,parse(path).objects(None,OWL.imports)))
 return seen

def require(condition, message):
 if not condition: raise ValueError(message)

def parse(path):
 return Graph().parse(path,format='xml' if path.suffix=='.owl' else 'turtle')

def ontology_graph(root):
 g=Graph()
 for name in CURRENT_MODULES: g.parse(root/'ontology'/name,format='turtle')
 return g

def universe(g):
 return sorted(s for s in set(g.subjects()) if isinstance(s,URIRef) and str(s).startswith('https://w3id.org/eudpp/textile-') and (s,RDF.type,OWL.Ontology) not in g)

def one(g,s,p):
 vals=sorted(set(map(str,g.objects(s,p))))
 require(len(vals)==1,f'Expected one value: {s} {p}')
 return vals[0]

def evidence_id(row):
 fields=[row[k] for k in ('resource_iri','source_document_id','source_locator','source_section','source_page')]
 canonical=json.dumps(fields,ensure_ascii=False,separators=(',',':')).encode('utf-8')
 return 'EVID-'+hashlib.sha256(canonical).hexdigest()[:16]

def identify(text):
 if text.startswith('Historical SOC 0.1.2'):return LEGACY_SOC
 if re.search(r'JRC DPP Study',text,re.I): return J26
 if re.search(r'JRC',text,re.I): return J25
 if re.search(r'ESPR|Regulation \(EU\) 2024/1781',text,re.I): return LEGAL
 if re.search(r'EU DPP MAT',text,re.I): return MAT
 if re.search(r'EU DPP EVENT',text,re.I): return EVENT
 return None

def scalar_parts(locator):
 sections=re.findall(r'\b(?:Section|Annex)\s+(\d+(?:\.\d+)*)',locator,re.I)
 pages=re.findall(r'\b(?:printed\s+)?pages?\s+(\d+(?:\s*[-?]\s*\d+)?(?:\s*,\s*\d+)*)',locator,re.I)
 # A compound locator retains its text; no independent columns imply a pairing.
 compound=';' in locator or len(sections)>1 or len(pages)>1 or any(',' in p for p in pages)
 return ('' if compound or len(sections)!=1 else sections[0], '' if compound or len(pages)!=1 else pages[0],compound)

def split_locations(raw, external):
 """Split only at explicit documentary boundaries. Never assign by row order."""
 chunks=re.split(r';\s*(?=(?:JRC\b|ESPR\b|Regulation \(EU\)|EU DPP MAT))',raw)
 assigned=collections.defaultdict(list); unassigned=[]
 for chunk in chunks:
  target=identify(chunk)
  if target in external: assigned[target].append(chunk)
  elif target is None and len(external)==1: assigned[external[0]].append(chunk)
  else: unassigned.append(chunk)
 # Pure single-document compound strings are retained byte-for-byte.
 if len(external)==1 and not unassigned and len(chunks)==1: assigned[external[0]]=[raw]
 return assigned, unassigned

def derive(g, root=ROOT):
 rows=[];evidence=[];used=set();multiple_sources=0
 for s in universe(g):
  iri=str(s);category=one(g,s,TXT.sourceType).split('#')[-1]
  require(category in CATEGORIES,'Unknown provenance category')
  module=one(g,s,RDFS.isDefinedBy).rsplit('/',1)[-1]
  raw=one(g,s,TXT.sourceLocator)
  sources=sorted(set(map(str,g.objects(s,DCT.source))))
  multiple_sources += len(sources)>1
  external=[x for x in sources if x!=PROJECT]
  require(all(x in SOURCE_META for x in external),'Unregistered source')
  adr=raw if re.fullmatch(r'docs/decisions/TXT-DEC-\d{3}\.md',raw) else ''
  assigned,unassigned=split_locations(raw,external) if external else ({},[])
  linked=[];partial=False
  for source in external:
   sid=SOURCE_META[source][0];used.add(source)
   locations=assigned.get(source,[])
   if not locations: locations=[''];partial=True
   for locator in locations:
    section,page,compound=scalar_parts(locator)
    if compound: partial=True
    # Existence/structural checks never upgrade source interpretation to VERIFIED.
    status='PRESENT_NOT_REVERIFIED' if locator else 'UNRESOLVED'
    note='COMPOUND_CITATION_PRESERVED' if compound else ''
    if not locator: note='Source is explicitly identified in the ontology; no separately attributable source locator is recorded.'
    er=dict(zip(EVIDENCE_FIELDS,['',iri,sid,section,page,locator,
      'EXTERNAL_REUSE_SOURCE' if category=='externalReuse' else ('SUPPORTING_SOURCE' if category in ('modellingAbstraction','projectDecision') else 'SOURCE_CITATION'),
      status,'not_reverified_for_publication',note]))
    er['evidence_id']=evidence_id(er)
    if not any(x['evidence_id']==er['evidence_id'] for x in linked):linked.append(er)
  notes=[]
  if unassigned:
   partial=True;notes.append('Additional compound or modelling context remains in the ontology sourceLocator annotation; it has not been reassigned to another document.')
  if not external:
   if adr: state='NO_EXTERNAL_SOURCE_REQUIRED'
   elif raw.startswith('CIRPASS Textile Ontology') and 'JRC' not in raw: state='NO_EXTERNAL_SOURCE_REQUIRED'
   else: state='PARTIAL';notes.append('Historical modelling or domain-motivation reference remains in the ontology; no independently identified external source relationship is inferred.')
  else: state='PARTIAL' if partial else 'COMPLETE'
  if PROJECT in sources and external:notes.append('Project modelling rationale is also identified in the ontology; it is not counted as external source evidence.')
  # Specific semantic types precede general NamedIndividual; retain genuine punning.
  kinds=[]
  for t,name in [(OWL.Class,'Class'),(OWL.ObjectProperty,'ObjectProperty'),(OWL.DatatypeProperty,'DatatypeProperty'),(OWL.AnnotationProperty,'AnnotationProperty'),(SKOS.ConceptScheme,'ConceptScheme'),(SKOS.Concept,'Concept')]:
   if (s,RDF.type,t) in g:kinds.append(name)
  if not kinds and (s,RDF.type,OWL.NamedIndividual) in g:kinds=['NamedIndividual']
  if not kinds:kinds=['SemanticResource']
  labels=sorted(g.objects(s,RDFS.label),key=lambda x:(getattr(x,'language',None)!='en',str(x)))
  if not labels:labels=sorted(g.objects(s,SKOS.prefLabel),key=str)
  qname=iri
  for prefix,ns in sorted(g.namespaces()):
   if str(ns).startswith('https://w3id.org/eudpp/textile-') and iri.startswith(str(ns)):
    qname=prefix+':'+iri[len(str(ns)):];break
  rows.append(dict(zip(RESOURCE_FIELDS,[iri,qname,' | '.join(kinds),str(labels[0]) if labels else '',module,category,str(len(linked)),str(any(x['source_document_id'].startswith('JRC-') for x in linked)).upper(),adr,state,' '.join(notes)])))
  evidence.extend(linked)
 registry=[]
 for uri in sorted(used,key=lambda x:SOURCE_META[x][0]):
  sid,title,publisher,date,scope,typ,note=SOURCE_META[uri]
  registry.append(dict(zip(SOURCE_FIELDS,[sid,title,publisher,date,scope,typ,uri,note])))
 apply_locator_resolutions(evidence,root)
 evidence.sort(key=lambda x:(x['resource_iri'],x['source_document_id'],x['source_locator'],x['evidence_id']))
 require(len({x['evidence_id'] for x in evidence})==len(evidence),'Truncated evidence ID collision')
 return rows,evidence,registry,multiple_sources

def csv_bytes(fields,rows):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows);return out.getvalue().encode('utf-8')

def read_csv(path,fields):
 raw=path.read_bytes();text=raw.decode('utf-8');require(not text.startswith('\ufeff'),'Unexpected UTF-8 BOM')
 rows=list(csv.reader(io.StringIO(text,newline=''),strict=True))
 require(rows and rows[0]==fields,'CSV header mismatch: '+path.name)
 require(all(len(r)==len(fields) for r in rows),'CSV row width mismatch')
 return [dict(zip(fields,r)) for r in rows[1:]]

def check_recorded_ranges(locator):
 # Lexical numeric order only, never documentary page/section resolution.
 for match in re.finditer(r"\b(?:lines?|pages?)\s+(\d+)\s*[-?]\s*(\d+)",locator,re.I):
  require(int(match.group(1))<=int(match.group(2)), 'Reversed recorded range')

def validate_links(resources,evidence,sources):
 for rows,key in [(resources,'resource_iri'),(evidence,'evidence_id'),(sources,'source_document_id')]:
  require(all(r[key] for r in rows),'Empty identifier');require(len({r[key] for r in rows})==len(rows),'Duplicate identifier')
 ri={r['resource_iri']:r for r in resources};si={r['source_document_id']:r for r in sources};counts=collections.Counter()
 for e in evidence:
  require(e['resource_iri'] in ri,'Orphan resource reference');require(e['source_document_id'] in si,'Orphan source reference')
  require(evidence_id(e)==e['evidence_id'],'Evidence ID mismatch');counts[e['resource_iri']]+=1
  require(not PRIVATE_PATH.search(e['source_locator']),'Private evidence path')
  check_recorded_ranges(e['source_locator'])
 for r in resources:
  linked=[e for e in evidence if e['resource_iri']==r['resource_iri']]
  require(int(r['evidence_count'])==counts[r['resource_iri']],'Evidence count mismatch')
  require(r['has_jrc_evidence']==str(any(si[e['source_document_id']]['source_type']=='JRC' for e in linked)).upper(),'JRC flag mismatch')
 require(set(si)=={e['source_document_id'] for e in evidence},'Unused source registry entry')

def summary(resources,evidence,sources):
 dist=collections.Counter(int(r['evidence_count']) for r in resources)
 return dict(resource_count=len(resources),evidence_rows=len(evidence),source_documents=len(sources),
  categories=dict(sorted(collections.Counter(r['provenance_category'] for r in resources).items())),
  modules=dict(sorted(collections.Counter(r['module'] for r in resources).items())),
  locator_statuses=dict(sorted(collections.Counter(e['locator_status'] for e in evidence).items())),
  traceability_statuses=dict(sorted(collections.Counter(r['traceability_status'] for r in resources).items())),
  evidence_by_source=dict(sorted(collections.Counter(e['source_document_id'] for e in evidence).items())),
  zero_evidence=dist[0],one_evidence=dist[1],multiple_evidence=sum(v for k,v in dist.items() if k>1),max_evidence=max(dist,default=0),
  evidence_count_distribution=dict(sorted(dist.items())),compound_citations=sum('COMPOUND_CITATION_PRESERVED' in e['notes'] for e in evidence),
  resources_with_jrc_evidence=sum(r['has_jrc_evidence']=='TRUE' for r in resources))

def structural_checks(root):
 try:
  from scripts.check_widoco_links import audit_tree
 except ImportError:
  from check_widoco_links import audit_tree
 links=audit_tree(root/'docs/widoco')
 require(not links['errors'],'Broken WIDOCO references: '+repr(links['errors']))
 g=ontology_graph(root);r,e,s,m=derive(g,root)
 for file,fields,expected in [('textile-resource-traceability.csv',RESOURCE_FIELDS,r),('textile-resource-evidence.csv',EVIDENCE_FIELDS,e),('source-documents.csv',SOURCE_FIELDS,s)]:
  actual=read_csv(root/'traceability'/file,fields);require(actual==expected,'Traceability differs from RDF-derived projection: '+file)
 validate_links(r,e,s)
 adr=set(x['modelling_decision_locator'] for x in r if x['modelling_decision_locator'])
 for a in adr:require((root/a).is_file(),'Missing public modelling rationale: '+a)
 cat={x.attrib['name']:x.attrib['uri'] for x in ET.parse(root/'catalog-v001.xml').getroot()}
 for rel in cat.values():
  require((root/rel).resolve().is_relative_to(root.resolve()),'Catalogue target outside repository')
  require(not rel.startswith('ontology/graphwise-ontology/'),'Catalogue references Graphwise material')
  require((root/rel).is_file(),'Missing catalogue target: '+rel)
 require(sorted(p.name for p in (root/'ontology').glob('*.ttl'))==list(CURRENT_MODULES),'Unexpected current ontology modules')
 closure=current_import_closure(root,cat)
 rdf_paths=[root/rel for rel in package_files(root) if Path(rel).suffix in ('.ttl','.owl')]
 historical=root/'migration/historical/1.1.2'
 hcat={x.attrib['name']:x.attrib['uri'] for x in ET.parse(historical/'catalog-v001.xml').getroot()}
 require(not any(k.endswith(('/1.1.2','/1.1.3')) or v.startswith('migration/historical/') for k,v in cat.items()),'Historical identities require the historical catalogue')
 for p in rdf_paths:
  gg=parse(p)
  selected,base=(hcat,historical) if p.is_relative_to(historical) else (cat,root)
  for uri in gg.objects(None,OWL.imports):
   require(str(uri) in selected and (base/selected[str(uri)]).is_file(),'Unmapped ontology import: '+str(uri))
  for uri in gg.objects(None,OWL.versionIRI):
   # The unchanged SI MIREOT retains its historical identity and exact bytes.
   # All current Textile modules have distinct 2.0.0 version identities.
   available=hcat if str(uri).endswith(('/1.1.2','/1.1.3')) else selected
   require(str(uri) in available,'Unmapped declared ontology version: '+str(uri))
  if p.parent==root/'ontology':
   ontology=URIRef('https://w3id.org/eudpp/'+p.stem)
   require(set(gg.subjects(RDF.type,OWL.Ontology))=={ontology},'Unexpected Textile ontology identity: '+p.name)
   require(set(gg.objects(ontology,OWL.versionIRI))=={URIRef(str(ontology)+'/2.0.0')},'Current Textile version must be 2.0.0: '+p.name)
 for rel in package_files(root):
  p=root/rel
  if p.is_file() and p.suffix in ('.md','.csv','.ttl','.owl','.xml','.json','.txt'):
   # A bare cache-directory name in the supplied reconciliation is public
   # tooling vocabulary; absolute/user/private paths still match independently.
   public_text=re.sub(r'(?<![\w./])\.pytest_cache[\\/]', 'pytest_cache/', p.read_text('utf-8'))
   require(not LOCAL_PATH.search(public_text), 'Content scan match: '+rel)
 manifest=manifest_sections(root)['CURRENT_PACKAGE']
 lines=(root/'SHA256SUMS').read_text('utf8').splitlines();want=[p for p in manifest if p!='SHA256SUMS']
 require(lines==[hashlib.sha256((root/p).read_bytes()).hexdigest()+'  '+p for p in want],'Checksum mismatch')
 report=summary(r,e,s);report.update(current_import_closure_files=len(closure),package_files=len(manifest),preserved_reference_files=len(PRESERVED_REFERENCE_MATERIAL),parsed_rdf_files=len(rdf_paths),public_adrs=len(adr),multiple_source_annotations=m,structural_checks='passed')
 report['widoco_links']={k:links[k] for k in ('html_files','assembled_pages','ajax_sections','reference_count','statuses')}
 return report

def match_shacl_results(results, shapes, scenario):
 """Match results one-to-one, resolving anonymous property shapes by ownership.

 Blank-node identifiers are serialization-local. A contract can name the owning
 node shape; the actual property shape must belong to it and have the reported
 path. Named source shapes are matched directly, without owner substitution.
 """
 actual=[]
 for result in set(results.subjects(RDF.type,SH.ValidationResult)):
  source=results.value(result,SH.sourceShape)
  path=results.value(result,SH.resultPath)
  owners={source}
  if isinstance(source,BNode):
   require((source,SH.path,path) in shapes,'Anonymous source shape has unexpected result path')
   owners=set(shapes.subjects(SH.property,source))
   require(owners,'Anonymous source shape has no owning node shape')
  actual.append(dict(
   focus_node=results.value(result,SH.focusNode),
   source_shapes=owners,
   source_constraint=results.value(result,SH.sourceConstraint),
   constraint_component=results.value(result,SH.sourceConstraintComponent),
   result_path=path,
   severity=results.value(result,SH.resultSeverity),
   message_hashes={hashlib.sha256(str(m).encode('utf8')).hexdigest()
                   for m in results.objects(result,SH.resultMessage)}))
 require(scenario['result_count_min']<=len(actual)<=scenario['result_count_max'],
         'Unexpected SHACL result count: '+scenario['scenario_id']+' '+repr(actual))
 unmatched=list(actual)
 for expected in scenario['expected_results']:
  def matches(row):
   for field in ('focus_node','constraint_component','result_path','severity'):
    value=row[field]
    if (None if value is None else str(value))!=expected[field]:return False
   if URIRef(expected['source_shape']) not in row['source_shapes']:return False
   if expected.get('source_constraint') is not None and str(row['source_constraint'])!=expected['source_constraint']:return False
   checksum=expected.get('source_constraint_message_sha256')
   return checksum is None or checksum in row['message_hashes']
  found=next((i for i,row in enumerate(unmatched) if matches(row)),None)
  require(found is not None,'Missing expected SHACL result: '+scenario['scenario_id']+' '+json.dumps(expected,sort_keys=True))
  unmatched.pop(found)
 require(scenario['allowed_additional_results'] or not unmatched,
         'Unexpected additional SHACL results: '+scenario['scenario_id'])


def reject_legacy_soc(graph, label):
 # Attribution to preserved source resources is metadata, never a semantic
 # bridge or a runtime import of the legacy ontology.
 attribution={DCT.source,URIRef('http://www.w3.org/ns/prov#wasDerivedFrom')}
 offenders=sorted({str(term) for triple in graph if triple[1] not in attribution for term in triple
                   if isinstance(term,URIRef) and (str(term).startswith('https://w3id.org/eudpp/soc#') or str(term)=='https://w3id.org/eudpp/soc')})
 require(not offenders,'Legacy SOC identity in '+label+': '+', '.join(offenders))


def runtime_checks(root, complete_report=False, progress=None):
 from pyshacl import validate
 from owlrl import DeductiveClosure,RDFS_Semantics,OWLRL_Semantics
 emit=progress or (lambda message: None)
 ont=Graph();shapes=Graph()
 ont += ontology_graph(root)
 for p in sorted((root/'mireot').glob('*.ttl')):ont += parse(p)
 for p in sorted((root/'shacl').glob('*.ttl')):shapes+=parse(p)
 if complete_report:shapes+=parse(root/'shacl/profiles/textile-soc-complete-report.ttl')
 reject_legacy_soc(ont,'active ontology closure');reject_legacy_soc(shapes,'active SHACL profiles')
 examples=0
 for p in sorted((root/'examples').glob('*.ttl')):
  emit('Example: '+p.name)
  reject_legacy_soc(parse(p),p.name)
  ok,_,_=validate(ont+parse(p),shacl_graph=shapes,inference='rdfs',advanced=True,do_owl_imports=False)
  require(ok,'Nonconformant public example: '+p.name);examples+=1
 sh=json.loads((root/'tests/abox_corpus/expectations/shacl-expectations.json').read_text('utf8'))
 for scenario in sh['scenarios']:
  emit('SHACL: '+scenario['scenario_id'])
  reject_legacy_soc(parse(root/scenario['fixture_path']),scenario['scenario_id'])
  ok,results,_=validate(ont+parse(root/scenario['fixture_path']),shacl_graph=shapes,inference='rdfs',advanced=True,do_owl_imports=False)
  require(bool(ok)==scenario['expected_conforms'],'Unexpected SHACL conformance: '+scenario['scenario_id'])
  match_shacl_results(results,shapes,scenario)
 rn=json.loads((root/'tests/abox_corpus/expectations/reasoning-expectations.json').read_text('utf8'))
 for scenario in rn['scenarios']:
  emit('Reasoning: '+scenario['scenario_id'])
  model=ont+parse(root/scenario['fixture_path'])
  DeductiveClosure(RDFS_Semantics if scenario['reasoning_profile']=='RDFS' else OWLRL_Semantics).expand(model)
  for t in scenario['required_named_triples']:require(tuple(map(URIRef,t)) in model,'Missing inferred triple: '+scenario['scenario_id'])
  for t in scenario['forbidden_named_triples']:require(tuple(map(URIRef,t)) not in model,'Forbidden inferred triple: '+scenario['scenario_id'])
  overlap=sum(len(set(model.subjects(RDF.type,URIRef(left))) & set(model.subjects(RDF.type,URIRef(right))))
              for left,right in scenario.get('disjoint_type_pairs_checked',[]))
  require(overlap==scenario.get('expected_disjoint_overlap_count',0),'Unexpected disjoint-type overlap: '+scenario['scenario_id'])
 # Discriminating inference control, using the recyclability profile alone.
 p=root/'examples/example-11-textile-recyclability-v1.1.2.ttl';shape=parse(root/'shacl/textile-recyclability-shapes.ttl')
 plain,_,_=validate(ont+parse(p),shacl_graph=shape,inference='none',advanced=True,do_owl_imports=False)
 require(not plain,'RDFS negative control unexpectedly conforms without inference')
 return dict(examples_conformant=examples,shacl_scenarios=len(sh['scenarios']),reasoning_scenarios=len(rn['scenarios']),rdfs_negative_control='passed')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--full',action='store_true');ap.add_argument('--complete-report',action='store_true',help='Also select the SoC concentration-completeness profile');args=ap.parse_args()
 result=structural_checks(ROOT)
 if args.full:result.update(runtime_checks(ROOT,complete_report=args.complete_report))
 print(json.dumps(result,indent=2));return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except (ValueError,OSError) as exc:print(str(exc),file=sys.stderr);raise SystemExit(1)
