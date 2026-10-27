# Migration stage checks

Preparation commit: `287d4d5cf90f0a5175986f0563a87495ea498add`.
Branch: `migration/october-2026-core-2.0.0`. Candidate: provisional **2.0.0**.

## Stage 1 — identity and source fidelity

The pre-existing historical archive was neither recreated nor modified. All 648
member digests and the archive digest are checked. Extracted historical runtime
bytes match the archive. Adopted current CORE sources match their staged originals
byte for byte. Six bounded subsets reproduce the complete selected source
subgraphs, including anonymous axioms, under graph-isomorphism checks. The current
20-graph closure excludes legacy SOC, IDENT and unrelated CORE dependencies.

## Stage 2 — semantic and instance preservation

E10 retains 0.0008 concentration, 0.001 threshold, unknown-scheme identifier,
material-group denominator, reporting level, analytical method, qualification
source and instruction text. The old concentration-wrapper node is recorded in
node-correspondence.json. Its old versioned example bytes remain in the archive;
the active example has a v2.0.0 filename. V08 retains range/maximum thresholds;
I08 retains the original reversed threshold range and focus node.

Core ranges intentionally entail SubstanceOfConcern for positive reports.
Generic chemicals do not acquire that type by default. Criterion-D applicability
does not propagate to the second product's presence. Generic groups/components
acquire neither Product nor MaterialOfComposition; the existing fibre-composition
bridge retains its specific material specialisation. Process executions do not
acquire ProductEvent, and thresholds/expressions do not acquire concentration type.
Creator metadata remains unchanged on every Textile module.

## Stage 3 — profiles and regressions

The original baseline passed 30 package tests and the full 11-example,
16-scenario, six-reasoning-scenario regression suite. The migrated regression
suite passes with strict multiset matching. Both positive partial and complete
profiles pass; a missing concentration fails only when complete-report is selected.

Forty-one additional scenarios check precise focus, named property/SPARQL shape,
constraint component, result path, severity and specific source constraints.
Every targeted SoC node shape has positive focus coverage and a discriminating
negative. Old anonymous property shapes retain container/path matching. Duplicate,
wrong-focus and wrong-constraint results cannot satisfy expectations.
Four direct converter controls additionally verify safe provenance transfer and
explicit conflicts for shared wrappers, external identity links and incompatible
metadata. Those guards raise migration conflicts without depending on Python
assertions or creating owl:sameAs bridges.

Failures caught and corrected during development are retained here:

- The initial extraction missed the two concentration range endpoint properties.
  The maximum-carrier/disjointness control failed until those source axioms were
  included; expected inference and constraint results were not weakened.
- Invalid unit fixtures produce both unit-identity and evaluation-compatibility
  violations. Their contracts now require those two exact diagnostics.
- Expanding the shared qualification fixture to two products yields two affected
  focus nodes when its substance is wrong. Both are explicitly required.
- pySHACL's recursive ontology inoculation was avoided by merging the same full
  offline ontology graph before RDFS processing. No axioms were discarded.
- The baseline pytest sandbox temporary-directory errors disappeared in the
  approved filesystem environment; the original tests themselves passed.

## Stage 4 — publication consistency

Three affected WIDOCO modules and the network landing page are regenerated.
Canonical TTL bytes match source; RDF/XML, NT and JSON-LD downloads are graph
isomorphic to the same source. Four SVG/PNG views are regenerated and their
source inventory is recomputed. The traceability projection has 899 resources,
904 evidence rows, five source documents, 902 PRESENT_NOT_REVERIFIED and two
UNRESOLVED relationships; no fresh documentary verification is claimed.

The candidate manifest includes migration authority, reproducibility inputs,
historical preservation and WIDOCO sources without importing those reference
graphs into runtime. Final machine-readable results are in validation-results.json
and validation-pytest.xml. Complete path/status inventory is in change-inventory.json.

WIDOCO's differing native RDF exports were corrected by canonical synchronisation.
Non-fatal optional configuration/logging/XML-property warnings and the installed
RDFLib JSON-LD deprecation warning are recorded, not treated as semantic failures.
Upstream and historical whitespace remains untouched. Changed candidate text uses
LF endings; creator and authoritative source bytes remain protected.
Two multiline CON comment lines also retain their source-literal trailing spaces;
removing them would fail exact selected-source graph comparison. The authored
whitespace check excludes those copied literals, authoritative snapshots,
historical bytes and the verbatim owner specification.

No substantive semantic conflict remains. Final release numbering, the separate
creator task and publication remain owner decisions. No push, merge, tag or
publication has occurred.

## Final recorded result

111 tests passed, with three RDFLib deprecation warnings. The public complete-report
run passed all eleven examples, sixteen original SHACL scenarios, six reasoning
scenarios and the recyclability control. Forty-one migration scenarios comprise
four positive and thirty-seven negative cases. All sixteen targeted SoC shapes
(including the optional complete profile) have positive and negative coverage.

## Post-audit corrections

The preceding stage counts describe accepted implementation `5bac1a2`. The
current [audit correction matrix](AUDIT_CORRECTIONS.md) and machine-readable
validation results supersede those counts. Traceability now has 946 rows and
six sources, with 944 PRESENT_NOT_REVERIFIED and the same two UNRESOLVED rows.
Historical aliases require the historical catalogue for the complete load.
