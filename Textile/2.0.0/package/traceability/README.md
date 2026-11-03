# Resource traceability

The CIRPASS Textile Ontology is grounded in the JRC textile studies while explicitly distinguishing direct extraction, adapted source content, modelling abstractions, project decisions and external reuse.

## Tables and relationships

- [Resource table](textile-resource-traceability.csv): one row per named Textile-controlled semantic resource.
- [Evidence table](textile-resource-evidence.csv): one row per safely attributable resource, source document and source location. An identified source with no attributable locator has an explicit unresolved row.
- [Source registry](source-documents.csv): source identities, public references and scope.

```text
Resource 1 --- 0..N Evidence N --- 1 SourceDocument
```

The universe is derived from named subjects in the 13 Textile graphs whose IRI begins with `https://w3id.org/eudpp/textile-`, excluding `owl:Ontology` headers. Blank nodes and externally owned MIREOT subjects are excluded. Each term's `rdfs:isDefinedBy` selects its module, including terms mentioned in other modules. Classes, properties (including annotation properties), concept schemes, concepts and other named semantic resources are retained. More specific SKOS types take precedence over the generic NamedIndividual display type; genuine multiple semantic types are separated by ` | `.

## Provenance categories

| Category | Meaning |
|---|---|
| directExtraction | The term and intended meaning occur directly in the identified source context. |
| adaptedDefinition | A controlled paraphrase supported by the cited source context. |
| adaptedRelation | An ontology formalisation of a relationship expressed or structurally implied by the source. |
| modellingAbstraction | A construct organising source-supported information; not a claim of a verbatim source term. |
| projectDecision | A resource defined by the ontology specification rather than extracted from JRC. |
| externalReuse | A resource or semantic commitment reused from an external ontology. |

## Source evidence and modelling rationale

Current `sourceType`, `sourceLocator` and `dcterms:source` annotations drive the baseline projection, followed by the seven explicit documentary supplements below. The publication preparation reconciled resource-level supporting catalogue evidence against these annotations; historical release counts and validation claims are not used.

Public modelling documents appear in `modelling_decision_locator` and resolve relative to the package root. They are not JRC sources and do not count as external evidence. The project specification source is likewise excluded from external-evidence counts. Its original modelling references remain in the ontology annotations. Resources with mixed JRC and project support retain their original category.

External MIREOT subjects are not duplicated as Textile resources. The Textile-controlled externalReuse resource identifies MAT semantics. A JRC fragment within its historical compound locator is not reassigned to a JRC source when the resource's explicit source annotations identify only MAT; this limitation is retained in its notes and PARTIAL status.

`has_jrc_evidence` is TRUE exactly when a linked evidence row references a source registry entry of type JRC. It means a recorded source association, not verified substantive support. Source links are taken from explicit source annotations, not inferred from provenance category or a generic mention of JRC.

## Multiplicity and compound citations

A source field is never paired with an unrelated page or section. Splitting occurs only at explicit documentary boundaries. Documentary fragments remain verbatim; separable fragments may share a source document. A fragment containing multiple locations remains intact with empty scalar section/page fields and `COMPOUND_CITATION_PRESERVED` in notes. Unassignable supplementary context remains in the public ontology annotation and prevents a COMPLETE status. Nothing is assigned to another source merely to fill a column.

## Status meanings

Evidence statuses:

- VERIFIED: applicable source-locator verification has been established and attributed to this evidence relationship. No rows in this candidate claim this status.
- PRESENT_NOT_REVERIFIED: a recorded documentary locator is preserved; this task has not independently revalidated its substantive interpretation or source-page resolution.
- UNRESOLVED: a source relationship is recorded but lacks a separately attributable locator.
- NOT_APPLICABLE: no locator is applicable; reserved and unused in this candidate.

