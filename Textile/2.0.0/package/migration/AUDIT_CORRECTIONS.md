# Targeted corrections following the independent audit

Review source: the owner's complete Claude final independent audit of accepted
implementation `5bac1a2cba2332b3e5ad7d45d305fbb786ee59f2`, verdict
ACCEPT_WITH_CORRECTIONS, supplied in this task. Branch:
`migration/october-2026-core-2.0.0`. No migration restart or historical regeneration.

| Finding | Before | Correction and evidence |
|---|---|---|
| MAJOR-01 historical closure | Historical entry aliases resolved versionless imports through the active catalogue. | Active historical aliases removed, including unchanged modules' old endpoints. The standalone historical catalogue resolves all imports in isolation. Full closure tests and an independent traversal record per-file original hashes. |
| MAJOR-02 attribution | 42 copied definitions/comments classified only as project decisions, without external evidence. | Independently compared both accepted and corrected graphs with SOC 0.1.2 DRAFT. Exact IRIs and matching statements recorded. Resources now have adaptedDefinition, historical dcterms:source and prov:wasDerivedFrom, alongside project source and local modelling notes. CC BY 4.0 attribution restored. |
| MAJOR-03 membership | Inverse axiom absent; only forward hasPart paths accepted. | Restored inverse. Membership follows `(hasPart|^isPartOfProduct|hasNonTextileComponent)+`. Forward/inverse/component positives and different-product negatives cover locations and denominators. RDFS/OWL checks preserve structural types. |
| MINOR-01 mapping | 61 of 96 old resources; threshold mappings looked unconditional. | All 96 historical MIREOT resources have classifications, including retired terms and inverses. Eight additional concentration-context alternatives distinguish carriers and field transfer. No equivalence assertions. |
| MINOR-02 converter | Unknown names became undeclared local IRIs; literals rewritten; legacy presence could become untargeted CORE presence. | Enumerated supported mapping only; unknown identity properties/resources fail for manual review. Literals preserved. Positive presence types target Textile shapes, and incomplete legacy contexts fail preflight. Quantitative wrapper edges remain transient and undergo checked transfer. |
| MINOR-03 evaluation | Cross-presence evaluation accepted. | EvaluationOwnership requires every attached presence to own the evaluated concentration. CE6 is a discriminating negative regression. |
| MINOR-04 E10 | Disclaimer and percentage explanations absent; unused dimensionless node retained. | Restored disclaimer and 0.08%/0.1% explanations. Removed the unit declaration from E10 and V09 only after confirming no incoming references. Values, qualifications, identifiers, thresholds and scopes remain. |
| MINOR-05 metadata | Mechanical duplicate labels and missing descriptions; scope property name ambiguous. | Removed redundant camelCase labels only where a descriptive English label exists. Added bounded model-derived descriptions to all previously undescribed new resources. Kept the public appliesToProduct IRI, labelled it qualification-specific and documented its distinct domain from the CORE homonym. |
| MINOR-06 domains | Both criterion-specific basis properties had a common qualification domain without explanation. | Product-group-list domain restored to TextileTypeDQualification. SVHC-list common CORE domain explicitly retained; SHACL requires explicit CriterionA. Tests cover criterion applicability and OWL domain/criterion effects. |
| MINOR-07 coverage | Per-shape coverage overstated constraint-level evidence. | Added qualification-substance/criteria, owner-product, evaluation applicability/ownership, criterion-specific basis, all threshold-expression units and all expression exclusion negatives. Original strict result contracts remain. Coverage limits below. |
| MINOR-08 CON | Unused concernsProduct/ProductEvent; omitted instruction superclass. | Removed unused concernsProduct root and its ProductEvent declaration. Selected complete CON SubstanceManagementInstruction description and DigitalInstruction support. All selected subgraphs still compared isomorphically with untouched CORE. |
| Informational serialization | Associated-materials prefixes missing. | Restored txt and txtamcs prefixes for readable source and downloads. Semantic change is only its new structural-part description. |

The M04 partial/complete fixtures now detach their dependent evaluation when
removing concentration. This preserves their concentration-completeness purpose
and exact expected result multisets. Their previous dangling evaluation is
separately represented by CE6; the ownership check is not disabled or weakened.

## Before/after counterexamples

`audit_counterexamples.py` loads the accepted files using read-only `git show`
and the corrected files directly, using all Textile modules, all MIREOTs and all
three structural profiles. It reproduces Claude's exact CE6/CE7/CE8 mutations.

| Counterexample | Accepted candidate conforms | Corrected candidate conforms |
|---|---:|---:|
| CE6 cross-presence evaluation | true (defect) | false: EvaluationOwnership |
| CE7 inverse part membership | false (defect) | true |
| CE8 canonical non-textile zipper location | false (defect) | true |

Exact results: [counterexample evidence](audit-counterexample-results.json).

## Historical and provenance evidence

Historical root closure: 19 graphs. Historical Textile SoC closure: 12 graphs.
Historical SoC MIREOT 1.1.2 and 1.1.3 aliases: one graph each. Every closure
declares the original 96 SOC resources, contains no CON MIREOT or 2.0.0 graph,
and every resolved file matches the original per-member inventory digest.
See [independent closure evidence](historical-closure-results.json).
The archive SHA-256 remains
`4384bfd9f8f4e8a0ce1a6b7a7fd679d2190d9be33df87b2f181207aa78a46e74`.
Consumer instructions are in [migration guidance](../docs/CORE_2026_MIGRATION.md).

[Accepted-commit attribution evidence](attribution-baseline-evidence.json)
records all 42 source-free project classifications and exact matching statements
before correction. [Corrected attribution inventory](legacy-soc-attribution.json)
records exact historical resource IRIs, statements and text hashes. No source
document, JRC locator or legal interpretation was invented or promoted to verified.

The corrected projection has 899 resources and 946 evidence rows: the original
904 relationships plus 42 SOC citations. All 944 located relationships remain
PRESENT_NOT_REVERIFIED; the two original UNRESOLVED relationships are byte-for-byte
identical as CSV records. The 42 newly cited resources are conservatively PARTIAL
because their locators retain both historical text attribution and local adaptation
context. Zero-evidence resources decrease from 343 to 301.

## Validation and limits

The full suite passes **164 tests**, including the original 111 regressions.
Both partial and complete-report public modes pass.

Machine-readable results are in [validation results](validation-results.json)
and [pytest report](validation-pytest.xml). All 41 previous migration scenarios
retain strict expected result multisets. Both public validation modes exercise
11 examples, 16 original SHACL scenarios, 6 reasoning scenarios and the
recyclability inference negative control. Source fidelity, historical bytes,
unchanged creators and WIDOCO RDF equivalence are regression gates.

Constraint coverage is targeted, not claimed to be 100%. The existing 41 scenario
contracts still select the SoC profile as documented; new audit regressions use
all structural profiles and the full runtime closure. Exact concentration dispatch
uses a SHACL-AF SPARQL target and requires advanced support. Under RDFS, endpoint
properties can infer a range type before exact-expression exclusion constraints
run; endpoint defects are also checked by range and disjointness constraints.
No attempt is made to force unreachable constraint carriers to fire.

Candidate numbering remains provisional 2.0.0. The remaining limits are documented
engine/profile scope and documentary verification limits, rather than unresolved
semantic conflicts. Subject to passing recorded checks, the targeted corrections
support owner release review. This work does not authorize publication, the
separate creator decision, or any remote Git action.
