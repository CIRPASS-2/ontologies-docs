# CIRPASS-2 Textile — Final CORE 2026 semantic reconciliation specification

**Status:** Reconciliation report reproduced from the completed Codex analysis. The owner decisions below were subsequently supplied for implementation. This document is the migration semantic specification, not evidence that migration has been implemented.

**Owner decisions (subsequent implementation authorization):**

- **OD-01 (Criterion D):** Adopt current CORE SOC 2.2.0 semantics for positive SoC presence reports, including the inferred `SubstanceOfConcern` typing; qualification applicability must remain product/presence-context specific. Generic non-SoC textile chemicals are not to be globally qualified by default.
- **OD-02 (Completeness):** A concentration is mandatory only for a separately designated *complete-report* SHACL profile, not for every partial Textile SoC presence.
- **OD-03 (IDENT):** Defer the IDENT MIREOT and general identifier integration. Use current SOC named identification properties where justified; retain unknown-scheme values without inventing their scheme.
- **OD-04 (Textile semantics):** Preserve supported exact/maximum/range threshold expressions, threshold evaluations, denominators, reporting levels, product parts, material groups, qualification sources, analytical methods, location types, and free-text instructions.
- **OD-05 (Historical version IRIs):** Preserve historical snapshot and MIREOT bytes outside the active new runtime; do not redirect previous version IRIs to migrated content.
- **OD-06 (Versioning):** Prepare a breaking-change release candidate *provisionally* numbered 2.0.0, subject to repository governance and owner approval; no push, tag, merge or publication.

**Execution boundary:** Existing migration preparation commit `287d4d5cf90f0a5175986f0563a87495ea498add` on branch `migration/october-2026-core-2.0.0` precedes semantic implementation. Do not repeat or overwrite its verified archive and preparatory tests. Check status/diffs before further edits; pause only on genuinely new material semantic conflicts.

---

# Complete final reconciliation report (verbatim)

**Reconciliation verdict: proceed with a bounded SOC/CON migration, preserve the supported Textile extensions, and defer IDENT.** Claude’s nine findings are substantially supported, with important qualifications concerning material groups, cardinalities and contextual qualification.

The specification below changes no upstream CORE files and introduces no COMP/LCA or general identifier dependency. Proposed new names are specification names, not implemented resources.

Prefixes:

- `e:` — `https://w3id.org/eudpp#`
- `txtsoc:` — `https://w3id.org/eudpp/textile-soc#`
- `txtam:` — `https://w3id.org/eudpp/textile-associated-materials#`
- `txtcon:` — `https://w3id.org/eudpp/textile-connector#`

**1. Disposition of M1–M9**

| Finding                                    | Disposition                      | Verified semantics and required treatment                                                                                                                                                                                                                                                                                |
| ------------------------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **M1 — Material groups become products**   | **CONFIRMED_WITH_QUALIFICATION** | `e:isLocatedInProduct rdfs:range e:Product` produces the reported inference. However, giving every material group range `MaterialOfComposition` would also narrow the existing model. Preserve structured group/part references; no universal product or material-occurrence typing.                                     |
| **M2 — Global SoC classification**         | **CONFIRMED_WITH_QUALIFICATION** | Both `concernsSubstance` and `qualifiesSubstance` have range `SubstanceOfConcern`. Keep `TextileChemicalSubstance ⊑ e:Substance`. Current CORE positive-reporting relationships necessarily entail SoC class membership; criterion-D applicability must remain presence-scoped.                                          |
| **M3 — Thresholds become concentrations**  | **CONFIRMED**                    | Maximum/range threshold expressions must remain distinct from `MaximumConcentration`/`ConcentrationRange`. Preserve them as Textile extensions using the shared quantitative-value model.                                                                                                                                |
| **M4 — Concentration expression patterns** | **CONFIRMED**                    | `MaximumConcentration` uses `e:numericalValue`. Using `maximumNumericalValue` infers `ConcentrationRange`, conflicting with their declared disjointness. Exact concentration needs discriminating SHACL, not necessarily a new OWL class.                                                                                |
| **M5 — Unrepresented legacy distinctions** | **CONFIRMED_WITH_QUALIFICATION** | Preserve the identified distinctions where used. They need not retain obsolete CORE identities or every unused inverse declaration.                                                                                                                                                                                      |
| **M6 — Instructions**                      | **CONFIRMED_WITH_QUALIFICATION** | Align handling information with `SubstanceManagementInstruction`; remove the obsolete subproperty axiom. Retain a Textile generic attachment and free-text content, while using appropriate CORE activity-specific edges.                                                                                                |
| **M7 — Historical version integrity**      | **CONFIRMED**                    | New semantics require new artifact identities. Historical catalogues and bytes must remain separate; lowercase `/soc` must not resolve to current uppercase `/SOC` content.                                                                                                                                              |
| **M8 — Negative-result identity**          | **CONFIRMED**                    | The validator ignores expected focus, source shape and constraint component. Strengthen result matching, including anonymous property-shape handling.                                                                                                                                                                    |
| **M9 — Lost mandatory relationships**      | **CONFIRMED_WITH_QUALIFICATION** | Legacy restrictions required product, substance, applicable qualification, quantitative expressions/units and evaluation inputs/results. They did **not** require every presence to contain concentration information or a threshold evaluation. Do not present new completeness requirements as inherited restrictions. |

