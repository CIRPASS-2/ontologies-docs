> Historical baseline examples below describe 1.1.2. The October 2026
> adoption is implemented by [TXT-DEC-010](../decisions/TXT-DEC-010.md)
> and the [migration guide](../CORE_2026_MIGRATION.md); policy rules remain in force.

# Nader review of the Textile community candidate

Review baseline: commit `1a88772`, following candidate integration at `ef7695d`.
This record concerns the current repository and its manifest-defined package;
it does not identify the package or revision received by the reviewer.

| ID | Verdict | Evidence and disposition |
| -- | -- | -- |
| NADER-01 | NOT_CONFIRMED | All six MIREOT subsets and `dependencies/soc.ttl` exist and are manifest/checksum-covered. The reviewer's package/revision remains unknown. |
| NADER-02 | PARTIALLY_CONFIRMED | A documentation/clarification question, not a demonstrated mapping defect. Existing CORE class reuse is present; the proposed property/value substitutions are not established. Correct the Indicator explanation only. |
| NADER-03 | NOT_CONFIRMED | No property declaration repeats under the same full IRI across current modules. Repeated local names use distinct namespaces and role-specific domains. |
| NADER-04 | UPSTREAM_RECOMMENDATION | Source-qualified recycled-content declarations are a candidate reusable pattern, subject to CORE/Battery governance. |

## Dependencies and composition evidence

[Dependency documentation](../DEPENDENCIES.md), the
manifest (`PUBLICATION_MANIFEST.txt`), checksums (`SHA256SUMS`) and
catalogue (`catalog-v001.xml`) expose the six actor, dpp, event, mat, si
and soc Textile MIREOT files. The upstream SoC snapshot uses
`https://w3id.org/eudpp/soc#` and declares `0.1.2 DRAFT`; its Textile subset
has its own version `1.1.3`, intentionally included in the community package
whose base label in `VERSION` is `1.1.2`. As documented in README and
[Dependencies](../DEPENDENCIES.md), package and graph versions need not match.
The catalogue maps both the declared `1.1.3` IRI and the legacy `1.1.2` alias
to the current subset; the alias does not retrieve historical bytes.
No missing source or current-package omission was established. The distributed
archive received by the reviewer was not available for comparison.

Textile Core (`ontology/textile-core.ttl`) already makes
`FibreCompositionComponent` a subclass of `dpp:MaterialOfComposition`.
Product-to-entry, entry-to-type and entry-to-value relations have distinct
roles. `hasFibreShare` is absent from the current model and occurs in preserved
Graphwise SHACL outside the current import closure. The current model uses
`hasFibreMassFraction`, illustrated in
example 01 (`examples/example-01-product-composition-v1.1.2.ttl`).
No current ObjectProperty uses `rdfs:subClassOf`.

The [modelling guide](../MODELLING_GUIDE.md) records the type-alignment question,
literal percentage versus structured fraction distinction, and quantitative
property versus value distinction. The Indicator annotation correction does
not alter a class/property axiom. No new mapping, deprecation or IRI change is
introduced. The five namespace-specific `hasTextualValue` properties remain
owned by Assessment, Context, Indicator, Process and Structure.

## Proposed upstream feedback: recycled content by source

Textile Recyclability (`ontology/textile-recyclability.ttl`) links a
product to a `RecycledContentDeclaration`, with a source category and a
structured mass-fraction value. Optional recycled-material mass and reference
product mass provide the numerator and denominator. Assessment results can
verify the declaration independently of the product's recyclability aspect.

The source vocabulary includes post-consumer, pre-consumer and post-industrial
categories. Example 11 (`examples/example-11-textile-recyclability-v1.1.2.ttl`)
illustrates a fraction of 0.30 from 0.075 kg divided by 0.250 kg.
Recyclability SHACL (`shacl/textile-recyclability-shapes.ttl`) checks one
source IRI and one fraction, paired optional masses, matching mass units and
arithmetic consistency. The shared quantitative profile checks fraction bounds
and units. Positive/negative V07/I07 fixtures exercise the declaration pattern.

## WIDOCO Context follow-up

The issue was reproduced and the self-referential ontology-header assertion
was confirmed as the cause of the identity/version defect. Before the fix,
WIDOCO displayed only the incorrect Durability import; after the correction,
the HTML import-list block is absent. Context vocabulary and logical axioms are
unchanged, and all four direct Context imports remain in the RDF
serializations. This HTML behavior remains a separate WIDOCO presentation
issue for investigation.

Possible CORE/Battery adoption requires upstream governance concerning
source-category semantics (including overlap), denominator scope, aggregation
and double-counting. The existing shapes do not establish an exhaustive source
vocabulary or prevent double-counting across declarations. These are questions
for an upstream proposal, not authorization to change CORE or Battery.
The contents, status and compatibility implications of `core#25` cannot be
established from this repository; this record makes no claim about them.

## Remaining decisions

- Identify the package/revision Nader received before diagnosing a distribution omission.
- Ask CORE governance whether Textile fibre concepts should also be `dpp:MaterialType` instances before proposing a type-property alignment.
- Agree the recycled-content source, denominator and aggregation semantics with CORE/Battery owners before adoption.

### Pending SoC/EVENT upstream governance

The current GitHub community candidate integrates the selected upstream SoC
`0.1.2 DRAFT` and EVENT `0.1.0 DRAFT` snapshots. Further upstream changes to
both modules are being developed/reviewed outside this repository. Those
forthcoming revisions are intentionally not integrated yet. Textile should
reassess and update these dependencies only once the upstream revisions are
considered stable, followed by the existing dependency compatibility/reuse
checks described in [upstream dependency governance](upstream-dependency-governance.md).

ACTOR, MAT, EVENT and P_DPP currently use the shared term namespace
`https://w3id.org/eudpp#`; the current SoC snapshot uses
`https://w3id.org/eudpp/soc#`. Moving SoC terms to the shared namespace would
change their actual IRIs, not merely clean up a local prefix. No such migration
is authorized by the current Textile repository. This namespace-governance
question should be resolved upstream when the next SoC version is stabilized;
it does not establish that the current SoC namespace is erroneous.

All six MIREOT subsets, upstream dependencies, Connector, examples and SHACL
remain unchanged by this review implementation. Provenance and namespace
ownership are preserved.
