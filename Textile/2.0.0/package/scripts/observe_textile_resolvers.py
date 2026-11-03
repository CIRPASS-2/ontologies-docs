"""Read-only resolver observations; never edits redirects or ontology sources."""
import concurrent.futures
import argparse
from datetime import datetime, timezone
import json
import hashlib
import sys
from pathlib import Path
import urllib.request
import urllib.error
from rdflib import Graph, RDF, OWL, URIRef
from rdflib.namespace import DCTERMS
from rdflib.compare import isomorphic
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))


def identities():
    rows=[]
    for area in ('ontology','mireot'):
        for path in sorted((ROOT/area).glob('*.ttl')):
            graph=Graph().parse(path)
            ontology=next(graph.subjects(RDF.type,OWL.Ontology))
            rows.append(dict(source=path.relative_to(ROOT).as_posix(),iri=str(ontology),
                             version_iri=str(graph.value(ontology,OWL.versionIRI))))
    return rows


def retained_versions():
    from migration.correct_version_identities import MODULES, project
    historical=ROOT/'migration/historical/1.1.2'
    active_catalog={x.attrib['name']:x.attrib['uri'] for x in ET.parse(ROOT/'catalog-v001.xml').getroot()}
    old_catalog={x.attrib['name']:x.attrib['uri'] for x in ET.parse(historical/'catalog-v001.xml').getroot()}
    rows=[]
    for row in identities():
        if row['source'] not in {'ontology/textile-'+module+'.ttl' for module in MODULES}:continue
        source=ROOT/row['source'];old=historical/row['source']
        current=Graph().parse(source);past=Graph().parse(old)
        current.remove((None,DCTERMS.creator,None));past.remove((None,DCTERMS.creator,None))
        ontology=URIRef(row['iri'])
        imports=sorted(map(str,current.objects(None,OWL.imports)))
        rows.append(dict(**row,current_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                         historical_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
                         historical_source=old.relative_to(ROOT).as_posix(),
                         isomorphic_excluding_only_creator=isomorphic(current,past),
                         isomorphic_excluding_creator_and_version_metadata=isomorphic(project(current,ontology),project(past,ontology)),
                         prior_version=str(current.value(ontology,OWL.priorVersion)),
                         imports=[dict(iri=uri,current=active_catalog[uri],
                                       historical=(historical/old_catalog[uri]).relative_to(ROOT).as_posix()) for uri in imports]))
    assert len(rows)==9
    (ROOT/'migration/retained-version-identities.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Corrected retained identities:',len(rows),'; non-metadata graphs equivalent:',sum(row['isomorphic_excluding_creator_and_version_metadata'] for row in rows))


def observe(pair):
    uri,accept=pair
    try:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):return None
        opener=urllib.request.build_opener(NoRedirect)
        try:
            response=opener.open(urllib.request.Request(uri,headers={'Accept':accept}),timeout=30)
        except urllib.error.HTTPError as response:
            return dict(iri=uri,accept=accept,status=response.code,
                        location=response.headers.get('Location'),content_type=response.headers.get('Content-Type'))
        with response:
            return dict(iri=uri,accept=accept,status=response.status,
                        location=response.headers.get('Location'),content_type=response.headers.get('Content-Type'))
    except (urllib.error.URLError,TimeoutError,OSError) as exc:
        return dict(iri=uri,accept=accept,error=type(exc).__name__)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retained-only',action='store_true',help='Only compare retained identities offline')
    args=parser.parse_args()
    retained_versions()
    if args.retained_only:raise SystemExit(0)
    rows=identities()
    iris={row[key] for row in rows for key in ('iri','version_iri')}
    iris.update('https://w3id.org/eudpp/'+name for name in ('ACTOR','MAT','EVENT','SOC','P_DPP','CON','soc'))
    queries=[(uri,accept) for uri in sorted(iris) for accept in ('text/html','text/turtle')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        observations=list(pool.map(observe,queries))
    report=dict(observed_utc=datetime.now(timezone.utc).isoformat(),method='GET, no redirect following',
                identities=rows,observations=observations)
    (ROOT/'migration/resolver-http-observations.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(identities=len(rows),requests=len(observations),
                         statuses=sorted({str(row.get('status',row.get('error'))) for row in observations}))))
