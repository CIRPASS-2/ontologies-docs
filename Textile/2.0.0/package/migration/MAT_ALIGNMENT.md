# Approved CORE MAT alignment — 2026-11-02

Nader Jelassi's [source PR #19 review](https://github.com/CIRPASS-2/ontologie-textiles/pull/19)
identified an unimplemented bridge. The owner approved both axioms after the
independent investigation of baseline `a2bc2642627bf9223b1e39dc54a4e45c233e9232`.

```turtle
<https://w3id.org/eudpp/textile-core#FibreTypeConcept>
    <http://www.w3.org/2000/01/rdf-schema#subClassOf>
    <https://w3id.org/eudpp#MaterialType> .
<https://w3id.org/eudpp/textile-core#hasFibreType>
    <http://www.w3.org/2000/01/rdf-schema#subPropertyOf>
    <https://w3id.org/eudpp#hasMaterialType> .
```

These are the only canonical RDF additions; no canonical RDF statement is
removed. All thirteen ontology graphs are compared against the frozen baseline.
This is an intentional entailment extension within the 2.0.0 candidate; every
existing ontology/MIREOT version identity and all six creators are preserved.

MAT 1.1.0 defines MaterialType as a sector classification placeholder, explicitly
mentioning cotton and nylon. FibreTypeConcept is an OWL class of controlled SKOS
classification individuals; its existing subclass axiom to skos:Concept remains.
These individuals can also instantiate MaterialType without becoming physical
fibres or OWL classes themselves. Broad fibre categories are classifications too.

hasFibreType links a FibreCompositionComponent to that classification. The
subject already subclasses MaterialOfComposition. Its MAT superproperty therefore
operates at the same conceptual level. hasFibreCompositionComponent continues to
link a product to an entry and is deliberately not aligned to hasMaterialType.
Physical TextileFibre batches remain products. Fractions and SI units are intact.

The JRC references motivate domain content and composition requirements. These
two OWL bridges are project decisions, not requirements attributed to JRC.
The earlier modelling guide explicitly left this bridge unresolved; this decision
resolves that question without reopening other migration decisions.

## Evidence and reproduction

[Machine-readable evidence](mat-alignment-results.json) records exact canonical
graph differences, protected input hashes, all 22 inferred fibre material types,
the two inferred public-example MAT edges, 48 isomorphic RDF downloads,
idempotent annotation rendering and the full local WIDOCO link audit.

The focused regression file adds 16 test cases, using both RDFS and OWL RL.
It checks the exact graph delta, preserved SKOS and material-entry typing,
property entailments, forbidden product typing/property alignment, historical
bytes and unchanged default/complete-report SHACL outcomes on public examples.
Earlier frozen creator and version proofs reverse only these exact two later
axioms before checking their original digests; the new exact-delta test checks
that no other canonical changes are concealed.

Run from the source root:

```powershell
python -B -m migration.mat_alignment
python -B -m migration.refresh_publication --integrity
python -B -m pytest -p no:cacheprovider tests -q
python -B scripts/validate_public.py --full
python -B scripts/validate_public.py --full --complete-report
```

RDFS/OWL RL tests establish their supported entailments. They are not a complete
OWL DL consistency proof. Plain queries without inference require materialized
MAT edges to discover the additional classifications. Full upstream MAT/SI inputs,
bounded MIREOTs, SHACL, example data and historical archives remain byte-identical.
The full existing regression suite independently checks MIREOT fidelity and
historical catalogue isolation. Generated Core WIDOCO/WebVOWL, RDF exports and
the Core diagram expose the same approved bridge; other module graphs are intact.

## Validation environment correction

The public content scanner remains unchanged. The review record now cites this
evidence through its GitHub source-branch URL instead of a rejected relative
path containing two parent-directory segments. The target is the same evidence
file; the local target and normal publication checks verify its availability.

The seven earlier pytest setup errors arose from Windows access denial while
enumerating pytest's private temporary directory. ACL inspection confirmed that
pytest's private directory permits the owner, administrators and SYSTEM but
omits the restricted execution token. This also affects a fresh workspace
basetemp; changing only the path is insufficient. The seven affected tests pass
when executed outside that restricted token. Final validation uses that same
execution context and a dedicated `--basetemp` outside package areas. No test,
fixture, ACL or validation rule is disabled or weakened.
Final results are recorded in [validation evidence](mat-alignment-validation.json).