Three targeted inference controls independently reproduced M1, M2 and M4.

**2. A1–A9: final semantic design**

**A1. Substance identity and contextual qualification**

Existing:

- `TextileChemicalSubstance ⊑ legacy:Substance`.
- Separate qualification and presence objects.

Proposed:

```
txtam:TextileChemicalSubstance
    rdfs:subClassOf e:Substance .

txtsoc:TextileSubstanceOfConcernPresenceContext
    rdfs:subClassOf e:SubstancePresence .
```

Use:

- `e:concernsSubstance` for positively reported SoC presences;
- `e:hasApplicableQualification` for the qualification applicable to that presence;
- `e:qualifiesSubstance` for the substance positively qualified by that assertion.

Preserve `TextileTypeDQualification` as a specialisation of `SoCQualificationAssertion`, with criterion D represented through `hasSoCCriterion`. An OWL `hasValue CriterionD` restriction may express the class commitment; the migration must also materialise the intended criterion explicitly in instance data.

SHACL must verify that an applicable qualification qualifies the **same substance** as its presence. A criterion-D qualification applicable to one product must not automatically become applicable to another.

**Consequence:** the substance receives global RDF class membership in `SubstanceOfConcern`. Product-specific applicability remains separately represented. No equivalence between a substance and its qualification assertion is introduced.

**Owner arbitration:** necessary only if the owner requires *no global SoC class membership whatsoever* for contextual criterion D. That requirement is incompatible with these current CORE relationship ranges; a distinct Textile contextual-claim pattern would then be necessary.

**A2. Regulatory sources and provenance**

Preserve structured sources rather than replacing them with `qualificationNote`.

- Retain `TextileProductGroupSoCReference`.
- Introduce a Textile-owned supporting regulatory-reference class for list/document identity.
- Retain a Textile `hasRegulatoryBasis` relationship from qualification assertions to these references.
- Preserve available source identifiers, version/date and product-group applicability.
- Preserve original source text as text; do not fabricate document IRIs or verified legal evidence.

`qualificationNote` remains explanatory metadata, not a substitute for provenance. A criterion individual identifies the qualification category, not its supporting document.

SHACL must verify required source relationships for the selected reporting profile. No inference from citation presence to legal applicability is permitted.

No owner arbitration is needed to preserve existing information.

**A3. Exact, maximum and range concentrations**

Rebase the existing class:

```
txtsoc:TextileConcentrationInformation
    rdfs:subClassOf e:ConcentrationOfSubstanceOfConcern .
```

Use CORE’s quantity carriers directly on concentration objects:

| Pattern | Representation                                                               |
| ------- | ---------------------------------------------------------------------------- |
| Exact   | `numericalValue` plus `hasMeasurementUnit`; neither maximum nor range typing |
| Maximum | `MaximumConcentration`, `numericalValue`, unit                               |
| Range   | `ConcentrationRange`, `minimumNumericalValue`, `maximumNumericalValue`, unit |

Define mutually discriminating SHACL branches:

