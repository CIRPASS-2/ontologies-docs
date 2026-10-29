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

`txt:hasFibreType` is a potential alignment candidate only if governance decides
that Textile fibre concepts are also instances of `dpp:MaterialType`. Their
current SKOS representation does not by itself establish or prohibit that
additional classification. No such mapping is asserted.

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
