"""Apply the documented expression migration to validation contracts."""
import json
import zipfile
from rdflib import BNode, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SH, XSD, OWL
from rdflib.collection import Collection
from migration.implement_core import ROOT, C, T, E, parse, save

S=Namespace('https://w3id.org/eudpp/textile-shacl#')
from rdflib import Graph
with zipfile.ZipFile(next((ROOT/'migration/historical').glob('*.zip'))) as archive:
    g=Graph().parse(data=archive.read('shacl/textile-quantitative-shapes.ttl'),format='turtle')
# The original scalar rule remains for ordinary quantities. Only the three
# explicitly authorised threshold roles extend the common value pattern.
for constraint in g.objects(S.NoQuantitativeValueSubclassShape,SH.sparql):
    g.set((constraint,SH.message,Literal('Only the three approved Textile threshold roles may specialise QuantitativeValue.',lang='en')))
    for query in list(g.objects(constraint,SH.select)):
        g.set((constraint,SH.select,Literal(str(query).replace('FILTER (?subclass != $this)',
          'FILTER (?subclass != $this && ?subclass NOT IN (<'+str(T.ExactThresholdValue)+'>, <'+str(T.MaximumThresholdValue)+'>, <'+str(T.RangeThresholdValue)+'>))'))))
for prop in g.objects(S.QuantitativeValueShape,SH.property):
    if g.value(prop,SH.path)==C.numericValue:
        g.remove((prop,SH.minCount,None))
        g.set((prop,SH.message,Literal('A scalar quantitative value must have at most one decimal numeric value.',lang='en')))
branches=[]
for cls in (T.MaximumThresholdValue,T.RangeThresholdValue):
    branch=BNode();g.add((branch,SH['class'],cls));branches.append(branch)
branch=BNode();p=BNode();g.add((branch,SH.property,p));g.add((p,SH.path,C.numericValue));g.add((p,SH.minCount,Literal(1)));branches.append(branch)
head=BNode();Collection(g,head,branches);g.add((S.QuantitativeValueShape,SH['or'],head))
for iri in list(g.subjects(RDF.type,OWL.Ontology)):
    g.set((iri,OWL.versionIRI,URIRef(str(iri)+'/2.0.0')))
save(g,ROOT/'shacl/textile-quantitative-shapes.ttl')

path=ROOT/'tests/abox_corpus/expectations/shacl-expectations.json'
doc=json.loads(path.read_text('utf8'))
for scenario in doc['scenarios']:
    if 'mireot/con-textile-mireot.ttl' not in scenario['dependency_graphs']:scenario['dependency_graphs'].append('mireot/con-textile-mireot.ttl')
    if scenario['scenario_id']=='I08':
        # Same node and original reversed-range defect, now a Textile threshold
        # expression. It must not be converted to a CORE concentration range.
        row=scenario['expected_results'][0]
        row['source_shape']=str(S.RangeThresholdValueShape)
        import hashlib
        row['source_constraint_message_sha256']=hashlib.sha256(b'The lower threshold bound must not exceed the upper bound.').hexdigest()
path.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf8',newline='\n')
path=ROOT/'tests/abox_corpus/expectations/reasoning-expectations.json'
doc=json.loads(path.read_text('utf8'))
for scenario in doc['scenarios']:
    if 'dependency_graphs' in scenario and 'mireot/con-textile-mireot.ttl' not in scenario['dependency_graphs']:scenario['dependency_graphs'].append('mireot/con-textile-mireot.ttl')
path.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf8',newline='\n')
print('Common quantitative constraints extended only for approved threshold roles; I08 retains its reversed threshold defect.')