- Exact excludes maximum/range typing and range endpoints.
- Maximum requires its type and one `numericalValue`; excludes range endpoints.
- Range requires both endpoints, excludes scalar `numericalValue`, and checks ordering.
- Every branch requires an approved compatible unit.

No dedicated `ExactConcentration` OWL class is necessary.

When removing the old value wrapper, transfer its values and provenance to the concentration object. Record old/new node correspondence. Shared value nodes, external references or conflicting metadata must trigger an explicit migration conflict—not an automatic merge or `owl:sameAs`.

**A4. Maximum and range thresholds**

**Retain them.** V08 explicitly exercises both; their removal would discard supported behaviour.

Use `e:ThresholdOfSubstanceOfConcern` as the shared threshold concept. Preserve Textile tracking, recycling-alert and non-exemption purposes beneath it.

Retain a threshold-to-expression relationship and three Textile expression roles:

- exact threshold value;
- maximum threshold value;
- range threshold value.

These specialise the existing `txtcon:QuantitativeValue` model rather than copying a second generic quantitative-value ontology. Add the necessary maximum/range value properties in Textile SOC.

Keep threshold objects and threshold expressions separate from concentration classes. Declare justified disjointness on the **Textile threshold classes/roles**, not blanket disjointness between all CORE quantitative properties and all Textile values.

SHACL must preserve exact/maximum/range threshold validation independently of concentration validation. No threshold expression may use a concentration class merely to obtain numeric fields.

No owner arbitration is needed to retain the existing supported distinctions.

**A5. Locations, parts, material groups and denominators**

Preserve the structured location object, controlled location type, reporting level, reference basis and analytical-method information.

Recommended supporting structure:

- Define a Textile product-part superclass in associated-materials.
- Keep material groups as structural/reporting groupings.
- Keep `TextileFibreCompositionMaterialGroup` under both `FibreCompositionComponent` and `TextileMaterialGroup`.
- Keep `NonTextileComponentMaterialGroup` distinct from the component itself.

Use `e:isSubstancePresenceOf` for the owning product. Use structured Textile location/part relationships for layers, zones and material groups.

Use `e:isLocatedInProduct` only when its object is appropriately a CORE product. Do not replace every part reference with it.

Claude’s proposed direct `isLocatedInMaterialGroup` edge is **not required** if the retained structured location model already expresses that relationship. Likewise, no blanket `hasMaterial` alignment is needed.

SHACL must check that location/denominator references belong to the reported product’s structure. Reporting level, concrete part and denominator must remain distinct.

**A6. Instructions**

```
txtsoc:TextileSoCHandlingInformation
    rdfs:subClassOf e:SubstanceManagementInstruction .
```

Keep `hasTextileHandlingInformation` with its Textile domain/range, removing its obsolete legacy superproperty.

Retain a Textile `instructionContent` property for the actual free text. Use CORE’s safe-use, recycling, reuse, disassembly and end-of-life edges according to the old instruction’s meaning. Do not map a generic instruction to every activity.

Where the old type is unspecified, retain the generic Textile attachment without inventing an activity classification.

**A7. Units and fractions**

Retain SI `MeasurementUnit` commitments and existing dimensionless ratio values.

- Preserve `0.001` as 0.1% by mass; do not multiply or divide merely because the unit IRI changes.
- `e:massFractionUnit` explicitly denotes a decimal mass ratio.
- Existing `units:one` remains usable when the quantity/reference-basis information supplies the mass-fraction meaning.
- Do not assert `owl:sameAs` between these unit resources.
- Do not globally equate legacy QUDT-based `Unit` with SI `MeasurementUnit`.

Unit migration must be quantity-specific and documented.

Validate against approved unit definitions **before range inference can make an arbitrary unit object appear correctly typed**. A temperature unit must fail a mass-fraction profile even though it is a measurement unit.

**A8. NonTextileComponent superclass**

Replace the obsolete superclass with the Textile-owned product-part superclass:

```
txtam:NonTextileComponent
    rdfs:subClassOf txtam:TextileProductPart .
```

Do not universally classify components as `Product` or `MaterialOfComposition`.

`hasComponentMaterial` continues to connect a component to its material occurrence. Product-like component specialisations can be added only where justified; they are unnecessary for this migration.

