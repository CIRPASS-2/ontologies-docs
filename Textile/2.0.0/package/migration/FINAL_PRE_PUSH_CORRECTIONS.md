# Final local pre-push corrections for Textile 2.0.0

Baseline: `ba6e12ef769d3849bde078ef4f1d32bdcf5e1af1`. Owner-approved Option B.
The candidate remains 2.0.0. No remote operation is authorized or performed.

## Exact scope and metadata proof

Assessment, connector, context, core, durability, indicator, process, repairability
and structure now declare `/2.0.0`, cite their historical `/1.1.2` IRI through
`owl:priorVersion`, use `Version 2.0.0 candidate`, and record the actual revision
date `2026-10-27`. Their header citation text also reflects 2.0.0 candidate.
Only these five predicates on the ontology header are excluded in the semantic
comparison. Exact statements before/after are in `version-identity-results.json`:
**36 removed, 45 added, zero non-metadata RDF differences** across all 13 graphs.
All approved creators and all domain assertions remain unchanged. The original
frozen creator proof is retained, with only this exact subsequent header diff
reversed for comparison; it is not replaced by a weaker creator-only check.

All thirteen Textile graphs and six rebuilt MIREOTs now declare 2.0.0 identities.
The unchanged SI MIREOT retains its 1.1.2 identity and bytes. The complete exact
inventory is `current-version-iri-inventory.json`. The active catalogue maps each
of the 19 current 2.0.0 version IRIs to its canonical file. Historical version
identities remain exclusively in the standalone historical catalogue; old SI
version resolution also uses that catalogue and its identical preserved bytes.

The archive, extracted historical runtime, historical catalogue, authoritative
CORE files, all seven MIREOTs, SHACL constraints, instances, diagrams and source
attribution are byte-unchanged. The historical root/SoC import closures remain
19/12 graphs, with no CON MIREOT or 2.0.0 graph entering history. Current closure
is 20 graphs, also reached through the current root's version-specific IRI.

## Regenerated documentation and reproducibility

The existing WIDOCO generator regenerated the nine affected modules and the
network landing page. All 36 affected RDF exports contain only the same header
metadata change as their canonical sources; all **48 exports** are graph-isomorphic
to canonical RDF. Serializer order and blank-node identifiers may change text
without changing the graph. The new provenance subjects identify 2.0.0 and record
`prov:wasRevisionOf` 1.1.2; exact provenance and export statement changes are
recorded separately in `final-pre-push-results.json`.

The existing annotation supplement was run for all twelve modules, including
core, durability and process. All twelve outputs are stable on repeat rendering;
every declared local annotation property has an anchor and no bare local property
href remains. Regression coverage now spans all twelve modules. Full Java output
is not claimed byte-deterministic: WebVOWL identifiers and serializer ordering
may vary. The maintained supplement's idempotency and RDF equivalence are checked.

The complete local inventory covers **121 HTML files, 37 assembled pages,
84 AJAX-loaded sections and 12,336 references**, with **zero broken local links**.
The twelve precise WebVOWL application routes remain verified separately from
DOM anchors. External references are inventoried, not exhaustively HTTP-tested.

WIDOCO could not retrieve historical version IRIs for its optional automated
changelog. Exact local differences replace that evidence. WIDOCO also retains
ontology-supplied creation dates in its existing documentation-provenance date
fields; the actual canonical revision date is explicitly 2026-10-27. These are
documentation-tool limitations, not changes to ontology assertions.

## Validation, traceability and coordination

`final-pre-push-results.json`, `validation-results.json` and `validation-pytest.xml`
record final checks. The suite contains **205 tests**, preserving the previous
180 and extending annotation idempotency by ten cases plus fifteen version,
metadata and catalogue cases. Both partial and complete-report modes validate
11 examples, 16 original SHACL scenarios, six reasoning scenarios and the
recyclability control. Migration-specific semantic cases, MIREOT fidelity,
creator preservation and historical closure checks remain in the full suite.
RDF-derived traceability tables remain byte-identical because ontology-header
metadata is outside their resource projection. Manifest and SHA-256 integrity
are refreshed after all evidence records are finalized. Exact changed files are
listed in the pre-push section of `change-inventory.json`; changed regenerated
assets and protected-file hashes are listed in `final-pre-push-results.json`.

The updated resolver coordination brief separates immutable version-specific
routes from versionless aliases, specifies proposed historical Turtle-only and
406 behavior, explains fragment inheritance and dynamically loaded HTML anchors,
and separates CIRPASS source publication from namespace-maintainer deployment.
The owner's Option B decision is complete; routing deployment requires maintainer
agreement and separate authorization. Existing CORE routes are untouched.

Earlier evidence files remain snapshots of their named baselines; in particular
the pre-correction HTTP record is not an inventory of the nine newly declared
version IRIs. This report and the current inventory describe the final candidate.
The source publication plan remains untracked, separate from the checksummed
release package. No push, merge, tag, Pages publication or namespace deployment
is performed. Successful local checks establish readiness for an authorized
GitHub branch push and PR review, not authorization to perform them.
