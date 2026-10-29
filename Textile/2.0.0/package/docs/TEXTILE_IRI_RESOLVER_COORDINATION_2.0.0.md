# Textile 2.0.0 resolver coordination brief

Prepared locally on 2026-10-27. This is a routing proposal for review, not a
deployment instruction. Owner-approved Option B corrects the nine module version
identities locally. No redirects or remote resources were changed. Source push,
merge, tagging and publication still require separate authorization.

## Complete identity and destination inventory

Notation: `E = https://w3id.org/eudpp/` and
`D = https://cirpass-2.github.io/ontologies-docs/Textile/2.0.0/`.
Every IRI below is the exact concatenation of E and its displayed suffix.
Every destination is the exact concatenation of D and its displayed path.
The [current identity inventory](../migration/current-version-iri-inventory.json)
contains all 20 full ontology IRIs, actual declared version IRIs and canonical
source paths. The [HTTP record](../migration/resolver-http-observations.json)
is a time-stamped pre-correction observation, not a current identity inventory.
These destinations are proposed paths;
their existence is not asserted before deployment.

| Ontology IRI suffix (current alias) | Actual declared version IRI suffix | Proposed HTML destination or policy | Proposed current Turtle |
|---|---|---|---|
| textile-assessment | textile-assessment/2.0.0 | assessment/index-en.html | package/ontology/textile-assessment.ttl |
| textile-associated-materials | textile-associated-materials/2.0.0 | associated-materials/index-en.html | package/ontology/textile-associated-materials.ttl |
| textile-connector | textile-connector/2.0.0 | connector/index-en.html | package/ontology/textile-connector.ttl |
| textile-context | textile-context/2.0.0 | context/index-en.html | package/ontology/textile-context.ttl |
| textile-core | textile-core/2.0.0 | core/index-en.html | package/ontology/textile-core.ttl |
| textile-durability | textile-durability/2.0.0 | durability/index-en.html | package/ontology/textile-durability.ttl |
| textile-indicator | textile-indicator/2.0.0 | indicator/index-en.html | package/ontology/textile-indicator.ttl |
| textile-ontology | textile-ontology/2.0.0 | index.html | package/ontology/textile-ontology.ttl |
| textile-process | textile-process/2.0.0 | process/index-en.html | package/ontology/textile-process.ttl |
| textile-recyclability | textile-recyclability/2.0.0 | recyclability/index-en.html | package/ontology/textile-recyclability.ttl |
| textile-repairability | textile-repairability/2.0.0 | repairability/index-en.html | package/ontology/textile-repairability.ttl |
| textile-soc | textile-soc/2.0.0 | soc/index-en.html | package/ontology/textile-soc.ttl |
| textile-structure | textile-structure/2.0.0 | structure/index-en.html | package/ontology/textile-structure.ttl |
| textile-actor-mireot | textile-actor-mireot/2.0.0 | 406 (Turtle-only) | package/mireot/actor-textile-mireot.ttl |
| textile-con-mireot | textile-con-mireot/2.0.0 | 406 (Turtle-only) | package/mireot/con-textile-mireot.ttl |
| textile-dpp-mireot | textile-dpp-mireot/2.0.0 | 406 (Turtle-only) | package/mireot/dpp-textile-mireot.ttl |
| textile-event-mireot | textile-event-mireot/2.0.0 | 406 (Turtle-only) | package/mireot/event-textile-mireot.ttl |
| textile-mat-mireot | textile-mat-mireot/2.0.0 | 406 (Turtle-only) | package/mireot/mat-textile-mireot.ttl |
| textile-si-mireot | textile-si-mireot/1.1.2 | 406 (Turtle-only) | package/mireot/si-textile-mireot.ttl |
| textile-soc-mireot | textile-soc-mireot/2.0.0 | 406 (Turtle-only) | package/mireot/soc-textile-mireot.ttl |

The MIREOT guide at `D + package/docs/DEPENDENCIES.md` is Markdown source, not a
generated HTML representation. The
proposed policy is Turtle-only: absent Accept, `*/*` and `text/turtle` select
Turtle; requests accepting only HTML or unsupported RDF formats receive 406.
The guide can be advertised through a Link header, not served as `text/html`.
This policy requires namespace-maintainer agreement before deployment.
The root landing page is a network guide, not a complete WIDOCO root rendering.

For each of the 12 non-root Textile modules, XML, N-Triples and JSON-LD downloads
are also available at `D + <module>/ontology.owl`, `ontology.nt` and
`ontology.jsonld`; `ontology.ttl` is an equivalent Turtle download. No equivalent
XML/JSON-LD root or MIREOT exports are promised by this package.

## Immutable version-specific routing, separate from current aliases

The table above describes **versionless aliases**, which may advance only after
a future release is authorized. The following **19 actual version IRIs** must
remain pinned to this reviewed 2.0.0 package, with no latest-version indirection.
`E` and `D` expand exactly as above. Freeze these paths/bytes at release; changes
after publication require a new release identity. The nine newly corrected IRIs
are assessment, connector, context, core, durability, indicator, process,
repairability and structure. SI is deliberately absent from this 2.0.0 table.

