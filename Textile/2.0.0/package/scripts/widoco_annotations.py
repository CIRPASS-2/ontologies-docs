"""Render omitted local annotation properties from canonical RDF, without edits to RDF."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from rdflib import Graph, URIRef, RDF, RDFS, OWL
from rdflib.namespace import SKOS, DCTERMS

ROOT=Path(__file__).resolve().parents[1]
START='<!-- BEGIN canonical annotation-property documentation -->'
END='<!-- END canonical annotation-property documentation -->'


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set()
    def handle_starttag(self,tag,attrs):
        self.ids.update(value for key,value in attrs if key in ('id','name') and value)


def render(graph, text):
    """Idempotent supplement for local declarations absent from native WIDOCO.

    A full generation starts from WIDOCO's cross-reference output. A supplement
    regeneration removes its own previous block and uses the same canonical RDF.
    """
    text=re.sub(re.escape(START)+r'.*?'+re.escape(END)+r'\n?', '',text,flags=re.S)
    ontology=next(graph.subjects(RDF.type,OWL.Ontology))
    namespace=str(ontology)+'#'
    properties=sorted(s for s in graph.subjects(RDF.type,OWL.AnnotationProperty)
                      if isinstance(s,URIRef) and str(s).startswith(namespace))
    anchors=Anchors();anchors.feed(text)
    missing=[s for s in properties if str(s)[len(namespace):] not in anchors.ids]
    if missing:
        rows=[START,'<div id="canonical-annotation-properties">',
              '<h3 class="list" id="canonical-annotation-properties-headline">Annotation properties</h3>',
              '<p>Declarations and descriptions below are rendered from the canonical module RDF.</p>']
        for subject in missing:
            local=str(subject)[len(namespace):]
            labels=sorted(graph.objects(subject,RDFS.label),key=lambda value:(value.language!='en',str(value)))
            label=str(labels[0]) if labels else local
            rows += [f'<div class="entity" id="{escape(local,quote=True)}">',
                     f'<h3>{escape(label)} <sup class="type-ap" title="annotation property">ap</sup></h3>',
                     f'<p><strong>IRI:</strong> <code>{escape(str(subject))}</code></p>']
            for predicate in (SKOS.definition,RDFS.comment):
                for value in sorted(graph.objects(subject,predicate),key=str):
                    rows.append('<div class="comment"><p>'+escape(str(value))+'</p></div>')
            for predicate,title in ((RDFS.domain,'Domain'),(RDFS.range,'Range'),
                                    (RDFS.subPropertyOf,'Subproperty of'),(RDFS.isDefinedBy,'Defined by'),
                                    (DCTERMS.source,'Source')):
                for value in sorted(graph.objects(subject,predicate),key=str):
                    # Render factual metadata without making new local hrefs or
                    # claiming that any externally hosted IRI is already live.
                    rows.append(f'<p><strong>{title}:</strong> <code>{escape(str(value))}</code></p>')
            rows += ['<p class="backlink"><a href="#toc">Back to table of contents</a></p>','</div>']
        rows += ['</div>',END]
        block='\n'.join(rows)+'\n'
        marker='<div id="legend">'
        if marker not in text:raise ValueError('WIDOCO legend insertion point not found')
        text=text.replace(marker,block+marker,1)
    # Only repair hrefs whose exact bare name is a declared local annotation
    # property. Literal text and external namespace references are untouched.
    for subject in properties:
        local=str(subject)[len(namespace):]
        pattern=r'(<a\b[^>]*\bhref=)(["\'])'+re.escape(local)+r'\2'
        text=re.sub(pattern,lambda match:match[1]+match[2]+'#'+local+match[2],text)
    return text


def regenerate(module):
    source=ROOT/f'ontology/textile-{module}.ttl'
    if not source.is_file():raise ValueError('Unknown module: '+module)
    path=ROOT/f'docs/widoco/{module}/sections/crossref-en.html'
    text=render(Graph().parse(source,format='turtle'),path.read_text('utf8'))
    path.write_text(text,encoding='utf8',newline='\n')
    print('Canonical annotation-property documentation:',module)


if __name__=='__main__':
    for module in sys.argv[1:]:regenerate(module)
