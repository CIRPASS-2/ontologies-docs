# Source traceability methodology

The public traceability layer consists of [resources](../traceability/textile-resource-traceability.csv), [evidence](../traceability/textile-resource-evidence.csv) and [source documents](../traceability/source-documents.csv). The historical internal Excel workbook is NOT part of this initial public package. It served only as reconciled resource-level evidence input; its release metadata, MIREOT counts and validation summaries are not publication authority.

## Public universe

Rows are derived from the current packaged Textile ontology graphs: one per Textile-controlled named semantic subject, excluding blank nodes, ontology headers and externally owned subjects. `rdfs:isDefinedBy` identifies the defining module. Cross-module mentions do not create duplicate rows. Missing evidence never causes a current resource to disappear.

## Categories

| Category | Meaning |
|---|---|
| directExtraction | The term and intended meaning occur directly in the identified source context. |
| adaptedDefinition | A controlled paraphrase supported by the cited source context. |
| adaptedRelation | An ontology formalisation of a relationship expressed or structurally implied by the source. |
| modellingAbstraction | A construct organising source-supported information; not a claim of a verbatim source term. |
| projectDecision | A resource defined by the ontology specification rather than extracted from JRC. |
| externalReuse | A resource or semantic commitment reused from an external ontology. |

## Documentary locators and project decisions

Every source location belongs to an evidence row and an identified source document. Recorded sections and pages are extracted only when their association is defensible. Compound citations are retained, and uncertain decomposition remains explicit. Documentary locators are references to source publications, not local copies of those publications.

Project decisions and modelling abstractions keep their categories even when motivated by JRC material. Public ADR links occupy the resource-level modelling-decision field. A public ADR explains project rationale and is not a JRC document.

## Verification and limits

COMPLETE denotes completeness of the recorded representation, not a finding that every source interpretation is verified. PARTIAL exposes preserved compound citations or unresolved relationships. PRESENT_NOT_REVERIFIED preserves a recorded locator without claiming a fresh source review; UNRESOLVED exposes a source without an attributable location. No evidence row is declared VERIFIED by this preparation. Numerical-range and CSV checks are not substantive source validation.

The six categories and both source studies must be read separately: JRC motivation does not make a project abstraction a direct extraction. [Traceability guidance](../traceability/README.md) defines all fields, statuses, evidence IDs and the precise projection limits.

## JRC source basis

The December 2025 JRC Textile Preparatory Study is a broad technical source for textile products, fibres, structures, processes, durability and testing. The May 2026 DPP-content study has a narrower scope concerning proposed apparel-DPP information. Absence from its tables does not establish absence of a JRC basis in the broader study. The later study does not supersede the entire earlier technical basis. Proposed content must not automatically be described as legally mandatory. Project modelling decisions remain distinct from JRC-derived statements.


## Seven publication locator supplements

The [locator-resolution table](../traceability/evidence-locator-resolutions.csv) records exactly seven explicit supplements: five EVENT term locators and two ESPR provisions. The original evidence ID, resource and source document identify each missing-locator relationship. The validator applies a supplement only to that unresolved relationship and recomputes its deterministic evidence ID. It rejects duplicate resolutions or a change of resource/source identity. RDF bytes, source categories, source-document identities and resource/evidence counts remain unchanged.

The supplements provide attributable locations; they do not claim full semantic re-verification. Their status is PRESENT_NOT_REVERIFIED and their verification basis records the public-locator check on 2026-09-11. EVENT locations name classes in the public upstream EVENT 0.1.0 DRAFT graph, connected through the source registry's upstream reference. The local Textile EVENT MIREOT IRI is not represented as a confirmed dereferencing endpoint. Regulatory locators support only the cited regulatory aspect of the Textile adaptation.

Exactly two relationships remain UNRESOLVED: `textile-soc#fibreCompositionLocation` and `textile-soc#nonTextileComponentLocation` against EU-2024-1781. Article 7(5)(b) addresses location generally and is not substituted as category-specific evidence. There are 944 PRESENT_NOT_REVERIFIED rows, two UNRESOLVED rows and zero VERIFIED rows. Resource-level PARTIAL states are conservatively retained from the original annotation projection; locator supplements do not erase its recorded limitations.

## October 2026 migration

Local modelling decisions are documented in [TXT-DEC-010](decisions/TXT-DEC-010.md).
Forty-two resources with copied historical SOC definitions/comments are classified
as adaptedDefinition and attributed to SOC 0.1.2 DRAFT and their exact source
resources. Local scope/alignment decisions remain separately annotated.
The projection contains 899 resources and 946 evidence rows:
the original 904 relationships plus 42 historical SOC citations, all remaining
PRESENT_NOT_REVERIFIED except the two unchanged UNRESOLVED relationships. Source registry
descriptions identify the adopted MAT 1.1.0 and EVENT 1.0.0 subsets. The seven
earlier locator supplements remain historical evidence statements; the migration
does not claim fresh documentary verification. The presence locator names the
current SubstancePresence pivot while retaining its ESPR source relationship.