| Immutable version IRI suffix | HTML destination or policy | Turtle destination |
|---|---|---|
| textile-assessment/2.0.0 | assessment/index-en.html | package/ontology/textile-assessment.ttl |
| textile-associated-materials/2.0.0 | associated-materials/index-en.html | package/ontology/textile-associated-materials.ttl |
| textile-connector/2.0.0 | connector/index-en.html | package/ontology/textile-connector.ttl |
| textile-context/2.0.0 | context/index-en.html | package/ontology/textile-context.ttl |
| textile-core/2.0.0 | core/index-en.html | package/ontology/textile-core.ttl |
| textile-durability/2.0.0 | durability/index-en.html | package/ontology/textile-durability.ttl |
| textile-indicator/2.0.0 | indicator/index-en.html | package/ontology/textile-indicator.ttl |
| textile-ontology/2.0.0 | index.html | package/ontology/textile-ontology.ttl |
| textile-process/2.0.0 | process/index-en.html | package/ontology/textile-process.ttl |
| textile-recyclability/2.0.0 | recyclability/index-en.html | package/ontology/textile-recyclability.ttl |
| textile-repairability/2.0.0 | repairability/index-en.html | package/ontology/textile-repairability.ttl |
| textile-soc/2.0.0 | soc/index-en.html | package/ontology/textile-soc.ttl |
| textile-structure/2.0.0 | structure/index-en.html | package/ontology/textile-structure.ttl |
| textile-actor-mireot/2.0.0 | 406 for HTML; Turtle-only policy | package/mireot/actor-textile-mireot.ttl |
| textile-con-mireot/2.0.0 | 406 for HTML; Turtle-only policy | package/mireot/con-textile-mireot.ttl |
| textile-dpp-mireot/2.0.0 | 406 for HTML; Turtle-only policy | package/mireot/dpp-textile-mireot.ttl |
| textile-event-mireot/2.0.0 | 406 for HTML; Turtle-only policy | package/mireot/event-textile-mireot.ttl |
| textile-mat-mireot/2.0.0 | 406 for HTML; Turtle-only policy | package/mireot/mat-textile-mireot.ttl |
| textile-soc-mireot/2.0.0 | 406 for HTML; Turtle-only policy | package/mireot/soc-textile-mireot.ttl |

The same 12 documented modules' immutable XML/NT/JSON-LD destinations are
`D + <module>/ontology.owl`, `D + <module>/ontology.nt` and
`D + <module>/ontology.jsonld` respectively. Negotiate those
formats only where present, with correct media types; the root and MIREOTs have
Turtle only. SI `/1.1.2` must select exact historical SI bytes as described below.

## Current HTTP observations and existing CORE routes

Read-only GET requests before Option B on 2026-10-27 at the UTC time in the
linked JSON, with redirect following disabled: all 40 then-active ontology and declared-version
endpoints returned **404**, with both `Accept: text/html` and `text/turtle`.
Lowercase `E + soc` also returned 404 for both. There were 94 requests in total,
including the following six CORE endpoints. A 404 does not establish namespace
ownership or permission to add a route. These observations cover initial
responses, not downstream availability or all possible media types. The nine new
version endpoints were not part of that earlier probe; their routes remain
undeployed and require maintainer acceptance tests. Do not treat the old probe
as evidence of live resolution for the corrected inventory.

All six CORE routes returned **303** for both Accept values, to
`https://dpp.vocabulary-hub.eu/api/ontology/-/version/OntologyVersion_` plus the
identifier below plus `/export?format=ttl`:

| Existing CORE suffix | Existing destination identifier (must remain unchanged) |
|---|---|
| ACTOR | e11d0f5e-fe86-4d51-86c4-53f9f66ac536 |
| MAT | 978009d5-042d-4d13-9ed6-7885433c1bce |
| EVENT | d3d95451-f2ac-4b4d-b2d0-5b413754591b |
| SOC | 11fcca33-b738-476a-a029-be53a333d81b |
| P_DPP | ab5a976e-95f4-4363-87c9-3abd11ee556b |
| CON | a50b649e-28cc-4107-a8e6-b69c3a401944 |

Preserve these routes and all other existing CORE rules. Never replace uppercase
SOC with lowercase legacy soc, redirect CORE modules to Textile MIREOT subsets,
or claim ownership of the shared `https://w3id.org/eudpp#` term namespace.
The six probes are a bounded inventory, not a claim that no other CORE routes exist.

## Approved Option B resolves the nine module identity collisions

The owner approved distinct `/2.0.0` version IRIs for assessment, connector,
context, core, durability, indicator, process, repairability and structure.
Each cites its historical `/1.1.2` IRI via `owl:priorVersion`. Version information,
revision date and citation annotations match the current candidate. All thirteen
current Textile graphs now have unambiguous 2.0.0 identities; unchanged SI alone
retains its 1.1.2 identity and exact bytes.

