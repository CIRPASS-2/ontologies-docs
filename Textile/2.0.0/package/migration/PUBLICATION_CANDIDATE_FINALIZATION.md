# Textile 2.0.0 publication candidate finalization

The owner accepted the local closeMatch declaration removal and the two MAT
bridges. This finalization changes regression expectations and derived
publication artifacts; it makes no further canonical ontology changes.

## Frozen baselines and complete RDF scope

The immutable pre-MAT baseline is
`a2bc2642627bf9223b1e39dc54a4e45c233e9232`. The complete current delta is
**seven additions and six removals**, restricted to three canonical modules:

| Module | Additions | Removals | Exact scope |
| --- | ---: | ---: | --- |
| Textile Core | 4 | 2 | Two MAT axioms, one modelling-note replacement, one modified-date replacement. |
| Associated Materials | 2 | 2 | One modelling-note replacement, one modified-date replacement. |
| Connector | 1 | 2 | One modified-date replacement and removal of the old local closeMatch object-property declaration. |
| Other ten canonical modules | 0 | 0 | Unchanged. |

Every date replacement is exactly `2026-10-27` to `2026-11-02`. The note
subjects and complete old/new English literals are fixed in
[the existing comparison helper](mat_alignment.py). There are no predicate-wide
metadata exclusions, new declarations or replacement closeMatch declarations.
The machine-readable [candidate evidence](approved-candidate-results.json)
contains every added/removed RDF statement, per-module source hashes and
protected-file hashes. Reproduce it with `python -B -m migration.mat_alignment`.

## Each of the eight original failures

Full original expected/observed digests and RDF differences for every failure
are in the [failure reconciliation](publication-failure-reconciliation.json).
All eight differences are within the now-verified approved scope.

| Original failing check | Original baseline | Exact expectation and observed difference | Resolution |
| --- | --- | --- | --- |
| Creator-only graph proof | `f527fc577bec246a25d9332df018be6a64ec9070` | After reversing the recorded version-header changes and MAT bridges, every non-creator triple must match the frozen digest. The two notes, three dates and closeMatch declaration removal exceed that older proof; its first failure is Associated Materials. | Verify the complete approved delta, restore the exact pre-MAT graph, then execute the original creator proof. The original digest record is unchanged. |
| MAT-only exact delta | `a2bc2642627bf9223b1e39dc54a4e45c233e9232` | Exactly two additions and zero removals were expected; seven additions and six removals are observed. | Keep the baseline and require exact per-module equality with all 13 approved statement changes. |
| Associated Materials downloads | `e9cf8542d104fefccf339761d138fcf9c32bc904` | TTL must equal canonical bytes and all four RDF formats must match the source graph. The old downloads omit the note/date replacements. | Regenerate with the established workflow; keep the download test unchanged. |
| Connector downloads | `e9cf8542d104fefccf339761d138fcf9c32bc904` | The same byte/graph checks fail because the old downloads retain the obsolete declaration and old date. | Regenerate with the established workflow; keep the download test unchanged. |
| Core downloads | `e9cf8542d104fefccf339761d138fcf9c32bc904` | The same byte/graph checks fail because the old downloads omit the note/date replacements. Their MAT bridges were already present. | Regenerate with the established workflow; keep the download test unchanged. |
| Associated Materials version proof | `ba6e12ef769d3849bde078ef4f1d32bdcf5e1af1` | The frozen non-header digest excludes only the recorded header predicates. The new note changes that digest; the approved new date is also outside the older header proof. | Verify the exact delta before restoring the frozen graph for its original digest/date checks. |
| Connector version proof | `ba6e12ef769d3849bde078ef4f1d32bdcf5e1af1` | The declaration removal changes the non-header digest; the approved new date differs from the older revision date. | Apply the same exact restoration; preserve current identity/catalogue checks. |
| Core version proof | `ba6e12ef769d3849bde078ef4f1d32bdcf5e1af1` | The note replacement changes the non-header digest after reversing MAT; the approved new date differs from the older revision date. | Apply the same exact restoration; preserve current identity/catalogue checks. |

The original creator, version-identity and MAT-only evidence files remain
unchanged. Ten mutation regressions reject added classes/properties/subclass
axioms, unrelated deletions, unapproved notes/dates/creators, missing MAT
bridges and a replacement closeMatch declaration. The exact frozen catalogue
and all 75 previously protected inputs remain byte-protected; their package
inventory must also remain unchanged.

## Source-driven generation and validation

The existing `scripts/generate-widoco-docs.ps1` workflow was run with
`-OnlyModules @('associated-materials','connector','core')`. It regenerates
WIDOCO/WebVOWL, injects the existing editorial sections, synchronizes all
four RDF formats from canonical sources and regenerates the network landing
page. No generated ontology representation was manually edited. Other
modules and all frozen historical artifacts are preserved.
The current diagram inventory table is also regenerated from canonical type
counts using the existing inventory algorithm: only Connector's object-property
count changes from 14 to 13. Diagram images and all other inventory rows remain
unchanged.

Final test, publication-mode, graph-equivalence, link and integrity results
are recorded separately in [validation results](publication-candidate-validation.json).
The full suite passes **232 tests** (the original 221 plus 11 strict-scope
checks), with zero failed assertions, zero setup errors and 12 existing
rdflib deprecation warnings. Both normal full publication modes pass;
each validates 11 examples, 16 SHACL scenarios, six reasoning scenarios and
the RDFS negative control. All 48 RDF exports are graph-equivalent and all
12 TTL downloads equal the canonical bytes. Local HTTP checks pass for 181
pages/data/downloads; WIDOCO reports zero link errors, and all 135 current
public Markdown file references resolve.

Package hashes are refreshed from actual file bytes using the established
integrity workflow; unchanged members retain their old hashes. The manifest
also includes the new review and validation evidence: 800 package members
and 799 SHA-256 rows, with three separately inventoried reference resources.

## Known limits and governance

The canonical graphs are unchanged from the bounded diagnostic candidate:
the original modular closure has 208 declaration/visibility diagnostics;
the serialized merged artifact passes OWL 2 DL with 290 added declarations
and no original OWL axioms removed. This does not establish individual module
profile conformance. HermiT reports consistency and no unsatisfiable named
classes with `ignoreUnsupportedDatatypes=true`; strict mode rejects
unsupported `xsd:date`. OWL RL is not a complete OWL DL consistency proof.
See the [modelling guide](../docs/MODELLING_GUIDE.md) for the three date ranges
and the diagnostic configuration.

WIDOCO generation succeeds with existing configuration/XML parser warnings.
Its optional automated historical changelog cannot fetch the old Connector
and Core version IRIs. Exact local RDF deltas remain available above; no
resolver changes are made to work around that optional remote operation.
External URLs are inventoried rather than exhaustively validated.

No commit, push, merge, tag, release or publication is performed by this
finalization. Successful local gates make a candidate available for human
review; they do not constitute a release or merge approval.
