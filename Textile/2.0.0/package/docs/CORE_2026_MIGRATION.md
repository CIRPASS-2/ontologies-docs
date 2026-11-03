# October 2026 CORE migration — 2.0.0 candidate

The [final reconciliation](../migration/TEXTILE_CORE_2026_FINAL_RECONCILIATION.md)
and OD-01 through OD-06 authorise this breaking migration. The accepted baseline
is preserved independently. The subsequent owner-approved creator update adds
Ivo Ladenius, Andreas Schneider, Jan Merckx and Piero de Sabbata alongside
Elio Hbeich and BOUGACHA Racem on all 13 Textile ontology headers. Release
approval remains separate.

| Existing pattern | Implemented representation |
|---|---|
| Generic chemical identity | TextileChemicalSubstance under CORE Substance |
| Positive SoC context | Existing Textile presence IRI under CORE SubstancePresence |
| Product and substance links | CORE isSubstancePresenceOf / concernsSubstance |
| Applicable qualification | CORE hasApplicableQualification / qualifiesSubstance, same substance |
| Type D | Existing TextileTypeDQualification under SoCQualificationAssertion, explicit CriterionD and appliesToProduct |
| Concentration value wrapper | CORE numericalValue and unit directly on the concentration; range endpoints for ranges |
| Maximum concentration | MaximumConcentration with numericalValue, never maximumNumericalValue |
| Threshold purpose | CORE ThresholdOfSubstanceOfConcern with Textile purpose subclasses |
| Exact/maximum/range thresholds | Textile expression roles under shared txtcon:QuantitativeValue |
| Location/denominator | Textile structured location, part membership, reference basis and reporting level |
| Non-textile component | TextileProductPart, with separate component-material relationship |
| Qualification source | Preserved text plus structured regulatory references, not qualificationNote substitution |
| Handling information | SubstanceManagementInstruction, generic Textile attachment and specific CORE activity edge where justified |
| Unknown identifier scheme | Textile substanceIdentifier text; known schemes use SOC properties |

The [term mapping](../migration/semantic-mapping.csv),
[node correspondence](../migration/node-correspondence.json) and
[extraction scopes](../migration/extraction-scopes.json) supply the detailed inventory.
Concentration-wrapper fields are transferred only for uniquely owned, unambiguous
nodes; shared/external references or conflicting metadata cause a migration error.
For concentration wrappers, old numeric/unit fields map to CORE carriers; for
threshold expressions they map to the shared Textile carriers and local endpoints.

E10 now resides at [example-10-textile-soc-v2.0.0.ttl](../examples/example-10-textile-soc-v2.0.0.ttl).
Its 0.0008 reported mass fraction and 0.001 threshold retain their scales. Its
unknown identifier string is not classified as CAS/EC/ECHA. The anonymous
dimensionless unit is replaced specifically for this mass-fraction use by
massFractionUnit; units:one remains approved. No owl:sameAs equates units.
The old concentration value node becomes its uniquely owning concentration node.
V08 retains range and maximum threshold expressions. I08 retains the same inverted
range at the same focus node; only its migrated shape/message identity changes.

Positive reports entail global SubstanceOfConcern membership through CORE ranges.
This does not propagate CriterionD applicability to another product. Generic
chemicals outside those reports remain Substance without inferred SoC membership.
Material groups are structural reporting objects, not universal products or
material occurrences. CORE isLocatedInProduct is limited to appropriate products.

Partial-report validation retains mandatory product, substance, qualification,
expression/unit and evaluation relationships. Concentration presence is mandatory
only with the separately selected complete-report profile. Shared quantitative
SHACL permits exactly three new threshold roles; ordinary scalar behaviour and
the ban on arbitrary quantity subclasses remain. Units are validated by approved
identities before range inference can mask an arbitrary unit.

Threshold comparison uses compatible mass ratios and the concentration's declared
scope through its applicable-threshold relation. Explicit threshold scope overrides
must match. Maximum-only mass-fraction intervals are [0, maximum]; overlapping
intervals are indeterminate. Below/above/equal outcomes do not establish compliance.
See [TXT-DEC-010](decisions/TXT-DEC-010.md).

## Historical compatibility and rollback

The original 648-file archive and inventory are unchanged. Historical version
IRIs and lowercase SOC are intentionally absent from the active catalogue.
For a historical load, select `migration/historical/1.1.2/catalog-v001.xml`
as the only catalogue for the entire session, disable network fallback, and
load `https://w3id.org/eudpp/textile-ontology/1.1.2` or
`https://w3id.org/eudpp/textile-soc/1.1.2`. Do not combine catalogues or load
current and historical versionless identities into the same ontology manager.
The historical catalogue also resolves SoC MIREOT 1.1.3 and its 1.1.2 alias.
The offline `catalogue_import_closure` helper in `scripts/validate_public.py`
fails on missing imports rather than consulting another catalogue or the network.
The archive also contains original examples, documentation and WIDOCO output.

Changed graphs receive new identities. Unchanged modules and SI retain their
accepted non-creator RDF and versions; their creator metadata is now updated.
The active runtime contains no legacy SOC semantic
terms or imports; historical IRIs occur only in source/provenance annotations.
It has no IDENT/COMP/LCA dependency. Removed unused P_DPP anchors and obsolete EVENT
restrictions are not recreated as Textile constraints.

## Validation and approval boundary

The regression suite retains eleven examples, sixteen original SHACL scenarios,
six reasoning scenarios and the recyclability control. Forty-one additional migration
scenarios check exact constraint identities, positive focus coverage, semantic
preservation and non-entailments. Source fidelity and historical/source hashes
are tested separately. This is bounded profile/inference evidence, not a proof
of complete OWL DL satisfiability or legal applicability.

The provisional candidate identity is 2.0.0. The separate creator-metadata task
is implemented under explicit owner approval. Final release numbering and
publication still require owner approval. Nothing
in this migration authorises a push, merge, tag or publication.

Owner-approved Option B gives all thirteen current Textile graphs distinct
2.0.0 version identities. Assessment, connector, context, core, durability,
indicator, process, repairability and structure now cite their historical 1.1.2
IRIs through owl:priorVersion. Only the byte-unchanged SI MIREOT retains 1.1.2.
Selecting a historical version endpoint requires the historical catalogue,
which resolves the complete original closure. Local file loading alone is not
historical resolution. See the resolver coordination brief for the separate
immutable version routes and current versionless aliases.

The converter is bounded to supported positive reports. Unknown legacy resources
(including identity properties whose semantics have not been reconciled) require
manual review. It preserves RDF literals verbatim. Quantitative-wrapper mappings
are context dependent and must complete the checked field-transfer stage; the
mapping inventory does not assert equivalences. Bare or incomplete legacy
presences are rejected before projection.
