# Modelling guide

## Products and composition

Use Textile Core classes for textile products and intermediate textile products. Represent structural subdivisions and composition through Textile Structure and Associated Materials rather than by introducing ad-hoc product subclasses.

## Processes and events

Use Textile Process for process types and executions. Use the event-aligned classes when an occurrence changes the state or lifecycle status of a product. A process description and a product event may describe different aspects of the same occurrence.

## Assessments and indicators

An assessment method specifies how a characteristic is evaluated. An assessment execution applies the method under stated conditions. The result records the observed or calculated outcome. Indicators interpret or aggregate such results for a defined purpose and context.

## Quantitative values

Use explicit quantitative-value nodes. Record the numerical value, unit and quantity kind when applicable. Do not encode a measurement and its unit as an unstructured string.

Use `txtcon:QuantitativeValue` with `txtcon:numericValue`, `txtcon:hasMeasurementUnit` and, where applicable, `txtcon:hasQuantityKind`. The related SI declarations are supplied in `mireot/si-textile-mireot.ttl`. Reference-period relationships are distinct from the measured numeric value. See [the composition example](../examples/example-01-product-composition-v1.1.2.ttl) and [the structure example](../examples/example-02-structure-v1.1.2.ttl) for complete RDF patterns.

The pattern is a modelling abstraction, not a claim that JRC defines this OWL structure. [Quantitative-value rationale](decisions/TXT-DEC-001.md) and [reference-duration rationale](decisions/TXT-DEC-004.md) preserve that distinction. This pattern does not by itself establish an equivalence mapping to a quantity-value model in another ontology. SHACL requirements are application-profile requirements; OWL domain and range axioms are not form-field validation rules.

## Substances of concern

Represent the substance identity separately from the substance-presence context and from its regulatory qualification. Attach concentration, location and handling information to the presence context. Positive reports use CORE SubstancePresence and concernsSubstance, which entails SubstanceOfConcern typing. Applicable qualifications remain presence-scoped and must qualify that same substance. Concentrations use CORE scalar/range carriers directly; threshold expressions retain Textile roles beneath the shared QuantitativeValue. See [the migration patterns](CORE_2026_MIGRATION.md).

## Verified CORE reuse and module ownership

`txt:FibreCompositionComponent` already specializes CORE
`dpp:MaterialOfComposition`. The relation `txt:hasFibreCompositionComponent`
links a product to a composition entry; it is not equivalent to
`dpp:hasMaterialType`, which links a material occurrence to its classification.
The MAT snapshot uses the `https://w3id.org/eudpp#` term namespace.

The owner-approved response to Nader Jelassi's [PR #19 review](https://github.com/CIRPASS-2/ontologie-textiles/pull/19)
adds `txt:FibreTypeConcept rdfs:subClassOf dpp:MaterialType` and
`txt:hasFibreType rdfs:subPropertyOf dpp:hasMaterialType`. Fibre concepts remain
SKOS individuals and also instantiate MAT's class of sector material
classifications. The property links a fibre composition entry, already a
`dpp:MaterialOfComposition`, to its classification at the same conceptual level
as MAT. RDFS/OWL inference therefore exposes every fibre concept as a MAT type
and every fibre-type assertion as a MAT classification assertion; consumers
without inference must materialize these consequences when needed.

The product-to-entry relation `txt:hasFibreCompositionComponent` remains distinct
and has no MAT type-property alignment. Physical `txt:TextileFibre` batches
remain products. Composition fractions, units, schemes and existing constraints
are preserved. These two OWL bridges are project modelling decisions supported
by MAT definitions, not alignments prescribed by the JRC study. See the
[alignment evidence](../migration/MAT_ALIGNMENT.md).

`dpp:materialPercentage` carries a literal decimal percentage. Textile uses
`txt:hasFibreMassFraction` to link to a structured `txtcon:QuantitativeValue`
on a 0?1 scale with `units:one`. Substitution would change the RDF kind, value
structure and scale interpretation; it is not semantics-preserving.

CORE `dpp:QuantitativeProperty` represents a quantitative property or measurand;
Textile `txtcon:QuantitativeValue` represents its structured value. The CORE
snapshot also supplies numerical-value and unit carriers, but this structural
overlap does not establish class equivalence. See the local
[CORE snapshot](../dependencies/current-core/p_dpp.owl) and
[MAT snapshot](../dependencies/current-core/mat.owl).

The five `hasTextualValue` local names belong to distinct IRIs in the
`textile-assessment#`, `textile-context#`, `textile-indicator#`,
`textile-process#` and `textile-structure#` namespaces under
`https://w3id.org/eudpp/`. Each module owns its property with a role-specific
domain. They are not duplicate declarations of one property. The shared value
structures remain in Connector; no centralization is required by this review.

See the [Nader review record](governance/nader-review.md) for evidence and
outstanding governance questions.

