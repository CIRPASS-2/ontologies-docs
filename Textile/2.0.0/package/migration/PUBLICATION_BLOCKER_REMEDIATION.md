# Textile 2.0.0 publication blocker remediation

Baseline: `1866acd9f998976481dcfaba3b531c016822b87f`. Candidate version remains
2.0.0. This correction is local preparation; remote publication is not authorized.

## Documentation correction and complete local link inventory

The WIDOCO supplement in `scripts/widoco_annotations.py` derives missing local
annotation-property sections from canonical RDF and converts only exact bare
local annotation-property hrefs into fragment links. It is idempotent and is
invoked by the existing `scripts/generate-widoco-docs.ps1` mechanism after RDF
synchronization. Only connector/context cross-reference HTML was regenerated;
the supplement renders all missing local annotation declarations in those modules
without creating or redefining any RDF resource. No RDF serialization changed.

| Link inventory | Before | After |
|---|---:|---:|
| HTML files / assembled pages / AJAX loads | 121 / 37 / 84 | 121 / 37 / 84 |
| Total references | 12,310 | 12,319 |
| Broken sourceLocator references | 20 | 0 |
| Broken sourceType references | 20 | 0 |
| Broken typicallyQualifiesProcess references | 9 | 0 |
| Other broken local files or anchors | 0 | 0 |
| Valid local references | 6,855 | 6,913 |
| Verified WebVOWL application-route references | 12 | 12 |
| External references inventoried, not locally checked | 5,394 | 5,394 |

Full per-reference inventories are in `widoco-links-before.json` and
`widoco-links-after.json`. The checker assembles literal jQuery-loaded sections
with the parent page URL base and combines their anchors. It does not execute
arbitrary JavaScript or claim that every external HTTP link works. The precise
WebVOWL `#opts=editorMode=true;#new_ontology1` route is generated and handled by
the bundled application; it is recognized only on its WebVOWL page when the
corresponding route-producing code exists. Unknown hash routes still fail.

Public structural validation now enforces the complete local link check.
Regression tests cover idempotent canonical rendering, missing files/anchors,
AJAX URL bases and the narrow application-route exception. The existing
untracked publication plan remains excluded by an explicit one-file package
rule; other migration documents continue to enter the integrity contract.

## Validation and boundaries

The final machine-readable results are recorded in `validation-results.json`,
`validation-pytest.xml` and `publication-blocker-results.json`. They include the
complete regression suite, both public validation modes, a protected-file byte
comparison to the accepted baseline, canonical graph equivalence, all 48 WIDOCO
export isomorphisms, manifest/checksum verification and historical closure tests.
The change inventory records exact files relative to the accepted baseline.

No canonical ontology RDF, creator metadata, MIREOT, SHACL, instance examples,
source attribution, historical artefact or authoritative CORE source is changed.
The RDF semantic difference is empty, with no metadata exclusions required.

## Resolver decisions still pending

The [coordination brief](../docs/TEXTILE_IRI_RESOLVER_COORDINATION_2.0.0.md)
contains all 20 actual identities/version IRIs, proposed destinations, 94 current
HTTP observations, preserved CORE redirects, historical closure requirements and
the nine retained version-identity conflict. It recommends protecting historical
bytes while selecting current package snapshots through versionless aliases,
subject to owner/maintainer agreement. No version metadata or redirect was edited.

Before release, the owner must authorize source merge, documentation deployment,
release artifacts and tagging. Namespace maintainers must confirm responsibility,
approve the identity/routing policy and content negotiation, then authorize their
own deployment. Neither this local correction nor the brief authorizes publishing.