`verification_basis=not_reverified_for_publication` records the scope of this publication projection. Machine checks verify representation, identifiers, foreign keys, recorded numeric ranges and package links. They do not prove source meaning, printed-page resolution, or exhaustive evidential support. Older whole-resource verification labels are not promoted to VERIFIED on newly split evidence rows because their applicability to every individual source-location relationship has not been established.

Resource statuses:

- COMPLETE: the explicitly recorded external relationships have attributable locators that fit the projection without omitted or compound context. This is representation completeness, not semantic verification.
- PARTIAL: a compound citation, unresolved source relationship or unnormalised historical modelling/domain reference remains. Original context is retained in the ontology.
- NO_EXTERNAL_SOURCE_REQUIRED: the recorded source is the project specification with a public ADR or an explicit project-specification reference; no external evidence row is asserted. This does not make a universal claim about all possible source obligations.
- UNRESOLVED: reserved for missing resource-level evidence; unused here.

## Deterministic evidence identifiers

Each ID is `EVID-` followed by the first 16 lowercase hexadecimal characters of SHA-256. The hashed bytes are a canonical JSON array of five strings in this exact order: `resource_iri`, `source_document_id`, `source_locator`, `source_section`, `source_page`. JSON uses UTF-8, `ensure_ascii=False`, compact comma/colon separators and no trailing newline. No Unicode or locator-content normalization is applied. IDs therefore do not depend on row order. The validator checks full regeneration and exposed-ID uniqueness; collisions fail validation and require a longer exposed digest.

## JRC source scopes

The December 2025 JRC Textile Preparatory Study is a broad technical source for textile products, fibres, structures, processes, durability and testing. The May 2026 DPP-content study has a narrower scope concerning proposed apparel-DPP information. Absence from its tables does not establish absence of a JRC basis in the broader study. The later study does not supersede the entire earlier technical basis. Proposed content must not automatically be described as legally mandatory. Project modelling decisions remain distinct from JRC-derived statements.

## Reproduction and limitations

Run `python -B scripts/validate_public.py` from the package root. The validator derives the three tables again from packaged RDF plus the locator supplements and compares every row, then checks CSV structure, source/resource links, counts, public ADR paths, the file manifest and hashes. `--full` adds the declared SHACL and reasoning checks. Neither the source documents nor the historical Excel workbook are distributed. Public references identify them without reproducing their text. Historical specification version labels in documentary locators are preserved as source references, not current release metadata.

The tables contain 899 resources, 946 evidence relationships and 6 source documents. 301 resources have no external evidence rows; 248 have multiple evidence rows. 549 resources have a recorded JRC source association.


## Seven publication locator supplements

The [locator-resolution table](evidence-locator-resolutions.csv) records exactly seven explicit supplements: five EVENT term locators and two ESPR provisions. The original evidence ID, resource and source document identify each missing-locator relationship. The validator applies a supplement only to that unresolved relationship and recomputes its deterministic evidence ID. It rejects duplicate resolutions or a change of resource/source identity. RDF bytes, source categories, source-document identities and resource/evidence counts remain unchanged.

The supplements provide attributable locations; they do not claim full semantic re-verification. Their status is PRESENT_NOT_REVERIFIED and their verification basis records the public-locator check on 2026-09-11. EVENT locations name classes in the public upstream EVENT 0.1.0 DRAFT graph, connected through the source registry's upstream reference. The local Textile EVENT MIREOT IRI is not represented as a confirmed dereferencing endpoint. Regulatory locators support only the cited regulatory aspect of the Textile adaptation.

Exactly two relationships remain UNRESOLVED: `textile-soc#fibreCompositionLocation` and `textile-soc#nonTextileComponentLocation` against EU-2024-1781. Article 7(5)(b) addresses location generally and is not substituted as category-specific evidence. There are 944 PRESENT_NOT_REVERIFIED rows, two UNRESOLVED rows and zero VERIFIED rows. Resource-level PARTIAL states are conservatively retained from the original annotation projection; locator supplements do not erase its recorded limitations.