The [exact header diff](../migration/version-identity-results.json) records every
changed triple. The [nine-module comparison](../migration/retained-version-identities.json)
records current/historical hashes and both catalogues' import targets. The nine
graphs differ from history by the approved creators and version metadata only.
Reproduce the comparison offline with
`python -B scripts/observe_textile_resolvers.py --retained-only`.

Distinguish four concepts:

| Concept | Meaning and proposed treatment |
|---|---|
| Historical ontology identity | A declared old version IRI, such as `E + textile-connector/1.1.2`; pin to the exact preserved historical file, never the creator-updated candidate. |
| Current released ontology document | The reviewed canonical graph selected for a release, including its existing metadata; publication is still pending here. |
| Release-package snapshot URL | An immutable document address such as `D + package/ontology/textile-connector.ttl`; its ontology now declares `E + textile-connector/2.0.0`. The document URL and ontology version IRI remain distinct identifiers. |
| Current versionless alias | `E + textile-connector`; after authorization it may select the current released document through content negotiation. It is not a reproducible historical selector. |

Route old version-specific IRIs only to preserved old bytes, current version
IRIs to immutable current snapshots, and versionless aliases to the approved
current release. Local metadata approval is complete; namespace maintainers
still must approve and deploy routing independently. Serving modified bytes
at historical version-specific IRIs remains prohibited.

## Historical closure and content negotiation

For historical `/1.1.2` and SoC MIREOT `/1.1.3`, use exact corresponding files
under `D + package/migration/historical/1.1.2/ontology/` or `mireot/`.
If a legacy lowercase `/soc` route is agreed, use only the preserved
`dependencies/soc.ttl` in that historical subtree. There is no historical CON
MIREOT. Do not synthesize one or regenerate any historical RDF.

No new historical HTML is proposed. Pending namespace-maintainer agreement,
historical routes use the same explicit Turtle-only/default/406 policy described
above: Turtle for absent Accept, `*/*` or acceptable `text/turtle`; 406 for
HTML-only requests and unsupported formats. Select exact paths from the preserved
historical catalogue, including SI `/1.1.2`; do not redirect to current HTML.
If maintainers prefer historical HTML, they must first identify and verify an
immutable rendering of those exact old graphs. Existing legacy HTML remains
available at its existing URLs without claiming unverified graph fidelity.

An old versioned entry file alone does not ensure historical closure: its imports
are absolute versionless IRIs. Reproducible loading requires the preserved
`migration/historical/1.1.2/catalog-v001.xml`, paths relative to that directory,
network fallback disabled and no simultaneous active catalogue. Use separate
ontology managers for history and current data. The root and SoC historical
closures remain 19 and 12 graphs respectively. A package snapshot URL without
its catalogue is not a promise of an isolated HTTP import closure.

At the namespace resolver, negotiate HTML and RDF with explicit Accept handling,
303 responses where appropriate, `Vary: Accept`, correct destination media types,
and an agreed default/406 policy for unsupported formats. Test q-values and
fragment-bearing term IRIs as well as ontology IRIs. GitHub Pages cannot execute
server redirect rules; negotiation belongs to the namespace service. Place
explicit historical/version routes before broad versionless aliases. Keep old
public documentation paths available; do not overwrite them with 2.0.0 content.

Fragments are not transmitted in HTTP requests. The resolver sees the ontology
document IRI, not a term's `#localName`; redirect targets must not introduce
competing fragments. Browser fragment inheritance must be tested through the
entire redirect chain. For HTML, verify the retained term fragment after the
dynamic WIDOCO sections finish loading, using the assembled DOM. Local
annotation-property anchors are checked for all twelve documented modules.
For RDF negotiation, retrieval returns the full ontology document, not a
term-only response; consumers select the fragment-identified resource locally.
No network-only test can establish that the HTML term anchor exists.

## Responsibilities and authorization questions

CIRPASS-2 owns preparation of reviewed Textile files, immutable package paths,
checksums, documentation hosting, source/release sign-off and post-deployment
destination tests. Existing eudpp namespace maintainers own resolver configuration,
rule precedence, content negotiation, protection of existing CORE routes,
resolver review/deployment and rollback. Neither party's preparation authorizes
the other's deployment. A named maintainer and the authoritative configuration
repository remain to be confirmed; no guessed configuration path is proposed.

Before any remote action, agree:

- Who maintains eudpp routing, where is its authoritative configuration, and who
  reviews/deploys Textile-only rules while preserving all CORE routes?
- Who reviews the immutable 2.0.0 version routes separately from the mutable
  versionless aliases? The owner's Option B metadata decision is already accepted.
- Which historical aliases are supported, and who guarantees exact old bytes
  and explains catalogue-bound closure rather than mixed HTTP imports?
- What are the HTML destination for MIREOTs, supported Accept formats/defaults,
  cache/rollback policy and post-deployment acceptance tests?
- Who authorizes source merge, documentation deployment, release artifacts and
  version tag, and when may versionless aliases advance to 2.0.0?

No merge, tag, push, publication or redirect implementation is authorized by this
brief. The accepted 2.0.0 target and separate documentation path remain unchanged.
