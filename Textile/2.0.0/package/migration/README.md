# October 2026 CORE migration — 2.0.0 candidate

Implemented on `migration/october-2026-core-2.0.0`, continuing preparation commit
`287d4d5cf90f0a5175986f0563a87495ea498add`. The accepted historical baseline is
`1ca2aa89241785dedeab430247bc9947daf69881`. No reset or archive recreation occurred.

The complete [final reconciliation](TEXTILE_CORE_2026_FINAL_RECONCILIATION.md)
supplies M1–M9, A1–A9 and OD-01 through OD-06. Its actual supplied filename is
retained. See [implementation guidance](../docs/CORE_2026_MIGRATION.md),
[term mappings](semantic-mapping.csv), [concentration node correspondence](node-correspondence.json)
and [bounded source selections](extraction-scopes.json).

## Historical preservation

The original 648-file archive is unchanged:
`historical/textile-1.1.2-1ca2aa89241785dedeab430247bc9947daf69881.zip`.
SHA-256: `4384bfd9f8f4e8a0ce1a6b7a7fd679d2190d9be33df87b2f181207aa78a46e74`.
`historical/inventory.json` records every member digest. Exact historical runtime
files and catalogue are extracted under `historical/1.1.2/`. They remain outside
the active closure. Previous version IRIs and lowercase SOC are absent from the active catalogue;
historical loading requires its own catalogue for the complete session. E10's original versioned file
is in the archive; the active E10 has a 2.0.0 filename.

Migration inputs, implementation records, historical preservation and WIDOCO
sources now participate in the candidate manifest/checksum inventory. Their
inclusion does not make historical/source graphs runtime dependencies. The
unpacked Graphwise reference copies remain excluded; the immutable archive
preserves them. Source staging remains byte-identical to the owner-designated
CORE and to adopted files in `dependencies/current-core/`.

## Implementation and gates

1. Branch and identity preservation: original preparation retained, historical
   hashes checked, six faithful bounded CORE subsets plus unchanged SI.
2. Semantic migration: Textile identity/presence alignment, retained source,
   location/denominator, instruction and threshold/evaluation semantics; E10 and
   V08/I08 migrated. No legacy SOC semantic term or import remains in active RDF; provenance
   annotations explicitly identify historical source resources.
3. Validation: separate partial/complete profiles, stable named constraints and
   strict multiset matching, forty-one additional scenarios, positive focus coverage,
   entailment/non-entailment tests and unchanged-purpose regressions.
4. Publication consistency: affected documentation, deterministic traceability,
   four SVG/PNG diagrams and three WIDOCO modules regenerated. Canonical RDF
   downloads are synchronised across TTL/RDFXML/NT/JSON-LD. Manifest and SHA-256
   cover the candidate and preserved historical archive.

The final check results and complete change inventory accompany the local commit.
The original baseline passed 30 package tests, eleven examples, sixteen SHACL
scenarios, six reasoning scenarios and the recyclability inference control.

Issues found and corrected during implementation:

- Missing SOC endpoint declarations were caught by the wrong maximum-carrier
  inference test. The authoritative properties are now included faithfully.
- Invalid-unit fixtures also fail comparison compatibility. Their contracts
  explicitly require both diagnostics rather than allowing arbitrary extras.
- The two-product shared-qualification control reports both affected presences
  for a wrong substance. Its contract requires both exact focus/constraint pairs.
- pySHACL ontology inoculation recursively cloned linked metadata. Explicitly
  merging the same offline closure avoids that copying without dropping axioms.
- WIDOCO's independent RDF exporters added differing declaration triples.
  Canonical RDF download synchronisation and graph-isomorphism tests correct this.

Unchanged upstream snapshots retain their whitespace. WIDOCO reports missing
optional configuration/logging and XML parser-property warnings but exits
successfully. The installed RDFLib JSON-LD parser emits a deprecation warning.
Initial pytest sandbox runs required approved access to temporary directories.
No substantive semantic conflict remains unresolved.

## Reproduction

The preparation script is retained for provenance and need not be rerun.
`implement_core.py 1` rebuilds bounded subsets and verifies historical extraction
without changing the archive; `implement_core.py 2` rebuilds Textile/data mappings.
Then run the `migration.build_soc_shapes`, `migration.update_validation_contracts`
and `migration.build_semantic_cases` modules. `migration.refresh_publication`
refreshes documentation/traceability; its `--integrity` mode refreshes the manifest
and checksums. PowerShell scripts regenerate diagrams and WIDOCO output.

The candidate version is provisional 2.0.0. Creator metadata is unchanged.
Final numbering, the separate approved creator task and publication remain owner
decisions. No push, merge, tag or publication has occurred.

## Targeted independent audit corrections

Continue from accepted implementation `5bac1a2` using the bounded correction
script `python -m migration.correct_audit`, rather than rerunning migration
stages. The [correction matrix](AUDIT_CORRECTIONS.md) records all findings,
counterexamples, historical closures and validation evidence.
