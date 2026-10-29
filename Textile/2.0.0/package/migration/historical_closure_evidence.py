"""Independent catalogue-only historical traversal and per-file hash evidence."""
import hashlib
import json
from xml.etree import ElementTree as ET
from rdflib import Graph, URIRef, RDF, OWL
from migration import implement_core as m


def record():
    cat={x.attrib['name']:x.attrib['uri'] for x in ET.parse(m.HISTORY/'catalog-v001.xml').getroot()}
    inventory=json.loads((m.ROOT/'migration/historical/inventory.json').read_text('utf8'))
    records={}
    for entry in ('textile-ontology/1.1.2','textile-soc/1.1.2','textile-soc-mireot/1.1.2','textile-soc-mireot/1.1.3'):
        queue=['https://w3id.org/eudpp/'+entry];files={};model=Graph()
        while queue:
            iri=queue.pop(0)
            assert iri in cat,iri
            rel=cat[iri]
            if rel in files:continue
            path=(m.HISTORY/rel).resolve()
            assert path.is_relative_to(m.HISTORY.resolve())
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest==inventory['files'][rel]
            graph=m.parse(path);model+=graph
            assert not any(str(v).endswith('/2.0.0') for v in graph.objects(None,OWL.versionIRI))
            files[rel]=digest
            queue.extend(str(i) for i in graph.objects(None,OWL.imports))
        assert not any('con-textile' in p for p in files)
        declared={str(s) for s in model.subjects(RDF.type,None) if isinstance(s,URIRef) and str(s).startswith(str(m.OLD))}
        assert len(declared)==96
        records[entry]={'file_count':len(files),'declared_legacy_soc_resources':len(declared),'contains_con_mireot':False,'contains_2_0_0_graph':False,'files_sha256':dict(sorted(files.items()))}
    result={'historical_baseline':inventory['baseline_commit'] if 'baseline_commit' in inventory else '1ca2aa89241785dedeab430247bc9947daf69881',
            'catalogue':'migration/historical/1.1.2/catalog-v001.xml','archive_sha256':inventory['archive_sha256'],'closures':records}
    (m.ROOT/'migration/historical-closure-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print({key:row['file_count'] for key,row in records.items()})


if __name__=='__main__':record()