**A9. Threshold evaluation**

Preserve:

- evaluation object;
- evaluated concentration;
- applicable threshold;
- result vocabulary;
- explanatory note;
- threshold purpose and source.

Recreate supporting properties in Textile’s namespace and retain the legacy minimum relationships on the local evaluation class.

A `BelowThreshold` result does not entail regulatory compliance, exemption or absence of SoC status.

Numerical checks require compatible units, denominator, reporting scope and comparison rule. Maximum/range comparisons must not be silently reduced to scalar equality. Ambiguous or overlapping intervals must not acquire an invented determinate outcome.

**3. IDENT decision and bounded extraction**

**Defer IDENT for this migration.** This revises my earlier recommendation to add it.

Use current SOC’s `casNumber`, `ecNumber`, `echaNumber` and naming properties where the identifier scheme is known. Preserve the existing arbitrary identifier string as an explicitly Textile-owned property when its scheme is unknown. In particular, `"illustrative-substance-id"` must not become a fabricated CAS or ECHA number.

The CAS issue is qualified:

- `CAS` is a `MaterialIdentifierScheme`.
- That class is disjoint with `SubstanceIdentifierScheme`.
- Explicit dual classification produces an OWL-RL inconsistency.
- Merely linking CAS through `hasScheme` does not force dual classification: the `SubstanceIdentifier` restriction is existential, not universal.

No product, passport, actor, facility or material identifier model is added.

The bounded extractions must contain:

| Extraction      | Required scope                                                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| SOC             | Substance/SoC, presence, qualification assertions/criteria, concentration specialisations, relevant instruction and literal identifier properties |
| CON             | Product–presence, presence–product and concentration relationships actually used                                                                  |
| P_DPP           | Concentration/threshold/quantitative-property support, numeric/unit carriers and existing retained anchors                                        |
| SI              | Existing approved measurement-unit declarations and selected units                                                                                |
| ACTOR/MAT/EVENT | Existing demonstrated reuse, with the previously identified source corrections                                                                    |

Copy necessary supporting axioms faithfully. Do not import full CORE or unrelated CON identifier relationships. Keep new Textile definitions outside MIREOT.

**4. Resources to discontinue**

Discontinue from the new runtime:

- every legacy `https://w3id.org/eudpp/soc#` dependency;
- obsolete legacy superproperties and superclass links;
- unused P_DPP `EnvironmentalFootprint`, `ResourceConsumption`, `RecycledMaterialsUse` and the old `CarbonFootprint` extraction;
- the stale recycled-content annotation;
- EVENT’s obsolete source-level minimum-product restriction, unless separately justified as a Textile constraint.

Do not remove supported thresholds, evaluation, denominator, location, reporting-level, source or instruction distinctions.

Unused legacy inverses need not be recreated automatically.

**5. Versioning and exact affected files**

Keep historical source snapshots, MIREOT bytes and their historical catalogue together in an immutable historical package or preserved release baseline, outside the new runtime closure.

The new catalogue must not redirect `/1.1.2`, `/1.1.3` or lowercase `/soc` to migrated content.

New version identities are required for directly changed graphs:

- `ontology/textile-soc.ttl`
- `ontology/textile-associated-materials.ttl`
- `ontology/textile-recyclability.ttl`
- changed SOC/P_DPP/EVENT MIREOT artifacts;
- the new CON MIREOT;
- any other artifact whose versioned bytes are changed.

The network entry point needs a new release identity when its release/import contract changes. Unchanged Textile module graphs need not all receive new version IRIs merely because another module changed; their historical closure must still remain reproducible.

**Version numbers remain owner-assigned.**

Implementation files:

- `mireot/soc-textile-mireot.ttl`
- `mireot/dpp-textile-mireot.ttl`
- `mireot/event-textile-mireot.ttl`
- proposed `mireot/con-textile-mireot.ttl`
- the three Textile modules above and the network entry point where required;
- `shacl/textile-soc-shapes.ttl`
- `examples/example-10-textile-soc-v1.1.2.ttl`
- V08/I08 fixtures;
- both JSON expectation files under `tests/abox_corpus/expectations/`;
- `tests/test_public_package.py`
- `scripts/validate_public.py`
- `catalog-v001.xml`
- adopted dependency snapshot paths and their historical preservation inventory;
- `README.md`, `CHANGELOG.md`, `VERSION`;
- `docs/DEPENDENCIES.md`, `docs/ARCHITECTURE.md`, `docs/MODELLING_GUIDE.md`, `docs/PUBLICATION_SCOPE.md`, `docs/SOURCE_TRACEABILITY.md`;
- relevant governance records, traceability projections, SOC/associated-materials/recyclability documentation and diagrams;
- publication manifest and checksums.

No IDENT extraction or dependency file is required. The recyclability relationship whose range is `TextileSubstanceOfConcernPresenceContext` can retain that range IRI.

**6. Validation acceptance criteria**

Strengthen the validator to compare the expected **result multiset**, including:

- focus node;
- actual source shape;
- constraint component;
- result path;
- severity;
- source-constraint/message identity where specified;
- permitted additional results.

A specific complication is confirmed: I01 returns an **anonymous property shape**, while its expectation names `MassFractionValueShape`, the containing node shape. Do not implement naïve IRI comparison. Identify the actual property shape through a stable structural selector/fingerprint and its named container, or assign stable property-shape IRIs. Reconcile expectations against actual constraint ownership without weakening them.

Required discriminating cases:

| Case                                                          | Required outcome                                             |
| ------------------------------------------------------------- | ------------------------------------------------------------ |
| Missing required product/substance/qualification              | Violation at the intended presence                           |
| Missing concentration                                         | Violation in the explicitly selected complete-report profile |
| Missing scalar/endpoints/unit                                 | Correct expression-specific violation                        |
| Inverted concentration and threshold ranges                   | Separate, identifiable violations                            |
| Threshold typed as concentration                              | Rejected                                                     |
| Maximum using `maximumNumericalValue`                         | Rejected; range/disjointness consequence detected            |
| Invalid or incompatible unit                                  | Rejected without relying on inferred unit typing             |
| Qualification targets another substance                       | Rejected                                                     |
| Criterion-D qualification attached to another product context | Rejected                                                     |
| Material group used as product-location object                | Mapping rejected; forbidden product inference tested         |
| Location/denominator outside reported product structure       | Rejected                                                     |
| Residual legacy SOC IRI                                       | Rejected in the active closure/data                          |
| Shapes receive no intended focus nodes                        | Coverage gate fails                                          |

Preserve justified local OWL existential commitments as well as SHACL checks. SHACL does not replace their entailments.

Retain all existing positive/negative coverage, eleven examples, six reasoning scenarios and the recyclability inference control. Changed fixtures must preserve their original defect/behaviour, not merely their pass/fail label.

**7. Remaining owner decisions**

Only two semantic alternatives remain:

1. **Criterion D:** accept current CORE’s global `SubstanceOfConcern` typing while keeping applicability contextual, or require a strictly contextual claim without that global typing. The latter needs a different Textile relationship pattern.
2. **Completeness scope:** make concentration mandatory only for designated complete reports—the recommended conservative option—or introduce a broader requirement for every Textile SoC presence. The latter is stronger than the verified legacy restrictions.

Maximum/range thresholds, structured scope, provenance, evaluation and free text should be retained under the supplied principles; they do not require another keep/drop decision.

Release numbering remains an owner governance decision, separate from these semantic alternatives. The four-person creator decision remains unchanged.

**8. Phased implementation gates**

1. **Resolve the two semantic alternatives and assign release identities.**
2. **Preserve historical artifacts; prepare bounded current extractions.** Gate: source fidelity, correct identities, no legacy/current runtime mixture.
3. **Implement Textile extensions and data transformation together.** Gate: information-preservation checks and documented node correspondence.
4. **Implement SHACL and strict result matching.** Gate: every discriminating negative fails for its intended reason; focus coverage is proven.
5. **Run full regressions and inference comparisons.** Gate: no unintended product, concentration or qualification entailments.
6. **Update documentation and publication artifacts.** Gate: historical resolution, traceability, manifest and checksum verification.

**No repository or CORE files were changed.** Staged and unstaged diffs remain empty, with the previously known `.pytest_cache/` access limitation.

7:20 PM