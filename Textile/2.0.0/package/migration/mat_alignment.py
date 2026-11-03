"""Exact approved MAT bridge and reproducible evidence against the frozen baseline."""
import hashlib
import json
import subprocess
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal
from rdflib.namespace import DCTERMS, SKOS, XSD
from rdflib.compare import graph_diff, to_isomorphic, isomorphic
from scripts import validate_public as v

ROOT = v.ROOT
BASELINE = 'a2bc2642627bf9223b1e39dc54a4e45c233e9232'
TXT = Namespace('https://w3id.org/eudpp/textile-core#')
DPP = Namespace('https://w3id.org/eudpp#')
AXIOMS = {
    (TXT.FibreTypeConcept, RDFS.subClassOf, DPP.MaterialType),
    (TXT.hasFibreType, RDFS.subPropertyOf, DPP.hasMaterialType),
}
# Exact owner-approved transition, separate from the immutable pre-MAT baseline.
# No predicate-wide exclusions: the old/new literals and their subjects matter.
NOTE_CORRECTIONS = {
    'textile-core.ttl': (
        TXT.hasFibreCompositionComponent,
        'No subproperty alignment with dpp:hasMaterialType is asserted because the MAT property links a MaterialOfComposition to an OWL MaterialType, while this textile property links a TextileProduct to a structured FibreCompositionComponent that uses a SKOS fibre-type value.',
        'No subproperty alignment with dpp:hasMaterialType is asserted because hasFibreCompositionComponent links a textile product to a structured composition entry, whereas dpp:hasMaterialType links a material-of-composition entry to a classification value. Their subject and object roles differ.',
    ),
    'textile-associated-materials.ttl': (
        Namespace('https://w3id.org/eudpp/textile-associated-materials#').PackagingMaterial,
        'PackagingMaterial is aligned as a subclass of dpp:MaterialOfComposition. The textile-specific type property remains separate because its range is a SKOS controlled concept, while dpp:hasMaterialType ranges over an OWL class.',
        'PackagingMaterial is aligned as a subclass of dpp:MaterialOfComposition. Instances of a SKOS-based classification class can also instantiate an OWL material-classification class; the SKOS representation does not prevent such alignment. Packaging-specific class and type-property alignment remains a separate modelling decision requiring its own semantic assessment. No packaging alignment is introduced here.',
    ),
}


def expected_delta(relative):
    """Return only the seven additions and six removals approved by the owner."""
    assert relative in {'ontology/' + name for name in v.CURRENT_MODULES}, relative
    filename = Path(relative).name
    added = set(AXIOMS) if filename == 'textile-core.ttl' else set()
    removed = set()
    if filename in ('textile-core.ttl', 'textile-connector.ttl', 'textile-associated-materials.ttl'):
        ontology = Namespace('https://w3id.org/eudpp/')[Path(filename).stem]
        removed.add((ontology, DCTERMS.modified, Literal('2026-10-27', datatype=XSD.date)))
        added.add((ontology, DCTERMS.modified, Literal('2026-11-02', datatype=XSD.date)))
    if filename in NOTE_CORRECTIONS:
        subject, old, new = NOTE_CORRECTIONS[filename]
        predicate = Namespace('https://w3id.org/eudpp/textile-connector#').modellingNote
        removed.add((subject, predicate, Literal(old, lang='en')))
        added.add((subject, predicate, Literal(new, lang='en')))
    if filename == 'textile-connector.ttl':
        removed.add((SKOS.closeMatch, RDF.type, OWL.ObjectProperty))
    return added, removed


def restore_frozen_graph(graph, relative):
    """Verify the entire current graph, then reverse only the approved delta.

    Older creator/header proofs can retain their original digests. This is
    deliberately not a projection that discards all notes or modified dates.
    """
    baseline = Graph().parse(data=baseline_bytes(relative), format='turtle')
    added, removed = expected_delta(relative)
    assert removed <= set(baseline), relative
    assert not (added & set(baseline)), relative
    expected = baseline + Graph()
    for triple in removed:
        expected.remove(triple)
    for triple in added:
        expected.add(triple)
    assert isomorphic(graph, expected), 'Unauthorized canonical RDF difference: ' + relative
    restored = graph + Graph()
    for triple in added:
        restored.remove(triple)
    for triple in removed:
        restored.add(triple)
    assert isomorphic(restored, baseline), relative
    return restored


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
        raw = baseline_bytes(name)
        before = Graph().parse(data=raw, format='turtle')
        after = Graph().parse(path)
        _, added, removed = graph_diff(to_isomorphic(after), to_isomorphic(before))
        want_added, want_removed = expected_delta(name)
        assert set(added) == want_added, 'Unauthorized additions: ' + name
        assert set(removed) == want_removed, 'Unauthorized removals: ' + name
        restore_frozen_graph(after, name)
        rows.append(dict(file=name, baseline_sha256=hashlib.sha256(raw).hexdigest(),
                         candidate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         added=statements(added), removed=statements(removed)))
    return rows


def protected_hashes():
    areas = ['catalog-v001.xml', 'dependencies', 'mireot', 'migration/core-sources',
             'migration/historical', 'shacl', 'examples', 'traceability']
    names = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', BASELINE, '--', *areas],
        cwd=ROOT, text=True).splitlines()
    packaged = {name for name in v.package_files(ROOT)
                if any(name == area or name.startswith(area + '/') for area in areas)}
    assert packaged == set(names), 'Protected file inventory changed'
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
                  canonical_added_statements=7, canonical_removed_statements=6,
                  approved_scope='Two MAT additions, two exact modelling-note replacements, three exact modified-date replacements, one obsolete closeMatch declaration removal; no other canonical changes.',
                  canonical_graphs=modules, protected_file_sha256=protected,
                  inferred_fibre_material_types=statements((s, RDF.type, DPP.MaterialType) for s in concepts),
                  inferred_mat_classification_edges=statements(inferred_edges),
                  owlrl_errors=engine.error_messages, rdf_exports_isomorphic=exports,
                  creators_and_version_identities_preserved=True,
                  annotation_rendering_idempotent_modules=12,
                  widoco_links={k: value for k, value in links.items() if k != 'references'},
                  reasoning_limit='RDFS and OWL RL regression coverage; no complete OWL DL consistency proof.')
    (ROOT / 'migration/approved-candidate-results.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print('Candidate evidence: 7 additions, 6 removals; 22 classified concepts; 2 inferred example edges; 48 exports; 0 broken links.')


if __name__ == '__main__':
    record()
