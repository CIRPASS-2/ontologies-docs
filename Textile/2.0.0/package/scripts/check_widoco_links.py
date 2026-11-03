"""Check local WIDOCO files and fragment anchors in their assembled AJAX DOM.

External HTTP links are inventoried, not treated as locally verified endpoints.
This checks static references and literal jQuery.load paths, not arbitrary JS.
"""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
LOAD=re.compile(r'\.load\(\s*["\']([^"\']+)["\']')


class Document(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if not value:continue
            if key in ('id','name'):self.ids.add(value)
            if key in ('href','src'):self.links.append((tag,key,value))


def audit_tree(root):
    root=Path(root).resolve()
    files=sorted(root.rglob('*.html'))
    parsed={};texts={}
    for path in files:
        texts[path]=path.read_text('utf8')
        parsed[path]=Document();parsed[path].feed(texts[path])
    # Sections are injected into the module document and inherit its URL base.
    roots=[p for p in files if p.parent.name!='sections']
    assemblies={};loads=[]
    for page in roots:
        members=[page]
        for url in LOAD.findall(texts[page]):
            target=(page.parent/unquote(urlsplit(url).path)).resolve()
            loads.append((page,url,target))
            if target in parsed:members.append(target)
        assemblies[page]=members
    ids={page:set().union(*(parsed[p].ids for p in members)) for page,members in assemblies.items()}
    references=[]
    def record(page,source,tag,attribute,url):
        split=urlsplit(url)
        row={'page':page.relative_to(root).as_posix(),'source':source.relative_to(root).as_posix(),
             'tag':tag,'attribute':attribute,'url':url}
        if split.scheme or split.netloc:row['status']='external_not_checked'
        else:
            path=(page.parent/unquote(split.path)).resolve() if split.path else page
            row['target']=path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
            if split.path.startswith('/'):row['status']='root_absolute_path'
            elif not path.is_relative_to(root):row['status']='outside_documentation_tree'
            elif not path.exists():row['status']='missing_file'
            elif split.fragment and (path in parsed):
                target_ids=ids.get(path,parsed[path].ids)
                app=path.parent/'js/webvowl.app.js'
                route=(path.parent.name=='webvowl' and path.name=='index.html'
                       and split.fragment=='opts=editorMode=true;#new_ontology1'
                       and app.is_file() and '"#opts=editorMode=true;#new_ontology"' in app.read_text('utf8'))
                row['status']=('application_route' if route else
                               'ok' if unquote(split.fragment) in target_ids else 'missing_anchor')
            else:row['status']='ok'
        references.append(row)
    injected=set()
    for page,members in assemblies.items():
        injected.update(members[1:])
        for member in members:
            for tag,attribute,url in parsed[member].links:record(page,member,tag,attribute,url)
    # Audit any orphan section as a standalone fragment, rather than silently
    # dropping it from the inventory. Standard WIDOCO sections are all loaded.
    for page in files:
        if page not in assemblies and page not in injected:
            for tag,attribute,url in parsed[page].links:record(page,page,tag,attribute,url)
    for page,url,target in loads:record(page,page,'ajax','load',url)
    references.sort(key=lambda row:tuple(str(row.get(k,'')) for k in ('page','source','tag','attribute','url')))
    errors=[row for row in references if row['status'] not in ('ok','external_not_checked','application_route')]
    return {'html_files':len(files),'assembled_pages':len(assemblies),'ajax_sections':len(loads),
            'reference_count':len(references),'statuses':dict(sorted(Counter(r['status'] for r in references).items())),
            'errors':errors,'references':references}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT/'docs/widoco')
    parser.add_argument('--json',type=Path)
    args=parser.parse_args();report=audit_tree(args.root)
    if args.json:args.json.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items() if k!='references'},indent=2))
    raise SystemExit(bool(report['errors']))
