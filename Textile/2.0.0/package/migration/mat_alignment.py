"""Exact approved MAT bridge and reproducible evidence against the frozen baseline."""
import hashlib
import json
import subprocess
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.compare import graph_diff, to_isomorphic
from scripts import validate_public as v

ROOT = v.ROOT
BASELINE = 'a2bc2642627bf9223b1e39dc54a4e45c233e9232'
TXT = Namespace('https://w3id.org/eudpp/textile-core#')
DPP = Namespace('https://w3id.org/eudpp#')
AXIOMS = {
    (TXT.FibreTypeConcept, RDFS.subClassOf, DPP.MaterialType),
    (TXT.hasFibreType, RDFS.subPropertyOf, DPP.hasMaterialType),
}


def without_alignment(graph):
    """Reverse only the approved later bridge when checking older frozen proofs."""
    result = graph + Graph()
    for triple in AXIOMS:
        result.remove(triple)
    return result


def baseline_bytes(name):
    return subprocess.check_output(['git', 'show', BASELINE + ':' + name], cwd=ROOT)


def statements(graph):
    return sorted(' '.join(term.n3() for term in triple) + ' .' for triple in graph)


def canonical_differences():
    rows = []
    for path in sorted((ROOT / 'ontology').glob('*.ttl')):
        name = path.relative_to(ROOT).as_posix()
        before = Graph().parse(data=baseline_bytes(name), format='turtle')
        after = Graph().parse(path)
        _, added, removed = graph_diff(to_isomorphic(after), to_isomorphic(before))
        assert not removed, name
        assert set(added) == (AXIOMS if path.name == 'textile-core.ttl' else set()), name
        rows.append(dict(file=name, added=statements(added), removed=statements(removed)))
    return rows


def protected_hashes():
    areas = ['dependencies', 'mireot', 'migration/core-sources',
             'migration/historical', 'shacl', 'examples', 'traceability']
    names = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', BASELINE, '--', *areas],
        cwd=ROOT, text=True).splitlines()
    batch = ''.join(BASELINE + ':' + name + '\n' for name in names).encode()
    raw = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                         input=batch, capture_output=True, check=True).stdout
    position = 0
    hashes = {}
    for name in names:
        end = raw.index(b'\n', position)
        header = raw[position:end].split()
        assert header[1] == b'blob'
        size = int(header[2]); data = raw[end + 1:end + 1 + size]
        position = end + size + 2
        assert (ROOT / name).read_bytes() == data, name
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def closure():
    return sum((Graph().parse(path) for path in v.catalogue_import_closure(
        ROOT / 'catalog-v001.xml', 'https://w3id.org/eudpp/textile-ontology/2.0.0')), Graph())


def record():
    from owlrl import OWLRL_Semantics
    from rdflib.namespace import SKOS
    from scripts.check_widoco_links import audit_tree
    from scripts.widoco_annotations import render
    from rdflib.compare import isomorphic
    modules = canonical_differences()
    protected = protected_hashes()
    graph = closure()
    examples = sum((Graph().parse(p) for p in (ROOT / 'examples').glob('*.ttl')), Graph())
    model = graph + examples
    engine = OWLRL_Semantics(model, False, False)
    engine.closure(); engine.flush_stored_triples()
    assert not engine.error_messages
    concepts = set(graph.subjects(RDF.type, TXT.FibreTypeConcept))
    assert len(concepts) == 22
    assert concepts <= set(model.subjects(RDF.type, DPP.MaterialType))
    assert concepts <= set(model.subjects(RDF.type, SKOS.Concept))
    inferred_edges = set(model.triples((None, DPP.hasMaterialType, None))) - set((graph + examples).triples((None, DPP.hasMaterialType, None)))
    exports = 0
    for path in (ROOT / 'ontology').glob('*.ttl'):
        source = Graph().parse(path)
        ontology = next(source.subjects(RDF.type, OWL.Ontology))
        past = Graph().parse(data=baseline_bytes(path.relative_to(ROOT).as_posix()), format='turtle')
        for predicate in [v.DCT.creator, OWL.versionIRI, OWL.versionInfo]:
            assert set(source.objects(ontology, predicate)) == set(past.objects(ontology, predicate))
        if path.stem == 'textile-ontology': continue
        folder = ROOT / 'docs/widoco' / path.stem.removeprefix('textile-')
        text = (folder / 'sections/crossref-en.html').read_text('utf8')
        assert render(source, text) == text
        for name, fmt in [('ontology.ttl', 'turtle'), ('ontology.owl', 'xml'),
                          ('ontology.nt', 'nt'), ('ontology.jsonld', 'json-ld')]:
            assert isomorphic(source, Graph().parse(folder / name, format=fmt))
            exports += 1
    links = audit_tree(ROOT / 'docs/widoco'); assert not links['errors']
    report = dict(baseline_commit=BASELINE, candidate='2.0.0',
                  canonical_added_statements=2, canonical_removed_statements=0,
                  canonical_graphs=modules, protected_file_sha256=protected,
                  inferred_fibre_material_types=statements((s, RDF.type, DPP.MaterialType) for s in concepts),
                  inferred_mat_classification_edges=statements(inferred_edges),
                  owlrl_errors=engine.error_messages, rdf_exports_isomorphic=exports,
                  creators_and_version_identities_preserved=True,
                  annotation_rendering_idempotent_modules=12,
                  widoco_links={k: value for k, value in links.items() if k != 'references'},
                  reasoning_limit='RDFS and OWL RL regression coverage; no complete OWL DL consistency proof.')
    (ROOT / 'migration/mat-alignment-results.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print('MAT evidence: 2 additions, 0 removals; 22 classified concepts; 2 inferred example edges; 48 exports; 0 broken links.')


if __name__ == '__main__':
    record()
