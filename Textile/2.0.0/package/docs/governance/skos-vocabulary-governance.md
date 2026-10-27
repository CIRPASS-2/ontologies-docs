# SKOS vocabulary governance

## Purpose

Textile-controlled schemes are project-maintained reference vocabularies. External schemes and explicit justified mappings provide the normal extension pattern.

## Scope

This document governs the ownership and conformance interpretation of Textile SKOS reference vocabularies. It is governance documentation only: it introduces no ontology, concept, mapping, or constraint change.

## Definitions

`CIRPASS_GOVERNED_REFERENCE_SCHEME` is a Textile project-maintained concept scheme. An `EXTERNAL_IMPLEMENTER_SCHEME` is controlled by its external owner. A `MAPPING_RELATION` relates concepts without transferring ownership. A `PROFILE_CONFORMANCE_RULE` specifies values accepted in a particular conformance context.

## CIRPASS-governed reference schemes

CIRPASS Textile concept schemes are governed project reference vocabularies. Their concepts and lifecycle remain subject to the Textile project governance process.

## External implementer schemes

External implementers should normally maintain concepts that they own in their own concept schemes. External schemes remain valid governance objects with their own owner, provenance, and lifecycle.

## Scheme ownership

Using a CIRPASS scheme does not give an external implementer authority to modify it. Likewise, relating concepts across schemes does not transfer ownership from either scheme owner.

## Project vocabulary evolution

A deliberate proposal to add or change a CIRPASS-governed concept is project vocabulary evolution. Its required outcome is `PROJECT_GOVERNANCE_REVIEW_REQUIRED`; this policy does not prevent Textile schemes from evolving through that process.

## External extension pattern

When an implementer needs a local concept beyond a Textile reference vocabulary, the normal pattern is an externally owned scheme and, where justified, an explicit mapping. Direct unmanaged insertion into a CIRPASS-governed scheme is `NOT_THE_NORMAL_GOVERNANCE_PATTERN`, not a prohibition on future project-governed evolution.

## Mapping relations

`skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch`, and `skos:relatedMatch` express different mapping relationships between concepts. The choice must reflect the particular relationship actually supported by evidence.

## Mapping evidence requirements

Mapping proposals require semantic evidence appropriate to the selected predicate. Label similarity alone is insufficient evidence for `skos:exactMatch`; a future mapping must be separately reviewed rather than inferred from wording or a shared label.

## Mapping non-equivalence guardrail

A SKOS mapping does not transfer scheme ownership, make an external concept a CIRPASS concept, or automatically satisfy a profile. In particular, `skos:exactMatch` is not an assertion of OWL class or property equivalence, nor an `owl:sameAs` assertion.

## Closure is a profile decision

A `skos:ConceptScheme` is not, by that fact alone, a closed conformance vocabulary. `skos:inScheme`, `skos:hasTopConcept`, `skos:topConceptOf`, and a finite current concept list likewise do not establish closure. Closure or extension behaviour belongs in an explicit applicable profile or constraint contract.

## Closed profile vocabularies

A profile may be a `CLOSED_PROFILE_VOCABULARY` when its explicit conformance contract restricts accepted values to a governed set. This policy does not declare the current Textile repository closed and does not add a SHACL mechanism to do so.

## Open/extensible profile vocabularies

A profile may be `OPEN_PROFILE_VOCABULARY` when its explicit contract permits stated extensions. The absence of `sh:closed` or `sh:in` does not establish that result; without an explicit applicable rule, the status is `NOT_DETERMINED_FROM_CURRENT_REPOSITORY`.

## Mapped external vocabularies

A profile may permit `MAPPED_EXTERNAL_VOCABULARY_ALLOWED` when its explicit rule accepts externally governed concepts through an accepted mapping approach. The external scheme, the mapping evidence, and the profile acceptance rule are separate concerns; a mapping alone does not establish acceptance.

## Current Textile repository evidence

The governed task evidence records 31 Textile-controlled schemes, 242 direct `skos:inScheme` memberships, 157 explicit top concepts, and 16 actual SKOS mapping assertions. The mapping assertion breakdown is four `exactMatch`, four `closeMatch`, three `broadMatch`, two `narrowMatch`, and three `relatedMatch`.

## Current scheme inventory summary

The controlled schemes can be inspected directly in the packaged ontology graphs.

## Current SHACL/constraint evidence

The fresh task scan reproduced zero current `sh:closed` assertions and zero current `sh:in` assertions. It did not reproduce an explicit current documentation, profile, or scheme instruction for closed, open-extension, or mapped-external acceptance. Accordingly, the current profile status is `NOT_DETERMINED_FROM_CURRENT_REPOSITORY`; absence is evidence, not proof of the opposite state.

## Governance decision table

| Situation | Governance outcome |
| --- | --- |
| Project modifies or adds a concept to a governed CIRPASS scheme | `PROJECT_GOVERNANCE_REVIEW_REQUIRED` |
| External implementer needs an externally owned concept | `EXTERNAL_SCHEME_AND_MAPPING_PATTERN` |
| External implementer directly inserts an unmanaged concept into a CIRPASS scheme | `NOT_THE_NORMAL_GOVERNANCE_PATTERN` |
| A closed profile wants a finite accepted vocabulary | `EXPLICIT_PROFILE_CONSTRAINT_REQUIRED` |
| An open/extensible profile wants external values | `EXPLICIT_PROFILE_CONSTRAINT_REQUIRED` |
| Closure is inferred merely from a finite ConceptScheme | `UNSUPPORTED_INFERENCE` |
| A semantic mapping is inferred merely from matching labels | `UNSUPPORTED_MAPPING_INFERENCE` |
| An existing CIRPASS scheme needs governed evolution | `PROJECT_GOVERNANCE_REVIEW_REQUIRED` |

## What implementers may safely do

Implementers may reuse suitable CIRPASS Textile concepts, maintain externally governed concepts in externally governed schemes, propose evidence-supported mappings, follow the applicable conformance profile, and seek project governance review for changes to CIRPASS-governed schemes.

## What implementers must not infer

Implementers must not infer that a finite scheme is closed; that missing `sh:closed` or `sh:in` establishes openness; that example data establishes normative closure; that a shared label proves an exact mapping; that `skos:exactMatch` supplies OWL equivalence; that mapping transfers ownership or automatically provides profile acceptance; or that direct unmanaged insertion is the normal extension pattern.

## Future scheme-change process

A bounded future change workflow is: proposal, semantic review, ownership and provenance check, impact assessment, mapping implications, validation and documentation update, then project acceptance. This does not imply external standards-body approval.

## Future mapping tasks

Additional mappings require separate relationship-specific semantic evidence and review. This policy does not commit to mappings that have not been accepted or implemented.

## Non-goals

This policy does not change ontology semantics; add, remove, rename, or reassign concepts; create, delete, or alter mappings; create closure constraints; add `sh:closed` or `sh:in`; modify SHACL profiles, dependencies, MIREOT, or the canonical workbook; define normative transformations; or make external mappings normative by implication.

