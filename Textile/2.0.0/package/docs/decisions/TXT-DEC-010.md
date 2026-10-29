# TXT-DEC-010 — October 2026 CORE migration

The owner authorises a breaking 2.0.0 candidate using bounded SOC 2.2.0,
CON 2.4.0, P_DPP 2.2.0, EVENT 1.0.0, ACTOR 2.2.0 and MAT 1.1.0 sources.
The final reconciliation (M1–M9, A1–A9) and OD-01 through OD-06 govern this
implementation. IDENT is deferred.

Positive SoC relationships entail SubstanceOfConcern. Qualification applicability
remains presence-scoped. Generic TextileChemicalSubstance remains a Substance.
Concentration is mandatory only in the separately selected complete-report
profile. Structured locations, material groups, denominators, regulatory source
references, thresholds, evaluations and free-text instructions remain Textile-owned.

Exact/maximum/range threshold expression roles specialise the existing common
QuantitativeValue. The common quantitative SHACL profile permits precisely these
three roles: ordinary values still require their scalar; maximum and range roles
receive their own scalar/endpoint validation. Its ban on arbitrary new quantity
subclasses remains. This deliberate extension reconciles A4 with the old scalar-only
profile; it does not suppress the original regression constraints.

Concentration wrappers are removed only when uniquely owned and metadata do not
conflict. Node correspondence records the transfer. Unknown identifier schemes
remain unknown. Mass fractions retain their decimal ratios and use approved SI
unit identities; no unit owl:sameAs is introduced.

An evaluation refers to an explicitly applicable threshold interpreted in that
concentration's scope. Explicit threshold basis/level/part overrides must agree.
For non-negative mass fractions, maximum-only reports represent [0, maximum].
Strictly separated intervals support BelowThreshold/AboveThreshold. Exact equality
supports AtThreshold; overlapping intervals support only an indeterminate result.
These vocabulary values assert a comparison, not compliance or exemption.

Historical catalogue and RDF bytes are preserved separately. Previous version
IRIs resolve only with the historical catalogue; the new closure excludes legacy
SOC semantic terms and imports. Provenance annotations identify the old sources.
Only changed module graphs receive 2.0.0 candidate identities. No release or
creator-metadata approval is implied.


## Independent audit corrections

The 42 retained definitions/comments copied from SOC 0.1.2 DRAFT are adapted
external content, attributed to that ontology and their exact source resources
under CC BY 4.0. The local namespace, scope, constraints and alignment remain
Textile decisions. These decisions do not make the copied text source-free.
See [migration guidance](../CORE_2026_MIGRATION.md) and the
`migration/legacy-soc-attribution.json` statement inventory.

Product membership follows forward hasPart, inverse isPartOfProduct and
hasNonTextileComponent edges, in the same direction away from the owning
product. It never follows arbitrary material references or crosses to another
product. The inverse axiom is restored. Evaluations attached to a presence
must evaluate a concentration owned by that presence.

The product-group-list property's domain is restored to TextileTypeDQualification,
retaining its OWL criterion-D inference. The SVHC-list property's common CORE
qualification domain is intentional: the candidate has no separate Textile type-A
class. Its SHACL constraint requires explicit CriterionA. This avoids inventing
a type-A class or silently inferring a criterion from a source link. Both cases
are tested. Criterion D likewise remains explicit for RDFS validation.

The public txtsoc:appliesToProduct IRI is retained and labelled "qualification
applies to product". Its domain is SoCQualificationAssertion; the homonymous
CORE property has DigitalProductPassport as domain. They are distinct properties,
without a bridge. Examples and shapes consistently use the txtsoc property.

The CON selection excludes unused concernsProduct (and its ProductEvent support),
and includes SubstanceManagementInstruction with its complete source superclass
axiom to DigitalInstruction and necessary supporting declarations. Each selected
subject remains graph-isomorphic to the supplied source; no blanket import is added.
