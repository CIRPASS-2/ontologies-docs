# Final creator metadata update for Textile 2.0.0

Baseline: correction commit `f527fc577bec246a25d9332df018be6a64ec9070`, branch
`migration/october-2026-core-2.0.0`. This task implements the owner's explicit
creator decision and subsequent approval of documentation-export normalization.

## Creator metadata and canonical RDF comparison

All 13 Textile ontology headers previously listed Elio Hbeich and BOUGACHA Racem.
All now list those two existing creators plus Ivo Ladenius, Andreas Schneider,
Jan Merckx and Piero de Sabbata, as English language-tagged `dcterms:creator`
literals. Existing values, spellings and creator representation are preserved.
There are six distinct creator values per header and no duplicate values.
The original order of existing values and every other source byte are preserved.

The canonical change is exactly **52 added creator triples**, with no removed
triples and no other metadata or semantic RDF changes. Each before/after graph
is isomorphic after removing only the four added creator statements. No
documentation annotations were excluded from the comparison. Classes,
properties, individuals, restrictions, hierarchies and imports remain unchanged.
[Comparison evidence](creator-update-results.json) records the baseline,
before/after creators, per-module results and canonical non-creator graph hashes.
A regression verifies those hashes without requiring Git.

The candidate stays **2.0.0**. Existing module version identities are unchanged;
metadata additions do not automatically allocate new module versions.
Copyright, licences and third-party source attribution are unchanged.

## WIDOCO documentation and approved export normalization

All twelve documented modules were regenerated with the existing WIDOCO script
and canonical download synchronization mechanism. The network landing page now
derives its creator list from the root ontology. README and current migration
guidance describe the completed creator decision.

Before this task, nine modules' XML, N-Triples and JSON-LD downloads were not
graph-isomorphic to their canonical sources. The owner explicitly approved
normalizing those 27 exports within this task. Canonical ontology source graphs
were not changed to accommodate serializer behavior.

[Exact export differences](creator-export-differences.json) lists every checked
file, original/final byte hashes, original/final source-isomorphism results and
every non-creator added/removed canonical RDF triple. Removed serializer-added
declarations are distinguished from other export triples, including anonymous
list serialization differences. Blank-node labels are local to each comparison;
list reordering can make a graph difference larger than the corresponding OWL
expression difference. These are documentation-export changes, not changes to
canonical ontology axioms. They are reported explicitly rather than excluded
from the canonical creator-only comparison.

All **48 exports** (12 modules x four RDF formats) are now graph-isomorphic to
their corresponding canonical sources. Turtle downloads remain byte-identical
to source. The normalized modules are assessment, connector, context, core,
durability, indicator, process, repairability and structure. Associated-materials,
recyclability and SOC exports were already canonical and require creator-only
RDF updates.

Across the 27 normalized files, the recorded non-creator differences remove
1,301 serializer-added declaration triples and 508 other export triples, and
add 495 export triples. These are per-file totals, not counts of distinct
ontology resources. The JSON evidence contains every triple in each category.

The twelve WIDOCO provenance Turtle graphs also receive the directly required
creator-derived agent names and attribution links, including generated agent
renumbering. Their exact differences are recorded separately in the same JSON.
After excluding only those creator-related documentation annotations, each
provenance graph is isomorphic to its baseline; tool attribution, dates and all
other documentary statements remain unchanged.

## Validation, integrity and release boundaries

The existing creator regression now checks preservation plus the approved
additions. The other original regression cases retain their expectations.
WIDOCO coverage expands from three to twelve modules and a new regression
enforces the creator-only source comparison. Results are recorded in
[validation results](validation-results.json) and [pytest XML](validation-pytest.xml).

The full suite passes **174 tests**, preserving the original 164 cases with the
creator expectation updated for this approved decision and adding ten cases for
broader export coverage and the creator-only graph invariant. Both partial and
complete-report public validation modes pass: 11 examples, 16 original SHACL
scenarios, six reasoning scenarios and the inference negative control per mode.
All 41 migration scenarios pass. The twelve pytest warnings are the existing
RDFLib JSON-LD parser deprecation warning, one per documented module.

The current runtime remains the same 20-graph closure. Both public validation
modes cover 11 examples, 16 original SHACL scenarios, six reasoning scenarios
and the recyclability inference negative control. All 41 previous migration
scenarios and historical closure/source-fidelity checks remain regression gates.
Historical files and catalogues, CORE/SI sources, MIREOTs, SHACL and examples
are outside the update and remain byte-identical to the baseline.

[Exact changed files](creator-update-files.txt) enumerates every path changed
from the correction commit, including generated assets and integrity records.
The publication manifest and SHA-256 contract are recomputed after recording
the final results.

Remaining steps are owner approval of the provisional release version and
candidate, followed by separately authorized tagging/publication or other remote
actions. No push, merge, tag or publication is part of this task. Documentary
source verification and the previously documented profile limitations are
unchanged by this metadata update.
