"""Validate byte-preserving Textile publication over HTTP and a real browser."""
import argparse,concurrent.futures,hashlib,json,re,subprocess,sys,tempfile,threading,time
from collections import Counter
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote,unquote,urljoin,urlsplit
from urllib.request import Request,urlopen
from rdflib import Graph,RDF,OWL
from rdflib.compare import isomorphic
import prepare as assembly

ROOT=assembly.ROOT
DEST=assembly.DEST
PACKAGE=DEST/'package'
PUBLICATION=DEST/'publication'
PREFIX='/ontologies-docs/'
MODULES=assembly.MODULES
SECTIONS=('abstract','introduction','nstable','overview','description','references','crossref')

class DOM(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=Counter();self.links=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if not value:continue
            if key in ('id','name'):self.ids[value]+=1
            if key in ('href','src'):self.links.append(dict(tag=tag,attribute=key,url=value))

class Handler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.ttl':'text/turtle','.owl':'application/rdf+xml','.nt':'application/n-triples','.jsonld':'application/ld+json','.mjs':'text/javascript'}
    def translate_path(self,path):
        path=unquote(urlsplit(path).path)
        if not path.startswith(PREFIX):return str(ROOT/'__not_served__')
        relative=path[len(PREFIX):]
        if relative.rstrip('/') not in self.case_paths:return str(ROOT/'__not_served__')
        if any(part in ('..','.git') for part in Path(relative).parts):return str(ROOT/'__not_served__')
        result=(ROOT/relative).resolve()
        return str(result) if result.is_relative_to(ROOT) else str(ROOT/'__not_served__')
    def list_directory(self,path):self.send_error(404,'Directory indexes are not published');return None
    def log_message(self,*args):pass

class Browser:
    def __init__(self,executable,tools):
        if tools:sys.path.insert(0,str(tools))
        import websocket
        self.websocket=websocket;self.counter=0
        self.profile=tempfile.TemporaryDirectory(prefix='textile-docs-cdp-',ignore_cleanup_errors=True)
        args=[str(executable),'--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-extensions','--disable-background-networking','--no-proxy-server','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1','--remote-debugging-port=0','--remote-allow-origins=http://localhost','--user-data-dir='+self.profile.name,'about:blank']
        self.process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        portfile=Path(self.profile.name)/'DevToolsActivePort';deadline=time.monotonic()+25
        while not portfile.exists() and time.monotonic()<deadline:time.sleep(.1)
        assert portfile.exists(),'Headless browser debugging endpoint unavailable'
        self.debug='http://127.0.0.1:'+portfile.read_text().splitlines()[0]
        with urlopen(self.debug+'/json/version') as response:self.version=json.load(response)
        self.control=self.websocket.create_connection(self.version['webSocketDebuggerUrl'],origin='http://localhost',timeout=15)
    def command(self,connection,method,params=None,events=None):
        self.counter+=1;identifier=self.counter
        connection.send(json.dumps(dict(id=identifier,method=method,params=params or {})))
        while True:
            message=json.loads(connection.recv())
            if message.get('id')==identifier:
                assert 'error' not in message,message
                return message.get('result',{})
            if events is not None and 'method' in message:events.append(message)
    def page(self,url,kind,annotations=()):
        with urlopen(Request(self.debug+'/json/new?about:blank',method='PUT')) as response:target=json.load(response)
        connection=self.websocket.create_connection(target['webSocketDebuggerUrl'],origin='http://localhost',timeout=15)
        events=[]
        try:
            for method in ('Page.enable','Runtime.enable','Network.enable','Log.enable'):self.command(connection,method,events=events)
            self.command(connection,'Page.navigate',dict(url=url),events)
            module=urlsplit(url).path.split('/Textile/2.0.0/',1)[1].split('/',1)[0]
            section_files={name:('ns' if name=='nstable' else name)+'-en.html' for name in SECTIONS}
            nonempty=[name for name,filename in section_files.items() if (DEST/module/'sections'/filename).stat().st_size]
            condition=('document.querySelectorAll("#graph .node").length > 0' if kind=='webvowl' else
                       'JSON.stringify('+json.dumps(nonempty)+'.map(id => (document.getElementById(id)?.textContent || "").trim().length))')
            deadline=time.monotonic()+35;ready=False
            while time.monotonic()<deadline:
                result=self.command(connection,'Runtime.evaluate',dict(expression=condition,returnByValue=True),events)
                value=result['result'].get('value')
                ready=bool(value) if kind=='webvowl' else bool(value and all(json.loads(value)))
                if ready:break
                time.sleep(.15)
            assert ready,'Browser did not render '+kind+': '+urlsplit(url).path
            time.sleep(.5)
            script='({html:document.documentElement.outerHTML,graphNodes:document.querySelectorAll("#graph .node").length,sections:Object.fromEntries('+json.dumps(list(SECTIONS))+'.map(id=>[id,(document.getElementById(id)?.textContent||"").trim().length])),location:location.href})'
            value=self.command(connection,'Runtime.evaluate',dict(expression=script,returnByValue=True),events)['result']['value']
            dom=DOM(value['html'])
            for name in annotations:assert dom.ids[name]==1,('Missing or duplicate annotation anchor',name,urlsplit(url).path)
            responses=[event['params'] for event in events if event['method']=='Network.responseReceived']
            local=[row for row in responses if row['response']['url'].startswith(url.split('/ontologies-docs/')[0]+'/')]
            ignored=[row for row in local if urlsplit(row['response']['url']).path=='/favicon.ico']
            bad=[row for row in local if row['response']['status']>=400 and row not in ignored]
            assert not bad,[(urlsplit(row['response']['url']).path,row['response']['status']) for row in bad]
            requests={event['params']['requestId']:event['params']['request']['url'] for event in events if event['method']=='Network.requestWillBeSent'}
            failed=[event['params'] for event in events if event['method']=='Network.loadingFailed' and requests.get(event['params']['requestId'],'').startswith(url.split('/ontologies-docs/')[0]+'/')]
            assert not failed,failed
            exceptions=[event['params']['exceptionDetails'].get('text') for event in events if event['method']=='Runtime.exceptionThrown']
            assert not exceptions,exceptions
            ajax=[urlsplit(row['response']['url']).path for row in local if '/sections/' in row['response']['url'] and row['response']['status']==200]
            if kind=='module':assert len(set(ajax))==7,ajax
            if kind=='webvowl':assert any(row['response']['url'].endswith('/webvowl/data/ontology.json') and row['response']['status']==200 for row in local)
            return dom,dict(path=urlsplit(url).path,expected_url=assembly.PUBLIC+urlsplit(url).path[len(PREFIX):],kind=kind,
                            annotation_anchors=list(annotations),ajax_sections=sorted(set(ajax)),empty_source_sections=[name for name in SECTIONS if name not in nonempty],graph_nodes=value['graphNodes'],
                            local_resource_responses=len(local),local_resource_errors=0,javascript_exceptions=exceptions,
                            ignored_implicit_favicon_responses=len(ignored),dom_sha256=hashlib.sha256(value['html'].encode()).hexdigest())
        finally:
            connection.close()
            with urlopen(self.debug+'/json/close/'+target['id']) as response:response.read()
    def close(self):
        try:self.command(self.control,'Browser.close')
        except self.websocket.WebSocketConnectionClosedException:pass
        finally:
            self.control.close()
            try:self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:self.process.terminate();self.process.wait(timeout=5)
            self.profile.cleanup()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edge',type=Path,default=Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'))
    parser.add_argument('--browser-tools',type=Path)
    args=parser.parse_args()
    inventory=json.loads((PUBLICATION/'transfer-inventory.json').read_text('utf8'))
    rows=inventory['files'];assert len(rows)==1290
    assert inventory['source_commit']==assembly.SHA and inventory['documentation_baseline']==assembly.BASE
    assert len({row['destination'] for row in rows})==len(rows)
    for row in rows:assert hashlib.sha256((ROOT/row['destination']).read_bytes()).hexdigest()==row['sha256'],row['destination']
    print('Committed-source copy hashes verified:',len(rows),flush=True)
    tracked=assembly.git('diff','--name-only',assembly.BASE).decode().splitlines()
    assert all(name in ('index.html','ontologies.html') or name.startswith('Textile/2.0.0/') for name in tracked),tracked
    original_files=assembly.git('ls-tree','-r','--name-only',assembly.BASE).decode().splitlines()
    for page in ('index.html','ontologies.html'):
        before=assembly.baseline(page);after=(ROOT/page).read_text('utf8')
        assert assembly.outside_regions(before,page)==assembly.outside_regions(after,page),'Non-Textile portal change: '+page
        old_links={row['url'] for row in DOM(before).links if row['url'].startswith('Textile/')}
        new_links={row['url'] for row in DOM(after).links if row['url'].startswith('Textile/')}
        assert old_links<=new_links,('Removed legacy links',page,old_links-new_links)
    print('Portal scope and all existing legacy links preserved; non-portal baseline files:',len(original_files)-2,flush=True)
    sys.path.insert(0,str(PACKAGE))
    from scripts import validate_public as public
    structure=public.structural_checks(PACKAGE)
    print('Packaged structural validation passed:',structure['package_files'],'members',flush=True)
    Handler.case_paths={''}|{p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if '.git' not in p.parts}
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    cache={};doms={};browser_results=[];http_results=[]
    def url(path):return origin+PREFIX+quote(path,safe='/')
    def content(path):
        if path not in cache:
            with urlopen(url(path),timeout=30) as response:
                assert response.status==200
                cache[path]=response.read()
        return cache[path]
    def fetch(row):
        digest=hashlib.sha256();length=0
        with urlopen(url(row['destination']),timeout=45) as response:
            assert response.status==200
            while chunk:=response.read(1024*1024):digest.update(chunk);length+=len(chunk)
            content_type=response.headers.get('Content-Type')
        assert digest.hexdigest()==row['sha256'] and length==row['bytes'],row['destination']
        return dict(path=row['destination'],status=200,bytes=length,sha256=digest.hexdigest(),content_type=content_type)
    browser=None
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:http_results=list(pool.map(fetch,rows))
        print('HTTP content/hash validation passed for all',len(http_results),'copied files',flush=True)
        exports=0;graphs=[]
        for module in MODULES:
            canonical=Graph().parse(data=content('Textile/2.0.0/package/ontology/textile-'+module+'.ttl'),format='turtle')
            for filename,format_ in [('ontology.ttl','turtle'),('ontology.owl','xml'),('ontology.nt','nt'),('ontology.jsonld','json-ld')]:
                graph=Graph().parse(data=content('Textile/2.0.0/'+module+'/'+filename),format=format_)
                assert isomorphic(canonical,graph),(module,filename)
                exports+=1
            data=json.loads(content('Textile/2.0.0/'+module+'/webvowl/data/ontology.json'))
            assert data.get('class') and data.get('classAttribute'),module
            graphs.append(dict(module=module,classes=len(data['class']),properties=len(data.get('property',[]))))
        print('HTTP RDF isomorphism passed:',exports,'exports; 12 WebVOWL JSON graphs valid',flush=True)
        for page in ('index.html','ontologies.html','Textile/2.0.0/index.html'):
            doms[urlsplit(url(page)).path]=DOM(content(page).decode('utf8'))
        browser=Browser(args.edge,args.browser_tools)
        for module in MODULES:
            canonical=Graph().parse(DEST/f'package/ontology/textile-{module}.ttl')
            namespace='https://w3id.org/eudpp/textile-'+module+'#'
            annotations=sorted(str(s)[len(namespace):] for s in canonical.subjects(RDF.type,OWL.AnnotationProperty) if str(s).startswith(namespace))
            path='Textile/2.0.0/'+module+'/index-en.html'
            dom,result=browser.page(url(path),'module',annotations)
            doms[urlsplit(url(path)).path]=dom;browser_results.append(result)
            path='Textile/2.0.0/'+module+'/webvowl/index.html'
            dom,result=browser.page(url(path),'webvowl')
            doms[urlsplit(url(path)).path]=dom;browser_results.append(result)
            print('Browser AJAX, annotation anchors and WebVOWL passed:',module,flush=True)
        references=0;fragments=0;application_routes=0;external=0;targets=set()
        for page,dom in list(doms.items()):
            for link in dom.links:
                target=urlsplit(urljoin(origin+page,link['url']))
                if target.scheme not in ('http','https') or target.netloc!=urlsplit(origin).netloc:
                    external+=1;continue
                if not target.path.startswith(PREFIX):raise AssertionError('Local URL escapes Pages prefix: '+target.path)
                relative=unquote(target.path[len(PREFIX):]);targets.add(relative);references+=1
                if target.fragment:
                    if target.path.endswith('/webvowl/index.html') and re.fullmatch(r'opts=editorMode=true;#new_ontology\d+',target.fragment):
                        application_routes+=1;continue
                    if target.path not in doms:
                        body=content(relative)
                        if target.path.endswith(('.html','/')):doms[target.path]=DOM(body.decode('utf8'))
                    if target.path in doms:
                        assert unquote(target.fragment) in doms[target.path].ids,(page,link['url'])
                        fragments+=1
        # Probe every local target, including unchanged sector and historic pages.
        for path in sorted(targets):content(path)
        for row in rows:
            if row['destination'].endswith('.css'):
                path=row['destination'];text=(ROOT/path).read_text('utf8')
                for value in re.findall(r'url\(\s*[\"\']?([^\"\')]+)',text):
                    target=urlsplit(urljoin(url(path),value.strip()))
                    if target.netloc==urlsplit(origin).netloc and target.path.startswith(PREFIX):content(unquote(target.path[len(PREFIX):]))
        legacy=[name for name in original_files if name.endswith('/index-en.html')]
        for name in legacy:content(name)
        result=dict(status='passed',source_commit=assembly.SHA,documentation_baseline=assembly.BASE,
                    expected_base_url=inventory['expected_base_url'],http_base_path=PREFIX,http_server='local loopback HTTP; directory listings disabled; exact case-sensitive paths enforced',
                    copied_files_verified=len(rows),copied_bytes=inventory['transfer_bytes'],package_files=inventory['package_files'],package_bytes=inventory['package_bytes'],
                    checksum_contract_files=structure['package_files'],sha256_contract_rows=structure['package_files']-1,
                    rdf_exports_isomorphic=exports,webvowl_json_graphs=graphs,
                    browser=browser.version['Browser'],browser_transport='Chrome DevTools Protocol; actual rendered DOM and Network events',
                    browser_pages=browser_results,ajax_sections_loaded=sum(len(row['ajax_sections']) for row in browser_results),
                    browser_rendered_webvowl_graphs=sum(row['kind']=='webvowl' and row['graph_nodes']>0 for row in browser_results),
                    local_dom_references_checked=references,fragment_targets_checked=fragments,application_routes=application_routes,
                    local_link_errors=0,external_references_inventoried=external,legacy_and_other_sector_pages_http_200=len(legacy),
                    prior_tracked_files_preserved=len(original_files)-2,portal_edits='Textile regions only; all legacy links retained',
                    structural_validation=structure,http_transfer_results=http_results,
                    limitations=['External DNS was disabled in the browser to isolate copied local assets; external badges, citations, ReSpec delivery and optional remote ontology loading are not claimed verified.',
                                 'Loopback HTTP and the actual Pages base path were tested; production deployment, CDN MIME behavior and persistent w3id redirects remain separate post-deployment checks.',
                                 'Canonical bytes and the 205-test source validation records are copied unchanged; the semantic regression suite was not rerun for this documentation-only transfer.'],
                    deployment_performed=False,remote_branch_pushed=False,remote_pr_opened=False)
        (PUBLICATION/'validation-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ('http_transfer_results','browser_pages','structural_validation')},indent=2),flush=True)
    finally:
        if browser:browser.close()
        server.shutdown();server.server_close()

if __name__=='__main__':main()