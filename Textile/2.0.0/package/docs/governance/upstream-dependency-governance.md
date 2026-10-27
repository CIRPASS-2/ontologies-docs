> Historical baseline examples below describe 1.1.2. The October 2026
> adoption is implemented by [TXT-DEC-010](../decisions/TXT-DEC-010.md)
> and the [migration guide](../CORE_2026_MIGRATION.md); policy rules remain in force.

# Upstream dependency governance

## 1. Purpose

This policy governs a proposed change to an
upstream ontology by its observable semantic effect on terms actually reused by
Textile. It does not adopt, update, or describe an upstream release.

## 2. Scope

It applies to any ontology represented in the accepted local dependency and
MIREOT architecture. It applies before a dependency-update task changes a
snapshot, MIREOT subset, Textile module, validation profile, example, contract,
or release artefact.

## 3. Definitions

An **accepted snapshot** is the local dependency file and its recorded metadata.
A **candidate revision** is externally supplied, reproducible source material
proposed for comparison. A **reused term** has evidence in the boundary below.
**Observable impact** is a reproducible change in axioms, inference, validation,
examples, import resolution, public contract, or workbook cross-reference.

## 4. Accepted upstream snapshot vs candidate revision

Record the accepted local file, ontology IRI, version/status annotations, digest,
and associated MIREOT file. Obtain a candidate from its upstream publisher with
a resolvable identifier and source/diff. Compare RDF kinds and semantic axioms;
do not fabricate a candidate, changelog, compatibility claim, or replacement.

## 5. Actually reused term boundary

A term is actually reused when it is reproduced in an accepted Textile MIREOT
subset used by Textile, referenced by a Textile ontology axiom, SHACL, official
example, import-resolution/validation behaviour, or accepted public contract.
Classify each term as `REUSED_DIRECTLY`,
`REPRODUCED_LOCALLY_BUT_NOT_CURRENTLY_REFERENCED`,
`UPSTREAM_ONLY_NOT_REPRODUCED`, or
`NOT_DETERMINED_FROM_CURRENT_REPOSITORY`. Presence in a dependency file alone
does not establish reuse.

## 6. Evidence hierarchy

Use current repository RDF and contracts first; then accepted historical facts;
then the owner decision. Candidate meaning, replacements, and compatibility not
proved by these sources require external confirmation. Record the evidence class
for every conclusion.

## 7. Change classification

Classify each candidate diff as one or more of: `ANNOTATION_ONLY`;
`ADDITIVE_UNUSED`; `ADDITIVE_REUSED_OR_RELEVANT`;
`REUSED_TERM_SEMANTIC_CHANGE`; `HIERARCHY_DOMAIN_RANGE_INFERENCE_CHANGE`;
`DEPRECATION_REUSED_TERM`; `REMOVAL_OR_RENAME_REUSED_TERM`; and
`SAME_IRI_MEANING_CHANGE`. Annotation changes remain annotation-only unless
current tooling executes them. An addition is unused only if it is outside the
reuse boundary and cannot change inference on a reused term.

## 8. Observable impact assessment

For each changed term, record `YES`, `NO`, `NOT_APPLICABLE`,
`NOT_DETERMINED`, or `EXTERNAL_CONFIRMATION_REQUIRED` for: reuse-boundary
membership; RDF kind; hierarchy; domain/range; equivalence, disjointness and
restrictions; property characteristics; deprecation; IRI removal/rename;
same-IRI meaning; Textile inference; SHACL; official examples; import
resolution; MIREOT reproduction; public contract; workbook cross-reference;
migration and compatibility bridges; annotation execution; and release rebuild.

## 9. Textile release consequences

The permitted Textile outcomes are `NO_TEXTILE_SEMANTIC_IMPACT`,
`TEXTILE_REVIEW_REQUIRED`, `TEXTILE_COMPATIBILITY_REVALIDATION_REQUIRED`,
`TEXTILE_MIGRATION_REQUIRED`, and `TEXTILE_RELEASE_BLOCKED_PENDING_MIGRATION`.
They are Textile governance outcomes, not claims about upstream SemVer.

## 10. SemVer/version-number rule

**An upstream version-number change alone does not determine Textile SemVer.**
For example, a hypothetical upstream major change with no changed reused
semantics can have no Textile semantic impact; a hypothetical patch change that
breaks the meaning of a reused same IRI can require migration and block release.

## 11. Migration requirements

Breaking changes to reused terms require migration guidance before adoption:
old and replacement terms; affected Textile modules/axioms and MIREOT; affected
SHACL/examples; data implications; compatibility bridge; required validation;
release consequence; and rollback/fallback to the previous accepted snapshot.
This policy specifies the record structure; it does not invent a migration.

## 12. Same-IRI semantic-change rule

Same-IRI continuity is not proof of compatibility. A materially changed
definition, axiom, role, inference, or constraint for a reused IRI is
`SAME_IRI_MEANING_CHANGE`, assessed as potentially breaking.

## 13. Deprecation rule

Deprecation of a reused term is `DEPRECATION_REUSED_TERM`. It triggers review
and external confirmation of the replacement and transition period; it does not
by itself prove immediate removal or present invalidity.

## 14. Removal/rename rule

Removal, rename, or replacement of a reused IRI is
`REMOVAL_OR_RENAME_REUSED_TERM`, requires migration guidance, and may block a
Textile release until migration and validation succeed.

## 15. Validation expectations

Re-run RDF syntax/import, relevant inference, SHACL profiles, official examples,
MIREOT reproduction, contracts, workbook checks, and release build checks when
their corresponding impact dimension is `YES`. Preserve the accepted snapshot
until the review record is complete.

## 16. Required review record

The record identifies snapshot and candidate evidence, sampled/reproduced reuse
terms, classifications, all impact dimensions, external confirmations, outcome,
migration guidance where triggered, validations, decision authority, and
rollback. The assessment should be recorded with the proposed public change.

## 17. Decision authority / external confirmation

The owner decides adoption and Textile release consequences. Upstream publisher
confirmation is required where candidate identity, intended meaning,
deprecation/replacement, or compatibility cannot be established from evidence.

## 18. Non-goals

This policy does not define upstream SemVer, require adoption of a newer version,
create equivalence mappings, update a dependency, or declare draft ontologies
unusable. It does not reopen prior modelling decisions.

## 19. Current EVENT/SoC status as repository examples

The current local EVENT dependency declares `Version 0.1.0 DRAFT` and its
Textile MIREOT record cites that source; the local SoC dependency declares
`Version 0.1.2 DRAFT` and its MIREOT record cites it. The EVENT MIREOT declares version `1.1.2`; the SoC MIREOT declares `1.1.3`. These are current repository facts and
governance inputs only: draft labels/version metadata do not alone prove present
Textile reuse invalid, and neither dependency is required to be upgraded.

## 20. Relationship to current MIREOT strategy

MIREOT makes the local reproduced subset auditable and bounds the initial reuse
inventory. It does not isolate Textile from every upstream semantic change: an
upstream change affecting a reproduced/reused term still needs this assessment.

## 21. Relationship to future dependency-update tasks

A future task must supply the candidate evidence, populate the impact record,
obtain required confirmation and owner decision, then implement any authorised
migration. This policy itself changes no upstream snapshot.
