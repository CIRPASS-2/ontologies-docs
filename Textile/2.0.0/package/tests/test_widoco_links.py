from pathlib import Path
import pytest
from rdflib import Graph, RDF, OWL
from scripts.check_widoco_links import audit_tree
from scripts.widoco_annotations import render, Anchors
from scripts.validate_public import package_files

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('module',[
    'assessment','associated-materials','connector','context','core','durability',
    'indicator','process','recyclability','repairability','soc','structure',
])
def test_canonical_annotation_rendering_is_idempotent(module):
    graph=Graph().parse(ROOT/f'ontology/textile-{module}.ttl')
    text=(ROOT/f'docs/widoco/{module}/sections/crossref-en.html').read_text('utf8')
    assert render(graph,text)==text
    anchors=Anchors();anchors.feed(text)
    namespace='https://w3id.org/eudpp/textile-'+module+'#'
    names=[str(subject)[len(namespace):] for subject in graph.subjects(RDF.type,OWL.AnnotationProperty)
           if str(subject).startswith(namespace)]
    for name in names:
        assert name in anchors.ids
        assert f'href="{name}"' not in text


def test_complete_widoco_inventory():
    report=audit_tree(ROOT/'docs/widoco')
    assert not report['errors']
    assert report['html_files']==121
    assert report['ajax_sections']==84
    assert report['statuses']['application_route']==12


def test_ajax_links_use_parent_document_base(tmp_path):
    (tmp_path/'sections').mkdir()
    (tmp_path/'index.html').write_text('<script>$("x").load("sections/x.html");</script>')
    section=tmp_path/'sections/x.html'
    section.write_text('<a href="#target">x</a><div id="target"></div>')
    assert not audit_tree(tmp_path)['errors']
    section.write_text('<a href="#missing">x</a>')
    assert audit_tree(tmp_path)['errors'][0]['status']=='missing_anchor'
    section.write_text('<a href="missing.html">x</a>')
    assert audit_tree(tmp_path)['errors'][0]['status']=='missing_file'


def test_webvowl_route_exception_requires_application_code(tmp_path):
    folder=tmp_path/'webvowl';folder.mkdir()
    page=folder/'index.html'
    page.write_text('<a href="#opts=editorMode=true;#new_ontology1">new</a>')
    assert audit_tree(tmp_path)['errors']
    (folder/'js').mkdir()
    (folder/'js/webvowl.app.js').write_text('href = "#opts=editorMode=true;#new_ontology" + counter;')
    assert not audit_tree(tmp_path)['errors']
    page.write_text('<a href="#unrecognised">broken</a>')
    assert audit_tree(tmp_path)['errors']


def test_planning_exclusion_is_narrow(tmp_path):
    folder=tmp_path/'migration';folder.mkdir()
    (folder/'PUBLICATION_PLAN_2.0.0.md').write_text('working plan')
    (folder/'other.md').write_text('release evidence')
    files=package_files(tmp_path)
    assert 'migration/PUBLICATION_PLAN_2.0.0.md' not in files
    assert 'migration/other.md' in files