## Bounded CORE closeMatch compatibility

Textile no longer declares `skos:closeMatch` locally. No active Textile source
module declares or asserts this property, and no replacement declaration is
introduced. Other SKOS mapping properties and concept relationships are
unchanged.

The upstream [P_DPP snapshot](../dependencies/current-core/p_dpp.owl) declares
it as an annotation property and uses
`dpp:Product skos:closeMatch "schema:Product"`. The
[bounded CORE MIREOT](../mireot/dpp-textile-mireot.ttl) retains that assertion
exactly, without extracting the property's declaration. Neither upstream
resource is changed by this correction. The literal is a descriptive CORE
annotation, not an equivalence between Product and schema:Product.

The [SKOS standard](https://www.w3.org/TR/skos-reference/#mapping) instead
defines `skos:closeMatch` as an object property for concept mappings.
Preserving the upstream annotation does not make it a SKOS-standard concept
mapping or redefine SKOS. Loading the full SKOS ontology together with CORE's
annotation-property definition would require a separate compatibility
assessment; no such import is introduced here.

The merged diagnostic artifact can acquire an annotation-property declaration
during serialization from the retained CORE usage. That generated declaration
is not a Textile source declaration, and a merged profile pass does not prove
that the individual modules pass or that all upstream vocabulary uses follow
SKOS semantics. The following procedure makes these limits explicit.

## OWL 2 DL diagnostic procedure and limits

The 2026-11-03 diagnostic applies to the local candidate with the retained MAT
alignment, the subsequent modelling-note and metadata corrections, and the
removal of Connector's local closeMatch declaration. It does not describe the
unmodified source commit
`e9cf8542d104fefccf339761d138fcf9c32bc904`. The runtime catalogue resolved
exactly the expected 20 ontology documents, including the bounded MIREOTs;
there was no accidental loading of full CORE modules or missing import.

### Reproduce the merged-artifact check

Use ROBOT 1.9.7 from the repository root. Set `$robotJar` to that release's
JAR and `$diagnosticDir` to an existing writable scratch directory outside the
publication package. The release JAR used for the diagnostic had SHA-256
`91890c2e83d0f092dd08731376f154b36610544cfbe8685337a1bf7244ccaa2d`.
The following PowerShell commands retain ontology annotations as well as OWL
axioms, collapse the imports into one artifact, and check that artifact:

```powershell
java -jar $robotJar merge --input ontology/textile-ontology.ttl --catalog catalog-v001.xml --include-annotations true --output "$diagnosticDir/merged.owl"
java -jar $robotJar validate-profile --profile DL --input "$diagnosticDir/merged.owl" --output "$diagnosticDir/merged-profile.txt"
java -jar $robotJar reason --reasoner hermit --input "$diagnosticDir/merged.owl" --remove-redundant-subclass-axioms false --output "$diagnosticDir/reasoned.owl"
```

Inspect each exit status and the profile report before interpreting the
reasoning result. See ROBOT's [merge](https://robot.obolibrary.org/merge),
[profile validation](https://robot.obolibrary.org/validate-profile) and
[reasoning](https://robot.obolibrary.org/reason) procedures. The retained
`dpp:Product skos:closeMatch "schema:Product"` annotation was present in the
actual checked artifact; no assertion was removed for this check.

### Modular and merged results

ROBOT 1.9.7 bundles OWLAPI 4.5.29. A comparison using OWLAPI 5.1.18 produced
the same results at each stage:

| Checked representation | Profile violations (occurrences) | OWL 2 DL profile |
| --- | ---: | --- |
| Original ontology and modular imports closure | 208 | Fails declaration checks |
| Union of the same OWL axioms in memory | 47 | Fails declaration checks |
| Serialized and reloaded union | 0 | Passes |
| ROBOT merged artifact | 0 | Passes |

The 208 occurrences comprise 188 annotation-property, nine class, eight
object-property and three datatype declaration diagnostics. Deduplication by
IRI and violation type gives 19 affected IRIs: 12 annotation properties,
four classes, two object properties and one datatype. Fifteen have
declarations elsewhere in the loaded closure, outside the individual
ontology's visible import scope. Flattening removes 161 such occurrences.
The remaining 47 concern declarations absent throughout the raw closure:
`skos:scopeNote` (one occurrence), `prov:wasDerivedFrom` (42 occurrences)
and `xsd:date` (three occurrences), plus `skos:closeMatch` (one occurrence).
The total modular count remains 208 after the local declaration removal:
the CORE annotation was already outside Connector's declaration visibility.

Thus the merged artifact passes the structural profile check, but this
does not establish that each original module, or the original modular
closure as checked by OWLAPI, passes. The remaining modular diagnostics
include genuinely absent explicit declarations as well as import-visibility
limitations. No source declarations or imports were changed to suppress them.

### Declarations introduced by serialization

The diagnostic compared the union of all original OWL axioms with the
serialized, reloaded merged artifact using OWLAPI axiom-set differences.
The original 10,014 distinct axioms became 10,304. The 290 additions were
exclusively declaration axioms:

| Entity type | Added declarations |
| --- | ---: |
| Named individual | 286 |
| Annotation property: `skos:scopeNote`, `prov:wasDerivedFrom`, `skos:closeMatch` | 3 |
| Datatype: `xsd:date` | 1 |

The earlier 2026-11-02 candidate had 10,015 original axioms and 289 added
declarations. Removing the local closeMatch declaration accounts exactly
for the one-axiom decrease and the additional serialization declaration;
the merged artifact's axiom count is unchanged.

Zero original OWL axioms were removed and the logical axiom sets were equal.
All original OWL axioms, including the closeMatch annotation assertion, were
preserved. These declarations belong to the serialized diagnostic artifact;
they were not added to the canonical modules. This is an OWL axiom-preservation
result, not a claim of RDF graph identity: merging collapses ontology
boundaries and import statements. Ontology annotations were retained with
`--include-annotations true`.

### HermiT configuration and qualified consistency result

The merged artifact was reasoned over with HermiT 1.4.5.456 bundled in ROBOT
1.9.7. ROBOT's HermiT factory path uses
`ignoreUnsupportedDatatypes=true`; the bundled factory implementation and a
direct factory run were checked to confirm this setting. It is not an
additional ROBOT command-line option in the commands above. An explicit
HermiT configuration must record the same value to reproduce this result.

With that setting the merged artifact was reported consistent, with zero
unsatisfiable named classes (excluding `owl:Nothing`). The direct check also
confirmed both accepted MAT entailments and all 22 fibre classifications.
With `ignoreUnsupportedDatatypes=false`, HermiT instead raised
`UnsupportedDatatypeException` for `xsd:date`, so no strict-mode consistency
result was obtained. This exception is not evidence of inconsistency.

The positive result is conditional on ignoring unsupported datatypes; it is
not a complete consistency proof under the intended date semantics.
Declaring `xsd:date` makes the artifact pass structural declaration checks
but supplies neither a supported datatype interpretation nor a custom
datatype definition. OWL RL regression validation likewise does not
establish complete OWL DL consistency.

### The three logical uses of xsd:date

These are the three `rdfs:range xsd:date` occurrences responsible for the
datatype profile diagnostics, not a count of every date-valued metadata
literal in the repository. Here `dpp:` means `https://w3id.org/eudpp#` and
`txtsoc:` means `https://w3id.org/eudpp/textile-soc#`.

| Property | Location | Modelling purpose |
| --- | --- | --- |
| `dpp:qualificationValidFrom` | [SOC MIREOT](../mireot/soc-textile-mireot.ttl) | First date on which a `dpp:SoCQualificationAssertion` is considered valid. |
| `dpp:qualificationValidUntil` | [SOC MIREOT](../mireot/soc-textile-mireot.ttl) | Last date on which that qualification assertion is considered valid, when bounded. |
| `txtsoc:referenceDate` | [Textile SOC](../ontology/textile-soc.ttl) | Date recorded for a `txtsoc:ExternalRegulatoryReference`. |

The first two ranges are retained CORE SOC qualification-validity metadata;
the third is a Textile project decision for external regulatory references.
They express calendar dates. Replacing them with timestamps or strings
would require an explicit modelling decision and is outside this correction.

### Retained regression contract

The accepted bridges remain
`txt:FibreTypeConcept rdfs:subClassOf dpp:MaterialType` and
`txt:hasFibreType rdfs:subPropertyOf dpp:hasMaterialType`.
The existing [MAT regression tests](../tests/test_mat_alignment.py) cover
all 22 classifications, property entailment, SKOS typing, composition-model
boundaries, historical preservation and both SHACL example modes. These
tests retain their behavioural expectations. The later owner-approved
corrections are now checked as an exact seven-addition/six-removal delta
against the unchanged pre-MAT commit. The old creator and version-identity
proofs first verify that complete delta, then restore only those exact
triples before checking their unchanged historical digests. Notes, metadata,
classes and properties are not ignored wholesale.

Ten mutation tests demonstrate rejection of unauthorized changes. The frozen
catalogue and protected external, MIREOT and historical inputs remain
byte-protected. The three stale WIDOCO/WebVOWL modules are regenerated from
canonical sources using the established workflow; generated RDF is checked
for graph equivalence. The original eight failures and their individual
baselines are documented in the
[publication finalization record](../migration/PUBLICATION_CANDIDATE_FINALIZATION.md).
See its linked machine-readable delta and final validation results for the
current publication candidate. The earlier MAT-only evidence remains an
unchanged historical proof of that narrower transition.
